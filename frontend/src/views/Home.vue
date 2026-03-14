<template>
  <div class="home">
    <header class="header">
      <h1 class="title">Agent Skills System</h1>
      <p class="subtitle">智能多技能编排系统</p>
    </header>

    <main class="main">
      <div class="hero">
        <h2>欢迎使用智能知识问答系统</h2>
        <p class="description">
          基于 AI 的多技能编排系统，支持知识问答、数据分析和可视化等功能
        </p>
        <div class="actions">
          <button class="btn btn-primary" @click="goToChat">
            开始对话
          </button>
          <button class="btn btn-secondary" @click="goToSkills">
            查看技能
          </button>
        </div>
      </div>

      <div class="features">
        <div class="feature-card">
          <div class="feature-icon">💬</div>
          <h3>智能对话</h3>
          <p>支持多轮对话，自动识别意图和提取参数</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">🔍</div>
          <h3>知识问答</h3>
          <p>基于 RAG 技术的文档检索和智能回答</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">📊</div>
          <h3>数据分析</h3>
          <p>支持 CSV/Excel 数据处理和统计分析</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">📈</div>
          <h3>数据可视化</h3>
          <p>将数据分析结果生成直观图表</p>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const goToChat = () => {
  router.push('/chat')
}

const goToSkills = () => {
  router.push('/skills')
}
</script>

<style scoped>
.home {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  flex-direction: column;
}

.header {
  text-align: center;
  padding: 4rem 2rem;
  color: white;
}

.title {
  font-size: 3rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.subtitle {
  font-size: 1.25rem;
  opacity: 0.9;
}

.main {
  flex: 1;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
  padding: 2rem;
}

.hero {
  text-align: center;
  color: white;
  margin-bottom: 4rem;
}

.hero h2 {
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

.description {
  font-size: 1.125rem;
  opacity: 0.9;
  max-width: 600px;
  margin: 0 auto 2rem;
}

.actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.btn {
  padding: 0.875rem 2rem;
  border-radius: 0.5rem;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.btn-primary {
  background: white;
  color: #667eea;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 2px solid rgba(255, 255, 255, 0.3);
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.3);
}

.features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
}

.feature-card {
  background: white;
  padding: 2rem;
  border-radius: 1rem;
  text-align: center;
  transition: transform 0.2s;
}

.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.feature-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.feature-card h3 {
  font-size: 1.25rem;
  margin-bottom: 0.5rem;
  color: #333;
}

.feature-card p {
  color: #666;
  line-height: 1.6;
}
</style>
