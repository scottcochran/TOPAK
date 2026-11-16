---
id: 2021-NET-FACEBOOK-BACKBONE
title: Facebook, 4 October 2021 — a capacity-assessment command, an audit that did not stop it, and DNS that withdrew itself
kind: incident
date: 2021-10-04
sector: networking
setting: Facebook's (now Meta's) global backbone, its edge DNS servers and its data centres; AS32934
concerns: [configuration-change, interlock, monitoring, emergency-path, cascading-failure, rollback]
rules_at_time:
  - document: Meta's command audit, as described in its post-mortem of 5 October 2021
    clause: audit of backbone maintenance commands
    paraphrase: commands of this kind are audited before they run, and the audit is meant to stop one that would cause harm
  - document: Meta's edge DNS design, as described in the same post-mortem
    clause: health-based BGP advertisement
    paraphrase: a DNS location advertises its addresses only while it can reach the data centres, and withdraws them when it cannot, so that traffic goes to a healthy location
analogue:
  - record: ADR-0062
    clause: "§5"
    note: a vehicle that stops hearing its plane loses its lease at once; the same fail-closed rule, applied to every edge at once, is what withdrew Facebook's DNS
  - record: ADR-0052
    clause: "§1, §6, §7"
    note: the emergency seat's key "does not depend on single sign-on", because a path that needs the provider fails with it; the path is drilled; a person acting outside the mechanism is not covered
  - record: ADR-0030
    clause: "§1"
    note: a floor evaluation error is a deny; a forbid that errors and is skipped is the hazard this clause closes
  - record: ADR-0050
    clause: "§4 and Consequences"
    note: a fleet fence leaves nobody able to regrant, and recovery is a quorum's work, "the safe direction and ... the slow one"
actors:
  - party: Facebook network engineering
    role: operator
    fault: honest-error
    note: Meta's post-mortem calls it "an error of our own making"; the command was issued during routine maintenance
  - party: Facebook's command audit tool
    role: safety-system
    fault: byzantine
    note: "a bug in that audit tool prevented it from properly stopping the command"
  - party: Facebook's edge DNS servers
    role: monitor
    fault: honest
    note: withdrew their BGP advertisements as designed when they could not reach the data centres
  - party: Recursive resolvers (Cloudflare 1.1.1.1 and others)
    role: peer
    fault: none-alleged
    note: returned SERVFAIL; 1.1.1.1 saw about 30 times its usual query load from retries
detection:
  means: [automated-monitor, peer, customer]
  latency: minutes
trace:
  - step: Actuate
    at: before 15:40 UTC
    note: a command "with the intention to assess the availability of global backbone capacity" takes down every backbone connection. Typed as an assessment, its effect was a disconnection
  - step: Decide
    at: before 15:40 UTC
    note: the command audit admits it; Meta says a bug kept it from "properly stopping the command" and does not say what the bug was
  - step: GoAlone
    at: about 15:40 UTC
    note: every DNS location, unable to reach the data centres, declares itself unhealthy and withdraws its prefixes. Cloudflare sees a peak of routing changes from AS32934
  - step: outside:resolvers-fail-and-retry
    at: 15:50 to 15:58 UTC
    note: facebook.com stops resolving on 1.1.1.1; Cloudflare finds the DNS prefixes 185.89.218.0/23 and 129.134.30.0/23 not in the table; SERVFAIL is cached worldwide
  - step: outside:diagnostic-tools-depend-on-dns
    at: from 15:40 UTC
    note: the loss of DNS "broke many of the internal tools"; primary and out-of-band network access were both down
  - step: outside:physical-access-to-data-centre
    at: hours
    note: engineers were sent on site; the facilities and hardware are built to be "hard to get into" and hard to modify; secure-access protocols took time
  - step: outside:staged-restoration-of-load
    at: about 21:00 to 21:28 UTC
    note: BGP activity from AS32934 resumes at about 21:00; DNS works on 1.1.1.1 from 21:20; services are brought back in steps for fear of power and cache surges
counterfactual:
  by: an emergency seating whose activation and calls travel on a channel that does not depend on the backbone or on DNS, drilled with the backbone down
  trace:
    - step: Approve
      at: minutes after 15:40
      note: the break-glass roster's quorum approves; the approvals have to reach the mechanism, which the model assumes and Facebook's network could not provide
    - step: Activate
      at: minutes after
      note: one person seated for one round, with an envelope that holds a rollback of the backbone change
    - step: EmCall
      at: minutes after
      note: uncoupled from any Observer, so a dead monitoring path cannot stop it
    - step: outside:independent-control-channel
      at: throughout
      note: no module has a channel whose availability is independent of the network the seat is repairing
  holds: [EmergencyNeverCoupled, EmergencyCallsWithoutObserver, EmergencyLeaseHasARosterQuorum]
