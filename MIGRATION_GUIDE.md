# 前端迁移指南：从 Vue 3 迁移到 Nuxt 3 + TinyVue

本文档说明如何从原 Vue 3 项目迁移到新的 Nuxt 3 + TinyVue 项目。

## 📋 迁移概述

### 原项目 (frontend/)
- Vue 3 + Vite
- 手动配置路由
- 需要手动导入组件
- 客户端渲染 (CSR)

### 新项目 (frontend-nuxt3/)
- ✅ Nuxt 3（基于 Vue 3）
- ✅ 自动路由
- ✅ 自动导入
- ✅ 服务端渲染 (SSR)
- ✅ TinyVue 组件库集成

## 🚀 快速开始

### 1. 启动新项目

```bash
cd frontend-nuxt3
npm install
npm run dev
```

访问 http://localhost:3000

### 2. 原项目备份

原 Vue 3 代码已备份到 `frontend/src_backup_vue/` 目录。

## 🔄 主要变化

### 1. 目录结构

#### Vue 3 结构
```
frontend/
├── src/
│   ├── views/
│   ├── components/
│   ├── router/
│   ├── stores/
│   └── App.vue
├── main.js
└── vite.config.js
```

#### Nuxt 3 结构
```
frontend-nuxt3/
├── pages/           # 页面（自动路由）
├── components/      # 组件（自动导入）
├── layouts/         # 布局
├── composables/     # 组合式函数（自动导入）
├── plugins/         # Nuxt 插件
├── assets/          # 静态资源
├── app.vue          # 根组件
└── nuxt.config.ts   # Nuxt 配置
```

### 2. 路由系统

#### Vue 3 - 手动配置
```javascript
// router/index.js
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', component: () => import('@/views/Home.vue') },
  { path: '/chat', component: () => import('@/views/Chat.vue') },
  { path: '/skills', component: () => import('@/views/Skills.vue') }
]

export default createRouter({
  history: createWebHistory(),
  routes
})
```

#### Nuxt 3 - 自动路由
```bash
# pages/ 目录结构自动生成路由
pages/
├── index.vue        # /
├── chat.vue         # /chat
└── skills.vue       # /skills
```

**无需手动配置路由！**

### 3. 组件导入

#### Vue 3 - 手动导入
```vue
<script setup>
import MyComponent from '@/components/MyComponent.vue'
</script>

<template>
  <MyComponent />
</template>
```

#### Nuxt 3 - 自动导入
```vue
<!-- 直接使用，无需导入 -->
<template>
  <MyComponent />
</template>
```

### 4. 组合式函数

#### Vue 3 - 手动导入
```vue
<script setup>
import { ref, computed } from 'vue'
import { useCounter } from '@/composables/useCounter'

const count = ref(0)
const { increment } = useCounter()
</script>
```

#### Nuxt 3 - 自动导入
```vue
<script setup>
// ref, computed 等自动导入
const count = ref(0)

// composables/ 目录下的函数自动导入
const { increment } = useCounter()
</script>
```

### 5. 页面导航

#### Vue 3
```vue
<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const navigate = () => {
  router.push('/chat')
}
</script>
```

#### Nuxt 3
```vue
<script setup>
// useRouter 自动导入
const router = useRouter()

const navigate = () => {
  router.push('/chat')
}
</script>

<template>
  <!-- 或使用 NuxtLink -->
  <NuxtLink to="/chat">去聊天</NuxtLink>
</template>
```

### 6. 页面元信息

#### Vue 3
```javascript
// 需要手动配置
// router/index.js
{
  path: '/chat',
  component: Chat,
  meta: { title: '智能对话' }
}
```

#### Nuxt 3
```vue
<script setup>
definePageMeta({
  layout: 'default'
})

useHead({
  title: '智能对话 - Agent Skills System'
})
</script>
```

### 7. 布局系统

#### Vue 3 - 需要手动实现
```vue
<!-- App.vue -->
<template>
  <div>
    <Nav />
    <router-view />
    <Footer />
  </div>
</template>
```

#### Nuxt 3 - 内置布局系统
```vue
<!-- layouts/default.vue -->
<template>
  <div>
    <Nav />
    <slot />
    <Footer />
  </div>
</template>

<!-- pages/index.vue -->
<script setup>
definePageMeta({
  layout: 'default'
})
</script>
```

### 8. TinyVue 组件

#### Vue 3 - 需要手动配置
```vue
<script setup>
import { Button as TinyButton } from '@opentiny/vue'
</script>

<template>
  <TinyButton>按钮</TinyButton>
</template>
```

#### Nuxt 3 - 全局注册
```typescript
// plugins/tinyvue.ts
import TinyVue from '@opentiny/vue'

export default defineNuxtPlugin((nuxtApp) => {
  nuxtApp.vueApp.use(TinyVue)
})
```

```vue
<!-- 直接使用 -->
<template>
  <tiny-button>按钮</tiny-button>
  <tiny-input v-model="value" />
</template>
```

