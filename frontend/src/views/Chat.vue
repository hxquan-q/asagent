<template>
  <div class="chat-page">
    <div class="chat-header">
      <span class="label">选择 Agent:</span>
      <el-select
        v-model="agentId"
        placeholder="请选择 Agent"
        style="width: 280px"
        @change="onAgentChange"
      >
        <el-option
          v-for="a in agents"
          :key="a.id"
          :label="a.name"
          :value="a.id"
        />
      </el-select>
      <el-button text @click="newConversation">新对话</el-button>
    </div>

    <div ref="messagesEl" class="messages">
      <el-empty v-if="messages.length === 0" description="开始与 Agent 对话" />
      <div
        v-for="(msg, i) in messages"
        :key="i"
        class="msg-row"
        :class="msg.role === 'user' ? 'msg-user' : 'msg-assistant'"
      >
        <div class="avatar" :class="msg.role">
          {{ msg.role === 'user' ? '我' : 'A' }}
        </div>
        <div class="bubble">
          <div v-if="msg.text" class="md-body" v-html="renderMarkdown(msg.text)"></div>
          <div v-if="msg.blocks && msg.blocks.length" class="blocks">
            <BlockRenderer
              v-for="(b, bi) in msg.blocks"
              :key="bi"
              :block="b"
            />
          </div>
          <div v-if="msg.error" class="msg-error">{{ msg.error }}</div>
          <div v-if="msg.streaming" class="typing">
            <span class="dot"></span><span class="dot"></span><span class="dot"></span>
          </div>
        </div>
      </div>
    </div>

    <div class="composer">
      <el-input
        v-model="input"
        type="textarea"
        :rows="2"
        :disabled="!agentId || sending"
        resize="none"
        placeholder="输入消息，Enter 发送，Shift+Enter 换行"
        @keydown.enter.exact.prevent="onSend"
      />
      <el-button
        type="primary"
        :loading="sending"
        :disabled="!agentId || !input.trim()"
        @click="onSend"
      >
        发送
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { nextTick, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { agentApi, chatStream } from '../api'
import { renderMarkdown } from '../utils/markdown'
import BlockRenderer from '../components/BlockRenderer.vue'

const agents = ref([])
const agentId = ref(null)
const messages = ref([])
const input = ref('')
const sending = ref(false)
const conversationId = ref(null)
const messagesEl = ref(null)

onMounted(async () => {
  try {
    const list = await agentApi.list()
    agents.value = Array.isArray(list) ? list : list.items || []
    if (agents.value.length && !agentId.value) {
      agentId.value = agents.value[0].id
    }
  } catch (e) {
    // handled by interceptor
  }
})

function onAgentChange() {
  conversationId.value = null
}

function newConversation() {
  messages.value = []
  conversationId.value = null
}

async function scrollBottom() {
  await nextTick()
  if (messagesEl.value) {
    messagesEl.value.scrollTop = messagesEl.value.scrollHeight
  }
}

async function onSend() {
  if (!agentId.value) {
    ElMessage.warning('请先选择 Agent')
    return
  }
  const text = input.value.trim()
  if (!text) return
  messages.value.push({ role: 'user', text })
  input.value = ''
  await scrollBottom()

  const assistantMsg = reactive({ role: 'assistant', text: '', blocks: [], streaming: true, error: '' })
  messages.value.push(assistantMsg)
  await scrollBottom()

  sending.value = true
  try {
    await chatStream({
      agentId: agentId.value,
      message: text,
      conversationId: conversationId.value,
      onEvent: (evt) => handleEvent(assistantMsg, evt)
    })
  } catch (e) {
    assistantMsg.error = assistantMsg.error || (e && e.message) || '请求失败'
  } finally {
    assistantMsg.streaming = false
    sending.value = false
    await scrollBottom()
  }
}

function handleEvent(msg, evt) {
  if (!evt || !evt.type) return
  switch (evt.type) {
    case 'conversation':
      conversationId.value = evt.conversation_id
      break
    case 'token':
      msg.text = (msg.text || '') + (evt.content || '')
      scrollBottom()
      break
    case 'tool_start':
      msg.text = (msg.text || '') + `\n\n> 调用工具: **${evt.name}**\n`
      break
    case 'tool_end':
      msg.text = (msg.text || '') + `\n> 工具完成: **${evt.name}**\n\n`
      break
    case 'block':
      if (evt.block) msg.blocks.push(evt.block)
      break
    case 'error':
      msg.error = evt.content || '服务返回错误'
      break
    case 'done':
      break
    default:
      break
  }
}
</script>

<style scoped>
.chat-page {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
}
.chat-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 16px;
  border-bottom: 1px solid #ebeef5;
}
.label {
  font-size: 13px;
  color: #606266;
}
.messages {
  flex: 1;
  overflow: auto;
  padding: 16px;
}
.msg-row {
  display: flex;
  margin-bottom: 16px;
  gap: 10px;
}
.msg-user {
  flex-direction: row-reverse;
}
.avatar {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 14px;
  font-weight: 600;
}
.avatar.user {
  background: #67c23a;
}
.avatar.assistant {
  background: #409eff;
}
.bubble {
  max-width: 78%;
  padding: 10px 14px;
  border-radius: 8px;
  background: #f5f7fa;
  word-break: break-word;
}
.msg-user .bubble {
  background: #ecf5ff;
}
.blocks {
  margin-top: 8px;
}
.msg-error {
  color: #f56c6c;
  font-size: 13px;
  margin-top: 6px;
}
.composer {
  display: flex;
  gap: 10px;
  padding: 12px 16px;
  border-top: 1px solid #ebeef5;
  align-items: flex-end;
}
.typing .dot {
  display: inline-block;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #909399;
  margin: 0 2px;
  animation: blink 1.2s infinite ease-in-out both;
}
.typing .dot:nth-child(2) {
  animation-delay: 0.2s;
}
.typing .dot:nth-child(3) {
  animation-delay: 0.4s;
}
@keyframes blink {
  0%,
  80%,
  100% {
    opacity: 0.2;
  }
  40% {
    opacity: 1;
  }
}
</style>
