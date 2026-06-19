<template>
  <div class="page">
    <div class="page-narrow">
      <!-- hero -->
      <section class="hero">
        <div class="hero-text">
          <span class="eyebrow">ASAGENT · 智能体工作台</span>
          <h1 class="hero-title">{{ greeting }}，{{ auth.isAdmin ? 'admin' : '用户' }}</h1>
          <p class="hero-sub">将智能体对准业务数据库，用自然语言提问，获取表格、图表与文件形式的多格式回答。</p>
          <div class="hero-actions">
            <router-link to="/chat" class="btn-primary">
              <AppIcon name="chat" :size="16" />&nbsp;进入工作台
            </router-link>
            <router-link v-if="auth.isAdmin" to="/agents" class="btn-ghost">
              <AppIcon name="plus" :size="15" />&nbsp;新建智能体
            </router-link>
          </div>
        </div>
        <div class="hero-art" aria-hidden="true">
          <div class="orb orb-a"></div>
          <div class="orb orb-b"></div>
          <div class="hero-glyph"><AppIcon name="sparkles" :size="30" /></div>
        </div>
      </section>

      <!-- stat grid -->
      <div class="stat-grid">
        <div v-for="s in cards" :key="s.key" class="stat-card">
          <div class="sc-top">
            <span class="sc-icon" :style="{ background: s.soft, color: s.color }">
              <AppIcon :name="s.icon" :size="18" />
            </span>
            <span v-if="s.sub" class="sc-sub">{{ s.sub }}</span>
          </div>
          <div class="sc-value">{{ s.value }}</div>
          <div class="sc-label">{{ s.label }}</div>
        </div>
      </div>

      <!-- columns -->
      <div class="dash-cols">
        <section class="panel">
          <header class="panel-head">
            <div>
              <h3 class="panel-title">最近对话</h3>
              <span class="panel-sub">最近的智能体交互记录</span>
            </div>
            <router-link to="/chat" class="link-more">查看全部 <AppIcon name="chevronRight" :size="13" /></router-link>
          </header>
          <div class="panel-body">
            <div v-if="!recent.length" class="panel-empty">
              <AppIcon name="chat" :size="22" />
              <p>还没有对话记录</p>
            </div>
            <button
              v-for="c in recent"
              :key="c.id"
              class="recent-row"
              @click="openConversation(c.id)"
            >
              <span class="rr-icon"><AppIcon name="robot" :size="14" /></span>
              <span class="rr-main">
                <span class="rr-title">{{ c.title || '新对话' }}</span>
                <span class="rr-meta">
                  <span v-if="c.agent_name" class="rr-agent">{{ c.agent_name }}</span>
                  <span>· {{ c.message_count }} 条消息</span>
                  <span>· {{ relTime(c.created_at) }}</span>
                </span>
              </span>
              <AppIcon class="rr-chev" name="chevronRight" :size="15" />
            </button>
          </div>
        </section>

        <section class="panel">
          <header class="panel-head">
            <div>
              <h3 class="panel-title">配置入口</h3>
              <span class="panel-sub">管理智能体所需的资源</span>
            </div>
          </header>
          <div class="panel-body">
            <router-link v-for="q in quickLinks" :key="q.path" :to="q.path" class="quick-row">
              <span class="qr-icon" :style="{ background: q.soft, color: q.color }">
                <AppIcon :name="q.icon" :size="16" />
              </span>
              <span class="qr-main">
                <span class="qr-title">{{ q.title }}</span>
                <span class="qr-sub">{{ q.sub }}</span>
              </span>
              <AppIcon class="rr-chev" name="chevronRight" :size="15" />
            </router-link>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { statsApi } from '../api'
import { useAuthStore } from '../stores/auth'
import { useChatStore } from '../stores/chat'
import AppIcon from '../components/AppIcon.vue'

const auth = useAuthStore()
const chat = useChatStore()
const router = useRouter()

const stats = ref(null)
const recent = ref([])

const greeting = computed(() => {
  const h = new Date().getHours()
  if (h < 6) return '夜深了'
  if (h < 12) return '早上好'
  if (h < 14) return '中午好'
  if (h < 18) return '下午好'
  return '晚上好'
})

