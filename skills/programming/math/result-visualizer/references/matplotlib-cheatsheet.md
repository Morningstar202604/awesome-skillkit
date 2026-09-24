# matplotlib Cheat Sheet (real pain points for CJK users first)

> Companion to result-visualizer. All code was tested to run on matplotlib 3.10.8 + Python 3.11 (this machine is Linux with no CJK fonts; CJK-related parts note the measured behavior).

## Table of Contents
- §0 Actual correspondence with `visualizer.py`
- §1 Chart-type selection reference
- §2 CJK font configuration (detected by OS, including fallback when fonts are missing)
- §3 Subplot layout
- §4 Logarithmic axes
- §5 Error bands and error bars
- §6 Color and colorblind-friendly palettes
- §7 Saving in publication-grade formats
- §8 Common pitfalls and pre-render checklist

## §0 Actual correspondence with `visualizer.py`

- The script uses `matplotlib.use("Agg")` (required in headless environments, and it must come **before** `import matplotlib.pyplot`), `figsize=(10,6)` (scatter/histogram are 8x6/8x5), `dpi=150`, `grid(alpha=0.3)`, `fig.tight_layout()`.
- `--type` implements only `line` / `scatter` / `histogram`; the **heatmap / bar / subplot scripts listed in the SKILL.md table are not implemented**—write them yourself per §3 and §7 when needed.
- The output JSON includes a `rendered` field: `plot_line` catches all `Exception`s and returns `rendered: false` (note: "plot failed, data is valid"). **You must check `rendered`**; looking only at `status: "success"` will make you think the plot was produced.
- When `--output` is not passed, it defaults to paths like `/tmp/plot_line.png`; for a real deliverable, specify it explicitly.

## §1 Chart-type selection reference

| What you want to express | Chart type | Key call |
|---|---|---|
| Trend over time/parameter | Line | `ax.plot(x, y)` |
| Relationship/correlation between two quantities | Scatter | `ax.scatter(x, y, alpha=0.6)` |
| Distribution of a single variable | Histogram / KDE | `ax.hist(v, bins=50)` |
| Comparing several distributions | Boxplot / violin | `ax.boxplot([a, b], labels=[...])` |
| Numeric comparison across categories | Bar | `ax.bar(labels, values)` |
| Composition (share changing over time) | Stacked area | `ax.stackplot(x, y1, y2)` |
| Results over a 2D parameter space | Heatmap | `ax.imshow(M, cmap="viridis", aspect="auto")` + `fig.colorbar` |
| Correlation matrix | Heatmap + annotations | `ax.imshow(corr, cmap="coolwarm", vmin=-1, vmax=1)` |
| Convergence / uncertainty | Line + error band | `ax.plot` + `ax.fill_between` |
| Magnitudes spanning multiple orders | Log axis | `ax.set_yscale("log")` |

## §2 CJK font configuration (detected by OS)

Available font names differ across systems (and the same font may be named differently on different systems):

| OS | Common CJK font names (in recommended order) |
|---|---|
| Windows | `Microsoft YaHei`, `SimHei`, `SimSun` |
| macOS | `PingFang SC`, `Heiti SC`, `STHeiti`, `Arial Unicode MS` |
| Linux | `Noto Sans CJK SC`, `Source Han Sans SC`, `WenQuanYi Zen Hei`, `WenQuanYi Micro Hei` |

Auto-pick an installed font by OS (**do not hard-code one name**—it will inevitably break on another machine):

```python
import platform, matplotlib
matplotlib.use("Agg")                      # must come before importing pyplot
import matplotlib.pyplot as plt
from matplotlib import font_manager

CJK = {
    "Windows": ["Microsoft YaHei", "SimHei", "SimSun"],
    "Darwin":  ["PingFang SC", "Heiti SC", "STHeiti", "Arial Unicode MS"],
    "Linux":   ["Noto Sans CJK SC", "Source Han Sans SC",
                "WenQuanYi Zen Hei", "WenQuanYi Micro Hei"],
}
available = {f.name for f in font_manager.fontManager.ttflist}
order = CJK.get(platform.system(), []) + ["DejaVu Sans"]
picked = [f for f in order if f in available] or ["DejaVu Sans"]
plt.rcParams["font.sans-serif"] = picked
plt.rcParams["axes.unicode_minus"] = False     # otherwise the minus sign renders as a box
print("picked:", picked)
```
Expected: on a machine with CJK fonts installed, the first entry of `picked` is a CJK sans font; **on this machine (Linux with no CJK fonts), the measured output is `picked: ['DejaVu Sans']`** → CJK characters render as boxes (tofu). In that case, don't try to fix it via rcParams—install the font:
```bash
# Debian/Ubuntu (package names per distribution, VERIFY BEFORE USE)
sudo apt-get install -y fonts-noto-cjk
python3 -c "import matplotlib; print(matplotlib.get_cachedir())"   # clear the cache after installing
rm -rf "$(python3 -c 'import matplotlib; print(matplotlib.get_cachedir())')"
```
You must clear the cache and **restart the Python process**, otherwise matplotlib still uses the old font list.

To use a single font file temporarily (without installing system-wide):
```python
from matplotlib import font_manager
font_manager.fontManager.addfont("assets/NotoSansCJKsc-Regular.otf")   # change to your font path
plt.rcParams["font.family"] = font_manager.FontProperties(
    fname="assets/NotoSansCJKsc-Regular.otf").get_name()
```
Criterion: after rendering, zoom in and check whether CJK text is crisp; if boxes or blanks appear, confirm the effective value with `print(plt.rcParams["font.sans-serif"])` and list the actually available names with `{f.name for f in font_manager.fontManager.ttflist}`.

