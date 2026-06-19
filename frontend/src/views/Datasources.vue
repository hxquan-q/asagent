<template>
  <div class="page">
   <div class="page-narrow">
    <PageHeader title="数据源" subtitle="以只读方式接入业务数据库（PostgreSQL）" icon="database">
      <template #actions>
        <el-button type="primary" @click="openCreate"><AppIcon name="plus" :size="14" />&nbsp;新建数据源</el-button>
      </template>
    </PageHeader>

    <div class="page-body">
    <el-table :data="list" v-loading="loading" border stripe>
      <el-table-column prop="name" label="名称" min-width="120" />
      <el-table-column prop="type" label="类型" width="100" />
      <el-table-column label="连接">
        <template #default="{ row }">
          {{ row.host }}:{{ row.port }} / {{ row.db }}
        </template>
      </el-table-column>
      <el-table-column prop="username" label="用户" width="120" />
      <el-table-column label="状态" width="90">
        <template #default="{ row }">
          <el-tag :type="row.enabled === false ? 'info' : 'success'" size="small">
            {{ row.enabled === false ? '禁用' : '启用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="230" fixed="right">
        <template #default="{ row }">
          <el-button text type="success" :loading="testingId === row.id" @click="onTest(row)">测试连接</el-button>
          <el-button text type="primary" @click="openEdit(row)">编辑</el-button>
          <el-button text type="danger" @click="onRemove(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    </div>

    <el-dialog v-model="dialog.visible" :title="dialog.id ? '编辑数据源' : '新建数据源'" width="560px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="名称" required>
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="form.type" style="width: 100%">
            <el-option label="Postgres" value="postgres" />
          </el-select>
        </el-form-item>
        <el-form-item label="主机" required>
          <el-input v-model="form.host" placeholder="如 127.0.0.1" />
        </el-form-item>
        <el-form-item label="端口" required>
          <el-input-number v-model="form.port" :min="1" :max="65535" controls-position="right" style="width: 100%" />
        </el-form-item>
        <el-form-item label="数据库" required>
          <el-input v-model="form.db" />
        </el-form-item>
        <el-form-item label="用户名" required>
          <el-input v-model="form.username" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" show-password :placeholder="dialog.id ? '留空则不修改' : ''" />
        </el-form-item>
        <el-form-item label="启用">
          <el-switch v-model="form.enabled" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog.visible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="onSave">保存</el-button>
      </template>
    </el-dialog>
   </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { datasourceApi } from '../api'
import AppIcon from '../components/AppIcon.vue'
import PageHeader from '../components/PageHeader.vue'

const list = ref([])
const loading = ref(false)
const saving = ref(false)
const testingId = ref(null)
const dialog = reactive({ visible: false, id: null })
const form = reactive({
  name: '',
  type: 'postgres',
  host: '',
  port: 5432,
  db: '',
  username: '',
  password: '',
  enabled: true
})

async function load() {
  loading.value = true
  try {
    const data = await datasourceApi.list()
    list.value = Array.isArray(data) ? data : data.items || []
  } finally {
    loading.value = false
  }
}

function resetForm() {
  Object.assign(form, {
    name: '',
    type: 'postgres',
    host: '',
    port: 5432,
    db: '',
    username: '',
    password: '',
    enabled: true
  })
  dialog.id = null
}
function openCreate() {
  resetForm()
  dialog.visible = true
}
function openEdit(row) {
  resetForm()
  dialog.id = row.id
  Object.assign(form, {
    name: row.name,
    type: row.type || 'postgres',
    host: row.host || '',
    port: row.port || 5432,
    db: row.db || '',
    username: row.username || '',
    password: '',
    enabled: row.enabled !== false
  })
  dialog.visible = true
}

function buildBody() {
  const body = { ...form }
  body.options = {}
  if (dialog.id && !body.password) delete body.password
  return body
}

async function onSave() {
  if (!form.name || !form.host || !form.db) {
    ElMessage.warning('请填写必填项')
    return
  }
  saving.value = true
  try {
    if (dialog.id) {
      await datasourceApi.update(dialog.id, buildBody())
      ElMessage.success('已更新')
    } else {
      await datasourceApi.create(buildBody())
      ElMessage.success('已创建')
    }
    dialog.visible = false
    await load()
  } finally {
    saving.value = false
  }
}

async function onTest(row) {
  testingId.value = row.id
  try {
    const res = await datasourceApi.test(row.id)
    if (res.ok) {
      ElMessage.success('连接成功')
      if (res.tables_preview) {
        ElMessageBox.alert(
          Array.isArray(res.tables_preview)
            ? res.tables_preview.join(', ')
            : JSON.stringify(res.tables_preview),
          '可用表'
        )
      }
    } else {
      ElMessage.error(res.error || '连接失败')
    }
  } finally {
    testingId.value = null
  }
}

async function onRemove(row) {
  try {
    await ElMessageBox.confirm(`确定删除数据源 "${row.name}" 吗?`, '提示', { type: 'warning' })
  } catch (e) {
    return
  }
  await datasourceApi.remove(row.id)
  ElMessage.success('已删除')
  await load()
}

onMounted(load)
</script>

<style scoped>
</style>
