# 代码模式速查表

## Python FastAPI CRUD

### 适用场景
- 实现新的资源模块（用户、订单、商品等）
- 标准 RESTful API + 数据模型 + 服务层

### 文件结构
```
src/{target}/
├── models.py    # Pydantic 模型（Create/Update/Base）
├── service.py   # 业务逻辑（CRUD 操作）
└── api.py       # FastAPI 路由（REST 接口）
```

### 字段推断规则
| scope 关键词 | 推断字段 |
|-------------|---------|
| auth/login | username, password_hash, email |
| user | username, email, name |
| order | user_id, total, status, items |
| product | name, price, description, stock |
| comment | content, user_id, post_id |

---

## TypeScript Express CRUD

### 适用场景
- Node.js/Express REST API
- TypeScript 项目

### 文件结构
```
src/{target}/
├── {target}.router.ts    # 路由定义
├── {target}.service.ts   # 服务层
├── {target}.model.ts     # 类型定义
└── {target}.dto.ts       # 数据传输对象
```

---

## Go Gin CRUD

### 适用场景
- Go + Gin 框架
- 高性能 API 服务

### 文件结构
```
internal/{target}/
├── model.go      # 数据结构
├── handler.go    # HTTP 处理器
├── service.go    # 业务逻辑
└── repository.go # 数据访问
```

---

## Bug Fix 模式

### 适用场景
- 修复运行时错误（crash、panic、exception）
- 需要标注根因和修复说明

### 文件规范
1. 在修复处添加注释块，说明：
   - Root cause（根因）
   - Before（修复前）
   - After（修复后）
2. 添加 guard clause 防止再次触发
3. 添加日志记录异常场景

---

## 测试桩生成规则

### 覆盖场景
1. **Happy path** — 正常流程
2. **Edge case** — 边界条件
3. **Error handling** — 错误处理

### 命名规范
- 测试类：`Test{ClassName}`
- 测试方法：`test_{方法名}_{场景}`

### 断言规范
- 使用 `assert` 而非 `assertTrue`
- 明确指定期望值
- 错误信息包含上下文
