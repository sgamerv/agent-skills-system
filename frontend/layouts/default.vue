<script setup lang="ts">
const route = useRoute()

// @ts-ignore - Nuxt UI 的 useColorMode 在运行时可用
const colorMode = useColorMode()
</script>

<template>
  <div class="layout">
    <!-- Navigation -->
    <nav class="nav">
      <div class="nav-container">
        <NuxtLink to="/" class="logo">
          Agent Skills
        </NuxtLink>

        <div class="nav-links">
          <NuxtLink to="/" :class="{ active: route.path === '/' }">
            首页
          </NuxtLink>
          <NuxtLink to="/chat" :class="{ active: route.path === '/chat' }">
            智能对话
          </NuxtLink>
          <NuxtLink to="/skills" :class="{ active: route.path === '/skills' }">
            技能列表
          </NuxtLink>
          <UButton
            :icon="colorMode.value === 'dark' ? 'i-heroicons-moon-20-solid' : 'i-heroicons-sun-20-solid'"
            color="gray"
            variant="ghost"
            size="lg"
            @click="colorMode.preference = colorMode.value === 'dark' ? 'light' : 'dark'"
          />
        </div>
      </div>
    </nav>

    <!-- Page Content -->
    <slot />
  </div>
</template>

<style scoped>
.layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.nav {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 1000;
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  font-size: 1.5rem;
  font-weight: 700;
  color: rgb(var(--color-primary-500));
  text-decoration: none;
  transition: color 0.2s;
}

.logo:hover {
  color: rgb(var(--color-primary-600));
}

.nav-links {
  display: flex;
  gap: 2rem;
  align-items: center;
}

.nav-links a {
  text-decoration: none;
  color: rgb(var(--color-gray-700));
  font-weight: 500;
  transition: all 0.2s;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
}

.nav-links a:hover {
  color: rgb(var(--color-primary-500));
  background: rgba(102, 126, 234, 0.1);
}

.nav-links a.active {
  color: rgb(var(--color-primary-500));
  background: rgba(102, 126, 234, 0.15);
}

@media (max-width: 768px) {
  .nav-container {
    flex-direction: column;
    gap: 1rem;
  }

  .nav-links {
    gap: 1rem;
    width: 100%;
    justify-content: center;
  }
}
</style>
