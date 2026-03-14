# Agent Skills Frontend - Nuxt 3

基于 Nuxt 3 和 Nuxt UI 的智能多技能编排系统前端界面

## 🚀 技术栈

### 核心框架
- **Nuxt 3** (v3.15.4) - 基于 Vue 3 的全栈框架
- **Vue 3** (v3.5.13) - 渐进式 JavaScript 框架
- **TypeScript** (v5.7.2) - JavaScript 的超集

### UI 组件库
- **Nuxt UI** (@nuxt/ui) - Nuxt 3 官方推荐的 UI 组件库
  - 基于 Tailwind CSS
  - 完美集成 Nuxt 3
  - 自动支持深色模式
  - 内置图标系统 (Heroicons)
  - 高度可定制的主题系统
  - 优秀的可访问性支持

### 开发工具
- **Vite** - 下一代前端构建工具
- **Tailwind CSS** - 实用优先的 CSS 框架
- **ESLint** - 代码质量检查
- **Prettier** - 代码格式化
- **Sass** - CSS 预处理器

## ✨ 特性

### Nuxt 3 核心特性
- 📁 **自动路由** - 基于 `pages/` 目录自动生成路由
- 🔌 **自动导入** - 组件、组合式函数、工具函数自动导入
- 🌐 **服务端渲染 (SSR)** - 更好的 SEO 和首屏加载性能
- ⚡ **快速刷新 (HMR)** - 开发时实时预览修改
- 📦 **代码分割** - 自动拆分代码，减少初始加载时间
- 🎯 **TypeScript 支持** - 完整的类型支持
- 🌍 **国际化** - 内置 i18n 支持
- 🔒 **环境变量** - 内置环境变量管理

### Nuxt UI 特性
- 🎨 **丰富的组件** - 50+ 高质量 UI 组件
- 🌓 **深色模式** - 自动支持主题切换
- 🎭 **主题定制** - 基于 Tailwind CSS 的灵活主题系统
- 🎯 **TypeScript 支持** - 完整的类型定义
- ♿ **无障碍访问** - 符合 WCAG 标准
- 📦 **按需引入** - 自动按需加载，减少包体积
- 🎨 **图标集成** - 内置 200+ Heroicons 图标

## 📦 安装依赖

```bash
npm install
```

## 🚀 开发

### 启动开发服务器

```bash
npm run dev
```

访问 http://localhost:3000

### 可用的开发命令

```bash
npm run dev         # 启动开发服务器
npm run build       # 构建生产版本
npm run generate    # 生成静态站点
npm run preview     # 预览生产构建
npm run lint        # 检查代码
npm run lint:fix    # 检查并修复代码
npm run format      # 格式化代码
npm run format:check # 检查代码格式
```

## 📁 项目结构

```
frontend-nuxt3/
├── .nuxt/                  # Nuxt 自动生成的文件（不提交）
├── assets/                 # 静态资源
│   └── css/
│       └── main.css       # 全局样式
├── components/             # Vue 组件（自动导入）
├── composables/            # 组合式函数（自动导入）
├── layouts/                # 布局组件
│   └── default.vue        # 默认布局
├── pages/                  # 页面（自动生成路由）
│   ├── index.vue          # 首页
│   ├── chat.vue           # 聊天页
│   └── skills.vue         # 技能列表
├── public/                 # 静态文件
├── app.vue                 # 根组件
├── nuxt.config.ts         # Nuxt 配置
├── tsconfig.json          # TypeScript 配置
├── .eslintrc.cjs          # ESLint 配置
├── .prettierrc            # Prettier 配置
├── .gitignore             # Git 忽略配置
├── package.json           # 项目配置
└── README.md              # 项目说明
```

## 🎨 Nuxt UI 组件使用

### 基本使用

Nuxt UI 组件可以直接在任何 Vue 文件中使用，无需额外导入：

```vue
<template>
  <div>
    <!-- 按钮组件 -->
    <UButton>默认按钮</UButton>
    <UButton color="primary">主要按钮</UButton>
    <UButton color="green">成功按钮</UButton>
    <UButton icon="i-heroicons-star">带图标</UButton>

    <!-- 输入框组件 -->
    <UInput v-model="value" placeholder="请输入内容" />

    <!-- 卡片组件 -->
    <UCard>
      <template #header>
        卡片标题
      </template>
      卡片内容
    </UCard>

    <!-- 徽章组件 -->
    <UBadge color="green">已启用</UBadge>
    <UBadge color="red" variant="subtle">已禁用</UBadge>

    <!-- 头像组件 -->
    <UAvatar icon="i-heroicons-user" />
    <UAvatar src="https://example.com/avatar.png" />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const value = ref('')
</script>
```

