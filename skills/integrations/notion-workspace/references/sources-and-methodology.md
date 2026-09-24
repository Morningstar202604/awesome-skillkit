# Methodology sources and design trade-offs（notion-workspace）

> 何时读：当你想升级 Notion API 版本、改分页策略，或质疑"为什么脚本不发请求"时读本文件。
> 本文件只讲设计依据，不重复 SKILL.md 里的操作步骤。

## Idea sources (distilled from public methodology; not copied text)

| This skill's approach | Idea distilled from |
|---|---|
| 请求构造与网络发送分离 | 六边形架构里"端口/适配器"的分离：业务规则（负载形状）不依赖 IO（HTTP 客户端） |
| `build-*` 只打印、不发送 | Terraform `plan` / `apply` 两阶段；`kubectl --dry-run=client` 的"先看负载"惯例 |
| 块类型白名单，未知类型报错 | 编译器对未知 AST 节点的 fail-fast 策略：静默降级会掩盖数据丢失 |
| 未映射块渲染成 HTML 注释 | Markdown 生态的 `<!-- -->` 注释占位惯例：降级但留痕，便于事后补齐 |
| 凭证永不进入脚本 | 十二要素应用（12-Factor App）第 III 条 config：配置存于环境，不存于代码 |
| 分页用游标而非 offset | Notion/Stripe/Twitter 等游标分页 API 的共识：游标在并发改动下不会跳条/重条 |

## Key trade-offs

**为什么脚本完全不发 HTTP 请求？** 一是让 `build-*` / `parse-*` 在没有网络、
没有 token 的环境里可被完整单测；二是把"能不能写进用户工作区"这个决定权
留在人手里。脚本只回答"负载长什么样"，不回答"是否发送"。代价是发送步骤
需要 AI 或用户自己拼 curl——这一段在 SKILL.md 步骤 3 里给了可直接复制的模板。

**为什么版本头写死在脚本里当常量？** Notion 的 `Notion-Version` 不是可选
装饰：不同版本的属性语义、块结构会变。散落在多处字符串里迟早不一致，
因此收敛到 `NOTION_VERSION` 一个常量，升级版本时是单点修改，且
`build-*` 输出里会把它打印出来供人工核对。

**为什么 `page_size` 上限在脚本层就拦掉？** 100 是服务端硬上限，本地拦住
可以省掉一次必然失败的往返；更重要的是把"翻页"这个正确解法直接推给用户，
而不是让人以为把 `page_size` 调大就能一次拉完。

**为什么 `parent-type` 要显式指定而非自动判断？** 页面与数据库的 `parent`
结构不同（`page_id` vs `database_id`），且两者 ID 长得一模一样，无法从
字符串推断。自动猜测会在猜错时产出 400，而 400 的错误信息不会告诉你
"其实是 parent 类型错了"。显式声明把错误提前到调用点。

**为什么块类型只支持 9 种？** 表格、同步块、嵌入、数据库视图这些块结构
复杂且各自有嵌套约束，半吊子支持会产出服务端拒绝的负载。白名单策略下，
遇到不支持的类型立刻报错并给出支持列表，行为可预测。

## Official documentation

- Notion API 版本与请求头：<https://developers.notion.com/reference/versioning>
- 创建页面（`POST /v1/pages` 与 `parent` 结构）：<https://developers.notion.com/reference/post-page>
- 查询数据库（游标分页、filter/sorts）：<https://developers.notion.com/reference/post-database-query>
- 块对象与类型清单：<https://developers.notion.com/reference/block>
- 富文本对象与 `annotations`：<https://developers.notion.com/reference/rich-text>
- 请求限速（约 3 req/s 与 429 处理）：<https://developers.notion.com/reference/request-limits>
- 集成授权模型（为何未授权返回 404）：<https://developers.notion.com/docs/authorization>
