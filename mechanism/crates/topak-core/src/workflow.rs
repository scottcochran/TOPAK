//! Workflows (ADR-0054) and meshes (ADR-0055), both Proposed: a promoted graph of seatings that the
//! mechanism runs.
//!
//! A workflow is a Build artifact, promoted like any other. Its promotion is the grant: the mechanism
//! grants each node's lease when the node becomes ready, under the tally's authority, with every
//! field the seating's (ADR-0054 §2; ADR-0024 A4, ADR-0031 A4, pending). Edges are **computed**, fired
//! by the mechanism inside the apply of the entry that made them evaluable, or **chosen**, selected by
//! an `orchestrator` seat with `Route(edge)` among those the mechanism has enabled, and checked again
//! where the route is applied (§3, §8). A guard is a mechanism check over attributes the mechanism
//! lifted when a round ended; it is not policy, and no attribute is a literal (§4).
//!
//! One engine runs both kinds. Every node run is an **activation** (ADR-0055 §3) with its trigger and
//! its causal history. A `dag` is the case in which a node runs at most once, its graph has no cycle,
//! and a guard reads only the source and the nodes that dominate it, which are always in the history.
//! A `mesh` may have cycles and runs out of a budget the promotion votes on (ADR-0055 §2).
//!
//! What this module is not: the gate's evidence for the vote (ADR-0055 §2), the tally's lineage check
//! (ADR-0035, Proposed: here the declared lineages are compared at load, D-0054-1), `T_wf` and the step
//! bound (no replicated clock), pools and parity seatings, fan-out-scoped joins in a mesh. Each is a
//! `PROVISIONAL` row in `GAPS-AND-ASSUMPTIONS.md` (I49) or a gap.

use std::collections::{BTreeMap, BTreeSet};

use serde::{Deserialize, Serialize};

use crate::confine::workspace_digest;
use crate::labels::{Delivery, Label, RESTRICTED, UNTRUSTED};
use crate::lease::Confinement;
use crate::state::{EndReason, GrantRequest, Seal};
use crate::types::*;

/// The workflow's single file in its promoted workspace, as a profile's is (ADR-0034 §1).
pub const WORKFLOW_FILE: &str = "workflow.json";

/// The digest of the single-file workspace a workflow is promoted as. A workflow loads only if this
/// artifact has been promoted: the completed tally is the authority for every lease it issues.
pub fn workflow_artifact(bytes: &[u8]) -> Digest {
    workspace_digest([(WORKFLOW_FILE.to_string(), bytes.to_vec())])
}

// ---- the promoted text -----------------------------------------------------------------------

#[derive(Clone, Copy, Debug, Default, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum Kind {
    /// ADR-0054: acyclic, checked at load. The default.
    #[default]
    Dag,
    /// ADR-0055 §1: cycles allowed, under a budget. A declared widening.
    Mesh,
}

/// A seating as a workflow names it (ADR-0024 A3, A4): everything a lease carries that the log does
/// not assign. The mechanism grants exactly this, so a grant can be no wider than what was voted on.
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct SeatingDef {
    pub seat: SeatId,
    pub principal: String,
    pub persona: Digest,
    pub bundle: Digest,
    pub confinement: Confinement,
    pub alphabet: BTreeSet<ActionKind>,
    pub ttl_ms: u64,
    /// The Thinker Persona's lineage, as declared (ADR-0054 §6). PROVISIONAL (workflow-lineage):
    /// ADR-0035 is Proposed, so lineage is a declared tag compared at load, D-0054-1.
    pub lineage: String,
    /// The task template, by digest, and its label (ADR-0054 §1; ADR-0047 §1). Promoted text: no
    /// principal writes a task.
    pub task: Digest,
    #[serde(default)]
    pub task_label: Label,
}

