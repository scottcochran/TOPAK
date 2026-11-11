# Self review of 2026.11.11: reader H's findings in full

Reader H read the specification graph. Annex to `derived/topak-open-findings-register-2026.11.11.md`, Part III. Each block is the finding as the reader wrote it, against the tree at `bbda621`, followed by the verdict of a verifier that did not find it. Paths are relative to the repository root. A path a finding names as absent is written without backticks. Nothing here is ratified, and every reader and verifier is of the same model lineage as the drafter of the corpus.

26 reported: 17 confirmed, 9 confirmed with a correction, 0 dropped.

### H-1: The graph and its results are behind the tree at bbda621: sixteen .tla files are not nodes, and the checker's own sync-script comparison no longer agrees
- Against: decisions/ADR-0057.md:261-274 (and spec/specification-graph.py:1000-1004, spec/specification-graph.json:5, spec/specification-graph-results-2026.11.07.txt:93-94 and :199)
- Basis: Proposed
- Claim: "**The graph is built for the corpus** at a named commit: every clause the reference follows, every module and proof module" and "the 31 modules and 24 proof modules" and "**Met** ⟨R1⟩: `spec/specification-graph-results-2026.11.07.txt` (`df1433d8a5f3bd6d`), byte for byte on a rerun."
- Why wrong: `ls spec/*.tla | grep -v _proof | wc -l` gives 39 and `ls spec/*_proof.tla | wc -l` gives 32. The graph has 31 and 24: `Alone`, `Federation`, `Intent`, `Membership`, `Outstanding`, `Peer`, `PlaneClock`, `Release` and their eight proof modules (results files dated 2026.11.10) are in the tree and are not nodes (my comparison of `spec/*.tla` with the JSON's node ids: 16 missing, none extra). The checker's fourth list is the tree's glob, not a stored list: `proofs = {rel(p) for p in glob.glob(os.path.join(HERE, "*_proof.tla"))}` then `if proofs != tl: ok = False` (spec/specification-graph.py:1000-1004); a list that disagrees is appended to `fail` (py:1182-1183) and the run ends `"FAILED: "` with exit 1 (py:1231-1234). On this tree that comparison is 32 against 24, so the committed lines "- the sync scripts: agrees" / "spec/proof-sync.sh: its 24 proof modules are the 24 TLAPS edges' lower ends" (results:93-94) and "Result: graph well formed, the four lists agree" (results:199) are not what a rerun gives. "13 of 31" modules with no binding row (results:76) and "all 31 modules" (ADR-0057:390) count the same stale node set; the binding names none of the eight new modules (`grep -c` gives 0 in both binding files). The JSON still says `"at": "9749dfa + working tree"` (json:5), so the build that "keeps every pin and records the commit" (ADR-0057:265-266) has not been made, and on this tree it could not leave the graph at 419 nodes. I did not run the checker; this is read from its code and from the tree.
- Fix belongs in: spec/specification-graph.json and a new results file; ADR-0057 §14, finding 10, Open obligations and History
- Severity: Medium-High
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** `ls spec/*.tla | grep -v _proof | wc -l` = 39 and `ls spec/*_proof.tla | wc -l` = 32; graph node ids against spec/*.tla: 31 modules and 24 proof modules, 16 files missing (Alone, Federation, Intent, Membership, Outstanding, Peer, PlaneClock, Release and their proof modules), none extra. spec/specification-graph.py:353 (nodes from the glob), :1000-1004, :1183, :1232-1234; spec/specification-graph-results-2026.11.07.txt:76, :93-94, :199; decisions/ADR-0057.md:261-274, :390; spec/specification-graph.json:5. `grep -c` for each of the eight module names in theorem-premise-binding.md and .json = 0. `grep -n -i 'specification.graph\|ADR-0057' decisions/ADR-0059.md decisions/ADR-006*.md` empty, so nothing later acknowledges it. Checker not run (brief); the FAILED outcome is read from its code, as the finding says.

### H-2: ADR-0059 to ADR-0068 take "overlay" from ADR-0058 as a deployment position for records that hold capabilities the archetype lacks; ADR-0058 defines no such thing and says the admission test is unchanged
- Against: decisions/ADR-0058.md:52-53, :101, :183 (and decisions/ADR-0059.md:19-20, :133-135, :148; decisions/ADR-0060.md:104, :151; decisions/ADR-0068.md:19-22, :169-171; decisions/ADR-0023.md:39; ADOPTERS_GUIDE_README.md:84-85)
- Basis: Proposed
- Claim: "**Deployment position:** **An overlay, not the archetype** ⟨Q11⟩. Under ADR-0058 (Proposed) a deployment adds the nodes this record describes and reports them upstream (§8)." and "**This record is therefore drafted as an overlay's**, and these are reported upstream under ADR-0058 §6" and "**ADR-0058 is ratified**, or the custodian takes this record into the archetype by the route §8 names." (all ADR-0059)
- Why wrong: ADR-0058 defines the word at :52-53: "**A deployment's graph is an overlay**: for each archetype node, one of four operations, and for each edge, a type." Its nodes are artifacts; its `Add` examples are "a tool's schema, a deployment's own policy, a runtime monitor" (ADR-0058:59); and its §5 is headed "A deployment may grade above the archetype, and the admission test is unchanged" (ADR-0058:101). The test it leaves unchanged is in force: "If it holds a capability `A` lacks, it is not a demotion: `A` is incomplete and must be extended before the variation is admitted." (ADR-0023:39), and the Guide restates it as "Report it; do not declare it as a variation." (ADOPTERS_GUIDE_README.md:85). So ratifying ADR-0058 would not make a record with new capabilities admissible as "an overlay", which is what ADR-0059:148 conditions on. None of the ten records states an edge, an edge type or a grade (`grep -n -i "grade\b\|graded\|edge type"` over ADR-0059 to ADR-0068 returns nothing; no overlay file exists under `spec/`). The seven "Reported under ADR-0058 §6" lines (ADR-0060:151, 0061:121, 0062:185, 0063:126, 0064:123, 0065:118, 0066:98) report capabilities, which are not among the four things §6 adds: "a route stronger than the archetype's (§5); a method with no row (§3); a node it had to add that every deployment of its kind will need, a schema above all (ADR-0057 §9); and an edge it could not re-establish because the archetype node was underspecified" (ADR-0058:113-115). ADR-0068 adds twelve trusted-base rows as "the overlay's declaration of what it trusts and assumes" (ADR-0068:19-20), where ADR-0058:183 says "**No row is added by this record.** A method a deployment brings enters by §3, as a D-row."; ADR-0068:170 concedes "An overlay that adds twelve is outside that sentence" and still lists "ADR-0058 (overlays; Proposed)" under Depends on (ADR-0068:22). ADR-0060:104 says "It omits Build, the people and Kafka. A deployment declares that under ADR-0058.", where ADR-0058's `Omit` is an operation on a graph node and a degeneracy is declared under ADR-0023 §6. ADR-0058 has no History row for the new use. A reader cannot tell what ratifying an "overlay" record would put in force.
- Fix belongs in: ADR-0059 to ADR-0068 (Deployment position, Depends on, the "Reported under" sections, ADR-0059 §9), or ADR-0058 if it is meant to define a position for records; decisions/README.md rows 72-81 repeat the phrase
- Severity: Medium-High
- Confidence: high
- Already on the corpus's own lists: no (ADR-0068 finding 2 notes the row sentence only)
- **Verifier:** confirmed with correction
- **Verifier's correction:** One limb overstated. ADR-0058 §6 opens by recalling the capability report (ADR-0058:112-113: "The Adopter's Guide already says, of a variation that holds a capability the archetype lacks: 'the archetype is incomplete. Report it.' **A deployment also reports**: ..."), so the seven "Reported under ADR-0058 §6" lines are a loose citation of a section that recalls that report without owning it (the rule is ADR-0023 §4 and Guide §2.1), not reports §6 excludes. Also say that ADR-0059 §8 itself recites ADR-0023 §4 ("is not a rung", ADR-0059:133-134) and that ⟨Q11⟩ records "Overlay first, reported upstream" (ADR-0059:225): the records do not ignore the admission test; the gap is that ADR-0058 defines an overlay as a deployment's graph and defines no position for a record, so ADR-0059:148 conditions on something ADR-0058 would not put in force. The rest stands.
- **Verifier's evidence:** decisions/ADR-0058.md:52-53, :59, :101, :112-116, :183, :259-261 (History: initial row only); decisions/ADR-0059.md:19-20, :131-135, :148, :225; decisions/ADR-0060.md:104, :151; ADR-0061:121, ADR-0062:185, ADR-0063:126, ADR-0064:123, ADR-0065:118, ADR-0066:98; decisions/ADR-0068.md:19-22, :169-171; decisions/ADR-0023.md:39; ADOPTERS_GUIDE_README.md:84-85; decisions/README.md:72-81 (10 rows). `grep -n -i "grade\b\|graded\|edge type" decisions/ADR-0059.md decisions/ADR-006[0-8].md` empty; `find . -iname '*overlay*'` finds only diagrams.

### H-3: ADR-0058 §9 states the reference's grades as read on 2026.11.06; ADR-0057's checker computed different ones the next day, and the Seats sentence contradicts itself
- Against: decisions/ADR-0058.md:156, :162-164 (and spec/specification-graph-results-2026.11.07.txt:23, :76-77, :109, :134-135, :151, :196; decisions/ADR-0057.md:372-373)
- Basis: Proposed
- Claim: "Read at grades: every floor theorem the stage carries is inherited at *executed*; the two `Seats` theorems at *proved of a reading* until `mechanism/lean` is brought into step, and at *replayed* or *trusted* while it is not; the operator theorems at *tested*; every other mechanism theorem at *trusted*."
- Why wrong: The computed inventory has nothing above *trusted*: "held at each grade: executed 0 · generated 0 · proved 0 · proved of a reading 0 · replayed 0 · tested 0 · read 0 · trusted 19" (results:109; 38 at :154). The floor gates are "void at every grade: routing-checked" for Annex B as declared (results:151) and *trusted* in the other declaration (results:196); ADR-0057 says so itself: "Counted, the executed edge would grade the floor gates *executed*, where they now grade *trusted*" (ADR-0057:372-373). There is no operator theorem to grade: `Operators` is among the "Modules no theorem in the binding is checked in" (results:76-77). The two `Seats` theorems grade *trusted* (results:134-135), and their Lean route includes `model-faithful(apply/Seats)`, the premise of a *replayed* edge (spec/specification-graph.json:11187-11192), so by ADR-0057 §5's "the strongest of each route's weakest edge" (ADR-0057:172-173) they could reach *replayed* at most, never *proved of a reading*. The sentence also gives two grades for one period: "until `mechanism/lean` is brought into step" and "while it is not" both describe the stale state. In the table, the `FloorComposition` row's freshness is "as of `mechanism/lean`" (ADR-0058:156) while the `Seats` row is "**stale**"; the checker reports both edges stale for the same files (results:23, :29).
- Fix belongs in: ADR-0058 §9 and its History; which edge carries a floor theorem is ADR-0057's to settle (H-4)
- Severity: Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0058.md:149-150 ("read and not computed"), :156-157, :162-164; spec/specification-graph-results-2026.11.07.txt:23, :29, :76-77 (Operators), :109 and :154 (nothing above trusted), :134-135, :151, :196; decisions/ADR-0057.md:170-173, :372-373; graph edge `replayed: mechanism/crates/topak-core → mechanism/lean/Topak/SeatsModel.lean` has premise model-faithful(apply/Seats) (json:10328), and refines(Seats)'s Lean route names it (json:11187-11192). `grep -n -i operator spec/theorem-premise-binding.md` finds no operator theorem. The two-grades-for-one-period reading of "until ... and ... while it is not" holds on the words.

### H-4: §4 and §5 define a route as any chain of edges from the code to the node a theorem is stated at; the graph holds fresh tested and replayed edges of that shape and counts none of them
- Against: decisions/ADR-0057.md:161-163, :180-182, :368-371 (and spec/specification-graph.json:10397, :10415, :10447, :10511, :11247-11251; spec/specification-graph.py:666-670, :685-688)
- Basis: Proposed
- Claim: "**T-0045-28 becomes a derived premise for every theorem whose route reaches the code**: the row, or any route of edges from the implementation to the module. Today the row is the only route for every theorem but the two of `Seats`, so no verdict moves." and finding 8: "**Two edges reach the code and are not counted as routes**"
- Why wrong: The graph has nine *tested* and four *replayed* edges whose lower end is `mechanism/crates/topak-core`. Six of them end at nodes where binding theorems are stated: `tested: mechanism/crates/topak-core → spec/FloorComposition.tla` (json:10447), `→ spec/RulesFloorNV_rev5.tla` (json:10511), `→ spec/Confinement.tla` (json:10415), `→ floor/proposed/workflow-floor.cedar` (json:10397, where `STATED_AT` puts "floor gates", py:92), and `replayed: … → spec/ConfinementRefinement.tla` and `→ spec/Mechanism.tla` (json:10350, :10374, where `TraceMatches` is stated). None carries `"route": false` (four other edges do: json:3109, :3218, :3262, :3306), and none is in any derived premise: `reaches-code(spec/RulesFloorNV_rev5.tla)` has the single route `edge(trusted, mechanism → spec/RulesFloorNV_rev5.tla)` (json:11247-11251), because `re_express` wires only the trusted edge and the `Seats` Lean route (py:666-670, :685-688). Under §5's own rule, "Its grade is taken over the edges from the layer it is stated at to the layer that runs: from a module to the code for a mechanism theorem, from a floor stage to the engine for a floor theorem" (ADR-0057:180-182), `P3_AuthorNotCounted` would grade *tested* and the floor gates *executed*; the results grade both *trusted* (results:123, :196). Finding 8 names two uncounted edges; the graph has six more. That the tested and replayed edges are not routes is a choice made in the builder which the Decision text does not state, and ADR-0058 §9 reads the text the other way ("the operator theorems at *tested*", ADR-0058:164). If tested edges were routes, the fourth declaration of `premise-routes.sh` (T-0045-28 excluded) would hold more than two theorems and "no verdict moves" would fail; the record has to say which it is.
- Fix belongs in: ADR-0057 §4, §5 and finding 8 (which edges are routes, and why the tested and replayed ones are not); ADR-0058 §9 and ADR-0045 A5 follow
- Severity: Medium
- Confidence: high
- Already on the corpus's own lists: no (finding 8 raises two of the edges only)
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0057.md:161-163, :180-182, :368-374; spec/specification-graph.json: 9 tested and 4 replayed edges from mechanism/crates/topak-core (ids at :10304-10527), six ending at reaches-code targets (:10350, :10374, :10397, :10415, :10447, :10511); "route": false on four edges only (:3109, :3218, :3262, :3306); no `edge(tested` or `edge(replayed` string in the binding section (python count: False, False); spec/specification-graph.py:88-94, :666-670, :680-688; results:123, :196; decisions/ADR-0058.md:163-164. `grep -n -i route decisions/ADR-0057.md` shows no sentence saying why tested or replayed edges are not routes.

### H-5: A tested edge is "fresh" with no evidence that any test ran or passed, and it does not go stale when the code under test changes
- Against: decisions/ADR-0057.md:136, :203-204 (and spec/specification-graph.py:556-557, :835-838; spec/specification-graph.json:10511-10524)
- Basis: Proposed
- Claim: "| **tested** | Passes tests named after the higher's properties |" and "each edge with its pins and its evidence by digest"
- Why wrong: `rule_tested` builds each tested edge from the `//!` header of a test file and pins two things, the test source and the module: `self.edge("tested", f"mechanism/crates/{c}", m, {t: d16(t), m: d16(m)},` with `evidence={"tests": t}` (py:556-557). The edge `tested: mechanism/crates/topak-core → spec/RulesFloorNV_rev5.tla` pins `mechanism/crates/topak-core/tests/mutations.rs` and the module, and its evidence is `"tests": "mechanism/crates/topak-core/tests/mutations.rs"` (json:10517-10523): a path, with no results file and no verdict. In evaluation such a premise is `v, x = True, a` whenever its pins match (py:835-838). So the type defined as "Passes tests" is true while the test file and the module are unchanged, whether or not the tests pass, and a change to `control.rs` or `state.rs` leaves it fresh. Finding 9(a) says "An edge with a results file pins what the file records, so a change to the code does make it stale." (ADR-0057:378-379); tested edges have no results file and are not mentioned there. The checker's line "entries C1 to C9, for the decision  ~  control.rs ControlFacts::permitted, restated at apply: tested (fresh)" (results:72) therefore says less than it reads as.
- Fix belongs in: spec/specification-graph.py (`rule_tested`) and ADR-0057 §3 or finding 9(a)
- Severity: Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** spec/specification-graph.py:542-557 (pins are the test file and the module, evidence a path), :789-801, :833-838; spec/specification-graph.json:10511-10524; decisions/ADR-0057.md:136, :148 ("It pins the content of both ends"), :155-156 (value is freshness "and, where the type has a results file, that file's verdict"), :375-379 (9(a) excepts read and trusted edges only), :203-204; results:72. §4's results-file clause discloses the mechanism but does not reconcile it with "Passes tests".

### H-6: Two of the four generated edges pin files that are git-ignored and absent from the tree, so the committed results cannot be reproduced from a checkout
- Against: spec/specification-graph.json:3124, :3156 (and floor/proposed/.gitignore:2; decisions/ADR-0057.md:271, :274; spec/specification-graph.py:117-121, :518-519, :794-801)
- Basis: evidence
- Claim: "Built again with every pin taken afresh, the graph is the same file." and "byte for byte on a rerun" (ADR-0057) and "== Stale edges (§3, §8): 8 of 435" (results:9)
- Why wrong: The graph pins `"floor/proposed/control-tests.json": "4247f94588f550f1"` and `"floor/proposed/labels-tests.json": "9877990b5ebeb101"`. floor/proposed/.gitignore has `*-tests.json` (line 2) with exceptions only for `emergency-tests.json` and `workflow-tests.json` (lines 5-6); `ls floor/proposed` in this copy shows neither file; and floor/proposed/README.md:34 says of the stage test files "the other two are not (about 2 MB)". The checker computes a missing file's digest as `None` (py:117-121) and gives `f"{k} {v} -> {now or 'gone'}"` as a reason for staleness (py:794-801). On a checkout of any commit the `control` and `labels` generated edges are therefore stale and the count is ten, not eight; and `build --repin-all` would write `null` for both pins (py:518-519), not the same file. The two claims hold only on a working tree where `floor/proposed/build.py` has been run first, which neither the record nor the results header says. The count of ten is inferred from the code, not run.
- Fix belongs in: spec/specification-graph.py (`rule_floor`: what a generated edge pins) and the graph; or ADR-0057 §14 states the precondition
- Severity: Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** `ls floor/proposed` shows emergency-tests.json and workflow-tests.json only; floor/proposed/.gitignore:2, :5-6; floor/proposed/README.md:34; spec/specification-graph.json:3124, :3156; spec/specification-graph.py:117-121, :518-519, :789-801; decisions/ADR-0057.md:271, :274; results:9. `grep -n 'tests.json\|build.py'` over ADR-0057 and the results file gives ADR-0057:132 only, and spec/README.md:245-254 states no precondition. The count of ten is inferred from the code, as the finding says; not run.

### H-7: The type proved is given to relations whose own evidence calls them a test, or whose upper end is prose
- Against: decisions/ADR-0057.md:133, :385-386 (and decisions/ADR-0053.md:255-256; spec/lean/GraphCheck-results-2026.10.07.txt:5; spec/specification-graph.json:3974, :4596; spec/theorem-premise-binding.md:126)
- Basis: Proposed
- Claim: "| **proved** | Is related to the higher by a machine-checked proof between two formal artifacts: implication, refinement, or equal state graphs | The prover or kernel (a row) | Proof modules to their modules (T-0045-31); the graph check of the `Seats`, `FloorComposition` and `Emergency` encodings (T-0045-37) |"
- Why wrong: (a) The accepted record says of the graph check "The mirrors are proved; the evaluation, the dump and its parse are a test." (ADR-0053:255-256), and both results files say "this run evaluates them on the graphs, a test" (GraphCheck-results-2026.10.07.txt:5; GraphCheckEmergency-results-2026.10.07.txt:5), the second at one instance ("Emergency and Emergency_live at MaxRound = 2"). The builder's `leaves` for these edges is "T-0045-37 and TLC: equal state graphs on the checked instance, under every Mut" (py:439), which is more than "The prover or kernel". An evaluation the corpus calls a test is typed three places above *tested*, and it carries `enc-faithful(Seats)` and `enc-faithful(FloorComposition)`. (b) Five edges `proved: <floor stage> → ADR-0030 §5` (json:3974 for the linked stage; row T-0045-14) have a record's clause as upper end, which is not a formal artifact. The same table gives "the floor gates' case suites" as an example of *tested* (ADR-0057:136), and the graph has no tested edge for any stage's suite: all nine tested edges start at `topak-core`. (c) `model-faithful(apply/Seats)` is in the binding a "condition, declared by the deployment" whose "trace replay is evidence, a test over the suites' traces" (theorem-premise-binding.md:126); the graph carries it on a *replayed* edge, while the eleven `enc-faithful(M)` conditions are carried on *read* edges (ADR-0057:292-294). The corpus keeps *checked*, *proved*, *certified* and *proved in Lean* apart; this one edge type covers TLAPS proofs, Lean proofs of a generated floor model, the gates' solver and folding verdicts, and a state-graph comparison.
- Fix belongs in: ADR-0057 §3's table and finding 9(d); spec/specification-graph.py (`rule_spec_lean`, `rule_floor`)
- Severity: Medium
- Confidence: medium
- Already on the corpus's own lists: no
- **Verifier:** confirmed with correction
- **Verifier's correction:** (a) is partly on the record's own list: finding 9(d) says "The graph check is *proved*, as §3's table has it" as a drafter's choice (ADR-0057:385-386); what it does not reconcile is ADR-0053:255-256 and both results headers calling the evaluation "a test". (c) is an asymmetry and not a contradiction: the pending ADR-0053 A1 itself puts `model-faithful(apply/Seats)` on the replay's edge (ADR-0053:288-290; ADR-0057:292-294). (a) and (b) stand as written.
- **Verifier's evidence:** decisions/ADR-0057.md:133, :136, :385-386; decisions/ADR-0053.md:255-256; spec/lean/GraphCheck-results-2026.10.07.txt:5; spec/lean/GraphCheckEmergency-results-2026.10.07.txt:5; spec/specification-graph.py:438-441; graph: 36 proved edges = 24 TLAPS + 4 graph-check + 3 floor/lean + 5 `<floor> → ADR-0030 §5` on T-0045-14 (json:3974 among them); all 9 tested edges start at topak-core; 11 read edges carry enc-faithful(M); spec/theorem-premise-binding.md:126; REVIEWERS_GUIDE_README.md:233-234 (the vocabulary kept apart).

### H-8: The exhaustiveness claim that earns C2 is not what the graph holds: no Rego policy is a node, and five of the ten layers are empty
- Against: decisions/ADR-0057.md:19-21, :79-80, :85-98 (and spec/specification-graph-results-2026.11.07.txt:4; spec/specification-graph.py:359-368; policies/actuate.rego:4; decisions/ADR-0033.md:959)
- Basis: Proposed
- Claim: "§3 claims that every relation between two specification artifacts the corpus relies on is an edge of the graph, which is an exhaustiveness claim" and "a record's clause, a module, a proof module, a Lean file, a floor stage, a Rego policy, a crate or a function in it, a schema" and "The corpus starts with the layers it has"
- Why wrong: "Layers: intent 0 · vocabulary 0 · record 325 · assurance 4 · model 69 · interface 0 · policy 6 · implementation 15 · runtime 0 · deployment 0" (results:4). The policy layer's row is "`floor/` and its stages; `policies/`" (ADR-0057:95), and the six policy nodes are all under `floor/`; the builder has ten rules (py:359-368) and none reads `policies/`. The Rego files are written against records, for example "# A bundle can only narrow (ADR-0030 §1)." (policies/actuate.rego:4), and the reference's cuts measure them ("`mechanism/` and `policies/` at commit `749d54f`", ADR-0033:959), so a relation the corpus relies on has no edge. The floor's schema files are pinned inside edges and are not nodes, though §1 lists "a schema" and puts Schema S in the interface layer; the narrative, the glossary, the checkpoint, the residual-risk statement and the recorded traces, each named in the layer table, have no node. §3 itself (ADR-0057:124-150) does not contain the exhaustiveness sentence the Status note attributes to it, and §14's first condition lists a narrower set. A C2 reviewer cannot tell which claim is to be confirmed.
- Fix belongs in: ADR-0057 Status note and §1 (what the claim is), and the builder if `policies/` is meant to be in the graph
- Severity: Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed with correction
- **Verifier's correction:** Part of the interface limb is answered by the record: §9 says "A format gains an interface node, with a machine-readable schema, when a record next touches it" *(drafter's choice: not a sweep)* (ADR-0057:213-219), so absent format schemas are by stated design; cite §9 and keep only Schema S, an existing file that §1's table lists and the graph does not hold. The Rego limb, the five empty layers and the absence of the exhaustiveness sentence from §3 stand.
- **Verifier's evidence:** decisions/ADR-0057.md:19-21, :79-81, :85-98, :124-150, :213-219, :261-262; `grep -n -i 'every relation\|exhausti' decisions/ADR-0057.md` gives :19-20 only; results:4; spec/specification-graph.py:359-368 (ten rules), `grep -n 'policies\|rego'` in it gives :81 (a layer label) only; policy-layer nodes are the six under floor/; no node id contains schema, narrative or polic; policies/actuate.rego:4; decisions/ADR-0033.md:959.

### H-9: §3 says a trusted relation "Has no edge"; the graph holds 21 trusted edges whose edge premises carry every theorem; the degeneracy rows then falsify every edge premise while voiding nothing
- Against: decisions/ADR-0057.md:138, :157, :249 and decisions/ADR-0058.md:176 (and spec/specification-graph.json:11247-11251; decisions/ADR-0057.md:269-270, :287)
- Basis: Proposed
- Claim: "| **D-0057-1** | Declaration | The graph: kept → not kept | Every `edge(…)` premise | None at grade *trusted*; every theorem's grade above *trusted* is unknown | None |"
- Why wrong: §3 has "| **trusted** | Has no edge; a row stands where the edge would be |" (ADR-0057:138). §14 counts "trusted 21" among the 435 edges (ADR-0057:269-270), and in the graph every theorem's T-0045-28 is replaced by a derived premise whose row route is an edge premise: `"reaches-code(spec/RulesFloorNV_rev5.tla)"` has `"any_of"` of one route, `"edge(trusted, mechanism → spec/RulesFloorNV_rev5.tla)"` (json:11247-11251). §4 says "An absent edge's premise is false" (ADR-0057:157), and §14 reports "Trusted edges on an undeclared row void all 19." (ADR-0057:287). With the graph's binding, D-0057-1's "Every `edge(…)` premise" falsified voids every theorem at grade *trusted*, not "None". The sentence under the table, "has the inventory it has today", is true only of the binding without the graph's re-expression, which the row does not say. D-0058-1 (ADR-0058:176) repeats the pattern for "Every `edge(…)` premise the deployment's own nodes would carry": the trusted edges start at the deployment's own `mechanism` node. A trusted edge also pins its upper end and can go stale (finding 9(a)), which a row cannot.
- Fix belongs in: ADR-0057 §3 (whether trusted is an edge) and §12; ADR-0058 §10
- Severity: Low-Medium
- Confidence: medium
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0057.md:138, :157, :249-251, :269-270, :287, :375-378; decisions/ADR-0058.md:176-179; graph: 21 trusted edges, all from the node `mechanism`; 23 reaches-code(...) derived premises each with the one route `edge(trusted, mechanism → ...)` (json:11247-11251); spec/specification-graph.py:623-639, :680-688, :833-834.

### H-10: "Six controls … move what they should" has no artifact, and the paragraph describes five
- Against: decisions/ADR-0057.md:284-287
- Basis: Proposed
- Claim: "Six controls, each run on an in-memory copy of the graph, move what they should. A pinned module with no read edge makes the pin file disagree, and a `lean-sync.sh` series with no edge makes the sync scripts disagree. A stale TLAPS edge moves the two `Seats` theorems to the Lean route, and a stale graph check with it voids them. Trusted edges on an undeclared row void all 19."
- Why wrong: `grep -rn -i "six controls\|in-memory copy" .` over the whole copy returns decisions/ADR-0057.md:284 only. spec/specification-graph.py has two commands, `build` and `check` (py:1237-1244), and no control; the results file's sections are at lines 7, 9, 52, 70, 76, 79, 83, 98 and 107 and none is a control. The paragraph sits inside a **Met** statement of a ratification condition, and nothing in the tree lets a reader rerun it. It lists five controls (pin file, sync scripts, stale TLAPS edge, stale graph check, undeclared row), not six. Every TLA+ module in `spec/` records its mutations in a rows file; this checker records none.
- Fix belongs in: spec/specification-graph.py and a results file that records the controls; or ADR-0057 §14
- Severity: Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed with correction
- **Verifier's correction:** The closing comparison is misstated: spec/ has 17 `*-rows*` files for 39 modules, and a module such as Seats records its mutation rows in its results file (spec/Seats-results-2026.09.29.txt:4-8). Say "records its mutation runs in a results file". The rest stands.
- **Verifier's evidence:** `grep -rn -i "six controls\|in-memory copy" .` gives decisions/ADR-0057.md:284 only; decisions/ADR-0057.md:284-287 (five controls described); spec/specification-graph.py:1237-1244 (build and check only), `grep -n -i control` in it gives :101-102 (RESTATES text) only; `grep -n '^=='` on the results file gives lines 7, 9, 52, 70, 76, 79, 83, 98, 107.

### H-11: ADR-0058's header cites §7 twice for the declaration's graph field; the field is §8
- Against: decisions/ADR-0058.md:14, :24-25 (and decisions/ADR-0058.md:118, :130, :193)
- Basis: Proposed
- Claim: "ADR-0023 §6's schema gains a field (§7), by amendment" and "**Carries a debt against:** ADR-0023 §6 (the declaration gains a graph, §7) · `ADOPTERS_GUIDE_README.md` §2 and §9.2 (the declaration and its checklist, §7)"
- Why wrong: "### 7. Suppliers publish subgraphs, and a deployment imports them" (ADR-0058:118) and "### 8. The declaration gains its graph, and the gate reads it" (ADR-0058:130). §8 is where the field, the ADR-0023 amendment and checklist items D-g1 to D-g5 are, and the body cites it correctly: "the ADR-0023 amendment (§8)" (ADR-0058:193). The Status note's argument that C3 does not apply rests on the mis-cited section.
- Fix belongs in: ADR-0058 header
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0058.md:14, :24-25, :118, :130, :132-145 (the field and D-g1 to D-g5 are in §8), :193, :247. The other reading, ADR-0023 §7, does not hold: line 25 applies "§7" to the Guide's checklist, and ADR-0023 §7 is composition (ADR-0023.md:53).

### H-12: ADR-0058 was not revised after ADR-0057 R1: it says the checker does not exist, its four ratification conditions carry no state, and none is met on the tree
- Against: decisions/ADR-0058.md:149-150, :188-193, :248, :259-261 (and decisions/ADR-0057.md:418; decisions/ADR-0023.md:16; ADOPTERS_GUIDE_README.md:424-432; spec/specification-graph.py:1237-1244)
- Basis: Proposed
- Claim: "The reference's overlay, as the corpus stands on 2026.11.06, **read and not computed** *(the checker of ADR-0057 §8 does not exist yet)*:"
- Why wrong: ADR-0057's R1 row says "Its builder and checker is `spec/specification-graph.py`" and "Built 2026.11.07" (ADR-0057:418), and the file is in the tree. ADR-0058's History has the initial row only (ADR-0058:259-261). §12 lists four conditions with no **Met** or **Not met** beside any (ADR-0058:188-193), where ADR-0057 §14, ADR-0059 §9 and ADR-0068 §6 each state one. By the tree: ADR-0057 is Proposed; the checker takes no overlay as input (py:1237-1244 accept `build` and `check` only), so no "reference's overlay" and no "replacement overlay" has been computed as such; ADR-0023's header says "**Pending:** none. A1 ratified 2026.10.04 (Batch 29) and applied inline" (ADR-0023:16), so the amendment of §8 is not drafted; and the Guide's §9.2 has items D1 to D5 and no D-g item (ADOPTERS_GUIDE_README.md:424-432). §8 makes the gate fail "a declaration whose overlay does not parse against the archetype version it names" (ADR-0058:134), and the Open obligations name "**The form of a supplier's subgraph**" (ADR-0058:248) but not the form of the overlay itself.
- Fix belongs in: ADR-0058 §9, §12, Open obligations and History
- Severity: Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed with correction
- **Verifier's correction:** "None is met" is too broad for the second condition: its substance, the inventory at *trusted* equal to Annex B's, is what ADR-0057's run reports for the corpus graph, which holds the reference's crates (results:99). It is unmet in form only: no overlay as such, and no named commit (json:5 "9749dfa + working tree"). Conditions 1, 3 and 4 are unmet, and §12 states a state for none of the four; that stands.
- **Verifier's evidence:** decisions/ADR-0058.md:149-150, :186-193, :246-251, :259-261 (one History row); decisions/ADR-0057.md:18, :418 ("Its builder and checker is `spec/specification-graph.py`"; "Built 2026.11.07"); decisions/ADR-0023.md:16, `grep -n '0058\|0057' decisions/ADR-0023.md` empty; ADOPTERS_GUIDE_README.md:424-432, `grep -n 'D-g\|0058\|overlay'` over both guides empty; spec/specification-graph.py:1237-1244; decisions/ADR-0059.md:152, :162 and decisions/ADR-0068.md:128-130 (records that do state Met or Not met).

### H-13: ADR-0058 says the reference is an overlay that "adds its crates"; the graph ADR-0057 built, which ADR-0058 calls the archetype's, already holds the crates as its own nodes
- Against: decisions/ADR-0058.md:52, :62 (and decisions/ADR-0057.md:267-268; spec/specification-graph-results-2026.11.07.txt:4; spec/specification-graph.json:2664)
- Basis: Proposed
- Claim: "The archetype's graph (ADR-0057 §8) is published with each archetype version, by digest." and "The reference is the first overlay (§9): it keeps every record and module, and adds its crates."
- Why wrong: ADR-0057's graph, "built for the corpus", includes "the reference's eight crates, its scripts and the reference as a whole" (ADR-0057:267-268). The JSON has `"id": "mechanism/crates/topak-bundle"` and the rest in layer `implementation` (json:2664 and following), and the results count "implementation 15" and "deployment 0" (results:4). Nothing in the file marks which nodes are the archetype's and which the reference's overlay adds, so a deployment that keeps the published graph keeps the reference's crates, the 139 read edges from them and the 21 trusted edges from `mechanism`. ADR-0058 §12's "**The reference's overlay is computed**" has no object to compute until the two are separated.
- Fix belongs in: ADR-0058 §1 and §9, or ADR-0057 §8 (what the published archetype graph contains)
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0058.md:52-53, :62, :189-190; decisions/ADR-0057.md:261-262, :267-269; results:4 (implementation 15, deployment 0); graph: 15 implementation nodes (json:2660-2664 on), 139 read edges from them, 21 trusted edges from `mechanism`; node keys are id, layer, path, clause, of, clauses, note only, and the string "overlay" occurs 0 times in the JSON. ADR-0057 never calls its graph the archetype's (`grep -n -i archetype decisions/ADR-0057.md`: :27, :33, :405).

### H-14: ADR-0058 types a Verus proof that Rust refines a TLA+ module as proved; by ADR-0057's table and finding 9(d) it is proved of a reading
- Against: decisions/ADR-0058.md:78-79, :168-169 (and decisions/ADR-0057.md:134, :386-387)
- Basis: Proposed
- Claim: "a Verus proof that a Rust mechanism refines a module is *proved*, and its prover is a row." and "proves it refines `Seats`, `Lease_A1` and `FloorComposition` with Verus: those theorems rise to *proved*"
- Why wrong: ADR-0057:134 has "| **proved of a reading** | Is proved, but one end is a hand transcription or a model of the other | The reading (`enc-faithful`, `model-faithful`), which a check may support |", and finding 9(d) has "The Lean proof of an encoding is *proved of a reading*" (ADR-0057:386-387). Verus does not take a TLA+ module as input, so the module's statement in Verus is a transcription of it, as the Lean encodings are, and the edge leaves that reading. This is the example ADR-0058 uses to show a deployment grading above the archetype (§5), so the grade it would report upstream is one type too high. This rests on how such a proof would be stated; the corpus has no Verus artifact to check.
- Fix belongs in: ADR-0058 §3 and §9
- Severity: Low-Medium
- Confidence: medium
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0058.md:77-79, :167-169; decisions/ADR-0057.md:133-134, :386; the tree's nearest case, `mechanism/lean` and the spec/lean encodings, is typed proved of a reading for the same reason. `find . -iname '*verus*'` empty, so nothing in the tree can test it; the premise that Verus needs the module restated by hand is a fact about the tool, outside the corpus and not checked here, as the finding itself says.

### H-15: §14's breakdown of the 419 nodes adds up to 373
- Against: decisions/ADR-0057.md:266-268 (and spec/specification-graph-results-2026.11.07.txt:4; decisions/ADR-0057.md:79-81)
- Basis: Proposed
- Claim: "It has 419 nodes: 283 clauses of 44 records, among them every clause of the 42 records the reference follows; the 31 modules and 24 proof modules; 14 Lean encodings and `mechanism/lean`'s five files; the genesis floor, its four stages and `floor/lean`; and the reference's eight crates, its scripts and the reference as a whole."
- Why wrong: 283 + 31 + 24 + 14 + 5 + 6 + 10 = 373. The other 46 are the 44 whole-record nodes (JSON nodes with a `clauses` list and no `clause` field, such as the node `ADR-0003` with `"clauses": ["text"]`) and the two binding files in the assurance layer. The results line "record 325 · assurance 4" (results:4) is 281 clause nodes plus 44 record nodes, and 2 annex clauses plus 2 binding files. §1's definition of a node lists "a record's clause" and not a record (ADR-0057:79-81), yet 183 of the 435 edges end at a whole-record node (181 read, 2 trusted) and 211 of the 281 record-layer clause nodes have no edge at all (my count over the JSON).
- Fix belongs in: ADR-0057 §14, and §1 if a whole record is a node
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0057.md:266-269, :79-81; results:4; recount over the JSON: 283 clause nodes (281 record, 2 assurance), 44 whole-record nodes, 2 binding files, 31 + 24 modules, 14 spec/lean, 5 mechanism/lean, 6 floor, 10 mechanism = 419, and the sentence's own terms sum to 373; 183 edges end at a whole-record node (181 read, 2 trusted); 211 of 281 record-layer clause nodes touch no edge; node ADR-0003 has "clauses": ["text"].

### H-16: A record whose Decision is a numbered list has no "§n" clauses, so citations the corpus makes ("ADR-0027 §2", "ADR-0023 §2") do not resolve; and A18 states the splitting rule more narrowly than clauses.py applies it
- Against: decisions/ADR-0057.md:104-106 and decisions/ADR-0033.md:985-990 (and spec/clauses.py:14-20; decisions/ADR-0027.md:30-39; spec/Anchor.tla:49; spec/RulesFloorBase.tla:60)
- Basis: Proposed
- Claim: "The binding point of the graph above the model layer is the **clause**: a numbered subsection of a record's Decision, with its inline amendments, cited as the corpus already cites it (\"ADR-0031 §4, A1\")." (ADR-0057) and, pending in ADR-0033 A18: "split by the rule `spec/clauses.py` states: each numbered subsection of its Decision, each numbered level-two section and each annex, with their inline amendments"
- Why wrong: `python3 spec/clauses.py decisions/ADR-0027.md` prints one clause, `ADR-0027 Decision`. ADR-0027's Decision is the list "1. **Genesis rules are pre-blessed and resident.**", "2. **Genesis rules must satisfy the rules floor**", "3. …" (ADR-0027:30-39), not `###` subsections. The corpus cites it by number: "(ADR-0027 §4)" (spec/Anchor.tla:49) and "ADR-0027 §2 / ADR-0029 §5" (spec/RulesFloorBase.tla:60). In the graph those become `read: spec/Anchor.tla → ADR-0027` with the one pin `ADR-0027 Decision` = `69432425ed85a65f`, so a change to item 3 trips a citation of item 2. `clauses.py` on ADR-0023 likewise prints only `ADR-0023 Decision`, though ADR-0057 depends on "ADR-0023 §2, §6" and defines a grade by "ADR-0023 §2's inventory". Finding 9(b) lists the splitter's choices (ADR-0057:379-383) and not this one. A18's summary omits what `clauses.py` also makes clauses: an unnumbered subsection named by its heading, the text before the first `###` as `Decision`, and a record with no Decision as the one clause `text` (clauses.py:14-20). Its pin-file form "`<pin>  decisions/ADR-NNNN.md §N`" (ADR-0033:990) cannot write those; the graph holds, for example, the clause `ADR-0018 Why the decoder need not be trusted` and eight records whose only clause is `text`.
- Fix belongs in: ADR-0057 §2 and finding 9(b); ADR-0033 A18; spec/clauses.py if list items are meant to be clauses
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** `python3 spec/clauses.py decisions/ADR-0027.md` prints `69432425ed85a65f  ADR-0027 Decision` only; the same on ADR-0023 prints `ADR-0023 Decision` only; on ADR-0018 it prints `ADR-0018 Why the decoder need not be trusted`; 8 records have the one clause `text`. decisions/ADR-0027.md:30-43; spec/Anchor.tla:49; spec/RulesFloorBase.tla:60; graph edges `read: spec/Anchor.tla → ADR-0027` and `read: spec/RulesFloorBase.tla → ADR-0027` pin `ADR-0027 Decision` = 69432425ed85a65f; decisions/ADR-0057.md:29, :104-106, :170, :379-383; decisions/ADR-0033.md:985-990; spec/clauses.py:14-20.

### H-17: The reference's read edges discard the section in every citation, so each pins every clause of the record; §7's "each clause the reference follows, by section" is not what is pinned
- Against: decisions/ADR-0057.md:195-196 (and spec/specification-graph.py:255, :580-582; mechanism/crates/topak-core/src/action.rs:1; mechanism/crates/topak-contain/src/docker.rs:6; decisions/ADR-0057.md:303-304, :383)
- Basis: Proposed
- Claim: "the pin of a record is the digest of each clause the reference follows, by section, with its inline amendments"
- Why wrong: `code_citations` keeps only the record: `found = {f"decisions/ADR-{n}.md" for n in re.findall(r"ADR-(\d{4})", text)}` (py:255), and `rule_reference_reads` pins `{f"{rec} {c}": p for c, p in cl.items()}`, every clause of the record, on an edge to the whole-record node (py:580-582). The Rust does cite sections: `grep -rnoE "ADR-00[0-9]{2} §[0-9]+" mechanism/crates --include=*.rs | wc -l` gives 640, the first being "ADR-0022 §1" (action.rs:1). None of the 139 read edges from the reference ends at a clause node (my count over the JSON: 0). The record shows the effect: "A5 moved ADR-0045 §3's clause pin, so eight read edges went stale, three from the reference" (ADR-0057:303-304), and one of the three is `topak-contain`, which cites ADR-0045 for a row of its annexes ("ADR-0045 T-0045-19", docker.rs:6). Finding 9(b) covers only "A citation of a record without a section" (ADR-0057:383). Finding 11's "no edge but the code's reading" inherits this: the code's reading of a clause is inferred from a citation of the record anywhere in the crate. Module citations are resolved by section (py:262-269), so the two halves of the graph differ.
- Fix belongs in: spec/specification-graph.py (`code_citations`, `rule_reference_reads`); ADR-0057 §7, finding 9(b), finding 11; ADR-0033 A18
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** spec/specification-graph.py:253-259, :262-269, :574-587; `grep -rnoE "ADR-00[0-9]{2} §[0-9]+" mechanism/crates --include=*.rs | wc -l` = 640, first hit mechanism/crates/topak-core/src/action.rs:1; graph: 139 read edges from implementation nodes, 0 end at a clause node (119 of 188 module read edges do); `read: mechanism/crates/topak-contain → ADR-0045` pins every clause of the record, while topak-contain cites ADR-0045 only for rows (docker.rs:6, wasmtool.rs:5); decisions/ADR-0057.md:195-196, :303-304, :383.

### H-18: "The checker lists every such pair" of twice-stated guarantees; the list is a constant of one entry written into the builder
- Against: decisions/ADR-0057.md:189-191 (and spec/specification-graph.py:97-104, :1136-1144; spec/specification-graph-results-2026.11.07.txt:70-74; decisions/ADR-0057.md:332)
- Basis: Proposed
- Claim: "**The checker lists every such pair with its type**, so that each is raised, by generating one from the other or by proving them equal, or kept, with the type showing."
- Why wrong: `RESTATES` (py:97-104) is hand-written and has one member, "the operator's envelope, C1 to C9 (ADR-0050 §4; mechanism/ I47 (e))"; the checker prints what that constant holds (py:1136-1144), and the results section has that one guarantee (results:70-74). Nothing computes which guarantees are stated twice, so "every" is the drafter's knowledge of I47 (e), the case the Context already had. The graph itself holds other restatements the section does not list: sixteen module-to-encoding pairs, the floor in Cedar and in `floor/lean`, `FloorComposition`'s `Decide` and `admit.rs`. Consequences repeats the claim: "**Twice-stated guarantees are listed**" (ADR-0057:332).
- Fix belongs in: ADR-0057 §6 and §8 (say the list is declared, not computed), or the builder
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0057.md:189-191, :332; spec/specification-graph.py:95-104 (one entry), :1133-1144 (prints the graph's `restates`); the JSON's `restates` has that one entry; results:70-74; the graph holds 16 distinct (Lean encoding, module) pairs under spec/lean, three `floor/lean → floor` edges and the proved-of-a-reading edge to FloorComposition.tla, none of them in the section.

### H-19: Two of the "four lists … agree with the graph" checks compare much less than the lists hold, and the pin-file check passes when a pinned text cannot be found
- Against: decisions/ADR-0057.md:209-210 (and spec/specification-graph.py:950-952, :984-996, :1020-1024; spec/specification-graph-results-2026.11.07.txt:90-96)
- Basis: Proposed
- Claim: "`corpus-pins.sha256`, the binding JSON's `check` columns, the manifest index and the sync scripts' file lists each gain a check that they agree with the graph."
- Why wrong: The manifest check takes the newest `reference` row and compares crate directory names only: `mcrates = {"/".join(p.split("/")[:3]) for p in man if p.startswith("mechanism/crates/")}` against the implementation nodes (py:984-991), giving "its 8 crates are the graph's 8 crate nodes" (results:91). No digest in a manifest is compared with any pin, though the Context says "`manifests/` measures each cut by digest" (ADR-0057:57-58), and the second manifest line is printed as "(information)" and cannot fail (py:992-996). For `spec/mechanism-trace-results.sh` the check is that some edge names the results glob (py:1020-1024): "its results are the replayed edges' evidence" (results:96) holds while both replayed edges are stale. For `corpus-pins.sha256`, a record whose pinned text is neither the tree's nor in history gives `want = None`, and the comparison is skipped by `if want is not None and want != e["pins"]` (py:950-952), so the list agrees exactly when it cannot be checked. Only the `check`-column comparison and the two glob comparisons are full.
- Fix belongs in: spec/specification-graph.py (`lists_against_graph`); ADR-0057 §8 and §14's "the four lists agree"
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0057.md:57-58, :209-210; spec/specification-graph.py:948-954 (`want is not None and`), :980-996 (crate directory names only; the second manifest line is information), :1020-1024 (any edge naming the results glob); results:90-96, with both replayed edges stale at results:44-49.

### H-20: The replayed edges are pinned to commit 9c57221, which is not the tree the traces were recorded on, so the "seventeen files" count does not measure what moved since the replay
- Against: decisions/ADR-0057.md:276-278 (and spec/Mechanism-trace-results-2026.10.05.txt:3; decisions/ADR-0033.md:26, :818, :825; spec/specification-graph.json:10357; spec/specification-graph.py:27-28, :478-485)
- Basis: Proposed
- Claim: "the two replayed edges, to `Mechanism.tla` and `ConfinementRefinement.tla`, are stale because `topak-core` has changed in seventeen files since `9c57221`, the commit the newest trace results name"
- Why wrong: The results header is "Reference: mechanism/ at 9c57221 + working tree" (Mechanism-trace-results-2026.10.05.txt:3). `9c57221` is A12's commit ("A12 (the emergency seating; `9c57221`)", ADR-0033:26); the replay is A14's, whose artifacts are "commit `7d8c7db`" (ADR-0033:818) and whose row says "`trace.rs` projects the state and the entries to match. The operator and emergency state tests are traced, and one test is added" (ADR-0033:825). The builder pins `"git 9c57221 mechanism/crates/topak-core": "unchanged"` (json:10357), which is "fresh while nothing under the path differs from that commit" (py:27-28). The traced tree already differed from `9c57221`, so by this pin the edge was stale on the day it was recorded and can never be fresh for a replay made on a working tree; the seventeen files (results:46 lists `src/trace.rs`, `tests/operators.rs` and `tests/emergency.rs` among them) include changes that were part of the replayed code. The edge's note admits the first half ("recorded on a working tree over the commit it names"); §14 gives the count as the cause. The conclusion (item 56: workflows are not replayed) stands; the evidence offered for it is not tight. I could not run `git diff` to separate the two sets.
- Fix belongs in: spec/specification-graph.py (`rule_traces`) and ADR-0057 §14; or spec/mechanism-trace-results.sh records file digests as the Lean results do
- Severity: Low-Medium
- Confidence: medium
- Already on the corpus's own lists: no (related: G11 item 56)
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0057.md:276-278; spec/Mechanism-trace-results-2026.10.05.txt:3 ("at 9c57221 + working tree"); decisions/ADR-0033.md:26 (A12 `9c57221`; A13 and A14 `7d8c7db`), :818, :825; spec/specification-graph.json:10357-10358, :10381-10394 (pins and the note); spec/specification-graph.py:26-28, :475-491; results:45-49 (the 17 files include src/trace.rs, tests/operators.rs, tests/emergency.rs). The copy has no .git, so the split of the 17 files cannot be measured here either; the finding rests on the headers and A14's row, and says so.

### H-21: inventory.py already has an "overlay" with a different meaning, and still calls ADR-0053's derived premises Proposed
- Against: spec/inventory.py:32, :45 (and decisions/ADR-0058.md:5, :52-53, :88; decisions/ADR-0053.md:16)
- Basis: evidence
- Claim: "**Derived premises** (ADR-0053 §5, R7, Proposed)." and "`--with` applies an overlay: its premise columns and derived premises are added, and each of its theorems, named as the binding names them, gets its `replaces`."
- Why wrong: ADR-0053 is "**Status:** Accepted (genesis) · 2026.10.06" (ADR-0053:16), so the docstring's "Proposed" is stale. ADR-0058 names `spec/inventory.py` among its sources (ADR-0058:5) and then defines "**A deployment's graph is an overlay**" (ADR-0058:52-53) without noting that the script it cites uses the word for a binding patch (`merge(binding, overlay)`, inventory.py:162-176). With ADR-0059 to ADR-0068 (H-2) the word has three senses in the tree and none in the glossary (`grep -n -i overlay narrative/glossary.md` returns nothing; ADR-0058's Open obligations owe the entry). A reader sent by ADR-0058 §4, "The deployment's inventory is computed from its overlay" (ADR-0058:88), to the script finds an `overlay.json` that is something else.
- Fix belongs in: spec/inventory.py docstring; ADR-0058 §1; the glossary
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** spec/inventory.py:32, :41-45, :162-176; decisions/ADR-0053.md:16-17 (Accepted, ratified at R8, so R7 is in force); decisions/ADR-0058.md:5, :52-53, :88, :250; `grep -n -i overlay narrative/glossary.md` empty.

### H-22: The decisions index omits the confirmation criteria for ADR-0057 and ADR-0058 that it gives for the records on either side of them
- Against: decisions/README.md:70-71 (and decisions/README.md:3, :12, :69, :72; decisions/ADR-0057.md:19-21; decisions/ADR-0058.md:12)
- Basis: living document
- Claim: "Proposed (drafted 2026.11.06, after G11)" (the whole status cell of both rows)
- Why wrong: ADR-0057 has "Confirmation required under **C2**" and "**C4**" (ADR-0057:19-21); ADR-0058 has "Confirmation required under **C2**" (ADR-0058:12). The row above reads "Proposed (drafted 2026.11.06, after G11); confirmation required: C1, with C2 applying to §5" (README:69, ADR-0056), and the row below ends "confirmation required: C1" (README:72, ADR-0059), as the nine after it end with theirs. The same table's column header is "Status at G8" (README:12) under a paragraph that says "**Status is as of Genesis Checkpoint G11 (2026.10.09)**" (README:3-4).
- Fix belongs in: decisions/README.md
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed with correction
- **Verifier's correction:** Scope. The index also omits the C1 that ADR-0054 and ADR-0055 state (decisions/README.md:67-68 against ADR-0054.md:21 and ADR-0055.md:17), so the omission is older than these two rows and the fix should cover all four. And of the nine rows after ADR-0059, eight end with a criterion; row 77 (ADR-0064) says "no confirmation criterion on the drafter's reading".
- **Verifier's evidence:** decisions/README.md:3-4, :12 ("Status at G8"), :67-81; decisions/ADR-0057.md:19-21; decisions/ADR-0058.md:12; decisions/ADR-0056.md:15.

### H-23: The two guides say they are kept current and say nothing of the graph, grades or overlays; the Reviewer's Guide's check list and "Where to push" leave out the new checker and its claims
- Against: REVIEWERS_GUIDE_README.md:4, :47, :117-140, :154-200 and ADOPTERS_GUIDE_README.md:11, :39
- Basis: living document
- Claim: "It is kept current and is not measured by any manifest" (both guides) and "stated as fifty-four decision records" (Adopter's Guide)
- Why wrong: `grep -n -i "0057\|0058\|specification graph\|overlay"` over both guides returns nothing. `ls decisions/ADR-*.md | wc -l` gives 67. The Reviewer's Guide §5 lists fourteen checks and not `spec/specification-graph.py check`, the one check whose results file this review finds stale (H-1) and unreproducible from a checkout (H-6). Its §6 lists "Model against prose", "Code against model" and "Proved in Lean" and not the claim that now sits over all three, that a theorem has a grade computed from typed edges, nor the ten records that call themselves overlays. Its state table still gives "Twenty-one of twenty-four proof modules" (REVIEWERS_GUIDE_README.md:47) against 32 in the tree. A reviewer who follows the guide's list would not open ADR-0057, ADR-0058 or the records that depend on them.
- Fix belongs in: REVIEWERS_GUIDE_README.md §2, §5, §6; ADOPTERS_GUIDE_README.md §1 (and §2, §9.2 when ADR-0058's entries are drafted)
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed with correction
- **Verifier's correction:** Both headers date the guide 2026.10.09, "written against Genesis Checkpoint G11" (REVIEWERS_GUIDE_README.md:3, ADOPTERS_GUIDE_README.md:10). At G11 the tree had 54 records (ADR-0001 to ADR-0055; there is no ADR-0014) and 24 proof modules, so "fifty-four" and "twenty-four" are stale against the tree and were right at the basis the header states. State the defect as "kept current" against thirteen records, eight proof modules and a checker added since, not as wrong counts.
- **Verifier's evidence:** `grep -n -i "0057\|0058\|specification graph\|overlay\|D-g" REVIEWERS_GUIDE_README.md ADOPTERS_GUIDE_README.md` empty; `ls decisions/ADR-*.md | wc -l` = 67; `ls spec/*_proof.tla | wc -l` = 32; REVIEWERS_GUIDE_README.md:3-5, :47, :117-140 (fourteen rows), :154-205 (items include Model against prose, Code against model, Proved in Lean); ADOPTERS_GUIDE_README.md:10-12, :39.

### H-24: §2 says a record drafted after ADR-0057 gives each clause four parts; none of the eleven records drafted with or after it does, including ADR-0058, which rests on it
- Against: decisions/ADR-0057.md:109-116 (and decisions/ADR-0058.md:15; decisions/ADR-0057.md:235)
- Basis: Proposed
- Claim: "**A record drafted after this one gives each clause four parts**, in this order"
- Why wrong: `grep -c -i "\*\*Givens\|\*\*Goal\.\|\*\*Discharge\|\*\*Guarantees"` gives 0 for ADR-0058 and for each of ADR-0059 to ADR-0068 (all drafted 2026.11.10). The rule is not in force, so this is not a breach. But ADR-0058 says "**It rests on ADR-0057**" (ADR-0058:15), the ten later records depend on ADR-0058, and none says the rule waits for ratification. ADR-0057 §11's "Should (this record)" cell is "Goal, givens, guarantees, discharge in each new clause (§2)" (ADR-0057:235), and the tree holds no clause written that way, so the form is untried.
- Fix belongs in: ADR-0057 §2 (from when the rule applies), or the later records
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** `grep -c -i "\*\*Givens\|\*\*Goal\.\|\*\*Discharge\|\*\*Guarantees"` = 0 for ADR-0058 and for each of ADR-0059 to ADR-0068; their Status lines read 2026.11.06 (0058) and 2026.11.10 (the ten); decisions/ADR-0057.md:18, :109-116, :235; decisions/ADR-0058.md:15. The finding says itself that a Proposed rule is not breached; what stands is that §2 gives no date from which it applies.

### H-25: The third ratification condition names premise-routes.sh; the Met paragraph reports a re-implementation inside the checker, and §4 still says nothing the derived premises compute changes
- Against: decisions/ADR-0057.md:159, :288-290, :418 (and spec/specification-graph.py:869-888, :1197-1209; spec/premise-routes-results-2026.11.03.txt:2; decisions/ADR-0053.md:291)
- Basis: Proposed
- Claim: "**ADR-0053's derived premises are re-expressed** as edge premises, and `spec/premise-routes.sh` prints the same verdicts." with "**Met for four of the five declarations** ⟨R1⟩." and, in §4, "ADR-0053's derived premises become instances, and nothing they compute changes:"
- Why wrong: The R1 row says "`premise-routes.sh` was not rerun" (ADR-0057:418). What ran is `routes_declarations`, described as "premise-routes.sh's five declarations, built as it builds them" (py:869-888), evaluated twice by the checker and compared with the parsed verdicts of the 2026.11.03 results file (py:1197-1209). The line "38 hold in the results file's run" (results:101) prints the checker's own evaluation, `sum(v[0] for v in p.values())` (py:1206), not a number read from the file. That is reasonable evidence, but it is not the script the condition names printing anything, and that script's newest results name `decisions/ADR-0045.md` at `b849108f349360bf` (premise-routes-results-2026.11.03.txt:2) where `sha256sum` on the tree gives `8e425f423b0b89ca`. §4's sentence is unqualified, while finding 7 and the pending ADR-0053 A1 say two verdicts of the fourth declaration move: "Nothing these premises compute changes while their edges are fresh." (ADR-0053:291). R1 added the finding and left §4 as it was.
- Fix belongs in: ADR-0057 §4 and §14 (third condition)
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no (finding 7 covers the fourth declaration)
- **Verifier:** confirmed with correction
- **Verifier's correction:** Two limbs are disclosed by the record and should be given as such: R1's row says "`premise-routes.sh` was not rerun: its newest results name ADR-0045 at its digest before A5, and are renewed at ratification" (ADR-0057:418), and the Met paragraph says the graph gives "the verdicts of `premise-routes-results-2026.11.03.txt`" (ADR-0057:294-296), a comparison with the file. What stands: the condition's words ("`spec/premise-routes.sh` prints the same verdicts", :288-289) are not what was done; the results label "hold in the results file's run" prints the checker's own count (py:1206), checked against the file only where the file has the theorem (py:1203); and §4's unqualified "nothing they compute changes" (:159) against ADR-0053:291 "while their edges are fresh".
- **Verifier's evidence:** decisions/ADR-0057.md:159-163, :288-297, :362-367, :418; spec/specification-graph.py:869-888, :891-903, :1197-1209; results:100-105; spec/premise-routes-results-2026.11.03.txt:2 (b849108f349360bf) against `sha256sum decisions/ADR-0045.md` = 8e425f423b0b89ca; decisions/ADR-0053.md:291.

### H-26: R1 says "No decision text changes" and R1's Met paragraphs are inside §14, a clause of the Decision by the record's own rule
- Against: decisions/ADR-0057.md:418 (and decisions/ADR-0057.md:75, :259, :263, :274, :290, :300; spec/clauses.py:14-15)
- Basis: Proposed
- Claim: "Findings 7 to 11 are new. No decision text changes."
- Why wrong: "### 14. Ratification condition" (ADR-0057:259) stands under "## Decision" (ADR-0057:75), and `clauses.py` makes "each `### ` subsection of it" a clause (clauses.py:14-15): `python3 spec/clauses.py decisions/ADR-0057.md` prints `e472c831b862e5a7  ADR-0057 §14`. The four paragraphs marked ⟨R1⟩ (ADR-0057:263, :274, :290, :300) are part of that clause's text, so its pin moved with R1. The review skeleton I was given marks §14, alone of the fourteen clauses, as changed after the module freeze. Either R1 changed a Decision clause while saying it did not, or §14 was edited after R1 with no History row; I cannot tell which without history. It matters here because §7 makes a clause's digest the unit a reader pins.
- Fix belongs in: ADR-0057 History (R1's wording), or the placement of the Met paragraphs
- Severity: Low
- Confidence: medium
- Already on the corpus's own lists: no
- **Verifier:** confirmed with correction
- **Verifier's correction:** The direction can be decided from the record: R1's row names "(§14)" as what it changed, and the four paragraphs carry ⟨R1⟩ (ADR-0057:263, :274, :290, :300), so it is R1 that changed a clause of the Decision while saying "No decision text changes". Nothing in the tree supports the other branch (a later edit with no History row). Drop the sentence about the review skeleton, which is not in the corpus and cannot be checked.
- **Verifier's evidence:** decisions/ADR-0057.md:75, :259, :263, :274, :290, :300, :308 (Decision ends), :418; spec/clauses.py:14-15; `python3 spec/clauses.py decisions/ADR-0057.md` prints `e472c831b862e5a7  ADR-0057 §14`.

