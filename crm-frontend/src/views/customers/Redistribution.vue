<template>
  <div>
    <div class="page-header">
      <h3>再分配客户</h3>
      <div style="display:flex; gap:8px">
        <el-button type="primary" @click="importVisible = true">
          <el-icon><Upload /></el-icon> 数据导入
        </el-button>
      </div>
    </div>

    <!-- 提示条 -->
    <el-alert
      title="再分配说明"
      type="info"
      :closable="false"
      style="margin:12px 0; border-radius:8px"
      show-icon
    >
      <template #default>
        被主管重新分配的客户会显示在此处，您可以继续跟进。
        点击上方「数据导入」可批量导入客户数据（Excel格式）。
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
        <!-- 入池类型（再分配固定为再分配） -->
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
            <el-option v-for="(name,val) in options.statusMap" :key="val" :label="name" :value="Number(val)" />
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
            <el-option v-for="s in options.sources || []" :key="s" :label="s" :value="s" />
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
            <el-option v-for="(name,val) in options.loanTypeMap" :key="val" :label="name" :value="Number(val)" />
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

    <!-- 表格 -->
    <el-card>
      <el-table :data="customers" v-loading="loading" @row-click="openDetail" row-class-name="clickable-row" :stripe="true" size="small">
        <el-table-column label="ID" prop="id" width="70" />
        <el-table-column label="姓名" prop="name" width="90">
          <template #default="{row}">
            <span :style="{color: row.is_important ? '#F56C6C' : ''}">{{ row.name || '—' }}</span>
            <el-tag v-if="row.is_important" type="danger" size="small" style="margin-left:4px">重要</el-tag>
            <el-tag v-if="row.is_locked" type="warning" size="small" style="margin-left:4px">🔒</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="手机" prop="phone" width="120" />
        <el-table-column label="性别" prop="genderText" width="50" />
        <el-table-column label="城市" prop="city" width="80" />
        <el-table-column label="年龄" prop="age" width="50" />
        <el-table-column label="状态" prop="statusText" width="90">
          <template #default="{row}"><el-tag size="small" :type="statusTagType[row.status]">{{ row.statusText }}</el-tag></template>
        </el-table-column>
        <el-table-column label="星级" prop="star_level" width="70">
          <template #default="{row}"><span style="color:#E6A23C">★</span>{{ row.star_level }}</template>
        </el-table-column>
        <el-table-column label="额度(万)" prop="apply_amount" width="80" />
        <el-table-column label="贷款类型" prop="loanTypeText" width="80" />
        <el-table-column label="来源" prop="source" width="100" show-overflow-tooltip />
        <el-table-column label="创建时间" prop="created_at" width="140">
          <template #default="{row}">{{ fmt(row.created_at) }}</template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div style="margin-top:12px; display:flex; justify-content:space-between; align-items:center">
        <span style="color:#888; font-size:13px">共 {{ total }} 条</span>
        <el-pagination
          background
          layout="prev,pager,next"
          :total="total"
          :page-size="params.page_size"
          v-model:current-page="params.page"
          @current-change="loadData"
        />
      </div>
    </el-card>

    <!-- 数据导入对话框 -->
    <el-dialog v-model="importVisible" title="数据导入" width="520px" :close-on-click-modal="false">
      <div class="import-area" @dragover.prevent @drop.prevent="handleDrop" @click="triggerFile">
        <div class="import-icon"><el-icon size="40" color="#E91E63"><Upload /></el-icon></div>
        <div class="import-text">
          <p style="font-size:14px; color:#333; margin:0 0 4px">拖拽 Excel 文件到此处</p>
          <p style="font-size:12px; color:#999; margin:0">或点击选择文件，支持 .xlsx / .xls 格式</p>
        </div>
        <input ref="fileInput" type="file" accept=".xlsx,.xls" style="display:none" @change="handleFileChange" />
      </div>

      <!-- 导入模板说明 -->
      <div class="import-template">
        <div class="template-title"><el-icon><InfoFilled /></el-icon> Excel 格式要求</div>
        <div style="font-size:12px; color:#666; line-height:1.8; margin-top:8px">
          <p>Excel 文件需包含以下列（第一行为表头）：</p>
          <div class="template-table">
            <table>
              <tr><th>手机号</th><th>姓名</th><th>性别</th><th>城市</th><th>年龄</th><th>申请额度</th><th>贷款类型</th><th>来源</th></tr>
              <tr><td>13800138000</td><td>张三</td><td>男</td><td>杭州</td><td>35</td><td>30</td><td>信用贷</td><td>BXMJ-excel</td></tr>
            </table>
          </div>
          <p style="margin-top:8px; color:#E91E63">* 手机号为必填项，其他字段可选</p>
        </div>
      </div>

      <!-- 导入历史 -->
      <div v-if="importHistory.length" class="import-history">
        <div class="template-title"><el-icon><Clock /></el-icon> 最近导入记录</div>
        <div v-for="h in importHistory" :key="h.time" style="font-size:12px; color:#666; padding:4px 0">
          {{ h.time }} — 成功导入 {{ h.count }} 条客户数据
        </div>
      </div>

      <template #footer>
        <el-button @click="importVisible=false">关闭</el-button>
        <el-button type="primary" :loading="importLoading" @click="triggerFile">
          <el-icon><Upload /></el-icon> 选择文件
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, inject } from 'vue'
import { ElMessage } from 'element-plus'
import { getCustomers, getAllOptions, getDepts, getTeamMembers } from '../../api'
import { Upload, Search, InfoFilled, Clock } from '@element-plus/icons-vue'