## §3 Subplot layout

```python
fig, axes = plt.subplots(2, 2, figsize=(12, 8), layout="constrained")  # matplotlib >= 3.5
for ax, data in zip(axes.ravel(), [y1, y2, y3, y4]):
    ax.plot(data)
fig.suptitle("Results overview")
fig.savefig("fig.png", dpi=300, bbox_inches="tight")
```
- `layout="constrained"` avoids title/colorbar overlap better than `tight_layout()` (older versions use `fig.tight_layout()`).
- Uneven layout: `gs = fig.add_gridspec(2, 2); ax_big = fig.add_subplot(gs[0, :])`.
- Shared axes: `plt.subplots(2, 1, sharex=True)` (required for multi-panel comparisons on the same x axis).
- Twin y axis: `ax2 = ax.twinx()`, but label clearly which is the left axis, otherwise readers misread.

## §4 Logarithmic axes

```python
ax.set_yscale("log")                       # pure log: all data must be positive
ax.set_yscale("symlog", linthresh=1e-2)    # use symlog for zero/negative values; linthresh sets the linear-region threshold
ax.set_xscale("log")
```
Pitfall: applying `log` to a series containing 0 or negatives does not error, it just **silently drops points** (non-positive values are discarded) → the plot looks like "a chunk is missing". Check `(v > 0).all()` first, otherwise use `symlog`.
Pitfall: a "mean line" on a log axis must state whether it is geometric or arithmetic; error bands on a log axis may show a negative lower bound and get clipped.

## §5 Error bands and error bars

```python
ax.plot(x, mean, color="#0072B2", label="mean")
ax.fill_between(x, mean - std, mean + std, alpha=0.2, color="#0072B2", label="±1 std")
ax.errorbar(x[::20], mean[::20], yerr=std[::20], fmt="o", capsize=3, color="#D55E00")
ax.legend()
```
Label the band clearly (±1 std / 95% CI / quantile interval), otherwise readers cannot judge the magnitude of uncertainty.
For curves from multiple runs, prefer drawing **thin lines per run + a thick mean line**, rather than only the mean (the mean hides bimodality, divergence, and similar issues).

## §6 Color and colorblind-friendly palettes

- For categorical data use `tab10`; for continuous data use `viridis` / `cividis` (`cividis` is friendlier to color-vision deficiency).
- Do not encode opposition with "red vs. green" (the most common red-green colorblind trap); use blue/orange instead.
- Okabe-Ito colorblind-friendly palette (hex values, listed per the commonly published palette; if the rendered colors differ from expectation, verify yourself—**VERIFY BEFORE USE**):
```python
OKABE_ITO = ["#000000", "#E69F00", "#56B4E9", "#009E73",
             "#F0E442", "#0072B2", "#D55E00", "#CC79A7"]
```
- Grayscale print check: convert the figure to grayscale and see if it still distinguishes (required for printed reports).
- Color meanings must be consistent within the same set of figures; don't use color to encode two different dimensions in one figure.

## §7 Saving in publication-grade formats

```python
fig.savefig("fig.png", dpi=300, bbox_inches="tight")            # raster: submissions / slides
fig.savefig("fig.svg")                                          # vector: re-editable
fig.savefig("fig.pdf", dpi=300, bbox_inches="tight")            # vector: common in papers
```
- `dpi`: 150 is enough for screen/web; 300 and up for print (journal requirements per the author guidelines, **VERIFY BEFORE USE**).
- `bbox_inches="tight"` crops the white margin but changes the actual size; when a submission has fixed-size requirements, use `fig.set_size_inches(w, h)` for exact control.
- Text in vector figures: for SVG use `plt.rcParams["svg.fonttype"] = "none"` to keep editable text; when you need "text independent of fonts", change it to `"path"` (converted to outlines, larger file but no missing glyphs). For PDF, `plt.rcParams["pdf.fonttype"] = 42` (TrueType) is common, avoiding Type 3 fonts being rejected by some journal systems.
- Transparent background: `transparent=True` (useful on dark slides).

## §8 Common pitfalls and pre-render checklist

Common pitfalls:
1. `matplotlib.use("Agg")` written after `import matplotlib.pyplot` → backend switch has no effect; raises `TclError` or hangs in headless environments.
2. CJK turns into boxes: fonts not installed or cache not cleared (§2).
3. Minus sign becomes a box: forgot `axes.unicode_minus = False`.
4. Overlapping figures / clipped labels: use `layout="constrained"` or `bbox_inches="tight"`.
5. Dropped points on log axis: see §4.
6. Memory leak: when plotting in a loop, call `plt.close(fig)` after each figure; otherwise memory balloons after a few hundred.
7. After plotting with `visualizer.py`, not checking the `rendered` field and getting a "false success".

Pre-render checks:
- [ ] Axes have labels **with units** (e.g. `time / s`, `cost / CNY`)
- [ ] Legend exists and does not overlap the curves; multi-panel figures have (a)(b)(c) labels
- [ ] Font size is readable at the final size (still legible when scaled to slide width; body ≥ 10pt)
- [ ] Colors are distinguishable in grayscale (if printing)
- [ ] Uncertainty is expressed (error band / error bars / multi-run curves)
- [ ] Filename and dpi meet the delivery requirements, and `rendered` is `true`
