<template>
  <div>
    <div class="page-header">
      <h3>团队管理</h3>
    </div>

    <!-- Tab1: 团队管理（主Tab） -->
    <div v-show="activeTab === 'manage'">
      <el-card style="margin:12px 0">
        <template #header>
          <div style="display:flex; justify-content:space-between; align-items:center">
            <span style="font-weight:600">团队成员管理（共 {{ teamMembers.length }} 人）</span>
            <div style="display:flex; gap:8px">
              <el-button size="small" type="primary" @click="addUserVisible = true">
                <el-icon><Plus /></el-icon> 添加成员
              </el-button>
              <el-button size="small" @click="loadTeamMembers"><Refresh /> 刷新</el-button>
            </div>
          </div>
        </template>
        <el-form inline style="margin-bottom:12px">
          <el-form-item label="状态">
            <el-select v-model="memberFilter" clearable placeholder="全部" style="width:110px">
              <el-option label="全部" :value="0" />
              <el-option label="在职" :value="1" />
              <el-option label="离职" :value="2" />
            </el-select>
          </el-form-item>
          <el-form-item label="搜索">
            <el-input v-model="memberKeyword" placeholder="姓名/手机" clearable style="width:150px" @clear="loadTeamMembers" />
          </el-form-item>
          <el-form-item>
            <el-button size="small" @click="loadTeamMembers">搜索</el-button>
          </el-form-item>
        </el-form>
        <el-table :data="filteredMembers" v-loading="loading2" size="small" :stripe="true" style="width:100%" :max-height="600">
          <el-table-column label="姓名" width="90" fixed="left">
            <template #default="{row}">
              <div style="display:flex; align-items:center; gap:8px">
                <div class="avatar-circle">{{ row.real_name?.charAt(0) }}</div>
                {{ row.real_name }}
              </div>
            </template>
          </el-table-column>
          <el-table-column label="部门" prop="dept_name" width="130" />
          <el-table-column label="职位" prop="position" width="100" />
          <el-table-column label="日分配上限" width="100">
            <template #default="{row}">
              <el-input-number size="small" v-model="row.daily_quota" :min="0" :max="500" @change="setQuota(row)" style="width:80px" />
            </template>
          </el-table-column>
          <el-table-column label="日实分" width="80" align="center">
            <template #default="{row}">
              <span>{{ row.today_alloc || 0 }}</span>
            </template>
          </el-table-column>
          <el-table-column label="客户数" width="80" align="center">
            <template #default="{row}">
              <span style="color:#E91E63; font-weight:bold">{{ row.customer_count || 0 }}</span>
            </template>
          </el-table-column>
          <el-table-column label="当月原始分配" width="110" align="center">
            <template #default="{row}">{{ row.month_alloc || 0 }}</template>
          </el-table-column>
          <el-table-column label="当月再分配" width="110" align="center">
            <template #default="{row}">{{ row.month_realloc || 0 }}</template>
          </el-table-column>
          <el-table-column label="当月优质率" width="100" align="center">
            <template #default="{row}">
              <el-progress :percentage="row.quality_rate || 0" :stroke-width="6" style="width:80px" />
            </template>
          </el-table-column>
          <el-table-column label="上门数" width="80" align="center">
            <template #default="{row}">{{ row.visit_count || 0 }}</template>
          </el-table-column>
          <el-table-column label="上门率" width="80" align="center">
            <template #default="{row}">{{ row.visit_rate || 0 }}%</template>
          </el-table-column>
          <el-table-column label="签约数" width="80" align="center">
            <template #default="{row}">{{ row.sign_count || 0 }}</template>
          </el-table-column>
          <el-table-column label="签约率" width="80" align="center">
            <template #default="{row}">{{ row.sign_rate || 0 }}%</template>
          </el-table-column>
          <el-table-column label="接受新数据" width="100" align="center">
            <template #default="{row}">
              <el-tag size="small" :type="row.accept_new_data ? 'success' : 'info'">
                {{ row.accept_new_data ? '接受' : '关闭' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="禁止登录" width="90" align="center">
            <template #default="{row}">
              <el-tag size="small" :type="row.is_disabled ? 'danger' : 'success'">
                {{ row.is_disabled ? '已禁' : '正常' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="入司日期" width="110" align="center">
            <template #default="{row}">{{ row.entry_date || '—' }}</template>
          </el-table-column>
          <el-table-column label="上级经理" width="100" align="center">
            <template #default="{row}">{{ row.manager_name || '—' }}</template>
          </el-table-column>
          <el-table-column label="当月备注数" width="100" align="center">
            <template #default="{row}">{{ row.month_remarks || 0 }}</template>
          </el-table-column>
          <el-table-column label="操作" width="160" fixed="right">
            <template #default="{row}">
              <el-button size="small" @click="openEditMember(row)">编辑</el-button>
              <el-button size="small" type="danger" v-if="row.status === 1" @click="handleDisableUser(row)">离职</el-button>
              <el-button size="small" type="success" v-if="row.status === 0" @click="handleEnableUser(row)">恢复</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>

    <!-- Tab2: 离职分配 -->
    <div v-show="activeTab === 'offboard'">
      <el-alert
        title="离职人员数据分配"
        type="warning"
        :closable="false"
        style="margin:12px 0; border-radius:8px"
        show-icon
      >
        <template #default>
          选择在职顾问，将离职员工的所有客户一键转移。转移后原员工无法访问，客户归属将变更为"再分配"类型。
        </template>
      </el-alert>

      <el-card v-loading="loading3">
        <template #header>
          <div style="display:flex; justify-content:space-between; align-items:center">
            <span style="font-weight:600">离职员工列表（共 {{ offboardUsers.length }} 人）</span>
            <el-button size="small" @click="loadOffboardUsers"><Refresh /> 刷新</el-button>
          </div>
        </template>

        <el-empty v-if="!offboardUsers.length && !loading3" description="暂无离职员工" style="padding:40px" />

        <div v-else class="offboard-grid">
          <div v-for="u in offboardUsers" :key="u.id" class="offboard-card">
            <div class="offboard-avatar">{{ u.real_name?.charAt(0) }}</div>
            <div class="offboard-info">
              <div class="offboard-name">{{ u.real_name }}</div>
              <div class="offboard-meta">账号: {{ u.username }} | 职位: {{ u.position || '顾问' }}</div>
              <div class="offboard-count">
                <span style="color:#E91E63; font-weight:bold; font-size:20px">{{ u.customer_count || 0 }}</span>
                <span style="color:#888; font-size:13px; margin-left:4px">名客户待分配</span>
              </div>
              <div style="margin-top:10px; display:flex; gap:8px; align-items:center">
                <el-select v-model="reassignTo[u.id]" placeholder="选择接收顾问" size="small" style="flex:1">
                  <el-option v-for="au in activeUsers" :key="au.id" :label="au.real_name + ' (' + (au.customer_count||0) + '客户)'" :value="au.id" />
                </el-select>
                <el-button size="small" type="primary" :disabled="!reassignTo[u.id]" :loading="reassignLoading[u.id]" @click="handleReassign(u)">
                  一键转移
                </el-button>
              </div>
              <el-button size="small" type="success" style="width:100%;margin-top:8px" @click="handleReenableUser(u)">
                🔄 恢复在职
              </el-button>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 添加成员弹窗 -->
    <el-dialog v-model="addUserVisible" title="添加团队成员" width="500px">
      <el-form :model="newUser" label-width="100px">
        <el-form-item label="姓名" required>
          <el-input v-model="newUser.real_name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="账号" required>
          <el-input v-model="newUser.username" placeholder="手机号或自定义账号" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="newUser.password" type="password" show-password placeholder="默认密码：123456" />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="newUser.role" style="width:100%">
            <el-option label="顾问" :value="5" />
            <el-option label="主管" :value="4" />
            <el-option label="二级主管" :value="3" />
            <el-option label="负责人" :value="0" />
          </el-select>
        </el-form-item>
        <el-form-item label="职位">
          <el-input v-model="newUser.position" placeholder="如：储备主管、顾问" />
        </el-form-item>
        <el-form-item label="上级经理">
          <el-select v-model="newUser.manager_id" clearable placeholder="选择上级" style="width:100%">
            <el-option v-for="u in allUsers" :key="u.id" :label="u.real_name" :value="u.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="入司日期">
          <el-date-picker v-model="newUser.entry_date" type="date" placeholder="选择日期" style="width:100%" />
        </el-form-item>
        <el-form-item label="日分配上限">
          <el-input-number v-model="newUser.daily_quota" :min="0" :max="500" style="width:100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addUserVisible = false">取消</el-button>
        <el-button type="primary" :loading="addLoading" @click="handleAddUser">添加</el-button>
      </template>
    </el-dialog>

    <!-- 编辑成员弹窗 -->
    <el-dialog v-model="editUserVisible" title="编辑成员信息" width="500px">
      <el-form :model="editUser" label-width="100px">
        <el-form-item label="姓名">
          <el-input v-model="editUser.real_name" />
        </el-form-item>
        <el-form-item label="职位">
          <el-input v-model="editUser.position" />
        </el-form-item>
        <el-form-item label="上级经理">
          <el-select v-model="editUser.manager_id" clearable placeholder="选择上级" style="width:100%">
            <el-option v-for="u in allUsers" :key="u.id" :label="u.real_name" :value="u.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="入司日期">
          <el-date-picker v-model="editUser.entry_date" type="date" placeholder="选择日期" style="width:100%" />
        </el-form-item>
        <el-form-item label="日分配上限">
          <el-input-number v-model="editUser.daily_quota" :min="0" :max="500" style="width:100%" />
        </el-form-item>
        <el-form-item label="接受新数据">
          <el-switch v-model="editUser.accept_new_data" :active-value="1" :inactive-value="0" />
        </el-form-item>
        <el-form-item label="禁止登录">
          <el-switch v-model="editUser.is_disabled" :active-value="1" :inactive-value="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editUserVisible = false">取消</el-button>
        <el-button type="primary" :loading="editLoading" @click="handleEditUser">保存</el-button>
      </template>
    </el-dialog>

  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, UserFilled, DocumentDelete, Refresh } from '@element-plus/icons-vue'
import api from '../api'

const activeTab = ref('manage')
const tabs = [
  { key: 'manage', label: '团队管理', icon: 'UserFilled' },
  { key: 'offboard', label: '离职分配', icon: 'DocumentDelete' }
]

// 团队管理
const loading2 = ref(false)
const teamMembers = ref([])
const memberFilter = ref(0)
const memberKeyword = ref('')
const allUsers = ref([])  // 所有用户（含离职，供上级选择）

// 离职分配
const offboardUsers = ref([])
const loading3 = ref(false)
const reassignTo = reactive({})
const reassignLoading = reactive({})

// 部门列表（用于添加成员时分配默认部门）
const departments = ref([])

// 在职顾问（供分配使用）
const activeUsers = computed(() => {
  return allUsers.value.filter(u => u.status === 1)
})

// 过滤后的团队成员
const filteredMembers = computed(() => {
  let list = teamMembers.value
  if (memberFilter.value === 1) list = list.filter(m => m.status === 1)
  if (memberFilter.value === 2) list = list.filter(m => m.status === 0)
  if (memberKeyword.value) {
    const kw = memberKeyword.value.toLowerCase()
    list = list.filter(m => (m.real_name || '').toLowerCase().includes(kw) || (m.username || '').includes(kw))
  }
  return list
})

// 添加/编辑成员
const addUserVisible = ref(false)
const addLoading = ref(false)
const newUser = reactive({
  real_name: '', username: '', password: '', role: 5,
  position: '', manager_id: '', entry_date: '', daily_quota: 50
})

const editUserVisible = ref(false)
const editLoading = ref(false)
const editUser = reactive({})

const switchTab = (key) => {
  activeTab.value = key
  if (key === 'offboard') loadOffboardUsers()
  if (key === 'manage') loadTeamMembers()
}
const loadTeamMembers = async () => {
  loading2.value = true
  try {
    const params = {}
    if (memberFilter.value === 1) params.status_filter = 1
    if (memberFilter.value === 2) params.status_filter = 2
    if (memberKeyword.value) params.keyword = memberKeyword.value
    teamMembers.value = await api.get('/team/members', { params })
    // 加载今日实际分配数
    await loadTodayAlloc()
  } catch (e) { ElMessage.error('加载失败') }
  finally { loading2.value = false }
}

const loadTodayAlloc = async () => {
  try {
    const today = new Date().toISOString().split('T')[0]
    const res = await api.get('/stats/team-daily', { params: { target_date: today } })
    // 将今日分配数匹配到团队成员
    for (const m of teamMembers.value) {
      const found = res.advisors?.find(a => a.advisor_id === m.id)
      m.today_alloc = found ? found.remark_count : 0
    }
  } catch (e) { /* 忽略 */ }
}

// 设置日分配上限
const setQuota = async (row) => {
  try {
    await api.put(`/users/${row.id}`, { daily_quota: row.daily_quota })
    ElMessage.success(`已设置「${row.real_name}」日分配上限为 ${row.daily_quota}`)
  } catch (e) { ElMessage.error('设置失败') }
}

// 编辑成员
const openEditMember = (row) => {
  Object.assign(editUser, {
    id: row.id, real_name: row.real_name, position: row.position || '',
    manager_id: row.manager_id || '', entry_date: row.entry_date || '',
    daily_quota: row.daily_quota, accept_new_data: row.accept_new_data,
    is_disabled: row.is_disabled || 0
  })
  editUserVisible.value = true
}

const handleEditUser = async () => {
  editLoading.value = true
  try {
    await api.put(`/users/${editUser.id}`, { ...editUser })
    ElMessage.success('已更新')
    editUserVisible.value = false
    await loadTeamMembers()
  } catch (e) { ElMessage.error(e.detail || '更新失败') }
  finally { editLoading.value = false }
}

// 离职处理
const handleDisableUser = async (row) => {
  await ElMessageBox.confirm(
    `确定将「${row.real_name}」设为离职？该账号将被禁用，其客户可在"离职分配"中转移。`,
    '离职处理确认', { type: 'warning' }
  )
  try {
    const data = new URLSearchParams()
    data.append('status', 0)
    await api.put(`/users/${row.id}/status`, data)
    ElMessage.success('已处理为离职')
    await loadTeamMembers()
  } catch (e) { ElMessage.error('操作失败') }
}

const handleEnableUser = async (row) => {
  await ElMessageBox.confirm(`确定恢复「${row.real_name}」为在职员工？`, '确认')
  try {
    const data = new URLSearchParams()
    data.append('status', 1)
    await api.put(`/users/${row.id}/status`, data)
    ElMessage.success('已恢复在职')
    await loadTeamMembers()
    await loadOffboardUsers()
  } catch (e) { ElMessage.error('操作失败') }
}

// ============ 离职分配 ============
const loadOffboardUsers = async () => {
  loading3.value = true
  try {
    offboardUsers.value = await api.get('/team/offboard')
  } catch (e) { ElMessage.error('加载离职人员失败') }
  finally { loading3.value = false }
}

const handleReassign = async (row) => {
  const toId = reassignTo[row.id]
  if (!toId) return
  const toUser = activeUsers.value.find(u => u.id === toId)
  await ElMessageBox.confirm(
    `确定将「${row.real_name}」的 ${row.customer_count || 0} 名客户全部转移给「${toUser?.real_name}」？`,
    '批量转移确认', { type: 'warning' }
  )
  reassignLoading[row.id] = true
  try {
    const data = new URLSearchParams()
    data.append('from_user_id', row.id)
    data.append('to_user_id', toId)
    const res = await api.post('/team/reassign-all', data)
    ElMessage.success(res.msg)
    reassignTo[row.id] = null
    await loadOffboardUsers()
  } catch (e) { ElMessage.error(e.detail || '转移失败') }
  finally { reassignLoading[row.id] = false }
}

const handleReenableUser = async (row) => {
  await ElMessageBox.confirm(`确定恢复「${row.real_name}」为在职员工？`, '确认')
  try {
    const data = new URLSearchParams()
    data.append('status', 1)
    await api.put(`/users/${row.id}/status`, data)
    ElMessage.success('已恢复在职')
    await loadOffboardUsers()
    await loadTeamMembers()
  } catch (e) { ElMessage.error('操作失败') }
}

// ============ 添加成员 ============
const handleAddUser = async () => {
  if (!newUser.real_name || !newUser.username) return ElMessage.warning('请填写姓名和账号')
  addLoading.value = true
  try {
    await api.post('/users', {
      username: newUser.username,
      password: newUser.password || '123456',
      real_name: newUser.real_name,
      role: newUser.role,
      position: newUser.position,
      manager_id: newUser.manager_id || 0,
      entry_date: newUser.entry_date || '',
      daily_quota: newUser.daily_quota,
      dept_id: departments.value[0]?.id || 1
    })
    ElMessage.success('成员已添加')
    addUserVisible.value = false
    Object.assign(newUser, { real_name: '', username: '', password: '', role: 5,
      position: '', manager_id: '', entry_date: '', daily_quota: 50 })
    await loadTeamMembers()
    await loadAllUsers()
  } catch (e) { ElMessage.error(e.detail || '添加失败') }
  finally { addLoading.value = false }
}

// 加载所有用户（含离职）
const loadAllUsers = async () => {
  try {
    allUsers.value = await api.get('/users')
  } catch (e) {}
}

// 加载部门
const loadDepartments = async () => {
  try {
    departments.value = await api.get('/departments')
  } catch (e) { departments.value = [] }
}

onMounted(async () => {
  await loadDepartments()
  await loadAllUsers()
  await loadTeamMembers()
})
</script>

<style scoped>
.team-tabs {
  display: flex;
  border-bottom: 2px solid #FCE4EC;
  margin-bottom: 0;
}
.team-tab {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 20px;
  cursor: pointer;
  font-size: 14px;
  color: #888;
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  transition: all 0.2s;
  position: relative;
}
.team-tab:hover { color: #E91E63; }
.team-tab.active {
  color: #E91E63;
  border-bottom-color: #E91E63;
  font-weight: 600;
}
.tab-badge { position: absolute; top: 4px; right: 4px; }

.avatar-circle {
  width: 28px; height: 28px; border-radius: 50%;
  background: linear-gradient(135deg, #E91E63, #F48FB1);
  display: flex; align-items: center; justify-content: center;
  color: white; font-size: 11px; font-weight: bold;
  flex-shrink: 0;
}

:deep(.clickable-row) { cursor: pointer; }
:deep(.clickable-row:hover) { background: #f0f9ff !important; }

/* 离职员工卡片网格 */
.offboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
  padding: 4px 0;
}
.offboard-card {
  border: 1px solid #ffe58f;
  border-radius: 8px;
  background: linear-gradient(135deg, #fffbe6 0%, #fff 100%);
  padding: 16px;
  display: flex;
  gap: 14px;
  align-items: flex-start;
}
.offboard-avatar {
  width: 44px; height: 44px; border-radius: 50%;
  background: linear-gradient(135deg, #888, #aaa);
  display: flex; align-items: center; justify-content: center;
  color: white; font-size: 16px; font-weight: bold;
  flex-shrink: 0;
}
.offboard-info { flex: 1; }
.offboard-name { font-size: 15px; font-weight: 600; color: #333; margin-bottom: 4px; }
.offboard-meta { font-size: 12px; color: #888; margin-bottom: 8px; }
.offboard-count { display: flex; align-items: baseline; }
</style>
