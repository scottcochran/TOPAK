"""H11 — TLA+ checks run in the tla-kit image (ADR-0077, Proposed, 2026.11.16): the image is a TOPAK pin by its
published digest, the `tlc` job runs in it, a `proofs` job reruns every proof module in it and refuses a count that
differs, and the prover pin moves to the image's build only by its own pull request. Drawn beside what exists today:
the jar pin, the local TLAPS build and a CI that does not prove. Nothing the record proposes is built."""
from lib import Canvas, STATE_G12, STATUS, text_width

ID, SLUG = "H11", "tla-kit-image"

W = 3600
S = 14


# ---------------------------------------------------------------------------------------------- layout helpers
def row_cards(c, x, y, w, gap, specs, size=S):
    """A row of cards of equal height, measured over every card in the row. specs: (title, body, accent, kwargs)."""
    n = len(specs)
    cw = (w - (n - 1) * gap) / n
    h = max(c.card(0, 0, cw, t, b, draw=False, size=size, status=k.get("status")) for t, b, _, k in specs)
    for i, (t, b, acc, k) in enumerate(specs):
        c.card(x + i * (cw + gap), y, cw, t, b, accent=acc, h=h, size=size, **k)
    return h


def stack(c, x, y, w, specs, gap=16, size=S):
    """Cards one under another. specs: (title, body, accent, kwargs). Returns the bottom."""
    for t, b, acc, k in specs:
        y += c.card(x, y, w, t, b, accent=acc, size=size, **k) + gap
    return y - gap


def band(c, x, y, title, accent="ink", status=None, extra=""):
    c.text(x, y + 22, title, 22, accent, bold=True)
    if status:
        c.status(x + text_width(title, 22, True) + 20, y + 4, status, extra)
    return y + 54


def status_strip(c, x0, x1, y, items):
    """items: (label, key, extra). key is a lib STATUS key, or (label, accent, dash) for a pill the library lacks."""
    c.text(x0, y + 15, "Status", 15, "faint", bold=True)
    px0 = x0 + 80
    px = px0
    for lab, key, extra in items:
        lw = text_width(lab, 13.5, True) + 8
        if isinstance(key, tuple):
            plab, acc, dash = key
            pw = text_width(plab, 11.5, True) + 18
        else:
            pw = text_width(STATUS[key][0] + (f" · {extra}" if extra else ""), 11.5, True) + 18
        if px + lw + pw > x1:
            px = px0
            y += 34
        c.text(px, y + 15, lab, 13.5, "ink", bold=True)
        px += lw
        if isinstance(key, tuple):
            px += c.pill(px, y, plab, acc, 11.5, dash=dash) + 26
        else:
            px += c.status(px, y, key, extra) + 26
    return y + 42


NOTWRITTEN = ("Not written", "red", "2 3")
NOTMADE = ("Not made", "red", "2 3")
NOTDRAFTED = ("Not drafted", "red", "2 3")
INTREE = ("In the tree at G12", "teal", None)
PUBLISHED = ("Published 2026.11.16 · outside the corpus", "grey", "6 4")

MET = "[[green|Met]]"
NOTMET = "[[red|Not met]]"
NOTDONE = "[[red|Not done]]"


