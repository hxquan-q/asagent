<template>
  <div class="page">
   <div class="page-narrow">
    <PageHeader title="LLM 配置" subtitle="多供应商模型接入（OpenAI / DeepSeek / 通义 / Ollama …）" icon="cpu">
      <template #actions>
        <el-button type="primary" @click="openCreate"><AppIcon name="plus" :size="14" />&nbsp;新建配置</el-button>
      </template>
    </PageHeader>

    <div class="page-body">
    <el-table :data="list" v-loading="loading" border stripe>
      <el-table-column prop="name" label="名称" min-width="120" />
      <el-table-column prop="provider" label="Provider" width="120" />
      <el-table-column prop="model_name" label="模型" min-width="140" />
      <el-table-column prop="api_base_url" label="API Base" min-width="200" show-overflow-tooltip />
      <el-table-column label="默认" width="80">
        <template #default="{ row }">
          <el-tag v-if="row.is_default" type="warning" size="small">默认</el-tag>
          <span v-else>-</span>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="80">
        <template #default="{ row }">
          <el-tag :type="row.enabled === false ? 'info' : 'success'" size="small">
            {{ row.enabled === false ? '禁用' : '启用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button v-if="!row.is_default" text type="warning" @click="onSetDefault(row)">设默认</el-button>
          <el-button text type="primary" @click="openEdit(row)">编辑</el-button>
          <el-button text type="danger" @click="onRemove(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    </div>

    <el-dialog v-model="dialog.visible" :title="dialog.id ? '编辑配置' : '新建配置'" width="560px">
      <el-form :model="form" label-width="110px">
        <el-form-item label="名称" required>
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="Provider" required>
          <el-select v-model="form.provider" filterable allow-create placeholder="选择或输入 provider" style="width: 100%" @change="onProviderChange">
            <el-option v-for="p in providers" :key="p" :label="p" :value="p" />
          </el-select>
        </el-form-item>
        <el-form-item label="模型名" required>
          <el-input v-model="form.model_name" placeholder="如 gpt-4o-mini" />
        </el-form-item>
        <el-form-item label="API Base URL">
          <el-input v-model="form.api_base_url" placeholder="可选，留空使用默认" />
        </el-form-item>
        <el-form-item label="API Key">
          <el-input v-model="form.api_key" type="password" show-password :placeholder="dialog.id ? '留空则不修改' : ''" />
        </el-form-item>
        <el-form-item label="附加参数">
          <el-input v-model="additionalParamsText" type="textarea" :rows="3" placeholder='JSON, 如 {"temperature": 0.2}' />
        </el-form-item>
        <el-form-item label="设为默认">
          <el-switch v-model="form.is_default" />
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
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { llmApi } from '../api'
import AppIcon from '../components/AppIcon.vue'
import PageHeader from '../components/PageHeader.vue'

const list = ref([])
const providers = ref([])
const defaultsMap = ref({})
const loading = ref(false)
const saving = ref(false)
const dialog = reactive({ visible: false, id: null })
const form = reactive({
  name: '',
  provider: '',
  model_name: '',
  api_base_url: '',
  api_key: '',
  is_default: false,
  enabled: true
})
const additionalParamsText = ref('{}')

const additionalParams = computed(() => {
  try {
    return JSON.parse(additionalParamsText.value || '{}')
  } catch (e) {
    return {}
  }
})

async function load() {
  loading.value = true
  try {
    const [data, prov] = await Promise.all([llmApi.list(), llmApi.providers()])
    list.value = Array.isArray(data) ? data : data.items || []
    providers.value = prov.providers || []
    defaultsMap.value = prov.defaults || {}
  } finally {
    loading.value = false
  }
}

function resetForm() {
  Object.assign(form, {
    name: '',
    provider: '',
    model_name: '',
    api_base_url: '',
    api_key: '',
    is_default: false,
    enabled: true
  })
  additionalParamsText.value = '{}'
  dialog.id = null
}
function openCreate() {
  resetForm()
  if (providers.value[0]) form.provider = providers.value[0]
  onProviderChange()
  dialog.visible = true
}
function openEdit(row) {
  resetForm()
  dialog.id = row.id
  Object.assign(form, {
    name: row.name,
    provider: row.provider,
    model_name: row.model_name,
    api_base_url: row.api_base_url || '',
    api_key: '',
    is_default: !!row.is_default,
    enabled: row.enabled !== false
  })
  additionalParamsText.value = row.additional_params
    ? JSON.stringify(row.additional_params, null, 2)
    : '{}'
  dialog.visible = true
}

function onProviderChange() {
  if (!form.api_base_url && defaultsMap.value[form.provider]) {
    form.api_base_url = defaultsMap.value[form.provider]
  }
}

async function onSave() {
  if (!form.name || !form.provider || !form.model_name) {
    ElMessage.warning('请填写必填项')
    return
  }
  let params
  try {
    params = JSON.parse(additionalParamsText.value || '{}')
  } catch (e) {
    ElMessage.error('附加参数 JSON 格式错误')
    return
  }
  saving.value = true
  try {
    const body = { ...form, additional_params: params }
    if (dialog.id && !body.api_key) delete body.api_key
    if (dialog.id) {
      await llmApi.update(dialog.id, body)
      ElMessage.success('已更新')
    } else {
      await llmApi.create(body)
      ElMessage.success('已创建')
    }
    dialog.visible = false
    await load()
  } finally {
    saving.value = false
  }
}

async function onSetDefault(row) {
  await llmApi.update(row.id, { ...row, is_default: true })
  ElMessage.success('已设为默认')
  await load()
}

async function onRemove(row) {
  try {
    await ElMessageBox.confirm(`确定删除配置 "${row.name}" 吗?`, '提示', { type: 'warning' })
  } catch (e) {
    return
  }
  await llmApi.remove(row.id)
  ElMessage.success('已删除')
  await load()
}

onMounted(load)
</script>

<style scoped>
</style>
