<template>
  <div>
    <div class="page-header">
      <h3>创收分析</h3>
      <div style="display:flex; gap:8px; align-items:center">
        <el-date-picker
          v-model="month"
          type="month"
          placeholder="选择月份"
          style="width:140px"
          @change="loadData"
        />
        <el-button @click="loadData"><Refresh /> 刷新</el-button>
      </div>
    </div>

    <!-- 核心指标 -->
    <el-row :gutter="14" style="margin:14px 0">
      <el-col :span="5">
        <div class="kpi-card" style="border-top-color:#E91E63">
          <div class="kpi-label">本月进件数</div>
          <div class="kpi-num" style="color:#E91E63">{{ monthData.caseCount }}</div>
          <div class="kpi-sub">件</div>
        </div>
      </el-col>
      <el-col :span="5">
        <div class="kpi-card" style="border-top-color:#67C23A">
          <div class="kpi-label">本月批款数</div>
          <div class="kpi-num" style="color:#67C23A">{{ monthData.approveCount }}</div>
          <div class="kpi-sub">件</div>
        </div>
      </el-col>
      <el-col :span="5">
        <div class="kpi-card" style="border-top-color:#409EFF">
          <div class="kpi-label">本月批款金额</div>
          <div class="kpi-num" style="color:#409EFF">{{ monthData.approveAmount.toFixed(1) }}</div>
          <div class="kpi-sub">万元</div>
        </div>
      </el-col>
      <el-col :span="5">
        <div class="kpi-card" style="border-top-color:#E6A23C">
          <div class="kpi-label">批款率</div>
          <div class="kpi-num" style="color:#E6A23C">{{ approveRate }}%</div>
          <div class="kpi-sub">{{ monthData.approveCount }}/{{ monthData.caseCount }}</div>
        </div>
      </el-col>
      <el-col :span="4">
        <div class="kpi-card" style="border-top-color:#F56C6C">
          <div class="kpi-label">收款数</div>
          <div class="kpi-num" style="color:#F56C6C">{{ monthData.collectionCount }}</div>
          <div class="kpi-sub">件</div>
        </div>
      </el-col>
    </el-row>

    <!-- 图表区 -->
    <el-row :gutter="14" style="margin-bottom:14px">
      <!-- 近6月趋势 -->
      <el-col :span="14">
        <el-card>
          <template #header><span>近6个月进件/批款趋势</span></template>
          <div ref="trendChart" style="height:260px"></div>
        </el-card>
      </el-col>

      <!-- 进件银行占比 -->
      <el-col :span="10">
        <el-card>
          <template #header><span>进件银行占比</span></template>
          <div ref="bankChart" style="height:260px"></div>
          <div v-if="!bankDist.length" class="empty-placeholder">
            <el-empty description="暂无进件数据" :image-size="60" />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 销售漏斗 + 进件明细 -->
    <el-row :gutter="14" style="margin-bottom:14px">
      <el-col :span="8">
        <el-card>
          <template #header><span>销售漏斗</span></template>
          <div ref="funnelChart" style="height:280px"></div>
        </el-card>
      </el-col>

      <el-col :span="16">
        <el-card>
          <template #header>
            <div style="display:flex; justify-content:space-between; align-items:center">
              <span>进件明细</span>
              <el-select v-model="filterStage" size="small" style="width:100px" @change="loadCases">
                <el-option label="全部" :value="-1" />
                <el-option v-for="(n,v) in stageMap" :key="v" :label="n" :value="Number(v)" />
              </el-select>
            </div>
          </template>
          <el-table :data="loanCases" v-loading="casesLoading" size="small" :stripe="true">
            <el-table-column label="客户" width="90">
              <template #default="{row}">
                <span style="color:#E91E63; cursor:pointer" @click="openCustomerDetail && openCustomerDetail(row.customer_id, row.customer_name)">
                  {{ row.customer_name }}
                </span>
              </template>
            </el-table-column>
            <el-table-column label="银行" prop="bank_name" width="90" />
            <el-table-column label="申请额(万)" prop="apply_amount" width="90">
              <template #default="{row}">{{ Number(row.apply_amount||0).toFixed(1) }}</template>
            </el-table-column>
            <el-table-column label="费率" prop="fee_rate" width="65">
              <template #default="{row}">{{ row.fee_rate ? (row.fee_rate*100).toFixed(1)+'%' : '—' }}</template>
            </el-table-column>
            <el-table-column label="阶段" width="80">
              <template #default="{row}">
                <el-tag size="small" :type="stageTagType[row.stage]">{{ row.stageText }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="批款额(万)" width="85">
              <template #default="{row}">{{ row.approve_amount ? Number(row.approve_amount).toFixed(1) : '—' }}</template>
            </el-table-column>
            <el-table-column label="提交时间" min-width="100">
              <template #default="{row}">{{ fmt(row.submit_at) }}</template>
            </el-table-column>
          </el-table>
          <div style="margin-top:10px;text-align:right">
            <el-pagination small background layout="prev,pager,next"
              :total="casesTotal" :page-size="10"
              v-model:current-page="casesPage" @current-change="loadCases" />
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick, inject } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import * as echarts from 'echarts'

const openCustomerDetail = inject('openCustomerDetail', null)

const month = ref(new Date())
const loading = ref(false)
const loanCases = ref([])
const casesTotal = ref(0)
const casesPage = ref(1)
const casesLoading = ref(false)
const filterStage = ref(-1)
const bankChart = ref()
const funnelChart = ref()
const trendChart = ref()
const bankDist = ref([])
const trendData = ref([])

