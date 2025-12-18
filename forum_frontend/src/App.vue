<template>
  <div class="app-wrapper">
    <router-view />
  </div>
</template>

<script setup>
// 禁用Vue开发者工具（拟真）
// if (window.__VUE_DEVTOOLS_GLOBAL_HOOK__) {
//   window.__VUE_DEVTOOLS_GLOBAL_HOOK__.emit('destroy')
//   window.__VUE_DEVTOOLS_GLOBAL_HOOK__.off('init', window.__VUE_DEVTOOLS_GLOBAL_HOOK__.listeners('init')[0])
// }
</script>

<style>
/* 全局样式：还原复古网页 */
html, body{
  margin: 0;
  padding: 0;
  height: 100%;
}

.app-wrapper {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

router-view {
  flex: 1;
}

body {
  background-color: #f0f0f0;
  color: #333333;
  font-family: SimSun, STSong, serif;
}
</style>