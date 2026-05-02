<template>
  <div>
    <!-- 公告滚动条 -->
    <div v-if="marqueeNotices.length > 0" class="notice-marquee">
      <span class="notice-tag">📢 公告</span>
      <el-scrollbar>
        <div class="marquee-inner">
          <span v-for="(n, i) in marqueeNotices" :key="n.id" class="marquee-text">
            {{ n.title }}{{ n.content ? '：' + n.content : '' }}
            <span v-if="i < marqueeNotices.length - 1" class="marquee-sep">｜</span>
          </span>
        </div>
      </el-scrollbar>
    </div>

    <!-- 公告卡片列表 -->
    <div v-if="normalNotices.length > 0" style="margin-bottom:14px">
      <div v-for="n in normalNotices" :key="n.id" class="notice-card">
        <el-icon><InfoFilled /></el-icon>
        <span class="notice-title">{{ n.title }}</span>
        <span class="notice-content">{{ n.content }}</span>
        <span class="notice-time">{{ n.created_at }}</span>
      </div>
    </div>

    <div class="page-header">
      <h3>工作简报</h3>
      <div style="display:flex; align-items:center; gap:8px">
        <el-tag type="danger" size="large" style="font-size:13px; padding:4px 12px">
          当前：{{ currentMonth }}
        </el-tag>
        <el-button size="small" @click="loadData"><Refresh /> 刷新</el-button>
      </div>
    </div>

    <!-- 数字指标卡 -->
    <el-row :gutter="14" style="margin:16px 0">
      <el-col :span="5">
        <div class="kpi-card" style="border-top-color:#E91E63">
          <div class="kpi-icon" style="background:#fff0f6; color:#E91E63">👥</div>
          <div class="kpi-num" style="color:#E91E63">{{ stats.total || 0 }}</div>
          <div class="kpi-label">我的客户总数</div>
        </div>
      </el-col>
      <el-col :span="5">
        <div class="kpi-card" style="border-top-color:#67C23A">
          <div class="kpi-icon" style="background:#f0f9eb; color:#67C23A">📥</div>
          <div class="kpi-num" style="color:#67C23A">{{ brief.today?.new_clients || stats.todayNew || 0 }}</div>
          <div class="kpi-label">今日新增</div>
        </div>
      </el-col>
      <el-col :span="5">
        <div class="kpi-card" style="border-top-color:#409EFF">
          <div class="kpi-icon" style="background:#ecf5ff; color:#409EFF">📝</div>
          <div class="kpi-num" style="color:#409EFF">{{ brief.today?.remarks || stats.todayRemark || 0 }}</div>
          <div class="kpi-label">今日跟进</div>
        </div>
      </el-col>
      <el-col :span="5">
        <div class="kpi-card" style="border-top-color:#E6A23C">
          <div class="kpi-icon" style="background:#fdf6ec; color:#E6A23C">📋</div>
          <div class="kpi-num" style="color:#E6A23C">{{ brief.today?.loan_in || stats.todayCases || 0 }}</div>
          <div class="kpi-label">今日进件</div>
        </div>
      </el-col>
      <el-col :span="4">
        <div class="kpi-card" style="border-top-color:#F56C6C">
          <div class="kpi-icon" style="background:#fef0f0; color:#F56C6C">🏊</div>
          <div class="kpi-num" style="color:#F56C6C">{{ stats.poolCount || 0 }}</div>
          <div class="kpi-label">公共池客户</div>
        </div>
      </el-col>
    </el-row>

    <!-- 今日/昨日工作概况对比 -->
    <el-row :gutter="14" style="margin-bottom:14px" v-if="brief.today">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header-title">
              <span style="background:#E91E63;color:white;padding:2px 8px;border-radius:4px;font-size:12px">今日</span>
              <span>工作概况</span>
              <el-tag type="success" size="small" effect="plain" style="margin-left:auto">{{ todayDate }}</el-tag>
            </div>
          </template>
          <div class="brief-grid">
            <div class="brief-cell">
              <div class="brief-label">新申请</div>
              <div class="brief-val" style="color:#E91E63">{{ brief.today?.new_clients || 0 }}</div>
            </div>
            <div class="brief-cell">
              <div class="brief-label">未处理</div>
              <div class="brief-val" style="color:#F56C6C">{{ brief.today?.unhandled || 0 }}</div>
            </div>
            <div class="brief-cell">
              <div class="brief-label">跟进数</div>
              <div class="brief-val" style="color:#409EFF">{{ brief.today?.remarks || 0 }}</div>
            </div>
            <div class="brief-cell">
              <div class="brief-label">进件数</div>
              <div class="brief-val" style="color:#E6A23C">{{ brief.today?.loan_in || 0 }}</div>
            </div>
            <div class="brief-cell">
              <div class="brief-label">批款数</div>
              <div class="brief-val" style="color:#67C23A">{{ brief.today?.loan_approved || 0 }}</div>
            </div>
            <div class="brief-cell">
              <div class="brief-label">批款金额</div>
              <div class="brief-val" style="color:#67C23A; font-size:16px">{{ brief.today?.approve_amount ? (brief.today.approve_amount / 10000).toFixed(1)+'万' : '-' }}</div>
            </div>
          </div>
          <div v-if="brief.review" class="review-bar">
            <span>主管点评：累计<b style="color:#E91E63">{{ brief.review?.total }}</b>次</span>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header-title">
              <span style="background:#aaa;color:white;padding:2px 8px;border-radius:4px;font-size:12px">昨日</span>
              <span>工作回顾</span>
            </div>
          </template>
          <div class="brief-grid">
            <div class="brief-cell">
              <div class="brief-label">新申请</div>
              <div class="brief-val">{{ brief.yesterday?.new_clients || 0 }}</div>
            </div>
            <div class="brief-cell">
              <div class="brief-label">未处理</div>
              <div class="brief-val">{{ brief.yesterday?.unhandled || 0 }}</div>
            </div>
            <div class="brief-cell">
              <div class="brief-label">跟进数</div>
              <div class="brief-val">{{ brief.yesterday?.remarks || 0 }}</div>
            </div>
            <div class="brief-cell">
              <div class="brief-label">进件数</div>
              <div class="brief-val">{{ brief.yesterday?.loan_in || 0 }}</div>
            </div>
            <div class="brief-cell">
              <div class="brief-label">批款数</div>
              <div class="brief-val">{{ brief.yesterday?.loan_approved || 0 }}</div>
            </div>
            <div class="brief-cell">
              <div class="brief-label">批款金额</div>
              <div class="brief-val" style="font-size:16px">{{ brief.yesterday?.approve_amount ? (brief.yesterday.approve_amount / 10000).toFixed(1)+'万' : '-' }}</div>
            </div>
          </div>
          <div class="month-progress">
            <span style="font-size:12px;color:#888">本月进件：</span>
            <el-progress :percentage="Math.min(100, Math.round((brief.month?.loan_in || 0) / 20 * 100))" :color="'#E91E63'" :stroke-width="8" style="flex:1" />
            <span style="font-size:12px;color:#E91E63;font-weight:600;white-space:nowrap">{{ brief.month?.loan_in || 0 }} / 20</span>
          </div>
          <div style="display:flex;gap:16px;margin-top:8px;padding-top:8px;border-top:1px solid #f0f0f0">
            <span style="font-size:12px;color:#F56C6C">
              <b>{{ brief.failed_assessment || 0 }}</b> 人未过考核
            </span>
            <span style="font-size:12px;color:#E6A23C">
              <b>{{ brief.suspended_count || 0 }}</b> 人已暂停
            </span>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表第一行：星级 + 状态分布 -->
    <el-row :gutter="14" style="margin-bottom:14px">
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header-title">
              <el-icon color="#E91E63"><PieChart /></el-icon>
              客户星级分布
            </div>
          </template>
          <div ref="starChartRef" style="height:260px"></div>
          <div v-if="!stats.starDist?.length" class="empty-chart">
            <el-empty description="暂无数据" :image-size="60" />
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header-title">
              <el-icon color="#409EFF"><DataLine /></el-icon>
              客户状态分布
            </div>
          </template>
          <div ref="statusChartRef" style="height:260px"></div>
          <div v-if="!statusDist?.length" class="empty-chart">
            <el-empty description="暂无数据" :image-size="60" />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表第二行：来源分布 + 本月统计 -->
    <el-row :gutter="14" style="margin-bottom:14px">
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header-title">
              <el-icon color="#E6A23C"><Histogram /></el-icon>
              客户来源分布
            </div>
          </template>
          <div ref="sourceChartRef" style="height:260px"></div>
          <div v-if="!sourceDist?.length" class="empty-chart">
            <el-empty description="暂无数据" :image-size="60" />
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header-title">
              <el-icon color="#67C23A"><TrendCharts /></el-icon>
              本月业绩统计
            </div>
          </template>
          <div style="padding:10px 0">
            <el-row :gutter="10">
              <el-col :span="8" v-for="item in monthStatsItems" :key="item.label">
                <div class="month-stat">
                  <div class="ms-icon">{{ item.icon }}</div>
                  <div class="ms-num" :style="{ color: item.color }">{{ item.value }}</div>
                  <div class="ms-label">{{ item.label }}</div>
                  <el-progress
                    v-if="item.target"
                    :percentage="Math.min(100, Math.round(item.value / item.target * 100))"
                    :stroke-width="4"
                    :color="item.color"
                    :show-text="false"
                    style="margin-top:6px"
                  />
                  <div v-if="item.target" style="font-size:10px;color:#aaa;margin-top:2px">
                    目标 {{ item.target }}
                  </div>
                </div>
              </el-col>
            </el-row>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 待处理提醒 -->
    <el-card v-if="reminders.length > 0" style="margin-top:14px; border-left: 3px solid #E6A23C">
      <template #header>
        <div style="display:flex; align-items:center; justify-content:space-between">
          <span style="color:#E6A23C; font-weight:bold">⚠️ 待处理提醒 ({{ reminders.length }})</span>
          <span style="font-size:12px; color:#999">过期及今日待跟进</span>
        </div>
      </template>
      <div v-for="r in reminders" :key="r.id" class="reminder-item">
        <div class="reminder-left">
          <span class="reminder-customer">{{ r.customer_name || '客户#'+r.customer_id }}</span>
          <span class="reminder-content">{{ r.content }}</span>
        </div>
        <div class="reminder-right">
          <span class="reminder-time">{{ r.reminder_at ? r.reminder_at.slice(0,16).replace('T',' ') : '' }}</span>
          <el-button size="small" type="success" @click="handleReminderDone(r.id)">完成</el-button>
        </div>
      </div>
    </el-card>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { getDashboard, getMonthlyStats, getUpcomingReminders, markReminderDone } from '../api'
