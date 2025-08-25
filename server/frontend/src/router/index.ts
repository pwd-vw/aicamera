import { createRouter, createWebHistory } from 'vue-router';
import type { RouteRecordRaw } from 'vue-router';
import LoginView from '../views/LoginView.vue';
import DashboardView from '../views/DashboardView.vue';
import CamerasView from '../views/CamerasView.vue';

const routes: RouteRecordRaw[] = [
  { path: '/', redirect: '/dashboard' },
  { path: '/login', name: 'login', component: LoginView, meta: { public: true } },
  { path: '/dashboard', name: 'dashboard', component: DashboardView },
  { path: '/cameras', name: 'cameras', component: CamerasView },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

router.beforeEach((to, _from, next) => {
  const isPublic = to.matched.some(r => r.meta.public);
  const token = localStorage.getItem('accessToken');
  if (!isPublic && !token) {
    return next({ name: 'login', query: { redirect: to.fullPath } });
  }
  if (isPublic && token && to.name === 'login') {
    return next({ name: 'dashboard' });
  }
  return next();
});

export default router;
