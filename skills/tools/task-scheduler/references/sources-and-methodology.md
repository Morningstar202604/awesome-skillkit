# 方法论来源与设计取舍

> 何时读：想扩展字段翻译规则、新增平台映射，或理解"为什么不直接写 crontab"时读本文件。
> 命令参数见 SKILL.md，此处只讲设计依据。

## 思想来源（公开方法论蒸馏，非代码搬运）

| 本脚本的做法 | 蒸馏自的思想 |
|--------------|--------------|
| 表达式翻译成人话后再执行 | 「先复述再动手」的变更管理惯例：执行前用另一种表述确认理解一致，是发现误解最便宜的手段 |
| 生成而不安装 | 配置管理工具的"渲染 + 人工 apply"模式；crontab 无版本控制、无撤销栈，写入即高风险 |
| 下次触发时间预览 | `systemd-analyze calendar`、云厂商 cron 预览器的通用交互：用具体时刻替代抽象的字段组合 |
| 绝对路径 + 重定向告警 | cron 运维的经典经验总结（`cron` 的 PATH 与邮件机制是其最著名的两个陷阱） |
| 语法先验证再输出 | 编译器前端思路：先做语法/语义检查，再产出目标代码，避免把坏配置交给下游 |

## 关键取舍

**为什么内置解析器而不用 croniter 做唯一实现？** croniter 能算时间但**不产生中文描述**，
而"人话确认"才是本技能的核心价值。两者分工：内置解析器负责字段展开与中文翻译（零依赖，
永远可用），croniter 负责精确的下次触发时刻（可选，缺失则降级并明确告知用户精度下降）。

**为什么 `@reboot` 不做时间预测？** 它没有可预测的时间点——机器什么时候重启是不可知的。
早期的实现让 croniter 去算，结果它直接抛错；现在提前挡掉并说明"仅在启动时触发"。

**为什么 `cron-add` 要检查命令里的绝对路径？** 这是定时任务第一大失败原因，
且它的表现是**静默不执行**——用户不会看到任何报错。把检查放在生成阶段，
成本极低而收益极高。

**为什么告警里区分"未指定 --log"和"命令里没有重定向"？** 两者处置不同：
前者加 `--log` 即可（脚本会自动补重定向），后者要改命令本身。
更早的版本把它们混为一谈，导致指定了 `--log` 还报警告，属于误报。

**为什么字段翻译要处理 `工作日` / `周末` 这类档位？** `* * * * 1-5` 逐字翻译成
"周一、周二、周三、周四、周五" 可读性差且易漏看；归约为"工作日"更接近用户的心智模型。
判据必须是**精确匹配**（恰好是那五个/两个），否则退回逐项列举，避免误归约。

## cron 字段语义要点（实现依据）

| 字段 | 取值范围 | 易错点 |
|------|---------|--------|
| 分钟 | 0-59 | `*/5` 是每 5 分钟，不是"第 5 分钟" |
| 小时 | 0-23 | **没有 24**；`0` 是午夜 |
| 日 | 1-31 | 与"星期"同时限定时，cron 语义是**或**而非且 |
| 月 | 1-12 | 不支持 0 |
| 星期 | 0-7 | **0 和 7 都是星期日**；1 是星期一（不是星期日） |
| 特殊 | `@reboot` `@daily` `@hourly` 等 | `@reboot` 无固定时刻 |

日与星期同时限定时取"或"关系，是 cron 语义中最反直觉的一点，脚本在描述里会显式标注。

## 官方文档

- `crontab(5)` 手册（字段定义与 `@` 特殊表达式）：<https://man7.org/linux/man-pages/man5/crontab.5.html>
- `cron(8)` 手册（环境变量与邮件机制）：<https://man7.org/linux/man-pages/man8/cron.8.html>
- Apple `launchd.plist` 手册（`StartCalendarInterval`、`StandardOutPath`）：<https://www.manpagez.com/man/5/launchd.plist/>
- Apple `launchctl` 手册（`load`/`kickstart`）：<https://www.manpagez.com/man/1/launchctl/>
- Microsoft `schtasks` 命令参考：<https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/schtasks>
- Microsoft 任务计划程序 XML 架构：<https://learn.microsoft.com/en-us/windows/win32/taskschd/task-scheduler-schema>
- croniter 项目（`croniter` 表达式迭代器）：<https://github.com/pallets-eco/croniter>
