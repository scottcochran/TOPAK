//! A log a workflow test writes into: the seats, the promotion of a workflow's single-file workspace,
//! the cell Observers, and the entries the mechanism and its cells would order. Shared by the core's
//! `workflow.rs` and the floor's, which lifts what this builds and asks the linked floor.
#![allow(dead_code)]

use std::collections::{BTreeMap, BTreeSet};

use serde_json::{Value, json};
use topak_core::action::{Action, ActionRequest};
use topak_core::labels::{Delivery, LabelFacts, RESTRICTED, UNTRUSTED};
use topak_core::lease::Confinement;
use topak_core::rules::*;
use topak_core::state::*;
use topak_core::workflow::*;
use topak_core::*;

pub fn seat(d: Domain, kind: SeatKind, key: &str) -> SeatDecl {
    SeatDecl { domain: d, kind, cell: None, key: key.into(), rung: 0 }
}

fn observer(of: &str) -> SeatDecl {
    SeatDecl { cell: Some(of.into()), ..seat(Domain::Run, SeatKind::Observer, &format!("k-o{of}")) }
}

/// Build seats to promote with; Run workers `ws`, `wb`, `wc`, `wj`, `ww`, `wx` with a cell Observer
/// each (`o<seat>`); the orchestrator `orc` with its Observer `oorc`; a correlator `cor`.
pub fn rules() -> Rules {
    let mut seats: BTreeMap<SeatId, SeatDecl> = BTreeMap::from([
        ("w1".into(), seat(Domain::Build, SeatKind::Thinker, "kw1")),
        ("o1".into(), SeatDecl { cell: Some("w1".into()), ..seat(Domain::Build, SeatKind::Observer, "ko1") }),
        ("g1".into(), seat(Domain::Build, SeatKind::Grant, "kg1")),
        ("g2".into(), seat(Domain::Build, SeatKind::Grant, "kg2")),
        ("g3".into(), seat(Domain::Build, SeatKind::Grant, "kg3")),
        ("orc".into(), seat(Domain::Run, SeatKind::Orchestrator, "korc")),
        ("cor".into(), seat(Domain::Run, SeatKind::Observer, "kcor")),
    ]);
    for w in ["ws", "wb", "wc", "wj", "ww", "wx"] {
        seats.insert(w.into(), seat(Domain::Run, SeatKind::Thinker, &format!("k{w}")));
        seats.insert(format!("o{w}"), observer(w));
    }
    seats.insert("oorc".into(), observer("orc"));
    Rules {
        rules_epoch: 0,
        quorum: Quorum::All,
        min_grant: 2,
        seats,
        grant_roster: ["g1", "g2", "g3"].into_iter().map(String::from).collect(),
        veto_roster: BTreeSet::new(),
        anchor_keys: BTreeSet::from(["kA".into()]),
        break_glass: None,
        erasure_roster: None,
        verifier_keys: BTreeSet::new(),
        bundle_keys: BTreeSet::new(),
        provider_keys: BTreeSet::new(),
        inside_targets: BTreeSet::new(),
        releasers: BTreeSet::new(),
        personas: BTreeMap::new(),
        criterion: None,
    }
}

pub fn params() -> Params {
    Params {
        corpus: BTreeSet::new(),
        build_tools: BTreeSet::new(),
        run_tools: BTreeSet::from(["post@d5".to_string()]),
        run_root: BTreeSet::new(),
        wasm_tools: BTreeSet::new(),
        round_bound: 8,
        lease_margin_ms: 0,
        after_topic_limit: 3,
        run_round_bound: Some(16),
    }
}

pub fn seating(seat: &str, lineage: &str, alphabet: &[ActionKind]) -> Value {
    json!({
        "seat": seat, "principal": format!("p-{seat}"), "persona": Digest::of(seat.as_bytes()),
        "bundle": Digest::of(b"bundle"), "confinement": { "digest": Digest::of(b"none"), "rung": 0 },
        "alphabet": alphabet, "ttl_ms": 1000, "lineage": lineage,
        "task": Digest::of(format!("task for {seat}").as_bytes()), "task_label": ["internal"],
    })
}

