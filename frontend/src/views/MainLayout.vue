<template>
  <el-container class="layout">
    <el-aside width="220px" class="aside">
      <div class="brand">
        <div class="logo">A</div>
        <span class="brand-name">Asagent</span>
      </div>
      <el-menu
        :default-active="activeMenu"
        router
        class="menu"
        background-color="#1f2933"
        text-color="#cfd6dd"
        active-text-color="#ffffff"
      >
        <el-menu-item index="/chat">
          <el-icon><ChatDotRound /></el-icon>
          <span>对话</span>
        </el-menu-item>
        <el-menu-item index="/agents">
          <el-icon><User /></el-icon>
          <span>Agent</span>
        </el-menu-item>
        <el-menu-item index="/datasources">
          <el-icon><Coin /></el-icon>
          <span>数据源</span>
        </el-menu-item>
        <el-menu-item index="/llm">
          <el-icon><Cpu /></el-icon>
          <span>LLM 配置</span>
        </el-menu-item>
        <el-menu-item index="/skills">
          <el-icon><Files /></el-icon>
          <span>Skills</span>
        </el-menu-item>
        <el-menu-item index="/apikeys">
          <el-icon><Key /></el-icon>
          <span>API Key</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="header">
        <div class="page-title">{{ currentTitle }}</div>
        <div class="header-right">
          <el-tag v-if="auth.isAdmin" type="warning" size="small" effect="plain">管理员</el-tag>
          <el-dropdown @command="onCommand">
            <span class="user-trigger">
              <el-icon><UserFilled /></el-icon>
              <span class="uname">{{ auth.isAdmin ? 'admin' : 'user' }}</span>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const activeMenu = computed(() => route.path)
const currentTitle = computed(() => route.meta.title || '控制台')

function onCommand(cmd) {
  if (cmd === 'logout') {
    auth.logout()
    router.push({ name: 'login' })
  }
}
</script>

<style scoped>
.layout {
  height: 100vh;
}
.aside {
  background: #1f2933;
  color: #fff;
  overflow: hidden;
}
.brand {
  height: 60px;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0 18px;
  color: #fff;
  font-size: 18px;
  font-weight: 700;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}
.logo {
  width: 30px;
  height: 30px;
  border-radius: 8px;
  background: #409eff;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
}
.menu {
  border-right: none;
}
.header {
  background: #fff;
  border-bottom: 1px solid #ebeef5;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}
.page-title {
  font-size: 16px;
  font-weight: 600;
}
.header-right {
  display: flex;
  align-items: center;
  gap: 14px;
}
.user-trigger {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  outline: none;
}
.uname {
  font-size: 14px;
}
.main {
  padding: 16px;
  background: var(--asagent-bg);
  overflow: auto;
}
</style>
