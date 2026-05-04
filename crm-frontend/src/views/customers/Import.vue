<template>
  <div style="padding:16px; max-width:900px">
    <!-- 页面标题 -->
    <div class="page-header" style="margin-bottom:16px">
      <h3 style="margin:0; color:#E91E63">📥 数据导入</h3>
      <p style="margin:4px 0 0; color:#888; font-size:13px">批量导入客户数据，支持Excel格式，可管理导入批次</p>
    </div>

    <el-row :gutter="16">
      <!-- ===== 左侧：上传区 ===== -->
      <el-col :span="8">
        <el-card shadow="hover">
          <template #header>
            <div style="font-weight:600; display:flex; align-items:center; gap:6px">
              <span style="font-size:16px">📤</span> 上传文件
            </div>
          </template>

          <!-- 上传区 -->
          <div v-if="!importResult" class="import-area" @dragover.prevent @drop.prevent="handleDrop" @click="triggerFile">
            <div class="import-icon"><el-icon size="40" color="#E91E63"><Upload /></el-icon></div>
            <div class="import-text">
              <p style="font-size:13px; color:#333; margin:0 0 4px">拖拽 Excel 到此处</p>
              <p style="font-size:11px; color:#999; margin:0">或点击选择 .xlsx/.xls</p>
            </div>
            <input ref="fileInput" type="file" accept=".xlsx,.xls" style="display:none" @change="handleFileChange" />
          </div>

          <!-- 导入结果 -->
          <div v-if="importResult">
            <el-alert
              v-if="importResult.count > 0"
              :title="`成功导入 ${importResult.count} 条`"
              type="success" :closable="false"
              style="margin-bottom:10px; border-radius:8px"
            />
            <el-alert
              v-else
              title="未能导入任何有效数据"
              type="error" :closable="false"
              style="margin-bottom:10px; border-radius:8px"
            />
            <el-row :gutter="8">
              <el-col :span="12"><div class="result-card" style="border-top:3px solid #67C23A"><div class="result-num" style="color:#67C23A">{{ importResult.count }}</div><div class="result-label">成功</div></div></el-col>
              <el-col :span="12"><div class="result-card" style="border-top:3px solid #E6A23C"><div class="result-num" style="color:#E6A23C">{{ importResult.duplicate }}</div><div class="result-label">重复跳过</div></div></el-col>
            </el-row>
            <el-row :gutter="8" style="margin-top:8px">
              <el-col :span="12"><div class="result-card" style="border-top:3px solid #F56C6C"><div class="result-num" style="color:#F56C6C">{{ importResult.skip_count }}</div><div class="result-label">无效跳过</div></div></el-col>
              <el-col :span="12"><div class="result-card" style="border-top:3px solid #909399"><div class="result-num" style="color:#909399">{{ importResult.errors?.length || 0 }}</div><div class="result-label">异常</div></div></el-col>
            </el-row>

            <!-- 跳过原因 -->
            <div v-if="importResult.skip_reasons?.length > 0" style="margin-top:10px">
              <el-collapse>
                <el-collapse-item title="查看无效数据" name="skip">
                  <el-table :data="importResult.skip_reasons" size="small" max-height="200" style="font-size:11px">
                    <el-table-column label="行" prop="row" width="45" />
                    <el-table-column label="手机号" prop="phone" width="110" show-overflow-tooltip />
                    <el-table-column label="原因" prop="reason" />
                  </el-table>
                </el-collapse-item>
              </el-collapse>
            </div>

            <el-button style="margin-top:10px; width:100%" @click="resetUpload">继续上传新文件</el-button>
          </div>

          <template #footer>
            <el-button type="info" plain style="width:100%" :loading="importLoading" @click="triggerFile">
              <el-icon><Upload /></el-icon> 选择文件导入
            </el-button>
          </template>
        </el-card>

        <!-- 模板下载 -->
        <el-card shadow="hover" style="margin-top:12px">
          <template #header>
            <div style="font-weight:600; display:flex; align-items:center; gap:6px">
              <span style="font-size:16px">📋</span> 导入模板
            </div>
          </template>
          <div style="font-size:12px; color:#666; line-height:1.8">
            <p>Excel 第一行为表头，数据从第二行开始：</p>
            <div class="template-table">
              <table>
                <tr><th>手机号码*</th><th>姓名</th><th>性别</th><th>城市</th><th>年龄</th><th>星级</th><th>状态</th><th>申请金额</th><th>来源</th></tr>
                <tr><td>13800138000</td><td>张三</td><td>男</td><td>杭州</td><td>35</td><td>5</td><td>新客户</td><td>30</td><td>BXMJ-excel</td></tr>
              </table>
            </div>
            <p style="margin-top:8px; color:#E91E63">* 手机号为必填（11位）</p>
            <p style="margin-top:4px">状态：新客户/有意向/成交/失败</p>
            <p style="margin-top:4px">资质（公积金/房/车/保单）：填"有"或"无"</p>
          </div>
          <el-button type="primary" style="margin-top:10px; width:100%" @click="downloadTemplate">
            <el-icon><Download /></el-icon> 下载完整模板（含示例）
          </el-button>
        </el-card>
      </el-col>

      <!-- ===== 右侧：导入批次历史 ===== -->
      <el-col :span="16">
        <el-card shadow="hover">
          <template #header>
            <div style="font-weight:600; display:flex; justify-content:space-between; align-items:center">
              <span>📊 导入批次记录</span>
              <el-button size="small" @click="loadBatches(1)"><el-icon><Refresh /></el-icon> 刷新</el-button>
            </div>
          </template>

          <el-table :data="batches" v-loading="batchLoading" size="small" :stripe="true">
            <el-table-column label="时间" prop="created_at" width="150">
              <template #default="{row}">{{ fmt(row.created_at) }}</template>
            </el-table-column>
            <el-table-column label="操作人" prop="operator_name" width="90" />
            <el-table-column label="文件名" prop="filename" min-width="140" show-overflow-tooltip />
            <el-table-column label="成功" prop="success_count" width="60">
              <template #default="{row}"><span style="color:#67C23A; font-weight:600">{{ row.success_count }}</span></template>
            </el-table-column>
            <el-table-column label="重复" prop="duplicate_count" width="60">
              <template #default="{row}"><span style="color:#E6A23C">{{ row.duplicate_count }}</span></template>
            </el-table-column>
            <el-table-column label="跳过" width="60">
              <template #default="{row}"><span style="color:#F56C6C">{{ row.skip_count || 0 }}</span></template>
            </el-table-column>
            <el-table-column label="状态" width="75">
              <template #default="{row}">
                <el-tag size="small" :type="batchStatusTag[row.status]">{{ batchStatusMap[row.status] }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="160" fixed="right">
              <template #default="{row}">
                <template v-if="row.status === 1">
                  <el-button size="small" type="primary" link @click="showSkipDetail(row)">详情</el-button>
                  <el-button size="small" type="warning" link @click="toPool(row)">转公共池</el-button>
                  <el-button size="small" type="danger" link @click="cancelBatch(row)">撤销</el-button>
                </template>
                <span v-else style="color:#ccc; font-size:12px">—</span>
              </template>
            </el-table-column>
          </el-table>

          <!-- 分页 -->
          <div style="margin-top:12px; display:flex; justify-content:space-between; align-items:center">
            <span style="color:#888; font-size:13px">共 {{ batchTotal }} 条</span>
            <el-pagination
              background layout="prev,pager,next"
              :total="batchTotal" :page-size="20"
              v-model:current-page="batchPage"
              @current-change="loadBatches"
            />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 跳过原因详情弹窗 -->
    <el-dialog v-model="skipDetailVisible" title="导入无效数据详情" width="600px">
      <div v-if="skipDetail">
        <p style="margin:0 0 12px; color:#666; font-size:13px">
          批次：{{ skipDetail.filename }} &nbsp;|&nbsp; 操作人：{{ skipDetail.operator_name }} &nbsp;|&nbsp;
          总计跳过 {{ skipDetail.skip_count || 0 }} 条
        </p>
        <el-table :data="skipDetail.skip_detail" size="small" max-height="400" :stripe="true">
          <el-table-column label="行号" prop="row" width="70" />
          <el-table-column label="手机号" prop="phone" width="140" />
          <el-table-column label="跳过原因" prop="reason" />
        </el-table>
        <div v-if="!skipDetail.skip_detail?.length" style="text-align:center; color:#999; padding:30px">
          暂无无效数据记录
        </div>
      </div>
      <template #footer>
        <el-button @click="skipDetailVisible=false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getImportLogs, cancelImportBatch, importBatchToPool } from '../../api'
import { Upload, Download, Refresh } from '@element-plus/icons-vue'

const fileInput = ref()
const importLoading = ref(false)
const importResult = ref(null)
const batches = ref([])
const batchTotal = ref(0)
const batchPage = ref(1)
const batchLoading = ref(false)
const skipDetailVisible = ref(false)
const skipDetail = ref(null)

const batchStatusMap = { 1: '已完成', 2: '已撤销', 3: '处理失败' }
const batchStatusTag = { 1: 'success', 2: 'info', 3: 'danger' }

const fmt = (t) => t ? String(t).replace('T', ' ').substring(0, 16) : '—'

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
      importResult.value = {
        count: 0, duplicate: 0, skip_count: 0,
        errors: result.detail ? [result.detail] : [],
        skip_reasons: [], missing_columns: [], has_issues: true
      }
      ElMessage.error(result.detail || '导入失败')
      return
    }
    importResult.value = result
    if (result.count > 0) {
      ElMessage.success(`成功导入 ${result.count} 条客户数据`)
    } else if (result.skip_count > 0) {
      ElMessage.warning(`未能导入有效数据，共 ${result.skip_count} 行手机号无效`)
    } else {
      ElMessage.warning('未检测到有效数据行')
    }
    loadBatches(1)
  } catch(e) {
    ElMessage.error(e.message || '导入失败')
  } finally {
    importLoading.value = false
  }
}

