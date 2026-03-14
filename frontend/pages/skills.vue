<script setup lang="ts">
useHead({
  title: '技能列表 - Agent Skills System'
})

// 技能列表
const skills = ref([
  {
    name: '智能对话',
    description: '支持多轮对话，自动识别意图和提取参数',
    icon: 'i-heroicons-chat-bubble-left',
    status: 'active'
  },
  {
    name: '知识问答',
    description: '基于 RAG 技术的文档检索和智能回答',
    icon: 'i-heroicons-magnifying-glass',
    status: 'active'
  },
  {
    name: '数据分析',
    description: '支持 CSV/Excel 数据处理和统计分析',
    icon: 'i-heroicons-chart-bar',
    status: 'active'
  },
  {
    name: '数据可视化',
    description: '将数据分析结果生成直观图表',
    icon: 'i-heroicons-chart-pie',
    status: 'active'
  }
])
</script>

<template>
  <NuxtLayout name="default">
    <div class="skills">
      <UContainer>
        <h1 class="title">技能列表</h1>
        <p class="subtitle">查看和管理所有可用的 AI 技能</p>

        <div class="skills-grid">
          <UCard v-for="skill in skills" :key="skill.name">
            <div class="skill-card">
              <UIcon :name="skill.icon" class="skill-icon" />
              <div class="skill-info">
                <h3>{{ skill.name }}</h3>
                <p>{{ skill.description }}</p>
              </div>
              <UBadge :color="skill.status === 'active' ? 'green' : 'red'" variant="subtle">
                {{ skill.status === 'active' ? '已启用' : '已禁用' }}
              </UBadge>
            </div>
          </UCard>
        </div>
      </UContainer>
    </div>
  </NuxtLayout>
</template>

<style scoped>
.skills {
  min-height: 100vh;
  padding: 2rem;
  background: linear-gradient(135deg, rgb(var(--color-primary-500)) 0%, rgb(var(--color-purple-500)) 100%);
}

.title {
  font-size: 2.5rem;
  color: white;
  text-align: center;
  margin-bottom: 0.5rem;
  font-weight: 700;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.subtitle {
  text-align: center;
  opacity: 0.9;
  margin-bottom: 3rem;
  font-size: 1.125rem;
  font-weight: 300;
  color: rgba(255, 255, 255, 0.9);
}

.skills-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.skill-card {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.skill-icon {
  font-size: 2.5rem;
  flex-shrink: 0;
  color: rgb(var(--color-primary-500));
}

.skill-info {
  flex: 1;
}

.skill-info h3 {
  font-size: 1.25rem;
  margin-bottom: 0.5rem;
  color: #1a1a2e;
  font-weight: 600;
}

.skill-info p {
  opacity: 0.7;
  font-size: 0.875rem;
  line-height: 1.5;
  color: #4a4a68;
  font-weight: 400;
}

@media (max-width: 768px) {
  .title {
    font-size: 1.75rem;
  }

  .subtitle {
    font-size: 1rem;
  }

  .skills-grid {
    grid-template-columns: 1fr;
  }

  .skill-card {
    flex-direction: column;
    text-align: center;
  }
}
</style>
