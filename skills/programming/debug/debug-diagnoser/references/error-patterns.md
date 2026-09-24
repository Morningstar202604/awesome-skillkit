# Error Patterns (Python error-message quick reference)

> Companion to debug-diagnoser. `diagnoser.py` runs 10 regexes (`ERROR_PATTERNS`) over the whole log with `re.search` (case-insensitive) and outputs JSON sorted by severity; it works best on **single-line error text** and cannot replace manual localization. This file is the manual-side supplement: by error type, it gives causes, localization steps, and fix examples.
> Each pattern's format: `original snippet` → cause → localization → fix.

## Table of Contents
- §0 Three rules for reading tracebacks + bisection localization
- §1 TypeError
- §2 KeyError (including the pandas column-name trap)
- §3 AttributeError
- §4 ValueError (including pandas Length mismatch)
- §5 IndexError
- §6 ImportError / ModuleNotFoundError
- §7 Misleading pandas/numpy-specific errors
- §8 Adding new patterns to diagnoser

## §0 Three rules for reading tracebacks + bisection localization

1. The **last line** is the error type and message (`TypeError: ...`); the **second-to-last section** is the specific code line where the exception occurred. The `File "...", line N, in func` lines in between are the call chain, read bottom-up.
2. When you see `During handling of the above exception, another exception occurred:`, the **real cause is the one above**; the one below is a new exception raised while handling the failure.
3. When you see `The above exception was the direct cause of ...`, look at Y in `raise X from Y`.

Bisection localization (when the error point is not the root cause):
```bash
python3 -m pdb your_script.py        # interactive debug: use p to print variables at the error frame
python3 -X dev your_script.py        # dev mode: turns on extra warnings, often exposing the root cause
```
Or insert a `print(repr(x))` line before and after the suspicious segment; first confirm whether the **input** is correct, then the **output**; if the input is already wrong, repeat the action on the upstream function.

## §1 TypeError

| Original snippet | Common cause |
|---|---|
| `TypeError: 'NoneType' object is not subscriptable` | A function with no return value (defaults to returning None) is indexed by `x[0]`; `dict.get()` returns None on a miss |
| `TypeError: unsupported operand type(s) for +: 'int' and 'str'` | Input from CSV/JSON was not type-converted |
| `TypeError: f() missing 1 required positional argument: 'y'` | Missing argument on the call / using a method as a function (missing self when an instance method is used as a callback) |
| `TypeError: 'int' object is not callable` | A variable shadowed a same-named function (e.g. `len = 5`) |

Localization: print the type of the object being operated on, not its value—`print(type(obj), repr(obj)[:80])`.
Fix:
```python
val = d.get("key")
if val is None:                 # explicitly handle None rather than assuming presence
    val = default
val = int(val)                  # unify type conversion at the input boundary
```

## §2 KeyError

| Original snippet | Common cause |
|---|---|
| `KeyError: 'amount'` (dict) | The key doesn't exist, or there's a spelling/case mismatch |
| `KeyError: 'amount '` (pandas) | **The column name has leading/trailing whitespace** (common in CSV exports) |
| `KeyError: ('a', 'b')` | This is a MultiIndex; you must pass a tuple |

Localization (mandatory first step in pandas):
```python
print([repr(c) for c in df.columns])      # repr exposes invisible spaces and newlines
df.columns = df.columns.str.strip()       # fix: strip whitespace uniformly
print(df.columns.tolist())
```
Fix: `d.get(k, default)`; in pandas, first validate `if col not in df.columns: raise KeyError(f"missing {col}; available={list(df.columns)}")` (printing the available keys is far more useful than the raw KeyError).

## §3 AttributeError

| Original snippet | Common cause |
|---|---|
| `AttributeError: 'NoneType' object has no attribute 'append'` | A chained call returned None in the middle (`list.append` / `sort` return None in place) |
| `AttributeError: 'DataFrame' object has no attribute 'append'` | `DataFrame.append` was removed in pandas 2.0 (use `pd.concat` instead) |
| `AttributeError: Can only use .dt accessor with datetimelike values` | The column is still object; date parsing failed (usually `errors="coerce"` produced NaN) |
| `AttributeError: module 'x' has no attribute 'y'` | Circular import left the module uninitialized; or a local file shares a name with a library (e.g. `json.py` in the current directory) |

Localization: confirm the object is **the class you think**—`print(type(obj), obj is None)`; for module issues, print `print(mod.__file__)` to see whether the imported file is the one you think.
Fix: `out = []` then `out.append(x)` (not `out = out.append(x)`); `pd.concat([df1, df2])`; after `df["ts"] = pd.to_datetime(df["ts"], errors="coerce")`, check `isna().sum()`.

## §4 ValueError

