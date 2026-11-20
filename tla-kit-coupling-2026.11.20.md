# tla-kit — Coupling records, specifications, evidence and CI into one checked chain

**2026.11.20** · a design note, not a record · draft for the custodian, to move into tla-kit (as `COUPLING.md` or
under `derived/`) if it is taken up · basis: tla-kit `main` at `a53425b` (README, PLAN.md, ADR-0001, 0002, 0007,
0013 to 0016, `spec/`, `.github/workflows/ci.yml`, `evidence.yml`, `agent.yml`, `vendor/`, CONSUMERS.md), TOPAK at
`1722432` (`spec/specification-graph.json`, `spec/theorem-premise-binding.md`, `mechanism/crates/topak-core/tests/drift.rs`,
ADR-0057, ADR-0058, ADR-0069, ADR-0077, `.claude/skills/`), gov-tla at `b8a82be` (README, `rows/`, `results/`,
`tools/TLA-KIT-PIN`) · prepared by the assistant at the custodian's request

Nothing here is built, and nothing here is accepted. Where it says what tla-kit does today, it cites the file; where
it proposes, it says so. The custodian settled one thing before it was written: **tla-kit is where the coupling
lives, because tla-kit already uses it on itself.**

---

## 0. In one paragraph

tla-kit already runs the whole chain on itself, at small scale. Its records name the actions of its own TLA+
modules (ADR-0015 item 2). Its results files are made only by the skill's generator and name what checked them.
Its CI reruns those rows when `spec/` or `decisions/` changes, and `main` merges only on a pass (ADR-0014 item 1).
Its pin moves carry evidence over the projects it serves (ADR-0013 item 3). An agent job repairs a proof with
nothing but the server's tools, and the repair is checked apart from the agent (`agent.yml`). And a person accepts
every record (the **Chosen by** line). What is missing is that most links between these are **prose**. A record
cites a row in a sentence; CI reruns every row because it cannot tell which ones a change touches; and the method
the whole chain runs on lives in another repository (ADR-0007). This note proposes three things to close that: a
**claims table** that writes the links down as data, a **claims check** that keeps them true, in the image and
behind a required CI check, and moving the **method**, the TLA+ skill and a records skill drawn from tla-kit's own
`decisions/`, into tla-kit. TOPAK and gov-tla then consume all of it by pin, at whatever depth they choose.

---

## 1. The chain

Each arrow is a link a reader has to be able to follow, and a check has to be able to fail on.

```
 Record item ──► Claim ──► Property ──► Result ──► Checker ──► CI ──► Acceptance
 (ADR-n §k)      (what     (module,     (dated     (image      (rerun,  (a named
                 the item   row,        file,      digest,     required person,
                 asserts)   expected    never      every tool  check)   with the
                            verdict)    edited)    by digest)           evidence)
```

- A **record item** is the unit a decision is made in: `ADR-0015 item 4`, not `ADR-0015`.
- A **claim** is what an item says is true and checked: "every release's evidence was run on the image the release
  publishes".
- A **property** is where it is checked: a module, a named operator, and the rows that exercise it, each with the
  verdict the row list expects (`HOLDS`, `COUNTEREXAMPLE`, `VIOLATED` for a witness, `PROVED` for a theorem).
