#!/usr/bin/env python3
"""Build the proposed floors from the genesis floor, in three cumulative stages, with their tests.

The genesis floor (../genesis-floor.cedar, ../genesis.cedarschema) is what the reference follows and is
not edited here. Each stage is the floor as it would stand if the records it names were in force:

  labels     ADR-0047 with ADR-0048 and ADR-0049 (ADR-0041 A1; ADR-0030 A2): R5, R6, R7
  control    + ADR-0050 (ADR-0041 A3): C1 to C9, the operator's requests
  emergency  + ADR-0052 (ADR-0041 A2): X1 retired, B10 admits the `emergency` kind for Actuate

Every edit to the genesis text is a replacement of a string asserted to occur exactly once, so a change
to the genesis floor that this file does not expect stops the build instead of producing a wrong floor.

Writes, per stage: <stage>.cedarschema, <stage>-floor.cedar, <stage>-tests.json.
Usage: build.py            (then: cedar validate / cedar run-tests / run-gates.py <stage>)
"""
import copy
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.dirname(HERE)
STAGES = ["labels", "control", "emergency"]


def once(text, old, new):
    assert text.count(old) == 1, f"expected exactly one occurrence of: {old[:60]!r}"
    return text.replace(old, new)


# ---- schema --------------------------------------------------------------------------------------

def schema_labels(s):
    s = once(s, "  entity Tool in [ToolSet] {\n    digest: String,\n  };",
             "  entity Tool in [ToolSet] {\n    digest: String,\n"
             "    outward: Bool,                        // ADR-0047 §7; ADR-0049 §4: derived by the lift from the entry's channel and\n"
             "                                          // the issued rules' list of targets inside the deployment; never declared\n"
             "  };")
    s = once(s, "    observerLive: Bool,                   // ADR-0039 §1: live(o) for some cell Observer o of this seat, a syntactic lift\n  };",
             "    observerLive: Bool,                   // ADR-0039 §1: live(o) for some cell Observer o of this seat, a syntactic lift\n"
             "    // ADR-0047 §4; ADR-0030 A2. All four are computed by the mechanism from the record and from the\n"
             "    // entry of the granted bundle revision. No policy computes them.\n"
             "    clearSet: Set<String>,                // labels of everything delivered clear to this principal this round\n"
             "    inputLabels: Set<String>,             // join of the labels of the call's inputs that are handles\n"
             "    destLiteral: Bool,                    // an input the entry marks a destination is a literal\n"
             "    destLabels: Set<String>,              // join of the labels of destination inputs that are handles\n"
             "  };")
    return s


def schema_control(s):
    s = once(s, "    kind: String,                         // \"thinker\" | \"observer\" | \"grant\"",
             "    kind: String,                         // \"thinker\" | \"observer\" | \"grant\" | \"operator\" (ADR-0050 §1)")
    s = once(s, "  type EraseCtx = {",
             "  // ADR-0050 §4. What the control entries read. Every field is a fact the mechanism holds about the\n"
             "  // operator, the target and the request; the operator supplies none of them.\n"
             "  type ControlCtx = {\n"
             "    personaInForce: Bool,                 // the operator's Persona is promoted and not revoked\n"
             "    hasLease: Bool,                       // the operator holds a live lease\n"
             "    peerLive: Bool,                       // another operator in the domain holds a live lease\n"
             "    freshAssertion: Bool,                 // a sign-on assertion naming the key and the current fence verified\n"
             "    targetSeated: Bool,                   // the target was seated by a quorum and is not revoked\n"
             "    targetLive: Bool,                     // the target holds a live lease\n"
             "    sameBinding: Bool,                    // Persona, bundle, confinement and seat are the last lease's\n"
             "    nextRound: Bool,                      // the round named is the last lease's, advanced by one\n"
             "    lastAlphabet: Set<String>,            // the last lease's alphabet\n"
             "    newAlphabet: Set<String>,             // the alphabet asked for\n"
             "    taskLabelled: Bool,                   // the task carries a label (ADR-0047 §1, R9)\n"
             "    taskLabel: Set<String>,\n"
             "    taskLabelsAllowed: Set<String>,       // the labels the target's seating allows a task (ADR-0050 §5)\n"
             "  };\n\n"
             "  type EraseCtx = {")
    s = once(s, "  entity ArchiveRecord {",
             "  entity Fleet;                           // what FenceEpoch acts on: every lease at the epoch\n\n"
             "  entity ArchiveRecord {")
    s = once(s, "  // ---- the erasure action (ADR-0006) -------------------------------------------------------",
             "  // ---- the control alphabet (ADR-0050 §4, Proposed) ---------------------------------------\n"
             "  // An `operator` seat's requests. Three add and need a live lease and a live peer; three deny.\n"
             "  action Regrant     appliesTo { principal: [Seat], resource: [Seat],     context: ControlCtx };\n"
             "  action Renew       appliesTo { principal: [Seat], resource: [Seat],     context: ControlCtx };\n"
             "  action AttestGates appliesTo { principal: [Seat], resource: [Artifact], context: ControlCtx };\n"
             "  action EndRound    appliesTo { principal: [Seat], resource: [Seat],     context: ControlCtx };\n"
             "  action Revoke      appliesTo { principal: [Seat], resource: [Seat],     context: ControlCtx };\n"
             "  action FenceEpoch  appliesTo { principal: [Seat], resource: [Fleet],    context: ControlCtx };\n\n"
             "  // ---- the erasure action (ADR-0006) -------------------------------------------------------")
    return s


