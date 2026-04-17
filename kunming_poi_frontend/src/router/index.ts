/**
 * Vue Router 路由配置
 * 实现多页面功能分离
 * @author Hackerdallas
 */
import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('../views/DashboardView.vue'),
    meta: { title: '态势感知大屏', transition: 'scale-fade' }
  },
  {
    path: '/patterns',
    name: 'Patterns',
    component: () => import('../views/PatternsView.vue'),
    meta: { title: '模式分析', transition: 'slide-fade' }
  },
  {
    path: '/districts',
    name: 'Districts',
    component: () => import('../views/DistrictsView.vue'),
    meta: { title: '区域分析', transition: 'slide-fade' }
  },
  {
    path: '/overview',
    name: 'Overview',
    component: () => import('../views/OverviewView.vue'),
    meta: { title: '数据总览', transition: 'slide-fade' }
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, _from, next) => {
  document.title = `${to.meta.title || '昆明POI'} - 昆明空间高频模式`
  next()
})

export default router
