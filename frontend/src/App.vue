<template>
  <router-view />
</template>

<style>
/* 全局路由过渡 */
.page-enter-active,
.page-leave-active {
  transition: opacity 0.25s ease;
}

.page-enter-from,
.page-leave-to {
  opacity: 0;
}
</style>
