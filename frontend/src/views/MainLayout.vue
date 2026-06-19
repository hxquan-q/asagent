<template>
  <div class="shell">
    <!-- icon rail -->
    <nav class="rail" :class="{ collapsed: ui.railCollapsed }">
      <router-link to="/chat" class="brand" title="Asagent">
        <span class="brand-mark">A</span>
      </router-link>

      <div class="rail-nav">
        <router-link
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="rail-item"
          :class="{ active: isActive(item) }"
          :title="item.label"
        >
          <AppIcon :name="item.icon" :size="20" />
          <span class="rail-label">{{ item.label }}</span>
        </router-link>
      </div>

      <div class="rail-foot">
        <button class="rail-item icon-btn" title="切换主题" @click="ui.toggleTheme()">
          <AppIcon :name="ui.theme === 'dark' ? 'sun' : 'moon'" :size="20" />
          <span class="rail-label">{{ ui.theme === 'dark' ? '浅色' : '深色' }}</span>
        </button>

        <el-dropdown placement="top-start" trigger="click" @command="onUserCmd">
          <div class="rail-item avatar-item" title="账户">
            <span class="avatar">{{ initial }}</span>
            <span class="rail-label">{{ auth.isAdmin ? 'admin' : 'user' }}</span>
          </div>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item disabled>
                <span class="mono" style="font-size: 12px">{{ auth.isAdmin ? 'admin' : 'user' }}</span>
              </el-dropdown-item>
              <el-dropdown-item divided command="logout">
                <AppIcon name="logout" :size="15" />&nbsp;退出登录
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </nav>

    <!-- main column -->
    <div class="main-col">
      <header class="topbar">
        <div class="topbar-left">
          <span class="topbar-eyebrow mono">{{ sectionLabel }}</span>
          <h1 class="topbar-title">{{ pageTitle }}</h1>
        </div>
        <div class="topbar-right">
          <el-tag
            v-if="auth.isAdmin"
            type="warning"
            effect="dark"
            size="small"
            round
            class="admin-chip"
          >
            <AppIcon name="key" :size="12" />&nbsp;管理员
          </el-tag>
          <router-link to="/chat" class="ghost-btn">
            <AppIcon name="chat" :size="16" />&nbsp;进入工作台
          </router-link>
        </div>
      </header>

      <main class="content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useUiStore } from '../stores/ui'
import AppIcon from '../components/AppIcon.vue'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const ui = useUiStore()

const allNav = [
  { path: '/dashboard', label: '概览', icon: 'grid', section: '总览' },
  { path: '/chat', label: '工作台', icon: 'chat', section: '对话', public: true },
  { path: '/agents', label: '智能体', icon: 'robot', section: '配置' },
  { path: '/datasources', label: '数据源', icon: 'database', section: '配置' },
  { path: '/llm', label: 'LLM 配置', icon: 'cpu', section: '配置' },
  { path: '/skills', label: '技能', icon: 'sparkles', section: '配置' },
  { path: '/apikeys', label: 'API Key', icon: 'key', section: '配置' }
]

const navItems = computed(() => allNav.filter((i) => i.public || auth.isAdmin))

const activePath = computed(() => {
  const top = '/' + (route.path.split('/')[1] || 'chat')
  return top
})
const isActive = (item) => '/' + item.path.split('/')[1] === activePath.value

const current = computed(() => allNav.find((i) => isActive(i)))
const pageTitle = computed(() => route.meta.title || current.value?.label || 'Asagent')
const sectionLabel = computed(() => current.value?.section || 'Asagent')

const initial = computed(() => (auth.isAdmin ? 'A' : 'U'))

function onUserCmd(cmd) {
  if (cmd === 'logout') {
    auth.logout()
    router.push({ name: 'login' })
  }
}
</script>

<style scoped>
.shell {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

/* ---------- icon rail ---------- */
.rail {
  width: 64px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  align-items: stretch;
  background: var(--surface);
  border-right: 1px solid var(--border);
  padding: 12px 0 10px;
  z-index: 10;
}
.brand {
  display: flex;
  justify-content: center;
  margin-bottom: 14px;
}
.brand-mark {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--font-display);
  font-weight: 700;
  font-size: 18px;
  color: #06281c;
  background: linear-gradient(140deg, var(--primary-strong), var(--primary));
  box-shadow: 0 6px 16px var(--primary-soft);
}
.rail-nav {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 0 8px;
  flex: 1;
}
.rail-foot {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 8px;
}
.rail-item {
  position: relative;
  width: 48px;
  height: 48px;
  border-radius: var(--r-md);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
  cursor: pointer;
  border: none;
  background: transparent;
  transition: all var(--dur) var(--ease);
}
.rail-item:hover {
  background: var(--surface-2);
  color: var(--text);
}
.rail-item.active {
  color: var(--primary-strong);
  background: var(--primary-soft);
}
.rail-item.active::before {
  content: '';
  position: absolute;
  left: -8px;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 20px;
  border-radius: 0 3px 3px 0;
  background: var(--primary);
}
.rail-label {
  display: none;
}
.avatar-item {
  background: var(--surface-2);
}
.avatar {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: var(--accent);
  color: #2a1c05;
  font-weight: 700;
  font-size: 13px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.icon-btn {
  font-family: inherit;
}

/* ---------- main column ---------- */
.main-col {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  background: var(--bg);
}
.topbar {
  height: 60px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  border-bottom: 1px solid var(--border);
  background: color-mix(in srgb, var(--surface) 72%, transparent);
  backdrop-filter: blur(10px);
}
.topbar-left {
  display: flex;
  flex-direction: column;
  gap: 1px;
}
.topbar-eyebrow {
  font-size: 10px;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--text-faint);
}
.topbar-title {
  margin: 0;
  font-size: var(--fs-lg);
  font-weight: 600;
}
.topbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
}
.admin-chip {
  display: inline-flex;
  align-items: center;
}
.ghost-btn {
  display: inline-flex;
  align-items: center;
  padding: 7px 13px;
  border-radius: var(--r-sm);
  border: 1px solid var(--border-strong);
  color: var(--text);
  font-size: var(--fs-sm);
  font-weight: 500;
  transition: all var(--dur) var(--ease);
}
.ghost-btn:hover {
  border-color: var(--primary-line);
  color: var(--primary-strong);
  text-decoration: none;
  background: var(--primary-soft);
}
.content {
  flex: 1;
  min-height: 0;
  overflow: auto;
}

/* responsive: collapse rail on tablets, hide on phones */
@media (max-width: 900px) {
  .rail {
    width: 52px;
  }
  .rail-item {
    width: 40px;
    height: 40px;
  }
  .topbar-eyebrow {
    display: none;
  }
}
@media (max-width: 600px) {
  .rail {
    display: none;
  }
  .topbar {
    padding: 0 14px;
  }
}
</style>
