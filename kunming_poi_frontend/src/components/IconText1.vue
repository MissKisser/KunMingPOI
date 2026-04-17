<!--
  图标文本卡片组件 - 样式1
  带图标、数值和标签的卡片展示组件，包含光效和旋转动画
  @author Hackerdallas
-->
<template>
    <div class="icon-text-1-container">
        <div class="icon-1">
            <img class="light" alt="light" src="@/assets/icon/icon-light.svg">
            <img class="bottom" alt="bottom" src="@/assets/icon/icon-bottom.svg">
            <img class="icon" v-if="icon" :src="icon">
        </div>
        <div class="value">
            <span class="value-text">{{ value }}</span>
            <span class="unit">{{unit}}</span>
        </div>
        <div class="label">{{ label }}</div>
    </div>
</template>

<script setup lang="ts">
const props = defineProps({
    icon:{
        type:String,
        default:''
    },
    value:{
        type:[String,Number],
        default:''
    },
    unit:{
        type:String,
        default:''
    },
    label:{
        type:String,
        default:''
    }
})
</script>

<style scoped lang="scss">
.icon-1 {
    display: flex;
    flex-direction: column;
    width: 64px;
    align-items: center;
    justify-content: center;
    position: relative;
    .bottom,.light {
        width: 100%;
        position: relative;
        z-index: 1;
    }
    .light {
        top: 16px;
        height: 46px;
        z-index: 2;
        animation:inout 1s linear infinite alternate;
    }
    .icon {
        width: 22px;
        position: absolute;
        left: 0;
        right: 0;
        top:28px;
        margin: auto;
        animation:circle 5s linear infinite;
    }
    @keyframes inout {
        from {
            opacity: .5;
        }
        to {
            opacity:1;
        }
    }
    @keyframes circle {
        from {
            transform: rotateY(0deg);
        }
        to {
            transform: rotateY(360deg);
        }
    }
}
.icon-text-1-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    .value {
        font-size: 20px;
        color:#fff;
        align-items: center;
        justify-content: center;
        font-family: MiSans-Demibold, serif;
        transform: skew(-6deg);
        display: inline-block;
        position: relative;
        top: -2px;
    }
    .label {
        font-size: 12px;
        color: #D9E7FF;
        align-items: center;
        justify-content: center;
        margin-top:-2px;
    }
    .unit {
        font-size: 12px;
    }
}
</style>
