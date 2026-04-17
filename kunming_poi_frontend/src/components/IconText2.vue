<!--
  图标文本卡片组件 - 样式2
  带圆形旋转图标和数值的卡片展示组件，包含装饰边角和背景
  @author Hackerdallas
-->
<template>
	<div class="icon-text-2-container">
		<img :src="ic3" class="ic-3" />
		<img :src="ic3" class="ic-4" />
		<img :src="bg3" class="ic-5" />
		<div class="circle-1">
			<img :src="circle1" class="bg" />
			<img :src="icon" v-if="icon" class="icon" />
		</div>
		<div class="info" :class="isRow ? 'row' : ''">
			<div class="label">{{ label }}</div>
			<div class="value">
				<span>{{ value }}</span><span class="unit-text">{{ unit }}</span>
			</div>
		</div>
	</div>
</template>

<script setup lang="ts">
// 图标资源
const ic3 = new URL('@/assets/icon/ic-3.svg', import.meta.url).href
const bg3 = new URL('@/assets/icon/bg-3.svg', import.meta.url).href
const circle1 = new URL('@/assets/icon/circle-1.svg', import.meta.url).href

const props = defineProps({
	icon: {
		type: String,
		default: ''
	},
	value: {
		type: [String, Number],
		default: ''
	},
	unit: {
		type: String,
		default: ''
	},
	label: {
		type: String,
		default: ''
	},
	isRow: {
		type: Boolean,
		default: false
	}
})
</script>

<style scoped lang="scss">
.icon-text-2-container {
	display: flex;
	padding: 8px;
	background: rgba(76, 153, 191, 0.09);
	position: relative;
	width: 100%;
	height: 100%;
	align-items: center;
	.ic-3 {
		position: absolute;
		left: 0;
		top: 0;
		filter: drop-shadow(0px 1px 4px rgba(24, 254, 254, 0.92));
	}
	.ic-4 {
		position: absolute;
		right: 0;
		bottom: 0;
		filter: drop-shadow(0px 1px 4px rgba(24, 254, 254, 0.92));
		transform: rotate(180deg);
	}
	.ic-5 {
		position: absolute;
		right: 0;
		bottom: 0;
		opacity: 0.3;
        height: 50%;
	}
	.circle-1 {
		width: 50px;
		height: 50px;
		display: flex;
		align-items: center;
		justify-content: center;
		position: relative;
	}
	.circle-1 .bg {
		width: 100%;
		height: 100%;
		animation: circle 5s linear infinite;
	}
	.circle-1 .icon {
		position: absolute;
		left: 0;
		right: 0;
		top: 0;
		bottom: 0;
		width: 24px;
		height: 24px;
		filter: drop-shadow(0px 0px 10px #4299c1);
		margin: auto;
	}

	.info {
		display: flex;
		flex-direction: column;
		padding-left: 8px;
		font-size: 12px;
		&.row {
			display: flex;
			flex-direction: row;
			align-items: center;
			flex: 1;
			.label {
				flex: 1;
			}
		}
		.label {
			color: #d9e7ff;
		}
		.value {
			color: #fff;
			display: flex;
			font-family: MiSans-Demibold, serif;
			font-weight: bold;
			font-size: 16px;
			align-items: center;
			position: relative;
		}
		.value .unit-text {
			color: #7facd1;
			font-size: 12px;
			margin-left: 4px;
			position: relative;
			top: 2px;
		}
	}

	@keyframes circle {
		from {
			transform: rotate(0deg);
		}
		to {
			transform: rotate(360deg);
		}
	}
}
</style>
