"""The frozen input, built as mechanism/crates/topak-core/src/lift.rs builds it.

This file is a model of the lift: the reference's `lift` needs a replica's whole State. What keeps it
honest is that the floor validates every request and entity against schema S in strict mode, and a
validation failure is a deny that the trace shows.

A `Frozen` is the five parts the floor reads. `bundle_input` is the bundle tier's view of the same facts.
"""
NS = "Topak"


def uid(t, i):
    return {"type": f"{NS}::{t}", "id": i}


def eref(t, i):
    return {"__entity": uid(t, i)}


def ent(t, i, attrs=None, parents=()):
    return {"uid": uid(t, i), "attrs": attrs or {}, "parents": list(parents)}


def _seat(seat, domain, kind, rosters=()):
    return ent("Seat", seat, {"domain": domain, "kind": kind}, [uid("Roster", r) for r in rosters])


def _base(seat, domain, kind, rosters, ws):
    return [ent("Roster", "grant"), ent("Roster", "veto"), _seat(seat, domain, kind, rosters),
            ent("CorpusRoot", "pinned"), ent("CorpusRoot", "run-pinned"), ent("Workspace", ws),
            ent("ToolSet", "build-allow"), ent("ToolSet", "run-allow")]


def tool_id(tool, digest):
    return f"{tool}@{digest}"


def topic_name(chain, domain, seat, epoch, round_):
    return f"topak.{chain[:12]}.{domain}.{seat}.e{epoch}.r{round_}"


def _frozen(seat, action, resource, context, entities, bundle_resource, inputs, handles, epoch, round_, role, rules_epoch, fence, domain):
    return {
        "floor": {"principal": uid("Seat", seat), "action": {"type": f"{NS}::Action", "id": action}, "resource": resource, "context": context, "entities": entities},
        "bundle_input": {"action": action, "principal": {"seat": seat, "domain": domain}, "resource": bundle_resource, "inputs": inputs, "handles": handles,
                         "context": {"epoch": epoch, "round": round_, "roundRole": role, "rulesEpoch": rules_epoch, "lease": fence}},
    }


def label_facts(entry, inputs, handles=None, inside_targets=()):
    """What the mechanism computes about an Actuate from its allowlist entry, as keyword arguments for
    run_action (allowlist.rs, ADR-0049 §4). Leave these out and floor rules R5 to R7 can never fire.

    `handles` maps each input given as a handle to its label. An entry's channel whose target is not
    in `inside_targets` is outward. A call with no entry is outward."""
    handles = handles or {}
    if entry is None:
        return {"outward": True}
    in_labels, dest_labels, dest_literal = set(), set(), False
    for f in (inputs or {}):
        destination = bool(entry.get("inputs", {}).get(f, {}).get("destination"))
        if f in handles:
            in_labels |= set(handles[f])
            if destination:
                dest_labels |= set(handles[f])
        elif destination:
            dest_literal = True
    channel = entry.get("channel")
    return {"input_labels": in_labels, "dest_labels": dest_labels, "dest_literal": dest_literal, "outward": bool(channel) and channel["target"] not in inside_targets}


