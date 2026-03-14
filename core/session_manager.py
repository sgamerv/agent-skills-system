"""会话管理系统 - 管理会话生命周期和上下文"""
import json
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from models.session import Session, Message, SessionStatus
from config import settings


class SessionManager:
    """会话管理器 - 管理会话生命周期"""
    
    def __init__(self, redis_client=None, postgres_client=None):
        self.redis_client = redis_client
        self.postgres_client = postgres_client
    
    async def create_session(
        self,
        user_id: str,
        title: Optional[str] = None
    ) -> Session:
        """
        创建新会话
        
        Args:
            user_id: 用户 ID
            title: 会话标题(可选)
        
        Returns:
            Session 对象
        """
        session_id = str(uuid.uuid4())
        created_at = datetime.now()
        expires_at = created_at + timedelta(seconds=settings.SESSION_TIMEOUT)
        
        session = Session(
            session_id=session_id,
            user_id=user_id,
            status=SessionStatus.ACTIVE,
            title=title,
            created_at=created_at.isoformat(),
            updated_at=created_at.isoformat(),
            expires_at=expires_at.isoformat()
        )
        
        # 保存到 Redis
        if self.redis_client:
            await self._save_session_to_redis(session)
        
        return session
    
    async def get_session(self, session_id: str) -> Optional[Session]:
        """获取会话"""
        if self.redis_client:
            session = await self._load_session_from_redis(session_id)
            if session:
                return session
        return None
    
    async def update_session(
        self,
        session_id: str,
        **kwargs
    ) -> Optional[Session]:
        """更新会话"""
        session = await self.get_session(session_id)
        if not session:
            return None
        
        for key, value in kwargs.items():
            if hasattr(session, key):
                setattr(session, key, value)
        
        session.updated_at = datetime.now().isoformat()
        
        if self.redis_client:
            await self._save_session_to_redis(session)
        
        return session
    
    async def close_session(self, session_id: str):
        """关闭会话"""
        session = await self.get_session(session_id)
        if session:
            session.status = SessionStatus.TERMINATED
            session.updated_at = datetime.now().isoformat()
            
            if self.redis_client:
                await self._save_session_to_redis(session)
    
    async def archive_session(self, session_id: str):
        """归档会话"""
        session = await self.get_session(session_id)
        if session:
            session.status = SessionStatus.ARCHIVED
            session.updated_at = datetime.now().isoformat()
            
            if self.redis_client:
                await self._save_session_to_redis(session)
    
    async def get_user_sessions(
        self,
        user_id: str,
        status: Optional[SessionStatus] = None
    ) -> List[Session]:
        """获取用户的所有会话"""
        if not self.redis_client:
            return []
        
        pattern = f"session:{user_id}:*"
        keys = await self.redis_client.keys(pattern)
        
        sessions = []
        for key in keys:
            data = await self.redis_client.hgetall(key)
            if data and b'data' in data:
                session_dict = json.loads(data[b'data'].decode('utf-8'))
                session = Session.from_dict(session_dict)
                
                # 过滤状态
                if status and session.status != status:
                    continue
                
                sessions.append(session)
        
        # 按更新时间倒序排序
        sessions.sort(key=lambda s: s.updated_at or "", reverse=True)
        return sessions
    
    async def _save_session_to_redis(self, session: Session):
        """保存会话到 Redis"""
        key = f"session:{session.user_id}:{session.session_id}"
        data = session.to_dict()
        await self.redis_client.hset(key, mapping={
            "data": json.dumps(data, ensure_ascii=False),
            "updated_at": session.updated_at
        })
        await self.redis_client.expire(key, settings.SESSION_TIMEOUT + 3600)  # 1小时缓冲


class MessageManager:
    """消息管理器 - 管理对话消息"""
    
    def __init__(self, redis_client=None, postgres_client=None):
        self.redis_client = redis_client
        self.postgres_client = postgres_client
    
    async def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        conversation_id: Optional[str] = None,
        skill_name: Optional[str] = None,
        skill_result: Optional[Dict[str, Any]] = None
    ) -> Message:
        """
        添加消息
        
        Args:
            session_id: 会话 ID
            role: 角色(user/assistant/system)
            content: 消息内容
            conversation_id: 对话 ID(可选)
            skill_name: 执行的技能名称(可选)
            skill_result: 技能执行结果(可选)
        
        Returns:
            Message 对象
        """
        message_id = str(uuid.uuid4())
        created_at = datetime.now()
        
        message = Message(
            message_id=message_id,
            session_id=session_id,
            conversation_id=conversation_id,
            role=role,
            content=content,
            created_at=created_at.isoformat(),
            skill_name=skill_name,
            skill_result=skill_result
        )
        
        # 保存到 Redis
        if self.redis_client:
            await self._save_message_to_redis(message)
        
        return message
    
    async def get_session_messages(
        self,
        session_id: str,
        limit: int = 50
    ) -> List[Message]:
        """获取会话的所有消息"""
        if not self.redis_client:
            return []
        
        pattern = f"message:{session_id}:*"
        keys = await self.redis_client.keys(pattern)
        
        messages = []
        for key in keys:
            data = await self.redis_client.hgetall(key)
            if data and b'data' in data:
                message_dict = json.loads(data[b'data'].decode('utf-8'))
                message = Message.from_dict(message_dict)
                messages.append(message)
        
        # 按时间排序并限制数量
        messages.sort(key=lambda m: m.created_at or "")
        return messages[-limit:]
    
    async def get_conversation_messages(
        self,
        conversation_id: str
    ) -> List[Message]:
        """获取对话的所有消息"""
        if not self.redis_client:
            return []
        
        pattern = "message:*"
        keys = await self.redis_client.keys(pattern)
        
        messages = []
        for key in keys:
            data = await self.redis_client.hgetall(key)
            if data and b'data' in data:
                message_dict = json.loads(data[b'data'].decode('utf-8'))
                if message_dict.get('conversation_id') == conversation_id:
                    message = Message.from_dict(message_dict)
                    messages.append(message)
        
        # 按时间排序
        messages.sort(key=lambda m: m.created_at or "")
        return messages
    
    async def _save_message_to_redis(self, message: Message):
        """保存消息到 Redis"""
        key = f"message:{message.session_id}:{message.message_id}"
        data = message.to_dict()
        await self.redis_client.hset(key, mapping={
            "data": json.dumps(data, ensure_ascii=False)
        })
        await self.redis_client.expire(key, 3600 * 24 * 7)  # 7天过期


class ArchiveManager:
    """归档管理器 - 管理会话归档"""
    
    def __init__(self, session_manager: SessionManager, message_manager: MessageManager):
        self.session_manager = session_manager
        self.message_manager = message_manager
    
    async def archive_session(self, session_id: str):
        """
        归档会话及其所有消息
        
        Args:
            session_id: 会话 ID
        """
        # 获取会话的所有消息
        messages = await self.message_manager.get_session_messages(session_id)
        
        # TODO: 将会话和消息保存到持久化存储(PostgreSQL/S3)
        # 这里简化处理,只是标记会话为已归档
        
        await self.session_manager.archive_session(session_id)
    
    async def restore_session(self, session_id: str):
        """
        从归档恢复会话
        
        Args:
            session_id: 会话 ID
        """
        # TODO: 从持久化存储恢复会话和消息
        pass
