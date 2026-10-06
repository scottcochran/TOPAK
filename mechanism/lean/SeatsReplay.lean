import Lean.Data.Json
import Topak.SeatsModel
/-!
# Replaying the reference's recorded traces through the Seats-shaped model

`crates/topak-core/src/trace.rs` records, for every applied entry, the entry, the result and a projection of the
state after it (`TOPAK_TRACE_DIR`). This program runs each recorded trace through `Topak.SeatsModel.apply`, the
same function the proofs in `Topak/SeatsModel.lean` are about, starting from the projection of the first state.
Each entry is applied with `ok` set to whether the reference applied it, and after each step the model's leases
(seat, principal, Persona, confinement digest, alphabet, ended or not), its `live_by_seat`, its seat kinds and its
`last_applied` are compared with the reference's projection, and the model's result with the reference's.

A MATCH means the model took the reference's step at every entry of the trace: wherever the reference applied an
entry the model's own checks passed and its effect was the reference's, and wherever the reference refused one the
model's fields were left as the reference left them. A test of the model against the code, not a proof.

usage: `lake env lean --run SeatsReplay.lean <trace.jsonl>...`
-/

open Lean Topak.SeatsModel

abbrev St := MState String String String
abbrev En := MEntry String String String

def actKind? : String → Option ActionKind
  | "Read" => some .Read | "Draft" => some .Draft | "Invoke" => some .Invoke | "Emit" => some .Emit
  | "Submit" => some .Submit | "Vote" => some .Vote | "Consult" => some .Consult | "Actuate" => some .Actuate
  | "Report" => some .Report | _ => none

def seatKind? : String → Option SeatKind
  | "thinker" => some .Thinker | "observer" => some .Observer | "grant" => some .Grant
  | "operator" => some .Operator | "emergency" => some .Emergency | _ => none

def field (j : Json) (k : String) : Except String Json := j.getObjVal? k
def str (j : Json) (k : String) : Except String String := do (← field j k).getStr?
def nat (j : Json) (k : String) : Except String Nat := do (← field j k).getNat?
def isNone (j : Json) : Bool := match j.getStr? with | .ok "none" => true | _ => false

/-- `{"$s": [..]}`. -/
def setItems (j : Json) : Except String (Array Json) := do (← field j "$s").getArr?

/-- `{"$f": [[k, v], ..]}`. -/
def fnPairs (j : Json) : Except String (Array (Json × Json)) := do
  let a ← (← field j "$f").getArr?
  a.mapM fun p => do
    let p ← p.getArr?
    if h : p.size = 2 then pure (p[0], p[1]) else throw "a function pair is not a pair"

def alphabetOf (j : Json) : Except String Alphabet := do
  let ks ← (← setItems j).mapM fun i => do
    let s ← i.getStr?
    match actKind? s with | some k => pure k | none => throw s!"unknown action kind {s}"
  pure fun a => ks.contains a

def alphaEq (α β : Alphabet) : Bool := ActionKind.all.all fun a => α a == β a

def alphaStr (α : Alphabet) : String := toString ((ActionKind.all.filter α).map fun a => reprStr a)

def kindsOf (seats : Json) : Except String (Array (String × SeatKind)) := do
  (← fnPairs seats).mapM fun (k, v) => do
    let s ← k.getStr?
    let kd ← str v "kind"
    match seatKind? kd with | some x => pure (s, x) | none => throw s!"unknown seat kind {kd}"

def lookup (xs : Array (String × α)) (k : String) : Option α := (xs.find? (·.1 == k)).map (·.2)

def recOf (j : Json) : Except String (Rec String String String) := do
  pure { seat := ← str j "seat", principal := ← str j "principal", persona := ← str j "persona",
         conf := ← str j "conf", alphabet := ← alphabetOf (← field j "alphabet"),
         live := isNone (← field j "ended") }

def leasesOf (state : Json) : Except String (Array (Nat × Rec String String String)) := do
  (← fnPairs (← field state "leases")).mapM fun (k, v) => do pure (← k.getNat?, ← recOf v)

