<template>
  <div>
    <div class="page-header">
      <h3>业绩排行榜</h3>
      <div style="display:flex; align-items:center; gap:8px">
        <el-radio-group v-model="period" size="small" @change="loadData">
          <el-radio-button value="today">今日</el-radio-button>
          <el-radio-button value="week">本周</el-radio-button>
          <el-radio-button value="month">本月</el-radio-button>
        </el-radio-group>
        <el-button size="small" @click="loadData"><Refresh /> 刷新</el-button>
      </div>
    </div>

    <div style="padding:16px">
      <!-- 时间范围提示 -->
      <div style="font-size:12px; color:#888; margin-bottom:12px">
        统计周期：{{ rankingData.start }} 至今 &nbsp;|&nbsp; 共 {{ rankingData.list?.length || 0 }} 位顾问
      </div>

      <!-- 前三名表彰卡 -->
      <el-row :gutter="16" style="margin-bottom:20px" v-if="rankingData.list?.length >= 3">
        <!-- 第二名 -->
        <el-col :span="8">
          <div class="podium-card rank-2">
            <div class="podium-rank">2</div>
            <div class="podium-avatar" style="background:linear-gradient(135deg,#aaa,#ddd)">
              {{ rankingData.list[1]?.real_name?.charAt(0) }}
            </div>
            <div class="podium-name">{{ rankingData.list[1]?.real_name }}</div>
            <div class="podium-role">{{ rankingData.list[1]?.role_text }}</div>
            <div class="podium-stats">
              <span class="stat-item">备注 <b>{{ rankingData.list[1]?.remark_count }}</b></span>
              <span class="stat-item">进件 <b>{{ rankingData.list[1]?.loan_count }}</b></span>
            </div>
          </div>
        </el-col>
        <!-- 第一名 -->
        <el-col :span="8">
          <div class="podium-card rank-1">
            <div class="podium-crown">👑</div>
            <div class="podium-rank">1</div>
            <div class="podium-avatar" style="background:linear-gradient(135deg,#FFD700,#FFA500)">
              {{ rankingData.list[0]?.real_name?.charAt(0) }}
            </div>
            <div class="podium-name">{{ rankingData.list[0]?.real_name }}</div>
            <div class="podium-role">{{ rankingData.list[0]?.role_text }}</div>
            <div class="podium-stats">
              <span class="stat-item">备注 <b>{{ rankingData.list[0]?.remark_count }}</b></span>
              <span class="stat-item">进件 <b>{{ rankingData.list[0]?.loan_count }}</b></span>
            </div>
          </div>
        </el-col>
        <!-- 第三名 -->
        <el-col :span="8">
          <div class="podium-card rank-3">
            <div class="podium-rank">3</div>
            <div class="podium-avatar" style="background:linear-gradient(135deg,#cd7f32,#e8a96e)">
              {{ rankingData.list[2]?.real_name?.charAt(0) }}
            </div>
            <div class="podium-name">{{ rankingData.list[2]?.real_name }}</div>
            <div class="podium-role">{{ rankingData.list[2]?.role_text }}</div>
            <div class="podium-stats">
              <span class="stat-item">备注 <b>{{ rankingData.list[2]?.remark_count }}</b></span>
              <span class="stat-item">进件 <b>{{ rankingData.list[2]?.loan_count }}</b></span>
            </div>
          </div>
        </el-col>
      </el-row>

      <!-- 完整排行表 -->
      <el-card>
        <template #header>
          <div class="card-header-title">
            <el-icon color="#E91E63"><Trophy /></el-icon>
            完整排行
          </div>
        </template>
        <el-table :data="rankingData.list || []" v-loading="loading" stripe>
          <el-table-column label="排名" width="70" align="center">
            <template #default="{ row }">
              <div :class="['rank-badge', `rank-badge-${row.rank}`]">{{ row.rank }}</div>
            </template>
          </el-table-column>
          <el-table-column label="顾问" min-width="120">
            <template #default="{ row }">
              <div style="display:flex; align-items:center; gap:8px">
                <div class="advisor-avatar">{{ row.real_name?.charAt(0) }}</div>
                <div>
                  <div style="font-weight:500">{{ row.real_name }}</div>
                  <div style="font-size:11px; color:#888">{{ row.role_text }}</div>
                </div>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="跟进备注数" prop="remark_count" sortable width="130" align="center">
            <template #default="{ row }">
              <el-tag type="primary" size="small">{{ row.remark_count }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="进件数" prop="loan_count" sortable width="100" align="center">
            <template #default="{ row }">
              <el-tag type="warning" size="small">{{ row.loan_count }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="批款金额" prop="approve_amount" sortable width="120" align="center">
            <template #default="{ row }">
              <span style="color:#E91E63; font-weight:500">{{ row.approve_amount ? row.approve_amount.toFixed(1) + '万' : '-' }}</span>
            </template>
          </el-table-column>
          <el-table-column label="新增客户" prop="new_count" sortable width="100" align="center">
            <template #default="{ row }">
              {{ row.new_count }}
            </template>
          </el-table-column>
          <el-table-column label="跟进进度" min-width="160">
            <template #default="{ row }">
              <div v-if="maxRemark > 0">
                <el-progress
                  :percentage="Math.round(row.remark_count / maxRemark * 100)"
                  :color="row.rank === 1 ? '#E91E63' : row.rank <= 3 ? '#E6A23C' : '#409EFF'"
                  :stroke-width="8"
                />
              </div>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Refresh, Trophy } from '@element-plus/icons-vue'
import { apiFetch } from '@/utils/api.js'

const loading = ref(false)
const period = ref('month')
const rankingData = ref({ list: [], start: '' })

const maxRemark = computed(() => {
  if (!rankingData.value.list?.length) return 0
  return Math.max(...rankingData.value.list.map(r => r.remark_count))
})

const loadData = async () => {
  loading.value = true
  try {
    const data = await apiFetch(`/api/stats/ranking?period=${period.value}`)
    rankingData.value = data
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

onMounted(loadData)
</script>

<style scoped>
.page-header { display:flex; justify-content:space-between; align-items:center; padding:16px 16px 0; }
.page-header h3 { margin:0; font-size:16px; color:#333; font-weight:600; }

.podium-card {
  text-align: center;
  padding: 20px 16px;
  border-radius: 12px;
  background: white;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
  position: relative;
  transition: transform 0.2s;
}
.podium-card:hover { transform: translateY(-2px); }
.rank-1 { border-top: 4px solid #FFD700; }
.rank-2 { border-top: 4px solid #aaa; }
.rank-3 { border-top: 4px solid #cd7f32; }
.podium-crown { font-size:24px; position:absolute; top:-16px; left:50%; transform:translateX(-50%); }
.podium-rank {
  font-size: 24px; font-weight: 800; color: #E91E63; margin-bottom: 8px;
}
.rank-2 .podium-rank { color: #aaa; }
.rank-3 .podium-rank { color: #cd7f32; }
.podium-avatar {
  width: 52px; height: 52px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  color: white; font-size: 20px; font-weight: bold;
  margin: 0 auto 10px;
}
.podium-name { font-size: 15px; font-weight: 600; color: #333; margin-bottom: 4px; }
.podium-role { font-size: 12px; color: #888; margin-bottom: 10px; }
.podium-stats { display: flex; justify-content: center; gap: 12px; }
.stat-item { font-size: 12px; color: #666; }
.stat-item b { color: #E91E63; font-size: 15px; }

.rank-badge {
  width: 28px; height: 28px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-weight: bold; font-size: 13px; margin: 0 auto;
  background: #f0f0f0; color: #666;
}
.rank-badge-1 { background: #FFD700; color: white; }
.rank-badge-2 { background: #aaa; color: white; }
.rank-badge-3 { background: #cd7f32; color: white; }

.advisor-avatar {
  width: 32px; height: 32px; border-radius: 50%;
  background: linear-gradient(135deg, #E91E63, #F48FB1);
  color: white; font-size: 14px; font-weight: bold;
  display: flex; align-items: center; justify-content: center;
}

.card-header-title { display: flex; align-items: center; gap: 6px; font-weight: 600; }
</style>
