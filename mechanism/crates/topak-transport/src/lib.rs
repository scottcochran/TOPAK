//! Round topics (ADR-0003) over Kafka (ADR-0005, Proposed).
//!
//! Kafka here is a transport with a durability window (`acks=all`; rskafka always produces with
//! `acks=-1`), **not** the ordering authority and **not** the system of record. Order comes
//! from the Paxos log: every emitted record carries the log index of the admit that authorized
//! it, the lease fence, and a per-principal sequence number (the ADR-0015 residual). An emitted
//! record is written only after its admit has committed. A **denial** record (ADR-0020: the
//! replayable record includes actions attempted and denied) has no admit: it is written,
//! unordered, by the replica that decided the denial: to the round's topic while it is open, and
//! after the seal to the round's `after` companion (ADR-0003 A2), up to a bound.
//!
//! One topic per principal per round, named by domain, seat, epoch and round. Kafka has no seal
//! primitive: sealing is enforced by the mechanism (the floor's `sealed` attribute refuses any
//! `Emit` once the round has ended), and the transport appends a seal marker so a reader can
//! see where the round closed.

use std::collections::{BTreeMap, BTreeSet, HashMap};
use std::sync::Arc;

use anyhow::{Context as _, bail};
use rskafka::client::partition::{Compression, PartitionClient, UnknownTopicHandling};
use rskafka::client::{Client, ClientBuilder};
use rskafka::record::Record;
use serde::{Deserialize, Serialize};
use serde_json::Value;
use tokio::sync::Mutex;
use topak_core::{Digest, LogIndex};

/// What a round-topic record is. Both are control-plane facts (ADR-0004).
#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum RecordKind {
    /// An admitted `Emit`: the effect itself.
    Emit,
    /// A denied action (ADR-0020). Never ordered (ADR-0015); carries no admit and no sequence.
    Deny,
    /// The `after` topic reached its bound (ADR-0003 A2); later denials are not written.
    Overflow,
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct EmitRecord {
    pub topic: String,
    pub seat: String,
    pub fence: LogIndex,
    pub kind: RecordKind,
    /// The log index of the `Admit` entry that authorized this emission. `None` for a denial.
    pub admit: Option<LogIndex>,
    /// The per-lease emission sequence number. `None` for a denial.
    pub seq: Option<u64>,
    pub digest: Digest,
    pub payload: Value,
}

pub enum Transport {
    Kafka(Kafka),
    Memory(Memory),
}

impl Transport {
    pub async fn emit(&self, rec: &EmitRecord) -> anyhow::Result<i64> {
        match self {
            Transport::Kafka(k) => k.emit(rec).await,
            Transport::Memory(m) => m.emit(rec).await,
        }
    }

    /// Append the seal marker. Idempotent.
    pub async fn seal(&self, topic: &str, reason: &str) -> anyhow::Result<()> {
        match self {
            Transport::Kafka(k) => k.seal(topic, reason).await,
            Transport::Memory(m) => m.seal(topic, reason).await,
        }
    }
}

fn headers(rec: &EmitRecord) -> BTreeMap<String, Vec<u8>> {
    let kind = match rec.kind {
        RecordKind::Emit => "emit",
        RecordKind::Deny => "deny",
        RecordKind::Overflow => "overflow",
    };
    let mut h = BTreeMap::from([
        ("topak-kind".to_owned(), kind.as_bytes().to_vec()),
        ("topak-seat".to_owned(), rec.seat.clone().into_bytes()),
        ("topak-fence".to_owned(), rec.fence.to_string().into_bytes()),
        ("topak-digest".to_owned(), rec.digest.0.clone().into_bytes()),
    ]);
    if let Some(a) = rec.admit {
        h.insert("topak-admit".to_owned(), a.to_string().into_bytes());
    }
    if let Some(s) = rec.seq {
        h.insert("topak-seq".to_owned(), s.to_string().into_bytes());
    }
    h
}

// ---- Kafka -----------------------------------------------------------------------------------

pub struct Kafka {
    client: Client,
    replication: i16,
    partitions: Mutex<HashMap<String, Arc<PartitionClient>>>,
    sealed: Mutex<BTreeSet<String>>,
}

impl Kafka {
    pub async fn connect(brokers: Vec<String>, replication: i16) -> anyhow::Result<Self> {
        let client = ClientBuilder::new(brokers).build().await.context("connecting to Kafka")?;
        Ok(Self { client, replication, partitions: Mutex::new(HashMap::new()), sealed: Mutex::new(BTreeSet::new()) })
    }

    async fn partition(&self, topic: &str) -> anyhow::Result<Arc<PartitionClient>> {
        if let Some(p) = self.partitions.lock().await.get(topic) {
            return Ok(p.clone());
        }
        // One partition: order within a round topic is the order of the principal's admits.
        let controller = self.client.controller_client()?;
        if let Err(e) = controller.create_topic(topic, 1, self.replication, 5_000).await {
            // Already exists is fine; anything else surfaces when we try to produce.
            tracing::debug!(topic, error = %e, "create_topic");
        }
        let p = Arc::new(self.client.partition_client(topic, 0, UnknownTopicHandling::Retry).await?);
        self.partitions.lock().await.insert(topic.to_string(), p.clone());
        Ok(p)
    }

    async fn emit(&self, rec: &EmitRecord) -> anyhow::Result<i64> {
        if self.sealed.lock().await.contains(&rec.topic) {
            bail!("topic {} is sealed", rec.topic);
        }
        let p = self.partition(&rec.topic).await?;
        let record = Record {
            key: Some(rec.seat.clone().into_bytes()),
            value: Some(serde_json::to_vec(&rec.payload)?),
            headers: headers(rec),
            // Informational only: no decision reads a transport timestamp (ADR-0032 §3).
            timestamp: chrono::Utc::now(),
        };
        let offsets = p.produce(vec![record], Compression::NoCompression).await?;
        offsets.first().copied().context("no offset returned")
    }

    async fn seal(&self, topic: &str, reason: &str) -> anyhow::Result<()> {
        if !self.sealed.lock().await.insert(topic.to_string()) {
            return Ok(());
        }
        let p = self.partition(topic).await?;
        let record = Record {
            key: None,
            value: None,
            headers: BTreeMap::from([("topak-seal".to_owned(), reason.as_bytes().to_vec())]),
            timestamp: chrono::Utc::now(),
        };
        p.produce(vec![record], Compression::NoCompression).await?;
        Ok(())
    }
}

// ---- in-memory, for tests and single-process demos ------------------------------------------

#[derive(Default)]
pub struct Memory {
    pub topics: Mutex<BTreeMap<String, Vec<EmitRecord>>>,
    pub sealed: Mutex<BTreeMap<String, String>>,
}

impl Memory {
    async fn emit(&self, rec: &EmitRecord) -> anyhow::Result<i64> {
        if self.sealed.lock().await.contains_key(&rec.topic) {
            bail!("topic {} is sealed", rec.topic);
        }
        let mut t = self.topics.lock().await;
        let v = t.entry(rec.topic.clone()).or_default();
        v.push(rec.clone());
        Ok(v.len() as i64 - 1)
    }

    async fn seal(&self, topic: &str, reason: &str) -> anyhow::Result<()> {
        self.sealed.lock().await.entry(topic.to_string()).or_insert_with(|| reason.to_string());
        Ok(())
    }
}