const resetUpload = () => {
  importResult.value = null
}

const loadBatches = async (p = batchPage.value) => {
  batchPage.value = p
  batchLoading.value = true
  try {
    const res = await getImportLogs({ page: p, page_size: 20 })
    batches.value = res.items || res
    batchTotal.value = res.total || 0
  } catch(e) {
    ElMessage.error('加载导入记录失败')
  } finally {
    batchLoading.value = false
  }
}

const showSkipDetail = (row) => {
  skipDetail.value = row
  skipDetailVisible.value = true
}

const cancelBatch = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定撤销 ${row.operator_name} 的导入批次（共 ${row.success_count} 条）？撤销后分配记录失效，客户数据保留。`,
      '撤销导入', { type: 'warning', confirmButtonText: '确定撤销', cancelButtonText: '取消' }
    )
    await cancelImportBatch(row.id)
    ElMessage.success('撤销成功')
    loadBatches(batchPage.value)
  } catch(e) {
    if (e !== 'cancel') ElMessage.error(e.message || '撤销失败')
  }
}

const toPool = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定将 ${row.operator_name} 导入的 ${row.success_count} 名客户转入公共池？`,
      '转入公共池', { type: 'info', confirmButtonText: '确定转入', cancelButtonText: '取消' }
    )
    await importBatchToPool(row.id)
    ElMessage.success('已转入公共池')
    loadBatches(batchPage.value)
  } catch(e) {
    if (e !== 'cancel') ElMessage.error(e.message || '操作失败')
  }
}

onMounted(() => {
  loadBatches(1)
})
</script>

<style scoped>
.import-area {
  border: 2px dashed #E91E63;
  border-radius: 10px;
  padding: 28px 16px;
  text-align: center;
  cursor: pointer;
  background: #FCE4EC;
  transition: all 0.2s;
  margin-bottom: 12px;
}
.import-area:hover { border-color: #C2185B; background: #F8BBD0; }
.import-icon { margin-bottom: 10px; }
.import-text p { margin: 0; }
.template-table { overflow-x: auto; }
.template-table table { width: 100%; border-collapse: collapse; font-size: 10px; }
.template-table th, .template-table td { border: 1px solid #eee; padding: 3px 5px; text-align: center; }
.template-table th { background: #FCE4EC; color: #E91E63; }
.result-card { background: #fff; border: 1px solid #eee; border-radius: 8px; padding: 10px 12px; text-align: center; }
.result-num { font-size: 22px; font-weight: 700; }
.result-label { font-size: 11px; color: #888; margin-top: 2px; }
</style>
