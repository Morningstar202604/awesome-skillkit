# 方法论来源与设计取舍（cloud-drive-manager）

> 何时读：当你要接入第四个云盘、调整分片阈值，或质疑"为什么脚本没有上传和删除
> 命令"时读本文件。本文件只讲设计依据。

## 思想来源（公开方法论蒸馏，非文本搬运）

| 本技能的做法 | 蒸馏自的思想 |
|---|---|
| 先出上传计划再执行 | Terraform `plan`/`apply` 与 `rsync -n` 的两阶段惯例：先看将发生什么 |
| 上传前后各跑一次哈希清单 | 备份领域的 verify-after-write 原则（如 `rsync --checksum`、ZFS scrub 的思路）：写完必须读回验证 |
| 用标准 `sha256sum -c` 格式输出 | Unix 工具链的"输出可被既有工具消费"传统：不发明私有格式 |
| 跳过符号链接 | 与 file-organizer 一致：跟随链接会让操作范围脱离用户意图 |
| 不提供删除命令 | 最小权限/最小破坏面原则：能力越小，误用面越小；把不可逆操作留在人手里 |
| 敏感信息只从环境变量取 | 十二要素应用 config 原则；凭证不进代码、不进命令行参数 |

## 关键取舍

**为什么脚本完全不碰网络？** 上传逻辑与"传什么"的逻辑耦合后，会导致一个
尴尬处境：想验证清单是否正确，就必须先有真实凭证并真的上传。拆开之后，
`plan-upload` 与 `checksum-plan` 在离线、无凭证的环境里可被完整测试，
而用户能在**付出任何传输成本之前**看到将要发生什么。代价是上传步骤需要
AI 或用户自己写——SKILL.md 步骤 3 把关键约束（分片顺序、令牌周期、断点续传）
列清楚了。

**为什么不提供删除命令？** 删除是云盘场景里唯一不可逆、且**后果随规模放大**
的操作——`rm -rf` 错一个路径，可能删掉整个归档目录。脚本提供删除会带来两个
风险：一是 AI 可能在没有充分确认时调用它；二是命令行参数里一个拼写错误就
造成不可逆损失。本技能的选择是：只提供"看清将删什么"的能力（`parse-list`），
把执行动作留给用户在自己的网盘客户端里做——那里有回收站和二次弹窗。

**为什么把秒传原理写进 SKILL.md 而不是脚本？** 秒传是**协议层的约束**，
不是一个函数能解决的问题：它要求客户端用对哈希算法、在上传前算好哈希、
并在命中后仍做校验。这三条都是流程要求，写进文档才能指导真实实现；
脚本能做的只是提供 `checksum-plan` 这个算哈希的工具。

**为什么分片阈值写成数据表而不是硬编码分支？** 三家的阈值（4MB / 100MB / 250MB）
是平台策略，会随版本调整。收敛成 `CHUNK_POLICY` 字典后，修正一处即可全链路生效，
且阈值与"依据说明"（`note` 字段）放在一起，不会出现"改了数忘了改文档"的漂移。

**为什么 `parse-list` 要归一化三家字段？** 三家的列表条目结构差异大
（百度的 `isdir` 整数、阿里的 `type` 字符串、OneDrive 的子对象），
但它们承载的信息相同。归一成 `(name, size, is_dir, mtime, id)` 之后，
"这个目录里有多少文件、共多大"这类判断只需写一次。归一化是**只读侧**的，
因为它不涉及写入语义——写入侧的差异（分片、秒传）无法这样统一。

**为什么体积校验和哈希校验要同时做？** 体积能极快地发现"没传完"；
哈希能发现"传完了但内容错了"（分片顺序错、编码转换）。只比体积会漏掉内容
损坏，只比哈希在大目录上代价高。两级检查，先便宜后昂贵。

## 官方文档

- 百度网盘开放平台（分片上传、秒传、文件列表）：<https://pan.baidu.com/union/doc/>
- 百度网盘上传流程与 4MB 分片约定：<https://pan.baidu.com/union/doc/nksg0sbfs>
- 阿里云盘开放平台（文件列表、上传、SHA1 去重）：<https://www.yuque.com/aliyundrive/zpfszx>
- OneDrive 上传 API（250MB 单请求上限）：<https://learn.microsoft.com/en-us/graph/api/driveitem-put-content>
- OneDrive 创建上传会话（分片必须为 320KiB 倍数）：<https://learn.microsoft.com/en-us/graph/api/driveitem-createuploadsession>
- Microsoft Graph 列表 children（`value[]` 与 `folder`/`file` 子对象）：<https://learn.microsoft.com/en-us/graph/api/driveitem-list-children>
- Python `hashlib`（`new()` 支持的算法名与流式摘要）：<https://docs.python.org/3/library/hashlib.html>
