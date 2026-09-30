#!/usr/bin/env python3
"""Generate genesis-tests.json for `cedar run-tests` against the genesis floor (ADR-0030).

Each case names the floor entry it exercises. Every permit has a case that allows and at least one
that denies, and every forbid has a case where it is the reason for a deny, so a policy that never
changes a decision would show up here as a missing reason.
"""
import json

NS = "Topak::"


def uid(t, i):
    return {"type": NS + t, "id": i}


def ref(t, i):
    return {"__entity": uid(t, i)}


def ent(t, i, attrs=None, parents=()):
    return {"uid": uid(t, i), "attrs": attrs or {}, "parents": [uid(*p) for p in parents]}


EPOCH, ROUND, RULES = 3, 7, 5

ENTITIES = [
    ent("Roster", "grant"), ent("Roster", "veto"),
    # ADR-0037 §1, §2: one seat per principal, each with a kind. a1 authors this round. g1 is a grant seat
    # that is also the author of art-g1, so recusal (B7) has something to refuse that B6/B10 do not.
    ent("Seat", "a1", {"domain": "build", "kind": "thinker"}),
    ent("Seat", "g1", {"domain": "build", "kind": "grant"}, [("Roster", "grant")]),
    ent("Seat", "v1", {"domain": "build", "kind": "grant"}, [("Roster", "grant")]),
    ent("Seat", "o1", {"domain": "build", "kind": "observer"}, [("Roster", "veto")]),
    ent("Seat", "t1", {"domain": "build", "kind": "thinker"}, [("Roster", "veto")]),    # wrong kind on a roster
    ent("Seat", "o2", {"domain": "build", "kind": "observer"}, [("Roster", "grant")]),  # wrong kind on a roster
    ent("Seat", "n1", {"domain": "build", "kind": "grant"}),
    ent("Seat", "r1", {"domain": "run", "kind": "thinker"}),
    ent("Seat", "ro1", {"domain": "run", "kind": "observer"}),
    ent("CorpusRoot", "pinned"),
    ent("CorpusObject", "sha-c1", parents=[("CorpusRoot", "pinned")]),
    ent("CorpusObject", "sha-x"),
    # ADR-0040 §3: Run's root is its own pinned set. sha-c1 is in Build's root only, sha-r1 in Run's only.
    ent("CorpusRoot", "run-pinned"),
    ent("CorpusObject", "sha-r1", parents=[("CorpusRoot", "run-pinned")]),
    ent("Workspace", "ws-a1-r7"), ent("Workspace", "ws-other"),
    ent("WorkspaceTarget", "ws-a1-r7/spec.tla", parents=[("Workspace", "ws-a1-r7")]),
    ent("WorkspaceTarget", "ws-other/spec.tla", parents=[("Workspace", "ws-other")]),
    ent("ToolSet", "build-allow"), ent("ToolSet", "run-allow"), ent("ToolSet", "bg-tools"),
    ent("Tool", "tlc@d1", {"digest": "d1"}, [("ToolSet", "build-allow")]),
    ent("Tool", "tlc@d2", {"digest": "d2"}),
    ent("Tool", "search@d3", {"digest": "d3"}, [("ToolSet", "run-allow")]),
    ent("Tool", "valve@d4", {"digest": "d4"}, [("ToolSet", "bg-tools")]),
    ent("Topic", "a1-r7", {"owner": ref("Seat", "a1"), "epoch": EPOCH, "round": ROUND, "sealed": False}),
    ent("Topic", "v1-r7", {"owner": ref("Seat", "v1"), "epoch": EPOCH, "round": ROUND, "sealed": False}),
    ent("Topic", "a1-r7-sealed", {"owner": ref("Seat", "a1"), "epoch": EPOCH, "round": ROUND, "sealed": True}),
    ent("Topic", "a1-e2", {"owner": ref("Seat", "a1"), "epoch": EPOCH - 1, "round": ROUND, "sealed": False}),
    ent("Topic", "r1-r7", {"owner": ref("Seat", "r1"), "epoch": EPOCH, "round": ROUND, "sealed": False}),
    ent("Topic", "o1-r7", {"owner": ref("Seat", "o1"), "epoch": EPOCH, "round": ROUND, "sealed": False}),
    ent("Topic", "ro1-r7", {"owner": ref("Seat", "ro1"), "epoch": EPOCH, "round": ROUND, "sealed": False}),
    ent("Artifact", "art-a1", {"author": ref("Seat", "a1")}),
    ent("Artifact", "art-v1", {"author": ref("Seat", "v1")}),
    ent("Artifact", "art-g1", {"author": ref("Seat", "g1")}),
    ent("ArchiveRecord", "payload-1", {"class": "payload"}),
] + [ent("ArchiveRecord", f"f{i}", {"class": f"F{i}"}) for i in range(1, 7)]

