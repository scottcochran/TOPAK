---
id: 2015-ICS-UKRAINE-GRID
title: Ukrainian distribution grid, 23 December 2015 — breakers opened through the operators' own HMIs, then the bridges blown
kind: incident
date: 2015-12-23
sector: industrial-control
setting: SCADA and distribution management systems of three Ukrainian regional distribution companies (oblenergos), Kyivoblenergo among them
concerns: [authority, identity, emergency-path, human-in-the-loop, actuation, rollback, deployment, monitoring]
rules_at_time:
  - document: Oblenergo remote-access practice (as E-ISAC and SANS describe it)
    clause: VPN into the ICS network
    paraphrase: the ICS networks were reachable by VPN from the business networks; the attackers used stolen credentials on those VPNs and the native remote control in the operators' systems, and no exploit against the distribution management system vendors
  - document: Distribution operating practice (as reported)
    clause: manual operation
    paraphrase: substations could be operated manually when SCADA control was lost; the oblenergos moved to manual operations and afterwards ran in an "operationally constrained mode"
analogue:
  - record: ADR-0052
    clause: "§1, §7"
    note: the emergency seat's key does not depend on single sign-on; the record does not cover "a person acting outside the mechanism"
  - record: ADR-0050
    clause: "§4, §6"
    note: an operator's deny needs no lease; operators observe each other, and a finding is a deny
  - record: ADR-0024
    clause: "§1, §2"
    note: code crosses into service only by promotion, under a unanimous quorum
  - record: ADR-0068
    clause: "TM7, TM2"
    note: 'TM7: "the mechanism cannot tell a person from a program holding the key"; TM2: denial is always available to a link adversary'
actors:
  - party: Unidentified intruders; the US Government in 2021 attributed the activity to Russian nation-state cyber actors
    role: attacker
    fault: byzantine
  - party: Three oblenergos, Kyivoblenergo among them
    role: operator
    fault: none-alleged
  - party: Dispatch operators
    role: operator
    fault: none-alleged
    note: locked out of their workstations while the breakers were opened through them; restored service by manual operation
  - party: Serial-to-Ethernet gateways at substations
    role: actuator
    fault: byzantine
    note: firmware overwritten with malicious images, leaving them inoperable or unrecoverable
  - party: Server UPS units
    role: automation
    fault: byzantine
    note: reconfigured through their remote management interface to disconnect on a schedule
  - party: DHS ICS-CERT; E-ISAC with the SANS ICS team
    role: investigator
    fault: none-alleged
detection:
  means: [operator, customer]
  latency: immediate
trace:
  - step: outside:spear-phish-business-network
    at: from March 2015
    note: e-mails with malicious Office attachments; BlackEnergy 3 found at each impacted company
  - step: outside:credentials-harvested
    at: during 2015
    note: legitimate credentials collected on the business networks; VPN paths into the ICS networks found
  - step: Grant
    at: before 23 December
    note: the VPN admits whoever presents the credentials. In Lease_A1 a grant goes to a principal; here the principal is whoever holds the key (TM7)
  - step: outside:attack-firmware-built-and-tested
    at: before 23 December
    note: E-ISAC and SANS assess with high confidence that the adversary tested its firmware before use
  - step: Actuate
    at: about 15:35 local, Kyivoblenergo
    note: breakers opened through the HMIs, by remote administration tools or remote ICS client software; at least 27 substations across three companies within 30 minutes; about 225,000 customers
  - step: outside:operators-locked-out
    at: same
    note: the last modification before the attack was taking control of the operator workstations
  - step: outside:unvoted-firmware-upload
    at: same
    note: malicious firmware written to serial-to-Ethernet gateways ("blowing the bridges") so that remote commands could not bring substations back
  - step: outside:hosts-and-logs-wiped
    at: same
    note: modified KillDisk erases master boot records on some systems and logs and events on others; an HMI card inside an RTU overwritten
  - step: outside:ups-disconnect
    at: same
    note: scheduled UPS disconnects meant to cut power to the companies' own buildings or data centres
  - step: outside:call-centre-flooded
    at: same
    note: thousands of calls to at least one company's call centre; SANS judges the aim was to frustrate customers
  - step: outside:manual-operation-outside-mechanism
    at: after the outage, several hours
    note: operators move to manual operations and restore service