- A **result** is the dated file the generator wrote, with the digests of the module, the rows and the runner.
- A **checker** is the image, by digest, that made the result.
- **CI** reruns what a change could have changed, and blocks the merge if a claim is no longer true.
- **Acceptance** is a person's, and is never inferred from a green check. A pull request's approval is not an
  acceptance (TOPAK's CONTRIBUTING.md says the same of ratification).

---

## 2. Where tla-kit stands on each link today

| Link | What tla-kit does today | Where | Written as |
|---|---|---|---|
| Record → property | Each action of `PinLifecycle.tla` names the record item it comes from; "a change to a record that changes an action changes the module in the same pull request" | ADR-0015 item 2; `spec/README.md`'s gap table maps each fix to its record item | **Prose** |
| Property → expected verdict | Row lists carry the expected verdict of every row, and the generator writes a file only when every row is as expected | `spec/*-rows.txt`; the vendored `tlc_rows.py` | Data |
| Result → module, rows, runner | Every results file names the sha256 of the module, the row list and the runner scripts | `spec/*-results-*.txt` headers | Data |
| Result → checker | Results name the **jar's** digest. ADR-0002 says every result names the **image's** digest; the TLC results at `a53425b` do not carry it in their header | `spec/PinLifecycle-results-2026.11.19.txt` lines 3 to 6 | **Gap** (or the image is named elsewhere; to confirm) |
| Result → current | `proof_sync` reports `IN SYNC`, `STALE`, `MISSING` for proof results. For TLC results, CI regenerates and compares | the skill's `proof_sync.py`; `ci.yml` | Data for proofs; rerun for TLC |
| Change → which rows rerun | Every row of both modules, whenever `spec/` or `decisions/` changes or a checker pin moves | `ci.yml` header, ADR-0015 item 8 | **Coarse**: the change's reach is not known |
| CI → merge | Required checks on `main` by ruleset; a pull request is retested if `main` moved | `ci.yml` header; ADR-0014 item 1 | Enforced |
| Pin move → consumers | Evidence over every project served, at a named commit of each | `evidence.yml`; ADR-0013 item 3 | Enforced for TOPAK; **gov-tla skipped** as private, which it no longer is |
| Agent → check | An agent repairs a broken proof with only the server's tools; the repair is checked apart from it | `agent.yml`; `examples/agent-repair/` | Enforced (run by hand, it costs an API call) |
| Method | The skill's scripts are vendored from TOPAK at a named commit and checked by digest | ADR-0007; `vendor/VENDOR-PIN` | Data, but **the source is outside tla-kit** |
| Records method | `decisions/` has a consistent form (Status, Chosen by, State, Depends on, Relates to, Pending, History), and accepted text is not edited | `decisions/README.md` | Convention; **no skill, no check** |
| Acceptance | The custodian accepts each record, and the README says who chose what | `decisions/README.md` table | Convention |

Six of the twelve links are enforced data already. The other six are what this note is about.

---

## 3. The design

### 3.1 The claims table

One file per project, `claims.tsv`, at the root of the project's `spec/` (proposed). One row per claim. TSV,
because TOPAK's `manifests/index.tsv` and the row lists are line-oriented and diff well, and because a person edits
it.

| Column | Meaning | Example |
|---|---|---|
| `claim` | A stable id, never reused | `C-0015-4a` |
| `record` | The record and item that makes the claim | `ADR-0015 item 4` |
| `says` | The claim in one line, as the record words it | `Every release's evidence was run on the image the release publishes` |
| `module` | The module that checks it | `spec/PinLifecycle.tla` |
| `property` | The operator, theorem or witness | `EvidenceFitsRelease` |
| `rows` | The rows that check it, by name, with the verdict each row list already expects | `n-none-evidence` |
| `breaks` | The rows whose counterexample shows the claim is not vacuous: the mutation that removes the item | `m-nof1-evidence` |
| `grade` | `checked` (TLC at stated constants), `proved` (TLAPS), `certified`, `sampled`, as the skill's vocabulary of claims defines them | `checked` |

What it deliberately leaves out:

- **The verdict.** It is in the row list already. The table names rows; it does not restate them.
- **Digests.** They are in the results files already. The check reads them there.
- **Premises.** TOPAK's `theorem-premise-binding.md` carries what each theorem rests on, and its specification
  graph (ADR-0057: 529 nodes, 495 typed edges at `1722432`) carries every edge with what it leaves to a person. Both
  are a **heavier profile** of the same idea. A project that has them can generate its `claims.tsv` from them; a
  project that has six modules, like gov-tla, writes it by hand. The table is the floor every project shares, not
  the ceiling.

### 3.2 The claims check

A script beside the skill's other scripts, `claims_check.py` (Python, standard library only, like them), and the
same thing as a fifteenth server tool, `claims`. It reads the claims table, the row lists, the results files and
the records, and prints one line per claim, in `proof_sync`'s words:

- `IN SYNC`: the record and item exist; every named row exists in the row list with the verdict the table needs
  (`HOLDS` or `PROVED` for `rows`, `COUNTEREXAMPLE` for `breaks`); the newest results file has every one of them as
  expected; and that file's module, rows and runner digests are those of the tree.
- `STALE`: all of that, except that the module, the row list or the record has changed since the results file was
  made. The record's digest is taken whole-file, as TOPAK's `drift.rs` does, so a History row trips it too. That is
  deliberate: re-running is cheap, and a reviewer reads the change.
- `MISSING`: a record, item, module, property or row the table names does not exist, or a results file has never
  been made.
- `BROKEN`: a results file contradicts the table: a row the claim needs is not as expected.

And two checks over the whole table:

- **Every property in a row list is claimed or marked.** A property no record claims is either a witness or a
  mutation's target, which the row list's `expected:` lines already say, or it is a check nobody decided on. The
  check lists the second kind.
- **Every record item that says it is checked has a claim.** A record marks such an item with the claim id in its
  text (`… (C-0015-4a)`). The check finds ids in records that the table lacks, and table rows whose id is not in
  the record.

Like `proof_sync`, the check **writes nothing**. ADR-0006 stands: the server has no way of its own to write a
results file, and the `claims` tool is read-only.

### 3.3 CI

- **Every pull request runs the claims check**, as a required check. It fails on `MISSING` and `BROKEN`.
- **`STALE` claims are rerun, and only those.** The claims table gives CI what it lacks today: which rows a change
  can reach. A change to `decisions/ADR-0016.md` reruns the claims of ADR-0016, not every row of both modules. A
  checker pin move still reruns everything (ADR-0013 item 3 is unchanged).
- **Evidence over consumers includes their claims check.** `evidence.yml` runs each consumer's claims check, if it
  has a table, in the candidate image. gov-tla joins the run now that it is public.
- **Results name the image.** Whatever closes the §2 gap on ADR-0002, the claims check then compares the image a
  result names with the image CI ran in, and calls a mismatch `STALE`.

### 3.4 The method moves into tla-kit

Today the method lives in TOPAK and tla-kit vendors it (ADR-0007), and gov-tla carries a hand copy of `SKILL.md`
taken at TOPAK `5ade81e`, with a README line asking that it be copied again when it changes. Three repositories, two
ways of keeping up, both by hand.

Proposed:

1. **The `writing-tla-specs-and-proofs` skill's source moves to tla-kit**, as `skills/writing-tla-specs-and-proofs/`,
   with its scripts. The plugin is published from tla-kit, and its `.mcp.json` names the image of the same release,
   so a skill release and an image release are one tag. ADR-0007 is superseded; its items 3 and 4 (a digest check;
   the skill stays usable without Docker) carry over.
2. **A records skill joins it**, `writing-decision-records`, generalized from tla-kit's own `decisions/` form, not
   from TOPAK's: the header lines (Status, Chosen by, State, Depends on, Relates to, Pending), History rows, accepted
   text never edited, claim ids on checked items. It drafts and revises; it never accepts.
3. **TOPAK's `.claude/skills/` become a profile over it.** `drafting-records`, `ratifying-records` and
   `cutting-manifests` keep what is TOPAK's (genesis, numbered Batches, confirmation markers, G-checkpoints) and
   take the shared form from the records skill.
4. **Projects consume by pin.** One file, the existing `tools/TLA-KIT-PIN`, names the release; the skill comes
   with it. TOPAK and gov-tla move to it by their own decision (ADR-0005 item 5's rule for pins).

### 3.5 Depth a project chooses

A project takes as much of the chain as it wants. Each level adds one thing.

| Level | What the project has | Who is there today |
|---|---|---|
| 0 | A pin of the image | gov-tla (`v0.1.0`), TOPAK (`v0.4.0`) |
| 1 | Its results regenerated and compared in the image, in its own CI and in tla-kit's evidence | TOPAK; tla-kit itself |
| 2 | A claims table, the claims check as a required check | tla-kit, first (§4) |
| 3 | Premises and a typed graph of every edge (ADR-0057's form), from which the claims table is generated | TOPAK, in part (ADR-0057 is Proposed) |

Level 2 is the product. Level 3 is TOPAK's, and is not required of anyone.

### 3.6 Specify before building

tla-kit's own habit is to write the module before the code (ADR-0016 item 2). The claims check has a small life
cycle worth the same treatment: a claim is made, a module or record changes, CI reruns, a result is regenerated or
a row breaks, a person accepts. Proposed: `spec/ClaimsSync.tla`, with the properties a reader would assume and
CI would otherwise only hope for:

- **No acceptance on a stale claim.** A record is never accepted while one of its claims is `STALE` or `BROKEN`.
- **A green check means a current result.** CI passes only if every claim's newest result was made from the tree
  CI checked out, in the image it names.
- **A rerun cannot hide a break.** A row that was `HOLDS` and is now a counterexample is reported, never
  regenerated over.

Its mutations are the shortcuts: CI that skips `STALE` claims, a generator that overwrites a failing file, an
acceptance that does not wait for the check.

---

## 4. Order of work

Each step has its own **Done when**, in tla-kit's way.

1. **tla-kit's own claims table.** Write `spec/claims.tsv` for `PinLifecycle` and `ProveRequests` by hand, from
   ADR-0005, 0013 to 0017 and `spec/README.md`'s gap table. *Done when* every property of both row lists is claimed
   or marked, and every checked item in those records carries its id.
2. **`spec/ClaimsSync.tla`**, rows and results, before the script. *Done when* `Mut = "none"` holds and each
   mutation breaks its property and no other.
3. **`claims_check.py` and the `claims` tool.** *Done when* it reports tla-kit `IN SYNC` at a clean tree, and
   `STALE`, `MISSING` and `BROKEN` each on a fixture built to cause it.
4. **CI.** The claims check becomes a required check; `STALE` claims scope the rerun; results name the image.
   *Done when* a pull request that edits one record reruns only that record's rows, and one that breaks a row
   cannot merge.
5. **The method moves.** The TLA+ skill's source into tla-kit; ADR-0007 superseded; one tag releases the image and
   the plugin. *Done when* TOPAK and gov-tla each load the skill from a tla-kit release, and `vendor/` is gone.
6. **The records skill.** *Done when* it drafts a tla-kit record that passes the claims check, and TOPAK's
   `drafting-records` uses its form.
7. **gov-tla to level 2.** Re-pin to the current release; consume the skill by pin; write its claims table from its
   README and modules. *Done when* tla-kit's evidence run reports gov-tla's claims `IN SYNC`. It is the first
   consumer to reach level 2 and the one a newcomer reads first.
8. **TOPAK generates its table** from its specification graph and binding table. *Done when* the generated table
   passes the check at a named TOPAK commit. This is after ADR-0057 is decided, not before.
9. **The end-to-end agent run.** `agent.yml` grows from one proof repair to: a change request, a draft record with a
   claim, a spec change, the claims check, a person's acceptance left open. Each step checked apart from the agent.
   *Done when* it passes in Actions, and the record it drafted is left Proposed for a person.

Steps 1 to 4 are tla-kit alone. Step 5 needs a TOPAK pull request. Step 8 waits on a TOPAK decision.

---

## 5. Records this needs

In tla-kit, each drafted as Proposed for the custodian:

| Proposed | Title, roughly | Changes |
|---|---|---|
| ADR-0018 | tla-kit is the home of the method and of the coupling, not only of the image | Widens ADR-0001's scope; item 3 ("nothing specific to one project") still binds |
| ADR-0019 | Claims are data: the claims table and what it names | §3.1 |
| ADR-0020 | The claims check, its words, and the `claims` tool, read-only | §3.2; relates to ADR-0006 |
| ADR-0021 | The claims check is a required check; stale claims scope the rerun; results name the image | §3.3; amends ADR-0014 item 1 and ADR-0015 item 8 by History rows |
| ADR-0022 | The skills' source moves here, released with the image | §3.4; supersedes ADR-0007 |
| ADR-0023 | `spec/ClaimsSync.tla` before the check is built | §3.6, as ADR-0016 did for `prove` |

In TOPAK: one record to consume the skill from tla-kit (and retire `skills/writing-tla-specs-and-proofs` as the
source), drafted when ADR-0022 is accepted. In gov-tla: a pin move, and its claims table.

---

## 6. Decisions owed

| | Decision | Recommendation |
|---|---|---|
| E1 | TSV or JSON for the claims table | TSV: edited by people, diffed in review, like the row lists |
| E2 | Claim ids in record text, or only in the table | Both: the id in the record is what lets the check find a checked item with no claim |
| E3 | Whole-file record digests, or per-item | Whole-file, as TOPAK's drift test. Per-item needs a parser of records, and a false `STALE` costs one rerun |
| E4 | Does the records skill ship before or after the claims check | After: it has a check to pass |
| E5 | `ClaimsSync.tla` first, or the script first | The module first, by tla-kit's own habit (ADR-0016 item 2) |
| E6 | One tag for image and plugin, or two release lines | One: a plugin names the image of its own release, and nobody pairs them by hand |

---

## 7. What this does not solve

- **One custodian.** tla-kit, TOPAK and gov-tla have the same custodian. The chain shows that each link is checked,
  not that anyone but its author has read it. The first project at level 2 that is not the custodian's is worth more
  than any step in §4.
- **Who wrote it.** tla-kit's records say most of their choices were the assistant's. The chain makes that visible
  (the **Chosen by** line), and does not change it.
- **Specifications, not code.** A claim is checked of a module. Whether the code does what the module says is a
  separate link (TOPAK's `drift.rs` and trace checks are one way), and the claims table does not supply it.
- **Small constants.** `checked` means every reachable state at the constants the row states, as the results files
  already say. The table carries the grade so that no claim reads as more.
