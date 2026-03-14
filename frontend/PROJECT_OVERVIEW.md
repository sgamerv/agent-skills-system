# 前端项目概览

## 项目简介

前端项目是一个基于 Nuxt 3 和 Nuxt UI 构建的智能对话系统，提供用户友好的界面与后端 API 交互。

## 技术栈

- **框架**: Nuxt 3.21.2
- **UI 组件库**: Nuxt UI 2.22.3
- **样式**: Tailwind CSS
- **语言**: TypeScript
- **Node 版本**: >= 18.0.0
- **npm 版本**: >= 9.0.0

## 项目结构

```
frontend/
├── pages/              # 页面组件
│   ├── index.vue      # 首页
│   ├── chat.vue       # 聊天页面（含会话管理）
│   └── skills.vue     # 技能列表页面
├── composables/        # 可组合函数
│   └── api.ts         # API 客户端
├── components/        # 可复用组件
├── app.config.ts      # Nuxt 配置
├── nuxt.config.ts     # Nuxt 配置
├── package.json       # 依赖配置
└── README.md          # 前端说明文档
```

## 核心功能

### 1. 会话管理

聊天页面集成了完整的会话管理功能，包括：

#### 功能特性

- **左侧会话列表**
  - 显示所有历史会话
  - 支持点击切换会话
  - 高亮显示当前选中会话
  - 显示会话更新时间（相对时间格式：刚刚、5分钟前、2小时前、3天前等）
  - 新建会话按钮

- **会话切换**
  - 点击会话列表项即可切换到对应会话
  - 自动加载该会话的历史消息记录
  - 保持会话状态和上下文

- **新建会话**
  - 点击"新建会话"按钮创建新会话
  - 新会话默认标题为"当前会话"
  - 新会话显示欢迎消息

- **智能标题生成**
  - 用户首次发送消息时，自动将消息内容（前20个字符）作为会话标题
  - 如果消息超过20字符，显示前20字符 + "..."
  - 之后的交互不再自动更新标题

#### 界面布局

```
┌─────────────────────────────────────────────────────────┐
│  左侧边栏          │  右侧聊天区域                      │
│  ┌──────────────┐  │  ┌──────────────────────────────┐ │
│  │ 会话列表     │  │  │ 消息显示区                   │ │
│  │ - 新建会话   │  │  │  - 用户消息                 │ │
│  │ - 会话1      │  │  │  - 助手回复                 │ │
│  │ - 会话2 [✓]  │  │  │  - ...                      │ │
│  │ - 会话3      │  │  └──────────────────────────────┘ │
│  │ - ...        │  │  ┌──────────────────────────────┐ │
│  └──────────────┘  │  │ 输入框 + 发送按钮            │ │
│                   │  └──────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

#### 响应式设计

- 桌面端：左右布局，左侧固定宽度 320px
- 移动端：上下布局，左侧高度 200px，聊天消息宽度调整至 90%

### 2. 聊天功能

#### 消息发送

- 支持用户输入问题并发送
- Enter 键快捷发送
- 发送中显示加载状态（思考中...）
- 错误处理和错误提示横幅

#### 消息显示

- 用户消息：右侧显示，蓝色背景，白色文字
- 助手消息：左侧显示，灰色背景，黑色文字
- 头像区分：用户头像、助手头像（带 Sparkles 图标）
- 消息自动滚动到底部

#### 与后端集成

- 调用 `/chat` 接口发送消息
- 携带 `user_id` 和 `session_id`
- 支持多轮对话和参数收集
- 支持技能匹配和执行

### 3. API 集成

#### API 客户端（composables/api.ts）

统一管理所有后端 API 请求，提供类型安全的接口。

**核心接口：**

```typescript
// 健康检查
api.healthCheck()

// 获取技能列表
api.getSkills()

// 获取技能详情
api.getSkill(skillName)

// 聊天
api.chat({
  user_input: string,
  user_id: string,
  conversation_id?: string,
  session_id?: string
})

