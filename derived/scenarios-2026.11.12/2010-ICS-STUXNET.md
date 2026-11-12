---
id: 2010-ICS-STUXNET
title: Stuxnet, disclosed 2010 — stolen signing keys, a lying engineering library, and protection inputs replayed to the operators
kind: disclosure
date: 2010-06-17
sector: industrial-control
setting: Siemens S7-315 and S7-417 controllers, WinCC and Step 7 engineering stations, and frequency-converter drives, in Iran; the Natanz Fuel Enrichment Plant per the analyses
concerns: [supply-chain, identity, monitoring, sensing, interlock, deployment, containment, actuation]
rules_at_time:
  - document: Code-signing public key infrastructure (as Symantec's timeline records it)
    clause: certificate revocation
    paraphrase: a driver signed under a certificate from a trusted issuer is accepted until the issuer revokes the certificate; VeriSign revoked Realtek's certificate on 16 July 2010 and JMicron's on 22 July 2010
  - document: Siemens S7 controller and Step 7 engineering practice (as Langner describes it)
    clause: block exchange with the PLC
    paraphrase: code blocks are read from and written to the controller by the engineering software through its library; at the controller level Stuxnet used "legitimate product features" and no zero-day
analogue:
  - record: ADR-0044
    clause: "§1, §3, §4"
    note: a bundle is trusted by a signature under a key in the issued rules; the key signs after the tally; the mechanism refuses an unsigned or mis-signed bundle
  - record: ADR-0024
    clause: "§3"
    note: a vote binds to the artifact's digest, the gate evidence's digest and the rules epoch
  - record: ADR-0039
    clause: "§5"
    note: coupling separates a present, keeping-up Observer from an absent one and cannot separate an honest Observer from a colluding one
  - record: ADR-0068
    clause: "TM3, TM10"
    note: 'TM3: "the interlock is moot when the effector itself is captured"; TM10: supply chain is bounded by promotion by digest'
actors:
  - party: Stuxnet's authors (unidentified in these sources)
    role: attacker
    fault: byzantine
  - party: Realtek Semiconductor and JMicron Technology code-signing keys
    role: vendor
    fault: byzantine
    note: valid certificates whose keys signed Stuxnet's drivers
  - party: VeriSign
    role: vendor
    fault: honest
    note: revoked both certificates in July 2010, after the public reports
  - party: Step 7 library s7otbxdx.dll (replaced)
    role: automation
    fault: byzantine
    note: 93 of 109 exports forwarded; 16, the routines that read, write and enumerate PLC blocks, intercepted
  - party: Cascade Protection System (S7-417), per Langner
    role: safety-system
    fault: byzantine
    note: in the earlier overpressure attack its inputs were recorded for 21 seconds and replayed in a loop to SCADA and alarm routines
  - party: Plant operators
    role: operator
    fault: none-alleged
  - party: VirusBlokAda, Symantec, Langner, ISIS
    role: investigator
    fault: none-alleged
detection:
  means: [researcher]
  latency: years
trace:
  - step: outside:seeded-by-removable-drive
    at: June 2009 to May 2010
    note: five organizations, all with a presence in Iran, targeted by ten initial infections; 12,000 infections traced back to them
  - step: outside:driver-signed-with-stolen-key
    at: 25 January 2010
    note: driver signed with Realtek's valid certificate; a JMicron-signed driver found 17 July 2010
  - step: outside:engineering-library-replaced
    at: on infection of a Step 7 station
    note: s7otbxdx.dll renamed and replaced; reads, writes and enumerations of PLC blocks pass through Stuxnet
  - step: Tamper
    at: every 15 minutes, when a matching PLC is found
    note: on an S7-315 with at least 33 Vacon or Fararo Paya drives on Profibus, malicious blocks are written and OB1 and OB35 infected. Confinement's Tamper alters a running guest after its launch was measured
  - step: outside:reader-hides-alteration
    at: whenever an engineer reads the PLC
    note: 'Symantec: "Victims attempting to verify the issue would not see any rogue PLC code"'
  - step: Heartbeat
    at: during the overpressure attack (earlier variant, S7-417)
    note: 21 seconds of sensor values replayed in a loop; the display shows live, changing, normal values. A watermark on replayed data advances
  - step: outside:protection-inputs-falsified
    at: same
    note: Langner assumes pressure-sensor de-calibration, so stage exhaust valves never open while pressure rises
  - step: outside:captured-controller-actuates
    at: after about 13 and 27 days of recorded normal operation
    note: rotor-speed attack sets maximum frequency to 1410 Hz, then 2 Hz, then 1064 Hz; normal operation 807 to 1210 Hz. Per Langner this attack does not replay values
  - step: Issue
    at: 16 and 22 July 2010
    note: certificates revoked by their issuer. In TOPAK replacing a bundle key is an anchor issuance (ADR-0044 §1)
outcome:
  by: Symantec (W32.Stuxnet Dossier v1.4); Langner (To Kill a Centrifuge); Institute for Science and International Security
  date: 2011-02
  summary: >-
    Symantec found a threat whose "final goal is to reprogram industrial control systems ... and to hide those changes
    from the operator", exploiting "a total of four unpatched Microsoft vulnerabilities", drivers signed
    with Realtek's and JMicron's certificates, a Windows rootkit and "the first ever PLC rootkit". It found about 60% of
    infected hosts in Iran and a payload for S7-315 controllers driving 33 or more frequency converters from Vacon or
    Fararo Paya, cycling them through 1410, 2 and 1064 Hz. Langner (November 2013) described an earlier payload against
    the S7-417 Cascade Protection System that replayed 21 seconds of recorded inputs while isolating stages and keeping
    exhaust valves shut, and judged that the attackers "took great care to avoid catastrophic damage". ISIS (December
    2010) reported that Iran decommissioned and replaced about 1,000 IR-1 centrifuges at Natanz in late 2009 or early
    2010, and said this "could have resulted" from Stuxnet. President Ahmadinejad said software had caused "problems for
    a limited number of our centrifuges".
  aftermath: >-
    Microsoft patched the shortcut (MS10-046, 2 August 2010) and print spooler (MS10-061, 14 September 2010)
    vulnerabilities; VeriSign revoked both certificates; Siemens investigated reports of malware on WinCC systems from
    19 July 2010. No investigating body has published findings on attribution in these sources.
  effect_reversed: "no"
model:
  modules: [Confinement, Coupling, RulesFloorNV_rev5, Labels, proposed:WorldObserver]
  properties: [ContainedMeansConfined, NoAdmitWithoutLiveObserver, UnreadBounded, P1_Unanimity, P3_AuthorNotCounted, OutsideResultIsUntrusted]
  mutations: [M_HOST, M_HW]
  records: [ADR-0044, ADR-0024, ADR-0039, ADR-0045, ADR-0068, ADR-0007, ADR-0034]
  findings: [TM3, TM10, TM11, TM1, CR-24]
  fault_class: an external adversary with valid keys, on the engineering host and in the controller; the protection layer's inputs replayed, so a monitor that was present and progressing reported nothing
sources:
  - https://www.cs.umd.edu/class/fall2023/cmsc614/papers/stuxnet-dossier.pdf
  - https://icscsi.org/library/Documents/Cyber_Events/Langner%20-%20To%20Kill%20a%20Centrifuge.pdf
  - https://www.isis-online.org/uploads/isis-reports/documents/stuxnet_FEP_22Dec2010.pdf
verified: 2026-11-12
---

## Summary

On 17 June 2010 VirusBlokAda reported malware, which it named RootkitTmphider, spreading through a Windows shortcut
vulnerability. Symantec renamed it W32.Stuxnet on 19 July. Its earliest sample seen dates from June 2009. From 25
January 2010 its drivers were signed with a valid Realtek certificate; on 17 July ESET found one signed with a
JMicron certificate. VeriSign revoked the two on 16 and 22 July. By 29 September 2010 Symantec counted about 100,000
infected hosts, about 60% of them in Iran.

On a computer running Siemens Step 7, Stuxnet renamed the library through which the software exchanges code with a
controller, `s7otbxdx.dll`, and put its own in its place. 93 of the 109 functions were passed through and 16 were
intercepted, among them reading, writing and enumerating code blocks. Through them it wrote its own blocks to S7-315
controllers that drove at least 33 frequency converters from Vacon or Fararo Paya, and hid them from anyone reading the
controller. After about 13 days of recording operation between 807 and 1210 Hz, the code set the drives' maximum
frequency to 1410 Hz, and in later sequences to 2 Hz and then 1064 Hz, over periods of about 27 days.

Langner describes an earlier payload, against S7-417 controllers of the Cascade Protection System, that recorded 21
seconds of sensor values and replayed them in a loop to the control room's SCADA screens and alarm routines while it
closed isolation valves and kept stage exhaust valves shut, so that pressure rose. ISIS reported in December 2010 that
about 1,000 IR-1 centrifuges at Natanz were decommissioned and replaced in late 2009 or early 2010.

## Defensive position

There is no defender on record arguing for the design. The positions on record:

- **Iranian officials** acknowledged a software attack and minimised it: Salehi said the virus was caught "exactly at
  the same spot it wanted to penetrate"; Ahmadinejad spoke of problems with "a limited number" of centrifuges (ISIS).
- **The protection system worked as designed against faults.** Langner describes the CPS as built to cope with
  ongoing centrifuge failures by isolating them, a "crude version of fault tolerance", and notes that during the
  rotor-speed attack the CPS was left alone and would "kick in, isolate and run down" a failing centrifuge.
- **On scope:** Symantec described the many infections outside the target as likely "collateral damage" of
  promiscuous propagation; the analyses agree the payload checked for one configuration before acting.

## Adversarial position

- **Symantec:** the payload was built to hide its changes "from the operator of the equipment"; anyone verifying the
  controller "would not see any rogue PLC code".
- **Langner:** "the worst vulnerabilities are not bugs, they are features"; protection systems "were never designed to
  withstand a cyber attack"; in the overpressure attack the payload "takes over control completely": legitimate logic
  receives fake inputs and its outputs have no effect.
- **ISIS:** the frequencies in the attack sequences imply the IR-1 as a target; if the goal was a limited set-back
  "while making detection of the malware difficult, it may have succeeded, at least for a while".

## Outcome

There is no adjudication. The record is the researchers' analyses (front matter): Symantec's dossier, revised to
version 1.4 in February 2011; Langner's November 2013 report; ISIS's December 2010 assessment, which it called
preliminary and whose link between Stuxnet and the centrifuge losses is a possibility, not a finding. The certificates
were revoked and the Windows vulnerabilities patched. The centrifuges were replaced, not recovered.

## Analysis

**Two signed drivers and ADR-0044.** TOPAK trusts a bundle by a signature under a key the issued rules carry, and
refuses an unsigned or mis-signed one (§3). Windows trusted Stuxnet's drivers on exactly that shape of rule, with a
wider key set. ADR-0044 narrows the set to keys named by issuance and puts signing after the tally (§4), but a
signature still proves only that the key signed. A stolen bundle key is a trust root's residual (ADR-0045 §2): "what
its holder can do while the identity stands". What TOPAK adds is that revocation is an anchor issuance, ordered on the
log; the Realtek certificate was trusted for six months, until someone outside noticed. CR-24 is the corpus's own
record of how long unsigned and single-key edges lasted in the reference. TM10 says supply chain is bounded "as the
corpus states it today".

**The lying library and the quorum.** Under ADR-0024 §3 a vote binds to the artifact's digest. Stuxnet's
library hid code from an engineer reading it back; a voter who reads through a compromised tool sees a clean
artifact. The digest defends what is loaded against a swap after the vote, provided the mechanism computes the digest
of what it loads. It does not defend a vote taken on the author's own host against a tool on that host that shows
the voter something else. `P3_AuthorNotCounted` keeps the author's vote out of the tally; nothing models a voter's
view being forged. `P1_Unanimity` holds and means less than it reads.

**Altered after load.** Stuxnet wrote its blocks to controllers in service. `Confinement` states the limit plainly:
"evidence is the launch measurement, not the running image", and rungs 2 and 3 do not detect a running guest being
altered, except that at rung 3 hardware turns the attempt into the guest's death (`M_HW` removes that). A PLC has no
rung. Under `M_HOST` the host is untrusted where the rung trusts it and `ContainedMeansConfined` fails at rungs 1 and
2; Stuxnet is `M_HOST` on the engineering station. TM3 has the general case: "the interlock is moot when the effector
itself is captured".

**Replay defeats progress-based liveness.** ADR-0039 replaced presence with progress: a heartbeat must carry a
rising watermark. A replayed loop of sensor values is progress. Every screen updates; every alarm routine runs; a
coupling to that monitor would read live, and `NoAdmitWithoutLiveObserver` and `UnreadBounded` would hold. ADR-0039 §5
admits this for a colluding Observer. Stuxnet shows a third case, neither dead nor colluding: an honest Observer whose
input is forged upstream. TOPAK's Observer reads the round topic, which the mechanism writes and no principal can
(ADR-0042 §3), so replay against it needs the mechanism. That is the design's real answer, and its price: the
Observer watches acts, never the plant. `proposed:WorldObserver` would model an Observer of sensed state, with replay
as a fault class and a property tying liveness to a challenge the source cannot pre-record. No record proposes one.

**The protection system as the target.** Langner's methodology for the attacker starts from the plant's HAZOP and
its protection systems. TOPAK's protection layer is its floor, and ADR-0030 §3 gives it no socket and no runtime write
path. The CPS had both. That comparison favours TOPAK only while the mechanism host is trusted, which is ADR-0045
§5's row and exactly what Stuxnet attacked one layer down.

**Damage that looks like unreliability.** Langner reads the rotor-speed attack as designed to produce failures
indistinguishable from the IR-1's known unreliability. TM1 says anything inside the envelope "was voted acceptable";
an adversary inside its envelope can still choose the acts whose harm looks like noise. Under ADR-0007 a judgment that
the noise is an attack is never a lift, so it never refuses an admit. TOPAK does not claim otherwise.
