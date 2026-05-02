<template>
  <div>
    <div class="page-header">
      <h3>绩效目标</h3>
      <div>
        <el-select v-model="currentMonth" style="width:140px" @change="loadData">
          <el-option
            v-for="m in monthOptions"
            :key="m.value"
            :label="m.label"
            :value="m.value"
          />
        </el-select>
      </div>
    </div>

    <!-- 我的目标 -->
    <el-card style="margin:16px 0">
      <template #header>
        <div style="display:flex; align-items:center; justify-content:space-between">
          <span style="font-weight:600">我的绩效目标</span>
          <el-button size="small" type="primary" @click="addTargetVisible = true">
            <el-icon><Plus /></el-icon> 添加目标
          </el-button>
        </div>
      </template>

      <el-table :data="targets" v-loading="loading" size="small" :stripe="true">
        <el-table-column label="目标类型" prop="target_type" width="120">
          <template #default="{row}">
            <el-tag size="small" type="danger">{{ targetTypeMap[row.target_type] || row.target_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="目标值" prop="target_value" width="100">
          <template #default="{row}">
            <span style="font-weight:bold; color:#E91E63">{{ row.target_value }}</span>
          </template>
        </el-table-column>
        <el-table-column label="已完成" prop="completed" width="100">
          <template #default="{row}">
            <span style="color:#67C23A; font-weight:bold">{{ row.completed || 0 }}</span>
          </template>
        </el-table-column>
        <el-table-column label="完成率">
          <template #default="{row}">
            <div style="display:flex; align-items:center; gap:8px">
              <el-progress
                :percentage="calcPercent(row)"
                :color="progressColor(calcPercent(row))"
                style="flex:1"
              />
              <span style="font-size:12px; color:#888; min-width:40px">{{ calcPercent(row) }}%</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="剩余缺口">
          <template #default="{row}">
            <span :style="{ color: row.target_value - (row.completed || 0) > 0 ? '#F56C6C' : '#67C23A', fontWeight: 'bold' }">
              {{ Math.max(0, row.target_value - (row.completed || 0)) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="周期" prop="start_date" width="200">
          <template #default="{row}">
            {{ fmtDate(row.start_date) }} ~ {{ fmtDate(row.end_date) }}
          </template>
        </el-table-column>
      </el-table>

      <!-- 进度甘特图 -->
      <div v-if="targets.length" style="margin-top:20px">
        <div style="font-weight:600; margin-bottom:12px; font-size:13px; color:#666">进度概览</div>
        <div v-for="t in targets" :key="t.id" class="gantt-row">
          <div class="gantt-label">{{ targetTypeMap[t.target_type] || t.target_type }}</div>
          <div class="gantt-bar-wrap">
            <div class="gantt-bar" :style="{ width: calcPercent(t) + '%', background: progressColor(calcPercent(t)) }">
              <span v-if="calcPercent(t) > 15">{{ calcPercent(t) }}%</span>
            </div>
          </div>
          <div class="gantt-num">{{ t.completed || 0 }}/{{ t.target_value }}</div>
        </div>
      </div>
    </el-card>

    <!-- 团队目标（主管可见） -->
    <el-card v-if="isManager">
      <template #header><span style="font-weight:600">团队绩效</span></template>
      <el-table :data="teamTargets" v-loading="loading2" size="small" :stripe="true">
        <el-table-column label="顾问" prop="advisor_name" width="100" />
        <el-table-column label="目标类型" width="120">
          <template #default="{row}">{{ targetTypeMap[row.target_type] || row.target_type }}</template>
        </el-table-column>
        <el-table-column label="目标" prop="target_value" width="80" />
        <el-table-column label="完成" prop="completed" width="80" />
        <el-table-column label="完成率">
          <template #default="{row}">
            <el-progress :percentage="calcPercent(row)" :color="progressColor(calcPercent(row))" style="width:120px" />
          </template>
        </el-table-column>
        <el-table-column label="缺口">
          <template #default="{row}">
            <span :style="{ color: row.target_value - (row.completed || 0) > 0 ? '#F56C6C' : '#67C23A' }">
              {{ Math.max(0, row.target_value - (row.completed || 0)) }}
            </span>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 添加目标弹窗 -->
    <el-dialog v-model="addTargetVisible" title="添加绩效目标" width="450px">
      <el-form :model="targetForm" label-width="100px">
        <el-form-item label="目标类型">
          <el-select v-model="targetForm.target_type" style="width:100%">
            <el-option label="进件数" value="进件数" />
            <el-option label="放款额(万)" value="放款额" />
            <el-option label="新增客户" value="新增客户" />
            <el-option label="跟进次数" value="跟进次数" />
          </el-select>
        </el-form-item>
        <el-form-item label="目标值">
          <el-input-number v-model="targetForm.target_value" :min="1" style="width:100%" />
        </el-form-item>
        <el-form-item label="开始日期">
          <el-date-picker v-model="targetForm.start_date" type="date" style="width:100%" />
        </el-form-item>
        <el-form-item label="结束日期">
          <el-date-picker v-model="targetForm.end_date" type="date" style="width:100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addTargetVisible = false">取消</el-button>
        <el-button type="primary" @click="handleAddTarget">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'

const user = computed(() => JSON.parse(localStorage.getItem('user') || '{}'))
const isManager = computed(() => user.value.role >= 2)

const loading = ref(false)
const loading2 = ref(false)
const targets = ref([])
const teamTargets = ref([])
const addTargetVisible = ref(false)

const currentMonth = ref(new Date().toISOString().substring(0, 7))

const monthOptions = Array.from({ length: 12 }, (_, i) => {
  const d = new Date()
  d.setMonth(d.getMonth() - i)
  return { value: d.toISOString().substring(0, 7), label: `${d.getFullYear()}年${d.getMonth()+1}月` }
})

const targetTypeMap = {
  '进件数': '进件数', '放款额': '放款额(万)',
  '新增客户': '新增客户', '跟进次数': '跟进次数'
}

const targetForm = reactive({
  target_type: '进件数', target_value: 10,
  start_date: new Date().toISOString().substring(0, 10),
  end_date: new Date(Date.now() + 86400000 * 30).toISOString().substring(0, 10)
})

const calcPercent = (t) => {
  const v = t.target_value || 1
  const c = t.completed || 0
  return Math.min(100, Math.round(c / v * 100))
}

const progressColor = (p) => {
  if (p >= 100) return '#67C23A'
  if (p >= 70) return '#409EFF'
  if (p >= 40) return '#E6A23C'
  return '#F56C6C'
}

const fmtDate = (d) => d ? d.substring(0, 10) : '—'

const loadData = async () => {
  loading.value = true
  try {
    const res = await fetch(`/api/stats/performance?month=${currentMonth.value}`, {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    })
    if (res.ok) {
      const d = await res.json()
      targets.value = d.targets || generateMockTargets()
    } else {
      targets.value = generateMockTargets()
    }
  } catch(e) {
    targets.value = generateMockTargets()
  } finally {
    loading.value = false
  }
}

const generateMockTargets = () => [
  { id: 1, target_type: '进件数', target_value: 20, completed: 12, start_date: currentMonth.value + '-01', end_date: currentMonth.value + '-30' },
  { id: 2, target_type: '新增客户', target_value: 50, completed: 38, start_date: currentMonth.value + '-01', end_date: currentMonth.value + '-30' },
  { id: 3, target_type: '跟进次数', target_value: 100, completed: 67, start_date: currentMonth.value + '-01', end_date: currentMonth.value + '-30' },
  { id: 4, target_type: '放款额', target_value: 200, completed: 85, start_date: currentMonth.value + '-01', end_date: currentMonth.value + '-30' }
]

const handleAddTarget = async () => {
  ElMessage.success('目标已保存（演示模式）')
  addTargetVisible.value = false
}

onMounted(loadData)
</script>

<style scoped>
.gantt-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 10px;
}
.gantt-label {
  width: 80px;
  font-size: 12px;
  color: #666;
  flex-shrink: 0;
  text-align: right;
}
.gantt-bar-wrap {
  flex: 1;
  height: 22px;
  background: #F5F5F5;
  border-radius: 4px;
  overflow: hidden;
}
.gantt-bar {
  height: 100%;
  border-radius: 4px;
  display: flex;
  align-items: center;
  padding: 0 8px;
  color: white;
  font-size: 11px;
  font-weight: bold;
  transition: width 0.5s;
  min-width: 30px;
}
.gantt-num {
  width: 60px;
  font-size: 12px;
  color: #888;
  text-align: right;
  flex-shrink: 0;
}
</style>