### 常用组件

#### 按钮 (UButton)
```vue
<UButton>默认按钮</UButton>
<UButton color="primary">主要按钮</UButton>
<UButton color="green">成功按钮</UButton>
<UButton color="yellow">警告按钮</UButton>
<UButton color="red">危险按钮</UButton>
<UButton variant="outline">轮廓按钮</UButton>
<UButton variant="ghost">幽灵按钮</UButton>
<UButton size="sm">小按钮</UButton>
<UButton size="lg">大按钮</UButton>
<UButton icon="i-heroicons-star-solid">带图标</UButton>
```

#### 输入框 (UInput)
```vue
<UInput v-model="value" placeholder="请输入" />
<UInput v-model="value" type="password" placeholder="密码" />
<UInput v-model="value" icon="i-heroicons-magnifying-glass" />
<UInput v-model="value" size="lg" placeholder="大输入框" />
<UInput v-model="value" disabled placeholder="禁用状态" />
```

#### 卡片 (UCard)
```vue
<UCard>
  <template #header>
    <h3>卡片标题</h3>
  </template>
  <p>卡片内容</p>
  <template #footer>
    <UButton>操作按钮</UButton>
  </template>
</UCard>
```

#### 徽章 (UBadge)
```vue
<UBadge>默认</UBadge>
<UBadge color="primary">主要</UBadge>
<UBadge color="green">成功</UBadge>
<UBadge color="red" variant="subtle">危险</UBadge>
<UBadge size="sm">小徽章</UBadge>
<UBadge size="lg">大徽章</UBadge>
```

#### 头像 (UAvatar)
```vue
<UAvatar icon="i-heroicons-user" />
<UAvatar src="/avatar.jpg" />
<UAvatar src="/avatar.jpg" size="sm" />
<UAvatar src="/avatar.jpg" size="lg" />
<UAvatar src="/avatar.jpg" alt="用户头像" />
```

#### 容器 (UContainer)
```vue
<UContainer>
  <h1>内容区域</h1>
  <p>这是一个受限宽度的容器</p>
</UContainer>
```

#### 图标 (UIcon)
```vue
<!-- 使用 Heroicons -->
<UIcon name="i-heroicons-home" />
<UIcon name="i-heroicons-heart-solid" />

<!-- 自定义样式 -->
<UIcon name="i-heroicons-star" class="text-red-500 text-2xl" />
```