outcome:
  by: US DHS ICS-CERT (IR-ALERT-H-16-056-01); E-ISAC and the SANS ICS team (Defense Use Case, 18 March 2016)
  date: 2016-02-25
  summary: >-
    ICS-CERT reported that on 23 December 2015 three oblenergos suffered outages caused by "malicious remote operation
    of the breakers", the attacks occurring "within 30 minutes of each other" and affecting about 225,000 customers,
    with KillDisk, corrupted serial-to-Ethernet firmware and scheduled UPS disconnects, and BlackEnergy found at each
    company with its role unknown. E-ISAC and SANS found that the cause of the outage was "the manipulation of the ICS
    itself and the loss of control due to direct interactive operations by the adversary", that the wiping and the
    firmware only delayed restoration, and that service was restored after several hours by manual operation.
    ICS-CERT's team did not independently review technical evidence; neither report attributed the attack. In 2021
    the US Government attributed the activity to Russian nation-state cyber actors.
  aftermath: >-
    ICS-CERT recommended isolating ICS networks from untrusted networks, limiting remote access and making it
    operator-controlled and time-limited, multi-factor authentication with tokens of different types, application
    whitelisting, and contingency plans for safe operation or shutdown after a breach. E-ISAC and SANS added protocol
    and communication-path authentication, log collection from SCADA applications, and plans to "activate manual
    operations only" by removing whole sections of cyber assets.
  effect_reversed: partial
model:
  modules: [Lease_A1, Operators, Emergency, RulesFloorNV_rev5, Confinement, proposed:ManualReversion]
  properties: [DenyAlwaysAvailable, EmergencyLeaseHasARosterQuorum, NoAgentHoldsAnEmergencySeat, P1_Unanimity, NoActionUnderFencedEpoch]
  mutations: [M_HOST, M_NOQUORUM]
  records: [ADR-0052, ADR-0050, ADR-0024, ADR-0066, ADR-0068, ADR-0045, ADR-0031]
  findings: [TM7, TM2, TM3, CR-15, CR-34]
  fault_class: an external adversary holding the operators' credentials and their consoles; acts inside every rule the system checked, then destroying the path back
sources:
  - https://www.cisa.gov/news-events/ics-alerts/ir-alert-h-16-056-01
  - https://nsarchive.gwu.edu/sites/default/files/documents/3891751/SANS-and-Electricity-Information-Sharing-and.pdf
verified: 2026-11-12
---

## Summary

On 23 December 2015 Kyivoblenergo reported outages. From about 15:35 local time seven 110 kV and 23 35 kV substations
were disconnected for three hours. Three oblenergos had been attacked, within 30 minutes of each other; about 225,000
customers lost power, and at least 27 substations were taken offline.

The intrusions began with spear-phishing of the business networks; BlackEnergy 3 was found at each company.
Credentials were harvested there and used on VPNs into the ICS networks. On the day, the intruders took control of
operator workstations, locking the operators out, and used the HMIs to open breakers. At the same time they uploaded
malicious firmware to serial-to-Ethernet gateways at substations, leaving them inoperable, ran a modified KillDisk that
erased master boot records or logs, scheduled disconnects of server UPS units, and flooded at least one company's call
centre with thousands of calls. The three companies used different distribution management systems, and no exploit
was used against them: the intruders operated the native controls. The companies moved to manual operations and
restored service after several hours, and continued to operate in a constrained mode afterwards.

## Defensive position

There is no defence of the attack on record; the positions are about scale and fault:

- **E-ISAC and SANS** rated the incidents "low" on a macro scale of power-system impact (a small share of
  consumers, limited duration), while expecting the companies to rate them high or critical.
- **On the vendors:** the DMS vendors were "simply abused with direct access"; no exploit was used against them.
  SANS also notes that application whitelisting "would have had a limited role" against this attack.
- **On restoration:** the oblenergos restored service in hours by manual operation, which E-ISAC and SANS recommend
  others prepare for.
- **On evidence:** ICS-CERT's team "was not able to independently review technical evidence", and neither report
  attributes the attack.

## Adversarial position

