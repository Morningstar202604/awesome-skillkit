# 方法论来源与设计取舍（feishu-dingtalk-bridge）

> 何时读：当你想新增一个平台（如 Slack / 企微应用消息）、调整加签实现，
> 或质疑"为什么三家不共用一套负载"时读本文件。本文件只讲设计依据。

## 思想来源（公开方法论蒸馏，非文本搬运）

| 本技能的做法 | 蒸馏自的思想 |
|---|---|
| 每家一个独立 builder，不写通用负载再翻译 | 适配器模式（Adapter）：接口差异过大时，包装优于归一化；强行统一会泄漏平台特例 |
| `build-message` / `parse-webhook` 两个子命令 | 端口-适配器架构的"出站/入站"分离：发消息与收消息的契约本就不同 |
| dry-run 打印负载再发送 | `kubectl --dry-run=client` 与 Terraform `plan` 的"先看将发生什么"惯例 |
| 只接受环境变量**名**而非密钥值 | 十二要素应用 config 原则 + 避免密钥进入 `ps` 可见的命令行参数 |
| 成功判定读业务码而非 HTTP 码 | 国内 IM 开放平台的通用约定：飞书/钉钉/企微都用 200 + 业务错误码，是"HTTP 之上再套一层状态"的典型 |
| 加签实现只作为参考函数暴露 | 把密钥运算放在调用方（代理层），脚本保持无密钥可测 |

## 关键取舍

**为什么不做统一的 `Message` 抽象？** 三家的差异不是"字段名不同"，而是
**语义层面不同**：飞书没有 markdown 类型（要借道富文本或消息卡片）、企微的
标题必须内联进正文、@ 的实现分别落在正文标签与顶层对象两种位置。抽象会立刻
退化成 "if platform == ..." 的伪抽象，反而让每个特例更难被看见。分离实现后，
平台差异被显式摆在对照表里，这也正是使用者最需要的信息。

**为什么脚本不计算钉钉加签？** 加签需要密钥明文。如果脚本接受密钥参数，
密钥就会出现在命令行历史与进程列表里；如果脚本读环境变量再算，它就与"脚本
不持有凭证"的原则冲突。折中：算法以 `dingtalk_sign()` 参考函数的形式提供
（可被调用方 import 并单测），`build-message` 只打印"timestamp 与算法说明"。
这样负载仍然完整可见，密钥始终留在代理层。

**为什么飞书的 `content` 要字符串化？** 这是平台方的设计，不是我们的选择——
飞书要求 `content` 是一个 JSON **字符串**而非嵌套对象。这一处若写错只会得到
泛化的 `19002 参数错误`，排查成本高。因此脚本统一做 `json.dumps`，
并在 SKILL.md 的对照表里标注这一差异。

**为什么在脚本层就拦截超长正文？** 企微上限 4096 字符、飞书 15000、钉钉 20000，
差异明显。本地拦截能省一次必然失败的往返，更重要的是迫使发送方**主动改写内容**
（改成摘要 + 链接），而不是依赖平台侧静默截断——截断后的告警消息可能丢掉最关键
的那一行。

**为什么把错误码解释硬编码进解析器？** 这三家的错误码语义不透明（`310000`
看起来像"参数错"，实际是安全设置问题）。把最常见的几个码的定向解释直接写进
解析输出，能让排查从"搜文档"变成"读一行提示"，这是使用频率最高的收益点。

## 官方文档

- 飞书自定义机器人（webhook、msg_type、加密回调）：<https://open.feishu.cn/document/client-docs/bot-v3/add-custom-bot>
- 飞书消息内容与富文本 `post` 结构：<https://open.feishu.cn/document/server-docs/im-v1/message-content-description/create_json>
- 飞书事件订阅与 `schema 2.0`：<https://open.feishu.cn/document/ukTMukTMukTM/uUTNz4SN1MjL1UzM>
- 钉钉自定义机器人（加签算法、安全设置、`errcode`）：<https://open.dingtalk.com/document/orgapp/custom-robot-access>
- 钉钉加签实现说明：<https://open.dingtalk.com/document/orgapp/custom-robot-access#title-jfe-ycv-4jb>
- 企业微信群机器人（markdown 限制、频率限制）：<https://developer.work.weixin.qq.com/document/path/91770>
- 企业微信回调与 AES 解密：<https://developer.work.weixin.qq.com/document/path/90930>
- Python `hmac` / `base64`（加签实现依据）：<https://docs.python.org/3/library/hmac.html>
