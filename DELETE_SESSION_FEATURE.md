# 删除会话功能实现说明

## 功能概述

为 chat 页面添加删除 session 的功能，允许用户删除不需要的会话及其所有历史消息。

## 实现的功能

### 1. 后端功能

#### SessionManager 添加删除方法

在 `backend/core/session_manager.py` 中添加 `delete_session` 方法：

```python
async def delete_session(self, session_id: str):
    """
    删除会话及其所有消息

    Args:
        session_id: 会话 ID
    """
    if not self.redis_client:
        return False

    try:
        # 删除会话数据
        pattern = f"session:*:{session_id}"
        keys = await self.redis_client.keys(pattern)
        if keys:
            await self.redis_client.delete(*keys)

        # 删除会话的所有消息
        message_pattern = f"message:{session_id}:*"
        message_keys = await self.redis_client.keys(message_pattern)
        if message_keys:
            await self.redis_client.delete(*message_keys)

        return True
    except Exception as e:
        logger.error(f"删除会话失败: {e}")
        return False
```

**功能说明：**
- 删除 Redis 中的会话数据
- 删除该会话的所有消息
- 使用 pattern matching 批量删除相关键
- 包含错误处理和日志记录

#### API 接口

在 `backend/api/main.py` 中添加删除会话接口：

```python
@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """
    删除会话及其所有消息
    """
    session_manager: SessionManager = app.state.session_manager

    success = await session_manager.delete_session(session_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete session")

    return {"message": "Session deleted successfully"}
```

**接口说明：**
- 路径: `DELETE /sessions/{session_id}`
- 参数: `session_id` (路径参数)
- 响应: `{ "message": "Session deleted successfully" }`
- 错误: 失败时返回 500 状态码

### 2. 前端功能

#### API 客户端

在 `frontend/composables/api.ts` 中添加删除会话方法：

```typescript
// 删除会话
deleteSession: (sessionId: string) => request<{ message: string }>(`/sessions/${sessionId}`, {
  method: 'DELETE',
})
```

#### 聊天页面

在 `frontend/pages/chat.vue` 中添加删除会话功能：

##### 1. 添加删除会话方法

```typescript
// 删除会话
const deleteSession = async (session: any, event: Event) => {
  // 阻止事件冒泡，避免触发切换会话
  event.stopPropagation()

  if (!confirm(`确定要删除会话"${session.title || '当前会话'}"吗？此操作不可恢复。`)) {
    return
  }

  try {
    await api.deleteSession(session.session_id)

    // 如果删除的是当前会话，重置消息和会话ID
    if (currentSessionId.value === session.session_id) {
      currentSessionId.value = null
      messages.value = [
        {
          role: 'assistant',
          content: '您好！我是智能助手，有什么可以帮助您的吗？'
        }
      ]
    }

    // 从会话列表中移除
    sessions.value = sessions.value.filter(s => s.session_id !== session.session_id)
  } catch (err: any) {
    console.error('删除会话失败:', err)
    error.value = '删除会话失败'
  }
}
```

**功能说明：**
- 使用 `confirm` 确认删除操作
- 阻止事件冒泡，避免触发会话切换
- 如果删除的是当前会话，重置消息显示和会话ID
- 从本地会话列表中移除已删除的会话
- 包含错误处理和错误提示

##### 2. 添加删除按钮到会话列表

```vue
<div
  v-for="session in sessions"
  :key="session.session_id"
  :class="['session-item', { active: session.session_id === currentSessionId }]"
  @click="switchSession(session)"
>
  <div class="session-info">
    <UIcon name="i-heroicons-chat-bubble-left" class="session-icon" />
    <div class="session-title">
      {{ session.title || '当前会话' }}
    </div>
  </div>
  <div class="session-actions">
    <UButton
      icon="i-heroicons-trash"
      size="xs"
      variant="ghost"
      color="red"
      @click="deleteSession(session, $event)"
    />
  </div>
  <div class="session-time">
    {{ formatTime(session.updated_at) }}
  </div>
</div>
```

##### 3. 添加删除按钮样式

```css
.session-actions {
  display: flex;
  align-items: center;
  opacity: 0;
  transition: opacity 0.2s;
}

.session-item:hover .session-actions {
  opacity: 1;
}
```

**样式说明：**
- 删除按钮默认隐藏（opacity: 0）
- 鼠标悬停在会话项上时显示删除按钮
- 使用过渡动画，提升用户体验

## 用户操作流程

### 删除会话流程

1. 用户将鼠标悬停在会话列表项上
2. 删除按钮（红色垃圾桶图标）出现
3. 用户点击删除按钮
4. 弹出确认对话框："确定要删除会话"xxx"吗？此操作不可恢复。"
5. 用户点击"确定"
6. 系统调用后端删除接口
7. 从本地会话列表中移除该会话
8. 如果删除的是当前会话，重置消息显示

### 删除当前会话的特殊处理

