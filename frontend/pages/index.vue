<script setup lang="ts">
useHead({
  title: '首页 - Agent Skills System'
})
</script>

<template>
  <div class="home">
    <!-- Header -->
    <header class="header">
      <h1 class="title">Agent Skills System</h1>
      <p class="subtitle">智能多技能编排系统</p>
    </header>

    <!-- Hero Section -->
    <main class="main">
      <div class="hero">
        <h2>欢迎使用智能知识问答系统</h2>
        <p class="description">
          强大的 AI 驱动平台，集成智能对话、知识问答、数据分析和可视化功能
        </p>
        <div class="actions">
          <ClientOnly>
            <UButton
              to="/chat"
              size="xl"
              icon="i-heroicons-chat-bubble-left-right"
              class="btn-primary"
            >
              开始对话
            </UButton>
            <UButton
              to="/skills"
              size="xl"
              class="btn-secondary"
              icon="i-heroicons-squares-2x2"
            >
              查看技能
            </UButton>
          </ClientOnly>
        </div>
      </div>

      <!-- Features -->
      <ClientOnly>
        <div class="features">
          <UCard class="feature-card">
            <div class="icon-wrapper">
              <UIcon name="i-heroicons-chat-bubble-left" class="icon" />
            </div>
            <h3>智能对话</h3>
            <p>支持多轮对话，自动识别意图和提取参数</p>
          </UCard>

          <UCard class="feature-card">
            <div class="icon-wrapper">
              <UIcon name="i-heroicons-magnifying-glass" class="icon" />
            </div>
            <h3>知识问答</h3>
            <p>基于 RAG 技术的文档检索和智能回答</p>
          </UCard>

          <UCard class="feature-card">
            <div class="icon-wrapper">
              <UIcon name="i-heroicons-chart-bar" class="icon" />
            </div>
            <h3>数据分析</h3>
            <p>支持 CSV/Excel 数据处理和统计分析</p>
          </UCard>

          <UCard class="feature-card">
            <div class="icon-wrapper">
              <UIcon name="i-heroicons-chart-pie" class="icon" />
            </div>
            <h3>数据可视化</h3>
            <p>将数据分析结果生成直观图表</p>
          </UCard>
        </div>
      </ClientOnly>
    </main>
  </div>
</template>

<style scoped>
.home {
  min-height: 100vh;
  padding: 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.header {
  text-align: center;
  color: white;
  padding: 3rem 0;
}

.title {
  font-size: 3.5rem;
  font-weight: 800;
  margin-bottom: 0.5rem;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  background: linear-gradient(135deg, #ffffff 0%, #f0f0f0 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.subtitle {
  font-size: 1.5rem;
  opacity: 0.95;
  font-weight: 300;
  color: rgba(255, 255, 255, 0.9);
}

.main {
  max-width: 1200px;
  margin: 0 auto;
}

.hero {
  text-align: center;
  padding: 4rem 2rem 5rem;
}

.hero h2 {
  font-size: 2.5rem;
  color: white;
  margin-bottom: 1.5rem;
  font-weight: 700;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.description {
  font-size: 1.125rem;
  color: rgba(255, 255, 255, 0.9);
  line-height: 1.8;
  max-width: 650px;
  margin: 0 auto 3rem;
  font-weight: 400;
}

.actions {
  display: flex;
  gap: 1.5rem;
  justify-content: center;
  flex-wrap: wrap;
}

.btn-primary {
  background: #ffffff !important;
  color: #667eea !important;
  font-weight: 600;
  border: 2px solid #ffffff;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transition: all 0.3s ease;
}

.btn-primary:hover {
  background: #f0f0f0 !important;
  border-color: #f0f0f0;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
}

.btn-secondary {
  background: transparent !important;
  color: #ffffff !important;
  font-weight: 600;
  border: 2px solid rgba(255, 255, 255, 0.8);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.15) !important;
  border-color: rgba(255, 255, 255, 1);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 1.5rem;
  padding: 2rem 0 4rem;
}

.feature-card {
  text-align: center;
  padding: 2rem 1.5rem;
  background: white;
  border-radius: 1rem;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  height: 100%;
  border: 1px solid rgba(255, 255, 255, 0.8);
}

.feature-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 10px 30px rgba(102, 126, 234, 0.2);
}

.icon-wrapper {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 64px;
  height: 64px;
  margin-bottom: 1rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 1rem;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.icon {
  font-size: 2.5rem;
  color: white;
}

.feature-card h3 {
  font-size: 1.25rem;
  margin-bottom: 0.75rem;
  color: #1a1a2e;
  font-weight: 600;
}

.feature-card p {
  color: #4a4a68;
  line-height: 1.6;
  font-size: 0.9375rem;
  opacity: 0.8;
}

@media (max-width: 768px) {
  .title {
    font-size: 2.25rem;
  }

  .subtitle {
    font-size: 1.25rem;
  }

  .hero h2 {
    font-size: 1.75rem;
  }

  .description {
    font-size: 1rem;
  }

  .features {
    grid-template-columns: 1fr;
  }

  .actions {
    flex-direction: column;
    align-items: center;
  }
}
</style>
