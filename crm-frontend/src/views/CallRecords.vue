<template>
  <div>
    <div class="page-header">
      <h3>通话管理</h3>
      <el-button type="primary" size="small" @click="addVisible = true">
        <el-icon><Plus /></el-icon> 记录通话
      </el-button>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="12" style="margin-bottom:14px">
      <el-col :span="4">
        <el-card shadow="hover" class="stat-card" style="border-top:3px solid #E91E63">
          <div style="font-size:11px; color:#888">今日拨出</div>
          <div class="stat-num" style="color:#E91E63">{{ todayStats.total }}</div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card shadow="hover" class="stat-card" style="border-top:3px solid #67C23A">
          <div style="font-size:11px; color:#888">今日接通</div>
          <div class="stat-num" style="color:#67C23A">{{ todayStats.connected }}</div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card shadow="hover" class="stat-card" style="border-top:3px solid #409EFF">
          <div style="font-size:11px; color:#888">接通率</div>
          <div class="stat-num" style="color:#409EFF">{{ todayStats.connect_rate }}%</div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card shadow="hover" class="stat-card" style="border-top:3px solid #E6A23C">
          <div style="font-size:11px; color:#888">今日通话(秒)</div>
          <div class="stat-num" style="color:#E6A23C">{{ todayStats.total_duration }}</div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card shadow="hover" class="stat-card" style="border-top:3px solid #909399">
          <div style="font-size:11px; color:#888">均通话时长(秒)</div>
          <div class="stat-num" style="color:#909399">{{ todayStats.avg_duration }}</div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card shadow="hover" class="stat-card" style="border-top:3px solid #F56C6C">
          <div style="font-size:11px; color:#888">本月拨出</div>
          <div class="stat-num" style="color:#F56C6C">{{ monthStats.total }}</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 接通结果分布 -->
    <el-card style="margin-bottom:14px">
      <template #header>
        <span style="font-size:13px; font-weight:600">今日通话结果分布</span>
      </template>
      <div class="result-dist">
        <div v-for="(cnt, label) in todayStats.result_dist" :key="label" class="result-item"
          :class="{active: filterResult === label}"
          @click="filterResult === label ? filterResult = '' : filterResult = label; loadData(1)">
          <div class="result-label">{{ label }}</div>
          <div class="result-count">{{ cnt }}</div>
          <div class="result-bar">
            <div class="result-bar-fill" :style="{width: todayStats.total ? (cnt/todayStats.total*100)+'%' : '0%', background: resultColors[label]}"></div>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 筛选栏 -->
    <el-card style="margin-bottom:12px">
      <el-form inline @submit.prevent="loadData(1)">
        <el-form-item label="关键词">
          <el-input v-model="params.keyword" placeholder="客户姓名/手机" clearable style="width:150px" />
        </el-form-item>
        <el-form-item label="通话结果">
          <el-select v-model="params.call_result" clearable placeholder="全部" style="width:100px">
            <el-option v-for="(n,v) in callResultMap" :key="v" :label="n" :value="Number(v)" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="isManager" label="顾问">
          <el-select v-model="params.advisor_id" clearable placeholder="全部" style="width:120px">
            <el-option v-for="u in teamUsers" :key="u.id" :label="u.real_name" :value="u.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="日期">
          <el-date-picker v-model="dateRange" type="daterange" range-separator="至"
            start-placeholder="开始" end-placeholder="结束" value-format="YYYY-MM-DD"
            size="default" style="width:220px" @change="onDateChange" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData(1)"><Search /> 搜索</el-button>
        </el-form-item>
        <el-form-item><el-button @click="resetParams">重置</el-button></el-form-item>
      </el-form>
    </el-card>

    <!-- 通话记录表格 -->
    <el-card>
      <el-table :data="records" v-loading="loading" size="small" :stripe="true">
        <el-table-column label="时间" width="150">
          <template #default="{row}">{{ fmt(row.call_at) }}</template>
        </el-table-column>
        <el-table-column label="客户" width="100">
          <template #default="{row}">
            <span class="link-name" @click="openCustomerDetail && openCustomerDetail(row.customer_id, row.customer_name)">
              {{ row.customer_name || '—' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="手机" prop="customer_phone" width="130" />
        <el-table-column label="顾问" prop="advisor_name" width="90" v-if="isManager" />
        <el-table-column label="类型" width="70">
          <template #default="{row}">
            <el-tag size="small" :type="row.call_type === 1 ? 'primary' : 'success'">
              {{ row.call_type_text }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="结果" width="90">
          <template #default="{row}">
            <el-tag size="small" :type="resultTagType[row.call_result]">{{ row.call_result_text }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="时长(秒)" prop="duration" width="90">
          <template #default="{row}">{{ row.duration ? row.duration + 's' : '—' }}</template>
        </el-table-column>
        <el-table-column label="备注" min-width="150" show-overflow-tooltip>
          <template #default="{row}">{{ row.note || '—' }}</template>
        </el-table-column>
        <el-table-column label="操作" width="70">
          <template #default="{row}">
            <el-button size="small" type="danger" link @click="deleteRecord(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div style="margin-top:12px; display:flex; justify-content:space-between; align-items:center">
        <span style="color:#888; font-size:13px">共 <b style="color:#E91E63">{{ total }}</b> 条</span>
        <el-pagination background layout="prev,pager,next" :total="total" :page-size="params.page_size"
          v-model:current-page="params.page" @current-change="loadData" />
      </div>
    </el-card>

    <!-- 记录通话弹窗 -->
    <el-dialog v-model="addVisible" title="记录通话" width="460px">
      <el-form :model="addForm" label-width="90px">
        <el-form-item label="客户" required>
          <el-select v-model="addForm.customer_id" filterable remote :remote-method="searchCustomers"
            :loading="searchLoading" placeholder="搜索客户姓名/手机" style="width:100%">
            <el-option v-for="c in searchList" :key="c.id"
              :label="`${c.name || '未命名'} (${c.phone || ''})`" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="通话类型">
          <el-radio-group v-model="addForm.call_type">
            <el-radio :value="1">呼出</el-radio>
            <el-radio :value="2">呼入</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="通话结果">
          <el-select v-model="addForm.call_result" style="width:100%">
            <el-option v-for="(n,v) in callResultMap" :key="v" :label="n" :value="Number(v)" />
          </el-select>
        </el-form-item>
        <el-form-item label="通话时长(秒)">
          <el-input-number v-model="addForm.duration" :min="0" :max="3600" style="width:100%" />
        </el-form-item>
        <el-form-item label="通话时间">
          <el-date-picker v-model="addForm.call_at" type="datetime" placeholder="默认当前时间"
            value-format="YYYY-MM-DDTHH:mm:ss" style="width:100%" />
        </el-form-item>
        <el-form-item label="通话备注">
          <el-input v-model="addForm.note" type="textarea" :rows="3" placeholder="记录通话内容要点..." maxlength="500" show-word-limit />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addVisible=false">取消</el-button>
        <el-button type="primary" :loading="saveLoading" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, inject } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'
import { getTeam } from '../api'

const openCustomerDetail = inject('openCustomerDetail', null)
const isManager = computed(() => JSON.parse(localStorage.getItem('user') || '{}').role >= 2)

const records = ref([])
const total = ref(0)
const loading = ref(false)
const dateRange = ref(null)
const filterResult = ref('')

const callResultMap = { 0: '未接', 1: '接通', 2: '占线', 3: '关机', 4: '空号', 5: '拒接' }
const resultTagType = { 0: 'info', 1: 'success', 2: 'warning', 3: 'danger', 4: 'danger', 5: 'warning' }
const resultColors = { '未接': '#909399', '接通': '#67C23A', '占线': '#E6A23C', '关机': '#F56C6C', '空号': '#F56C6C', '拒接': '#E6A23C' }

const todayStats = ref({ total: 0, connected: 0, connect_rate: 0, total_duration: 0, avg_duration: 0, result_dist: {} })
const monthStats = ref({ total: 0 })
const teamUsers = ref([])

const params = reactive({ keyword: '', call_result: -1, advisor_id: null, start_date: '', end_date: '', page: 1, page_size: 20 })

const fmt = t => t ? t.replace('T', ' ').substring(0, 16) : '—'

const onDateChange = (val) => {
  if (val && val.length === 2) {
    params.start_date = val[0]
    params.end_date = val[1]
  } else {
    params.start_date = ''
    params.end_date = ''
  }
}

const apiFetch = (url, opts = {}) => fetch(url, {
  ...opts,
  headers: { ...(opts.headers || {}), 'Authorization': `Bearer ${localStorage.getItem('token')}` }
})

const loadData = async (page = params.page) => {
  params.page = page
  loading.value = true
  try {
    const p = { ...params }
    if (p.call_result < 0) delete p.call_result
    if (!p.advisor_id) delete p.advisor_id
    if (!p.keyword) delete p.keyword
    if (!p.start_date) delete p.start_date
    if (!p.end_date) delete p.end_date
    const qs = new URLSearchParams(p).toString()
    const res = await apiFetch(`/api/call-records?${qs}`)
    const d = await res.json()
    records.value = d.items || []
    total.value = d.total || 0
  } finally { loading.value = false }
}

const loadStats = async () => {
  const [todayRes, monthRes] = await Promise.all([
    apiFetch('/api/call-records/stats?period=today'),
    apiFetch('/api/call-records/stats?period=month')
  ])
  todayStats.value = await todayRes.json()
  monthStats.value = await monthRes.json()
}

const resetParams = () => {
  Object.assign(params, { keyword: '', call_result: -1, advisor_id: null, start_date: '', end_date: '', page: 1 })
  dateRange.value = null
  filterResult.value = ''
  loadData(1)
}

const deleteRecord = async (row) => {
  await ElMessageBox.confirm('确定删除此通话记录？', '提示', { type: 'warning' })
  try {
    await apiFetch(`/api/call-records/${row.id}`, { method: 'DELETE' })
    ElMessage.success('已删除')
    loadData()
    loadStats()
  } catch(e) { ElMessage.error('删除失败') }
}

// ====== 添加通话 ======
const addVisible = ref(false)
const saveLoading = ref(false)
const addForm = reactive({ customer_id: null, call_type: 1, call_result: 1, duration: 0, call_at: '', note: '' })
const searchList = ref([])
const searchLoading = ref(false)

const searchCustomers = async (query) => {
  if (!query) return
  searchLoading.value = true
  try {
    const res = await apiFetch(`/api/customers?keyword=${encodeURIComponent(query)}&page_size=20&page=1`)
    const d = await res.json()
    searchList.value = d.items || []
  } finally { searchLoading.value = false }
}

const handleSave = async () => {
  if (!addForm.customer_id) return ElMessage.warning('请选择客户')
  saveLoading.value = true
  try {
    const res = await apiFetch('/api/call-records', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(addForm)
    })
    if (!res.ok) throw new Error((await res.json()).detail || '保存失败')
    ElMessage.success('通话已记录')
    addVisible.value = false
    Object.assign(addForm, { customer_id: null, call_type: 1, call_result: 1, duration: 0, call_at: '', note: '' })
    loadData(1)
    loadStats()
  } catch(e) { ElMessage.error(e.message || '保存失败') }
  finally { saveLoading.value = false }
}

onMounted(async () => {
  loadData()
  loadStats()
  if (isManager.value) {
    try { teamUsers.value = await getTeam() || [] } catch(e) {}
  }
})
</script>

<style scoped>
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 0 8px;
}
.page-header h3 { margin: 0; font-size: 18px; }
.stat-card { text-align: center; }
.stat-num { font-size: 28px; font-weight: bold; margin: 4px 0; }
.link-name { color: #E91E63; cursor: pointer; font-weight: 500; }
.link-name:hover { text-decoration: underline; }

.result-dist {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}
.result-item {
  flex: 1;
  min-width: 80px;
  padding: 10px 12px;
  border-radius: 8px;
  cursor: pointer;
  background: #f8f9fa;
  border: 2px solid transparent;
  transition: all 0.2s;
}
.result-item:hover, .result-item.active {
  background: #FDE8F1;
  border-color: #E91E63;
}
.result-label { font-size: 12px; color: #888; }
.result-count { font-size: 22px; font-weight: bold; color: #333; }
.result-bar { height: 4px; background: #eee; border-radius: 2px; margin-top: 6px; overflow: hidden; }
.result-bar-fill { height: 100%; border-radius: 2px; transition: width 0.3s; }
</style>
