<template>
  <div>
    <div class="page-header">
      <h3>公共池</h3>
      <div>
        <el-tag type="danger" size="large" style="font-size:14px; padding:6px 16px">
          池中共有 <strong>{{ poolCount }}</strong> 名客户
        </el-tag>
      </div>
    </div>

    <!-- 提示条 -->
    <el-alert
      title="公共池说明"
      type="info"
      :closable="false"
      style="margin:12px 0; border-radius:8px"
      show-icon
    >
      <template #default>
        公共池中的客户来自顾问主动存入或系统分配。您可以领取感兴趣的客户，被领取后自动进入「我的客户」。
      </template>
    </el-alert>

    <!-- 高级筛选（完全按老系统三行结构） -->
    <el-card style="margin:12px 0">

      <!-- 第一行：关键词 + 入池类型 + 时间类型 + 状态 + 星级 -->
      <div class="filter-row">
        <!-- 关键词 -->
        <div class="filter-group">
          <span class="filter-label">客户</span>
          <el-input v-model="params.keyword" placeholder="请输入" clearable style="width:140px" @keyup.enter="loadData(1)">
            <template #prepend>
              <el-select v-model="params.kw_type" style="width:80px" :clearable="false">
                <el-option label="综合" value="" />
                <el-option label="手机" value="phone" />
                <el-option label="姓名" value="name" />
                <el-option label="ID" value="id" />
              </el-select>
            </template>
          </el-input>
        </div>
        <!-- 入池类型 -->
        <div class="filter-group">
          <span class="filter-label">入池类型</span>
          <el-select v-model="params.pool_type" clearable placeholder="不限" style="width:120px" size="small">
            <el-option label="不限" :value="-1" />
            <el-option label="重新分配" :value="2" />
            <el-option label="存入公共池" :value="3" />
            <el-option label="转介" :value="4" />
          </el-select>
        </div>
        <!-- 时间类型 -->
        <div class="filter-group">
          <span class="filter-label">时间类型</span>
          <el-select v-model="params.time_type" clearable placeholder="不限" style="width:110px" size="small">
            <el-option label="不限" :value="-1" />
            <el-option label="入池时间" :value="1" />
            <el-option label="创建时间" :value="2" />
          </el-select>
        </div>
        <!-- 状态 -->
        <div class="filter-group">
          <span class="filter-label">状态</span>
          <el-select v-model="selectedStatuses" multiple clearable collapse-tags placeholder="全部状态" style="width:130px" size="small">
            <el-option v-for="(name,val) in statusMap" :key="val" :label="name" :value="Number(val)" />
          </el-select>
        </div>
        <!-- 星级 -->
        <div class="filter-group">
          <span class="filter-label">星级</span>
          <el-select v-model="selectedStars" multiple clearable collapse-tags placeholder="全部星级" style="width:110px" size="small">
            <el-option v-for="n in 7" :key="n-1" :label="(n-1)+'星'" :value="n-1" />
          </el-select>
        </div>
      </div>

      <!-- 第二行：未备注超过 + 备注关键词 + 备注次数 + 备注历史 + 锁定 -->
      <div class="filter-row" style="margin-top:8px">
        <!-- 未备注超过N天 -->
        <div class="filter-group">
          <span class="filter-label">未备注超过</span>
          <el-input-number v-model="params.no_remark_days" :min="0" :max="9999" placeholder="天" style="width:80px" size="small" controls-position="right" :step="1" />
          <span style="font-size:11px;color:#999">天</span>
        </div>
        <!-- 备注关键词 -->
        <div class="filter-group">
          <span class="filter-label">备注关键词</span>
          <el-input v-model="params.remark_keyword" placeholder="备注关键词" clearable style="width:120px" size="small" />
        </div>
        <!-- 备注次数 -->
        <div class="filter-group">
          <span class="filter-label">备注次数</span>
          <el-input-number v-model="params.remark_count_min" :min="0" :max="9999" placeholder="最小" style="width:70px" size="small" controls-position="right" :step="1" />
          <span style="margin:0 4px;color:#999">~</span>
          <el-input-number v-model="params.remark_count_max" :min="0" :max="9999" placeholder="最大" style="width:70px" size="small" controls-position="right" :step="1" />
        </div>
        <!-- 备注历史 -->
        <div class="filter-group">
          <span class="filter-label">备注历史</span>
          <el-select v-model="params.remark_history" clearable placeholder="不限" style="width:110px" size="small">
            <el-option label="不限" :value="-1" />
            <el-option label="今天" :value="0" />
            <el-option label="近三天" :value="3" />
            <el-option label="近一周" :value="7" />
            <el-option label="近一月" :value="30" />
            <el-option label="近三月" :value="90" />
            <el-option label="近半年" :value="180" />
          </el-select>
        </div>
        <!-- 备注顾问 -->
        <div class="filter-group">
          <span class="filter-label">备注顾问</span>
          <el-select v-model="params.remark_advisor_id" clearable filterable placeholder="不限" style="width:120px" size="small">
            <el-option label="不限" :value="-1" />
            <el-option v-for="u in remarkAdvisorList" :key="u.id" :label="u.name || u.username" :value="u.id" />
          </el-select>
        </div>
        <!-- 锁定客户 -->
        <div class="filter-group">
          <span class="filter-label">锁定客户</span>
          <el-select v-model="params.locked" clearable placeholder="不限" style="width:100px" size="small">
            <el-option label="不限" :value="-1" />
            <el-option label="已锁定" :value="1" />
            <el-option label="未锁定" :value="0" />
          </el-select>
        </div>
      </div>

      <!-- 第三行：所属部门 + 来源 + 其他条件 + 贷款条件 + 资质关键词 -->
      <div class="filter-row" style="margin-top:8px">
        <!-- 所属部门 -->
        <div class="filter-group">
          <span class="filter-label">所属部门</span>
          <el-select v-model="params.dept_id" clearable filterable placeholder="不限" style="width:130px" size="small" @change="onDeptChange">
            <el-option label="不限" :value="-1" />
            <el-option v-for="d in deptList" :key="d.id" :label="d.name" :value="d.id" />
          </el-select>
        </div>
        <!-- 来源 -->
        <div class="filter-group">
          <span class="filter-label">来源</span>
          <el-select v-model="selectedSources" multiple clearable collapse-tags placeholder="来源" style="width:150px" size="small">
            <el-option v-for="s in sourcesList" :key="s" :label="s" :value="s" />
          </el-select>
        </div>
        <!-- 其他条件 -->
        <div class="filter-group">
          <span class="filter-label">其他条件</span>
          <el-select v-model="params.other_condition" clearable placeholder="不限" style="width:130px" size="small">
            <el-option label="不限" :value="-1" />
            <el-option label="第一个备注顾问" :value="1" />
            <el-option label="第一次跟进时间" :value="2" />
            <el-option label="第一次贷款申请时间" :value="3" />
          </el-select>
        </div>
        <!-- 贷款条件 -->
        <div class="filter-group">
          <span class="filter-label">贷款条件</span>
          <el-select v-model="params.loan_type" clearable placeholder="不限" style="width:110px" size="small">
            <el-option label="不限" :value="-1" />
            <el-option v-for="(name,val) in loanTypeMap" :key="val" :label="name" :value="Number(val)" />
          </el-select>
        </div>
        <!-- 资质关键词 -->
        <div class="filter-group">
          <span class="filter-label">资质关键词</span>
          <el-input v-model="params.quals_keyword" placeholder="资质关键词" clearable style="width:130px" size="small" />
        </div>
        <!-- 按钮 -->
        <div class="filter-group" style="display:flex;align-items:flex-end;gap:6px">
          <el-button type="primary" size="small" @click="loadData(1)"><Search /> 搜索</el-button>
          <el-button size="small" @click="resetParams">重置</el-button>
          <span style="color:#E91E63;font-size:12px;margin-left:4px" v-if="activeFilterCount > 0">已选 {{ activeFilterCount }} 个筛选条件</span>
        </div>
      </div>
    </el-card>

    <el-card>
      <!-- 批量操作栏 -->
      <div v-if="selectedRows.length > 0" class="batch-bar">
        <span style="font-size:13px">已选 <b style="color:#E91E63">{{ selectedRows.length }}</b> 条</span>
        <el-button type="primary" size="small" @click="batchClaim">批量领取</el-button>
        <el-button v-if="isAdmin" type="warning" size="small" @click="openBatchAssignDialog">批量分配</el-button>
      </div>

      <el-table :data="customers" v-loading="loading" @row-click="openDetail" row-class-name="clickable-row" size="small" :stripe="true"
        @selection-change="onSelectionChange">
        <el-table-column type="selection" width="40" />
        <el-table-column label="姓名" prop="name" width="90">
          <template #default="{row}">
            <span :style="{color: row.is_important ? '#F56C6C' : ''}">{{ row.name || '—' }}</span>
            <el-tag v-if="row.is_important" type="danger" size="small" style="margin-left:4px">重要</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="手机" prop="phone" width="120" />
        <el-table-column label="性别" prop="genderText" width="50" />
        <el-table-column label="城市" prop="city" width="80" />
        <el-table-column label="年龄" prop="age" width="50" />
        <el-table-column label="状态" prop="statusText" width="90">
          <template #default="{row}">
            <el-tag size="small">{{ row.statusText }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="星级" width="70">
          <template #default="{row}"><span style="color:#E6A23C">★</span>{{ row.star_level }}星</template>
        </el-table-column>
        <el-table-column label="额度(万)" prop="apply_amount" width="80" />
        <el-table-column label="贷款类型" prop="loanTypeText" width="80" />
        <el-table-column label="来源" prop="source" width="100" show-overflow-tooltip />
        <el-table-column label="创建时间" prop="created_at" width="140">
          <template #default="{row}">{{ fmt(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="160">
          <template #default="{row}">
            <el-button type="primary" size="small" @click.stop="handleFromPool(row)">领取</el-button>
            <el-button v-if="isAdmin" type="warning" size="small" @click.stop="openAssignDialog(row)">分配</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div style="margin-top:12px; display:flex; justify-content:space-between; align-items:center">
        <div style="display:flex; align-items:center; gap:8px">
          <span style="color:#888; font-size:13px">共 <b style="color:#E91E63">{{ total }}</b> 条</span>
          <span style="color:#888; font-size:13px">每页</span>
          <el-select v-model="params.page_size" size="small" style="width:80px" @change="loadData(1)">
            <el-option :label="10" :value="10" /><el-option :label="20" :value="20" />
            <el-option :label="50" :value="50" /><el-option :label="100" :value="100" /><el-option :label="200" :value="200" />
          </el-select>
        </div>
        <el-pagination background layout="prev,pager,next" :total="total" :page-size="params.page_size" v-model:current-page="params.page" @current-change="loadData" />
      </div>
    </el-card>

    <!-- 单个分配对话框 -->
    <el-dialog v-model="assignDialogVisible" title="分配给顾问" width="420px" :close-on-click-modal="false">
      <div style="padding:8px 0">
        <span style="font-size:14px">选择目标顾问：</span>
        <el-select v-model="assignTargetUserId" placeholder="请选择顾问" style="width:100%;margin-top:12px" size="large">
          <el-option v-for="u in allUsersList" :key="u.id" :label="u.real_name || u.username" :value="u.id" />
        </el-select>
      </div>
      <template #footer>
        <el-button @click="assignDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="doAssign">确认分配</el-button>
      </template>
    </el-dialog>

    <!-- 批量分配对话框 -->
    <el-dialog v-model="batchAssignDialogVisible" title="批量分配给顾问" width="420px" :close-on-click-modal="false">
      <div style="padding:8px 0">
        <span style="font-size:14px">已选 <b>{{ selectedRows.length }}</b> 条客户，选择目标顾问：</span>
        <el-select v-model="batchAssignTargetUserId" placeholder="请选择顾问" style="width:100%;margin-top:12px" size="large">
          <el-option v-for="u in allUsersList" :key="u.id" :label="u.real_name || u.username" :value="u.id" />
        </el-select>
      </div>
      <template #footer>
        <el-button @click="batchAssignDialogVisible = false">取消</el-button>
        <el-button type="warning" @click="doBatchAssign">确认批量分配</el-button>
      </template>
    </el-dialog>

  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, inject } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { getPool, fromPool, getPoolCount, getAllOptions, getDepts, getTeamMembers, getUsers, poolAssign, poolBatchAssign } from '../api'
