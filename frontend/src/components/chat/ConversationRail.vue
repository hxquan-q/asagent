<template>
  <aside class="rail">
    <div class="rail-top">
      <button class="new-btn" @click="newChat">
        <AppIcon name="plus" :size="16" />
        <span>新对话</span>
      </button>
      <el-select
        :model-value="chat.agentId"
        placeholder="选择 Agent"
        size="large"
        class="agent-select"
        @update:model-value="onAgent"
      >
        <el-option v-for="a in chat.agents" :key="a.id" :label="a.name" :value="a.id">
          <span class="ag-opt">
            <AppIcon name="robot" :size="14" />
            <span>{{ a.name }}</span>
          </span>
        </el-option>
      </el-select>
    </div>

    <div class="search">
      <AppIcon name="search" :size="15" />
      <input v-model="query" placeholder="搜索对话" />
    </div>

    <div class="conv-list">
      <div v-if="chat.conversationsLoading && !chat.conversations.length" class="list-empty">
        加载中…
      </div>
      <div v-else-if="!filtered.length" class="list-empty">
        <AppIcon name="chat" :size="22" />
        <p>还没有对话</p>
        <span>向 Agent 提问后会出现在这里</span>
      </div>

      <button
        v-for="c in filtered"
        :key="c.id"
        class="conv"
        :class="{ active: c.id === chat.currentConversationId }"
        @click="chat.selectConversation(c.id)"
      >
        <div class="conv-main">
          <div class="conv-title-row">
            <span class="conv-title">{{ c.title || '新对话' }}</span>
          </div>
          <div class="conv-preview">{{ c.preview || '（空对话）' }}</div>
          <div class="conv-meta">
            <span class="agent-chip" v-if="c.agent_name">
              <AppIcon name="robot" :size="11" />{{ c.agent_name }}
            </span>
            <span class="dot-sep">·</span>
            <span>{{ relTime(c.updated_at || c.created_at) }}</span>
            <span class="dot-sep">·</span>
            <span>{{ c.message_count }} 条</span>
          </div>
        </div>
        <div class="conv-tools" @click.stop>
          <span class="tool" title="重命名" @click="startRename(c)"><AppIcon name="pencil" :size="13" /></span>
          <span class="tool danger" title="删除" @click="onDelete(c)"><AppIcon name="trash" :size="13" /></span>
        </div>
      </button>
    </div>

    <!-- rename dialog -->
    <el-dialog v-model="renameOpen" title="重命名对话" width="380px" :close-on-click-modal="false">
      <el-input v-model="renameTitle" maxlength="80" show-word-limit @keydown.enter="confirmRename" />
      <template #footer>
        <el-button @click="renameOpen = false">取消</el-button>
        <el-button type="primary" @click="confirmRename">保存</el-button>
      </template>
    </el-dialog>
  </aside>
</template>

<script setup>
import { computed, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useChatStore } from '../../stores/chat'
import AppIcon from '../AppIcon.vue'

const chat = useChatStore()
const query = ref('')

const filtered = computed(() => {
  const q = query.value.trim().toLowerCase()
  if (!q) return chat.conversations
  return chat.conversations.filter(
    (c) =>
      (c.title || '').toLowerCase().includes(q) ||
      (c.preview || '').toLowerCase().includes(q) ||
      (c.agent_name || '').toLowerCase().includes(q)
  )
})

function onAgent(id) {
  chat.setAgent(id)
}
function newChat() {
  chat.reset()
}

const renameOpen = ref(false)
const renameTitle = ref('')
const renameTarget = ref(null)
function startRename(c) {
  renameTarget.value = c
  renameTitle.value = c.title || '新对话'
  renameOpen.value = true
}
async function confirmRename() {
  if (!renameTarget.value) return
  const t = renameTitle.value.trim()
  if (!t) return
  await chat.renameConversation(renameTarget.value.id, t)
  renameOpen.value = false
  ElMessage.success('已重命名')
}
async function onDelete(c) {
  try {
    await ElMessageBox.confirm(`删除对话「${c.title || '新对话'}」？此操作不可撤销。`, '删除对话', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消'
    })
  } catch (e) {
    return
  }
  await chat.deleteConversation(c.id)
  ElMessage.success('已删除')
}

function relTime(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  const now = Date.now()
  const diff = Math.max(0, now - d.getTime())
  const min = 60 * 1000
  const hr = 60 * min
  const day = 24 * hr
  if (diff < min) return '刚刚'
  if (diff < hr) return Math.floor(diff / min) + ' 分钟前'
  if (diff < day) return Math.floor(diff / hr) + ' 小时前'
  if (diff < 7 * day) return Math.floor(diff / day) + ' 天前'
  return d.toLocaleDateString('zh-CN')
}
</script>

<style scoped>
.rail {
  width: 286px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  background: var(--surface);
  border-right: 1px solid var(--border);
  overflow: hidden;
}
.rail-top {
  padding: 14px 14px 10px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.new-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 7px;
  padding: 10px;
  border-radius: var(--r-md);
  border: 1px dashed var(--border-strong);
  background: var(--surface-2);
  color: var(--text);
  font-family: inherit;
  font-size: var(--fs-sm);
  font-weight: 600;
  cursor: pointer;
  transition: all var(--dur) var(--ease);
}
.new-btn:hover {
  border-color: var(--primary-line);
  border-style: solid;
  background: var(--primary-soft);
  color: var(--primary-strong);
}
.agent-select :deep(.el-select__wrapper) {
  background: var(--surface-2) !important;
  border-radius: var(--r-md) !important;
}

.search {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 14px 10px;
  padding: 8px 11px;
  border-radius: var(--r-md);
  background: var(--surface-2);
  border: 1px solid var(--border);
  color: var(--text-faint);
}
.search input {
  border: none;
  outline: none;
  background: transparent;
  color: var(--text);
  font-family: inherit;
  font-size: var(--fs-sm);
  width: 100%;
}
.search input::placeholder {
  color: var(--text-faint);
}

.conv-list {
  flex: 1;
  overflow-y: auto;
  padding: 0 10px 12px;
}
.list-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  text-align: center;
  padding: 40px 16px;
  color: var(--text-faint);
}
.list-empty p {
  margin: 4px 0 0;
  font-size: var(--fs-sm);
  color: var(--text-muted);
}
.list-empty span {
  font-size: var(--fs-xs);
}

.conv {
  position: relative;
  display: block;
  width: 100%;
  text-align: left;
  padding: 10px 11px;
  margin-bottom: 4px;
  border-radius: var(--r-md);
  border: 1px solid transparent;
  background: transparent;
  color: var(--text);
  font-family: inherit;
  cursor: pointer;
  transition: background var(--dur) var(--ease);
}
.conv:hover {
  background: var(--surface-2);
}
.conv.active {
  background: var(--primary-soft);
  border-color: var(--primary-line);
}
.conv-title {
  font-size: var(--fs-sm);
  font-weight: 600;
  display: block;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.conv-preview {
  font-size: var(--fs-xs);
  color: var(--text-muted);
  margin-top: 3px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.conv-meta {
  display: flex;
  align-items: center;
  gap: 5px;
  margin-top: 6px;
  font-size: 10px;
  color: var(--text-faint);
}
.agent-chip {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  color: var(--accent);
}
.dot-sep {
  opacity: 0.6;
}
.conv-tools {
  position: absolute;
  top: 8px;
  right: 8px;
  display: flex;
  gap: 2px;
  opacity: 0;
  transition: opacity var(--dur) var(--ease);
}
.conv:hover .conv-tools {
  opacity: 1;
}
.tool {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  border-radius: var(--r-xs);
  color: var(--text-muted);
  cursor: pointer;
  background: var(--surface-3);
}
.tool:hover {
  color: var(--text);
  background: var(--surface-hi);
}
.tool.danger:hover {
  color: var(--danger);
}
.ag-opt {
  display: inline-flex;
  align-items: center;
  gap: 7px;
}
</style>
