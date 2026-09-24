# Notation Guide (mathematical modeling notation and expression conventions)

> Companion to model-formulator. The `variables` field output by `model_formulator.py` is **JSON keys → string descriptions** (e.g. `"x[i,j]": "truck i assigned to delivery j (binary)"`); the keys must stay ASCII so that model-solver and code generation can use them safely. This file prescribes how to name these keys, how to write formulas, and how to label units.

## Table of Contents
- §1 Four classes of symbols: sets / indices / parameters / variables
- §2 Subscript/superscript and naming convention reference
- §3 Units and dimensions
- §4 Formula readability rules
- §5 Writing in Markdown / LaTeX
- §6 Common error reference
- §7 Correspondence with the model spec JSON

## §1 Four classes of symbols: sets / indices / parameters / variables

The first step of modeling is not writing formulas, but partitioning symbols into four classes and listing them; write the objective and constraints only after all four classes are present.

| Class | Meaning | Convention | Example |
|---|---|---|---|
| Set | The full universe of entities/time periods | Uppercase `I, J, T, N` | `I`: set of trucks, `T`: set of time periods |
| Index | An element in a set | Lowercase `i, j, t` | `i ∈ I`, `t ∈ T` |
| Parameter | A known quantity given as input | Lowercase Greek or uppercase `c, a, b, d` | `d[j]`: demand at delivery point j (units) |
| Variable | The quantity to solve for | Lowercase end-of-alphabet letters `x, y, z` | `x[i,j] ∈ {0,1}`: whether assigned |

Write it as a table rather than scattered in the prose (example):

| Symbol | Type | Meaning | Unit |
|---|---|---|---|
| `I` | set | set of trucks, `|I| = 5` | — |
| `c[i,j]` | parameter | cost of truck i serving delivery point j | CNY |
| `x[i,j]` | variable | whether assigned (1/0) | — |
| `z` | variable | total cost | CNY |

## §2 Subscript/superscript and naming convention reference

| Situation | Recommended | Counter-example | Reason |
|---|---|---|---|
| Entity numbering | Subscript `x[i,j]` | Superscript `xⁱʲ` | Reserve superscripts for powers/time steps to avoid ambiguity |
| Time step / iteration count | Superscript `x⁽ᵏ⁾`, `x^{(k)}` | Subscript `x_k` mixed with entity subscripts | Distinguish "the k-th iteration" from "the k-th element" |
| Transpose | `Aᵀ` / `A^T` | `A'` | The prime is easily confused with a derivative |
| Power | `x^2`, `x²` | `x**2` | Use math notation in math text; `**` is code |
| Optimal value | `x*`, `x^*` | Mixing `x_opt` and `x*` | Pick one within a document and stay consistent |
| Estimate | `ĥ`, `\hat{y}` | Mixing `y_est` and `ŷ` | Same as above |
| Vector/matrix | Bold lowercase/uppercase `x`, `A` | Leaving it to the reader to guess | State dimensions on first use: `x ∈ ℝⁿ` |
| Set cardinality | `|I|` | `#I` (code smell) | Use bars in math text |
| Summation | `Σ_{i∈I} c[i]·x[i]` | `sum(c*x)` | Use math notation in formulas; code goes in code blocks |
| Boolean/indicator | `x[i,j] ∈ {0,1}` | `x[i,j] = 0 or 1` | The former is directly understandable by a solver |
| Integer | `y ∈ ℤ₊` | `y is an integer` | Make nonnegativity explicit |
| Real | `x ∈ ℝ` | omitted | Without it, the reader cannot determine the domain |

Rule: **use only one notation for the same meaning within a document**; any newly introduced symbol must be registered in this table.

## §3 Units and dimensions

- Label the unit in the last column of the symbol table for every parameter and variable; write `—` for dimensionless ones (counts, ratios, 0-1 variables)—do not leave it blank.
- Dimensional consistency check (required before writing constraints): the two sides of a constraint must have the same units.
  - Counter-example: `travel_time[i,j] ≤ 30` (left side hours, right side minutes) → either unify units, or write `travel_time[i,j] ≤ 0.5 h`.
- Dimensionless scaling: when variables span multiple orders of magnitude (e.g. CNY vs. 10k CNY, seconds vs. days), unify to a baseline unit set at modeling time, and state in the doc "this document uses **CNY / hour / units** as the baseline units".
- The objective's unit is the cost/revenue unit itself; in multi-objective cases you **must first state** how to combine them (weighted sum? ε-constraint? lexicographic priority?)—you cannot min two quantities simultaneously without a combination rule.
- Numerical magnitude: write the typical magnitude of parameters into the symbol table (e.g. `c[i,j] ~ 10² CNY`), which helps spot an off-by-one coefficient typo and judge solver numerical stability.

