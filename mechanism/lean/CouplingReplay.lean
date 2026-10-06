import Lean.Data.Json
import Topak.CouplingModel
/-!
# Replaying the reference's recorded traces through the Coupling-shaped model

As `SeatsReplay.lean`, through `Topak.CouplingModel.rapply`, the function `Topak/CouplingModel.lean`'s proofs are
about, which runs the Seats-shaped step with the coupling checks folded into its gate. Each recorded entry is
applied with `ok` set to whether the reference applied it; after each step the model's leases, live index, seat
kinds and `last_applied` are compared with the reference's projection as before, and so are each lease's epoch,
round, sequence number and action count, the fleet epoch, every watermark, every seal and every seat's last round.
`K` and the round bounds are read from the projection.

A MATCH means the model took the reference's step at every entry of the trace: where the reference applied an
entry the model's own checks, the coupling checks among them, passed and its effect was the reference's. A test of
the model against the code, not a proof.

usage: `lake env lean --run CouplingReplay.lean <trace.jsonl>...`
-/

open Lean Topak.SeatsModel Topak.CouplingModel

abbrev St := RState String String String
abbrev En := REntry String String String
abbrev Tp := Topic String

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

def domainOf? : String → Option Domain
  | "build" => some .build | "run" => some .run | _ => none

/-- The issued seats: each one's kind, domain and cell. -/
def declsOf (seats : Json) : Except String (Array (String × SeatKind × Domain × Option String)) := do
  (← fnPairs seats).mapM fun (k, v) => do
    let s ← k.getStr?
    let kd ← str v "kind"
    let dm ← str v "domain"
    let c ← field v "cell"
    let cell := if isNone c then none else (c.getStr?).toOption
    match seatKind? kd, domainOf? dm with
    | some x, some d => pure (s, x, d, cell)
    | _, _ => throw s!"unknown seat kind or domain {kd} {dm}"

/-- `<<seat, epoch, round>>`. -/
def topicOf? (j : Json) : Except String Tp := do
  let a ← j.getArr?
  if h : a.size = 3 then pure (← a[0].getStr?, ← a[1].getNat?, ← a[2].getNat?) else throw "a topic is not a triple"

def lxOf (j : Json) : Except String LX := do
  pure { epoch := ← nat j "epoch", round := ← nat j "round", seq := ← nat j "seq", actions := ← nat j "actions" }

def marksOf (state : Json) : Except String (Array ((String × Tp) × Nat)) := do
  let os ← fnPairs (← field state "marks")
  let mut out := #[]
  for (o, m) in os do
    let o ← o.getStr?
    for (t, w) in ← fnPairs m do
      out := out.push ((o, ← topicOf? t), ← w.getNat?)
  pure out

def sealsOf (state : Json) : Except String (Array (String × (Tp × Nat))) := do
  (← fnPairs (← field state "seals")).mapM fun (k, v) => do
    pure (← k.getStr?, (← topicOf? (← field v "topic"), ← nat v "seq"))

def natMapOf (state : Json) (k : String) : Except String (Array (String × Nat)) := do
  (← fnPairs (← field state k)).mapM fun (k, v) => do pure (← k.getStr?, ← v.getNat?)

def lookupF (xs : Array (Nat × α)) (f : Nat) : Option α := (xs.find? (·.1 == f)).map (·.2)

