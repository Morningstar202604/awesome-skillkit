---
name: api-test-suite-builder
description: "Use when the user asks to generate API tests, create integration test suites, test REST endpoints, or build contract tests. 当用户要求 生成接口测试 / 写集成测试 / 契约测试 时使用。 Do NOT use for running the generated suites inside CI (it only generates them)."
license: Apache-2.0
compatibility: Pure prompt-based; may read project structure via Bash.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: api
  pattern: pipeline-builder
  tier: powerful
  verified-date: "2026-09-09"
---

# API Test Suite Builder

Scan API route definitions across frameworks (Next.js App Router, Express, FastAPI, Django REST) and generate ready-to-run test suites for Vitest+Supertest (Node) or Pytest+httpx (Python), covering auth, input validation, error codes, pagination, file uploads, and rate limiting.

## 输入清单

| 输入 | 必需 | 说明 |
|---|---|---|
| 项目根目录 | 是 | 含 API 路由定义的代码库路径 |
| 框架 | 是 | next-app-router / express / fastapi / django-rest（不确定时由步骤 1 探测命令判定） |
| 测试栈 | 是 | vitest+supertest（Node）或 pytest+httpx（Python） |
| 输出位置 | 否 | 测试文件目录，缺省按项目惯例（`tests/` 或 `__tests__/`） |
| 生成范围 | 否 | 全部路由或指定路由组；缺省全部 |

输入缺失时一次性问齐："请提供：① 项目根目录；② 测试栈（Vitest+Supertest 还是 Pytest+httpx）；③ 是否只生成部分路由。框架不确定我会先用探测命令判定。"

## 前置自检

逐条执行，任一失败 → 按修复处置后 STOP：

```bash
# 1. 项目目录存在
ls <项目根目录> > /dev/null && echo OK
# 预期：OK。失败→向用户确认路径，STOP。

# 2. 探测框架信号（至少一种命中）
ls <项目根目录>/package.json <项目根目录>/requirements.txt <项目根目录>/pyproject.toml 2>/dev/null
# 预期：至少列出一个文件。全部缺失→确认这是否 API 项目，STOP。

# 3. 测试运行器可用
node --version || python3 --version
# 预期：输出版本号。失败→测试文件生成不受影响，但向用户注明本地无法验证。
```

## 工作流

### 步骤 1：探测路由

按框架执行对应探测命令（在项目根目录）：

**Next.js App Router**
```bash
find ./app/api -name "route.ts" -o -name "route.js" | sort
grep -rn "export async function\|export function" app/api/**/route.ts | \
  grep -oE "(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)" | sort -u
find ./app/api -name "route.ts" | while read f; do
  route=$(echo $f | sed 's|./app||' | sed 's|/route.ts||')
  methods=$(grep -oE "export (async )?function (GET|POST|PUT|PATCH|DELETE)" "$f" | \
    grep -oE "(GET|POST|PUT|PATCH|DELETE)")
  echo "$methods $route"
done
```

**Express**
```bash
find ./src -name "*.ts" -o -name "*.js" | xargs grep -l "router\.\(get\|post\|put\|delete\|patch\)" 2>/dev/null
grep -rn "router\.\(get\|post\|put\|delete\|patch\)\|app\.\(get\|post\|put\|delete\|patch\)" \
  src/ --include="*.ts" | grep -oE "(get|post|put|delete|patch)\(['\"][^'\"]*['\"]"
grep -rn "router\.\|app\." src/ --include="*.ts" | \
  grep -oE "\.(get|post|put|delete|patch)\(['\"][^'\"]+['\"]" | \
  sed "s/\.\(.*\)('\(.*\)'/\U\1 \2/"
```

**FastAPI**
```bash
grep -rn "@app\.\|@router\." . --include="*.py" | \
  grep -E "@(app|router)\.(get|post|put|delete|patch)"
grep -rn "@\(app\|router\)\.\(get\|post\|put\|delete\|patch\)" . --include="*.py" | \
  grep -oE "@(app|router)\.(get|post|put|delete|patch)\(['\"][^'\"]*['\"]"
```

