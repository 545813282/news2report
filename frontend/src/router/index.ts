import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'
import DailyReportView from '@/views/DailyReportView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/daily-report',
      name: 'daily-report',
      component: DailyReportView,
    },
  ],
})

export default router
