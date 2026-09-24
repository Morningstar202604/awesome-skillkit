# Debug Checklist (systematic debugging process checklist)

> Companion to debug-diagnoser. `diagnoser.py` only does **pattern matching on log text**, giving candidate causes and severity; the subsequent localization and verification are driven by this checklist. Principle: **hypothesis-driven, not random trial-and-error**—before every change you must be able to say "what change I expect to see"; otherwise that is not debugging, it's guessing.

## Table of Contents
- §0 Time-boxing and stopping loss
- §1 Reproduce (an unreproducible problem cannot be debugged)
- §2 Minimize
- §3 Hypothesis-driven (write it down, then verify)
- §4 Bisection localization
- §5 Logging and breakpoints
- §6 git bisect (regression-type problems)
- §7 When to stop guessing and read the source
- §8 Wrap-up after the fix
- §9 One-page quick-reference checklist

## §0 Time-boxing and stopping loss

- Give yourself a time-box (e.g. 30 minutes); if still no clue → **change methods**: switch to bisection, switch to reading the source, or explain it to someone else (rubber duck).
- Forbidden: doing "change a little, run, see if it's better" three or more times in a row without being able to state a causal hypothesis.

## §1 Reproduce

- [ ] Get the **complete** error text (every line of the traceback), not one line from a screenshot
- [ ] Fix the input: same command, same data, same environment
```bash
python3 -X dev your_script.py 2>&1 | tee err.log    # keep the full output for diagnoser to read
python3 diagnoser.py --file err.log                 # machine first-pass judgment (optional)
```
Expected: stable reproduction (≥3 consistent results).
If it's **flaky** → first suspect: random seed not fixed, dict/set iteration order, concurrency races, dependency caching. Verify: `for i in 1 2 3 4 5; do python3 your_script.py; done` and compare whether the output is consistent.
If it only reproduces in CI → compare `python3 -m pip freeze` differences from local, and environment variables.

## §2 Minimize

Goal: compress the problem to **about ten lines** with no external dependencies.
- [ ] Delete input data unrelated to the error (trim the CSV to 5 rows)
- [ ] Delete unrelated code paths (comment out or early-`return`)
- [ ] Replace external dependencies (API/DB) with hard-coded constants
- [ ] Output a minimal repro script `minrepro.py`; it must be **independently runnable**

Criterion: `python3 minrepro.py` still raises the same error. If the error disappears after minimization → the part that disappeared is the clue (go back and bisect it per §4).

## §3 Hypothesis-driven

- [ ] Write down the hypothesis: "I think `X` is `None` at `f()`, because `g()` has no return value"
- [ ] Write down the **expected observation**: "if it holds, `print(type(X))` should output `<class 'NoneType'>`"
- [ ] Make only one change to verify it; if the observed result does not match the expectation → the hypothesis is wrong; change the hypothesis instead of continuing to change code

Counter-examples (forbidden): changing three places at once, swapping library versions, or adding try/except and calling it fixed once "it doesn't error anymore".

## §4 Bisection localization

Three granularities, from coarse to fine:

1. **Code bisection**: insert a checkpoint at the midpoint of the flow; confirm "everything before here is correct", so the root cause is in the second half; then take the midpoint of the second half, until you locate the specific line.
2. **Data bisection**: for data errors (parse failure, dimension mismatch), feed the data in halves:
```python
df.iloc[:len(df)//2]      # if this half doesn't error, the bad data is in the other half
```
3. **Commit bisection**: it worked yesterday and broke today → use `git bisect` (§6).

## §5 Logging and breakpoints

- [ ] Use `logging` rather than `print`, with levels so you can turn off noise:
```python
import logging
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(name)s %(message)s")
log = logging.getLogger(__name__)
log.debug("x=%r type=%s", x, type(x))     # print with %r to see spaces and None
```
- [ ] Break into the error frame:
```bash
python3 -m pdb your_script.py
```
Common commands: `l` (list code), `n` (next line), `s` (step into function), `c` (continue), `p expr` (print), `w` (show call stack), `q` (quit).
- [ ] Post-mortem debugging after a crash (preserves the local variables):
```bash
python3 -m pdb -c continue your_script.py    # stops at the error frame after an exception
```
- [ ] For hangs/freezes: use `faulthandler` to print which stack it's stuck in:
```bash
python3 -X faulthandler your_script.py       # then press Ctrl+\ to trigger a stack dump
```

## §6 git bisect (regression-type problems)

Applies when you clearly know "it worked before some version".
```bash
git bisect start
git bisect bad                 # the current commit is broken
git bisect good <good-commit>  # a known-good commit or tag
git bisect run python3 -m pytest -x    # auto-bisect: a non-zero test exit is treated as bad
git bisect log                 # view/review the bisection process
git bisect reset               # finish and return to the original branch (required)
```
Expected: finally outputs "X is the first bad commit".
Prerequisite: `git bisect run` relies on the test **stably** reflecting good/bad; if the test itself is flaky, fix the test before bisecting.
Note: if the working tree has uncommitted changes, `git stash` first; after finishing, `git stash pop` to confirm recovery.

## §7 When to stop guessing and read the source

At any of the following signals, stop trial-and-error and read the implementation directly:
- The parameter name is right but the behavior differs from the docs (version difference is the most common cause)
- The error comes from inside the library, and your call looks perfectly legal
- The same call "sometimes right, sometimes wrong" on different data (usually an implicit dtype/in-place-mutation convention)

```bash
python3 -c "import mod; print(mod.__file__)"          # locate the actually loaded source file
python3 -c "import inspect, mod; print(inspect.getsource(mod.func))"   # read the function source directly
python3 -m pip show -f package                        # confirm version and install location
```
In IPython/Jupyter you can use `mod.func??` to view the source. When reading the source, look first at: the function's **default parameters**, the "Notes" section in the docstring (boundary conditions are often written there), and whether there is in-place mutation semantics.

## §8 Wrap-up after the fix

- [ ] Add a test that **reproduces the original bug** and confirm it fails before the fix (`git stash` the fix and re-run to verify)
- [ ] Confirm you did not introduce `except Exception: pass` (that hides the next bug)
- [ ] Run the full suite with `python3 -m pytest -x`, not just the case you just changed
- [ ] Record in the commit message: symptom / root cause / fix / how verified

## §9 One-page quick-reference checklist

1. Get the full traceback → `python3 diagnoser.py --file err.log` (machine first-pass)
2. Stably reproducible? No → check seed / order / concurrency / environment
3. Compress to `minrepro.py` (~ten lines, independently runnable)
4. Write the hypothesis + expected observation → change only one place at a time
5. Not localized → bisect (code / data / `git bisect`)
6. Logging with `logging` + breakpoints `python3 -m pdb`; if needed, `python3 -X faulthandler`
7. Library behavior suspicious → read the source (`inspect.getsource`) instead of continuing to guess
8. After fixing, add a test → full `python3 -m pytest -x` → commit message states the root cause clearly
