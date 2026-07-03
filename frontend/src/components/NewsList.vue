<template>
  <el-card class="news-card">
    <template #header>
      <div class="card-header">
        <span>📰 近期 AI 新闻（原始）</span>
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
      暂无新闻数据
    </div>

    <div v-else class="news-list">
      <div
        v-for="(item, index) in newsList"
        :key="index"
        class="news-item"
      >
        <div class="news-header">
          <h3 class="news-title">{{ item.title }}</h3>
          <div class="news-meta">
            <el-tag size="small" effect="plain">{{ item.source }}</el-tag>
            <span class="news-date">{{ item.published_at }}</span>
          </div>
        </div>
        <p class="news-content">{{ item.content }}</p>
        <div class="news-footer">
          <el-link
            :href="item.url"
            target="_blank"
            type="primary"
            :underline="false"
          >
            阅读原文 <el-icon><ArrowRight /></el-icon>
          </el-link>
        </div>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ArrowRight, Refresh } from '@element-plus/icons-vue'
import type { NewsItem, NewsResponse } from '@/types/news'

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
  gap: 16px;
}

.news-item {
  padding: 16px;
  background: #ffffff;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  transition: box-shadow 0.2s;
}

.news-item:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.news-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 10px;
}

.news-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
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
  color: #909399;
}

.news-content {
  font-size: 14px;
  color: #606266;
  line-height: 1.7;
  margin: 0 0 12px 0;
}

.news-footer {
  display: flex;
  justify-content: flex-end;
}

.empty-tip {
  text-align: center;
  color: #909399;
  padding: 40px 0;
}
</style>
