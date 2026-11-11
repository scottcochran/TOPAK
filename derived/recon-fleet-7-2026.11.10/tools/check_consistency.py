#!/usr/bin/env python3
"""Cross-file consistency checks for deployment recon-7.

Each check compares two files that state the same fact, or recomputes a fact one file derives. It
says nothing about whether a value is right, and it does not run the mechanism.

    uv run --with pyyaml tools/check_consistency.py      (from this directory's parent)

Needs `opa` on PATH, which it uses to read constants out of the Rego. Exits 1 if any check fails.
"""
import hashlib
import json
import math
import pathlib
import shutil
import subprocess
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
OPA = shutil.which("opa") or "/opt/homebrew/bin/opa"
failures = []
passed = 0


def check(name, ok, detail=""):
    global passed
    if ok:
        passed += 1
    else:
        failures.append(name)
        print(f"FAIL  {name}  {detail}")


def load(p):
    return yaml.safe_load((ROOT / p).read_text())


def jload(p):
    return json.loads((ROOT / p).read_text())


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def rego(bundle, ref):
    r = subprocess.run([OPA, "eval", "-f", "json", "-d", str(ROOT / bundle), ref], capture_output=True, text=True, check=True)
    return json.loads(r.stdout)["result"][0]["expressions"][0]["value"]


def bundle_rev(d):
    """mechanism/scripts/build-bundle.sh's revision."""
    d = ROOT / d
    names = sorted(("./" + p.relative_to(d).as_posix()).encode() for p in d.rglob("*")
                   if p.is_file() and ((p.suffix == ".rego" and not p.name.endswith("_test.rego")) or p.name == "data.json"))
    h = hashlib.sha256()
    for n in names:
        h.update(n + b"\0" + (d / n.decode()).read_bytes() + b"\0")
    return h.hexdigest()


root = load("3-planes/root.plane.yaml")
ib_c = load("3-planes/ib1.charter.yaml")
ap_c = load("3-planes/ap1.charter.yaml")
ib_p = load("3-planes/ib1.plane.yaml")
ap_p = load("3-planes/ap1.plane.yaml")
tally = load("3-planes/tally.msn-0001.yaml")
values = load("5-deployment/values.yaml")["declared"]
deploy = load("5-deployment/deployment.yaml")
dag = jload("2-workflows/staff-cycle.dag.json")
mesh = jload("2-workflows/recon-sectors.mesh.json")
mission = jload("4-mission/data.json")["topak"]
command = jload("1-bundles/command/data.json")["topak"]
plan = rego("4-mission", "data.topak.mission.plan")
roe = rego("4-mission", "data.topak.mission.roe")
cmd = rego("1-bundles/command", "data.topak.command")

REVS = {n: bundle_rev(d) for n, d in {"standing": "1-bundles/standing", "command": "1-bundles/command",
                                      "fleet": "1-bundles/fleet", "mission": "4-mission"}.items()}

# ---- digests pinned across files -----------------------------------------------------------------

for name, pinned in [("root", root["limits"]["bundles"]), ("ib1", ib_c["bundles"]), ("ap1", ap_c["bundles"])]:
    for b in pinned:
        check(f"{name} pins {b['name']}'s real revision", b["revision"] == REVS[b["name"]])
check("tally pins the fleet bundle", tally["artifacts"]["fleet_bundle"] == REVS["fleet"])
check("tally pins the mission bundle", tally["artifacts"]["mission_bundle"] == REVS["mission"])
check("tally pins the mesh", tally["artifacts"]["mesh"] == sha("2-workflows/recon-sectors.mesh.json"))
check("tally pins ap1's charter", tally["artifacts"]["ap1_charter"] == sha("3-planes/ap1.charter.yaml"))
check("tally pins ap1's seating", tally["artifacts"]["ap1_seating"] == sha("3-planes/ap1.plane.yaml"))
check("ib1 plane pins its charter", ib_p["charter"]["sha256"] == sha("3-planes/ib1.charter.yaml"))
check("ap1 plane pins its charter", ap_p["charter"]["sha256"] == sha("3-planes/ap1.charter.yaml"))
check("ap1 plane pins the mesh", ap_p["workflow"]["sha256"] == sha("2-workflows/recon-sectors.mesh.json"))
check("ib1 plane pins the DAG", ib_p["workflows"][0]["sha256"] == sha("2-workflows/staff-cycle.dag.json"))
check("ap1's task is the plan", ap_c["task"] == sha("4-mission/plan.rego"))
for n, node in mesh["nodes"].items():
    check(f"mesh node {n} names the mission bundle", node["bundle"] == REVS["mission"])
