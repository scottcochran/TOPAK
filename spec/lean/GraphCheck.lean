import GraphCheckCore
import TopakSpec.Mirror.Seats
import TopakSpec.Mirror.FloorComposition
/-!
# Checking the Seats and FloorComposition encodings against TLC's state graphs

`graph-check.sh` has TLC dump every reachable state and transition of `Seats.tla` and `FloorComposition.tla` at their
configured constants, under every `Mut`, with a derived variable `props` carrying each property's value, and
`dot2lines.py` turns each dump into lines. This program decodes them and evaluates the module's Lean encoding on them
through its proved mirror (`TopakSpec/Mirror/Seats.lean`, `TopakSpec/Mirror/FloorComposition.lean`), with
`GraphCheckCore.lean`'s `check`:

1. every TLC edge is a step of the encoding's `Next` (through `next_iff`: the target is among `succC`);
2. every step of the encoding's `Next` from a TLC state is a TLC edge, or leaves the state as it is;
3. the TLC initial states are exactly the encoding's `Init` (through `init_iff`);
4. each property the encoding states has, in every TLC state, the value TLC gave it.

With 1 to 3 the encoding and the module reach the same states by the same steps, at those constants. The mirror's
theorems are proved; this evaluation is a test.

usage: `graphcheck <module> <mut> <graph.lines>`, the module `Seats` or `FloorComposition`
-/

open Lean

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
