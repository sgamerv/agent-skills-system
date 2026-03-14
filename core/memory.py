"""记忆系统 - 管理短期记忆、长期记忆和用户画像"""
import json
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime

from models.memory import Memory, MemoryType, MemorySource, UserProfile


class MemoryExtractor:
    """记忆提取器 - 从对话中提取关键信息"""
    
    def __init__(self, llm):
        self.llm = llm
    
    async def extract_facts(
        self,
        conversation_history: List[Dict[str, Any]],
        user_id: str
    ) -> List[Memory]:
        """
        从对话历史中提取事实信息
        
        Args:
            conversation_history: 对话历史
            user_id: 用户 ID
        
        Returns:
            提取的记忆列表
        """
        if not conversation_history:
            return []
        
        # 构建对话文本
        dialogue_text = "\n".join([
            f"{msg['role']}: {msg['content']}"
            for msg in conversation_history[-10:]  # 只取最近10条消息
        ])
        
        prompt = f"""从以下对话中提取关键事实信息:

对话内容:
{dialogue_text}

以 JSON 格式返回提取的事实:
{{
  "facts": [
    {{
      "key": "用户名/公司名/项目名等",
      "value": "具体值",
      "importance": 0.9,
      "content": "完整描述"
    }}
  ]
}}

只提取明确陈述的事实,不要推断。
"""
        
        try:
            response = await self.llm.ainvoke(prompt)
            response = response.strip()
            
            # 清理响应
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            data = json.loads(response)
            facts = data.get("facts", [])
            
            memories = []
            for fact in facts:
                memory = Memory(
                    memory_id=str(uuid.uuid4()),
                    user_id=user_id,
                    memory_type=MemoryType.FACT,
                    content=fact.get("content", ""),
                    key=fact.get("key"),
                    value=fact.get("value"),
                    source=MemorySource.INFERRED,
                    importance=fact.get("importance", 0.8),
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat()
                )
                memories.append(memory)
            
            return memories
        except Exception as e:
            print(f"Error extracting facts: {e}")
            return []
    
    async def extract_preferences(
        self,
        conversation_history: List[Dict[str, Any]],
        user_id: str
    ) -> List[Memory]:
        """
        从对话历史中提取用户偏好
        
        Args:
            conversation_history: 对话历史
            user_id: 用户 ID
        
        Returns:
            提取的记忆列表
        """
        if not conversation_history:
            return []
        
        dialogue_text = "\n".join([
            f"{msg['role']}: {msg['content']}"
            for msg in conversation_history[-10:]
        ])
        
        prompt = f"""从以下对话中提取用户偏好信息:

对话内容:
{dialogue_text}

以 JSON 格式返回提取的偏好:
{{
  "preferences": [
    {{
      "key": "偏好类型(如: 分析类型、图表类型、输出格式等)",
      "value": "具体偏好值",
      "importance": 0.9,
      "content": "完整描述"
    }}
  ]
}}

只提取明确表达的偏好。
"""
        
        try:
            response = await self.llm.ainvoke(prompt)
            response = response.strip()
            
            # 清理响应
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            data = json.loads(response)
            preferences = data.get("preferences", [])
            
            memories = []
            for pref in preferences:
                memory = Memory(
                    memory_id=str(uuid.uuid4()),
                    user_id=user_id,
                    memory_type=MemoryType.PREFERENCE,
                    content=pref.get("content", ""),
                    key=pref.get("key"),
                    value=pref.get("value"),
                    source=MemorySource.INFERRED,
                    importance=pref.get("importance", 0.8),
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat()
                )
                memories.append(memory)
            
            return memories
        except Exception as e:
            print(f"Error extracting preferences: {e}")
            return []