import api from '../api'
import * as echarts from 'echarts'
import { PieChart, DataLine, TrendCharts, Histogram, Refresh, InfoFilled } from '@element-plus/icons-vue'
import { apiFetch } from '@/utils/api.js'

const stats = ref({})
import { ElMessage } from 'element-plus'
const monthStats = ref({})
const reminders = ref([])
const sourceDist = ref([])
const statusDist = ref([])
const starChartRef = ref()
const statusChartRef = ref()
const sourceChartRef = ref()
const brief = ref({})  // 今日/昨日工作简报
const allNotices = ref([])  // 公告列表
const marqueeNotices = computed(() => allNotices.value.filter(n => n.notice_type === 2 && n.is_visible))
const normalNotices = computed(() => allNotices.value.filter(n => n.notice_type === 1 && n.is_visible))

const COLORS = ['#E91E63', '#F48FB1', '#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399', '#8E24AA', '#00ACC1', '#43A047']

const currentMonth = computed(() => {
  const d = new Date()
  return `${d.getFullYear()}年${d.getMonth() + 1}月`
})

const todayDate = computed(() => {
  const d = new Date()
  return `${d.getMonth()+1}月${d.getDate()}日`
})

const monthStatsItems = computed(() => [
  { label: '新增客户', value: monthStats.value.newCount || 0, color: '#67C23A', icon: '📥', target: 50 },
  { label: '跟进备注', value: monthStats.value.remarkCount || 0, color: '#409EFF', icon: '📝', target: 100 },
  { label: '进件数', value: monthStats.value.caseCount || 0, color: '#E6A23C', icon: '📋', target: 20 },
  { label: '批款数', value: monthStats.value.approveCount || 0, color: '#E91E63', icon: '✅', target: null },
  { label: '收款数', value: monthStats.value.collectionCount || 0, color: '#F56C6C', icon: '💰', target: null },
])

