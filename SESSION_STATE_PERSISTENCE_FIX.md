# Session State 持久化修复总结

## 问题描述
前端与后端接口通过chat交互时，`session_state`为空，导致无法进入`_continue_flow`逻辑，多轮对话功能无法正常工作。

## 根本原因分析

### 1. **内存状态的生命周期问题**
后端的`_session_states`是一个内存字典：
```python
self._session_states: Dict[str, Dict[str, Any]] = {}
```

**问题**：
- 存储在AgentRuntime实例的内存中
- 后端服务重启时，所有session_state都会丢失
- 前端切换会话后，新会话的session_state在内存中不存在
- 导致每次都重新进入`_step1_skill_matching`而不是`_continue_flow`

### 2. **状态不持久化**
- SessionManager使用Redis持久化会话数据
- 但`_session_states`只保存在内存中
- 两者之间没有同步机制

## 解决方案

### 实现session_state的Redis持久化

#### 1. 添加Redis客户端引用
```python
class AgentRuntime:
    def __init__(self, redis_client: Any | None = None):
        # ... 其他初始化
        self.redis_client = redis_client  # 添加Redis客户端
```

#### 2. 实现`_get_session_state`方法
```python
async def _get_session_state(self, state_key: str) -> Dict[str, Any] | None:
    """从Redis或内存获取会话状态"""
    # 先从Redis获取
    if self.redis_client:
        try:
            state_data = await self.redis_client.get(f"session_state:{state_key}")
            if state_data:
                logger.info(f"[DEBUG] 从Redis获取到session_state: {state_key}")
                return json.loads(state_data)
        except Exception as e:
            logger.error(f"从Redis获取会话状态失败: {e}")

    # 降级到内存获取
    return self._session_states.get(state_key)
```

#### 3. 实现`_set_session_state`方法
```python
async def _set_session_state(self, state_key: str, state: Dict[str, Any]):
    """将会话状态保存到Redis和内存"""
    # 保存到Redis
    if self.redis_client:
        try:
            await self.redis_client.setex(
                f"session_state:{state_key}",
                3600,  # 1小时过期
                json.dumps(state)
            )
            logger.info(f"[DEBUG] session_state已保存到Redis: {state_key}")
        except Exception as e:
            logger.error(f"保存会话状态到Redis失败: {e}")

    # 同时保存到内存（降级）
    self._session_states[state_key] = state
    logger.info(f"[DEBUG] session_state已保存到内存: {state_key}")
```

#### 4. 实现`_clear_session_state`方法
```python
async def _clear_session_state(self, state_key: str):
    """清除会话状态"""
    # 从Redis删除
    if self.redis_client:
        try:
            await self.redis_client.delete(f"session_state:{state_key}")
        except Exception as e:
            logger.error(f"从Redis删除会话状态失败: {e}")

    # 从内存删除
    if state_key in self._session_states:
        del self._session_states[state_key]
```

#### 5. 更新所有设置session_state的地方
将所有的：
```python
self._session_states[state_key] = session_state
```
改为：
```python
await self._set_session_state(state_key, session_state)
```

共修改了4处：
- `_step1_skill_matching` (line ~313)
- `_step2_parameter_collection` 选择技能后 (line ~416)
- `_step2_parameter_collection` 收集参数时 (line ~461, ~475)
- `_step2_parameter_collection` 完成参数收集 (line ~491)

#### 6. 更新获取session_state的地方
将：
```python
session_state = self._session_states.get(state_key)
```
改为：
```python
session_state = await self._get_session_state(state_key)
```

### 前端优化

#### 确保session_id正确传递
```typescript
// frontend/pages/chat.vue
const sendMessage = async () => {
  if (!currentSessionId.value) {
    await createNewSession()
    // 等待确保session_id已设置
    await new Promise(resolve => setTimeout(resolve, 100))
  }

  // 确保有session_id
  if (!currentSessionId.value) {
    console.error('无法获取session_id')
    return
  }

  // 调用API时传递有效的session_id
  const response = await api.chat({
    user_input: userMessage,
    user_id: userId.value,
    session_id: currentSessionId.value  // 直接传递，不使用|| undefined
  })
}
```

## 技术细节

### Redis数据结构
- **Key**: `session_state:{user_id}:{session_id}`
- **Value**: JSON字符串
- **TTL**: 3600秒（1小时自动过期）

### 降级策略
1. 优先从Redis读取session_state
2. Redis失败时降级到内存存储
3. 同时写入Redis和内存（双写）

### 日志增强
```python
# 后端日志
logger.info(f"[DEBUG] 检查会话状态: state_key={state_key}, session_id={session_id}")
logger.info(f"[DEBUG] 从Redis获取到session_state: {state_key}")
logger.info(f"[DEBUG] session_state已保存到Redis: {state_key}")
```

## 测试步骤

### 1. 重启后端服务
```bash
cd /Users/mangguo/CodeBuddy/20260314024028/backend
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. 测试多轮对话流程
1. 前端发送第一条消息
2. 查看后端日志，确认session_state被保存到Redis
3. 用户回复选择技能
4. 查看后端日志，确认session_state能从Redis获取
5. 确认进入了`_continue_flow`而不是`_step1_skill_matching`

### 3. 验证持久化
1. 发送消息到某个会话，进入参数收集阶段
2. 重启后端服务
3. 继续在该会话中发送消息
4. 确认能继续参数收集流程（session_state从Redis恢复）

## 预期效果

### 修复前
1. 用户发送消息 → `_step1_skill_matching` → 返回技能列表
2. 用户选择技能 → session_state为空 → 重新回到步骤1
3. **问题**：无法进入参数收集流程

### 修复后
1. 用户发送消息 → `_step1_skill_matching` → 保存session_state到Redis → 返回技能列表
2. 用户选择技能 → 从Redis获取session_state → `_continue_flow` → `_step2_parameter_collection`
3. **效果**：正常进入参数收集流程

## 文件修改清单

1. **backend/core/agent_runtime.py**
   - 添加`_get_session_state`方法
   - 添加`_set_session_state`方法
   - 添加`_clear_session_state`方法
   - 更新`chat`方法中的session_state获取
   - 更新4处session_state设置

2. **frontend/pages/chat.vue**
   - 优化sendMessage函数确保session_id正确传递
   - 添加100ms延迟确保Vue响应式更新完成

3. **backend/api/main.py**
   - 增强chat接口的日志记录

## 注意事项

1. **TTL设置**：session_state在Redis中1小时自动过期，可以根据实际需求调整
2. **内存降级**：如果Redis不可用，自动降级到内存存储
3. **日志监控**：通过日志可以追踪session_state的读写情况
4. **性能考虑**：每次读取session_state都会先访问Redis，如果性能有问题可以考虑增加本地缓存

## 未来优化方向

1. **会话完成时清理**：在会话完成时主动清除session_state
2. **TTL动态调整**：根据会话活跃度动态调整过期时间
3. **状态压缩**：如果session_state较大，可以考虑压缩存储
4. **批量操作**：如果需要批量清理过期的session_state
