<template>
  <div class="msg" :class="message.role">
    <!-- user -->
    <template v-if="message.role === 'user'">
      <div class="u-bubble">
        <div class="md-body" v-html="renderMarkdown(message.text)"></div>
      </div>
    </template>

    <!-- assistant -->
    <template v-else>
      <div class="a-avatar" :class="{ thinking: message.streaming }">
        <AppIcon name="robot" :size="16" />
      </div>
      <div class="a-body">
        <div class="a-name">
          {{ agentName || 'Agent' }}
          <span v-if="message.streaming" class="a-live"><span class="live-dot"></span>思考中</span>
        </div>

        <!-- tool steps -->
        <div v-if="message.steps.length" class="steps">
          <div
            v-for="(s, i) in message.steps"
            :key="i"
            class="step"
            :class="s.status"
            @click="toggleStep(i)"
          >
            <span class="step-icon">
              <span v-if="s.status === 'running'" class="spinner"></span>
              <AppIcon v-else name="check" :size="13" />
            </span>
            <span class="step-name mono">{{ s.name }}</span>
            <span class="step-state">{{ s.status === 'running' ? '运行中' : '完成' }}</span>
            <AppIcon
              v-if="s.content"
              class="step-chev"
              name="chevronDown"
              :size="14"
              :class="{ open: openSteps[i] }"
            />
            <div v-if="s.content && openSteps[i]" class="step-content mono" @click.stop>
              <pre>{{ s.content }}</pre>
            </div>
          </div>
        </div>

        <!-- text -->
        <div v-if="message.text" class="md-body" v-html="renderMarkdown(message.text)"></div>
        <span v-if="message.streaming && message.text" class="caret"></span>

        <!-- typing indicator -->
        <div v-if="message.streaming && !message.text && !message.steps.length" class="typing">
          <span class="dot"></span><span class="dot"></span><span class="dot"></span>
        </div>

        <!-- artifact cards -->
        <div v-if="message.blocks.length" class="artifacts-inline">
          <button
            v-for="(b, i) in message.blocks"
            :key="i"
            class="artifact-card"
            @click="$emit('focus-block', b)"
          >
            <span class="ac-icon" :style="{ color: artifactColor(b.type) }">
              <AppIcon :name="artifactIcon(b.type)" :size="16" />
            </span>
            <span class="ac-meta">
              <span class="ac-title">{{ b.title || artifactLabel(b.type, i) }}</span>
              <span class="ac-type mono">{{ b.type }}</span>
            </span>
            <AppIcon class="ac-open" name="chevronRight" :size="15" />
          </button>
        </div>

        <div v-if="message.error" class="msg-error">
          <AppIcon name="alert" :size="14" /> {{ message.error }}
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { renderMarkdown } from '../../utils/markdown'
import AppIcon from '../AppIcon.vue'

const props = defineProps({
  message: { type: Object, required: true },
  agentName: { type: String, default: '' }
})
defineEmits(['focus-block'])

const openSteps = ref({})
function toggleStep(i) {
  openSteps.value[i] = !openSteps.value[i]
}

function artifactIcon(t) {
  return {
    table: 'table',
    chart: 'chart',
    diagram: 'branch',
    svg: 'layers',
    html: 'code',
    image: 'file',
    file: 'file'
  }[t] || 'file'
}
function artifactColor(t) {
  return {
    table: 'var(--info)',
    chart: 'var(--primary)',
    diagram: 'var(--accent)',
    svg: 'var(--accent)',
    html: '#b48bff',
    image: 'var(--info)',
    file: 'var(--text-muted)'
  }[t] || 'var(--text-muted)'
}
function artifactLabel(t, i) {
  const m = {
    table: '数据表', chart: '图表', diagram: '流程图', svg: '矢量图', html: '网页', image: '图片', file: '文件'
  }
  return `${m[t] || '内容'} ${i + 1}`
}
</script>

<style scoped>
.msg {
  display: flex;
  gap: 12px;
  padding: 4px 0;
}
.msg.user {
  justify-content: flex-end;
}

/* user bubble */
.u-bubble {
  max-width: 72%;
  padding: 10px 14px;
  border-radius: var(--r-md);
  background: var(--primary-soft);
  border: 1px solid var(--primary-line);
  color: var(--text);
  font-size: var(--fs-base);
  line-height: 1.65;
}
.u-bubble :deep(.md-body) {
  font-size: var(--fs-base);
}
.u-bubble :deep(p) {
  margin: 0.2em 0;
}