#[derive(Clone, Copy, Debug, Default, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum Join {
    /// The first incoming edge to fire activates the node.
    #[default]
    Any,
    /// Every incoming edge has fired or can no longer fire, and at least one fired (ADR-0054 §1).
    All,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct NodeDef {
    #[serde(flatten)]
    pub seating: SeatingDef,
    /// The node's closed enum of outcomes, the values a worker's typed `outcome` may take (§4).
    pub outcomes: BTreeSet<String>,
    /// The node's lease reaches an outward entry (ADR-0049 §5). Declared; the deciding replica adds
    /// what the bundle says at load, and the mechanism takes the union (`Entry::WorkflowLoad`).
    #[serde(default)]
    pub outward: bool,
    #[serde(default)]
    pub join: Join,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum EdgeKind {
    Computed,
    Chosen,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct EdgeDef {
    pub from: String,
    pub to: String,
    pub kind: EdgeKind,
    #[serde(default = "Guard::always")]
    pub guard: Guard,
    pub delivery: Delivery,
}

/// ADR-0055 §2: the bound on the leases a mesh may ever issue, orchestrator rounds included, and
/// optionally per node.
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Budget {
    pub n: u64,
    #[serde(default)]
    pub per_node: BTreeMap<String, u64>,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Definition {
    #[serde(default)]
    pub kind: Kind,
    pub root: String,
    pub sinks: BTreeSet<String>,
    pub nodes: BTreeMap<String, NodeDef>,
    pub edges: BTreeMap<String, EdgeDef>,
    /// Seated if and only if the graph has a chosen edge (ADR-0054 §3), checked at load.
    #[serde(default)]
    pub orchestrator: Option<SeatingDef>,
    #[serde(default)]
    pub budget: Option<Budget>,
}

// ---- guards ----------------------------------------------------------------------------------

/// How a round ended (ADR-0054 §4).
#[derive(Clone, Copy, Debug, PartialEq, Eq, PartialOrd, Ord, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum EndKind {
    Outcome,
    Expired,
    Fenced,
    Revoked,
}

impl EndKind {
    pub fn of(r: EndReason) -> EndKind {
        match r {
            EndReason::Outcome | EndReason::Routed | EndReason::Submitted | EndReason::Voted | EndReason::Abstained => {
                EndKind::Outcome
            }
            EndReason::Expired | EndReason::Renewed => EndKind::Expired,
            EndReason::Fenced | EndReason::RulesChanged => EndKind::Fenced,
            EndReason::Revoked | EndReason::Operator => EndKind::Revoked,
        }
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum Counter {
    Actuates,
    Denials,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum Cmp {
    Lt,
    Le,
    Eq,
    Ge,
    Gt,
}

/// A guard, in ADR-0054 §4's fixed and decidable language: set membership over enums, label
/// membership, comparison of a bounded count with a constant, and the connectives. No string is
/// compared with anything a principal wrote, and no arithmetic, clock or history operator exists.
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum Guard {
    True,
    Not(Box<Guard>),
    All(Vec<Guard>),
    Any(Vec<Guard>),
    Outcome { node: String, any_of: BTreeSet<String> },
    End { node: String, any_of: BTreeSet<EndKind> },
    Label { node: String, has: String },
    Count { node: String, of: Counter, cmp: Cmp, value: u64 },
}

impl Guard {
    pub fn always() -> Guard {
        Guard::True
    }

    /// The nodes whose attributes the guard reads.
    pub fn reads(&self) -> BTreeSet<String> {
        let mut out = BTreeSet::new();
        self.collect(&mut out);
        out
    }

    fn collect(&self, out: &mut BTreeSet<String>) {
        match self {
            Guard::True => {}
            Guard::Not(g) => g.collect(out),
            Guard::All(gs) | Guard::Any(gs) => gs.iter().for_each(|g| g.collect(out)),
            Guard::Outcome { node, .. }
            | Guard::End { node, .. }
            | Guard::Label { node, .. }
            | Guard::Count { node, .. } => {
                out.insert(node.clone());
            }
        }
    }

    /// Evaluate against the attributes `at(node)` resolves. A node with no attributes in reach makes
    /// every atom over it false, so an absent value never enables an edge.
    pub fn eval(&self, at: &dyn Fn(&str) -> Option<Attributes>) -> bool {
        match self {
            Guard::True => true,
            Guard::Not(g) => !g.eval(at),
            Guard::All(gs) => gs.iter().all(|g| g.eval(at)),
            Guard::Any(gs) => gs.iter().any(|g| g.eval(at)),
            Guard::Outcome { node, any_of } => {
                at(node).is_some_and(|a| any_of.contains(a.outcome.as_deref().unwrap_or("none")))
            }
            Guard::End { node, any_of } => at(node).is_some_and(|a| any_of.contains(&a.end)),
            Guard::Label { node, has } => at(node).is_some_and(|a| a.label.contains(has)),
            Guard::Count { node, of, cmp, value } => at(node).is_some_and(|a| {
                let n = match of {
                    Counter::Actuates => a.actuates,
                    Counter::Denials => a.denials,
                };
                match cmp {
                    Cmp::Lt => n < *value,
                    Cmp::Le => n <= *value,
                    Cmp::Eq => n == *value,
                    Cmp::Ge => n >= *value,
                    Cmp::Gt => n > *value,
                }
            }),
        }
    }
}

// ---- the running state -----------------------------------------------------------------------

/// What the mechanism lifts when a node's round ends (ADR-0054 §4; ADR-0047 A1, pending). Written
/// once; `found` is kept on the activation, because it is the one attribute that changes after the
/// end, and only from false to true.
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct Attributes {
    pub end: EndKind,
    pub actuates: u64,
    /// PROVISIONAL (workflow-denials): a denial is never logged (ADR-0015), so no replica can count
    /// one. Always 0 in the reference.
    pub denials: u64,
    /// The worker's `clearSet` at its seal. Every attribute of the node carries it (§5).
    pub label: Label,
    /// The declared outcome, `None` if the worker reported none.
    pub outcome: Option<String>,
    /// The sequence numbers of the worker's reports: a handle on its output.
    pub output: Vec<u64>,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(tag = "status", rename_all = "snake_case")]
pub enum ActStatus {
    /// An `all` join with some incoming edges still able to fire.
    Waiting,
    Ready,
    Running {
        fence: LogIndex,
    },
    Ended,
    Failed {
        why: String,
    },
    /// Every incoming edge can no longer fire (ADR-0054 §1).
    Skipped,
}

/// One round of one cell (ADR-0055 §3).
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct Activation {
    pub node: String,
    /// The activation it was entered from, and the edge; `None` for the root.
    pub trig: Option<usize>,
    pub via: Option<String>,
    /// Every incoming edge that has fired into it (an `all` join has more than one).
    pub fired: BTreeSet<String>,
    pub status: ActStatus,
    /// Itself and its triggers' histories: the activations whose attributes a guard may read.
    pub hist: BTreeSet<usize>,
    pub created_at: LogIndex,
    /// The join of the labels of its inputs delivered clear: they join the round's `clearSet` at
    /// grant (ADR-0043 A3, ADR-0047 A1).
    pub clear_inputs: Label,
    /// The join of the labels of its inputs delivered as handles. PROVISIONAL (workflow-handles):
    /// recorded, and not resolvable by the guest in the reference.
    pub handle_inputs: Label,
    pub attrs: Option<Attributes>,
    pub found: bool,
    pub seal: Option<Seal>,
    pub covered: bool,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(tag = "state", rename_all = "snake_case")]
pub enum EventState {
    /// The decision node's round ended; no orchestrator round has been granted for it.
    Open,
    /// An orchestrator round holds it.
    Served {
        fence: LogIndex,
    },
    /// A route applied.
    Consumed {
        edge: String,
    },
    Failed {
        why: String,
    },
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(tag = "status", rename_all = "snake_case")]
pub enum RunStatus {
    Running,
    Completed,
    Failed { why: String },
}

/// One loaded workflow and everything the mechanism has done with it.
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct Run {
    pub def: Definition,
    pub artifact: Digest,
    pub loaded_at: LogIndex,
    /// The epoch and rules epoch of the load: a grant under any other is refused (ADR-0024 A4).
    pub epoch: Epoch,
    pub rules_epoch: RulesEpoch,
    /// Declared outward nodes, joined with what the deciding replica computed from the bundle.
    pub outward: BTreeSet<String>,
    pub status: RunStatus,
    pub acts: Vec<Activation>,
    /// Decision events, by the activation whose end opened them.
    pub events: BTreeMap<usize, EventState>,
    /// Leases charged to the budget, and per node; the orchestrator's under its seat.
    pub charged: u64,
    pub charged_node: BTreeMap<String, u64>,
    pub exhausted: bool,
    /// (activation, computed edge) pairs already evaluated: a computed edge is evaluated once.
    pub evaluated: BTreeSet<(usize, String)>,
}

/// What a lease granted by a workflow is for.
#[derive(Clone, Debug, PartialEq, Eq, PartialOrd, Ord, Serialize, Deserialize)]
#[serde(tag = "slot", content = "act", rename_all = "snake_case")]
pub enum Slot {
    /// A worker's round: the activation.
    Node(usize),
    /// An orchestrator's round: the decision event.
    Decision(usize),
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct Binding {
    pub workflow: Digest,
    pub slot: Slot,
    /// `Actuate` admits under the lease, and the sequence numbers of its reports.
    #[serde(default)]
    pub actuates: u64,
    #[serde(default)]
    pub reports: Vec<u64>,
    #[serde(default)]
    pub outcome: Option<String>,
    /// The end has been lifted into the run.
    #[serde(default)]
    pub lifted: bool,
}

/// What a route carries beyond its edge, stamped by the deciding replica from the lease (ADR-0055
/// §6): the workflow and decision event its round was granted for, and the basis, the log index of
/// the state the orchestrator was shown (ADR-0054 §8). The round is the lease's fence.
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct RouteStamp {
    pub workflow: Digest,
    pub event: usize,
    pub basis: LogIndex,
}

/// The Cedar id of a workflow's node or edge: unique across workflows.
pub fn node_uid(workflow: &Digest, node: &str) -> String {
    format!("{}/{}", workflow.short(), node)
}

pub fn edge_uid(workflow: &Digest, edge: &str) -> String {
    format!("{}/{}", workflow.short(), edge)
}

// ---- load checks -----------------------------------------------------------------------------

/// What a load check reads of a declared seat in the issued rules: its kind, domain and rung.
pub type SeatLookup<'a> = dyn Fn(&str) -> Option<(SeatKind, Domain, u8)> + 'a;

impl Definition {
    pub fn parse(text: &str) -> Result<Definition, String> {
        serde_json::from_str(text).map_err(|e| format!("not a workflow: {e}"))
    }

    pub fn out_edges<'a>(&'a self, node: &'a str) -> impl Iterator<Item = (&'a String, &'a EdgeDef)> + 'a {
        self.edges.iter().filter(move |(_, e)| e.from == node)
    }

    pub fn in_edges<'a>(&'a self, node: &'a str) -> impl Iterator<Item = (&'a String, &'a EdgeDef)> + 'a {
        self.edges.iter().filter(move |(_, e)| e.to == node)
    }

    pub fn has_chosen(&self, node: &str) -> bool {
        self.out_edges(node).any(|(_, e)| e.kind == EdgeKind::Chosen)
    }

    /// The graph has a cycle, self-loops included.
    pub fn has_cycle(&self) -> bool {
        // Kahn's algorithm over the declared nodes.
        let mut indeg: BTreeMap<&str, usize> = self.nodes.keys().map(|n| (n.as_str(), 0)).collect();
        for e in self.edges.values() {
            *indeg.entry(e.to.as_str()).or_default() += 1;
        }
        let mut queue: Vec<&str> = indeg.iter().filter(|(_, d)| **d == 0).map(|(n, _)| *n).collect();
        let mut seen = 0;
        while let Some(n) = queue.pop() {
            seen += 1;
            for e in self.edges.values().filter(|e| e.from == n) {
                let d = indeg.get_mut(e.to.as_str()).expect("declared");
                *d -= 1;
                if *d == 0 {
                    queue.push(e.to.as_str());
                }
            }
        }
        seen != indeg.len()
    }

    /// The nodes on every path from the root to `node`, `node` excluded (its strict dominators). In
    /// a DAG they have all ended before `node` is ready, so a guard on an edge out of `node` may read
    /// them and its read set is settled when it is first evaluable (ADR-0054 §4).
    pub fn dominators(&self, node: &str) -> BTreeSet<String> {
        let all: BTreeSet<String> = self.nodes.keys().cloned().collect();
        let mut dom: BTreeMap<String, BTreeSet<String>> = self
            .nodes
            .keys()
            .map(|n| (n.clone(), if *n == self.root { BTreeSet::from([n.clone()]) } else { all.clone() }))
            .collect();
        loop {
            let mut changed = false;
            for n in self.nodes.keys().filter(|n| **n != self.root) {
                let preds: Vec<&String> = self.in_edges(n).map(|(_, e)| &e.from).collect();
                let mut d = preds
                    .iter()
                    .map(|p| dom[*p].clone())
                    .reduce(|a, b| a.intersection(&b).cloned().collect())
                    .unwrap_or_default();
                d.insert(n.clone());
                if d != dom[n] {
                    dom.insert(n.clone(), d);
                    changed = true;
                }
            }
            if !changed {
                break;
            }
        }
        let mut d = dom.remove(node).unwrap_or_default();
        d.remove(node);
        d
    }

    /// Every load check that needs nothing but the text. `seat_kind` reads the issued rules.
    pub fn check(&self, seat_kind: &SeatLookup) -> Vec<String> {
        let mut bad = Vec::new();
        if !self.nodes.contains_key(&self.root) {
            bad.push(format!("the root {} is not a node", self.root));
        }
        if self.sinks.is_empty() || self.sinks.iter().any(|s| !self.nodes.contains_key(s)) {
            bad.push("the sinks are empty or name a node that is not declared".into());
        }
        for (id, e) in &self.edges {
            if !self.nodes.contains_key(&e.from) || !self.nodes.contains_key(&e.to) {
                bad.push(format!("edge {id} names a node that is not declared"));
            }
        }
        if !bad.is_empty() {
            return bad;
        }
        if self.in_edges(&self.root).next().is_some() && self.kind == Kind::Dag {
            bad.push(format!("the root {} of a dag has an incoming edge", self.root));
        }
        match self.kind {
            // ADR-0054 §1: a dag whose graph has a cycle does not load.
            Kind::Dag if self.has_cycle() => {
                bad.push("the graph has a cycle and the workflow is a dag (ADR-0054 §1)".into())
            }
            Kind::Dag if self.budget.is_some() => bad.push("a dag carries no budget".into()),
            Kind::Dag => {}
            // ADR-0055 §2: a mesh does not load without a budget.
            Kind::Mesh => match &self.budget {
                None => bad.push("a mesh does not load without a budget (ADR-0055 §2)".into()),
                Some(b) if b.n == 0 => bad.push("a mesh's budget is zero".into()),
                Some(b) if b.per_node.keys().any(|n| !self.nodes.contains_key(n)) => {
                    bad.push("the budget names a node that is not declared".into())
                }
                Some(_) => {}
            },
        }
        // PROVISIONAL (workflow-mesh-joins): ADR-0055 §4 scopes an `all` join to a fan-out, and the
        // reference does not build fan-out scoping. A mesh with an `all` join does not load.
        if self.kind == Kind::Mesh && self.nodes.values().any(|n| n.join == Join::All) {
            bad.push("an `all` join in a mesh is not built in the reference (ADR-0055 §4)".into());
        }
        // ADR-0054 §3: an orchestrator is seated if and only if the graph has a chosen edge.
        let chosen = self.edges.values().any(|e| e.kind == EdgeKind::Chosen);
        match (&self.orchestrator, chosen) {
            (None, true) => bad.push("a chosen edge and no orchestrator (ADR-0054 §3)".into()),
            (Some(_), false) => bad.push("an orchestrator and no chosen edge (ADR-0054 §3)".into()),
            _ => {}
        }
        // Seatings: the seat's kind, the domain, the alphabet the kind allows, rung 0.
        let mut seatings: Vec<(&str, &SeatingDef, SeatKind)> =
            self.nodes.iter().map(|(n, d)| (n.as_str(), &d.seating, SeatKind::Thinker)).collect();
        if let Some(o) = &self.orchestrator {
            seatings.push(("orchestrator", o, SeatKind::Orchestrator));
        }
        for (who, s, want) in &seatings {
            match seat_kind(&s.seat) {
                None => bad.push(format!("{who}'s seat {} is not declared", s.seat)),
                Some((k, d, rung)) => {
                    if k != *want {
                        bad.push(format!("{who}'s seat {} is a {k} seat, not a {want} seat", s.seat));
                    }
                    if d != Domain::Run {
                        bad.push(format!("{who}'s seat {} is not a Run seat", s.seat));
                    }
                    if let Some(a) = s.alphabet.iter().find(|a| !want.allows(**a)) {
                        bad.push(format!("{who}'s alphabet holds {a}, outside the {want} kind (ADR-0037 §4)"));
                    }
                    // PROVISIONAL (workflow-rung0): a grant at rung 1 or above is appraised with a
                    // nonce from the log (ADR-0031 A4), and the reference's workflow grant carries no
                    // appraisal. A seating above rung 0 does not load.
                    if s.confinement.rung != 0 || rung != 0 {
                        bad.push(format!("{who}'s seating is above rung 0, which the reference does not grant"));
                    }
                }
            }
        }
        for (n, d) in &self.nodes {
            if d.outcomes.is_empty() || d.outcomes.contains("none") {
                bad.push(format!("node {n}'s outcomes are empty or use the reserved `none`"));
            }
        }
        // ADR-0054 §4: a guard reads the source and its dominators (a dag), or what the activation's
        // causal history holds (a mesh), so any declared node.
        for (id, e) in &self.edges {
            let reads = e.guard.reads();
            if let Some(n) = reads.iter().find(|n| !self.nodes.contains_key(*n)) {
                bad.push(format!("edge {id}'s guard reads {n}, which is not a node"));
                continue;
            }
            if self.kind == Kind::Dag {
                let mut may = self.dominators(&e.from);
                may.insert(e.from.clone());
                if let Some(n) = reads.iter().find(|n| !may.contains(*n)) {
                    bad.push(format!("edge {id}'s guard reads {n}, which does not dominate {} (ADR-0054 §4)", e.from));
                }
            }
        }
        // ADR-0054 §6, ADR-0055 §5: a clear edge joins two lineages. Checked over the declared tags,
        // so a clear self-loop never loads. PROVISIONAL (workflow-lineage): D-0054-1.
        for (id, e) in self.edges.iter().filter(|(_, e)| e.delivery == Delivery::Clear) {
            if self.nodes[&e.from].seating.lineage == self.nodes[&e.to].seating.lineage {
                bad.push(format!("clear edge {id} joins one lineage on both ends (ADR-0054 §6)"));
            }
        }
        bad
    }
}

// ---- the run ---------------------------------------------------------------------------------

impl Run {
    pub fn new(
        def: Definition,
        artifact: Digest,
        at: LogIndex,
        epoch: Epoch,
        rules_epoch: RulesEpoch,
        outward: BTreeSet<String>,
    ) -> Run {
        let root = Activation {
            node: def.root.clone(),
            trig: None,
            via: None,
            fired: BTreeSet::new(),
            status: ActStatus::Ready,
            hist: BTreeSet::from([0]),
            created_at: at,
            clear_inputs: Label::new(),
            handle_inputs: Label::new(),
            attrs: None,
            found: false,
            seal: None,
            covered: false,
        };
        Run {
            def,
            artifact,
            loaded_at: at,
            epoch,
            rules_epoch,
            outward,
            status: RunStatus::Running,
            acts: vec![root],
            events: BTreeMap::new(),
            charged: 0,
            charged_node: BTreeMap::new(),
            exhausted: false,
            evaluated: BTreeSet::new(),
        }
    }

    pub fn running(&self) -> bool {
        self.status == RunStatus::Running
    }

    /// The attributes of `node` as a guard on an edge out of activation `i` sees them: the latest
    /// ended activation of `node` in `i`'s causal history (ADR-0055 §3), never a node's latest value.
    pub fn attrs_in_history(&self, i: usize, node: &str) -> Option<Attributes> {
        self.acts[i]
            .hist
            .iter()
            .rev()
            .find(|j| self.acts[**j].node == node && self.acts[**j].attrs.is_some())
            .and_then(|j| self.acts[*j].attrs.clone())
    }

    /// Why edge `e` out of activation `i` is not enabled, or `None` if it is: the source ended and
    /// covered (ADR-0054 §7), its guard true (§4), the routing rule (§5), and no finding against any
    /// activation in its causal history (ADR-0055 §3).
    pub fn disabled(&self, i: usize, edge: &str) -> Option<&'static str> {
        let Some(e) = self.def.edges.get(edge) else { return Some("guard") };
        let a = &self.acts[i];
        if a.node != e.from || a.status != ActStatus::Ended {
            return Some("guard");
        }
        if !a.covered {
            return Some("uncovered");
        }
        if a.hist.iter().any(|j| self.acts[*j].found) {
            return Some(if a.found { "finding" } else { "history" });
        }
        let at = |n: &str| self.attrs_in_history(i, n);
        if !e.guard.eval(&at) {
            return Some("guard");
        }
        // The routing rule: an edge into a node that reaches outward, or that receives restricted
        // input in the clear, is disabled when any attribute its guard reads is labelled untrusted.
        // An attribute carries its node's label; the source's is always read, since the edge
        // delivers its output.
        let restricted_in =
            e.delivery == Delivery::Clear && a.attrs.as_ref().is_some_and(|x| x.label.contains(RESTRICTED));
        if self.outward.contains(&e.to) || restricted_in {
            let mut reads = e.guard.reads();
            reads.insert(e.from.clone());
            if reads.iter().any(|n| at(n).is_some_and(|x| x.label.contains(UNTRUSTED))) {
                return Some("taint");
            }
        }
        None
    }

    /// Enter `edge` from activation `src`: a new activation of its target (a mesh, or a dag node not
    /// yet entered), or one more fired edge into a waiting `all` join.
    pub fn enter(&mut self, src: usize, edge: &str, at: LogIndex) {
        let e = self.def.edges[edge].clone();
        let label = self.acts[src].attrs.as_ref().map(|a| a.label.clone()).unwrap_or_default();
        let (clear, handle) = match e.delivery {
            Delivery::Clear => (label, Label::new()),
            Delivery::Handle => (Label::new(), label),
        };
        if self.def.kind == Kind::Dag
            && let Some(j) = self.acts.iter().position(|a| a.node == e.to)
        {
            let a = &mut self.acts[j];
            if a.status == ActStatus::Waiting {
                a.fired.insert(edge.to_string());
                a.clear_inputs.extend(clear);
                a.handle_inputs.extend(handle);
                let h = self.acts[src].hist.clone();
                self.acts[j].hist.extend(h);
            }
            // An `any` join already entered: the edge is taken and changes nothing (ADR-0054 §1).
            return;
        }
        let n = self.acts.len();
        let mut hist = self.acts[src].hist.clone();
        hist.insert(n);
        let join = self.def.nodes[&e.to].join;
        self.acts.push(Activation {
            node: e.to.clone(),
            trig: Some(src),
            via: Some(edge.to_string()),
            fired: BTreeSet::from([edge.to_string()]),
            status: if join == Join::All { ActStatus::Waiting } else { ActStatus::Ready },
            hist,
            created_at: at,
            clear_inputs: clear,
            handle_inputs: handle,
            attrs: None,
            found: false,
            seal: None,
            covered: false,
        });
    }

    /// In a dag: whether edge `edge` can no longer fire.
    fn dead(&self, edge: &str) -> bool {
        let e = &self.def.edges[edge];
        let Some(i) = self.acts.iter().position(|a| a.node == e.from) else { return false };
        match &self.acts[i].status {
            ActStatus::Failed { .. } | ActStatus::Skipped => true,
            ActStatus::Ended => match e.kind {
                EdgeKind::Computed => {
                    self.evaluated.contains(&(i, edge.to_string()))
                        && !self.acts.iter().any(|a| a.node == e.to && a.fired.contains(edge))
                }
                EdgeKind::Chosen => match self.events.get(&i) {
                    Some(EventState::Consumed { edge: taken }) => taken != edge,
                    Some(EventState::Failed { .. }) => true,
                    _ => false,
                },
            },
            _ => false,
        }
    }

    /// A dag's joins and skips (ADR-0054 §1): an `all` join is ready when every incoming edge fired
    /// or is dead; a node every incoming edge of which is dead is skipped, and the skip propagates.
    pub fn settle_joins(&mut self, at: LogIndex) {
        if self.def.kind != Kind::Dag {
            return;
        }
        loop {
            let mut changed = false;
            let names: Vec<String> = self.def.nodes.keys().cloned().collect();
            for n in names.iter().filter(|n| **n != self.def.root) {
                let ins: Vec<String> = self.def.in_edges(n).map(|(id, _)| id.clone()).collect();
                let pos = self.acts.iter().position(|a| &a.node == n);
                match pos {
                    None if !ins.is_empty() && ins.iter().all(|e| self.dead(e)) => {
                        self.acts.push(Activation {
                            node: n.clone(),
                            trig: None,
                            via: None,
                            fired: BTreeSet::new(),
                            status: ActStatus::Skipped,
                            hist: BTreeSet::new(),
                            created_at: at,
                            clear_inputs: Label::new(),
                            handle_inputs: Label::new(),
                            attrs: None,
                            found: false,
                            seal: None,
                            covered: false,
                        });
                        changed = true;
                    }
                    Some(j) if self.acts[j].status == ActStatus::Waiting => {
                        let a = &self.acts[j];
                        if ins.iter().all(|e| a.fired.contains(e) || self.dead(e)) {
                            self.acts[j].status = ActStatus::Ready;
                            changed = true;
                        }
                    }
                    _ => {}
                }
            }
            if !changed {
                break;
            }
        }
    }

    pub fn fail(&mut self, why: impl Into<String>) {
        if self.running() {
            self.status = RunStatus::Failed { why: why.into() };
        }
    }

    /// Completion and failure (ADR-0054 §9, ADR-0055 §8). Completion is checked first: it says the
    /// graph was traversed, and nothing about whether the work is right.
    pub fn settle(&mut self) {
        if !self.running() {
            return;
        }
        let ended = |a: &Activation| a.status == ActStatus::Ended;
        let sink_ended = self.acts.iter().any(|a| self.def.sinks.contains(&a.node) && ended(a));
        match self.def.kind {
            Kind::Dag => {
                let sinks_done = self.def.sinks.iter().all(|s| {
                    self.acts.iter().any(|a| &a.node == s && matches!(a.status, ActStatus::Ended | ActStatus::Skipped))
                });
                if sinks_done && sink_ended {
                    self.status = RunStatus::Completed;
                    return;
                }
                if let Some(a) = self.acts.iter().find(|a| matches!(a.status, ActStatus::Failed { .. })) {
                    let ActStatus::Failed { why } = &a.status else { unreachable!() };
                    let why = format!("node {} failed: {why}", a.node);
                    self.fail(why);
                    return;
                }
                if let Some((_, EventState::Failed { why })) =
                    self.events.iter().find(|(_, e)| matches!(e, EventState::Failed { .. }))
                {
                    let why = format!("a decision point failed: {why}");
                    self.fail(why);
                    return;
                }
            }
            Kind::Mesh => {
                if sink_ended {
                    self.status = RunStatus::Completed;
                    return;
                }
                if self.exhausted {
                    self.fail("the budget refused a grant (ADR-0055 §2)");
                    return;
                }
            }
        }
        // Quiescent: nothing ready, running or waiting, no decision event open or served.
        let busy = self
            .acts
            .iter()
            .any(|a| matches!(a.status, ActStatus::Ready | ActStatus::Running { .. } | ActStatus::Waiting));
        let deciding = self.events.values().any(|e| matches!(e, EventState::Open | EventState::Served { .. }));
        // An ended activation not yet covered may still fire an edge once its Observer catches up.
        let pending = self
            .acts
            .iter()
            .any(|a| a.status == ActStatus::Ended && !a.covered && self.def.out_edges(&a.node).next().is_some());
        if !busy && !deciding && !pending {
            self.fail("quiescent, and no sink has ended (ADR-0055 §8)");
        }
    }

    /// The budget, at a grant (ADR-0055 §2). `Err` refuses the grant and fails the workflow.
    pub fn charge(&mut self, node: &str) -> Result<(), String> {
        let Some(b) = &self.def.budget else { return Ok(()) };
        if self.charged >= b.n {
            self.exhausted = true;
            return Err(format!("the budget of {} leases is spent (ADR-0055 §2)", b.n));
        }
        if let Some(cap) = b.per_node.get(node)
            && self.charged_node.get(node).copied().unwrap_or(0) >= *cap
        {
            self.exhausted = true;
            return Err(format!("node {node}'s budget of {cap} leases is spent (ADR-0055 §2)"));
        }
        self.charged += 1;
        *self.charged_node.entry(node.to_string()).or_default() += 1;
        Ok(())
    }
}

/// The grant a workflow slot is entitled to: the seating's fields, the next round, and the task's
/// label joined with its clear inputs' (ADR-0054 §2, §5). The deciding replica builds it, and every
/// replica rebuilds it at apply and requires equality.
pub fn grant_for(s: &SeatingDef, round: Round, clear_inputs: &Label) -> GrantRequest {
    let mut label = s.task_label.clone();
    label.extend(clear_inputs.iter().cloned());
    GrantRequest {
        principal: s.principal.clone(),
        seat: s.seat.clone(),
        persona: s.persona.clone(),
        bundle: s.bundle.clone(),
        confinement: s.confinement.clone(),
        alphabet: s.alphabet.clone(),
        ttl_ms: s.ttl_ms,
        round,
        role: RoundRole::Author,
        task_label: Some(label),
        task_labels_allowed: None,
        sign_on: None,
    }
}

// ---- the state machine -----------------------------------------------------------------------

use crate::action::{Action, ActionRequest};
use crate::confine::Appraisal;
use crate::observer::Finding;
use crate::state::{Admitted, Applied, MechanismDeny, State};

impl State {
    /// `Entry::WorkflowLoad`: a workflow loads only from a promoted single-file workspace (ADR-0054
    /// §1, §2), and only if every load check passes. `outward` is what the deciding replica read from
    /// the bundle; it can only add to what the text declares.
    pub(crate) fn apply_workflow_load(&mut self, index: LogIndex, text: &str, outward: &BTreeSet<String>) -> Applied {
        let artifact = workflow_artifact(text.as_bytes());
        if !self.candidates.get(&artifact).is_some_and(|c| c.promoted_at.is_some()) {
            return Applied::Rejected("the workflow's artifact is not promoted (ADR-0054 §2)".into());
        }
        let def = match Definition::parse(text) {
            Ok(d) => d,
            Err(e) => return Applied::Rejected(e),
        };
        let rules = &self.rules;
        let bad = def.check(&|seat| rules.seats.get(seat).map(|d| (d.kind, d.domain, d.rung)));
        if !bad.is_empty() {
            return Applied::Rejected(format!("the workflow does not load: {}", bad.join("; ")));
        }
        if let Some(n) = outward.iter().find(|n| !def.nodes.contains_key(*n)) {
            return Applied::Rejected(format!("outward names {n}, which is not a node"));
        }
        let id = Digest::of(text.as_bytes());
        if self.workflows.contains_key(&id) {
            return Applied::Rejected("the workflow is already loaded".into());
        }
        let mut out: BTreeSet<String> = def.nodes.iter().filter(|(_, d)| d.outward).map(|(n, _)| n.clone()).collect();
        out.extend(outward.iter().cloned());
        let run = Run::new(def, artifact, index, self.epoch, self.rules.rules_epoch, out);
        self.workflows.insert(id.clone(), run);
        Applied::WorkflowLoaded { workflow: id }
    }

    /// The seating a slot is granted under, and the clear inputs its task's label joins.
    fn slot_seating(&self, wf: &Digest, slot: &Slot) -> Result<(SeatingDef, Label, String), String> {
        let run = self.workflows.get(wf).ok_or("no such workflow")?;
        match slot {
            Slot::Node(i) => {
                let a = run.acts.get(*i).ok_or("no such activation")?;
                Ok((run.def.nodes[&a.node].seating.clone(), a.clear_inputs.clone(), a.node.clone()))
            }
            Slot::Decision(_) => {
                let o = run.def.orchestrator.clone().ok_or("the workflow seats no orchestrator")?;
                Ok((o, Label::new(), "orchestrator".into()))
            }
        }
    }

    /// The grant a slot is entitled to now. The deciding replica proposes it; apply rebuilds it.
    pub fn workflow_grant_request(&self, wf: &Digest, slot: &Slot) -> Result<GrantRequest, String> {
        let (seating, clear, _) = self.slot_seating(wf, slot)?;
        let round = self.last_round.get(&seating.seat).map_or(1, |r| r + 1);
        Ok(grant_for(&seating, round, &clear))
    }

    /// The slots that are ready for a grant, in log order. What a replica's driver proposes; an
    /// entry for a slot that is no longer ready is refused at apply and changes nothing.
    pub fn workflow_ready(&self) -> Vec<(Digest, Slot)> {
        let mut out = Vec::new();
        for (id, run) in self.workflows.iter().filter(|(_, r)| r.running()) {
            for (i, a) in run.acts.iter().enumerate() {
                if a.status == ActStatus::Ready {
                    out.push((id.clone(), Slot::Node(i)));
                }
            }
            // Decision events are served in log order: the earliest open one, once no orchestrator
            // round of this workflow is live (ADR-0054 §3; a principal holds one live lease).
            let serving = run.events.values().any(|e| matches!(e, EventState::Served { .. }));
            if !serving && let Some((ev, _)) = run.events.iter().find(|(_, e)| **e == EventState::Open) {
                out.push((id.clone(), Slot::Decision(*ev)));
            }
        }
        out
    }

    /// `Entry::WorkflowGrant`. A slot that is not ready, or must wait, is refused and nothing
    /// changes. Otherwise the grant is made under the promotion; one refused by the budget or by any
    /// grant check fails the slot, and nothing stands in (ADR-0054 §2; ADR-0031 A4).
    pub(crate) fn apply_workflow_grant(
        &mut self,
        index: LogIndex,
        wf: &Digest,
        slot: &Slot,
        req: &GrantRequest,
        appraisal: Option<&Appraisal>,
    ) -> Applied {
        let Some(run) = self.workflows.get(wf) else { return Applied::Rejected("no such workflow".into()) };
        if !run.running() {
            return Applied::Rejected("the workflow is not running".into());
        }
        match slot {
            Slot::Node(i) if run.acts.get(*i).map(|a| &a.status) != Some(&ActStatus::Ready) => {
                return Applied::Rejected("the activation is not ready".into());
            }
            Slot::Decision(ev) => {
                if run.events.get(ev) != Some(&EventState::Open) {
                    return Applied::Rejected("the decision event is not open".into());
                }
                if run.events.iter().any(|(e, s)| e < ev && *s == EventState::Open) {
                    return Applied::Rejected("decision events are served in log order (ADR-0054 §3)".into());
                }
            }
            _ => {}
        }
        let (seating, _, node) = match self.slot_seating(wf, slot) {
            Ok(s) => s,
            Err(e) => return Applied::Rejected(e),
        };
        match self.workflow_grant_request(wf, slot) {
            Ok(want) if &want == req => {}
            _ => return Applied::Rejected("the grant is not the seating's (ADR-0054 §2)".into()),
        }
        // Waits, not failures: the seat holds a live lease (one per principal and seat; a node has
        // one live activation, ADR-0055 §3), or its last round is not yet read to the seal.
        if self.live_by_seat.contains_key(&seating.seat)
            || self
                .live_by_seat
                .values()
                .filter_map(|f| self.leases.get(f))
                .any(|r| r.lease.principal == seating.principal)
        {
            return Applied::Rejected(format!(
                "seat {} or its principal holds a live lease: the slot waits",
                seating.seat
            ));
        }
        if let Some(seal) = self.seals.get(&seating.seat)
            && !self.rules.cell_observers(&seating.seat).iter().any(|o| self.mark(o, &seal.topic) >= seal.seq)
        {
            return Applied::Rejected(format!(
                "seat {}'s last round is unread to its seal: the slot waits",
                seating.seat
            ));
        }
        let fail = |st: &mut State, why: String| {
            let run = st.workflows.get_mut(wf).expect("present");
            match slot {
                Slot::Node(i) => run.acts[*i].status = ActStatus::Failed { why: why.clone() },
                Slot::Decision(ev) => {
                    run.events.insert(*ev, EventState::Failed { why: why.clone() });
                }
            }
            st.workflow_advance(index);
            Applied::WorkflowFailed { reason: why }
        };
        // ADR-0024 A4: a rules-epoch change voids every lease the workflow has not yet issued, and a
        // fence fails it closed (ADR-0054 §9).
        if run.epoch != self.epoch || run.rules_epoch != self.rules.rules_epoch {
            return fail(self, "the epoch or rules epoch has moved since the promotion (ADR-0024 A4)".into());
        }
        let charge = self.workflows.get_mut(wf).expect("present").charge(&node);
        if let Err(why) = charge {
            return fail(self, why);
        }
        match self.apply_grant(index, req, appraisal) {
            Applied::LeaseGranted { fence } => {
                let run = self.workflows.get_mut(wf).expect("present");
                match slot {
                    Slot::Node(i) => run.acts[*i].status = ActStatus::Running { fence },
                    Slot::Decision(ev) => {
                        run.events.insert(*ev, EventState::Served { fence });
                    }
                }
                self.wf_bindings.insert(
                    fence,
                    Binding {
                        workflow: wf.clone(),
                        slot: slot.clone(),
                        actuates: 0,
                        reports: vec![],
                        outcome: None,
                        lifted: false,
                    },
                );
                Applied::LeaseGranted { fence }
            }
            Applied::Rejected(why) => fail(self, format!("the grant was refused: {why}")),
            other => other,
        }
    }

    /// The typed summary of an admitted request, with what the mechanism stamps on it: a route's
    /// workflow, event and basis, and a worker report's declared outcome (ADR-0054 §4, §8).
    pub fn admitted(&self, req: &ActionRequest, emergency: bool) -> Admitted {
        let mut a = Admitted::from_request(req, emergency);
        match (&mut a, self.wf_bindings.get(&req.lease)) {
            (Admitted::Route { stamp, .. }, Some(b)) => {
                if let Slot::Decision(ev) = b.slot {
                    *stamp = Some(RouteStamp { workflow: b.workflow.clone(), event: ev, basis: self.last_applied });
                }
            }
            (Admitted::Report { outcome, .. }, Some(b)) if matches!(b.slot, Slot::Node(_)) => {
                if let Action::Report { record } = &req.action {
                    *outcome = record.get("outcome").and_then(|v| v.as_str()).map(str::to_string);
                }
            }
            _ => {}
        }
        a
    }

    /// The mechanism checks a route needs, at decide and again at apply (ADR-0054 §8): the round is
    /// the one granted for the event the route names, the workflow running, the event not consumed,
    /// and the edge a chosen edge out of it and enabled. `Err` names why, as `Workflow.tla`'s `Why`.
    pub fn route_check(&self, fence: LogIndex, edge: &str, stamp: &RouteStamp) -> Result<(), String> {
        let b = self.wf_bindings.get(&fence).ok_or("lease")?;
        if b.workflow != stamp.workflow || b.slot != Slot::Decision(stamp.event) {
            return Err("lease".into());
        }
        let run = self.workflows.get(&stamp.workflow).ok_or("lease")?;
        if !run.running() {
            return Err("ended".into());
        }
        match run.events.get(&stamp.event) {
            Some(EventState::Served { fence: f }) if *f == fence => {}
            Some(EventState::Consumed { .. }) => return Err("consumed".into()),
            _ => return Err("closed".into()),
        }
        let e = run.def.edges.get(edge).ok_or("guard")?;
        if e.kind != EdgeKind::Chosen || e.from != run.acts[stamp.event].node {
            return Err("guard".into());
        }
        match run.disabled(stamp.event, edge) {
            None => Ok(()),
            Some(why) => Err(why.into()),
        }
    }

    /// Decide-time preconditions for workflow requests: a route's check, and a worker's outcome
    /// drawn from its node's closed enum.
    pub(crate) fn workflow_preconditions(&self, req: &ActionRequest) -> Result<(), MechanismDeny> {
        match &req.action {
            Action::Route { edge } => {
                let Admitted::Route { stamp: Some(stamp), .. } = self.admitted(req, false) else {
                    return Err(MechanismDeny::Other(
                        "a route is made only under an orchestrator's round (ADR-0054 §3)".into(),
                    ));
                };
                self.route_check(req.lease, edge, &stamp)
                    .map_err(|why| MechanismDeny::Other(format!("route not enabled: {why}")))
            }
            Action::Report { .. } => match (self.admitted(req, false), self.wf_bindings.get(&req.lease)) {
                (Admitted::Report { outcome: Some(o), .. }, Some(b)) => {
                    self.outcome_ok(b, &o).map_err(MechanismDeny::Other)
                }
                _ => Ok(()),
            },
            _ => Ok(()),
        }
    }

    fn outcome_ok(&self, b: &Binding, o: &str) -> Result<(), String> {
        let Slot::Node(i) = b.slot else { return Ok(()) };
        let run = &self.workflows[&b.workflow];
        let node = &run.def.nodes[&run.acts[i].node];
        if node.outcomes.contains(o) {
            Ok(())
        } else {
            Err(format!("outcome {o:?} is not in the node's enum (ADR-0054 §4)"))
        }
    }

    /// At apply, after the generic checks: a route re-checked, or void.
    pub(crate) fn workflow_admit_check(&self, fence: LogIndex, action: &Admitted) -> Result<(), String> {
        match action {
            Admitted::Route { edge, stamp } => {
                let stamp = stamp.as_ref().ok_or("a route carries no stamp")?;
                self.route_check(fence, edge, stamp).map_err(|why| format!("route void ({why}) (ADR-0054 §8)"))
            }
            Admitted::Report { outcome: Some(o), .. } => match self.wf_bindings.get(&fence) {
                Some(b) if matches!(b.slot, Slot::Node(_)) => self.outcome_ok(b, o),
                _ => Err("an outcome is reported only at a workflow node".into()),
            },
            _ => Ok(()),
        }
    }

    /// At apply, after an admit under a workflow lease is counted: a route consumes its event and
    /// enters its target, and ends the orchestrator's round; an outcome ends the worker's
    /// (ADR-0042 A3).
    pub(crate) fn workflow_admitted(&mut self, index: LogIndex, fence: LogIndex, action: &Admitted, seq: Option<u64>) {
        let Some(b) = self.wf_bindings.get_mut(&fence) else { return };
        match action {
            Admitted::Actuate { .. } => b.actuates += 1,
            Admitted::Report { outcome, .. } => {
                b.reports.extend(seq);
                if let Some(o) = outcome {
                    b.outcome = Some(o.clone());
                    self.end_lease(fence, EndReason::Outcome);
                }
            }
            Admitted::Route { edge, stamp: Some(stamp) } => {
                let run = self.workflows.get_mut(&stamp.workflow).expect("checked");
                run.events.insert(stamp.event, EventState::Consumed { edge: edge.clone() });
                run.enter(stamp.event, edge, index);
                self.end_lease(fence, EndReason::Routed);
            }
            _ => {}
        }
    }

    /// An Observer's finding against a round (ADR-0007; ADR-0054 §4's `found`): every activation run
    /// in that round is marked, and every edge out of its causal descendants closes.
    pub(crate) fn workflow_finding(&mut self, f: &Finding) {
        let hits: Vec<(Digest, usize)> = self
            .wf_bindings
            .iter()
            .filter_map(|(fence, b)| match b.slot {
                Slot::Node(i) => {
                    let rec = self.leases.get(fence)?;
                    (self.topic_of(rec).as_deref() == Some(f.topic.as_str())).then(|| (b.workflow.clone(), i))
                }
                Slot::Decision(_) => None,
            })
            .collect();
        for (wf, i) in hits {
            self.workflows.get_mut(&wf).expect("bound").acts[i].found = true;
        }
    }

    /// A finding names a round of a coupled seat in the Observer's reach, live or ended.
    pub(crate) fn check_finding(&self, seat: &str, f: &Finding) -> Result<(), MechanismDeny> {
        let bad = |s: &str| Err(MechanismDeny::Other(format!("bad finding: {s}")));
        if self.rules.seat_kind(seat) != Some(SeatKind::Observer) {
            return bad("only an observer seat makes a finding");
        }
        let Some(rec) = self.leases.values().find(|r| self.topic_of(r).as_deref() == Some(f.topic.as_str())) else {
            return bad("names no round");
        };
        if !self.rules.watches(seat, &rec.lease.seat) {
            return bad("the round is outside this observer's reach");
        }
        Ok(())
    }

    /// After every apply: lift the ends of workflow leases, then let each running workflow move as
    /// far as the state allows, deterministically and in one step, so every replica agrees.
    pub(crate) fn workflow_advance(&mut self, index: LogIndex) {
        // 1. Lift: a workflow lease that has ended since the last apply.
        let ended: Vec<LogIndex> = self
            .wf_bindings
            .iter()
            .filter(|(f, b)| !b.lifted && self.leases.get(f).is_some_and(|r| !r.live()))
            .map(|(f, _)| *f)
            .collect();
        for fence in ended {
            let rec = self.leases[&fence].clone();
            let seal = self.topic_of(&rec).map(|topic| Seal { topic, seq: rec.seq });
            let b = self.wf_bindings.get_mut(&fence).expect("present");
            b.lifted = true;
            let b = b.clone();
            let reason = rec.ended.expect("ended");
            let run = self.workflows.get_mut(&b.workflow).expect("bound");
            match b.slot {
                Slot::Node(i) => {
                    let end = EndKind::of(reason);
                    let a = &mut run.acts[i];
                    a.seal = seal;
                    if matches!(end, EndKind::Fenced | EndKind::Revoked) {
                        a.status = ActStatus::Failed { why: format!("its round ended {reason:?}") };
                    } else {
                        a.status = ActStatus::Ended;
                        a.attrs = Some(Attributes {
                            end,
                            actuates: b.actuates,
                            denials: 0,
                            label: rec.labels.clear_set.clone(),
                            outcome: b.outcome.clone(),
                            output: b.reports.clone(),
                        });
                        if run.def.has_chosen(&a.node) {
                            run.events.insert(i, EventState::Open);
                        }
                    }
                }
                // ADR-0054 §8: a lapsed orchestrator fails its decision point and takes no edge.
                Slot::Decision(ev) => {
                    if run.events.get(&ev) == Some(&EventState::Served { fence }) {
                        run.events.insert(
                            ev,
                            EventState::Failed { why: format!("its orchestrator's round ended {reason:?}") },
                        );
                    }
                }
            }
        }
        let ids: Vec<Digest> = self.workflows.iter().filter(|(_, r)| r.running()).map(|(id, _)| id.clone()).collect();
        for id in ids {
            // 2. The fence: what the workflow has not yet issued is void (ADR-0024 A4, ADR-0054 §9).
            let moved = {
                let run = &self.workflows[&id];
                run.epoch != self.epoch || run.rules_epoch != self.rules.rules_epoch
            };
            if moved {
                let run = self.workflows.get_mut(&id).expect("present");
                for a in run.acts.iter_mut().filter(|a| matches!(a.status, ActStatus::Ready | ActStatus::Waiting)) {
                    a.status = ActStatus::Failed { why: "fenced before its grant".into() };
                }
                run.fail("the epoch or rules epoch moved (ADR-0054 §9)");
                continue;
            }
            // 3. Coverage at the edge (ADR-0039 A3, ADR-0054 §7).
            let mut covered = Vec::new();
            {
                let run = &self.workflows[&id];
                for (i, a) in run.acts.iter().enumerate() {
                    if a.status == ActStatus::Ended
                        && !a.covered
                        && let Some(seal) = &a.seal
                    {
                        let seat = &run.def.nodes[&a.node].seating.seat;
                        if self.rules.cell_observers(seat).iter().any(|o| self.mark(o, &seal.topic) >= seal.seq) {
                            covered.push(i);
                        }
                    }
                }
            }
            let run = self.workflows.get_mut(&id).expect("present");
            for i in covered {
                run.acts[i].covered = true;
            }
            // 4. Computed edges, each evaluated once, when its source has ended and is covered.
            loop {
                let mut fire = None;
                'find: for (i, a) in run.acts.iter().enumerate() {
                    if a.status != ActStatus::Ended || !a.covered {
                        continue;
                    }
                    for (eid, e) in run.def.out_edges(&a.node) {
                        if e.kind == EdgeKind::Computed && !run.evaluated.contains(&(i, eid.clone())) {
                            fire = Some((i, eid.clone()));
                            break 'find;
                        }
                    }
                }
                let Some((i, eid)) = fire else { break };
                run.evaluated.insert((i, eid.clone()));
                if run.disabled(i, &eid).is_none() {
                    run.enter(i, &eid, index);
                }
            }
            // 5. A decision event no orchestrator round holds, with no chosen edge left enabled,
            // fails (ADR-0054 §8). Once its source is covered a chosen edge can only become disabled,
            // by a finding. An event a round holds stays open while the round is live, and fails
            // when it ends: "the orchestrator may route again while its lease is live".
            let dead: Vec<usize> = run
                .events
                .iter()
                .filter(|(ev, s)| {
                    **s == EventState::Open
                        && run.acts[**ev].covered
                        && run
                            .def
                            .out_edges(&run.acts[**ev].node)
                            .filter(|(_, e)| e.kind == EdgeKind::Chosen)
                            .all(|(eid, _)| run.disabled(**ev, eid).is_some())
                })
                .map(|(ev, _)| *ev)
                .collect();
            for ev in dead {
                run.events.insert(ev, EventState::Failed { why: "no chosen edge is enabled".into() });
            }
            // 6. Joins and skips, then completion and failure.
            run.settle_joins(index);
            run.settle();
        }
    }
}
