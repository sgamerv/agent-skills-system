"""对话相关数据模型"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class DialogueState(Enum):
    """对话状态"""
    INITIALIZING = "initializing"      # 初始化
    SLOT_FILLING = "slot_filling"      # 填充槽位
    EXECUTING = "executing"            # 执行中
    WAITING_CONFIRMATION = "waiting_confirmation"  # 等待确认
    COMPLETED = "completed"            # 完成
    FAILED = "failed"                  # 失败


@dataclass
class SlotValue:
    """槽位值"""
    name: str
    value: Any
    source: str = "user"  # user, default, inferred
    confidence: float = 1.0
    timestamp: Optional[str] = None


@dataclass
class SlotDefinition:
    """槽位定义"""
    name: str
    type: str  # string, number, enum, file, boolean, array, object, date, email
    required: bool
    description: str
    prompt: str
    options: Optional[Dict[str, str]] = None
    validation: Optional[Dict[str, Any]] = None
    default_value: Optional[Any] = None
    depends_on: Optional[List[str]] = None  # 依赖的槽位名称列表


@dataclass
class DialogueContext:
    """对话上下文"""
    conversation_id: str
    user_id: str
    skill_name: str
    state: DialogueState = DialogueState.INITIALIZING

    # 槽位信息
    slots_def: List[SlotDefinition] = field(default_factory=list)
    filled_slots: Dict[str, SlotValue] = field(default_factory=dict)
    pending_slots: List[str] = field(default_factory=list)  # 待填充的槽位

    # 对话历史
    messages: List[Dict[str, Any]] = field(default_factory=list)

    # 上下文数据
    context_data: Dict[str, Any] = field(default_factory=dict)

    # 元数据
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def is_ready_for_execution(self) -> bool:
        """检查是否所有必填槽位都已填充"""
        for slot_def in self.slots_def:
            if slot_def.required and slot_def.name not in self.filled_slots:
                return False
        return True

    def get_next_slot_to_fill(self) -> Optional[SlotDefinition]:
        """获取下一个需要填充的槽位"""
        for slot_name in self.pending_slots:
            # 检查依赖是否满足
            slot_def = self._get_slot_def(slot_name)
            if slot_def and self._dependencies_met(slot_def):
                return slot_def
        return None

    def _dependencies_met(self, slot_def: SlotDefinition) -> bool:
        """检查槽位的依赖是否已满足"""
        if not slot_def.depends_on:
            return True

        for dep_slot in slot_def.depends_on:
            if dep_slot not in self.filled_slots:
                return False
        return True

    def _get_slot_def(self, slot_name: str) -> Optional[SlotDefinition]:
        """获取槽位定义"""
        for slot_def in self.slots_def:
            if slot_def.name == slot_name:
                return slot_def
        return None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "conversation_id": self.conversation_id,
            "user_id": self.user_id,
            "skill_name": self.skill_name,
            "state": self.state.value,
            "slots_def": [
                {
                    "name": slot.name,
                    "type": slot.type,
                    "required": slot.required,
                    "description": slot.description,
                    "prompt": slot.prompt,
                    "options": slot.options,
                    "validation": slot.validation,
                    "default_value": slot.default_value,
                    "depends_on": slot.depends_on
                }
                for slot in self.slots_def
            ],
            "filled_slots": {
                name: {
                    "name": value.name,
                    "value": value.value,
                    "source": value.source,
                    "confidence": value.confidence,
                    "timestamp": value.timestamp
                }
                for name, value in self.filled_slots.items()
            },
            "pending_slots": self.pending_slots,
            "messages": self.messages,
            "context_data": self.context_data,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DialogueContext':
        """从字典创建"""
        slots_def = [
            SlotDefinition(**slot) for slot in data.get("slots_def", [])
        ]
        filled_slots = {
            name: SlotValue(**value)
            for name, value in data.get("filled_slots", {}).items()
        }
        
        return cls(
            conversation_id=data["conversation_id"],
            user_id=data["user_id"],
            skill_name=data["skill_name"],
            state=DialogueState(data.get("state", "initializing")),
            slots_def=slots_def,
            filled_slots=filled_slots,
            pending_slots=data.get("pending_slots", []),
            messages=data.get("messages", []),
            context_data=data.get("context_data", {}),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )
