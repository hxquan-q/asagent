<template>
  <div class="composer">
    <div class="composer-box" :class="{ focused }">
      <textarea
        ref="ta"
        v-model="text"
        class="composer-input"
        rows="1"
        :placeholder="placeholder"
        :disabled="!chat.agentId"
        @focus="focused = true"
        @blur="focused = false"
        @input="autoGrow"
        @keydown.enter.exact.prevent="onSend"
      ></textarea>
      <div class="composer-actions">
        <span class="hint mono">{{ chat.agentId ? (chat.currentAgent?.name || 'Agent') : '未选择 Agent' }}</span>
        <button
          v-if="!chat.sending"
          class="send-btn"
          :disabled="!chat.agentId || !text.trim()"
          @click="onSend"
        >
          <AppIcon name="send" :size="16" />
          <span>发送</span>
        </button>
        <button v-else class="stop-btn" @click="chat.stop()">
          <AppIcon name="stop" :size="14" />
          <span>停止</span>
        </button>
      </div>
    </div>
    <div class="composer-foot">
      <span class="kbd-hint">
        <kbd>Enter</kbd> 发送 · <kbd>Shift</kbd>+<kbd>Enter</kbd> 换行
      </span>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, ref } from 'vue'
import { useChatStore } from '../../stores/chat'
import AppIcon from '../AppIcon.vue'

const chat = useChatStore()
const text = ref('')
const ta = ref(null)
const focused = ref(false)

const placeholder = computed(() =>
  chat.agentId ? `向 ${chat.currentAgent?.name || 'Agent'} 提问…` : '请先选择一个 Agent'
)

function autoGrow() {
  const el = ta.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 200) + 'px'
}

async function onSend() {
  const v = text.value.trim()
  if (!v || chat.sending || !chat.agentId) return
  text.value = ''
  await nextTick()
  autoGrow()
  await chat.send(v)
}

defineExpose({ focus: () => ta.value?.focus() })
</script>

<style scoped>
.composer {
  padding: 12px 0 4px;
}
.composer-box {
  border: 1px solid var(--border-strong);
  border-radius: var(--r-lg);
  background: var(--surface);
  padding: 10px 10px 8px;
  transition: border-color var(--dur) var(--ease), box-shadow var(--dur) var(--ease);
}
.composer-box.focused {
  border-color: var(--primary-line);
  box-shadow: 0 0 0 3px var(--primary-soft);
}
.composer-input {
  width: 100%;
  border: none;
  outline: none;
  resize: none;
  background: transparent;
  color: var(--text);
  font-family: var(--font-sans);
  font-size: var(--fs-base);
  line-height: 1.6;
  max-height: 200px;
  padding: 4px 6px;
}
.composer-input::placeholder {
  color: var(--text-faint);
}
.composer-input:disabled {
  cursor: not-allowed;
}
.composer-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 4px 0;
}
.hint {
  font-size: var(--fs-xs);
  color: var(--text-faint);
}
.send-btn,
.stop-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 7px 15px;
  border-radius: var(--r-sm);
  border: none;
  font-family: inherit;
  font-size: var(--fs-sm);
  font-weight: 600;
  cursor: pointer;
  transition: all var(--dur) var(--ease);
}
.send-btn {
  background: var(--primary);
  color: #06281c;
}
.send-btn:hover:not(:disabled) {
  background: var(--primary-strong);
}
.send-btn:disabled {
  background: var(--surface-3);
  color: var(--text-faint);
  cursor: not-allowed;
}
.stop-btn {
  background: var(--danger-soft);
  color: var(--danger);
  border: 1px solid color-mix(in srgb, var(--danger) 35%, transparent);
}
.composer-foot {
  text-align: center;
  margin-top: 7px;
}
.kbd-hint {
  font-size: 11px;
  color: var(--text-faint);
}
kbd {
  font-family: var(--font-mono);
  font-size: 10px;
  padding: 1px 5px;
  border-radius: 4px;
  border: 1px solid var(--border-strong);
  background: var(--surface-2);
  color: var(--text-muted);
}
</style>
