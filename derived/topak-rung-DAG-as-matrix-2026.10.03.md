> Can the Rung/Theorem DAG of TOPAK best be represented as a Tensor?

**Verdict:** no. It is best represented as a **Boolean matrix**, the theorem × premise incidence matrix that
`spec/theorem-premise-binding.md` already is in prose. A tensor would add a dimension the data does not need. The
matrix form is now machine-readable as `spec/theorem-premise-binding.json`, and `spec/inventory.py` evaluates it.
This note follows `derived/topak-rung-DAG-2026.09.27.md`, which it does not revise.

## What the structure actually is

The 09.27 analysis draws the graph with two kinds of node. **Premise nodes** are the trusted-base rows (T-0045-n,
ADR-0045 Annex A), the degeneracy parameter values (ADR-0023 §6a) and the declared gaps. **Theorem nodes** are one
per checked property. Edges run from a theorem to every premise it needs, and the binding table is that edge list.
Read against the table as it stands, two things follow.

1. **The graph is bipartite and one level deep.** No row of the binding table names another theorem as a premise.
   Every edge runs from a theorem to a premise, so the "DAG" is a bipartite graph, and its natural form is one
   **incidence matrix**: *B[t][p] = 1* when theorem row *t* needs premise *p*. At this date that is 43 theorem rows
   against 48 premise columns: the five BASE rows, the 23 further T-rows the table cites, and 20 parameter,
   condition and gap premises. The G3 diagram (`diagrams/topak/G3-theorem-premise-dag-2026.10.02.svg`) already
   draws the binding as this matrix.
2. **Evaluating a deployment is one Boolean matrix operation.** A declaration is a 0/1 vector *d* over the premise
   columns. An undeclared, excluded or refused row is 0, and so is a parameter the declaration does not state
   (ADR-0045 §3, rule 1). Theorem *t* holds iff every premise it needs is 1:

   *holds = ¬(B · ¬d)*, over the Boolean semiring (AND for ·, OR for +).

   The output vector is the deployment's order ideal, ADR-0023 §2's inventory. `spec/inventory.py` computed this
   one row at a time from the table's text, for the T-row columns only. Given the JSON form, it now computes every
   column.

A theorem with several premises is a **directed hyperedge**, several premises to one theorem. Tensors represent
hypergraphs only when they are *k-uniform*, every hyperedge the same size. The binding's rows have between none and
nine non-BASE premises, and the standard representation for hyperedges of mixed size is exactly this bipartite
incidence matrix.

Three limits of the matrix form, stated so a reader does not take the JSON for more than it is:

