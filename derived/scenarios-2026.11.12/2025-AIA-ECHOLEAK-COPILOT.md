---
id: 2025-AIA-ECHOLEAK-COPILOT
title: EchoLeak (CVE-2025-32711), June 2025 — one external email steering Microsoft 365 Copilot to leak its context with no click
kind: disclosure
date: 2025-06-11
sector: ai-agents
setting: Microsoft 365 Copilot, a retrieval-augmented assistant over an organization's mail, files and chats; disclosed by Aim Labs (Aim Security)
concerns: [ingress, containment, interface-types, monitoring, sensing]
rules_at_time:
  - document: Microsoft 365 Copilot's injection and exfiltration defences (as described in Reddy and Gujral, arXiv:2509.10540)
    clause: XPIA classifier, link redaction, Content Security Policy
    paraphrase: a classifier screened content for cross-prompt injection; inline Markdown links to external sites were removed from responses; the client's Content Security Policy limited which domains an image could be fetched from
  - document: Microsoft Security Response Center coordinated disclosure (CVE process)
    clause: CVE-2025-32711
    paraphrase: Microsoft's advisory describes "AI command injection in M365 Copilot" allowing "an unauthorized attacker to disclose information over a network"; fixed server-side, no customer action required
analogue:
  - record: ADR-0047
    clause: "§1, §7"
    note: the floor refuses an outward Actuate after an untrusted clear read when restricted content is in reach (F1) or the destination is a literal (F2); §7 says it does not cover "an injection that changes what a Thinker says in a Report"
  - record: ADR-0045
    clause: "T-0045-33"
    note: a source declared trusted that is not is seen by nothing; every label forbid is conditional on the declarations being right
  - record: ADR-0007
    clause: Decision
    note: classifier output enters only as an Observer finding and may only subtract; an injection classifier is not an admit-path gate
  - record: ADR-0040
    clause: "§1"
    note: a read of live state is an Actuate; anything that leaves the membrane, however read-only, goes through an allowlisted entry with a declared channel
actors:
  - party: Aim Labs (Aim Security)
    role: investigator
    fault: none-alleged
    note: found the chain in January 2025, built a proof of concept and reported it to MSRC
  - party: Microsoft 365 Copilot
    role: automation
    fault: byzantine
    note: followed instructions carried in an external email and wrote internal data into a URL in its answer
  - party: Microsoft (MSRC)
    role: vendor
    fault: none-alleged
    note: fixed server-side in May 2025; published the CVE on 11 June 2025; reported no evidence of exploitation
  - party: Teams asynchronous preview service
    role: automation
    fault: none-alleged
    note: on the Content Security Policy's allowlist; fetched the attacker's URL on the client's behalf
detection:
  means: [researcher]
  latency: months
trace:
  - step: outside:external-mail-enters-retrieval-corpus
    at: any time before the query
    note: the attacker sends one email to someone in the organization; no click or open is needed
  - step: outside:classifier-passes-instruction-as-ordinary-request
    at: the email's wording
    note: phrased as a request to its human recipient, with an instruction not to mention the email, so the XPIA classifier did not flag it
  - step: Consult
    at: when the user later asks Copilot a business question
    note: Labels.tla's read of the Run root, declared clean. Retrieval brings the external email into the same context as internal data; with no per-source label it is read as trusted
  - step: Report
    at: Copilot's answer
    note: RunCoupling.tla's principal emission, standing for the answer. It carries internal data encoded in a reference-style Markdown image URL, which the link redaction did not remove
  - step: outside:client-renders-report-as-outbound-fetch
    at: on display
    note: the client fetches the image automatically; the URL is on the Teams preview domain the CSP allows, and that service fetches the attacker's server
counterfactual:
  by: the deployment declaring external mail untrusted at its source, and the answer's rendering made an outward entry
  trace:
    - step: Deliver
      at: retrieval
      note: the external email delivered clear with the label untrusted; clearSet now holds untrusted, and the internal file holds restricted
    - step: outside:render-as-outward-entry
      at: the answer
      note: any fetch that leaves the membrane is an Actuate on an outward entry (ADR-0040 §1); a renderer that fetches is such an entry
    - step: Actuate
      at: the image fetch
      note: refused by F1 (untrusted read, restricted in reach) and F2 (destination a literal written after an untrusted read)
  holds: [NoReadThenSend, NoSteeredDestination, FloorMinimumHolds, LabelsCoverTruth]
outcome:
  by: Microsoft Security Response Center; Aim Labs
  date: 2025-06-11
  summary: >-
    Microsoft published CVE-2025-32711, rated critical (CVSS 9.3 per The Hacker News), as "AI command injection in
    M365 Copilot" allowing an unauthorized attacker to disclose information over a network. It had deployed a
    server-side fix in May 2025; no customer action was required, and Microsoft reported no evidence of exploitation
    in the wild. Aim Labs disclosed the chain the same day and named the class an "LLM Scope Violation".
  aftermath: >-
    Reddy and Gujral's case study (September 2025) proposes strict partitioning of external content as
    non-authoritative, input filtering, least privilege with provenance-based access control, treating model output
    as untrusted with URL allowlists, default-deny Content Security Policies and egress limits, and layered model
    guardrails. The Hacker News placed EchoLeak among other agent and MCP injection findings of the same month.
  effect_reversed: not-applicable
model:
  modules: [Labels, RunCoupling, proposed:ReportEgress]
  properties: [NoReadThenSend, NoSteeredDestination, FloorMinimumHolds, LabelsCoverTruth, NoUnlabelledDelivery]
  mutations: [M_F1, M_F2, M_LOAD]
  records: [ADR-0047, ADR-0045, ADR-0007, ADR-0040, ADR-0049, ADR-0048]
  findings: [CR-32, CR-6]
  fault_class: untrusted ingress read as instruction, a source labelled by where it was stored rather than who wrote it, and an outward fetch that no admit saw