def lbsOf (state : Json) : Except String (Array (String × Nat)) := do
  (← fnPairs (← field state "liveBySeat")).mapM fun (k, v) => do pure (← k.getStr?, ← v.getNat?)

/-- The model state the reference's projection describes. `acted` starts empty: the model's history variable. -/
def stateOf (state : Json) : Except String St := do
  let ks ← kindsOf (← field state "seats")
  let ls ← leasesOf state
  let lbs ← lbsOf state
  pure { kinds := lookup ks, leases := fun f => lookup' ls f, liveBySeat := lookup lbs,
         last := ← nat state "lastApplied", acted := [] }
where lookup' (ls : Array (Nat × Rec String String String)) (f : Nat) := (ls.find? (·.1 == f)).map (·.2)

def targetOf (t : Json) : Except String (RevTarget String String) := do
  let k ← str t "kind"
  let id ← str t "id"
  match k with
  | "principal" => pure (.principal id)
  | "persona" => pure (.persona id)
  | "confinement" => pure (.confinement id)
  | _ => throw s!"unknown revocation target {k}"

def grantOf (g : Json) : Except String En := do
  pure (.grant (← str g "seat") (← str g "principal") (← str g "persona") (← str g "conf")
    (← alphabetOf (← field g "alphabet")))

def renewOf (r : Json) : Except String En := do
  pure (.renew (← str r "seat") (← nat r "fence") (← alphabetOf (← field r "alphabet")))

/-- The admitted action's kind, as `probe_action` reads it: a heartbeat is the `Emit` or `Report` it travels by. -/
def admitKind (a : Json) : Except String ActionKind := do
  let k ← str a "kind"
  let k ← if k == "Heartbeat" then str a "via" else pure k
  match actKind? k with | some x => pure x | none => throw s!"unknown admitted kind {k}"

def entryOf (e : Json) : Except String En := do
  match ← str e "kind" with
  | "Grant" => grantOf e
  | "Activate" =>
    pure (.grant (← str e "seat") (← str e "person") (← str e "persona") (← str e "conf")
      fun a => a == .Consult || a == .Actuate || a == .Report)
  | "Renew" => renewOf e
  | "Admit" => pure (.admit (← str e "seat") (← nat e "lease") (← admitKind (← field e "action")))
  | "EndRound" => pure (.endRound (← str e "seat") (← nat e "fence"))
  | "Revoke" => pure (.revoke (← targetOf (← field e "target")))
  | "Contested" => pure (.revoke (.principal (← str (← field e "appraisal") "principal")))
  | "EpochIncrement" => pure .fence
  | "Issue" => do
    let ks ← kindsOf (← field (← field e "rules") "seats")
    pure (.issue (lookup ks))
  | "Control" => do
    let a ← field e "action"
    match ← str a "kind" with
    | "Regrant" => let g ← field e "grant"; if isNone g then pure .other else grantOf g
    | "Renew" => let r ← field e "renew"; if isNone r then pure .other else renewOf r
    | "EndRound" => pure (.endSeat (← str a "target"))
    | "Revoke" => pure (.revoke (← targetOf (← field a "target")))
    | "FenceEpoch" => pure .fence
    | _ => pure .other
  | _ => pure .other

/-- The reference's result, as the model's. -/
def expected (a : Json) : Except String MApplied := do
  match ← str a "kind" with
  | "LeaseGranted" => pure (.granted (← nat a "fence"))
  | "Renewed" => pure (.renewed (← nat a "fence"))
  | "Admitted" => pure .admitted
  | "RoundEnded" => pure .roundEnded
  | "Revoked" | "Contested" => pure .revoked
  | "EpochIncremented" => pure .fenced
  | "Issued" => pure .issued
  | "Rejected" | "Duplicate" => pure .rejected
  | _ => pure .unmodelled

def recEq (a b : Rec String String String) : Bool :=
  a.seat == b.seat && a.principal == b.principal && a.persona == b.persona && a.conf == b.conf &&
    alphaEq a.alphabet b.alphabet && a.live == b.live

def recStr (r : Rec String String String) : String :=
  s!"⟨{r.seat}, {r.principal}, {alphaStr r.alphabet}, {if r.live then "live" else "ended"}⟩"

