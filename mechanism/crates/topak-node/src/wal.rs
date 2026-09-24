//! The acceptor's write-ahead log. Paxos is safe across a crash only if promises and accepted
//! votes are durable before the replies that depend on them leave the process.

use std::fs::{File, OpenOptions};
use std::io::{BufRead, BufReader, Write};
use std::path::Path;

use serde::{Deserialize, Serialize};
use topak_core::state::Entry;
use topak_paxos::{Ballot, Cmd, Durable, Output, Slot};

// Records are transient (serialized, then dropped), so the variant size difference is moot.
#[allow(clippy::large_enum_variant)]
#[derive(Serialize, Deserialize)]
enum Record {
    Promise { ballot: Ballot },
    Accept { slot: Slot, ballot: Ballot, cmd: Cmd<Entry> },
}

pub struct Wal {
    file: File,
}

impl Wal {
    /// Open (creating if absent) and replay into the durable acceptor image.
    pub fn open(path: &Path) -> anyhow::Result<(Self, Durable<Entry>)> {
        let mut durable = Durable::default();
        if path.exists() {
            for line in BufReader::new(File::open(path)?).lines() {
                let line = line?;
                if line.trim().is_empty() {
                    continue;
                }
                // A torn final line from a crash mid-write was never fsynced, so nothing that
                // depended on it was sent. Stop there.
                let Ok(rec) = serde_json::from_str::<Record>(&line) else { break };
                durable.absorb(&match rec {
                    Record::Promise { ballot } => Output::PersistPromise { ballot },
                    Record::Accept { slot, ballot, cmd } => Output::PersistAccept { slot, ballot, cmd },
                });
            }
        }
        let file = OpenOptions::new().create(true).append(true).open(path)?;
        Ok((Self { file }, durable))
    }

    /// Append the persist outputs of one batch and fsync once.
    pub fn append(&mut self, outs: &[&Output<Entry>]) -> anyhow::Result<()> {
        if outs.is_empty() {
            return Ok(());
        }
        for o in outs {
            let rec = match o {
                Output::PersistPromise { ballot } => Record::Promise { ballot: *ballot },
                Output::PersistAccept { slot, ballot, cmd } => {
                    Record::Accept { slot: *slot, ballot: *ballot, cmd: cmd.clone() }
                }
                _ => continue,
            };
            let mut line = serde_json::to_vec(&rec)?;
            line.push(b'\n');
            self.file.write_all(&line)?;
        }
        self.file.sync_data()?;
        Ok(())
    }
}