/* assistant */
.a-avatar {
  width: 30px;
  height: 30px;
  border-radius: 9px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--accent-soft);
  color: var(--accent);
  border: 1px solid color-mix(in srgb, var(--accent) 30%, transparent);
  margin-top: 2px;
}
.a-avatar.thinking {
  animation: pulse 1.6s ease-in-out infinite;
}
@keyframes pulse {
  0%, 100% { box-shadow: 0 0 0 0 var(--accent-soft); }
  50% { box-shadow: 0 0 0 5px transparent; }
}
.a-body {
  min-width: 0;
  flex: 1;
  max-width: calc(100% - 42px);
}
.a-name {
  font-size: var(--fs-sm);
  font-weight: 600;
  color: var(--text-muted);
  margin-bottom: 5px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.a-live {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  color: var(--accent);
  font-weight: 500;
  font-size: var(--fs-xs);
}
.live-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--accent);
  animation: blink 1s ease-in-out infinite;
}
@keyframes blink {
  0%, 100% { opacity: 0.3; }
  50% { opacity: 1; }
}

/* tool steps */
.steps {
  display: flex;
  flex-direction: column;
  gap: 5px;
  margin: 6px 0 8px;
}
.step {
  position: relative;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  align-self: flex-start;
  max-width: 100%;
  padding: 5px 11px;
  border-radius: var(--r-sm);
  background: var(--surface-2);
  border: 1px solid var(--border);
  font-size: var(--fs-xs);
  color: var(--text-muted);
  cursor: pointer;
  transition: all var(--dur) var(--ease);
}
.step:hover {
  border-color: var(--border-strong);
}
.step.running {
  border-color: color-mix(in srgb, var(--accent) 40%, transparent);
  background: var(--accent-soft);
  color: var(--text);
}
.step.done {
  color: var(--text-muted);
}
.step-icon {
  display: inline-flex;
  color: var(--primary);
}
.step.running .step-icon {
  color: var(--accent);
}
.step-name {
  font-weight: 500;
  color: var(--text);
}
.step-state {
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text-faint);
}
.step-chev {
  color: var(--text-faint);
  transition: transform var(--dur) var(--ease);
}
.step-chev.open {
  transform: rotate(180deg);
}
.step-content {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  width: 440px;
  max-width: 70vw;
  z-index: 5;
  background: var(--surface-3);
  border: 1px solid var(--border-strong);
  border-radius: var(--r-md);
  box-shadow: var(--shadow);
  padding: 4px;
}
.step-content pre {
  margin: 0;
  padding: 10px;
  max-height: 260px;
  overflow: auto;
  font-size: 11px;
  line-height: 1.55;
  white-space: pre-wrap;
  word-break: break-word;
  color: var(--text-muted);
}
.spinner {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 2px solid color-mix(in srgb, var(--accent) 30%, transparent);
  border-top-color: var(--accent);
  animation: spin 0.7s linear infinite;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}

/* text + caret */
.caret {
  display: inline-block;
  width: 7px;
  height: 15px;
  margin-left: 2px;
  vertical-align: text-bottom;
  background: var(--primary);
  border-radius: 1px;
  animation: caret 1s steps(2) infinite;
}
@keyframes caret {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}

.typing {
  display: flex;
  gap: 5px;
  padding: 6px 0;
}
.typing .dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--text-faint);
  animation: typing 1.3s ease-in-out infinite;
}
.typing .dot:nth-child(2) { animation-delay: 0.2s; }
.typing .dot:nth-child(3) { animation-delay: 0.4s; }
@keyframes typing {
  0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
  30% { transform: translateY(-4px); opacity: 1; }
}

/* artifact cards */
.artifacts-inline {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 10px;
}
.artifact-card {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 12px;
  border-radius: var(--r-md);
  background: var(--surface);
  border: 1px solid var(--border-strong);
  cursor: pointer;
  font-family: inherit;
  color: var(--text);
  transition: all var(--dur) var(--ease);
  text-align: left;
}
.artifact-card:hover {
  border-color: var(--primary-line);
  background: var(--primary-soft);
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}
.ac-icon {
  display: flex;
}
.ac-meta {
  display: flex;
  flex-direction: column;
  gap: 1px;
}
.ac-title {
  font-size: var(--fs-sm);
  font-weight: 600;
}
.ac-type {
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-faint);
}
.ac-open {
  color: var(--text-faint);
  margin-left: 4px;
}

.msg-error {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  margin-top: 8px;
  padding: 7px 11px;
  border-radius: var(--r-sm);
  background: var(--danger-soft);
  border: 1px solid color-mix(in srgb, var(--danger) 35%, transparent);
  color: var(--danger);
  font-size: var(--fs-sm);
}
</style>