class MemoryManager:
    """记忆管理器 - 管理记忆的存储和检索"""
    
    def __init__(self, redis_client=None):
        self.redis_client = redis_client
    
    async def save_memory(self, memory: Memory):
        """保存记忆"""
        if not self.redis_client:
            return
        
        key = f"memory:{memory.user_id}:{memory.memory_id}"
        data = memory.to_dict()
        await self.redis_client.hset(key, mapping={
            "data": json.dumps(data, ensure_ascii=False),
            "updated_at": memory.updated_at or datetime.now().isoformat()
        })
        
        # 设置过期时间
        ttl = 3600 * 24 * 30  # 30天
        if memory.expires_at:
            # 计算到过期时间的秒数
            from datetime import datetime
            expires = datetime.fromisoformat(memory.expires_at)
            ttl = int((expires - datetime.now()).total_seconds())
        
        await self.redis_client.expire(key, ttl)
    
    async def get_memories(
        self,
        user_id: str,
        memory_type: Optional[MemoryType] = None,
        limit: int = 10
    ) -> List[Memory]:
        """获取用户的记忆"""
        if not self.redis_client:
            return []
        
        pattern = f"memory:{user_id}:*"
        keys = await self.redis_client.keys(pattern)
        
        memories = []
        for key in keys[:limit]:
            data = await self.redis_client.hgetall(key)
            if data and b'data' in data:
                memory_dict = json.loads(data[b'data'].decode('utf-8'))
                
                # 过滤类型
                if memory_type and MemoryType(memory_dict.get('memory_type')) != memory_type:
                    continue
                
                memory = Memory.from_dict(memory_dict)
                memories.append(memory)
        
        # 按重要性排序
        memories.sort(key=lambda m: m.importance, reverse=True)
        return memories
    
    async def search_memories(
        self,
        user_id: str,
        query: str,
        limit: int = 5
    ) -> List[Memory]:
        """搜索记忆"""
        memories = await self.get_memories(user_id, limit=50)
        
        # 简单的关键词匹配
        query_lower = query.lower()
        matched = []
        
        for memory in memories:
            content_lower = memory.content.lower()
            if query_lower in content_lower:
                matched.append(memory)
            elif memory.key and query_lower in memory.key.lower():
                matched.append(memory)
        
        return matched[:limit]
    
    async def delete_memory(self, user_id: str, memory_id: str):
        """删除记忆"""
        if not self.redis_client:
            return
        
        key = f"memory:{user_id}:{memory_id}"
        await self.redis_client.delete(key)


class MemoryInjector:
    """记忆注入器 - 将相关记忆注入到对话上下文中"""
    
    def __init__(self, memory_manager: MemoryManager):
        self.memory_manager = memory_manager
    
    async def build_context(
        self,
        user_id: str,
        query: str
    ) -> Dict[str, Any]:
        """
        构建包含相关记忆的上下文
        
        Args:
            user_id: 用户 ID
            query: 当前查询
        
        Returns:
            包含相关记忆的上下文
        """
        # 搜索相关记忆
        relevant_memories = await self.memory_manager.search_memories(user_id, query)
        
        # 分类记忆
        facts = [m for m in relevant_memories if m.memory_type == MemoryType.FACT]
        preferences = [m for m in relevant_memories if m.memory_type == MemoryType.PREFERENCE]
        
        # 格式化记忆
        facts_text = "\n".join([
            f"- {m.key}: {m.value}" if m.key else f"- {m.content}"
            for m in facts[:5]
        ])
        
        preferences_text = "\n".join([
            f"- {m.key}: {m.value}" if m.key else f"- {m.content}"
            for m in preferences[:5]
        ])
        
        return {
            "facts": facts_text if facts else "无",
            "preferences": preferences_text if preferences else "无",
            "memories": relevant_memories
        }


class ProfileManager:
    """用户画像管理器 - 管理用户特征和行为模式"""
    
    def __init__(self, redis_client=None):
        self.redis_client = redis_client
    
    async def get_profile(self, user_id: str) -> UserProfile:
        """获取用户画像"""
        if not self.redis_client:
            return UserProfile(user_id=user_id)
        
        key = f"profile:{user_id}"
        data = await self.redis_client.hgetall(key)
        
        if data and b'data' in data:
            profile_dict = json.loads(data[b'data'].decode('utf-8'))
            return UserProfile.from_dict(profile_dict)
        
        return UserProfile(user_id=user_id)
    
    async def save_profile(self, profile: UserProfile):
        """保存用户画像"""
        if not self.redis_client:
            return
        
        key = f"profile:{profile.user_id}"
        data = profile.to_dict()
        await self.redis_client.hset(key, mapping={
            "data": json.dumps(data, ensure_ascii=False),
            "updated_at": datetime.now().isoformat()
        })
        await self.redis_client.expire(key, 3600 * 24 * 90)  # 90天过期
    
    async def update_skill_usage(
        self,
        user_id: str,
        skill_name: str
    ):
        """更新技能使用统计"""
        profile = await self.get_profile(user_id)
        
        if skill_name not in profile.skill_usage:
            profile.skill_usage[skill_name] = 0
        profile.skill_usage[skill_name] += 1
        
        profile.updated_at = datetime.now().isoformat()
        await self.save_profile(profile)
    
    async def increment_dialogues(self, user_id: str):
        """增加对话计数"""
        profile = await self.get_profile(user_id)
        profile.total_dialogues += 1
        profile.updated_at = datetime.now().isoformat()
        await self.save_profile(profile)
    
    async def increment_messages(self, user_id: str):
        """增加消息计数"""
        profile = await self.get_profile(user_id)
        profile.total_messages += 1
        profile.updated_at = datetime.now().isoformat()
        await self.save_profile(profile)
