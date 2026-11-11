# Proving

## The shape

```lean
inductive Reachable {σ} (Init : σ → Prop) (Next : σ → σ → Prop) : σ → Prop
  | init {s} : Init s → Reachable Init Next s
  | step {s s'} : Reachable Init Next s → Next s s' → Reachable Init Next s'

theorem invariant {σ} {Init : σ → Prop} {Next : σ → σ → Prop} (Inv P : σ → Prop)
    (hinit : ∀ s, Init s → Inv s)
    (hstep : ∀ s s', Inv s → Next s s' → Inv s')
    (hP : ∀ s, Inv s → P s) :
    ∀ s, Reachable Init Next s → P s
```

That induction is the temporal step another prover may leave unchecked, and here the kernel checks it.

A worked property:

```lean
/-- `Alphabets`: under the specified grant a live alphabet is the seat's kind bound. -/
def Alphabets (st : State) : Prop :=
  ∀ s, (st.lease s).live → (st.lease s).alphabet = KindBound (KindOf s)

def InvA (st : State) : Prop := Alphabets st ∧ OnlyThinkersAuthor st

theorem InitInvA (st : State) (h : Init st) : InvA st := ...

theorem NextInvA (m : Mut) (hm : m ≠ .M_KIND) (st st' : State) (hi : InvA st) (hn : Next m st st') :
    InvA st' := by
  obtain ⟨hA, hO⟩ := hi
  obtain ⟨s, hs⟩ := hn
  rcases hs with ⟨hlive, ⟨a, ha, hacted⟩, hlease⟩ | ⟨-, hlease, hacted⟩ | ⟨p, -, -, hlease, hacted⟩
  · -- Act(s)
    ...
  · -- EndRound(s)
    ...
  · -- Grant(p, s): the issued alphabet is the kind bound, since Mut # "M_KIND"
    ...

/-- `THEOREM OnlyThinkersAuthorAlways == ASSUME Mut # "M_KIND" PROVE Spec => []OnlyThinkersAuthor` -/
theorem OnlyThinkersAuthorAlways (m : Mut) (hm : m ≠ .M_KIND) :
    ∀ st, Reachable Init (Next m) st → OnlyThinkersAuthor st :=
  invariant InvA OnlyThinkersAuthor InitInvA (NextInvA m hm) (fun _ h => h.2)

#print axioms OnlyThinkersAuthorAlways
```

The `rcases` pattern mirrors the action's conjunction, and each case has a comment naming the action. The theorem's
doc-comment is the other proof's `THEOREM` line.

**Mutation lemmas.** One per mutation, saying what it admits, stated of the action:

```lean
/-- `MutKindGrantsAll`: under M_KIND a grant issues every act. -/
theorem MutKindGrantsAll (p : Principal) (s : Seat) (st st' : State) (h : Grant .M_KIND p s st st') :
    (st'.lease s).alphabet = Acts := ...
```

Counterexamples stay with the model checker. A Lean theorem is universal.

**Where you may depart from the other proof.** The invariants should be the original proof's. Add one only where the
encoding needs it, and say so in the header: a `Decided` invariant so a step can case on an `IF` without choice, or a
bound for an `ENABLED` theorem. `TypeOK` has no counterpart.

**A theorem may be stronger than its source.** An assumption the proof never uses is a finding: report that the claim
holds without it. A constant bound the original proof needed may simply disappear.

## The prover's habits

- `omega` does not unfold definitions. Destructure `Rounds c r` and the like first.
- `simp only [upd_same, upd_other …]` must also be applied to hypotheses (`at h ⊢`), or a hypothesis about the old
  state no longer matches. After `simp only`, `a = a` is `True`: close it with `trivial`, not `rfl`.
- A term-mode `by …` inside `⟨…, …⟩` swallows the comma after it. Parenthesize it.
- `by decide` on a proposition about a structure literal with free variables fails. `by simp` does it.
- `by_contra` and `push_neg` are Mathlib's. Use `by_cases` and `absurd` in a package without it.
- Case on the finite types and let simp finish: `cases s <;> cases a <;> simp_all [KindBound, KindOf, Authoring]`.
- For `upd`, `by_cases hts : t = s`, then `subst` on one branch and `upd_other _ _ _ _ hts` on the other.
- A `Prop`-valued structure field means `simp [NoLease] at hs` will close `False` cases that `rfl` will not.
- In a verified semantics built by well-founded recursion the kernel's `decide` cannot reduce maps and sets. Closed
  evaluations there use `native_decide`, which trusts the compiler and shows one axiom per use.

## Axioms

| Axiom | Status |
|---|---|
| `propext`, `Quot.sound` | Expected |
| `Classical.choice` | Only where a step cases on an undecidable condition, as a set membership. Name it in the header. If a lemma seems to need it, check whether stating it over reachable states avoids it. A theorem proved to require excluded middle is worth stating. |
| `<theorem>._native.native_decide.ax_1_1` | From `native_decide`. Only for closed evaluation in a verified semantics, and it appears once per use. |
| `sorryAx` | Never in a result. |
| Anything else | A new premise. Stop and say so. |

`lean_lint.py` catches `sorry`, `axiom`, `native_decide`, `unsafe`, `implemented_by`, `extern` and
`debug.skipKernelTC` in source.
