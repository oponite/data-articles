# Can Uncertainty Be Programmable?

Programming is a recipe: take inputs, apply rules, produce outputs. The implicit assumption is that every value in the recipe is *definite* — known, fixed, fully specified. Uncertainty breaks that assumption. When a program encounters sometrhing it cannot pin down, what happens?

Lana 1.0 treats uncertainty as a first-class value. Its semantics define `STATE`, `STATE_DIST`, and the operations `MEASURE`, `TRANSFORM`, and `APPEND` as mathematical objects. They work on *information about the world*, not on the world itself. The answer to the title question is the semantics that follow.

---

## 1. The state

A concrete Lana state lives in a family of $2\times 2$ complex matrices, called $\mathcal S$.

Every $\rho \in \mathcal S$ satisfies three conditions: Hermitian ($\rho = \rho^\dagger$), positive semidefinite ($\rho \succeq 0$), and trace-one ($\operatorname{Tr}(\rho) = 1$):

$$
\mathcal S = \left\{ \rho \in \mathcal L(\mathbb C^2) \;\middle|\; \rho = \rho^\dagger,\; \rho \succeq 0,\; \operatorname{Tr}(\rho) = 1 \right\}.
$$

The canonical matrix form makes this concrete. For every state:

$$
\rho = \begin{pmatrix}
1-p & c \\
c^* & p
\end{pmatrix},
$$

where $p = \rho_{11} \in [0,1]$, $c = \rho_{01} \in \mathbb C$, and $|c|^2 \leq p(1-p)$. Here $p$ is the probability of seeing outcome $1$ in the computational basis, and $c$ carries the "quantumness" — the off-diagonal information that computational-basis measurement cannot see.

The normalization $d = c / \sqrt{p(1-p)}$, defined for $0 < p < 1$, collapses to $d = 0$ at the boundaries $p \in \{0, 1\}$. The invariant $(p, c)$ with $0 \leq p \leq 1$ and $|c|^2 \leq p(1-p)$ is both necessary and sufficient for membership in $\mathcal S$.

A state is built from this data alone. Nothing else.

---

## 2. Measuring the state

`MEASURE` is a read-only probe. It extracts outcome probabilities from a state without mutating it:

$$
\operatorname{MEASURE}(\rho) = \operatorname{Bernoulli}(p).
$$

The outcome $1$ occurs with probability $p$, outcome $0$ with probability $1-p$. Only $p$ matters. The value $c$ is invisible to computational-basis measurement.

Two states that agree on their diagonal probability $p$ produce identical measurement distributions, regardless of their off-diagonal $c$. This is a structural fact: measurement is a projection onto the diagonal.

Formal properties of `MEASURE`:

- **Well-definedness.** For every $\rho \in \mathcal S$, the output is a valid probability distribution because $p$ and $1-p$ are non-negative and sum to one.
- **State preservation.** `MEASURE` reads $p$; it never produces a new state or replaces its input. The input $\rho$ remains exactly what it was.
- **Internal-parameter independence.** If $\rho_1, \rho_2 \in \mathcal S$ share the same $p$, then $\operatorname{MEASURE}(\rho_1) = \operatorname{MEASURE}(\rho_2)$.

The measurement is read-only. It does not collapse the state.

Named bases extend this. Beyond the computational basis $B_{\text{computational}} = (|0\rangle, |1\rangle)$, Lana defines:

$$
q_{\mathrm{computational}}(\rho) = p, \quad q_x(\rho) = \tfrac12 + \operatorname{Re}(c), \quad q_y(\rho) = \tfrac12 - \operatorname{Im}(c).
$$

Each basis has a distinct probability rule. All of them are read-only; measurement never collapses the state.

---

## 3. Transforming the state

A transform $\Phi$ on a state is defined as a deterministic, Borel-measurable endofunction $\Phi: \mathcal S \to \mathcal S$. The mathematical domain is abstract — the transform acts on $\mathcal S$ without requiring physical realization. The only constraint is that for every $\rho \in \mathcal S$, the output $\Phi(\rho)$ must also satisfy the state invariant: $0 \leq p' \leq 1$ and $|c'|^2 \leq p'(1-p')$.

Valid transforms form a monoid under composition: they are closed, associative, and include an identity. They are not required to be invertible. This means transforms can model irreversible processes, which distinguishes them from CPTP maps in physical quantum mechanics.