import { useRouter } from 'vue-router'

const openCustomerDetail = inject('openCustomerDetail', null)

const customers = ref([])
const total = ref(0)
const loading = ref(false)
const poolCount = ref(0)
const selectedRows = ref([])
const statusMap = ref({})
const loanTypeMap = ref({})
const sourcesList = ref([])
const deptList = ref([])
const memberList = ref([])
const remarkAdvisorList = ref([])
const selectedStatuses = ref([])
const selectedStars = ref([])
const selectedSources = ref([])
const currentUser = ref({})
const allUsersList = ref([])
const isAdmin = computed(() => (currentUser.value?.role || 0) >= 2)
const assignDialogVisible = ref(false)
const assignTargetUserId = ref(null)
const assignCustomerId = ref(null)
const batchAssignDialogVisible = ref(false)
const batchAssignTargetUserId = ref(null)

const params = reactive({
  kw_type: '',
  keyword: '',
  pool_type: -1,
  time_type: -1,
  status: -1,
  status_list: '',
  star: -1,
  star_list: '',
  loan_type: -1,
  locked: -1,
  important: -1,
  sources: [],
  city: '',
  age_min: 0,
  age_max: 0,
  marital_status: -1,
  has_insurance: -1,
  has_credit_card: -1,
  // 新增字段
  no_remark_days: 0,
  remark_keyword: '',
  remark_count_min: 0,
  remark_count_max: 0,
  remark_history: -1,
  remark_advisor_id: -1,
  dept_id: -1,
  other_condition: -1,
  quals_keyword: '',
  page: 1,
  page_size: 20
})

