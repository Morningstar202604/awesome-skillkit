# 代码生成案例库

> 来源：真实项目 + 边缘场景测试

## 目录

- [案例 1：L1 模板直接生成（Python FastAPI CRUD）](#case-1)
- [案例 2：L2 LLM 生成（复杂业务逻辑）](#case-2)
- [案例 3：Bug Fix 生成](#case-3)
- [案例 4：多意图混合生成](#case-4)
- [案例 5：L1 无匹配 → L2 兜底](#case-5)
- [案例 6：生成验证失败 → 重试](#case-6)
- [案例来源](#case-sources)

---

<a id="case-1"></a>

## 案例 1：L1 模板直接生成（Python FastAPI CRUD）

**输入（来自 code-intent-planner）：**
```json
{
  "intent_type": "implement",
  "confidence": 0.90,
  "source_layer": "L1",
  "slots": [
    {"name": "target", "value": "product", "evidence": "verified"},
    {"name": "scope", "value": "crud", "evidence": "provisional"}
  ],
  "sub_tasks": [
    {"id": "T1", "description": "设计数据模型", "priority": "P0"},
    {"id": "T2", "description": "实现服务层", "priority": "P0"},
    {"id": "T3", "description": "实现 API 接口", "priority": "P1"}
  ]
}
```

**输出文件：**
```
src/product/models.py    (42 行)
src/product/service.py   (68 行)
src/product/api.py       (55 行)
```

**生成的 models.py 片段：**
```python
class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    stock: int = Field(..., ge=0)
```

---

<a id="case-2"></a>

## 案例 2：L2 LLM 生成（复杂业务逻辑）

**输入：**
```json
{
  "intent_type": "implement",
  "confidence": 0.55,
  "source_layer": "L2",
  "description": "实现库存扣减逻辑，需要分布式锁",
  "slots": [
    {"name": "target", "value": "inventory", "evidence": "verified"},
    {"name": "scope", "value": "deduct+lock", "evidence": "provisional"}
  ]
}
```

**分析：** L1 无库存扣减模板 → 升级 L2

**L2 Prompt 注入：**
- 项目技术栈：python/fastapi + redis
- 已有模块：auth, orders
- 代码风格样本：2 个代表性文件

**L2 输出：**
```python
# src/inventory/service.py
import redis
from typing import Optional
from src.auth.models import User

class InventoryService:
    def __init__(self):
        self.redis = redis.Redis(host='localhost', port=6379)
    
    def deduct(self, product_id: int, quantity: int, user: User) -> bool:
        """分布式锁扣减库存"""
        lock_key = f"inventory:lock:{product_id}"
        with redis.lock(lock_key, timeout=10):
            # 检查库存
            stock = self.redis.get(f"inventory:{product_id}:stock")
            if not stock or int(stock) < quantity:
                raise InsufficientStockError(product_id)
            # 扣减
            self.redis.decrby(f"inventory:{product_id}:stock", quantity)
            # 记录日志
            self.redis.lpush("inventory:log", f"{user.id} deducted {quantity}")
            return True
```

---

<a id="case-3"></a>

## 案例 3：Bug Fix 生成

**输入：**
```json
{
  "intent_type": "fix",
  "subtype": "runtime",
  "confidence": 0.95,
  "source_layer": "L1",
  "description": "修复用户登录时 null pointer crash",
  "slots": [
    {"name": "target", "value": "auth", "evidence": "verified"},
    {"name": "scope", "value": "login", "evidence": "verified"}
  ]
}
```

**输出（带注释的修复）：**
```python
# src/auth/service.py
def login(self, username: str, password: str) -> Optional[Token]:
    """
    Fixed: 修复 null pointer crash
    
    Root cause: user 对象可能为 None 时直接访问 .email
    Before:
        return Token(user.email, user.id)  # crash if user is None
    
    After:
        添加 guard clause
    """
    user = self.find_by_username(username)
    if not user:  # ← 新增 guard
        logger.warning(f"Login failed: user {username} not found")
        return None
    
    if not self.verify_password(password, user.password_hash):
        return None
    
    return Token(user.email, user.id)
```

---

<a id="case-4"></a>

## 案例 4：多意图混合生成

**输入（多意图）：**
```json
{
  "primary_intent": "implement",
  "secondary_intents": ["test"],
  "recommendation": "先实现 API，再写测试",
  "sub_tasks": [
    {"id": "T1", "description": "实现用户注册 API", "priority": "P0"},
    {"id": "T2", "description": "编写注册 API 测试", "priority": "P0", "depends_on": ["T1"]}
  ]
}
```

**输出：**（下列路径相对**被生成项目的根目录**，不是本技能包内的文件）

```text
1. 先生成 src/auth/api.py（T1）
2. 再生成 tests/test_auth_api.py（T2，依赖 T1 完成）
```

两次产出分别来自 `references/templates/` 下的 FastAPI CRUD 模板与测试桩模板，
渲染后都需先过 SKILL.md 步骤 4 的语法校验才落盘。

---

<a id="case-5"></a>

## 案例 5：L1 无匹配 → L2 兜底

**输入：**
```json
{
  "intent_type": "implement",
  "confidence": 0.88,
  "source_layer": "L1",
  "description": "实现一个实时聊天 WebSocket 服务",
  "slots": [
    {"name": "target", "value": "chat", "evidence": "verified"},
    {"name": "scope", "value": "websocket+realtime", "evidence": "provisional"}
  ]
}
```

**分析：** L1 无 WebSocket 模板 → 自动升级 L2

**L2 输出：**
```python
# src/chat/handler.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Set

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, room: str):
        await websocket.accept()
        self.active_connections[websocket.client.host] = websocket
    
    async def disconnect(self, websocket: WebSocket):
        self.active_connections.pop(websocket.client.host, None)
    
    async def send_personal(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

manager = ConnectionManager()

router = APIRouter()

@router.websocket("/ws/{room}")
async def websocket_endpoint(websocket: WebSocket, room: str):
    await manager.connect(websocket, room)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal(f"Room {room}: {data}", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
```

---

<a id="case-6"></a>

## 案例 6：生成验证失败 → 重试

**输入：**
```json
{
  "intent_type": "implement",
  "source_layer": "L1",
  "description": "实现用户模块"
}
```

**L1 生成：**
```python
# src/user/models.py
from pydantic import BaseModel
class UserCreate(BaseModel):
    name: str
```

**验证失败：** `ImportError: cannot import name 'Field' from 'pydantic'`

**处置：** 
1. 检测到 pydantic v1/v2 兼容性问题
2. 自动调整模板（移除 Field 导入）
3. 重新生成 → 通过

---

<a id="case-sources"></a>

## 案例来源

| 案例 | 来源 | 场景 |
|------|------|------|
| 案例 1 | 真实电商项目 | 标准 CRUD |
| 案例 2 | 并发编程挑战 | 分布式锁 |
| 案例 3 | Bug 报告 | 运行时错误修复 |
| 案例 4 | 多步骤需求 | 主从任务依赖 |
| 案例 5 | 新技术引入 | WebSocket |
| 案例 6 | 版本兼容性 | 库版本差异 |