- **It is a conjunction only.** Two premises in the table are disjunctions: a proved invariant rests on T-0045-31
  *in place of* T-0045-29 (the table's BASE paragraph), and the TLC rows still rest on T-0045-29. A matrix row cannot
  say "29 or 31". The JSON keeps the table's convention, BASE with T-0045-29, and records the proof module in
  `proved_in`. A deployment that wants credit for the prover alone needs a derived premise node, `checked`, that
  is true when either row is. That node is not added here because the table does not ask for it.
- **The parameter and gap columns are a transcription.** The table is canonical for its T-row premises, and
  `inventory.py --check` fails if the JSON disagrees with it at any rung. The other 20 columns are transcribed from
  the table's "Parameter and gap premises" column with struck text omitted (the two struck `K < R` premises). Nothing
  checks that transcription mechanically. The `kind` field separates ADR-0023 §6a parameters, each with the
  degeneracies that falsify it, from *conditions*, a record in force or a capability delivered, and from the
  table's declared *gaps*.
- **A `holds` is only as good as the declaration.** The matrix decides what follows from a declaration, not
  whether the declaration is true. A premise declared true is not thereby verified, which is the 09.29 reading of
  ADR-0036 R1 restated.

## Where a tensor axis does show up

**Rung-conditioned premises.** The table has cells like "at rung 3 T-0045-16, T-0045-17; at rung 2 T-0045-18;
at rung 1 T-0045-19", and Annex A limits some rows to some rungs ("confinement 1–3", "confinement 0"). Read
literally, that is a third-order tensor *B[t][p][r]*, theorem × premise × rung, with one matrix slice per rung.
`inventory.py`'s `rows_in` selects the slice.

The axis is almost entirely empty. Of the 43 rows, **four** change with the rung: `ContainedMeansConfined`,
`NoSilentDowngrade`, `ContestedStopped` and the effect-exclusivity claim. The other 39 are the same matrix row at
every rung. The JSON therefore stores the axis sparsely, as a rung-independent `rows` list plus a `rows_at_rung`
override on those four, so that *B(r) = B₀ + B_r*. That is the tensor stored as a matrix plus a sparse correction,
not a dense third dimension.

The 09.27 analysis already flattens the rest of the axis. It treats "confinement rung ≥ 2" as a **premise node**,
not as a dimension, and the JSON does the same: `confinement>=1` and `confinement>=2` are columns whose value is
`derived` from the declared rung. Flattening is the better choice for three reasons:

- **The rung parameterises one axis, not every premise.** It belongs to confinement (ADR-0034), and most premises
  have no rung at all. As a tensor dimension it would be almost entirely zeros, which the count above confirms.
- **"≥ k" premises are monotone**, so they are just more columns. A deployment at rung 2 has both `confinement>=1`
  and `confinement>=2` true, and the ordering is carried by the premises rather than by an index.
- **Further axes would each add a dimension.** Observer scoping, custody and coupling are axes too. As tensor
  dimensions each would multiply the shape, while under the 09.27 extension rule ("a new axis is a new family of
  premise nodes") each adds only columns. That rule is also what keeps ADR-0023's incomparable pairs visible:
  they are two ideals of one matrix, not two points on one index.

**When a tensor does make sense: analysing many evaluations at once.**

- **Deployment × theorem** across a set of declarations is a matrix of results.
- **Deployment × theorem × archetype version** is a third-order tensor. It answers "which deployments lost which
  theorems when the archetype moved", the question the archetype-evolution record (G6 item 7) has to answer, and
  it turns ToO §7.8's declaration debt into a computed fact.
- **Theorem × premise × archetype version** tracks premise edges added into existing theorems. ADR-0023's carried
  scope says each such edge weakens a theorem and needs a record of its own, and this tensor's diffs list them.

Even then, the numeric toolkit (CP or Tucker decomposition, embeddings) does not apply. The entries are Boolean
logic, not measurements. A low-rank approximation gives exactly the kind of summary the 09.27 analysis rejected
for theorem-count height, because ADR-0023 §2's point is *which* theorems hold, not how many or how similar.

## What was added with this note

- **`spec/theorem-premise-binding.json`**: the binding as the matrix above, with a `base` list, the row classes
  that count as holding, one entry per premise column (`kind`, `text`, `record`, `falsified_by`, and `derived` for
  the rung columns), and one entry per table row in the table's order (`names`, `checked_in`, `proved_in`, `rows`,
  `rows_at_rung`, `premises`).
- **`spec/inventory.py`**: given the JSON in place of the table, it evaluates *¬(B · ¬d)* for a declaration that
  carries `"premises": {"coupling-on": true, ...}` beside its rung and rows, and prints `holds` or `void` with the
  premises that fail. `inventory.py --check` compares the JSON's T-row premises with the table's at every rung.
  Table mode is unchanged except that a row now counts only when declared `trust root` or `delegated`, as the
  table's own rule says. Before, a `refused` row passed.
- **`spec/theorem-premise-binding.md`** gains a paragraph pointing at both, and the obligation that a change to a
  row's premises changes the JSON in the same commit.

No record, row, theorem or verdict changes. The JSON's versioning stays with the table's, under the archetype-
evolution record.
