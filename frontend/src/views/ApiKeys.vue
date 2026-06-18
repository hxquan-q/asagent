<template>
  <div class="page-card">
    <div class="toolbar">
      <h3 class="page-title">API Key 管理</h3>
      <el-button type="primary" @click="openCreate">新建 API Key</el-button>
    </div>

    <el-alert
      class="tip"
      title="完整密钥仅在创建时显示一次，请立即复制保存。"
      type="warning"
      :closable="false"
      show-icon
    />

    <el-table :data="list" v-loading="loading" border stripe style="margin-top: 12px">
      <el-table-column prop="name" label="名称" min-width="140" />
      <el-table-column prop="key_prefix" label="Key 前缀" min-width="120">
        <template #default="{ row }">
          <code>{{ row.key_prefix || row.prefix || '-' }}</code>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="180">
        <template #default="{ row }">{{ row.created_at || '-' }}</template>
      </el-table-column>
      <el-table-column prop="expires_at" label="过期时间" width="180">
        <template #default="{ row }">{{ row.expires_at || '永不过期' }}</template>
      </el-table-column>
      <el-table-column label="操作" width="120" fixed="right">
        <template #default="{ row }">
          <el-button text type="danger" @click="onRevoke(row)">吊销</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialog.visible" title="新建 API Key" width="480px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="名称" required>
          <el-input v-model="form.name" placeholder="便于识别的名称" />
        </el-form-item>
        <el-form-item label="过期时间">
          <el-date-picker
            v-model="form.expires_at"
            type="datetime"
            placeholder="留空表示永不过期"
            value-format="YYYY-MM-DDTHH:mm:ss"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog.visible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="onSave">创建</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="resultDialog.visible" title="API Key 已创建" width="560px">
      <el-alert
        title="请立即复制，关闭后将无法再次查看完整密钥。"
        type="warning"
        :closable="false"
        show-icon
      />
      <div class="key-box">
        <code>{{ resultDialog.fullKey }}</code>
      </div>
      <template #footer>
        <el-button type="primary" @click="copyKey">复制密钥</el-button>
        <el-button @click="resultDialog.visible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { apiKeyApi } from '../api'

const list = ref([])
const loading = ref(false)
const saving = ref(false)
const dialog = reactive({ visible: false })
const resultDialog = reactive({ visible: false, fullKey: '' })
const form = reactive({ name: '', expires_at: null })

async function load() {
  loading.value = true
  try {
    const data = await apiKeyApi.list()
    list.value = Array.isArray(data) ? data : data.items || []
  } finally {
    loading.value = false
  }
}

function openCreate() {
  form.name = ''
  form.expires_at = null
  dialog.visible = true
}

async function onSave() {
  if (!form.name) {
    ElMessage.warning('请填写名称')
    return
  }
  saving.value = true
  try {
    const body = { name: form.name }
    if (form.expires_at) body.expires_at = form.expires_at
    const res = await apiKeyApi.create(body)
    const fullKey = res.full_key || res.key || res.api_key || ''
    dialog.visible = false
    resultDialog.fullKey = fullKey
    resultDialog.visible = true
    await load()
  } finally {
    saving.value = false
  }
}

async function copyKey() {
  try {
    await navigator.clipboard.writeText(resultDialog.fullKey)
    ElMessage.success('已复制到剪贴板')
  } catch (e) {
    ElMessage.warning('复制失败，请手动复制')
  }
}

async function onRevoke(row) {
  try {
    await ElMessageBox.confirm(`确定吊销 API Key "${row.name}" 吗?此操作不可恢复。`, '提示', { type: 'warning' })
  } catch (e) {
    return
  }
  await apiKeyApi.remove(row.id)
  ElMessage.success('已吊销')
  await load()
}

onMounted(load)
</script>

<style scoped>
.page-card {
  background: #fff;
  border-radius: 8px;
  padding: 16px;
  height: 100%;
  overflow: auto;
}
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.page-title {
  margin: 0;
}
.key-box {
  margin: 14px 0;
  padding: 12px;
  background: #f5f7fa;
  border: 1px dashed #dcdfe6;
  border-radius: 6px;
  word-break: break-all;
}
.key-box code {
  font-size: 14px;
}
</style>
