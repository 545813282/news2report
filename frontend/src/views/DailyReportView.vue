<template>
  <div class="daily-report-view">
    <header class="app-header">
      <div class="header-brand" @click="router.push('/')">
        <div class="logo">
          <el-icon size="24"><TrendCharts /></el-icon>
        </div>
        <div class="brand-text">
          <h1>NEWS2REPORT</h1>
          <span class="subtitle">AI 舆情日报系统</span>
        </div>
      </div>
      <div class="header-actions">
        <el-button :icon="ArrowLeft" @click="router.push('/')">
          返回首页
        </el-button>
      </div>
    </header>

    <main class="app-main">
      <DailyReport />
    </main>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { TrendCharts, ArrowLeft } from '@element-plus/icons-vue'
import DailyReport from '@/components/DailyReport.vue'

const router = useRouter()
</script>

<style scoped>
.daily-report-view {
  min-height: 100vh;
  background: var(--bg);
}

.app-header {
  position: sticky;
  top: 0;
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 32px;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border);
  box-shadow: var(--shadow-sm);
}

.header-brand {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
}

.logo {
  width: 42px;
  height: 42px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--primary), var(--primary-dark));
  color: #fff;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25);
}

.brand-text h1 {
  font-size: 18px;
  font-weight: 800;
  letter-spacing: 1px;
  color: var(--text);
  line-height: 1.1;
}

.brand-text .subtitle {
  font-size: 11px;
  color: var(--text-secondary);
  letter-spacing: 1.5px;
  text-transform: uppercase;
}

.app-main {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px 32px 48px;
}
</style>
