#!/usr/bin/env python3
"""Generate TopakFloor/Genesis.lean and TopakFloor/Tests.lean from the floor's own files.

  Genesis.lean  genesis.cedarschema -> Schema, genesis-floor.cedar -> Policies, in cedar-spec's abstract syntax
  Tests.lean    genesis-tests.json  -> one Request/Entities per case and one theorem that the model's
                                       isAuthorized returns the case's decision and reasons

The Cedar text is parsed by the cedar CLI (`translate-policy`, `translate-schema`), whose JSON this script walks.
What this script trusts: that CLI's parse and its own walk. The output puts each policy's Cedar id on its Lean
term, and the digests of the three sources in the header.  usage: python3 gen.py   (from floor/lean/)
"""
import hashlib, json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
FLOOR_DIR = os.path.dirname(HERE)
FLOOR = os.path.join(FLOOR_DIR, "genesis-floor.cedar")
SCHEMA = os.path.join(FLOOR_DIR, "genesis.cedarschema")
TESTS = os.path.join(FLOOR_DIR, "genesis-tests.json")

def d16(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()[:16]

def cedar(*args):
    r = subprocess.run(["cedar", *args], capture_output=True, text=True, check=True)
    return json.loads(r.stdout)

def ls(s):
    return json.dumps(s)  # Lean string literal syntax matches JSON for these identifiers

# ---- names -------------------------------------------------------------------------------------------
NS = ["Topak"]  # the schema's one namespace; bare names in its JSON are relative to it

def qual(name):
    return name if "::" in name else "::".join(NS + [name])

def ety(name):
    parts = qual(name).split("::")
    return f'(ety [{", ".join(ls(p) for p in parts[:-1])}] {ls(parts[-1])})'

def uid(d):
    parts = d["type"].split("::")
    if d["type"] == "Topak::Action":
        return f'(act {ls(d["id"])})'
    return f'(uid [{", ".join(ls(p) for p in parts[:-1])}] {ls(parts[-1])} {ls(d["id"])})'

def uid_str(s):  # 'Topak::Seat::"a1"'
    ty, _, eid = s.rpartition("::")
    return uid({"type": ty, "id": json.loads(eid)})

# ---- expressions (EST) ---------------------------------------------------------------------------------
def expr(e):
    assert len(e) == 1, e
    (k, v), = e.items()
    if k == "Value":
        return value_lit(v)
    if k == "Var":
        return f"(.var .{v})"
    if k == "&&":
        return f"(.and {expr(v['left'])} {expr(v['right'])})"
    if k == "||":
        return f"(.or {expr(v['left'])} {expr(v['right'])})"
    if k == "!":
        return f"(.unaryApp .not {expr(v['arg'])})"
    if k == "==":
        return f"(.binaryApp .eq {expr(v['left'])} {expr(v['right'])})"
    if k == "!=":
        return f"(.unaryApp .not (.binaryApp .eq {expr(v['left'])} {expr(v['right'])}))"
    if k == "in":
        return f"(.binaryApp .mem {expr(v['left'])} {expr(v['right'])})"
    if k == "contains":
        return f"(.binaryApp .contains {expr(v['left'])} {expr(v['right'])})"
    if k == ".":
        return f"(.getAttr {expr(v['left'])} {ls(v['attr'])})"
    if k == "has":
        return f"(.hasAttr {expr(v['left'])} {ls(v['attr'])})"
    if k == "Set":
        return f"(.set [{', '.join(expr(x) for x in v)}])"
    raise SystemExit(f"unsupported EST node {k}")

def value_lit(v):
    if isinstance(v, bool):
        return f"(.lit (.bool {'true' if v else 'false'}))"
    if isinstance(v, int):
        return f"(.lit (.int (Int64.ofInt {v})))"
    if isinstance(v, str):
        return f"(.lit (.string {ls(v)}))"
    if isinstance(v, dict) and "__entity" in v:
        return f"(.lit (.entityUID {uid(v['__entity'])}))"
    raise SystemExit(f"unsupported literal {v!r}")

def scope(kind, s):
    op = s["op"]
    if op == "All":
        inner = ".any"
    elif op == "==":
        inner = f"(.eq {uid(s['entity'])})"
    elif op == "in" and "entity" in s:
        inner = f"(.mem {uid(s['entity'])})"
    elif op == "in" and "entities" in s and kind == "action":
        return f"(.actionInAny [{', '.join(uid(x) for x in s['entities'])}])"
    elif op == "is":
        inner = f"(.is {ety(s['entity_type'])})"
    else:
        raise SystemExit(f"unsupported scope {s}")
    return f"(.{kind}Scope {inner})"

def policy(pid, p):
    conds = ", ".join(f"{{ kind := .{c['kind']}, body := {expr(c['body'])} }}" for c in p["conditions"])
    return (f"  {{ id := {ls(pid)}, effect := .{p['effect']},\n"
            f"    principalScope := {scope('principal', p['principal'])},\n"
            f"    actionScope := {scope('action', p['action'])},\n"
            f"    resourceScope := {scope('resource', p['resource'])},\n"
            f"    condition := [{conds}] }}")

# ---- schema -----------------------------------------------------------------------------------------
PRIMS = {"String": ".string", "Long": ".int", "Bool": "(.bool .anyBool)", "Boolean": "(.bool .anyBool)"}

def cedar_type(t, common, ns, ets=()):
    ty = t["type"]
    if ty == "EntityOrCommon":
        name = t["name"]
        base = name[len(ns) + 2:] if name.startswith(ns + "::") else name
        if base in PRIMS and base not in common and base not in ets:
            return PRIMS[base]
        if base in common:
            return cedar_type(common[base], common, ns, ets)
        if base in ets:
            return f"(.entity {ety(ns + '::' + base)})"
        raise SystemExit(f"unresolved EntityOrCommon {name}")
    if ty == "String": return ".string"
    if ty == "Long": return ".int"
    if ty in ("Bool", "Boolean"): return "(.bool .anyBool)"
    if ty == "Entity": return f"(.entity {ety(t['name'])})"
    if ty == "Set": return f"(.set {cedar_type(t['element'], common, ns, ets)})"
    if ty == "Record": return f"(.record {record_type(t['attributes'], common, ns, ets)})"
    base = ty[len(ns) + 2:] if ty.startswith(ns + "::") else ty
    if base in common:
        return cedar_type(common[base], common, ns, ets)
    raise SystemExit(f"unsupported schema type {t}")

def record_type(attrs, common, ns, ets=()):
    items = []
    for a, t in attrs.items():
        q = ".required" if t.get("required", True) else ".optional"
        items.append(f"({ls(a)}, {q} {cedar_type(t, common, ns, ets)})")
    return f"(Map.make [{', '.join(items)}])"

def schema_term(sj):
    (ns, body), = sj.items()
    assert ns == "::".join(NS), ns
    common = body.get("commonTypes", {})
    etnames = tuple(body["entityTypes"].keys())
    ets = []
    for name, e in body["entityTypes"].items():
        anc = ", ".join(ety(a) for a in e.get("memberOfTypes", []))
        attrs = record_type(e["shape"]["attributes"], common, ns, etnames) if "shape" in e else "(Map.make [])"
        ets.append(f"  ({ety(ns + '::' + name)},\n   .standard {{ ancestors := Set.make [{anc}], attrs := {attrs}, tags := none }})")
    acts = []
    for name, a in body["actions"].items():
        ap = a["appliesTo"]
        ctx = ap.get("context", {"type": "Record", "attributes": {}})
        ctx_t = cedar_type(ctx, common, ns, etnames)
        assert ctx_t.startswith("(.record "), ctx_t
        ctx_map = ctx_t[len("(.record "):-1]
        acts.append(f"  ({uid({'type': ns + '::Action', 'id': name})},\n"
                    f"   {{ appliesToPrincipal := Set.make [{', '.join(ety(x) for x in ap['principalTypes'])}],\n"
                    f"     appliesToResource := Set.make [{', '.join(ety(x) for x in ap['resourceTypes'])}],\n"
                    f"     ancestors := Set.make [], context := {ctx_map} }})")
    return ("def genesisSchema : Schema :=\n  { ets := Map.make [\n" + ",\n".join(ets) +
            "],\n    acts := Map.make [\n" + ",\n".join(acts) + "] }\n")

# ---- values (tests) ------------------------------------------------------------------------------------
def value(v):
    if isinstance(v, bool): return f"(.prim (.bool {'true' if v else 'false'}))"
    if isinstance(v, int): return f"(long {v})"
    if isinstance(v, str): return f"(.prim (.string {ls(v)}))"
    if isinstance(v, list): return f"(.set (Set.make [{', '.join(value(x) for x in v)}]))"
    if isinstance(v, dict) and "__entity" in v: return f"(.prim (.entityUID {uid(v['__entity'])}))"
    if isinstance(v, dict):
        return f"(.record (Map.make [{', '.join(f'({ls(k)}, {value(x)})' for k, x in v.items())}]))"
    raise SystemExit(f"unsupported value {v!r}")

def entities_term(es, action_names=()):
    rows = []
    # The Rust engine adds the schema's action entities to every store it loads with a schema; the Lean model's
    # entity validator expects them to be present, so they are written out here, with no attributes or parents.
    for a in action_names:
        rows.append(f"    ((act {ls(a)}),\n     {{ attrs := Map.empty, ancestors := Set.make [], tags := Map.empty }})")
    for e in es:
        attrs = ", ".join(f"({ls(k)}, {value(x)})" for k, x in e["attrs"].items())
        parents = ", ".join(uid(p) for p in e.get("parents", []))
        rows.append(f"    ({uid(e['uid'])},\n     {{ attrs := Map.make [{attrs}], ancestors := Set.make [{parents}], tags := Map.empty }})")
    return "Map.make [\n" + ",\n".join(rows) + "]"

def request_term(r):
    ctx = ", ".join(f"({ls(k)}, {value(x)})" for k, x in r["context"].items())
    return (f"{{ principal := {uid_str(r['principal'])}, action := {uid_str(r['action'])},\n"
            f"    resource := {uid_str(r['resource'])},\n    context := Map.make [{ctx}] }}")

def main():
    cedar_version = subprocess.run(["cedar", "--version"], capture_output=True, text=True).stdout.strip()
    floor = cedar("translate-policy", "--direction", "cedar-to-json", "-p", FLOOR)
    schema = cedar("translate-schema", "--direction", "cedar-to-json-with-resolved-types", "-s", SCHEMA)
    tests = json.load(open(TESTS))
    action_names = list(next(iter(schema.values()))["actions"].keys())
    hdr = (f"-- GENERATED by gen.py from genesis-floor.cedar (sha256 {d16(FLOOR)}), genesis.cedarschema (sha256 {d16(SCHEMA)})\n"
           f"-- and genesis-tests.json (sha256 {d16(TESTS)}), parsed by {cedar_version}. Do not edit; regenerate.\n")
    pols = floor["staticPolicies"]
    assert not floor.get("templates") and not floor.get("templateLinks")
    policies = []
    for key, p in pols.items():
        pid = p.get("annotations", {}).get("id", key)
        policies.append(policy(pid, p))
    with open(os.path.join(HERE, "TopakFloor", "Genesis.lean"), "w") as f:
        f.write(hdr)
        f.write("import TopakFloor.Basic\n/-! The genesis floor and schema S in cedar-spec's abstract syntax. -/\n")
        f.write("namespace TopakFloor\nopen Cedar.Spec Cedar.Validation Cedar.Data\n\n")
        f.write("/-- `genesis.cedarschema`: schema S (ADR-0030 §4). -/\n")
        f.write(schema_term(schema))
        f.write("\n/-- `genesis-floor.cedar`: the 17 policies, in file order, each under its `@id`. -/\n")
        f.write("def genesisFloor : Policies := [\n" + ",\n".join(policies) + "]\n\n")
        f.write("/-- The policy ids, in file order. -/\ndef genesisIds : List PolicyID := genesisFloor.map Policy.id\n\n")
        f.write("end TopakFloor\n")
    # tests
    ents = [json.dumps(c["entities"], sort_keys=True) for c in tests]
    shared = len(set(ents)) == 1
    with open(os.path.join(HERE, "TopakFloor", "Tests.lean"), "w") as f:
        f.write(hdr)
        f.write("import TopakFloor.Genesis\n/-! `genesis-tests.json` under the model's `isAuthorized`: each case's request, and a theorem that the\n"
                "verified authorizer returns the case's decision with the case's determining policies and no errors. -/\n")
        f.write("namespace TopakFloor\nopen Cedar.Spec Cedar.Validation Cedar.Data\n\n")
        if shared:
            f.write("/-- The entity store every case shares (`gen-tests.py` ENTITIES), with the schema's action entities. -/\n")
            f.write(f"def genesisEntities : Entities :=\n  {entities_term(tests[0]['entities'], action_names)}\n\n")
        names = []
        for i, c in enumerate(tests, 1):
            n = f"case{i:02d}"
            names.append(n)
            f.write(f"/-- {c['name']} -/\n")
            f.write(f"def {n}_request : Request :=\n  {request_term(c['request'])}\n")
            if not shared:
                f.write(f"def {n}_entities : Entities :=\n  {entities_term(c['entities'], action_names)}\n")
            e = "genesisEntities" if shared else f"{n}_entities"
            reasons = ", ".join(ls(r) for r in c["reason"])
            assert c["num_errors"] == 0
            f.write(f"theorem {n} : isAuthorized {n}_request {e} genesisFloor =\n"
                    f"    {{ decision := .{c['decision']}, determiningPolicies := Set.make [{reasons}], erroringPolicies := Set.make [] }} := by\n"
                    f"  native_decide\n\n")
        f.write("/-- The requests of every case, for the witnesses. -/\n")
        f.write("def caseRequests : List Request := [" + ", ".join(f"{n}_request" for n in names) + "]\n\n")
        f.write("end TopakFloor\n")
    print(f"wrote Genesis.lean ({len(policies)} policies) and Tests.lean ({len(tests)} cases, shared entities={shared})")

if __name__ == "__main__":
    main()