const activeFilterCount = computed(() => {
  let c = 0
  if (params.keyword) c++
  if (params.pool_type !== -1) c++
  if (params.time_type !== -1) c++
  if (selectedStatuses.value.length > 0) c++
  if (selectedStars.value.length > 0) c++
  if (params.loan_type !== -1) c++
  if (params.locked !== -1) c++
  if (params.important !== -1) c++
  if (selectedSources.value.length > 0) c++
  if (params.city) c++
  if (params.age_min > 0 || params.age_max > 0) c++
  if (params.marital_status >= 0) c++
  if (params.has_insurance !== -1) c++
  if (params.has_credit_card !== -1) c++
  if (params.no_remark_days > 0) c++
  if (params.remark_keyword) c++
  if (params.remark_count_min > 0 || params.remark_count_max > 0) c++
  if (params.remark_history !== -1) c++
  if (params.remark_advisor_id !== -1) c++
  if (params.dept_id !== -1) c++
  if (params.other_condition !== -1) c++
  if (params.quals_keyword) c++
  return c
})

const fmt = t => t ? t.replace('T',' ').substring(0,16) : '—'

const onDeptChange = async (deptId) => {
  if (deptId && deptId !== -1) {
    const res = await getTeamMembers(deptId)
    memberList.value = res.members || []
  } else {
    memberList.value = []
  }
}

