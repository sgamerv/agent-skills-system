# 前端 API 集成指南

## 概述

本项目前端已集成后端 API，通过统一的 API 客户端 (`composables/api.ts`) 管理所有后端请求。

## 目录结构

```
frontend/
├── composables/
│   └── api.ts              # API 客户端
├── pages/
│   ├── chat.vue            # 聊天页面（使用 API）
│   └── skills.vue          # 技能列表（使用 API）
├── .env                    # 环境变量配置
└── .env.example            # 环境变量示例
```

## 快速开始

### 1. 配置环境变量

确保 `.env` 文件中配置了正确的后端 API 地址：

```bash
NUXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

### 2. 启动后端服务

确保后端服务已启动：

```bash
cd backend
python -m uvicorn api.main:app --reload
```

### 3. 启动前端服务

```bash
cd frontend
npm run dev
```

访问 http://localhost:3000 查看前端页面。

## API 客户端

### 位置

`composables/api.ts`

### 特性

- 统一的请求封装
- 自动错误处理
- TypeScript 类型支持
- 环境变量配置

### 使用示例

```typescript
import { api } from '~/composables/api'

// 获取技能列表
const skills = await api.getSkills()

// 发送聊天消息
const response = await api.chat({
  user_input: '你好',
  user_id: 'default_user'
})
```

## API 端点

### 健康检查

```typescript
api.healthCheck()
```

**返回：**
```typescript
{
  status: "healthy"
}
```

---

### 技能管理

#### 获取所有技能

```typescript
api.getSkills()
```

**返回：**
```typescript
{
  skills: [
    {
      name: string
      description: string
      category: string
      tags: string[]
      version: string
    }
  ],
  total: number
}
```

**使用示例：**
```vue
<script setup lang="ts">
const skills = ref([])

const fetchSkills = async () => {
  const response = await api.getSkills()
  skills.value = response.skills
}

onMounted(() => fetchSkills())
</script>
```

#### 获取技能详情

```typescript
api.getSkill(skillName: string)
```

**参数：**
- `skillName` - 技能名称

**返回：**
```typescript
{
  name: string
  description: string
  category: string
  tags: string[]
  version: string
  slots: any[]
  can_call: boolean
}
```

---

### 聊天

```typescript
api.chat(data: ChatRequest)
```

**参数：**
```typescript
{
  user_input: string      // 用户输入
  user_id: string         // 用户 ID
  conversation_id?: string  // 会话 ID（可选）
  session_id?: string     // 会话 ID（可选）
}
```

**返回：**
```typescript
{
  response: string
  conversation_id?: string
  session_id?: string
  mode: string
  state: string
  filled_slots?: Record<string, any>
  next_slot?: string
  ready_to_execute: boolean
  needs_confirmation: boolean
}
```

**使用示例：**
```vue
<script setup lang="ts">
const sendMessage = async () => {
  try {
    const response = await api.chat({
      user_input: inputMessage.value,
      user_id: 'default_user'
    })

    messages.value.push({
      role: 'assistant',
      content: response.response
    })
  } catch (error) {
    console.error('发送失败:', error)
  }
}
</script>
```

---

### 会话管理

#### 创建会话

```typescript
api.createSession(userId: string, title?: string)
```

**参数：**
- `userId` - 用户 ID
- `title` - 会话标题（可选）

**返回：**
```typescript
{
  session_id: string
  user_id: string
  status: string
  title?: string
  created_at?: string
  updated_at?: string
}
```

#### 获取会话详情

```typescript
api.getSession(sessionId: string)
```

**返回：** 同创建会话

#### 获取用户会话列表

```typescript
api.getUserSessions(userId: string)
```

**返回：**
```typescript
{
  sessions: Session[]
  total: number
}
```

#### 获取会话消息

```typescript
api.getSessionMessages(sessionId: string, limit?: number)
```

**参数：**
- `sessionId` - 会话 ID
- `limit` - 消息数量限制（默认 50）

**返回：**
```typescript
{
  messages: any[]
  total: number
}
```

---

### 用户数据

#### 获取用户画像

```typescript
api.getUserProfile(userId: string)
```

**返回：**
```typescript
{
  // 用户画像数据
}
```

#### 获取用户记忆

```typescript
api.getUserMemories(userId: string, memoryType?: string, limit?: number)
```

**参数：**
- `userId` - 用户 ID
- `memoryType` - 记忆类型（可选）
- `limit` - 记忆数量限制（默认 10）

**返回：**
```typescript
{
  memories: any[]
  total: number
}
```

## 错误处理

### ApiError 类

所有 API 错误都抛出 `ApiError` 实例：

```typescript
class ApiError extends Error {
  message: string           // 错误消息
  statusCode: number       // HTTP 状态码
  data?: any              // 错误数据
}
```

### 错误处理示例

```typescript
try {
  const response = await api.getSkills()
  // 处理响应
} catch (error) {
  if (error instanceof ApiError) {
    console.error('API 错误:', error.message)
    console.error('状态码:', error.statusCode)
    console.error('错误数据:', error.data)

    if (error.statusCode === 404) {
      // 处理 404 错误
    } else if (error.statusCode === 500) {
      // 处理服务器错误
    }
  } else {
    console.error('未知错误:', error)
  }
}
```

## 状态管理

### 加载状态

在异步请求时显示加载状态：

```vue
<script setup lang="ts">
const loading = ref(true)
const error = ref(null)

