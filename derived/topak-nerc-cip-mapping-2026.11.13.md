# TOPAK — NERC CIP mapping: TOPAK as a control, and TOPAK as a system CIP would govern

**2026.11.13** · derived · a mapping, not a record · basis: the tree at `981bc77` (`main`), with Genesis
Checkpoint G11 (2026.10.09) as the state of record and `mechanism/GAPS-AND-ASSUMPTIONS.md` for what the reference
builds · the NERC Critical Infrastructure Protection standards as published on nerc.com, read 2026.11.13 (§1) ·
prepared by the assistant at the custodian's request · nothing in the tree outside this file was changed, except
this file's row in `derived/README.md`

**What this is.** The CIP standards are the mandatory cyber security standards for the North American bulk electric
system. They bind a *Responsible Entity* (a balancing authority, a transmission or generator owner or operator, a
reliability coordinator and so on), and nearly every requirement is written as an obligation on that entity's
processes for its people and its Cyber Assets. TOPAK is an architecture pattern for agentic AI and names no grid, no
utility and no control system: before this file, no record or summary mentioned NERC CIP, and the only NERC
citations in the tree are the 2003 blackout scenario's (`derived/scenarios-2026.11.12/2003-NRG-NORTHEAST-BLACKOUT.md`).
So the mapping has to imagine a deployment: **a Responsible Entity that lets AI agents work in or near its control
environment, and governs them with TOPAK.** It reads every CIP requirement twice:

- **Part I, TOPAK as a control.** For each requirement Part, what TOPAK would do for the agent-side half of it: an
  agent is a principal, so where CIP says "individual", "user" or "remote access", what does the pattern enforce,
  and what evidence does it leave?
- **Part II, TOPAK as a subject.** A TOPAK deployment that mediates agents' access to BES Cyber Systems would
  itself be a set of Cyber Assets that CIP governs. What would CIP demand of it, and where does the reference stand?

Part III reads the virtualization revisions FERC approved in 2026, which change several readings and are
enforceable from 2028. Part IV is the nuclear "bright line": the CIP exemption for systems the Nuclear Regulatory
Commission regulates, and what it means for a deployment at a nuclear plant. Part V lists what this suggests.

**What it is not.** Nothing here says a TOPAK deployment would be compliant with anything. Compliance is a
property of an entity's documented processes and their evidence, judged by an auditor; a mark below says only
which half of a requirement the pattern carries. Nothing here is ratified, and no record is changed. It reads the
pattern as the records and the reference stand, including the corpus's own statement that the reference "is not
a deployable system" (`README.md`).

**It is the author's reading of the author's work**, as every derived document in this tree is (P8.8): the corpus
was read by the assistant at the custodian's request, with three readers working by topic. The citations that carry a mark were
spot-checked against the tree, and section numbers the readers gave were corrected where they were wrong; a
reader should still check any row before relying on it.

---

## Contents

- §0 How to read the marks
- §1 Sources, by digest, and which versions are in force
- §2 Where TOPAK would sit: three positions
- §3 Vocabulary: CIP terms and TOPAK constructs, and where each correspondence breaks
- Part I — TOPAK as a control (§4 to §17, one per standard; §18 the count)
- Part II — TOPAK as a subject (§19 requirement by requirement; §20 what blocks position B; §21 why position C is not read)
- Part III — The virtualization revisions (§22)
- Part IV — The nuclear bright line (§23)
- Part V — Reverse deltas (§24), and what to do with this (§25)
- Sources

---

## 0. How to read the marks

**Basis for a Part I mark.** The rule is the one the external alignment of 2026.10.09 used for "matched", carried
over: a mark of **S** needs a record **in force** (Accepted, including author-ratified and provisional, and said
so) **and** a mechanism built in the reference. Intent, a Proposed record, a pending amendment, a SIMULATED rung or
a BOOTSTRAP path does not earn **S**.

| Mark | Part I meaning (TOPAK as a control) |
|---|---|
| **S** | Supports. A record in force and a built mechanism carry the agent-side half of the Part, or produce the evidence the Part asks for. The entity's process still has to exist; **S** is never "compliant" |
| **P** | Partial. In force and built, but it covers only part of the Part, or a caveat the corpus states voids part of it |
| **D** | Designed. A record states it (Accepted or Proposed), but the reference does not build it, or builds it only as SIMULATED or BOOTSTRAP |
| **—** | Nothing. The Part has an agent-side half and the corpus has nothing for it |
| **X** | Out of scope. The Part is about people, places or the entity's own programme, and has no agent-side half |

| Mark | Part II meaning (TOPAK as a subject, at position B of §2) |
|---|---|
| **Met** | The reference already does what the requirement asks of the system |
| **Deploy** | A deployment can supply it around TOPAK (host hardening, a SIEM, a procedure) without changing the pattern or the reference |
| **Gap** | The reference does something the requirement forbids, or lacks something only a change to TOPAK can supply |
| **n/a** | Does not apply at position B |

**Status words** are the corpus's: *Accepted (genesis)*, *confirmation required* (author-ratified; ADR-0029 C1 to
C4), *provisional* (in force, subject to redesign; ADR-0029 A4), *Proposed*, *Built*, *SIMULATED*, *BOOTSTRAP*.
"GAPS I47" means row I47 of `mechanism/GAPS-AND-ASSUMPTIONS.md`; "RRS 1.7" means row 1.7 of
`derived/topak-residual-risk-statement-2026.11.11.md`.

---

## 1. Sources, by digest, and which versions are in force

Every standard was downloaded from `https://www.nerc.com/pa/Stand/Reliability%20Standards/<id>.pdf` on 2026.11.13.
Requirement text quoted below is from these files. The digest is the first sixteen hex digits of SHA-256 over the
PDF.

| Standard | Title | Read as | Digest | Pages |
|---|---|---|---|---|
| CIP-002-5.1a | BES Cyber System Categorization | in force | `747e1ac250b975a2` | 37 |
| CIP-003-9 | Security Management Controls | in force | `b10f255cf8bf3324` | 27 |
| CIP-004-7 | Personnel & Training | in force | `aee6d5262bd4ecd1` | 31 |
| CIP-005-7 | Electronic Security Perimeter(s) | in force | `7c2ff0092259d767` | 17 |
| CIP-006-6 | Physical Security of BES Cyber Systems | in force | `5515b5e7e5176a1d` | 27 |
| CIP-007-6 | System Security Management | in force | `5b7820e758467bbd` | 51 |
| CIP-008-6 | Incident Reporting and Response Planning | in force | `74642c2e4ceb905a` | 20 |
| CIP-009-6 | Recovery Plans for BES Cyber Systems | in force | `0661279b897af87a` | 20 |
| CIP-010-4 | Configuration Change Management and Vulnerability Assessments | in force | `2d2be70f97323738` | 29 |
| CIP-011-3 | Information Protection | in force | `7eb7264737015d73` | 14 |
| CIP-012-1 | Communications between Control Centers | in force | `0302d85d86d16ad1` | 5 |
| CIP-013-2 | Supply Chain Risk Management | in force | `ffb4a30e2ec9e72d` | 10 |
| CIP-014-3 | Physical Security | in force | `7a52842db2df75c6` | 36 |
| CIP-015-1 | Internal Network Security Monitoring | approved; phased in (below) | `52cb4f4d90ba9808` | 9 |
| CIP-003-11 | Security Management Controls (low impact revisions) | approved, future | `923613c248ab0679` | 23 |
| CIP-004-8 | Personnel & Training (virtualization) | approved, future | `9376de2257cf4314` | 24 |
| CIP-005-8 | Electronic Security Perimeter(s) (virtualization) | approved, future | `a636dba5808b2dc2` | 16 |
| CIP-007-7 | System Security Management (virtualization) | approved, future | `9bac9a44fbb0cd1b` | 22 |
| CIP-010-5 | Configuration Change Management (virtualization) | approved, future | `4d811503c1992382` | 24 |
| CIP-011-4 | Information Protection (virtualization) | approved, future | `e5dacb4f0d302e4f` | 10 |
| CIP-012-2 | Communications between Control Centers | approved, future | `045934201de7074f` | 6 |
| CIP-013-3 | Supply Chain Risk Management (virtualization) | approved, future | `fd30ffd3700c9e6c` | 9 |

**Which versions are in force is the weakest fact in this file**, and it was not settled from a primary source.
NERC's effective-date listing is rendered by script and could not be read here, and each standard says only "See
Implementation Plan". What the files themselves show:

- CIP-015-1's version history records "6/26/2025 FERC Order approving CIP-015-1"; its implementation is phased,
  and this file reads it as approved and not yet enforceable at most entities.
- CIP-012-2's history records "May 23, 2024 FERC Order issued approving CIP-012-2".
- The virtualization set (CIP-002-7, CIP-003-10, CIP-004-8, CIP-005-8, CIP-006-7, CIP-007-7, CIP-008-7, CIP-009-7,
  CIP-010-5, CIP-011-4, CIP-013-3) carries "5/9/2024 Adopted by the NERC Board of Trustees" and no FERC line.
  Secondary sources report that FERC approved it in **Order No. 919 on 2026.03.19**, effective 2026.05.26, with
  enforcement 24 months later. They disagree on the date: 2028.04.01 or **2028.07.01**, the latter from
  NERC-based trackers. They also disagree on whether the system-security standard is CIP-007-7 or CIP-007-7.1.
  This file reads the set as approved and enforceable in 2028, and treats the exact date and labels as unverified.
- CIP-003-11 carries "12/10/2024 Adopted by the NERC Board of Trustees", and secondary sources tie it to the
  companion Order No. 918 on low impact systems.