const resetParams = () => {
  Object.assign(params, {
    kw_type: '', keyword: '', pool_type: -1, time_type: -1,
    status: -1, status_list: '', star: -1, star_list: '',
    loan_type: -1, locked: -1, important: -1,
    sources: [], city: '',
    age_min: 0, age_max: 0, marital_status: -1,
    has_insurance: -1, has_credit_card: -1,
    no_remark_days: 0, remark_keyword: '',
    remark_count_min: 0, remark_count_max: 0, remark_history: -1, remark_advisor_id: -1,
    dept_id: -1, other_condition: -1, quals_keyword: ''
  })
  selectedStatuses.value = []
  selectedStars.value = []
  selectedSources.value = []
  selectedRows.value = []
  memberList.value = []
  loadData(1)
}

const loadData = async (page = params.page) => {
  params.page = page
  params.status_list = selectedStatuses.value.join(',')
  params.star_list = selectedStars.value.join(',')
  params.status = selectedStatuses.value.length > 0 ? -1 : params.status
  params.star = selectedStars.value.length > 0 ? -1 : params.star

  loading.value = true
  try {
    const p = { ...params }
    // 来源：数组转逗号分隔字符串
    if (p.sources && p.sources.length > 0) {
      p.sources = p.sources.join(',')
    } else {
      delete p.sources
    }
    // 删除默认值参数
    if (p.status < 0) delete p.status
    if (p.star < 0) delete p.star
    if (p.loan_type < 0) delete p.loan_type
    if (p.locked < 0) delete p.locked
    if (p.important < 0) delete p.important
    if (!p.city) delete p.city
    if (p.age_min <= 0) delete p.age_min
    if (p.age_max <= 0) delete p.age_max
    if (p.marital_status < 0) delete p.marital_status
    if (p.has_insurance < 0) delete p.has_insurance
    if (p.has_credit_card < 0) delete p.has_credit_card
    if (!p.status_list) delete p.status_list
    if (!p.star_list) delete p.star_list
    if (p.no_remark_days <= 0) delete p.no_remark_days
    if (!p.remark_keyword) delete p.remark_keyword
    if (p.remark_count_min <= 0) delete p.remark_count_min
    if (p.remark_count_max <= 0) delete p.remark_count_max
    if (p.remark_history < 0) delete p.remark_history
    if (p.remark_advisor_id < 0) delete p.remark_advisor_id
    if (p.dept_id < 0) delete p.dept_id
    if (p.other_condition < 0) delete p.other_condition
    if (!p.quals_keyword) delete p.quals_keyword
    const res = await getPool(p)
    customers.value = res.items
    total.value = res.total
  } catch(e) { ElMessage.error(e.detail || '加载失败') }
  finally { loading.value = false }
}

