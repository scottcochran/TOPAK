"""H7 — The Lean route (ADR-0053, Proposed): a second derivation beside the TLAPS proofs and the floor's gates, in three
uses and one kernel; how a Lean result is made, replayed and kept in step; what it trusts against a certified proof;
and the trusted-base row ADR-0053 proposes. The three Lean results files, tools/LEAN-PIN, ADR-0053's row, dependent
entries, findings and open obligations, and the certified TLAPS results are read at build time."""
import hashlib
import pathlib
import re

from lib import Canvas
from d_h6_proof_certification import read_cert, _clean

ID, SLUG = "H7", "lean-route"

_HERE = pathlib.Path(__file__).resolve()
ROOT = next((p for p in [*_HERE.parents, pathlib.Path.cwd(), *pathlib.Path.cwd().parents]
             if (p / "tools" / "LEAN-PIN").exists()), _HERE.parents[3])
ADR53 = ROOT / "decisions" / "ADR-0053.md"
PIN = ROOT / "tools" / "LEAN-PIN"

PKGS = [
    # (dir, results glob, use, accent, what it states, premise it adds) — ADR-0053 §1, §2
    ("spec/lean", "TopakSpec-results-*.txt", "Re-encoding", "blue",
     "Thirteen TLA+ modules written as Lean transition systems, each definition beside the TLA+ it transcribes. "
     "Their twelve `*_proof.tla` modules' theorems, proved by induction on the reachable states "
     "(`Prelude.invariant`): the step TLAPS hands to LS4. Same inductive invariants, same hypotheses on `Mut`.",
     "The Lean transition system is the TLA+ module. Read, beside the frozen text; `Prelude.lean` states the "
     "conventions and each file the places a reading was chosen."),
    ("mechanism/lean", "Admit-results-*.txt", "Transcription", "teal",
     "`admit.rs`'s `floor_gate` and `compose`, their call site in `topak-node`, and `clock.rs`'s "
     "`subtracting_interval_elapsed`, and the `topak-floor` wrapper, transcribed. `FloorComposition`'s three "
     "composition properties and `admit ⟺ floor_permit ∧ ¬bundle_deny` of the transcription; since 2026.10.06 the "
     "whole decision, wrapper and `compose`, proved a `Decide` step of `FloorComposition`'s re-encoding, on Cedar's "
     "rule as the engine premise (ADR-0053 R2); ADR-0032 §2's \"fails closed\" of the arithmetic.",
     "The Lean function is the Rust function. Read, each definition beside the Rust; no Rust-to-Lean translator was "
     "run. Pinned, not frozen: the Rust moves."),
    ("floor/lean", "TopakFloor-results-*.txt", "Statement in Cedar's model", "violet",
     "The genesis floor and, since R3, **the floor in force**, the `emergency` stage the reference links, each with its "
     "schema S, in cedar-spec's abstract syntax (tag `v4.13.0`), generated through the cedar CLI's parser by `gen.py`. "
     "Each validates, so by cedar-spec's proved `validation_is_sound` it never errors on a conforming input but by a "
     "missing entity; the 62 and 107 cases under the model's authorizer; per-action witnesses.",
     "The CLI's parse and `gen.py`'s walk are the policies and schema. The model's fidelity to the engine is "
     "T-0045-3's own premise, not a new one. Closed evaluations by `native_decide`, which trusts the compiler."),
]

# The thirteen proof modules spec/lean re-encodes, and the Lean file for each (spec/lean/README.md; ADR-0053 §4, R2).
ENC = [("Seats", "Seats"), ("Observers", "Observers"), ("RunSeats", "RunSeats"), ("FloorRouting", "FloorRouting"),
       ("FloorComposition", "FloorComposition"),
       ("NonComposition", "NonComposition"), ("Anchor", "Anchor"), ("BreakGlass", "BreakGlass"),
       ("Coupling", "Coupling"), ("Lease_A1", "Lease_A1"), ("RulesFloorNV_rev5", "RulesFloorNV_rev5"),
       ("Confinement", "Confinement"), ("Confinement_A1", "Confinement")]


