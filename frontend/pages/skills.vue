<script setup lang="ts">
useHead({
  title: '技能列表 - Agent Skills System'
})

// 加载状态
const loading = ref(true)
const error = ref<string | null>(null)

// 技能列表
const skills = ref<any[]>([])

// 技能图标映射
const skillIconMap: Record<string, string> = {
  '智能对话': 'i-heroicons-chat-bubble-left',
  '知识问答': 'i-heroicons-magnifying-glass',
  '数据分析': 'i-heroicons-chart-bar',
  '数据可视化': 'i-heroicons-chart-pie',
  'default': 'i-heroicons-cube'
}

// 获取技能图标
const getSkillIcon = (name: string) => {
  return skillIconMap[name] || skillIconMap.default
}

// 获取技能列表
const fetchSkills = async () => {
  loading.value = true
  error.value = null

  try {
    const response = await api.getSkills()
    skills.value = response.skills.map(skill => ({
      ...skill,
      icon: getSkillIcon(skill.name),
      status: 'active'
    }))
  } catch (err: any) {
    console.error('获取技能列表失败:', err)
    error.value = err.message || '获取技能列表失败'
  } finally {
    loading.value = false
  }
}

// 页面加载时获取数据
onMounted(() => {
  fetchSkills()
})
</script>

<template>
  <NuxtLayout name="default">
    <div class="skills">
      <UContainer>
        <h1 class="title">技能列表</h1>
        <p class="subtitle">查看和管理所有可用的 AI 技能</p>

        <!-- 加载状态 -->
        <div v-if="loading" class="loading-container">
          <UIcon name="i-heroicons-arrow-path" class="loading-icon" />
          <p>加载中...</p>
        </div>

        <!-- 错误状态 -->
        <div v-else-if="error" class="error-container">
          <UIcon name="i-heroicons-exclamation-triangle" class="error-icon" />
          <p>{{ error }}</p>
          <UButton @click="fetchSkills" icon="i-heroicons-arrow-clockwise">重试</UButton>
        </div>

        <!-- 技能列表 -->
        <div v-else class="skills-grid">
          <UCard v-for="skill in skills" :key="skill.name">
            <div class="skill-card">
              <UIcon :name="skill.icon" class="skill-icon" />
              <div class="skill-info">
                <h3>{{ skill.name }}</h3>
                <p>{{ skill.description }}</p>
                <div v-if="skill.category" class="skill-tags">
                  <UBadge size="sm" color="purple" variant="subtle">{{ skill.category }}</UBadge>
                  <UBadge
                    v-for="tag in skill.tags"
                    :key="tag"
                    size="sm"
                    color="gray"
                    variant="subtle"
                  >
                    {{ tag }}
                  </UBadge>
                </div>
              </div>
              <UBadge :color="skill.status === 'active' ? 'green' : 'red'" variant="subtle">
                {{ skill.status === 'active' ? '已启用' : '已禁用' }}
              </UBadge>
            </div>
          </UCard>

          <!-- 空状态 -->
          <div v-if="skills.length === 0" class="empty-container">
            <UIcon name="i-heroicons-inbox" class="empty-icon" />
            <p>暂无技能</p>
          </div>
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

.loading-container,
.error-container,
.empty-container {
  text-align: center;
  padding: 4rem 2rem;
  color: white;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.loading-icon {
  font-size: 3rem;
  animation: spin 1s linear infinite;
}

.error-icon,
.empty-icon {
  font-size: 3rem;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
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
  margin-bottom: 0.75rem;
}

.skill-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
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
