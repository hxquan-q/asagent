<template>
  <div class="page">
   <div class="page-narrow">
    <PageHeader title="智能体" subtitle="为每个 Agent 绑定模型、数据源与技能" icon="robot">
      <template #actions>
        <el-button type="primary" @click="openCreate">
          <AppIcon name="plus" :size="14" />&nbsp;新建 Agent
        </el-button>
      </template>
    </PageHeader>

    <div class="page-body">
    <el-table :data="list" v-loading="loading" border stripe>
      <el-table-column prop="name" label="名称" min-width="120" />
      <el-table-column prop="description" label="描述" min-width="160" show-overflow-tooltip />
      <el-table-column label="LLM 配置" width="140">
        <template #default="{ row }">
          {{ llmNameOf(row.llm_config_id) }}
        </template>
      </el-table-column>
      <el-table-column label="数据源" min-width="140">
        <template #default="{ row }">
          <el-tag v-for="id in row.datasource_ids || []" :key="id" size="small" class="tag">
            {{ dsNameOf(id) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="180">
        <template #default="{ row }">{{ row.created_at || '-' }}</template>
      </el-table-column>
      <el-table-column label="操作" width="160" fixed="right">
        <template #default="{ row }">
          <el-button text type="primary" @click="openEdit(row)">编辑</el-button>
          <el-button text type="danger" @click="onRemove(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    </div>

    <el-dialog v-model="dialog.visible" :title="dialog.id ? '编辑 Agent' : '新建 Agent'" width="640px">
      <el-form :model="form" label-width="110px">
        <el-form-item label="名称" required>
          <el-input v-model="form.name" placeholder="Agent 名称" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="系统提示词">
          <el-input v-model="form.system_prompt" type="textarea" :rows="4" />
        </el-form-item>
        <el-form-item label="LLM 配置">
          <el-select v-model="form.llm_config_id" placeholder="选择 LLM 配置" clearable style="width: 100%">
            <el-option v-for="l in llms" :key="l.id" :label="`${l.name} (${l.provider}/${l.model_name})`" :value="l.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="数据源">
          <el-select v-model="form.datasource_ids" multiple placeholder="选择数据源" style="width: 100%">
            <el-option v-for="d in datasources" :key="d.id" :label="d.name" :value="d.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="工具集">
          <el-select v-model="form.tool_set" multiple filterable allow-create default-first-option placeholder="输入工具名" style="width: 100%">
          </el-select>
        </el-form-item>
        <el-form-item label="Skills">
          <el-select v-model="form.skill_ids" multiple placeholder="选择 Skills" style="width: 100%">
            <el-option v-for="s in skills" :key="s.id" :label="s.name" :value="s.id" />
          </el-select>
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
import { agentApi, datasourceApi, llmApi, skillApi } from '../api'
import AppIcon from '../components/AppIcon.vue'
import PageHeader from '../components/PageHeader.vue'

const list = ref([])
const llms = ref([])
const datasources = ref([])
const skills = ref([])
const loading = ref(false)
const saving = ref(false)

const dialog = reactive({ visible: false, id: null })
const form = reactive({
  name: '',
  description: '',
  system_prompt: '',
  llm_config_id: null,
  datasource_ids: [],
  tool_set: [],
  skill_ids: []
})

function llmNameOf(id) {
  const l = llms.value.find((x) => x.id === id)
  return l ? `${l.name}` : '-'
}
function dsNameOf(id) {
  const d = datasources.value.find((x) => x.id === id)
  return d ? d.name : id
}

async function loadAll() {
  loading.value = true
  try {
    const [a, l, d, s] = await Promise.all([
      agentApi.list(),
      llmApi.list(),
      datasourceApi.list(),
      skillApi.list()
    ])
    list.value = asArray(a)
    llms.value = asArray(l)
    datasources.value = asArray(d)
    skills.value = asArray(s)
  } finally {
    loading.value = false
  }
}
function asArray(v) {
  return Array.isArray(v) ? v : v.items || []
}

function resetForm() {
  Object.assign(form, {
    name: '',
    description: '',
    system_prompt: '',
    llm_config_id: null,
    datasource_ids: [],
    tool_set: [],
    skill_ids: []
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
    name: row.name || '',
    description: row.description || '',
    system_prompt: row.system_prompt || '',
    llm_config_id: row.llm_config_id ?? null,
    datasource_ids: [...(row.datasource_ids || [])],
    tool_set: [...(row.tool_set || [])],
    skill_ids: [...(row.skill_ids || [])]
  })
  dialog.visible = true
}

async function onSave() {
  if (!form.name) {
    ElMessage.warning('请填写名称')
    return
  }
  saving.value = true
  try {
    const body = { ...form }
    if (dialog.id) {
      await agentApi.update(dialog.id, body)
      ElMessage.success('已更新')
    } else {
      await agentApi.create(body)
      ElMessage.success('已创建')
    }
    dialog.visible = false
    await loadAll()
  } finally {
    saving.value = false
  }
}

async function onRemove(row) {
  try {
    await ElMessageBox.confirm(`确定删除 Agent "${row.name}" 吗?`, '提示', { type: 'warning' })
  } catch (e) {
    return
  }
  await agentApi.remove(row.id)
  ElMessage.success('已删除')
  await loadAll()
}

onMounted(loadAll)
</script>

<style scoped>
.tag {
  margin: 2px 4px 2px 0;
}
</style>
