<template>
  <div>
    <div class="page-header">
      <h3>日志报表</h3>
      <div style="display:flex; gap:8px; flex-wrap:wrap">
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          value-format="YYYY-MM-DD"
          size="default"
          style="width:240px"
          @change="activeTab === 'remark' && loadData(1)"
        />
        <el-select v-if="activeTab === 'remark'" v-model="advisorId" clearable placeholder="全部顾问" style="width:120px" @change="loadData(1)">
          <el-option v-for="u in teamUsers" :key="u.id" :label="u.real_name" :value="u.id" />
        </el-select>
        <el-select v-if="activeTab === 'remark'" v-model="remarkType" clearable placeholder="备注类型" style="width:110px" @change="loadData(1)">
          <el-option label="跟进记录" :value="0" />
          <el-option label="主管点评" :value="1" />
          <el-option label="备忘" :value="2" />
        </el-select>
        <el-button v-if="activeTab === 'remark'" @click="loadData(1)"><Search /> 刷新</el-button>
        <el-button v-if="activeTab === 'remark'" type="success" @click="exportCsv"><Download /> 导出CSV</el-button>
        <el-button v-if="activeTab === 'import'" @click="loadImportBatches(1)"><Search /> 刷新</el-button>
      </div>
    </div>

    <!-- Tab切换 -->
    <div class="tab-bar">
      <button class="tab-btn" :class="{active: activeTab === 'remark'}" @click="switchTab('remark')">
        📋 跟进日志
      </button>
      <button class="tab-btn" :class="{active: activeTab === 'import'}" @click="switchTab('import')">
        📥 导入日志
      </button>
    </div>

    <!-- ====== 跟进日志 Tab ====== -->
    <div v-show="activeTab === 'remark'">

    <!-- 统计卡片 -->
    <el-row :gutter="14" style="margin:14px 0">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card" style="border-top-color:#E91E63">
          <div class="stat-num" style="color:#E91E63">{{ stats.total }}</div>
          <div class="stat-label">本次查询总数</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card" style="border-top-color:#67C23A">
          <div class="stat-num" style="color:#67C23A">{{ stats.todayRemarks }}</div>
          <div class="stat-label">今日跟进</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card" style="border-top-color:#409EFF">
          <div class="stat-num" style="color:#409EFF">{{ stats.totalCustomers }}</div>
          <div class="stat-label">我的客户总数</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card" style="border-top-color:#E6A23C">
          <div class="stat-num" style="color:#E6A23C">{{ stats.activeAdvisors }}</div>
          <div class="stat-label">今日活跃顾问</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 顾问日报（主管可见） -->
    <el-card v-if="teamUsers.length > 0" style="margin-bottom:14px">
      <template #header>
        <div style="display:flex; justify-content:space-between; align-items:center">
          <span style="font-weight:600">📊 团队今日跟进统计</span>
          <el-button size="small" link @click="loadDailyStats">刷新</el-button>
        </div>
      </template>
      <div class="daily-grid">
        <div v-for="a in dailyStats" :key="a.advisor_id" class="daily-card" :class="{active: a.remark_count > 0}">
          <div class="daily-avatar">{{ a.advisor_name?.charAt(0) }}</div>
          <div class="daily-name">{{ a.advisor_name }}</div>
          <div class="daily-count" :style="{color: a.remark_count > 0 ? '#E91E63' : '#ccc'}">{{ a.remark_count }}</div>
          <div class="daily-label">条跟进</div>
        </div>
      </div>
    </el-card>

    <!-- 日志列表 -->
    <el-card>
      <template #header>
        <div style="display:flex; justify-content:space-between; align-items:center">
          <span style="font-weight:600">跟进日志明细（共 {{ total }} 条）</span>
          <el-checkbox v-model="showManagerComment" style="font-size:13px" @change="loadData(1)">只看主管点评</el-checkbox>
        </div>
      </template>

      <el-table :data="logs" v-loading="loading" size="small" :stripe="true">
        <el-table-column label="时间" width="150">
          <template #default="{row}">{{ fmt(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="顾问" prop="advisor_name" width="90" />
        <el-table-column label="客户" width="100">
          <template #default="{row}">
            <span style="color:#E91E63; cursor:pointer" @click="openCustomer(row)">{{ row.customer_name || '未知' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="手机" prop="customer_phone" width="130" />
        <el-table-column label="类型" width="90">
          <template #default="{row}">
            <el-tag size="small" :type="remarkTagType[row.remark_type]">
              {{ remarkTypeMap[row.remark_type] }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="90">
          <template #default="{row}">
            <el-tag size="small" :type="statusTagType[row.status_at_remark]">
              {{ statusMap[row.status_at_remark] || '—' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="备注内容">
          <template #default="{row}">
            <span style="font-size:13px">{{ row.content }}</span>
          </template>
        </el-table-column>
        <el-table-column v-if="isManager" label="主管点评" width="100">
          <template #default="{row}">
            <el-button size="small" type="warning" link @click="addManagerComment(row)">点评</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div style="margin-top:12px; display:flex; justify-content:space-between; align-items:center">
        <span style="color:#888; font-size:13px">共 {{ total }} 条</span>
        <el-pagination
          background
          layout="prev,pager,next"
          :total="total"
          :page-size="20"
          v-model:current-page="page"
          @current-change="loadData"
        />
      </div>
    </el-card>

    <!-- 主管点评弹窗 -->
    <el-dialog v-model="commentVisible" title="主管点评" width="480px">
      <div style="margin-bottom:12px;padding:10px;background:#f5f5f5;border-radius:6px;font-size:13px;color:#666">
        <b>原备注：</b>{{ commentRow?.content }}
      </div>
      <el-input
        v-model="commentContent"
        type="textarea"
        :rows="4"
        placeholder="写下点评意见..."
      />
      <template #footer>
        <el-button @click="commentVisible = false">取消</el-button>
        <el-button type="primary" :loading="commentLoading" @click="submitComment">提交点评</el-button>
      </template>
    </el-dialog>

    <!-- 客户详情抽屉 -->
    <CustomerDetail :visible="detailVisible" :customer-id="curCustomerId" @close="detailVisible = false" @updated="loadData(page)" />

    </div><!-- end 跟进日志 Tab -->

    <!-- ====== 导入日志 Tab ====== -->
    <div v-show="activeTab === 'import'">

    <el-card>
      <template #header>
        <span style="font-weight:600">📥 导入日志（共 {{ importTotal }} 条）</span>
      </template>

      <el-table :data="importBatches" v-loading="importLoading" size="small" :stripe="true">
        <el-table-column label="导入时间" width="160">
          <template #default="{row}">{{ fmt(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作人" prop="operator_name" width="100" />
        <el-table-column label="文件名" prop="filename" min-width="160" />
        <el-table-column label="成功" width="70">
          <template #default="{row}">
            <span style="color:#67C23A; font-weight:600">{{ row.success_count }}</span>
          </template>
        </el-table-column>
        <el-table-column label="重复跳过" width="90">
          <template #default="{row}">
            <span style="color:#909399">{{ row.duplicate_count }}</span>
          </template>
        </el-table-column>
        <el-table-column label="无效跳过" width="70">
          <template #default="{row}"><span style="color:#F56C6C">{{ row.skip_count || 0 }}</span></template>
        </el-table-column>
        <el-table-column label="状态" width="90">
          <template #default="{row}">
            <el-tag size="small" :type="batchStatusTag[row.status]">
              {{ batchStatusMap[row.status] }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{row}">
            <template v-if="row.status === 1">
              <el-button size="small" type="info" link @click="showSkipDetailLogs(row)">详情</el-button>
              <el-button size="small" type="primary" link @click="toPool(row)">转入公共池</el-button>
              <el-button size="small" type="danger" link @click="cancelBatch(row)">撤销</el-button>
            </template>
            <span v-else style="color:#ccc; font-size:12px">—</span>
          </template>
        </el-table-column>
      </el-table>

      <div style="margin-top:12px; display:flex; justify-content:space-between; align-items:center">
        <span style="color:#888; font-size:13px">共 {{ importTotal }} 条</span>
        <el-pagination
          background
          layout="prev,pager,next"
          :total="importTotal"
          :page-size="20"
          v-model:current-page="importPage"
          @current-change="loadImportBatches"
        />
      </div>
    </el-card>

    <!-- 跳过原因详情弹窗（日志报表页） -->
    <el-dialog v-model="logsSkipVisible" title="无效数据详情" width="600px">
      <div v-if="logsSkipDetail">
        <p style="margin:0 0 12px; color:#666; font-size:13px">
          {{ logsSkipDetail.filename }} — 操作人：{{ logsSkipDetail.operator_name }}
          &nbsp;|&nbsp; 跳过 {{ logsSkipDetail.skip_count || 0 }} 条
        </p>
        <el-table :data="logsSkipDetail.skip_detail" size="small" max-height="400" :stripe="true">
          <el-table-column label="行号" prop="row" width="60" />
          <el-table-column label="手机号" prop="phone" width="130" />
          <el-table-column label="跳过原因" prop="reason" />
        </el-table>
        <div v-if="!logsSkipDetail.skip_detail?.length" style="text-align:center; color:#999; padding:30px">
          暂无无效数据记录
        </div>
      </div>
      <template #footer>
        <el-button @click="logsSkipVisible=false">关闭</el-button>
      </template>
    </el-dialog>

    </div><!-- end 导入日志 Tab -->

  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Download } from '@element-plus/icons-vue'
import api, { getImportLogs, cancelImportBatch, importBatchToPool } from '../api'
import CustomerDetail from './customers/CustomerDetail.vue'

const activeTab = ref('remark')  // 'remark' | 'import'
const logs = ref([])
const total = ref(0)
const page = ref(1)
const loading = ref(false)
const dateRange = ref([])
const advisorId = ref('')
const remarkType = ref(null)
const teamUsers = ref([])
const showManagerComment = ref(false)
const dailyStats = ref([])

const stats = ref({ total: 0, todayRemarks: 0, totalCustomers: 0, activeAdvisors: 0 })

const isManager = computed(() => {
  try { return JSON.parse(localStorage.getItem('user') || '{}').role >= 2 } catch { return false }
})

const commentVisible = ref(false)
const commentRow = ref(null)
const commentContent = ref('')
const commentLoading = ref(false)

const detailVisible = ref(false)
const curCustomerId = ref(null)

// 导入日志
const importBatches = ref([])
const importTotal = ref(0)
const importPage = ref(1)
const importLoading = ref(false)
const batchStatusMap = { 1: '已完成', 2: '已撤销', 3: '处理失败' }
const batchStatusTag = { 1: 'success', 2: 'info', 3: 'danger' }

const remarkTypeMap = { 0: '跟进', 1: '主管点评', 2: '备忘' }
const remarkTagType = { 0: '', 1: 'warning', 2: 'success' }
const statusMap = {
  0: '待跟进', 1: '有意向', 2: '未接通', 3: '预约上门', 4: '已上门',
  5: '已受理', 6: '待签约', 7: '已签约', 8: '银行已放款', 9: '银行已拒绝',
  10: '审核中', 11: '无意向', 12: '资质不符', 13: '捣乱申请', 14: '重复申请',
  15: '外地申请', 16: '停机', 17: '空号', 18: '外地号码'
}
const statusTagType = {
  0: '', 1: 'success', 2: 'info', 3: 'warning', 4: 'warning', 5: '',
  6: '', 7: 'success', 8: 'success', 9: 'danger', 10: '', 11: 'info',
  12: 'danger', 13: 'danger', 14: 'danger', 15: '', 16: 'danger', 17: 'danger', 18: ''
}

const fmt = (t) => t ? t.replace('T', ' ').substring(0, 16) : '—'

// Tab切换
const switchTab = (tab) => {
  activeTab.value = tab
  if (tab === 'import' && importBatches.value.length === 0) {
    loadImportBatches(1)
  }
}

const loadData = async (p = page.value) => {
  page.value = p
  loading.value = true
  try {
    const params = { page: p, page_size: 20 }
    if (advisorId.value) params.advisor_id = advisorId.value
    if (dateRange.value?.length === 2) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }
    if (remarkType.value !== null) params.remark_type = remarkType.value
    if (showManagerComment.value) params.remark_type = 1

    const res = await api.get('/stats/remarks', { params })
    logs.value = res.items
    total.value = res.total
    stats.value.total = res.total

    // 加载dashboard统计
    const d = await api.get('/stats/dashboard')
    stats.value.todayRemarks = d.todayRemark
    stats.value.totalCustomers = d.total
    stats.value.activeAdvisors = teamUsers.value.length
  } catch (e) {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

// 加载导入批次
const loadImportBatches = async (p = importPage.value) => {
  importPage.value = p
  importLoading.value = true
  try {
    const res = await getImportLogs({ page: p, page_size: 20 })
    importBatches.value = res.items || res
    importTotal.value = res.total || (Array.isArray(res) ? res.length : 0)
  } catch (e) {
    ElMessage.error('加载导入日志失败')
  } finally {
    importLoading.value = false
  }
}

// 撤销导入
const cancelBatch = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定撤销 ${row.operator_name} 的导入批次（共 ${row.success_count} 人）？撤销后该批次分配记录将失效（客户数据保留）。`,
      '撤销导入', { type: 'warning', confirmButtonText: '确定撤销', cancelButtonText: '取消' }
    )
    const res = await cancelImportBatch(row.id)
    ElMessage.success(res.msg || '撤销成功')
    loadImportBatches(importPage.value)
  } catch (e) {
    if (e !== 'cancel') ElMessage.error(e.message || '撤销失败')
  }
}

// 转入公共池
const toPool = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定将 ${row.operator_name} 导入的 ${row.success_count} 名客户转入公共池？`,
      '转入公共池', { type: 'info', confirmButtonText: '确定转入', cancelButtonText: '取消' }
    )
    const res = await importBatchToPool(row.id)
    ElMessage.success(res.msg || '已转入公共池')
    loadImportBatches(importPage.value)
  } catch (e) {
    if (e !== 'cancel') ElMessage.error(e.message || '操作失败')
  }
}

// 加载团队今日统计
const loadDailyStats = async () => {
  try {
    const res = await api.get('/stats/team-daily')
    dailyStats.value = res.advisors || []
  } catch (e) {}
}

// 导出CSV
const exportCsv = () => {
  const params = new URLSearchParams()
  if (advisorId.value) params.append('advisor_id', advisorId.value)
  if (dateRange.value?.length === 2) {
    params.append('start_date', dateRange.value[0])
    params.append('end_date', dateRange.value[1])
  }
  const token = localStorage.getItem('token')
  const url = `/api/stats/remarks/export?${params}`
  fetch(url, { headers: { Authorization: `Bearer ${token}` } })
    .then(r => r.blob())
    .then(blob => {
      const a = document.createElement('a')
      a.href = URL.createObjectURL(blob)
      a.download = `跟进日志_${new Date().toLocaleDateString('zh-CN').replace(/\//g, '-')}.csv`
      a.click()
    })
    .catch(() => ElMessage.error('导出失败'))
}

// 主管点评
const addManagerComment = (row) => {
  commentRow.value = row
  commentContent.value = ''
  commentVisible.value = true
}

const submitComment = async () => {
  if (!commentContent.value.trim()) return ElMessage.warning('请输入点评内容')
  commentLoading.value = true
  try {
    await api.post(`/customers/${commentRow.value.customer_id}/remarks`, {
      content: commentContent.value,
      remark_type: 1
    })
    ElMessage.success('点评已提交')
    commentVisible.value = false
    await loadData(page.value)
  } catch (e) { ElMessage.error('提交失败') }
  finally { commentLoading.value = false }
}

// 点击客户名打开详情
const openCustomer = (row) => {
  if (row.customer_id) {
    curCustomerId.value = row.customer_id
    detailVisible.value = true
  }
}

// 导入日志：查看跳过详情
const logsSkipVisible = ref(false)
const logsSkipDetail = ref(null)
const showSkipDetailLogs = (row) => {
  logsSkipDetail.value = row
  logsSkipVisible.value = true
}

onMounted(async () => {
  try {
    teamUsers.value = await api.get('/users/team')
    await loadDailyStats()
  } catch (e) {}
  await loadData(1)
})
</script>

<style scoped>
.stat-card { text-align: center; padding: 8px 0; border-top: 3px solid #ccc; }
.stat-num { font-size: 32px; font-weight: bold; }
.stat-label { color: #888; margin-top: 6px; font-size: 13px; }

/* Tab栏 */
.tab-bar {
  display: flex;
  border-bottom: 2px solid #E91E63;
  margin-bottom: 14px;
}
.tab-btn {
  padding: 10px 20px;
  border: none;
  background: none;
  cursor: pointer;
  font-size: 14px;
  color: #666;
  border-bottom: 3px solid transparent;
  margin-bottom: -2px;
  transition: all 0.2s;
  border-radius: 6px 6px 0 0;
}
.tab-btn:hover { color: #E91E63; background: #fff0f5; }
.tab-btn.active {
  color: #E91E63;
  font-weight: 600;
  border-bottom: 3px solid #E91E63;
  background: #fff0f5;
}

/* 团队日报 */
.daily-grid {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}
.daily-card {
  width: 90px;
  text-align: center;
  padding: 10px 8px;
  border: 1px solid #eee;
  border-radius: 8px;
  background: #fafafa;
  transition: all 0.2s;
}
.daily-card.active {
  border-color: #E91E63;
  background: #fff0f6;
  box-shadow: 0 2px 8px rgba(233,30,99,0.1);
}
.daily-avatar {
  width: 32px; height: 32px; border-radius: 50%;
  background: linear-gradient(135deg, #E91E63, #F48FB1);
  display: flex; align-items: center; justify-content: center;
  color: white; font-size: 13px; font-weight: bold;
  margin: 0 auto 6px;
}
.daily-name { font-size: 12px; color: #333; margin-bottom: 4px; }
.daily-count { font-size: 22px; font-weight: bold; }
.daily-label { font-size: 11px; color: #888; }
</style>