outcome:
  by: Meta (Facebook engineering post-mortems of 4 and 5 October 2021); no regulator's finding in the sources read
  date: 2021-10-05
  summary: >-
    Meta first attributed the outage to "configuration changes on the backbone routers" and said there was no
    malicious activity and no evidence that user data was compromised. Its second post said a maintenance command
    meant to assess backbone capacity "unintentionally took down all the connections in our backbone network", that
    its systems "are designed to audit commands like these" but a bug in the audit tool kept it from stopping this
    one, that its DNS servers then withdrew their advertisements by design, and that the loss of DNS broke the
    internal tools engineers would have used. Recovery needed people on site, slowed by the security of the
    facilities. Cloudflare's measurements put the withdrawal at about 15:40 UTC and DNS working again at about 21:28.
  aftermath: >-
    Meta said it had run "storm" drills that take a service, data centre or region offline, had never simulated a
    global backbone outage, and would look for ways to. Its author said he believed the trade of everyday security
    against slower recovery from a rare event "is worth it".
  effect_reversed: partial
model:
  modules: [Alone, Emergency, Emergency_live, FloorComposition, Operators, Observers, proposed:RecoveryPath, proposed:SubtractionReach]
  properties: [AlonePermitsNothing, EmergencyNeverCoupled, FloorErrorIsDeny, AdmitImpliesFloorPermit, ReachIsBounded]
  mutations: [M_ERR, M_REACH]
  records: [ADR-0062, ADR-0052, ADR-0030, ADR-0050, ADR-0049, ADR-0038, ADR-0045]
  findings: [TM6, CR-17, CR-29, CR-37]
  fault_class: an honest operator's command passed by a faulty interlock; correct fail-closed health checks on every node withdrew together; the repair path ran over what had failed
sources:
  - https://engineering.fb.com/2021/10/05/networking-traffic/outage-details/
  - https://engineering.fb.com/2021/10/04/networking-traffic/outage/
  - https://blog.cloudflare.com/october-2021-facebook-outage/
verified: 2026-11-12
---

## Summary

On 4 October 2021, during routine maintenance of Facebook's backbone, a command was issued "with the intention to
assess the availability of global backbone capacity". Meta says it "unintentionally took down all the connections in
our backbone network". Meta's systems audit commands of this kind; a bug in the audit tool "prevented it from
properly stopping the command".

Facebook's authoritative DNS servers advertise their addresses by BGP and withdraw the advertisements when they
cannot reach the data centres. With the backbone down, every location did so. Cloudflare saw a peak of routing
changes from AS32934 at about 15:40 UTC; facebook.com stopped resolving on 1.1.1.1 at about 15:50; at 15:58 it found
the DNS prefixes 185.89.218.0/23 and 129.134.30.0/23 gone from the routing table. Resolvers returned SERVFAIL, and
retries drove 1.1.1.1 to about 30 times its usual load.

The loss of DNS broke many of Meta's internal tools. Primary and out-of-band network access were both down, so
engineers went to the data centres, which are built to be "hard to get into", with hardware "difficult to modify
even when you have physical access". BGP activity resumed at about 21:00 UTC; facebook.com resolved again on 1.1.1.1
at 21:20, and Cloudflare judged Facebook reconnected at 21:28. Meta restored load in steps, citing power swings of
"tens of megawatts" at individual data centres.

## Defensive position

**Meta's case** (its 5 October post-mortem):

- The command was routine maintenance, and the audit that should have stopped it exists; the failure was a bug in it.
- The DNS withdrawal is a designed health behaviour: a location that cannot reach the data centres should not
  attract traffic.
- The physical and system security that slowed recovery protects the network every day. "I believe a tradeoff like
  this is worth it."
- Storm drills had prepared the team to bring load back without overloading power and caches.
- There was "no malicious activity" and no evidence that user data was compromised.

## Adversarial position

No regulator, court or claimant on record in the sources read. What stands against the design is in Meta's own
account and Cloudflare's measurements:

- **Meta** concedes the outage was "an error of our own making", that the audit failed, and that it had never
  drilled a global backbone outage.