def schema_emergency(s):
    s = once(s, "| \"operator\" (ADR-0050 §1)", "| \"operator\" (ADR-0050 §1) | \"emergency\" (ADR-0052 §1)")
    s = once(s, "    breakGlass: {\n"
                "      quorum: Bool,                       // a break-glass quorum on the issued roster (ADR-0013 §1)\n"
                "      tools: ToolSet,                     // the break-glass envelope, issued with the roster\n"
                "    },\n",
             "    // ADR-0052 §2: no break-glass fields. An emergency seat's envelope is its `toolAllowlist`,\n"
             "    // computed at activation; the roster's quorum is what granted its lease and is not a request property.\n")
    return s


# ---- floor ---------------------------------------------------------------------------------------

LABELS = '''// ---- carve-outs on Run's effects by label — ADR-0047 §7 (F1 to F3), named by ADR-0041 A1 ---------
// Each is a set-membership test on attributes the mechanism computed. `untrusted` and `restricted`
// are the two names the floor reserves. `outward` is derived, never declared. They are forbids, so
// they deny whatever permit is satisfied, a break-glass permit included.

// F1, read then send: a principal that has read untrusted content in the clear makes an outward
// call while holding restricted content, read in the clear or passed by handle.
@id("R5-no-read-then-send")
forbid (principal, action == Topak::Action::"Actuate", resource)
when {
  resource.outward &&
  context.clearSet.contains("untrusted") &&
  (context.clearSet.contains("restricted") || context.inputLabels.contains("restricted"))
};

// F2, steered destination: a principal that has read untrusted content in the clear types the
// destination of an outward call. A literal carries anything the principal has read.
@id("R6-no-steered-destination")
forbid (principal, action == Topak::Action::"Actuate", resource)
when {
  resource.outward &&
  context.clearSet.contains("untrusted") &&
  context.destLiteral
};

// F3, replayed content: the destination of an outward call is a handle to untrusted content,
// whatever the principal has read.
@id("R7-no-replayed-destination")
forbid (principal, action == Topak::Action::"Actuate", resource)
when {
  resource.outward &&
  context.destLabels.contains("untrusted")
};

'''