const cards = computed(() => {
  const s = stats.value || {}
  return [
    { key: 'agents', label: '智能体', icon: 'robot', value: s.agents ?? '–', color: 'var(--primary)', soft: 'var(--primary-soft)' },
    { key: 'conversations', label: '对话', icon: 'chat', value: s.conversations ?? '–', color: 'var(--accent)', soft: 'var(--accent-soft)' },
    { key: 'messages', label: '消息', icon: 'layers', value: s.messages ?? '–', color: 'var(--info)', soft: 'var(--info-soft)' },
    {
      key: 'skills', label: '技能', icon: 'sparkles',
      value: s.skills ?? '–', sub: s.enabled_skills ? `启用 ${s.enabled_skills}` : '',
      color: '#b48bff', soft: 'rgba(180,139,255,0.14)'
    },
    { key: 'datasources', label: '数据源', icon: 'database', value: s.datasources ?? '–', color: 'var(--info)', soft: 'var(--info-soft)' },
    { key: 'llm', label: 'LLM 配置', icon: 'cpu', value: s.llm_configs ?? '–', color: 'var(--primary)', soft: 'var(--primary-soft)' },
    { key: 'apikeys', label: 'API Key', icon: 'key', value: s.api_keys ?? '–', color: 'var(--accent)', soft: 'var(--accent-soft)' }
  ]
})

const quickLinks = computed(() =>
  [
    { path: '/agents', title: '智能体', sub: '配置模型、数据源与技能', icon: 'robot', color: 'var(--primary)', soft: 'var(--primary-soft)' },
    { path: '/datasources', title: '数据源', sub: '接入只读业务数据库', icon: 'database', color: 'var(--info)', soft: 'var(--info-soft)' },
    { path: '/llm', title: 'LLM 配置', sub: '多供应商模型接入', icon: 'cpu', color: 'var(--accent)', soft: 'var(--accent-soft)' },
    { path: '/skills', title: '技能', sub: '上传与热加载 Agent Skills', icon: 'sparkles', color: '#b48bff', soft: 'rgba(180,139,255,0.14)' },
    { path: '/apikeys', title: 'API Key', sub: '外部程序调用凭证', icon: 'key', color: 'var(--accent)', soft: 'var(--accent-soft)' }
  ].filter(() => auth.isAdmin)
)

async function openConversation(id) {
  router.push('/chat')
  await chat.loadAgents()
  await chat.selectConversation(id)
}

function relTime(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  const diff = Math.max(0, Date.now() - d.getTime())
  const min = 60000, hr = 3600000, day = 86400000
  if (diff < hr) return Math.floor(diff / min) + ' 分钟前'
  if (diff < day) return Math.floor(diff / hr) + ' 小时前'
  if (diff < 7 * day) return Math.floor(diff / day) + ' 天前'
  return d.toLocaleDateString('zh-CN')
}

onMounted(async () => {
  try {
    const data = await statsApi.overview()
    stats.value = data
    recent.value = data.recent_conversations || []
  } catch (e) {
    /* surfaced by interceptor */
  }
})
</script>

<style scoped>
/* hero */
.hero {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  padding: 30px 32px;
  border-radius: var(--r-xl);
  background: linear-gradient(135deg, var(--surface) 0%, var(--surface-2) 100%);
  border: 1px solid var(--border);
  margin-bottom: 22px;
  position: relative;
  overflow: hidden;
}
.hero-text {
  position: relative;
  z-index: 1;
  min-width: 0;
}
.hero-title {
  margin: 8px 0 6px;
  font-size: var(--fs-3xl);
  font-weight: 700;
  letter-spacing: -0.02em;
}
.hero-title span {
  color: var(--primary-strong);
}
.hero-sub {
  margin: 0 0 18px;
  color: var(--text-muted);
  font-size: var(--fs-base);
  max-width: 540px;
  line-height: 1.6;
}
.hero-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}
.btn-primary {
  display: inline-flex;
  align-items: center;
  padding: 10px 18px;
  border-radius: var(--r-sm);
  background: var(--primary);
  color: #06281c;
  font-weight: 600;
  font-size: var(--fs-sm);
  transition: all var(--dur) var(--ease);
}
.btn-primary:hover {
  background: var(--primary-strong);
  text-decoration: none;
  transform: translateY(-1px);
  box-shadow: 0 8px 20px var(--primary-soft);
}
.btn-ghost {
  display: inline-flex;
  align-items: center;
  padding: 10px 16px;
  border-radius: var(--r-sm);
  border: 1px solid var(--border-strong);
  color: var(--text);
  font-weight: 500;
  font-size: var(--fs-sm);
  transition: all var(--dur) var(--ease);
}
.btn-ghost:hover {
  border-color: var(--primary-line);
  color: var(--primary-strong);
  text-decoration: none;
}