更多组件和详细用法请参考 [Nuxt UI 官方文档](https://ui.nuxt.com/)

## 🎯 页面说明

### 首页 (`/`)
- 系统介绍和功能展示
- 快速导航到各个功能模块
- 响应式设计

### 智能对话 (`/chat`)
- 多轮对话界面
- 消息历史记录
- 实时输入和发送

### 技能列表 (`/skills`)
- 显示所有可用的 AI 技能
- 技能状态管理
- 技能详情展示

## 🎨 设计规范

### 配色方案
- **主色调**: 紫色渐变 `#667eea → #764ba2`
- **背景**: 135° 线性渐变
- **卡片背景**: 纯白色 `#ffffff`
- **主按钮**: 白色背景，紫色文字
- **次要按钮**: 半透明白色 `rgba(255, 255, 255, 0.2)`

### CSS 变量
```css
:root {
  --primary-color: #667eea;
  --secondary-color: #764ba2;
  --gradient-bg: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  --text-primary: #333;
  --text-secondary: #666;
  --text-white: #ffffff;
  --bg-white: #ffffff;
  --shadow-sm: 0 2px 4px rgba(0, 0, 0, 0.1);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);
}
```

### 字体样式规范

项目中所有页面使用统一的字体样式系统，确保视觉一致性：

#### 标题样式 (Heading)
- **大标题** (3.5rem)
  - `font-weight: 800`
  - `text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1)`
  - 渐变文字效果：`background: linear-gradient(135deg, #ffffff 0%, #f0f0f0 100%)`
  - 使用场景：首页主标题

- **中标题** (2.5rem)
  - `font-weight: 700`
  - `text-shadow: 0 2px 8px rgba(0, 0, 0, 0.15)`
  - 使用场景：页面主标题、英雄区标题

- **小标题** (1.25rem)
  - `font-weight: 600`
  - `color: #1a1a2e`
  - 使用场景：卡片标题、技能名称

#### 副标题样式 (Subtitle)
- `font-size: 1.125rem`
- `font-weight: 300`
- `color: rgba(255, 255, 255, 0.9)`
- 使用场景：页面副标题

#### 正文样式 (Body)
- `font-size: 0.9375rem` - 卡片描述文字
- `font-size: 1.125rem` - 描述段落
- `font-weight: 400`
- `line-height: 1.6-1.8`
- `color: #4a4a68` (深灰色) 或 `rgba(255, 255, 255, 0.9)` (白色背景)

#### 特殊强调
- **用户消息**: `font-weight: 500` (略粗)
- **普通消息**: `font-weight: 400` (常规)

#### 响应式设计
移动端自适应（max-width: 768px）：
- 大标题：2.25rem
- 中标题：1.75rem
- 小标题：1rem
- 副标题：1rem

#### 使用示例
```vue
<style scoped>
.title {
  font-size: 2.5rem;
  font-weight: 700;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  color: white;
}

.subtitle {
  font-size: 1.125rem;
  font-weight: 300;
  color: rgba(255, 255, 255, 0.9);
}

.card-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1a1a2e;
}

.description {
  font-size: 0.9375rem;
  font-weight: 400;
  line-height: 1.6;
  color: #4a4a68;
}
</style>
```

#### 字体系列
项目使用系统默认字体栈，确保在各种设备上都有良好的显示效果。如有需要，可在 `nuxt.config.ts` 或全局 CSS 文件中配置自定义字体。


## 🔧 配置说明

### Nuxt 配置 (nuxt.config.ts)

```typescript
export default defineNuxtConfig({
  compatibilityDate: '2024-11-01',
  devtools: { enabled: true },

  // 启用 Nuxt UI 模块
  modules: ['@nuxt/ui'],

  app: {
    head: {
      title: 'Agent Skills System',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' }
      ]
    }
  },

  css: ['~/assets/css/main.css'],

  typescript: {
    strict: true,
    typeCheck: true
  }
})
```

### Nuxt UI 配置

Nuxt UI 会自动配置 Tailwind CSS 和主题。你可以在 `app.config.ts` 中自定义主题：

```typescript
// app.config.ts
export default defineAppConfig({
  ui: {
    primary: 'green',
    gray: 'slate',
    global: true
  }
})
```

## 📝 开发指南

### 创建新页面

在 `pages/` 目录下创建 `.vue` 文件：

```bash
# 创建 pages/about.vue
touch pages/about.vue
```

访问 http://localhost:3000/about

### 创建新组件

在 `components/` 目录下创建 `.vue` 文件：

```bash
# 创建 components/MyButton.vue
touch components/MyButton.vue
```

组件会自动注册，可以直接在任何地方使用：

```vue
<template>
  <MyButton>点击我</MyButton>
</template>
```

### 创建组合式函数

在 `composables/` 目录下创建 `.ts` 文件：

```typescript
// composables/useCounter.ts
export const useCounter = () => {
  const count = ref(0)

  const increment = () => count.value++
  const decrement = () => count.value--

  return { count, increment, decrement }
}
```

自动导入，直接使用：

```vue
<script setup lang="ts">
const { count, increment } = useCounter()
</script>
```

## 🌐 环境变量

在项目根目录创建 `.env` 文件：

```bash
# .env
NUXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

在代码中使用：

```typescript
const apiUrl = useRuntimeConfig().public.apiBaseUrl
```

## 🔌 后端 API 集成

### API 配置

项目已集成后端 API，通过 `composables/api.ts` 统一管理所有 API 请求。

### 环境变量配置

确保 `.env` 文件中配置了正确的后端 API 地址：

```bash
NUXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

### API 客户端使用

项目提供了统一的 API 客户端（`composables/api.ts`），所有 API 请求都通过该客户端进行：

```typescript
import { api } from '~/composables/api'

// 获取技能列表
const skills = await api.getSkills()

// 发送聊天消息
const response = await api.chat({
  user_input: '你好',
  user_id: 'default_user'
})

// 获取会话列表
const sessions = await api.getUserSessions('user_id')
```

### 可用 API 端点

#### 健康检查
```typescript
api.healthCheck() // 返回: { status: string }
```

#### 技能管理
```typescript
api.getSkills() // 获取所有技能
api.getSkill(skillName: string) // 获取技能详情
```

#### 聊天
```typescript
api.chat(data: ChatRequest) // 发送聊天消息
// ChatRequest: { user_input, user_id, conversation_id?, session_id? }
```

#### 会话管理
```typescript
api.createSession(userId: string, title?: string) // 创建会话
api.getSession(sessionId: string) // 获取会话详情
api.getUserSessions(userId: string) // 获取用户会话列表
api.getSessionMessages(sessionId: string, limit?: number) // 获取会话消息
```

#### 用户数据
```typescript
api.getUserProfile(userId: string) // 获取用户画像
api.getUserMemories(userId: string, memoryType?: string, limit?: number) // 获取用户记忆
```

### 错误处理

API 客户端提供了统一的错误处理机制：

```typescript
try {
  const response = await api.getSkills()
} catch (error) {
  if (error instanceof ApiError) {
    console.error('API 错误:', error.message, error.statusCode)
  } else {
    console.error('未知错误:', error)
  }
}
```

### 页面中的实际应用

#### 技能列表页面 (pages/skills.vue)

- 从后端 API 获取技能列表
- 显示加载状态和错误提示
- 技能卡片展示技能信息

```vue
<script setup lang="ts">
const skills = ref([])
const loading = ref(true)
const error = ref(null)

const fetchSkills = async () => {
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
```

#### 聊天页面 (pages/chat.vue)

- 通过 API 发送用户消息
- 显示 AI 回复
- 支持加载状态显示

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
  } catch (err) {
    console.error('发送失败:', err)
  }
}
</script>
```

### 注意事项

1. **启动后端服务**：确保后端服务已启动并运行在 `http://localhost:8000`
2. **CORS 配置**：后端已配置 CORS 允许跨域请求
3. **错误处理**：所有 API 调用都应包含错误处理
4. **加载状态**：在异步请求时显示加载状态，提升用户体验
5. **数据格式**：确保前端数据格式与后端 API 响应格式一致

