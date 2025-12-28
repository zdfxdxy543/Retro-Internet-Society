<template>
  <div class="bg-retro-bg border-t border-retro-border py-4 px-4 mt-6 footer-sticky">
    <div class="max-w-5xl mx-auto text-center text-sm text-retro-text">
      <p>© 2010-2025 复古论坛 版权所有</p>
      <p class="mt-1">备案号：Having Fun! | 联系邮箱：contact@nottrue.com</p>
    </div>
  </div>
</template>

<style scoped>
    .footer-sticky{
        /* 核心：固定在页面底端，内容不足时贴底，内容过长时跟随滚动 */
        position: sticky;
        bottom: 0;
        width: 100%;
        /* 避免被内容遮挡，同时保持复古边框质感 */
        z-index: 10;
        box-shadow: 0 -1px 0 #cccccc; /* 细微阴影，增强层次感但不破坏复古感 */
        box-sizing: border-box;
    }

    .text-center{
        text-align: center;
    }
</style>