| Original snippet | Common cause |
|---|---|
| `ValueError: could not convert string to float: 'abc'` | Dirty data (unit suffixes, thousands separators, empty strings) |
| `ValueError: Length of values (3) does not match length of index (4)` | The assigned right-hand length doesn't match the DataFrame row count (common after `apply` returns variable-length results that are directly assigned to a column) |
| `ValueError: The truth value of a Series is ambiguous...` | A Series used in `if` / `and` / `or`; use `&`, `|`, `~` with parentheses for boolean ops, and `.any()` / `.all()` for aggregation |
| `ValueError: cannot set a DataFrame with multiple columns to the single column y` | Assignment shape mismatch (right side is 1D, left side selected multiple columns) |

Fix example:
```python
df["x"] = pd.to_numeric(df["x"].str.replace(",", ""), errors="coerce")   # clean the format first, then convert
mask = (df["a"] > 0) & (df["b"] < 10)      # parentheses required; & binds tighter than comparisons
if mask.any():                              # collapse to a scalar with any()/all()
    ...
```
Localizing length mismatch: `print(len(rhs), len(df))`, then check whether the `apply` return is a list (handle with `result_type="expand"` or `pd.Series(...)`).

## §5 IndexError

| Original snippet | Common cause |
|---|---|
| `IndexError: list index out of range` | Wrong loop upper bound; indexing `[0]` on an empty list (e.g. `re.findall(...)[0]` with no match) |
| `IndexError: single positional indexer is out-of-bounds` (pandas `.iloc`) | `.iloc` indexes by **position**, mixed up with `.loc`'s **labels** |

Localization: after `print(len(seq))`, immediately print the index value; for regex cases use `m = re.search(...)` + `if m:` to check for emptiness, don't index `[0]` directly.
Fix: `seq[i] if i < len(seq) else default`; in pandas use `.loc[label]` for labels and `.iloc[pos]` for positions; when mixing, confirm with `df.index` first.

## §6 ImportError / ModuleNotFoundError

| Original snippet | Common cause |
|---|---|
| `ModuleNotFoundError: No module named 'cv2'` | **Package name ≠ import name** (`cv2 → opencv-python`, `PIL → Pillow`, `sklearn → scikit-learn`, `yaml → PyYAML`) |
| `ImportError: cannot import name 'X' from 'Y' (unknown location)` | Circular import; or a local file shares a name with the library and is imported first |
| `ImportError: attempted relative import with no known parent package` | Running a file inside a package directly with `python3 pkg/mod.py`; use `python3 -m pkg.mod` instead |

Localization:
```bash
python3 -c "import mod; print(mod.__file__)"   # see the actual import path
python3 -m pip show -f scikit-learn            # confirm it's installed and where
python3 -m pip install package                 # install with the current interpreter to avoid installing into another environment
```
Note: `pip` and `python3` must belong to the same environment; `python3 -m pip` is the most robust way to avoid "installed but can't import".

## §7 Misleading pandas/numpy-specific errors

| Symptom | Truth |
|---|---|
| `SettingWithCopyWarning` (**a warning, not an error**) | Chained assignment may not have taken effect. Change to `df.loc[mask, "col"] = v`; after slicing, `.copy()` first. As of pandas 3.0, Copy-on-Write is on by default and this warning no longer appears (VERIFY BEFORE USE) |
| `ValueError: cannot reindex on an axis with duplicate labels` | The index has duplicate values; `join` / `reindex` cannot determine a one-to-one correspondence → `df.reset_index(drop=True)` or dedupe first |
| `ValueError: Length mismatch: Expected axis has N elements, new values have M elements` | The counts don't match when assigning `columns=` or `index=` → print the lengths on both sides |
| `RuntimeWarning: invalid value encountered in divide` | 0/0 or inf participated in the operation; the result is NaN/inf rather than an error → use `np.errstate` or filter the denominator first |
| `ValueError: operands could not be broadcast together with shapes (3,) (4,)` | numpy shape mismatch; print `.shape` and align one by one |
| A `KeyError` that is actually a MultiIndex | See §2; confirm the number of levels with `df.columns.nlevels` |
| The result is wrong though nothing seems wrong | Usually a silent dtype change or silent NaN introduction; after every transform re-check `df.dtypes` + `isna().sum()` |

## §8 Adding new patterns to diagnoser

The `ERROR_PATTERNS` list at the top of `diagnoser.py` contains entries with `pattern` (regex), `cause`, `fix`, `severity`. To add one:
```python
{
    "pattern": r"ValueError: cannot reindex",      # uses re.search; no need to match the whole line
    "cause": "The index has duplicate labels",
    "fix": "reset_index(drop=True) or drop_duplicates first",
    "severity": "medium",
}
```
Expected: on a hit, the JSON output is `status: "diagnosed"` and `top_severity` takes the max of critical > high > medium > low; on no hit, `status: "no_match"`, in which case localize manually per §0—do not trust "no match = no problem".
Note: the script runs a case-insensitive `re.search` over the whole log, so "the log merely mentions an error" also counts as a hit—the `file:line` in the `locations` field is the primary basis for judging the current error location (at most 5 entries kept).
