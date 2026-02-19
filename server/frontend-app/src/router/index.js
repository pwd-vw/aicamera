import { createRouter, createWebHistory } from 'vue-router'
import ServerHome from '../views/ServerHome.vue'
import Network from '../views/Network.vue'
import EdgeControl from '../views/EdgeControl.vue'

const base = (typeof window !== 'undefined' && window.location.pathname.startsWith('/server'))
  ? '/server/'
  : '/'

const routes = [
  { path: '/', name: 'Server', component: ServerHome, meta: { title: 'Detection Dashboard' } },
  { path: '/network', name: 'Network', component: Network, meta: { title: 'Communication Network' } },
  { path: '/edge_control', name: 'EdgeControl', component: EdgeControl, meta: { title: 'Edge AI Dashboard' } }
]

const router = createRouter({
  history: createWebHistory(base),
  routes
})

router.afterEach((to) => {
  if (to.meta && to.meta.title && typeof document !== 'undefined') {
    document.title = to.meta.title + ' – LPR Server'
  }
})

export default router