const stageMap = { 1: '审核中', 2: '已批款', 3: '已收款', 4: '已拒批', 5: '已违约' }
const stageTagType = { 1: 'warning', 2: 'success', 3: 'primary', 4: 'danger', 5: 'info' }

const monthData = reactive({
  caseCount: 0, approveCount: 0, collectionCount: 0, approveAmount: 0
})

const approveRate = computed(() => {
  if (!monthData.caseCount) return 0
  return Math.round(monthData.approveCount / monthData.caseCount * 100)
})

const fmt = (t) => t ? t.replace('T', ' ').substring(0, 16) : '—'

const monthStr = computed(() => {
  const d = month.value
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`
})

const apiFetch = (url) => fetch(url, {
  headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
})

const loadData = async () => {
  loading.value = true
  try {
    // 月度统计
    const mRes = await apiFetch(`/api/stats/monthly?month=${monthStr.value}`)
    if (mRes.ok) {
      const d = await mRes.json()
      Object.assign(monthData, d)
      monthData.approveAmount = d.approveAmount || 0
    }

    // 银行分布
    const bankRes = await apiFetch(`/api/stats/bank-dist?month=${monthStr.value}`)
    if (bankRes.ok) bankDist.value = await bankRes.json()

    // 月度趋势
    const trendRes = await apiFetch('/api/stats/monthly-trend?months=6')
    if (trendRes.ok) trendData.value = await trendRes.json()

    await loadCases(1)
    await nextTick()
    setTimeout(renderCharts, 50)
  } catch(e) {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

const loadCases = async (p = casesPage.value) => {
  casesPage.value = p
  casesLoading.value = true
  try {
    const stage = filterStage.value > 0 ? `&stage=${filterStage.value}` : ''
    const res = await apiFetch(`/api/loan-cases?page=${p}&page_size=10${stage}`)
    if (res.ok) {
      const d = await res.json()
      loanCases.value = d.items
      casesTotal.value = d.total
    }
  } catch(e) {} finally { casesLoading.value = false }
}

const COLORS = ['#E91E63', '#F48FB1', '#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399', '#8E24AA', '#00ACC1', '#43A047']

const renderCharts = () => {
  // 近6月趋势折线图
  if (trendChart.value && trendData.value.length) {
    const chart = echarts.getInstanceByDom(trendChart.value) || echarts.init(trendChart.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { bottom: 0, data: ['进件数', '批款数', '收款数'], textStyle: { fontSize: 11 } },
      grid: { left: 10, right: 10, bottom: 40, top: 10, containLabel: true },
      xAxis: { type: 'category', data: trendData.value.map(d => d.label), axisLabel: { fontSize: 11 } },
      yAxis: { type: 'value', minInterval: 1 },
      series: [
        {
          name: '进件数', type: 'line', smooth: true,
          data: trendData.value.map(d => d.case_count),
          itemStyle: { color: '#E91E63' },
          areaStyle: { color: 'rgba(233,30,99,0.1)' }
        },
        {
          name: '批款数', type: 'line', smooth: true,
          data: trendData.value.map(d => d.approve_count),
          itemStyle: { color: '#67C23A' },
          areaStyle: { color: 'rgba(103,194,58,0.1)' }
        },
        {
          name: '收款数', type: 'line', smooth: true,
          data: trendData.value.map(d => d.collection_count),
          itemStyle: { color: '#409EFF' }
        }
      ]
    })
  }

  // 银行占比饼图
  if (bankChart.value && bankDist.value.length) {
    const chart = echarts.getInstanceByDom(bankChart.value) || echarts.init(bankChart.value)
    chart.setOption({
      tooltip: { trigger: 'item' },
      legend: { bottom: 0, textStyle: { fontSize: 11 } },
      series: [{
        type: 'pie', radius: ['40%', '70%'],
        data: bankDist.value.map((d, i) => ({
          ...d,
          itemStyle: { color: COLORS[i % COLORS.length] }
        })),
        label: { fontSize: 11 },
        emphasis: { label: { fontSize: 14 } }
      }]
    })
  }

  // 销售漏斗
  if (funnelChart.value) {
    const chart = echarts.getInstanceByDom(funnelChart.value) || echarts.init(funnelChart.value)
    const total = monthData.caseCount || 1
    chart.setOption({
      tooltip: { trigger: 'item' },
      series: [{
        type: 'funnel', left: '10%', top: 30, bottom: 20,
        width: '80%', gap: 4,
        data: [
          { name: `进件 ${monthData.caseCount}件`, value: 100 },
          { name: `批款 ${monthData.approveCount}件`, value: Math.round(monthData.approveCount / total * 100) },
          { name: `收款 ${monthData.collectionCount}件`, value: Math.round(monthData.collectionCount / total * 100) }
        ].map((d, i) => ({ ...d, itemStyle: { color: ['#E91E63', '#67C23A', '#409EFF'][i] } })),
        label: { show: true, position: 'inside', fontSize: 12, color: 'white' }
      }]
    })
  }
}

onMounted(loadData)
</script>

<style scoped>
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 0 8px;
}
.page-header h3 { margin: 0; font-size: 18px; }

.kpi-card {
  background: white;
  border-radius: 10px;
  padding: 16px 12px;
  border-top: 4px solid;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
  text-align: center;
  transition: transform 0.2s;
}
.kpi-card:hover { transform: translateY(-2px); }
.kpi-label { font-size: 11px; color: #888; margin-bottom: 4px; }
.kpi-num { font-size: 32px; font-weight: bold; line-height: 1.1; }
.kpi-sub { font-size: 11px; color: #aaa; margin-top: 3px; }

.empty-placeholder {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255,255,255,0.85);
}
</style>
