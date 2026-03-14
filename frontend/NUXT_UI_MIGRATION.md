# Nuxt UI 迁移概述

## 迁移时间
2026-03-14

## 迁移原因
原计划使用的 TinyVue 组件库在 Nuxt 3 中存在模块路径解析问题，无法正常运行。经过评估，决定迁移到 Nuxt UI。

## Nuxt UI 优势
- ✅ 完美集成 Nuxt 3，无需额外配置
- ✅ 自动支持深色模式
- ✅ 基于 Tailwind CSS，样式定制更灵活
- ✅ 内置丰富的图标库（200+ Heroicons）
- ✅ 更好的 TypeScript 支持
- ✅ 持续维护和更新
- ✅ 按需自动导入，减少包体积

## 主要变更

### 1. 依赖更新
**新增:**
- `@nuxt/ui` - Nuxt UI 组件库
- 自动安装 Tailwind CSS

**移除:**
- `@opentiny/vue` - TinyVue 组件库
- `@opentiny/vue-renderless` - TinyVue 渲染层

### 2. 配置文件更新
- `nuxt.config.ts`: 添加 `@nuxt/ui` 模块
- `app.config.ts`: 新建主题配置文件，设置 primary 和 gray 颜色

### 3. 页面组件更新

#### layouts/default.vue
- 添加深色模式切换按钮 (UButton)
- 使用 Nuxt UI 颜色变量替换自定义 CSS 变量

#### pages/index.vue
- 按钮组件: 自定义 `.btn` → `UButton`
- 卡片组件: 自定义 `.feature-card` → `UCard`
- 图标: Emoji → `UIcon` (Heroicons)

#### pages/chat.vue
- 卡片容器: 自定义样式 → `UCard`
- 输入框: `<input>` → `UInput`
- 按钮: 自定义 `.btn` → `UButton`
- 头像: 新增 `UAvatar` 组件显示消息发送者

#### pages/skills.vue
- 容器: 自定义 `.container` → `UContainer`
- 卡片组件: 自定义 `.skill-card` → `UCard`
- 徽章: 自定义 `.skill-status` → `UBadge`
- 图标: Emoji → `UIcon` (Heroicons)

### 4. 样式调整
- 使用 Nuxt UI 的 Tailwind CSS 类
- 使用 Nuxt UI 的颜色变量（如 `rgb(var(--color-primary-500))`）
- 减少自定义 CSS 代码量约 60%
- 保留必要的页面特定样式

### 5. 文档更新
- README.md 更新为 Nuxt UI 使用说明
- 更新技术栈描述
- 更新组件使用示例
- 添加深色模式使用说明
- 添加 Nuxt UI 配置说明
- 删除 TINYVUE_ISSUE.md 问题文档

## Nuxt UI 核心组件使用

### 按钮 (UButton)
```vue
<UButton>默认按钮</UButton>
<UButton color="primary">主要按钮</UButton>
<UButton icon="i-heroicons-star">带图标</UButton>
```

### 卡片 (UCard)
```vue
<UCard>
  <template #header>标题</template>
  内容
</UCard>
```

### 输入框 (UInput)
```vue
<UInput v-model="value" placeholder="请输入" />
```

### 徽章 (UBadge)
```vue
<UBadge color="green">已启用</UBadge>
```

### 头像 (UAvatar)
```vue
<UAvatar icon="i-heroicons-user" />
```

### 图标 (UIcon)
```vue
<UIcon name="i-heroicons-home" />
```

## 深色模式实现
使用 `useColorMode()` 切换主题：
```typescript
const colorMode = useColorMode()
colorMode.preference = 'dark' // 或 'light' 或 'system'
```

## 测试结果
- ✅ 所有页面正常显示
- ✅ 组件功能正常
- ✅ 深色模式切换正常
- ✅ 响应式布局正常
- ✅ 开发服务器启动无错误
- ✅ 类型检查通过

## 后续优化建议
1. 进一步优化主题定制
2. 添加更多 Nuxt UI 组件的使用
3. 实现主题持久化（localStorage）
4. 添加单元测试
5. 优化性能（代码分割、懒加载）

## 参考资料
- [Nuxt UI 官方文档](https://ui.nuxt.com/)
- [Tailwind CSS 文档](https://tailwindcss.com/docs)
- [Heroicons 图标库](https://heroicons.com/)
