<template>
  <div class="skills">
    <header class="header">
      <button class="back-btn" @click="goBack">←</button>
      <h1>技能列表</h1>
    </header>

    <main class="main">
      <div v-if="loading" class="loading">
        加载中...
      </div>

      <div v-else-if="error" class="error">
        {{ error }}
      </div>

      <div v-else class="skills-grid">
        <div
          v-for="skill in skills"
          :key="skill.name"
          class="skill-card"
        >
          <div class="skill-header">
            <h2 class="skill-name">{{ skill.name }}</h2>
            <span class="skill-version">v{{ skill.version }}</span>
          </div>
          <p class="skill-description">{{ skill.description }}</p>
          <div class="skill-meta">
            <span class="skill-category">分类: {{ skill.category }}</span>
          </div>
          <div class="skill-tags">
            <span
              v-for="tag in skill.tags"
              :key="tag"
              class="tag"
            >
              {{ tag }}
            </span>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const skills = ref([])
const loading = ref(true)
const error = ref(null)

const goBack = () => {
  router.push('/')
}

const loadSkills = async () => {
  loading.value = true
  error.value = null

  try {
    // TODO: 实际调用后端 API
    // const response = await fetch('/api/skills')
    // const data = await response.json()
    // skills.value = data.skills

    // 模拟数据
    await new Promise(resolve => setTimeout(resolve, 500))
    skills.value = [
      {
        name: 'visualization',
        description: '数据可视化技能，将数据分析结果生成图表',
        category: 'visualization',
        tags: ['chart', 'plot', 'graph'],
        version: '1.0.0'
      },
      {
        name: 'data-analysis',
        description: '数据分析技能，支持 CSV/Excel 数据处理和统计分析',
        category: 'analysis',
        tags: ['data', 'analysis', 'statistics'],
        version: '1.0.0'
      },
      {
        name: 'knowledge-qa',
        description: '专业知识问答技能，支持基于 RAG 的文档检索和智能回答',
        category: 'knowledge',
        tags: ['qa', 'rag', 'search'],
        version: '1.0.0'
      }
    ]
  } catch (e) {
    error.value = '加载技能列表失败: ' + e.message
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadSkills()
})
</script>

<style scoped>
.skills {
  min-height: 100vh;
  background: #f5f5f5;
}

.header {
  background: white;
  padding: 1rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.back-btn {
  font-size: 1.5rem;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.5rem;
}

.header h1 {
  font-size: 1.5rem;
  margin: 0;
}

.main {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.loading,
.error {
  text-align: center;
  padding: 3rem;
  font-size: 1.125rem;
}

.error {
  color: #ef4444;
}

.skills-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.skill-card {
  background: white;
  border-radius: 0.75rem;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  transition: transform 0.2s, box-shadow 0.2s;
}

.skill-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.skill-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.skill-name {
  font-size: 1.25rem;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.skill-version {
  font-size: 0.875rem;
  color: #999;
  padding: 0.25rem 0.5rem;
  background: #f0f0f0;
  border-radius: 0.25rem;
}

.skill-description {
  color: #666;
  line-height: 1.6;
  margin-bottom: 1rem;
}

.skill-meta {
  margin-bottom: 0.75rem;
}

.skill-category {
  font-size: 0.875rem;
  color: #999;
}

.skill-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.tag {
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
  background: #667eea;
  color: white;
  border-radius: 0.25rem;
}
</style>
