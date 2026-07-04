<template>
  <el-card class="news-card" shadow="never">
    <template #header>
      <div class="card-header">
        <span>📰 新闻原文</span>
        <div class="header-actions">
          <el-tag v-if="total > 0" type="info">共 {{ total }} 条</el-tag>
          <el-button :icon="Refresh" circle size="small" @click.stop="fetchNews" :loading="loading" />
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
      暂无新闻数据
    </div>

    <div v-else class="news-list">
      <div
        v-for="(item, index) in newsList"
        :key="index"
        class="news-item"
        @click="openDetail(item)"
      >
        <div class="news-date-badge">
          <div class="date-day">{{ formatDay(item.published_at) }}</div>
          <div class="date-month">{{ formatMonth(item.published_at) }}</div>
        </div>
        <div class="news-body">
          <div class="news-header">
            <h3 class="news-title">{{ item.title }}</h3>
            <el-tag size="small" effect="plain">{{ item.source }}</el-tag>
          </div>
          <p class="news-content">{{ item.content }}</p>
          <div class="news-footer">
            <span class="news-full-date">{{ item.published_at }}</span>
            <el-link
              :href="item.url"
              target="_blank"
              type="primary"
              :underline="false"
              @click.stop
            >
              阅读原文 <el-icon><ArrowRight /></el-icon>
            </el-link>
          </div>
        </div>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ArrowRight, Refresh } from '@element-plus/icons-vue'
import type { NewsItem, NewsResponse } from '@/types/news'
import type { StructuredNewsItem } from '@/types/structured_news'

const emit = defineEmits<{
  (e: 'open-detail', item: StructuredNewsItem): void
}>()

const newsList = ref<NewsItem[]>([])
const total = ref(0)
const loading = ref(true)
const error = ref('')

const fetchNews = async () => {
  loading.value = true
  error.value = ''
  try {
    const response = await fetch('/api/news')
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }
    const result: NewsResponse = await response.json()
    if (result.status === 'ok') {
      newsList.value = result.data
      total.value = result.total
    } else {
      throw new Error(result.message || '未知错误')
    }
  } catch (err: any) {
    console.error('获取新闻失败:', err)
    error.value = `获取新闻失败: ${err.message}`
  } finally {
    loading.value = false
  }
}

const formatDay = (dateStr: string) => {
  if (!dateStr) return '--'
  const d = new Date(dateStr)
  return isNaN(d.getTime()) ? '--' : String(d.getDate()).padStart(2, '0')
}

const formatMonth = (dateStr: string) => {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  if (isNaN(d.getTime())) return ''
  return `${d.getMonth() + 1}月`
}

const openDetail = async (item: NewsItem) => {
  // 通过 id 找对应的结构化数据
  try {
    const response = await fetch('/api/structured-news')
    if (!response.ok) return
    const result = await response.json()
    if (result.status === 'ok') {
      const structured = result.data.find((n: StructuredNewsItem) => n.id === item.id || n.title === item.title)
      if (structured) {
        emit('open-detail', structured)
      }
    }
  } catch (e) {
    console.error('查找结构化数据失败:', e)
  }
}

onMounted(() => {
  fetchNews()
})
</script>

<style scoped>
.news-card {
  border: none;
  box-shadow: var(--shadow) !important;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  font-size: 16px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.news-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.news-item {
  display: flex;
  gap: 16px;
  padding: 20px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  transition: all 0.2s ease;
  cursor: pointer;
}

.news-item:hover {
  box-shadow: var(--shadow-md);
  border-color: var(--primary-light);
  transform: translateY(-2px);
}

.news-date-badge {
  flex-shrink: 0;
  width: 56px;
  height: 56px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--primary), var(--primary-dark));
  color: #fff;
  border-radius: var(--radius);
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
}

.date-day {
  font-size: 22px;
  font-weight: 700;
  line-height: 1;
}

.date-month {
  font-size: 11px;
  margin-top: 2px;
  opacity: 0.9;
}

.news-body {
  flex: 1;
  min-width: 0;
}

.news-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 10px;
}

.news-title {
  font-size: 17px;
  font-weight: 600;
  color: var(--text);
  margin: 0;
  flex: 1;
  line-height: 1.5;
}

.news-content {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.7;
  margin: 0 0 14px 0;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.news-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.news-full-date {
  font-size: 13px;
  color: var(--text-muted);
}

.empty-tip {
  text-align: center;
  color: var(--text-secondary);
  padding: 60px 0;
}
</style>