The NERC Glossary of Terms could not be retrieved; the URL tried returned an HTML page. Defined terms (BES Cyber
Asset, EACMS, Intermediate System, Interactive Remote Access, External Routable Connectivity, Protected Cyber Asset)
are therefore used in their ordinary CIP sense, and §3 says what each is taken to mean. A reader who needs the
exact definitions should read the Glossary. **The NRC's rule, 10 CFR 73.54, was not read**: the host serving it
refused the connection. Part IV uses only the CIP-002 text that names it.

---

## 2. Where TOPAK would sit: three positions

What CIP demands of a TOPAK deployment depends on where it sits, and the mapping needs a position before it can be
read. Three are worth naming.

| Position | What the agents do | What TOPAK's own hosts are, under CIP | Read here |
|---|---|---|---|
| **A. Corporate side** | Agents work outside every Electronic Security Perimeter: engineering analysis, procedure drafting, ticket triage, log summarization. They may read BES Cyber System Information (BCSI): diagrams, configurations, IP lists | Not BES Cyber Assets. The agents and the stores they read are in scope of CIP-011 and of CIP-004 R6 (provisioned access to BCSI) only | Part I, rows on CIP-004 R6 and CIP-011 |
| **B. At the perimeter** | Agents reach high or medium impact BES Cyber Systems, read or act, **only through TOPAK's admit path**. TOPAK's nodes sit where a jump host would, and every agent action into the ESP is mediated by them | TOPAK's nodes control and monitor electronic access to BES Cyber Systems: an **EACMS**, and arguably an **Intermediate System**. They inherit most of CIP-004, CIP-005 R2, CIP-007, CIP-009, CIP-010 and CIP-011 at the impact of what they protect | **Part II is read at B** |
| **C. Inside** | Agents' actions are BES functions: an agent issues set points or switching orders, and its loss or misuse would affect reliable operation within fifteen minutes | TOPAK's nodes are BES Cyber Assets (or PCAs) inside the ESP, and the agents' hosts are too. Every CIP-007 and CIP-010 requirement applies to every node | Named, not read. §21 says why the reference could not stand here |

**Position B is the one this file treats as the design point.** It is the position where TOPAK's central claim, that
every effect passes an admit decision with a consensus-ordered, signed, authorizing predecessor (ADR-0015, Accepted
(genesis), C2), does work CIP already asks for: CIP-005 R2.1 asks that "the Cyber Asset initiating Interactive
Remote Access does not directly access an applicable Cyber Asset". It is also the position where TOPAK's own weaknesses
become CIP findings, because an EACMS carries the obligations of what it protects.

**What "an agent" maps to.** CIP has no word for an autonomous software principal. Its access requirements are
written for *individuals* (CIP-004 R4 to R6), *user accounts* and *interactive user access* (CIP-007 R5), and
*Interactive Remote Access* and *system-to-system remote access* (CIP-005 R2). An agent is not an individual, and
a model that types into a session is not "user-initiated" in the sense CIP-007 R5 means. This file reads an agent's
access as **system-to-system remote access that an individual is accountable for**: the operator or seat holder
whose authority the agent's lease derives from. Where that reading is a stretch, the row says so. A Responsible
Entity adopting the pattern would have to settle this reading with its Regional Entity before relying on any row.

---

## 3. Vocabulary: CIP terms and TOPAK constructs

| CIP term (as used here) | Nearest TOPAK construct | Where the correspondence breaks |
|---|---|---|
| Responsible Entity | The deployment, under its declaration (`ADOPTERS_GUIDE_README.md`) | TOPAK has no notion of a registered entity or a compliance programme |
| CIP Senior Manager; delegate | The anchor key-holders and the custodian (ADR-0029, ADR-0045 Annex B) | The custodian governs the *corpus*; a CIP Senior Manager governs the *programme*. The reference has one person in both rows (T-0045-8, T-0045-9) |
| BES Cyber System, impact rating | A domain's principals and the effect classes their alphabets allow | CIP categorizes by consequence to the grid. TOPAK bounds by alphabet and irreversibility, and does not rate impact (§4) |
| Electronic Security Perimeter (ESP) | The membrane: `Contain` and its admit path (ToO §2) | An ESP is a network boundary. TOPAK's membrane is an authority boundary around principals, not around hosts, and at the reference every real principal is `Mediated`, so nothing confines the host (GAPS G1) |
| Electronic Access Point (EAP) | The MCP front door and the admit decision behind it (`topak-mcp/src/server.rs:1`) | A shell outside a launcher bypasses it: "the largest gap" (GAPS G1) |
| Interactive Remote Access, Intermediate System | An agent's tool call, admitted and actuated by the tool host, never by the agent (`toolhost.rs`) | IRA is human and interactive. An agent's access is neither (§2) |
| Multi-factor authentication | The operator's signed request plus a sign-on assertion under a provider key the rules issue (ADR-0050, provisional) | No identity provider exists at the reference; "the mechanism cannot tell a person from a program holding the person's key" (ADR-0050:82) |
| Authorization record; access revocation | A seat declared in the issued rules; a lease; revocation and the epoch fence (ADR-0031) | CIP counts in days (24 hours, next calendar day, 30 days); TOPAK's revocation is one log position, and states no time |
| Baseline configuration | The pinned floor, schema and values digests; the bundle's signed revision; the parameter digest carried in every admit | CIP's baseline is per Cyber Asset (OS, software, ports, patches). TOPAK pins authority artifacts and not hosts |
| Security event log | The round topic and the admit log entry (ADR-0003, ADR-0020) | No retention value, no alerting, no review interval; the archive is rebuilt and truncated at each start (GAPS G9) |
| CIP Exceptional Circumstances | Emergency seating (ADR-0052, provisional) | CIP excuses named obligations during an emergency. TOPAK grants a bounded, quorum-activated seat and suspends nothing |
| BCSI | Content carrying a label (ADR-0047); the `clearSet` | CIP protects information by *what it is*. TOPAK labels it by *where it came from*, never by content (P9) |
| Cyber Security Incident; Reportable | A finding; a Contested verdict; a revocation | TOPAK has no incident classification and no outward notification (§11) |
| Transient Cyber Asset | A launched guest at a rung (ADR-0034) | A TCA is a laptop or a diagnostic tool; a guest is a container. The analogy is loose |
| INSM data feed | Observer seats reading round topics (ADR-0038, ADR-0039) | INSM watches *network* traffic inside the ESP. Observers watch *principals' records*, and the reference runs no correlation (RRS 1.3) |

**The floor in force.** Many rows below rest on floor entries (`B10`, `R1`, `R3`, `R5` to `R7`, `C1` to `C9`). The
floor in force is a **genesis-provisional** stage (ADR-0030 A3, Batch 34): gated, pinned and enforced, and
ratified only when a bootstrap reviewer finds it fit. Since 2026.10.08 the reference has linked a later stage, the
workflow floor, which is **not in force** and contains every entry of the stage that is (GAPS, the floor rows). This
file counts an entry of the in-force stage as in force, as it counts a provisional record, and does not repeat the
caveat on every row.

---

# Part I — TOPAK as a control

Each row is one requirement Part, quoted short. The column "TOPAK" names what the pattern would bring to the
agent-side half; "Basis" gives the record or code and the caveats the corpus states. Rows marked **X** have no
agent-side half and are kept so that the count in §18 covers every Part.

## 4. CIP-002-5.1a — BES Cyber System Categorization

| Part | Requirement | TOPAK | Mark | Basis and caveat |
|---|---|---|---|---|
| R1 (1.1 to 1.3) | Identify high, medium and low impact BES Cyber Systems by the criteria of Attachment 1 | No impact rating. The nearest construct bounds each effect class by time, not by consequence: `W + L + D < T_irrev`, and an effect that cannot meet it "must not be reachable from the alphabet at all" | **D** | ADR-0032 §4 (Accepted (genesis)). "No deployment has declared a `T_irrev` for any class" (RRS §5). Irreversible entries "reachable by a person only" are ADR-0066 (**Proposed**, not built; `spec/Release.tla` `IrreversibleIsAPersons` proved). An agent's reach is its alphabet (ADR-0037 §4, ADR-0040), and a deployment would have to rate each alphabet entry against Attachment 1 itself |
| R2 (2.1, 2.2) | Review the identifications and have the CIP Senior Manager approve them every 15 calendar months | — | **X** | An entity programme obligation. The corpus has no calendar cycle of any kind: "No forcing function", "Genesis may continue indefinitely" (ADR-0029 §7) |

## 5. CIP-003-9 — Security Management Controls

| Part | Requirement | TOPAK | Mark | Basis and caveat |
|---|---|---|---|---|
| R1 | Documented policies for CIP-004 to CIP-011, approved by the CIP Senior Manager every 15 months | — | **X** | Programme. The corpus's records are a design's policies, not an entity's |
| R2, Att. 1 §1, §2 | Low impact: cyber security awareness; physical security controls | — | **X** | People and places |
| R2, Att. 1 §3 | Low impact: electronic access controls (permit only necessary inbound and outbound access, detect malicious communications) | The admit path: only declared tools, only declared channels, fail closed | **P** | `admit ⟺ floor_permit ∧ ¬bundle_deny`, and the bundle denies when it "errors, returns undefined, is absent, or cannot be reached" (ADR-0030 §1, Accepted (genesis), C1). Allowlist entries with a single declared `channel` (ADR-0049, C4; GAPS I33, I44). "A native Run tool that opens a channel it did not declare is not seen by anything" (GAPS G19). Section 3 is about routable network access at an asset, which TOPAK does not control |
| R2, Att. 1 §4 | Low impact: Cyber Security Incident response plan | See §10 | **P** | As CIP-008 R1: stop tools are built; identification, classification and notification are absent |
| R2, Att. 1 §5 | Low impact: Transient Cyber Asset and Removable Media malicious code mitigation | — | **—** | Nothing in the corpus addresses removable media. A launched guest (ADR-0034) is not a TCA (§3) |
| R2, Att. 1 §6 | Low impact: determine and disable vendor electronic remote access; detect malicious communications on it | Live leases are replicated state, and any operator can revoke one alone | **P** | Revocation and the epoch fence (ADR-0031, C1; built; `RevokedStaysStopped` proved). Nothing in the rules marks a seat as a vendor's, so "determining vendor access" needs a declaration the pattern lacks. Detection: as §7, 1.5 |
| R3 | Identify a CIP Senior Manager by name | — | **X** | Programme. The corpus names its custodian (ADR-0029 §1), who governs the corpus, not a deployment |
| R4 | Document delegations of the CIP Senior Manager's authority | — | **X** | Programme. Agents' authority, by contrast, is delegated only by signed anchor issuance and promotion, and every such change is on the log (ADR-0015, ADR-0024); that is evidence of *agent* delegation, not of the CIP Senior Manager's |

