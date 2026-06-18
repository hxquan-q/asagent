<template>
  <div class="page-card">
    <div class="toolbar">
      <h3 class="page-title">Skills 管理</h3>
      <div class="toolbar-right">
        <el-checkbox v-model="overwrite">覆盖已存在</el-checkbox>
        <el-upload
          :show-file-list="false"
          :before-upload="onUpload"
          accept=".zip"
        >
          <el-button type="primary">上传 Skill (zip)</el-button>
        </el-upload>
      </div>
    </div>

    <el-table :data="list" v-loading="loading" border stripe>
      <el-table-column prop="name" label="名称" min-width="140" />
      <el-table-column prop="description" label="描述" min-width="220" show-overflow-tooltip />
      <el-table-column label="启用状态" width="120">
        <template #default="{ row }">
          <el-switch
            :model-value="row.enabled !== false"
            :loading="togglingId === row.id"
            @change="(v) => onToggle(row, v)"
          />
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button text type="primary" :loading="mdLoadingId === row.id" @click="viewMd(row)">查看 SKILL.md</el-button>
          <el-button text type="danger" @click="onRemove(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="mdDialog.visible" :title="`SKILL.md - ${mdDialog.name}`" width="720px">
      <pre class="md-pre">{{ mdDialog.content }}</pre>
      <template #footer>
        <el-button @click="mdDialog.visible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { skillApi } from '../api'

const list = ref([])
const loading = ref(false)
const overwrite = ref(false)
const togglingId = ref(null)
const mdLoadingId = ref(null)
const mdDialog = reactive({ visible: false, name: '', content: '' })

async function load() {
  loading.value = true
  try {
    const data = await skillApi.list()
    list.value = Array.isArray(data) ? data : data.items || []
  } finally {
    loading.value = false
  }
}

async function onUpload(file) {
  try {
    await skillApi.upload(file, overwrite.value)
    ElMessage.success(`已上传 ${file.name}`)
    await load()
  } catch (e) {
    // handled by interceptor
  }
  return false // prevent el-upload auto upload
}

async function onToggle(row, enabled) {
  togglingId.value = row.id
  try {
    await skillApi.setEnabled(row.id, enabled)
    row.enabled = enabled
    ElMessage.success(enabled ? '已启用' : '已禁用')
  } finally {
    togglingId.value = null
  }
}

async function viewMd(row) {
  mdLoadingId.value = row.id
  try {
    const res = await skillApi.skillMd(row.id)
    mdDialog.name = res.name || row.name
    mdDialog.content = res.content || '(无内容)'
    mdDialog.visible = true
  } finally {
    mdLoadingId.value = null
  }
}

async function onRemove(row) {
  try {
    await ElMessageBox.confirm(`确定删除 Skill "${row.name}" 吗?`, '提示', { type: 'warning' })
  } catch (e) {
    return
  }
  await skillApi.remove(row.id)
  ElMessage.success('已删除')
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
.toolbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
}
.page-title {
  margin: 0;
}
.md-pre {
  background: #1e1e1e;
  color: #e6e6e6;
  padding: 14px;
  border-radius: 6px;
  max-height: 60vh;
  overflow: auto;
  font-size: 13px;
  white-space: pre-wrap;
  word-break: break-word;
}
</style>