**Django REST Framework**
```bash
grep -rn "path\|re_path\|url(" . --include="*.py" | grep "urlpatterns" -A 50 | \
  grep -E "path\(['\"]" | grep -oE "['\"][^'\"]+['\"]" | head -40
grep -rn "router\.register\|DefaultRouter\|SimpleRouter" . --include="*.py"
```

- **预期**：输出路由→HTTP 方法映射，至少一条路由。
- **若失败**：输出为空 → 换下一种框架的探测命令；全空 → 该项目无 API 路由，回报并 STOP。

### 步骤 2：读取路由处理程序

- **动作**：逐个读路由文件，记录：请求体 schema、鉴权要求（middleware/decorator）、返回类型与状态码、业务规则（所有权/角色检查）。
- **预期**：每个路由都有一份上述四项记录；未知项显式标注而不是假设。
- **若失败**：路由文件无法定位处理逻辑 → 向用户确认该路由的契约后再生成，不要凭猜测写断言。

### 步骤 3：按矩阵生成测试

对每个鉴权端点生成 Auth 矩阵，对每个带请求体的 POST/PUT/PATCH 生成输入校验矩阵：

**Auth Test Matrix**（预期状态码）：

| Test Case | Expected Status |
|-----------|----------------|
| No Authorization header | 401 |
| Invalid token format | 401 |
| Valid token, wrong user role | 403 |
| Expired JWT token | 401 |
| Valid token, correct role | 2xx |
| Token from deleted user | 401 |

**Input Validation Matrix**（预期状态码）：

| Test Case | Expected Status |
|-----------|----------------|
| Empty body `{}` | 400 or 422 |
| Missing required fields (one at a time) | 400 or 422 |
| Wrong type (string where int expected) | 400 or 422 |
| Boundary: value at min-1 | 400 or 422 |
| Boundary: value at min | 2xx |
| Boundary: value at max | 2xx |
| Boundary: value at max+1 | 400 or 422 |
| SQL injection in string field | 400 or 200 (sanitized) |
| XSS payload in string field | 400 or 200 (sanitized) |
| Null values for required fields | 400 or 422 |

生成规则：
1. 测试名描述化：`"returns 401 when token is expired"`，不用 `"auth test 3"`
2. 用 factories/fixtures 构造数据，绝不硬编码 ID
3. 断言响应结构，不只是状态码
4. 每个端点一个 describe block
5. 敏感字段（password/secret）断言不出现在响应中

- **预期**：每个路由组产出一个测试文件；文件内矩阵条目与上表一一对应。
- **若失败**：某矩阵项无法落地（如路由无鉴权）→ 删除该行并在文件头注释说明原因，不得留空测试。

### 步骤 4：验证产物

- **动作**：运行 `node --test` / `npx vitest list` 或 `python3 -m pytest --collect-only <生成的文件>` 验证语法可解析。
- **预期**：collect/test-list 输出包含全部生成的测试名，无语法错误。
- **若失败**：语法报错 → 修复生成文件后重跑收集；仍失败 → 回报生成器输出有误。

## 失败处置表

| 现象/错误码 | 原因 | 处置 |
|---|---|---|
| 探测命令输出为空 | 框架判定错误或无路由 | 依次尝试四种框架探测；全空则 STOP 回报 |
| pytest collect 报 SyntaxError | 生成文件语法错误 | 修复后重跑 `--collect-only` |
| 路由契约不明 | 处理程序逻辑分散/中间件隐式 | 向用户确认契约，禁止猜测断言 |
| 测试间相互污染 | 共享状态未清理 | 在 afterEach/afterAll 中清理，rate limit 测试放最后单独跑 |

## 交付标准

- 成功定义：扫描到的每条路由都有对应测试块；Auth/输入校验矩阵按表落地；步骤 4 collect 通过。
- 产物命名：每路由组一个文件，如 `tests/test_<route-group>_api.py` 或 `__tests__/<route-group>.test.ts`。
- 保存位置：项目测试目录（`tests/` / `__tests__/`），或用户指定位置。
- 完整性验证：`--collect-only`（pytest）或 `vitest list`（vitest）能列出全部测试名，数量与生成清单一致。

## 参考

- `references/example-test-files.md` — Vitest+Supertest 与 Pytest+httpx 的完整示例测试文件；步骤 3 生成前通读一遍，按其风格生成。