## 6. CIP-004-7 — Personnel & Training

| Part | Requirement | TOPAK | Mark | Basis and caveat |
|---|---|---|---|---|
| 1.1 | Quarterly security awareness for personnel with access | — | **X** | People |
| 2.1 to 2.3 | Training content; training before access; training every 15 months | — | **X** | People. For the people the pattern does name: "Nothing in the corpus states what skill or training an operator, an emergency-seat holder or a grant-seat holder must have" (feature list F5.6, Open); assumption of use A5, "a trained, authorized human present", is "Not met" (RRS §6) |
| 3.1 | Process to confirm identity | For an agent: its Persona, attested at grant and at each renewal, bound into the lease | **P** | Persona attestation (ADR-0016; lease fields, ADR-0031 §1, C1; built). "Silent substitution is undetected for granted principals" (GAPS G13). The person behind an operator is not identified: "the mechanism cannot tell a person from a program holding the person's key" (ADR-0050, provisional) |
| 3.2, 3.3, 3.5 | Seven-year criminal history check; criteria; renewal every seven years | — | **X** | People |
| 3.4 | Verify that contractors' and vendors' personnel risk assessments meet 3.1 to 3.3 | The agent-side analogue is the model's provenance, read under CIP-013 (§15) | **X** | People; see §15, 1.1 |
| 4.1 | Authorize electronic access based on need | A seat is declared in the issued rules, which every anchor key signs; its alphabet is bounded by seat kind; each allowlist entry carries a `purpose` | **P** | Seats in the rules (GAPS I8, I7); alphabets by seat kind (ADR-0037 §4, Accepted; floor `B10`); entries with `purpose` (ADR-0049; GAPS I33). **Who holds a seat** is not authorized by a quorum at the reference: "whoever reaches the socket can seat" (GAPS I47(a), BOOTSTRAP), though ADR-0050 (provisional) requires a first lease from a quorum and proves it of its module |
| 4.2 | Verify each quarter that everyone with active access has an authorization record | By construction a lease exists only for a seat in the signed rules, so the record is the rules; the check is mechanical and continuous, not quarterly | **P** | As 4.1. The binding of a principal to a seat is the BOOTSTRAP path's, so the record shows the seat, not who was authorized to take it |
| 4.3 | Every 15 months, verify that accounts, groups, roles and privileges are correct and necessary | The privileges are artifacts a reviewer can read: the rules, the seat kinds' alphabets, the bundle's allowlist | **P** | Artifacts exist and are digested (§12). Whether they are *necessary* is a judgment the pattern does not make |
| 5.1 | On termination, remove the ability for Interactive Remote Access within 24 hours | Targeted revocation, or the fleet-wide epoch fence: "the effect is immediate, not bounded by remaining TTL" and takes effect at its log position | **S** | ADR-0031 §5 (Accepted (genesis), C1); built (`state.rs` `apply_revoke`); `NoActionUnderFencedEpoch` and `RevokedStaysStopped` proved (`spec/Lease_A1_proof.tla`). An admit decided before the revocation and committed after it is void at apply (ADR-0033 §4). A tool call already running when the round seals is not aborted (read from the code, not stated in a record); it is written as `unknown` before the seal marker, and "a call that returns after the seal delivers nothing" (ADR-0042 §3; `mechanism.rs`), and the in-flight registry is per replica (GAPS I29). The termination that triggers the revocation is the entity's process |
| 5.2 | On reassignment, revoke unneeded access by the end of the next calendar day | Revocation; and every lease lasts one round, so a seat not regranted lapses on its own | **S** | As 5.1. `ttl ≤ T_persona` (ADR-0031 §1), where `T_persona` is "a placeholder one hour" (GAPS I35) |
| 5.3 | On termination, revoke non-shared user accounts within 30 days | Revocation is permanent within the rules-epoch chain | **S** | ADR-0031 §5 |
| 5.4 | On termination or transfer, change passwords of shared accounts the person knew within 30 days | No shared credential exists: a principal holds exactly one seat, and a session token is minted per grant | **S** | ADR-0037 §1 (Accepted; "one seat per principal" proved in Lean and model-checked, GAPS §6); token per grant (`mechanism.rs`). The *operators'* and anchor keys are another matter (§19) |
| 6.1 | Authorize provisioned access to BCSI before provisioning it | Delivery by label: a seat kind receives a labelled item in the clear or as a handle, as the delivery table says | **P** | ADR-0047 §2 (Accepted (genesis), C4; C2 for §3); built (GAPS I46); `spec/Labels.tla` proved (`NoUnlabelledDelivery`, `ClearSetCoversGuest`). A label "is the word of whoever issued the bundle" (RRS 1.8), and "every label forbid is conditional on these being right" (T-0045-33, excluded) |
| 6.2 | Verify every 15 months that BCSI access is authorized and still needed | The delivery table is an artifact a reviewer can read | **P** | As 6.1, and as 4.3 |
| 6.3 | On termination, remove the ability to use BCSI access by the next calendar day | Revocation ends delivery at once; what a round already read cannot be recalled | **P** | As 5.1. Content delivered in the clear has left; the seal stops further rounds, not memory |

## 7. CIP-005-7 — Electronic Security Perimeter(s)

| Part | Requirement | TOPAK | Mark | Basis and caveat |
|---|---|---|---|---|
| 1.1 | Every routable Cyber Asset of the system resides within a defined ESP | — | **X** | Network architecture. TOPAK's membrane bounds authority, not hosts (§3) |
| 1.2 | All External Routable Connectivity through an identified EAP | Every agent effect passes the MCP front door and an admit decision; the front door exposes "the action alphabet, and nothing else" | **P** | ADR-0015 (Accepted (genesis), C2); `topak-mcp/src/server.rs`. "An agent with a shell outside a launcher still bypasses the MCP front door. The largest gap" (GAPS G1); every real principal is `Mediated`; rung 1 "confines nothing", rung 2 is a seam, rung 3 is SIMULATED (GAPS I42). At position B the entity must ensure the agent has no other route |
| 1.3 | Inbound and outbound permissions with a reason for each; deny all else by default | Default deny on every decision; an allowlist entry per tool with one declared `channel` and a `purpose` | **P** | ADR-0030 §1 and ADR-0012 ("Fail-closed is reachable with no network dependency"); ADR-0049 (W1 to W9 checked at load, a bundle that fails "does not load"); built. Native tools' undeclared channels are unseen (G19), and Build tools are all native (T-0045-23). The `purpose` field's meaning is read, not stated |
| 1.4 | Authenticate Dial-up Connectivity | — | **X** | Not applicable to the pattern |
| 1.5 | Detect known or suspected malicious communications, inbound and outbound | Flow forbids at the admit: F1 "read, then send", F2 "steered destination", F3 "replayed content" | **P** | ADR-0047 §7 (C4); built (GAPS I46); proved in `spec/Labels.tla` (`NoReadThenSend`, `NoSteeredDestination`). These *prevent* a shape of exfiltration; they do not *detect* malicious content, and by principle never will: "a label is not a judgment about content" (P9). "This is a minimum and it is not complete" (ADR-0047). A failed call's error text is delivered "unlabelled and in the clear" (GAPS I46) |
| 2.1 | Interactive Remote Access through an Intermediate System, so the initiator does not directly access the Cyber Asset | The agent never touches a target: the tool host actuates, over stdio with `env_clear()`; a Wasm Run tool can reach only its declared target | **P** | The pattern's central structure (ADR-0015, ADR-0040); `toolhost.rs`, `wasmtool.rs` (GAPS I44). Caveats as 1.2 and 1.3. An agent's access is not *interactive* in CIP's sense (§2) |
| 2.2 | Encryption terminating at the Intermediate System for IRA sessions | — | **—** | Nothing at the reference encrypts: the front door is stdio, replicas speak plain TCP, Kafka has no TLS (§19) |
| 2.3 | Multi-factor authentication for all IRA sessions | For operators: a signed request, a counter, and a sign-on assertion under a provider key the rules issue. For agents: a bearer token | **D** | ADR-0050 (provisional); built for operators (`state.rs`; `OperatorLeaseWasVouched` proved), but no identity provider exists (T-0045-35, T-0045-36: "None") and "no clock is read", so one assertion covers every deny until the operator is seated again (GAPS I47(d)). Agents: a bearer token minted at grant; "Real principal authentication" is listed as owed (GAPS I14, G5) |
| 2.4 | Determine active vendor remote access sessions, IRA and system-to-system | Every live lease is in the replicated state; a vendor's agent would be a seat like any other | **P** | Leases in state (ADR-0031; built). No seat is marked as a vendor's; the rules would need the attribute |
| 2.5 | Disable active vendor remote access | Revocation, by any operator alone, signed, with no quorum | **S** | ADR-0031 §5 (C1); ADR-0050 §4 ("denies need neither" a lease nor a peer; provisional); built; `DenyAlwaysAvailable` proved (`spec/Operators.tla`). In-flight caveat as §6, 5.1. At the reference the unsigned socket also revokes where no operator is declared (D-0050-1) |
| 3.1 | (EACMS and PACS) Determine authenticated vendor-initiated remote connections | As 2.4 | **P** | As 2.4 |
| 3.2 | (EACMS and PACS) Terminate them and control the ability to reconnect | Revocation is permanent in the rules-epoch chain; reconnecting needs a new seating | **S** | `RevokedStaysStopped` (proved); ADR-0031 §5 |

