<template>
  <el-card class="daily-report-card" shadow="never">
    <template #header>
      <div class="card-header">
        <div class="header-left">
          <span class="report-title">📊 AI 领域日报</span>
          <el-tag v-if="report?.date" type="info" size="small">{{ report.date }}</el-tag>
        </div>
        <div class="header-actions">
          <el-button
            v-if="report?.markdown"
            size="small"
            text
            :icon="DocumentCopy"
            @click="copyMarkdown"
          >
            复制 Markdown
          </el-button>
          <el-button
            v-if="report?.date"
            size="small"
            text
            :icon="Download"
            @click="downloadPdf"
          >
            下载 PDF
          </el-button>
          <el-button
            type="primary"
            size="small"
            :loading="loading"
            :icon="Refresh"
            @click="fetchReport(true)"
          >
            {{ loading ? '生成中...' : '重新生成' }}
          </el-button>
        </div>
      </div>
    </template>

    <el-alert
      v-if="error"
      :title="error"
      type="error"
      :closable="false"
      show-icon
      class="report-alert"
    />

    <div v-if="loading && !report" class="loading-wrapper">
      <el-skeleton :rows="10" animated />
    </div>

    <div v-else-if="report?.sections && report.sections.length > 0" class="report-sections">
      <DailyReportSection
        v-for="(section, index) in report.sections"
        :key="index"
        :section="section"
      />
    </div>

    <div v-else-if="report?.html" class="report-content" v-html="report.html"></div>

    <el-empty v-else description="暂无日报，点击上方按钮生成">
      <template #image>
        <div class="empty-illustration">📰</div>
      </template>
    </el-empty>
  </el-card>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Refresh, DocumentCopy, Download } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import DailyReportSection from './DailyReportSection.vue'

interface ReportSection {
  level: number
  title: string
  type: string
  content: string
}

interface DailyReport {
  status: string
  date: string
  markdown: string
  html: string
  sections: ReportSection[]
  generated_at: string
  path: string
}

const report = ref<DailyReport | null>(null)
const loading = ref(false)
const error = ref('')

async function fetchReport(force = false) {
  loading.value = true
  error.value = ''
  try {
    const url = force ? '/api/daily-report/generate?force=true' : '/api/daily-report'
    const response = await fetch(url, force ? { method: 'POST' } : undefined)
    const data = await response.json()
    if (!response.ok) {
      throw new Error(data.detail || '获取日报失败')
    }
    report.value = data
  } catch (err: any) {
    error.value = err.message || '获取日报失败'
    console.error('获取日报失败:', err)
  } finally {
    loading.value = false
  }
}

function copyMarkdown() {
  if (!report.value?.markdown) return
  navigator.clipboard.writeText(report.value.markdown).then(() => {
    ElMessage.success('Markdown 已复制')
  }).catch(() => {
    ElMessage.error('复制失败')
  })
}

function downloadPdf() {
  if (!report.value?.date) return
  const date = report.value.date
  window.open(`/api/daily-report/pdf?date=${date}`, '_blank')
}

onMounted(() => {
  fetchReport(false)
})

defineExpose({
  fetchReport,
})
</script>

<style scoped>
.daily-report-card {
  border: none;
  box-shadow: var(--shadow) !important;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.report-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.report-alert {
  margin-bottom: 16px;
  border-radius: 8px;
}

.loading-wrapper {
  padding: 20px;
}

.empty-illustration {
  font-size: 48px;
  opacity: 0.5;
  margin-bottom: 12px;
}

.report-sections {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.report-content {
  font-size: 15px;
  line-height: 1.85;
  color: var(--text);
  padding: 8px 4px;
}

.report-content :deep(h1) {
  font-size: 24px;
  font-weight: 700;
  margin: 24px 0 16px;
  padding-bottom: 10px;
  color: var(--text);
  border-bottom: 2px solid var(--primary);
}

.report-content :deep(h2) {
  font-size: 19px;
  font-weight: 600;
  margin: 22px 0 12px;
  color: var(--primary-dark);
}

.report-content :deep(h3) {
  font-size: 16px;
  font-weight: 600;
  margin: 16px 0 8px;
  color: var(--text);
}
</style>
