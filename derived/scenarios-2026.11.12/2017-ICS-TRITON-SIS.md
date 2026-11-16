---
id: 2017-ICS-TRITON-SIS
title: Triton/TRISIS, 2017 — the safety instrumented system as the target, and a payload fault that tripped the plant safe
kind: incident
date: 2017-08
sector: industrial-control
setting: Schneider Electric Triconex safety instrumented system (3008 processor modules) and its engineering workstation, at a petrochemical facility in the Middle East
concerns: [interlock, containment, deployment, identity, monitoring, configuration-change, actuation]
rules_at_time:
  - document: IEC 61508 (as Dragos summarises it)
    clause: Safety Integrity Level design
    paraphrase: safety controller hardware and software are designed and built to the SIL standards, with error-correcting memory, redundant components and a design that favours failing safe over continuing operation
  - document: Schneider Electric deployment recommendations for Triconex (as Dragos relays them)
    clause: network isolation, key switch
    paraphrase: safety systems on isolated networks; controllers in locked cabinets and never left in Program mode; TriStation terminals connected to no network but the safety network; an operator-station alarm whenever the key switch is in Program mode
analogue:
  - record: ADR-0030
    clause: "§3"
    note: the floor is linked into the mechanism, "no process, no socket, no fetch"; its inputs are written only by the typed lift and the issued rules; nothing it evaluates depends on bundle output
  - record: ADR-0045
    clause: "§2, §5"
    note: a component enters the trusted base if its failure can only subtract; the verified object is the specification, and what runs it is a row
  - record: ADR-0024
    clause: "§2, §4, §7"
    note: a change crosses into service by a unanimous promotion that gates enable and that lasts one round
  - record: ADR-0068
    clause: "§2 (T-0068-1, T-0068-8)"
    note: the admit path and the effector interlock are trust roots; if either fails, anything requested may reach an actuator
actors:
  - party: Unidentified intruders; the US Treasury in 2020 designated TsNIIKhM as responsible for building the tools
    role: attacker
    fault: byzantine
  - party: Triconex safety controllers
    role: safety-system
    fault: honest
    note: some entered a failed safe state when application code on redundant processors failed a validation check, shutting the process down
  - party: The facility's operator (not named in these sources)
    role: operator
    fault: contested
    note: Dragos reports the controller's physical key switch was in Program mode during operation
  - party: Schneider Electric
    role: vendor
    fault: none-alleged
    note: Dragos found the malware used "no inherent vulnerability" in its products and called the vendor a victim
  - party: Mandiant (FireEye) and Dragos
    role: investigator
    fault: none-alleged
  - party: US Department of the Treasury (OFAC)
    role: regulator
    fault: none-alleged
detection:
  means: [interlock, investigation]
  latency: months
trace:
  - step: outside:engineering-workstation-reached
    at: before the trip
    note: remote access to an SIS engineering workstation; TRITON deployed as trilog.exe, named after the Triconex Trilog application
  - step: outside:key-switch-left-in-program
    at: during operation
    note: per Dragos; in Run mode "arbitrary changes in logic are not possible"
  - step: BundleWrite
    at: during the intrusion
    note: TRISIS uploads binaries that replace logic on the safety controller, from a host able to communicate with it. In FloorComposition a write path from outside into what the floor reads exists only under M_WRITE
  - step: outside:payload-fails-redundancy-check
    at: August 2017 (per Treasury)
    note: application code differs between redundant processing units and fails the controllers' validation check
  - step: Decide
    at: same
    note: the controllers decide as an error decides in FloorComposition, as a deny; FloorErrorIsDeny holds
  - step: outside:process-trips-safe
    at: same
    note: some SIS controllers enter a failed safe state and shut the industrial process down; the owner opens an investigation
  - step: outside:malware-found-and-reported
    at: mid-November to 14 December 2017
    note: Dragos finds TRISIS in mid-November and notifies DHS, DOE and E-ISAC; Mandiant publishes on 14 December
  - step: outside:attribution-by-sanction
    at: 23 October 2020
    note: OFAC designates TsNIIKhM under CAATSA section 224