Registered transforms like `INVERT` and `NEUTRALIZE` are concrete examples. Both are deterministic, continuous, and thus Borel-measurable. `INVERT` maps $(p, d) \mapsto (1-p, \bar{d})$ and preserves the invariant structure. `NEUTRALIZE` maps every disposition to $(p, 0)$.

---

## 4. Appending states

`APPEND(A, B)` for two ordinary states $A, B \in \mathcal S$ returns a `STATE_DIST`. The operation explicitly asserts independence between operands for that operation only — it does not claim all distinct states are independent. This is a modeling choice, not a universal assumption.

For states with observable probabilities $p_A$ and $p_B$, the observable probability is:

$$
p_C = p_A + p_B - p_A p_B = 1 - (1 - p_A)(1 - p_B).
$$

The internal distribution of the resulting `STATE_DIST` is defined by:

$$
\rho_C = \begin{pmatrix}
1 - p_C & c_C \\
c_C^* & p_C
\end{pmatrix},
$$

where $c_C = d_C \sqrt{p_C(1 - p_C)}$, with $d_C$ being the normalized disposition derived from the input states. If the conditions allow, the internal distribution is continuous; otherwise, it degenerates to a Dirac distribution concentrated at appropriate boundary values.

Properties: observable probability is bounded in $[0, 1]$, every concrete state in the output satisfies the state invariant, `APPEND` is commutative, and the observable probability is associative.

Chaining: for multiple independent inputs, the observable probability is:

$$
p_{\operatorname{APPEND}} = 1 - \prod_{i=1}^{n} (1 - p_i),
$$

This is commutative and associative under the independence assumption.

Internal non-associativity means the grouping of operands matters for the internal distribution structure. The internal distribution is evaluated as a binary tree, and binary grouping affects the result unless a later canonical form is defined.

---

## 5. Composition semantics

Nested `APPEND` trees follow deterministic evaluation order. For example:

```
APPEND(APPEND(A, B), C)
```

evaluates to `APPEND(APPEND(A, B), C)`, meaning first `APPEND(A, B)` is evaluated, then `APPEND` is applied to that `STATE_DIST` and `C`. It must not be silently rewritten as `APPEND(A, APPEND(B, C))` because the internal distributions are not assumed equal.

Lifting introduces the embedding $\eta: \mathcal S \to \operatorname{Dist}(\mathcal S)$, defined as $\eta(\rho) = \delta_\rho$. This mapping embeds ordinary states as degenerate distributions, allowing them to participate uniformly in lifted operations.

For an admissible transform $\Phi$, the lifted operation is the pushforward:

$$
\widehat{\operatorname{TRANSFORM}}_\Phi(\mu) = \Phi_*\mu,
$$

where $(\Phi_*\mu)(E) = \mu(\Phi^{-1}(E))$. Sampling from this pushforward does not introduce randomness beyond that already represented by $\mu$. The transformation is deterministic with respect to the state.

For lifted `APPEND`:

$$
\lambda(E) = \int_{\mathcal S} \int_{\mathcal S} K(\rho_A, \rho_B)(E) \, d\mu(\rho_A) \, d\nu(\rho_B),
$$

where $K$ is the ordinary `APPEND` kernel, independently drawing one state from each input distribution. For distributed inputs, $p_C$ is computed conditionally from each sampled pair.

For lifted `MEASURE` of `STATE_DIST`:

$$
P(X=1) = \int_{\mathcal S} p(\rho) \, d\mu(\rho), \quad P(X=0) = 1 - P(X=1).
$$

This operation returns a distribution unless classical sampling is explicitly requested.

---

## 6. Boundary conditions and failure handling

A state is invalid if $p \notin [0,1]$ or $|c|^2 > p(1-p)$. A runtime must reject invalid construction rather than silently reinterpret it as another state.

At boundary values $p \in \{0, 1\}$, positive semidefiniteness forces $c = 0$, and by convention $d = 0$. The state is still valid at these points.

`APPEND` degeneracy follows: when $p_C \in \{0, 1\}$, the internal distribution collapses to $d_C = 0$. When $0 < p_C < 1$ and $\sigma_C = 0$, it collapses to $d_C = m_C$. These boundary conditions are encoded explicitly in the runtime.

Transform outputs that violate `STATE` invariants are not valid transforms for that input. The runtime must reject or trap such results.

Core operations are defined only over declared domains. Unsupported type combinations produce type errors or runtime errors. No conversion is permitted unless explicitly defined in the semantics.

