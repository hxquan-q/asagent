import { defineStore } from 'pinia'
import { agentApi, conversationApi, chatStream } from '../api'

/** Blocks that are worth lifting out of the scroll and into the artifact canvas. */
function isArtifact(block) {
  return (
    block &&
    ['table', 'chart', 'diagram', 'svg', 'html', 'image', 'file'].includes(block.type)
  )
}

function artifactTitle(block, idx) {
  if (block.title) return block.title
  const labels = {
    table: '数据表',
    chart: '图表',
    diagram: '流程图',
    svg: '矢量图',
    html: '网页',
    image: '图片',
    file: '文件'
  }
  return `${labels[block.type] || '内容'} ${idx + 1}`
}

/** Turn a stored message (list of blocks) into a renderable message object. */
function decodeMessage(m) {
  const blocks = Array.isArray(m.blocks) ? m.blocks : []
  const text = blocks
    .filter((b) => b && b.type === 'text')
    .map((b) => b.content || '')
    .join('')
  const rich = blocks.filter((b) => b && b.type !== 'text')
  return {
    id: m.id,
    role: m.role,
    text,
    blocks: rich,
    steps: [],
    streaming: false,
    error: '',
    created_at: m.created_at
  }
}

export const useChatStore = defineStore('chat', {
  state: () => ({
    agents: [],
    agentId: null,

    conversations: [],
    conversationsLoading: false,

    currentConversationId: null,
    messages: [],
    loadingConversation: false,

    sending: false,
    abortCtrl: null,

    // artifact canvas
    artifacts: [], // [{ block, title, midx, bidx }]
    activeArtifact: -1
  }),
  getters: {
    currentAgent: (s) => s.agents.find((a) => a.id === s.agentId) || null,
    hasArtifacts: (s) => s.artifacts.length > 0
  },
  actions: {
    /* ---------- agents ---------- */
    async loadAgents() {
      try {
        const list = await agentApi.list()
        this.agents = Array.isArray(list) ? list : list.items || []
        if (!this.agentId && this.agents.length) this.agentId = this.agents[0].id
      } catch (e) {
        /* surfaced by interceptor */
      }
    },
    setAgent(id) {
      this.agentId = id
    },

    /* ---------- conversations ---------- */
    async loadConversations() {
      this.conversationsLoading = true
      try {
        this.conversations = (await conversationApi.list()) || []
      } catch (e) {
        /* surfaced by interceptor */
      } finally {
        this.conversationsLoading = false
      }
    },

    async selectConversation(id) {
      if (!id) return this.reset()
      this.currentConversationId = id
      this.loadingConversation = true
      try {
        const data = await conversationApi.get(id)
        this.messages = (data.messages || []).map(decodeMessage)
        this.rebuildArtifacts()
      } catch (e) {
        /* surfaced by interceptor */
      } finally {
        this.loadingConversation = false
      }
    },

    reset() {
      if (this.abortCtrl) this.abortCtrl.abort()
      this.abortCtrl = null
      this.currentConversationId = null
      this.messages = []
      this.artifacts = []
      this.activeArtifact = -1
      this.sending = false
    },

    async deleteConversation(id) {
      await conversationApi.remove(id)
      if (this.currentConversationId === id) this.reset()
      await this.loadConversations()
    },

    async renameConversation(id, title) {
      await conversationApi.rename(id, title)
      const c = this.conversations.find((x) => x.id === id)
      if (c) c.title = title
    },

    /* ---------- artifacts ---------- */
    rebuildArtifacts() {
      const arts = []
      this.messages.forEach((m, midx) => {
        if (m.role !== 'assistant') return
        ;(m.blocks || []).forEach((b, bidx) => {
          if (isArtifact(b)) arts.push({ block: b, title: artifactTitle(b, arts.length), midx, bidx })
        })
      })
      this.artifacts = arts
      this.activeArtifact = arts.length ? arts.length - 1 : -1
    },

    _pushArtifact(block) {
      if (!isArtifact(block)) return
      this.artifacts.push({
        block,
        title: artifactTitle(block, this.artifacts.length),
        midx: this.messages.length - 1,
        bidx: -1
      })
      this.activeArtifact = this.artifacts.length - 1
    },

    selectArtifact(i) {
      this.activeArtifact = i
    },

    /** Focus a specific block in the canvas (matched by object reference). */
    focusBlock(block) {
      const i = this.artifacts.findIndex((a) => a.block === block)
      if (i >= 0) {
        this.activeArtifact = i
        return true
      }
      return false
    },

    /* ---------- send + stream ---------- */
    async send(text) {
      const content = (text || '').trim()
      if (!content || this.sending || !this.agentId) return

      this.messages.push({ role: 'user', text: content, blocks: [], steps: [], streaming: false, error: '' })
      const assistant = {
        role: 'assistant',
        text: '',
        blocks: [],
        steps: [],
        streaming: true,
        error: ''
      }
      this.messages.push(assistant)

      this.sending = true
      this.abortCtrl = new AbortController()
      try {
        await chatStream({
          agentId: this.agentId,
          message: content,
          conversationId: this.currentConversationId,
          signal: this.abortCtrl.signal,
          onEvent: (evt) => this._handleEvent(assistant, evt)
        })
      } catch (e) {
        if (e && e.name === 'AbortError') {
          assistant.text = (assistant.text || '') + '\n\n_（已停止）_'
        } else {
          assistant.error = (e && e.message) || '请求失败'
        }
      } finally {
        assistant.streaming = false
        this.sending = false
        this.abortCtrl = null
        // refresh sidebar so the (possibly new) conversation shows up with its title
        this.loadConversations()
      }
    },

    stop() {
      if (this.abortCtrl) this.abortCtrl.abort()
    },

    _handleEvent(msg, evt) {
      if (!evt || !evt.type) return
      switch (evt.type) {
        case 'conversation':
          this.currentConversationId = evt.conversation_id
          break
        case 'token':
          msg.text = (msg.text || '') + (evt.content || '')
          break
        case 'tool_start': {
          // collapse repeated tool_start for the same name into one running step
          const existing = msg.steps.find((s) => s.name === evt.name && s.status === 'running')
          if (!existing) msg.steps.push({ name: evt.name, status: 'running', content: '' })
          break
        }
        case 'tool_end': {
          const step = msg.steps.find((s) => s.name === evt.name && s.status === 'running')
          if (step) {
            step.status = 'done'
            step.content = evt.content || ''
          } else {
            msg.steps.push({ name: evt.name, status: 'done', content: evt.content || '' })
          }
          break
        }
        case 'block':
          if (evt.block) {
            msg.blocks.push(evt.block)
            this._pushArtifact(evt.block)
          }
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
  }
})
