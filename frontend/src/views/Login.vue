<template>
  <div class="login">
    <div class="login-art" aria-hidden="true">
      <div class="orb orb-a"></div>
      <div class="orb orb-b"></div>
      <div class="grid-lines"></div>
    </div>

    <div class="login-card">
      <div class="lc-brand">
        <span class="brand-mark">A</span>
        <span class="brand-name">Asagent</span>
      </div>
      <h1 class="lc-title">智能体工作台</h1>
      <p class="lc-sub">登录以管理智能体、数据源与对话</p>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-position="top"
        class="lc-form"
        @submit.prevent="onSubmit"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名" size="large" autocomplete="username">
            <template #prefix><AppIcon name="user" :size="16" /></template>
          </el-input>
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            size="large"
            show-password
            autocomplete="current-password"
            @keyup.enter="onSubmit"
          >
            <template #prefix><AppIcon name="key" :size="16" /></template>
          </el-input>
        </el-form-item>
        <el-button
          type="primary"
          size="large"
          class="lc-btn"
          :loading="loading"
          @click="onSubmit"
        >
          登录
        </el-button>
      </el-form>

      <div class="lc-foot">
        <span class="mono">v0.2 · Graphite</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { authApi } from '../api'
import { useAuthStore } from '../stores/auth'
import AppIcon from '../components/AppIcon.vue'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

const formRef = ref(null)
const loading = ref(false)
const form = reactive({
  username: 'admin',
  password: 'admin123'
})
const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

async function onSubmit() {
  if (!formRef.value) return
  try {
    await formRef.value.validate()
  } catch (e) {
    return
  }
  loading.value = true
  try {
    const data = await authApi.login(form.username, form.password)
    auth.setAuth(data.access_token, data.is_admin)
    ElMessage.success('登录成功')
    const redirect = route.query.redirect || '/dashboard'
    router.push(redirect)
  } catch (e) {
    /* handled by interceptor */
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login {
  position: relative;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background: var(--bg);
  overflow: hidden;
}
.login-art {
  position: absolute;
  inset: 0;
  pointer-events: none;
}
.orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(70px);
}
.orb-a {
  width: 460px;
  height: 460px;
  top: -140px;
  right: -120px;
  background: radial-gradient(circle, var(--primary) 0%, transparent 70%);
  opacity: 0.22;
}
.orb-b {
  width: 420px;
  height: 420px;
  bottom: -160px;
  left: -120px;
  background: radial-gradient(circle, var(--accent) 0%, transparent 70%);
  opacity: 0.18;
}
.grid-lines {
  position: absolute;
  inset: 0;
  background-image: linear-gradient(var(--border-faint) 1px, transparent 1px),
    linear-gradient(90deg, var(--border-faint) 1px, transparent 1px);
  background-size: 48px 48px;
  mask-image: radial-gradient(ellipse at center, black 30%, transparent 75%);
  opacity: 0.5;
}

.login-card {
  position: relative;
  z-index: 1;
  width: 400px;
  max-width: 100%;
  padding: 34px 34px 24px;
  border-radius: var(--r-xl);
  background: color-mix(in srgb, var(--surface) 92%, transparent);
  border: 1px solid var(--border-strong);
  backdrop-filter: blur(14px);
  box-shadow: var(--shadow-lg);
}
.lc-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 22px;
}
.brand-mark {
  width: 36px;
  height: 36px;
  border-radius: 11px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--font-display);
  font-weight: 700;
  font-size: 19px;
  color: #06281c;
  background: linear-gradient(140deg, var(--primary-strong), var(--primary));
  box-shadow: 0 6px 16px var(--primary-soft);
}
.brand-name {
  font-family: var(--font-display);
  font-weight: 700;
  font-size: var(--fs-xl);
  letter-spacing: -0.01em;
}
.lc-title {
  margin: 0 0 6px;
  font-size: var(--fs-2xl);
  font-weight: 600;
}
.lc-sub {
  margin: 0 0 26px;
  color: var(--text-muted);
  font-size: var(--fs-sm);
}
.lc-form :deep(.el-form-item__label) {
  font-size: var(--fs-xs);
  color: var(--text-muted);
  padding-bottom: 4px;
}
.lc-form :deep(.el-input__wrapper) {
  border-radius: var(--r-md) !important;
  padding: 4px 12px;
}
.lc-btn {
  width: 100%;
  margin-top: 6px;
  height: 44px;
  border-radius: var(--r-md) !important;
  font-weight: 600;
  font-size: var(--fs-base);
}
.lc-foot {
  margin-top: 22px;
  text-align: center;
  font-size: 11px;
  color: var(--text-faint);
}
</style>
