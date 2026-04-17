/**
 * 大屏自适应适配工具类
 * 基于 CSS Transform Scale 方案，以 1920x1080 为基准画布进行缩放
 * @author Hackerdallas
 */
export type AutofitOptions = {
    width: number
    height: number
    el: string
    resize?: boolean
}

export default class Autofit {
    private options: AutofitOptions
    private el: HTMLElement | null = null
    private timer: any = null

    constructor(options: AutofitOptions) {
        this.options = {
            resize: true,
            ...options
        }
        this.el = document.querySelector(this.options.el)
        if (!this.el) return

        this.init()
    }

    private init() {
        // 禁用 body 滚动条
        document.body.style.overflow = 'hidden'
        
        this.render()

        if (this.options.resize) {
            window.addEventListener('resize', this.onResize)
        }
    }

    private onResize = () => {
        if (this.timer) clearTimeout(this.timer)
        this.timer = setTimeout(() => {
            this.render()
        }, 100)
    }

    public render() {
        if (!this.el) return

        const { width, height } = this.options
        const clientWidth = document.documentElement.clientWidth
        const clientHeight = document.documentElement.clientHeight

        // 计算缩放比例 (取宽高中较小的一个比例，确保内容完整显示且不超出视口)
        const scaleW = clientWidth / width
        const scaleH = clientHeight / height
        const scale = scaleW < scaleH ? scaleW : scaleH

        // 应用变换
        this.el.style.width = `${width}px`
        this.el.style.height = `${height}px`
        this.el.style.transform = `scale(${scale})`
        this.el.style.transformOrigin = 'left top'
        
        // 居中对齐 (基于 left top 原点进行平移计算)
        const left = (clientWidth - width * scale) / 2
        const top = (clientHeight - height * scale) / 2
        
        this.el.style.position = 'absolute'
        this.el.style.left = `${left}px`
        this.el.style.top = `${top}px`
        this.el.style.transition = 'all 0.3s ease-out' // 增加平滑过渡
    }

    public destroy() {
        window.removeEventListener('resize', this.onResize)
        if (this.timer) clearTimeout(this.timer)
    }
}
