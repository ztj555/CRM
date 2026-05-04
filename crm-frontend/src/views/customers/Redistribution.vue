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
      <!-- 批量操作栏 -->
      <div v-if="selectedRows.length > 0" class="batch-bar" style="margin-bottom:12px">
        <span style="font-size:13px">已选 <b style="color:#E91E63">{{ selectedRows.length }}</b> 条</span>
        <el-button size="small" type="danger" @click="batchToPool">批量转公共池</el-button>
        <el-button size="small" type="success" @click="batchToMyCustomers">批量加入我的客户</el-button>
        <el-button size="small" @click="selectedRows=[];onTableRef?.clearSelection()">取消选择</el-button>
      </div>

      <el-table ref="onTableRef" :data="customers" v-loading="loading" @row-click="openDetail" row-class-name="clickable-row" :stripe="true" size="small" @selection-change="onSelectionChange">
        <el-table-column type="selection" width="38" @click.stop />
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
          <template #default="{row}"><span style="color:#E6A23C">★</span>{{ row.star_level }}星</template>
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

    <!-- 数据导入对话框 -->
    <el-dialog v-model="importVisible" title="数据导入" width="580px" :close-on-click-modal="false">
      <!-- 上传区 -->
      <div v-if="!importResult" class="import-area" @dragover.prevent @drop.prevent="handleDrop" @click="triggerFile">
        <div class="import-icon"><el-icon size="40" color="#E91E63"><Upload /></el-icon></div>
        <div class="import-text">
          <p style="font-size:14px; color:#333; margin:0 0 4px">拖拽 Excel 文件到此处</p>
          <p style="font-size:12px; color:#999; margin:0">或点击选择文件，支持 .xlsx / .xls 格式</p>
        </div>
        <input ref="fileInput" type="file" accept=".xlsx,.xls" style="display:none" @change="handleFileChange" />
      </div>

      <!-- 导入结果区 -->
      <div v-if="importResult">
        <el-alert
          v-if="importResult.count > 0"
          :title="`成功导入 ${importResult.count} 条客户数据`"
          type="success" :closable="false"
          style="margin-bottom:12px; border-radius:8px"
        />
        <el-alert
          v-else
          title="导入失败：未能导入任何有效数据"
          type="error" :closable="false"
          style="margin-bottom:12px; border-radius:8px"
        />

        <!-- 统计卡片 -->
        <el-row :gutter="10" style="margin-bottom:12px">
          <el-col :span="6">
            <div class="result-card" style="border-top:3px solid #67C23A">
              <div class="result-num" style="color:#67C23A">{{ importResult.count }}</div>
              <div class="result-label">成功导入</div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="result-card" style="border-top:3px solid #E6A23C">
              <div class="result-num" style="color:#E6A23C">{{ importResult.duplicate }}</div>
              <div class="result-label">重复跳过</div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="result-card" style="border-top:3px solid #F56C6C">
              <div class="result-num" style="color:#F56C6C">{{ importResult.skip_count }}</div>
              <div class="result-label">无效跳过</div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="result-card" style="border-top:3px solid #909399">
              <div class="result-num" style="color:#909399">{{ importResult.errors?.length || 0 }}</div>
              <div class="result-label">处理异常</div>
            </div>
          </el-col>
        </el-row>

        <!-- 跳过原因详情（可展开） -->
        <div v-if="importResult.skip_reasons?.length > 0">
          <el-collapse>
            <el-collapse-item title="查看无效数据详情" name="skip">
              <el-table :data="importResult.skip_reasons" size="small" max-height="240" style="font-size:12px">
                <el-table-column label="行号" prop="row" width="60" />
                <el-table-column label="手机号" prop="phone" width="130" show-overflow-tooltip />
                <el-table-column label="原因" prop="reason" />
              </el-table>
              <div v-if="importResult.skip_count > importResult.skip_reasons.length" style="font-size:12px;color:#999;margin-top:4px">
                还有 {{ importResult.skip_count - importResult.skip_reasons.length }} 条未显示
              </div>
            </el-collapse-item>
          </el-collapse>
        </div>

        <!-- 缺失列提示 -->
        <div v-if="importResult.missing_columns?.length" style="margin-top:10px">
          <el-alert
            :title="`文件缺少列：${importResult.missing_columns.join('、')}，` + (importResult.count === 0 ? '请下载最新模板重新填写' : '这些字段将使用默认值')"
            :type="importResult.count === 0 ? 'error' : 'warning'" :closable="false"
            style="border-radius:8px"
          />
        </div>
      </div>

      <!-- 导入模板说明（上传前显示） -->
      <div v-if="!importResult" class="import-template">
        <div class="template-title"><el-icon><InfoFilled /></el-icon> Excel 格式要求</div>
        <div style="font-size:12px; color:#666; line-height:1.8; margin-top:8px">
          <p>Excel 文件需包含以下列（第一行为表头）：</p>
          <div class="template-table">
            <table>
              <tr><th>手机号码</th><th>姓名</th><th>性别</th><th>城市</th><th>年龄</th><th>星级</th><th>状态</th><th>申请金额(万)</th><th>来源</th></tr>
              <tr><td>13800138000</td><td>张三</td><td>男</td><td>杭州</td><td>35</td><td>5</td><td>新客户</td><td>30</td><td>BXMJ-excel</td></tr>
            </table>
          </div>
          <p style="margin-top:8px; color:#E91E63">* 手机号为必填项（11位数字），其他字段可选。星级填1-5，状态如：新客户/有意向/成交/失败</p>
          <p style="margin-top:4px">资质字段（公积金/房/车/保单）：填"有"或"无"</p>
        </div>
      </div>

      <template #footer>
        <el-button @click="closeImportDialog">关闭</el-button>
        <el-button @click="downloadTemplate" type="info">
          <el-icon><Download /></el-icon> 下载模板
        </el-button>
        <el-button v-if="!importResult" type="primary" :loading="importLoading" @click="triggerFile">
          <el-icon><Upload /></el-icon> 选择文件
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, inject } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getCustomers, getAllOptions, getDepts, getTeamMembers, toPool } from '../../api'
import { Upload, Search, InfoFilled, Download } from '@element-plus/icons-vue'

