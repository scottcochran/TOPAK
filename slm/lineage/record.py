"""The lineage record of ADR-0035 §1, as data.

A record describes the artifact DAG under a Persona's weights. It is built in one of two ways,
which share this code:

- **projected** from the reference mechanism's log (`project.py`), which is the ADR's evidence.
  A round at rung 0 still makes the record *declared* (§2): at rung 0 the projection is
  attribution, not a bound.
- **declared** from an authored manifest (`../manifest.py`), for runs made outside the
  mechanism. That is the SLM session's shape, which the ADR keeps only as a cross-check.

Aggregates over the DAG (ingress, consumed, generators, curators, weight ancestry) are computed
here from the nodes and parents, never taken from the caller. That keeps §2's over-approximation
in one place: a record's ingress is the union of its own round's ingress and every parent's.

Two sets per record (ADR-0035 §1, R2):
  ingress    what the round COULD read: the corpus root in force, plus parents' ingress. Over-
             approximated. Enters only the numerators of E3 and the distillation rule.
  consumed   what the round DID read: the ingress objects `Read` into the workspace, plus
             authored drafts into the data directory, plus parents' consumed. Never over-
             approximated. It is the denominator, so charging a round with more root cannot
             lower any share the gate computes (§2's bound). A declared record's consumed set is
             its whole ingress: the author claims to have trained on what the manifest lists.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from common import sha256_json  # noqa: E402

SCHEMA = "topak.lineage/0"
STRENGTHS = ("projected", "declared")


def ingress_entry(digest: str, nbytes: int, declaration: dict | None, corpus: str | None = None) -> dict:
    """One content-addressed object a round could read, with its admission declaration.
    An object with no declaration is charged with no generator and no curator: the unlabeled
    model text residual of §7, stated rather than guessed."""
    d = declaration or {}
    return {
        "digest": digest,
        "bytes": int(nbytes),
        "corpus": corpus,
        "generators": sorted(d.get("generators", [])),
        "generated_share": float(d.get("generated_share", 0.0)),
        "curators": sorted(d.get("curators", [])),
        "declared": declaration is not None,
    }


def build(*, lineage: str, strength: str, rung: int, root: str, weights: str, tokenizer: str, family: str,
          trainer: dict, ingress: list[dict], parents: list[dict] = (), nodes: list[dict] = (),
          evidence: dict | None = None, consumed: list[str] | None = None) -> dict:
    """Assemble a record and its digest. `parents` are full parent records; their ingress,
    consumed set, weight ancestry and rung are folded in (weakest link, §2). `consumed` is the
    digests of the round's own ingress objects it actually read; None means all of them."""
    assert strength in STRENGTHS
    by_digest = {e["digest"]: e for p in parents for e in p["ingress"]}
    by_digest.update({e["digest"]: e for e in ingress})
    ing = sorted(by_digest.values(), key=lambda e: e["digest"])
    total = sum(e["bytes"] for e in ing) or 1

    own = {e["digest"] for e in ingress} if consumed is None else set(consumed) & {e["digest"] for e in ingress}
    cons = set(own)
    for p in parents:
        cons |= set(p.get("consumed", [e["digest"] for e in p["ingress"]]))
    consumed_bytes = sum(by_digest[d]["bytes"] for d in cons if d in by_digest)
    generated_bytes = round(sum(e["bytes"] * e["generated_share"] for e in ing))

    generated_by: dict[str, float] = {}
    for e in ing:
        for g in e["generators"]:
            generated_by[g] = generated_by.get(g, 0.0) + e["bytes"] * e["generated_share"] / total
    generated_share = sum(e["bytes"] * e["generated_share"] for e in ing) / total
    curated_by = sorted({c for e in ing for c in e["curators"]})

    ancestry = {weights}
    for p in parents:
        ancestry |= set(p["weight_ancestry"])
    weakest = min([rung] + [p["rung"] for p in parents])
    if weakest == 0 or any(p["strength"] == "declared" for p in parents):
        strength = "declared"

    rec = {
        "schema": SCHEMA,
        "lineage": lineage,
        "strength": strength,
        "rung": weakest,
        "root": root,
        "weights": weights,
        "weight_ancestry": sorted(ancestry),
        "parents": sorted(p["digest"] for p in parents),
        "ingress": ing,
        "ingress_bytes": sum(e["bytes"] for e in ing),
        "consumed": sorted(cons),
        "consumed_bytes": consumed_bytes,
        "generatedBy": {k: round(v, 6) for k, v in sorted(generated_by.items())},
        "generated_share": round(generated_share, 6),
        "generated_bytes": generated_bytes,
        "curatedBy": curated_by,
        "tokenizer": tokenizer,
        "family": family,
        "trainer": trainer,
        "nodes": list(nodes),
        "evidence": evidence or {},
    }
    rec["digest"] = sha256_json({k: v for k, v in rec.items() if k != "digest"})
    return rec


def ingress_set_digest(rec: dict) -> str:
    """Identity of a record's ingress set: what an overlap measurement must have covered."""
    return sha256_json(sorted(e["digest"] for e in rec["ingress"]))


def models_of(rec: dict) -> set[str]:
    """Names under which this lineage can appear as another lineage's generator: its label and
    every weights digest in its DAG."""
    return {rec["lineage"], *rec["weight_ancestry"], *(f"topak-weights:{w}" for w in rec["weight_ancestry"])}
