import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes = [
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/Login.vue'),
    meta: { public: true }
  },
  {
    path: '/',
    component: () => import('../views/MainLayout.vue'),
    redirect: '/chat',
    children: [
      { path: 'chat', name: 'chat', component: () => import('../views/Chat.vue'), meta: { title: '对话' } },
      { path: 'agents', name: 'agents', component: () => import('../views/Agents.vue'), meta: { title: 'Agent' } },
      { path: 'datasources', name: 'datasources', component: () => import('../views/Datasources.vue'), meta: { title: '数据源' } },
      { path: 'llm', name: 'llm', component: () => import('../views/LLMConfigs.vue'), meta: { title: 'LLM 配置' } },
      { path: 'skills', name: 'skills', component: () => import('../views/Skills.vue'), meta: { title: 'Skills' } },
      { path: 'apikeys', name: 'apikeys', component: () => import('../views/ApiKeys.vue'), meta: { title: 'API Key' } }
    ]
  },
  { path: '/:pathMatch(.*)*', redirect: '/' }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  auth.restore()
  if (!to.meta.public && !auth.token) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
  if (to.name === 'login' && auth.token) {
    return { name: 'chat' }
  }
})

export default router