// 创建会话
api.createSession(userId: string, title?: string)

// 获取会话
api.getSession(sessionId: string)

// 更新会话标题
api.updateSession(sessionId: string, title: string)

// 获取用户会话列表
api.getUserSessions(userId: string)

// 获取会话消息
api.getSessionMessages(sessionId: string, limit?: number)
```

#### 错误处理

- 自动捕获网络错误
- 统一错误提示
- 错误状态管理

### 4. 页面路由

- `/` - 首页（欢迎页）
- `/chat` - 聊天页面（含会话管理）
- `/skills` - 技能列表页面

## 开发指南

### 环境配置

1. **安装依赖**

```bash
cd frontend
npm install
```

2. **配置环境变量**

创建 `.env` 文件（可选）：

```env
NUXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

3. **启动开发服务器**

```bash
npm run dev
```

访问 http://localhost:3000

### 构建部署

```bash
# 构建生产版本
npm run build

# 预览生产版本
npm run preview
```

### 代码规范

- 使用 TypeScript 进行类型检查
- 使用 ESLint 进行代码检查
- 使用 Prettier 进行代码格式化
- 遵循 Vue 3 Composition API 规范

## 后端 API 对接

### 后端服务

- 地址: http://localhost:8000
- 健康检查: GET /health
- API 文档: 访问后端项目查看详细文档

### 会话管理接口

#### 创建会话

```
POST /sessions
Body: { user_id: string, title?: string }
Response: { session_id, user_id, status, title, created_at, updated_at }
```

#### 获取会话列表

```
GET /users/{user_id}/sessions
Response: { sessions: [...], total: number }
```

#### 获取会话详情

```
GET /sessions/{session_id}
Response: { session_id, user_id, status, title, created_at, updated_at }
```

#### 更新会话标题

```
PUT /sessions/{session_id}
Body: { title: string }
Response: { session_id, user_id, status, title, created_at, updated_at }
```

#### 获取会话消息

```
GET /sessions/{session_id}/messages?limit=50
Response: { messages: [...], total: number }
```

### 聊天接口

```
POST /chat
Body: { user_input: string, user_id: string, conversation_id?: string, session_id?: string }
Response: {
  response: string,
  conversation_id?: string,
  session_id?: string,
  mode: string,
  state: string,
  available_skills?: any[],
  current_slot?: any,
  collected_parameters?: Record<string, any>,
  execution_result?: any,
  task_id?: string,
  feedback_required?: boolean,
  feedback?: any,
  next_action?: string
}
```

## 设计原则

1. **用户体验优先**
   - 清晰的界面布局
   - 流畅的交互动画
   - 友好的错误提示

2. **响应式设计**
   - 支持桌面端和移动端
   - 自适应屏幕尺寸

3. **类型安全**
   - TypeScript 类型定义
   - API 接口类型化

4. **可维护性**
   - 组件化开发
   - 统一的 API 管理
   - 清晰的代码结构

## 未来计划

- [ ] 添加会话删除功能
- [ ] 添加会话搜索功能
- [ ] 添加会话归档功能
- [ ] 优化移动端体验
- [ ] 添加消息复制功能
- [ ] 添加消息反馈功能（赞/踩）
- [ ] 添加技能执行结果展示
- [ ] 添加深色模式切换

## 常见问题

### 1. 如何切换会话？

点击左侧会话列表中的任意会话即可切换。

### 2. 如何创建新会话？

点击左侧边栏顶部的"新建会话"按钮。

### 3. 会话标题如何生成？

首次发送消息时，系统自动将消息内容（前20字符）作为会话标题。

### 4. 如何查看会话历史消息？

切换到对应会话后，右侧聊天区域会自动加载该会话的历史消息。

### 5. 移动端如何使用？

在移动设备上，左侧会话列表会变为顶部区域，点击会话后下方显示聊天内容。

## 联系方式

如有问题，请查看后端项目文档或联系开发团队。
