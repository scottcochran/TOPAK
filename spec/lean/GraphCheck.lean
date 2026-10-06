import Lean.Data.Json
import Std.Data.HashMap
import TopakSpec.Mirror.Seats
import TopakSpec.Mirror.FloorComposition
/-!
# Checking a re-encoding against TLC's state graph

`graph-check.sh` has TLC dump every reachable state and transition of a TLA+ module at its configured constants, with
a derived variable `props` carrying each property's value, and `dot2lines.py` turns the dump into lines. This program
reads them and, for the module's Lean encoding through its proved mirror (`TopakSpec/Mirror/*.lean`), checks:

1. every TLC edge is a step of the encoding's `Next` (through `next_iff`: the target is among `succC`);
2. every step of the encoding's `Next` from a TLC state is a TLC edge, or leaves the state as it is;
3. the TLC initial states are exactly the encoding's `Init` (through `init_iff`);
4. each property the encoding states has, in every TLC state, the value TLC gave it.

With 1 to 3 the encoding and the module reach the same states by the same steps, at those constants. The mirror's
theorems are proved; this evaluation is a test.

usage: `graphcheck <module> <mut> <graph.lines>`
-/

open Lean Std

structure Graph (α : Type) where
  states : HashMap String α
  props : HashMap String Json
  init : Array String
  edges : Array (String × String)
  succ : HashMap String (Array String)

