<script setup lang="ts">
useHead({
  title: '智能对话 - Agent Skills System'
})

// 加载状态
const loading = ref(false)
const error = ref<string | null>(null)

// 消息列表
const messages = ref([
  {
    role: 'assistant',
    content: '您好！我是智能助手，有什么可以帮助您的吗？'
  }
])

// 输入框内容
const inputMessage = ref('')

// 发送消息
const sendMessage = async () => {
  if (!inputMessage.value.trim()) return

  const userMessage = inputMessage.value.trim()

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
      user_id: 'default_user'
    })

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
  }
}
</script>

<template>
  <div class="chat">
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
</template>

<style scoped>
.chat {
  min-height: 100vh;
  padding: 2rem;
  background: rgb(var(--color-gray-50));
}

.chat-container {
  max-width: 800px;
  margin: 0 auto;
  height: calc(100vh - 4rem);
  display: flex;
  flex-direction: column;
}

.messages {
  flex: 1;
  overflow-y: auto;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.message {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  max-width: 70%;
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
}

.message-content {
  padding: 1rem 1.5rem;
  border-radius: 1rem;
  line-height: 1.6;
  font-weight: 400;
}

.message.user .message-content {
  background: rgb(var(--color-primary-500));
  color: white;
  border-bottom-right-radius: 0.25rem;
  font-weight: 500;
}

.message.assistant .message-content {
  background: rgb(var(--color-gray-100));
  color: rgb(var(--color-gray-900));
  border-bottom-left-radius: 0.25rem;
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
}

.error-banner {
  padding: 1rem 1.5rem;
  background: rgb(var(--color-red-50));
  border-top: 1px solid rgb(var(--color-red-200));
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: rgb(var(--color-red-600));
  font-size: 0.875rem;
}
</style>