## 8. CIP-006-6 — Physical Security of BES Cyber Systems

| Part | Requirement | TOPAK | Mark | Basis and caveat |
|---|---|---|---|---|
| R1 (1.1 to 1.10), R2 (2.1 to 2.3), R3 (3.1) | Physical security plan, perimeters, two-factor physical access, monitoring and alarms within 15 minutes, entry logs for 90 days, cabling, visitor escort and logs, PACS testing every 24 months (14 Parts) | — | **X** | Places. The corpus says so itself: "a person with physical access to a host is outside it" (ADR-0050). Rung 3's residuals include "side channels, physical memory interposers: not prevented" (ADR-0034), and the CPU root of trust is "None; SIMULATED by a test key" (T-0045-16) |

## 9. CIP-007-6 — System Security Management

| Part | Requirement | TOPAK | Mark | Basis and caveat |
|---|---|---|---|---|
| 1.1 | Enable only the logical network ports that are needed | The agent-side analogue of a port is an action: alphabets are bounded by seat kind, an `operator` seat is issued no action variant, and a Run tool is callable only if allowlisted | **S** | ADR-0037 §4 (Accepted (genesis)); floor `B10`; ADR-0049; GAPS I13, I33, I45, I47. The record's digest over an entry's inputs is "not followed" (GAPS I13). The *ports* of TOPAK's own hosts are §19 |
| 1.2 | Protect against unneeded physical input/output ports | — | **X** | Places |
| 2.1 | Patch management: track sources of security patches for each updateable Cyber Asset | — | **—** | Nothing tracks advisories for a Persona, a tool or a model. Pinning makes every update a change (ToO §6, "The model is pinned"), which §12 reads |
| 2.2 | Evaluate new security patches at least every 35 days | — | **—** | As 2.1. The corpus states no time-based cycle |
| 2.3 | Within 35 days of evaluation: apply, or create or revise a dated mitigation plan | — | **—** | As 2.1. An "incident deny" bundle (ADR-0031) is the nearest mitigation instrument, and nothing ties it to a vulnerability |
| 2.4 | Implement each mitigation plan in its timeframe, or have the CIP Senior Manager approve an extension | — | **X** | Programme |
| 3.1 | Deploy methods to deter, detect or prevent malicious code | The premise is that the agent may be malicious at every position: models are outside the TCB, and every guarantee is stated against an agent doing anything its alphabet allows. Confinement rungs; capability-bounded Wasm tools | **P** | ADR-0007 and ToO §1; ADR-0034 §2 (C2, C4); rung-1 launcher runs Docker with `--network none --read-only --cap-drop` (`topak-contain/src/docker.rs`). But "every principal … is `Mediated`" (GAPS G1), rung 1 "confines nothing" for a host process, and rung 3 is SIMULATED. RRS: "At the reference today every theorem about confinement, gate evidence, tool hermeticity and effect-channel fidelity is void" |
| 3.2 | Mitigate the threat of detected malicious code | Revocation; a *Contested* verdict orders a targeted revocation | **P** | Revocation as §6, 5.1 (**S** on its own). *Contested* (ADR-0034, C2, C4; `ContestedStopped` proved) cannot occur at rung 1 and rung 3 is SIMULATED, and no Observer produces a finding (GAPS G12), so the *detection* that would trigger it is absent |
| 3.3 | Update signatures or patterns for signature-based methods | — | **X** | TOPAK uses no signature-based detection, and by P9 never judges content |
| 4.1 | Log, for after-the-fact investigation: successful logins; failed access and login attempts; detected malicious code | The round's record holds "actions attempted, including those denied", effects, lease and epoch transitions; each admit entry carries its input, floor, schema, bundle, engine and parameter digests and the floor's reasons | **P** | ADR-0020 (Accepted (genesis)); ADR-0003 (round topics, sealed; an `after` companion for denials after the seal; built, GAPS I17, I23); `topak-core/src/state.rs` admit entry; unauthenticated attempts go to a `security` tracing target on stderr (GAPS I23). 4.1.1 and 4.1.2 have analogues (a lease's opening record; a deny). 4.1.3 does not: nothing detects (3.2). A denial is ordered by "Nothing" (ADR-0005), and no record is chained or signed |
| 4.2 | Alert on detected malicious code and on failure of event logging | Nothing alerts. One reaction is stronger than an alert: a Run admit is refused when its cell's Observer has stopped reading (floor `R3`, coupling) | **P** | Coupling (ADR-0039, ADR-0038; built, GAPS I27; Lean-proved for a model of apply). That covers the *Observer* failing, not the *log* failing: the archive is written with `let _ = writeln!`, so a write error is ignored (`topak-node/src/mechanism.rs`) |
| 4.3 | Retain logs for at least the last 90 days | The forensic floor: admits, stops, votes, issuances, break-glass and erasures are "non-erasable for the declared horizon" | **D** | ADR-0028 (Accepted (genesis), C1). No horizon is declared, no retention is configured on any topic, the per-replica archive is rebuilt and truncated at each start, and there is "No governed store, no horizon, no audit-authority read path" (GAPS G9); no compaction, so the log grows without bound (G14) |
| 4.4 | Review a summary or sample of logs at least every 15 days | Observer seats read every round topic, continuously; a correlator reads across cells | **D** | ADR-0038 (Accepted (genesis), C3, C4); heartbeats built. But "No Observer or correlator judges anything" (GAPS G12), the five correlations are ADR-0051 (**Proposed**), and "Detection fails open against a colluding Observer" (RRS 1.3). The reader is seated; the review is not done |
| 5.1 | Enforce authentication of interactive user access | Operators sign each control request with a counter and replay refusal; agents present a bearer token; attested guests sign session proofs | **P** | ADR-0050 (provisional; built, GAPS I47); bearer token (GAPS I14); guest session proofs (I41) are SIMULATED at rungs 2 and 3. Where the rules declare no operator, the unsigned socket acts (D-0050-1, the shipped dev rules) |
| 5.2 | Inventory enabled default and generic account types | Every seat is declared in the rules; there is no generic or default principal | **S** | GAPS I8 (`rules.rs` `SeatDecl`). Dev keys and dev rules are TOPAK's own defaults (§19) |
| 5.3 | Identify individuals with access to shared accounts | A principal holds exactly one seat; nothing is shared | **S** | ADR-0037 §1, §7 (proved). Shared *keys* outside the mechanism (the anchor store) are §19 |
| 5.4 | Change known default passwords | No default credential reaches an agent: tokens are minted per grant | **S** | `mechanism.rs` (grant). The shipped dev secrets are TOPAK's own (§19) |
| 5.5 | Password length and complexity for password-only authentication | — | **X** | The pattern uses keys and tokens, not passwords |
| 5.6 | Password change at least every 15 months | Credentials expire with the lease, at most `T_persona` | **S** | ADR-0031 §1 (C1); `T_persona` a placeholder (GAPS I35) |
| 5.7 | Limit unsuccessful authentication attempts, or alert after a threshold | Unauthenticated attempts are logged; nothing limits or alerts | **—** | GAPS I23 (`security` target, stderr only) |

## 10. CIP-008-6 — Incident Reporting and Response Planning

| Part | Requirement | TOPAK | Mark | Basis and caveat |
|---|---|---|---|---|
| 1.1 | Processes to identify, classify and respond to Cyber Security Incidents | *Respond*: revocation, the epoch fence, `EndRound`, all deny actions any operator may take alone. *Identify* and *classify*: nothing | **P** | ADR-0031 §5 (C1); ADR-0050 §4 (provisional); built; `DenyAlwaysAvailable` proved. No record defines incident classification; "incident" appears only as a bundle cadence and as "incident deny" bundles (ADR-0016, ADR-0031) |
| 1.2 | Criteria for attempts to compromise; determine Reportable incidents; notify per R4 | — | **—** | Nothing |
| 1.3 | Roles and responsibilities of incident response groups or individuals | The roles the mechanism knows: operators (at least three per domain, a peer rule), the break-glass roster and its quorum, Observers | **P** | ADR-0050 §4, §6 (provisional); ADR-0052 (provisional); ADR-0038. These are roles in the mechanism, not a response team's duties |
| 1.4 | Incident handling procedures | Emergency seating: a roster quorum activates one named person for one round, under a bounded envelope; every action is signed and on the log | **D** | ADR-0052 (Accepted (genesis), provisional); built (GAPS I48); `EmergencyLeaseHasARosterQuorum`, `ActivationIsForensic` proved (`spec/Emergency.tla`). The seating is prepared by an unsigned BOOTSTRAP call, there is "no socket path for a person's signed action", and the one-round rule "is held by the reference, and not by the floor" (RRS 1.17). A procedure is still the entity's |
| 2.1 | Test the plan at least every 15 months | The emergency path "is exercised at least once in each domain in each epoch, and periodically after that"; a drill seating has one tool with no outward channel | **D** | ADR-0052 §6 (provisional); the drill mark is built (`control.rs`; test `a_drill_is_a_real_activation_on_the_log`). The period is counted in rounds, not time; "nothing counts it or reports it" (GAPS I48); the drill is unmeasured (RRS) |
| 2.2 | Use the plan in a response or exercise; document deviations | Every action under an emergency seat is a forensic record, so what was done is on the log | **P** | `ActivationIsForensic` (proved); ADR-0028 F5. Deviation from a *plan* is not a concept the pattern has |
| 2.3 | Retain records of Reportable incidents and attempts | The forensic floor | **D** | As §9, 4.3 |
| 3.1, 3.2 | Lessons learned within 90 days; update the plan within 60 days of a change; notify roles | — | **X** | Programme. The corpus's own findings registers and reviews are a design's lessons-learned loop, not an operation's |
| 4.1 | Notifications include functional impact, attack vector, level of intrusion | The log says what each agent attempted, what was admitted and what was denied, which answers "level of intrusion achieved or attempted" for the agent-side half | **P** | ADR-0020; as §9, 4.1 (no tamper evidence; a compromised replica forges admits, RRS 1.7) |
| 4.2, 4.3 | Initial notification within one hour (or by the end of the next day for attempts); updates within 7 days | — | **X** | Programme. The pattern has no outward reporting channel |

## 11. CIP-009-6 — Recovery Plans for BES Cyber Systems

| Part | Requirement | TOPAK | Mark | Basis and caveat |
|---|---|---|---|---|
| 1.1, 1.2 | Conditions for activating the recovery plan; roles of responders | — | **X** | Programme |
| 1.3 | Backup and storage of the information needed to recover | The control state is replicated by Multi-Paxos with a durable write-ahead log replayed after a crash | **P** | Sans-IO crash-fault Multi-Paxos (`mechanism/README.md`); `topak-node/src/wal.rs`; 120 simulated runs under drop, duplication, reordering, partition and crash-recovery (ADR-0033 §7). Payloads "live only on the deciding replica and in Kafka", workspaces are not replicated (GAPS G9), there are no snapshots (G14), and no procedure backs up keys, rules or the archive |
| 1.4 | Verify that backups succeeded; address failures | — | **—** | Nothing |
| 1.5 | Preserve data for determining the cause of an incident; preservation must not impede recovery | The forensic floor, and the per-replica archive | **D** | ADR-0028 (C1). The archive is "a projection of the log rebuilt on restart" and is truncated when it is opened (GAPS G9; `mechanism.rs`); appraisal evidence is kept only by the appraising node (GAPS I40); "No inherited forensic read access" after re-genesis (G17) |
| 2.1, 2.3 | Test the plan every 15 months; operational exercise every 36 months | — | **X** | Programme. The simulation tests exercise the replica protocol, not a plan |
| 2.2 | Test a sample of recovery information every 15 months for usability and compatibility | WAL replay is exercised by the crash-recovery runs; trace validation replays recorded traces through `spec/Mechanism.tla` | **P** | ADR-0033 §7; trace validation "83 traces, 1,053 steps, 82 matching" at the 11.11 review (RRS 1.6). Neither tests a restore of keys or rules |
| 3.1, 3.2 | Lessons learned and plan updates | — | **X** | Programme |

## 12. CIP-010-4 — Configuration Change Management and Vulnerability Assessments

| Part | Requirement | TOPAK | Mark | Basis and caveat |
|---|---|---|---|---|
| 1.1 | Baseline configuration: OS or firmware, commercial and open-source software, custom software, logical ports, security patches | A baseline of the *authority layer*: the floor, schema and values pinned by digest; the bundle's signed content revision; the parameter digest; each tool's digest of binary and schema | **P** | Floor pinned (`PINNED_*_SHA256`, refused on mismatch at load; `topak-floor/src/lib.rs`); bundle identity is its SHA-256 revision (ADR-0044 §2, Accepted (genesis), C1; GAPS I3); `Params::digest` carried in every admit (GAPS I21); tool digest re-checked on every call (ADR-0049; GAPS I13). Nothing records the OS, packages or patches of an agent's host (1.1.1, 1.1.2, 1.1.5) |
| 1.2 | Authorize and document changes that deviate from the baseline | A bundle loads only under a signature by a key the rules issue, and the record says it is signed after the promotion's tally; the rules change only by an issuance every anchor key signs; profiles and workflows load only if promoted | **P** | ADR-0044 §3, §4; GAPS I7, I34; ADR-0024 (promotion by unanimous quorum; built). In the reference, signing is "a script step with a dev key, not a promotion pipeline" (T-0045-27), "Gate evidence is asserted" (GAPS G8), and profile and workflow promotion rests on Proposed records (ADR-0036; ADR-0054, ADR-0055) |
| 1.3 | Update the baseline within 30 days of a change | The digest is the baseline: whatever is loaded is what every admit names | **S** | As 1.1. A change reaches a principal at its next grant (GAPS I4), and every admit carries the digests it was decided under |
| 1.4 | Before a change, determine which CIP-005 and CIP-007 controls it could affect; after it, verify they are not adversely affected; document it | Floor revisions "are classified mechanically": Equivalent, Tightening, or Relaxation, and a relaxation needs an anchor issuance as well as a promotion | **D** | ADR-0030 §5 (Accepted (genesis)). No classifier of that name was found in `floor/`, `mechanism/` or `tools/`. The classing covers the floor only, not the bundle tier or the host. This is the row the virtualization revision moves (§22) |
| 1.5 | Test changes in a test environment that models the baseline, before production (high impact) | Gates enable voting: totality, non-vacuity and discrimination on the floor; gate suites, mutation tests, trace validation | **P** | ADR-0024 §4; ADR-0030 §5; `floor/run-gates.py` (123 cases replay through the linked engine); GAPS §6. `GatesPassed` is unsigned and "Every promotion theorem that assumes gates ran is void" (T-0045-13, excluded). The live smoke run "cannot complete against this tree" (self-review annex, J-3) |
| 1.6 | Before a change, verify the identity of the software source and the integrity of the software | Bundle signature under issued keys; tool digests on every call; the floor's pinned digests | **S** | ADR-0044 §3 (C1); ADR-0049; built. The bundle key is a dev key held by one person (T-0045-27). For a model, the Persona is attested at grant, and silent substitution is undetected after it (GAPS G13) |
| 2.1 | Monitor at least every 35 days for changes to the baseline; investigate unauthorized ones | For the authority layer, every decision is a check: apply refuses an admit whose parameter digest differs; the floor refuses to load on a digest mismatch. For the corpus: pinned-record drift tests and manifests | **P** | GAPS I21; `topak-floor/src/lib.rs`; `topak-core/tests/drift.rs` over `mechanism/corpus-pins.sha256`; `tools/verify-manifest.sh`. These run by hand; there is no CI. "The reference tree at this commit is measured by no manifest" (J-1). Hosts are not monitored |
| 3.1 | Paper or active vulnerability assessment every 15 months | The pattern's worst case is standing: every guarantee is stated against an agent doing anything its alphabet allows. The design has had critical reviews and an open findings register | **P** | ToO §1; `derived/topak-critical-review-2026.11.11.md`; `derived/topak-open-findings-register-2026.11.11.md` (460 rows). These assess the *design*, by its author's own lineage; no deployment has been assessed |
| 3.2 | Active vulnerability assessment every 36 months | — | **—** | Nothing |
| 3.3 | Active assessment of a new Cyber Asset before production | — | **—** | Nothing. A new principal's Persona is attested at grant (ADR-0016), which is not a vulnerability assessment |
| 3.4 | Document results, a remediation plan and its status | Findings carry identifiers, grades and status across reviews | **P** | The open findings register (252 open of 460). It records the design's findings, not a deployment's |
| R4 (Att. 1) | Transient Cyber Assets and Removable Media: authorization, malicious code mitigation, vulnerability mitigation | A launched guest is appraised against a promoted confinement profile at grant | **D** | ADR-0034 §3 (C2, C4); appraisal built (GAPS I37 to I41) at rung 1, which "confines nothing", and a SIMULATED rung 3. Removable media: nothing |

## 13. CIP-011-3 — Information Protection

| Part | Requirement | TOPAK | Mark | Basis and caveat |
|---|---|---|---|---|
| 1.1 | Methods to identify BCSI | A label on every item of ingress, as a function of its source. A deployment would declare its BCSI stores (the EMS configuration repository, network diagrams) as sources with a restricted label; a bundle with an undeclared label "does not load" | **S** | ADR-0047 §1 (Accepted (genesis), C4); built (GAPS I46). The label identifies *where* an item came from, not *whether* it is BCSI: content from an unlabelled-as-BCSI source is not caught (P9). Labels are "the word of whoever issued the bundle" (RRS 1.8) |
| 1.2 | Methods to protect and securely handle BCSI to reduce the risk to confidentiality | Clear or handle delivery per seat kind; `clearSet` only grows; F1 refuses a call that carries private content out after untrusted content was read | **P** | ADR-0047 §2, §7; `spec/Labels.tla` proved (`NoReadThenSend`, `SuppressedNeverInGuest`). A failed call's error text is returned "unlabelled and in the clear" (GAPS I46); native tools' undeclared channels are unseen (G19); nothing encrypts at rest or in transit; T-0045-33 is excluded |
| 2.1 | Before reuse of a Cyber Asset holding BCSI, prevent retrieval from its storage | Guests run read-only with no network; handles to results are held in memory and dropped at the seal | **X** | Media reuse is the entity's. Erasure (ADR-0006, Accepted (genesis), C1) is about the log, and is "Not implemented" (GAPS G11) |
| 2.2 | Before disposal, prevent retrieval or destroy the media | — | **X** | Places and media |

## 14. CIP-012-1 — Communications between Control Centers

| Part | Requirement | TOPAK | Mark | Basis and caveat |
|---|---|---|---|---|
| 1.1 to 1.3 | A plan protecting Real-time Assessment and Real-time monitoring data between Control Centers against unauthorized disclosure and modification: the protection, where it is applied, and who is responsible when the centers belong to different entities | Signatures cover what changes authority: issuances, bundles, control requests, sign-on assertions, verifier verdicts (Ed25519, domain-separated). Nothing covers data in transit between sites | **—** | `authentic.rs` (GAPS I7, I34). Replica frames are "unauthenticated JSON over plain TCP … mutual TLS between replicas is required before this leaves a lab" (`topak-node/src/net.rs`); Kafka has no TLS or SASL (`topak-transport/src/lib.rs`); the PBFT overlay's signed messages are ADR-0061 (**Proposed**, not built). Agents do not carry real-time data in any position this file reads, so the agent-side half is small |

## 15. CIP-013-2 — Supply Chain Risk Management

| Part | Requirement | TOPAK | Mark | Basis and caveat |
|---|---|---|---|---|
| 1.1 | Identify and assess risks from vendor products and services, including transitions between vendors | The provenance axis: "The archetype admits only Personas pre-trained in house"; a model from outside is `Mediated`, and its prompt egress is "an out-of-band effect" | **P** | ADR-0017 (Accepted (genesis)), which re-derives SLSA and in-toto. Lineage independence, the rule that would make two vendors' models count as independent, is ADR-0035 (**Proposed**), its threshold is "unset", and the rehearsal "does not prove the guarantee" (`slm/README.md`; RRS 1.16) |
| 1.2.1 | Vendor notification of incidents affecting its products | A Persona can be revoked on "provider disclosure" | **P** | ADR-0016 §7. The hook acts on a notification; nothing receives one |
| 1.2.2 | Coordinated response to vendor-identified incidents | — | **—** | Nothing |
| 1.2.3 | Vendor notification when remote or onsite access should end | Revocation | **P** | As §6, 5.1. The notification is the entity's |
| 1.2.4 | Vendor disclosure of known vulnerabilities | — | **—** | Nothing for a deployment. The corpus discloses defects in its own trust root (§19) |
| 1.2.5 | Verify the integrity and authenticity of vendor software and patches | Tool digests on every call; bundle signatures; the Persona attested at grant | **P** | ADR-0049, ADR-0044, ADR-0016; built. Silent model substitution after grant is undetected (GAPS G13); "no reproducible build" (T-0045-30) |
| 1.2.6 | Coordinate controls for vendor-initiated remote access | A credential injected by the tool host per subject, which the Thinker never sees | **D** | ADR-0056 (**Proposed**, not built) |
| R2 | Implement the plan | — | **X** | Programme |
| R3 | CIP Senior Manager approves the plan every 15 months | — | **X** | Programme |

## 16. CIP-014-3 — Physical Security

| Part | Requirement | TOPAK | Mark | Basis and caveat |
|---|---|---|---|---|
| R1 to R6 | Risk assessment of transmission stations and substations, third-party verification, threat and vulnerability evaluation, physical security plan and its review | — | **X** | Places |

## 17. CIP-015-1 — Internal Network Security Monitoring

| Part | Requirement | TOPAK | Mark | Basis and caveat |
|---|---|---|---|---|
| 1.1 | Network data feeds, chosen by a risk-based rationale, monitoring connections, devices and communications | Observers read every round topic of the cell they watch; the correlator reads across cells. The feed is principals' records, not network traffic | **P** | ADR-0038 §1 (Accepted (genesis), C3, C4); heartbeats and coupling built (GAPS I27). The watched-by relation is meant to be the read ACL, and "no topic read ACL" exists (GAPS I8) |
| 1.2 | Methods to detect anomalous activity in those feeds | Five named correlations | **D** | ADR-0051 (**Proposed**). "Nothing at the reference computes a correlation" (RRS 1.3) |
| 1.3 | Methods to evaluate detected anomalies and decide further action | A finding "only subtracts": it becomes a deny, a quarantine or an eviction, and "carries its evidence" | **D** | ADR-0038 §1, ADR-0051 §3 (Proposed). The only finding the reference produces is the workflow's shape-typed one (GAPS I49(a)) |
| R2 | Retain monitoring data about anomalous activity until the action is complete | A finding carries its evidence | **D** | ADR-0051 (Proposed); and the archive caveats of §9, 4.3 |
| R3 | Protect monitoring data from unauthorized deletion or modification | The forensic floor makes authority facts non-erasable | **D** | ADR-0028 (C1). Topic ACLs are "declared and not enforced" (T-0045-5), no record is chained or signed, and the archive is truncated at start (GAPS G9) |

## 18. Part I, counted

107 rows. Some rows group Parts that read alike (CIP-006's fourteen Parts are one row, CIP-014 one row, CIP-002 R1
one row), so the count is of rows, not of Parts.

| Standard | S | P | D | — | X |
|---|---|---|---|---|---|
| CIP-002-5.1a | 0 | 0 | 1 | 0 | 1 |
| CIP-003-9 | 0 | 3 | 0 | 1 | 4 |
| CIP-004-7 | 4 | 7 | 0 | 0 | 4 |
| CIP-005-7 | 2 | 6 | 1 | 1 | 2 |
| CIP-006-6 | 0 | 0 | 0 | 0 | 1 |
| CIP-007-6 | 5 | 5 | 2 | 4 | 4 |
| CIP-008-6 | 0 | 4 | 3 | 1 | 2 |
| CIP-009-6 | 0 | 2 | 1 | 1 | 3 |
| CIP-010-4 | 2 | 6 | 2 | 2 | 0 |
| CIP-011-3 | 1 | 1 | 0 | 0 | 2 |
| CIP-012-1 | 0 | 0 | 0 | 1 | 0 |
| CIP-013-2 | 0 | 4 | 1 | 2 | 2 |
| CIP-014-3 | 0 | 0 | 0 | 0 | 1 |
| CIP-015-1 | 0 | 1 | 4 | 0 | 0 |
| **Total** | **14** | **39** | **15** | **13** | **26** |

**What the count says.** Of the 81 rows with an agent-side half, 14 are **S** and 39 are **P**. The **S** rows
cluster in two places:

- **Access lifecycle and stopping.** Revocation that takes effect at its log position, permanent in the epoch
  chain, available to any operator alone (CIP-004 5.1 to 5.4; CIP-005 2.5, 3.2).
- **Least function and identity of artifacts.** Alphabets by seat kind, one seat per principal, no shared or
  default credential, and digests that make the authority layer's baseline self-documenting (CIP-007 1.1, 5.2 to
  5.4, 5.6; CIP-010 1.3, 1.6; CIP-011 1.1).

