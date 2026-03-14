# 消息加载问题修复说明

## 问题描述

用户反馈：前端 chat 页面切换到历史 session 时，之前 session 的 chat 内容并没有显示出来。

## 问题分析

### 根本原因

后端的 `AgentRuntime` 类中缺少 `message_manager` 实例，导致在处理聊天消息时没有将用户和助手的对话保存到 Redis 中。虽然前端正确调用了 `getSessionMessages` 接口，但后端返回的消息列表为空。

### 具体表现

1. 用户在会话中发送消息
2. 后端处理消息并返回响应
3. 但消息没有被保存到 Redis
4. 切换会话时，`/sessions/{session_id}/messages` 接口返回空数组
5. 前端显示默认欢迎消息，而非历史对话内容

## 解决方案

### 1. 添加 MessageManager 到 AgentRuntime

在 `backend/core/agent_runtime.py` 中：

```python
# 导入 MessageManager
from backend.core.session_manager import MessageManager

class AgentRuntime:
    def __init__(self, ...):
        # ... 其他初始化代码 ...

        # 初始化消息管理器
        self.message_manager = MessageManager(redis_client)
```

### 2. 添加消息保存辅助方法

```python
async def _save_messages(
    self,
    user_input: str,
    response: str,
    user_id: str,
    conversation_id: str = None,
    session_id: str = None
):
    """保存用户和助手的消息"""
    if not session_id:
        return

    try:
        # 保存用户消息
        await self.message_manager.add_message(
            session_id=session_id,
            role="user",
            content=user_input,
            conversation_id=conversation_id
        )

        # 保存助手消息
        await self.message_manager.add_message(
            session_id=session_id,
            role="assistant",
            content=response,
            conversation_id=conversation_id
        )
    except Exception as e:
        logger.error(f"保存消息失败: {e}")
```

### 3. 在 chat 方法中统一保存消息

修改 `chat` 方法，在返回结果前统一保存消息：

```python
async def chat(
    self,
    user_input: str,
    user_id: str,
    conversation_id: str = None,
    session_id: str = None
) -> Dict[str, Any]:
    # ... 注入记忆和更新用户画像 ...

    # 检查会话状态
    state_key = f"{user_id}:{session_id or 'default'}"
    session_state = self._session_states.get(state_key)

    # 根据会话状态调用相应的方法
    if session_state:
        result = await self._continue_flow(user_input, user_id, conversation_id, session_id, session_state)
    else:
        result = await self._step1_skill_matching(user_input, user_id, conversation_id, session_id, memory_context)

    # 统一保存消息（无论哪个步骤返回，都会保存消息）
    if result and "response" in result:
        await self._save_messages(user_input, result["response"], user_id, conversation_id, session_id)

    return result
```

### 4. 修复 SessionManager 的 get_session 方法

在 `backend/core/session_manager.py` 中，修复 `get_session` 方法：

```python
async def get_session(self, session_id: str) -> Optional[Session]:
    """获取会话"""
    if self.redis_client:
        # 先尝试从 Redis 获取
        pattern = f"session:*:{session_id}"
        keys = await self.redis_client.keys(pattern)
        if keys:
            data = await self.redis_client.hgetall(keys[0])
            if data and b'data' in data:
                session_dict = json.loads(data[b'data'].decode('utf-8'))
                return Session.from_dict(session_dict)
    return None
```

## 测试验证

### 1. 后端接口测试

```bash
# 发送消息到会话
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "你好",
    "user_id": "test_user",
    "session_id": "8c0bdb5e-0ad0-4fab-91e9-c9679b3bae5b"
  }'

# 检查会话消息
curl http://localhost:8000/sessions/8c0bdb5e-0ad0-4fab-91e9-c9679b3bae5b/messages
```

**测试结果：**
- ✅ 消息正确保存到 Redis
- ✅ 获取会话消息接口返回正确的历史消息
- ✅ 消息包含 role（user/assistant）和 content

### 2. 前端功能测试

访问 http://localhost:3000/chat

**测试结果：**
- ✅ 会话列表正常显示
- ✅ 点击切换会话后，历史消息正确加载
- ✅ 消息按时间顺序正确显示
- ✅ 用户消息和助手消息样式正确

## 相关文件修改

### 后端文件

1. **backend/core/agent_runtime.py**
   - 导入 `MessageManager`
   - 在 `__init__` 中初始化 `message_manager`
   - 添加 `_save_messages` 辅助方法
   - 修改 `chat` 方法，统一保存消息

2. **backend/core/session_manager.py**
   - 修复 `get_session` 方法的 Redis 加载逻辑

### 前端文件

前端代码无需修改，已有的代码逻辑正确：

- `frontend/pages/chat.vue`: `switchSession` 方法正确调用 `getSessionMessages` API
- `frontend/composables/api.ts`: `getSessionMessages` 方法正确实现

## 数据流说明

### 消息保存流程

```
用户发送消息
    ↓
前端调用 /chat API
    ↓
AgentRuntime.chat() 处理
    ↓
执行相应的步骤（_step1_skill_matching 等）
    ↓
返回结果
    ↓
AgentRuntime._save_messages() 保存消息到 Redis
    ↓
Redis 存储消息（key: message:{session_id}:{message_id}）
```

### 消息加载流程

```
用户点击会话列表
    ↓
前端调用 switchSession(session)
    ↓
前端调用 /sessions/{session_id}/messages API
    ↓
SessionManager.get_session_messages()
    ↓
从 Redis 查询消息（pattern: message:{session_id}:*）
    ↓
返回消息列表给前端
    ↓
前端更新 messages.value 并渲染
```

## 技术细节

### Redis 存储结构

#### 会话存储
```
Key: session:{user_id}:{session_id}
Type: Hash
Fields:
  - data: JSON 格式的会话数据
  - updated_at: 更新时间戳
```

#### 消息存储
```
Key: message:{session_id}:{message_id}
Type: Hash
Fields:
  - data: JSON 格式的消息数据
```

### 消息数据结构

```json
{
  "message_id": "fd570c01-05b5-42e3-8e42-d40b7d623844",
  "session_id": "8c0bdb5e-0ad0-4fab-91e9-c9679b3bae5b",
  "conversation_id": null,
  "role": "user",
  "content": "你好",
  "created_at": "2026-03-15T02:05:56.871059",
  "skill_name": null,
  "skill_result": null,
  "rating": null,
  "feedback": null
}
```

## 注意事项

1. **session_id 必须提供**: 消息只有在提供了 `session_id` 时才会被保存
2. **消息保存是异步的**: 使用 `await` 保存消息，不影响响应速度
3. **错误处理**: 保存消息失败不会影响主要流程，只会记录错误日志
4. **消息过期时间**: 消息在 Redis 中默认保存 7 天

## 后续优化建议

1. **批量保存消息**: 如果需要保存大量消息，可以考虑使用 Redis pipeline
2. **消息加密**: 对于敏感信息，可以考虑对消息内容进行加密
3. **消息压缩**: 对于长消息，可以考虑压缩存储
4. **消息索引**: 如果需要按消息内容搜索，可以考虑添加索引

## 总结

通过添加 `MessageManager` 到 `AgentRuntime`，并在 `chat` 方法中统一保存消息，成功解决了切换历史会话时消息不显示的问题。现在用户可以：

- ✅ 在多个会话之间自由切换
- ✅ 查看每个会话的完整历史对话
- ✅ 继续之前未完成的对话
- ✅ 享受流畅的多会话管理体验