---

## 7. Implementation obligations

A concrete `STATE` implementation must retain enough information to reconstruct $(p, c)$ and therefore the canonical matrix. If a runtime stores $d$ instead of $c$, it must preserve the full complex value and reconstruct $c = d\sqrt{p(1-p)}$ with the boundary convention.

`STATE_DIST` is represented as a finite lazy expression — not an enumeration of possible states. Conceptually, it has fields: `distribution_kind`, `parameters`, `inputs`. Chain operations may form trees like `AppendDist(AppendDist(A, B), C)`, which evaluation, measurement, or sampling recursively evaluate only the portions needed.

Floating-point policy allows sufficient precision to preserve the domain. Near-boundary violations at $p = 0$ or $p = 1$ may be clamped within tolerance. The C runtime sets $\varepsilon = 10^{-12}$, which does not materially enlarge $\mathcal S$ but permits canonicalization of accepted near-boundary values.

Randomness requires a seeded pseudo-random source. Algorithm selection and stream ownership belong in runtime or VM documentation, not in the mathematical definition.

---

## 8. The mathematical boundary wall

A Lana-1.0 program built on these semantics cannot exceed these mathematical constraints:

**The dimension limit.** `STATE` is strictly a $2 \times 2$ complex matrix. Everything beyond qubit-1 — higher-dimensional systems, continuous variables — is outside the state representation. The math does not support them unless a new representation is defined.

**Independence is not automatic.** `APPEND` asserts independence between inputs for that operation only. If two states are correlated, `APPEND` cannot be applied without changing the input structure. Correlations must be represented explicitly via joint laws, not through implicit assumptions.

**Measurement is read-only, but observation is effectful.** `MEASURE` reads $p$ and returns a probability distribution; it never modifies the input state. However, the information model distinguishes `observe` — which records or consumes evidence in the execution context — from `MEASURE`, which is purely a mathematical probe. The distinction matters when a program tracks information over time.

**Sampling consumes, without replacing.** `SAMPLE_STATE_DIST` returns one concrete state but the runtime does not preserve the sampled value for subsequent operations. It exposes a single value that must be used immediately. The original distribution remains, mathematically, but the sample is an elimination of one representative.

**Numerical tolerance is approximation, not extension.** The tolerance $\varepsilon \leq 10^{-12}$ handles floating-point precision, but the mathematical operations still assume exact arithmetic. Two values that differ by $10^{-12}$ or less are treated as equivalent in runtime, but this does not change the mathematical definition.

**Joint sampling does not independently sample each variable.** `sample` on a joint law returns one definite member — not independently sampled values for each variable. To obtain values for multiple variables from a single call, the program must restructure the sampling operation.

**Lazy evaluation defers exact distributions.** Chained `APPEND` operations form a tree structure where the internal distribution is evaluated on demand. A full internal distribution cannot be retrieved without explicit materialization. The runtime only evaluates the portions required to produce the requested result.

**Quantum interpretation is not built-in.** `STATE` is abstract-state, not necessarily a physical quantum system. Physical quantum constraints — CPTP maps, Born rule, etc. — require additional specification. Lana 1.0 does not interpret `STATE` as a quantum state by default.

**Equality for complex distributions is hard.** Exact equality between states and distributions is generally undecidable without fixing a canonical form. The runtime represents distributions as expressions; two mathematically equal expressions may not reduce to the same runtime object without explicit normalization.

---

## 9. Why this answers the question

The answer is: **yes, uncertainty is programmable, but only under strict rules**. Lana 1.0 treats uncertainty as data — a first-class value (`STATE`, `STATE_DIST`) with well-defined operations (`MEASURE`, `TRANSFORM`, `APPEND`, `SAMPLE`, `CONDITION`, etc.).

The key insight is that uncertainty can be represented mathematically and composed through operations that have well-defined properties. When uncertainty is treated as data, the program becomes a *reasoning machine* rather than a deterministic value transformer. The state represents the world the program knows about; measurement extracts information without collapse; transforms are valid mappings; `APPEND` models independent events; and lifting extends everything to the distribution level.

The boundary conditions ensure the program never silently assumes independence, never collapses without explicit operation, and never silently extends the mathematical scope. Everything that can be composed follows from well-defined mathematical rules.

Uncertainty becomes programmable — not because it becomes trivial, but because its representation is precise, its operations are well-defined, and its failures are caught rather than silently hidden.
