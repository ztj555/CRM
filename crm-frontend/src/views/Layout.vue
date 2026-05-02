<template>
  <el-container style="height:100vh">
    <!-- 左侧粉色导航 -->
    <el-aside width="210px" style="background:#FDD0E3; overflow:hidden; display:flex; flex-direction:column">
      <!-- Logo区 -->
      <div class="logo-area">
        <div class="logo-icon">CRM</div>
        <div class="logo-text">
          <span class="logo-name">融鑫汇</span>
          <span class="logo-sub">客户管理系统</span>
        </div>
      </div>

      <!-- 菜单 -->
      <div class="menu-area">
        <!-- 工作台 -->
        <div class="menu-section-label">工作台</div>
        <div
          v-for="item in workMenu"
          :key="item.path"
          class="menu-item"
          :class="{ active: $route.path === item.path }"
          @click="go(item.path)"
        >
          <span class="menu-dot"></span>
          <span>{{ item.label }}</span>
        </div>

        <!-- 客户管理 -->
        <div class="menu-section-label" style="margin-top:6px">客户管理</div>
        <div
          v-for="item in customerMenu"
          :key="item.path"
          class="menu-item"
          :class="{ active: $route.path === item.path }"
          @click="go(item.path)"
        >
          <span class="menu-dot"></span>
          <span>{{ item.label }}</span>
        </div>

        <!-- 贷款进件 -->
        <div class="menu-section-label" style="margin-top:6px">贷款进件</div>
        <div
          v-for="item in loanMenu"
          :key="item.path"
          class="menu-item"
          :class="{ active: $route.path === item.path }"
          @click="go(item.path)"
        >
          <span class="menu-dot"></span>
          <span>{{ item.label }}</span>
        </div>

        <!-- 数据报表 -->
        <div class="menu-section-label" style="margin-top:6px">数据报表</div>
        <div
          v-for="item in reportMenu"
          :key="item.path"
          class="menu-item"
          :class="{ active: $route.path === item.path }"
          @click="go(item.path)"
        >
          <span class="menu-dot"></span>
          <span>{{ item.label }}</span>
        </div>

        <!-- 团队管理（主管/管理员可见） -->
        <template v-if="isManager">
          <div class="menu-section-label" style="margin-top:6px">团队管理</div>
          <div
            v-for="item in teamMenu"
            :key="item.path"
            class="menu-item"
            :class="{ active: $route.path === item.path }"
            @click="go(item.path)"
          >
            <span class="menu-dot"></span>
            <span>{{ item.label }}</span>
          </div>
        </template>

        <!-- 系统 -->
        <div class="menu-section-label" style="margin-top:6px">系统</div>
        <div
          v-for="item in systemMenu"
          :key="item.path"
          class="menu-item"
          :class="{ active: $route.path === item.path }"
          @click="go(item.path)"
        >
          <span class="menu-dot"></span>
          <span>{{ item.label }}</span>
        </div>
      </div>
    </el-aside>

    <el-container>
      <!-- 顶部栏 -->
      <el-header height="56px" style="background:white; border-bottom:1px solid #F0E0EB; display:flex; align-items:center; justify-content:space-between; padding:0 20px; box-shadow: 0 1px 4px rgba(0,0,0,0.06)">
        <!-- 左侧：日期+欢迎语 -->
        <div style="display:flex; flex-direction:column">
          <span style="font-size:13px; color:#888">{{ currentDate }}</span>
          <span style="font-size:14px; color:#E91E63; font-weight:600; margin-top:1px">{{ greeting }}</span>
        </div>

        <!-- 右侧：用户信息 -->
        <div style="display:flex; align-items:center; gap:12px">
          <!-- 公告/通知占位 -->
          <div style="display:flex; align-items:center; gap:4px; color:#888; font-size:13px; cursor:pointer" @click="showNotice">
            <el-icon><Bell /></el-icon>
            <span>公告</span>
          </div>

          <div style="width:1px; height:24px; background:#eee"></div>

          <div style="display:flex; align-items:center; gap:8px">
            <div style="width:32px; height:32px; border-radius:50%; background:linear-gradient(135deg,#E91E63,#F48FB1); display:flex; align-items:center; justify-content:center; color:white; font-size:13px; font-weight:bold">
              {{ user?.real_name?.charAt(0) || '管' }}
            </div>
            <div style="display:flex; flex-direction:column">
              <span style="font-size:13px; color:#333; font-weight:500">{{ user?.real_name }}</span>
              <span style="font-size:11px; color:#E91E63">{{ roleText }}</span>
            </div>
          </div>

          <el-dropdown @command="handleCommand" trigger="click">
            <el-icon style="cursor:pointer; color:#888; font-size:18px; margin-left:4px"><Setting /></el-icon>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="info">
                  <el-icon><User /></el-icon> 个人信息
                </el-dropdown-item>
                <el-dropdown-item command="pwd">
                  <el-icon><Lock /></el-icon> 修改密码
                </el-dropdown-item>
                <el-dropdown-item command="logout" divided>
                  <el-icon><SwitchButton /></el-icon> 退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- 主内容区 -->
      <el-main style="background:#F5F7FA; padding:0; overflow:hidden; display:flex; flex-direction:column">
        <!-- 顶部标签栏：主导航 -->
        <div class="main-tabs" v-if="tabs.length > 1">
          <div
            v-for="tab in tabs"
            :key="tab.id"
            class="main-tab"
            :class="{ active: activeTabId === tab.id }"
            @click="switchTab(tab.id)"
          >
            <span>{{ tab.label }}</span>
            <el-icon v-if="tabs.length > 1" class="tab-close" @click.stop="closeTab(tab.id)"><Close /></el-icon>
          </div>
        </div>

        <!-- 内容：支持双栏布局 -->
        <div class="main-body" :class="{ 'has-detail': !!detailPanel.id }">
          <!-- 左侧：列表页 -->
          <div class="list-panel">
            <router-view />
          </div>

          <!-- 右侧：客户详情面板（原系统风格） -->
          <transition name="slide-in">
            <div class="detail-panel" v-if="detailPanel.id">
              <CustomerPage
                :customer-id="detailPanel.id"
                :customer-name="detailPanel.name"
                @close="closeDetailPanel"
                @prev="navigateCustomer('prev')"
                @next="navigateCustomer('next')"
                @updated="detailPanel.name = $event"
              />
            </div>
          </transition>
        </div>
      </el-main>
    </el-container>
  </el-container>

  <!-- 全局客户详情抽屉（备用，当没有激活的列表页时使用） -->
  <CustomerDetailDrawer
    v-if="drawerCustomer.id"
    :visible="drawerVisible"
    :customer-id="drawerCustomer.id"
    @close="closeDrawer"
    @updated="closeDrawer"
  />
