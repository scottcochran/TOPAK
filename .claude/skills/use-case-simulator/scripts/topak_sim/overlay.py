"""An autonomous plane of the command-chain overlay (ADR-0059 to ADR-0068, all Proposed and unbuilt).

Nothing in this file is the reference: the governor, PBFT, the watermark and the federation floor stage
do not exist. It is the overlay's rules written as a model, with each check naming the entry of ADR-0067
§3 it stands in for. The workflow it drives and the policies it consults are real.

A plane owns bodies. A body is whatever a governor sits on: a vehicle, a robot, a disconnected host. A
world supplies what a body does, through these hooks:

    body_of(node_def)                        the body a workflow node's rounds run on
    seat_of(body)                            the body's stack's seat
    body_state(body)                         the world's own fields of a body
    plane_state(pid)                         the world's own fields of a plane
    principal(plane, body)                   input.principal for the body's stack
    facts(plane, body, t)                    input.facts, what the governor lifts for itself
    context_extra(plane, body, t)            extra input.context
    parent_context(plane)                    input.context at the parent plane
    body_active(body)                        whether the body is out working: beacons and holds apply
    start_entry(plane, body, t, name, inputs)   a permitted allowlist entry takes effect
    stop_entries(plane, body)                the body's running entries end, because its lease has
    expire_entries(plane, t)                 extents that end at this tick
    stack(plane, body, t)                    the Byzantine half: what the stack asks for
    physics(plane, t)                        the world moves
    measures(plane, t)                       what the mission delivered
    begin_terminal(plane, body, t, why)      the body's declared behaviour with no lease
    on_destroyed(plane, body, t)             a body is lost
    on_edge_fired(plane, fired, t)           an edge fired
    inject(ev, t)                            an environment event the kernel does not know
    invariants_extra(plane, t)               the world's own invariants
"""
import copy
import hashlib
import math

from . import lift
from .core import Core
from .trace import canonical
from .workflow import status_of


def body_defaults():
    return {"alive": True, "mode": "idle", "hears": True, "alone": False, "silent_until": -1, "lease": None, "clear_set": [], "last_watermark": 0, "sends": 0, "beacons": 0,
            "own_unwatermarked": 0, "chain_head": "0" * 16, "chain_len": 0, "terminal": None, "wait_until": None, "lease_idx": 0, "revoked": False}


