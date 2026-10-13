# Contributing to TOPAK

TOPAK is a design corpus with one custodian. Read [SECURITY.md](../SECURITY.md) first: nothing here is deployable,
and the most useful contribution is a finding against a safety claim. If you are reviewing the corpus, the
[Reviewer's Guide](../REVIEWERS_GUIDE_README.md) is the place to start. This file covers how a change gets in.

## Three lanes

Every contribution is in one of three lanes, and they are handled differently.

1. **Safety findings do not start as pull requests.** A guarantee the specification does not establish, a policy
   that admits what the design denies, a gap in a confinement or anchor argument: report it privately, as
   SECURITY.md says, through GitHub's private vulnerability reporting or the email address there. A wrong safety
   claim that is public and not yet corrected is the worst state the corpus can be in. Once the finding is
   dispositioned, its correction comes in as a pull request in lane 2.
2. **Records, checkpoints and the narrative are the custodian's.** `decisions/`, `checkpoints/` and `narrative/`
   change only when the custodian ratifies, in a numbered batch under ADR-0029, and writes the History rows.
   A pull request here is welcome as a **proposal**: it shows the change you would make, and the custodian
   carries it into a batch, declines it with written reasons, or records it as named debt. Expect it to be closed
   rather than merged, with a link to the commit that applied it.
3. **Everything else is ordinary.** The reference in `mechanism/`, the bundle policies in `policies/`, the tools,
   the diagrams and their generators, and the two guides at the root. Open a pull request; it merges when the
   checks pass and the custodian approves.

**An approval is not a ratification.** Twenty-nine records are marked as needing independent confirmation
(ADR-0029 C1 to C4), and that confirmation is a post-bootstrap quorum's vote. A merged pull request, a review
comment or an approval on GitHub is none of those, and the corpus will not cite one as such.

## What never changes

The corpus cites its own files by digest, so some files are frozen once written. A pull request that modifies,
deletes or renames one fails the `frozen-files` check. Add a new file instead.

| Frozen | Instead |
|---|---|
| A checkpoint, `checkpoints/*.md` other than the README | An erratum row in `checkpoints/README.md`; the next checkpoint corrects it |
| A derived document, `derived/*.md` other than the README | A new dated document that supersedes it |
| A results or evidence file, `*-results-*.txt` or a `*-evidence-*` directory | A new dated file from the generating script. A file may still change on the date in its name |
| A manifest, `manifests/SHA256SUMS*` | A new cut |
| A TLA+ module whose digest an accepted record cites | A successor module (`Lease` to `Lease_A1`), with its proof in the same commit (`spec/README.md`) |
| The narrative archive and the process logs | Nothing; they are closed |
| A decision record's file | Never deleted or renamed. Its text changes only by typed History rows, in lane 2 |

PDFs, zips and files over 5 MB are refused too. Reference material is not ours to redistribute.

## Commits

- **Sign your commits.** Pull requests merge by merge commit, so your commits land on `main` as you wrote them,
  and `main` accepts only signed commits. GitHub's guide to
  [signing commits](https://docs.github.com/en/authentication/managing-commit-signature-verification/signing-commits)
  covers SSH and GPG keys. An unsigned commit in a pull request blocks its merge.
- **Sign off your commits** with `git commit -s`. The `Signed-off-by` line is your statement under the
  [Developer Certificate of Origin](https://developercertificate.org/) that you may contribute the change under the
  repository's licences: Apache-2.0 for code, specifications, policies and tooling, CC BY 4.0 for documentation
  ([NOTICE](../NOTICE)). The DCO check enforces it. There is no CLA.
- **Name what the commit does in the corpus's terms**: the record, amendment, module or finding it touches, as the
  history does (`ADR-0033 A17 (pending): …`, `Diagrams against G11: …`). No conventional-commit prefixes.
- **Say whether an AI assistant drafted it.** Much of the corpus was drafted with one, and the corpus records that
  for every ratified text (G11 item 66). Say so in the pull request description, and name what you checked
  yourself.

## The checks

Seven checks run on every pull request. None runs the model checker, the prover, Lean or the floor's solver gates:
the dated results files are the evidence, and the sync checks confirm they are current.

| Check | What it asks |
|---|---|
| `check-refs` | Does every path a document cites exist, and is every date `YYYY.MM.DD`? |
| `frozen-files` | Is anything in the table above modified, deleted or renamed? |
| `verify-manifests` | Does every manifest still verify at the commit it measured? |
| `proof-sync` | Is every proof's results file current with the modules it proves? |
| `lean-sync` | Is every Lean results file current with what it transcribes, and on the pin? |
| `mechanism-tests` | Is the tracked bundle built from the current policies, and do the Rego tests and the reference's tests pass? |
| `DCO` | Does every commit carry a sign-off? |

**`check-refs`, `proof-sync` and `lean-sync` are ratchets.** Each fails on `main` today, for debts the state of
record already lists: citations left stale inside frozen files, two modules without a proof or a recorded reason,
and Lean replays behind the reference. A pull request may carry those debts; it fails only if it adds one. The
check's log lists the carried debts as notices and the new ones as errors.

If you change anything in `policies/`, rebuild the bundle with `mechanism/scripts/build-bundle.sh`, remove the
old tarball from `mechanism/bundles/`, and commit the new one; `mechanism-tests` fails otherwise. The script needs
Docker.

Run the checks yourself before pushing:

```sh
python3 -I .github/scripts/frozen-files.py main HEAD
python3 -I .github/scripts/ratchet.py main check-refs
python3 -I .github/scripts/ratchet.py main proof-sync
python3 -I .github/scripts/ratchet.py main lean-sync
tools/verify-manifest.sh --all
(cd mechanism && cargo test --workspace --release)
```

**The custodian can lift the freeze for one pull request** by adding the label `frozen-override`. It is for a
change the corpus itself authorizes, such as a layout move or a revision in place that a record's amendment
states. The check then reports what is frozen as warnings. The label counts only when a code owner adds it.
