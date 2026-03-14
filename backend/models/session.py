"""会话相关数据模型"""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class SessionStatus(Enum):
    """会话状态"""
    ACTIVE = "active"        # 活跃
    ARCHIVED = "archived"    # 已归档
    TERMINATED = "terminated"  # 已终止


@dataclass
class Session:
    """会话信息"""
    session_id: str
    user_id: str
    status: SessionStatus = SessionStatus.ACTIVE
    
    # 会话元数据
    title: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    expires_at: Optional[str] = None
    
    # 统计信息
    message_count: int = 0
    dialogue_count: int = 0
    
    # 上下文数据
    context_data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "status": self.status.value,
            "title": self.title,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "expires_at": self.expires_at,
            "message_count": self.message_count,
            "dialogue_count": self.dialogue_count,
            "context_data": self.context_data
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Session':
        """从字典创建"""
        return cls(
            session_id=data["session_id"],
            user_id=data["user_id"],
            status=SessionStatus(data.get("status", "active")),
            title=data.get("title"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            expires_at=data.get("expires_at"),
            message_count=data.get("message_count", 0),
            dialogue_count=data.get("dialogue_count", 0),
            context_data=data.get("context_data", {})
        )


@dataclass
class Message:
    """消息"""
    message_id: str
    session_id: str
    role: str  # user, assistant, system
    content: str

    conversation_id: Optional[str] = None
    # 消息元数据
    created_at: Optional[str] = None
    
    # 关联信息
    skill_name: Optional[str] = None
    skill_result: Optional[Dict[str, Any]] = None
    
    # 评分和反馈
    rating: Optional[int] = None  # 1-5 星
    feedback: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "message_id": self.message_id,
            "session_id": self.session_id,
            "conversation_id": self.conversation_id,
            "role": self.role,
            "content": self.content,
            "created_at": self.created_at,
            "skill_name": self.skill_name,
            "skill_result": self.skill_result,
            "rating": self.rating,
            "feedback": self.feedback
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """从字典创建"""
        return cls(
            message_id=data["message_id"],
            session_id=data["session_id"],
            conversation_id=data.get("conversation_id"),
            role=data["role"],
            content=data["content"],
            created_at=data.get("created_at"),
            skill_name=data.get("skill_name"),
            skill_result=data.get("skill_result"),
            rating=data.get("rating"),
            feedback=data.get("feedback")
        )
