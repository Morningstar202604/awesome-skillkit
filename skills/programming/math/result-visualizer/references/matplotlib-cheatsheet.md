# matplotlib 速查（中文用户的真实痛点优先）

> 配套 result-visualizer。全部代码在 matplotlib 3.10.8 + Python 3.11 实测可运行（本机 Linux、无中文字体环境，中文相关部分已标注实测表现）。

## 目录
- §0 与 `visualizer.py` 的实际对应关系
- §1 图表类型选择对照表
- §2 中文字体配置（按系统判定，含缺字体时的兜底）
- §3 子图布局
- §4 对数轴
- §5 误差带与误差棒
- §6 配色与色盲友好
- §7 保存为出版级格式
- §8 常见坑与出图前检查表

## §0 与 `visualizer.py` 的实际对应关系

- 脚本用 `matplotlib.use("Agg")`（无显示环境必备，且必须在 `import matplotlib.pyplot` **之前**），`figsize=(10,6)`（scatter/histogram 为 8x6/8x5），`dpi=150`，`grid(alpha=0.3)`，`fig.tight_layout()`。
- `--type` 只实现 `line` / `scatter` / `histogram` 三种；SKILL.md 表格里列的 **heatmap / bar / subplot 脚本未实现**，需要时按 §3、§7 自己写。
- 输出 JSON 含 `rendered` 字段：`plot_line` 捕获了所有 `Exception` 并返回 `rendered: false`（note: "plot failed, data is valid"）。**必须检查 `rendered`**，只看 `status: "success"` 会误以为图已生成。
- 未传 `--output` 时默认写到 `/tmp/plot_line.png` 等路径；正式交付要显式指定。

## §1 图表类型选择对照表

| 你要表达什么 | 图类型 | 关键调用 |
|---|---|---|
| 随时间/参数变化的趋势 | 折线 | `ax.plot(x, y)` |
| 两个量的关系、相关性 | 散点 | `ax.scatter(x, y, alpha=0.6)` |
| 单个变量的分布 | 直方图 / KDE | `ax.hist(v, bins=50)` |
| 多组分布对比 | 箱线图 / 小提琴图 | `ax.boxplot([a, b], labels=[...])` |
| 类别间数值比较 | 柱状图 | `ax.bar(labels, values)` |
| 构成（占比随时间变化） | 堆叠面积 | `ax.stackplot(x, y1, y2)` |
| 二维参数空间的结果 | 热力图 | `ax.imshow(M, cmap="viridis", aspect="auto")` + `fig.colorbar` |
| 相关矩阵 | 热力图 + 标注 | `ax.imshow(corr, cmap="coolwarm", vmin=-1, vmax=1)` |
| 收敛/不确定性 | 折线 + 误差带 | `ax.plot` + `ax.fill_between` |
| 量级跨多个数量级 | 对数轴 | `ax.set_yscale("log")` |

## §2 中文字体配置（按系统判定）

不同系统的可用字体名不同（同一字体在不同系统上名字也未必一致）：

| 系统 | 常见中文字体名（按推荐顺序） |
|---|---|
| Windows | `Microsoft YaHei`（微软雅黑）、`SimHei`（黑体）、`SimSun`（宋体） |
| macOS | `PingFang SC`（苹方）、`Heiti SC`、`STHeiti`、`Arial Unicode MS` |
| Linux | `Noto Sans CJK SC`、`Source Han Sans SC`（思源黑体）、`WenQuanYi Zen Hei`、`WenQuanYi Micro Hei` |

按系统自动挑选已安装字体（**不要硬编码一个名字**，换机器必然失效）：

```python
import platform, matplotlib
matplotlib.use("Agg")                      # 必须在 import pyplot 之前
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
plt.rcParams["axes.unicode_minus"] = False     # 否则负号显示为方块
print("picked:", picked)
```
预期：装了中文字体的机器上 `picked` 第一项是中文黑体；**本机（Linux 未装 CJK 字体）实测输出 `picked: ['DejaVu Sans']`** → 中文会渲染成方框（tofu）。此时不要靠改 rcParams 解决，要装字体：
```bash
# Debian/Ubuntu（包名以发行版为准，VERIFY BEFORE USE）
sudo apt-get install -y fonts-noto-cjk
python3 -c "import matplotlib; print(matplotlib.get_cachedir())"   # 装完清缓存
rm -rf "$(python3 -c 'import matplotlib; print(matplotlib.get_cachedir())')"
```
必须清缓存并**重启 Python 进程**，否则 matplotlib 仍用旧字体列表。

只想临时用某一个字体文件（不想装到系统）：
```python
from matplotlib import font_manager
font_manager.fontManager.addfont("assets/NotoSansCJKsc-Regular.otf")   # 换成你的字体路径
plt.rcParams["font.family"] = font_manager.FontProperties(
    fname="assets/NotoSansCJKsc-Regular.otf").get_name()
```
判据：出图后放大看中文是否清晰；若出现方框或空白，用 `print(plt.rcParams["font.sans-serif"])` 确认生效值，并用 `{f.name for f in font_manager.fontManager.ttflist}` 查实际可用名。

## §3 子图布局

