# Recurring defects

Drawn from `derived/topak-command-chain-diagram-findings-2026.11.10.md` (eighteen findings against ten records revised
the same day) and from the errata in History. The ids are that document's.

## The sweep

A claim is usually stated in several places, and a revision reaches only the one its author was looking at. After any
change to what a record says or to what has been done:

1. **The record itself**: the Status note, each Ratification condition item, Open obligations, Consequences, the
   title, and any count or "would" that assumed the old state.
2. **Every number and list against its table.** Count the rows.
3. **Sibling records**, by `grep -l 'ADR-NNNN' decisions/*.md`, for anything they say of the changed clause.
4. **Modules whose headers describe the record as drafted.** A module cited by digest cannot be edited; report it.
5. **Non-record prose that cites it**: `spec/README.md` and the README of each results area.

Fix what is in this record. Report what is in others.

## Defects to look for

**A record is not revised when its evidence arrives (R-1, A-1).** ADR-0068's Status note still said "Nothing here is
modelled, checked or built", its condition "no module is written", and §3 what modules "would prove", after eight
modules existed and its siblings cited them by digest. When a module, result or reference arrives, every record that
waits on it needs an R-revision.

**A word changes meaning in one clause and not its neighbours (R-3).** ADR-0065 §1 moved to "originates" because a
relayed lease is received from a peer. Its §9 and ADR-0067 §7 kept "received".

**A count and its table disagree (R-2).** A Consequences bullet said three adversaries were bounded by nothing. The
table had two, and a third whose cell began with the word "Nothing" and stated a bound.

**A quotation is short, or is a paraphrase (R-5, R-10).** ADR-0062 §8 said R3 "refuses `Actuate`". The table forbids
`Actuate` and `Report`, and the omitted one was what mattered there. Quote words that appear in the source, or do not
use quotation marks.

**A pending amendment is counted as in force (R-6).** ADR-0065 called something "a sixth item", counting a fifth that
was Pending on another record. Read that record's Pending line.

**A clause names something its condition does not ask for (R-7).** ADR-0061 §3 cites floor entries, and its condition,
unlike its siblings', had no floor item. Check the condition against every artifact the Decision names.

**Items are unmarked (R-8).** The module and reference items said Met or Not met, and every floor and reader item said
neither. None of those was met.

**A sibling set has a section one member lacks (R-9).** Compare headings across records drafted together.

**A fact is stated of a plane that has to be honest (R-4).** "Arrives a day old" assumes the clock ticks, and a
captured plane can stop it. Say what a claim assumes.

**A record's number is not the module's (M-3, M-5).** A bound "more than one tick past" against a module's "one tick or
more". Losses at seven replicas against a module checked and proved at five. Say which constants a result is at, and
when the record's are others, say that it was not checked at those.

**A decision is stated in a record that no module states (M-1, M-2).** Note it in Open obligations or the condition
rather than let the citation imply it.

**A citation is mis-assigned (ADR-0024 E1).** One sentence cited Moon & Varshney §4.6 for the half of a claim that
source says nothing about. Check what each citation in a sentence supports.

**Digests are copied rather than computed.** A record citing a file by digest should get it from the file.

**An overlay relaxes the archetype and doesn't say so (R-9).** If a record relaxes something accepted, an Overlay
position section says what it would owe on admission, and which criterion (often C3) would attach.