const loadData = async () => {
  try {
    stats.value = await getDashboard()
    const d = new Date()
    monthStats.value = await getMonthlyStats(`${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`)
  } catch (e) {}

  // 加载工作简报
  try {
    brief.value = await apiFetch('/api/dashboard/brief')
  } catch (e) { console.error('brief', e) }

  // 加载来源分布
  try {
    sourceDist.value = await api.get('/stats/source-dist')
  } catch (e) {}

  // 加载状态分布（更详细版本）
  try {
    statusDist.value = await api.get('/stats/status-dist')
  } catch (e) {
    statusDist.value = stats.value.statusDist || []
  }

  // 加载待处理提醒
  try {
    const r = await getUpcomingReminders()
    reminders.value = r.items || []
  } catch (e) {}

  // 加载公告
  try {
    const noticeRes = await apiFetch('/api/notices?visible=1')
    allNotices.value = noticeRes.items || noticeRes || []
  } catch(e) {}

  await nextTick()
  setTimeout(renderCharts, 50)
}

const handleReminderDone = async (rid) => {
  try {
    await markReminderDone(rid)
    reminders.value = reminders.value.filter(r => r.id !== rid)
    ElMessage.success('已标记完成')
  } catch(e) { ElMessage.error('操作失败') }
}

const renderCharts = () => {
  // 星级分布饼图
  if (starChartRef.value && stats.value.starDist?.length) {
    const chart = echarts.getInstanceByDom(starChartRef.value) || echarts.init(starChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'item', formatter: '{b}: {c}人 ({d}%)' },
      legend: { bottom: 0, textStyle: { fontSize: 11 } },
      series: [{
        type: 'pie', radius: ['38%', '68%'],
        data: stats.value.starDist.map((d, i) => ({
          ...d,
          itemStyle: { color: COLORS[i % COLORS.length], borderRadius: 5 }
        })),
        label: { fontSize: 11, color: '#666' },
        emphasis: { label: { fontSize: 14, fontWeight: 'bold' } }
      }]
    })
  }

  // 状态分布柱状图
  const sd = statusDist.value?.length ? statusDist.value : (stats.value.statusDist || [])
  if (statusChartRef.value && sd.length) {
    const chart = echarts.getInstanceByDom(statusChartRef.value) || echarts.init(statusChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      grid: { left: 10, right: 10, bottom: 50, top: 10, containLabel: true },
      xAxis: { type: 'category', data: sd.map(d => d.name), axisLabel: { rotate: 35, fontSize: 10 } },
      yAxis: { type: 'value', minInterval: 1 },
      series: [{
        type: 'bar',
        data: sd.map((d, i) => ({
          value: d.value,
          itemStyle: { color: COLORS[i % COLORS.length], borderRadius: [4, 4, 0, 0] }
        })),
        barWidth: '55%'
      }]
    })
  }

  // 来源分布饼图
  if (sourceChartRef.value && sourceDist.value?.length) {
    const chart = echarts.getInstanceByDom(sourceChartRef.value) || echarts.init(sourceChartRef.value)
    const sortedDist = [...sourceDist.value].sort((a, b) => b.value - a.value)
    chart.setOption({
      tooltip: { trigger: 'item', formatter: '{b}: {c}人 ({d}%)' },
      legend: { bottom: 0, type: 'scroll', textStyle: { fontSize: 10 } },
      series: [{
        type: 'pie', radius: ['30%', '65%'],
        data: sortedDist.map((d, i) => ({
          ...d,
          itemStyle: { color: COLORS[i % COLORS.length], borderRadius: 5 }
        })),
        label: { fontSize: 11 },
        labelLine: { length: 8, length2: 6 },
        emphasis: { label: { fontSize: 13, fontWeight: 'bold' } }
      }]
    })
  }
}