class AutonomousPlane:
    def __init__(self, w, pid, parent, charter, seating, parent_seating, wf, tools, floor_K, bodies):
        self.w, self.pid, self.parent, self.charter, self.seating, self.parent_seating, self.wf = w, pid, parent, charter, seating, parent_seating, wf
        self.bodies = list(bodies)
        self.by_name = {t["name"]: t for t in tools.values()}
        self.topics = wf.defn.get("topics", {})
        self.K, self.K_UP = floor_K, charter["kUp"]
        self.T_EXP = charter["expiry"]["from_tick"] + charter["expiry"]["ticks"]
        self.chain = w.chains[pid]
        self.sent_tick = {}
        self.link_restore = None
        self.real_floor = w.dep.get("floor") == "cedar"
        self.path = f"planes/{pid}"

    @staticmethod
    def state(charter, extra=None):
        return {"index": 0, "epoch": 1, "seated": False, "membership": [m["id"] for m in charter["replicas"]["members"]], "certificate": charter["replicas"]["certificate"],
                "budget_cap": charter["budget"], "budget_spent": 0, "per_node_spent": {}, "outstanding": 0, "intent_live": False, "last_tick_ordered": None, "silent_since": {},
                "grants_blocked_ku": 0, **(extra or {})}

    @staticmethod
    def parent_state(extra=None):
        return {"index": 0, "epoch": 1, "budget_spent": 0, "seated": False, "link_up": True, "watermarks": 0, "revocations": {}, **(extra or {})}

    # ---- reading state ----------------------------------------------------------------------------

    @property
    def P(self):
        return self.w.s["planes"][self.pid]

    @property
    def up(self):
        return self.w.s["planes"][self.parent]

    def B(self, b):
        return self.w.s["bodies"][b]

    def radio_ok(self, b):
        V = self.B(b)
        return V["alive"] and self.w.s["tick"] > V["silent_until"]

    def members_signing(self):
        return [b for b in self.P["membership"] if self.radio_ok(b)]

    # ---- the charter is applied --------------------------------------------------------------------

    def apply_charter(self):
        w = self.w
        w.set(f"{self.path}/seated", True)
        w.set(f"{self.path}/intent_live", True)
        w.emit("charter_applied", plane=self.pid, expiry_tick=self.T_EXP, kUp=self.K_UP, note="tick zero: the intent's time starts here")

    # ---- environment ------------------------------------------------------------------------------

    def inject(self, ev, t):
        """The faults every autonomous plane can suffer. Returns False for one this plane does not know."""
        w, k = self.w, ev["kind"]
        if k == "silence":
            w.set(f"bodies/{ev['body']}/silent_until", t + ev["ticks"] - 1)
            w.emit("inject", what="silence", body=ev["body"], ticks=ev["ticks"], why=ev["why"])
        elif k == "link_cut":
            self.link_restore = t + ev["ticks"]
            w.set(f"planes/{self.parent}/link_up", False)
            w.emit("inject", what="link_cut", ticks=ev["ticks"], why=ev["why"], restores_at=self.link_restore)
        elif k == "revoke":
            b = ev["body"]
            op = {"seat": ev["by"], "kind": "operator", "actor": "person"}
            w.admit(f"plane:{self.parent}", w.chains[self.parent], {"action": "Revoke", "principal": op, "resource": {"seat": w.seat_of(b)}, "context": w.parent_context(self)}, f"revoke {b}", why=ev["why"])
            w.inc(f"planes/{self.parent}/index")
            w.set(f"planes/{self.parent}/revocations/{b}", {"ordered_at": t, "delivered_at": None, "effects_since_order": 0})
            w.emit("revocation_ordered", body=b, link_up=self.up["link_up"])
        elif k == "destroy":
            b = ev["body"]
            w.set(f"bodies/{b}/alive", False)
            w.set(f"bodies/{b}/mode", "destroyed")
            w.on_destroyed(self, b, t)
            lease = self.B(b)["lease"]
            if lease:
                w.set(f"bodies/{b}/lease", None)
                w.set(f"leases/{lease['id']}/status", "lost")
                w.set(f"leases/{lease['id']}/ended_tick", t)
                self.wf.end(lease["act"], end="expired")
            w.emit("inject", what="destroyed", body=b, why=ev["why"], record="the body's chain is gone and can never be sealed")
        else:
            return False
        return True

    def tick_environment(self, t):
        if self.link_restore == t:
            self.w.set(f"planes/{self.parent}/link_up", True)
            self.w.emit("inject", what="link_restored")

    def silence_on_lease_end(self, b, t):
        for i, ev in enumerate(self.w.sc.get("environment", [])):
            if ev["kind"] == "silence_on_lease_end" and ev["watch"] == b and t >= ev["after_tick"] and i not in self.w.fired_triggers:
                self.w.fired_triggers.add(i)
                self.w.set(f"bodies/{ev['body']}/silent_until", t + ev["ticks"] - 1)
                self.w.emit("inject", what="silence", body=ev["body"], ticks=ev["ticks"], why=ev["why"])

    # ---- hearing the plane -------------------------------------------------------------------------

    def hearing(self, t, ordered):
        w = self.w
        for b in self.bodies:
            V = self.B(b)
            if not V["alive"]:
                continue
            w.tick_body(self, b, t)
            hears = ordered and self.radio_ok(b)
            if V["hears"] and not hears:
                w.set(f"bodies/{b}/hears", False)
                w.set(f"bodies/{b}/alone", True)
                self.go_alone(b, t)
            elif not V["hears"] and hears:
                w.set(f"bodies/{b}/hears", True)
                w.set(f"bodies/{b}/alone", False)
                self.back(b, t)

    def go_alone(self, b, t):
        lease = self.B(b)["lease"]
        if lease:
            self.end_lease(b, t, "expired", "the next tick is overdue: the body is alone")
            # An ending grants nothing: no successor wait, because it no longer hears any plane.
            self.w.begin_terminal(self, b, t, "alone")
        self.w.emit("alone", body=b, had_lease=bool(lease))

    def back(self, b, t):
        pending = [lid for lid, L in self.w.s["leases"].items() if L["body"] == b and L["status"] == "ended" and not L["sealed"]]
        for lid in pending:
            self.seal(lid, t, "handed up after the body heard its plane again")
        self.w.emit("heard_again", body=b, sealed=pending)

    # ---- leases -------------------------------------------------------------------------------------

    def end_lease(self, b, t, end, why, outcome=None):
        w = self.w
        V = self.B(b)
        lease = V["lease"]
        lid, act = lease["id"], lease["act"]
        w.set(f"bodies/{b}/lease", None)
        w.stop_entries(self, b)
        w.set(f"leases/{lid}/status", "ended")
        w.set(f"leases/{lid}/ended_tick", t)
        w.set(f"leases/{lid}/end", end)
        w.set(f"leases/{lid}/used", lease["used"])
        self.wf.end(act, end=end if end in ("outcome", "expired", "fenced", "revoked") else "expired", outcome=outcome, label=V["clear_set"], actuates=lease["used"])
        w.emit("lease_end", body=b, lease=lid, end=end, used=lease["used"], why=why)
        self.silence_on_lease_end(b, t)
        if V["hears"] and V["alive"]:
            self.seal(lid, t, "the governor closes the chain and the plane orders it")

    def seal(self, lid, t, why):
        w = self.w
        w.set(f"leases/{lid}/sealed", True)
        w.set(f"leases/{lid}/sealed_tick", t)
        w.inc(f"{self.path}/index")
        w.emit("seal", lease=lid, why=why)

    def observers_read(self, t):
        """Coupling (ADR-0062 §8; ADR-0054 §7): an Observer reads a sealed record if its host can be reached."""
        w, wf = self.w, self.wf
        for i, A in enumerate(wf.run["acts"]):
            if status_of(A["status"]) != "ended" or A["covered"]:
                continue
            lid = w.lease_of_act.get((self.pid, i))
            if lid is None or not w.s["leases"][lid]["sealed"]:
                continue
            obs = wf.defn["nodes"][A["node"]]["observer"]
            if self.radio_ok(obs["host"]):
                r = wf.cover(i)
                w.emit("covered", act=i, node=A["node"], observer=obs["seat"], host=obs["host"])
                for f in r.get("fired", []):
                    if "blocked" not in f:
                        w.on_edge_fired(self, f, t)
                w.emit("edges", act=i, node=A["node"], fired=r.get("fired", []))
                if wf.status() != "running":
                    w.emit("workflow_ended", workflow=wf.name, status=wf.run["status"], tick=t)

    def grant_ready(self, t):
        w, wf, ap = self.w, self.wf, self.P
        if wf.status() != "running":
            return
        for i in wf.ready():
            A = wf.act(i)
            node = A["node"]
            nd = wf.defn["nodes"][node]
            b = w.body_of(nd)
            V = self.B(b)
            if wf.running_node(node):
                continue
            if V["lease"] or not V["alive"] or not V["hears"]:
                continue
            if V["revoked"]:
                wf.fail(i, "the body's authority was revoked")
                w.emit("grant_refused", act=i, node=node, body=b, why="the body's authority was revoked")
                continue
            count, ttl = nd["lease"]["count"], nd["lease"]["ttl_ticks"]
            # The plane's cap, which shrinks with its membership (ADR-0061). A grant it cannot pay fails the workflow.
            spent, cap = ap["budget_spent"], ap["budget_cap"]
            if spent >= cap:
                w.emit("workflow_failed", why="the plane's budget refused a grant", act=i, node=node, spent=spent, cap=cap)
                wf.fence()
                return
            # ADR-0063 §3: the strict form.
            if ap["outstanding"] + count >= self.K_UP:
                w.inc(f"{self.path}/grants_blocked_ku")
                if ap["grants_blocked_ku"] % 50 == 1:
                    w.emit("grant_blocked", act=i, node=node, outstanding=ap["outstanding"], count=count, kUp=self.K_UP, rule="FD10-outstanding-bound")
                continue
            if t >= self.T_EXP or not ap["intent_live"]:
                continue
            if V["own_unwatermarked"] + count >= self.K_UP:
                w.emit("grant_refused", act=i, node=node, why="the governor's own account is at K_up", rule="FD10-outstanding-bound")
                continue
            signers = self.members_signing()
            if len(signers) < ap["certificate"]:
                continue
            r = wf.grant(i, fence=w.s["next_lease"])
            if "refused" in r:
                w.emit("workflow_failed", why=r["refused"], act=i, node=node)
                return
            lid = f"L{w.s['next_lease']}"
            w.set("next_lease", w.s["next_lease"] + 1)
            ttl_end = min(t + ttl, self.T_EXP)
            lease = {"id": lid, "act": i, "node": node, "body": b, "seat": nd["seat"], "count": count, "used": 0, "ttl_ticks": ttl, "granted": t, "ttl_end": ttl_end}
            w.set(f"leases/{lid}", {"body": b, "node": node, "act": i, "plane": self.pid, "count": count, "granted": t, "ttl_end": ttl_end, "status": "live", "sealed": False, "watermarked": False,
                                    "charge": count, "certificate": len(signers), "fences": {p: w.s["planes"][p]["epoch"] for p in w.s["planes"]}})
            w.lease_of_act[(self.pid, i)] = lid
            w.set(f"bodies/{b}/lease", lease)
            w.set(f"bodies/{b}/sends", 0)
            w.set(f"bodies/{b}/beacons", 0)
            w.set(f"bodies/{b}/clear_set", [])
            w.reset_for_lease(self, b)
            w.inc(f"bodies/{b}/lease_idx")
            w.inc(f"bodies/{b}/own_unwatermarked", count)
            w.set(f"bodies/{b}/wait_until", None)
            w.resume_from_terminal(self, b)
            w.inc(f"{self.path}/outstanding", count)
            w.inc(f"{self.path}/budget_spent")
            w.set(f"{self.path}/per_node_spent/{node}", ap["per_node_spent"].get(node, 0) + 1)
            w.inc(f"{self.path}/index")
            w.emit("lease_grant", body=b, lease=lid, act=i, node=node, via=A["via"], count=count, ttl_end=ttl_end, certificate=len(signers), outstanding=ap["outstanding"])

    def watermark(self, t):
        w, up = self.w, self.up
        if not up["link_up"]:
            return
        for b, rev in list(up["revocations"].items()):
            if rev["delivered_at"] is None:
                self.deliver_revocation(b, t)
        if t % self.parent_seating["watermark"]["segment_ticks"] != 0:
            return
        covered = [lid for lid, L in w.s["leases"].items() if L["plane"] == self.pid and L["sealed"] and not L["watermarked"]]
        for lid in covered:
            L = w.s["leases"][lid]
            w.set(f"leases/{lid}/watermarked", True)
            w.inc(f"{self.path}/outstanding", -L["charge"])
            w.inc(f"bodies/{L['body']}/own_unwatermarked", -L["charge"])
        w.inc(f"planes/{self.parent}/watermarks")
        w.inc(f"planes/{self.parent}/index")
        for b in self.bodies:
            if self.B(b)["alive"] and self.B(b)["hears"]:
                w.set(f"bodies/{b}/last_watermark", t)
        if covered:
            w.emit("watermark", covers=covered, released=sum(w.s["leases"][x]["charge"] for x in covered), outstanding=self.P["outstanding"], fences=[self.parent])

    def deliver_revocation(self, b, t):
        w, up = self.w, self.up
        w.set(f"planes/{self.parent}/revocations/{b}/delivered_at", t)
        w.set(f"bodies/{b}/revoked", True)
        w.inc(f"{self.path}/index")
        rev = up["revocations"][b]
        lease = self.B(b)["lease"]
        w.emit("revocation_delivered", body=b, ordered_at=rev["ordered_at"], delay_ticks=t - rev["ordered_at"], effects_since_order=rev["effects_since_order"], live_lease=bool(lease))
        if lease:
            self.end_lease(b, t, "revoked", "the revocation arrived")
            w.begin_terminal(self, b, t, "revoked")

    def membership_step(self, t):
        w, ap = self.w, self.P
        ms = self.charter["membership"]
        for b in list(ap["membership"]):
            silent = not self.radio_ok(b)
            since = ap["silent_since"].get(b)
            if silent and since is None:
                w.set(f"{self.path}/silent_since/{b}", t)
            elif not silent and since is not None:
                w.delete(f"{self.path}/silent_since/{b}")
            if silent and since is not None and t - since >= ms["drop_silent_after_ticks"]:
                n = len(ap["membership"]) - 1
                if n not in ms["schedule"]:
                    continue
                f = (n - 1) // 3
                cert = math.floor((n + f) / 2) + 1
                w.set(f"{self.path}/membership", [x for x in ap["membership"] if x != b])
                w.set(f"{self.path}/certificate", cert)
                w.set(f"{self.path}/budget_cap", ms["budgets"][n])
                w.delete(f"{self.path}/silent_since/{b}")
                w.inc(f"{self.path}/index")
                w.emit("membership_step", dropped=b, members=n, certificate=cert, budget_cap=ms["budgets"][n], rule="FD13-step-in-schedule")

    # ---- the governor ---------------------------------------------------------------------------------

    def context(self, b, t, permitted_by="governor"):
        V, ap = self.B(b), self.P
        sent = self.sent_tick.get(b, {})
        return {"plane": self.pid, "planeKind": "autonomous", "tick": t, "permittedBy": permitted_by, "hearsPlane": V["hears"], "ticksSinceWatermark": t - V["last_watermark"], "clearSet": list(V["clear_set"]),
                "sendsThisTick": {k: sent.get(k, 0) for k in self.topics}, "sendsThisLease": V["sends"], "beaconsThisLease": V["beacons"], "outstanding": ap["outstanding"], "epoch": ap["epoch"], "rulesEpoch": 0,
                **self.w.context_extra(self, b, t)}

    def record(self, b, what):
        w, V = self.w, self.B(b)
        head = hashlib.sha256((V["chain_head"] + canonical(what)).encode()).hexdigest()[:16]
        w.set(f"bodies/{b}/chain_head", head)
        w.inc(f"bodies/{b}/chain_len")

    def effect_happened(self, b):
        w = self.w
        w.inc("counters/effects")
        for tv, r in self.up["revocations"].items():
            if r["delivered_at"] is None:
                w.inc(f"planes/{self.parent}/revocations/{tv}/effects_since_order")

    def spend(self, b, n=1):
        lease = self.B(b)["lease"]
        self.w.set(f"bodies/{b}/lease/used", lease["used"] + n)

    def _floor(self, b, action, tool=None, entry=None, handles=None):
        """The linked floor's rules over this request, when the deployment asks for them."""
        if not self.real_floor:
            return None
        V, nd = self.B(b), None
        lease = V["lease"]
        alphabet = self.wf.defn["nodes"][lease["node"]]["alphabet"] if lease else ["Actuate", "Consult", "Report"]
        round_ = V["lease_idx"]
        kw = dict(epoch=self.P["epoch"], round_=round_, fence=round_, clear_set=V["clear_set"], observer_live=self.w.observer_live(self, b))
        if action == "Actuate":
            return lift.run_action(self.w.seat_of(b), "thinker", "Actuate", alphabet, tool=tool, digest=entry["digest"], outward=entry["effect"].get("outward", False),
                                   input_labels=sorted({x for ls in (handles or {}).values() for x in ls}), **kw)["floor"]
        if action == "Report":
            return lift.run_action(self.w.seat_of(b), "thinker", "Report", alphabet, **kw)["floor"]
        return lift.run_action(self.w.seat_of(b), "thinker", "Consult", alphabet, obj=tool, **kw)["floor"]

    def actuate(self, b, t, name, inputs, why=None, handles=None):
        w, V = self.w, self.B(b)
        by = f"gov:{b}"
        entry = self.by_name.get(name)
        beacon = bool(entry and entry["effect"]["beacon"])
        # The modelled floor. The bundle is consulted only after the floor has permitted (ADR-0030 §1).
        if entry is None:
            w.refuse_modelled(by, "R1-actuate-allowlisted", "Actuate", name, why)
            return False
        if V["alone"] and not beacon:
            w.refuse_modelled(by, "FD11-alone-permits-nothing", "Actuate", name, why)
            return False
        if not beacon:
            lease = V["lease"]
            if not lease:
                w.refuse_modelled(by, "FD8-local-bounds", "Actuate", name, why or "no live lease")
                return False
            if lease["used"] >= lease["count"]:
                w.refuse_modelled(by, "FD8-local-bounds", "Actuate", name, why or "the lease's count is spent")
                return False
        ordered = entry["effect"]["permit"] == "ordered"
        ap = self.P
        if ordered and len(self.members_signing()) < ap["certificate"]:
            w.refuse_modelled(by, "ordered-needs-quorum", "Actuate", name, why)
            return False
        if ordered and ap["outstanding"] + 1 >= self.K_UP:
            w.refuse_modelled(by, "FD10-outstanding-bound", "Actuate", name, why)
            return False
        inp = {"action": "Actuate", "principal": w.principal(self, b), "resource": {"tool": name, "digest": entry["digest"], "effect": entry["effect"]}, "inputs": inputs, "handles": handles or {},
               "context": self.context(b, t, "plane" if ordered else "governor"), "facts": w.facts(self, b, t)}
        if not w.admit(f"plane:{self.pid}" if ordered else by, self.chain, inp, name, why, floor=self._floor(b, "Actuate", name, entry, handles)):
            return False
        # Peer reports must never have enabled this (ADR-0065 §1). Checked by evaluating it again.
        peer_labels = {x["label"] for x in self.topics.values()}
        peer_names = [x for x in V["clear_set"] if x in peer_labels]
        if peer_names:
            cf = copy.deepcopy(inp)
            cf["context"]["clearSet"] = [x for x in cf["context"]["clearSet"] if x not in peer_names]
            cf_ok, res = w.bundles(self.chain, cf)
            w.emit("peer_adds_nothing", body=b, what=name, removed=peer_names, input=cf, evals=res, holds=cf_ok)
            if not cf_ok:
                w.inc("counters/invariant_failures")
        self.record(b, {"t": t, "permit": name, "i": inputs})
        if beacon:
            w.inc(f"bodies/{b}/beacons")
            w.inc("counters/beacons")
        else:
            self.spend(b)
            self.effect_happened(b)
        if ordered:
            lid = V["lease"]["id"]
            w.inc(f"{self.path}/outstanding", 1)
            w.inc(f"leases/{lid}/charge", 1)
            w.inc(f"bodies/{b}/own_unwatermarked", 1)
        w.start_entry(self, b, t, name, inputs)
        return True

    def consult(self, b, t, obj, what=None):
        w = self.w
        inp = {"action": "Consult", "principal": w.principal(self, b), "resource": {"object": obj}, "context": self.context(b, t), "facts": w.facts(self, b, t)}
        return w.admit(f"gov:{b}", self.chain, inp, what or f"Consult {obj}", floor=self._floor(b, "Consult", obj))

    def peer_report(self, b, t, topic, inputs, why=None):
        w, V = self.w, self.B(b)
        by = f"gov:{b}"
        if V["alone"]:
            w.refuse_modelled(by, "FD11-alone-permits-nothing", "Report", topic, why)
            return False
        if not V["lease"]:
            w.refuse_modelled(by, "FD8-local-bounds", "Report", topic, why or "no live lease")
            return False
        if topic not in self.topics:
            w.refuse_modelled(by, "FD12-topic-declared", "Report", topic, why)
            return False
        inp = {"action": "Report", "principal": w.principal(self, b), "resource": {"kind": "peer", "topic": topic}, "inputs": inputs, "context": self.context(b, t), "facts": w.facts(self, b, t)}
        if not w.admit(by, self.chain, inp, topic, why, floor=self._floor(b, "Report")):
            return False
        self.sent_tick.setdefault(b, {}).setdefault(topic, 0)
        self.sent_tick[b][topic] += 1
        w.inc(f"bodies/{b}/sends")
        w.inc("counters/sends")
        self.record(b, {"t": t, "send": topic, "d": hashlib.sha256(canonical(inputs).encode()).hexdigest()[:12]})
        spec = self.topics[topic]
        recv = []
        for o in spec["hear"]:
            O = self.B(o)
            if o == b or not O["alive"] or not O["hears"] or not O["lease"]:
                continue
            recv.append(o)
            if spec["delivery"] == "clear":
                new = sorted(set(O["clear_set"]) | {"untrusted", spec["label"]})
                if new != O["clear_set"]:
                    w.set(f"bodies/{o}/clear_set", new)
        w.emit("deliver", sender=b, topic=topic, receivers=recv, delivery=spec["delivery"], label=["untrusted", spec["label"]])
        return True

    def round_report(self, b, t, outcome):
        w, V = self.w, self.B(b)
        lease = V["lease"]
        if lease["used"] >= lease["count"]:
            w.refuse_modelled(f"gov:{b}", "FD8-local-bounds", "Report", "round outcome", "the lease's count is spent")
            return False
        inp = {"action": "Report", "principal": w.principal(self, b), "resource": {"kind": "round"}, "inputs": {"outcome": outcome}, "context": self.context(b, t), "facts": w.facts(self, b, t)}
        if not w.admit(f"gov:{b}", self.chain, inp, f"round outcome {outcome}", floor=self._floor(b, "Report")):
            return False
        self.spend(b)
        self.effect_happened(b)
        self.record(b, {"t": t, "outcome": outcome})
        self.end_lease(b, t, "outcome", f"the stack reported {outcome}", outcome=outcome)
        w.set(f"bodies/{b}/wait_until", t + w.a["successor_wait_ticks"])
        return True

    def misbehave(self, t):
        """The scenario's scripted bad requests: each should be refused by the rule meant to catch it."""
        for m in self.w.sc.get("stack_misbehaviour", []):
            if m["tick"] != t or m["body"] not in self.bodies:
                continue
            if "topic" in m:
                self.peer_report(m["body"], t, m["topic"], m["inputs"], why=m["why"])
            else:
                self.actuate(m["body"], t, m["tool"], m["inputs"], why=m["why"])

    def beacons(self, t):
        for b in self.bodies:
            V = self.B(b)
            if V["alive"] and V["alone"] and self.w.body_active(b) and t % 2 == 0 and self.w.beacon_tool:
                self.actuate(b, t, self.w.beacon_tool, {}, why="the governor's beacon while alone")

    def lease_ttls(self, t):
        for b in self.bodies:
            V = self.B(b)
            if V["lease"] and t >= V["lease"]["ttl_end"]:
                self.end_lease(b, t, "expired", "the lease's ttl")
                self.w.set(f"bodies/{b}/wait_until", t + self.w.a["successor_wait_ticks"])

    # ---- invariants: properties of the records, checked of the running state -----------------------

    def invariants(self, t):
        w, ap = self.w, self.P
        fails = []
        if not ap["outstanding"] < self.K_UP:
            fails.append("FD10: outstanding reached K_up")
        if ap["budget_spent"] > self.charter["budget"]:
            fails.append("FD3: budget exceeded")
        for b in self.bodies:
            V, L = self.B(b), self.B(b)["lease"]
            if L:
                if L["used"] > L["count"] or L["count"] > self.K:
                    fails.append(f"FD8/FD14: {b} count")
                if L["ttl_end"] > self.T_EXP:
                    fails.append(f"ADR-0064 §3: {b} ttl past the intent")
                if V["alone"]:
                    fails.append(f"FD11: {b} holds a lease while alone")
            elif w.body_running_entry(b):
                fails.append(f"ADR-0062 §7: {b} runs an entry with no lease")
        fails += w.invariants_extra(self, t) or []
        if fails:
            w.inc("counters/invariant_failures", len(fails))
            w.emit("invariant_failure", fails=fails)

    # ---- one tick ------------------------------------------------------------------------------------

    def step(self, t):
        w, ap = self.w, self.P
        self.sent_tick = {}
        self.tick_environment(t)
        signers = self.members_signing()
        ordered = len(signers) >= ap["certificate"]
        if ordered:
            w.set(f"{self.path}/last_tick_ordered", t)
            w.inc(f"{self.path}/index")
        self.hearing(t, ordered)
        self.watermark(t)
        self.membership_step(t)
        if t == self.T_EXP:
            w.set(f"{self.path}/intent_live", False)
            w.emit("intent_expired", plane=self.pid, tick=t, note="the intent's last tick. No grant, and no lease survives it")
            for b in self.bodies:
                if self.B(b)["lease"]:
                    self.end_lease(b, t, "expired", "the intent ended")
                    w.begin_terminal(self, b, t, "the intent ended")
        self.observers_read(t)
        self.grant_ready(t)
        w.expire_entries(self, t)
        self.misbehave(t)
        for b in self.bodies:
            if self.B(b)["alive"] and not self.B(b)["alone"]:
                w.stack(self, b, t)
        self.beacons(t)
        self.lease_ttls(t)
        w.physics(self, t)
        w.measures(self, t)
        self.invariants(t)
        return {"signers": len(signers), "ordered": ordered}


