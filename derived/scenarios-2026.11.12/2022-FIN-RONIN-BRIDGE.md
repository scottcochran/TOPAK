---
id: 2022-FIN-RONIN-BRIDGE
title: The Ronin bridge, March 2022 — five of nine signatures, four from one operator and one from a delegation never revoked
kind: incident
date: 2022-03
sector: fintech
setting: The Ronin bridge between Ethereum and Ronin, a proof-of-authority sidechain run by Sky Mavis for Axie Infinity, with nine validators
concerns: [quorum, delegation, revocation, identity, monitoring, actuation]
rules_at_time:
  - document: Ronin bridge validator scheme (as reported by rekt.news)
    clause: withdrawal approval
    paraphrase: nine validators; five signatures approve a deposit or withdrawal; four validators were operated by Sky Mavis
  - document: Axie DAO allowlist arrangement, November 2021 (Sky Mavis's postmortem, as reported)
    clause: delegated signing
    paraphrase: under heavy load the Axie DAO allowlisted Sky Mavis to sign transactions on its behalf for a gas-free RPC node; the arrangement was discontinued in December 2021 and "the allowlist access was not revoked"
analogue:
  - record: ADR-0061
    clause: "§1"
    note: a certificate for n replicas tolerating f captured is the least whole number above (n + f) / 2; five of nine is that number for f = 0
  - record: ADR-0031
    clause: "§2, §5"
    note: no lease outlives the round it was granted for; a targeted revocation ends every lease the target matches, at once
  - record: ADR-0037
    clause: "§1"
    note: a principal holds exactly one seat; the rule is about principals, not about who runs them
  - record: ADR-0050
    clause: "§3"
    note: an operator's sign-on assertion is checked at the lease boundary, so a provider that stops vouching ends the lease at its next boundary
  - record: ADR-0063
    clause: "§3"
    note: a plane may have K_up effects outstanding and no more, and each honest governor keeps its own account, the plane signing anything
  - record: ADR-0068
    clause: "TM4, TM5"
    note: fewer than a third of replicas captured is tolerated; a captured quorum can issue anything within its charter and is bounded by what each honest governor checks
actors:
  - party: The attacker
    role: attacker
    fault: byzantine
    note: the US government later tied the incident to North Korea's Lazarus group, per The Block
  - party: Sky Mavis
    role: operator
    fault: omission
    note: ran four of nine validators; its postmortem says the Axie DAO allowlist access was not revoked
  - party: A senior Sky Mavis engineer
    role: insider
    fault: honest-error
    note: compromised by spear-phishing, per the postmortem; The Block's sources describe a fake job offer delivered as a PDF
  - party: Axie DAO validator
    role: peer
    fault: none-alleged
    note: its signature was obtained through the allowlist; what it should have done is not in what was read
  - party: The other four validators
    role: peer
    fault: none-alleged
  - party: A Ronin user
    role: user
    fault: none-alleged
    note: reported being unable to withdraw 5,000 ETH, which is how the drain was found
detection:
  means: [customer]
  latency: days
trace:
  - step: outside:signers-share-a-fault-domain
    at: before November 2021
    note: four of the nine validators run by one operator; one compromise reaches four signatures, one short of the threshold
  - step: outside:standing-delegation
    at: November 2021
    note: the Axie DAO allowlists Sky Mavis to sign on its behalf, for a gas-free RPC node under heavy traffic; no expiry in the allowlist
  - step: Unvouch
    at: December 2021
    note: the arrangement is discontinued and the allowlist entry stays; in Operators a provider's withdrawal ends a lease at its next boundary, and the trace is M_NOATTEST, where the boundary does not read it
  - step: outside:infrastructure-phished
    at: before the drain
    note: spear-phishing of an engineer gives the attacker Sky Mavis's IT infrastructure and its validator nodes
  - step: outside:delegated-signature-obtained
    at: day of the drain
    note: through the allowlist, the attacker gets the Axie DAO validator's signature, the fifth; one party now speaks for two seats, which is M_SEAT
  - step: outside:threshold-withdrawal
    at: day of the drain, about six days before 29 March 2022
    note: two withdrawals, 173,600 ETH and then 25.5 million USDC, each approved by five valid signatures
  - step: outside:unmonitored-six-days
    at: to 29 March 2022
    note: no alert; rekt's account is that "nobody noticed for six days"
  - step: outside:user-report
    at: 29 March 2022
    note: a user cannot withdraw 5,000 ETH; Sky Mavis announces the breach
  - step: outside:threshold-raised
    at: 29 March 2022
    note: the threshold moves to eight of nine, about 11 hours before the announcement, per rekt
  - step: RevokeLease
    at: by 1 April 2022
    note: Ronin replaces all of the former Sky Mavis validators; a targeted revocation of known keys
  - step: outside:users-reimbursed
    at: from 28 June 2022, as announced
    note: a $150 million Binance-led round and Sky Mavis's own funds; the bridge relaunched by early July, per The Block
counterfactual:
  by: the Axie DAO's delegation granted as a one-round lease, read again at every boundary, as ADR-0031 §2 and ADR-0050 §3 would have it
  trace:
    - step: Grant
      at: November 2021
      note: a lease to sign on the Axie DAO's behalf, for one round
    - step: EndRound
      at: by December 2021
      note: the round ends and so does the lease; with the arrangement ended no successor is granted, and there is nothing to forget to revoke
    - step: outside:infrastructure-phished
      at: March 2022
      note: the same compromise yields the same four Sky Mavis signatures
    - step: outside:certificate-short
      at: March 2022
      note: four signatures against a threshold of five; under ADR-0061 §1's rule for nine replicas, six
  holds: [OperatorLeaseWasVouched, OneSeatPerPrincipal, LeaseAuthorityMonotone]
outcome:
  by: Sky Mavis (postmortem); US government (attribution)
  date: 2022-04
  summary: >-
    Sky Mavis's postmortem said an employee was compromised by advanced spear-phishing and no longer worked there; that
    the attacker used that access to penetrate its IT infrastructure and reach the validator nodes; and that the
    Axie DAO had allowlisted Sky Mavis to sign on its behalf, which was discontinued in December 2021 but "the
    allowlist access was not revoked", so the attacker obtained the Axie DAO validator's signature. The US government
    tied the incident to the Lazarus group. Ronin had already replaced the former Sky Mavis validators and raised the
    threshold to eight of nine; about a month after the hack it increased the validator set to 11, with a long-term
    goal of more than 100.
  aftermath: >-
    Sky Mavis raised $150 million in a round led by Binance and said it would use it, with its own funds, to reimburse
    users from 28 June 2022; the Ethereum bridge had relaunched by early July, per The Block. rekt.news asked why the set had not been widened before, and
    compared the case to the Wormhole bailout. The stolen funds were not returned in what was read.
  effect_reversed: "no"
model:
  modules: [Operators, Lease_A1, Seats, Membership, Outstanding, RunCoupling, proposed:SignerIndependence]
  properties: [OperatorLeaseWasVouched, OneSeatPerPrincipal, LeaseAuthorityMonotone, RevokedStaysStopped, HavocPlaneBoundedInEffects, NoEffectWithoutLiveObserver]
  mutations: [M_NOATTEST, M_SEAT]
  records: [ADR-0061, ADR-0031, ADR-0037, ADR-0050, ADR-0063, ADR-0039, ADR-0038, ADR-0035, ADR-0068]
  findings: [TM5, TM4, TM7, CR-3]
  fault_class: quorum capture through a shared fault domain plus a standing delegation nobody revoked; no budget on what the captured quorum could move, and no monitor
sources:
  - https://rekt.news/ronin-rekt
  - https://www.theblock.co/post/156038/how-a-fake-job-offer-took-down-the-worlds-most-popular-crypto-game
  - https://www.theblock.co/post/140165/ronin-replaces-compromised-validators-and-plans-to-bolster-security-after-600-million-hack
verified: 2026-11-12
---

## Summary

Ronin was a proof-of-authority sidechain for the game Axie Infinity, run by Sky Mavis, with a bridge to Ethereum.
Nine validators approved bridge deposits and withdrawals, and five signatures were needed. Sky Mavis ran four. In
November 2021, under heavy traffic, the Axie DAO allowlisted Sky Mavis to sign on its behalf so that a gas-free RPC
node could be run. The arrangement was discontinued in December 2021; the allowlist access was not revoked.

In Sky Mavis's postmortem's account, an attacker compromised a senior Sky Mavis engineer by spear-phishing; The Block's sources said the lure was a
fake job offer, delivered as a PDF after several rounds of interviews. From there the attacker reached Sky Mavis's
four validator nodes and, through the allowlist, obtained the Axie DAO validator's signature: five of nine. It
authorized two withdrawals from the bridge, 173,600 ETH and then 25.5 million USDC, about $624 million at rekt's
count. Nobody noticed for six days. Ronin's alert, quoted by rekt on 29 March 2022, said: "We discovered the attack this morning after a
report from a user being unable to withdraw 5k ETH from the bridge."

Sky Mavis said "the threshold will be eight out of nine", a change rekt reported was made about 11 hours before the
announcement. By 1 April Ronin had replaced all the former Sky Mavis validators, having admitted to a "small
validator set". About a month later it had 11 validators.

## Defensive position

**Sky Mavis** (postmortem, as reported by The Block):

- Its employees face constant advanced spear-phishing, and one was compromised; that employee no longer works there.
- The Axie DAO arrangement was discontinued in December 2021; the failure was that its allowlist access was not
  revoked, which the postmortem states plainly.
- It responded by replacing the validators, raising the threshold, expanding the set toward more than 100, and
  reimbursing users with a $150 million Binance-led round and its own funds.

## Adversarial position

**rekt.news** (29 March 2022):

- Decentralization and trustlessness were traded for throughput: four of nine validators in one operator's hands
  meant one more signature gave control.
- Key infrastructure appeared unmonitored; the only alert was a user, days later.
- Why had the set not been widened before? And, comparing the Wormhole bailout: "who's bailing out $624M?"

## Outcome

No regulator's or court's finding is in what was read. Sky Mavis's postmortem of April 2022 gave the account in the
front matter. The US government tied the attack to the Lazarus group, per The Block. Sky Mavis said it would begin
reimbursing users on 28 June 2022, and the bridge had relaunched by early July. The stolen funds themselves were not recovered in the
sources read, so the effect was compensated, not reversed.

## Analysis

**Five of nine tolerates no capture.** ADR-0061 §1 sizes a certificate as "the least whole number above (n + f) / 2,
so that any two certificates share an honest signer". For nine replicas five is that number with f = 0, and with f =
2, which is (n − 1) div 3 as `Membership` takes it, it is six. Ronin's threshold was a simple majority, sized for
honest signers. On the facts reported, the attacker held four Sky Mavis keys and one delegated signature, five in all.
Under ADR-0061's sizing, the same attack falls one signature short. That is the cheapest change the corpus would
have made, and it is luck as much as design: one more compromised party and it is gone.

**The deeper fault is one fault domain holding four seats.** TM4 tolerates fewer than a third of replicas captured,
and TM5 describes what a captured quorum can do. Both assume captures are independent. Four validators behind one
company's IT are one capture. ADR-0037 §1, "a principal holds exactly one seat", does not help: it is about principals,
and Sky Mavis's four validators were four principals with four keys. The corpus has independence rules for Observers,
by device (ADR-0038 §4), and for Personas, by lineage (ADR-0035). It has none for the signers of a certificate. ADR-0061
counts replicas and its archetype puts each on its own vehicle, which makes the question disappear in the overlay's
setting and leaves it open everywhere else. `proposed:SignerIndependence` would declare each signer's fault domain and
require that a certificate's threshold exceed what any one domain holds plus f. CR-3, "no delegation or chain model",
is the matching finding, and this is the delegation half.

**A delegation that cannot be forgotten.** ADR-0031 §2: "There is no lease that outlives the round it was granted
for." In TOPAK the Axie DAO's grant to Sky Mavis would have been a lease, and it would have ended with its round. The
failure mode, a temporary permission still live three months after the arrangement ended, is not expressible: authority
lapses by default and must be renewed. `Operators` states the boundary version: `OperatorLeaseWasVouched`, a live lease
was attested at its last boundary by a provider that vouched, and `Unvouch` is the provider withdrawing. `M_NOATTEST`,
"the sign-on assertion is not read at a lease boundary", breaks it, and is exactly an allowlist nobody re-reads. Once
the allowlist let Sky Mavis's infrastructure produce the Axie DAO's signature, one party spoke for two seats, which is
`Seats`' `M_SEAT` breaking `OneSeatPerPrincipal`. The counterfactual is this lapse and nothing more. It holds only if
the deployment used leases for the delegation, which is the whole claim: TOPAK makes the default expiry, and Ronin's
default was permanence.

**Revocation was available and late.** Replacing the Sky Mavis validators is ADR-0031 §5's targeted revocation, whose
effect "is immediate, not bounded by remaining TTL", and `Lease_A1`'s `RevokedStaysStopped` says a revoked key does not
come back. It ran after the money had gone. The bound that would have mattered during the six days is ADR-0063's:
a plane "may have `K_up` effects outstanding and no more", and each honest governor keeps its own account
(`Outstanding`'s `HavocPlaneBoundedInEffects`, "the plane signing anything"). A bridge contract that checked five
signatures and nothing else is a governor with no count. A withdrawal budget per period would have bounded the loss
under a captured quorum; the threshold could not.

**Six days with no Observer.** ADR-0039 §2 couples every effect-bearing admit to a live Observer, so withdrawals of
this size would have been read within `K` (`NoEffectWithoutLiveObserver`). Whether anything would have been found is a
judgment; that the bridge kept paying with no one reading is what coupling forbids. rekt's "key infrastructure appeared
unmonitored" is CR-2 in a sentence.

**Where the pattern stops.** The phishing itself is TM7's insider with a key: "the mechanism cannot tell a person from a
program holding the key". Nothing here stops a compromised machine from signing. What TOPAK changes is how many such
machines it takes, how long a temporary grant lives, and how much a captured quorum can move before something counts.
