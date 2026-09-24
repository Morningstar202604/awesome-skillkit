# Code Generation Case Library

> Sources: real projects + edge-case tests

## Table of Contents

- [Case 1: L1 template direct generation (Python FastAPI CRUD)](#case-1)
- [Case 2: L2 LLM generation (complex business logic)](#case-2)
- [Case 3: Bug fix generation](#case-3)
- [Case 4: Multi-intent mixed generation](#case-4)
- [Case 5: L1 no match → L2 fallback](#case-5)
- [Case 6: Generated validation fails → retry](#case-6)
- [Case sources](#case-sources)

---

<a id="case-1"></a>

## Case 1: L1 template direct generation (Python FastAPI CRUD)

**Input (from code-intent-planner):**
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
    {"id": "T1", "description": "Design the data model", "priority": "P0"},
    {"id": "T2", "description": "Implement the service layer", "priority": "P0"},
    {"id": "T3", "description": "Implement the API endpoints", "priority": "P1"}
  ]
}
```

**Output files:**
```
src/product/models.py    (42 lines)
src/product/service.py   (68 lines)
src/product/api.py       (55 lines)
```

**Generated models.py snippet:**
```python
class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    stock: int = Field(..., ge=0)
```

---

<a id="case-2"></a>

## Case 2: L2 LLM generation (complex business logic)

**Input:**
```json
{
  "intent_type": "implement",
  "confidence": 0.55,
  "source_layer": "L2",
  "description": "Implement the inventory deduction logic, requiring a distributed lock",
  "slots": [
    {"name": "target", "value": "inventory", "evidence": "verified"},
    {"name": "scope", "value": "deduct+lock", "evidence": "provisional"}
  ]
}
```

**Analysis:** L1 has no inventory-deduction template → escalate to L2

**L2 prompt injection:**
- Project tech stack: python/fastapi + redis
- Existing modules: auth, orders
- Code-style samples: 2 representative files

**L2 output:**
```python
# src/inventory/service.py
import redis
from typing import Optional
from src.auth.models import User

class InventoryService:
    def __init__(self):
        self.redis = redis.Redis(host='localhost', port=6379)
    
    def deduct(self, product_id: int, quantity: int, user: User) -> bool:
        """Deduct stock under a distributed lock"""
        lock_key = f"inventory:lock:{product_id}"
        with redis.lock(lock_key, timeout=10):
            # check stock
            stock = self.redis.get(f"inventory:{product_id}:stock")
            if not stock or int(stock) < quantity:
                raise InsufficientStockError(product_id)
            # deduct
            self.redis.decrby(f"inventory:{product_id}:stock", quantity)
            # log
            self.redis.lpush("inventory:log", f"{user.id} deducted {quantity}")
            return True
```

---

<a id="case-3"></a>

## Case 3: Bug fix generation

**Input:**
```json
{
  "intent_type": "fix",
  "subtype": "runtime",
  "confidence": 0.95,
  "source_layer": "L1",
  "description": "Fix the null pointer crash on user login",
  "slots": [
    {"name": "target", "value": "auth", "evidence": "verified"},
    {"name": "scope", "value": "login", "evidence": "verified"}
  ]
}
```

**Output (annotated fix):**
```python
# src/auth/service.py
def login(self, username: str, password: str) -> Optional[Token]:
    """
    Fixed: fix the null pointer crash
    
    Root cause: the user object may be None while .email is accessed directly
    Before:
        return Token(user.email, user.id)  # crash if user is None
    
    After:
        add a guard clause
    """
    user = self.find_by_username(username)
    if not user:  # ← new guard
        logger.warning(f"Login failed: user {username} not found")
        return None
    
    if not self.verify_password(password, user.password_hash):
        return None
    
    return Token(user.email, user.id)
```

---

<a id="case-4"></a>

## Case 4: Multi-intent mixed generation

**Input (multi-intent):**
```json
{
  "primary_intent": "implement",
  "secondary_intents": ["test"],
  "recommendation": "Implement the API first, then write the tests",
  "sub_tasks": [
    {"id": "T1", "description": "Implement the user registration API", "priority": "P0"},
    {"id": "T2", "description": "Write registration API tests", "priority": "P0", "depends_on": ["T1"]}
  ]
}
```

**Output:** (the following paths are relative to **the generated project's root**, not to files in this skill pack)

```text
1. First generate src/auth/api.py (T1)
2. Then generate tests/test_auth_api.py (T2, depends on T1)
```

The two outputs come respectively from the FastAPI CRUD template and the test stub template under `references/templates/`;
after rendering, both must pass the syntax check in SKILL.md step 4 before being written to disk.

---

<a id="case-5"></a>

## Case 5: L1 no match → L2 fallback

**Input:**
```json
{
  "intent_type": "implement",
  "confidence": 0.88,
  "source_layer": "L1",
  "description": "Implement a real-time chat WebSocket service",
  "slots": [
    {"name": "target", "value": "chat", "evidence": "verified"},
    {"name": "scope", "value": "websocket+realtime", "evidence": "provisional"}
  ]
}
```

**Analysis:** L1 has no WebSocket template → auto-escalate to L2

**L2 output:**
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

## Case 6: Generated validation fails → retry

**Input:**
```json
{
  "intent_type": "implement",
  "source_layer": "L1",
  "description": "Implement the user module"
}
```

**L1 generation:**
```python
# src/user/models.py
from pydantic import BaseModel
class UserCreate(BaseModel):
    name: str
```

**Validation failure:** `ImportError: cannot import name 'Field' from 'pydantic'`

**Handling:** 
1. Detected a pydantic v1/v2 compatibility issue
2. Auto-adjusted the template (removed the Field import)
3. Regenerated → passed

---

<a id="case-sources"></a>

## Case sources

| Case | Source | Scenario |
|------|------|------|
| Case 1 | Real e-commerce project | Standard CRUD |
| Case 2 | Concurrency programming challenge | Distributed lock |
| Case 3 | Bug report | Runtime error fix |
| Case 4 | Multi-step requirement | Master/slave task dependency |
| Case 5 | New technology introduction | WebSocket |
| Case 6 | Version compatibility | Library version differences |
