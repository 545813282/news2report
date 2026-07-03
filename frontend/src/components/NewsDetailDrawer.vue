<template>
  <el-drawer
    v-model="visible"
    :title="news?.title"
    size="85%"
    direction="rtl"
    destroy-on-close
    class="news-detail-drawer"
  >
    <div v-if="news" class="detail-container">
      <!-- 顶部元信息 -->
      <div class="detail-header">
        <div class="meta-row">
          <el-tag type="primary" size="small">{{ news.category }}</el-tag>
          <el-tag size="small" effect="plain">{{ news.source.name }}</el-tag>
          <span class="publish-time">{{ formatDate(news.publish_time) }}</span>
        </div>
        <div class="tags-row">
          <el-tag
            v-for="tag in news.tags"
            :key="tag"
            type="info"
            size="small"
            class="header-tag"
          >
            {{ tag }}
          </el-tag>
        </div>
      </div>

      <!-- 左右对比区域 -->
      <el-row :gutter="24" class="detail-content">
        <!-- 左侧：原文 -->
        <el-col :span="12" class="left-panel">
          <div class="panel-title">
            <el-icon><Document /></el-icon>
            <span>原文内容</span>
          </div>
          <div class="original-text">
            {{ news.original_text }}
          </div>
          <div v-if="news.translated_text" class="translated-text">
            <div class="sub-title">英文翻译</div>
            {{ news.translated_text }}
          </div>
          <div class="source-link">
            <el-link :href="news.source.url" target="_blank" type="primary">
              查看原文链接 <el-icon><Link /></el-icon>
            </el-link>
          </div>
        </el-col>

        <!-- 右侧：结构化 AI 分析 -->
        <el-col :span="12" class="right-panel">
          <div class="panel-title">
            <el-icon><Cpu /></el-icon>
            <span>结构化 AI 分析</span>
          </div>

          <!-- AI 摘要 -->
          <div class="analysis-section">
            <div class="section-title">📝 AI 摘要</div>
            <div class="ai-summary">{{ news.ai_summary }}</div>
          </div>

          <!-- AI 观点 -->
          <div class="analysis-section">
            <div class="section-title">💡 AI 观点</div>
            <p class="viewpoint">{{ news.ai_opinion.viewpoint }}</p>
            <div class="opinion-tags">
              <el-tag :type="significanceType(news.ai_opinion.significance)" size="small">
                重要性：{{ news.ai_opinion.significance }}
              </el-tag>
              <el-tag :type="impactType(news.ai_opinion.impact_direction)" size="small">
                影响方向：{{ news.ai_opinion.impact_direction }}
              </el-tag>
            </div>
          </div>

          <!-- 事件类型 -->
          <div class="analysis-section">
            <div class="section-title">📂 事件类型</div>
            <el-tag type="warning" size="small">{{ news.event_type }}</el-tag>
          </div>

          <!-- 关键实体 -->
          <div class="analysis-section" v-if="news.entities.length > 0">
            <div class="section-title">🏢 关键实体</div>
            <div class="entity-list">
              <el-tag
                v-for="entity in news.entities"
                :key="entity.name"
                type="info"
                size="small"
                class="entity-tag"
              >
                {{ entity.name }}
                <span class="entity-type">({{ entity.type }})</span>
              </el-tag>
            </div>
          </div>

          <!-- 涉及技术 -->
          <div class="analysis-section" v-if="news.technologies.length > 0">
            <div class="section-title">🔧 涉及技术</div>
            <div class="tech-list">
              <el-tag
                v-for="tech in news.technologies"
                :key="tech"
                type="warning"
                size="small"
                class="tech-tag"
              >
                {{ tech }}
              </el-tag>
            </div>
          </div>

          <!-- 情感分析 -->
          <div class="analysis-section">
            <div class="section-title">😊 情感分析</div>
            <div class="sentiment-row">
              <el-tag :type="sentimentType(news.sentiment.overall)" size="small">
                {{ news.sentiment.overall }} {{ news.sentiment.score }}
              </el-tag>
              <span class="sentiment-reason">{{ news.sentiment.reason }}</span>
            </div>
          </div>

          <!-- 核心要点 -->
          <div class="analysis-section" v-if="news.key_points.length > 0">
            <div class="section-title">📌 核心要点</div>
            <ol class="key-points">
              <li v-for="(point, idx) in news.key_points" :key="idx">{{ point }}</li>
            </ol>
          </div>

          <!-- 实体关系 -->
          <div class="analysis-section" v-if="news.relations.length > 0">
            <div class="section-title">🔗 实体关系</div>
            <div class="relation-list">
              <div v-for="(rel, idx) in news.relations" :key="idx" class="relation-item">
                <span class="relation-subject">{{ rel.subject }}</span>
                <span class="relation-predicate">{{ rel.predicate }}</span>
                <span class="relation-object">{{ rel.object }}</span>
              </div>
            </div>
          </div>

          <!-- 处理元数据 -->
          <div class="analysis-section processing-meta">
            <div class="section-title">⚙️ 处理信息</div>
            <div class="meta-grid">
              <div><span class="meta-label">模型：</span>{{ news.processing.model }}</div>
              <div><span class="meta-label">批次：</span>{{ news.processing.batch_id }}</div>
              <div><span class="meta-label">时间：</span>{{ formatDate(news.processing.extracted_at) }}</div>
              <div><span class="meta-label">状态：</span>{{ news.processing.status }}</div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>
  </el-drawer>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Document, Cpu, Link } from '@element-plus/icons-vue'