/-- Every difference between the model's fields and the reference's projection. -/
def compare (st : St) (state : Json) : Except String (List String) := do
  let ls ← leasesOf state
  let lbs ← lbsOf state
  let ks ← kindsOf (← field state "seats")
  let last ← nat state "lastApplied"
  let mut out : List String := []
  if st.last != last then out := s!"lastApplied {st.last}, reference {last}" :: out
  let maxF := ls.foldl (fun m (f, _) => max m f) st.last
  for f in List.range (maxF + 1) do
    match st.leases f, ls.find? (·.1 == f) with
    | none, none => pure ()
    | some r, none => out := s!"fence {f}: model {recStr r}, reference none" :: out
    | none, some (_, r) => out := s!"fence {f}: model none, reference {recStr r}" :: out
    | some r, some (_, r') => if !recEq r r' then out := s!"fence {f}: model {recStr r}, reference {recStr r'}" :: out
  let seats := (lbs.map (·.1)).toList ++ (ks.map (·.1)).toList ++
    ((List.range (maxF + 1)).filterMap fun f => (st.leases f).map (·.seat))
  for s in seats.eraseDups do
    if st.liveBySeat s != lookup lbs s then
      out := s!"liveBySeat {s}: model {st.liveBySeat s}, reference {lookup lbs s}" :: out
    if st.kinds s != lookup ks s then out := s!"seat {s}: kind differs" :: out
  pure out.reverse

structure Tally where
  steps : Nat := 0
  byResult : List (String × Nat) := []

def bump (t : Tally) (k : String) : Tally :=
  { t with byResult := match t.byResult.find? (·.1 == k) with
    | some _ => t.byResult.map fun (k', n) => if k' == k then (k', n + 1) else (k', n)
    | none => t.byResult ++ [(k, 1)] }

def resultName : MApplied → String
  | .granted _ => "granted" | .renewed _ => "renewed" | .admitted => "admitted" | .roundEnded => "ended"
  | .revoked => "revoked" | .fenced => "fenced" | .issued => "issued" | .rejected => "rejected"
  | .unmodelled => "unmodelled"

/-- One trace: `none` on a MATCH, else the first step at which the model and the reference part. -/
def replay (lines : Array String) (t : Tally) : Except String (Tally × Option String) := do
  let first ← Json.parse lines[0]!
  let mut st ← stateOf (← field first "init")
  let mut t := t
  let mut i := 0
  for line in lines[1:] do
    i := i + 1
    if line.isEmpty then continue
    let j ← Json.parse line
    let e ← entryOf (← field j "entry")
    let want ← expected (← field j "applied")
    let ok := want != .rejected
    let (st', got) := apply st (← nat j "index") e ok
    t := bump { t with steps := t.steps + 1 } (resultName got)
    if got != want then
      return (t, some s!"step {i}: model {reprStr got}, reference {reprStr want}")
    let diffs ← compare st' (← field j "state")
    if !diffs.isEmpty then
      return (t, some s!"step {i}: {String.intercalate "; " diffs}")
    st := st'
  pure (t, none)

def main (args : List String) : IO UInt32 := do
  let mut t : Tally := {}
  let mut bad := 0
  let name := fun (p : String) => (System.FilePath.mk p).fileStem.getD p
  for path in (args.toArray.qsort fun a b => name a < name b).toList do
    let name := name path
    let lines ← IO.FS.lines path
    let before := t.steps
    match replay lines t with
    | .error e => IO.println s!"{name} | ERROR {e}"; bad := bad + 1
    | .ok (t', r) =>
      t := t'
      match r with
      | none => IO.println s!"{name} | {t'.steps - before} steps | MATCH"
      | some why => IO.println s!"{name} | MISMATCH at {why}"; bad := bad + 1
  IO.println ""
  IO.println s!"{args.length} traces · {t.steps} steps · {bad} not matching"
  IO.println s!"model results: {String.intercalate ", " (t.byResult.map fun (k, n) => s!"{k} {n}")}"
  pure (if bad == 0 then 0 else 1)
