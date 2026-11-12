---
id: 2017-CLD-S3-PLAYBOOK-TYPO
title: Amazon S3 us-east-1, 28 February 2017 — a playbook command whose input removed more capacity than intended
kind: incident
date: 2017-02-28
sector: cloud
setting: Amazon Simple Storage Service (S3), the US-EAST-1 region (northern Virginia), operated by Amazon Web Services
concerns: [authority, actuation, interface-types, interlock, cascading-failure, monitoring, rollback]
rules_at_time:
  - document: AWS S3 operational playbook (internal; as described in AWS's post-event summary)
    clause: capacity removal from an S3 subsystem
    paraphrase: an authorized S3 team member could run an established playbook command that removes a set of servers from a subsystem; the inputs chose how many, and the tool removed capacity as fast as it was asked to
  - document: AWS post-event summary, safeguards added afterwards
    clause: capacity-removal tool
    paraphrase: none of the later checks (removal rate, a floor at each subsystem's minimum required capacity) were in the tool at the time; AWS says it added them after the event
analogue:
  - record: ADR-0040
    clause: "§5"
    note: Run's alphabet is finite in variants, not in instances; a tool's arguments are parameters of one variant, so the floor sees "remove capacity", not how much
  - record: ADR-0062
    clause: "§4"
    note: '"Without an extent a count bounds nothing": every entry declares how far one act runs, and an entry with none does not load. Stated for vehicles in the command-chain overlay (Proposed), not for Run tools'
  - record: ADR-0050
    clause: "§4"
    note: the operator's control alphabet (Regrant, Renew, AttestGates, EndRound, Revoke, FenceEpoch) has no variant for work on the infrastructure under the mechanism
  - record: ADR-0038
    clause: "§4"
    note: placement is stated for Observer seats sharing a device; the status channel's dependence on the service it reports on is not covered
actors:
  - party: Authorized S3 team member
    role: operator
    fault: honest-error
    note: AWS's summary says one input to an established playbook command "was entered incorrectly"; it names no individual
  - party: Capacity-removal tool
    role: automation
    fault: none-alleged
    note: did what it was told; AWS added a rate limit and a minimum-capacity check to it afterwards
  - party: S3 index and placement subsystems
    role: automation
    fault: crash
    note: lost enough capacity to need a full restart, which AWS had not done in its larger regions for many years
  - party: AWS Service Health Dashboard administration console
    role: monitor
    fault: omission
    note: depended on S3, so individual service status could not be updated until 11:37 AM PST
  - party: Amazon Web Services
    role: investigator
    fault: none-alleged
    note: published the post-event summary
detection:
  means: [public, operator]
  latency: minutes
trace:
  - step: outside:operator-infrastructure-command
    at: 9:37 AM PST
    note: the S3 team was debugging a billing system that was slower than expected; the command was meant to remove a small number of servers from a subsystem the billing process used
  - step: outside:argument-selects-larger-set
    at: 9:37 AM PST
    note: one input was entered incorrectly, and a larger set of servers was removed, including servers of two other subsystems
  - step: outside:capacity-below-subsystem-minimum
    at: 9:37 AM PST onward
    note: the index subsystem (metadata and location of every object in the region, needed for GET, LIST, PUT and DELETE) and the placement subsystem (allocates storage for PUT, depends on the index) both needed a full restart; S3 could not serve requests while they restarted
  - step: outside:dependent-services-fail
    at: same period
    note: the S3 console, new EC2 instance launches, EBS volumes needing data from an S3 snapshot, and AWS Lambda in the region were affected
  - step: outside:status-channel-shares-failure-domain
    at: until 11:37 AM PST
    note: the Service Health Dashboard console depended on S3; AWS used its Twitter feed and a banner on the dashboard
  - step: outside:subsystem-restart-and-integrity-check
    at: 12:26 PM to 1:54 PM PST
    note: index able to serve GET, LIST and DELETE at 12:26; fully recovered at 1:18; placement recovered and S3 normal at 1:54
counterfactual:
  by: AWS's own safeguards, read as a lease with a count and an entry with an extent
  trace:
    - step: Grant
      at: before the command
      note: Intent.tla's lease under an intent, with a count of effects
    - step: Effect
      at: 9:37 AM PST
      note: one removal within the count; the count bounds commands, not servers
    - step: outside:extent-measured-against-subsystem-minimum
      at: 9:37 AM PST
      note: AWS's added check, refusing a removal that would take any subsystem below its minimum required capacity; it reads live state, which ADR-0040 §1 makes an Actuate and which no module has as a guard
    - step: RefuseEffect
      at: after the count is spent
      note: AWS's other added check, removing capacity more slowly, is a count per period
  holds: [EveryEffectHasALease]
outcome:
  by: Amazon Web Services (post-event summary)
  date: "2017"
  summary: >-
    AWS attributed the event to a playbook command run by an authorized team member in which one input was entered
    incorrectly, removing a larger set of servers than intended, including servers of the index and placement
    subsystems. Both needed a full restart. AWS said it had not fully restarted them in its larger regions for many
    years and that the restart and its safety checks took longer than expected. S3 was operating normally at 1:54 PM
    PST.
  aftermath: >-
    AWS modified the capacity-removal tool to remove capacity more slowly and to refuse a removal that would take any
    subsystem below its minimum required capacity; began auditing other operational tools for similar checks; worked
    on the recovery time of key S3 subsystems; brought forward the partitioning of the index subsystem into cells; and
    moved the Service Health Dashboard's administration console to run across multiple regions.
  effect_reversed: partial
model:
  modules: [Intent, Operators, proposed:ExtentGuard]
  properties: [EveryEffectHasALease]
  mutations: [M_NOCOUNT]
  records: [ADR-0040, ADR-0062, ADR-0050, ADR-0038, ADR-0045, ADR-0022]
  findings: [CR-34, TM7]
  fault_class: an honest operator's mistyped argument to an allowlisted command; the guard on how far one act runs was absent
sources:
  - https://aws.amazon.com/message/41926/
  - https://www.theregister.com/2017/03/01/aws_s3_outage/
verified: 2026-11-12
---

## Summary

At 9:37 AM PST on 28 February 2017, an authorized member of the S3 team ran a command from an established playbook
to remove a small number of servers from an S3 subsystem used by the billing process, which was running slower than
expected. AWS's summary says one of the command's inputs was entered incorrectly, and a larger set of servers was
removed. Among them were servers supporting two other subsystems: the index subsystem, which holds the metadata and
location of every S3 object in the region, and the placement subsystem, which allocates storage for new objects and
depends on the index.

Both needed a full restart, and S3 could not serve requests while they restarted. Other services in the region that
depend on S3 were affected: the S3 console, launches of new EC2 instances, EBS volumes needing data from an S3
snapshot, and Lambda. The Register reported that sites and services storing data in S3 failed, and that monitoring
sites went down with them. The Service Health Dashboard's administration console depended on S3, so until 11:37 AM
AWS could not update individual services' status there and posted updates on Twitter and in a banner.

The index subsystem could serve GET, LIST and DELETE at 12:26 PM and was fully recovered at 1:18 PM. The placement
subsystem finished recovering at 1:54 PM, and S3 was operating normally.

## Defensive position

**AWS's summary** gives the operator's context and the reasons the recovery took as long as it did:

- The person was authorized and was using an established playbook. AWS describes the cause as one incorrectly
  entered input, not as a departure from procedure.
- The subsystems were "designed to support the removal or failure of significant capacity with little or no
  customer impact". What took time was the full restart,
  which AWS had not done in its larger regions for many years while the regions grew, and the safety checks on the
  integrity of the metadata.
- AWS states it builds its systems on the assumption that things will occasionally fail.

## Adversarial position

No party on record alleged misconduct. The case against the design is AWS's own, by the changes it made:

- The tool let one command remove capacity faster and further than was safe. AWS called this "too quickly" and
  changed both the rate and the floor.
- The status channel shared the failure it was meant to report.
- The Register noted that customers are encouraged to spread applications across regions and that many, for cost
  and complexity, had not, so a single region's storage took down a wide set of services.

## Outcome

AWS published a post-event summary; the page carries no publication date. It made six changes: a slower capacity-removal
tool; a check that refuses a removal taking any subsystem below its minimum required capacity; an audit of other
operational tools for similar checks; work on recovery time for key S3 subsystems; earlier partitioning of the index
subsystem into cells; and a multi-region administration console for the Service Health Dashboard. AWS apologised to
its customers. S3 was back to normal a little over four hours after the command, and some services that had built up
backlogs needed more time to recover fully.

## Analysis

**The command was allowlisted, and the argument was the hazard.** Read against TOPAK, the playbook is an allowlisted
entry and the operator held a seat that reached it. The floor would have admitted the command whatever its input,
because ADR-0040 §5 (carrying ADR-0022 §4) decides `bundle ⊑ floor` over variants with symbolic parameters. That is
a deliberate choice, and it means the floor never sees "how many servers". A bundle rule can bound an argument it is
given, but "below the subsystem's minimum" is a fact about live state, and ADR-0040 §1 makes any read of live state
an `Actuate`. ADR-0030 §4 lets history into schema S only as a fixed set of attributes the mechanism computes;
remaining capacity is not one of them, and should not be, since it would put the target system's state into the
mechanism's.

**The corpus already says the principle, in the wrong place.** ADR-0062 §4, for vehicles in the command-chain overlay
(Proposed), says "without an extent a count bounds nothing" and refuses to load an entry with no extent. Intent.tla
counts effects (`Counted`, `RefuseEffect`; `M_NOCOUNT` breaks `EveryEffectHasALease`), and AWS's first fix, a slower
removal, is exactly a count per period. But a count counts admits: one `Effect` that names a thousand servers is one
effect. AWS's second fix is an extent, measured. Nothing in ADR-0040 or ADR-0049 asks a Run entry to declare one, and
ADR-0062 §4 itself notes that an extent is a declaration that nothing checks. The suggestion is an entry part,
carried from ADR-0062 §4 into ADR-0049 for Run, with the tool host (not the Thinker or operator) measuring it. That
is `proposed:ExtentGuard`: an entry's extent is checked by the host against a measurement, the act is refused when
the measurement would pass the floor, and a mutation that drops the check breaks a property bounding effects by
reach rather than by count.

**Who held the seat.** ADR-0050 makes an operator a principal, but its control alphabet is about leases. The command
here is work on infrastructure, which in TOPAK would be an `Actuate` by some seat. CR-34 calls the operator channel
"the untyped half of the control-plane alphabet", and TM7 (an insider with a key) says a wrong act by a person in a
seat "is recorded and not prevented". This was not an insider acting against the system; it is the honest-error case
of the same row. TOPAK would attribute the act and log it, and would not have stopped it.

**"Failure can only subtract" is about authority.** ADR-0045 §2 admits a component to the trusted base if its
failure produces only subtractions: a denial, an ended round, a stalled promotion. Removing servers subtracts
capacity, and under that test it is harmless. The corpus has no vocabulary in which an effect that removes the
system's own capacity is worse than one that adds a file. That is where the pattern stops: TOPAK bounds who may act
and through what, not what the act does to the availability of the thing acted on.

**The status channel.** ADR-0038 §4 keeps Observer seats off the device of the Thinker they watch, on fault-domain
grounds. The dashboard's console here was not an Observer but a reporting path, and it shared a service dependency,
not a device. The step `outside:status-channel-shares-failure-domain` is a placement question the corpus asks only of
Observers.

**Outside steps, the to-do list.** `operator-infrastructure-command` (no seat or variant for it),
`argument-selects-larger-set` and `capacity-below-subsystem-minimum` (no extent on a Run entry),
`dependent-services-fail` and `subsystem-restart-and-integrity-check` (outside the pattern by design), and
`status-channel-shares-failure-domain`.
