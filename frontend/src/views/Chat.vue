<template>
  <div class="workspace">
    <ConversationRail />

    <section class="thread-col">
      <header class="thread-head">
        <div class="th-left">
          <div class="th-agent-icon"><AppIcon name="robot" :size="16" /></div>
          <div>
            <div class="th-name">{{ agent?.name || '未选择 Agent' }}</div>
            <div class="th-sub">{{ agent?.description || '选择一个 Agent 开始对话' }}</div>
          </div>
        </div>
        <div class="th-right">
          <button
            class="canvas-toggle"
            :class="{ on: ui.canvasOpen, has: chat.hasArtifacts }"
            :title="ui.canvasOpen ? '隐藏画布' : '显示画布'"
            @click="ui.toggleCanvas()"
          >
            <AppIcon name="panelRight" :size="16" />
            <span v-if="chat.hasArtifacts" class="ct-badge">{{ chat.artifacts.length }}</span>
          </button>
        </div>
      </header>

      <div ref="scrollEl" class="thread-scroll">
        <!-- empty hero -->
        <div v-if="!chat.messages.length && !chat.loadingConversation" class="hero">
          <template v-if="chat.agents.length">
            <div class="hero-mark"><AppIcon name="sparkles" :size="26" /></div>
            <h2 class="hero-title">向 <span>{{ agent?.name }}</span> 提问</h2>
            <p class="hero-sub">
              {{ agent?.description || '基于你的业务数据进行分析、可视化与总结。' }}
            </p>
            <div class="suggest">
              <button v-for="s in suggestions" :key="s" class="suggest-chip" @click="quickSend(s)">
                <AppIcon name="bolt" :size="13" />
                <span>{{ s }}</span>
              </button>
            </div>
          </template>
          <template v-else>
            <div class="hero-mark"><AppIcon name="robot" :size="26" /></div>
            <h2 class="hero-title">还没有可用的 Agent</h2>
            <p class="hero-sub">先创建一个 Agent 并绑定 LLM 与数据源，再回到这里对话。</p>
            <router-link v-if="auth.isAdmin" to="/agents" class="hero-cta">
              <AppIcon name="plus" :size="15" /> 创建 Agent
            </router-link>
          </template>
        </div>

        <!-- loading -->
        <div v-else-if="chat.loadingConversation" class="hero">
          <div class="hero-mark"><span class="spinner-lg"></span></div>
          <p class="hero-sub">加载对话…</p>
        </div>

        <!-- messages -->
        <div v-else class="thread-inner">
          <MessageItem
            v-for="(m, i) in chat.messages"
            :key="i"
            :message="m"
            :agent-name="agent?.name"
            @focus-block="onFocusBlock"
          />
        </div>
      </div>

      <div class="thread-foot">
        <div class="composer-wrap">
          <Composer />
        </div>
      </div>
    </section>

    <ArtifactCanvas v-if="ui.canvasOpen" />
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { useChatStore } from '../stores/chat'
import { useUiStore } from '../stores/ui'
import { useAuthStore } from '../stores/auth'
import AppIcon from '../components/AppIcon.vue'
import ConversationRail from '../components/chat/ConversationRail.vue'
import MessageItem from '../components/chat/MessageItem.vue'
import Composer from '../components/chat/Composer.vue'
import ArtifactCanvas from '../components/chat/ArtifactCanvas.vue'

const chat = useChatStore()
const ui = useUiStore()
const auth = useAuthStore()

const scrollEl = ref(null)
const agent = computed(() => chat.currentAgent)

const suggestions = [
  '统计每个状态的订单数量',
  '查询库存最高的 10 个 SKU',
  '用柱状图展示近 30 天销售趋势',
  '画出核心业务的流程图'
]

onMounted(async () => {
  await chat.loadAgents()
  await chat.loadConversations()
  ui.canvasOpen = true
})

async function quickSend(text) {
  await chat.send(text)
}

function onFocusBlock(block) {
  if (chat.focusBlock(block)) {
    ui.canvasOpen = true
  }
}

function scrollToBottom() {
  nextTick(() => {
    const el = scrollEl.value
    if (el) el.scrollTop = el.scrollHeight
  })
}