</template>

<script setup>
import { computed, ref, reactive, provide, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessageBox, ElMessage } from 'element-plus'
import CustomerPage from './customers/CustomerPage.vue'
import CustomerDetailDrawer from './customers/CustomerDetail.vue'

const router = useRouter()
const route = useRoute()
const user = computed(() => JSON.parse(localStorage.getItem('user') || '{}'))
const isManager = computed(() => user.value.role >= 0)
const roleText = computed(() => ({ 1: '顾问', 2: '主管', 3: '管理员' }[user.value.role] || '顾问'))

// ===================== 双栏标签系统 =====================
const tabs = ref([{ id: 'main', label: '主页面' }])
const activeTabId = ref('main')
const detailPanel = ref({ id: null, name: '' })
const drawerCustomer = ref({ id: null })
const drawerVisible = ref(false)

// 打开客户详情（注入给子组件调用）
const openCustomerDetail = (id, name) => {
  detailPanel.value = { id, name }
  const tab = tabs.value.find(t => t.id === 'customer-' + id)
  if (tab) {
    activeTabId.value = tab.id
  } else {
    tabs.value.push({ id: 'customer-' + id, label: `客户:${name || id}` })
    activeTabId.value = 'customer-' + id
  }
}

// 关闭详情面板
const closeDetailPanel = () => {
  const idx = tabs.value.findIndex(t => t.id === activeTabId.value)
  if (idx > 0) {
    tabs.value.splice(idx, 1)
    activeTabId.value = tabs.value[Math.max(0, idx - 1)].id
  }
  if (activeTabId.value === 'main') {
    detailPanel.value = { id: null, name: '' }
  }
}

