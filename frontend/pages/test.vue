<script setup lang="ts">
useHead({
  title: '测试 - Agent Skills System'
})
</script>

<template>
  <div class="test">
    <h1>Nuxt UI 组件测试</h1>

    <div class="section">
      <h2>按钮测试</h2>
      <UButton>默认按钮</UButton>
      <UButton color="primary">主要按钮</UButton>
      <UButton color="green">绿色按钮</UButton>
    </div>

    <div class="section">
      <h2>卡片测试</h2>
      <UCard>
        <template #header>
          卡片标题
        </template>
        <p>这是卡片内容</p>
      </UCard>
    </div>

    <div class="section">
      <h2>徽章测试</h2>
      <UBadge>默认</UBadge>
      <UBadge color="green">绿色</UBadge>
      <UBadge color="red">红色</UBadge>
    </div>
  </div>
</template>

<style scoped>
.test {
  padding: 2rem;
  max-width: 800px;
  margin: 0 auto;
}

.section {
  margin: 2rem 0;
}

h1 {
  font-size: 2rem;
  margin-bottom: 1rem;
}

h2 {
  font-size: 1.5rem;
  margin-bottom: 1rem;
}

.section > :deep(*) {
  margin-right: 1rem;
}
</style>