outcome:
  by: Mandiant (FireEye); Dragos; US Department of the Treasury (OFAC)
  date: 2020-10-23
  summary: >-
    Mandiant reported that an attacker "gained remote access to an SIS engineering workstation and deployed the TRITON
    attack framework to reprogram the SIS controllers", that some controllers "entered a failed safe state, which
    automatically shutdown the industrial process", and assessed with moderate confidence that the attacker
    "inadvertently shutdown operations while developing the ability to cause physical damage", sponsored by a nation
    state. Dragos found the malware targeted Triconex 3008 processor modules, leveraged "no inherent vulnerability" in
    Schneider products, and worked because the key switch was in Program mode; it judged loss of life possible "but
    not easily nor likely directly". On 23 October 2020 Treasury designated TsNIIKhM, "a Russian government-controlled
    research institution", as "responsible for building customized tools that enabled the attack", and said the
    attackers had been reported scanning US facilities and, in 2019, at least 20 US electric utilities.
  aftermath: >-
    Mandiant recommended segregating safety networks from process control and information networks, unidirectional
    gateways for applications that need SIS data, strict access control and whitelisting on any host that can reach
    the SIS, and keys in Program mode only during scheduled programming, with the key state audited. Dragos recommended
    program-download detection and keys in Run or Remote. Neither publication names the facility.
  effect_reversed: not-applicable
model:
  modules: [FloorComposition, FloorRouting, RulesFloorNV_rev5, Release, proposed:FloorHostCompromise]
  properties: [BundleCannotWriteFloorInputs, FloorErrorIsDeny, AdmitImpliesFloorPermit, NoWideningWithoutIssuance, P1_Unanimity, IrreversibleIsAPersons]
  mutations: [M_WRITE, M_FAILOPEN, M_ERR]
  records: [ADR-0030, ADR-0045, ADR-0024, ADR-0068, ADR-0010, ADR-0051, ADR-0034]
  findings: [TM3]
  fault_class: an external adversary writing to the last layer of protection through its own programming channel; saved by that layer's fault direction, not by its security
sources:
  - https://cloud.google.com/blog/topics/threat-intelligence/attackers-deploy-new-ics-attack-framework-triton
  - https://www.energy.senate.gov/services/files/40B2ED59-D34E-47C3-B9E2-1E8D030C5748
  - https://home.treasury.gov/news/press-releases/sm1162
verified: 2026-11-12
---

## Summary

A safety instrumented system (SIS) monitors a process independently of its normal control and acts on actuators to
stop it when a dangerous condition arises. The Triconex controllers at this facility ran three processor modules
that each vote on every output; a module that disagrees is taken out of service.

An intruder gained remote access to an SIS engineering workstation and deployed a framework, named `trilog.exe` after
Triconex's legitimate Trilog application, that uploads binaries to replace the logic on Triconex 3008 processor
modules. Dragos reports that the controller's physical key switch was in Program mode during operation;
in Run mode arbitrary logic changes are not possible. When the intruder's application code differed between the
redundant processing units, it failed the controllers' validation check, and some controllers entered a failed safe
state, shutting the process down. The owner investigated. Treasury dates the attack to August 2017. Dragos found the
malware in mid-November 2017 and notified DHS, DOE and E-ISAC; Mandiant published on 14 December 2017. Dragos was not
given the logic files the framework uploaded, so the intended effect is not known.

## Defensive position

- **The safety function held.** Dragos: "Compromising the security of an SIS does not necessarily compromise the
  safety of the system", and a system that fails safe "has performed its function". Mandiant records that the
  controllers initiated a safe shutdown on the failed validation check.
- **The vendor.** Dragos: the malware "leverages no inherent vulnerability in Schneider Electric products"; vendors
  "are victims", and had the victim used another SIS the malware would have targeted that one.
- **Scale.** Dragos judged TRISIS highly targeted, "not a highly scalable attack", needing process-specific
  knowledge to cause harm.

## Adversarial position

- **Mandiant:** the attacker "was intent on causing a specific outcome beyond a process shutdown"; the incident shows
  "the risk associated with integrated designs that allow bi-directional communication between DCS and SIS network
  hosts".
- **Dragos:** with the key switch in Run mode "arbitrary changes in logic are not possible"; TRISIS "could deny the intended safety functionality when it is needed"; targeting SIS is "a dangerous evolution",
  an escalation "specifically designed to target the safety function of the process".
- **Treasury:** TsNIIKhM built the tools; the same actors were reported probing US facilities.

