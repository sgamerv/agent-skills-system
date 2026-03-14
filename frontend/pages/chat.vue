<script setup lang="ts">
useHead({
  title: '智能对话 - Agent Skills System'
})

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
const sendMessage = () => {
  if (!inputMessage.value.trim()) return

  // 添加用户消息
  messages.value.push({
    role: 'user',
    content: inputMessage.value
  })

  // 模拟 AI 回复
  setTimeout(() => {
    messages.value.push({
      role: 'assistant',
      content: '收到您的消息：' + inputMessage.value
    })
  }, 1000)

  inputMessage.value = ''
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
      </div>

      <!-- 输入框 -->
      <div class="input-area">
        <UInput
          v-model="inputMessage"
          placeholder="输入您的问题..."
          size="lg"
          @keyup.enter="sendMessage"
        />
        <UButton size="lg" icon="i-heroicons-paper-airplane" @click="sendMessage">
          发送
        </UButton>
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

.input-area {
  padding: 1.5rem;
  border-top: 1px solid rgb(var(--color-gray-200));
  display: flex;
  gap: 1rem;
}
</style>
