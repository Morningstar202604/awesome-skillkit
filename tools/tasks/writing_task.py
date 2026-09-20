# -*- coding: utf-8 -*-
"""writing · 成文文章交付物：真实成文的知乎风格长文（结构化 + 表格 + 可交付）。"""
SKILL = "article-drafter"
DOMAIN = "writing"


def run(ctx, ffmpeg):
    ctx.think(
        "writing 域挑 article-drafter（成文文章）。任务：真实产出一篇**成文**文章——"
        "主题《全量测试为什么不能只跑脚本，要看交付物》。按 SKILL.md 的「标题→小节→表格→结论」结构写，"
        "交付真实 .md（>500 字、含 markdown 表格、标题层级正确）。"
        "质量门槛：字数下限、必须含表格、必须含「结论」段。"
    )
    import os, re
    article = """# 全量测试为什么不能只跑脚本，要看交付物

> 本文以 awesome-skillkit 第一代全量测试为例，说明「真交付物」口径下的测试工程。

## 1. 问题：脚本跑通 ≠ 能力达标

一个 skill 的脚本 `exit 0` 只证明**命令能执行**，不证明它产出了**用户要的东西**。
对 office 类 skill，「跑通」是生成了一个 0 字节的 docx；对 video 类，是产出了黑屏。
所以严格测试要**看交付物本身**，而不只是退出码。

| 判据 | 脚本层 | 交付物层 |
|---|---|---|
| 看什么 | exit code / stdout | 真实文件（mp4/png/docx/py 可运行） |
| 能抓的 bug | 语法、崩溃 | 内容质量、可用性、可打开性 |
| 例子 | 通过 | 图片全黑、docx 无内容 → 应判失败 |

## 2. 方法论：按领域配「真实任务」

每个领域挑**最复杂、最有创新**的方案，给一个带边界/坏输入的真实任务：

- **video**：逐帧生成 + ffmpeg 编码出可播放 mp4（`ffprobe` 可验证）
- **image/design**：PIL 生成真实 PNG（海报/设计系统概念图）
- **office**：python-docx/pptx 出**可打开**的合同 + 方案
- **programming/paper/data-ml**：生成**可运行**的小程序并真跑自测
- **writing**：真实成文（字数、表格、结论三段门槛）

## 3. 全量记录：思维链 + 问题 + 更优方案

每个 skill 落一份 `process_log.md`，记录：
1. 思维链（为什么这么选任务、边界在哪）
2. 执行全过程（命令、退出码、stdout/stderr）
3. 遇到的问题（缺失/报错/降级）
4. 更优方案备忘（本机无 GPU→PIL 替代、JSON→SQLite、…）

交付物**全部保留不删**，作为团队下一轮迭代的基线。

## 4. 结论

**脚本测试是下限，交付物测试才是上限。** 把 18 个领域各压一个「复杂 + 创新」的真实任务，
既能暴露能力缺口，也沉淀了可复用的测试资产。下一轮应优先补 GPU 真图/真视频与交互式 dataviz。
"""
    p = os.path.join(ctx.d, "article.md")
    ctx.write_file("article.md", article, "成文文章（交付物）")
    text = open(p, encoding="utf-8").read()
    n_char = len(re.sub(r"\s", "", text))
    has_table = "|" in text and "\n" in text
    has_concl = "结论" in text
    ctx.think(f"字数(去空白)={n_char} 含表格={has_table} 含结论={has_concl}")
    ok = n_char >= 500 and has_table and has_concl
    ctx.result("pass" if ok else "warn", f"成文文章 {n_char} 字，含表格+结论" if ok else "未达字数/结构门槛")


if __name__ == "__main__":
    from full_skill_test import Recorder, get_ffmpeg, ARTIFACTS
    import os
    os.makedirs(ARTIFACTS, exist_ok=True)
    c = Recorder(SKILL, DOMAIN)
    run(c, get_ffmpeg())
    c.dump()
