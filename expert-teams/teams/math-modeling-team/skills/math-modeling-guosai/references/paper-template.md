# 国赛论文结构规范与 LaTeX 骨架

> 毕成文（写作）Phase 3 套用。国赛与美赛关键差异：**摘要单独成页、无需英文摘要、程序放附录、强调现实意义、查重极严**。

## 国赛标准章节顺序
1. **摘要（单独一页）** ← 评委最先看，决定成败
2. 问题重述
3. 模型假设与符号说明
4. 模型建立与求解（按小问分节 1/2/3…）
5. 模型检验 / 灵敏度分析 / 稳健性
6. 模型评价、改进与推广
7. 参考文献
8. **附录：程序代码与原始数据**

## 摘要写作七要素（毕成文必检）
- ① 针对什么问题；② 做了什么假设；③ 建了什么模型；④ 用了什么方法求解；⑤ 得到什么关键结果（给数字）；⑥ 做了什么检验；⑦ 创新点一句话。
- 摘要里**必须出现具体数值结论**，不能只有「得出合理结果」。
- 国赛摘要页不可出现队伍信息（匿名评阅）。

## LaTeX 骨架（节选）
```latex
\documentclass[12pt]{article}
\usepackage[UTF8]{ctex}      % 中文
\usepackage{amsmath,amssymb} % 公式
\usepackage{graphicx,float}  % 图表
\usepackage{booktabs}        % 三线表
\usepackage{geometry}\geometry{a4paper,margin=2.5cm}
\title{全国大学生数学建模竞赛\\\\论文题目}
\begin{document}
\maketitle

% ===== 摘要单独一页 =====
\newpage
\section*{摘要}
% 七要素，含具体数值与创新点

\section{问题重述}
\section{模型假设与符号说明}
% 符号用 table 或 align 环境
\section{模型建立与求解}
\subsection{问题一 ...}
\subsection{问题二 ...}
\section{模型检验与灵敏度分析}
\section{模型评价、改进与推广}
\section*{参考文献}
\begin{thebibliography}{9}
\bibitem{...}
\end{thebibliography}

% ===== 附录：程序 =====
\newpage
\section*{附录}
\begin{verbatim}
% 核心代码（Python/MATLAB），标注文件名与运行环境
\end{verbatim}
\end{document}
```

## 图表规范（苏解元出图、毕成文排版统一）
- 图：有编号（图1、图2…）、有图题（置于图下）、坐标轴有标签与单位、可黑白打印、分辨率≥300dpi。
- 表：用三线表（booktabs）、有表题（置于表上）、数值带单位与必要的小数位/误差。
- 公式：统一编号，符号在「符号说明」中集中定义，全文不重复定义、不前后矛盾。
- 数据溯源：凡是引用外部数据/图表，须在正文或参考文献标注来源。

## 查重规避（全队铁律）
- **严禁大段复制往届获奖论文、网文、教材原文**。
- 模型表述用自己的话重写；公式可引用但说明须原创。
- 程序必须自己写，附录代码与正文逻辑一致。
- 同校往年雷同题勿直接套用，评阅会比对。