for n, node in dag["nodes"].items():
    check(f"DAG node {n} names the command bundle", node["bundle"] == REVS["command"])

# ---- every charter field is the parent's or narrower (ADR-0059 §1) --------------------------------

check("one floor", root["limits"]["floor"] == ib_c["floor"] == ap_c["floor"])


def prefix(a, b):
    return [x["revision"] for x in b[: len(a)]] == [x["revision"] for x in a]


check("ib1's bundles extend root's", prefix(root["limits"]["bundles"], ib_c["bundles"]))
check("ap1's bundles extend ib1's", prefix(ib_c["bundles"], ap_c["bundles"]))
check("ib1's entries within root's", set(ib_c["alphabet"]["entries"]) <= set(root["limits"]["alphabet"]["entries"]))
check("ap1's entries within ib1's", set(ap_c["alphabet"]["entries"]) <= set(ib_c["alphabet"]["entries"]))
check("ib1's actions within root's", set(ib_c["alphabet"]["actions"]) <= set(root["limits"]["alphabet"]["actions"]))
check("ap1's actions within ib1's", set(ap_c["alphabet"]["actions"]) <= set(ib_c["alphabet"]["actions"]))
check("ib1's labels within root's", set(ib_c["labels"]) <= set(root["limits"]["labels"]))
check("ap1's labels within ib1's", set(ap_c["labels"]) <= set(ib_c["labels"]))
check("ib1's budget within root's", ib_c["budget"] <= root["limits"]["budget"])
check("ap1's budget within ib1's", ap_c["budget"] <= ib_c["budget"])
check("no plane carries release", not (root["limits"]["release"] or ib_c["release"] or ap_c["release"]))
check("release roster empty", root["rules"]["release_roster"] == [])

TICK = ap_c["tick"]["period_ms"]
ap_ttl_ms = ap_c["ttlMax"]["reversible"] * TICK
check("ap1's ttlMax within ib1's", ap_ttl_ms <= ib_c["ttlMax"]["reversible"])
check("ib1's ttlMax within root's", ib_c["ttlMax"]["reversible"] <= root["limits"]["ttlMax"]["reversible"])
check("no ttl above T_persona", root["limits"]["ttlMax"]["reversible"] <= root["floor_values"]["T_persona_ms"])
check("ap1's expiry within ib1's", ap_c["expiry"]["ticks"] * TICK <= ib_c["expiry"]["after_seating"])
check("ib1's expiry within root's", ib_c["expiry"]["after_seating"] <= root["limits"]["expiry"]["after_genesis"])
for c, name in [(ib_c, "ib1"), (ap_c, "ap1")]:
    check(f"{name}: count at most K", c["countMax"]["reversible"] <= root["floor_values"]["K"])
    check(f"{name}: no irreversible allowance", c["countMax"]["irreversible"] == 0 and c["ttlMax"]["irreversible"] == 0)
check("K below R", root["floor_values"]["K"] < root["params"]["run_round_bound"])

# ---- the 24 hours ---------------------------------------------------------------------------------

E = ap_c["expiry"]["from_tick"] + ap_c["expiry"]["ticks"]
check("the expiry keeps every grant inside 24 h, and one tick later would not", (E + 1) * TICK == 86_400_000)
check("the expiry counts from tick zero ⟨Q13⟩", ap_c["expiry"]["from_tick"] == 0)
check("plan's expiry equals the charter's", plan["intent"]["expiry_tick"] == E and plan["intent"]["tick_ms"] == TICK)
check("command bundle's limit equals the charter's", cmd["max_expiry_tick"] == E)
check("command bundle's budget equals the charter's", cmd["max_budget"] == ap_c["budget"])

# ---- PBFT and the schedule (ADR-0061 §1) ----------------------------------------------------------


def cert(n, f):
    return math.floor((n + f) / 2) + 1


for c, name in [(ib_c, "ib1"), (ap_c, "ap1")]:
    r = c["replicas"]
    check(f"{name}: n = 3f + 1 or more", r["n"] >= 3 * r["f"] + 1)
    check(f"{name}: certificate size", r["certificate"] == cert(r["n"], r["f"]))
    check(f"{name}: member count", len(r["members"]) == r["n"])
