<template>
  <div>
    <div class="page-header">
      <h3>必跟进客户 <el-tag type="warning">超过7天未备注</el-tag></h3>
      <el-button size="small" @click="loadData(1)"><Refresh /> 刷新</el-button>
    </div>

    <!-- 提示条 -->
    <el-alert
      title="必跟进说明"
      type="warning"
      :closable="false"
      style="margin:12px 0; border-radius:8px"
      show-icon
    >
      <template #default>
        超过 <b>7天</b> 未添加跟进备注的客户将自动进入必跟进列表。及时跟进并添加备注可使客户移出此列表。
      </template>
    </el-alert>

    <!-- 搜索栏 -->
    <el-card style="margin:12px 0">
      <el-form inline @submit.prevent="loadData(1)">
        <el-form-item label="关键词">
          <el-input v-model="params.keyword" placeholder="姓名/手机/ID" clearable style="width:150px" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="params.status" clearable placeholder="全部" style="width:120px">
            <el-option v-for="(name,val) in options.statusMap" :key="val" :label="name" :value="Number(val)" />
          </el-select>
        </el-form-item>
        <el-form-item label="星级">
          <el-select v-model="params.star" clearable placeholder="全部" style="width:100px">
            <el-option v-for="n in 7" :key="n-1" :label="`${n-1}星`" :value="n-1" />
          </el-select>
        </el-form-item>
        <el-form-item label="贷款类型">
          <el-select v-model="params.loan_type" clearable placeholder="全部" style="width:110px">
            <el-option v-for="(name,val) in options.loanTypeMap" :key="val" :label="name" :value="Number(val)" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData(1)"><Search /> 搜索</el-button>
        </el-form-item>
        <el-form-item>
          <el-button @click="resetParams">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 表格 -->
    <el-card>
      <div class="table-toolbar">
        <span style="color:#888; font-size:13px">共 <b style="color:#E91E63">{{ total }}</b> 条</span>
      </div>

      <el-table :data="customers" v-loading="loading" @row-click="openDetail" row-class-name="clickable-row" :stripe="true" size="small">
        <el-table-column label="ID" prop="id" width="65" />
        <el-table-column label="姓名" width="85">
          <template #default="{row}">
            <span :style="{color: row.is_important ? '#F56C6C' : ''}">{{ row.name || '—' }}</span>
            <el-tag v-if="row.is_important" type="danger" size="small" style="margin-left:2px">重要</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="性别" prop="genderText" width="45" />
        <el-table-column label="城市" prop="city" width="65" />
        <el-table-column label="年龄" prop="age" width="45" />
        <el-table-column label="状态" width="82">
          <template #default="{row}"><el-tag size="small" :type="statusTagType[row.status]">{{ row.statusText }}</el-tag></template>
        </el-table-column>
        <el-table-column label="星级" width="55">
          <template #default="{row}"><span style="color:#E6A23C">★</span>{{ row.star_level }}</template>
        </el-table-column>
        <el-table-column label="额度" prop="apply_amount" width="60">
          <template #default="{row}">{{ row.apply_amount ? row.apply_amount + '万' : '—' }}</template>
        </el-table-column>
        <el-table-column label="房" width="38">
          <template #default="{row}">
            <el-tag size="small" :type="row.qualifications?.has_house ? 'success' : 'info'" style="padding:0 4px">{{ row.qualifications?.has_house ? '✓' : '—' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="车" width="38">
          <template #default="{row}">
            <el-tag size="small" :type="row.qualifications?.has_car ? 'success' : 'info'" style="padding:0 4px">{{ row.qualifications?.has_car ? '✓' : '—' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="保单" width="38">
          <template #default="{row}">
            <el-tag size="small" :type="row.qualifications?.has_insurance ? 'success' : 'info'" style="padding:0 4px">{{ row.qualifications?.has_insurance ? '✓' : '—' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="最后备注" width="130">
          <template #default="{row}">{{ fmt(row.last_remark_at) }}</template>
        </el-table-column>
        <el-table-column label="创建时间" width="130">
          <template #default="{row}">{{ fmt(row.created_at) }}</template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div style="margin-top:12px; display:flex; justify-content:space-between; align-items:center">
        <div style="display:flex; align-items:center; gap:8px">
          <span style="color:#888; font-size:13px">每页</span>
          <el-select v-model="params.page_size" size="small" style="width:80px" @change="loadData(1)">
            <el-option :label="10" :value="10" /><el-option :label="20" :value="20" />
            <el-option :label="50" :value="50" /><el-option :label="100" :value="100" />
          </el-select>
        </div>
        <el-pagination background layout="prev,pager,next" :total="total" :page-size="params.page_size" v-model:current-page="params.page" @current-change="loadData" />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, inject } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, Search } from '@element-plus/icons-vue'
import { getAllOptions } from '../api'
import api from '../api'

const openCustomerDetail = inject('openCustomerDetail', null)

const customers = ref([])
const total = ref(0)
const loading = ref(false)
const options = ref({ statusMap: {}, loanTypeMap: {} })

const params = reactive({
  keyword: '', status: -1, star: -1, loan_type: -1,
  page: 1, page_size: 20
})

const statusTagType = {
  0:'', 1:'success', 2:'info', 3:'warning', 4:'warning', 5:'',
  6:'', 7:'success', 8:'success', 9:'danger', 10:'', 11:'info',
  12:'danger', 13:'danger', 14:'danger', 15:'', 16:'danger', 17:'danger', 18:''
}

const fmt = (t) => t ? t.replace('T',' ').substring(0,16) : '—'

const loadData = async (page = params.page) => {
  params.page = page
  loading.value = true
  try {
    const p = { page: params.page, page_size: params.page_size }
    if (params.keyword) p.keyword = params.keyword
    if (params.status >= 0) p.status = params.status
    if (params.star >= 0) p.star = params.star
    if (params.loan_type > 0) p.loan_type = params.loan_type
    // 必跟进 = pool_type=4 且超过7天未备注
    const res = await api.get('/important-pool', { params: p })
    customers.value = res.items || []
    total.value = res.total || 0
  } catch(e) { ElMessage.error(e.detail || '加载失败') }
  finally { loading.value = false }
}

const resetParams = () => {
  Object.assign(params, { keyword:'', status:-1, star:-1, loan_type:-1, page:1 })
  loadData(1)
}

const openDetail = (row) => {
  if (openCustomerDetail) openCustomerDetail(row.id, row.name)
}

onMounted(async () => {
  const opts = await getAllOptions()
  options.value = opts
  loadData()
})
</script>

<style scoped>
:deep(.clickable-row) { cursor: pointer; }
:deep(.clickable-row:hover) { background: #f0f9ff !important; }
.page-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 12px 0; flex-wrap: wrap; gap: 10px;
}
.page-header h3 { margin: 0; font-size: 18px; color: #303133; }
.table-toolbar {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 10px;
}
</style>
