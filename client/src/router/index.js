import { createRouter, createWebHistory } from 'vue-router'
import LaptopsView from '@/views/LaptopsView.vue'
import BrandsView from '@/views/BrandsView.vue'
import ProcessorBrandsView from '@/views/ProcessorBrandsView.vue'    // новый
import ProcessorFamiliesView from '@/views/ProcessorFamiliesView.vue' // новый
import ReviewsView from '@/views/ReviewsView.vue'
import LoginView from '@/views/LoginView.vue'
import { useUserStore } from '@/stores/user'

const routes = [
  {
    path: '/login',
    name: 'login',
    component: LoginView,
  },
  {
    path: '/',
    name: 'laptops',
    component: LaptopsView,
    meta: { requiresAuth: true },
  },
  {
    path: '/brands',
    name: 'brands',
    component: BrandsView,
    meta: { requiresAuth: true },
  },
  {
    path: '/processor-brands',
    name: 'processor-brands',
    component: ProcessorBrandsView,
    meta: { requiresAuth: true },
  },
  {
    path: '/processor-families',
    name: 'processor-families',
    component: ProcessorFamiliesView,
    meta: { requiresAuth: true },
  },
  {
    path: '/reviews',
    name: 'reviews',
    component: ReviewsView,
    meta: { requiresAuth: true },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to) => {
  const userStore = useUserStore()

  if (!userStore.isAuthChecked) {
    await userStore.fetchMe()
  }

  if (to.meta.requiresAuth && !userStore.isAuthenticated) {
    return '/login'
  }

  if (to.path === '/login' && userStore.isAuthenticated) {
    return '/'
  }
})

export default router