def readGraph (decode : Json → Except String α) (path : String) : IO (Graph α) := do
  let lines ← IO.FS.lines path
  let mut states : HashMap String α := {}
  let mut props : HashMap String Json := {}
  let mut init := #[]
  let mut edges := #[]
  let mut succ : HashMap String (Array String) := {}
  for line in lines do
    if line.startsWith "S " then
      let id := (line.splitOn " ").getD 1 ""
      let j ← IO.ofExcept (Json.parse (line.drop ("S " ++ id ++ " ").length).toString)
      states := states.insert id (← IO.ofExcept (decode j))
      props := props.insert id ((j.getObjVal? "props").toOption.getD Json.null)
    else if line.startsWith "I " then
      init := init.push (line.drop 2).toString
    else if line.startsWith "E " then
      match line.splitOn " " with
      | [_, a, b] =>
        edges := edges.push (a, b)
        succ := succ.insert a ((succ.getD a #[]).push b)
      | _ => throw (IO.userError s!"bad edge line {line}")
  pure { states, props, init, edges, succ }

/-- What a module supplies: its mirror's successors, equality, initial state and properties. -/
structure Mirror (α : Type) where
  decode : Json → Except String α
  succ : α → List α
  eq : α → α → Bool
  cInit : α
  props : List (String × (α → Bool))

def check [Inhabited α] (name : String) (M : Mirror α) (path : String) : IO Bool := do
  let g ← readGraph M.decode path
  let get := fun id => g.states.get! id
  let mut bad : Array String := #[]
  -- 1. every TLC edge is a Next step
  let mut n1 := 0
  for (a, b) in g.edges do
    if !(M.succ (get a)).any (M.eq · (get b)) then
      n1 := n1 + 1
      if bad.size < 5 then bad := bad.push s!"edge {a} -> {b} is not a Next step"
  -- 2. every Next step from a TLC state is a TLC edge or a stutter
  let mut n2 := 0
  let mut nsteps := 0
  for (a, s) in g.states.toList do
    let tlc := (g.succ.getD a #[]).map get
    for d in M.succ s do
      nsteps := nsteps + 1
      if !(M.eq d s || tlc.any (M.eq d ·)) then
        n2 := n2 + 1
        if bad.size < 5 then bad := bad.push s!"a Next step from {a} is not a TLC edge"
  -- 3. Init
  let initOk := g.init.size == 1 && g.init.all fun i => M.eq (get i) M.cInit
  if !initOk then bad := bad.push s!"the initial states differ ({g.init.size} in TLC)"
  -- 4. properties
  let mut propLines : Array String := #[]
  for (pn, pf) in M.props do
    let mut disagree := 0
    let mut falses := 0
    for (a, s) in g.states.toList do
      let tlcVal := ((g.props.getD a Json.null).getObjValAs? Bool pn).toOption
      let leanVal := pf s
      if !leanVal then falses := falses + 1
      if tlcVal != some leanVal then
        disagree := disagree + 1
        if bad.size < 5 then bad := bad.push s!"{pn} at {a}: TLC {tlcVal}, Lean {leanVal}"
    propLines := propLines.push s!"{pn} agrees on {g.states.size - disagree} of {g.states.size} states, false in {falses}"
  let ok := n1 == 0 && n2 == 0 && initOk && bad.isEmpty
  IO.println s!"{name} | {g.states.size} states · {g.edges.size} edges · {nsteps} Next steps · {g.init.size} initial | {if ok then "MATCH" else "MISMATCH"}"
  IO.println s!"  edges not Next steps: {n1} · Next steps not TLC edges: {n2} · Init {if initOk then "agrees" else "DIFFERS"} · {String.intercalate " · " propLines.toList}"
  for b in bad do IO.println s!"  {b}"
  pure ok

/-! ## Seats -/

namespace SeatsG
open Topak.Spec.Seats Topak.Spec.Seats.Mirror

def field (j : Json) (k : String) : Except String Json := j.getObjVal? k
def setStrs (j : Json) : Except String (Array String) := do (← (← field j "$s").getArr?).mapM (·.getStr?)

def act? : String → Except String Act
  | "Read" => pure .Read | "Draft" => pure .Draft | "Emit" => pure .Emit | "Vote" => pure .Vote
  | s => throw s!"act {s}"
def kind? : String → Except String Kind
  | "thinker" => pure .thinker | "observer" => pure .observer | "grant" => pure .grant | s => throw s!"kind {s}"
def principal? : String → Except String (Option Principal)
  | "p1" => pure (some .p1) | "p2" => pure (some .p2) | "none" => pure none | s => throw s!"principal {s}"

def lease? (j : Json) : Except String CLease := do
  let live ← (← field j "live").getBool?
  let p ← principal? (← (← field j "principal").getStr?)
  let acts ← (← setStrs (← field j "alphabet")).mapM act?
  pure ⟨live, p, fun a => acts.contains a⟩

def decode (j : Json) : Except String CState := do
  let l ← field j "lease"
  let l1 ← lease? (← field l "s1")
  let l2 ← lease? (← field l "s2")
  let l3 ← lease? (← field l "s3")
  let recs ← (← (← field (← field j "acted") "$s").getArr?).mapM fun r => do
    pure (← act? (← (← field r "act").getStr?), ← kind? (← (← field r "kind").getStr?))
  pure ⟨fun | .s1 => l1 | .s2 => l2 | .s3 => l3, fun a k => recs.contains (a, k)⟩

instance : Inhabited CState := ⟨cInit⟩

def mut? : String → Except String Mut
  | "none" => pure .none | "M_KIND" => pure .M_KIND | "M_SEAT" => pure .M_SEAT | s => throw s!"Mut {s}"

def mirror (m : Mut) : Mirror CState :=
  { decode, succ := succC m, eq := eqC, cInit,
    props := [("OnlyThinkersAuthor", otaB), ("OneSeatPerPrincipal", ospB)] }

end SeatsG

/-! ## FloorComposition -/

namespace FloorCompositionG
open Topak.Spec.FloorComposition Topak.Spec.FloorComposition.Mirror

def field (j : Json) (k : String) : Except String Json := j.getObjVal? k
def str (j : Json) (k : String) : Except String String := do (← field j k).getStr?
def bool (j : Json) (k : String) : Except String Bool := do (← field j k).getBool?

def owner? : String → Except String (Option Seat)
  | "s1" => pure (some .s1) | "s2" => pure (some .s2) | "none" => pure none | s => throw s!"owner {s}"
def sealed? : String → Except String (Option Bool)
  | "yes" => pure (some true) | "no" => pure (some false) | "none" => pure none | s => throw s!"sealed {s}"

def rec? (j : Json) : Except String Rec := do pure ⟨← owner? (← str j "owner"), ← sealed? (← str j "sealed")⟩

def store? (j : Json) : Except String (Target → Rec) := do
  let r1 ← rec? (← field j "t1")
  let r2 ← rec? (← field j "t2")
  pure fun | .t1 => r1 | .t2 => r2

def decode (j : Json) : Except String CState := do
  pure ⟨← store? (← field j "truth"), ← store? (← field j "fstore"), ← bool j "admitNoFloor", ← bool j "admitWithErr",
    ← bool j "admitNoBundle", ← bool j "admitOutside", ← bool j "sawAdmit", ← bool j "sawNarrow",
    ← bool j "sawFloorErr"⟩

instance : Inhabited CState := ⟨cInit⟩

def mut? : String → Except String Mut
  | "none" => pure .none | "M_OVERRIDE" => pure .M_OVERRIDE | "M_ERR" => pure .M_ERR
  | "M_FAILOPEN" => pure .M_FAILOPEN | "M_WRITE" => pure .M_WRITE | s => throw s!"Mut {s}"

def mirror (m : Mut) : Mirror CState :=
  { decode, succ := succC m, eq := eqC, cInit,
    props := [("AdmitImpliesFloorPermit", aifpB), ("FloorErrorIsDeny", fedB), ("BundleRefusalHonored", brhB),
              ("BundleCannotWriteFloorInputs", bcwB), ("EnvelopeHolds", envB)] }

end FloorCompositionG

def main (args : List String) : IO UInt32 := do
  match args with
  | ["Seats", m, path] =>
    let mm ← IO.ofExcept (SeatsG.mut? m)
    pure (if ← check s!"Seats Mut={m}" (SeatsG.mirror mm) path then 0 else 1)
  | ["FloorComposition", m, path] =>
    let mm ← IO.ofExcept (FloorCompositionG.mut? m)
    pure (if ← check s!"FloorComposition Mut={m}" (FloorCompositionG.mirror mm) path then 0 else 1)
  | _ =>
    IO.println "usage: graphcheck <module> <mut> <graph.lines>"
    pure 2
