<script setup lang="ts">
useHead({
  title: '智能对话 - Agent Skills System'
})

// 用户ID
const userId = ref('default_user')

// 加载状态
const loading = ref(false)
const error = ref<string | null>(null)
const sessionsLoading = ref(false)

// 会话相关
const sessions = ref<any[]>([])
const currentSessionId = ref<string | null>(null)

// 消息列表
const messages = ref([
  {
    role: 'assistant',
    content: '您好！我是智能助手，有什么可以帮助您的吗？'
  }
])

// 输入框内容
const inputMessage = ref('')

// 创建新会话
const createNewSession = async () => {
  try {
    const newSession = await api.createSession(userId.value, '当前会话')
    sessions.value.unshift(newSession)
    currentSessionId.value = newSession.session_id
    messages.value = [
      {
        role: 'assistant',
        content: '您好！我是智能助手，有什么可以帮助您的吗？'
      }
    ]
  } catch (err: any) {
    console.error('创建会话失败:', err)
    error.value = '创建会话失败'
  }
}

// 切换会话
const switchSession = async (session: any) => {
  if (currentSessionId.value === session.session_id) return

  currentSessionId.value = session.session_id
  messages.value = []
  loading.value = true

  try {
    const response = await api.getSessionMessages(session.session_id)
    if (response.messages && response.messages.length > 0) {
      messages.value = response.messages.map((msg: any) => ({
        role: msg.role,
        content: msg.content
      }))
    } else {
      messages.value = [
        {
          role: 'assistant',
          content: '您好！我是智能助手，有什么可以帮助您的吗？'
        }
      ]
    }
  } catch (err: any) {
    console.error('加载会话消息失败:', err)
    error.value = '加载会话消息失败'
    messages.value = [
      {
        role: 'assistant',
        content: '您好！我是智能助手，有什么可以帮助您的吗？'
      }
    ]
  } finally {
    loading.value = false
  }
}

// 加载会话列表
const loadSessions = async () => {
  sessionsLoading.value = true
  try {
    const response = await api.getUserSessions(userId.value)
    sessions.value = response.sessions || []
  } catch (err: any) {
    console.error('加载会话列表失败:', err)
  } finally {
    sessionsLoading.value = false
  }
}

// 更新会话标题
const updateSessionTitle = async (sessionId: string, title: string) => {
  try {
    await api.updateSession(sessionId, title)
    const session = sessions.value.find(s => s.session_id === sessionId)
    if (session) {
      session.title = title
    }
  } catch (err: any) {
    console.error('更新会话标题失败:', err)
  }
}

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

// 发送消息
const sendMessage = async () => {
  if (!inputMessage.value.trim()) return

  const userMessage = inputMessage.value.trim()

  // 如果没有当前会话，先创建一个
  if (!currentSessionId.value) {
    await createNewSession()
  }

  // 更新会话标题（如果是第一条消息）
  const session = sessions.value.find(s => s.session_id === currentSessionId.value)
  if (session && session.title === '当前会话') {
    // 简单总结：取前20个字符
    const summary = userMessage.length > 20 ? userMessage.substring(0, 20) + '...' : userMessage
    await updateSessionTitle(session.session_id, summary)
  }

  // 添加用户消息
  messages.value.push({
    role: 'user',
    content: userMessage
  })

  // 清空输入框
  inputMessage.value = ''

  // 设置加载状态
  loading.value = true
  error.value = null

  try {
    // 调用后端 API
    const response = await api.chat({
      user_input: userMessage,
      user_id: userId.value,
      session_id: currentSessionId.value || undefined
    })

    // 更新会话ID（如果是第一次创建的会话）
    if (response.session_id && !currentSessionId.value) {
      currentSessionId.value = response.session_id
    }

    // 添加 AI 回复
    messages.value.push({
      role: 'assistant',
      content: response.response
    })
  } catch (err: any) {
    console.error('发送消息失败:', err)
    error.value = err.message || '发送消息失败'

    // 添加错误消息
    messages.value.push({
      role: 'assistant',
      content: `抱歉，发生错误：${err.message || '未知错误'}`
    })
  } finally {
    loading.value = false
    await loadSessions() // 刷新会话列表
  }
}

// 页面加载时获取会话列表
onMounted(() => {
  loadSessions()
})

