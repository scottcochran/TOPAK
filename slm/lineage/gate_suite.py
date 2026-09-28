#!/usr/bin/env python3
"""ADR-0035 §8 ratification evidence, items 1 and 2, over synthetic records.

    uv run lineage/gate_suite.py                 # the rule as the ADR writes it
    uv run lineage/gate_suite.py --mode ratio    # the text as first drafted (finding 5)
    uv run lineage/gate_suite.py --mode absolute # the monotone candidate not taken
    uv run lineage/gate_suite.py --json runs/gate-suite.json

1. **Cases.** Every clause E1–E5 and the distillation rule, each seen to fire, including cases
   where it fires *alone*, so no clause passes only because a neighbour caught its case. Also
   the relation's properties (irreflexive, symmetric, not transitive), fail-closed E3, and
   weakest-link strength.
2. **Monotonicity (§2).** Random universes of objects with sizes, declarations and a
   near-duplicate relation. For random lineages A, B and a superset A' ⊇ A of A's ingress,
   rebuild the records, re-measure the overlap and check that no clause (and not the
   distillation rule) turns from fail to pass. A violation prints a minimal counterexample.

Exit status: 0 if every case passes and the property holds, 1 if a case fails, 2 if only the
property is violated. Thresholds here are test values, not proposals.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import independence as ind  # noqa: E402
import record  # noqa: E402
from common import write_json  # noqa: E402

TOOL = "f" * 64
GRAN = "doc"


def thresholds(mode: str) -> dict:
    return {"mode": mode, "theta_exact": 0.01, "theta_near": 0.05, "theta_gen": 0.5,
            "theta_exact_bytes": 100, "theta_near_bytes": 500, "theta_gen_bytes": 1000,
            "near_tool": TOOL, "granularity": GRAN}


def h(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


def obj(name: str, nbytes: int = 1000, gens=(), gshare: float = 0.0, curs=()):
    decl = {"generators": list(gens), "generated_share": gshare, "curators": list(curs)}
    return record.ingress_entry(h("obj:" + name), nbytes, decl, corpus=name.split("/")[0])


def lin(name, family, objs, tok=None, root=None, weights=None, parents=(), rung=0, strength="declared",
        consumed=None):
    return record.build(lineage=name, strength=strength, rung=rung, root=root or h("root:" + name),
                        weights=weights or h("w:" + name), tokenizer=tok or h("tok:" + name), family=family,
                        trainer={"tool": "t", "config": h("cfg:" + name), "seed": 0}, ingress=list(objs),
                        parents=list(parents), consumed=consumed)


# ---------------------------------------------------------------------------------------------
# Synthetic measurement: what the pinned tool would report. Objects are the units here, and
# `near` is a symmetric relation over object digests.

def measure(a: dict, b: dict, near: set = frozenset()) -> dict:
    A = {e["digest"]: e["bytes"] for e in a["ingress"]}
    B = {e["digest"]: e["bytes"] for e in b["ingress"]}

    def matched(X, Y, rel):
        return sum(n for d, n in X.items() if d in Y or any((d, y) in rel for y in Y))

    ex_a, ex_b = matched(A, B, set()), matched(B, A, set())
    nr_a, nr_b = matched(A, B, near), matched(B, A, near)
    small_a = sum(A.values()) <= sum(B.values())
    denom = max(1, min(sum(A.values()), sum(B.values())))
    return {
        "schema": "topak.overlap/0", "tool": TOOL, "params": {"granularity": GRAN},
        "a": {"ingress_set": record.ingress_set_digest(a)}, "b": {"ingress_set": record.ingress_set_digest(b)},
        "exact": {"share_of_smaller": (ex_a if small_a else ex_b) / denom, "matched_bytes_a": ex_a, "matched_bytes_b": ex_b},
        "near": {"share_of_smaller": (nr_a if small_a else nr_b) / denom, "matched_bytes_a": nr_a, "matched_bytes_b": nr_b},
    }


def ov(*reports) -> dict:
    return {frozenset((r["a"]["ingress_set"], r["b"]["ingress_set"])): r for r in reports}


def near_pairs(pairs) -> set:
    return {(x, y) for a, b in pairs for x, y in ((a["digest"], b["digest"]), (b["digest"], a["digest"]))}


# ---------------------------------------------------------------------------------------------
# The §8 lineages, synthetically. Declarations mirror corpora.json.

LID = "fasttext/lid.176"
EDU = "HuggingFaceFW/fineweb-edu-classifier"
LLAMA70 = "meta-llama/Meta-Llama-3-70B-Instruct"

edu = [obj(f"edu/{i}", 1000, curs=(LID, EDU, LLAMA70)) for i in range(20)]
web_extra = [obj(f"web/{i}", 1000, curs=(LID,)) for i in range(60)]
books = [obj(f"books/{i}", 5000) for i in range(10)]
books2 = [obj(f"books2/{i}", 5000) for i in range(10)]
edu23 = [obj(f"edu23/{i}", 1000, curs=(LID, EDU, LLAMA70)) for i in range(20)]
ts_a = [obj(f"tsa/{i}", 500, gens=("openai/gpt-3.5", "openai/gpt-4"), gshare=1.0) for i in range(10)]
ts_b = [obj(f"tsb/{i}", 500, gens=("openai/gpt-3.5", "openai/gpt-4"), gshare=1.0) for i in range(10)]
fresh = [obj(f"fresh/{i}", 1000) for i in range(10)]

L_A = lin("L-A", "decoder-transformer", edu)
L_B = lin("L-B", "ssm", books)
L_A1 = lin("L-A'", "decoder-transformer", books[:2], tok=L_A["tokenizer"], root=L_A["root"], parents=[L_A])
L_C = lin("L-C", "ssm", edu + web_extra)  # FineWeb ⊃ FineWeb-Edu
L_D = lin("L-D", "decoder-transformer", books2)
L_T = lin("L-T", "decoder-transformer", ts_a)
L_T2 = lin("L-T2", "ssm", ts_b)
L_E5 = lin("L-E5", "ssm", edu23)


def cases(mode: str):
    """(name, A, B, overlaps, expect_fired, exact) — `exact` means the fired set must equal the
    expectation, i.e. the clause fired alone."""
    m = lambda a, b, near=(): measure(a, b, near_pairs(near))  # noqa: E731
    v1 = lin("L-A v1", "decoder-transformer", fresh[:3], root=h("root:shared"))
    v2 = lin("L-A v2", "ssm", fresh[3:6], root=h("root:shared"))
    merge = lin("L-M", "ssm", fresh[6:9], parents=[lin("donor", "rwkv", [], weights=L_A["weights"])])
    teacher_b = lin("L-S", "ssm", [obj("syn/0", 500, gens=(f"topak-weights:{L_A['weights']}",), gshare=1.0)])
    near_only = lin("L-N", "ssm", [obj(f"nn/{i}", 1000) for i in range(20)])
    same_tok = lin("L-K", "ssm", fresh[:4], tok=L_A["tokenizer"])
    no_curator_c = lin("L-C0", "rwkv", [obj(f"web0/{i}", 1000) for i in range(40)])
    return [
        ("pass: L-A ⊥ L-B (web-edu/llama vs books/ssm)", L_A, L_B, ov(m(L_A, L_B)), set(), True),
        ("E1: L-A vs its fine-tune L-A'", L_A, L_A1, ov(m(L_A, L_A1)), {"E1"}, False),
        ("E1 alone: two versions of one lineage (same root)", v1, v2, ov(m(v1, v2)), {"E1"}, True),
        ("E1 alone: weights reused through a parent (merge)", L_A, merge, ov(m(L_A, merge)), {"E1"}, True),
        ("E2 alone: common generator (TinyStories halves)", L_T, L_T2, ov(m(L_T, L_T2)), {"E2"}, True),
        ("E2 alone: one lineage distilled from the other", L_A, teacher_b, ov(m(L_A, teacher_b)), {"E2"}, True),
        ("E3: L-A vs L-C, FineWeb ⊃ FineWeb-Edu (real curators)", L_A, L_C, ov(m(L_A, L_C)), {"E3", "E5"}, True),
        ("E3 alone: near-duplicate overlap only", L_A, near_only,
         ov(m(L_A, near_only, zip(edu[:6], near_only["ingress"][:6]))), {"E3"}, True),
        ("E3 alone: disjoint objects, doc-level exact overlap", L_B, no_curator_c,
         ov({**m(L_B, no_curator_c), "exact": {"share_of_smaller": 0.2, "matched_bytes_a": 8000,
                                               "matched_bytes_b": 8000}}), {"E3"}, True),
        ("E3 alone: no measurement → fails closed", L_A, L_B, {}, {"E3"}, True),
        ("E3 alone: measured by an unpinned tool", L_A, L_B, ov({**m(L_A, L_B), "tool": "0" * 64}), {"E3"}, True),
        ("E4 alone: L-A vs L-D (llama on books)", L_A, L_D, ov(m(L_A, L_D)), {"E4"}, True),
        ("E4 alone: different family, same tokenizer", L_A, same_tok, ov(m(L_A, same_tok)), {"E4"}, True),
        ("E5 alone: same classifier, different crawl", L_A, L_E5, ov(m(L_A, L_E5)), {"E5"}, True),
        ("irreflexive: L-A vs L-A", L_A, L_A, ov(m(L_A, L_A)), set(ind.CLAUSES), True),
    ]


def run_cases(mode: str, out: list) -> bool:
    th = thresholds(mode)
    ok_all, alone = True, set()
    print(f"cases (mode {mode})")
    for name, a, b, ovs, expect, exact in cases(mode):
        r = ind.evaluate(a, b, th, ovs)
        fired = set(r["fired"])
        ok = fired == expect if exact else expect <= fired
        if ok and exact and len(expect) == 1:
            alone |= expect
        ok_all &= ok
        why = "; ".join(f"{c}: {r['clauses'][c]['why']}" for c in r["fired"]) or "all clauses hold"
        print(f"  {'PASS' if ok else 'FAIL'}  {name:<58} fired {sorted(fired) or '∅'}  {why[:90]}")
        out.append({"case": name, "ok": ok, "expect": sorted(expect), "fired": sorted(fired)})

    # Distillation.
    for r_, want in ((L_T, True), (L_A, False), (L_C, False)):
        got, why = ind.distillation(r_, th)
        ok = got == want
        ok_all &= ok
        print(f"  {'PASS' if ok else 'FAIL'}  distillation({r_['lineage']}) = {got:<5} {'':<34} {why}")
        out.append({"case": f"distillation {r_['lineage']}", "ok": ok, "expect": want, "got": got})

    # Symmetry over every pair of the §8 lineages, with measurements for all.
    pool = [L_A, L_B, L_A1, L_C, L_D, L_T, L_T2, L_E5]
    ovs = ov(*(measure(a, b) for a in pool for b in pool))
    sym = all(set(ind.evaluate(a, b, th, ovs)["fired"]) == set(ind.evaluate(b, a, th, ovs)["fired"])
              for a in pool for b in pool)
    ok_all &= sym
    print(f"  {'PASS' if sym else 'FAIL'}  symmetric over all {len(pool)}² ordered pairs")

    # Not transitive: A ⊥ B and B ⊥ C, but not A ⊥ C.
    a_, b_, c_ = L_A, L_B, L_D
    ovs3 = ov(measure(a_, b_), measure(b_, c_), measure(a_, c_))
    chain = [ind.evaluate(x, y, th, ovs3)["independent"] for x, y in ((a_, b_), (b_, c_), (a_, c_))]
    nt = chain == [True, True, False]
    ok_all &= nt
    print(f"  {'PASS' if nt else 'FAIL'}  not transitive: L-A⊥L-B {chain[0]}, L-B⊥L-D {chain[1]}, L-A⊥L-D {chain[2]}")

    # Strength: weakest link.
    hi = lin("hi", "ssm", fresh[:2], rung=3, strength="projected")
    hi2 = lin("hi2", "rwkv", fresh[2:4], rung=2, strength="projected")
    child = lin("child", "ssm", fresh[4:5], rung=3, strength="projected", parents=[L_A])
    st = (hi["strength"], ind.evaluate(hi, hi2, th, ov(measure(hi, hi2)))["strength"],
          ind.evaluate(hi, L_B, th, ov(measure(hi, L_B)))["strength"], child["strength"], child["rung"])
    st_ok = st == ("projected", "projected", "declared", "declared", 0)
    ok_all &= st_ok
    print(f"  {'PASS' if st_ok else 'FAIL'}  weakest link: rung-3 record {st[0]}, projected pair {st[1]}, "
          f"mixed pair {st[2]}, child of a rung-0 parent {st[3]} at rung {st[4]}")

    missing = [c for c in ind.CLAUSES if c not in alone]
    print(f"  coverage: fired alone at least once: {sorted(alone)}" + (f"; NEVER alone: {missing}" if missing else ""))
    return ok_all and not missing


# ---------------------------------------------------------------------------------------------

def property_check(mode: str, trials: int, seed: int, out: dict) -> bool:
    """§2: adding to what a round COULD read (ingress) never turns a fail into a pass. The extra
    objects enter A's ingress and not its consumed set: the round is charged with more root and
    Read nothing more."""
    th = thresholds(mode)
    # Scale byte thresholds to the random universe so both outcomes are common.
    th.update(theta_exact=0.2, theta_near=0.3, theta_gen=0.3, theta_exact_bytes=2500, theta_near_bytes=4000,
              theta_gen_bytes=3000)
    rng = random.Random(seed)
    violations: dict[str, list] = {}
    checked = 0
    for t in range(trials):
        U = [obj(f"u{t}/{i}", rng.randint(100, 2000),
                 gens=rng.choice([(), (), ("g1",), ("g2",)]), gshare=rng.choice([0.0, 0.5, 1.0]),
                 curs=rng.choice([(), (), ("c1",), ("c2",)])) for i in range(24)]
        for e in U:
            if not e["generators"]:
                e["generated_share"] = 0.0
        near = {(U[i]["digest"], U[j]["digest"]) for i in range(24) for j in range(24)
                if i != j and rng.random() < 0.04}
        near |= {(y, x) for x, y in near}
        sa = rng.sample(U, rng.randint(1, 8))
        sb = rng.sample(U, rng.randint(1, 8))
        extra = rng.sample([u for u in U if u not in sa], rng.randint(1, 8))
        A = lin("A", "decoder-transformer", sa, root="rA", weights="wA", tok="tA")
        A2 = lin("A", "decoder-transformer", sa + extra, root="rA", weights="wA", tok="tA",
                 consumed=[e["digest"] for e in sa])
        B = lin("B", "ssm", sb, root="rB", weights="wB", tok="tB")
        r1 = ind.evaluate(A, B, th, ov(measure(A, B, near)))
        r2 = ind.evaluate(A2, B, th, ov(measure(A2, B, near)))
        checked += 1
        for c in ind.CLAUSES:
            if not r1["clauses"][c]["pass"] and r2["clauses"][c]["pass"]:
                violations.setdefault(c, []).append((A, A2, B, r1["clauses"][c]["why"], r2["clauses"][c]["why"]))
        d1, d2 = ind.distillation(A, th), ind.distillation(A2, th)
        if d1[0] and not d2[0]:
            violations.setdefault("distillation", []).append((A, A2, B, d1[1], d2[1]))

    print(f"\nmonotonicity in ingress (mode {mode}, {checked} random trials, seed {seed})")
    holds = True
    for c in list(ind.CLAUSES) + ["distillation"]:
        v = violations.get(c, [])
        out[c] = len(v)
        if not v:
            print(f"  holds     {c}")
            continue
        holds = False
        A, A2, B, why1, why2 = min(v, key=lambda x: len(x[1]["ingress"]))
        print(f"  VIOLATED  {c}: {len(v)} of {checked} trials turn fail → pass by adding ingress")
        print(f"            e.g. A has {len(A['ingress'])} objects ({A['ingress_bytes']} B), B has "
              f"{len(B['ingress'])} ({B['ingress_bytes']} B)")
        print(f"            before: {why1}")
        print(f"            after adding {len(A2['ingress']) - len(A['ingress'])} objects to A "
              f"({A2['ingress_bytes'] - A['ingress_bytes']} B): {why2}")
    if not holds and mode == "ratio":
        print("  FINDING 5: a ratio whose denominator grows with ingress is not monotone. Mounting more\n"
              "  (non-overlapping, non-generated) corpus dilutes the share, so §2's over-approximation\n"
              "  helps a pair pass E3 and helps a distillation escape the rule. Compare --mode bounded.")
    return holds


def padding_residual(mode: str, trials: int, seed: int, out: dict) -> None:
    """§7 residual, shown rather than hidden: a round that Reads more than it trains on grows its
    consumed set and can dilute E3 and the distillation rule. Here the extra objects enter both
    ingress and consumed. This is not a violation of §2, which is about ingress alone; the log
    shows the reads and not the training, and only §6 can see the difference."""
    th = thresholds(mode)
    th.update(theta_exact=0.2, theta_near=0.3, theta_gen=0.3, theta_exact_bytes=2500, theta_near_bytes=4000,
              theta_gen_bytes=3000)
    rng = random.Random(seed)
    diluted: dict[str, int] = {}
    for t in range(trials):
        U = [obj(f"p{t}/{i}", rng.randint(100, 2000), gens=rng.choice([(), (), ("g1",), ("g2",)]),
                 gshare=rng.choice([0.0, 0.5, 1.0])) for i in range(24)]
        for e in U:
            if not e["generators"]:
                e["generated_share"] = 0.0
        sa = rng.sample(U, rng.randint(1, 8))
        sb = rng.sample(U, rng.randint(1, 8))
        extra = rng.sample([u for u in U if u not in sa], rng.randint(1, 8))
        A = lin("A", "decoder-transformer", sa, root="rA", weights="wA", tok="tA")
        A3 = lin("A", "decoder-transformer", sa + extra, root="rA", weights="wA", tok="tA")  # Read as well
        B = lin("B", "ssm", sb, root="rB", weights="wB", tok="tB")
        r1 = ind.evaluate(A, B, th, ov(measure(A, B)))
        r3 = ind.evaluate(A3, B, th, ov(measure(A3, B)))
        if not r1["clauses"]["E3"]["pass"] and r3["clauses"]["E3"]["pass"]:
            diluted["E3"] = diluted.get("E3", 0) + 1
        if ind.distillation(A, th)[0] and not ind.distillation(A3, th)[0]:
            diluted["distillation"] = diluted.get("distillation", 0) + 1
    out.update(diluted)
    print(f"\npadding residual (mode {mode}, {trials} trials, seed {seed}): the round also Reads the extra objects")
    for c in ("E3", "distillation"):
        n = diluted.get(c, 0)
        tag = "RESIDUAL" if n else "unaffected"
        print(f"  {tag:<10} {c}: {n} of {trials} trials turn fail → pass by Reading more")
    if mode == "bounded" and diluted:
        print("  §7: a pair whose rounds Read more than they train on can dilute the bound. The log shows the\n"
              "  reads, not the training. Not a §2 violation; --mode absolute is the only mode this cannot move.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--mode", choices=list(ind.MODES), default="bounded")
    ap.add_argument("--trials", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=35)
    ap.add_argument("--json", type=Path, help="write results here")
    a = ap.parse_args()

    results: list = []
    prop: dict = {}
    cases_ok = run_cases(a.mode, results)
    prop_ok = property_check(a.mode, a.trials, a.seed, prop)
    pad: dict = {}
    padding_residual(a.mode, a.trials, a.seed, pad)
    if a.json:
        write_json(a.json, {"mode": a.mode, "cases": results, "cases_ok": cases_ok,
                            "monotonicity_violations": prop, "property_holds": prop_ok, "padding_residual": pad,
                            "trials": a.trials, "seed": a.seed})
    print(f"\ncases {'PASS' if cases_ok else 'FAIL'} · monotonicity {'HOLDS' if prop_ok else 'VIOLATED'}")
    sys.exit(0 if cases_ok and prop_ok else (1 if not cases_ok else 2))


if __name__ == "__main__":
    main()
