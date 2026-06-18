<template>
  <div class="login-wrap">
    <el-card class="login-card" shadow="always">
      <div class="login-header">
        <div class="logo">A</div>
        <h2>Asagent 控制台</h2>
        <p class="sub">智能体平台管理后台</p>
      </div>
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-position="top"
        @submit.prevent="onSubmit"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名" autocomplete="username" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            show-password
            autocomplete="current-password"
            @keyup.enter="onSubmit"
          />
        </el-form-item>
        <el-button
          type="primary"
          class="login-btn"
          :loading="loading"
          @click="onSubmit"
        >
          登录
        </el-button>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { authApi } from '../api'
import { useAuthStore } from '../stores/auth'

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
    const redirect = route.query.redirect || '/chat'
    router.push(redirect)
  } catch (e) {
    // handled by interceptor
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-wrap {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #409eff 0%, #1f6fd0 100%);
}
.login-card {
  width: 380px;
  border-radius: 12px;
}
.login-header {
  text-align: center;
  margin-bottom: 18px;
}
.logo {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  background: #409eff;
  color: #fff;
  font-size: 30px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 10px;
}
.login-header h2 {
  margin: 0 0 4px;
}
.sub {
  margin: 0;
  color: #909399;
  font-size: 13px;
}
.login-btn {
  width: 100%;
}
</style>