## 📦 功能迁移对照表

| 功能 | Vue 3 | Nuxt 3 |
|------|-------|--------|
| 路由 | `vue-router` 手动配置 | `pages/` 自动生成 |
| 组件导入 | 手动 `import` | 自动导入 |
| 组合式函数 | 手动 `import` | 自动导入 |
| Vue API | 手动 `import` | 自动导入 |
| 页面导航 | `router.push()` | `router.push()` / `<NuxtLink>` |
| SEO | 需要额外配置 | 内置 SSR |
| 热更新 | Vite HMR | Vite HMR |
| 类型支持 | 需配置 TypeScript | 内置 TypeScript |
| 状态管理 | Pinia | 可用 Pinia |
| HTTP 客户端 | Axios | `$fetch` / Axios |
| 插件系统 | Vue 插件 | Nuxt 插件 |

## 🎯 迁移步骤

### 1. 迁移页面组件

将 `src/views/` 下的文件移到 `pages/` 目录，并调整：

```vue
<!-- 原始 Vue 3 -->
<script setup>
import { ref } from 'vue'
</script>

<!-- Nuxt 3 -->
<script setup>
// ref 自动导入，无需 import
definePageMeta({
  layout: 'default'
})

useHead({
  title: '页面标题'
})
</script>
```

### 2. 迁移公共组件

将 `src/components/` 下的文件移到 `components/` 目录，移除所有 import 语句。

### 3. 迁移路由配置

删除 `src/router/index.js`，使用 `pages/` 目录自动生成路由。

### 4. 迁移布局

将公共布局移到 `layouts/default.vue`。

### 5. 迁移状态管理

如果使用 Pinia，可以继续使用：

```typescript
// stores/counter.ts
export const useCounterStore = defineStore('counter', () => {
  const count = ref(0)
  const increment = () => count.value++

  return { count, increment }
})
```

### 6. 更新 API 调用

```vue
<!-- Vue 3 - Axios -->
<script setup>
import axios from 'axios'

const fetchData = async () => {
  const response = await axios.get('/api/data')
}
</script>

<!-- Nuxt 3 - $fetch -->
<script setup>
const fetchData = async () => {
  const data = await $fetch('/api/data')
}
</script>
```

## 💡 最佳实践

### 1. 使用 Nuxt 3 特性

- ✅ 利用自动路由
- ✅ 利用自动导入
- ✅ 使用 `useHead()` 管理 SEO
- ✅ 使用 `<NuxtLink>` 进行导航
- ✅ 使用 `$fetch` 进行数据获取

### 2. 使用 TinyVue 组件

```vue
<template>
  <tiny-button type="primary">主要按钮</tiny-button>
  <tiny-input v-model="value" placeholder="请输入" />
  <tiny-form :model="form" :rules="rules">
    <tiny-form-item label="用户名" prop="username">
      <tiny-input v-model="form.username" />
    </tiny-form-item>
  </tiny-form>
</template>
```

### 3. 使用组合式函数

```typescript
// composables/useApi.ts
export const useApi = () => {
  const data = ref(null)
  const loading = ref(false)
  const error = ref(null)

  const fetch = async (url: string) => {
    loading.value = true
    error.value = null

    try {
      data.value = await $fetch(url)
    } catch (e) {
      error.value = e
    } finally {
      loading.value = false
    }
  }

  return { data, loading, error, fetch }
}
```

## 🔗 相关文档

- [Nuxt 3 官方文档](https://nuxt.com/docs)
- [TinyVue 官方文档](https://opentiny.design/vue-doc/)
- [Vue 3 官方文档](https://vuejs.org/)
- [前端项目文档](frontend-nuxt3/README.md)

## ❓ 常见问题

### Q: 原项目代码还能用吗？
A: 可以，原代码已备份到 `frontend/src_backup_vue/`，但推荐使用新的 Nuxt 3 项目。

### Q: 如何迁移现有功能？
A: 按照本文档的迁移步骤，将组件和逻辑移到新的 Nuxt 3 结构中。

### Q: TinyVue 组件有哪些？
A: 查看 [TinyVue 文档](https://opentiny.design/vue-doc/) 或 [前端 README](frontend-nuxt3/README.md)。

### Q: 如何配置环境变量？
A: 创建 `.env` 文件，使用 `useRuntimeConfig()` 访问。

## ✅ 迁移检查清单

- [ ] 安装依赖
- [ ] 迁移页面组件到 `pages/`
- [ ] 迁移公共组件到 `components/`
- [ ] 创建布局文件 `layouts/default.vue`
- [ ] 移除路由配置
- [ ] 移除手动 import 语句
- [ ] 使用 `useHead()` 管理 SEO
- [ ] 使用 `<NuxtLink>` 替代 `router-link`
- [ ] 集成 TinyVue 组件
- [ ] 测试所有功能

---

**迁移完成后，你将享受到 Nuxt 3 带来的更好的开发体验和性能！**