import type { StructuredNewsItem } from '@/types/structured_news'

const props = defineProps<{
  modelValue: boolean
  news: StructuredNewsItem | null
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
}>()

const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value),
})

const formatDate = (dateStr: string) => {
  if (!dateStr) return ''
  return dateStr.split('T')[0]
}

const significanceType = (significance: string) => {
  const map: Record<string, any> = { '重大': 'danger', '重要': 'warning', '一般': 'info', '轻微': '' }
  return map[significance] || ''
}

const impactType = (impact: string) => {
  const map: Record<string, any> = { '积极': 'success', '消极': 'danger', '中性': 'info', '复杂': 'warning' }
  return map[impact] || ''
}

const sentimentType = (sentiment: string) => {
  const map: Record<string, any> = { 'positive': 'success', 'negative': 'danger', 'neutral': 'info', 'mixed': 'warning' }
  return map[sentiment] || ''
}
</script>

<style scoped>
.detail-container {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.detail-header {
  padding-bottom: 16px;
  border-bottom: 1px solid #ebeef5;
  margin-bottom: 16px;
}

.meta-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.publish-time {
  font-size: 13px;
  color: #909399;
}

.tags-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.header-tag {
  margin: 0;
}

.detail-content {
  flex: 1;
  min-height: 0;
}

.left-panel,
.right-panel {
  height: calc(100vh - 200px);
  overflow-y: auto;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
}

.panel-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 16px;
  padding-bottom: 10px;
  border-bottom: 2px solid #409eff;
}

.original-text {
  font-size: 15px;
  line-height: 1.8;
  color: #303133;
  white-space: pre-wrap;
  background: #ffffff;
  padding: 16px;
  border-radius: 6px;
  border-left: 4px solid #409eff;
}

.translated-text {
  margin-top: 16px;
  background: #ffffff;
  padding: 16px;
  border-radius: 6px;
  border-left: 4px solid #67c23a;
}

.sub-title {
  font-size: 13px;
  font-weight: 600;
  color: #67c23a;
  margin-bottom: 8px;
}

.source-link {
  margin-top: 16px;
}

.analysis-section {
  margin-bottom: 20px;
  background: #ffffff;
  padding: 14px;
  border-radius: 6px;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: #606266;
  margin-bottom: 10px;
}

.ai-summary {
  font-size: 14px;
  line-height: 1.7;
  color: #303133;
}

.viewpoint {
  font-size: 14px;
  line-height: 1.6;
  color: #303133;
  margin: 0 0 10px 0;
}

.opinion-tags {
  display: flex;
  gap: 10px;
}

.entity-list,
.tech-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.entity-tag,
.tech-tag {
  margin: 0;
}

.entity-type {
  font-size: 11px;
  color: #909399;
}

.sentiment-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.sentiment-reason {
  font-size: 13px;
  color: #606266;
}

.key-points {
  margin: 0;
  padding-left: 18px;
  font-size: 14px;
  line-height: 1.8;
  color: #606266;
}

.relation-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.relation-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  padding: 8px 12px;
  background: #f5f7fa;
  border-radius: 4px;
}

.relation-subject {
  font-weight: 600;
  color: #409eff;
}

.relation-predicate {
  color: #606266;
}

.relation-object {
  font-weight: 600;
  color: #67c23a;
}

.processing-meta {
  background: #f0f9ff;
}

.meta-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  font-size: 13px;
  color: #606266;
}

.meta-label {
  color: #909399;
}
</style>