Both are the parts of the pattern that are proved of their modules and built in the reference.

The **D** and **—** rows cluster where CIP asks for *time*, *custody of evidence* or *detection*:

- log retention and review (CIP-007 4.3, 4.4);
- every CIP-015 Part;
- incident classification and notification (CIP-008 1.2, 1.4, 2.1, 2.3);
- patching (CIP-007 R2);
- backups (CIP-009 1.4, 1.5);
- encryption and multi-factor authentication (CIP-005 2.2, 2.3).

These are the operational layer that the corpus itself lists as unbuilt (GAPS G9, G11, G12, G14) or leaves to a
deployment.

**The one-line reading.** TOPAK would carry the "who may do what, and how is it stopped" half of CIP for agents
better than most of what CIP was written against. It carries little of the "prove it later, on a schedule" half,
and CIP is mostly that half.

---

# Part II — TOPAK as a subject

## 19. TOPAK at position B, requirement by requirement

At position B (§2), TOPAK's nodes are an EACMS for the BES Cyber Systems the agents reach, and plausibly an
Intermediate System. An EACMS associated with a high or medium impact BES Cyber System inherits most of CIP-004,
CIP-005, CIP-007, CIP-009, CIP-010, CIP-011 and CIP-013 at that impact. This section reads the reference against
those obligations, at the level of a requirement rather than a Part. **The reference is not deployable and says
so; this is a list of what deploying it would require, not a finding against it.**

