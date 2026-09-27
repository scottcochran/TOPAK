> Is the following a feasible 1st pass on defining something which is mediated(a)?:
> 1. Local pretrained slm
> 2. Docker container
> 3. MlFlow

I'll look at the repo to see how "mediated" and the "(a)" notation are defined before answering.

**Verdict:** feasible, and almost too easy. Every principal in the corpus is `Mediated` today, so the risk is not that this stack fails the predicate. The risk is that the definition says nothing. At rung 0 the verdict is `Mediated` by ADR-0031 §3 before anyone looks at the SLM, the container or MLflow. The first pass is worth doing only as a *declared* `Mediated` principal: one whose out-of-band effect paths are named, so the verdict is derived from a profile rather than from the absence of one.

**How the three items map onto `Contained(p)`** (ADR-0034 §4 has three conjuncts; `Mediated` is failing any one):

- **Local pretrained SLM** satisfies the provenance conjunct. It is in house on ADR-0017's axis, and it is the same occupant the closure-options note recommended for the `Contained` witness. Say which role it plays. As the Persona it is the occupant. As a tool the principal `Invoke`s, it is a native tool and D-0034-3 makes the principal `Mediated` on that alone. Practical catch: the weights are portable safetensors, but `slm/model.py` is MLX only, and a Linux container has no Metal. You need a small numpy or torch loader for the preset, or a Linux GPU host.
- **Docker** is a mechanism, not a rung. The rung says how the mechanism's presence was established. If the node launches the container and asserts a profile digest in the grant, that is rung 1. A container started by hand is rung 0. Default Docker fails P1 (network device), P3 (shell, package manager, interpreter reachable) and P4 (native tools). It can pass P5 if the weights are baked into the image and P6 with one `docker run --rm` per grant. That pass/fail list is the definition of `Mediated(a)`.
- **MLflow** is the cleanest single witness. A tracking client inside the principal's reach is network egress and a path into an artifactory other than `Submit`, which ADR-0022 §6 forbids by name. So it is not incidental plumbing. It is the effect no action names.

**Decide what MLflow is before you build.** Inside the principal, it is the channel that makes `a` `Mediated`, and that is a fine thing for a first pass to demonstrate. Outside the principal, on the operator side, it is an experiment store, and then it must not become the source of record. ADR-0035 §1 says lineage records are projected from the log, not authored, and MLflow autologging is authored by the trainer. Its model registry is a mutable, network-addressable artifactory with no row in ADR-0024 promotion. MLflow may mirror the archive. It cannot replace it.

**What turns a stack into a definition:**

1. The seat, role and which of Build's six variants `a` holds in its lease.
2. The lease's confinement field: a profile artifact, even an unpromoted dev stand-in flagged the way G6 flags dev rules, plus the rung. Rung 1 is the one that means something.
3. An honest profile. ADR-0034 §3.4 forbids silent downgrade: a rung-1 declaration that claims P1 to P5 and does not meet them is refused, not granted as `Mediated`. The profile has to state which clauses it fails.
4. A discriminating check. The end-to-end test in `mechanism/crates/topak-node/tests/e2e.rs` already asserts `contained` is false at rung 0. For a rung-1 `Mediated` principal, `is_contained()` in `topak-core/src/lease.rs` needs the ADR-0034 §4 rewrite, because today it returns false through the provenance constant and cannot tell "Mediated by profile" from "Mediated by unwritten code."

**Why this is the right first pass.** It is the `Contained` witness with the residual channels left in. The difference between the two is a subtraction list: remove the network device, remove the shell and interpreter, replace MLflow with `Emit`, drop `Invoke`. That is the corpus's own monotone shape, and it runs on tooling the repo already has, since `mechanism/docker-compose.yml` and the SLM pipeline both exist. Build the `Mediated` one first, name its channels, then subtract toward rung 1.
