// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2024-11-01',
  devtools: { enabled: true },

  app: {
    head: {
      title: 'Agent Skills System',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { name: 'description', content: '智能多技能编排系统' },
        { name: 'keywords', content: 'Agent Skills, AI, Nuxt 3, Vue 3' }
      ],
      link: [
        { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' }
      ]
    },
    pageTransition: false,
    layoutTransition: false
  },

  css: ['~/assets/css/main.css'],

  modules: ['@nuxt/ui'],

  vite: {
    css: {
      preprocessorOptions: {
        scss: {
          additionalData: `@use "~/assets/css/variables.scss" as *;`
        }
      }
    }
  },

  typescript: {
    strict: true,
    typeCheck: false
  }
})