fn node(seat: &str, lineage: &str, outcomes: &[&str], outward: bool) -> Value {
    let mut v = seating(seat, lineage, &[ActionKind::Consult, ActionKind::Actuate, ActionKind::Report]);
    v["outcomes"] = json!(outcomes);
    v["outward"] = json!(outward);
    v
}

fn orchestrator() -> Value {
    seating("orc", "A", &[ActionKind::Route, ActionKind::Report])
}

/// ADR-0054 §12's workflow: four nodes, one decision point, one join, as `spec/Workflow.tla` has it.
/// `s` decides between `b` (clear, when `s` reports `ok`) and the outward `c` (by handle); `b` and
/// `c` join at the sink `j` on `any`, `b`'s edge firing only when `b` reports `done`.
pub fn dag() -> Value {
    json!({
        "kind": "dag", "root": "s", "sinks": ["j"],
        "nodes": {
            "s": node("ws", "A", &["ok", "bad"], false),
            "b": node("wb", "B", &["done", "retry"], false),
            "c": node("wc", "B", &["done"], true),
            "j": node("wj", "A", &["done"], false),
        },
        "edges": {
            "e1": { "from": "s", "to": "b", "kind": "chosen", "delivery": "clear",
                    "guard": { "outcome": { "node": "s", "any_of": ["ok"] } } },
            "e2": { "from": "s", "to": "c", "kind": "chosen", "delivery": "handle" },
            "e3": { "from": "b", "to": "j", "kind": "computed", "delivery": "clear",
                    "guard": { "outcome": { "node": "b", "any_of": ["done"] } } },
            "e4": { "from": "c", "to": "j", "kind": "computed", "delivery": "handle" },
        },
        "orchestrator": orchestrator(),
    })
}

/// ADR-0055 §11's mesh, as `spec/Mesh.tla` has it: `s` loops through `w` while it reports `again`,
/// and exits by handle to the outward sink `x` once it reports `ok`. The loop's edges are clear.
pub fn mesh(n: u64) -> Value {
    json!({
        "kind": "mesh", "root": "s", "sinks": ["x"],
        "nodes": {
            "s": node("ws", "A", &["ok", "again"], false),
            "w": node("ww", "B", &["done"], false),
            "x": node("wx", "B", &["done"], true),
        },
        "edges": {
            "e1": { "from": "s", "to": "w", "kind": "chosen", "delivery": "clear" },
            "e2": { "from": "s", "to": "x", "kind": "chosen", "delivery": "handle",
                    "guard": { "outcome": { "node": "s", "any_of": ["ok"] } } },
            "e3": { "from": "w", "to": "s", "kind": "computed", "delivery": "clear" },
        },
        "orchestrator": orchestrator(),
        "budget": { "n": n },
    })
}

pub struct Log {
    pub s: State,
    pub at: LogIndex,
    pub wf: Digest,
    round: Round,
    decided: std::cell::Cell<u64>,
}

pub fn refused(a: &Applied, why: &str) -> bool {
    matches!(a, Applied::Rejected(r) if r.contains(why))
}

impl Log {
    pub fn new() -> Log {
        let mut s = State::genesis(rules(), 2).unwrap();
        s.trace = topak_core::trace::name_from_env("wf");
        Log { s, at: 0, wf: Digest(String::new()), round: 100, decided: std::cell::Cell::new(0) }
    }

    pub fn apply(&mut self, e: Entry) -> Applied {
        self.at += 1;
        self.s.apply(self.at, &e, &params())
    }

    pub fn id(&self, what: &str) -> String {
        format!("{what}-{}", self.at + 1)
    }

    fn plain(&mut self, seat: &str, alphabet: &[ActionKind], role: RoundRole) -> LogIndex {
        self.round += 1;
        let req = GrantRequest {
            principal: format!("p-{seat}"),
            seat: seat.into(),
            persona: Digest::of(b"observer persona"),
            bundle: Digest::of(b"bundle"),
            confinement: Confinement { digest: Digest::of(b"none"), rung: 0 },
            alphabet: alphabet.iter().copied().collect(),
            ttl_ms: 3_600_000,
            round: self.round,
            role,
            task_label: None,
            task_labels_allowed: None,
            sign_on: None,
        };
        let id = self.id("g");
        match self.apply(Entry::Grant { id, req, appraisal: None }) {
            Applied::LeaseGranted { fence } => fence,
            a => panic!("grant of {seat} refused: {a:?}"),
        }
    }

