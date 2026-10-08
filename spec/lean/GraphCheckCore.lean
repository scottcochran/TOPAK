import Lean.Data.Json
import Std.Data.HashMap
/-!
# Checking a re-encoding against TLC's state graph: the reading and the check

A graph-check script has TLC dump every reachable state and transition of a TLA+ module at its configured constants,
with a derived variable `props` carrying each property's value, and `dot2lines.py` turns the dump into lines.
`readGraph` reads them, decoding each state with the module's decoder, and `check` evaluates the module's Lean
encoding on them through its proved mirror (`TopakSpec/Mirror/*.lean`). It checks:

1. every TLC edge is a step of the relation whose successors the mirror's `succ` lists, which the mirror proves are
   the encoding's `Next` (`next_iff`) or, for `Emergency_live`, its `NextL` (`nextL_iff`); `rel` only names that
   relation in the output;
2. every step of that relation from a TLC state is a TLC edge, or leaves the state as it is;
3. the TLC initial states are exactly the encoding's `Init` (through `init_iff`);
4. each property the encoding states has, in every TLC state, the value TLC gave it.

With 1 to 3 the encoding and the module reach the same states by the same steps, at those constants. The mirror's
theorems are proved; this evaluation is a test.

Nothing here is of one module. Each checker supplies its modules' decoders and mirrors and is an executable of its
own, with its own script and results series (`lakefile.toml`): `GraphCheck.lean` and `GraphCheckEmergency.lean`.
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

/-- What a module supplies: its mirror's successors, equality, initial state and properties, and the name of the
relation the successors are of. -/
structure Mirror (α : Type) where
  decode : Json → Except String α
  succ : α → List α
  eq : α → α → Bool
  cInit : α
  props : List (String × (α → Bool))
  rel : String := "Next"

def check [Inhabited α] (name : String) (M : Mirror α) (path : String) : IO Bool := do
  let g ← readGraph M.decode path
  let get := fun id => g.states.get! id
  let mut bad : Array String := #[]
  -- 1. every TLC edge is a step of the relation
  let mut n1 := 0
  for (a, b) in g.edges do
    if !(M.succ (get a)).any (M.eq · (get b)) then
      n1 := n1 + 1
      if bad.size < 5 then bad := bad.push s!"edge {a} -> {b} is not a {M.rel} step"
  -- 2. every step of the relation from a TLC state is a TLC edge or a stutter
  let mut n2 := 0
  let mut nsteps := 0
  for (a, s) in g.states.toList do
    let tlc := (g.succ.getD a #[]).map get
    for d in M.succ s do
      nsteps := nsteps + 1
      if !(M.eq d s || tlc.any (M.eq d ·)) then
        n2 := n2 + 1
        if bad.size < 5 then bad := bad.push s!"a {M.rel} step from {a} is not a TLC edge"
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
  IO.println s!"{name} | {g.states.size} states · {g.edges.size} edges · {nsteps} {M.rel} steps · {g.init.size} initial | {if ok then "MATCH" else "MISMATCH"}"
  IO.println s!"  edges not {M.rel} steps: {n1} · {M.rel} steps not TLC edges: {n2} · Init {if initOk then "agrees" else "DIFFERS"} · {String.intercalate " · " propLines.toList}"
  for b in bad do IO.println s!"  {b}"
  pure ok
