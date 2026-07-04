<template>
  <el-card class="news-card">
    <template #header>
      <div class="card-header">
        <span>🧠 AI 结构化分析报告</span>
        <div class="header-actions">
          <el-tag v-if="total > 0" type="success">共 {{ total }} 条</el-tag>
          <el-button :icon="Refresh" circle size="small" @click="fetchNews" :loading="loading" />
        </div>
      </div>
    </template>

    <el-skeleton :rows="6" animated v-if="loading" />

    <el-alert
      v-else-if="error"
      :title="error"
      type="error"
      :closable="false"
      show-icon
    />

    <div v-else-if="newsList.length === 0" class="empty-tip">
      暂无结构化新闻数据
    </div>

    <div v-else class="news-list">
      <div
        v-for="(item, index) in newsList"
        :key="index"
        class="news-item"
        @click="openDetail(item)"
      >
        <div class="news-header">
          <h3 class="news-title">{{ item.title }}</h3>
          <div class="news-meta">
            <el-tag size="small" type="primary">{{ item.category }}</el-tag>
            <el-tag size="small" effect="plain">{{ item.source.name }}</el-tag>
            <span class="news-date">{{ item.publish_time.split('T')[0] }}</span>
          </div>
        </div>

        <div class="section">
          <div class="section-title">🏷️ 标签</div>
          <div class="tags">
            <el-tag v-for="tag in item.tags" :key="tag" size="small" class="tag-item">
              {{ tag }}
            </el-tag>
          </div>
        </div>

        <div class="section">
          <div class="section-title">📝 AI 摘要</div>
          <p class="ai-summary">{{ item.ai_summary }}</p>
        </div>

        <div class="section">
          <div class="section-title">💡 AI 观点</div>
          <p class="viewpoint">{{ item.ai_opinion.viewpoint }}</p>
          <div class="opinion-tags">
            <el-tag :type="significanceType(item.ai_opinion.significance)" size="small">
              重要性: {{ item.ai_opinion.significance }}
            </el-tag>
            <el-tag :type="impactType(item.ai_opinion.impact_direction)" size="small">
              影响: {{ item.ai_opinion.impact_direction }}
            </el-tag>
          </div>
        </div>

        <div class="section" v-if="item.entities.length > 0">
          <div class="section-title">🏢 关键实体</div>
          <div class="tags">
            <el-tag v-for="entity in item.entities" :key="entity.name" type="info" size="small" class="tag-item">
              {{ entity.name }} <span class="entity-type">({{ entity.type }})</span>
            </el-tag>
          </div>
        </div>

        <div class="section" v-if="item.technologies.length > 0">
          <div class="section-title">🔧 涉及技术</div>
          <div class="tags">
            <el-tag v-for="tech in item.technologies" :key="tech" type="warning" size="small" class="tag-item">
              {{ tech }}
            </el-tag>
          </div>
        </div>

        <div class="section">
          <div class="section-title">😊 情感分析</div>
          <div class="sentiment">
            <el-tag :type="sentimentType(item.sentiment.overall)" size="small">
              {{ item.sentiment.overall }} ({{ item.sentiment.score }})
            </el-tag>
            <span class="sentiment-reason">{{ item.sentiment.reason }}</span>
          </div>
        </div>

        <div class="section" v-if="item.key_points.length > 0">
          <div class="section-title">📌 核心要点</div>
          <ul class="key-points">
            <li v-for="(point, idx) in item.key_points" :key="idx">{{ point }}</li>
          </ul>
        </div>

        <div class="news-footer">
          <el-link
            :href="item.source.url"
            target="_blank"
            type="primary"
            :underline="false"
          >
            阅读原文 <el-icon><ArrowRight /></el-icon>
          </el-link>
        </div>
      </div>
    </div>

    <NewsDetailDrawer v-model="detailVisible" :news="selectedNews" />
  </el-card>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ArrowRight, Refresh } from '@element-plus/icons-vue'
import NewsDetailDrawer from '@/components/NewsDetailDrawer.vue'
import type { StructuredNewsItem, StructuredNewsResponse } from '@/types/structured_news'

const newsList = ref<StructuredNewsItem[]>([])
const total = ref(0)
const loading = ref(true)
const error = ref('')
const detailVisible = ref(false)
const selectedNews = ref<StructuredNewsItem | null>(null)

const openDetail = (item: StructuredNewsItem) => {
  selectedNews.value = item
  detailVisible.value = true
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

const fetchNews = async () => {
  loading.value = true
  error.value = ''
  try {
    const response = await fetch('/api/structured-news')
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }
    const result: StructuredNewsResponse = await response.json()
    if (result.status === 'ok') {
      newsList.value = result.data
      total.value = result.total
    } else {
      throw new Error(result.message || '未知错误')
    }
  } catch (err: any) {
    console.error('获取结构化新闻失败:', err)
    error.value = `获取结构化新闻失败: ${err.message}`
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchNews()
})
</script>

<style scoped>
.news-card {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.news-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.news-item {
  padding: 20px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  transition: all 0.2s ease;
  cursor: pointer;
  position: relative;
}

.news-item:hover {
  box-shadow: var(--shadow-md);
  border-color: var(--primary-light);
  transform: translateY(-2px);
}

.news-item::after {
  content: '点击查看详情';
  position: absolute;
  top: 20px;
  right: 20px;
  font-size: 12px;
  color: var(--primary);
  opacity: 0;
  transition: opacity 0.2s;
}

.news-item:hover::after {
  opacity: 1;
}

.news-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 16px;
}

.news-title {
  font-size: 17px;
  font-weight: 600;
  color: var(--text);
  margin: 0;
  flex: 1;
  line-height: 1.5;
}

.news-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.news-date {
  font-size: 13px;
  color: var(--text-muted);
}

.section {
  margin-bottom: 14px;
}

.section-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--primary-dark);
  margin-bottom: 6px;
}

.ai-summary {
  font-size: 14px;
  color: var(--text);
  line-height: 1.7;
  margin: 0;
  background: var(--bg-soft);
  padding: 10px;
  border-radius: 6px;
}

.viewpoint {
  font-size: 14px;
  color: var(--text);
  line-height: 1.6;
  margin: 0 0 8px 0;
}

.opinion-tags {
  display: flex;
  gap: 8px;
}

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-item {
  margin: 0;
}

.entity-type {
  font-size: 11px;
  color: var(--text-muted);
}

.sentiment {
  display: flex;
  align-items: center;
  gap: 10px;
}

.sentiment-reason {
  font-size: 13px;
  color: var(--text-secondary);
}

.key-points {
  margin: 0;
  padding-left: 18px;
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.8;
}

.news-footer {
  display: flex;
  justify-content: flex-end;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--border);
}

.empty-tip {
  text-align: center;
  color: var(--text-secondary);
  padding: 40px 0;
}
</style>