# ---------------------------------------------------------------------------------------------- the diagram
def build():
    c = Canvas(ID, "TLA+ checks run in the tla-kit image: the image is a pin by its published digest, CI reruns every "
               "proof module in it and refuses a count that differs, and the prover pin moves to the image's build only "
               "by its own pull request",
               "ADR-0077 (Proposed, 2026.11.16) answers tla-kit's Phase 2, which asks four things of TOPAK: run the "
               "`tlc` job in the image, add a `proofs` job, fix the pin key the skill's scripts read, and record the pin. "
               "**Today CI does not rerun the proofs**: `tools/TLAPS-PIN` names a 1.6.0-pre build at `7824dab` for "
               "arm64-darwin that upstream no longer serves, 1.9 GB and untracked, so `results.yml` has no proofs job and "
               "`checks.yml` only reports which proofs are stale. The record adds a pin file `TLA-KIT-PIN`, runs `tlc` "
               "and a new `proofs` job in the pinned image, adds the owed full digest to `tools/TLAPS-PIN`, and "
               "recommends moving the prover pin to the image's `ff40755`, after five reruns, by its own pull request "
               "(D1 is TOPAK's decision; Q1). **The custodian settled one thing ⟨K1⟩: that a record is drafted. Every "
               "other choice is the drafter's, and Q1 to Q3 are open.** **Nothing here is built in TOPAK**: no "
               "`TLA-KIT-PIN`, no container in CI, no `proofs` job, no `binary_sha256` in the pin, no move, no "
               "dependent entry. tla-kit's side exists: `v0.1.0` was published and attested on 2026.11.16, outside the "
               "corpus.",
               W, "ADR-0077 provenance note (⟨K1⟩, Q1–Q3), Status and Status note (C2, C4), Depends on, Relates to, "
               "Carries a debt against, Context (the four asks, F-3, F-4, F-7, F-9, the repeat, upstream #309/#310/"
               "#314/#339/`ff40755`, the measured digest), Decision §1–§7 (§1's field list and `v0.1.0` values, §5's "
               "five steps and the move, §7 item by item), Options considered (whole), Consequences, Open obligations, "
               "Annex A (four entries), History (three rows); tools/TLA-PIN (its header and line); tools/TLAPS-PIN "
               "(every field and comment); tools/LEAN-PIN (header); tools/check-pins.sh (header); tools/tlapm "
               "(header); tools/ci-plan.sh (header); tools/install-tlaps.sh (line 3); spec/proof-sync.sh (header); "
               ".github/workflows/results.yml (header, jobs) and checks.yml (header, steps); spec/defects/"
               "defects-results-2026.10.22.txt (header); the 34 `spec/*-proof-results-*.txt` and 34 "
               "`spec/*-proof-cert-results-*.txt` as counted in the tree (every one names `7824dab`); ADR-0045 Status; "
               "ADR-0046 Status, A1, A2, A3, Open obligations; ADR-0069 Status, §6 G-1, G-3, §9 C-2, §10.2, §10.3; "
               "ADR-0029 A2; G12 §9 (34 proof modules). tla-kit's own files are drawn only as ADR-0077 quotes them.",
               state=STATE_G12)
    X0, X1 = c.x0, c.x1
    WW = X1 - X0
    y = c.y

    # ================================================================== status strip
    y = status_strip(c, X0, X1, y, [
        ("ADR-0077", "proposed", "C2, C4 · drafted 2026.11.16, updated twice that day, not reviewed"),
        ("`TLA-KIT-PIN` (§1)", NOTWRITTEN, ""),
        ("`tlc` in the image (§2)", "notbuilt", ""),
        ("the `proofs` job (§3)", "notbuilt", ""),
        ("`binary_sha256` in `tools/TLAPS-PIN` (§4)", "notbuilt", "value measured, file unchanged"),
        ("the prover pin's move (§5)", NOTMADE, ""),
        ("§6's two corrections", "notbuilt", ""),
        ("Annex A's four dependent entries", NOTDRAFTED, ""),
        ("tla-kit `v0.1.0`", PUBLISHED, ""),
        ("`tools/TLA-PIN`, `tools/TLAPS-PIN`, `tools/check-pins.sh`, `results.yml`", INTREE, ""),
        ("rests on ADR-0069 §6 G-3, §9 C-2, §10.2", "proposed", "2026.11.12"),
        ("ADR-0045 T-0045-29, T-0045-31", "accepted", "C2, C4"),
        ("ADR-0046 §3, §4, A2, A3", "accepted", "C2, C4"),
    ])
    y += c.para(X0, y, WW, "**Proposed means nothing here is in force.** The custodian settled that a record is drafted "
                "for what tla-kit's Phase 2 asks ⟨K1⟩. Every other choice is the drafter's, marked *(drafter's choice)* "
                "where the alternative was live or *(drafter's recommendation)* where tla-kit's `PLAN.md` leaves the "
                "decision to TOPAK (D1). **Three questions are open**: Q1, whether §5's move is made at all; Q2, whether "
                "it waits for tla-kit to carry cvc5 and ethos; Q3, whether `proofs` is strict or ratcheted. **C2** "
                "attaches because §3 claims to rerun every proof module in `spec/`; **C4** because §5, if carried out, "
                "resolves ADR-0046's open obligation \"Track or pin the prover\", and §4 pays the debt `tools/TLAPS-PIN` "
                "records against itself. C1 and C3 do not apply. Not a deployment matter (ADR-0069 §10.3). Closes "
                "nothing. Carries a debt against ADR-0069 (an R-revision), ADR-0045 and ADR-0046 (amendments on §5). "
                "Everything tla-kit's spike found (F-3, F-4, F-7) is tla-kit's run at TOPAK `0ad9f88` and was not "
                "reproduced for the draft.", 14.5, "muted") + 34

    # ================================================================== band 1: today beside the proposal
    y = band(c, X0, y, "What exists today, beside what the record proposes: four rows, three columns (Context; §1–§5; "
             "the pin files and workflows as they are)", status="proposed", extra="middle column: nothing built")
    GAP = 180
    CW = [900, 1420, WW - 900 - 1420 - 2 * GAP]
    CX = [X0, X0 + CW[0] + GAP, X0 + CW[0] + GAP + CW[1] + GAP]
    top = y + 40

    rows = [
        # ---- row A: the image pin
        [("No tla-kit pin, no image, no container", [
            "**`tools/` holds three pins today**: `TLA-PIN`, `TLAPS-PIN`, `LEAN-PIN`, each one line per field. No "
            "`TLA-KIT-PIN` exists, and no `tools/tla-kit` script (the tree; Context, quoting tla-kit's `CONSUMERS.md`: "
            "\"Neither pin file exists yet. Phase 2 adds them, in each project and by its own decision\").",
            "**No job in `results.yml` runs in a container.** Its `tlc` job installs Java with `actions/setup-java` "
            "(Temurin 25, whichever release is current: §2) and Python 3.12 on the runner.",
            "**`tools/check-pins.sh` checks one thing**: the tracked jar against `tools/TLA-PIN`. Its header says the "
            "other two pins are checked where their binaries are cited (`spec/proof-sync.sh`, `tools/lean-sync.sh`).",
         ], "red", {"tint": False, "dash": "6 4"}),
         ("§1 · `TLA-KIT-PIN`, new in `tools/`, in the form of `tools/TLAPS-PIN` ⟨K1⟩", [
            "**One line per field, `key value`** *(drafter's choice)*: `release` (the tla-kit tag), `image` (the full "
            "digest), `commit` (the tla-kit commit the release was built from), `jar_sha256` and `tlapm_sha256` (the "
            "digests that release's `PINS.json` gives for `/opt/tla/tla2tools.jar` and `/opt/tlaps/bin/tlapm`), "
            "`pinned` (the date). **For `v0.1.0`:**",
            "`release v0.1.0`\n`image ghcr.io/scottcochran/tla-kit@sha256:454328cd7464efcf8a27a063c51c10086e09571c462c"
            "73d085b4a249e44950c6`\n`commit bfeecc8f0bf9ea9446488a03ebd92ccb574c421a`\n`jar_sha256 936a262061c914694dfd"
            "669a543be24573c45d5aa0ff20a8b96b23d01e050e88`\n`tlapm_sha256 6182df63c4513b09c31c8de12c37f8045ace9cab2517"
            "c017a2fa75f466685bb2`",
            "**Only a digest tla-kit's release workflow published is pinned** (tla-kit ADR-0002 item 7). A local build "
            "of the image is working output.",
            "**Provenance checked, not assumed**: CI runs `gh attestation verify` on the pinned digest against "
            "`scottcochran/tla-kit` before any job uses the image *(drafter's choice)*. Each attestation is signed "
            "under GitHub's identity, not an issued key: under ADR-0069 §10.1 it meets C-2 and not G-2.",
            "**`tools/check-pins.sh` gains two checks** *(drafter's choice)*: the jar digest in `tools/TLA-PIN` equals "
            "`jar_sha256`; after §5, the binary digest in `tools/TLAPS-PIN` equals `tlapm_sha256`. Until §5 the second "
            "is reported and does not fail, since the pins name different builds on purpose.",
            "**One pull request moves the pin**, with evidence that fits what the release changed, by tla-kit's version "
            "number (tla-kit ADR-0014 item 2): **MAJOR**, a checker moved, waits on a record, as §5 is for the prover; "
            "**MINOR or PATCH**, `results` and `proofs` run green on the pull request and no results file changes; "
            "**before tla-kit's 1.0** the number does not say it, so the pull request reads which pins moved from the "
            "release's `PINS.json` *(drafter's choice)*.",
            "**TOPAK decides its own moves** (tla-kit ADR-0005 item 5). tla-kit's weekly check reads the pin; its "
            "`CONSUMERS.md` log records each change, entered by tla-kit's custodian. This repository sends nothing there.",
         ], "amber", {"status": "notbuilt"}),
         ("tla-kit `v0.1.0`: the first release, attested (Context; Status; §7 item 1)", [
            "**`ghcr.io/scottcochran/tla-kit@sha256:454328cd7464efcf8a27a063c51c10086e09571c462c73d085b4a249e44950c6`**, "
            "published 2026.11.16, built from tla-kit `bfeecc8`, with build-provenance and SBOM attestations that "
            "`gh attestation verify` passes, signed for tla-kit's `release.yml` at `refs/tags/v0.1.0`.",
            "**Its repository is public**; its kept prover release `tlapm-ff40755` exists; it never deletes a released "
            "digest (tla-kit ADR-0014 item 5). It carries the skill's scripts at TOPAK `5ade81e`.",
            "**An image of the TLA+ tools, referenced by digest.** It sets `TLA_JAR` and `TLAPM` to its own jar and "
            "prover, the variables TOPAK's scripts already read (tla-kit ADR-0004 item 1).",
            "**§7's first condition is** " + MET + " **by this release.** The rest are TOPAK's. If tla-kit stops "
            "publishing, the pinned digest still resolves, but no new one comes (Consequences).",
         ], "grey", {})],
        # ---- row B: the jar
        [("The jar: `tools/TLA-PIN` and `tools/tla2tools.jar` (T-0045-29)", [
            "**`v1.7.4 936a262061c914694dfd669a543be24573c45d5aa0ff20a8b96b23d01e050e88`**: version and the sha256 of "
            "`tools/tla2tools.jar`, which is tracked (the file's one line).",
            "**`tools/check-pins.sh` checks the jar against it on every push** (`checks.yml`, \"The TLC jar matches its "
            "pin\", strict because it passes on `main`). Every TLC results file prints the jar's digest; replacing the "
            "jar changes every later results file's Module line, and moving this pin is the record of that (its "
            "header). Form from f1-tla's `tools/TLA-PIN`; ADR-0069 §10.2.",
            "**The `tlc` job today**: one job per module of the tier (`spec/modules.tsv`, tier `pr` on push and pull "
            "request), `tools/check-results.sh` regenerates and compares; a fresh file that differs is uploaded for "
            "reading, never committed (`results.yml` header).",
         ], "blue", {}),
         ("§2 · the `tlc` job runs in the image, and §1's jar check", [
            "**`results.yml`'s `tlc` job runs in the pinned image** (`container:` by digest), in place of "
            "`actions/setup-java`. `tools/check-results.sh` runs unchanged and finds the jar through `TLA_JAR` "
            "(tla-kit ADR-0004 item 4: no adapter).",
            "**The jar is the same bytes as before, so no results file should change.** The first run on a pull "
            "request has to show 0 differences for every module of the tier. The JRE becomes the image's pinned "
            "Temurin 25 build, where `setup-java` gave whichever 25 release was current.",
            "**`tools/ci-plan.sh` adds `TLA-KIT-PIN` to the `tlc` suite's inputs.** Today the suite is `spec/`, the "
            "jar, `TLA-PIN`, `check-results.sh` and `compare-results.py` (its header).",
            "**The `reference`, `lean` and `floor` jobs are not changed.** Their tools are not in the image.",
            "**§1's check**: `tools/check-pins.sh` compares `tools/TLA-PIN`'s digest with `TLA-KIT-PIN`'s "
            "`jar_sha256`. They are equal for `v0.1.0`.",
         ], "amber", {"status": "notbuilt"}),
         ("The image's jar is the same jar (Context; F-4)", [
            "**`PINS.json` names `tla2tools.jar` v1.7.4 at sha256 `936a262061c91469…`**, which is the jar "
            "`tools/TLA-PIN` pins, at `/opt/tla/tla2tools.jar`.",
            "**F-4**: TOPAK's `tools/check-results.sh` on the 14 `pr`-tier modules, in tla-kit's spike at TOPAK "
            "`0ad9f88`: **490 rows, 0 differences**. Repeated from the published image on 2026.11.16: 490 rows and 0 "
            "differences again. Once each, in tla-kit's runs, not in CI (§7 item 3).",
            "**What TLC checks is unchanged by where it runs**: small constants, each mutation failing the property it "
            "targets (H3). A pinned JRE as well as a pinned jar is the gain (Consequences).",
         ], "grey", {})],
        # ---- row C: the prover
        [("The prover: `tools/TLAPS-PIN` and the local build (T-0045-31)", [
            "**`tlapm` 1.6.0-pre, commit `7824dab`, `binary_sha256_16 e150fb793fb28592`, arm64-darwin**, backends Z3 "
            "4.8.9, Zenon 0.8.4 [a268], Isabelle2025, LS4; pinned 2026.10.03 (the file's six fields).",
            "**The file says of itself: \"The full digest is owed: one `shasum -a 256 tools/tlaps-1.6.0-pre/bin/tlapm` "
            "on the machine that ran the proofs.\"** It has no `binary_sha256` field.",
            "**The binary is installed, not tracked**: `tools/install-tlaps.sh` fetches the release into "
            "`tools/tlaps-1.6.0-pre/` (git-ignored; \"1.1 GB compressed, 1.9 GB on disk\", its line 3). `tools/tlapm` "
            "refuses a binary whose digest does not begin with `binary_sha256_16` unless `TLAPM_UNPINNED=1` is set. "
            "Three scripts read the short key: `tools/tlapm`, `tools/install-tlaps.sh`, `spec/proof-sync.sh`.",
            "**The release tag floats**: on 2026.10.03 both `1.6.0-pre` assets were builds of `bfa9468`, so a fresh "
            "install no longer yields the pinned binary (the file's comment). Upstream does not serve `7824dab`.",
            "**All 34 `*-proof-results-*.txt` and all 34 `*-proof-cert-results-*.txt` in `spec/` name `7824dab` "
            "(binary `e150fb793fb28592`)**, counted in the tree for this diagram; so does "
            "`spec/defects/defects-results-2026.10.22.txt`, the record of the two unsound cases reproduced.",
            "**Known unsound in two ways** (ADR-0046 A2, A3): a term under a binder; two terms with one name. A3 "
            "recorded both reported upstream, \"neither fixed as of 2026.11.03\".",
         ], "blue", {}),
         ("§4 · `tools/TLAPS-PIN` gains `binary_sha256` · §5 · the prover pin moves by its own pull request, after "
          "five things (drafter's recommendation; Q1)", [
            "**§4: the full digest, measured 2026.11.16 on the machine that ran the proofs**: "
            "`e150fb793fb285922801252ddf96a227b060be293c2604e87be23935ef371e93`, which begins with the pinned "
            "`e150fb793fb28592`. The owed-digest comment is removed. `binary_sha256_16` stays as the first 16 hex "
            "*(drafter's choice)*: changing its three readers would change three files that work. `tools/check-pins.sh` "
            "checks that the two fields agree. The skill's `setup_check.py --proofs` then reports the prover pinned, "
            "with no change to the skill. [[red|The value is measured; the file is not changed]] (§7 item 5).",
            "**§5, the recommendation to move, for two reasons**: the pinned build has both known unsound cases, and the "
            "image's build carries upstream's fixes for the first and for the collision half of the second; and it is "
            "the only route by which CI reruns the proofs under the pin. **Ratifying this record decides that the "
            "move is made, and when. It does not make the move.** §5 is not a condition of this record: it can be "
            "ratified with the pin still on `7824dab`.",
            "**The move itself, in one pull request, after (a)–(e) (band 2)**: `tools/TLAPS-PIN` names `ff40755`, "
            "x86_64-linux, the image's `tlapm_sha256` as `binary_sha256`, its first 16 hex as `binary_sha256_16`, and "
            "the backends `tla-kit-info` prints; it gains `image`, naming `TLA-KIT-PIN`. The results files of (a) and "
            "(b) are committed. The `proofs` job switches to regenerate and compare.",
            "**The results files that name `7824dab` stay results of `7824dab`** (ADR-0046 A3). The records that cite "
            "them by digest keep citing them *(drafter's choice)*; a record moves its citation by its own amendment.",
            "**Proof runs on the custodian's machine then go through the image**, under emulation on Apple Silicon "
            "(tla-kit measured the full run twice on 12 CPUs: 6 min 43 s on a local build, 417 s from the published "
            "image), by a new `tools/tla-kit` script *(drafter's choice)* that runs a command in the pinned image with "
            "the repository at `/work`. The darwin install is then not the pinned prover, and `tools/tlapm` refuses it "
            "without `TLAPM_UNPINNED=1`, as it should. [[red|Not made.]]",
         ], "amber", {"status": "notbuilt"}),
         ("The image's prover: `tlapm` 1.6.0-pre at `ff40755`, x86_64-linux (Context)", [
            "**Installed binary sha256 `6182df63c4513b09c31c8de12c37f8045ace9cab2517c017a2fa75f466685bb2`**, at "
            "`/opt/tlaps/bin/tlapm`; the image sets `TLAPM` to it.",
            "**Its tarball is kept** in a release of tla-kit's own, `tlapm-ff40755` (tla-kit ADR-0005 item 2): the "
            "reproducibility of the install that ADR-0046's open obligation asks about (C4).",
            "**`ff40755` (\"Add soundness test for ENABLED binder order.\", 2026.11.10) is 5 commits ahead of #314's "
            "merge and 4 ahead of #339's**, behind neither: both fixes are in the build (band 3).",
            "**No cvc5 and no ethos in the image** (tla-kit Phase 6), so the certified configuration cannot run in it "
            "(§3; §5 (c); Q2).",
            "**D1 is TOPAK's**: \"Does TOPAK move `tools/TLAPS-PIN` to the image's Linux prover? TOPAK's decision, "
            "made there.\" tla-kit ADR-0005 item 5: \"tla-kit does not decide a project's pin.\"",
         ], "grey", {})],
        # ---- row D: CI
        [("CI today: `checks.yml` and `results.yml` (ADR-0069 §10.2, Proposed)", [
            "**`checks.yml`, on every push and pull request, no prover**: `tools/check-pins.sh` (strict), "
            "`spec/proof-sync.sh` (strict: every `spec/<M>_proof.tla`'s newest results file names the digests of its "
            "EXTENDS chain as proved, and `tools/TLAPS-PIN`'s prover; exit 1 if a proof is stale), "
            "`tools/verify-manifest.sh --all`; then the ratchets: corpus pins, Lean results, path citations, record lint.",
            "**`results.yml`, for the suites a change touches (`tools/ci-plan.sh`)**: `plan`, `tlc`, `reference`, "
            "`lean`, `floor`. **No `proofs` job.** Its header: \"Not here, and why: TLAPS. The pinned prover "
            "(tools/TLAPS-PIN, arm64-darwin) is not what upstream serves, so a runner cannot rerun the proofs with it "
            "(ADR-0069 §6 G-3); checks.yml reports which proofs are stale.\"",
            "**ADR-0069 §6 G-3**: \"A gate that cannot be rerun from its pin is checked for being in step, not "
            "re-derived.\" Its Consequences say \"CI does not prove\"; its open obligations list \"Hosting the pinned "
            "prover\" (Context).",
            "**What CI proves today**: nothing. It checks that results files name the pinned prover and match their "
            "modules' digests (Consequences).",
         ], "blue", {}),
         ("§3 · a `proofs` job reruns every proof module in the image, and refuses a count that differs", [
            "**Which modules**: every `spec/*_proof.tla`, as `spec/proof-sync.sh` enumerates them (the C2 claim), in "
            "one job *(drafter's choice; F-3's run took 539 s in all)*. 34 at G12 (§9).",
            "**When**: `tools/ci-plan.sh` gains a `proofs` suite whose inputs are `spec/*.tla`, `spec/proof-results.sh`, "
            "`tools/tlapm`, `tools/TLAPS-PIN` and `TLA-KIT-PIN`; also on every manual dispatch.",
            "**Until §5, counts only.** Each module is proved under the image's prover with `TLAPM_UNPINNED=1` and "
            "`--cleanfp`; its obligation count and outcome are compared with the newest committed results file. No "
            "results file is written. The output is kept as a workflow artifact, labelled working output that names "
            "a prover the results files do not.",
            "**After §5, regenerated and compared.** `spec/proof-results.sh` writes a fresh file per module, compared "
            "with the committed one as `tlc` compares TLC's. A file that differs is kept for reading; the committed "
            "file is regenerated by hand as a new dated file. CI never writes one (ADR-0069 §6 G-1).",
            "**Strict** *(drafter's choice; Q3)*: F-3 found every count equal, and §10.2 makes strict a check that "
            "passes on `main`. If the first run on `main` does not pass, the job is ratcheted and the findings listed.",
            "**Not in this job**: the certified runs (`spec/proof-cert.sh`) and the defect run's certified step, since "
            "the image has no cvc5 and no ethos; and `spec/proof-scan.sh`, about 16 minutes, on manual dispatch only "
            "*(drafter's choice)*.",
            "**What a green job means**: a carrier's check under ADR-0069 §9 C-2, it refuses and never admits. "
            "T-0045-13 stays excluded. The evidence is the committed results file and its digest, as before. **A pass "
            "corroborates and does not regenerate; a failure may be the newer prover's and not the proof's** "
            "(Consequences).",
            "**This reverses ADR-0069 §6 G-3 for this repository**: once this job exists, a proof is rerun, until §5 "
            "under another build than the pin. ADR-0069 is Proposed, so an R-revision is owed (Annex A item 1).",
         ], "amber", {"status": "notbuilt"}),
         ("tla-kit's Phase 2 asks four things of TOPAK (`PLAN.md`, quoted in Context)", [
            "\"TOPAK: run the `tlc` job in the image; add a `proofs` job that reruns every proof module; fix the pin "
            "key the skill's scripts read (`binary_sha256`, where `tools/TLAPS-PIN` has `binary_sha256_16`).\"",
            "\"Before D1 the proofs job reports counts only. After it, the results files are regenerated in the image.\"",
            "\"Each project's tla-kit pin is recorded in `CONSUMERS.md`'s log (ADR-0014 item 6).\"",
            "\"**Done when** a pull request in TOPAK shows its proofs rerun in CI.\" That is §7 item 4.",
            "**F-3, the spike's proof run at TOPAK `0ad9f88`, 4 CPUs**: under `ff40755`, 34 of 34 proof modules prove, "
            "13,622 obligations, every count equal to its committed results file, 539 s. Repeated from the published "
            "image under emulation on 12 CPUs: 34 of 34, 13,622, every count equal, 417 s. tla-kit's runs, not "
            "reproduced in TOPAK; no results file names them.",
            "**F-9**: the skill's `tla_common.py` reads `binary_sha256`; `tools/TLAPS-PIN` has `binary_sha256_16`. "
            "Read literally, the skill's proof scripts treat TOPAK's prover as unpinned. `find_prover` confirms it, and "
            "still does at TOPAK `5ade81e`.",
         ], "grey", {})],
    ]
    arrows = [
        ("§1: a pin file for it", "§1: pinned by its published digest"),
        ("§2: the same jar, in a container", "`TLA_JAR`; the same bytes"),
        ("§4 adds the digest; §5 would move the pin", "`TLAPM`; `ff40755` after §5 (Q1)"),
        ("§3 adds a job `results.yml` lacks", "Phase 2's four asks; D1"),
    ]
    ry = top
    row_bottoms = []
    for specs, (lab_l, lab_r) in zip(rows, arrows):
        h = max(c.card(0, 0, CW[i], t, b, draw=False, size=S, status=k.get("status"))
                for i, (t, b, _, k) in enumerate(specs))
        for i, (t, b, acc, k) in enumerate(specs):
            c.card(CX[i], ry, CW[i], t, b, accent=acc, h=h, size=S, **k)
        ay = ry + 44
        c.arrow([(CX[0] + CW[0] + 2, ay), (CX[1] - 3, ay)], "amber", sw=2.2, label=lab_l, lpos=0.5, lw=112)
        c.arrow([(CX[2] - 2, ay), (CX[1] + CW[1] + 3, ay)], "grey", sw=2.2, label=lab_r, lpos=0.5, lw=112)
        row_bottoms.append(ry + h)
        ry += h + 44
    pic_bot = row_bottoms[-1]
    c.region(CX[0] - 24, top - 50, CW[0] + 48, pic_bot - top + 50 + 28,
             "Today, at G12: the tree as it is (T-0045-29, T-0045-31; ADR-0069 §10.2)", "blue", dash=None)
    c.region(CX[1] - 24, top - 50, CW[1] + 48, pic_bot - top + 50 + 28,
             "ADR-0077 proposes · Proposed · nothing here is built", "amber", dash="10 6")
    c.region(CX[2] - 24, top - 50, CW[2] + 48, pic_bot - top + 50 + 28,
             "tla-kit, outside the corpus, as ADR-0077 quotes it · `v0.1.0` published 2026.11.16", "grey")
    lg = c.legend(X0, pic_bot + 60, [
        ("box", "blue", "in the tree at G12"),
        ("box", "amber", "Proposed, not built (dotted border)", "2 3"),
        ("box", "grey", "outside the corpus: tla-kit's files and runs, drawn only as the record quotes them"),
        ("box", "red", "does not exist today", "6 4"),
        ("arrow", "amber", "what the record would change"),
        ("arrow", "grey", "what the image supplies"),
    ])
    y = pic_bot + 60 + lg + 70

    # ================================================================== band 2: §5's five things and the move
    y = band(c, X0, y, "§5: five things before the pull request that moves `tools/TLAPS-PIN`, then the move "
             "(drafter's recommendation; Q1, Q2)", status="proposed", extra="not a condition of this record")
    wt = WW
    cols = [("Step", 80, {"bold": True}), ("What §5 asks", 1560),
            ("What the tree holds today (the diagram's reading)", 1000)]
    cols.append(("State", wt - sum(cl[1] for cl in cols)))
    t = c.table(X0, y, cols, [
        {"cells": ["(a)", "**The defect record is rerun under `ff40755`, in the image, and read.** Every listing of "
                   "`spec/proof-certification.md` §8 is read for its outcome under every route: tlapm, the certified "
                   "run and TLC. The run states, for each false statement, whether it still proves on any route, and "
                   "for each true statement, whether it still proves. The capture listings (`CaptureName`, "
                   "`CapturePTL`) are read separately, since #339 does not say it addresses a capture. A successor of "
                   "`defects-run.sh` states its expectations for each build, so that a fixed case reads as the expected "
                   "outcome and not as \"DIFFERS\". Its results are a new dated file.",
                   "`spec/defects/defects-run.sh` states its expectations of `7824dab` (\"Both cases reproduce\"); "
                   "`spec/defects/defects-results-2026.10.22.txt` (`692d74d63b6bbec4`) stays the record of `7824dab`: "
                   "13 listings, tlapm, the certified run and TLC. F-7 found 13 of the expected lemmas fail under "
                   "`ff40755`, the false statements among them, with the certified step unable to run.",
                   NOTDONE], "accent": "red"},
        {"cells": ["(b)", "**Every proof module is regenerated in the image**, with `spec/proof-results.sh` "
                   "(`5476b45862cf54b9`), as a new dated results file. The counts are compared with `7824dab`'s, and "
                   "every difference is listed and explained.",
                   "34 `spec/*-proof-results-*.txt`, every one naming `7824dab`. F-3 found every count equal under "
                   "`ff40755`, in tla-kit's runs.",
                   NOTDONE], "accent": "red"},
        {"cells": ["(c)", "**The certified configuration is rerun** with `spec/proof-cert.sh` (`315fa3d07b7a42de`), "
                   "for every module with a certified results file. Without this rerun, those modules' certified "
                   "standing rests on `7824dab`'s files and not on the pin. The image has no cvc5 or ethos. **The "
                   "recommendation is to wait for tla-kit to carry them** (Q2). Supplying them from outside would put "
                   "tools in the run that the image's digest does not name (tla-kit ADR-0002 item 6, ADR-0004 item 4).",
                   "34 `spec/*-proof-cert-results-*.txt`, every one naming `7824dab`, against the eleven certified "
                   "modules ADR-0046 A1 listed. Which of the 34 certify was not counted for the draft (§5 (c)). The "
                   "image cannot run this step today.",
                   NOTDONE + " · waits on tla-kit Phase 6 (Q2)"], "accent": "red"},
        {"cells": ["(d)", "**`spec/proof-scan.sh` (`9da631cea50b3807`) is rerun under `ff40755`, and read.** Whether "
                   "the scan is still needed after #339 is for ADR-0046 to say, by amendment. This record does not "
                   "retire it.",
                   "`spec/proof-scan.sh` exists; about 16 minutes (§3). Not in the `proofs` job; manual dispatch only.",
                   NOTDONE], "accent": "red"},
        {"cells": ["(e)", "**The records that cite the two cases are read**: ADR-0037, ADR-0045, ADR-0046, ADR-0053 and "
                   "ADR-0069, and `spec/proof-certification.md` §8 and §10. Their dependent entries are drafted "
                   "(Annex A items 2 and 3).",
                   "ADR-0037 and ADR-0053 were not re-read for the draft (provenance note); §5 (e) owes it. Annex A: "
                   "\"None is drafted.\"",
                   NOTDONE], "accent": "red"},
        {"cells": ["The move", "**One pull request**: `tools/TLAPS-PIN` names `ff40755`, x86_64-linux, `tlapm_sha256` "
                   "as `binary_sha256` and its first 16 hex as `binary_sha256_16`, the backends `tla-kit-info` prints, "
                   "and gains `image` naming `TLA-KIT-PIN`; (a)'s and (b)'s results files are committed; `proofs` "
                   "switches to regenerate and compare; `7824dab`'s files stay `7824dab`'s (ADR-0046 A3); proof runs on "
                   "the custodian's machine go through the image (`tools/tla-kit`, new).",
                   "`tools/TLAPS-PIN` names `7824dab`, arm64-darwin, `binary_sha256_16` only, no `image` field. No "
                   "`tools/tla-kit`.",
                   "[[red|Not made]] · Q1 open"], "accent": "amber"},
    ], size=S, accent="amber")
    y += t + 24
    y += row_cards(c, X0, y, WW, 36, [
        ("After §5: what the corpus would cite (Consequences)", [
            "**Two prover builds**: `7824dab` in the files the accepted records cite, and `ff40755` in every file "
            "after. A reader has to tell which a citation is on.",
            "**The defect record has a successor and two expectations**, one per build.",
            "**Proving on the custodian's machine runs under emulation, and needs Docker.**",
            "**The prover TOPAK cites** is one whose tarball is kept and whose digest is published and attested, and "
            "which upstream has fixed for the first case and for collisions. ADR-0046's open obligation on the "
            "prover's install is answered.",
        ], "amber", {"tint": False}),
        ("Until §5: what a `proofs` run can and cannot say (§3; Consequences)", [
            "**`proofs` reruns under a build the results files do not name.** A pass corroborates and does not "
            "regenerate. A failure may be the newer prover's and not the proof's, and has to be read as such.",
            "**Every pull request that touches a proof module reruns it.** Before, CI only checked that results files "
            "named the pinned prover and matched their modules' digests.",
            "**TLC runs on a pinned JRE as well as a pinned jar** (§2). The skill's scripts recognise TOPAK's prover "
            "pin (§4).",
        ], "teal", {"tint": False}),
        ("§6: two corrections the session listed, made with §4", [
            "**`spec/defects/defects-run.sh` says plainly when its certified step cannot run**, where today it prints "
            "empty counts (session record §9 item 5).",
            "**`tools/install-tlaps.sh` states the size of what it fetches as measured.** The session measured the "
            "current x86_64 tarball at 52 MB; the script says \"1.1 GB compressed, 1.9 GB on disk\" (F-6; its line 3 "
            "today). The darwin tarball was not measured, so the record does not say which figure is wrong. "
            "[[red|Not made]] (§7 item 6).",
        ], "amber", {"status": "notbuilt"}),
    ]) + 70

    # ================================================================== band 3: the evidence and upstream
    y = band(c, X0, y, "What the draft rests on: tla-kit's spike, upstream's fixes, and the owed digest (Context; "
             "Status note)", status="proposed", extra="none of it reproduced in TOPAK")
    g = 40
    wl = 1900
    wr = WW - wl - g
    xr = X0 + wl + g
    c.text(X0, y + 16, "**What tla-kit's spike found of TOPAK**, at TOPAK `0ad9f88`, run once on 4 CPUs (session "
           "record §4), and repeated from the published image on 2026.11.16 under emulation on 12 CPUs", 15, "ink")
    cols = [("Finding", 110, {"bold": True}), ("What was run", 560), ("Result, as the record states it", 830)]
    cols.append(("Standing in TOPAK", wl - sum(cl[1] for cl in cols)))
    t = c.table(X0, y + 32, cols, [
        ["F-3", "Every proof module under `ff40755`, in the image", "**34 of 34 proof modules prove, 13,622 obligations, "
         "every count equal to its committed results file**, in 539 s; repeated: 34 of 34, 13,622, every count equal, "
         "417 s", "tla-kit's runs; no TOPAK results file names `ff40755`"],
        ["F-4", "`tools/check-results.sh` on the 14 `pr`-tier modules", "**490 rows, 0 differences**; repeated: 490 rows, "
         "0 differences", "once, not in CI (§7 item 3)"],
        ["F-7", "`spec/defects/defects-run.sh` under `ff40755`", "**Does not reproduce its record**: \"Of the lemmas the "
         "record expects to prove, 13 fail (12 it expects SMT to prove, 1 LS4), the false statements among them; 5 "
         "others it expects SMT to prove still prove; TLC still finds all 8 statements false\". The certified step "
         "could not run (no cvc5, no ethos). Repeated: the same lines, with two state counts of violated temporal "
         "properties different, counts that depend on TLC's clock",
         "an inference from one uncertified run (Context); §5 (a) reads it"],
        ["F-9", "The skill's `tla_common.py` at `find_prover`", "Reads `binary_sha256`; `tools/TLAPS-PIN` has "
         "`binary_sha256_16`; so the skill's proof scripts treat TOPAK's prover as unpinned", "stands at `5ade81e`; "
         "§4 answers it"],
    ], size=S, accent="grey")
    bl = stack(c, X0, y + 32 + t + 18, wl, [
        ("No module is asked for; one T-0045 instance (§7; Status note)", [
            "**No module** *(drafter's choice)*: the record moves where tools run and adds checks that refuse. It states "
            "no property of the mechanism. `tla-kit:spec/PinLifecycle.tla` models the pin process on tla-kit's side.",
            "**§5 adds an instance of T-0045-31**, which ADR-0045 Annex B and ADR-0046 A3 already provide for (\"A "
            "release that fixes either is a new instance of T-0045-31, by its digest\"). It reverses no accepted "
            "clause: C3 does not apply. C1 does not apply: no privileged path gains an obligation.",
        ], "teal", {"tint": False}),
    ])
    br = stack(c, xr, y, wr, [
        ("Upstream has moved since ADR-0046 A3 (read through the GitHub API, 2026.11.16)", [
            "**#309, the first case (a term under a binder)**: closed 2026.11.10 by a maintainer, citing PR #314, \"Do "
            "not prove false theorems about ENABLED, <>, and \\cdot under a binder\", merged as `265da7476b69`.",
            "**#310, the second case (two terms with one name)**: open. A maintainer commented that \"Collisions are "
            "not checked\" is fixed by PR #339, merged that day as `a0e1bd370986`, which uses \"the full 128-bit MD5 "
            "digest instead of a truncated prefix\". **It does not say whether the hashed print now tells a bound "
            "variable from a constant of its name**, the capture half of the case.",
            "**Both fixes are in `ff40755`**, the build tla-kit pins. **Neither has been checked in TOPAK**, and the "
            "capture half has not been looked at (Open obligations).",
        ], "grey", {"tint": False}),
        ("The owed digest, measured (Context; §4)", [
            "`tools/TLAPS-PIN` says \"The full digest is owed\". Run by the assistant on 2026.11.16 on the machine that "
            "ran the proofs: `e150fb793fb285922801252ddf96a227b060be293c2604e87be23935ef371e93`, which begins with the "
            "pinned `e150fb793fb28592`. **Measured, not written**: the file still has the owed-digest comment.",
        ], "blue", {"tint": False}),
    ], gap=18)
    y = max(bl, br) + 70

    # ================================================================== band 4: options, whole
    y = band(c, X0, y, "Options considered, whole", status="proposed")
    cols = [("Option", 820, {"bold": True}), ("Disposition", WW - 820)]
    t = c.table(X0, y, cols, [
        {"cells": ["**Keep `7824dab` and host it**, on a macOS arm64 runner with the binary as a release asset "
                   "(ADR-0069's \"Hosting the pinned prover\")",
                   "[[red|Not taken]] *(drafter's recommendation)*. The pin would stay on a build with both unsound "
                   "cases. No tarball of it is kept anywhere, and the 1.9 GB install would need its own licence check "
                   "before it could be redistributed, as tla-kit's D7 was for `ff40755`"], "accent": "red"},
        {"cells": ["**Move the prover pin with the CI change**, in one step",
                   "[[red|Not taken.]] tla-kit's plan separates them (\"Before D1 the proofs job reports counts only\"). "
                   "The move needs §5's runs, and the certified one cannot run in the image yet"], "accent": "red"},
        {"cells": ["**Move the pin without the certified rerun** (§5 (c)), leaving the certified modules certified "
                   "under `7824dab` only",
                   "[[red|Not taken]] *(drafter's recommendation)*. **Open for the custodian as Q2.** It moves sooner, "
                   "and leaves certified standing on a prover the pin no longer names"], "accent": "amber"},
        {"cells": ["**Supply cvc5 and ethos to the container** from the runner",
                   "[[red|Not taken.]] Tools in the run that the image's digest does not name (tla-kit ADR-0002 item 6, "
                   "ADR-0004 item 4)"], "accent": "red"},
        {"cells": ["**Pin the image by tag**",
                   "[[red|Not taken.]] A tag can move. tla-kit protects `v*` tags and never moves them (tla-kit "
                   "ADR-0014 item 2), but a digest needs no trust in that"], "accent": "red"},
        {"cells": ["**Rename `binary_sha256_16` to `binary_sha256`** and change its three readers",
                   "[[red|Not taken]] *(drafter's choice)*. §4 adds the full key and keeps the short one"],
         "accent": "red"},
        {"cells": ["**Print the image's digest in every results file** (tla-kit ADR-0002 item 2: \"A project's results "
                   "name it\")",
                   "[[red|Not taken]] *(drafter's choice)*. An image cannot read its own digest, so it would have to be "
                   "passed in. The binary's digest already fixes the prover, and `TLA-KIT-PIN` at the results file's "
                   "commit names the image. **The alternative is live**"], "accent": "amber"},
        {"cells": ["**A new T-0045 row for the image**",
                   "[[red|Not taken]] *(drafter's choice)*. The image carries T-0045-29's jar and T-0045-31's prover, "
                   "which already have rows, and a runtime. ADR-0045's dependent entries (Annex A item 2) name the "
                   "image in those rows' instances. A reviewer who counts the JRE and base as components may prefer a "
                   "row. The next free id is T-0045-41"], "accent": "amber"},
        {"cells": ["**`proofs` ratcheted from the start**",
                   "[[red|Not taken]] *(drafter's choice; Q3)*. Strict, unless the first run on `main` fails"],
         "accent": "amber"},
        {"cells": ["**`spec/proof-scan.sh` on every pull request**",
                   "[[red|Not taken]] *(drafter's choice)*. About 16 minutes. On dispatch, and as §5 (d)"],
         "accent": "red"},
    ], size=S, accent="grey")
    y += t + 70

    # ================================================================== band 5: ratification, debts, obligations
    y = band(c, X0, y, "Ratification condition item by item (§7), the entries owed (Annex A), what stays open, "
             "and the record's History", status="proposed", extra="one of nine conditions met")
    cols = [("", 50, {"bold": True}), ("Condition (§7)", 1120), ("State, as the record marks it", 700),
            ("The tree at G12 (the diagram's reading)", 900)]
    cols.append(("Source", WW - sum(cl[1] for cl in cols)))
    t = c.table(X0, y, cols, [
        {"cells": ["1", "**tla-kit has published an attested release**", MET + " on 2026.11.16: `v0.1.0`, "
                   "`sha256:454328cd…50c6`, whose attestations verify. tla-kit's repository is public, and its kept "
                   "prover release `tlapm-ff40755` exists",
                   "Outside the corpus; the diagram takes the record's word", "§7; Status; Context"],
         "accent": "green"},
        {"cells": ["2", "**`TLA-KIT-PIN` names that release by digest, and `tools/check-pins.sh` checks it**", NOTMET,
                   "No `TLA-KIT-PIN` in `tools/`; `check-pins.sh` checks the jar only", "§1"], "accent": "red"},
        {"cells": ["3", "**`tlc` runs in the image on a pull request, with 0 differences on every module of the `pr` "
                   "tier**", NOTMET + ". F-4 found 0 differences once, in tla-kit's spike, not in CI",
                   "`results.yml`'s `tlc` job uses `actions/setup-java`; no `container:`", "§2"], "accent": "red"},
        {"cells": ["4", "**`proofs` runs on a pull request and passes, counts only.** tla-kit's \"Done when\" for "
                   "Phase 2", NOTMET, "`results.yml` has no `proofs` job; `tools/ci-plan.sh` has no `proofs` suite",
                   "§3"], "accent": "red"},
        {"cells": ["5", "**`tools/TLAPS-PIN` carries `binary_sha256`, and the skill's setup check reports the prover "
                   "pinned**", NOTMET + ". The value is measured (Context). The file is not changed",
                   "`tools/TLAPS-PIN` has `binary_sha256_16` and the owed-digest comment", "§4"], "accent": "red"},
        {"cells": ["6", "**§6's two corrections**", NOTMET,
                   "`tools/install-tlaps.sh` line 3 still says \"1.1 GB compressed, 1.9 GB on disk\"", "§6"],
         "accent": "red"},
        {"cells": ["7", "**The dependent entries in Annex A are drafted**, and the pins of the records they touch are "
                   "moved", NOTMET, "Annex A: \"None is drafted.\"", "Annex A"], "accent": "red"},
        {"cells": ["8", "**A reader who is not the drafter** (ADR-0029 A2)", NOTMET,
                   "Every History row: \"not reviewed\"", "§7; History"], "accent": "red"},
        {"cells": ["9", "**The custodian's reading of every drafter's choice and recommendation**, Q1 to Q3 among them",
                   NOTMET, "Q1–Q3 open (provenance note)", "§7"], "accent": "red"},
    ], size=S, accent="blue")
    y += t + 24
    w3 = (WW - 2 * g) / 3
    xs = [X0, X0 + w3 + g, X0 + 2 * (w3 + g)]
    b1 = stack(c, xs[0], y, w3, [
        ("Annex A: four dependent entries owed, none drafted", [
            "**1. ADR-0069, R-revision (dependent on ADR-0077, Proposed).** §6 G-3: the proofs are rerun in CI under "
            "the image's prover. §10.2: \"What the carrier cannot do here\" and its \"As built\" list gain the `proofs` "
            "job and the image. The `sources` row no longer compares the tlapm upstream tag with `tools/TLAPS-PIN`. "
            "Consequences: \"CI does not prove\". Open obligations: \"Hosting the pinned prover\".",
            "**2. ADR-0045 Annex B, amendment (dependent), on §5.** T-0045-31 gains an instance at `ff40755` by its "
            "digest, run from the image named in `TLA-KIT-PIN`, as A3 and A4 provide. Its note gains the upstream "
            "state of 2026.11.16. On §2, T-0045-29's instance names the image. ADR-0045 is pinned "
            "(`mechanism/corpus-pins.sha256`), so the entry moves its pin.",
            "**3. ADR-0046 Open obligations, amendment (dependent), on §5.** \"Track or pin the prover\" is discharged "
            "by tla-kit's kept tarball. The *Upstream* clause gains #314 and #339. Whether `spec/proof-scan.sh` is "
            "still required is decided there, after §5 (d).",
            "**4. ADR-0037 and ADR-0053.** Read for what they say of the two cases, and an entry drafted if one is owed "
            "(§5 (e)).",
        ], "red", {"tint": False, "status": "notbuilt"}),
    ])
    b2 = stack(c, xs[1], y, w3, [
        ("Open obligations", [
            "**tla-kit's Phase 6** (cvc5 and ethos) for §5 (c). Its first release, `v0.1.0`, is published.",
            "**The capture half of tlaplus/tlapm#310**, which #339 does not claim to fix. §5 (a) reads it.",
            "**`spec/proof-certification.md` §8 and §10, and `spec/README.md`**, which describe the cases and the scan "
            "under `7824dab`. They are not records, and are revised with §5.",
            "**The size statement in `tools/install-tlaps.sh`**, measured for the darwin tarball (§6).",
            "**gov-tla** faces the same changes and its own D1. That is its own repository's decision, out of scope.",
        ], "red", {"tint": False, "status": "open"}),
        ("Consequences, negative", [
            "**TOPAK's CI depends on a registry and on a repository with one custodian.** If tla-kit stops publishing, "
            "the pinned digest still resolves (tla-kit ADR-0014 item 5), but no new one comes.",
            "Until §5, `proofs` reruns under a build the results files do not name. After §5, emulation and Docker, "
            "two prover builds cited, and a defect record with two expectations (band 2).",
        ], "grey", {"tint": False}),
    ], gap=18)
    b3 = stack(c, xs[2], y, w3, [
        ("What is settled and by whom (provenance note; Status note)", [
            "**⟨K1⟩ The custodian**: a record is drafted for the changes tla-kit's Phase 2 asks of TOPAK.",
            "**The drafter**: the pin file's form and fields; attestation checked in CI; two new checks in "
            "`check-pins.sh`; reading `PINS.json` before tla-kit's 1.0; one `proofs` job; strict (Q3); the scan on "
            "dispatch; keeping `binary_sha256_16`; citations staying on `7824dab`'s files; a `tools/tla-kit` script; "
            "no module; no T-0045 row.",
            "**The drafter's recommendations, D1 being the custodian's**: move the prover pin (Q1); wait for tla-kit "
            "to carry cvc5 and ethos (Q2).",
            "**Drafted and twice updated on 2026.11.16, not reviewed** (History). Sources were tla-kit at `c721b15` "
            "then `main` at `7b97bed`; TOPAK at `9656e35` then `5ade81e`.",
        ], "brown", {"tint": False}),
        ("Depends on, relates to, closes", [
            "**Depends on**: ADR-0045 (T-0045-29 and T-0045-31, Annex A and B), ADR-0046 (§3, §4; A2 and A3), ADR-0069 "
            "(§6 G-3, §9 C-2 and §10.2; Proposed).",
            "**Relates to**: ADR-0037 and ADR-0053 (they cite the two cases), ADR-0029 A2. Outside the corpus: "
            "tla-kit's ADR-0002, ADR-0004, ADR-0005, ADR-0013 and ADR-0014, and its `PLAN.md` D1 and Phase 2.",
            "**Closes**: nothing.",
        ], "blue", {"tint": False}),
    ], gap=18)
    y = max(b1, b2, b3) + 30

    # ---- History, whole
    c.text(X0, y + 16, "**History, whole** (three rows, each \"not reviewed\")", 15, "ink")
    cols = [("Tag", 60), ("Kind", 60), ("Change", 2020), ("Source", 700)]
    cols.append(("State", WW - sum(cl[1] for cl in cols)))
    t = c.table(X0, y + 32, cols, [
        ["—", "—", "Initial draft. The tla-kit image is a TOPAK pin by published digest in `TLA-KIT-PIN`, checked by "
         "attestation and against `tools/TLA-PIN`; the `tlc` job runs in it; a `proofs` job reruns every proof module "
         "in it, counts only until the prover pin moves, strict; `tools/TLAPS-PIN` gains `binary_sha256`, with "
         "`7824dab`'s full digest measured; the prover pin moves to `ff40755` by its own pull request after the defect "
         "record, every proof module, the certified configuration and the scan are rerun under it and the records "
         "citing the two cases are read (the drafter's recommendation, D1 being the custodian's); two small "
         "corrections; four dependent entries owed. Records that upstream fixed the first case (#314) and the "
         "collision half of the second (#339) on 2026.11.10, both in `ff40755`, with #310 still open",
         "tla-kit `PLAN.md` Phase 2 at `c721b15`; tla-kit's session record of 2026.11.15; tlaplus/tlapm through the "
         "GitHub API, 2026.11.16", "Drafted 2026.11.16 by the assistant at the custodian's direction, not reviewed"],
        ["—", "—", "Brought up to tla-kit's published state. tla-kit released `v0.1.0` (`sha256:454328cd…50c6`, from "
         "`bfeecc8`), attested, with its repository public, so §7's first condition is met. §1 gains `v0.1.0`'s values "
         "and the attestation's result, and says that before tla-kit's 1.0 the version number does not tell a checker "
         "move (tla-kit ADR-0014 item 2). Context and §5 gain tla-kit's repeat of the spike's checks from the published "
         "image. Status and Open obligations follow. No decision changes",
         "tla-kit `main` at `7b97bed`, its Phase 1c record of 2026.11.16; TOPAK `main` at `5ade81e`",
         "Updated 2026.11.16 by the assistant at the custodian's direction, not reviewed"],
        ["—", "—", "Citations made to pass the path check: tla-kit's files are cited as `tla-kit:<path>`, and the two "
         "files this record would create in `tools/`, `TLA-KIT-PIN` and `tla-kit`, are named without their directory, "
         "as is the prover's install directory, which git ignores. No decision changes",
         "TOPAK pull request #58, its `Path citations` check",
         "Updated 2026.11.16 by the assistant at the custodian's direction, not reviewed"],
    ], size=S, accent="grey")
    y += 32 + t
    c.ymax = max(c.ymax, y)
    return c