// 切换标签
const switchTab = (id) => {
  activeTabId.value = id
  if (id === 'main') {
    detailPanel.value = { id: null, name: '' }
    router.push('/customers')
  }
}

// 关闭标签
const closeTab = (id) => {
  if (id === 'main') return
  const idx = tabs.value.findIndex(t => t.id === id)
  tabs.value.splice(idx, 1)
  if (activeTabId.value === id) {
    activeTabId.value = tabs.value[Math.max(0, idx - 1)].id
    if (activeTabId.value === 'main') {
      detailPanel.value = { id: null, name: '' }
      router.push('/customers')
    }
  }
}

// 上一位/下一位导航
const allCustomerIds = ref([])
const navigateCustomer = (dir) => {
  const curId = detailPanel.value.id
  const curIdx = allCustomerIds.value.indexOf(curId)
  if (curIdx < 0) return
  const newIdx = dir === 'prev' ? curIdx - 1 : curIdx + 1
  if (newIdx >= 0 && newIdx < allCustomerIds.value.length) {
    openCustomerDetail(allCustomerIds.value[newIdx], '')
  }
}

// 注入到所有子组件
provide('openCustomerDetail', openCustomerDetail)
provide('setAllCustomerIds', (ids) => { allCustomerIds.value = ids })

// 备用抽屉方式（当没有路由支持时）
const openDrawer = (id) => {
  drawerCustomer.value = { id }
  drawerVisible.value = true
}
const closeDrawer = () => {
  drawerVisible.value = false
  drawerCustomer.value = { id: null }
}
provide('openDrawer', openDrawer)

const weekDays = ['日', '一', '二', '三', '四', '五', '六']
const currentDate = computed(() => {
  const d = new Date()
  return `${d.getFullYear()}年${d.getMonth() + 1}月${d.getDate()}日 星期${weekDays[d.getDay()]}`
})

const greeting = computed(() => {
  const h = new Date().getHours()
  if (h < 12) return '上午好 ' + (user.value.real_name || '')
  if (h < 18) return '下午好 ' + (user.value.real_name || '')
  return '晚上好 ' + (user.value.real_name || '')
})

const go = (path) => router.push('/' + path)

const workMenu = [
  { path: 'dashboard', label: '工作简报' }
]

const customerMenu = [
  { path: 'customers', label: '我的客户' },
  { path: 'redistribution', label: '再分配' },
  { path: 'pool', label: '公共池' },
  { path: 'important-pool', label: '必跟进' }
]

const loanMenu = [
  { path: 'loan-cases', label: '在审件' },
  { path: 'call-records', label: '通话管理' }
]

const reportMenu = [
  { path: 'logs', label: '日志报表' },
  { path: 'statistics', label: '数据统计' },
  { path: 'ranking', label: '业绩排行榜' },
  { path: 'revenue', label: '创收分析' },
  { path: 'performance', label: '绩效目标' }
]

const teamMenu = [
  { path: 'team', label: '团队管理' },
  { path: 'team-customers', label: '团队客户' }
]

const systemMenu = [
  { path: 'notice', label: '公告管理' },
  { path: 'settings', label: '系统设置' }
]

const showNotice = () => {
  router.push('/notice')
}

const handleCommand = async (cmd) => {
  if (cmd === 'logout') {
    await ElMessageBox.confirm('确定退出登录？', '提示')
    localStorage.clear()
    router.push('/')
  } else if (cmd === 'pwd') {
    router.push('/settings?tab=password')
  } else if (cmd === 'info') {
    router.push('/settings?tab=info')
  }
}
</script>

