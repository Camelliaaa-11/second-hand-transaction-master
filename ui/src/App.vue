<template>
  <router-view v-slot="{ Component, route }">
    <keep-alive>
      <component :is="Component" v-if="route.meta.keepAlive" :key="route.path" />
    </keep-alive>

    <component :is="Component" v-if="!route.meta.keepAlive" :key="route.path" />
  </router-view>
</template>

<style>
/* 全局样式 */
body {
  margin: 0;
  background-color: #f7f8fa; /* 统一背景色 */
  -webkit-font-smoothing: antialiased;
}
</style>