- **E-ISAC and SANS:** "the actual cause of the outage was the manipulation of the ICS itself"; BlackEnergy,
  KillDisk and the firmware were components "for the purposes of access and delay of restoration". The firmware
  attack was "blowing the bridges".
- **ICS-CERT:** remote access should be limited, operator-controlled and time-limited, with multi-factor
  authentication.
- **The US Government**, in 2021, attributed the activity to Russian nation-state cyber actors (ICS-CERT alert,
  revised 20 July 2021).

## Outcome

ICS-CERT's alert of 25 February 2016 and the E-ISAC/SANS Defense Use Case of 18 March 2016 are the findings on
record (front matter). Service was restored manually within hours; the companies continued in a constrained mode.
Gateways whose firmware was overwritten, and systems KillDisk had wiped, were not restored by any remote act.

## Analysis

**Every breaker opening was authorised by the rules the system checked.** The intruders held working credentials and
used the operators' own consoles; the DMSs saw operators. In TOPAK terms the lease was granted to whoever presented
the key, and every `Actuate` was admitted under it. TM7 states the limit: "the mechanism cannot tell a person from a
program holding the person's key". ADR-0050 §3 attests an operator's sign-on at the lease boundary and §6 puts at least
three operators in a domain who read each other's topics. That would make a burst of breaker openings visible to the
other operators, and any of them could deny. It would not have stopped acts that complete in seconds, by an intruder
who had first taken every operator's console.

**The deny path was the captured path.** `Operators` proves `DenyAlwaysAvailable`: while an operator is in force,
the mechanism enables its revocation of any principal. The property is about the mechanism. In Ukraine the operators'
means of issuing anything was the workstation the intruders held. A deny that runs through the same console as the
attack is not available in the sense that matters. ADR-0052 §1 sees half of this ("an emergency path that needs the
identity provider fails when the provider does") and keeps the emergency key off single sign-on. It does not ask for
an emergency path off the operators' consoles.

**Manual reversion is outside the corpus by declaration.** What restored power was people operating substations by
hand. ADR-0052 §7 lists "a person acting outside the mechanism" among what it does not cover. That is honest, and it
is the whole of Ukraine's recovery. The emergency seating (ADR-0052 §2) is a quorum seating a person *inside* the
mechanism; `Emergency` proves `EmergencyLeaseHasARosterQuorum` and `NoAgentHoldsAnEmergencySeat`, and under
`M_NOQUORUM` the first fails. All of it assumes the mechanism and the roster's keys are the defenders'. When the
control plane is captured, the safe direction is to leave it. `proposed:ManualReversion` would model a declared,
out-of-band path that bypasses the mechanism, with a property that the mechanism's subsequent state is reconciled
from what the people did, not the reverse. It would also need a record, since every current record treats a path
around the mechanism as the thing to prevent.

**Reversibility depends on the channel surviving.** Opening a breaker is reversible. Overwriting the gateway firmware
made it irreversible from the control room: only a person on site could close it. ADR-0066 types an entry's effect
class at declaration, and CR-15 says reversibility had no mechanism. Ukraine shows the class is not a property of the
act alone. The same `Actuate` is reversible while the path back exists, and an adversary can remove the path after
acting. No module expresses an effect whose class changes after it is admitted.

**The firmware upload was an unvoted promotion.** Under ADR-0024 code crosses into service only by promotion, under
a unanimous quorum (`P1_Unanimity`). A gateway that accepts firmware over the network from anyone on the control
network is a promotion path with no tally. TOPAK's own trusted base would class those gateways as rows whose failure
adds (ADR-0045 §2), and `Confinement` under `M_HOST` is the nearest model: the host is untrusted where the rung
trusts it.

**The UPS and the call centre.** Both struck at the defenders' own capacity: power to their buildings, and a
channel from customers. TM2 says "denial is always available" to an adversary of the links. TOPAK's posture under
denial is to stall, which for a utility already in outage means the outage lasts until people act by hand.

**What TOPAK would have changed.** Round-coterminous leases, fenced fleet-wide by an epoch increment (ADR-0031
§2, §5; `NoActionUnderFencedEpoch` in `Lease_A1`), would have bounded how long harvested credentials were good for, if renewal required a fresh attestation the intruder could
not produce. That is the one place the pattern bites. The rest of the attack ran on hosts and devices TOPAK places
outside the verified object.