CONTROL = '''
// ============================================================================================
// The control entries — ADR-0050 §4, named by ADR-0041 A3. An `operator` seat's requests.
// A first lease is not here: the mechanism grants one when a quorum completes (ADR-0050 §2).
// ============================================================================================

// A successor grant: the target's next round, with nothing wider. The binding and the round are
// compared by the lift; the alphabet is compared here.
@id("C1-regrant-successor")
permit (principal, action == Topak::Action::"Regrant", resource)
when {
  principal.kind == "operator" &&
  resource.domain == principal.domain &&
  context.targetSeated &&
  !context.targetLive &&
  context.sameBinding &&
  context.nextRound &&
  context.lastAlphabet.containsAll(context.newAlphabet)
};

@id("C2-renew")
permit (principal, action == Topak::Action::"Renew", resource)
when {
  principal.kind == "operator" &&
  resource.domain == principal.domain &&
  context.targetLive
};

@id("C3-attest-gates")
permit (principal, action == Topak::Action::"AttestGates", resource)
when { principal.kind == "operator" && principal.domain == "build" };

// A deny needs no lease: a Persona in force, and a credential that is fresh, by the lease or by a
// sign-on assertion (ADR-0050 §4, R1).
@id("C4-deny")
permit (
  principal,
  action in [Topak::Action::"EndRound", Topak::Action::"Revoke", Topak::Action::"FenceEpoch"],
  resource
)
when {
  principal.kind == "operator" &&
  context.personaInForce &&
  (context.hasLease || context.freshAssertion)
};

// An add needs a live lease and a live peer.
@id("C5-add-needs-lease-and-peer")
forbid (
  principal,
  action in [Topak::Action::"Regrant", Topak::Action::"Renew", Topak::Action::"AttestGates"],
  resource
)
when { !context.hasLease || !context.peerLive };

@id("C6-no-self")
forbid (principal, action in [Topak::Action::"Regrant", Topak::Action::"Renew"], resource)
when { resource == principal };

// The fleet fence is the one deny that needs a live lease (ADR-0050 §4, R5).
@id("C7-fence-needs-lease")
forbid (principal, action == Topak::Action::"FenceEpoch", resource)
when { !context.hasLease };

// The round's task carries a label, and one its seating allows (ADR-0047 §1, R9; ADR-0050 §5).
@id("C8-task-label-in-bounds")
forbid (principal, action == Topak::Action::"Regrant", resource)
when { !context.taskLabelled || !context.taskLabelsAllowed.containsAll(context.taskLabel) };

// An operator ends rounds and revokes in its own domain. Across domains the tool is the fence.
@id("C9-stop-in-own-domain")
forbid (principal, action in [Topak::Action::"EndRound", Topak::Action::"Revoke"], resource)
when { resource.domain != principal.domain };
'''


def floor_labels(f):
    return once(f, "// ============================================================================================\n"
                   "// Floor exceptions — ADR-0013 §2. Count: 2, bounded by ADR-0026 R6.",
                LABELS +
                "// ============================================================================================\n"
                "// Floor exceptions — ADR-0013 §2. Count: 2, bounded by ADR-0026 R6.")


def floor_control(f):
    return f.rstrip("\n") + "\n" + CONTROL


def floor_emergency(f):
    i = f.index("// X1 break-glass (ADR-0009).")
    j = f.index("// X2 erasure (ADR-0006).")
    assert '@id("X1-break-glass")' in f[i:j]
    f = f[:i] + ("// X1 break-glass is retired (ADR-0052 §2). Break-glass is an emergency seating: the break-glass\n"
                 "// roster's quorum seats a named person on a seat of kind `emergency` for one round, and that seat's\n"
                 "// calls are admitted by R1 over an envelope computed at activation.\n\n") + f[j:]
    f = once(f, "// Floor exceptions — ADR-0013 §2. Count: 2, bounded by ADR-0026 R6.",
             "// Floor exceptions — ADR-0013 §2. Count: 1, bounded by ADR-0026 R6.")
    f = once(f, 'when { principal.kind != "thinker" };',
             '// ADR-0052 §1: an `emergency` seat, held by a person for one round, may Actuate and nothing else here.\n'
             'when {\n'
             '  principal.kind != "thinker" &&\n'
             '  !(principal.kind == "emergency" && action == Topak::Action::"Actuate")\n'
             '};')
    return f


# ---- tests ---------------------------------------------------------------------------------------

NS = "Topak::"
uid = lambda t, i: {"type": NS + t, "id": i}
ref = lambda t, i: {"__entity": uid(t, i)}
ent = lambda t, i, attrs=None, parents=(): {"uid": uid(t, i), "attrs": attrs or {}, "parents": [uid(*p) for p in parents]}
RUN_ALPHA = ["Consult", "Actuate", "Report"]
U, R = "untrusted", "restricted"


def is_run_ctx(c):
    return "runRoot" in c


def case(ents, name, p, a, r, ctx, decision, reason=()):
    rt, rid = r
    return {"name": name,
            "request": {"principal": f'{NS}Seat::"{p}"', "action": f'{NS}Action::"{a}"',
                        "resource": f'{NS}{rt}::"{rid}"', "context": ctx},
            "entities": ents, "decision": decision, "reason": list(reason), "num_errors": 0}


