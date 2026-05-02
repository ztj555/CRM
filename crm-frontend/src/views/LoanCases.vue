<template>
  <div>
    <div class="page-header">
      <h3>在审件管理</h3>
      <div style="display:flex; gap:8px">
        <el-button type="primary" size="small" @click="openAddCase">
          <el-icon><Plus /></el-icon> 新增进件
        </el-button>
        <el-button size="small" @click="loadData(1)"><Refresh /> 刷新</el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="12" style="margin-bottom:14px">
      <el-col :span="4" v-for="s in stageStats" :key="s.stage">
        <el-card shadow="hover" class="stat-card" :style="{borderTop: '3px solid ' + s.color}">
          <div style="font-size:11px; color:#888">{{ s.label }}</div>
          <div style="font-size:26px; font-weight:bold" :style="{color: s.color}">{{ s.count }}</div>
          <div v-if="s.amount > 0" style="font-size:11px; color:#aaa">{{ s.amount.toFixed(1) }}万</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 搜索栏 -->
    <el-card style="margin:0 0 12px">
      <el-form inline @submit.prevent="loadData(1)">
        <el-form-item label="关键词">
          <el-input v-model="params.keyword" placeholder="客户姓名/手机" clearable style="width:150px" />
        </el-form-item>
        <el-form-item label="阶段">
          <el-select v-model="params.stage" clearable style="width:120px" placeholder="全部">
            <el-option v-for="(n,v) in stageMap" :key="v" :label="n" :value="Number(v)" />
          </el-select>
        </el-form-item>
        <el-form-item label="银行">
          <el-input v-model="params.bank" placeholder="银行名称" clearable style="width:120px" />
        </el-form-item>
        <el-form-item label="时间">
          <el-date-picker v-model="dateRange" type="daterange" range-separator="至"
            start-placeholder="开始" end-placeholder="结束" value-format="YYYY-MM-DD"
            size="default" style="width:220px" @change="onDateChange" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData(1)"><Search/> 搜索</el-button>
        </el-form-item>
        <el-form-item><el-button @click="resetParams">重置</el-button></el-form-item>
      </el-form>
    </el-card>

    <el-card>
      <el-table :data="cases" v-loading="loading" size="small" :stripe="true" @row-click="openDetail">
        <el-table-column label="ID" prop="id" width="60" />
        <el-table-column label="客户姓名" width="90">
          <template #default="{row}">
            <span style="color:#E91E63; font-weight:500; cursor:pointer" @click.stop="openCustomerDetail && openCustomerDetail(row.customer_id, row.customer_name)">
              {{ row.customer_name || '—' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="手机" prop="customer_phone" width="120" />
        <el-table-column label="进件银行" prop="bank_name" width="110" />
        <el-table-column label="银行经理" prop="bank_manager" width="90" />
        <el-table-column label="进件额度(万)" prop="apply_amount" width="100">
          <template #default="{row}">{{ row.apply_amount ? Number(row.apply_amount).toFixed(1) : '—' }}</template>
        </el-table-column>
        <el-table-column label="费率" width="70">
          <template #default="{row}">{{ row.fee_rate ? (row.fee_rate*100).toFixed(1)+'%' : '—' }}</template>
        </el-table-column>
        <el-table-column label="阶段" width="90">
          <template #default="{row}">
            <el-tag size="small" :type="stageTagType[row.stage]">{{ row.stageText }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="批款额度" width="90">
          <template #default="{row}">{{ row.approve_amount ? Number(row.approve_amount).toFixed(1)+'万' : '—' }}</template>
        </el-table-column>
        <el-table-column label="收款金额" width="90">
          <template #default="{row}">{{ row.collection_amount ? Number(row.collection_amount).toFixed(1)+'万' : '—' }}</template>
        </el-table-column>
        <el-table-column label="提交时间" width="140">
          <template #default="{row}">{{ fmt(row.submit_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{row}">
            <el-button v-if="row.stage===1" size="small" type="success" @click.stop="advance(row,2)">批款</el-button>
            <el-button v-if="row.stage===2" size="small" type="warning" @click.stop="advance(row,3)">收款</el-button>
            <el-button v-if="row.stage===1" size="small" type="danger" @click.stop="confirmReject(row)">拒批</el-button>
            <el-button v-if="row.stage <= 3" size="small" type="primary" plain @click.stop="editCase(row)">编辑</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div style="margin-top:12px;display:flex;justify-content:space-between;align-items:center">
        <div>
          <span style="color:#888;font-size:13px">共 <b style="color:#E91E63">{{ total }}</b> 条</span>
          <span style="color:#888;font-size:13px;margin-left:16px">
            总批款额：<b style="color:#67C23A">{{ totalApproveAmount.toFixed(1) }}万</b>
          </span>
        </div>
        <el-pagination background layout="prev,pager,next" :total="total" :page-size="params.page_size"
          v-model:current-page="params.page" @current-change="loadData" />
      </div>
    </el-card>

    <!-- 新增/编辑进件弹窗 -->
    <el-dialog v-model="addVisible" :title="editMode ? '编辑进件' : '新增进件'" width="520px" :close-on-click-modal="false">
      <el-form :model="addForm" label-width="90px">
        <el-form-item label="客户" required>
          <el-select v-model="addForm.customer_id" filterable remote :remote-method="searchCustomers"
            :loading="customerSearchLoading" placeholder="搜索客户姓名/手机" style="width:100%"
            @change="handleCustomerSelect">
            <el-option v-for="c in customerSearchList" :key="c.id"
              :label="`${c.name || '未命名'} (${c.phone || ''})`" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="进件银行" required>
          <el-autocomplete v-model="addForm.bank_name" :fetch-suggestions="bankSuggest"
            placeholder="输入银行名称" style="width:100%" />
        </el-form-item>
        <el-form-item label="银行经理">
          <el-input v-model="addForm.bank_manager" placeholder="可选" />
        </el-form-item>
        <el-form-item label="进件额度(万)" required>
          <el-input-number v-model="addForm.apply_amount" :min="0" :step="1" :precision="2" style="width:100%" />
        </el-form-item>
        <el-form-item label="费率(%)">
          <el-input-number v-model="addForm.fee_rate_pct" :min="0" :max="100" :step="0.1" :precision="2"
            style="width:100%" placeholder="例：1.5 表示1.5%">
            <template #suffix>%</template>
          </el-input-number>
        </el-form-item>
        <el-form-item label="提交时间">
          <el-date-picker v-model="addForm.submit_at" type="datetime" placeholder="默认为当前时间"
            value-format="YYYY-MM-DDTHH:mm:ss" style="width:100%" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="addForm.note" type="textarea" :rows="2" placeholder="进件备注（可选）" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addVisible=false">取消</el-button>
        <el-button type="primary" :loading="addLoading" @click="handleSave">{{ editMode ? '保存修改' : '确认提交' }}</el-button>
      </template>
    </el-dialog>

    <!-- 批款/收款弹窗 -->
    <el-dialog v-model="stageVisible" :title="stageDialogTitle" width="400px">
      <el-form label-width="100px">
        <el-form-item :label="stageDialogTitle + '额度(万)'">
          <el-input-number v-model="stageAmount" :min="0" :precision="2" style="width:100%" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="stageNote" type="textarea" :rows="2" placeholder="可选" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="stageVisible=false">取消</el-button>
        <el-button type="primary" @click="confirmStage">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, inject } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getLoanCases, updateCaseStage } from '../api'
import { Plus, Refresh, Search } from '@element-plus/icons-vue'

const openCustomerDetail = inject('openCustomerDetail', null)

const cases = ref([])
const total = ref(0)
const loading = ref(false)
const dateRange = ref(null)

const stageMap = { 1: '审核中', 2: '已批款', 3: '已收款', 4: '已拒批', 5: '已违约' }
const stageColors = { 1: '#E6A23C', 2: '#67C23A', 3: '#409EFF', 4: '#F56C6C', 5: '#909399' }
const stageTagType = { 1:'warning', 2:'success', 3:'primary', 4:'danger', 5:'info' }

const params = reactive({
  keyword: '', stage: -1, bank: '',
  start_date: '', end_date: '',
  page: 1, page_size: 20
})

const stageStats = computed(() => {
  return [1, 2, 3, 4, 5].map(s => ({
    stage: s,
    label: stageMap[s],
    color: stageColors[s],
    count: cases.value.filter(c => c.stage === s).length,
    amount: cases.value.filter(c => c.stage === s).reduce((a, c) => a + Number(c.approve_amount || 0), 0)
  }))
})

const totalApproveAmount = computed(() =>
  cases.value.filter(c => c.stage >= 2).reduce((a, c) => a + Number(c.approve_amount || 0), 0)
)

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

const loadData = async (page = params.page) => {
  params.page = page
  loading.value = true
  try {
    const p = { ...params, page_size: 200 }  // 加载全量用于统计
    if (p.stage < 0) delete p.stage
    if (!p.keyword) delete p.keyword
    if (!p.bank) delete p.bank
    if (!p.start_date) delete p.start_date
    if (!p.end_date) delete p.end_date
    const res = await getLoanCases(p)
    cases.value = res.items
    total.value = res.total
  } finally { loading.value = false }
}

const resetParams = () => {
  Object.assign(params, { keyword: '', stage: -1, bank: '', start_date: '', end_date: '', page: 1 })
  dateRange.value = null
  loadData(1)
}

const openDetail = (row) => {}

// ====== 阶段推进 ======
const stageVisible = ref(false)
const stageDialogTitle = ref('')
const stageAmount = ref(0)
const stageNote = ref('')
const stageTarget = ref(null)

const advance = async (row, stage) => {
  stageTarget.value = { id: row.id, stage }
  stageDialogTitle.value = stage === 2 ? '批款' : '收款'
  stageAmount.value = Number(row.apply_amount || 0)
  stageNote.value = ''
  stageVisible.value = true
}

const confirmReject = async (row) => {
  await ElMessageBox.confirm(`确定将「${row.customer_name}」的进件标记为拒批？`, '确认拒批', { type: 'warning' })
  try {
    await updateCaseStage(row.id, 4, 0)
    ElMessage.success('已标记为拒批')
    loadData()
  } catch(e) { ElMessage.error(e.detail || '操作失败') }
}

const confirmStage = async () => {
  try {
    await updateCaseStage(stageTarget.value.id, stageTarget.value.stage, stageAmount.value)
    ElMessage.success('更新成功')
    stageVisible.value = false
    loadData()
  } catch(e) { ElMessage.error(e.detail || '更新失败') }
}

// ====== 新增/编辑进件 ======
const addVisible = ref(false)
const addLoading = ref(false)
const editMode = ref(false)
const editCaseId = ref(null)
const addForm = reactive({
  customer_id: null, bank_name: '', bank_manager: '',
  apply_amount: 0, fee_rate_pct: 1.5, submit_at: '', note: ''
})

const customerSearchList = ref([])
const customerSearchLoading = ref(false)

const searchCustomers = async (query) => {
  if (!query || query.length < 1) return
  customerSearchLoading.value = true
  try {
    const res = await fetch(`/api/customers?keyword=${encodeURIComponent(query)}&page_size=20&page=1`, {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    })
    const d = await res.json()
    customerSearchList.value = d.items || []
  } finally { customerSearchLoading.value = false }
}

const handleCustomerSelect = (id) => {
  const c = customerSearchList.value.find(x => x.id === id)
  if (c && !addForm.apply_amount) {
    addForm.apply_amount = Number(c.apply_amount || 0)
  }
}

const commonBanks = [
  '农业银行', '工商银行', '建设银行', '中国银行', '招商银行',
  '民生银行', '浦发银行', '中信银行', '光大银行', '平安银行',
  '兴业银行', '华夏银行', '北京银行', '上海银行', '宁波银行'
]

const bankSuggest = (query, cb) => {
  const res = commonBanks.filter(b => b.includes(query))
  cb(res.map(b => ({ value: b })))
}

const openAddCase = () => {
  editMode.value = false
  editCaseId.value = null
  Object.assign(addForm, { customer_id: null, bank_name: '', bank_manager: '', apply_amount: 0, fee_rate_pct: 1.5, submit_at: '', note: '' })
  customerSearchList.value = []
  addVisible.value = true
}

const editCase = (row) => {
  editMode.value = true
  editCaseId.value = row.id
  Object.assign(addForm, {
    customer_id: row.customer_id,
    bank_name: row.bank_name || '',
    bank_manager: row.bank_manager || '',
    apply_amount: Number(row.apply_amount || 0),
    fee_rate_pct: row.fee_rate ? Number(row.fee_rate) * 100 : 1.5,
    submit_at: row.submit_at || '',
    note: ''
  })
  customerSearchList.value = [{ id: row.customer_id, name: row.customer_name, phone: row.customer_phone }]
  addVisible.value = true
}

const handleSave = async () => {
  if (!addForm.customer_id) return ElMessage.warning('请选择客户')
  if (!addForm.bank_name) return ElMessage.warning('请填写进件银行')
  if (!addForm.apply_amount || addForm.apply_amount <= 0) return ElMessage.warning('请填写进件额度')
  addLoading.value = true
  try {
    const payload = {
      customer_id: addForm.customer_id,
      bank_name: addForm.bank_name,
      bank_manager: addForm.bank_manager || '',
      apply_amount: addForm.apply_amount,
      fee_rate: addForm.fee_rate_pct / 100,
      submit_at: addForm.submit_at || new Date().toISOString()
    }
    if (editMode.value) {
      await fetch(`/api/loan-cases/${editCaseId.value}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${localStorage.getItem('token')}` },
        body: JSON.stringify(payload)
      })
      ElMessage.success('编辑成功')
    } else {
      const res = await fetch('/api/loan-cases', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${localStorage.getItem('token')}` },
        body: JSON.stringify(payload)
      })
      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail || '提交失败')
      }
      ElMessage.success('进件已提交')
    }
    addVisible.value = false
    loadData(1)
  } catch(e) { ElMessage.error(e.message || '操作失败') }
  finally { addLoading.value = false }
}

onMounted(() => loadData())
</script>

<style scoped>
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 0 8px;
}
.page-header h3 { margin: 0; font-size: 18px; }
.stat-card { text-align: center; padding: 8px 0; }
:deep(.el-card__body) { padding: 12px; }
</style>