<style scoped>
/* Logo区 */
.logo-area {
  height: 70px;
  background: linear-gradient(135deg, #E91E63 0%, #F06292 100%);
  display: flex;
  align-items: center;
  padding: 0 16px;
  gap: 10px;
  flex-shrink: 0;
}
.logo-icon {
  width: 40px;
  height: 40px;
  background: rgba(255,255,255,0.2);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 12px;
  font-weight: bold;
  letter-spacing: 1px;
  flex-shrink: 0;
}
.logo-text {
  display: flex;
  flex-direction: column;
}
.logo-name {
  color: white;
  font-size: 15px;
  font-weight: bold;
  letter-spacing: 2px;
}
.logo-sub {
  color: rgba(255,255,255,0.8);
  font-size: 10px;
  margin-top: 2px;
}

/* 菜单区域 */
.menu-area {
  flex: 1;
  overflow-y: auto;
  padding: 10px 0 16px;
}
.menu-area::-webkit-scrollbar { width: 3px; }
.menu-area::-webkit-scrollbar-thumb { background: #F48FB1; border-radius: 2px; }

.menu-section-label {
  font-size: 10px;
  font-weight: 600;
  color: #AD1457;
  letter-spacing: 1px;
  padding: 6px 16px 3px;
  text-transform: uppercase;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 8px;
  height: 38px;
  padding: 0 16px;
  cursor: pointer;
  font-size: 13px;
  color: #5D4037;
  transition: all 0.15s;
  position: relative;
}
.menu-item:hover {
  background: rgba(233, 30, 99, 0.08);
  color: #C2185B;
}
.menu-item.active {
  background: linear-gradient(90deg, #E91E63 0%, #F06292 100%);
  color: white;
  font-weight: 500;
  box-shadow: 0 2px 8px rgba(233, 30, 99, 0.3);
}
.menu-item.active::before {
  content: '';
  position: absolute;
  right: -1px;
  top: 50%;
  transform: translateY(-50%);
  border: 5px solid transparent;
  border-left-color: white;
}
.menu-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: currentColor;
  flex-shrink: 0;
  opacity: 0.6;
}
.menu-item.active .menu-dot {
  background: white;
  opacity: 1;
}
</style>

<!-- 全局样式（非scoped，供过渡动画使用） -->
<style>
.slide-in-enter-active, .slide-in-leave-active {
  transition: all 0.25s ease;
}
.slide-in-enter-from, .slide-in-leave-to {
  width: 0 !important;
  opacity: 0;
}
</style>

<style scoped>
/* 双栏标签系统 */
.main-tabs {
  height: 38px;
  background: white;
  border-bottom: 2px solid #FCE4EC;
  display: flex;
  align-items: stretch;
  padding: 0 8px;
  gap: 2px;
  flex-shrink: 0;
  overflow-x: auto;
}
.main-tabs::-webkit-scrollbar { height: 0; }

.main-tab {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 0 14px;
  cursor: pointer;
  font-size: 13px;
  color: #888;
  border-bottom: 2px solid transparent;
  white-space: nowrap;
  transition: all 0.15s;
}
.main-tab:hover { color: #E91E63; }
.main-tab.active {
  color: #E91E63;
  border-bottom-color: #E91E63;
  font-weight: 600;
}
.tab-close {
  font-size: 12px;
  margin-left: 4px;
  padding: 2px;
  border-radius: 3px;
  transition: background 0.15s;
}
.tab-close:hover { background: rgba(233, 30, 99, 0.1); }

/* 双栏主体 */
.main-body {
  flex: 1;
  display: flex;
  overflow: hidden;
  padding: 12px;
  gap: 12px;
  background: #F5F7FA;
}
.list-panel {
  flex: 1;
  overflow-y: auto;
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
  min-width: 0;
  transition: flex 0.25s ease;
}
.main-body:not(.has-detail) .list-panel {
  flex: 1;
}
.main-body.has-detail .list-panel {
  flex: 0 0 520px;
  max-width: 520px;
}

/* 详情面板 */
.detail-panel {
  flex: 1;
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
  overflow: hidden;
  min-width: 0;
}
</style>