## Outcome

There was no public investigation report on the facility. The record is the two vendor analyses (Mandiant, 14
December 2017; Dragos, version 1.20171213) and Treasury's designation of TsNIIKhM on 23 October 2020 under CAATSA
section 224. The plant tripped safely; neither analysis reports physical harm.

## Analysis

**TOPAK's SIS is the floor.** The correspondence is close. An SIS runs independently of the process logic and stops
the process; the floor (ADR-0010, ADR-0030) runs independently of the bundles and denies. An SIS's process logic may
ask for anything and the SIS overrides it; under ADR-0030 a bundle may allow anything and the admit still needs
`floor_permit` (`AdmitImpliesFloorPermit`). An SIS favours failing safe; the floor turns an engine error into a deny
(`FloorErrorIsDeny`, broken under `M_ERR` and `M_FAILOPEN`). The plant's actual outcome is that property: the
intruder's fault in the safety layer decided as a deny, and a deny shut the process down. ADR-0045's rule, "failure
can only subtract", is what Dragos means by "as long as it fails safe".

**Where the floor is built differently.** Triconex's logic could be replaced over the network from an engineering
workstation, gated by a key switch left open. ADR-0030 §3 gives the floor "no process, no socket, no
fetch": it ships in the mechanism release, its inputs are written only by the lift and the issued rules, and "no
bundle has a write path to any value the floor reads". `FloorComposition` checks the last of these as
`BundleCannotWriteFloorInputs`, and `M_WRITE`, a write path from the bundle tier into the floor's store, is the
mutation that is TRISIS's channel. Mandiant's remedy, a unidirectional gateway for anything that needs SIS data, is
ADR-0030 §3's "the dependency is one-directional" stated for a network. A change to the floor is a mechanism release:
a relaxation needs an anchor issuance (`NoWideningWithoutIssuance` in `FloorRouting`) and every change a unanimous
promotion (`P1_Unanimity`), bounded to a round (ADR-0024 §7). The key switch left in Program mode is a promotion that
never closed. TOPAK has no equivalent of that state, which is the design's point.

**What if the floor's host is the target.** None of the above survives an intruder on the host that runs the
mechanism. ADR-0045 §5 says the verified object is the specification and what runs it is a row. ADR-0068's T-0068-1
puts the overlay's admit path on every vehicle as a trust root whose failure lets "anything the stack requests
reach an actuator". TRISIS is that failure attempted. The engineering workstation was the SIS's Build host, and the
corpus's Build author is Byzantine by premise; but the corpus assumes the author proposes and the quorum disposes,
not that the author's host can write to the running floor. `proposed:FloorHostCompromise` would take the floor's host
as an adversary and ask what still holds: that a floor which runs is the one promoted (a measured, attested launch,
as `Confinement` gives a guest), and that a floor that differs from it fails closed. It should also model what the
Triconex modules did by construction: redundant evaluation that votes, so that one altered copy is a fault and not a
decision.

**The fault direction was luck.** Mandiant reads the trip as inadvertent, during development. The floor's safety in
TOPAK is proved for the floor's own errors; it is not proved against an adversary who writes a well-formed floor.
A floor that an intruder replaces cleanly, with every copy agreeing, permits whatever the intruder wrote, and
`FloorErrorIsDeny` holds throughout. Dragos says the same of TRISIS: it "would likely not directly lead to an unsafe
condition" but could deny safety "when it is needed".

**The SIS as the actuator's interlock.** In the overlay, ADR-0068 T-0068-8 makes the effector interlock a trust root
and `Release` rests `IrreversibleIsAPersons` on it alone. An SIS is that interlock for a plant. TRISIS shows the
interlock attacked through its maintenance channel rather than bypassed, which ADR-0068 §6 already counts among rows
"whose identity nothing issues". TM3's residual, "the interlock is moot when the effector itself is captured", is
the overlay's name for the attempt.

**Monitoring the safety layer's writability.** Schneider's recommendation of an operator-station alarm whenever the
key switch is in Program mode is a monitor on the protection layer's own state. In TOPAK every floor change is an
issuance and a promotion on the log, so a correlator (ADR-0051) can read it. Whether one would notice a change that
did not come through the log is the question `proposed:FloorHostCompromise` would have to answer.
