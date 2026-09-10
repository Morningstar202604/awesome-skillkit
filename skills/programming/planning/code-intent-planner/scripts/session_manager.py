#!/usr/bin/env python3
"""Session 管理器 — 跨轮累积、缓存、状态持久化"""
import json
import os
import time
import hashlib
from dataclasses import dataclass, asdict, field
from typing import Optional
from pathlib import Path


SESSION_DIR = Path.home() / ".code_intent_planner" / "sessions"
SESSION_DIR.mkdir(parents=True, exist_ok=True)
SESSION_TTL = 24 * 3600  # 24 小时


@dataclass
class Slot:
    name: str
    value: str
    evidence: str  # verified | provisional | assumed
    confidence: float = 1.0


@dataclass
class IntentState:
    intent_type: str
    confidence: float
    source_layer: str
    slots: list[Slot] = field(default_factory=list)
    constraints_hard: list[str] = field(default_factory=list)
    constraints_soft: list[str] = field(default_factory=list)
    description: str = ""
    sub_tasks: list[dict] = field(default_factory=list)
    critical_path: list[str] = field(default_factory=list)
    parallel_groups: list[list[str]] = field(default_factory=list)
    solution: str = ""
    assumptions: list[dict] = field(default_factory=list)
    timestamp: str = ""


@dataclass
class SessionState:
    session_id: str
    turn: int = 0
    last_intent: Optional[IntentState] = None
    slots_history: list[dict] = field(default_factory=list)
    intent_history: list[dict] = field(default_factory=list)
    pending_slots: list[str] = field(default_factory=list)
    cache: dict = field(default_factory=dict)
    created_at: str = ""
    updated_at: str = ""


class SessionManager:
    def __init__(self):
        self.session_dir = SESSION_DIR

    def _session_file(self, session_id: str) -> Path:
        return self.session_dir / f"_session_{session_id}.json"

    def _cache_key(self, session_id: str, intent_type: str, text: str) -> str:
        """生成缓存键：session_id:intent_type:hash(text[:100])"""
        h = hashlib.md5(text[:100].encode()).hexdigest()[:16]
        return f"{session_id}:{intent_type}:{h}"

    def load(self, session_id: str) -> SessionState:
        """加载 session 状态"""
        f = self._session_file(session_id)
        if not f.exists():
            return SessionState(
                session_id=session_id,
                turn=0,
                created_at=time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                updated_at=time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            )
        data = json.loads(f.read_text())
        state = SessionState(**data)
        if state.last_intent:
            state.last_intent = IntentState(**state.last_intent)
        return state

    def save(self, state: SessionState):
        """保存 session 状态"""
        state.updated_at = time.strftime("%Y-%m-%dT%H:%M:%SZ")
        f = self._session_file(state.session_id)
        # 转换为可序列化格式
        data = asdict(state)
        if state.last_intent:
            data["last_intent"] = asdict(state.last_intent)
        f.write_text(json.dumps(data, ensure_ascii=False, indent=2))

    def new_session(self, session_id: Optional[str] = None) -> SessionState:
        """创建新 session"""
        if not session_id:
            session_id = f"auto_{time.strftime('%Y%m%d_%H%M%S')}"
        return SessionState(
            session_id=session_id,
            turn=0,
            created_at=time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            updated_at=time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        )

    def merge_slots(self, state: SessionState, new_slots: list[Slot], new_intent: IntentState) -> list[Slot]:
        """合并槽位：latest-wins + 冲突检测"""
        merged = {}
        # 先加载历史槽位
        for slot in state.last_intent.slots if state.last_intent else []:
            merged[slot.name] = slot

        # 合并新槽位
        for slot in new_slots:
            if slot.name in merged:
                old = merged[slot.name]
                if old.value != slot.value:
                    # 冲突：标记 provisional，请用户裁决
                    slot.evidence = "provisional"
                    slot.confidence = min(slot.confidence, 0.7)
            merged[slot.name] = slot

        return list(merged.values())

    def inject_last_intent(self, state: SessionState) -> dict:
        """将上一轮意图注入上下文"""
        if not state.last_intent:
            return {}
        return {
            "last_intent_type": state.last_intent.intent_type,
            "last_slots": {s.name: s.value for s in state.last_intent.slots},
            "last_description": state.last_intent.description,
        }

    def get_cache(self, state: SessionState, intent_type: str, text: str) -> Optional[dict]:
        """获取缓存"""
        key = self._cache_key(state.session_id, intent_type, text)
        return state.cache.get(key)

    def set_cache(self, state: SessionState, intent_type: str, text: str, value: dict):
        """设置缓存"""
        key = self._cache_key(state.session_id, intent_type, text)
        state.cache[key] = value

    def cleanup_expired(self):
        """清理过期 session"""
        now = time.time()
        for f in self.session_dir.glob("_session_*.json"):
            try:
                data = json.loads(f.read_text())
                updated = time.mktime(time.strptime(data.get("updated_at", ""), "%Y-%m-%dT%H:%M:%SZ"))
                if now - updated > SESSION_TTL:
                    f.unlink()
            except Exception:
                pass


def create_session_id() -> str:
    return f"auto_{time.strftime('%Y%m%d_%H%M%S')}"


if __name__ == "__main__":
    mgr = SessionManager()
    mgr.cleanup_expired()
    print("Session manager ready")