m = ap_c["membership"]
check("seven replicas, one per vehicle", [x["id"] for x in ap_c["replicas"]["members"]] == [f"v{i}" for i in range(1, 8)])
check("schedule steps by one from n", m["schedule"][0] == ap_c["replicas"]["n"] and all(a - b == 1 for a, b in zip(m["schedule"], m["schedule"][1:])))
check("schedule stays at or above the capture floor", all((n - 1) // 3 >= m["capture_floor"] for n in m["schedule"]))
check("full membership holds the charter's budget", m["budgets"][7] == ap_c["budget"])
check("budgets fall with membership", all(m["budgets"][a] > m["budgets"][b] for a, b in zip(m["schedule"], m["schedule"][1:])))

# ---- K_up (ADR-0063 §3) ---------------------------------------------------------------------------

K = root["floor_values"]["K"]
check("K_up above K", ap_c["kUp"] > K)
check("K_up allows every vehicle a live and an unread lease", ap_c["kUp"] > 7 * 2 * K)

# ---- allowlist and ROE ----------------------------------------------------------------------------

tools = mission["tools"]
check("ap1's entries are the mission allowlist", set(ap_c["alphabet"]["entries"]) == set(tools))
check("ib1's entries cover the command allowlist", set(command["tools"]) <= set(ib_c["alphabet"]["entries"]))
inside = set(root["rules"]["inside_targets"])
by_name = {t["name"]: t for t in tools.values()}
for t in list(tools.values()) + [x for x in command["tools"].values() if x["domain"] == "run"]:
    e = t["effect"]
    check(f"{t['name']}: reversible", e["class"] == "reversible")
    check(f"{t['name']}: has an extent", e["extent"].get("kind") in {"act", "ticks", "distance", "region"})
    check(f"{t['name']}: declares while_unattended", e["while_unattended"] in {"permit", "refuse"})
    check(f"{t['name']}: finite T_irrev", e["t_irrev_ms"] > 0)
for t in tools.values():
    check(f"{t['name']}: target is inside the deployment", t["channel"]["target"] in inside)
check("SAR is the only ordered entry", {t["name"] for t in tools.values() if t["effect"]["permit"] == "ordered"} == {"sensor.sar_strip"})
check("one beacon", [t["name"] for t in tools.values() if t["effect"]["beacon"]] == ["comms.beacon"])
check("ROE transit extent matches the entry", roe["transit_extent_m"] == by_name["flight.transit"]["effect"]["extent"]["metres"])
check("ROE SAR extent matches the entry", roe["sar_extent_m"] == by_name["sensor.sar_strip"]["effect"]["extent"]["metres"])
check("SAR refused while unattended", by_name["sensor.sar_strip"]["effect"]["while_unattended"] == "refuse")
check("topics identical in bundle and mesh", {k: {x: v[x] for x in v if x != "hear"} for k, v in mesh["topics"].items()} == mission["topics"])
for name, t in mesh["topics"].items():
    check(f"{name}: label is in the vocabulary", t["label"] in mission["labels"]["vocabulary"])
    check(f"{name}: delivery table agrees", mission["labels"]["delivery"]["thinker"][t["label"]] == t["delivery"])

# ---- values.yaml against the files that hold each number ------------------------------------------

check("values: T_tick", values["time"]["T_tick_ms"] == TICK)
check("values: expiry", values["time"]["intent_expiry_tick"] == E)
check("values: lease ttl", values["time"]["lease_ttl_ticks"] == ap_c["ttlMax"]["reversible"])
check("values: drop", values["time"]["drop_silent_after_ticks"] == m["drop_silent_after_ticks"])
check("values: segment", values["time"]["watermark_segment_ticks"] == ib_p["watermark"]["segment_ticks"])
check("values: unattended", values["time"]["unattended_after_ticks"] == roe["ticks_unattended"])
check("values: grace", values["time"]["overdue_grace_ms"] == ap_p["runtime"]["watchdog"]["overdue_grace_ms"])
check("values: K", values["counts"]["K"] == K)
check("values: R", values["counts"]["run_round_bound_R"] == root["params"]["run_round_bound"])
check("values: K_up", values["counts"]["K_up"] == ap_c["kUp"])
check("values: sends", values["counts"]["sends_per_lease"] == roe["sends_per_lease"])
check("values: beacons", values["counts"]["beacons_per_lease"] == roe["beacons_per_lease"])
check("values: budgets", (values["budget"]["root"], values["budget"]["ib1"], values["budget"]["ap1"]) == (root["limits"]["budget"], ib_c["budget"], ap_c["budget"]))
check("values: membership budgets", values["budget"]["ap1_by_membership"] == m["budgets"])
for n, v in values["t_irrev_ms"].items():
    check(f"values: T_irrev of {n}", v == by_name[n]["effect"]["t_irrev_ms"])
check("segments are shorter than the unattended bound", ib_p["watermark"]["segment_ticks"] < roe["ticks_unattended"])
check("a replica is not dropped before a segment passes", m["drop_silent_after_ticks"] >= ib_p["watermark"]["segment_ticks"])
check("tick grace exceeds the placeholder round", ap_p["runtime"]["watchdog"]["overdue_grace_ms"] > ap_p["runtime"]["pbft"]["round_p99_ms_placeholder"])
check("tick period is long against a round", TICK >= 10 * ap_p["runtime"]["pbft"]["round_p99_ms_placeholder"])

# ---- the DAG --------------------------------------------------------------------------------------


def guard_atoms(g):
    if isinstance(g, str):
        return
    for k, v in g.items():
        if k in ("all", "any"):
            for x in v:
                yield from guard_atoms(x)
        elif k == "not":
            yield from guard_atoms(v)
        else:
            yield k, v


def check_workflow(wf, name):
    nodes, edges = wf["nodes"], wf["edges"]
    check(f"{name}: root is a node", wf["root"] in nodes)
    check(f"{name}: sinks are nodes", set(wf["sinks"]) <= set(nodes))
    for eid, e in edges.items():
        check(f"{name}: {eid} joins nodes", e["from"] in nodes and e["to"] in nodes)
        for k, a in guard_atoms(e["guard"]):
            if k == "outcome":
                check(f"{name}: {eid} guard names real outcomes", set(a["any_of"]) <= set(nodes[a["node"]]["outcomes"]))
            if k == "end":
                check(f"{name}: {eid} guard names end kinds", set(a["any_of"]) <= {"outcome", "expired", "fenced", "revoked"})
    seen, todo = set(), [wf["root"]]
    while todo:
        n = todo.pop()
        if n not in seen:
            seen.add(n)
            todo += [e["to"] for e in edges.values() if e["from"] == n]
    check(f"{name}: every node reachable", seen == set(nodes))
    check(f"{name}: a sink is reachable", bool(seen & set(wf["sinks"])))
    has_chosen = any(e["kind"] == "chosen" for e in edges.values())
    check(f"{name}: orchestrator iff a chosen edge", has_chosen == (wf.get("orchestrator") is not None))
    color = {}
    ok = True
    for e in edges.values():
        if e["delivery"] == "clear":
            ok = ok and nodes[e["from"]]["lineage"] != nodes[e["to"]]["lineage"]
    check(f"{name}: lineages alternate on clear edges", ok)


check_workflow(dag, "DAG")
check_workflow(mesh, "mesh")
check("DAG is declared dag", dag["kind"] == "dag")


def acyclic(wf):
    indeg = {n: 0 for n in wf["nodes"]}
    for e in wf["edges"].values():
        indeg[e["to"]] += 1
    q = [n for n, d in indeg.items() if d == 0]
    done = 0
    while q:
        n = q.pop()
        done += 1
        for e in wf["edges"].values():
            if e["from"] == n:
                indeg[e["to"]] -= 1
                if indeg[e["to"]] == 0:
                    q.append(e["to"])
    return done == len(wf["nodes"])


check("DAG is acyclic", acyclic(dag))
check("chosen edges equal command.rego's", {k for k, e in dag["edges"].items() if e["kind"] == "chosen"} == set(cmd["chosen_edges"]))
check("the orchestrator seat equals command.rego's", dag["orchestrator"]["seat"] == cmd["route_seat"])
check("the orchestrator is a person", dag["orchestrator"]["principal"].startswith("person:") and dag["orchestrator"]["lineage"] == "human")
seats = ib_p["rules"]["seats"]
check("orchestrator seat is held by a person", seats[cmd["route_seat"]]["actor"] == "person")
check("command.rego's operators exist", set(cmd["operator_seats"]) <= {s for s, d in seats.items() if d["kind"] == "operator"})
for n, node in dag["nodes"].items():
    check(f"DAG node {n}'s seat exists", node["seat"] in seats)
    check(f"DAG node {n}'s ttl within T_persona", node["ttl_ms"] <= root["floor_values"]["T_persona_ms"])
# A DAG guard reads only the source and nodes that dominate it. The graph is chain-shaped up to `plan`.
chain = ["reqs", "airspace", "readiness", "plan"]
for eid in ("e-go",):
    reads = {a["node"] for k, a in guard_atoms(dag["edges"][eid]["guard"])}
    check(f"{eid}'s guard reads only dominators", reads <= set(chain))

# ---- the mesh -------------------------------------------------------------------------------------

check("mesh is declared mesh", mesh["kind"] == "mesh")
check("mesh has no orchestrator", mesh["orchestrator"] is None)
check("mesh budget equals the charter's", mesh["budget"]["n"] == ap_c["budget"])
check("per-node budgets cover every node", set(mesh["budget"]["per_node"]) == set(mesh["nodes"]))
check("no clear edge at all (one stack lineage)", all(e["delivery"] == "handle" for e in mesh["edges"].values()))
ap_seats = ap_p["seats"]
for n, node in mesh["nodes"].items():
    check(f"mesh node {n}'s seat exists", node["seat"] in ap_seats)
    check(f"mesh node {n}: count at most K", node["lease"]["count"] <= K)
    check(f"mesh node {n}: ttl within charter", node["lease"]["ttl_ticks"] <= ap_c["ttlMax"]["reversible"])
    check(f"mesh node {n}: ttl_ms agrees with ticks", node["ttl_ms"] == node["lease"]["ttl_ticks"] * TICK)
    check(f"mesh node {n}: actions within charter", set(node["alphabet"]) <= set(ap_c["alphabet"]["actions"]))
    obs = node["observer"]
    check(f"mesh node {n}: Observer seat exists", obs["seat"] in ap_seats and ap_seats[obs["seat"]]["kind"] == "observer")
    check(f"mesh node {n}: Observer is on another vehicle", obs["host"] != ap_seats[node["seat"]]["vehicle"])
    check(f"mesh node {n}: Observer's host is its seat's", obs["host"] == ap_seats[obs["seat"]]["vehicle"])
    check(f"mesh node {n}: Observer differs in lineage", obs["lineage"] != node["lineage"])

# ---- the plan --------------------------------------------------------------------------------------

waves = plan["waves"]
vehicles = {f"v{i}" for i in range(1, 8)}
assigned = {v for w in waves.values() for v in w["assignments"]}
check("the plan flies the fleet", assigned | {plan["spare"]["vehicle"]} == vehicles)
check("each wave covers all three sectors", all(set(w["assignments"].values()) == set(plan["sectors"]) for w in waves.values()))
for name, w in waves.items():
    check(f"{name}: launch before station before recovery", w["launch"] < w["station_from"] < w["station_to"] < w["recover_by"])
    check(f"{name}: recovered before expiry", w["recover_by"] < E)
    hours = (w["recover_by"] - w["launch"]) * TICK / 3_600_000
    check(f"{name}: within endurance", hours <= deploy["fleet"]["endurance_hours"])
ordered = sorted(waves.values(), key=lambda w: w["launch"])
check("station coverage is continuous", all(a["station_to"] >= b["station_from"] for a, b in zip(ordered, ordered[1:])))
need = {}
for w in waves.values():
    for v in w["assignments"]:
        leases = math.ceil((w["recover_by"] - w["launch"]) / ap_c["ttlMax"]["reversible"]) + 1
        need[v] = need.get(v, 0) + leases
for v, n in need.items():
    check(f"{v}: per-node budget covers its sorties", mesh["budget"]["per_node"][v] >= n, f"{mesh['budget']['per_node'][v]} < {n}")
baseline = sum(need.values()) + 2 + 2 * 10   # the sorties, muster and close, and v7's two sorties
RELEASE_MARGIN = 3                            # ⟨Q15⟩ re-leases
check("the budget is the plan's baseline plus the re-lease margin", baseline + RELEASE_MARGIN == ap_c["budget"], f"{baseline} + {RELEASE_MARGIN} != {ap_c['budget']}")
turnarounds = sorted((w for w in waves.values() if "v1" in w["assignments"]), key=lambda w: w["launch"])
check("v1's turnaround is at least 4 hours", (turnarounds[1]["launch"] - turnarounds[0]["recover_by"]) * TICK >= 4 * 3_600_000)

# ---- geometry --------------------------------------------------------------------------------------


def in_poly(poly, e, n):
    inside_ = False
    for i, a in enumerate(poly):
        b = poly[(i + 1) % len(poly)]
        if (a[1] > n) != (b[1] > n) and e < (b[0] - a[0]) * (n - a[1]) / (b[1] - a[1]) + a[0]:
            inside_ = not inside_
    return inside_


def in_zone(z, e, n):
    if z["shape"] == "circle":
        return (e - z["centre"]["e"]) ** 2 + (n - z["centre"]["n"]) ** 2 < z["radius_m"] ** 2
    return in_poly(z["points"], e, n)


def leg_clear(a, b, zones, step=250):
    dist = math.hypot(b[0] - a[0], b[1] - a[1])
    k = max(1, int(dist / step))
    for i in range(k + 1):
        e, n = a[0] + (b[0] - a[0]) * i / k, a[1] + (b[1] - a[1]) * i / k
        if any(in_zone(z, e, n) for z in zones.values()):
            return False
    return True


ao = plan["operating_area"]
for name, poly in list(plan["sectors"].items()) + [("ingress", plan["ingress"])]:
    check(f"{name} lies inside the operating area", all(min(p[0] for p in ao) <= e <= max(p[0] for p in ao) and min(p[1] for p in ao) <= n <= max(p[1] for p in ao) for e, n in poly))
for name, poly in plan["sectors"].items():
    check(f"sector {name} overlaps the lanes", any(in_poly(plan["ingress"], e, n) for e, n in [(20500, poly[0][1] + 100), (21500, poly[0][1] + 100)]))
routes = ap_p["seating"]["recovery"]["routes"]["rtb-by-sector"]
nfz = plan["no_fly"]
for sector, wps in routes.items():
    pts = [(p["e"], p["n"]) for p in wps]
    check(f"route {sector} stays out of every no-fly zone past its gate", all(leg_clear(a, b, nfz) for a, b in zip(pts, pts[1:])))
    check(f"route {sector} ends at R1", pts[-1] == (0, 0))
    gate = pts[0]
    poly = plan["sectors"][sector]
    es = [p[0] for p in poly]
    ns = [p[1] for p in poly]
    bad = []
    for e in range(min(es), max(es) + 1, 500):
        for n in range(min(ns), max(ns) + 1, 500):
            if not any(in_zone(z, e, n) for z in nfz.values()) and not leg_clear((e, n), gate, nfz):
                bad.append((e, n))
    check(f"sector {sector}: every point reaches its gate clear of no-fly zones", not bad, f"{len(bad)} points, e.g. {bad[:3]}")
for alt in ap_p["seating"]["recovery"]["alternates"]:
    check(f"{alt['id']} is in the operating area and clear", in_poly(ao, alt["e"], alt["n"]) and not any(in_zone(z, alt["e"], alt["n"]) for z in nfz.values()))

# ---- deployment against planes ---------------------------------------------------------------------

site_hosts = {h for s in deploy["sites"].values() for h in s["hosts"]}
for m_ in ib_c["replicas"]["members"]:
    check(f"host for {m_['id']}", m_["id"] in site_hosts)
for m_ in ap_c["replicas"]["members"]:
    check(f"host for {m_['id']}", m_["id"] in site_hosts)
for m_ in root["replicas"]["members"]:
    check(f"host for {m_['id']}", m_["id"] in site_hosts)
for plane_name, chain in [("root", ["standing"]), ("ib1", ["standing", "command"]), ("ap1", ["standing", "command", "fleet", "mission"])]:
    check(f"{plane_name}: deployment's chain equals the charter's", deploy["mechanism"][plane_name]["bundle_engine"]["chain"] == chain)
served = {k for a in deploy["applications"].values() for k in a.get("serves", {})}
for t in list(tools.values()) + [x for x in command["tools"].values() if x["domain"] == "run"]:
    tg = t["channel"]["target"]
    if tg.endswith(".ib1.local:7443") or tg.endswith(".ib1.local:7444") or tg.endswith(".ib1.local:443"):
        check(f"{t['name']}'s target is served", tg in served)
for t in root["rules"]["inside_targets"]:
    if ".ib1.local" in t:
        check(f"inside target {t} is served", t in served)

print(f"{passed} passed, {len(failures)} failed")
sys.exit(1 if failures else 0)
