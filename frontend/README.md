# Agent Skills Frontend

基于 Vue 3 的智能多技能编排系统前端界面

## 设计特点

### 🎨 视觉设计

#### 配色方案
- **主色调**: 紫色渐变 `#667eea → #764ba2`
- **背景**: 135° 线性渐变
- **卡片背景**: 纯白色 `#ffffff`
- **主按钮**: 白色背景,紫色文字
- **次要按钮**: 半透明白色 `rgba(255, 255, 255, 0.2)`

#### 字体系统
- **字体族**: `-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif`
- **标题**: 700 加粗, 3rem 大小
- **副标题**: 1.25rem, 透明度 0.9
- **正文**: 1.125rem, 行高 1.6

### 📐 布局设计

#### 首页布局
```
┌─────────────────────────────────┐
│      Header (标题区)            │
│  Agent Skills System             │
│  智能多技能编排系统              │
├─────────────────────────────────┤
│                                 │
│      Hero (主视觉区)            │
│  欢迎使用智能知识问答系统        │
│  [开始对话] [查看技能]          │
│                                 │
├─────────────────────────────────┤
│  ┌──────┐ ┌──────┐ ┌──────┐  │
│  │智能  │ │知识  │ │数据  │  │
│  │对话  │ │问答  │ │分析  │  │
│  └──────┘ └──────┘ └──────┘  │
│  ┌──────┐                       │
│  │数据  │                       │
│  │可视化│                       │
│  └──────┘                       │
└─────────────────────────────────┘
```

#### 响应式网格
- **网格布局**: `grid-template-columns: repeat(auto-fit, minmax(250px, 1fr))`
- **卡片间距**: 2rem
- **最小宽度**: 250px
- **自适应**: 根据屏幕宽度自动调整列数

### ✨ 交互设计

#### 按钮样式
```css
.btn-primary {
  background: white;
  color: #667eea;
  border-radius: 0.5rem;
  padding: 0.875rem 2rem;
  transition: all 0.2s;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}
```

#### 卡片悬停效果
```css
.feature-card {
  background: white;
  border-radius: 1rem;
  padding: 2rem;
  transition: transform 0.2s;
}

.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}
```

#### 动画细节
- **按钮悬停**: 向上平移 2px,添加阴影
- **卡片悬停**: 向上平移 4px,增强阴影
- **过渡时间**: 0.2s 快速响应

### 🎯 设计原则

1. **视觉层次**
   - 清晰的标题层级
   - 合理的留白间距
   - 突出主要操作按钮

2. **色彩运用**
   - 渐变背景营造现代感
   - 白色卡片突出内容
   - 紫色主题贯穿整体

3. **用户体验**
   - 直观的功能入口
   - 清晰的视觉反馈
   - 流畅的交互动画

4. **响应式设计**
   - 自适应网格布局
   - 移动端友好
   - 不同屏幕优化

## 页面结构

### 首页 (`Home.vue`)

#### 组件结构
```vue
<template>
  <div class="home">
    <header class="header">
      <h1 class="title">Agent Skills System</h1>
      <p class="subtitle">智能多技能编排系统</p>
    </header>

    <main class="main">
      <div class="hero">
        <h2>欢迎使用智能知识问答系统</h2>
        <p class="description">...</p>
        <div class="actions">
          <button class="btn btn-primary">开始对话</button>
          <button class="btn btn-secondary">查看技能</button>
        </div>
      </div>

      <div class="features">
        <div class="feature-card">...</div>
      </div>
    </main>
  </div>
</template>
```

#### 功能卡片
1. 💬 **智能对话** - 支持多轮对话,自动识别意图和提取参数
2. 🔍 **知识问答** - 基于 RAG 技术的文档检索和智能回答
3. 📊 **数据分析** - 支持 CSV/Excel 数据处理和统计分析
4. 📈 **数据可视化** - 将数据分析结果生成直观图表

## 技术栈

- **框架**: Vue 3 (Composition API)
- **构建工具**: Vite
- **路由**: Vue Router 4
- **状态管理**: Pinia
- **HTTP 客户端**: Axios
- **工具库**: @vueuse/core

## 开发指南

### 安装依赖
```bash
npm install
```

### 启动开发服务器
```bash
npm run dev
```

### 构建生产版本
```bash
npm run build
```

### 预览生产构建
```bash
npm run preview
```

## 项目结构

```
frontend/
├── src/
│   ├── assets/
│   │   └── styles/
│   │       └── main.css          # 全局样式
│   ├── components/              # 公共组件
│   ├── router/
│   │   └── index.js             # 路由配置
│   ├── stores/                  # Pinia 状态管理
│   ├── views/
│   │   ├── Home.vue             # 首页
│   │   ├── Chat.vue             # 聊天页
│   │   └── Skills.vue           # 技能列表
│   ├── App.vue                  # 根组件
│   └── main.js                  # 入口文件
├── public/                      # 静态资源
├── index.html                   # HTML 模板
├── package.json
├── vite.config.js               # Vite 配置
└── README.md
```

## 样式规范

### CSS 变量
```css
:root {
  /* 主色调 */
  --primary-color: #667eea;
  --secondary-color: #764ba2;
  
  /* 渐变 */
  --gradient-bg: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  
  /* 文字颜色 */
  --text-primary: #333;
  --text-secondary: #666;
  --text-white: #ffffff;
}
```

### 响应式断点
```css
@media (max-width: 768px) {
  /* 移动端样式 */
}

@media (max-width: 1024px) {
  /* 平板样式 */
}
```

## 浏览器支持

- Chrome (最新版)
- Firefox (最新版)
- Safari (最新版)
- Edge (最新版)

## 未来扩展

- [ ] 深色模式
- [ ] 国际化支持
- [ ] 主题切换
- [ ] 更多页面动画
- [ ] WebSocket 实时通信
- [ ] 图表组件集成

## 许可证

MIT License