def run_action(seat, kind, action, alphabet, *, epoch=1, round_=1, rules_epoch=1, fence=1, role="author", rosters=(), observer_live=True, clear_set=(),
               input_labels=(), dest_literal=False, dest_labels=(), obj=None, in_root=True, tool=None, digest=None, allowlisted=True, outward=False, inputs=None,
               handles=None, chain="0" * 64, edge=None, edge_uid=None, edge_source="-", edge_chosen=False, decision_point=None, sealed=False, topic_owner=None):
    """A Run-domain request: Consult, Actuate, Report or Route. Spread lift.label_facts into an Actuate,
    and WorkflowRun.route_facts into a Route. `topic_owner` makes a Report to another seat's topic."""
    ws = f"ws-{seat}-e{epoch}-r{round_}"
    entities = _base(seat, "run", kind, rosters, ws)
    ctx = {"lease": {"alphabet": sorted(alphabet), "rulesEpoch": rules_epoch}, "epoch": epoch, "round": round_, "runRoot": eref("CorpusRoot", "run-pinned"),
           "toolAllowlist": eref("ToolSet", "run-allow"), "observerLive": observer_live, "clearSet": sorted(clear_set), "inputLabels": sorted(input_labels),
           "destLiteral": dest_literal, "destLabels": sorted(dest_labels), "decisionPoint": [eref("WorkflowNode", decision_point)] if decision_point else []}
    nodes = {decision_point} if decision_point else set()
    if action == "Consult":
        entities.append(ent("CorpusObject", obj, parents=[uid("CorpusRoot", "run-pinned")] if in_root else []))
        res, bres = uid("CorpusObject", obj), {"object": obj}
    elif action == "Actuate":
        tid = tool_id(tool, digest)
        entities.append(ent("Tool", tid, {"digest": digest, "outward": outward}, [uid("ToolSet", "run-allow")] if allowlisted else []))
        res, bres = uid("Tool", tid), {"tool": tool, "digest": digest}
    elif action == "Report":
        name = topic_name(chain, "run", seat, epoch, round_)
        entities.append(ent("Topic", name, {"owner": eref("Seat", topic_owner or seat), "epoch": epoch, "round": round_, "sealed": sealed}))
        if topic_owner and topic_owner != seat:
            entities.append(_seat(topic_owner, "run", "thinker"))
        res, bres = uid("Topic", name), {"topic": name}
    elif action == "Route":
        nodes.add(edge_source)
        entities.append(ent("Edge", edge_uid or edge, {"source": eref("WorkflowNode", edge_source), "chosen": edge_chosen}))
        res, bres = uid("Edge", edge_uid or edge), {"edge": edge}
    else:
        raise ValueError(action)
    entities += [ent("WorkflowNode", n) for n in sorted(nodes)]
    return _frozen(seat, action, res, ctx, entities, bres, inputs, handles or {}, epoch, round_, role, rules_epoch, fence, "run")


def build_action(seat, kind, action, alphabet, *, epoch=1, round_=1, rules_epoch=1, fence=1, role="author", rosters=(), obj=None, in_root=True, target=None,
                 tool=None, digest=None, allowlisted=True, inputs=None, inputs_ok=True, artifact=None, author=None, author_kind="thinker", author_rosters=(), verdict=None,
                 vote_rules_epoch=None, chain="0" * 64, sealed=False, evidence=None):
    """A Build-domain request: Read, Draft, Invoke, Emit, Submit or Vote."""
    ws = f"ws-{seat}-e{epoch}-r{round_}"
    entities = _base(seat, "build", kind, rosters, ws)
    lease = {"alphabet": sorted(alphabet), "rulesEpoch": rules_epoch}
    ctx = {"lease": lease, "epoch": epoch, "round": round_, "roundRole": role, "corpusRoot": eref("CorpusRoot", "pinned"), "workspace": eref("Workspace", ws),
           "toolAllowlist": eref("ToolSet", "build-allow"), "inputsInWorkspace": inputs_ok}
    if action == "Read":
        entities.append(ent("CorpusObject", obj, parents=[uid("CorpusRoot", "pinned")] if in_root else []))
        res, bres = uid("CorpusObject", obj), {"object": obj}
    elif action == "Draft":
        tid = f"{ws}/{target}"
        entities.append(ent("WorkspaceTarget", tid, parents=[uid("Workspace", ws)]))
        res, bres = uid("WorkspaceTarget", tid), {"target": target}
    elif action == "Invoke":
        tid = tool_id(tool, digest)
        entities.append(ent("Tool", tid, {"digest": digest, "outward": False}, [uid("ToolSet", "build-allow")] if allowlisted else []))
        res, bres = uid("Tool", tid), {"tool": tool, "digest": digest}
    elif action == "Emit":
        name = topic_name(chain, "build", seat, epoch, round_)
        entities.append(ent("Topic", name, {"owner": eref("Seat", seat), "epoch": epoch, "round": round_, "sealed": sealed}))
        res, bres = uid("Topic", name), {"topic": name}
    elif action == "Submit":
        entities.append(ent("Artifact", artifact, {"author": eref("Seat", seat)}))
        res, bres = uid("Artifact", artifact), {"artifact": artifact}
    elif action == "Vote":
        entities.append(ent("Artifact", artifact, {"author": eref("Seat", author)}))
        if author != seat:
            entities.append(_seat(author, "build", author_kind, author_rosters))
        ctx = {"lease": lease, "epoch": epoch, "rulesEpoch": rules_epoch, "verdict": verdict, "voteRulesEpoch": rules_epoch if vote_rules_epoch is None else vote_rules_epoch,
               "grantRoster": eref("Roster", "grant"), "vetoRoster": eref("Roster", "veto")}
        res, bres = uid("Artifact", artifact), {"artifact": artifact, "evidence": evidence}
    else:
        raise ValueError(action)
    return _frozen(seat, action, res, ctx, entities, bres, inputs, {}, epoch, round_, role, rules_epoch, fence, "build")