/-- The model state the reference's projection describes. `acted` starts empty: the model's history variable. -/
def stateOf (state : Json) : Except String St := do
  let ds ← declsOf (← field state "seats")
  let ls ← leasesOf state
  let lxs ← (← fnPairs (← field state "leases")).mapM fun (k, v) => do pure (← k.getNat?, ← lxOf v)
  let lbs ← lbsOf state
  let ms ← marksOf state
  let ss ← sealsOf state
  let lr ← natMapOf state "lastRound"
  let base : MState String String String :=
    { kinds := lookup (ds.map fun (s, k, _, _) => (s, k)), leases := lookupF ls, liveBySeat := lookup lbs,
      last := ← nat state "lastApplied", acted := [] }
  let x : XState String :=
    { seats := (ds.map (·.1)).toList, domain := lookup (ds.map fun (s, _, d, _) => (s, d)),
      cell := fun s => (lookup (ds.map fun (s, _, _, c) => (s, c)) s).bind id,
      epoch := ← nat state "epoch", lx := fun f => (lookupF lxs f).getD ⟨0, 0, 0, 0⟩,
      marks := fun o t => (lookup' ms (o, t)).getD 0, seals := lookup ss, lastRound := lookup lr }
  pure { base, x }
where lookup' (xs : Array ((String × Tp) × Nat)) (k : String × Tp) := (xs.find? (·.1 == k)).map (·.2)

def paramsOf (state : Json) : Except String Params := do
  pure { K := ← nat state "k", buildBound := ← nat state "buildBound", runBound := ← nat state "runBound" }

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
    (← alphabetOf (← field g "alphabet")) (← nat g "round"))

def renewOf (r : Json) : Except String En := do
  pure (.renew (← str r "seat") (← nat r "fence") (← alphabetOf (← field r "alphabet")))

/-- The admitted action's kind, as `probe_action` reads it: a heartbeat is the `Emit` or `Report` it travels by,
and carries its topic and watermark. -/
def admitOf (a : Json) : Except String (ActionKind × Option (Tp × Nat)) := do
  let k ← str a "kind"
  if k == "Heartbeat" then
    let v ← str a "via"
    match actKind? v with
    | some x => pure (x, some (← topicOf? (← field a "topic"), ← nat a "watermark"))
    | none => throw s!"unknown heartbeat via {v}"
  else
    match actKind? k with | some x => pure (x, none) | none => throw s!"unknown admitted kind {k}"

def entryOf (e : Json) : Except String En := do
  match ← str e "kind" with
  | "Grant" => grantOf e
  | "Activate" =>
    pure (.grant (← str e "seat") (← str e "person") (← str e "persona") (← str e "conf")
      (fun a => a == .Consult || a == .Actuate || a == .Report) (← nat e "round"))
  | "Renew" => renewOf e
  | "Admit" =>
    let (a, hb) ← admitOf (← field e "action")
    pure (.admit (← str e "seat") (← nat e "lease") a hb)
  | "EndRound" => pure (.endRound (← str e "seat") (← nat e "fence"))
  | "Revoke" => pure (.revoke (← targetOf (← field e "target")))
  | "Contested" => pure (.revoke (.principal (← str (← field e "appraisal") "principal")))
  | "EpochIncrement" => pure .fence
  | "Issue" => do
    let ds ← declsOf (← field (← field e "rules") "seats")
    pure (.issue (lookup (ds.map fun (s, k, _, _) => (s, k))) (lookup (ds.map fun (s, _, d, _) => (s, d)))
      (fun s => (lookup (ds.map fun (s, _, _, c) => (s, c)) s).bind id) (ds.map (·.1)).toList)
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

def tpStr (t : Tp) : String := s!"<<{t.1}, {t.2.1}, {t.2.2}>>"

/-- Every difference between the model's fields and the reference's projection. `written` is every
(observer, topic) a heartbeat of the trace has set, so that a watermark the model holds and the reference does
not is found. -/
def compare (st : St) (state : Json) (written : List (String × Tp)) : Except String (List String) := do
  let ls ← leasesOf state
  let lxs ← (← fnPairs (← field state "leases")).mapM fun (k, v) => do pure (← k.getNat?, ← lxOf v)
  let lbs ← lbsOf state
  let ds ← declsOf (← field state "seats")
  let ms ← marksOf state
  let ss ← sealsOf state
  let lr ← natMapOf state "lastRound"
  let last ← nat state "lastApplied"
  let ep ← nat state "epoch"
  let b := st.base
  let x := st.x
  let mut out : List String := []
  if b.last != last then out := s!"lastApplied {b.last}, reference {last}" :: out
  if x.epoch != ep then out := s!"epoch {x.epoch}, reference {ep}" :: out
  let maxF := ls.foldl (fun m (f, _) => max m f) b.last
  for f in List.range (maxF + 1) do
    match b.leases f, ls.find? (·.1 == f) with
    | none, none => pure ()
    | some r, none => out := s!"fence {f}: model {recStr r}, reference none" :: out
    | none, some (_, r) => out := s!"fence {f}: model none, reference {recStr r}" :: out
    | some r, some (_, r') =>
      if !recEq r r' then out := s!"fence {f}: model {recStr r}, reference {recStr r'}" :: out
      match lookupF lxs f with
      | some l => if x.lx f != l then out := s!"fence {f}: model {reprStr (x.lx f)}, reference {reprStr l}" :: out
      | none => out := s!"fence {f}: no epoch, round, seq or actions in the reference" :: out
  let seats := (lbs.map (·.1)).toList ++ (ds.map (·.1)).toList ++ (ss.map (·.1)).toList ++ (lr.map (·.1)).toList ++
    ((List.range (maxF + 1)).filterMap fun f => (b.leases f).map (·.seat))
  for s in seats.eraseDups do
    if b.liveBySeat s != lookup lbs s then
      out := s!"liveBySeat {s}: model {b.liveBySeat s}, reference {lookup lbs s}" :: out
    if b.kinds s != lookup (ds.map fun (s, k, _, _) => (s, k)) s then out := s!"seat {s}: kind differs" :: out
    if x.domain s != lookup (ds.map fun (s, _, d, _) => (s, d)) s then out := s!"seat {s}: domain differs" :: out
    if x.cell s != (lookup (ds.map fun (s, _, _, c) => (s, c)) s).bind id then out := s!"seat {s}: cell differs" :: out
    if x.seals s != lookup ss s then
      out := s!"seal {s}: model {(x.seals s).map fun (t, n) => (tpStr t, n)}, reference {(lookup ss s).map fun (t, n) => (tpStr t, n)}" :: out
    if x.lastRound s != lookup lr s then
      out := s!"lastRound {s}: model {x.lastRound s}, reference {lookup lr s}" :: out
  if x.seats != (ds.map (·.1)).toList then out := "the seat list differs" :: out
  for (o, t) in ((ms.map (·.1)).toList ++ written).eraseDups do
    let want := ((ms.find? (·.1 == (o, t))).map (·.2)).getD 0
    if x.marks o t != want then out := s!"mark {o} {tpStr t}: model {x.marks o t}, reference {want}" :: out
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
  let init ← field first "init"
  let P ← paramsOf init
  let mut st ← stateOf init
  let mut written : List (String × Tp) := []
  let mut t := t
  let mut i := 0
  for line in lines[1:] do
    i := i + 1
    if line.isEmpty then continue
    let j ← Json.parse line
    let e ← entryOf (← field j "entry")
    let want ← expected (← field j "applied")
    let ok := want != .rejected
    let (st', got) := rapply P st (← nat j "index") e ok
    t := bump { t with steps := t.steps + 1 } (resultName got)
    -- what the coupling checks were exercised on
    match e, got with
    | .admit _ _ _ (some _), .admitted => t := bump t "heartbeats admitted"
    | .admit seat _ a none, .admitted => if coupled st seat a none then t := bump t "coupled admits"
    | .grant seat _ _ _ _ _, .granted _ =>
      if st.x.domain seat = some .run ∧ st.base.kinds seat = some .Thinker ∧ (st.x.seals seat).isSome then
        t := bump t "cross-round grants"
    | .admit _ _ _ (some _), .rejected => t := bump t "heartbeats refused"
    | _, _ => pure ()
    if got != want then
      return (t, some s!"step {i}: model {reprStr got}, reference {reprStr want}")
    if let .admit seat _ _ (some (T, _)) := e then written := (seat, T) :: written
    let diffs ← compare st' (← field j "state") written
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