## 🌓 深色模式

Nuxt UI 自动支持深色模式。你可以在组件中使用 `useColorMode()` 来切换主题：

```vue
<script setup lang="ts">
const colorMode = useColorMode()
</script>

<template>
  <UButton
    :icon="colorMode.value === 'dark' ? 'i-heroicons-moon-20-solid' : 'i-heroicons-sun-20-solid'"
    @click="colorMode.preference = colorMode.value === 'dark' ? 'light' : 'dark'"
  >
    切换主题
  </UButton>
</template>
```

### 主题配置

在 `app.config.ts` 中配置主题：

```typescript
export default defineAppConfig({
  ui: {
    primary: 'green',
    gray: 'slate'
  }
})
```

## 📚 相关资源

- [Nuxt 3 官方文档](https://nuxt.com/docs)
- [Nuxt UI 官方文档](https://ui.nuxt.com/)
- [Tailwind CSS 文档](https://tailwindcss.com/docs)
- [Vue 3 官方文档](https://vuejs.org/)
- [TypeScript 官方文档](https://www.typescriptlang.org/)

## 🤝 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

MIT License

## 🎯 未来计划

- [ ] 添加更多 Nuxt UI 组件示例
- [ ] 优化主题定制
- [ ] 添加国际化支持
- [ ] 集成后端 API
- [ ] 添加单元测试
- [ ] 优化性能
- [ ] 添加动画效果
- [ ] 实现 WebSocket 实时通信

## 🔄 迁移说明

本项目已从 TinyVue 迁移到 Nuxt UI。Nuxt UI 是 Nuxt 3 官方推荐的 UI 组件库，具有以下优势：

- ✅ 完美集成 Nuxt 3，无需额外配置
- ✅ 自动支持深色模式
- ✅ 基于 Tailwind CSS，样式定制更灵活
- ✅ 内置丰富的图标库（Heroicons）
- ✅ 更好的 TypeScript 支持
- ✅ 持续维护和更新

---

**Note**: 本项目使用 Nuxt 3 和 Nuxt UI 构建，提供了现代化的开发体验和丰富的 UI 组件，并自动支持深色模式。