    pub fn admit(&mut self, seat: &str, lease: LogIndex, action: Admitted, labels: Option<LabelFacts>) -> Applied {
        let id = self.id("admit");
        self.apply(admit_entry(&id, seat, lease, self.s.epoch, action, labels))
    }

    /// Promote the workflow's single-file workspace by tally (ADR-0054 §2) and load it.
    pub fn promote(&mut self, text: &str) -> Digest {
        let artifact = workflow_artifact(text.as_bytes());
        let f = self.plain("w1", &[ActionKind::Submit], RoundRole::Author);
        assert!(matches!(
            self.admit("w1", f, Admitted::Submit { artifact: artifact.clone() }, None),
            Applied::Admitted { .. }
        ));
        let evidence = Digest::of(b"gates");
        let id = self.id("gates");
        self.apply(Entry::GatesPassed { id, artifact: artifact.clone(), evidence: evidence.clone() });
        for g in ["g1", "g2", "g3"] {
            let f = self.plain(g, &[ActionKind::Vote], RoundRole::Voter);
            let vote = Admitted::Vote {
                verdict: Verdict::Grant,
                artifact: artifact.clone(),
                evidence: evidence.clone(),
                rules_epoch: 0,
            };
            self.admit(g, f, vote, None);
        }
        assert!(self.s.candidates[&artifact].promoted_at.is_some(), "the workflow's artifact promotes");
        artifact
    }

    pub fn load(&mut self, text: &str) -> Applied {
        let id = self.id("load");
        self.apply(Entry::WorkflowLoad { id, text: text.into(), outward: BTreeSet::new() })
    }

    /// Seat every cell Observer and the correlator for the length of the test, then promote and load.
    pub fn started(def: &Value) -> Log {
        let mut log = Log::new();
        for o in ["ows", "owb", "owc", "owj", "oww", "owx", "oorc", "cor"] {
            log.plain(o, &[ActionKind::Consult, ActionKind::Report], RoundRole::Author);
        }
        let text = serde_json::to_string_pretty(def).unwrap();
        log.promote(&text);
        match log.load(&text) {
            Applied::WorkflowLoaded { workflow } => log.wf = workflow,
            a => panic!("the workflow does not load: {a:?}"),
        }
        log
    }

    pub fn run(&self) -> &Run {
        &self.s.workflows[&self.wf]
    }

    /// The mechanism's grant of a slot, as any replica's driver proposes it.
    pub fn grant(&mut self, slot: Slot) -> Applied {
        let req = self.s.workflow_grant_request(&self.wf, &slot).unwrap();
        let id = self.id("wfg");
        self.apply(Entry::WorkflowGrant { id, workflow: self.wf.clone(), slot, req, appraisal: None })
    }

    /// Grant every ready slot, once, in the order the state lists them.
    pub fn grant_ready(&mut self) -> Vec<Applied> {
        let ready: Vec<Slot> =
            self.s.workflow_ready().into_iter().filter(|(w, _)| *w == self.wf).map(|(_, s)| s).collect();
        ready.into_iter().map(|slot| self.grant(slot)).collect()
    }

    pub fn fence_of(&self, seat: &str) -> LogIndex {
        self.s.live_by_seat[seat]
    }

    pub fn topic(&self, fence: LogIndex) -> String {
        let r = &self.s.leases[&fence];
        lift::topic_name(&self.s.chain, Domain::Run, &r.lease.seat, r.lease.epoch, r.lease.round)
    }

    /// The request a cell makes, as the deciding replica stamps it.
    pub fn request(&self, seat: &str, action: Action) -> ActionRequest {
        ActionRequest { seat: seat.into(), lease: self.fence_of(seat), epoch: self.s.epoch, action }
    }

    /// Decide at this state (the mechanism's checks before policy), then return the entry to order.
    pub fn decide(&self, seat: &str, action: Action) -> Result<Entry, MechanismDeny> {
        let req = self.request(seat, action);
        self.s.check_live(&req, &params())?;
        self.decided.set(self.decided.get() + 1);
        let id = format!("decided-{seat}-{}", self.decided.get());
        Ok(admit_entry(&id, seat, req.lease, self.s.epoch, self.s.admitted(&req, false), None))
    }

