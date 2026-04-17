<!--
  加载状态指示器
  三环同轴旋转动画，覆盖在容器正中央
  @author Hackerdallas
-->
<template>
    <div class="w-full h-full absolute flex items-center justify-center left-0 top-0 z-10">
        <div class="loader"></div>
    </div>
</template>

<script setup lang="ts">
</script>

<style scoped lang="scss">
.loader {
    width: 50px;
    aspect-ratio: 1;
    border-radius: 50%;
    border: 8px solid transparent;
    border-right-color: rgba(24, 254, 254, 0.3);
    position: relative;
    animation: l24 1s infinite linear;
}
.loader:before,
.loader:after {
    content: '';
    position: absolute;
    inset: -8px;
    border-radius: 50%;
    border: inherit;
    animation: inherit;
    animation-duration: 2s;
}
.loader:after {
    animation-duration: 4s;
}
@keyframes l24 {
    100% {
        transform: rotate(1turn);
    }
}
</style>