onMounted(loadData)
</script>

<style scoped>
.kpi-card {
  background: white;
  border-radius: 10px;
  padding: 16px 14px;
  border-top: 4px solid;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.07);
  text-align: center;
  transition: transform 0.2s, box-shadow 0.2s;
}
.kpi-card:hover { transform: translateY(-2px); box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12); }
.kpi-icon { width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 16px; margin: 0 auto 8px; }
.kpi-num { font-size: 34px; font-weight: bold; line-height: 1.1; }
.kpi-label { color: #888; font-size: 12px; margin-top: 5px; }

.chart-card { border-radius: 10px; overflow: hidden; position: relative; }
.card-header-title { display: flex; align-items: center; gap: 6px; font-weight: 600; font-size: 14px; color: #333; }

.empty-chart {
  position: absolute; inset: 0;
  display: flex; align-items: center; justify-content: center;
  background: rgba(255, 255, 255, 0.7);
}

.month-stat { text-align: center; padding: 12px 6px; border-radius: 8px; background: #fafafa; }
.ms-icon { font-size: 20px; margin-bottom: 4px; }
.ms-num { font-size: 26px; font-weight: bold; line-height: 1.2; }
.ms-label { font-size: 11px; color: #888; margin-top: 3px; }

.reminder-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
  gap: 12px;
}
.reminder-item:last-child { border-bottom: none; }
.reminder-left { flex: 1; display: flex; flex-direction: column; gap: 2px; }
.reminder-customer { font-size: 13px; font-weight: bold; color: #303133; }
.reminder-content { font-size: 12px; color: #606266; }
.reminder-right { display: flex; align-items: center; gap: 8px; flex-shrink: 0; }
.reminder-time { font-size: 12px; color: #999; white-space: nowrap; }

/* 今日/昨日简报 */
.brief-grid {
  display: grid; grid-template-columns: repeat(3, 1fr);
  gap: 8px; margin-bottom: 10px;
}
.brief-cell {
  text-align: center; padding: 10px 6px; background: #fafafa;
  border-radius: 8px; border: 1px solid #f0f0f0;
}
.brief-label { font-size: 11px; color: #888; margin-bottom: 4px; }
.brief-val { font-size: 22px; font-weight: 700; color: #333; line-height: 1.1; }
.review-bar { font-size: 12px; color: #666; padding: 6px 0 0; border-top: 1px solid #f0f0f0; margin-top: 4px; }
.month-progress { display:flex; align-items:center; gap:8px; padding-top:10px; border-top:1px solid #f0f0f0; margin-top:4px; }

/* 公告区域 */
.notice-marquee {
  display: flex;
  align-items: center;
  background: linear-gradient(90deg, #FFF0F6 0%, #fff 100%);
  border: 1px solid #F48FB1;
  border-radius: 8px;
  padding: 8px 12px;
  margin-bottom: 12px;
  gap: 10px;
  overflow: hidden;
}
.notice-tag {
  white-space: nowrap;
  background: #E91E63;
  color: white;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
  flex-shrink: 0;
}
.marquee-inner {
  display: flex;
  gap: 8px;
  white-space: nowrap;
  animation: marquee 20s linear infinite;
}
.marquee-text { font-size: 13px; color: #C2185B; }
.marquee-sep { margin: 0 8px; color: #F48FB1; }
@keyframes marquee {
  0% { transform: translateX(0); }
  100% { transform: translateX(-50%); }
}

.notice-card {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #FFFDE7;
  border: 1px solid #FFE082;
  border-radius: 8px;
  padding: 10px 14px;
  margin-bottom: 8px;
  font-size: 13px;
}
.notice-card .el-icon { color: #E6A23C; flex-shrink: 0; }
.notice-title { font-weight: 600; color: #333; white-space: nowrap; }
.notice-content { color: #666; flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.notice-time { color: #aaa; font-size: 11px; white-space: nowrap; flex-shrink: 0; }
</style>
