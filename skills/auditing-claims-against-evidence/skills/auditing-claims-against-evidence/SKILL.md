---
name: auditing-claims-against-evidence
description: "Audits a technical document claim by claim against the evidence it rests on: results files, digests, counts against their tables, internal and external citations, quotations, status marks, and whether the wording claims more than the result shows. Uses a reader who has not seen the drafter's conclusions, re-checks every finding before reporting it, gives a verdict per claim, and says what was not checked. Use whenever asked to audit, fact-check, verify, sanity-check or give a second reading of a record, design document, assessment, README or external draft, to check that its numbers, citations or status claims hold, or to look it over before it is published or ratified, even if the request is only 'give this a once-over'. Not for reviewing code, and not for writing or fixing the document."
---

# Auditing Claims Against Evidence

## Contents

- [When to Use](#when-to-use)
- [When NOT to Use](#when-not-to-use)
- [The workflow](#the-workflow)
- [Verdicts](#verdicts)
- [What this is not](#what-this-is-not)
- [Quick reference](#quick-reference)
- [Rationalizations to reject](#rationalizations-to-reject)
- [References](#references)

A method for reading a technical document as a set of checkable statements, distilled from a design corpus whose
critical reviews, errata and diagram generation repeatedly found prose that had drifted from its evidence.

**Core principle: a claim is checked only when someone has compared it with the thing it is about.** The document's
own confidence is not evidence, and neither is a summary of the source, the drafter's assurance, or the fact that a
sentence sounds right. Report what was compared with what, and say plainly what was not.

The method exists because prose tolerates things a check does not: a stale sentence, a miscounted list, a citation
that supports only half its sentence, a quotation that has drifted, a pending change counted as in force.

## When to Use

- Before a record is ratified or a document goes outside the project
- When a document cites results, digests, counts or other records
- After a revision, to see what it left behind
- When asked for a second reading, however lightly the request is put

## When NOT to Use

- Code review
- Fixing what is found: an audit reports. Corrections go through whatever process the document is under
- Judging whether a design is good. An audit asks whether the document's statements are true of its evidence

## The workflow

**1. Get an independent reader.** If you drafted or revised the target in this session, or the request comes with
reassurance about its quality, you are anchored, and an agent handed a hypothesis tends to return it confirmed. Where
you can start a fresh agent, do, using [assets/reader-brief.md](assets/reader-brief.md): it gets the target's path and
the method, and none of the drafter's conclusions. If you are that fresh agent, or cannot start one, proceed and say
which it was. Discount any "it should be clean".

**2. List the claims.** Go through the target from the top and write down each checkable statement, including the ones
in status notes, table cells, headers and asides. Numbers and "every", "no", "all", "nothing" are claims. So is each
half of a sentence with two citations.

**3. Check each by its class**, as [claim-classes.md](references/claim-classes.md) says. Run
`scripts/check_citations.py <file>` for the mechanical part. Regenerate or re-run where that is cheap, and where it is
not, read the dated results file and say that is what you did.

**4. Put things side by side.** Most inconsistencies appear only when two things are read together. Take every table
whole and count its rows against any number stated about it. Read each cited clause in its own record. Compare a
document with its siblings, and a claim with the module or test that states it. An empty cell in that comparison, a
claim nothing states, is a finding. Where the document says something is permitted, refused, recorded or bounded, walk
that action through the rules as written, as
[claim-classes.md](references/claim-classes.md#what-the-rest-of-the-system-permits) says.

**5. Re-check every finding before reporting it.** Go back to the source and try to show the finding is wrong. In one
review, two of twenty inconsistencies did not survive: both sentences were true and said different things. A true but
surprising claim stays Supported. A false alarm costs the reader's trust in the other findings.

**6. Report**, in the form below. A finding is a lead for whoever owns the document. Nothing in an audit decides
anything, and an audit changes no file unless told to.

## Verdicts

| Verdict | Means |
|---|---|
| **Supported** | Compared with the evidence, and it holds |
| **Wrong** | The evidence says otherwise |
| **Overstated** | True of something narrower: other constants, a model rather than the code, some cases rather than all, checked rather than proved |
| **Stale** | Was true. The evidence has moved |
| **Misattributed** | The fact may be right; the citation does not support it, or the quotation is not the source's words |
| **Not in force** | Rests on a pending or proposed change, stated as settled |
| **Unsupported** | Nothing cited or findable backs it |
| **Not checked** | Not compared, with why and what would settle it. External source unavailable is this, and never Supported |

**The report:**

```markdown
**Reader:** <fresh agent, or the session's own, and whether it saw the drafter's view>
**Checked at:** <commit or date> · **Target:** <path>
**Counts:** n claims: a Supported, b Wrong, ...

| # | Where | Claim | Verdict | Compared with | What it shows |

**Not checked:** <each, and what would settle it>
**Not an independent review.** <see below>
```

List every finding, and summarize the Supported claims by count unless asked for them all.

## What this is not

An audit by an agent is not the independent human reading a governance process may require. If a process asks for a
reader other than the drafter, this does not meet it unless the process owner rules that it does, and the report says
so, particularly when asked to count it as one. An audit also does not sign anything off. Saying "I found no problems
in what I checked" is as far as it goes, and "what I checked" has to be stated.

## Quick reference

| Claim | Check |
|---|---|
| A number | Count it, or read the results file, and name which |
| A digest | Compute it |
| "Every", "no", "only" | Search for the counterexample |
| A status | The target record's own status and pending lines |
| A clause cited | Read the clause there |
| A quotation | Exact words in the source |
| "Proved" or "verified" | Which tool, of what artifact, at which constants, on which premises |
| "Is permitted", "is refused", "is recorded", "is bounded" | Walk the action through the rules as written; under default deny, find the permit |
| Result "is current" | Run the sync check |
| An external paper | Read it, or mark Not checked |

## Rationalizations to reject

| Rationalization | Reality |
|---|---|
| "The author has double-checked it." | Then the audit will be short. Check it anyway. |
| "It reads consistently, so it's probably right." | Consistent prose is what drift looks like. Compare with the source. |
| "A derived summary says the same thing." | That is another copy of the claim. Find the source. |
| "This number comes from a results file, so it's fine." | Open the file and find the number. |
| "The paper isn't here, but the citation looks right." | Not checked. |
| "The rule is called report-own-topic, so it covers reports." | Read its conditions against this case. |
| "It surprised me, so it's a finding." | Surprise is a reason to look. Report only what the evidence contradicts. |
| "I have twenty findings, so I'm done." | Re-check them. Some will not survive. |
| "They want a sign-off, so I'll give one." | Report what was checked. A sign-off is someone else's act. |
| "I'll fix these while I'm here." | Report. The fix is the owner's, and has its own process. |
| "No problems found, so it's correct." | Only of what you compared. Say what that was. |

## References

- [claim-classes.md](references/claim-classes.md): how to check each kind of claim, with what has gone wrong. Read at
  step 3.
- [assets/reader-brief.md](assets/reader-brief.md): the brief for a fresh reader.
- [this-repository.md](references/this-repository.md): TOPAK's evidence, sync tools and vocabulary. Read first when
  working in that repository.
- `scripts/check_citations.py`: digest and path citations.