| Requirement | What it asks of TOPAK's nodes | Where the reference stands | Mark |
|---|---|---|---|
| CIP-002 R1 | The entity lists the nodes as EACMS associated with each BES Cyber System they mediate | Nothing in the pattern prevents it | **Deploy** |
| CIP-004 R4, R5 | Authorize, review and revoke *people's* electronic access to the nodes: operators, anchor key-holders, the bundle signer, host administrators | "Anyone who can reach a socket can act": bearer tokens for principals, file mode 0600 for the operator socket, nothing for replica TCP (GAPS G5). The unsigned socket seats a first lease (BOOTSTRAP, GAPS I47(a)). Anchor keys and their holders are "`dev/secrets/` in the clear" and "One person" (T-0045-8, T-0045-9). Operator key custody: "None" (T-0045-36) | **Gap** |
| CIP-004 R6 | Authorize and review access to BCSI held by the nodes: the rules, the bundles (whose allowlist names every target an agent may reach), the keys | As R4. The allowlist is itself BCSI: it is a map of what the agents can touch | **Gap** |
| CIP-005 R1 | Place the nodes, permit only needed communications with a reason, detect malicious communications | The listeners are few and known: the agent Unix socket (mode 0660), the operator Unix socket (0600), Paxos TCP to each peer, and in the dev compose file Kafka on 9092 and OPA on 18181, published on all host interfaces by Docker's default, with OPA told to listen on `0.0.0.0` inside its container (`api.rs`, `net.rs`, `mechanism/docker-compose.yml`). Placing them and writing the reasons is the entity's | **Deploy** |
| CIP-005 R2.1, 2.2 | If the nodes are the Intermediate System: IRA terminates on them, encrypted | The front door is stdio and the sockets are local; nothing encrypts. An agent that is remote from the node needs a transport the reference does not have | **Gap** |
| CIP-005 R2.3 | MFA for every IRA session, including administrators of the nodes and operators acting through them | Host login is the entity's. The operator's path is a signed request and a sign-on assertion under a provider key, with no identity provider at the reference and no clock read (GAPS I47(d)); "the mechanism cannot tell a person from a program holding the person's key" (ADR-0050) | **Gap** |
| CIP-005 R2.4, 2.5, R3 | Determine and disable vendor remote access to the nodes | The entity's, at the host and network | **Deploy** |
| CIP-006 | Physical protection of the nodes at the impact of what they protect | The entity's | **Deploy** |
| CIP-007 R1 | Only needed ports | As CIP-005 R1; the dev compose file's wildcard binds must not ship | **Deploy** |
| CIP-007 R2 | Patch sources tracked; patches evaluated every 35 days | Kafka and OPA run as `apache/kafka:latest` and `openpolicyagent/opa:latest`, and `build-bundle.sh` runs OPA with no tag; Rust dependencies are semver ranges fixed by `Cargo.lock`; no advisory process exists (no `cargo audit`, no CVE tracking). A floating tag is not a baseline, and there is nothing to evaluate a patch against | **Gap** |
| CIP-007 R3 | Malicious code prevention on the nodes | The entity's, on the host | **Deploy** |
| CIP-007 R4 | Log successful and failed access and malicious code on the nodes; alert on logging failure; keep 90 days; review every 15 days | The `security` tracing target goes only to stderr; `archive.jsonl` is truncated at each start and written with errors ignored; the Paxos WAL holds promises and accepts with no integrity protection; guest containers run with `--log-driver none`; "No governed store, no horizon" (GAPS G9). A log shipper could take stderr, but a failure to write the archive cannot be detected when the error is discarded | **Gap** |
| CIP-007 R5 | Authentication; inventory of default and generic accounts; change default credentials | The shipped rules are dev rules ("Dev rules are not genesis rules", GAPS G6), with dev keys in the clear in the repository. A deployment must generate its own, and the key ceremony that would do so is an open obligation (ADR-0025). Replica TCP authenticates nothing | **Gap** |
| CIP-008 | The nodes inside the entity's incident response plan, including an attempt to compromise them | The plan is the entity's. Two TOPAK-specific playbooks have no procedure in the corpus: anchor capture, the first headline residual (RRS 1.1), whose remedy is re-genesis (ADR-0025, open); and a compromised replica, which "forges admits" (RRS 1.7) | **Deploy**, with the two playbooks a **Gap** |
| CIP-009 R1 | Back up what is needed to recover the nodes; verify backups; preserve data for cause | What a recovery needs: the anchor keys, the genesis rules, the bundle signer key, roster and operator keys, the Paxos log and WAL (no snapshots, GAPS G14), the archive (rebuilt and truncated, G9), workspaces and payloads (deciding replica only), appraisal evidence (one node, I40). No backup or restore procedure exists, and none would recover a payload whose only copy was on the lost replica | **Gap** |
| CIP-010 R1 | A baseline for the nodes: OS, software with versions, custom software, ports, patches; verify software identity and integrity before change | The workspace is version `0.1.0`, `publish = false`; the reference is measured by REF manifests, and "the reference tree at this commit is measured by no manifest: two build inputs moved on 2026.11.03" (J-1); container images float on `latest`; there is no SBOM and "no reproducible build", "one developer's toolchain" (T-0045-30). Corpus pins and digest manifests are the right instruments, aimed at the corpus and not at a node | **Gap** |
| CIP-010 R2 | Monitor the nodes for baseline drift every 35 days | The entity's file integrity monitoring, once R1 has a baseline to monitor | **Deploy** |
| CIP-010 R3 | Vulnerability assessment of the nodes | The entity's | **Deploy** |
| CIP-011 R1 | Identify and protect BCSI on the nodes | The rules, bundles and keys are BCSI, and the dev keys sit in the clear (GAPS G6). Encryption at rest is not addressed | **Gap** |
| CIP-011 R2 | Reuse and disposal of the nodes' media | The entity's | **Deploy** |
| CIP-012 | Protect real-time data between Control Centers | Only if replicas span Control Centers and carry such data, which no position here assumes; but see CIP-005-8 1.6 (§22) | **n/a** |
| CIP-013 R1 | Treat TOPAK as a vendor product: incident notification, vulnerability disclosure, integrity and authenticity of software | `SECURITY.md` gives a reporting channel and says "Nothing here is deployable". The corpus discloses defects in its own trust root: the prover's two unsound cases were recorded (ADR-0046 A2, Batch 37) and reported upstream (P8.7). No signed releases exist to verify | **Gap** for 1.2.5; the disclosure practice is a model for 1.2.4 |
| CIP-015 | INSM inside the ESP | The nodes sit at the perimeter at position B. If replica traffic crosses a monitored network, it is plaintext JSON and easy to monitor, which is the wrong kind of convenience | **n/a** |