.hero-art {
  position: relative;
  width: 200px;
  height: 140px;
  flex-shrink: 0;
}
.orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(8px);
}
.orb-a {
  width: 150px;
  height: 150px;
  right: 20px;
  top: -20px;
  background: radial-gradient(circle, var(--primary) 0%, transparent 70%);
  opacity: 0.35;
}
.orb-b {
  width: 120px;
  height: 120px;
  right: -10px;
  bottom: -30px;
  background: radial-gradient(circle, var(--accent) 0%, transparent 70%);
  opacity: 0.3;
}
.hero-glyph {
  position: absolute;
  right: 50px;
  top: 45px;
  width: 54px;
  height: 54px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(140deg, var(--primary-strong), var(--primary));
  color: #06281c;
  box-shadow: var(--shadow);
}

/* stat grid */
.stat-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 14px;
  margin-bottom: 22px;
}
.stat-card {
  padding: 16px;
  border-radius: var(--r-lg);
  background: var(--surface);
  border: 1px solid var(--border);
  transition: all var(--dur) var(--ease);
}
.stat-card:hover {
  border-color: var(--border-strong);
  transform: translateY(-2px);
  box-shadow: var(--shadow);
}
.sc-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}
.sc-icon {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.sc-sub {
  font-size: 10px;
  font-family: var(--font-mono);
  color: var(--text-faint);
  background: var(--surface-2);
  padding: 2px 7px;
  border-radius: var(--r-xs);
}
.sc-value {
  font-family: var(--font-display);
  font-size: var(--fs-3xl);
  font-weight: 700;
  line-height: 1;
  letter-spacing: -0.02em;
}
.sc-label {
  margin-top: 5px;
  font-size: var(--fs-sm);
  color: var(--text-muted);
}

/* columns */
.dash-cols {
  display: grid;
  grid-template-columns: 1.4fr 1fr;
  gap: 18px;
}
@media (max-width: 980px) {
  .dash-cols {
    grid-template-columns: 1fr;
  }
  .hero-art {
    display: none;
  }
}
.panel {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--r-lg);
  overflow: hidden;
}
.panel-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 18px;
  border-bottom: 1px solid var(--border);
}
.panel-title {
  margin: 0;
  font-size: var(--fs-md);
  font-weight: 600;
}
.panel-sub {
  font-size: var(--fs-xs);
  color: var(--text-muted);
}
.link-more {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  font-size: var(--fs-xs);
  color: var(--text-muted);
}
.link-more:hover {
  color: var(--primary-strong);
  text-decoration: none;
}
.panel-body {
  padding: 8px;
}
.panel-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 36px;
  color: var(--text-faint);
}
.panel-empty p {
  margin: 0;
  font-size: var(--fs-sm);
  color: var(--text-muted);
}

.recent-row,
.quick-row {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  padding: 11px 12px;
  border-radius: var(--r-md);
  border: none;
  background: transparent;
  color: var(--text);
  font-family: inherit;
  cursor: pointer;
  text-align: left;
  text-decoration: none;
  transition: background var(--dur) var(--ease);
}
.recent-row:hover,
.quick-row:hover {
  background: var(--surface-2);
  text-decoration: none;
}
.rr-icon {
  width: 30px;
  height: 30px;
  border-radius: 9px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--accent-soft);
  color: var(--accent);
}
.rr-main,
.qr-main {
  min-width: 0;
  flex: 1;
}
.rr-title,
.qr-title {
  display: block;
  font-size: var(--fs-sm);
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.rr-meta {
  display: block;
  margin-top: 2px;
  font-size: var(--fs-xs);
  color: var(--text-faint);
}
.rr-agent {
  color: var(--accent);
}
.rr-chev {
  color: var(--text-faint);
  flex-shrink: 0;
}
.qr-icon {
  width: 32px;
  height: 32px;
  border-radius: 9px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}
.qr-sub {
  display: block;
  margin-top: 2px;
  font-size: var(--fs-xs);
  color: var(--text-muted);
}
</style>
