import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', component: () => import('../views/Login.vue'), meta: { guest: true } },
  {
    path: '/',
    component: () => import('../views/Layout.vue'),
    meta: { requiresAuth: true },
    children: [
      { path: 'dashboard', name: 'Dashboard', component: () => import('../views/Dashboard.vue') },
      { path: 'customers', name: 'Customers', component: () => import('../views/customers/MyCustomers.vue') },
      { path: 'redistribution', name: 'Redistribution', component: () => import('../views/customers/Redistribution.vue') },
      { path: 'pool', name: 'Pool', component: () => import('../views/Pool.vue') },
      { path: 'important-pool', name: 'ImportantPool', component: () => import('../views/ImportantPool.vue') },
      { path: 'loan-cases', name: 'LoanCases', component: () => import('../views/LoanCases.vue') },
      { path: 'logs', name: 'Logs', component: () => import('../views/Logs.vue') },
      { path: 'revenue', name: 'Revenue', component: () => import('../views/Revenue.vue') },
      { path: 'performance', name: 'Performance', component: () => import('../views/Performance.vue') },
      { path: 'team', name: 'Team', component: () => import('../views/Team.vue') },
      { path: 'team-customers', name: 'TeamCustomers', component: () => import('../views/TeamCustomers.vue') },
      { path: 'settings', name: 'Settings', component: () => import('../views/Settings.vue') },
      { path: 'statistics', name: 'Statistics', component: () => import('../views/Statistics.vue') },
      // 新增页面
      { path: 'ranking', name: 'Ranking', component: () => import('../views/Ranking.vue') },
      { path: 'notice', name: 'Notice', component: () => import('../views/Notice.vue') },
      { path: 'call-records', name: 'CallRecords', component: () => import('../views/CallRecords.vue') },
      { path: '', redirect: '/dashboard' }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.meta.requiresAuth && !token) {
    next('/')
  } else if (to.meta.guest && token) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router