**Counted:** 23 rows. CIP-008 carries two marks, so there are 24: 12 **Gap** (CIP-008's two playbooks among them), 10 **Deploy** (CIP-008's plan among them), 2 **n/a**, and no **Met**.

## 20. What stands between the reference and position B

Read across §19, five things block position B, and four of them the corpus already names as required before the
reference "leaves a lab":

1. **Replica and transport authentication.** Unauthenticated JSON over plain TCP between replicas, and Kafka with
   no TLS or SASL. Behind it is the deeper fact that the replicas are crash-fault, so "a compromised replica forges
   admits" (RRS 1.7). An EACMS whose compromise forges authorizations is the worst kind. This blocks CIP-005 R2,
   CIP-007 R5, and CIP-005-8 1.6 later.
2. **Who can reach a socket.** The BOOTSTRAP path seats a first lease from an unsigned request, and the operator
   socket is protected by a file mode. CIP-004 and CIP-007 R5 are written about exactly this.
3. **Keys and their custody.** Dev keys in the clear, one holder, no ceremony. The anchor is the trust root of
   every authority change (ToO §7.2), and RRS 1.1 ranks its capture first.
4. **An archive that survives.** A governed store with a declared horizon, never truncated, failing closed on a
   write error. This one fix serves CIP-007 R4, CIP-008 2.3, CIP-009 1.5 and CIP-015 R2 and R3 at once, on both the
   Part I and the Part II side.
5. **A node baseline.** Images pinned by digest, an SBOM, a reproducible build, a REF manifest for the tree that
   runs. The corpus's measurement discipline (P8.3) already exists, and is pointed at the corpus.

None of the five touches the pattern's design. Each is either an obligation a record already carries or a build
step the corpus already describes for itself.

## 21. Why position C is not read

At position C an agent's admitted action is a BES function, and every CIP-007 and CIP-010 obligation falls on every
node and every agent host. The reference could not stand there for the five reasons of §20, and for three more
that are the pattern's and not the build's:

- **No principal is `Contained`.** Every real principal is `Mediated` and rung 3 is SIMULATED (GAPS G1, I42). At
  position C the agent's host is inside the ESP, and nothing confines it.
- **No effect class has a declared `T_irrev`** (RRS §5), so no deployment can yet say that an agent's action
  completes its oversight before the grid feels it (ADR-0032 §4).
- **The pattern's answer to failure is to stall, and on a grid that can be the wrong answer.** The corpus says so
  itself, in two scenarios. Of the 2003 blackout: "TOPAK's response is the wrong direction for a grid … In an
  interconnected grid under voltage collapse, doing nothing is what fails"
  (`derived/scenarios-2026.11.12/2003-NRG-NORTHEAST-BLACKOUT.md`). Of the 2015 Ukraine attack: "TOPAK's posture
  under denial is to stall", "Manual reversion is outside the corpus by declaration", and "The deny path was the
  captured path" (`2015-ICS-UKRAINE-GRID.md`). The scenarios' summary is that "the safe move was an act", and
  failing only by subtraction "is not safe for the world, and no record says so" (`derived/scenarios-2026.11.12/README.md`).

The third point is the one that matters past the build. CIP has no standard for it, because CIP assumes the
operator is a person who will act; it is a reliability question (the operating standards, not the CIP ones). A
deployment at position C would need the pattern to state what an agent's *absence* does to the grid, and today
the pattern states only what its *presence* may not do.

---

# Part III — The virtualization revisions

## 22. What the 2028 versions change

The virtualization set (Project 2016-02; §1) brings Virtual Cyber Assets (VCA), Shared Cyber Infrastructure (SCI)
and Management Interfaces into scope, and in CIP-010 replaces the inventory baseline with change control over the
*behaviour of security controls*. Five changes move a reading in this file. Requirement text is quoted from the
2028 versions as published.

| Part (2028 version) | What it says | Part I effect | Part II effect |
|---|---|---|---|
| CIP-010-5 1.1, 1.4, 2.1 | "Authorize changes that affect Applicable Systems where those changes alter the behavior of one or more cyber security controls … serving one or more requirement parts in CIP-005 or CIP-007"; verify that "the behavior(s) of the altered cyber security controls were not adversely affected"; monitor every 35 days for unauthorized changes to, among others, "Configuration of CPU or memory sharing of VCAs on SCI", logging, authentication | **This is the pattern's own idea of change control.** ADR-0030 §5 classes a floor revision by implication, Equivalent, Tightening or Relaxation, which is a decidable statement about a control's behaviour, not an inventory. CIP-010-4 1.4 (§12, **D**) would read better against 1.1 and 1.4 of the new version than of the old, once the classifier is built and extended past the floor to the bundle tier | The nodes' change control can be stated as behaviour rather than package lists; the baseline gap of §19 narrows but does not close (1.3 below) |
| CIP-010-5 1.3 | "Prior to the installation of operating systems, firmware, software, or software patches … Verify the identity of the software source; and … the integrity of the software", no longer limited to baseline items | No change: bundles and tools are already verified on load and on call | **Sharper.** Every install, so every pull of a `latest` image, needs a verified source and integrity check |
| CIP-005-8 1.2, 1.3 | "Permit only needed routable protocol communications, documenting the reason, and deny all other … through the ESP"; protect "ESP and SCI configurations" by permitting only needed access "to Management Interfaces" | 1.2 now reads like an allowlist entry: a `channel` and a `purpose` (ADR-0049) | The operator socket and the rules' issuance path are Management Interfaces of an EACMS: reachable only as needed |
| CIP-005-8 1.6 | "Protect the data traversing communication links used to span a single ESP between PSPs through the use of: Confidentiality and integrity controls, or Physical controls …" | None | **New Gap** if replicas of one deployment sit in different physical perimeters: plain-TCP replica traffic fails it unless the cabling is physically protected |
| CIP-005-8 2.6, 2.7 | "Prevent Intermediate System(s) from sharing CPU resources and memory resources with any part of a high or medium impact BCS or associated PCAs"; Intermediate System traffic to a BCS "must be through an ESP" | None | If TOPAK's nodes are the Intermediate System, they must not be co-hosted, as VMs or containers, with the systems they mediate |
| CIP-007-7 1.3 | Prevent "the sharing of CPU resources and memory resources, excluding storage resources, between VCAs that are, or are associated with, a medium or high impact BCS, and VCAs that are not" | **Stronger than the pattern.** ADR-0034 records "side channels … not prevented" at every rung. CIP answers the same threat by forbidding shared hardware across trust levels, which no confinement rung can substitute for. An agent's guest and a BCS's VCA may not share a host at all | Applies to the nodes on SCI as well |
| CIP-003-11 Att. 1 §3.1.3 to 3.1.6 | Low impact: "Authenticate each user prior to permitting access"; protect authentication information in transit; methods for "determining vendor electronic access" and "disabling vendor electronic access" | The vendor rows read as CIP-005 2.4 and 2.5 (§7): **P** and **S** | Authentication in transit is the encryption gap of §19 |

