<!--
  大屏侧边容器
  基于 3D perspective/rotateY 实现左右侧面板的驾驶舱入场动画
  通过 isInit prop 控制激活时机，position 控制左右方向
  @author Hackerdallas
-->
<template>
    <div class="screen-container" :class="[position, isInit ? 'active' : '', d3 ? 'd3' : 'nd3']">
        <div class="container-3d">
            <slot></slot>
        </div>
    </div>
</template>

<script setup lang="ts">
defineProps({
    isInit: {
        type: Boolean,
        default: false
    },
    d3: {
        type: Boolean,
        default: true
    },
    position: {
        type: String,
        default: 'left'
    }
})
</script>

<style scoped lang="scss">
.screen-container {
    position: absolute;
    height: 100%;
    display: flex;
    flex-direction: column;
    transform-style: preserve-3d;
    z-index: 99;
    perspective: 1000px;
    perspective-origin: 50% 50%;
    pointer-events: none;
    padding: 80px 0 20px;
    box-sizing: border-box;

    .container-3d {
        transform-style: preserve-3d;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        gap: 16px;
        flex: 1;
        transition: all 0.5s linear;
    }

    &.nd3 {
        .container-3d {
            max-width: 0;
            overflow: hidden;
        }
        &.active .container-3d {
            max-width: 1000px;
        }
    }

    &.active {
        pointer-events: auto;
    }

    &.left {
        left: 20px;
    }
    &.left.d3 {
        .container-3d {
            transform: translateZ(0) scaleX(0) scaleY(1) rotateX(0) rotateY(-12deg) rotate(0) skew(0) skewY(0);
        }
        &.active {
            .container-3d {
                transform: translateZ(0) scaleX(1) scaleY(1) rotateX(0) rotateY(6deg) rotate(0) skew(0) skewY(0);
            }
        }
    }

    &.right {
        right: 20px;
    }
    &.right.d3 {
        .container-3d {
            transform: translateZ(0) scaleX(0) scaleY(1) rotateX(0) rotateY(12deg) rotate(0) skew(0) skewY(0);
        }
        &.active {
            .container-3d {
                transform: translateZ(0) scaleX(1) scaleY(1) rotateX(0) rotateY(-6deg) rotate(0) skew(0) skewY(0);
            }
        }
    }
}
</style>