// 格式化时间
const formatTime = (timeStr?: string) => {
  if (!timeStr) return ''
  const date = new Date(timeStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()

  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days < 7) return `${days}天前`

  return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
}
</script>

<template>
  <div class="chat">
    <div class="chat-layout">
      <!-- 左侧会话列表 -->
      <aside class="sidebar">
        <div class="sidebar-header">
          <h2>会话列表</h2>
          <UButton
            icon="i-heroicons-plus"
            size="sm"
            @click="createNewSession"
          >
            新建会话
          </UButton>
        </div>

        <div class="sessions-list">
          <div v-if="sessionsLoading" class="loading-sessions">
            <UIcon name="i-heroicons-arrow-path" class="loading-icon" />
            加载中...
          </div>

          <div
            v-for="session in sessions"
            :key="session.session_id"
            :class="['session-item', { active: session.session_id === currentSessionId }]"
            @click="switchSession(session)"
          >
            <div class="session-header">
              <div class="session-title-wrapper">
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
            </div>
            <div class="session-time">
              {{ formatTime(session.updated_at) }}
            </div>
          </div>

          <div v-if="!sessionsLoading && sessions.length === 0" class="empty-sessions">
            暂无会话
          </div>
        </div>
      </aside>

      <!-- 右侧聊天区域 -->
      <UCard class="chat-container">
        <!-- 消息列表 -->
        <div class="messages">
          <div
            v-for="(msg, index) in messages"
            :key="index"
            :class="['message', msg.role]"
          >
            <UAvatar
              v-if="msg.role === 'assistant'"
              icon="i-heroicons-sparkles"
              size="sm"
              class="message-avatar"
            />
            <UAvatar
              v-else
              icon="i-heroicons-user"
              size="sm"
              class="message-avatar"
            />
            <div class="message-content">
              {{ msg.content }}
            </div>
          </div>

          <!-- 加载状态 -->
          <div v-if="loading" class="message assistant">
            <UAvatar icon="i-heroicons-sparkles" size="sm" class="message-avatar" />
            <div class="message-content loading-content">
              <UIcon name="i-heroicons-arrow-path" class="loading-icon" />
              思考中...
            </div>
          </div>
        </div>

        <!-- 输入框 -->
        <div class="input-area">
          <UInput
            v-model="inputMessage"
            placeholder="输入您的问题..."
            size="lg"
            :disabled="loading"
            @keyup.enter="sendMessage"
          />
          <UButton
            size="lg"
            icon="i-heroicons-paper-airplane"
            :loading="loading"
            :disabled="loading || !inputMessage.trim()"
            @click="sendMessage"
          >
            发送
          </UButton>
        </div>

        <!-- 错误提示 -->
        <div v-if="error" class="error-banner">
          <UIcon name="i-heroicons-exclamation-triangle" />
          <span>{{ error }}</span>
          <UButton
            size="sm"
            icon="i-heroicons-x-mark"
            variant="ghost"
            @click="error = null"
          />
        </div>
      </UCard>
    </div>
  </div>
</template>

<style scoped>
.chat {
  min-height: 100vh;
  padding: 2rem;
  background: linear-gradient(135deg, rgb(var(--color-gray-50)) 0%, rgb(var(--color-gray-100)) 100%);
}

.chat-layout {
  display: flex;
  gap: 1.5rem;
  max-width: 1400px;
  margin: 0 auto;
  height: calc(100vh - 4rem);
}

/* 左侧边栏 */
.sidebar {
  width: 320px;
  background: white;
  border-radius: 1rem;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border: 1px solid rgb(var(--color-gray-200));
}

.sidebar-header {
  padding: 1.5rem;
  border-bottom: 1px solid rgb(var(--color-gray-200));
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(180deg, rgb(var(--color-gray-50)) 0%, white 100%);
}

.sidebar-header h2 {
  font-size: 1.125rem;
  font-weight: 700;
  color: rgb(var(--color-gray-900));
  letter-spacing: -0.025em;
}