const openCustomerDetail = inject('openCustomerDetail', null)

const customers = ref([])
const total = ref(0)
const loading = ref(false)
const options = ref({ statusMap: {}, loanTypeMap: {}, sources: [], cityList: [] })

const importVisible = ref(false)
const importLoading = ref(false)
const fileInput = ref()
const importHistory = ref([])
const selectedStatuses = ref([])
const selectedStars = ref([])
const selectedSources = ref([])
const deptList = ref([])
const memberList = ref([])

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
  dept_id: -1,
  other_condition: -1,
  quals_keyword: '',
  page: 1,
  page_size: 20,
  sort_field: 'created_at',
  sort_order: 'desc',
  data_type: 2  // 再分配
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
  if (params.dept_id !== -1) c++
  if (params.other_condition !== -1) c++
  if (params.quals_keyword) c++
  return c
})

const statusTagType = {
  0:'', 1:'success', 2:'info', 3:'warning', 4:'warning', 5:'',
  6:'', 7:'success', 8:'success', 9:'danger', 10:'', 11:'info',
  12:'danger', 13:'danger', 14:'danger', 15:'', 16:'danger', 17:'danger', 18:''
}

const fmt = (t) => t ? t.replace('T',' ').substring(0,16) : '—'

const onDeptChange = async (deptId) => {
  if (deptId && deptId !== -1) {
    const res = await getTeamMembers(deptId)
    memberList.value = res.members || []
  } else {
    memberList.value = []
  }
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
    if (p.dept_id < 0) delete p.dept_id
    if (p.other_condition < 0) delete p.other_condition
    if (!p.quals_keyword) delete p.quals_keyword
    if (p.pool_type < 0) delete p.pool_type
    if (p.time_type < 0) delete p.time_type
    const res = await getCustomers(p)
    customers.value = res.items
    total.value = res.total
  } catch(e) { ElMessage.error(e.detail || '加载失败') }
  finally { loading.value = false }
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
    remark_count_min: 0, remark_count_max: 0, remark_history: -1,
    dept_id: -1, other_condition: -1, quals_keyword: ''
  })
  selectedStatuses.value = []
  selectedStars.value = []
  selectedSources.value = []
  memberList.value = []
  loadData(1)
}

const openDetail = (row) => {
  if (openCustomerDetail) openCustomerDetail(row.id, row.name)
}

const triggerFile = () => fileInput.value?.click()

const handleFileChange = async (e) => {
  const file = e.target.files[0]
  if (file) await processFile(file)
  e.target.value = ''
}

const handleDrop = async (e) => {
  const file = e.dataTransfer.files[0]
  if (file) await processFile(file)
}

const processFile = async (file) => {
  if (!file.name.match(/\.(xlsx|xls)$/i)) {
    return ElMessage.error('请选择 Excel 文件（.xlsx 或 .xls）')
  }
  importLoading.value = true
  try {
    const formData = new FormData()
    formData.append('file', file)
    const response = await fetch('/api/customers/import-file', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` },
      body: formData
    })
    if (!response.ok) {
      const err = await response.json()
      throw new Error(err.detail || '导入失败')
    }
    const result = await response.json()
    ElMessage.success(`成功导入 ${result.count || 0} 条客户数据`)
    importHistory.value.unshift({
      time: new Date().toLocaleString(),
      count: result.count || 0
    })
    if (importHistory.value.length > 5) importHistory.value.pop()
    importVisible.value = false
    loadData(1)
  } catch(e) {
    ElMessage.error(e.message || '导入失败，请检查文件格式')
  } finally {
    importLoading.value = false
  }
}

onMounted(async () => {
  const opts = await getAllOptions()
  options.value = opts
  // 加载部门列表
  try {
    const deptRes = await getDepts()
    deptList.value = deptRes.departments || deptRes.items || []
  } catch(e) {}
  loadData()
})
</script>

<style scoped>
.filter-row { display:flex; flex-wrap:wrap; align-items:center; gap:12px; margin-bottom:4px }
.filter-group { display:flex; align-items:center; gap:6px }
.filter-label { font-size:12px; color:#666; white-space:nowrap }

.import-area {
  border:2px dashed #F48FB1; border-radius:12px; padding:40px;
  text-align:center; cursor:pointer; background:#FDF2F7; transition:all 0.2s; margin-bottom:16px;
}
.import-area:hover { border-color:#E91E63; background:#FCE4EC; }
.import-icon { margin-bottom:12px; }
.import-template { background:#F8F8F8; border-radius:8px; padding:16px; margin-bottom:12px; }
.template-title { font-size:13px; font-weight:600; color:#333; display:flex; align-items:center; gap:6px; }
.template-table { overflow-x:auto; margin-top:8px; }
.template-table table { width:100%; border-collapse:collapse; font-size:11px; }
.template-table th, .template-table td { border:1px solid #eee; padding:4px 8px; text-align:center; }
.template-table th { background:#FCE4EC; color:#E91E63; }
.import-history { background:#F8F8F8; border-radius:8px; padding:12px 16px; }

:deep(.clickable-row) { cursor: pointer; }
:deep(.clickable-row:hover) { background: #f0f9ff !important; }
</style>
