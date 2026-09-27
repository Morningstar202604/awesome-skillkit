---
name: game-qa-checklist
description: 游戏质量门禁清单。规定功能测试（正常路径/边界/bug 分级）与设计评审（乐趣/平衡/完整度/受众）的 critical/major/minor 标准与放行规则，适用于 qa 与 reviewer 双门禁。
license: MIT
compatibility: universal
---

# 游戏质量门禁清单

本 skill 是 game-qa 与 game-reviewer 的门禁标尺。核心原则：**能跑 + 好玩才放行，功能 qa 与设计 reviewer 双门禁并行，有 critical/major 一律打回。** 不崩不代表好玩，好玩也得能跑。

## 这是什么

一份游戏交付的质量门禁清单。把检查分成功能项（qa 负责）与设计项（reviewer 负责）两大类，每项给 critical/major/minor 判定标准与放行规则。它让双门禁结论可复现。

## 何时使用

- game-qa 做功能测试、game-reviewer 做设计评审时必加载。
- prototype-developer 交付原型前按本清单自检。
- team-lead 判断能否交付时以双门禁结论为准。

## 核心步骤

1. **功能-正常路径**：核心循环能否完整跑通；跑不通 = critical。
2. **功能-边界**：极端输入/快速操作/空状态；崩溃/卡死 = critical。
3. **功能-bug 分级**：崩溃 blocker、阻断流程 major、体验小瑕疵 minor。
4. **设计-乐趣**：核心循环是否 fun，有无"再来一局"钩子；不好玩 = major。
5. **设计-平衡**：有无无敌套路/pay-to-win/无解点；有 = major。
6. **设计-完整度与受众**：首版是否自洽、是否匹配目标玩家。
7. **出结论**：双门禁均无 critical/major → 放行；任一有 → 打回。

## 清单

- [ ] 核心循环完整可跑通。
- [ ] 边界 case 无崩溃/卡死。
- [ ] bug 按 blocker/major/minor 分级。
- [ ] 每条 bug 有可复现步骤。
- [ ] 核心循环有乐趣钩子。
- [ ] 无无敌/无解/pay-to-win 套路。
- [ ] 首版范围自洽无缺失。
- [ ] 符合目标玩家画像。
- [ ] 每条评审问题有理由。
- [ ] 双门禁无 critical/major 才放行。

## 易错点

- **只测功能不评乐趣**：原型能跑就放行，结果不好玩。双门禁都要过。
- **bug 不可复现**：报了 bug 却给不出步骤，开发没法修。每条给复现步骤。
- **漏跑边界**：只走正常路径，放过崩溃。边界必须测。
- **放过低劣核心**：核心循环不好玩却放行。不 fun 就是 major。
- **平衡放水**：有无敌套路却判 minor。无敌/pay-to-win 一律 major。
- **口味当问题**：把个人偏好当 major。个人口味降级 minor。
- **漏 blocker**：有崩溃却放行。blocker/critical 零容忍。
