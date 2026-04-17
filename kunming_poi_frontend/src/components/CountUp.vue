<!--
  数字动画组件
  基于 countup.js 实现数字滚动效果
  @author Hackerdallas
-->
<template>
	<span :class="textClass" ref="domRef"></span>
</template>

<script setup lang="ts">
import { ref, shallowRef, watch, onMounted, computed } from 'vue'
import { CountUp } from 'countup.js'
import { isUndefined } from 'lodash-es'

const domRef = shallowRef<any>(null)
interface CountUpProps {
	endVal?: number | string
	value?: number | string
	decimalPlaces?: number | string
	textClass?: string
	useGrouping?: boolean
	duration?: number
}
const props = withDefaults(defineProps<CountUpProps>(), {
	value: 0,
	endVal: 0,
	decimalPlaces: 0,
	textClass: '',
	useGrouping: false,
	duration: 2000
})

// 兼容 endVal 和 value 两种 prop 名称
const actualValue = computed(() => {
	const val = props.endVal ?? props.value ?? 0
	return Number(val)
})

watch(
	() => actualValue.value,
	(newVal: number) => {
		if (countUp.value) {
			countUp.value.update(newVal)
		} else if (domRef.value) {
			countUp.value = new CountUp(domRef.value, newVal, {
				startVal: 0,
				useGrouping: props.useGrouping,
				decimalPlaces: props.decimalPlaces as number,
				duration: (props.duration ?? 2000) / 1000
			})
			countUp.value.start()
		}
	}
)
const countUp = ref<any>(null)
onMounted(() => {
	if (!domRef.value) return
	countUp.value = new CountUp(domRef.value, actualValue.value, {
		startVal: 0,
		useGrouping: props.useGrouping,
		decimalPlaces: props.decimalPlaces as number,
		duration: (props.duration ?? 2000) / 1000
	})
	countUp.value.start()
})
</script>