watch(
  () => chat.messages,
  () => scrollToBottom(),
  { deep: true }
)
watch(() => chat.messages.length, () => scrollToBottom())
</script>

<style scoped>
.workspace {
  display: flex;
  height: 100%;
  min-height: 0;
  position: relative;
}

/* thread column */
.thread-col {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  background: var(--bg);
}
.thread-head {
  height: 56px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  border-bottom: 1px solid var(--border);
  background: color-mix(in srgb, var(--surface) 60%, transparent);
  backdrop-filter: blur(8px);
}
.th-left {
  display: flex;
  align-items: center;
  gap: 11px;
  min-width: 0;
}
.th-agent-icon {
  width: 32px;
  height: 32px;
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--accent-soft);
  color: var(--accent);
  border: 1px solid color-mix(in srgb, var(--accent) 28%, transparent);
  flex-shrink: 0;
}
.th-name {
  font-weight: 600;
  font-size: var(--fs-base);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.th-sub {
  font-size: var(--fs-xs);
  color: var(--text-muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 50vw;
}
.th-right {
  display: flex;
  gap: 8px;
}
.canvas-toggle {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: var(--r-sm);
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--text-muted);
  cursor: pointer;
  transition: all var(--dur) var(--ease);
}
.canvas-toggle:hover {
  color: var(--text);
  border-color: var(--border-strong);
}
.canvas-toggle.on {
  color: var(--primary-strong);
  border-color: var(--primary-line);
  background: var(--primary-soft);
}
.ct-badge {
  position: absolute;
  top: -5px;
  right: -5px;
  min-width: 16px;
  height: 16px;
  padding: 0 4px;
  border-radius: var(--r-pill);
  background: var(--accent);
  color: #2a1c05;
  font-size: 10px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}

.thread-scroll {
  flex: 1;
  overflow-y: auto;
  scroll-behavior: smooth;
}
.thread-inner {
  max-width: 820px;
  margin: 0 auto;
  padding: 22px 24px 30px;
  display: flex;
  flex-direction: column;
  gap: 18px;
}

/* hero / empty state */
.hero {
  height: 100%;
  max-width: 640px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 40px 24px;
  gap: 6px;
}
.hero-mark {
  width: 60px;
  height: 60px;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(140deg, var(--primary-strong), var(--primary));
  color: #06281c;
  margin-bottom: 10px;
  box-shadow: 0 10px 30px var(--primary-soft);
}
.hero-title {
  margin: 0;
  font-size: var(--fs-2xl);
  font-weight: 600;
}
.hero-title span {
  color: var(--primary-strong);
}
.hero-sub {
  margin: 4px 0 18px;
  color: var(--text-muted);
  font-size: var(--fs-base);
  line-height: 1.6;
  max-width: 460px;
}
.suggest {
  display: flex;
  flex-wrap: wrap;
  gap: 9px;
  justify-content: center;
  max-width: 560px;
}
.suggest-chip {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  padding: 9px 14px;
  border-radius: var(--r-pill);
  border: 1px solid var(--border-strong);
  background: var(--surface);
  color: var(--text);
  font-family: inherit;
  font-size: var(--fs-sm);
  cursor: pointer;
  transition: all var(--dur) var(--ease);
}
.suggest-chip:hover {
  border-color: var(--primary-line);
  background: var(--primary-soft);
  color: var(--primary-strong);
  transform: translateY(-1px);
}
.suggest-chip :deep(svg) {
  color: var(--accent);
}
.hero-cta {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  margin-top: 10px;
  padding: 10px 18px;
  border-radius: var(--r-sm);
  background: var(--primary);
  color: #06281c;
  font-weight: 600;
  text-decoration: none;
}
.hero-cta:hover {
  background: var(--primary-strong);
  text-decoration: none;
}
.spinner-lg {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  border: 3px solid var(--primary-soft);
  border-top-color: var(--primary);
  animation: spin 0.8s linear infinite;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}

.thread-foot {
  flex-shrink: 0;
  padding: 0 24px 16px;
  background: linear-gradient(to top, var(--bg) 60%, transparent);
}
.composer-wrap {
  max-width: 820px;
  margin: 0 auto;
}
</style>
