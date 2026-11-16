# Contributing to TOPAK

TOPAK is a design corpus with one custodian. Read [SECURITY.md](../SECURITY.md) first: nothing here is deployable,
and the most useful contribution is a finding against a safety claim. If you are reviewing the corpus, start with
the [Reviewer's Guide](../REVIEWERS_GUIDE_README.md). This file covers how a change gets in.

## Three lanes

Every contribution is in one of three lanes, and each is handled differently.

1. **Safety findings do not start as pull requests.** Examples: a guarantee the specification does not establish, a
   policy that admits what the design denies, a gap in a confinement or anchor argument. Report it privately, as
   SECURITY.md says, through GitHub's private vulnerability reporting or the email address there. A wrong safety
   claim that is public and not yet corrected is the worst state the corpus can be in. Once the finding is
   dispositioned, its correction comes in as a pull request in lane 2.
2. **Records, checkpoints and the narrative are the custodian's.** `decisions/`, `checkpoints/` and `narrative/`
   change only when the custodian ratifies, in a numbered batch under ADR-0029, and writes the History rows.
   A pull request here is welcome as a **proposal**: it shows the change you would make. The custodian then carries
   it into a batch, declines it with written reasons, or records it as named debt. Expect it to be closed rather than
   merged, with a link to the commit that applied it.
3. **Everything else is ordinary.** That covers the reference in `mechanism/`, the bundle policies in `policies/`,
   the tools, the diagrams and their generators, and the guides at the root. Open a pull request; it merges when
   the checks pass and the custodian approves.

**An approval is not a ratification.** Some accepted records are marked as needing independent confirmation
(ADR-0029 C1 to C4; the current checkpoint gives the count), and that confirmation is a post-bootstrap quorum's
vote. A merged pull request, a review comment and an approval on GitHub are none of those, and the corpus will not
cite one as such.

## What never changes

The corpus cites its own files by digest, so some files are frozen once written. A pull request that modifies,
deletes or renames one fails the `frozen-files` check. Add a new file instead.

| Frozen | Instead |
|---|---|
| A checkpoint, `checkpoints/*.md` other than the README | An erratum row in `checkpoints/README.md`; the next checkpoint corrects it |
| A derived document, `derived/*.md` other than the README | A new dated document that supersedes it |
| A results or evidence file, `*-results-*.txt` or a `*-evidence-*` directory | A new dated file from the generating script |
| A manifest, `manifests/SHA256SUMS*` | A new cut |
| A TLA+ module whose digest a record that is not Proposed cites | A successor module (`Lease` to `Lease_A1`), with its proof in the same commit (`spec/README.md`) |
| The narrative archive and the process logs | Nothing; they are closed |
| A decision record's file | Never deleted or renamed. Its text changes only by typed History rows, in lane 2 |

A derived document or a results file may still change on the date in its name. PDFs, zips and files over 5 MB are
refused too, because reference material is not ours to redistribute.

## Commits

- **Sign your commits.** Pull requests merge by merge commit, so your commits land on `main` as you wrote them,
  and `main` accepts only signed commits. GitHub's guide to
  [signing commits](https://docs.github.com/en/authentication/managing-commit-signature-verification/signing-commits)
  covers SSH and GPG keys. An unsigned commit in a pull request blocks its merge.
- **Sign off your commits** with `git commit -s`. The `Signed-off-by` line is your statement under the
  [Developer Certificate of Origin](https://developercertificate.org/) that you may contribute the change under the
  repository's licences: Apache-2.0 for code, specifications, policies and tooling, CC BY 4.0 for documentation
  ([NOTICE](../NOTICE)). There is no CLA.
- **Name what the commit does in the corpus's terms**: the record, amendment, module or finding it touches, as the
  history does (`ADR-0033 A17 (pending): …`, `Diagrams against G11: …`). No conventional-commit prefixes.
- **Say whether an AI assistant drafted it.** Much of the corpus was drafted with one, and the corpus records that
  for every ratified text (G11 item 66). Say so in the pull request description, and name what you checked
  yourself.

## The checks

Three workflows run on pull requests (ADR-0069 §10.2, Proposed). During genesis they support the custodian's review
and promote nothing.

| Check | When | What it asks |
|---|---|---|
| `checks` | every pull request | Does the TLC jar match its pin? Are the proofs in step with the specifications (`spec/proof-sync.sh`)? Does every manifest still verify at the commit it measured? And, ratcheted: the corpus pins the reference follows, the Lean results in step (`tools/lean-sync.sh`), the path citations (`tools/check-refs.py`), and the record lint |
| `frozen-files` | every pull request | Is anything in the table above modified, deleted or renamed? |
| `results` | when `spec/`, `tools/`, `mechanism/`, `policies/` or `floor/` change | Do TLC, the reference's tests, the Lean builds and the floor's gates still reproduce the committed evidence, for the suites the change touches? |

`checks` and `frozen-files` are the required checks. `results` is read at review. It never writes a results file.
When a fresh run differs from the committed file, it uploads the fresh one, and the committed file is regenerated by
hand as a new dated file.

**The ratcheted steps fail only on what a change adds.** Each of them has findings on `main` that predate CI, for
debts the state of record already lists. `tools/ratchet.py` runs the check on the base and on the pull request,
lists the standing findings in the job summary, and fails only on a new one.

If you change anything in `policies/`, rebuild the bundle with `mechanism/scripts/build-bundle.sh`, remove the old
tarball from `mechanism/bundles/`, and commit the new one. The script needs Docker.

Run the required checks yourself before pushing:

```sh
tools/check-pins.sh
spec/proof-sync.sh
tools/verify-manifest.sh --all
tools/ratchet.py --base main --name "Path citations" --include '^  \S' --context '^\S.*:$' -- python3 tools/check-refs.py
tools/ratchet.py --base main --name "Lean results in step" \
  --include 'STALE$|MISSING RESULTS|NOT STATED IN LEAN|OFF THE PIN|NOT THE PINNED KERNEL' -- tools/lean-sync.sh
python3 -I .github/scripts/frozen-files.py main HEAD
```

`.github/workflows/checks.yml` lists every step with its exact command.

**The custodian can lift the freeze for one pull request** by adding the label `frozen-override`. It is for a
change the corpus itself authorizes, such as a layout move, or a revision in place that a record's amendment states.
The check then reports what is frozen as warnings. The label counts only when a code owner adds it.