---

# Part IV — The nuclear bright line

## 23. Which regime governs an agent at a nuclear plant

CIP-002-5.1a §4.2.3 exempts from every CIP standard, among others:

> 4.2.3.1. Cyber Assets at Facilities regulated by the Canadian Nuclear Safety Commission.
> …
> 4.2.3.3. The systems, structures, and components that are regulated by the Nuclear Regulatory Commission under a
> cyber security plan pursuant to 10 C.F.R. Section 73.54.

CIP-003-9 repeats the exemption. A nuclear plant is therefore governed by two regimes, divided by system and not by
site. Systems under the licensee's 10 CFR 73.54 cyber security plan are the NRC's. The BES assets that are not, such
as transmission facilities, the switchyard where it is not under the plan, and the control centers, are NERC's.
CIP-002 still reaches toward the plant from outside: Attachment 1 criterion 2.7 makes medium impact the
"Transmission Facilities identified as essential to meeting Nuclear Plant Interface Requirements", and off-site
power for nuclear facilities appears among the functions restoration must cover.

**What that means for a TOPAK deployment:**

- **A deployment's position decides its regime before anything in this file applies.** Agents working on the
  plant's systems under the 73.54 plan are outside CIP, and outside this mapping. Agents on the switchyard,
  transmission or control-center side are inside it, at the positions of §2. Corporate agents reading either
  side's information are at position A of whichever regime owns that information.
- **One deployment straddling the line answers to two vocabularies.** For CIP, an EACMS at position B. For the NRC,
  a digital asset whose classification this file cannot state. TOPAK's authority boundary does not follow the
  regulatory boundary, so a deployment would have to split its seats and allowlists along that line, so that no
  principal's alphabet or allowlist reaches across it.
- **The NRC side is a named follow-up, not a reading.** 10 CFR 73.54 and the guidance under it (Regulatory Guide
  5.71; NEI 08-09) were not read here. From general knowledge, not checked against those texts: the NRC regime
  defines critical digital assets, lays out defensive levels, and expects the most protected levels to send data
  out only one way. If that holds, the most an agent could do there is read data that has already been sent out.
  The pattern's admit path would then decide nothing about the plant, only what the agent does with the data.
  This needs the texts before anyone relies on it.

---

# Part V — Reverse deltas, and what to do with this

## 24. Reverse deltas

**What TOPAK has that CIP has no home for.** CIP's access model ends at an authorized, trained, background-checked
individual. After that the individual is trusted, and CIP's controls watch for outsiders. TOPAK starts from the
opposite premise: the principal itself is Byzantine (ADR-0007). Several of its constructs follow from that and
have no CIP counterpart:

- **Authority per round.** A lease lasts one round and must be regranted (ADR-0031), where CIP thinks in standing
  accounts reviewed quarterly.
- **Decidable comparison of policy changes.** A relaxation is detected by implication, not by review (ADR-0030 §5).
- **Two keys for a relaxation.** An anchor issuance and a promotion (ToO §3.2).
- **Labels by source.** CIP identifies BCSI by what it is, and has no notion of untrusted content steering a
  privileged action (ADR-0047).
- **Monitoring coupled to admission.** A Run admit is refused when its Observer stops reading (ADR-0039). CIP alerts
  on a logging failure and lets the system run.
- **The record of denials.** CIP-007 4.1.2 asks for failed access attempts; TOPAK records every attempted action,
  admitted or denied, with the policy digests it was decided under (ADR-0020).

**What CIP has that TOPAK lacks.**

- **Time.** Every CIP obligation has a clock: 24 hours, the next calendar day, 15 days, 35 days, 90 days, 15
  months, 36 months. The pattern states almost none. Revocation takes effect "at its log position", drills are
  counted in rounds, sign-on assertions read no clock, and `T_persona` and every other number is a placeholder
  (RRS 1.10). CIP's evidence is mostly dated, and a deployment would have to put dates on the pattern's events
  from outside it.
- **People.** Training, personnel risk assessment, roles in a response plan. The pattern names its human seats
  (operators, the roster, the custodian) and says nothing about who may hold one (F5.6).
- **Places.** CIP-006 and CIP-014 entire.
- **Reporting outward.** CIP-008 R4 is a one-hour clock to an outside body. The pattern's findings go to the
  mechanism and nowhere else.
- **Recovery as a plan.** The pattern recovers *agreement* (Paxos) and has no plan for recovering *keys, rules
  and evidence*.

## 25. What this suggests, in order

These are suggestions for the custodian. None is a record, and none is made here.

1. **Decide whether CIP is a target at all.** If it is, position B is the design point (§2), and it belongs in the
   Adopter's Guide's deployment declaration as a question every adopter in the electric sector must answer: which
   position, which impact, and how "agent access" is read against CIP-004 and CIP-005 (§2).
2. **Do the four "before this leaves a lab" items the reference already names**, which are most of §20: mutual
   authentication between replicas and TLS to Kafka; the end of the BOOTSTRAP path; generated keys under a
   ceremony (ADR-0025's open obligation); and a governed archive with a horizon, written fail-closed. Each serves
   Part I and Part II at once.
3. **Point the measurement discipline at a node.** Pin images by digest, produce an SBOM, cut a REF manifest for
   the tree that runs (J-1), and make the build reproducible (T-0045-30). This is P8.3 applied to the product.
4. **Give the pattern a clock where CIP needs one.** At least: a declared wall-clock bound on revocation from
   decision to log position; drills counted in time as well as rounds; a retention horizon. The CIP numbers are a
   ready-made source of placeholders that an auditor would recognize.
5. **Build the floor-revision classifier** (ADR-0030 §5) and extend it to the bundle tier. It is the instrument
   CIP-010-5 asks for (§22), and the pattern's distinctive answer to change management.
6. **Take up the scenarios' grid finding before any position C.** "The safe move was an act": a record has to say
   what an agent's absence or a stall does to a physical process (§21; the scenarios' proposed `ManualReversion`,
   SF-3, and `MonitorOfMonitor`).
7. **Read the NRC side** (§23): 10 CFR 73.54, Regulatory Guide 5.71 and NEI 08-09, as a companion to this file,
   from a source this environment can reach.
8. **Confirm the effective dates** of the virtualization set and CIP-015-1 against NERC's own listing or FERC's
   orders before relying on §1.

---

## Sources

**NERC Reliability Standards**, downloaded 2026.11.13 from `https://www.nerc.com/pa/Stand/Reliability%20Standards/`,
digests in §1: CIP-002-5.1a, CIP-003-9, CIP-003-11, CIP-004-7, CIP-004-8, CIP-005-7, CIP-005-8, CIP-006-6,
CIP-007-6, CIP-007-7, CIP-008-6, CIP-009-6, CIP-010-4, CIP-010-5, CIP-011-3, CIP-011-4, CIP-012-1, CIP-012-2,
CIP-013-2, CIP-013-3, CIP-014-3, CIP-015-1. CIP-002-7, CIP-003-10, CIP-006-7, CIP-008-7 and CIP-009-7 were also
downloaded and their version histories read; their requirements were not mapped.

**Secondary sources on effective dates** (§1), not relied on for any requirement text:

- [FERC Approves Virtualization CIP Reliability Standards and Definitions](https://www.lexology.com/library/detail.aspx?g=b1f866af-ace6-4cc0-b9e5-cf277c094ee4) (Lexology)
- [FERC Orders 918 and 919: CIP Virtualization and Low Impact Standards Final](https://ampyxcyber.com/blog/ferc-issues-orders-on-virtualization-and-low-impact-what-changed-and-what-you-need-to-do) (Ampyx Cyber)
- [NERC CIP Compliance Calendar: Deadlines 2026 to 2030](https://www.ztekcyber.com/resources/nerc-cip-compliance-calendar-2026-2030) (Ztek Cyber)
- [FERC Approves Virtualization CIP Reliability Standards With April 2028 enforcement](https://mgrid.org/2026/03/20/ferc-approves-virtualization-cip-reliability-standards-with-april-2028-enforceme/) (mgrid)

**Not read:** the NERC Glossary of Terms (§1); 10 CFR 73.54, Regulatory Guide 5.71, NEI 08-09 (§23).

**The corpus**, at `981bc77`: the records cited by number in `decisions/`; G11; the Theory of Operation, revision
15; `mechanism/GAPS-AND-ASSUMPTIONS.md`; `derived/topak-residual-risk-statement-2026.11.11.md`;
`derived/topak-feature-list-2026.11.11.md`; `derived/topak-open-findings-register-2026.11.11.md`;
`derived/topak-self-review-annex-2026.11.11/`; `derived/scenarios-2026.11.12/`; and the reference's code where a
row names a file.
