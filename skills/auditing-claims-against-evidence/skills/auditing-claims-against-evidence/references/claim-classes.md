# Claim classes

How to check each kind of claim. The examples are real ones, found in a design corpus.

## Numbers and counts

Count the thing, or find the number in its results file, and say which. Compare every stated count with its table.
Three adversaries were said to be bounded by "nothing" where the table had two, and a third whose cell began with the
word "Nothing" and stated a bound.

## Digests and paths

Compute the digest from the file. A citation of a file at a digest makes a statement about those bytes. A mismatch
means Stale when the file has legitimately moved, and Wrong when it never matched. Check history if that matters.

## Results

"892 obligations proved": open the results file, find the count, check that the file's own digest lines match the
sources, and note its date. A sync script, if one exists, says whether it is still current. Say whether you re-ran it
or read it.

## Universal claims

"Every", "no", "none", "all", "only", "nothing": search for a counterexample, and report what you searched. "No module
is written" was false the day eight modules arrived. "Every obligation is certified" fails on a handful a checker
never confirms.

## Status

Read the target's own status and pending lines, never another document's account of them. A record described as
ratified may be Proposed, and a change described as in force may be pending.

**Not in force** is easy to miss because the sentence is true of the draft: one record counted "a sixth item" by
including a fifth that was a pending amendment on another record.

## Citations

Read the clause cited, in its own record, as it stands. Check each half of a sentence with more than one citation
separately: one sentence cited a paper for a claim about human reviewers that the paper's relevant section does not
make. Check what kind of source it is, too. A study of independently written program versions, cited for humans
reviewing together, supports that only by analogy.

## Quotations

Words in quotation marks have to be the source's words, and whole. "Refuses `Actuate`" for a rule that forbids
`Actuate` and `Report` left out the half that mattered. A faithful paraphrase in quotation marks is still Misattributed.

## Scope and wording

The most common way a true result gets overstated. Ask of each result:

- **Which tool?** Checked at small constants, proved for all, sampled, tested. These are different claims.
- **Of what?** A specification, a re-encoding, a transcription, a model, or the code. A theorem about one is not a
  theorem about another.
- **At which constants?** A model proved at any size, and its refinement proved at a module's constants, are two
  claims. Losses counted at seven replicas are not the module's, checked at five.
- **On which premises?** Say which are stated and which are assumed. "A day old" assumed a clock a captured party can
  stop.
- **Is "correct" defined?** "Proved correct" needs a stated specification of correct.

## Two things on one page

Read together: a record and its siblings, a clause and its ratification condition, a claim and the module that states
it, a word in one section and in another. "Received" in one clause and "originates" in another came apart after a
revision to one. A condition asked for nothing about floor entries its own clause cited. Compare headings across a set
drafted together, since one member may lack a section the others have.

## What the rest of the system permits

A document that says something is allowed, refused, recorded, counted or reachable is making a claim about other
artifacts: the policy, the schema, the state machine, the code. A sentence can be consistent with every other sentence
and still describe something the system as written cannot do. Walk the action through them, one step at a time:

1. **Name the case**: the action, the actor, the resource, and the state it happens in.
2. **Find every rule that can allow or refuse it.** Under default deny, something has to permit it explicitly, so find
   that rule.
3. **Evaluate each rule's conditions against this case.** Read the conditions and not the rule's name.
4. **Follow the effect**: who records it, what counts it, what bound covers it, and what happens after the state it
   needs has ended.
5. **For a proposed change, ask whether it adds what the action needs.** A proposal that adds only forbids grants
   nothing, and an exception written into one forbid does not lift another.

Real examples. A record called a peer send "a `Report` permitted under the floor", while the only permit for `Report`
required the topic to be the sender's own. Another allowed a beacon after a lease had ended, while a forbid refused any
permit under an ended lease and only a different forbid carried the beacon exception. A bound of "at most `K` of a
Thinker's effects" did not cover a new kind of effect with "a count of its own".

Report the rule and the condition that fails. The verdict is Wrong where a rule contradicts the claim, and Unsupported
where a rule the claim needs does not exist. Whether the system ought to permit it is the owner's question.

## External sources

Read the source if it can be had, and record which version. If it cannot, the verdict is Not checked, and name what
would settle it. A secondary document that repeats the citation does not settle it.

## Attribution

"The custodian decided" and "drafted by": does a record say so? A mark claiming that every choice is marked needs the
marks to exist.
