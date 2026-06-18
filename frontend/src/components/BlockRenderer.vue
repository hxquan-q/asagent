<template>
  <div class="block-renderer">
    <template v-if="block.type === 'text'">
      <div class="md-body" v-html="renderedText"></div>
    </template>

    <template v-else-if="block.type === 'table'">
      <div v-if="block.title" class="block-title">{{ block.title }}</div>
      <el-table
        :data="tableRows"
        border
        size="small"
        style="width: 100%"
        :max-height="480"
      >
        <el-table-column
          v-for="col in tableColumns"
          :key="col.name"
          :prop="col.name"
          :label="col.name"
          min-width="120"
        >
          <template #default="{ row }">
            {{ formatCell(row[col.name]) }}
          </template>
        </el-table-column>
      </el-table>
    </template>

    <template v-else-if="block.type === 'chart'">
      <div v-if="block.title" class="block-title">{{ block.title }}</div>
      <div ref="chartEl" class="chart-box"></div>
    </template>

    <template v-else-if="block.type === 'diagram'">
      <div v-if="block.title" class="block-title">{{ block.title }}</div>
      <div ref="mermaidEl" class="mermaid-box" v-html="mermaidSvg"></div>
    </template>

    <template v-else-if="block.type === 'svg'">
      <div v-if="block.title" class="block-title">{{ block.title }}</div>
      <div class="svg-box" v-html="block.content"></div>
    </template>

    <template v-else-if="block.type === 'html'">
      <div v-if="block.title" class="block-title">{{ block.title }}</div>
      <iframe
        class="html-frame"
        sandbox="allow-scripts allow-same-origin"
        :srcdoc="sanitizedHtml"
      ></iframe>
    </template>

    <template v-else-if="block.type === 'image'">
      <div v-if="block.title" class="block-title">{{ block.title }}</div>
      <img :src="block.url" :alt="block.alt || block.title || ''" class="block-image" />
    </template>

    <template v-else-if="block.type === 'file'">
      <div class="file-block">
        <el-link type="primary" :href="block.url" target="_blank" :underline="false">
          <el-icon><Document /></el-icon>
          <span class="file-name">{{ block.filename }}</span>
          <span v-if="block.size" class="file-size">({{ humanSize(block.size) }})</span>
        </el-link>
      </div>
    </template>

    <template v-else-if="block.type === 'data'">
      <el-collapse>
        <el-collapse-item title="原始数据" name="data">
          <pre class="data-pre">{{ typeof block.content === 'string' ? block.content : JSON.stringify(block.content, null, 2) }}</pre>
        </el-collapse-item>
      </el-collapse>
    </template>

    <template v-else>
      <el-alert
        :title="`未知内容块类型: ${block.type}`"
        type="warning"
        :closable="false"
      />
    </template>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, ref, watch } from 'vue'
import * as echarts from 'echarts'
import DOMPurify from 'dompurify'
import mermaid from 'mermaid'
import { renderMarkdown } from '../utils/markdown'

const props = defineProps({
  block: { type: Object, required: true }
})

const renderedText = computed(() => renderMarkdown(props.block.content || ''))
const sanitizedHtml = computed(() =>
  DOMPurify.sanitize(props.block.content || '', { ADD_ATTR: ['target'] })
)

const tableColumns = computed(() => props.block.columns || [])
const tableRows = computed(() => props.block.rows || [])

function formatCell(v) {
  if (v === null || v === undefined) return ''
  if (typeof v === 'object') return JSON.stringify(v)
  return String(v)
}

function humanSize(n) {
  if (!n && n !== 0) return ''
  const units = ['B', 'KB', 'MB', 'GB']
  let i = 0
  let size = Number(n)
  while (size >= 1024 && i < units.length - 1) {
    size /= 1024
    i++
  }
  return `${size.toFixed(1)} ${units[i]}`
}

// ----- ECharts -----
const chartEl = ref(null)
let chartInstance = null

async function renderChart() {
  if (props.block.type !== 'chart') return
  await nextTick()
  if (!chartEl.value) return
  if (!chartInstance) {
    chartInstance = echarts.init(chartEl.value)
  }
  try {
    chartInstance.setOption(props.block.spec || {}, true)
  } catch (e) {
    // ignore
  }
}

// ----- Mermaid -----
const mermaidEl = ref(null)
const mermaidSvg = ref('')
let mermaidInited = false

async function renderMermaid() {
  if (props.block.type !== 'diagram') return
  if (!mermaidInited) {
    mermaid.initialize({ startOnLoad: false, securityLevel: 'loose', theme: 'default' })
    mermaidInited = true
  }
  const source = props.block.source || ''
  if (!source) return
  try {
    const id = `mmd-${Math.random().toString(36).slice(2, 10)}`
    const { svg } = await mermaid.render(id, source)
    mermaidSvg.value = svg
  } catch (e) {
    mermaidSvg.value = `<pre style="color:#c00">Mermaid 渲染失败: ${escapeHtml(e.message || String(e))}\n\n${escapeHtml(source)}</pre>`
  }
}

function escapeHtml(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
}

watch(
  () => props.block,
  () => {
    if (props.block.type === 'chart') renderChart()
    if (props.block.type === 'diagram') renderMermaid()
  },
  { immediate: true, deep: true }
)

function onResize() {
  chartInstance && chartInstance.resize()
}
window.addEventListener('resize', onResize)

onBeforeUnmount(() => {
  window.removeEventListener('resize', onResize)
  chartInstance && chartInstance.dispose()
})
</script>

<style scoped>
.block-renderer {
  margin: 6px 0;
}
.block-title {
  font-weight: 600;
  margin: 4px 0 6px;
  font-size: 14px;
  color: #303133;
}
.chart-box {
  width: 100%;
  height: 360px;
}
.mermaid-box,
.svg-box {
  width: 100%;
  overflow: auto;
  background: #fff;
  border-radius: 6px;
}
.mermaid-box :deep(svg),
.svg-box :deep(svg) {
  max-width: 100%;
  height: auto;
}
.html-frame {
  width: 100%;
  min-height: 320px;
  border: 1px solid #ebeef5;
  border-radius: 6px;
  background: #fff;
}
.block-image {
  max-width: 100%;
  border-radius: 6px;
}
.file-block {
  padding: 4px 0;
}
.file-name {
  margin: 0 6px;
}
.file-size {
  color: #909399;
  font-size: 12px;
}
.data-pre {
  background: #1e1e1e;
  color: #e6e6e6;
  padding: 10px;
  border-radius: 6px;
  overflow: auto;
  font-size: 12px;
}
</style>