    /// A worker reports its typed outcome: the admit ends its round (ADR-0042 A3).
    pub fn outcome(&mut self, seat: &str, outcome: &str) -> Applied {
        let e = self
            .decide(seat, Action::Report { record: json!({ "outcome": outcome, "summary": "…" }) })
            .expect("decided");
        self.apply(e)
    }

    /// A worker reads content in the clear, labelled `label`: its `clearSet` grows (ADR-0047 §4).
    pub fn reads(&mut self, seat: &str, label: &[&str]) -> Applied {
        let fence = self.fence_of(seat);
        let clear_set = self.s.leases[&fence].labels.clear_set.clone();
        let facts = LabelFacts {
            clear_set,
            result_label: label.iter().map(|l| l.to_string()).collect(),
            delivery: Delivery::Clear,
            ..Default::default()
        };
        let object = Digest::of(format!("object {:?}", label).as_bytes());
        self.admit(seat, fence, Admitted::Consult { object }, Some(facts))
    }

    /// A cell Observer reads `fence`'s round to its seal (ADR-0039 §1).
    pub fn cover(&mut self, fence: LogIndex) -> Applied {
        let rec = &self.s.leases[&fence];
        let observer = format!("o{}", rec.lease.seat);
        let topic = self.topic(fence);
        let record = Heartbeat { topic, watermark: rec.seq }.record();
        let e = self.decide(&observer, Action::Report { record }).expect("heartbeat decided");
        self.apply(e)
    }

    /// The correlator's finding against `fence`'s round (ADR-0038 §1; PROVISIONAL finding-record).
    pub fn finding(&mut self, fence: LogIndex) -> Applied {
        let record = Finding { topic: self.topic(fence) }.record();
        let e = self.decide("cor", Action::Report { record }).expect("finding decided");
        self.apply(e)
    }

    pub fn route(&mut self, edge: &str) -> Applied {
        match self.decide("orc", Action::Route { edge: edge.into() }) {
            Ok(e) => self.apply(e),
            Err(d) => Applied::Rejected(format!("denied at decide: {d}")),
        }
    }

    /// The latest orchestrator round, live or ended.
    pub fn orc_round(&self) -> LogIndex {
        self.s
            .wf_bindings
            .iter()
            .filter(|(_, b)| matches!(b.slot, Slot::Decision(_)))
            .map(|(f, _)| *f)
            .max()
            .expect("an orchestrator round")
    }

    /// Its Observer reads the latest orchestrator round to the seal, so the next may be granted.
    pub fn cover_orc(&mut self) -> Applied {
        let f = self.orc_round();
        self.cover(f)
    }

    /// Run a worker's node: grant it, report `outcome`, and cover the round.
    pub fn work(&mut self, seat: &str, outcome: &str) -> LogIndex {
        self.grant_ready();
        let fence = self.fence_of(seat);
        assert!(matches!(self.outcome(seat, outcome), Applied::Admitted { .. }), "{seat} reports {outcome}");
        assert!(matches!(self.cover(fence), Applied::Admitted { .. }));
        fence
    }

    /// The index of `node`'s first activation.
    pub fn act_of(&self, node: &str) -> usize {
        self.run().acts.iter().position(|a| a.node == node).expect("entered")
    }

    /// The activations of `node`, in log order.
    pub fn acts(&self, node: &str) -> Vec<&Activation> {
        self.run().acts.iter().filter(|a| a.node == node).collect()
    }

    pub fn untrusted() -> Vec<&'static str> {
        vec![UNTRUSTED]
    }

    pub fn restricted() -> Vec<&'static str> {
        vec![RESTRICTED]
    }
}

pub fn admit_entry(
    id: &str,
    seat: &str,
    lease: LogIndex,
    epoch: Epoch,
    action: Admitted,
    labels: Option<LabelFacts>,
) -> Entry {
    Entry::Admit {
        id: id.into(),
        rec: AdmitRecord {
            seat: seat.into(),
            lease,
            epoch,
            action,
            input: Digest::of(b"input"),
            floor: Digest::of(b"floor"),
            schema: Digest::of(b"schema"),
            floor_reasons: vec![],
            bundle: Digest::of(b"bundle"),
            engine: BundleEngine::LocalWasm,
            params: params().digest(),
            decided_by: 1,
            session: None,
            labels,
        },
    }
}