BUILD_ALPHA = ["Read", "Draft", "Invoke", "Emit", "Submit"]
VOTE_ALPHA = ["Read", "Emit", "Vote"]
OBS_ALPHA = ["Read", "Emit"]                    # ADR-0037 §4: an observer seat's Build alphabet
RUN_ALPHA = ["Consult", "Actuate", "Report"]    # ADR-0040 §1
RUN_OBS_ALPHA = ["Consult", "Report"]           # ADR-0043 §2: an observer seat's Run alphabet


def build_ctx(role="author", alphabet=BUILD_ALPHA, inputs=True):
    return {
        "lease": {"alphabet": alphabet, "rulesEpoch": RULES},
        "epoch": EPOCH, "round": ROUND, "roundRole": role,
        "corpusRoot": ref("CorpusRoot", "pinned"),
        "workspace": ref("Workspace", "ws-a1-r7"),
        "toolAllowlist": ref("ToolSet", "build-allow"),
        "inputsInWorkspace": inputs,
    }


def vote_ctx(verdict="grant", vre=RULES):
    return {
        "lease": {"alphabet": VOTE_ALPHA, "rulesEpoch": RULES},
        "epoch": EPOCH, "rulesEpoch": RULES, "verdict": verdict, "voteRulesEpoch": vre,
        "grantRoster": ref("Roster", "grant"), "vetoRoster": ref("Roster", "veto"),
    }


def run_ctx(bg=False, live=True, alphabet=RUN_ALPHA):
    return {
        "lease": {"alphabet": alphabet, "rulesEpoch": RULES},
        "epoch": EPOCH, "round": ROUND,
        "runRoot": ref("CorpusRoot", "run-pinned"),
        "toolAllowlist": ref("ToolSet", "run-allow"),
        "breakGlass": {"quorum": bg, "tools": ref("ToolSet", "bg-tools")},
        "observerLive": live,                   # ADR-0039 §1
    }


def erase_ctx(q):
    return {"erasureQuorum": q}


def case(name, p, a, r, ctx, decision, reason=()):
    rt, rid = r
    return {
        "name": name,
        "request": {
            "principal": f'{NS}Seat::"{p}"',
            "action": f'{NS}Action::"{a}"',
            "resource": f'{NS}{rt}::"{rid}"',
            "context": ctx,
        },
        "entities": ENTITIES,
        "decision": decision,
        "reason": list(reason),
        "num_errors": 0,
    }


