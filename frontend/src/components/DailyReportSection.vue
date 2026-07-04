<template>
  <div class="report-section" :class="`type-${section.type}`">
    <div class="section-header">
      <div class="section-icon">{{ icon }}</div>
      <div class="section-title">{{ section.title }}</div>
      <div class="section-badge">{{ badgeText }}</div>
    </div>
    <div class="section-body" v-html="renderedContent"></div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { marked } from 'marked'

interface ReportSection {
  level: number
  title: string
  type: string
  content: string
}

const props = defineProps<{
  section: ReportSection
}>()

const renderedContent = computed(() => {
  if (!props.section.content) return ''
  return marked.parse(props.section.content, { breaks: true })
})

const icon = computed(() => {
  const icons: Record<string, string> = {
    overview: '📰',
    hotspots: '🔥',
    analysis: '🔍',
    trends: '📈',
    risks_opportunities: '⚠️',
    summary: '📝',
    others: '📄',
  }
  return icons[props.section.type] || '📄'
})

const badgeText = computed(() => {
  const labels: Record<string, string> = {
    overview: '概览',
    hotspots: '热点',
    analysis: '深度分析',
    trends: '趋势',
    risks_opportunities: '风险与机会',
    summary: '总结',
    others: '其他',
  }
  return labels[props.section.type] || '内容'
})
</script>

<style scoped>
.report-section {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  overflow: hidden;
  transition: box-shadow 0.2s ease;
}

.report-section:hover {
  box-shadow: var(--shadow-md);
}

.report-section.type-hotspots {
  border-left: 4px solid #2563eb;
}

.report-section.type-analysis {
  border-left: 4px solid #7c3aed;
}

.report-section.type-trends {
  border-left: 4px solid #16a34a;
}

.report-section.type-risks_opportunities {
  border-left: 4px solid #ea580c;
}

.report-section.type-overview {
  border-left: 4px solid #0891b2;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 16px 20px;
  background: var(--bg-soft);
  border-bottom: 1px solid var(--border);
}

.section-icon {
  font-size: 20px;
}

.section-title {
  flex: 1;
  font-size: 17px;
  font-weight: 600;
  color: var(--text);
}

.section-badge {
  font-size: 12px;
  padding: 4px 10px;
  border-radius: 20px;
  background: var(--bg-card);
  color: var(--text-secondary);
  border: 1px solid var(--border);
}

.section-body {
  padding: 20px;
  font-size: 14px;
  line-height: 1.8;
  color: var(--text);
}

.section-body :deep(h1),
.section-body :deep(h2),
.section-body :deep(h3) {
  color: var(--text);
  margin: 16px 0 10px;
}

.section-body :deep(h3) {
  font-size: 15px;
  font-weight: 600;
}

.section-body :deep(p) {
  margin: 8px 0;
}

.section-body :deep(ul),
.section-body :deep(ol) {
  padding-left: 22px;
  margin: 8px 0;
}

.section-body :deep(li) {
  margin: 6px 0;
}

.section-body :deep(strong) {
  color: var(--primary-dark);
  font-weight: 600;
}

.section-body :deep(hr) {
  border: none;
  border-top: 1px solid var(--border);
  margin: 16px 0;
}

.section-body :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 12px 0;
  border: 1px solid var(--border);
  border-radius: 8px;
  overflow: hidden;
}

.section-body :deep(th),
.section-body :deep(td) {
  padding: 8px 12px;
  text-align: left;
  border-bottom: 1px solid var(--border);
}

.section-body :deep(th) {
  background: var(--bg-soft);
  font-weight: 600;
}

.section-body :deep(blockquote) {
  border-left: 3px solid var(--accent);
  padding: 10px 14px;
  margin: 12px 0;
  background: var(--accent-light);
  border-radius: 0 8px 8px 0;
  color: var(--text-secondary);
}

.section-body :deep(code) {
  background: var(--bg-soft);
  color: var(--primary-dark);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Consolas', monospace;
  font-size: 13px;
}

.section-body :deep(pre) {
  background: var(--bg-soft);
  padding: 12px;
  border-radius: 8px;
  overflow-x: auto;
  border: 1px solid var(--border);
}
</style>