如果删除的是当前正在查看的会话：
- 重置 `currentSessionId` 为 `null`
- 清空消息列表，显示默认欢迎消息
- 用户需要重新创建会话或切换到其他会话

## 界面展示

### 会话列表项结构

```
┌─────────────────────────────────────┐
│ 💬 会话标题          [🗑️] 2小时前 │
└─────────────────────────────────────┘
     ↑          ↑        ↑      ↑
   图标      标题    删除按钮 时间
```

### 悬停状态

```
┌─────────────────────────────────────┐
│ 💬 会话标题          [🗑️] 2小时前 │ ← 鼠标悬停
└─────────────────────────────────────┘
     ↑                    ↑
   图标              删除按钮可见
```

## 技术细节

### 后端

#### Redis 数据删除

```python
# 删除会话数据
pattern = f"session:*:{session_id}"
keys = await self.redis_client.keys(pattern)
if keys:
    await self.redis_client.delete(*keys)

# 删除会话的所有消息
message_pattern = f"message:{session_id}:*"
message_keys = await self.redis_client.keys(message_pattern)
if message_keys:
    await self.redis_client.delete(*message_keys)
```

**删除的键：**
- `session:{user_id}:{session_id}` - 会话数据
- `message:{session_id}:{message_id}` - 所有消息（可能有多个）

#### 错误处理

- 删除失败时记录日志
- 返回 `False` 表示失败
- API 接口捕获失败并返回 500 错误

### 前端

#### 事件处理

```typescript
// 阻止事件冒泡，避免触发切换会话
event.stopPropagation()
```

**原因：**
- 删除按钮在会话列表项内部
- 点击删除按钮会冒泡到父元素（会话列表项）
- 需要阻止冒泡，避免触发会话切换

#### 状态管理

```typescript
// 如果删除的是当前会话，重置状态
if (currentSessionId.value === session.session_id) {
  currentSessionId.value = null
  messages.value = [
    {
      role: 'assistant',
      content: '您好！我是智能助手，有什么可以帮助您的吗？'
    }
  ]
}
```

## 测试结果

### 后端测试

```bash
# 创建测试会话
curl -X POST http://localhost:8000/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "title": "测试删除会话"
  }'

# 响应: {"session_id": "...", ...}

# 删除会话
curl -X DELETE http://localhost:8000/sessions/{session_id}

# 响应: {"message": "Session deleted successfully"}

# 验证删除
curl http://localhost:8000/users/test_user/sessions

# 响应: {"sessions": [], "total": 0}
```

**测试结果：** ✅ 所有测试通过

### 前端测试

1. ✅ 删除按钮在悬停时正确显示
2. ✅ 点击删除按钮弹出确认对话框
3. ✅ 取消确认对话框不删除会话
4. ✅ 确认删除后，会话从列表中移除
5. ✅ 删除当前会话后，消息正确重置
6. ✅ 删除其他会话不影响当前会话
7. ✅ 删除按钮不触发会话切换

## 用户体验优化

### 1. 悬停显示
- 删除按钮默认隐藏，减少视觉干扰
- 悬停时显示，提供直观的操作入口

### 2. 确认对话框
- 防止误操作
- 明确告知删除的会话名称
- 提示操作不可恢复

### 3. 平滑动画
- 按钮淡入淡出动画
- 提升用户体验

### 4. 状态管理
- 删除当前会话时正确重置状态
- 避免显示错误的数据

## 安全考虑

### 1. 确认机制
- 使用浏览器原生 `confirm` 对话框
- 二次确认，防止误删除

### 2. 事件隔离
- 使用 `stopPropagation` 阻止事件冒泡
- 确保删除操作不会触发其他事件

### 3. 错误处理
- 前端捕获删除失败
- 显示错误提示
- 不会导致页面崩溃

## 未来优化

### 短期优化
- [ ] 添加批量删除功能
- [ ] 添加回收站功能（软删除）
- [ ] 添加删除动画

### 长期优化
- [ ] 支持删除确认的自定义提示
- [ ] 添加删除历史记录
- [ ] 支持按时间范围批量删除

## 相关文件

### 后端
- `backend/core/session_manager.py` - 添加 `delete_session` 方法
- `backend/api/main.py` - 添加 `DELETE /sessions/{session_id}` 接口

### 前端
- `frontend/composables/api.ts` - 添加 `deleteSession` 方法
- `frontend/pages/chat.vue` - 添加删除按钮和删除逻辑

## 总结

成功实现了删除会话功能，包括：

✅ 后端 API 接口支持删除会话及其所有消息
✅ 前端界面支持悬停显示删除按钮
✅ 删除确认机制，防止误操作
✅ 正确处理删除当前会话的特殊情况
✅ 优雅的 UI 交互和动画效果
✅ 完善的错误处理和用户提示

用户现在可以：
- 方便地删除不需要的会话
- 安全地管理会话历史
- 享受流畅的用户体验
