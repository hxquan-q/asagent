<template>
  <section class="canvas" :class="{ wide }">
    <header class="canvas-head">
      <div class="ch-left">
        <AppIcon name="panelRight" :size="15" />
        <span class="ch-title">画布</span>
        <span v-if="chat.artifacts.length" class="ch-count">{{ chat.activeArtifact + 1 }}/{{ chat.artifacts.length }}</span>
      </div>
      <div class="ch-right">
        <button class="icon-btn" :title="wide ? '收起' : '放大'" @click="wide = !wide">
          <AppIcon :name="wide ? 'fold' : 'expand'" :size="15" />
        </button>
        <button class="icon-btn" title="关闭画布" @click="ui.canvasOpen = false">
          <AppIcon name="close" :size="15" />
        </button>
      </div>
    </header>

    <nav v-if="chat.artifacts.length > 1" class="tabs">
      <button
        v-for="(a, i) in chat.artifacts"
        :key="i"
        class="tab"
        :class="{ active: i === chat.activeArtifact }"
        @click="chat.selectArtifact(i)"
      >
        <AppIcon :name="iconFor(a.block.type)" :size="13" />
        <span>{{ a.title }}</span>
      </button>
    </nav>

    <div class="canvas-body">
      <div v-if="!chat.artifacts.length" class="canvas-empty">
        <div class="ce-icon"><AppIcon name="layers" :size="26" /></div>
        <p class="ce-title">还没有可展示的内容</p>
        <span class="ce-sub">Agent 生成的图表、表格、流程图和文件会在这里呈现，便于查看与对比。</span>
      </div>

      <div v-else-if="active" class="artifact-view">
        <div v-if="active.block.title" class="artifact-heading">{{ active.block.title }}</div>
        <BlockRenderer :block="active.block" />
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useChatStore } from '../../stores/chat'
import { useUiStore } from '../../stores/ui'
import AppIcon from '../AppIcon.vue'
import BlockRenderer from '../BlockRenderer.vue'

const chat = useChatStore()
const ui = useUiStore()
const wide = ref(false)

const active = computed(() =>
  chat.activeArtifact >= 0 ? chat.artifacts[chat.activeArtifact] : null
)

function iconFor(t) {
  return { table: 'table', chart: 'chart', diagram: 'branch', svg: 'layers', html: 'code', image: 'file', file: 'file' }[t] || 'file'
}
</script>

<style scoped>
.canvas {
  width: 420px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  background: var(--surface);
  border-left: 1px solid var(--border);
  overflow: hidden;
  position: relative;
}
.canvas.wide {
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  width: min(1080px, 72vw);
  z-index: 20;
  box-shadow: var(--shadow-lg);
}

.canvas-head {
  height: 50px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 12px;
  border-bottom: 1px solid var(--border);
}
.ch-left {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-muted);
}
.ch-title {
  font-weight: 600;
  color: var(--text);
  font-size: var(--fs-sm);
}
.ch-count {
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--text-faint);
  background: var(--surface-2);
  padding: 1px 6px;
  border-radius: var(--r-xs);
}
.ch-right {
  display: flex;
  gap: 2px;
}
.icon-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  border-radius: var(--r-sm);
  border: none;
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
  transition: all var(--dur) var(--ease);
}
.icon-btn:hover {
  background: var(--surface-2);
  color: var(--text);
}

.tabs {
  display: flex;
  gap: 4px;
  padding: 8px 12px;
  border-bottom: 1px solid var(--border);
  overflow-x: auto;
  flex-shrink: 0;
}
.tab {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 11px;
  border-radius: var(--r-sm);
  border: 1px solid var(--border);
  background: var(--surface-2);
  color: var(--text-muted);
  font-family: inherit;
  font-size: var(--fs-xs);
  white-space: nowrap;
  cursor: pointer;
  transition: all var(--dur) var(--ease);
}
.tab:hover {
  color: var(--text);
}
.tab.active {
  background: var(--primary-soft);
  border-color: var(--primary-line);
  color: var(--primary-strong);
}

.canvas-body {
  flex: 1;
  overflow: auto;
  padding: 16px;
}
.canvas-empty {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  gap: 8px;
  padding: 30px;
}
.ce-icon {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--surface-2);
  color: var(--text-faint);
  margin-bottom: 4px;
}
.ce-title {
  margin: 0;
  font-size: var(--fs-md);
  font-weight: 600;
}
.ce-sub {
  font-size: var(--fs-sm);
  color: var(--text-muted);
  max-width: 280px;
  line-height: 1.6;
}

.artifact-view {
  min-width: 0;
}
.artifact-heading {
  font-family: var(--font-display);
  font-size: var(--fs-lg);
  font-weight: 600;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border);
}
</style>
