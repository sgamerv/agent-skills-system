/**
 * API 客户端
 * 统一管理所有后端 API 请求
 */

const API_BASE_URL = process.env.NUXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'

// 技能接口
export interface Skill {
  name: string
  description: string
  category: string
  tags: string[]
  version: string
}

export interface SkillListResponse {
  skills: Skill[]
  total: number
}

// 聊天接口
export interface ChatRequest {
  user_input: string
  user_id: string
  conversation_id?: string
  session_id?: string
}

export interface ChatResponse {
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

// 会话接口
export interface Session {
  session_id: string
  user_id: string
  status: string
  title?: string
  created_at?: string
  updated_at?: string
}

export interface SessionListResponse {
  sessions: Session[]
  total: number
}

// 通用错误处理
class ApiError extends Error {
  constructor(
    message: string,
    public statusCode: number = 500,
    public data?: any
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

// 封装 fetch 请求
async function request<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`

  const config: RequestInit = {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  }

  try {
    const response = await fetch(url, config)

    // 处理 HTTP 错误
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new ApiError(
        errorData.detail || 'API 请求失败',
        response.status,
        errorData
      )
    }

    return await response.json()
  } catch (error) {
    if (error instanceof ApiError) {
      throw error
    }
    throw new ApiError('网络请求失败，请检查后端服务是否启动')
  }
}

// API 方法
export const api = {
  // 健康检查
  healthCheck: () => request<{ status: string }>('/health'),

  // 获取技能列表
  getSkills: () => request<SkillListResponse>('/skills'),

  // 获取技能详情
  getSkill: (skillName: string) => request<any>(`/skills/${skillName}`),

  // 聊天
  chat: (data: ChatRequest) => request<ChatResponse>('/chat', {
    method: 'POST',
    body: JSON.stringify(data),
  }),

  // 创建会话
  createSession: (userId: string, title?: string) => request<Session>('/sessions', {
    method: 'POST',
    body: JSON.stringify({ user_id: userId, title }),
  }),

  // 获取会话
  getSession: (sessionId: string) => request<Session>(`/sessions/${sessionId}`),

  // 获取用户会话列表
  getUserSessions: (userId: string) => request<SessionListResponse>(`/users/${userId}/sessions`),

  // 获取会话消息
  getSessionMessages: (sessionId: string, limit = 50) => request<{ messages: any[], total: number }>(
    `/sessions/${sessionId}/messages?limit=${limit}`
  ),

  // 获取用户画像
  getUserProfile: (userId: string) => request<any>(`/users/${userId}/profile`),

  // 获取用户记忆
  getUserMemories: (userId: string, memoryType?: string, limit = 10) => {
    const params = new URLSearchParams({ limit: limit.toString() })
    if (memoryType) params.append('memory_type', memoryType)
    return request<{ memories: any[], total: number }>(`/users/${userId}/memories?${params.toString()}`)
  },
}

export default api