.sessions-list {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.session-item {
  padding: 1rem;
  border-radius: 0.75rem;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid rgb(var(--color-gray-200));
  background: white;
}

.session-item:hover {
  background: rgb(var(--color-gray-50));
  border-color: rgb(var(--color-gray-300));
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.session-item.active {
  background: linear-gradient(135deg, rgb(var(--color-primary-50)) 0%, rgb(var(--color-primary-100)) 100%);
  border-color: rgb(var(--color-primary-300));
  box-shadow: 0 2px 8px rgba(var(--color-primary-200), 0.3);
}

.session-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.5rem;
}

.session-title-wrapper {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  flex: 1;
  min-width: 0;
}

.session-icon {
  color: rgb(var(--color-gray-400));
  font-size: 1.125rem;
  flex-shrink: 0;
}

.session-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: rgb(var(--color-gray-900));
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  letter-spacing: -0.01em;
}

.session-actions {
  display: flex;
  align-items: center;
  opacity: 0;
  transition: opacity 0.2s;
}

.session-item:hover .session-actions {
  opacity: 1;
}

.session-time {
  font-size: 0.75rem;
  color: rgb(var(--color-gray-400));
  margin-top: 0.5rem;
  padding-left: 1.75rem;
  font-weight: 500;
}

.loading-sessions {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 2rem;
  color: rgb(var(--color-gray-400));
  font-size: 0.875rem;
}

.empty-sessions {
  padding: 2rem;
  text-align: center;
  color: rgb(var(--color-gray-400));
  font-size: 0.875rem;
  font-weight: 500;
}

/* 右侧聊天区域 */
.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border-radius: 1rem;
  border: 1px solid rgb(var(--color-gray-200));
  background: white;
  overflow: hidden;
}

.messages {
  flex: 1;
  overflow-y: auto;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  background: linear-gradient(180deg, rgb(var(--color-gray-50)) 0%, white 100%);
}

.message {
  display: flex;
  align-items: flex-start;
  gap: 0.875rem;
  max-width: 75%;
  animation: messageSlideIn 0.3s ease;
}

@keyframes messageSlideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message.user {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.message.assistant {
  align-self: flex-start;
}

.message-avatar {
  flex-shrink: 0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.message-content {
  padding: 1.125rem 1.5rem;
  border-radius: 1.25rem;
  line-height: 1.6;
  font-weight: 400;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  word-wrap: break-word;
}

.message.user .message-content {
  background: linear-gradient(135deg, rgb(var(--color-primary-500)) 0%, rgb(var(--color-primary-600)) 100%);
  color: white;
  border-bottom-right-radius: 0.375rem;
  font-weight: 500;
  letter-spacing: 0.005em;
}

.message.assistant .message-content {
  background: white;
  color: rgb(var(--color-gray-900));
  border: 1px solid rgb(var(--color-gray-200));
  border-bottom-left-radius: 0.375rem;
  font-weight: 400;
}

.loading-content {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.loading-icon {
  font-size: 1rem;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.input-area {
  padding: 1.5rem;
  border-top: 1px solid rgb(var(--color-gray-200));
  display: flex;
  gap: 1rem;
  background: linear-gradient(180deg, rgb(var(--color-gray-50)) 0%, white 100%);
}

.error-banner {
  padding: 1rem 1.5rem;
  background: linear-gradient(135deg, rgb(var(--color-red-50)) 0%, rgb(var(--color-red-100)) 100%);
  border-top: 1px solid rgb(var(--color-red-200));
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: rgb(var(--color-red-600));
  font-size: 0.875rem;
  font-weight: 500;
}

/* 滚动条美化 */
.messages::-webkit-scrollbar,
.sessions-list::-webkit-scrollbar {
  width: 6px;
}

.messages::-webkit-scrollbar-track,
.sessions-list::-webkit-scrollbar-track {
  background: transparent;
}

.messages::-webkit-scrollbar-thumb,
.sessions-list::-webkit-scrollbar-thumb {
  background: rgb(var(--color-gray-300));
  border-radius: 3px;
}

.messages::-webkit-scrollbar-thumb:hover,
.sessions-list::-webkit-scrollbar-thumb:hover {
  background: rgb(var(--color-gray-400));
}

@media (max-width: 768px) {
  .chat {
    padding: 0.5rem;
  }

  .chat-layout {
    flex-direction: column;
    height: calc(100vh - 1rem);
    gap: 0.75rem;
  }

  .sidebar {
    width: 100%;
    height: 200px;
  }

  .message {
    max-width: 90%;
  }

  .messages {
    padding: 1rem;
    gap: 1rem;
  }

  .input-area {
    padding: 1rem;
  }
}
</style>
