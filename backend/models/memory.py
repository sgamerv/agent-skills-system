"""记忆相关数据模型"""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class MemoryType(Enum):
    """记忆类型"""
    FACT = "fact"              # 事实记忆
    PREFERENCE = "preference"  # 偏好记忆
    CONTEXT = "context"        # 上下文记忆
    PATTERN = "pattern"        # 模式记忆


class MemorySource(Enum):
    """记忆来源"""
    EXPLICIT = "explicit"  # 用户明确提供
    INFERRED = "inferred"  # 系统推断
    LEARNED = "learned"    # 通过学习获得


@dataclass
class Memory:
    """记忆条目"""
    memory_id: str
    user_id: str
    memory_type: MemoryType
    content: str
    
    # 记忆详情
    key: Optional[str] = None  # 用于检索的键
    value: Optional[Any] = None
    source: MemorySource = MemorySource.EXPLICIT
    
    # 重要性
    importance: float = 1.0  # 0-1
    
    # 时间信息
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    expires_at: Optional[str] = None
    
    # 访问统计
    access_count: int = 0
    last_accessed_at: Optional[str] = None
    
    # 关联信息
    related_memories: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "memory_id": self.memory_id,
            "user_id": self.user_id,
            "memory_type": self.memory_type.value,
            "content": self.content,
            "key": self.key,
            "value": self.value,
            "source": self.source.value,
            "importance": self.importance,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "expires_at": self.expires_at,
            "access_count": self.access_count,
            "last_accessed_at": self.last_accessed_at,
            "related_memories": self.related_memories,
            "tags": self.tags
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Memory':
        """从字典创建"""
        return cls(
            memory_id=data["memory_id"],
            user_id=data["user_id"],
            memory_type=MemoryType(data["memory_type"]),
            content=data["content"],
            key=data.get("key"),
            value=data.get("value"),
            source=MemorySource(data.get("source", "explicit")),
            importance=data.get("importance", 1.0),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            expires_at=data.get("expires_at"),
            access_count=data.get("access_count", 0),
            last_accessed_at=data.get("last_accessed_at"),
            related_memories=data.get("related_memories", []),
            tags=data.get("tags", [])
        )


@dataclass
class UserProfile:
    """用户画像"""
    user_id: str
    
    # 基本信息
    name: Optional[str] = None
    email: Optional[str] = None
    
    # 偏好设置
    preferences: Dict[str, Any] = field(default_factory=dict)
    
    # 技能使用统计
    skill_usage: Dict[str, int] = field(default_factory=dict)
    
    # 行为模式
    behavior_patterns: Dict[str, Any] = field(default_factory=dict)
    
    # 时间信息
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    # 统计信息
    total_dialogues: int = 0
    total_messages: int = 0
    satisfaction_score: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
            "preferences": self.preferences,
            "skill_usage": self.skill_usage,
            "behavior_patterns": self.behavior_patterns,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "total_dialogues": self.total_dialogues,
            "total_messages": self.total_messages,
            "satisfaction_score": self.satisfaction_score
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserProfile':
        """从字典创建"""
        return cls(
            user_id=data["user_id"],
            name=data.get("name"),
            email=data.get("email"),
            preferences=data.get("preferences", {}),
            skill_usage=data.get("skill_usage", {}),
            behavior_patterns=data.get("behavior_patterns", {}),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            total_dialogues=data.get("total_dialogues", 0),
            total_messages=data.get("total_messages", 0),
            satisfaction_score=data.get("satisfaction_score")
        )
