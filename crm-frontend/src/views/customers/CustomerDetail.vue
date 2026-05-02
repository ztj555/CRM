<template>
  <div class="cd-page" v-loading="loading">

    <!-- ===== 顶部操作栏 ===== -->
    <div class="cd-topbar">
      <div class="cd-topbar-left">
        <span class="cd-title">
          <span class="cd-id">ID: {{ detail.id }}</span>
          <span class="cd-name">{{ detail.name || '未知客户' }}</span>
        </span>
        <el-tag v-if="detail.is_important" type="danger" size="small" effect="plain">重要</el-tag>
        <el-tag v-if="detail.is_locked" type="warning" size="small" effect="plain">🔒 锁定</el-tag>
        <el-tag v-if="detail.is_blacklisted" type="info" size="small" effect="plain">🚫 黑名单</el-tag>
        <el-tag v-if="detail.source" size="small" effect="plain">{{ detail.source }}</el-tag>
        <el-tag v-if="detail.city" size="small" effect="plain">{{ detail.city }}</el-tag>
      </div>
      <div class="cd-topbar-right">
        <span class="cd-label">星级</span>
        <el-rate v-model="detail.star_level" :max="6" size="small" void-color="#ccc" @change="saveField('star_level')" style="margin-right:8px" />
        <span class="cd-label">状态</span>
        <el-select v-model="detail.status" size="small" style="width:120px;margin-right:6px" @change="saveField('status')">
          <el-option v-for="(n,v) in options.statusMap" :key="v" :label="n" :value="Number(v)" />
        </el-select>
        <el-button size="small" :type="detail.is_important ? 'danger' : 'default'" plain @click="toggleImportant">
          {{ detail.is_important ? '取消重要' : '标为重要' }}
        </el-button>
        <el-button size="small" :type="detail.is_locked ? 'warning' : 'default'" plain @click="toggleLock">
          {{ detail.is_locked ? '解锁' : '锁定' }}
        </el-button>
        <el-button size="small" type="default" plain @click="openEdit">编辑</el-button>
        <el-button size="small" type="warning" plain @click="handleToPool">加入公共池</el-button>
        <el-button size="small" type="success" plain @click="handleToMustFollow">加入必跟进</el-button>
        <el-button size="small" :type="detail.is_blacklisted ? 'info' : 'danger'" plain @click="handleBlacklist">
          {{ detail.is_blacklisted ? '移除黑名单' : '拉黑' }}
        </el-button>
      </div>
    </div>

    <!-- ===== 主体：左右分栏 ===== -->
    <div class="cd-body">

      <!-- ---- 左侧：信息区（75%） ---- -->
      <div class="cd-main">

        <!-- 信息Tab -->
        <div class="cd-tab-bar">
          <div
            v-for="t in infoTabs" :key="t.key"
            class="cd-tab"
            :class="{ active: activeInfoTab === t.key }"
            @click="activeInfoTab = t.key"
          >{{ t.label }}</div>
        </div>

        <!-- 信息内容：密集网格布局 -->
        <div class="cd-info-content">

          <!-- 基本信息 -->
          <div v-show="activeInfoTab === 'basic'" class="cd-info-grid">
            <div class="grid-item"><span class="grid-label">姓名</span><span class="grid-value">{{ detail.name || '—' }}</span></div>
            <div class="grid-item"><span class="grid-label">手机</span><span class="grid-value">{{ detail.phone || '—' }}</span></div>
            <div class="grid-item"><span class="grid-label">性别</span><span class="grid-value">{{ {0:'未知',1:'男',2:'女'}[detail.gender] || '—' }}</span></div>
            <div class="grid-item"><span class="grid-label">城市</span><span class="grid-value">{{ detail.city || '—' }}</span></div>
            <div class="grid-item"><span class="grid-label">年龄</span><span class="grid-value">{{ detail.age ? detail.age + '岁' : '—' }}</span></div>
            <div class="grid-item"><span class="grid-label">申请额度</span><span class="grid-value">{{ detail.apply_amount ? detail.apply_amount + '万' : '—' }}</span></div>
            <div class="grid-item"><span class="grid-label">贷款类型</span><span class="grid-value">{{ options.loanTypeMap[detail.loan_type] || '—' }}</span></div>
            <div class="grid-item"><span class="grid-label">来源</span><span class="grid-value">{{ detail.source || '—' }}</span></div>
            <div class="grid-item"><span class="grid-label">申请时间</span><span class="grid-value">{{ fmt(detail.created_at) }}</span></div>
            <div class="grid-item"><span class="grid-label">归属顾问</span><span class="grid-value">{{ detail.advisor_name || '—' }}</span></div>
          </div>

          <!-- 身份信息 -->
          <div v-show="activeInfoTab === 'identity'" class="cd-info-grid">
            <div class="grid-item"><span class="grid-label">户籍</span><span class="grid-value">{{ detailQ('huji_city') || '—' }}</span></div>
            <div class="grid-item"><span class="grid-label">婚姻</span><span class="grid-value">{{ detailQ('marriage') || '—' }}</span></div>
            <div class="grid-item"><span class="grid-label">学历</span><span class="grid-value">{{ detailQ('education') || '—' }}</span></div>
            <div class="grid-item"><span class="grid-label">职业</span><span class="grid-value">{{ detailQ('occupation') || '—' }}</span></div>
            <div class="grid-item"><span class="grid-label">月收入(元)</span><span class="grid-value">{{ detailQ('salary_amount') || '—' }}</span></div>
            <div class="grid-item"><span class="grid-label">收入方式</span><span class="grid-value">{{ detailQ('income_type') || '—' }}</span></div>
          </div>

          <!-- 房产信息 -->
          <div v-show="activeInfoTab === 'estate'" class="cd-info-grid">
            <div class="grid-item"><span class="grid-label">房产状况</span><span class="grid-value" :class="hasEstate ? 'val-yes' : 'val-no'">{{ hasEstate ? '有' : '无' }}</span></div>
            <template v-if="hasEstate">
              <div class="grid-item"><span class="grid-label">房屋类型</span><span class="grid-value">{{ detailQ('real_estate.type') || '—' }}</span></div>
              <div class="grid-item"><span class="grid-label">房屋面积</span><span class="grid-value">{{ detailQ('real_estate.area') ? detailQ('real_estate.area') + 'm²' : '—' }}</span></div>
              <div class="grid-item"><span class="grid-label">市场估值</span><span class="grid-value">{{ detailQ('real_estate.market_value') ? detailQ('real_estate.market_value') + '万' : '—' }}</span></div>
              <div class="grid-item"><span class="grid-label">抵押状态</span><span class="grid-value">{{ detailQ('real_estate.mortgage_status') || '—' }}</span></div>
              <div class="grid-item"><span class="grid-label">房屋性质</span><span class="grid-value">{{ detailQ('real_estate.property_type') || '—' }}</span></div>
              <div class="grid-item" style="grid-column:1/-1"><span class="grid-label">房产地址</span><span class="grid-value">{{ detailQ('real_estate.address') || '—' }}</span></div>
            </template>
          </div>

          <!-- 车产信息 -->
          <div v-show="activeInfoTab === 'vehicle'" class="cd-info-grid">
            <div class="grid-item"><span class="grid-label">车产状况</span><span class="grid-value" :class="hasVehicle ? 'val-yes' : 'val-no'">{{ hasVehicle ? '有' : '无' }}</span></div>
            <template v-if="hasVehicle">
              <div class="grid-item"><span class="grid-label">车辆类型</span><span class="grid-value">{{ detailQ('vehicle.type') || '—' }}</span></div>
              <div class="grid-item"><span class="grid-label">品牌型号</span><span class="grid-value">{{ detailQ('vehicle.brand') || '—' }}</span></div>
              <div class="grid-item"><span class="grid-label">使用年限</span><span class="grid-value">{{ detailQ('vehicle.years') ? detailQ('vehicle.years') + '年' : '—' }}</span></div>
              <div class="grid-item"><span class="grid-label">车辆估值</span><span class="grid-value">{{ detailQ('vehicle.value') ? detailQ('vehicle.value') + '万' : '—' }}</span></div>
              <div class="grid-item"><span class="grid-label">按揭状态</span><span class="grid-value">{{ detailQ('vehicle.payment_type') || '—' }}</span></div>
            </template>
          </div>

          <!-- 保单社保公积金 -->
          <div v-show="activeInfoTab === 'insurance'" class="cd-info-grid">
            <div class="grid-item"><span class="grid-label">保单</span><span class="grid-value" :class="hasInsurance ? 'val-yes' : 'val-no'">{{ hasInsurance ? '有' : '无' }}</span></div>
            <template v-if="hasInsurance">
              <div class="grid-item"><span class="grid-label">保险公司</span><span class="grid-value">{{ detailQ('insurance.company') || '—' }}</span></div>
              <div class="grid-item"><span class="grid-label">保单类型</span><span class="grid-value">{{ detailQ('insurance.type') || '—' }}</span></div>
              <div class="grid-item"><span class="grid-label">年缴保费</span><span class="grid-value">{{ detailQ('insurance.annual_premium') ? detailQ('insurance.annual_premium') + '元' : '—' }}</span></div>
              <div class="grid-item"><span class="grid-label">已缴年限</span><span class="grid-value">{{ detailQ('insurance.paid_years') ? detailQ('insurance.paid_years') + '年' : '—' }}</span></div>
              <div class="grid-item"><span class="grid-label">保单现值</span><span class="grid-value">{{ detailQ('insurance.cash_value') ? detailQ('insurance.cash_value') + '万' : '—' }}</span></div>
            </template>
            <div class="grid-item"><span class="grid-label">社保</span><span class="grid-value" :class="detailQ('social_security') ? 'val-yes' : 'val-no'">{{ detailQ('social_security') ? '有' : '无' }}</span></div>
            <div class="grid-item"><span class="grid-label">公积金</span><span class="grid-value" :class="detailQ('housing_fund') ? 'val-yes' : 'val-no'">{{ detailQ('housing_fund') ? '有' : '无' }}</span></div>
          </div>

          <!-- 信用信息 -->
          <div v-show="activeInfoTab === 'credit'" class="cd-info-grid">
            <div class="grid-item"><span class="grid-label">征信等级</span><span class="grid-value">{{ detailQ('credit.credit_grade') || '—' }}</span></div>
            <div class="grid-item"><span class="grid-label">信用卡额度</span><span class="grid-value">{{ detailQ('credit.credit_limit') ? detailQ('credit.credit_limit') + '万' : '—' }}</span></div>
            <div class="grid-item"><span class="grid-label">近6月查询</span><span class="grid-value">{{ detailQ('credit.query_count') || '—' }}</span></div>
            <div class="grid-item"><span class="grid-label">微粒贷额度</span><span class="grid-value">{{ detailQ('credit.weili_amount') || '—' }}</span></div>
            <div class="grid-item"><span class="grid-label">网贷平台数</span><span class="grid-value">{{ detailQ('credit.online_loan_count') || '—' }}</span></div>
            <div class="grid-item"><span class="grid-label">是否有逾期</span><span class="grid-value">{{ {0:'无',1:'偶尔',2:'较多'}[detailQ('credit.has_overdue')] || '—' }}</span></div>
          </div>

          <!-- 负债情况 -->
          <div v-show="activeInfoTab === 'liabilities'" class="cd-info-grid">
            <div class="grid-item"><span class="grid-label">信用卡已用</span><span class="grid-value">{{ detailQ('liabilities.credit_card_used') ? detailQ('liabilities.credit_card_used') + '万' : '无' }}</span></div>
            <div class="grid-item"><span class="grid-label">房贷月还款</span><span class="grid-value">{{ detailQ('liabilities.mortgage_monthly') ? detailQ('liabilities.mortgage_monthly') + '元/月' : '无' }}</span></div>
            <div class="grid-item"><span class="grid-label">车贷月还款</span><span class="grid-value">{{ detailQ('liabilities.car_loan_monthly') ? detailQ('liabilities.car_loan_monthly') + '元/月' : '无' }}</span></div>
            <div class="grid-item"><span class="grid-label">网贷月还款</span><span class="grid-value">{{ detailQ('liabilities.online_loan_monthly') ? detailQ('liabilities.online_loan_monthly') + '元/月' : '无' }}</span></div>
            <div class="grid-item"><span class="grid-label">其他月还款</span><span class="grid-value">{{ detailQ('liabilities.other_monthly') ? detailQ('liabilities.other_monthly') + '元/月' : '无' }}</span></div>
            <div class="grid-item grid-item--total"><span class="grid-label">月负债合计</span><span class="grid-value val-total">{{ totalLiabilities }}元/月</span></div>
          </div>

          <!-- 需求信息 -->
          <div v-show="activeInfoTab === 'needs'" class="cd-info-grid">
            <div class="grid-item"><span class="grid-label">贷款用途</span><span class="grid-value">{{ detailQ('needs.purpose') || '—' }}</span></div>
            <div class="grid-item"><span class="grid-label">期望期限</span><span class="grid-value">{{ detailQ('needs.expect_term') || '—' }}</span></div>
            <div class="grid-item"><span class="grid-label">紧迫程度</span><span class="grid-value">{{ detailQ('needs.urgency') || '—' }}</span></div>
            <div class="grid-item" style="grid-column:1/-1"><span class="grid-label">其他说明</span><span class="grid-value">{{ detailQ('needs.description') || '—' }}</span></div>
          </div>

          <!-- 全部信息 -->
          <div v-show="activeInfoTab === 'all'" class="cd-info-grid">
            <div class="grid-section-title">基本信息</div>
            <div class="grid-item"><span class="grid-label">姓名</span><span class="grid-value">{{ detail.name || '—' }}</span></div>
            <div class="grid-item"><span class="grid-label">手机</span><span class="grid-value">{{ detail.phone || '—' }}</span></div>
            <div class="grid-item"><span class="grid-label">性别/年龄</span><span class="grid-value">{{ {0:'未知',1:'男',2:'女'}[detail.gender] }} / {{ detail.age ? detail.age + '岁' : '—' }}</span></div>
            <div class="grid-item"><span class="grid-label">城市</span><span class="grid-value">{{ detail.city || '—' }}</span></div>
            <div class="grid-item"><span class="grid-label">申请额度</span><span class="grid-value">{{ detail.apply_amount ? detail.apply_amount + '万' : '—' }}</span></div>
            <div class="grid-item"><span class="grid-label">来源</span><span class="grid-value">{{ detail.source || '—' }}</span></div>
            <div class="grid-item"><span class="grid-label">申请时间</span><span class="grid-value">{{ fmt(detail.created_at) }}</span></div>
            <div class="grid-section-title">资产资质</div>
            <div class="grid-item"><span class="grid-label">房产</span><span class="grid-value" :class="hasEstate ? 'val-yes' : 'val-no'">{{ hasEstate ? '有' : '无' }}</span></div>
            <div class="grid-item"><span class="grid-label">车产</span><span class="grid-value" :class="hasVehicle ? 'val-yes' : 'val-no'">{{ hasVehicle ? '有' : '无' }}</span></div>
            <div class="grid-item"><span class="grid-label">保单</span><span class="grid-value" :class="hasInsurance ? 'val-yes' : 'val-no'">{{ hasInsurance ? '有' : '无' }}</span></div>
            <div class="grid-item"><span class="grid-label">社保/公积金</span><span class="grid-value">{{ detailQ('social_security') ? '有' : '无' }} / {{ detailQ('housing_fund') ? '有' : '无' }}</span></div>
            <div class="grid-item"><span class="grid-label">征信等级</span><span class="grid-value">{{ detailQ('credit.credit_grade') || '—' }}</span></div>
            <div class="grid-item"><span class="grid-label">信用卡额度</span><span class="grid-value">{{ detailQ('credit.credit_limit') ? detailQ('credit.credit_limit') + '万' : '—' }}</span></div>
            <div class="grid-item grid-item--total"><span class="grid-label">月负债合计</span><span class="grid-value val-total">{{ totalLiabilities }}元/月</span></div>
            <div class="grid-section-title">贷款需求</div>
            <div class="grid-item"><span class="grid-label">用途</span><span class="grid-value">{{ detailQ('needs.purpose') || '—' }}</span></div>
            <div class="grid-item"><span class="grid-label">紧迫度</span><span class="grid-value">{{ detailQ('needs.urgency') || '—' }}</span></div>
          </div>

        </div>
      </div>

      <!-- ---- 右侧：操作面板（25%） ---- -->
      <div class="cd-sidebar">

        <!-- 状态 -->
        <div class="sd-section sd-status">
          <div class="sd-section-title">当前状态</div>
          <div class="sd-status-row">
            <el-tag size="small" type="default">{{ options.statusMap[detail.status] || '未知' }}</el-tag>
            <span class="sd-phone">{{ detail.phone || '—' }}</span>
          </div>
        </div>

        <!-- 资质摘要 -->
        <div class="sd-section">
          <div class="sd-section-title">资质摘要</div>
          <el-input v-model="quals.customer_ability_text" size="small" placeholder="如：有房/征信A级/有公积金" @blur="saveQuals" />
        </div>

        <!-- 快捷备注 -->
        <div class="sd-section">
          <div class="sd-section-title">快捷备注</div>
          <div class="sd-quick-btns">
            <el-tag
              v-for="r in quickRemarks"
              :key="r"
              class="sd-quick-tag"
              :disable-transitions="false"
              @click="applyQuickRemark(r)"
            >{{ r }}</el-tag>
          </div>
        </div>

        <!-- 新增备注 -->
        <div class="sd-section">
          <div class="sd-section-title">新增跟进记录</div>
          <div class="sd-remark-form">
            <el-input
              v-model="remarkText"
              type="textarea"
              :rows="3"
              :maxlength="200"
              show-word-limit
              placeholder="输入跟进备注内容..."
              resize="none"
            />
            <div class="sd-remark-bottom">
              <span class="sd-label">备注后状态</span>
              <el-select v-model="remarkNewStatus" size="small" style="width:110px" clearable placeholder="不变">
                <el-option v-for="(n,v) in options.statusMap" :key="v" :label="n" :value="Number(v)" />
              </el-select>
            </div>
            <el-button type="primary" size="small" style="width:100%;margin-top:6px" :loading="remarkLoading" @click="submitRemark">
              确定提交
            </el-button>
          </div>
        </div>

        <!-- 侧边Tab：跟进/备忘/分配 -->
        <div class="sd-section sd-history-section">
          <div class="sd-tab-bar">
            <div
              v-for="t in rightTabs" :key="t.key"
              class="sd-tab"
              :class="{ active: activeRightTab === t.key }"
              @click="activeRightTab = t.key; if(t.key==='assign') loadAssignHistory()"
            >{{ t.label }}</div>
          </div>

          <!-- 跟进记录 -->
          <div v-show="activeRightTab === 'remark'" class="sd-history-list">
            <div v-if="!remarks.length" class="sd-empty">暂无跟进记录</div>
            <div v-for="r in remarks" :key="r.id" class="sd-history-item">
              <div class="sd-history-header">
                <el-tag size="mini" :type="remarkTagType[r.remark_type]">{{ remarkTypeMap[r.remark_type] }}</el-tag>
                <span class="sd-history-advisor">{{ r.advisor_name || '顾问' }}</span>
                <span class="sd-history-time">{{ fmt(r.created_at) }}</span>
              </div>
              <div class="sd-history-content">{{ r.content }}</div>
            </div>
          </div>

          <!-- 备忘记录 -->
          <div v-show="activeRightTab === 'memo'" class="sd-history-list">
            <div v-if="!memoRemarks.length" class="sd-empty">暂无备忘记录</div>
            <div v-for="r in memoRemarks" :key="r.id" class="sd-history-item">
              <div class="sd-history-header">
                <el-tag size="mini" type="success">备忘</el-tag>
                <span class="sd-history-advisor">{{ r.advisor_name || '顾问' }}</span>
                <span class="sd-history-time">{{ fmt(r.created_at) }}</span>
              </div>
              <div class="sd-history-content">{{ r.content }}</div>
            </div>
          </div>

          <!-- 分配记录 -->
          <div v-show="activeRightTab === 'assign'" v-loading="loadingAssign" class="sd-history-list">
            <div v-if="!assignHistory.length" class="sd-empty">暂无分配记录</div>
            <div v-for="a in assignHistory" :key="a.id" class="sd-assign-item">
              <span class="sd-assign-time">{{ fmt(a.assigned_at) }}</span>
              <div class="sd-assign-flow">
                <span>{{ a.from_name || '系统' }}</span>
                <span class="sd-arrow">→</span>
                <span>{{ a.to_name || '未知' }}</span>
                <el-tag size="mini" style="margin-left:4px">{{ poolTypeMap[a.pool_type] || a.pool_type }}</el-tag>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>

    <!-- ===== 编辑弹窗 ===== -->
    <el-dialog v-model="editVisible" title="编辑客户信息" width="520px" :append-to-body="true">
      <el-form :model="editForm" label-width="90px" size="default">
        <el-form-item label="姓名"><el-input v-model="editForm.name" placeholder="客户姓名" /></el-form-item>
        <el-form-item label="性别">
          <el-radio-group v-model="editForm.gender">
            <el-radio :label="1">男</el-radio><el-radio :label="2">女</el-radio><el-radio :label="0">未知</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="城市"><el-input v-model="editForm.city" placeholder="所在城市" /></el-form-item>
        <el-form-item label="年龄"><el-input-number v-model="editForm.age" :min="18" :max="100" /></el-form-item>
        <el-form-item label="贷款类型">
          <el-select v-model="editForm.loan_type" style="width:100%">
            <el-option v-for="(n,v) in options.loanTypeMap" :key="v" :label="n" :value="Number(v)" />
          </el-select>
        </el-form-item>
        <el-form-item label="申请额度"><el-input-number v-model="editForm.apply_amount" :min="0" :precision="2" /></el-form-item>
        <el-form-item label="来源">
          <el-select v-model="editForm.source" style="width:100%" filterable allow-create clearable placeholder="选择或输入">
            <el-option v-for="s in options.sources" :key="s" :label="s" :value="s" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editVisible=false">取消</el-button>
        <el-button type="primary" :loading="editLoading" @click="handleEditSave">保存</el-button>
      </template>
    </el-dialog>

  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getCustomer, updateCustomer, getRemarks, addRemark, toPool, toMustFollow, lockCustomer, markImportant, blacklist, getAllOptions, getCustomerAssignHistory } from '../../api'

const route = useRoute()
const router = useRouter()

// 从路由参数取客户ID
const customerId = computed(() => Number(route.query.id) || Number(route.params.id) || null)

const loading = ref(false)
const detail = ref({})
const quals = ref({})
const remarks = ref([])
const remarkText = ref('')
const remarkLoading = ref(false)
const remarkNewStatus = ref(null)
const options = ref({ statusMap: {}, loanTypeMap: {}, sources: [] })
const activeInfoTab = ref('basic')
const activeRightTab = ref('remark')

const loadingAssign = ref(false)
const assignHistory = ref([])

const editVisible = ref(false)
const editLoading = ref(false)
const editForm = reactive({ name:'', gender:0, city:'', age:0, loan_type:1, apply_amount:0, source:'' })

const infoTabs = [
  { key: 'basic', label: '基本信息' },
  { key: 'identity', label: '身份信息' },
  { key: 'estate', label: '房产信息' },
  { key: 'vehicle', label: '车产信息' },
  { key: 'insurance', label: '保单社保' },
  { key: 'credit', label: '信用信息' },
  { key: 'liabilities', label: '负债情况' },
  { key: 'needs', label: '需求信息' },
  { key: 'all', label: '全部信息' },
]

const rightTabs = [
  { key: 'remark', label: '跟进' },
  { key: 'memo', label: '备忘' },
  { key: 'assign', label: '分配' },
]

const quickRemarks = [
  '未接', '拒接', '空号', '停机', '关机', '无法接通',
  '不需要了', '通话中', '接了就挂', '用户正忙',
  '贷款即挂', '外地号码', '现在不方便', '不是本人',
  '微信待通过', '已加微信', '已发短信',
]

const remarkTip = '1、户籍地在哪  2、上班还是做生意  3、工资多少/营业执照多长时间  4、是否有社保和公积金  5、自己和配偶是否有房车和保单  6、负债和征信情况  7、初步判断可以做哪些银行  8、预约什么时候上门'
const remarkTypeMap = { 0: '跟进', 1: '主管点评', 2: '备忘' }
const remarkTagType = { 0: '', 1: 'warning', 2: 'success' }
const poolTypeMap = { 1: '我的客户', 2: '再分配', 3: '公共池', 4: '必跟进' }

const hasEstate = computed(() => !!(quals.value?.real_estate?.type || quals.value?.real_estate?.property_type))
const hasVehicle = computed(() => !!(quals.value?.vehicle?.type))
const hasInsurance = computed(() => !!(quals.value?.insurance?.company || quals.value?.insurance?.type))
const memoRemarks = computed(() => remarks.value.filter(r => r.remark_type === 2))

const detailQ = (path) => {
  if (!path || !quals.value) return null
  return path.split('.').reduce((obj, key) => (obj || {})[key], quals.value) || null
}

const totalLiabilities = computed(() => {
  const l = quals.value?.liabilities || {}
  const total = (l.mortgage_monthly || 0) + (l.car_loan_monthly || 0) + (l.online_loan_monthly || 0) + (l.other_monthly || 0)
  return total.toLocaleString()
})

const fmt = (t) => t ? String(t).replace('T', ' ').substring(0, 16) : '—'

const loadDetail = async () => {
  if (!customerId.value) return
  loading.value = true
  try {
    const res = await getCustomer(customerId.value)
    detail.value = res
    quals.value = res.qualifications || {}
    options.value = { statusMap: res._statusMap || {}, loanTypeMap: res._loanTypeMap || {}, sources: res._sources || [] }
  } catch (e) { ElMessage.error('加载客户详情失败') }
  finally { loading.value = false }
}

const loadRemarks = async () => {
  if (!customerId.value) return
  try {
    const res = await getRemarks(customerId.value)
    remarks.value = res.items || []
  } catch (e) {}
}

const loadAssignHistory = async () => {
  loadingAssign.value = true
  try {
    const res = await getCustomerAssignHistory(customerId.value)
    assignHistory.value = res.items || []
  } catch (e) { assignHistory.value = [] }
  finally { loadingAssign.value = false }
}

const saveField = async (field) => {
  try {
    await updateCustomer(customerId.value, { [field]: detail.value[field] })
    ElMessage.success('已保存')
  } catch (e) { ElMessage.error('保存失败') }
}

const saveQuals = async () => {
  try { await updateCustomer(customerId.value, { qualifications: quals.value }); ElMessage.success('已保存') }
  catch (e) { ElMessage.error('保存失败') }
}

const toggleImportant = async () => {
  try {
    await markImportant(customerId.value)
    detail.value.is_important = detail.value.is_important ? 0 : 1
    ElMessage.success(detail.value.is_important ? '已标记为重要' : '已取消重要')
  } catch (e) { ElMessage.error('操作失败') }
}

const toggleLock = async () => {
  try {
    await lockCustomer(customerId.value)
    detail.value.is_locked = detail.value.is_locked ? 0 : 1
    ElMessage.success(detail.value.is_locked ? '已锁定' : '已解锁')
  } catch (e) { ElMessage.error('操作失败') }
}

const handleToPool = async () => {
  try {
    await ElMessageBox.confirm('确定将此客户加入公共池？', '提示')
    await toPool(customerId.value)
    ElMessage.success('已加入公共池')
    router.push('/team-customers')
  } catch (e) {}
}

const handleToMustFollow = async () => {
  try {
    await toMustFollow(customerId.value)
    ElMessage.success('已加入必跟进')
    router.push('/team-customers')
  } catch (e) { ElMessage.error('操作失败') }
}

const handleBlacklist = async () => {
  try {
    await ElMessageBox.confirm(detail.value.is_blacklisted ? '确定移除黑名单？' : '确定拉黑此客户？', '提示')
    await blacklist(customerId.value)
    detail.value.is_blacklisted = detail.value.is_blacklisted ? 0 : 1
    ElMessage.success(detail.value.is_blacklisted ? '已拉黑' : '已移除黑名单')
  } catch (e) {}
}

const applyQuickRemark = (r) => { remarkText.value = r }

const submitRemark = async () => {
  if (!remarkText.value.trim()) return ElMessage.warning('请输入备注内容')
  remarkLoading.value = true
  try {
    const data = { content: remarkText.value, remark_type: 0 }
    if (remarkNewStatus.value !== null) data.new_status = remarkNewStatus.value
    await addRemark(customerId.value, data)
    ElMessage.success('备注已提交')
    remarkText.value = ''
    remarkNewStatus.value = null
    await loadRemarks()
  } catch (e) { ElMessage.error('提交失败') }
  finally { remarkLoading.value = false }
}

const openEdit = () => {
  const d = detail.value
  Object.assign(editForm, {
    name: d.name || '', gender: d.gender || 0, city: d.city || '',
    age: d.age || 0, loan_type: d.loan_type || 1, apply_amount: d.apply_amount || 0, source: d.source || ''
  })
  editVisible.value = true
}

const handleEditSave = async () => {
  editLoading.value = true
  try {
    const data = {}
    if (editForm.name !== (detail.value.name || '')) data.name = editForm.name
    if (editForm.gender !== (detail.value.gender || 0)) data.gender = editForm.gender
    if (editForm.city !== (detail.value.city || '')) data.city = editForm.city
    if (editForm.age !== (detail.value.age || 0)) data.age = editForm.age
    if (editForm.loan_type !== (detail.value.loan_type || 1)) data.loan_type = editForm.loan_type
    if (editForm.apply_amount !== (detail.value.apply_amount || 0)) data.apply_amount = editForm.apply_amount
    if (editForm.source !== (detail.value.source || '')) data.source = editForm.source
    await updateCustomer(customerId.value, data)
    ElMessage.success('保存成功')
    editVisible.value = false
    await loadDetail()
  } catch (e) { ElMessage.error('保存失败') }
  finally { editLoading.value = false }
}

// 监听路由参数变化（支持URL直接访问）
watch(customerId, async (newId) => {
  if (newId) {
    activeInfoTab.value = 'basic'
    activeRightTab.value = 'remark'
    remarkText.value = ''
    remarkNewStatus.value = null
    editVisible.value = false
    await loadDetail()
    await loadRemarks()
  }
}, { immediate: true })
</script>

<style scoped>
/* ===== 全页面框架 ===== */
.cd-page {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #f0f2f5;
  overflow: hidden;
}

/* ===== 顶部操作栏 ===== */
.cd-topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 16px;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  flex-shrink: 0;
  gap: 12px;
  min-height: 48px;
  flex-wrap: wrap;
}
.cd-topbar-left {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}
.cd-topbar-right {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}
.cd-title {
  font-size: 14px;
  font-weight: 700;
  color: #1f2937;
  display: flex;
  align-items: center;
  gap: 8px;
}
.cd-id {
  color: #6b7280;
  font-weight: 400;
  font-size: 12px;
}
.cd-name {
  color: #111827;
}
.cd-label {
  font-size: 12px;
  color: #6b7280;
  margin-right: 2px;
}

/* ===== 主体左右分栏 ===== */
.cd-body {
  flex: 1;
  display: flex;
  overflow: hidden;
  min-height: 0;
}

/* ---- 左侧主区 ---- */
.cd-main {
  flex: 0 0 75%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: #fff;
  border-right: 1px solid #e4e7ed;
}

/* Tab栏 */
.cd-tab-bar {
  display: flex;
  border-bottom: 2px solid #dcdfe6;
  background: #fafafa;
  flex-shrink: 0;
  overflow-x: auto;
}
.cd-tab-bar::-webkit-scrollbar { height: 0; }
.cd-tab {
  padding: 9px 16px;
  cursor: pointer;
  font-size: 13px;
  color: #606266;
  white-space: nowrap;
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  transition: all 0.15s;
  font-weight: 500;
}
.cd-tab:hover { color: #409eff; background: #ecf5ff; }
.cd-tab.active {
  color: #409eff;
  border-bottom-color: #409eff;
  background: #f0f7ff;
}

/* 信息内容区 */
.cd-info-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

/* 密集网格 */
.cd-info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  overflow: hidden;
}
.grid-item {
  display: flex;
  align-items: center;
  padding: 7px 12px;
  border-bottom: 1px solid #f0f0f0;
  border-right: 1px solid #f0f0f0;
  min-height: 36px;
}
.grid-item:nth-child(2n) { border-right: none; }
/* 整行占满的item */
.grid-item[style*="grid-column"] { grid-column: 1 / -1; border-right: none; }
.grid-item--total {
  grid-column: 1 / -1;
  border-right: none;
  background: #fff7f0;
  border-top: 1px dashed #ffd591;
}
.grid-section-title {
  grid-column: 1 / -1;
  background: #f5f7fa;
  padding: 5px 12px;
  font-size: 12px;
  font-weight: 700;
  color: #409eff;
  border-bottom: 1px solid #e4e7ed;
  border-right: none;
}
.grid-label {
  font-size: 12px;
  color: #909399;
  width: 90px;
  flex-shrink: 0;
  font-weight: 600;
}
.grid-value {
  flex: 1;
  font-size: 13px;
  color: #303133;
  word-break: break-all;
}
.val-yes { color: #67c23a; font-weight: 600; }
.val-no  { color: #909399; }
.val-total { color: #e6a23c; font-weight: 700; font-size: 14px; }

/* ---- 右侧操作面板 ---- */
.cd-sidebar {
  flex: 0 0 25%;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  background: #fafbfc;
  min-width: 0;
}

.sd-section {
  padding: 10px 12px;
  border-bottom: 1px solid #e4e7ed;
}
.sd-section-title {
  font-size: 12px;
  font-weight: 700;
  color: #303133;
  margin-bottom: 7px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.sd-section-title::before {
  content: '■ ';
  color: #409eff;
  font-size: 10px;
}

/* 状态 */
.sd-status-row {
  display: flex;
  align-items: center;
  gap: 8px;
}
.sd-phone {
  font-size: 13px;
  color: #303133;
  font-family: monospace;
  letter-spacing: 1px;
}

/* 快捷标签 */
.sd-quick-btns {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}
.sd-quick-tag {
  font-size: 11px;
  cursor: pointer;
  padding: 2px 7px;
  color: #c0392b;
  border-color: #f5c6cb;
  background: #fff5f5;
  transition: all 0.15s;
}
.sd-quick-tag:hover {
  background: #ffeaea;
  border-color: #e74c3c;
  color: #c0392b;
}

/* 备注表单 */
.sd-remark-form {}
.sd-remark-bottom {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 6px;
}
.sd-label {
  font-size: 12px;
  color: #909399;
  white-space: nowrap;
}

/* 历史记录 */
.sd-history-section {
  flex: 1;
  padding: 0;
  border-bottom: none;
  display: flex;
  flex-direction: column;
}
.sd-tab-bar {
  display: flex;
  border-bottom: 1px solid #e4e7ed;
  background: #f5f7fa;
  flex-shrink: 0;
  padding: 0 12px;
}
.sd-tab {
  padding: 8px 12px;
  cursor: pointer;
  font-size: 12px;
  color: #606266;
  border-bottom: 2px solid transparent;
  margin-bottom: -1px;
}
.sd-tab:hover { color: #409eff; }
.sd-tab.active { color: #409eff; border-bottom-color: #409eff; font-weight: 600; }

.sd-history-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px 12px;
}
.sd-empty {
  text-align: center;
  color: #c0c4cc;
  font-size: 12px;
  padding: 24px 0;
}
.sd-history-item {
  padding: 7px 0;
  border-bottom: 1px solid #f0f0f0;
}
.sd-history-item:last-child { border-bottom: none; }
.sd-history-header {
  display: flex;
  align-items: center;
  gap: 5px;
  margin-bottom: 3px;
}
.sd-history-advisor {
  font-size: 11px;
  color: #303133;
  font-weight: 600;
}
.sd-history-time {
  font-size: 11px;
  color: #c0c4cc;
  margin-left: auto;
}
.sd-history-content {
  font-size: 12px;
  color: #606266;
  line-height: 1.5;
  word-break: break-all;
}
.sd-assign-item {
  padding: 6px 0;
  border-bottom: 1px solid #f0f0f0;
}
.sd-assign-time {
  font-size: 11px;
  color: #c0c4cc;
  display: block;
  margin-bottom: 2px;
}
.sd-assign-flow {
  font-size: 12px;
  color: #303133;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 2px;
}
.sd-arrow { color: #e6a23c; font-weight: bold; }
</style>