class AutonomousWorld(Core):
    """A Core that holds autonomous planes. A world fills in `self.auto`, in preflight, and the hooks it needs."""

    beacon_tool = None

    def __init__(self, sim_dir, scenario="scenario.json"):
        self.auto, self.lease_of_act, self.fired_triggers = {}, {}, set()
        super().__init__(sim_dir, scenario)

    def environment(self, t):
        for ev in self.sc.get("environment", []):
            if ev.get("tick") == t:
                plane = self.auto[ev.get("plane", next(iter(self.auto)))]
                if not plane.inject(ev, t):
                    self.inject(ev, t)

    def step(self, t):
        self.environment(t)
        info = {}
        for p in self.auto.values():
            info[p.pid] = p.step(t)
        return info if len(info) != 1 else next(iter(info.values()))

    # Defaults, for a world that does not care.
    def inject(self, ev, t):
        raise SystemExit(f"this world does not know the environment event {ev['kind']}")

    def body_state(self, b):
        return {}

    def tick_body(self, plane, b, t):
        pass

    def context_extra(self, plane, b, t):
        return {}

    def facts(self, plane, b, t):
        return {}

    def body_active(self, b):
        return True

    def start_entry(self, plane, b, t, name, inputs):
        pass

    def stop_entries(self, plane, b):
        pass

    def expire_entries(self, plane, t):
        pass

    def body_running_entry(self, b):
        return False

    def physics(self, plane, t):
        pass

    def measures(self, plane, t):
        pass

    def begin_terminal(self, plane, b, t, why):
        self.set(f"bodies/{b}/wait_until", None)

    def resume_from_terminal(self, plane, b):
        pass

    def reset_for_lease(self, plane, b):
        pass

    def on_destroyed(self, plane, b, t):
        pass

    def on_edge_fired(self, plane, fired, t):
        pass

    def invariants_extra(self, plane, t):
        return []

    def observer_live(self, plane, b):
        return True