def read_results(pkg, glob):
    """-> dict of one Lean results file, as results.sh and tools/lean-report.sh print it."""
    f = sorted((ROOT / pkg).glob(glob))[-1]
    raw = f.read_bytes()
    t = raw.decode("utf-8")
    lines = t.splitlines()
    thms = {m.group(1): m.group(2) for m in (re.match(r"Theorems \(([^)]+)\): (.*)", ln) for ln in lines) if m}
    files = re.findall(r"([A-Za-z0-9_./-]+) \(sha256 ([0-9a-f]{16})", "\n".join(
        ln for ln in lines if ln.startswith(("Transcribes:", "Floor:", "Sources:"))))
    ax = {}
    nthm = 0
    for ln in lines:
        m = re.match(r"info: \S+: '([^']+)' (?:depends on axioms: \[(.*)\]|does not depend on any axioms)", ln)
        if not m:
            continue
        nthm += 1
        for a in ([x.strip() for x in m.group(2).split(",")] if m.group(2) else []):
            key = "`native_decide`, one axiom per use" if "native_decide" in a else f"`{a}`"
            ax[key] = ax.get(key, 0) + 1
    prover = next(ln for ln in lines if ln.startswith("Prover:"))
    kern = re.search(r"libleanshared \(sha256 ([0-9a-f]{16})", prover).group(1)
    return {
        "file": f"{pkg}/{f.name}", "digest": hashlib.sha256(raw).hexdigest()[:16], "thms": thms,
        "files": files, "ax": ax, "nprint": nthm, "kernel": kern,
        "built": next((ln for ln in lines if ln.startswith("Build completed")), "BUILD FAILED"),
        "replay": next((ln for ln in lines if ln.startswith("Replay:")), "Replay: missing"),
    }


def _replay(line):
    """`Replay: leanchecker --fresh X: verdict` -> a rich string with the command in code and the verdict marked."""
    m = re.match(r"Replay: (leanchecker [^:]+): (.*), (accepted|REFUSED)$", line)
    if not m:
        return f"[[red|{line}]]"
    acc = "teal" if m.group(3) == "accepted" else "red"
    return f"**Replay.** `{m.group(1)}`: {m.group(2)}, [[{acc}|{m.group(3)}]]"


def read_pin():
    out = {}
    for ln in PIN.read_text(encoding="utf-8").splitlines():
        if ln and not ln.startswith("#"):
            k, _, v = ln.partition(" ")
            out[k] = v
    return out


def read_adr53():
    t = ADR53.read_text(encoding="utf-8")
    rowA = next(ln for ln in t.splitlines() if ln.startswith("| **T-0045-37** |"))
    rowB = next(ln for ln in t.splitlines() if ln.startswith("| T-0045-37 |"))
    cells = lambda ln: [_clean(x.strip()) for x in ln.strip().strip("|").split("|")]
    sec6 = t.split("### 6. Dependent entries on ratification")[1].split("### 7.")[0]
    deps = [re.sub(r"\s+", " ", b).strip() for b in re.split(r"\n- ", "\n" + sec6.strip())[1:]]
    find = t.split("## Findings")[1].split("## Open obligations")[0]
    finds = [re.sub(r"\s+", " ", b).strip() for b in re.split(r"\n\d+\. ", "\n" + find.strip())[1:]]
    opn = t.split("## Open obligations")[1].split("## History")[0]
    opens = [re.sub(r"\s+", " ", b).strip() for b in re.split(r"\n- ", "\n" + opn.strip())[1:]]
    cond = re.sub(r"\s+", " ", t.split("### 7. Ratification condition")[1].split("## Options")[0]).strip()
    return cells(rowA), cells(rowB), [_clean(d) for d in deps], [_clean(f) for f in finds], \
        [_clean(o) for o in opens], _clean(cond), hashlib.sha256(t.encode()).hexdigest()[:16]