def tests_labels(cases):
    ents = copy.deepcopy(cases[0]["entities"])
    for e in ents:
        if e["uid"]["type"] == NS + "Tool":
            e["attrs"]["outward"] = e["uid"]["id"] == "valve@d4"     # the break-glass tool reaches outside
    ents.append(ent("Tool", "post@d5", {"digest": "d5", "outward": True}, [("ToolSet", "run-allow")]))
    for c in cases:
        c["entities"] = ents
        if is_run_ctx(c["request"]["context"]):
            c["request"]["context"].update(clearSet=[], inputLabels=[], destLiteral=False, destLabels=[])

    def run_ctx(clear=(), inl=(), lit=False, dest=(), bg=False, live=True, allow="run-allow", alphabet=RUN_ALPHA):
        return {"lease": {"alphabet": alphabet, "rulesEpoch": 5}, "epoch": 3, "round": 7,
                "runRoot": ref("CorpusRoot", "run-pinned"), "toolAllowlist": ref("ToolSet", allow),
                "breakGlass": {"quorum": bg, "tools": ref("ToolSet", "bg-tools")}, "observerLive": live,
                "clearSet": list(clear), "inputLabels": list(inl), "destLiteral": lit, "destLabels": list(dest)}
    k = lambda *a, **kw: case(ents, *a, **kw)
    post, inside = ("Tool", "post@d5"), ("Tool", "search@d3")
    cases += [
        k("R5 outward call after reading untrusted and restricted in the clear", "r1", "Actuate", post, run_ctx(clear=[U, R]), "deny", ["R5-no-read-then-send"]),
        k("R5 outward call after reading untrusted, with restricted by handle", "r1", "Actuate", post, run_ctx(clear=[U], inl=[R]), "deny", ["R5-no-read-then-send"]),
        k("R5 does not refuse a principal that has read nothing untrusted", "r1", "Actuate", post, run_ctx(clear=[R], inl=[R]), "allow", ["R1-actuate-allowlisted"]),
        k("R5 does not refuse when nothing restricted is held", "r1", "Actuate", post, run_ctx(clear=[U]), "allow", ["R1-actuate-allowlisted"]),
        k("R5 does not refuse a call that is not outward", "r1", "Actuate", inside, run_ctx(clear=[U, R], lit=True, dest=[U]), "allow", ["R1-actuate-allowlisted"]),
        k("R6 literal destination after reading untrusted in the clear", "r1", "Actuate", post, run_ctx(clear=[U], lit=True), "deny", ["R6-no-steered-destination"]),
        k("R6 does not refuse a literal destination from a principal that has read nothing untrusted", "r1", "Actuate", post, run_ctx(lit=True), "allow", ["R1-actuate-allowlisted"]),
        k("R6 does not refuse a destination by handle from a clean source", "r1", "Actuate", post, run_ctx(clear=[U], dest=["directory"]), "allow", ["R1-actuate-allowlisted"]),
        k("R7 destination is a handle to untrusted content", "r1", "Actuate", post, run_ctx(dest=[U]), "deny", ["R7-no-replayed-destination"]),
        k("R7 does not read the labels of inputs that are not destinations", "r1", "Actuate", post, run_ctx(inl=[U]), "allow", ["R1-actuate-allowlisted"]),
        k("R5 holds under break-glass", "r1", "Actuate", ("Tool", "valve@d4"), run_ctx(clear=[U, R], bg=True), "deny", ["R5-no-read-then-send"]),
        k("R6 holds under break-glass", "r1", "Actuate", ("Tool", "valve@d4"), run_ctx(clear=[U], lit=True, bg=True), "deny", ["R6-no-steered-destination"]),
    ]
    return cases