## §4 Formula readability rules

1. One formula expresses one thing; number constraints one by one (C1, C2…) so errors can be located.
2. Write the summation range explicitly: `Σ_{i∈I}`, not `Σᵢ` with the range explained in prose.
3. Put quantifiers at the end, parenthesized: `Σ_{i∈I} x[i,j] = 1, ∀ j ∈ J`.
4. For complex formulas, give the verbal reading first, then the symbolic form. Example:
   - Verbal: each delivery point must be served by exactly one vehicle, exactly once.
   - Symbolic: `Σ_{i∈I} x[i,j] = 1, ∀ j ∈ J` (C1)
5. Break long formulas and align at the equals/plus sign; don't cram them on one line.
6. Use meaningful letters rather than random ones for variables: `cost[i,j]` beats `a[i,j]`; but when using single letters in formulas, register them in the symbol table.
7. When 0-1/integer is involved, write the domain in the variable description, not only in the constraints.

## §5 Writing in Markdown / LaTeX

- Inline formulas `$...$`, display block `$$ ... $$`.
- Common notations:

| Want to express | LaTeX |
|---|---|
| Summation | `\sum_{i=1}^{n}` |
| Product | `\prod_{i=1}^{n}` |
| In / for all | `\in` / `\forall` |
| Reals / nonnegative integers | `\mathbb{R}` / `\mathbb{Z}_{+}` |
| ≤ / ≥ | `\leq` / `\geq` |
| Dot product | `\cdot` |
| Sub/superscript | `x_{i,j}` / `x^{(k)}` |
| Transpose | `A^{\top}` |
| hat / bar | `\hat{y}` / `\bar{x}` |
| Piecewise function | `\begin{cases} ... \end{cases}` |

- Markdown note: underscores are treated as emphasis markers in some renderers; if `x_i` renders oddly, wrap it in LaTeX `$x_{i}$` or escape it as `x\_i`.
- Support for `$$` display blocks varies across renderers (GitHub and various Markdown editors differ; **VERIFY BEFORE USE**: first render a `$$x^2$$` on the target platform before writing the whole document). If the target platform does not support it, fallbacks: ① inline `$...$`; ② pure ASCII form (e.g. `sum_{i in I} c[i]*x[i] <= B`); ③ render to an image and insert it.
- When writing formulas in code blocks, use ASCII form for easy copying into solver code:

```text
min  sum_{i in I} sum_{j in J} c[i,j] * x[i,j]
s.t. sum_{i in I} x[i,j] = 1          for all j in J   (C1)
     x[i,j] in {0,1}
```

## §6 Common error reference

| Wrong | Problem | Correct |
|---|---|---|
| `x[ij]` | 2D index unreadable | `x[i,j]` |
| Mixing `X` and `x` for the same variable | Case is treated as two symbols | Unify the case |
| `x[i,j] = 1 if assigned` | Natural language inside the formula | `x[i,j] ∈ {0,1}`, meaning goes in the symbol table |
| `min cost` | Doesn't say over what or the dimension | `min Σ_{i∈I} Σ_{j∈J} c[i,j]·x[i,j]` (CNY) |
| `≤ 30` | Unit unclear | `≤ 30 min` or convert to baseline units |
| A pile of unnumbered constraints after `s.t.` | Errors cannot be located | Number them C1, C2… |
| Two mins in the objective | Multi-objective not combined | State weighting / priority / ε-constraint |

## §7 Correspondence with the model spec JSON

Field-filling conventions for `model_formulator.py`:

- `variables`: keys in ASCII (`"x[i,j]"`), values with an English description and **type and unit**, e.g. `"x[i,j]": "0-1; whether truck i serves delivery point j"`.
- `objective`: one line of ASCII formula, consistent with the code-block style in §5, so it can later be translated directly into solver code.
- `constraints`: array of strings, each ending with a number like `(C1)`, matching the numbering of the formulas in the prose.
- `assumptions`: written as testable statements ("service time at every point is a constant 10 min"), not "appropriately simplified".
- `knowns` / `unknowns`: the former are parameters (with units), the latter the quantities to solve for; do not register the same symbol in both.
