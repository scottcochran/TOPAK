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
    # a1 authors this round and also holds a grant seat, so recusal has something to refuse.
    ent("Seat", "a1", {"domain": "build"}, [("Roster", "grant")]),
    ent("Seat", "v1", {"domain": "build"}, [("Roster", "grant")]),
    ent("Seat", "o1", {"domain": "build"}, [("Roster", "veto")]),
    ent("Seat", "n1", {"domain": "build"}),
    ent("Seat", "r1", {"domain": "run"}),
    ent("CorpusRoot", "pinned"),
    ent("CorpusObject", "sha-c1", parents=[("CorpusRoot", "pinned")]),
    ent("CorpusObject", "sha-x"),
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
    ent("Artifact", "art-a1", {"author": ref("Seat", "a1")}),
    ent("Artifact", "art-v1", {"author": ref("Seat", "v1")}),
    ent("ArchiveRecord", "payload-1", {"class": "payload"}),
] + [ent("ArchiveRecord", f"f{i}", {"class": f"F{i}"}) for i in range(1, 7)]

BUILD_ALPHA = ["Read", "Draft", "Invoke", "Emit", "Submit"]
VOTE_ALPHA = ["Read", "Emit", "Vote"]


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


def run_ctx(bg=False):
    return {
        "lease": {"alphabet": ["RunInvoke", "RunEmit"], "rulesEpoch": RULES},
        "epoch": EPOCH, "round": ROUND,
        "corpusRoot": ref("CorpusRoot", "pinned"),
        "toolAllowlist": ref("ToolSet", "run-allow"),
        "breakGlass": {"quorum": bg, "tools": ref("ToolSet", "bg-tools")},
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
]
# ---- carve-outs
C += [
    case("B7 author's own grant vote is refused", "a1", "Vote", ("Artifact", "art-a1"), vote_ctx(), "deny", ["B7-author-recused"]),
    case("B8 veto seat cannot grant", "o1", "Vote", ("Artifact", "art-a1"), vote_ctx("grant"), "deny", ["B8-grant-only-from-grant-seat"]),
    case("B9 a voter cannot draft", "a1", "Draft", ("WorkspaceTarget", "ws-a1-r7/spec.tla"), build_ctx(role="voter"), "deny", ["B9-voters-do-not-author"]),
    case("B9 a voter cannot invoke", "a1", "Invoke", ("Tool", "tlc@d1"), build_ctx(role="voter"), "deny", ["B9-voters-do-not-author"]),
    case("B9 a voter cannot submit", "a1", "Submit", ("Artifact", "art-a1"), build_ctx(role="voter"), "deny", ["B9-voters-do-not-author"]),
]
# ---- Run (provisional) and break-glass
C += [
    case("R1 run invoke, allowlisted", "r1", "RunInvoke", ("Tool", "search@d3"), run_ctx(), "allow", ["R1-run-invoke-allowlisted"]),
    case("R1 run invoke by a Build seat", "a1", "RunInvoke", ("Tool", "search@d3"), run_ctx(), "deny"),
    case("R2 run emit to own topic", "r1", "RunEmit", ("Topic", "r1-r7"), run_ctx(), "allow", ["R2-run-emit-own-topic"]),
    case("X1 break-glass tool without a quorum", "r1", "RunInvoke", ("Tool", "valve@d4"), run_ctx(bg=False), "deny"),
    case("X1 break-glass tool under a quorum", "r1", "RunInvoke", ("Tool", "valve@d4"), run_ctx(bg=True), "allow", ["X1-break-glass"]),
    case("X1 break-glass does not reach a tool outside its envelope", "r1", "RunInvoke", ("Tool", "tlc@d2"), run_ctx(bg=True), "deny"),
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
