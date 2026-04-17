<!--
  基础面板容器
  提供标题栏（渐变背景、dot 装饰、光效扫描动画、边线）+ 内容区 + 可选 loading 覆盖层的统一面板样式
  @author Hackerdallas
-->
<template>
    <div class="basic-container" :class="[dark?'dark':'']" :style="getContainerStyle">
        <div class="title" :class="[titleWidth ? '' : '']" :style="{ width: titleWidth ? `${titleWidth}px` : '100%' }">
            <img class="bg1" src="@/assets/icon/ic-1.svg">
            <img class="bg2" src="@/assets/icon/ic-2.svg">
            <div class="dot"></div>
            <span class="line-left"></span>
            <span class="line-right"></span>
            <div class="context text-i z-20">{{title}}</div>
            <div class="slot"><slot name="title"></slot></div>
            <div class="end">
                <slot name="end">
                    <div class="dots">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                </slot>
            </div>

            <svg class="animate" width="89" height="36" viewBox="0 0 89 36" fill="none" xmlns="http://www.w3.org/2000/svg">
                <g clip-path="url(#clip0_74_264)">
                    <path d="M30 36H89L59 0H0L30 36Z" fill="url(#paint0_linear_74_264)" />
                </g>
                <defs>
                    <linearGradient id="paint0_linear_74_264" x1="28.8956" y1="18" x2="103.442" y2="18" gradientUnits="userSpaceOnUse">
                        <stop stop-color="#2795BB" stop-opacity="0" />
                        <stop offset="1" stop-color="#2897BD" />
                    </linearGradient>
                    <clipPath id="clip0_74_264">
                        <rect width="89" height="36" fill="white" />
                    </clipPath>
                </defs>
            </svg>
        </div>
        <div class="container-body">
            <span class="line-left"></span>
            <span class="line-right"></span>
            <div class="container-main">
                <slot></slot>
            </div>
            <Loader v-if="loading"></Loader>
        </div>
    </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import Loader from './Loader.vue'

const props = defineProps({
    title: {
        type: String,
        default: ''
    },
    loading: {
        type: Boolean,
        default: false
    },
    dark:{
        type:Boolean,
        default:true
    },
    padding: {
        type: String,
        default: '20px'
    },
    width: {
        type: [Number, String],
        default: 400
    },
    height: {
        type: [Number, String],
        default: ''
    },
    titleWidth: {
        type: Number,
        default: 0
    }
})

const getContainerStyle = computed(() => {
    const w = Number(props.width)
    const h = Number(props.height)
    const style = {
        width: isNaN(w) ? props.width : w <= 100 ? `${props.width}%` : props.width + 'px',
        height: isNaN(h) ? props.height : h <= 100 ? `${props.height}%` : props.height + 'px'
    }
    return {
        ...style
    }
})
</script>

<style scoped lang="scss">
.basic-container {
    display: flex;
    flex-direction: column;
    pointer-events: auto;
    z-index: 999;
    &.dark {
        background: rgba(4,33,53,.7);
    }
    .title {
        height: 32px;
        position: relative;
        display: flex;
        align-items: center;
        padding: 0 8px;
        font-size: 14px;
        box-sizing: border-box;
        font-family: MiSans-Demibold, serif;
        overflow: hidden;

        background: radial-gradient(50% 50% at 50% 100%, #4C99BF 0%, rgba(50, 88, 108, 0.2) 99%, rgba(50, 88, 108, 0.2) 100%);
        box-shadow: 0 12px 8px 0 rgba(12, 19, 18, 0.15);
        .dot {
            width: 16px;
            height: 16px;
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 12px;
            border: 2px solid #40A3FF;
            &:before {
                width: 5px;
                height: 5px;
                background: #fff;
                content: '';
                transform: rotate(45deg);
            }
        }
        .end {
            height: 100%;
            margin-left: auto;
            display: flex;
            align-items: center;
        }
        .dots {
            height: 100%;
            margin-left: auto;
            display: flex;
            align-items: center;
            gap: 6px;
            span {width: 5px;height: 5px;background: #fff;transform: rotate(45deg);}
            span:nth-child(1) {opacity: .8;}
            span:nth-child(2) {opacity: .6;}
            span:nth-child(3) {opacity: .4;}
        }
        .bg1 {opacity: .2;position: absolute;height: 100%;left: 0;z-index: 1;}
        .bg2 {opacity: .2;position: absolute;height: 100%;right: 0;z-index: 1;}
        .context {color: #fff;font-family: D-JinBu serif;}
        .slot {display: flex;flex: 1;position: relative;z-index: 10;padding-right: 8px;}
        .line-left {
            position: absolute;
            height: 100%;
            top: 0;
            width: 2px;
            background: linear-gradient(180deg, rgba(102, 177, 186, 0) 0%, #539BA6 100%);
            left: 0;
        }
        .line-right {
            position: absolute;
            height: 100%;
            top: 0;
            width: 2px;
            background: linear-gradient(180deg, rgba(102, 177, 186, 0) 0%, #539BA6 100%);
            right: 0;

        }
        &:before {
            background: linear-gradient(270deg, rgba(151, 151, 151, .5) 0%, rgba(153, 200, 255, 0.8) 51%, rgba(200, 200, 200, .5) 100%);
            bottom: 0;
            left: 0;
            width: 100%;
            height: 2px;
            position: absolute;
            content:'';
            z-index: 1;
        }
        .animate {
            position: absolute;
            left: 100%;
            top: 0;
            height: 100%;
            animation: light-in 3s linear infinite;
            @keyframes light-in {
                0% {
                    left: 0;
                }
                100% {
                    left: 400%;
                }
            }
        }
    }
    .container-body {
        width: 100%;
        position: relative;
        flex: 1;
        min-height: 0;
        .line-left {
            position: absolute;
            height: 100%;
            top: 0;
            width: 2px;
            background: linear-gradient(180deg, rgba(102, 177, 186, 0) 0%, #539BA660 100%);
            left: 0;
        }
        .line-right {
            position: absolute;
            height: 100%;
            top: 0;
            width: 2px;
            background: linear-gradient(180deg, rgba(102, 177, 186, 0) 0%, #539BA660 100%);
            right: 0;
        }
        &:before {
            background: linear-gradient(270deg, rgba(151, 151, 151, .1) 0%, rgba(153, 200, 255, 0.3) 51%, rgba(200, 200, 200, .1) 100%);
            bottom: 0;
            left: 0;
            width: 100%;
            height: 2px;
            position: absolute;
            content:'';
            z-index: 1;
        }
        .container-main {
            position: relative;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            min-height: 0;
            overflow: auto;
        }
    }

}
</style>