C = []
# ---- Build envelopes (ADR-0022 §1)
C += [
    case("B1 read inside the corpus root", "a1", "Read", ("CorpusObject", "sha-c1"), build_ctx(), "allow", ["B1-read-corpus"]),
    case("B1 read outside the corpus root", "a1", "Read", ("CorpusObject", "sha-x"), build_ctx(), "deny"),
    case("B1 read by a Run seat", "r1", "Read", ("CorpusObject", "sha-c1"), build_ctx(), "deny"),
    case("B1 read not in the lease alphabet", "a1", "Read", ("CorpusObject", "sha-c1"), build_ctx(alphabet=["Draft"]), "deny"),
    case("B1 read of an object in Run's root only", "a1", "Read", ("CorpusObject", "sha-r1"), build_ctx(), "deny"),
    case("B2 draft in own workspace", "a1", "Draft", ("WorkspaceTarget", "ws-a1-r7/spec.tla"), build_ctx(), "allow", ["B2-draft-workspace"]),
    case("B2 draft outside own workspace", "a1", "Draft", ("WorkspaceTarget", "ws-other/spec.tla"), build_ctx(), "deny"),
    case("B3 invoke allowlisted, inputs resident", "a1", "Invoke", ("Tool", "tlc@d1"), build_ctx(), "allow", ["B3-invoke-allowlisted"]),
    case("B3 invoke same name, other digest", "a1", "Invoke", ("Tool", "tlc@d2"), build_ctx(), "deny"),
    case("B3 invoke with inputs outside the workspace", "a1", "Invoke", ("Tool", "tlc@d1"), build_ctx(inputs=False), "deny"),
    case("B4 emit to own current topic", "a1", "Emit", ("Topic", "a1-r7"), build_ctx(), "allow", ["B4-emit-own-topic"]),
    case("B4 emit to another principal's topic", "a1", "Emit", ("Topic", "v1-r7"), build_ctx(), "deny"),
    case("B4 emit to a sealed topic", "a1", "Emit", ("Topic", "a1-r7-sealed"), build_ctx(), "deny"),
    case("B4 emit to a topic at a fenced epoch", "a1", "Emit", ("Topic", "a1-e2"), build_ctx(), "deny"),
    case("B5 submit own artifact", "a1", "Submit", ("Artifact", "art-a1"), build_ctx(), "allow", ["B5-submit-own-artifact"]),
    case("B5 submit another's artifact", "a1", "Submit", ("Artifact", "art-v1"), build_ctx(), "deny"),
    case("B6 grant vote from a grant seat", "v1", "Vote", ("Artifact", "art-a1"), vote_ctx(), "allow", ["B6-vote-seated"]),
    case("B6 deny vote from a veto seat", "o1", "Vote", ("Artifact", "art-a1"), vote_ctx("deny"), "allow", ["B6-vote-seated"]),
    case("B6 vote bound to a superseded rules epoch", "v1", "Vote", ("Artifact", "art-a1"), vote_ctx(vre=RULES - 1), "deny"),
    case("B6 vote from an unseated principal", "n1", "Vote", ("Artifact", "art-a1"), vote_ctx("deny"), "deny"),
    case("B6 a thinker seat on the veto roster cannot vote", "t1", "Vote", ("Artifact", "art-a1"), vote_ctx("deny"), "deny"),
    case("B6 an observer seat on the grant roster cannot vote", "o2", "Vote", ("Artifact", "art-a1"), vote_ctx("deny"), "deny"),
]
# ---- ADR-0037 §4: observer seats read and emit, and nothing else
C += [
    case("B1 an observer seat reads the corpus", "o1", "Read", ("CorpusObject", "sha-c1"), build_ctx(alphabet=OBS_ALPHA), "allow", ["B1-read-corpus"]),
    case("B4 an observer seat emits to its own topic", "o1", "Emit", ("Topic", "o1-r7"), build_ctx(alphabet=OBS_ALPHA), "allow", ["B4-emit-own-topic"]),
]
# ---- carve-outs
C += [
    case("B7 author's own grant vote is refused", "g1", "Vote", ("Artifact", "art-g1"), vote_ctx(), "deny", ["B7-author-recused"]),
    case("B8 veto seat cannot grant", "o1", "Vote", ("Artifact", "art-a1"), vote_ctx("grant"), "deny", ["B8-grant-only-from-grant-seat"]),
    case("B9 a voter cannot draft", "a1", "Draft", ("WorkspaceTarget", "ws-a1-r7/spec.tla"), build_ctx(role="voter"), "deny", ["B9-voters-do-not-author"]),
    case("B9 a voter cannot invoke", "a1", "Invoke", ("Tool", "tlc@d1"), build_ctx(role="voter"), "deny", ["B9-voters-do-not-author"]),
    case("B9 a voter cannot submit", "a1", "Submit", ("Artifact", "art-a1"), build_ctx(role="voter"), "deny", ["B9-voters-do-not-author"]),
    # B10: the lease alphabet and workspace would permit each of these; the kind is the only reason.
    case("B10 an observer seat cannot draft", "o1", "Draft", ("WorkspaceTarget", "ws-a1-r7/spec.tla"), build_ctx(), "deny", ["B10-only-thinkers-author"]),
    case("B10 an observer seat cannot invoke", "o1", "Invoke", ("Tool", "tlc@d1"), build_ctx(), "deny", ["B10-only-thinkers-author"]),
    case("B10 an observer seat cannot submit", "o1", "Submit", ("Artifact", "art-a1"), build_ctx(), "deny", ["B10-only-thinkers-author"]),
    case("B10 a grant seat cannot draft", "g1", "Draft", ("WorkspaceTarget", "ws-a1-r7/spec.tla"), build_ctx(), "deny", ["B10-only-thinkers-author"]),
    case("B10 a Run observer seat cannot actuate", "ro1", "Actuate", ("Tool", "search@d3"), run_ctx(), "deny", ["B10-only-thinkers-author"]),
]
# ---- Run (ADR-0040 §1, ADR-0041 §1) and break-glass
C += [
    case("R1 actuate, allowlisted", "r1", "Actuate", ("Tool", "search@d3"), run_ctx(), "allow", ["R1-actuate-allowlisted"]),
    case("R1 actuate by a Build seat", "a1", "Actuate", ("Tool", "search@d3"), run_ctx(), "deny"),
    case("R1 actuate not in the lease alphabet", "r1", "Actuate", ("Tool", "search@d3"), run_ctx(alphabet=["Consult", "Report"]), "deny"),
    case("R2 report to own topic", "r1", "Report", ("Topic", "r1-r7"), run_ctx(), "allow", ["R2-report-own-topic"]),
    case("R2 report to another principal's topic", "r1", "Report", ("Topic", "ro1-r7"), run_ctx(), "deny"),
    case("X1 break-glass tool without a quorum", "r1", "Actuate", ("Tool", "valve@d4"), run_ctx(bg=False), "deny"),
    case("X1 break-glass tool under a quorum", "r1", "Actuate", ("Tool", "valve@d4"), run_ctx(bg=True), "allow", ["X1-break-glass"]),
    case("X1 break-glass does not reach a tool outside its envelope", "r1", "Actuate", ("Tool", "tlc@d2"), run_ctx(bg=True), "deny"),
    # ADR-0040 §1, ADR-0041 §1: Consult is scoped to the pinned Run root, and to nothing else.
    case("R4 consult inside the Run root", "r1", "Consult", ("CorpusObject", "sha-r1"), run_ctx(), "allow", ["R4-consult-pinned"]),
    case("R4 consult outside the Run root", "r1", "Consult", ("CorpusObject", "sha-x"), run_ctx(), "deny"),
    case("R4 consult of an object in Build's root only", "r1", "Consult", ("CorpusObject", "sha-c1"), run_ctx(), "deny"),
    case("R4 consult by a Build seat", "a1", "Consult", ("CorpusObject", "sha-r1"), run_ctx(), "deny"),
    case("R4 consult not in the lease alphabet", "r1", "Consult", ("CorpusObject", "sha-r1"), run_ctx(alphabet=["Actuate", "Report"]), "deny"),
    case("R4 a Run observer seat consults", "ro1", "Consult", ("CorpusObject", "sha-r1"), run_ctx(alphabet=RUN_OBS_ALPHA), "allow", ["R4-consult-pinned"]),
    # ADR-0041 §3: break-glass widens what may be actuated. It does not widen the Run root.
    case("X1 break-glass does not reach Consult", "r1", "Consult", ("CorpusObject", "sha-x"), run_ctx(bg=True), "deny"),
    # ADR-0039 §2: the allowlist and alphabet would permit each of these; a dead cell Observer is the only reason.
    case("R3 actuate with no live cell Observer", "r1", "Actuate", ("Tool", "search@d3"), run_ctx(live=False), "deny", ["R3-observer-live"]),
    case("R3 report with no live cell Observer", "r1", "Report", ("Topic", "r1-r7"), run_ctx(live=False), "deny", ["R3-observer-live"]),
    case("R3 break-glass under a quorum with no live cell Observer", "r1", "Actuate", ("Tool", "valve@d4"), run_ctx(bg=True, live=False), "deny", ["R3-observer-live"]),
    # An observer seat's own report (its heartbeat) is not coupled: it is what makes the Thinker live.
    case("R3 does not couple a Run observer seat's own report", "ro1", "Report", ("Topic", "ro1-r7"), run_ctx(live=False, alphabet=RUN_OBS_ALPHA), "allow", ["R2-report-own-topic"]),
    # ADR-0041 §2: Consult is not an effect and is not coupled. A Thinker whose Observer lags can read and cannot act.
    case("R3 does not couple Consult", "r1", "Consult", ("CorpusObject", "sha-r1"), run_ctx(live=False), "allow", ["R4-consult-pinned"]),
]
# ---- erasure and the forensic floor
C += [
    case("X2 erase a payload at genesis (no erasure roster)", "v1", "Erase", ("ArchiveRecord", "payload-1"), erase_ctx(False), "deny"),
    case("X2 erase a payload under an erasure quorum", "v1", "Erase", ("ArchiveRecord", "payload-1"), erase_ctx(True), "allow", ["X2-erasure"]),
]
C += [
    case(f"F erase forensic class F{i} under a quorum", "v1", "Erase", ("ArchiveRecord", f"f{i}"), erase_ctx(True), "deny", ["F-forensic-classes"])
    for i in range(1, 7)
]

with open("genesis-tests.json", "w") as f:
    json.dump(C, f, indent=1)
print(f"{len(C)} cases")
