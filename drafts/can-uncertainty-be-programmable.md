# Can Uncertainty Be Programmable?

Programming is a recipe: take inputs, apply rules, produce outputs. Mainstream programming languages generally treat uncertainty as application data rather than a fundamental property of values and computation. Specifically, when information is incomplete, a programmer must manually encode what that uncertainty means and how it should propagate.

What if uncertainty itself became something a program could represent, propagate, reason about, and report?

## A Different Computation Model

**Lana** is a general-purpose programming language built around **the explicit representation of information about modelled values and events**.

Consider the following:

```Lana
let risk = possibility([0.4, 0.6]);

if (risk > 0.5) {
    approve_loan();
}
```

Imagine a language where risk does not have to collapse to one definite value before the rest of the program can continue. Imagine if that was a runtime guarantee rather than a class or library.

That's essentially Lana.

## OK, Cool. Why though?

Imagine an automated trading system deciding whether to place an order.

```lana
let signal = possibility([0.45, 0.72]);

if (signal > 0.60) {
    place_order();
}
```

The signal is unresolved: one possible value says **don't trade**, the other says **trade**.

Lana can continue calculating with both possibilities, but it will not let that unresolved decision trigger the external `place_order()` effect.

In other words, Lana lets you build systems that can **reason with incomplete information without pretending that incomplete information is certainty**.

## Why is this not a Java/Python library?

Because when it comes to *information-aware programming*, Lana cooks harder alone.

Consider the use case of a bank deciding whether to approve a loan based on dynamic risk metrics. A Python library can wrap uncertainty:

```Python
risk = Uncertain([0.4, 0.6])

if risk > 0.5:
    approve_loan()
```

Python can customize what `risk > 0.5` returns, but a library cannot redefine the semantics of Python's `if` to branch over unresolved alternatives and merge the resulting program states.

Lana laughs at this problem, as it can make unresolved control flow itself legal:

```Lana
let risk = possibility([0.4, 0.6]);

if (risk > 0.5) {
    approve_loan();
}
```

Lana programs can evaluate both pure paths while preventing `approve_loan()` from executing until the controlling condition is resolved.

Java is even more awkward, as operators aren't generally overridable:

```Java
Uncertain<Double> risk = uncertain(0.4, 0.6);

if (risk.gt(0.5).isResolved() &&
    risk.gt(0.5).getValue()) {
    approveLoan();
}
```

Lana makes the same representation far more elegant:

```Lana
if (risk > 0.5) {
    approve_loan();
}
```

Java can model an uncertain value. Lana can make uncertainty participate directly in ordinary control flow.

## Cool idea. Does it survive reality?

**Use Case #1: Financial Systems**

Conflicting prices can propagate through valuation while settlement remains blocked.

**Use Case #2: Fraud/Credit/Compliance**

Competing classifications can remain alive while irreversible action is gated.

**Use Case #3: Autonomous Software**

An agent can inspect multiple candidate targets without deleting one prematurely.

**Use Case #4: Data Pipelines**

Downstream work can continue without silently converting missing data into a fabricated certainty.

The primary conceptual pain point Lana addresses is that most software forces information states into:
```
KNOW → CONTINUE
DON'T KNOW → ERROR / STOP / GUESS
```

Lana proposes:
```
KNOW → CONTINUE
DON'T KNOW  → CONTINUE, PRESERVE UNCERTAINTY
NEED TO ACT → REQUIRE RESOLUTION, THEN CONTINUE
```

Lana lets programs postpone commitment without postponing computation.

The sections below cover the mathematical specification of how Lana concepts become programmable.

## 1. The state

In 1.0, Lana treats uncertainty as a first-class value. Its semantics define `STATE`, `STATE_DIST`, and the operations `MEASURE`, `TRANSFORM`, and `APPEND` as primitives.

Importantly, these values describe information about a world. They do not claim to be the world itself.

`STATE` is a $2 \times 2$ complex matrix in the set $\mathcal S$:

$$
\mathcal S = \left\{ \rho \in \mathcal L(\mathbb C^2) \mid \rho = \rho^\dagger,\; \rho \succeq 0,\; \operatorname{Tr}(\rho) = 1 \right\}.
$$

Every state has this form:

$$
\rho = \begin{pmatrix} 1-p & c \\ c^* & p \end{pmatrix}.
$$

The values satisfy $0 \leq p \leq 1$ and $|c|^2 \leq p(1-p)$.

The value $p$ is the probability for outcome $1$ in the computational basis. The complex value $c$ is internal state information.

Lana also uses the normalized value $d$. For $0 < p < 1$, $d = c / \sqrt{p(1-p)}$. At $p = 0$ or $p = 1$, Lana sets $d = 0$.

These rules define valid `STATE` values. Lana treats `STATE` as an abstract mathematical value. It does not claim that every state is a physical quantum state.

## 2. Measuring the state

`MEASURE` maps a concrete `STATE` to a probability distribution:

$$
\operatorname{MEASURE}(\rho) = \operatorname{Bernoulli}(p).
$$

The distribution gives outcome $1$ probability $p$ and outcome $0$ probability $1-p$. The operation reads the state and does not change it.

The computational-basis result depends on $p$. It does not depend on $c$ or $d$. Therefore, two states with the same $p$ have the same computational-basis measurement distribution.

Lana also defines named binary bases. For the canonical value $c = \rho_{01}$:

$$
q_{\mathrm{computational}}(\rho)=p,\qquad q_x(\rho)=\frac12-\operatorname{Re}(c),\qquad q_y(\rho)=\frac12+\operatorname{Im}(c).
$$

Named-basis measurement remains read-only. It does not collapse or replace the input state.

## 3. Transforming the state

A valid transform is a deterministic, Borel-measurable function:

$$
\Phi : \mathcal S \rightarrow \mathcal S.
$$

The transform must return a valid `STATE` for every input in its declared domain. Its output must satisfy $0 \leq p' \leq 1$ and $|c'|^2 \leq p'(1-p')$.

Valid transforms compose. Composition is associative, and the identity transform exists.

A transform does not need an inverse. Therefore, valid transforms form a monoid, not necessarily a group.

Lana 1.0 registers `INVERT` and `NEUTRALIZE` as operands for transformation. `INVERT` changes $(p,d)$ to $(1-p,\overline d)$. `NEUTRALIZE` changes $(p,d)$ to $(p,0)$. Both transforms preserve the state rules.

## 4. Appending states

`APPEND(A, B)` accepts two concrete `STATE` values and returns a `STATE_DIST`. For this operation, Lana models the two represented events as independent. The operation does not state that all events are independent.

If the input probabilities are $p_A$ and $p_B$, the output probability is:

$$
p_C = 1-(1-p_A)(1-p_B).
$$

The output distribution contains valid states with this value of $p_C$. Lana computes the distribution of the internal value $d_C$ from $d_A$ and $d_B$.

For $0 < p_C < 1$, define:

$$
m_C=\frac{d_A+d_B}{2},\qquad \sigma_C=\frac{|d_A-d_B|}{2}.
$$

If $\sigma_C > 0$, $d_C$ has a truncated circular complex-normal distribution on the unit disk. If $\sigma_C = 0$, $d_C$ has a Dirac distribution at $m_C$. If $p_C$ is $0$ or $1$, $d_C$ has a Dirac distribution at $0$.

The observable probability is bounded and associative. The internal distribution is evaluated as a binary tree. Lana 1.0 gives no associativity guarantee for that internal distribution.

## 5. Composition semantics

Lana evaluates nested operations in their written order. In:

```lana
APPEND(APPEND(A, B), C)
```

the runtime evaluates `APPEND(A, B)` first. It then applies `APPEND` to that result and `C` by the declared lifted rules. It does not rewrite the expression with a different grouping.

Lana embeds a concrete state $\rho$ in a distribution as the Dirac distribution $\delta_\rho$. This embedding lets lifted operations use a concrete state as a degenerate `STATE_DIST`.

For a valid transform $\Phi$ and a distribution $\mu$, the lifted transform is the pushforward $\Phi_*\mu$. It applies the deterministic transform to each state in the distribution.

The lifted `APPEND` applies the ordinary `APPEND` rule to states from the input distributions. The output is the resulting distribution over states.

`MEASURE` of a `STATE_DIST` returns a probability distribution. Its outcome-1 probability is the exact expectation of the state probability:

$$
P(X=1)=\int_{\mathcal S}p(\rho)\,d\mu(\rho).
$$

Sampling is separate from these exact operations. `SAMPLE_STATE_DIST` returns one concrete state and does not mutate the source distribution.

## 6. Boundary conditions and failure handling

The runtime rejects a `STATE` when $p$ is outside $[0,1]$ or $|c|^2 > p(1-p)$. It does not reinterpret invalid input as another state.

At $p=0$ or $p=1$, the state rule requires $c=0$. Lana sets $d=0$ at both boundaries.

The runtime handles `APPEND` degeneracy explicitly. It uses the Dirac distribution at $d_C=0$ when $p_C$ is $0$ or $1$. It uses the Dirac distribution at $d_C=m_C$ when $0 < p_C < 1$ and $\sigma_C=0$.

A transform is invalid for an input when its output does not satisfy the `STATE` invariant. The runtime rejects that result.

Each operation has a declared domain. Unsupported type combinations return an error. Lana does not perform an implicit conversion unless the semantics define it.

## 7. Implementation obligations

The runtime must retain enough information to reconstruct $p$ and $c$. If it stores $d$, it must preserve the full complex value and reconstruct $c=d\sqrt{p(1-p)}$.

`STATE_DIST` is a finite lazy expression over `STATE` values. It is not an enumeration of every possible state. A chain can remain a tree until measurement or sampling needs a result.

The C runtime uses a tolerance of $\varepsilon=10^{-12}$ for accepted floating-point boundary error. This tolerance supports numerical representation. It does not expand the mathematical state domain.

Sampling uses a seeded pseudo-random source. The runtime and VM documents define stream ownership and algorithm details.

## Conclusion, or why this article answers the title question

**Uncertainty is programmable**, provided its representation is precise, operations well-defined, and failures caught rather than silently hidden.

Other languages make the programmer build uncertainity semantics, whereas Lana 1.0 treats uncertainty as data — a first-class value (`STATE`, `STATE_DIST`) with well-defined operations (`MEASURE`, `TRANSFORM`, `APPEND`, `SAMPLE`, `CONDITION`, etc.).

The key insight is that when uncertainty is treated as data, the program becomes a *reasoning machine* rather than a deterministic value transformer. Everything that can be composed follows from well-defined mathematical rules.