- **Meta** also concedes that the tools for diagnosis depended on the DNS that had gone, and that out-of-band access
  was down with the backbone.
- **Cloudflare** records the cost outside Facebook: SERVFAIL cached by resolvers worldwide, 30 times the usual query
  load on 1.1.1.1, and traffic shifting to other platforms.

## Outcome

Meta's two posts are the finding of record; nothing in the sources reports a regulator's review. Meta named no
person and gave no clock times; Cloudflare's timeline puts the outage at about six hours. Meta said it would look
for ways to simulate a global backbone outage. Service was restored; the hours without it were not.

## Analysis

**Three of the four themes in one episode.** A command promoted into effect with no staged step; a monitor whose own
action made the outage total; and an emergency path that ran over the thing that had failed.

**The command.** It was meant to read capacity and it disconnected the backbone. ToO §2.9, as ADR-0065 §3 quotes it,
already types a read of live state as an `Actuate` "because the request itself leaves the membrane", so TOPAK would
not have admitted it as a harmless query. But what an entry does is largely
declared: ADR-0049 §4 marks its `purpose` and `channel.kind` claimed, and ADR-0066 §1 says of effect classes that "an
irreversible effect declared reversible is seen by nothing here". A command declared as an assessment that
disconnects everything passes every check the corpus has.

**The audit.** Meta does not say what the bug was. If the audit errored and skipped its check, that is the hazard
ADR-0030 §1 closes and `FloorComposition` proves: `FloorErrorIsDeny`, which `M_ERR` (the engine's decision taken
despite an error) breaks. If the audit's rule was simply wrong, `AdmitImpliesFloorPermit` holds and the command is
admitted anyway. The floor checks a typed request against entries; it has no model of what a backbone command does.

**The DNS withdrawal is `GoAlone`, at every node at once.** ADR-0062 §5 says a vehicle that stops hearing its plane
loses its lease at once; `Alone` proves `AlonePermitsNothing`. That is the right rule for one vehicle, and it is
Facebook's rule for one DNS location. The incident is what it does when the partition is at the centre: every edge
is alone together, and the system stops. TM6 names this for a mesh split into pieces too small: it "admits nothing,
and every vehicle is alone". The corpus treats that as the safe residual. It is safe; it is also a total outage, and
no property bounds how many cells one central failure can make alone. `Observers` has the shape of the missing
property, `ReachIsBounded` (a cell Observer's finding reaches only its cell; `M_REACH` breaks it), but it bounds
whom a monitor may name, not how many monitors one shared dependency can trip. That is `proposed:SubtractionReach`.

**ADR-0045's line does not reach this.** A component "whose failure can only subtract" is delegated and "needs no
proof, no key and no quorum". Every failure here was a subtraction, so the episode sits in the safe class, and every
safety theorem holds throughout. The liveness work (CR-37) has no module about recovery from a fleet-wide stop.

**The emergency path.** ADR-0052 §1 already saw half of this: the emergency key "does not depend on single sign-on"
because "an emergency path that needs the identity provider fails when the provider does". The same argument applies
to the network, and no record makes it. Activation needs the roster's approvals to reach the mechanism; the
counterfactual's `Approve` and `Activate` assume they arrive. `Emergency_live` proves `EmergencyNeverCoupled`, that a
live seat's calls do not wait on an Observer; its own header notes that "an activation that waited for a live
Observer would pass every check here". Nothing checks that activation is reachable when the network is down. ADR-0052
§6 requires a drill per domain per epoch, and a drill run with the network up proves the roster and the keys, not
this path. Meta had drills, and none of them took out the backbone. ADR-0052 §7 leaves "a person acting outside the
mechanism" out of scope. Getting into a data centre is exactly that, and it is how Facebook recovered.

**Recovery is a quorum's work.** ADR-0050 says a fleet fence "leaves nobody able to regrant", and that recovery is
"the safe direction and ... the slow one, at the moment a deployment most wants to be fast". Facebook is a measured
instance of that sentence, with physical security in the quorum's place.

**What it suggests.** `proposed:RecoveryPath`: the emergency seating declares the channel its approvals and calls
travel on, a trusted-base row for that channel with its failure direction, and a property that activation stays
enabled under the failure of any component the seat may be asked to repair. The drill obligation of ADR-0052 §6
should name the failure the drill assumes. `proposed:SubtractionReach` would bound how many cells a single fault
can stop.
