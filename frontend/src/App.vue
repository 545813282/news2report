<template>
  <div class="app-container">
    <el-container>
      <el-header class="app-header">
        <div class="header-content">
          <el-icon size="24"><TrendCharts /></el-icon>
          <h1>AI舆情分析日报系统</h1>
        </div>
      </el-header>

      <el-main>
        <el-row :gutter="20">
          <el-col :span="24">
            <el-card class="welcome-card">
              <template #header>
                <div class="card-header">
                  <span>项目架构</span>
                </div>
              </template>
              <div class="pipeline">
                <div class="pipeline-item">
                  <div class="item-title">阶段1: 数据层</div>
                  <div class="item-desc">获取AI新闻数据、数据清洗去重、存入JSON</div>
                </div>
                <div class="pipeline-arrow">→</div>
                <div class="pipeline-item">
                  <div class="item-title">阶段2: 结构化层</div>
                  <div class="item-desc">Schema设计、逐条结构化抽取、数据校验、存入JSON</div>
                </div>
                <div class="pipeline-arrow">→</div>
                <div class="pipeline-item">
                  <div class="item-title">阶段3: 分析层</div>
                  <div class="item-desc">热点聚合排序、事件深度分析、趋势判断、风险/机会识别</div>
                </div>
                <div class="pipeline-arrow">→</div>
                <div class="pipeline-item">
                  <div class="item-title">阶段4: 输出层</div>
                  <div class="item-desc">日报Markdown生成、可视化图表生成、HTML页面渲染、结果展示</div>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>

        <el-row :gutter="20" class="mt-20">
          <el-col :span="12">
            <el-card>
              <template #header>
                <div class="card-header">
                  <span>后端环境</span>
                  <el-tag type="success">Python 3.11</el-tag>
                </div>
              </template>
              <p>虚拟环境: <code>backend/.venv</code></p>
              <p class="mt-10">模型: <code>{{ modelName }}</code></p>
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card>
              <template #header>
                <div class="card-header">
                  <span>前端环境</span>
                  <el-tag type="primary">Vue 3 + Vite</el-tag>
                </div>
              </template>
              <p>Node 包: <code>frontend/node_modules</code></p>
              <p class="mt-10">启动: <code>npm run dev</code></p>
            </el-card>
          </el-col>
        </el-row>

        <!-- 新闻数据展示 -->
        <el-row :gutter="20" class="mt-20">
          <el-col :span="24">
            <el-tabs type="border-card" v-model="activeTab">
              <el-tab-pane label="📰 新闻原文" name="original">
                <NewsList />
              </el-tab-pane>
              <el-tab-pane label="🧠 AI 结构化分析" name="structured">
                <StructuredNewsList />
              </el-tab-pane>
              <el-tab-pane label="📤 上传新文章" name="upload">
                <UploadNews />
              </el-tab-pane>
            </el-tabs>
          </el-col>
        </el-row>
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { TrendCharts } from '@element-plus/icons-vue'
import NewsList from '@/components/NewsList.vue'
import StructuredNewsList from '@/components/StructuredNewsList.vue'
import UploadNews from '@/components/UploadNews.vue'

const activeTab = ref('original')
const modelName = ref('kimi-for-coding')

onMounted(async () => {
  try {
    const res = await fetch('/api/')
    const data = await res.json()
    if (data.model) {
      modelName.value = data.model
    }
  } catch (e) {
    console.error('获取后端信息失败:', e)
  }
})
</script>

<style scoped>
.app-header {
  background: linear-gradient(90deg, #409eff 0%, #1677ff 100%);
  color: white;
  display: flex;
  align-items: center;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 18px;
}

.welcome-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.pipeline {
  display: flex;
  align-items: stretch;
  gap: 12px;
  flex-wrap: wrap;
}

.pipeline-item {
  flex: 1;
  min-width: 200px;
  background: #f0f9ff;
  border: 1px solid #bae6fd;
  border-radius: 8px;
  padding: 16px;
}

.item-title {
  font-weight: 600;
  color: #0369a1;
  margin-bottom: 8px;
}

.item-desc {
  font-size: 13px;
  color: #475569;
  line-height: 1.6;
}

.pipeline-arrow {
  display: flex;
  align-items: center;
  font-size: 24px;
  color: #94a3b8;
}

.mt-20 {
  margin-top: 20px;
}

.mt-10 {
  margin-top: 10px;
}

code {
  background: #f1f5f9;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Consolas', monospace;
  font-size: 13px;
}
</style>