def build():
    res = {p[0]: read_results(p[0], p[1]) for p in PKGS}
    pin = read_pin()
    rowA, rowB, deps, finds, opens, cond, adr_dig = read_adr53()
    cert = {m: read_cert(m) for m, _ in ENC}
    spec = res["spec/lean"]
    total_thm = sum(r["nprint"] for r in res.values())
    c = Canvas(ID, "The Lean route: a second derivation, in three uses and one kernel",
               "Beside the TLAPS proofs and the floor's gates, three Lean 4 packages prove the same claims again by a "
               "different route (ADR-0053, **Proposed**, drafted 2026.10.05). A **re-encoding** writes a TLA+ module as "
               "a Lean transition system; a **transcription** writes a function of the reference in Lean; a "
               "**statement in Cedar's model** writes the floor in cedar-spec's syntax. Each is proved by the Lean "
               "kernel, and each adds one premise that is read and not checked: that the Lean is what it claims to "
               "state. The words stay apart (ADR-0053 §1): TLAPS **proves**, a certified run **certifies**, Lean "
               "**proves in Lean** of an encoding, a transcription or a statement, and TLC **checks**. The TLA+ "
               "module, its TLAPS proof and the Rust stay canonical; nothing here is a claim about the running "
               "reference (T-0045-28).",
               3200,
               f"decisions/ADR-0053.md (Proposed; {adr_dig}), §1–§7, Findings, Open obligations (read at build time); "
               f"the three Lean results files, read at build time: {', '.join(r['file'] for r in res.values())}; "
               "tools/LEAN-PIN (read at build time), tools/install-lean.sh, tools/lean-report.sh, tools/lean-sync.sh; "
               "spec/lean/README.md, mechanism/lean/README.md, floor/lean/README.md (mutation checks); "
               "spec/proof-method.md §5b, §6; spec/proof-certification.md §8, §12; the certified TLAPS results "
               "spec/*-proof-cert-results-*.txt (read at build time, as H6 reads them); ADR-0045 Annex A T-0045-3, "
               "T-0045-28, T-0045-31; ADR-0046 §1, §4, A1; ADR-0030 §3, §5 A1; ADR-0032 §2; "
               "derived/topak-lean-formalization-options-2026.10.05.md")
    X0, X1 = c.x0, c.x1
    W = X1 - X0
    y = c.y

    # ---- status band
    sx = X0
    sx += c.status(sx, y, "proposed", "ADR-0053 · drafted 2026.10.05, after G10") + 14
    c.text(sx, y + 16, "Not ratified. The kernel and toolchain are proposed as trusted-base row **T-0045-37** (§6 below); "
                       "until then a Lean result is evidence no record cites. The packages, the results and the tooling "
                       "are the drafter's.", 14.5, "muted")
    y += 52

    # ================================================================ 1 · three uses
    y += c.heading(X0, y, f"1 · Three uses, one kernel: {total_thm} theorems with their axioms printed, every "
                          f"constant replayed", size=22)
    cw = (W - 2 * 40) / 3
    tops = []
    for i, (pkg, _g, use, acc, states, premise) in enumerate(PKGS):
        r = res[pkg]
        th = [f"**{k}**: {v}" for k, v in r["thms"].items()]
        body = [f"**States.** {states}", "**Theorems** (the results file's lines):", *th,
                f"**Adds the premise.** {premise}",
                f"**Results.** `{r['file']}` (`{r['digest']}`): {len(r['files'])} files by repository path and "
                f"digest; {r['built'].rstrip('.')}.",
                _replay(r["replay"])]
        tops.append((pkg, use, acc, body))
    hs = [c.card(X0 + i * (cw + 40), y, cw, f"`{p}` · {u}", b, accent=a, status="proposed", status_extra="ADR-0053",
                 size=13.5, draw=False) for i, (p, u, a, b) in enumerate(tops)]
    for i, (p, u, a, b) in enumerate(tops):
        c.card(X0 + i * (cw + 40), y, cw, f"`{p}` · {u}", b, accent=a, status="proposed", status_extra="ADR-0053",
               size=13.5, h=max(hs))
    y += max(hs) + 18
    axs = []
    for i, (pkg, _g, use, acc, _s, _p) in enumerate(PKGS):
        r = res[pkg]
        rows = [[k, str(v)] for k, v in sorted(r["ax"].items(), key=lambda kv: -kv[1])]
        rows.append([f"**Theorems with `#print axioms`**", f"**{r['nprint']}**"])
        axs.append(c.table(X0 + i * (cw + 40), y, [(f"Axioms used in `{pkg}`", cw * 0.78),
                                                   ("Theorems using it", cw * 0.22)], rows, size=13.5, accent=acc))
    y += max(axs) + 10
    y += c.para(X0, y, W, "`propext` and `Quot.sound` are Lean's own. `Classical.choice` appears in the spec package "
                "for `NonComposition` alone, whose `Erase` step cases on a set membership as TLA+ does, and in the floor "
                "package through cedar-spec's proofs. `native_decide` appears only in the floor package: the kernel's "
                "`decide` cannot reduce the model's maps and sets, which are built by well-founded recursion (ADR-0053 "
                "§2). No `sorry` anywhere.", 14, "muted") + 40

    # ================================================================ 2 · made and kept in step
    y += c.heading(X0, y, "2 · How a Lean result is made, replayed and kept in step (`tools/lean-report.sh`, "
                          "`tools/lean-sync.sh`)", size=22)
    steps = [
        ("`results.sh`", "teal", ["One per package. The floor's first runs `gen.py`, which regenerates `Genesis.lean` and "
                                  "`Tests.lean` from the floor's files through the cedar CLI."]),
        ("`lake build`, clean", "teal", ["The elaborator turns each proof into a term and the **kernel checks every "
                                         "term** as it is added. Any failure stops the run."]),
        ("`#print axioms`", "grey", ["Every theorem's axioms, joined and sorted so that the file regenerates byte for "
                                     "byte. **Not enough by itself**: §3."]),
        ("`leanchecker --fresh`", "teal", ["Replays every constant the root reaches, Lean's library and cedar-spec "
                                           "included, through the kernel in a fresh environment, from the stored build. "
                                           "The same kernel, a separate process."]),
        ("The results file", "blue", ["Every file transcribed and every Lean source by repository path and digest; the "
                                      "prover line with the kernel's digest; theorems; axioms; the replay's verdict."]),
        ("`tools/lean-sync.sh`", "blue", ["Compares every digest with the tree, and every kernel, toolchain and cedar-spec "
                                          "commit with `tools/LEAN-PIN`. `IN SYNC`, or `STALE` and exit 1."]),
    ]
    n = len(steps)
    gap = 46
    sw = (W - (n - 1) * gap) / n
    shs = [c.card(X0 + i * (sw + gap), y, sw, t, b, accent=a, size=13.5, draw=False) for i, (t, b, a) in
           enumerate([(s[0], s[2], s[1]) for s in steps])]
    sh = max(shs)
    for i, (t, a, b) in enumerate(steps):
        x = X0 + i * (sw + gap)
        c.card(x, y, sw, f"{i + 1} · {t}", b, accent=a, size=13.5, h=sh)
        if i < n - 1:
            c.arrow([(x + sw + 4, y + sh / 2), (x + sw + gap - 4, y + sh / 2)], "ink")
    lx = X0 + (n - 1) * (sw + gap) + sw / 2
    fx = X0 + sw / 2
    c.arrow([(lx, y + sh + 4), (lx, y + sh + 40), (fx, y + sh + 40), (fx, y + sh + 6)], "red", dash="7 5",
            label="STALE: re-read the Lean against what moved, change it if the meaning changed, regenerate",
            lpos=0.5)
    y += sh + 74
    pin_rows = [[f"`{k}`", f"`{v}`"] for k, v in pin.items()]
    pw = W * 0.36
    tp = c.table(X0, y, [("`tools/LEAN-PIN` (read at build time)", pw * 0.42), ("Value", pw * 0.58)], pin_rows,
                 size=13.5, accent="blue")
    kern_ok = all(r["kernel"] == pin["libleanshared_sha256_16"] for r in res.values())
    rx = X0 + pw + 40
    rw2 = W - pw - 40
    keep = [
        "**One toolchain** for all three packages, cedar-spec's own: the two older packages built unchanged on it.",
        f"**Every results file names the pinned kernel**: "
        f"{'[[teal|yes]]' if kern_ok else '[[red|NO]]'}, `libleanshared` `{pin['libleanshared_sha256_16']}`, read "
        "from each file's prover line at build time.",
        "**`tools/install-lean.sh`** installs the toolchain through elan (about 2 GB under `~/.elan`, not tracked) "
        "and compares the kernel, `lean`, `leanchecker` and Lake with the pin, as `tools/install-tlaps.sh` does "
        "for the prover.",
        "**Regenerates byte for byte**: each `results.sh` was run twice on 2026.10.05 and the runs were identical, "
        "which is ADR-0053 §7 (a).",
        "**Frozen or pinned** (ADR-0053 §4): the re-encodings freeze with their base modules on ratification; a "
        "successor module gets a successor Lean file. The transcriptions and the floor statement are pinned, not "
        "frozen, as `Mechanism.tla` is: they follow code and a floor that move.",
        "**Staleness was tested**: one byte appended to `admit.rs` made `tools/lean-sync.sh` report "
        "`mechanism/lean` `STALE` and exit 1; restored, it exited 0.",
    ]
    tk = c.card(rx, y, rw2, "Kept in step, the way the TLAPS proofs are", keep, accent="blue", size=14)
    y += max(tp, tk) + 56

    # ================================================================ 3 · the control
    y += c.heading(X0, y, "3 · Why every results file ends with the replay: the control of 2026.10.05", "red", 22)
    tw3 = W * 0.6
    t3 = c.table(X0, y, [("Step, in a scratch copy of `mechanism/lean`", tw3 * 0.42), ("What Lean said", tw3 * 0.58)], [
        ["A module adds `smuggled : False` with the kernel check off (`set_option debug.skipKernelTC true`, then "
         "`addDecl`), and derives `uses_smuggled : 1 = 2` from it", "`lake build`: **builds**"],
        ["`#print axioms uses_smuggled`", "[[red|\"does not depend on any axioms\"]]"],
        ["`leanchecker Topak.Smuggled`", "[[teal|refused]]: a type mismatch, `True` where `False` was expected; exit 1"],
        ["`leanchecker --fresh Topak`", "[[teal|refused]], the same; exit 1"],
        ["`leanchecker --fresh` on each real package", "accepted; exit 0 (about 25 s, 25 s and 48 s)"],
    ], size=14, accent="red")
    c.card(X0 + tw3 + 40, y, W - tw3 - 40, "What the control shows (ADR-0053 finding 1; proof-method.md §5b)", [
        "An axiom list is a statement about the declarations the environment holds, not about whether the kernel "
        "checked them. A results file with only `#print axioms` would have certified a proof of `1 = 2`.",
        "The replay re-checks every stored constant through the kernel, so a declaration that entered past it is "
        "found. It is **the same kernel** in a fresh process: an independent kernel (lean4lean) is an open "
        "obligation, as ethos is the independent checker for cvc5's proofs.",
        "The corpus's other checkers carry the same kind of control: three lying solvers for `floor/cvc5-checked`, "
        "four stand-in solvers for `spec/smt-checked`.",
    ], accent="red", size=14)
    y += t3 + 56

    # ================================================================ 4 · two routes
    y += c.heading(X0, y, "4 · Two routes to the same theorems: every proof module `spec/lean` re-encodes", size=22)
    y += c.para(X0, y, W, "The TLAPS columns are read from the certified results files, as H6 reads them; the Lean "
                "column from `spec/lean`'s results file. A row is red where the TLAPS proof does not certify: its "
                "theorems are then proved twice, once by TLAPS with an uncertified step and once in Lean with every "
                "step kernel-checked, of the encoding.", 15, "muted") + 12
    cols = [("Proof module", 250), ("TLAPS obligations", 150), ("LS4 steps, unchecked", 160),
            ("Certified run", 360), ("Lean file (`spec/lean/TopakSpec/`)", 290), ("Proved in Lean, with the same "
                                                                                 "hypotheses", W - 1630),
            ("What the Lean route trusts instead", 420)]
    rows = []
    for mod, lf in ENC:
        r = cert[mod]
        th = spec["thms"].get(lf, "")
        if mod == "Confinement_A1":
            th = "the same theorems, under the flag `a1 = true`; by name, `Confinement_A1_SafeAlways`"
        elif mod == "Confinement":
            th = th.replace(" · Confinement_A1_SafeAlways", "") + " (flag `a1 = false`)"
        trust = "the encoding, read; the kernel (T-0045-37, proposed)"
        if mod == "NonComposition":
            trust += "; `Classical.choice`"
        cr = "[[teal|Certified]]" if r["certified"] else f"[[red|NOT CERTIFIED]]: {r['last'][15:]}"
        cells = [f"`{mod}_proof`", f"**{r['n']}**", str(r["ls4"]), cr, f"`{lf}.lean`", th, trust]
        rows.append({"cells": cells, "accent": "red"} if not r["certified"] else cells)
    rows.append({"group": "At the code level and in the model", "accent": "teal"})
    rows.append(["The admit decision, refining `FloorComposition`'s `Decide` (ADR-0053 R2)", "—", "—",
                 "not a TLAPS claim: of the code", "`mechanism/lean/Topak/` `FloorRefinement.lean`",
                 "`codeDecide_refines`: wrapper and `compose` together are a `Decide` step, so `code_behaviours_safe`: all "
                 "five invariants hold of every behaviour in which the code decides; and `decide_is_code`",
                 "the transcriptions, read; the kernel; T-0045-3 at the module's size; the module's four policies, not "
                 "the floor in force"])
    rows.append(["The floor's totality gate", "23 and 41 `holds°`", "—", "not a proof: cedar's term folding, on "
                 "T-0045-3", "`floor/lean/TopakFloor/` `Gates.lean`, `InForce.lean`", "`floor_never_errors` of the "
                 "genesis floor, `inForce_never_errors` of the floor in force (R3), by cedar-spec's proved "
                 "`validation_is_sound`", "the parse, read; the kernel; `native_decide`; T-0045-3"])
    y += c.table(X0, y, cols, rows, size=13.5, accent="blue") + 56

    # ================================================================ 5 · what each trusts
    y += c.heading(X0, y, "5 · What each route still trusts", "red", 22)
    t5w = W * 0.62
    t5 = c.table(X0, y, [("Premise", t5w * 0.26), ("A certified TLAPS proof (ADR-0046 A1)", t5w * 0.37),
                         ("A result proved in Lean (ADR-0053 §2)", t5w * 0.37)], [
        ["The SMT solver", "[[teal|Not trusted]]: an answer counts only with a proof `ethos` accepted",
         "[[teal|Not used]]: arithmetic is `omega`, a decision procedure whose output the kernel checks"],
        ["The temporal step", "[[red|LS4, unchecked]]: one to three obligations per theorem",
         "[[teal|Kernel-checked]]: an induction on `Reachable`"],
        ["The prover's front end", "[[red|Trusted]]: tlapm's translation and normalization",
         "[[teal|Not trusted]]: the elaborator only proposes terms; the kernel checks them, and the replay again"],
        ["What is proved of", "[[teal|The frozen TLA+ text itself]]",
         "[[red|An encoding of it, read]]: the premise this route adds"],
        ["The checker or kernel", "`ethos` and its signature (T-0045-14); Isabelle for Zenon's scripts",
         "The Lean kernel (T-0045-37, proposed); the replay is the same kernel"],
        ["Floor package only", "—", "[[red|The compiler]], where `native_decide` evaluates"],
    ], size=14, accent="red")
    c.card(X0 + t5w + 40, y, W - t5w - 40, "Why two routes, and why the table's premises do not change", [
        "The two routes fail in different places: TLAPS on LS4 and its front end, Lean on the encoding. A theorem "
        "proved by both is wrong only if both fail.",
        "**The premise table cannot say so** (ADR-0053 §5, finding 2). It computes holds = ¬(B·¬d), a conjunction "
        "of premises; two proofs give \"T-0045-31, or T-0045-37 and the encoding\". So no premise moves: the table "
        "keeps T-0045-31 and names the Lean file in its *Checked in* column, as evidence.",
        "**The floor's totality is the exception that changes what it rests on**: from cedar's folding code to the "
        "model's proved validator and T-0045-3, which already reads \"the Cedar engine, as faithful to the Lean "
        "model\".",
    ], accent="blue", size=14)
    y += t5 + 56

    # ================================================================ 6 · the row
    y += c.heading(X0, y, "6 · The trusted-base row ADR-0053 proposes: not in ADR-0045 until ratified", "amber", 22)
    colsA = [("Id", 130), ("Component", 420), ("Layer", 110), ("Trusted for", 380), ("Rungs", 70), ("Class", 110),
             ("Failure can produce", 380), ("Identity fixed by", 400), ("Residual", W - 2000)]
    y += c.table(X0, y, colsA, [{"cells": rowA, "accent": "amber"}], size=13.5, accent="amber") + 14
    colsB = [("Row (Annex B)", 160), ("Instance at the reference", W * 0.5), ("Class here", 130),
             ("Note", W - 160 - W * 0.5 - 130)]
    y += c.table(X0, y, colsB, [{"cells": rowB, "accent": "amber"}], size=13.5, accent="amber") + 14
    y += c.para(X0, y, W, "Both rows are read from ADR-0053 §3 at build time. ADR-0045 is pinned by the reference's "
                "drift test (`mechanism/corpus-pins.sha256`) and changes only by a History row at ratification, so "
                "the row lands there then, with the re-pin, and not before. T-0045-31's row does not change: the TLAPS "
                "proofs still rest on LS4 and, for three modules, on Z3.", 14, "muted") + 44

    # ================================================================ 7 · ratification, findings, open
    y += c.heading(X0, y, "7 · On ratification, what it found, and what is open", size=22)
    w7 = (W - 2 * 40) / 3
    h7 = [c.card(X0, y, w7, "Dependent entries on ratification (ADR-0053 §6)", deps, accent="amber",
                 status="proposed", size=13.5, draw=False),
          c.card(X0 + w7 + 40, y, w7, "Findings (ADR-0053)", finds, accent="red", size=13.5, draw=False),
          c.card(X0 + 2 * (w7 + 40), y, w7, "Open obligations (ADR-0053)", opens, accent="red", status="open",
                 size=13.5, draw=False)]
    hh = max(h7)
    c.card(X0, y, w7, "Dependent entries on ratification (ADR-0053 §6)", deps, accent="amber", status="proposed",
           size=13.5, h=hh)
    c.card(X0 + w7 + 40, y, w7, "Findings (ADR-0053)", finds, accent="red", size=13.5, h=hh)
    c.card(X0 + 2 * (w7 + 40), y, w7, "Open obligations (ADR-0053)", opens, accent="red", status="open",
           size=13.5, h=hh)
    y += hh + 18
    y += c.card(X0, y, W, "Ratification condition (ADR-0053 §7)", [cond], accent="amber", size=14, bullets=False) + 18
    mut = [
        "**Mutation checks, 2026.10.05** (each package's README): nine mutated encodings of the small modules and "
        "nine of the parameterized ones, three of the code (`M_OVERRIDE`, `M_ERR`, R4) and two of the floor (a "
        "type error in `B1`, a permit-all). Each fails to build in the theorem its mutation breaks. Mutations and "
        "witnesses as behaviours stay with TLC, as ADR-0046 §2 says of the TLAPS proofs.",
    ]
    y += c.card(X0, y, W, "What must fail, and did", mut, accent="green", size=14, bullets=False) + 30
    c.legend(X0, y, [("box", "teal", "kernel-checked, or a check that ran"),
                     ("box", "amber", "Proposed (ADR-0053)"),
                     ("box", "red", "trusted unchecked, refused, or a gap"),
                     ("box", "blue", "the record, the pin, the sync"),
                     ("box", "violet", "the floor, genesis-provisional, in Cedar's model")])
    return c