def tests_control(cases):
    ents = cases[0]["entities"]
    ents += [ent("Seat", "op1", {"domain": "run", "kind": "operator"}),
             ent("Seat", "op2", {"domain": "run", "kind": "operator"}),
             ent("Seat", "opb", {"domain": "build", "kind": "operator"}),
             ent("Fleet", "fleet")]

    def cc(**kw):
        c = dict(personaInForce=True, hasLease=True, peerLive=True, freshAssertion=False, targetSeated=True,
                 targetLive=False, sameBinding=True, nextRound=True, lastAlphabet=RUN_ALPHA, newAlphabet=RUN_ALPHA,
                 taskLabelled=True, taskLabel=[U], taskLabelsAllowed=[U, R])
        c.update(kw)
        return c
    k = lambda *a, **kw: case(ents, *a, **kw)
    r1, a1, op1, fleet, art = ("Seat", "r1"), ("Seat", "a1"), ("Seat", "op1"), ("Fleet", "fleet"), ("Artifact", "art-a1")
    C5, C6, C7, C8, C9 = ("C5-add-needs-lease-and-peer", "C6-no-self", "C7-fence-needs-lease",
                          "C8-task-label-in-bounds", "C9-stop-in-own-domain")
    cases += [
        k("C1 successor grant, nothing wider", "op1", "Regrant", r1, cc(), "allow", ["C1-regrant-successor"]),
        k("C1 successor grant with a narrower alphabet", "op1", "Regrant", r1, cc(newAlphabet=["Consult", "Report"]), "allow", ["C1-regrant-successor"]),
        k("C1 a wider alphabet is not a successor", "op1", "Regrant", r1, cc(lastAlphabet=["Consult", "Report"]), "deny"),
        k("C1 a changed Persona, bundle or profile is not a successor", "op1", "Regrant", r1, cc(sameBinding=False), "deny"),
        k("C1 a round that is not the next is not a successor", "op1", "Regrant", r1, cc(nextRound=False), "deny"),
        k("C1 a target no quorum seated", "op1", "Regrant", r1, cc(targetSeated=False), "deny"),
        k("C1 a target that still holds a live lease", "op1", "Regrant", r1, cc(targetLive=True), "deny"),
        k("C1 a target in another domain", "op1", "Regrant", a1, cc(), "deny"),
        k("C1 a regrant by a seat that is not an operator", "r1", "Regrant", ("Seat", "ro1"), cc(), "deny"),
        k("C2 renewal of a live lease", "op1", "Renew", r1, cc(targetLive=True), "allow", ["C2-renew"]),
        k("C2 renewal of a lease that is not live", "op1", "Renew", r1, cc(), "deny"),
        k("C3 a Build operator attests the gates", "opb", "AttestGates", art, cc(), "allow", ["C3-attest-gates"]),
        k("C3 a Run operator does not", "op1", "AttestGates", art, cc(), "deny"),
        k("C4 end a round under a live lease", "op1", "EndRound", r1, cc(targetLive=True), "allow", ["C4-deny"]),
        k("C4 revoke with a lapsed lease and a fresh assertion", "op1", "Revoke", r1, cc(hasLease=False, peerLive=False, freshAssertion=True), "allow", ["C4-deny"]),
        k("C4 revoke with a lapsed lease and no assertion", "op1", "Revoke", r1, cc(hasLease=False), "deny"),
        k("C4 a revoked operator cannot deny", "op1", "EndRound", r1, cc(personaInForce=False), "deny"),
        k("C4 fence the fleet under a live lease", "op1", "FenceEpoch", fleet, cc(), "allow", ["C4-deny"]),
        k("C4 a deny needs no peer", "op1", "Revoke", r1, cc(peerLive=False), "allow", ["C4-deny"]),
        k("C5 a regrant with no live lease", "op1", "Regrant", r1, cc(hasLease=False), "deny", [C5]),
        k("C5 a regrant with no live peer", "op1", "Regrant", r1, cc(peerLive=False), "deny", [C5]),
        k("C5 a renewal with no live peer", "op1", "Renew", r1, cc(targetLive=True, peerLive=False), "deny", [C5]),
        k("C5 gates attested with no live peer", "opb", "AttestGates", art, cc(peerLive=False), "deny", [C5]),
        k("C6 an operator regrants itself", "op1", "Regrant", op1, cc(), "deny", [C6]),
        k("C6 an operator renews itself", "op1", "Renew", op1, cc(targetLive=True), "deny", [C6]),
        k("C6 an operator regrants a peer", "op1", "Regrant", ("Seat", "op2"), cc(), "allow", ["C1-regrant-successor"]),
        k("C7 a lapsed operator may not fence the fleet", "op1", "FenceEpoch", fleet, cc(hasLease=False, freshAssertion=True), "deny", [C7]),
        k("C8 a task with no label", "op1", "Regrant", r1, cc(taskLabelled=False, taskLabel=[]), "deny", [C8]),
        k("C8 a task label its seating does not allow", "op1", "Regrant", r1, cc(taskLabel=["directory"]), "deny", [C8]),
        k("C9 end a round in another domain", "op1", "EndRound", a1, cc(), "deny", [C9]),
        k("C9 revoke in another domain", "op1", "Revoke", a1, cc(), "deny", [C9]),
        k("B10 an operator seat cannot actuate", "op1", "Actuate", ("Tool", "search@d3"),
          next(c["request"]["context"] for c in cases if c["name"] == "R1 actuate, allowlisted"), "deny", ["B10-only-thinkers-author"]),
    ]
    return cases