const fetchData = async () => {
  loading.value = true
  error.value = null

  try {
    const response = await api.getSkills()
    // 处理数据
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

onMounted(() => fetchData())
</script>

<template>
  <div v-if="loading">加载中...</div>
  <div v-else-if="error">错误: {{ error }}</div>
  <div v-else>数据内容</div>
</template>
```

## 实际应用

### 技能列表页面 (pages/skills.vue)

```vue
<script setup lang="ts">
const loading = ref(true)
const error = ref(null)
const skills = ref([])

const fetchSkills = async () => {
  loading.value = true
  error.value = null

  try {
    const response = await api.getSkills()
    skills.value = response.skills
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

onMounted(() => fetchSkills())
</script>

<template>
  <div v-if="loading" class="loading">加载中...</div>
  <div v-else-if="error" class="error">{{ error }}</div>
  <div v-else class="skills-list">
    <UCard v-for="skill in skills" :key="skill.name">
      <h3>{{ skill.name }}</h3>
      <p>{{ skill.description }}</p>
    </UCard>
  </div>
</template>
```

### 聊天页面 (pages/chat.vue)

```vue
<script setup lang="ts">
const messages = ref([])
const inputMessage = ref('')
const loading = ref(false)

const sendMessage = async () => {
  if (!inputMessage.value.trim()) return

  // 添加用户消息
  messages.value.push({
    role: 'user',
    content: inputMessage.value
  })

  const userMessage = inputMessage.value
  inputMessage.value = ''
  loading.value = true

  try {
    const response = await api.chat({
      user_input: userMessage,
      user_id: 'default_user'
    })

    // 添加 AI 回复
    messages.value.push({
      role: 'assistant',
      content: response.response
    })
  } catch (err) {
    console.error('发送失败:', err)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="chat">
    <div class="messages">
      <div v-for="msg in messages" :key="index" :class="['message', msg.role]">
        <UAvatar :icon="msg.role === 'assistant' ? 'i-heroicons-sparkles' : 'i-heroicons-user'" />
        <div class="content">{{ msg.content }}</div>
      </div>
    </div>

    <div class="input-area">
      <UInput v-model="inputMessage" @keyup.enter="sendMessage" />
      <UButton @click="sendMessage" :loading="loading">发送</UButton>
    </div>
  </div>
</template>
```

## 注意事项

1. **启动后端服务**：确保后端服务已启动并运行在配置的地址
2. **环境变量**：检查 `.env` 文件中的 `NUXT_PUBLIC_API_BASE_URL` 配置
3. **CORS 配置**：后端已配置 CORS 允许跨域请求
4. **错误处理**：所有 API 调用都应包含错误处理
5. **加载状态**：在异步请求时显示加载状态
6. **数据格式**：确保前端数据格式与后端 API 响应格式一致

## 故障排除

### 连接失败

**问题：** 无法连接到后端 API

**解决方案：**
1. 检查后端服务是否启动
2. 检查 `.env` 文件中的 API 地址配置
3. 检查网络连接
4. 查看浏览器控制台错误信息

### CORS 错误

**问题：** 跨域请求被阻止

**解决方案：**
1. 检查后端 CORS 配置
2. 确保后端允许前端域名访问

### 数据格式错误

**问题：** API 返回数据格式不匹配

**解决方案：**
1. 检查后端 API 文档
2. 更新前端数据类型定义
3. 使用 TypeScript 类型检查

## 扩展

### 添加新的 API 端点

在 `composables/api.ts` 中添加新方法：

```typescript
export const api = {
  // 现有方法...

  // 新方法
  myNewApi: (param: string) => request<any>(`/new-endpoint/${param}`),
}
```

### 自定义请求配置

```typescript
const customResponse = await request<any>('/custom-endpoint', {
  method: 'POST',
  headers: {
    'X-Custom-Header': 'value'
  },
  body: JSON.stringify({ key: 'value' })
})
```

## 相关资源

- [Nuxt 3 官方文档](https://nuxt.com/docs)
- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [后端 API 文档](../backend/api/main.py)