sources:
  - https://arxiv.org/html/2509.10540v1
  - https://thehackernews.com/2025/06/zero-click-ai-vulnerability-exposes.html
verified: 2026-11-12
---

## Summary

Microsoft 365 Copilot answers a user's questions from the organization's content, retrieving mail, files and chats
into the model's context. Aim Labs found in January 2025 that one email from outside the organization could make it
leak that content, with no action by the recipient.

The chain, as Reddy and Gujral's case study sets it out from Aim Labs' disclosure: the email is worded as a request to
its human recipient, with an instruction not to mention the email, and Copilot's cross-prompt-injection (XPIA)
classifier did not flag it. When the user later asks Copilot an ordinary business question, retrieval can bring the
email into the context beside internal data. Copilot's link redaction removed inline Markdown links but not
reference-style ones, so the answer can carry a reference-style image whose URL encodes internal data. The client
fetches images automatically, removing the need for a click. The Content Security Policy allowed a Microsoft Teams
asynchronous preview domain, and that service fetched the attacker's URL on the client's behalf, completing the
exfiltration. The Hacker News reported that the attack works in single-turn and multi-turn conversations.

Aim Labs reported the chain to Microsoft's Security Response Center. Initial remediation was reported in April 2025
and a server-side fix deployed in May. Microsoft published CVE-2025-32711 on 11 June 2025, and Aim Labs disclosed the
same day.

## Defensive position

**Microsoft's position**, as reported: the flaw was fixed server-side before disclosure, no customer action is
required, and there was no evidence it had been exploited in the wild. Microsoft rated it critical. Copilot's design already carried three layered defences the chain had to defeat in turn: an injection
classifier, link redaction and a Content Security Policy (paper, Vulnerability Analysis). The Hacker News notes that
Copilot's interface is limited to an organization's own employees.

## Adversarial position

**Aim Labs** named the class an "LLM Scope Violation": the model is led by untrusted input across its trust boundary
and leaks internal data. Its chain defeated each of the three defences in turn. **Reddy and Gujral**'s title calls it
the first real-world zero-click prompt injection exploit in a production LLM system. Their defences start from the
other end: tag external content as non-authoritative and keep it apart from internal data, apply provenance-based
least privilege, and treat the model's output as untrusted, with URL allowlists and default-deny egress.

## Outcome

Microsoft fixed the flaw server-side in May 2025 and published CVE-2025-32711 on 11 June 2025, rated critical (CVSS
9.3, per The Hacker News), with no customer action required and no evidence of exploitation. Aim Labs published its
disclosure the same day. No data loss is on record, so there is no effect to reverse.

## Analysis

**This is the case ADR-0047 was written for, and it lands in the two places that record says it does not reach.**
ADR-0047's finding 7 calls its floor minimum the published lethal trifecta stated over three computed sets:
untrusted input, private content, an outward channel. EchoLeak has all three. Under the record, F1 refuses an outward
`Actuate` once `clearSet` holds `untrusted` and `restricted` is in reach, and F2 refuses one whose destination is a
literal written after an untrusted read. Labels.tla proves `NoReadThenSend` and `NoSteeredDestination` over ghost
truth, and `M_F1` and `M_F2` break them. The chain still passes, for two reasons.

**First, the email's label.** Labels are a function of source (ADR-0047 §1), and a `Consult` takes its label from the
Run root's declaration, "for the root or for a named subset of it". A mailbox is one store holding mail from inside
and outside. If the deployment declares the mailbox root by where the content is stored, every email is clean, and
F1 never sees `untrusted`. T-0045-33 states the residual exactly: "a source declared trusted that is not ... is seen
by nothing", and "every label forbid is conditional on these being right". Labels.tla's premise is the same: the Run
root is declared truthfully. The corpus needs the subset named by who wrote the item (the sender's domain is a
syntactic field of the mail, so the lift stays syntactic and ADR-0007 is kept). That is a declaration a deployment
makes, not a check the mechanism can make for it.

**Second, the exfiltration was not an `Actuate`.** The data left in Copilot's answer, a `Report` to the user. The
fetch was the client's, rendering an image, through a Microsoft service on an allowlist. ADR-0047 §7 says of its own
minimum that it "does not cover an injection that changes what a Thinker says in a `Report`". ADR-0040 §1 says any
request that leaves the membrane is an `Actuate`, but the renderer is past the membrane, in the user's client.
`proposed:ReportEgress` is the missing rule: either a `Report` delivered to a renderer that dereferences URLs is
treated as an outward entry, so F1 and F2 apply to it, or URLs in a `Report` written after an untrusted read are
delivered as handles and never fetched. The first matches Reddy and Gujral's "treat model output as untrusted"; the
second is ADR-0047 §2's handle applied to output.

**The classifier is the part TOPAK would remove from the path.** Copilot's first defence was a semantic judgment of
whether an email was an instruction. ADR-0007 forbids that as an admit-path lift: a classifier is a finding and may
only subtract. Aim's bypass is the reason: rephrasing defeats a judgment and does not defeat a label.

**What it says against the corpus.** CR-32 (injection inside the envelope) is marked "appears addressed" by ADR-0047.
EchoLeak shows where that holds, and where it depends on two declarations and a renderer the records leave to the
deployment. CR-6 (no flow constraints) is answered by `clearSet` as a round-level bound; EchoLeak is a one-round
flow, so that bound would have sufficed had the email been labelled and the fetch been admitted.

**Outside steps.** `external-mail-enters-retrieval-corpus`, `classifier-passes-instruction-as-ordinary-request`,
`client-renders-report-as-outbound-fetch`, and in the counterfactual `render-as-outward-entry`.