def tests_emergency(cases):
    ents = cases[0]["entities"]
    for e in ents:
        if e["uid"] == uid("Tool", "valve@d4"):
            e["parents"] = [uid("ToolSet", "em-env")]
    ents[:] = [e for e in ents if e["uid"] != uid("ToolSet", "bg-tools")]
    ents += [ent("ToolSet", "em-env"), ent("Seat", "e1", {"domain": "run", "kind": "emergency"}),
             ent("Topic", "e1-r7", {"owner": ref("Seat", "e1"), "epoch": 3, "round": 7, "sealed": False})]
    gone = lambda c: c["name"].startswith("X1 ") or "break-glass" in c["name"]
    cases[:] = [c for c in cases if not gone(c)]
    for c in cases:
        c["request"]["context"].pop("breakGlass", None)

    def run_ctx(clear=(), lit=False, live=True, allow="em-env", alphabet=RUN_ALPHA):
        return {"lease": {"alphabet": alphabet, "rulesEpoch": 5}, "epoch": 3, "round": 7,
                "runRoot": ref("CorpusRoot", "run-pinned"), "toolAllowlist": ref("ToolSet", allow),
                "observerLive": live, "clearSet": list(clear), "inputLabels": [], "destLiteral": lit, "destLabels": []}
    build = next(c["request"]["context"] for c in cases if c["name"] == "B2 draft in own workspace")
    k = lambda *a, **kw: case(ents, *a, **kw)
    valve = ("Tool", "valve@d4")
    cases += [
        k("R1 an emergency seat calls a tool in its envelope", "e1", "Actuate", valve, run_ctx(), "allow", ["R1-actuate-allowlisted"]),
        k("R3 does not couple an emergency seat: no live Observer", "e1", "Actuate", valve, run_ctx(live=False), "allow", ["R1-actuate-allowlisted"]),
        k("R1 an emergency seat calls a tool outside its envelope", "e1", "Actuate", ("Tool", "tlc@d2"), run_ctx(), "deny"),
        k("R2 an emergency seat reports with no live Observer", "e1", "Report", ("Topic", "e1-r7"), run_ctx(live=False), "allow", ["R2-report-own-topic"]),
        k("X1 is retired: a Thinker cannot reach the emergency envelope", "r1", "Actuate", valve, run_ctx(allow="run-allow"), "deny"),
        k("R6 binds the person holding an emergency seat", "e1", "Actuate", valve, run_ctx(clear=[U], lit=True), "deny", ["R6-no-steered-destination"]),
        k("B10 an emergency seat cannot draft", "e1", "Draft", ("WorkspaceTarget", "ws-a1-r7/spec.tla"), build, "deny", ["B10-only-thinkers-author"]),
        k("B10 an emergency seat cannot submit", "e1", "Submit", ("Artifact", "art-a1"), build, "deny", ["B10-only-thinkers-author"]),
    ]
    return cases


def main():
    schema = open(os.path.join(GEN, "genesis.cedarschema")).read()
    floor = open(os.path.join(GEN, "genesis-floor.cedar")).read()
    cases = json.load(open(os.path.join(GEN, "genesis-tests.json")))
    for c in cases[1:]:
        c["entities"] = cases[0]["entities"]            # one shared list, as the generator made it
    steps = {"labels": (schema_labels, floor_labels, tests_labels),
             "control": (schema_control, floor_control, tests_control),
             "emergency": (schema_emergency, floor_emergency, tests_emergency)}
    banner = ("// PROPOSED · built by floor/proposed/build.py from the genesis floor · stage: {} · not ratified,\n"
              "// and not what the reference follows. Edit build.py, not this file.\n")
    for stage in STAGES:
        fs, ff, ft = steps[stage]
        schema, floor, cases = fs(schema), ff(floor), ft(cases)
        open(os.path.join(HERE, f"{stage}.cedarschema"), "w").write(banner.format(stage) + schema)
        open(os.path.join(HERE, f"{stage}-floor.cedar"), "w").write(banner.format(stage) + floor)
        json.dump(cases, open(os.path.join(HERE, f"{stage}-tests.json"), "w"), indent=1)
        print(f"{stage:10} {floor.count('@id(')} policies · {len(cases)} cases")


if __name__ == "__main__":
    main()
