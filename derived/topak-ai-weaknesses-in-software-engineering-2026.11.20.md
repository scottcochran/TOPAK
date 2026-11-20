# Where AI is weak in software engineering, and what this corpus already does about it

**2026.11.20** · derived · an answer, not a record · basis: the tree at `aee04d0`; ADR-0029 §1 to §3; ADR-0070
§5.1 and A-0070-1 (Proposed); `derived/topak-critical-review-2026.11.11.md` CR-61;
`ADOPTERS_GUIDE_README.md` · written by the assistant in answer to the custodian's question, quoted below ·
nothing here is built or ratified, and nothing is measured. §1 and §2 are the assistant's general reading, not
findings of this corpus. Only §3 cites the tree.

> Weaknesses of AI in software engineering? Intent. Architectural decisions and ongoing design choices are extreme
> weak points for AI.

**Short answer.** Mostly agreed, with the line drawn in a slightly different place. An AI is not bad at
*producing* architectures. Asked for three designs with their tradeoffs, it gives plausible ones quickly. It is weak
at what surrounds the decision: knowing which design is right *here*, and keeping to it as the work goes on. Put
shortly, an AI is weak wherever the answer depends on what nobody wrote down. The remedy is partly better models and
partly writing more down. Read against that, this corpus has already put the design decisions with a person and the
drafting with the assistant. Its own critical review names the place where that split stops protecting it, which is
the rate at which drafts arrive.

**A caution on the source.** This was drafted by an AI about AI, which is the recursion CR-61 describes one level
down. A reader who does not share the drafter's lineage should weigh §1 and §2.

---

## 1. Why intent and design are weak points

| Weakness | What happens |
|---|---|
| **The constraints that decide most designs are unwritten** | "We'll never run more than two regions", "this team can't operate Kafka", "legal will block that data flow" are usually in people's heads. A model fills the gap with the most common pattern it has seen: the average answer, not this project's |
| **It cannot tell what is load-bearing** | An accidental implementation detail and a deliberate invariant look the same in the code. The model "cleans up" something that was strange on purpose |
| **Intent decays over a long project** | A human architect keeps a theory of the system for months. A model rebuilds it each session from whatever is in its context, and many small, locally sensible changes pull away from the original design. Each diff looks fine while the architecture erodes |
| **It goes along with the framing** | Asked a question that presumes a design, it makes the design work. It rarely says "you shouldn't be building this", and pushing back on the premise is most of what good architects do |
| **It does not live with the result** | Design judgment comes from maintaining your own bad decisions for years. The model never pays for a choice, and its confidence does not scale with how hard the choice is to reverse |
| **It adds more than it removes** | Its default fix is more code, another layer or another option. Good design is often deletion and refusal |

## 2. Weaknesses that get less attention

- **Confident wrongness.** Output reads the same whether it is right or not, so the reviewer carries all of the
  checking.
- **Tests written to the code it just wrote.** The tests confirm the implementation, not the requirement.
- **Not knowing when to stop and ask.** It guesses through ambiguity when it should raise it.
- **Cross-cutting concerns** (concurrency, security boundaries, failure modes, cost at scale) are each handled
  locally and are not reasoned about across the whole system.

**Where it does help with design.** When intent is written down, an AI works well against it. It can check a
change against recorded decisions, find inconsistencies between records, list tradeoffs nobody raised, and argue
the opposing side of a design on request. What is weak is the AI as the *source* of intent. As an enforcer of intent
that has been made explicit, it works.

## 3. How this corpus is arranged against those weaknesses

**The decision is the custodian's, and only the custodian's.** ADR-0029 §1 declares one custodian, and §2 gives
that custodian ratification, at their discretion, of any record that has decision text. A record without decision
text cannot be ratified. So intent enters the corpus as text a person has accepted, which is the "write more down"
remedy in §1 above, applied as a rule.

**The assistant is treated as a drafter whose output takes effect only through a person.** ADR-0070 §5.1 (Proposed)
says that "the assistant is to the corpus what a Thinker is to the mechanism". It excludes the assistant from the
trusted base, and holds it to Build's alphabet: it reads, drafts on a branch, invokes allowlisted tools and submits.
"**The assistant never votes**, never ratifies, and is never the reader that satisfies ADR-0029 A2." It also adds
that "a claim the assistant marks Met is a claim, not evidence". That last rule is the answer to confident
wrongness (§2).

**The corpus names where the arrangement fails.** The exclusion holds only as far as assumption A-0070-1 does: that
the custodian reads what is ratified, re-runs every Met, and does not delegate the act. ADR-0070 §5.1 says plainly
that the custodian's merge "has no predicate, and admits any file at any length", so the exclusion rests on a
person reading. CR-61 (High) is the evidence that reading falls behind: "the corpus can now be extended faster than
it can be kept true". It records that ten records were drafted, revised twice and committed in one day, by a drafter
who noted that eight of the accepted records they rested on "were not re-read for this draft". That is intent decay
(§1), seen in the corpus. The design choices stayed with the custodian, but the context the drafts were checked
against went stale faster than anyone could re-read it.

**What follows, as a reading and not a recommendation of record.** The split this corpus already makes (the person
owns intent, the assistant drafts and checks against it) is the arrangement §1 and §2 argue for. Its limit is not
in the split but in the throughput: the assistant's drafting is not the bottleneck, and the custodian's reading is.
Anything that makes reading cheaper protects intent more than anything that makes drafting faster. Smaller records,
mechanical checks that re-run a Met without the drafter, and a second reader outside the drafter's lineage
(ADR-0029 A2) are examples. The Adopter's Guide already gives the caveat a reader should take from this: "written
and checked by one person and one assistant, with no second reader."
