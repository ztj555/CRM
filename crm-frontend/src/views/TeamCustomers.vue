<template>
  <div>
    <!-- 页面头部 -->
    <div class="page-header">
      <h3>团队客户</h3>
      <div class="header-toolbar">
        <el-button size="small" @click="loadData(1)"><Refresh /> 刷新</el-button>
        <el-button size="small" type="success" @click="handleExport" :loading="exporting">
          <el-icon><Download /></el-icon> 导出Excel
        </el-button>
      </div>
    </div>

    <!-- 搜索卡片（老系统风格） -->
    <el-card class="search-card">
      <el-form inline @submit.prevent="loadData(1)">
        <el-form-item label="关键词">
          <el-input v-model="params.keyword" placeholder="姓名/手机" clearable style="width:140px" />
        </el-form-item>
        <el-form-item label="分配类型">
          <el-select v-model="params.allocation_type" clearable placeholder="全部" style="width:160px">
            <el-option label="全部" :value="0" />
            <el-option label="原始分配" :value="1" />
            <el-option label="全部再分配数据" :value="2" />
            <el-option label="再分配_离职客服" :value="3" />
            <el-option label="再分配_备注2月未更新" :value="4" />
            <el-option label="再分配_错误城市" :value="5" />
          </el-select>
        </el-form-item>
        <el-form-item label="数据类型">
          <el-select v-model="params.data_type" clearable placeholder="全部" style="width:110px">
            <el-option label="全部有效" :value="0" />
            <el-option label="原始数据" :value="1" />
            <el-option label="再分配" :value="2" />
          </el-select>
        </el-form-item>
        <el-form-item label="数据池">
          <el-select v-model="params.pool_type" clearable placeholder="全部" style="width:130px">
            <el-option label="全部" :value="0" />
            <el-option label="我的客户池" :value="1" />
            <el-option label="再分配客户池" :value="2" />
            <el-option label="必跟进池" :value="4" />
            <el-option label="公共池" :value="3" />
          </el-select>
        </el-form-item>
        <el-form-item label="部门">
          <el-select v-model="params.dept_id" clearable placeholder="全部部门" style="width:140px">
            <el-option v-for="d in departments" :key="d.id" :label="d.name" :value="d.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="顾问">
          <el-select v-model="params.advisor_id" clearable placeholder="全部顾问" style="width:120px">
            <el-option v-for="u in activeUsers" :key="u.id" :label="u.real_name" :value="u.id" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData(1)"><Search /> 搜索</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 数据统计摘要条 -->
    <div class="summary-bar">
      <span class="summary-item">
        <span class="summary-label">总计客户</span>
        <span class="summary-value">{{ total }}</span>
      </span>
      <span class="summary-divider">|</span>
      <span class="summary-item">
        <span class="summary-label">原始分配</span>
        <span class="summary-value primary">{{ countByType1 }}</span>
      </span>
      <span class="summary-divider">|</span>
      <span class="summary-item">
        <span class="summary-label">再分配</span>
        <span class="summary-value warning">{{ countByType2 }}</span>
      </span>
    </div>

    <!-- 数据表格 -->
    <el-card class="table-card">
      <el-table
        :data="tableData"
        v-loading="loading"
        size="small"
        :stripe="true"
        :max-height="620"
        row-class-name="clickable-row"
        @row-click="openDetail"
      >
        <el-table-column type="index" label="序号" width="55" align="center" />
        <el-table-column label="顾问姓名" prop="advisor_name" width="90">
          <template #default="{row}">
            <div style="display:flex; align-items:center; gap:6px">
              <div class="tiny-avatar">{{ row.advisor_name?.charAt(0) }}</div>
              {{ row.advisor_name }}
            </div>
          </template>
        </el-table-column>
        <el-table-column label="部门" prop="dept_name" width="130" show-overflow-tooltip />
        <el-table-column label="姓名" prop="name" width="90">
          <template #default="{row}">
            <span :style="{color: row.is_important ? '#F56C6C' : '', fontWeight: row.is_important ? 600 : 400}">
              {{ row.name || '—' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="手机" prop="phone" width="120" />
        <el-table-column label="城市" prop="city" width="75" />
        <el-table-column label="意向产品" prop="loanTypeText" width="90" />
        <el-table-column label="意向额度" width="85">
          <template #default="{row}">{{ row.apply_amount ? row.apply_amount + '万' : '—' }}</template>
        </el-table-column>
        <el-table-column label="星级" width="65" align="center">
          <template #default="{row}">
            <span style="color:#E6A23C; font-size:13px">
              <span v-for="n in (row.star_level || 0)" :key="n">★</span>
            </span>
          </template>
        </el-table-column>
        <el-table-column label="客户状态" width="85">
          <template #default="{row}">
            <el-tag size="small" :type="statusTagType(row.status)">{{ row.statusText }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="最后备注" width="140">
          <template #default="{row}">{{ fmt(row.last_remark_at) }}</template>
        </el-table-column>
        <el-table-column label="数据池" width="90" align="center">
          <template #default="{row}">
            <el-tag size="small" :type="poolTagType(row.pool_type)">{{ poolTagText(row.pool_type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="重新分配" width="170" fixed="right">
          <template #default="{row}">
            <el-select
              size="small"
              v-model="assignTo[row.id]"
              placeholder="选择顾问"
              style="width:140px"
              @change="handleAssign(row)"
              :disabled="!activeUsers.length"
            >
              <el-option
                v-for="u in activeUsers"
                :key="u.id"
                :label="u.real_name + ' (' + (u.customer_count||0) + ')'"
                :value="u.id"
              />
            </el-select>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-bar">
        <span class="total-hint">共 <b style="color:#E91E63">{{ total }}</b> 条</span>
        <el-pagination
          background
          layout="prev, pager, next, sizes"
          :total="total"
          :page-size="params.page_size"
          v-model:current-page="params.page"
          :page-sizes="[20, 50, 100, 200]"
          @current-change="loadData"
          @size-change="p => { params.page_size = p; loadData(1) }"
        />
      </div>
    </el-card>

    <!-- 客户详情抽屉 -->
    <CustomerDetail
      :visible="detailVisible"
      :customer-id="curId"
      @close="detailVisible = false"
      @updated="loadData()"
    />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Refresh, Download } from '@element-plus/icons-vue'
import api from '../api'
import CustomerDetail from './customers/CustomerDetail.vue'

// 筛选参数
const params = reactive({
  keyword: '',
  allocation_type: 0,
  data_type: 0,
  pool_type: 0,
  dept_id: '',
  advisor_id: '',
  page: 1,
  page_size: 20
})

const tableData = ref([])
const total = ref(0)
const loading = ref(false)
const departments = ref([])
const allUsers = ref([])
const assignTo = reactive({})
const detailVisible = ref(false)
const curId = ref(null)
const exporting = ref(false)

// 在职顾问
const activeUsers = computed(() => allUsers.value.filter(u => u.status === 1))

// 分配池统计（前端估算，实际以total为准）
const countByType1 = computed(() => {
  if (params.allocation_type === 1) return total.value
  return '—'
})
const countByType2 = computed(() => {
  if (params.allocation_type === 2) return total.value
  return '—'
})

const statusTagType = (s) => {
  const map = { 0: 'info', 1: 'warning', 2: 'success', 3: 'danger', 4: 'danger', 10: 'primary' }
  return map[s] || 'info'
}
const poolTagType = (pt) => {
  const map = { 1: 'primary', 2: 'warning', 3: 'success', 4: 'danger' }
  return map[pt] || 'info'
}
const poolTagText = (pt) => {
  const map = { 1: '我的客户', 2: '再分配', 3: '公共池', 4: '必跟进' }
  return map[pt] || '其他'
}

const fmt = (t) => t ? t.replace('T', ' ').substring(0, 16) : '—'

const openDetail = (row) => {
  curId.value = row.id
  detailVisible.value = true
}

// 加载数据
const loadData = async (page = 1) => {
  params.page = page
  loading.value = true
  try {
    const p = { ...params }
    if (!p.advisor_id) delete p.advisor_id
    if (!p.keyword) delete p.keyword
    if (!p.dept_id) delete p.dept_id
    if (p.allocation_type === 0) delete p.allocation_type
    if (p.data_type === 0) delete p.data_type
    if (p.pool_type === 0) delete p.pool_type
    const res = await api.get('/team/customers', { params: p })
    tableData.value = res.items
    total.value = res.total
  } catch (e) {
    ElMessage.error('加载失败: ' + (e.detail || e.message || ''))
  } finally {
    loading.value = false
  }
}

// 重新分配
const handleAssign = async (row) => {
  const toId = assignTo[row.id]
  if (!toId) return
  try {
    const fd = new FormData()
    fd.append('customer_id', row.id)
    fd.append('to_user_id', toId)
    await api.post('/team/assign', fd)
    ElMessage.success(`已分配给 ${activeUsers.value.find(u => u.id == toId)?.real_name || '顾问'}`)
    assignTo[row.id] = null
    loadData()
  } catch (e) {
    ElMessage.error(e.detail || '分配失败')
    assignTo[row.id] = null
  }
}

// 导出Excel（CSV格式）
const handleExport = async () => {
  exporting.value = true
  try {
    const p = { ...params, page: 1, page_size: 99999 }
    if (!p.advisor_id) delete p.advisor_id
    if (!p.keyword) delete p.keyword
    if (!p.dept_id) delete p.dept_id
    if (p.allocation_type === 0) delete p.allocation_type
    if (p.data_type === 0) delete p.data_type
    if (p.pool_type === 0) delete p.pool_type

    const res = await api.get('/team/customers', { params: p })
    const rows = res.items

    // BOM + CSV头部
    const BOM = '\uFEFF'
    const header = ['序号', '顾问姓名', '部门', '姓名', '手机', '城市', '意向产品', '意向额度(万)', '星级', '客户状态', '最后备注', '数据池']
    const lines = [header.join(',')]

    rows.forEach((r, i) => {
      lines.push([
        i + 1,
        r.advisor_name || '',
        r.dept_name || '',
        r.name || '',
        r.phone || '',
        r.city || '',
        r.loanTypeText || '',
        r.apply_amount || '',
        r.star_level || 0,
        r.statusText || '',
        r.last_remark_at ? r.last_remark_at.replace('T', ' ').substring(0, 16) : '',
        poolTagText(r.pool_type)
      ].map(v => `"${String(v).replace(/"/g, '""')}"`).join(','))
    })

    const blob = new Blob([BOM + lines.join('\r\n')], { type: 'text/csv;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `团队客户_${new Date().toISOString().slice(0, 10)}.csv`
    a.click()
    URL.revokeObjectURL(url)
    ElMessage.success(`已导出 ${rows.length} 条记录`)
  } catch (e) {
    ElMessage.error('导出失败')
  } finally {
    exporting.value = false
  }
}

// 加载部门
const loadDepartments = async () => {
  try { departments.value = await api.get('/departments') } catch (e) {}
}

// 加载所有用户
const loadAllUsers = async () => {
  try {
    allUsers.value = await api.get('/users')
    // 补充客户数
    for (const u of allUsers.value) {
      if (u.status === 1) {
        try {
          const res = await api.get('/my/customers', { params: { page: 1, page_size: 1 } })
          u.customer_count = res.total || 0
        } catch {}
      }
    }
  } catch (e) {}
}

onMounted(async () => {
  await loadDepartments()
  await loadAllUsers()
  await loadData()
})
</script>

<style scoped>
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px 0;
}
.page-header h3 {
  margin: 0;
  font-size: 16px;
  color: #333;
}
.header-toolbar {
  display: flex;
  gap: 8px;
}

.search-card {
  margin: 10px 0;
  border-radius: 6px;
}

.summary-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 16px;
  background: white;
  border-radius: 6px;
  margin-bottom: 10px;
  border: 1px solid #f0f0f0;
}
.summary-item {
  display: flex;
  align-items: center;
  gap: 6px;
}
.summary-label {
  color: #888;
  font-size: 13px;
}
.summary-value {
  font-size: 15px;
  font-weight: 600;
  color: #333;
}
.summary-value.primary { color: #409EFF; }
.summary-value.warning { color: #E6A23C; }
.summary-divider { color: #ddd; }

.table-card { border-radius: 6px; }

.tiny-avatar {
  width: 22px; height: 22px; border-radius: 50%;
  background: linear-gradient(135deg, #E91E63, #F48FB1);
  display: flex; align-items: center; justify-content: center;
  color: white; font-size: 10px; font-weight: bold;
  flex-shrink: 0;
}

.pagination-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 12px;
}
.total-hint { font-size: 13px; color: #888; }

:deep(.clickable-row) { cursor: pointer; }
:deep(.clickable-row:hover) { background: #f0f9ff !important; }
</style>
