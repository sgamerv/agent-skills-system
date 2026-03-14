<template>
  <div class="chat">
    <div class="chat-container">
      <header class="chat-header">
        <button class="back-btn" @click="goBack">←</button>
        <h1>知识问答</h1>
      </header>

      <div class="chat-messages" ref="messagesContainer">
        <div
          v-for="(message, index) in messages"
          :key="index"
          :class="['message', message.role]"
        >
          <div class="message-content">{{ message.content }}</div>
          <div class="message-time">{{ formatTime(message.timestamp) }}</div>
        </div>

        <div v-if="loading" class="message assistant loading">
          <div class="message-content">
            <span class="dots">...</span>
          </div>
        </div>
      </div>

      <div class="chat-input">
        <textarea
          v-model="input"
          placeholder="输入您的问题..."
          @keydown.enter.prevent="sendMessage"
          rows="1"
          ref="inputRef"
        />
        <button
          class="send-btn"
          @click="sendMessage"
          :disabled="loading || !input.trim()"
        >
          发送
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const input = ref('')
const messages = ref([])
const loading = ref(false)
const messagesContainer = ref(null)
const inputRef = ref(null)

const userId = 'demo-user-' + Date.now()

const goBack = () => {
  router.push('/')
}

const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

const formatTime = (timestamp) => {
  const date = new Date(timestamp)
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

const sendMessage = async () => {
  if (!input.value.trim() || loading.value) return

  const userMessage = {
    role: 'user',
    content: input.value.trim(),
    timestamp: Date.now()
  }

  messages.value.push(userMessage)
  input.value = ''
  loading.value = true

  await scrollToBottom()

  try {
    // TODO: 实际调用后端 API
    // const response = await fetch('/api/chat', {
    //   method: 'POST',
    //   headers: { 'Content-Type': 'application/json' },
    //   body: JSON.stringify({
    //     user_input: userMessage.content,
    //     user_id: userId
    //   })
    // })
    // const data = await response.json()

    // 模拟响应
    await new Promise(resolve => setTimeout(resolve, 1500))

    const assistantMessage = {
      role: 'assistant',
      content: '这是一个演示响应。实际应用中，这里将连接到后端 API 来获取 AI 生成的回复。',
      timestamp: Date.now()
    }

    messages.value.push(assistantMessage)
  } catch (error) {
    const errorMessage = {
      role: 'assistant',
      content: '抱歉，发生错误：' + error.message,
      timestamp: Date.now()
    }
    messages.value.push(errorMessage)
  } finally {
    loading.value = false
    await scrollToBottom()
    inputRef.value?.focus()
  }
}
</script>

<style scoped>
.chat {
  height: 100vh;
  background: #f5f5f5;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 1rem;
}

.chat-container {
  width: 100%;
  max-width: 800px;
  height: calc(100vh - 2rem);
  background: white;
  border-radius: 1rem;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.chat-header {
  padding: 1rem;
  border-bottom: 1px solid #eee;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.back-btn {
  font-size: 1.5rem;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.5rem;
}

.chat-header h1 {
  font-size: 1.25rem;
  margin: 0;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.message {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.message.user {
  align-items: flex-end;
}

.message.assistant {
  align-items: flex-start;
}

.message-content {
  max-width: 80%;
  padding: 0.75rem 1rem;
  border-radius: 1rem;
  line-height: 1.6;
}

.message.user .message-content {
  background: #667eea;
  color: white;
  border-bottom-right-radius: 0.25rem;
}

.message.assistant .message-content {
  background: #f0f0f0;
  color: #333;
  border-bottom-left-radius: 0.25rem;
}

.message.loading .message-content {
  color: #999;
}

.message-time {
  font-size: 0.75rem;
  color: #999;
}

.dots {
  display: inline-block;
}

.dots::after {
  content: '...';
  animation: dots 1.5s infinite;
}

@keyframes dots {
  0%, 20% { content: '.'; }
  40% { content: '..'; }
  60%, 100% { content: '...'; }
}

.chat-input {
  padding: 1rem;
  border-top: 1px solid #eee;
  display: flex;
  gap: 0.5rem;
}

.chat-input textarea {
  flex: 1;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 0.5rem;
  resize: none;
  font-family: inherit;
  font-size: 1rem;
}

.chat-input textarea:focus {
  outline: none;
  border-color: #667eea;
}

.send-btn {
  padding: 0.75rem 1.5rem;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.send-btn:hover:not(:disabled) {
  background: #5568d3;
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