const openCustomerDetail = inject('openCustomerDetail', null)

const customers = ref([])
const total = ref(0)
const loading = ref(false)
const options = ref({ statusMap: {}, loanTypeMap: {}, sources: [], cityList: [] })

const importVisible = ref(false)
const importLoading = ref(false)
const fileInput = ref()
const importResult = ref(null)  // 导入结果详情
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

const downloadTemplate = () => {
  const a = document.createElement('a')
  a.href = '/static/template.xlsx'
  a.download = '客户导入模板.xlsx'
  a.click()
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
  importResult.value = null
  try {
    const formData = new FormData()
    formData.append('file', file)
    const response = await fetch('/api/customers/import-file', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` },
      body: formData
    })
    const result = await response.json()
    if (!response.ok) {
      // 文件级错误（如列缺失、全部无效），也显示结果区
      importResult.value = {
        count: 0,
        duplicate: 0,
        skip_count: 0,
        errors: result.detail ? [result.detail] : [],
        skip_reasons: [],
        missing_columns: [],
        has_issues: true
      }
      ElMessage.error(result.detail || '导入失败')
      return
    }
    // 成功：显示详细结果
    importResult.value = result
    if (result.count > 0) {
      ElMessage.success(`成功导入 ${result.count} 条客户数据`)
    } else if (result.skip_count > 0) {
      ElMessage.warning(`未能导入有效数据，共 ${result.skip_count} 行手机号无效`)
    } else {
      ElMessage.warning('未检测到有效数据行')
    }
    loadData(1)
  } catch(e) {
    ElMessage.error(e.message || '导入失败，请检查文件格式')
  } finally {
    importLoading.value = false
  }
}

const closeImportDialog = () => {
  importVisible.value = false
  importResult.value = null
}

// ====== 批量操作 ======
const onTableRef = ref(null)
const selectedRows = ref([])

const onSelectionChange = (selection) => {
  selectedRows.value = selection
}

const batchToPool = async () => {
  if (!selectedRows.value.length) return
  await ElMessageBox.confirm(`确定将选中的 ${selectedRows.value.length} 个客户批量移入公共池？`, '批量转公共池', { type: 'warning' })
  try {
    const res = await fetch('/api/customers/batch-to-pool', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${localStorage.getItem('token')}` },
      body: JSON.stringify({ customer_ids: selectedRows.value.map(r => r.id) })
    })
    const d = await res.json()
    ElMessage.success(`已将 ${d.moved} 个客户移入公共池`)
    selectedRows.value = []
    onTableRef.value?.clearSelection()
    loadData(1)
  } catch(e) { if (e !== 'cancel') ElMessage.error('批量操作失败') }
}

const batchToMyCustomers = async () => {
  if (!selectedRows.value.length) return
  await ElMessageBox.confirm(`确定将选中的 ${selectedRows.value.length} 个客户加入我的客户？`, '批量加入我的客户', { type: 'success' })
  try {
    const res = await fetch('/api/customers/batch-to-mine', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${localStorage.getItem('token')}` },
      body: JSON.stringify({ customer_ids: selectedRows.value.map(r => r.id) })
    })
    const d = await res.json()
    ElMessage.success(`已将 ${d.assigned} 个客户加入我的客户`)
    selectedRows.value = []
    onTableRef.value?.clearSelection()
    loadData(1)
  } catch(e) { if (e !== 'cancel') ElMessage.error('批量操作失败') }
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
onUnmounted(() => {})
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
.result-card { background:#fff; border:1px solid #eee; border-radius:8px; padding:10px 12px; text-align:center; }
.result-num { font-size:22px; font-weight:700; }
.result-label { font-size:11px; color:#888; margin-top:2px; }
.import-history { background:#F8F8F8; border-radius:8px; padding:12px 16px; }

:deep(.clickable-row) { cursor: pointer; }
:deep(.clickable-row:hover) { background: #f0f9ff !important; }
</style>