const openDetail = (row) => {
  if (openCustomerDetail) openCustomerDetail(row.id, row.name)
}

const handleFromPool = async (row) => {
  await ElMessageBox.confirm(`确定领取客户「${row.name || row.phone}」？`, '领取确认', { type: 'warning' })
  try {
    await fromPool(row.id)
    ElMessage.success('领取成功！该客户已进入再分配池')
    poolCount.value = (await getPoolCount()).count
    loadData()
  } catch(e) { ElMessage.error(e.detail || e || '领取失败') }
}

// 多选变化
const onSelectionChange = (selection) => {
  selectedRows.value = selection
}

// 批量领取
const batchClaim = async () => {
  if (selectedRows.value.length === 0) return
  await ElMessageBox.confirm(
    `确定批量领取选中的 ${selectedRows.value.length} 名客户？`,
    '批量领取确认',
    { type: 'warning' }
  )
  try {
    const promises = selectedRows.value.map(row => fromPool(row.id))
    await Promise.all(promises)
    ElMessage.success(`成功领取 ${selectedRows.value.length} 名客户！`)
    selectedRows.value = []
    poolCount.value = (await getPoolCount()).count
    loadData()
  } catch(e) { ElMessage.error(e.detail || e || '批量领取失败') }
}

// ============ 管理员分配功能 ============
// 单个分配
const openAssignDialog = (row) => {
  assignCustomerId.value = row.id
  assignTargetUserId.value = null
  assignDialogVisible.value = true
}

const doAssign = async () => {
  if (!assignTargetUserId.value) {
    ElMessage.warning('请选择目标顾问')
    return
  }
  try {
    await poolAssign(assignCustomerId.value, assignTargetUserId.value)
    ElMessage.success('分配成功！客户已归入再分配池')
    assignDialogVisible.value = false
    poolCount.value = (await getPoolCount()).count
    loadData()
  } catch(e) { ElMessage.error(e.detail || e || '分配失败') }
}

// 批量分配
const openBatchAssignDialog = () => {
  if (selectedRows.value.length === 0) {
    ElMessage.warning('请先选择客户')
    return
  }
  batchAssignTargetUserId.value = null
  batchAssignDialogVisible.value = true
}

const doBatchAssign = async () => {
  if (!batchAssignTargetUserId.value) {
    ElMessage.warning('请选择目标顾问')
    return
  }
  try {
    await poolBatchAssign(selectedRows.value.map(r => r.id), batchAssignTargetUserId.value)
    ElMessage.success('批量分配成功！客户已归入再分配池')
    batchAssignDialogVisible.value = false
    selectedRows.value = []
    poolCount.value = (await getPoolCount()).count
    loadData()
  } catch(e) { ElMessage.error(e.detail || e || '批量分配失败') }
}

onMounted(async () => {
  // 加载当前用户
  try {
    const u = JSON.parse(localStorage.getItem('user') || '{}')
    currentUser.value = u
    // 管理员/主管：加载所有用户用于分配
    if ((u.role || 0) >= 2) {
      const allRes = await getUsers()
      allUsersList.value = Array.isArray(allRes) ? allRes : (allRes.items || [])
    }
  } catch(e) {}

  const opts = await getAllOptions()
  statusMap.value = opts.statusMap || {}
  loanTypeMap.value = opts.loanTypeMap || {}
  sourcesList.value = opts.sources || []
  poolCount.value = (await getPoolCount()).count
  // 加载部门列表
  try {
    const deptRes = await getDepts()
    deptList.value = deptRes.departments || deptRes.items || []
  } catch(e) {}
  // 加载所有顾问列表（用于备注顾问筛选）
  try {
    const usersRes = await getUsers()
    remarkAdvisorList.value = Array.isArray(usersRes) ? usersRes : (usersRes.items || [])
  } catch(e) {}
  loadData()
})
onUnmounted(() => {})
</script>

<style scoped>
.filter-row { display:flex; flex-wrap:wrap; align-items:center; gap:12px; margin-bottom:4px }
.filter-group { display:flex; align-items:center; gap:6px }
.filter-label { font-size:12px; color:#666; white-space:nowrap }

:deep(.clickable-row) { cursor: pointer; }
:deep(.clickable-row:hover) { background: #f0f9ff !important; }

.batch-bar {
  display: flex; align-items: center; gap: 12px;
  background: #fff7ed; border: 1px solid #f59e0b;
  border-radius: 6px; padding: 8px 16px; margin-bottom: 12px;
}
</style>