```python
fig, axes = plt.subplots(2, 2, figsize=(12, 8), layout="constrained")  # matplotlib >= 3.5
for ax, data in zip(axes.ravel(), [y1, y2, y3, y4]):
    ax.plot(data)
fig.suptitle("结果总览")
fig.savefig("fig.png", dpi=300, bbox_inches="tight")
```
- `layout="constrained"` 比 `tight_layout()` 更能避免标题/色标重叠（老版本用 `fig.tight_layout()`）。
- 不等分布局：`gs = fig.add_gridspec(2, 2); ax_big = fig.add_subplot(gs[0, :])`。
- 共享坐标轴：`plt.subplots(2, 1, sharex=True)`（对比同一 x 轴的多面板时必开）。
- 双 y 轴：`ax2 = ax.twinx()`，但要标注清楚哪个是左轴，否则读者会误读。

## §4 对数轴

```python
ax.set_yscale("log")                       # 纯对数：数据必须全为正
ax.set_yscale("symlog", linthresh=1e-2)    # 含零或负值用 symlog，linthresh 指定线性区阈值
ax.set_xscale("log")
```
坑：对含 0 或负数的序列用 `log` 不会报错，只会**静默丢点**（非正值被丢弃）→ 出图看似"缺了一截"。先用 `(v > 0).all()` 判断，否则用 `symlog`。
坑：对数轴上的"均值线"要说明是几何意义还是算术意义；误差带在对数轴上可能显示为负下界而被截断。

## §5 误差带与误差棒

```python
ax.plot(x, mean, color="#0072B2", label="mean")
ax.fill_between(x, mean - std, mean + std, alpha=0.2, color="#0072B2", label="±1 std")
ax.errorbar(x[::20], mean[::20], yerr=std[::20], fmt="o", capsize=3, color="#D55E00")
ax.legend()
```
标注清楚带的含义（±1 标准差 / 95% 置信区间 / 分位数区间），否则读者无法判断不确定性大小。
多次实验的曲线建议画**逐条细线 + 均值粗线**，而不是只画均值（均值会掩盖双峰、发散等问题）。

## §6 配色与色盲友好

- 分类数据用 `tab10`；连续数据用 `viridis` / `cividis`（`cividis` 对色觉障碍更友好）。
- 不用"红 vs 绿"表达对立含义（最常见的红绿色盲陷阱）；改用蓝/橙。
- Okabe-Ito 色盲友好调色板（十六进制值，按常见公开配色列出，若渲染颜色与预期不符请自行核对，**VERIFY BEFORE USE**）：
```python
OKABE_ITO = ["#000000", "#E69F00", "#56B4E9", "#009E73",
             "#F0E442", "#0072B2", "#D55E00", "#CC79A7"]
```
- 灰度打印检查：把图转成灰度看是否还能区分（打印版报告必备）。
- 同一组图里颜色含义必须一致；别在一张图里用颜色编码两个不同维度。

## §7 保存为出版级格式

```python
fig.savefig("fig.png", dpi=300, bbox_inches="tight")            # 位图：投稿/幻灯片
fig.savefig("fig.svg")                                          # 矢量：可再编辑
fig.savefig("fig.pdf", dpi=300, bbox_inches="tight")            # 矢量：论文常用
```
- `dpi`：屏幕/网页 150 足够，印刷 300 起（期刊要求以投稿指南为准，**VERIFY BEFORE USE**）。
- `bbox_inches="tight"` 裁掉白边，但会改变实际尺寸；投稿有固定尺寸要求时改用 `fig.set_size_inches(w, h)` 精确控制。
- 矢量图中的文字：SVG 用 `plt.rcParams["svg.fonttype"] = "none"` 保留可编辑文字；需要"文字不依赖字体"时改为 `"path"`（转成路径，体积变大但不会缺字）。PDF 常用 `plt.rcParams["pdf.fonttype"] = 42`（TrueType，避免 Type 3 字体在部分期刊系统被拒）。
- 透明背景：`transparent=True`（放在深色幻灯片上时有用）。

## §8 常见坑与出图前检查表

常见坑：
1. `matplotlib.use("Agg")` 写在 `import matplotlib.pyplot` 之后 → 后端切换无效，无显示环境时报 `TclError` 或卡住。
2. 中文变方框：字体没装或缓存没清（§2）。
3. 负号变方块：忘了 `axes.unicode_minus = False`。
4. 图重叠/标签被裁：用 `layout="constrained"` 或 `bbox_inches="tight"`。
5. 对数轴丢点：见 §4。
6. 内存泄漏：循环出图时每张图后 `plt.close(fig)`，否则几百张后内存暴涨。
7. 用 `visualizer.py` 出图后没检查 `rendered` 字段，拿到了"假成功"。

出图前检查：
- [ ] 坐标轴有标签**且带单位**（如 `时间 / s`、`成本 / 元`）
- [ ] 图例存在且不与曲线重叠；多面板有 (a)(b)(c) 编号
- [ ] 字号在最终尺寸下可读（缩小到幻灯片宽度后仍看得清，正文 ≥ 10pt）
- [ ] 颜色在灰度下可区分（若需打印）
- [ ] 不确定性已表达（误差带/误差棒/多次实验曲线）
- [ ] 文件名与 dpi 符合交付要求，且 `rendered` 为 `true`
