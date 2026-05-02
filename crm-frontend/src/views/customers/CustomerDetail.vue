<template>
  <el-dialog
    :model-value="visible"
    :title="`客户详情 — ${detail.name || '未知'} · ID:${detail.id || ''}`"
    width="96%"
    top="2vh"
    :close-on-click-modal="false"
    @update:model-value="v => !v && emits('close')"
    class="customer-detail-modal"
  >
    <div v-loading="!detail.id" class="cdm-wrap">

      <!-- 顶部操作栏 -->
      <div class="cdm-header">
        <div class="cdm-header-left">
          <el-tag type="info" size="small">ID: {{ detail.id }}</el-tag>
          <el-tag v-if="detail.is_important" type="danger" size="small" style="margin-left:4px">重要</el-tag>
          <el-tag v-if="detail.is_locked" type="warning" size="small" style="margin-left:4px">🔒 锁定</el-tag>
          <el-tag v-if="detail.is_blacklisted" type="danger" size="small" style="margin-left:4px">🚫 黑名单</el-tag>
          <el-tag v-if="detail.source" type="info" size="small" style="margin-left:8px">{{ detail.source }}</el-tag>
        </div>
        <div class="cdm-header-right">
          <span style="margin-right:4px;color:#888;font-size:12px">星级</span>
          <el-rate v-model="detail.star_level" :max="6" size="small" @change="saveField('star_level')" style="margin-right:10px" />
          <el-select v-model="detail.status" size="small" style="width:110px;margin-right:6px" @change="saveField('status')">
            <el-option v-for="(n,v) in options.statusMap" :key="v" :label="n" :value="Number(v)" />
          </el-select>
          <el-button size="small" :type="detail.is_important?'danger':''" @click="toggleImportant">
            {{ detail.is_important ? '取消重要' : '标为重要' }}
          </el-button>
          <el-button size="small" :type="detail.is_locked?'warning':''" @click="toggleLock">
            {{ detail.is_locked ? '解锁' : '锁定' }}
          </el-button>
          <el-button size="small" type="info" @click="openEdit">编辑</el-button>
          <el-button size="small" type="warning" @click="handleToPool">加入公共池</el-button>
          <el-button size="small" type="success" @click="handleToMustFollow">加入必跟进</el-button>
          <el-button size="small" :type="detail.is_blacklisted?'':'danger'" @click="handleBlacklist">
            {{ detail.is_blacklisted ? '移除黑名单' : '拉黑' }}
          </el-button>
        </div>
      </div>

      <!-- 主内容区：左右分栏 -->
      <div class="cdm-body">
        <!-- 左侧：9大信息分类 -->
        <div class="cdm-left">
          <!-- Tab导航（水平排列） -->
          <div class="cdm-info-tabs">
            <div
              v-for="t in infoTabs" :key="t.key"
              class="cdm-info-tab"
              :class="{ active: activeInfoTab === t.key }"
              @click="activeInfoTab = t.key"
            >{{ t.label }}</div>
          </div>

          <!-- 信息内容区 -->
          <div class="cdm-info-area">
            <!-- 基本信息 -->
            <div v-show="activeInfoTab === 'basic'" class="info-section">
              <div class="info-row"><span class="info-label">姓名</span><span class="info-value">{{ detail.name || '—' }}</span></div>
              <div class="info-row"><span class="info-label">手机</span><span class="info-value">{{ detail.phone || '—' }}</span></div>
              <div class="info-row"><span class="info-label">性别</span><span class="info-value">{{ {0:'未知',1:'男',2:'女'}[detail.gender] || '—' }}</span></div>
              <div class="info-row"><span class="info-label">城市</span><span class="info-value">{{ detail.city || '—' }}</span></div>
              <div class="info-row"><span class="info-label">年龄</span><span class="info-value">{{ detail.age ? detail.age + '岁' : '—' }}</span></div>
              <div class="info-row"><span class="info-label">申请额度</span><span class="info-value">{{ detail.apply_amount ? detail.apply_amount + '万' : '—' }}</span></div>
              <div class="info-row"><span class="info-label">贷款类型</span><span class="info-value">{{ options.loanTypeMap[detail.loan_type] || '—' }}</span></div>
              <div class="info-row"><span class="info-label">来源</span><span class="info-value">{{ detail.source || '—' }}</span></div>
              <div class="info-row"><span class="info-label">申请时间</span><span class="info-value">{{ fmt(detail.created_at) }}</span></div>
            </div>

            <!-- 身份信息 -->
            <div v-show="activeInfoTab === 'identity'" class="info-section">
              <div class="info-row"><span class="info-label">户籍</span><span class="info-value">{{ detailQ('huji_city') || '—' }}</span></div>
              <div class="info-row"><span class="info-label">婚姻</span><span class="info-value">{{ detailQ('marriage') || '—' }}</span></div>
              <div class="info-row"><span class="info-label">学历</span><span class="info-value">{{ detailQ('education') || '—' }}</span></div>
              <div class="info-row"><span class="info-label">职业</span><span class="info-value">{{ detailQ('occupation') || '—' }}</span></div>
              <div class="info-row"><span class="info-label">月收入(元)</span><span class="info-value">{{ detailQ('salary_amount') || '—' }}</span></div>
              <div class="info-row"><span class="info-label">收入方式</span><span class="info-value">{{ detailQ('income_type') || '—' }}</span></div>
            </div>

            <!-- 房产信息 -->
            <div v-show="activeInfoTab === 'estate'" class="info-section">
              <div class="info-row"><span class="info-label">房产状况</span><span class="info-value">{{ hasEstate ? '有' : '无' }}</span></div>
              <template v-if="hasEstate">
                <div class="info-row"><span class="info-label">房屋类型</span><span class="info-value">{{ detailQ('real_estate.type') || '—' }}</span></div>
                <div class="info-row"><span class="info-label">房屋面积</span><span class="info-value">{{ detailQ('real_estate.area') ? detailQ('real_estate.area') + 'm²' : '—' }}</span></div>
                <div class="info-row"><span class="info-label">市场估值</span><span class="info-value">{{ detailQ('real_estate.market_value') ? detailQ('real_estate.market_value') + '万' : '—' }}</span></div>
                <div class="info-row"><span class="info-label">抵押状态</span><span class="info-value">{{ detailQ('real_estate.mortgage_status') || '—' }}</span></div>
                <div class="info-row"><span class="info-label">房屋性质</span><span class="info-value">{{ detailQ('real_estate.property_type') || '—' }}</span></div>
                <div class="info-row"><span class="info-label">房产地址</span><span class="info-value">{{ detailQ('real_estate.address') || '—' }}</span></div>
              </template>
            </div>

            <!-- 车产信息 -->
            <div v-show="activeInfoTab === 'vehicle'" class="info-section">
              <div class="info-row"><span class="info-label">车产状况</span><span class="info-value">{{ hasVehicle ? '有' : '无' }}</span></div>
              <template v-if="hasVehicle">
                <div class="info-row"><span class="info-label">车辆类型</span><span class="info-value">{{ detailQ('vehicle.type') || '—' }}</span></div>
                <div class="info-row"><span class="info-label">品牌型号</span><span class="info-value">{{ detailQ('vehicle.brand') || '—' }}</span></div>
                <div class="info-row"><span class="info-label">使用年限</span><span class="info-value">{{ detailQ('vehicle.years') ? detailQ('vehicle.years') + '年' : '—' }}</span></div>
                <div class="info-row"><span class="info-label">车辆估值</span><span class="info-value">{{ detailQ('vehicle.value') ? detailQ('vehicle.value') + '万' : '—' }}</span></div>
                <div class="info-row"><span class="info-label">按揭状态</span><span class="info-value">{{ detailQ('vehicle.payment_type') || '—' }}</span></div>
              </template>
            </div>

            <!-- 保单社保公积金 -->
            <div v-show="activeInfoTab === 'insurance'" class="info-section">
              <div class="info-row"><span class="info-label">保单</span><span class="info-value">{{ hasInsurance ? '有' : '无' }}</span></div>
              <template v-if="hasInsurance">
                <div class="info-row"><span class="info-label">保险公司</span><span class="info-value">{{ detailQ('insurance.company') || '—' }}</span></div>
                <div class="info-row"><span class="info-label">保单类型</span><span class="info-value">{{ detailQ('insurance.type') || '—' }}</span></div>
                <div class="info-row"><span class="info-label">年缴保费</span><span class="info-value">{{ detailQ('insurance.annual_premium') ? detailQ('insurance.annual_premium') + '元' : '—' }}</span></div>
                <div class="info-row"><span class="info-label">已缴年限</span><span class="info-value">{{ detailQ('insurance.paid_years') ? detailQ('insurance.paid_years') + '年' : '—' }}</span></div>
                <div class="info-row"><span class="info-label">保单现值</span><span class="info-value">{{ detailQ('insurance.cash_value') ? detailQ('insurance.cash_value') + '万' : '—' }}</span></div>
              </template>
              <div class="info-row"><span class="info-label">社保</span><span class="info-value">{{ detailQ('social_security') ? '有' : '无' }}</span></div>
              <div class="info-row"><span class="info-label">公积金</span><span class="info-value">{{ detailQ('housing_fund') ? '有' : '无' }}</span></div>
            </div>

            <!-- 信用信息 -->
            <div v-show="activeInfoTab === 'credit'" class="info-section">
              <div class="info-row"><span class="info-label">征信等级</span><span class="info-value">{{ detailQ('credit.credit_grade') || '—' }}</span></div>
              <div class="info-row"><span class="info-label">信用卡额度</span><span class="info-value">{{ detailQ('credit.credit_limit') ? detailQ('credit.credit_limit') + '万' : '—' }}</span></div>
              <div class="info-row"><span class="info-label">近6月查询</span><span class="info-value">{{ detailQ('credit.query_count') || '—' }}</span></div>
              <div class="info-row"><span class="info-label">微粒贷额度</span><span class="info-value">{{ detailQ('credit.weili_amount') || '—' }}</span></div>
              <div class="info-row"><span class="info-label">网贷平台数</span><span class="info-value">{{ detailQ('credit.online_loan_count') || '—' }}</span></div>
              <div class="info-row"><span class="info-label">是否有逾期</span><span class="info-value">{{ {0:'无',1:'偶尔',2:'较多'}[detailQ('credit.has_overdue')] || '—' }}</span></div>
            </div>

            <!-- 负债情况 -->
            <div v-show="activeInfoTab === 'liabilities'" class="info-section">
              <div class="info-row"><span class="info-label">信用卡已用</span><span class="info-value">{{ detailQ('liabilities.credit_card_used') ? detailQ('liabilities.credit_card_used') + '万' : '无' }}</span></div>
              <div class="info-row"><span class="info-label">房贷月还款</span><span class="info-value">{{ detailQ('liabilities.mortgage_monthly') ? detailQ('liabilities.mortgage_monthly') + '元/月' : '无' }}</span></div>
              <div class="info-row"><span class="info-label">车贷月还款</span><span class="info-value">{{ detailQ('liabilities.car_loan_monthly') ? detailQ('liabilities.car_loan_monthly') + '元/月' : '无' }}</span></div>
              <div class="info-row"><span class="info-label">网贷月还款</span><span class="info-value">{{ detailQ('liabilities.online_loan_monthly') ? detailQ('liabilities.online_loan_monthly') + '元/月' : '无' }}</span></div>
              <div class="info-row"><span class="info-label">其他月还款</span><span class="info-value">{{ detailQ('liabilities.other_monthly') ? detailQ('liabilities.other_monthly') + '元/月' : '无' }}</span></div>
              <div class="info-row total-debt"><span class="info-label">月负债合计</span><span class="info-value" style="color:#E91E63;font-weight:bold">{{ totalLiabilities }}元/月</span></div>
            </div>

            <!-- 需求信息 -->
            <div v-show="activeInfoTab === 'needs'" class="info-section">
              <div class="info-row"><span class="info-label">贷款用途</span><span class="info-value">{{ detailQ('needs.purpose') || '—' }}</span></div>
              <div class="info-row"><span class="info-label">期望期限</span><span class="info-value">{{ detailQ('needs.expect_term') || '—' }}</span></div>
              <div class="info-row"><span class="info-label">紧迫程度</span><span class="info-value">{{ detailQ('needs.urgency') || '—' }}</span></div>
              <div class="info-row"><span class="info-label">其他说明</span><span class="info-value">{{ detailQ('needs.description') || '—' }}</span></div>
            </div>

            <!-- 全部信息 -->
            <div v-show="activeInfoTab === 'all'" class="info-section">
              <div class="info-group-title">基本信息</div>
              <div class="info-row"><span class="info-label">姓名</span><span class="info-value">{{ detail.name || '—' }}</span></div>
              <div class="info-row"><span class="info-label">手机</span><span class="info-value">{{ detail.phone || '—' }}</span></div>
              <div class="info-row"><span class="info-label">性别/年龄</span><span class="info-value">{{ {0:'未知',1:'男',2:'女'}[detail.gender] }} / {{ detail.age ? detail.age + '岁' : '—' }}</span></div>
              <div class="info-row"><span class="info-label">城市</span><span class="info-value">{{ detail.city || '—' }}</span></div>
              <div class="info-row"><span class="info-label">申请额度</span><span class="info-value">{{ detail.apply_amount ? detail.apply_amount + '万' : '—' }}</span></div>
              <div class="info-row"><span class="info-label">来源</span><span class="info-value">{{ detail.source || '—' }}</span></div>
              <div class="info-row"><span class="info-label">申请时间</span><span class="info-value">{{ fmt(detail.created_at) }}</span></div>
              <div class="info-group-title">资产资质</div>
              <div class="info-row"><span class="info-label">房产</span><span class="info-value">{{ hasEstate ? '有' : '无' }}</span></div>
              <div class="info-row"><span class="info-label">车产</span><span class="info-value">{{ hasVehicle ? '有' : '无' }}</span></div>
              <div class="info-row"><span class="info-label">保单</span><span class="info-value">{{ hasInsurance ? '有' : '无' }}</span></div>
              <div class="info-row"><span class="info-label">社保/公积金</span><span class="info-value">{{ detailQ('social_security') ? '有' : '无' }} / {{ detailQ('housing_fund') ? '有' : '无' }}</span></div>
              <div class="info-row"><span class="info-label">征信等级</span><span class="info-value">{{ detailQ('credit.credit_grade') || '—' }}</span></div>
              <div class="info-row"><span class="info-label">信用卡额度</span><span class="info-value">{{ detailQ('credit.credit_limit') ? detailQ('credit.credit_limit') + '万' : '—' }}</span></div>
              <div class="info-row total-debt"><span class="info-label">月负债合计</span><span class="info-value" style="color:#E91E63;font-weight:bold">{{ totalLiabilities }}元/月</span></div>
              <div class="info-group-title">贷款需求</div>
              <div class="info-row"><span class="info-label">用途</span><span class="info-value">{{ detailQ('needs.purpose') || '—' }}</span></div>
              <div class="info-row"><span class="info-label">紧迫度</span><span class="info-value">{{ detailQ('needs.urgency') || '—' }}</span></div>
            </div>
          </div>
        </div>

        <!-- 右侧：备注区域 -->
        <div class="cdm-right">
          <!-- 子Tab -->
          <div class="cdm-right-tabs">
            <div
              v-for="t in rightTabs" :key="t.key"
              class="cdm-right-tab"
              :class="{ active: activeRightTab === t.key }"
              @click="activeRightTab = t.key; if(t.key==='assign') loadAssignHistory()"
            >{{ t.label }}</div>
          </div>

          <!-- 客户跟踪（默认） -->
          <div v-show="activeRightTab === 'remark'" class="cdm-remark-area">
            <!-- 快捷备注按钮 -->
            <div class="quick-btns">
              <el-button
                v-for="r in quickRemarks"
                :key="r"
                size="small"
                class="quick-btn"
                @click="applyQuickRemark(r)"
              >{{ r }}</el-button>
            </div>
            <!-- 备注提示 -->
            <div class="remark-tip">
              <el-icon color="#E6A23C"><InfoFilled /></el-icon>
              <span>{{ remarkTip }}</span>
            </div>
            <!-- 客户资质摘要 -->
            <div class="ability-row">
              <span style="font-size:12px;color:#888">资质摘要：</span>
              <el-input v-model="quals.customer_ability_text" size="small" placeholder="如：有房/征信A级" @blur="saveQuals" style="flex:1" />
            </div>
            <!-- 备注后状态 -->
            <div class="remark-status-row">
              <span style="font-size:12px;color:#888">备注后状态</span>
              <el-select v-model="remarkNewStatus" size="small" style="width:120px" clearable placeholder="不变">
                <el-option v-for="(n,v) in options.statusMap" :key="v" :label="n" :value="Number(v)" />
              </el-select>
            </div>
            <!-- 备注输入 -->
            <div class="remark-input-area">
              <el-input
                v-model="remarkText"
                type="textarea"
                :rows="3"
                placeholder="输入跟进备注..."
                resize="none"
              />
              <div style="margin-top:8px; display:flex; justify-content:space-between; align-items:center">
                <span style="font-size:12px; color:#888">{{ remarkText.length }}/200</span>
                <el-button type="primary" size="small" :loading="remarkLoading" @click="submitRemark">提交备注</el-button>
              </div>
            </div>
            <!-- 历史备注 -->
            <div class="remark-list">
              <div v-if="!remarks.length" style="color:#ccc; text-align:center; padding:20px">暂无备注记录</div>
              <div v-for="r in remarks" :key="r.id" class="remark-item">
                <div class="remark-item-header">
                  <el-tag size="small" :type="remarkTagType[r.remark_type]">{{ remarkTypeMap[r.remark_type] }}</el-tag>
                  <span class="remark-item-advisor">{{ r.advisor_name || '顾问' }}</span>
                  <span class="remark-item-time">{{ fmt(r.created_at) }}</span>
                </div>
                <div class="remark-item-content">{{ r.content }}</div>
              </div>
            </div>
          </div>

          <!-- 备忘记录 -->
          <div v-show="activeRightTab === 'memo'" class="cdm-remark-area">
            <div v-if="!memoRemarks.length" style="color:#ccc; text-align:center; padding:30px">暂无备忘记录</div>
            <div v-for="r in memoRemarks" :key="r.id" class="remark-item">
              <div class="remark-item-header">
                <el-tag size="small" type="success">备忘</el-tag>
                <span class="remark-item-advisor">{{ r.advisor_name || '顾问' }}</span>
                <span class="remark-item-time">{{ fmt(r.created_at) }}</span>
              </div>
              <div class="remark-item-content">{{ r.content }}</div>
            </div>
          </div>

          <!-- 通话录音 -->
          <div v-show="activeRightTab === 'call'" class="cdm-call-area">
            <el-empty description="通话录音功能需对接第三方通话系统" :image-size="80" />
            <div style="padding:12px; font-size:13px; color:#888">当前显示placeholder，待对接点拨通等通话系统后自动展示录音记录。</div>
          </div>

          <!-- 分配记录 -->
          <div v-show="activeRightTab === 'assign'" class="cdm-assign-area" v-loading="loadingAssign">
            <div v-if="!assignHistory.length" style="color:#ccc; text-align:center; padding:30px">暂无分配记录</div>
            <div v-for="a in assignHistory" :key="a.id" class="assign-item">
              <div class="assign-time">{{ fmt(a.assigned_at) }}</div>
              <div class="assign-content">
                <span>{{ a.from_name || '系统' }}</span>
                <span style="color:#E6A23C; margin:0 4px">→</span>
                <span>{{ a.to_name || '未知' }}</span>
                <el-tag size="small" style="margin-left:6px">{{ poolTypeMap[a.pool_type] || a.pool_type }}</el-tag>
              </div>
            </div>
          </div>
        </div>
      </div>

    </div>
  </el-dialog>

  <!-- 编辑客户弹窗 -->
  <el-dialog v-model="editVisible" title="编辑客户" width="480px">
    <el-form :model="editForm" label-width="80px">
      <el-form-item label="姓名"><el-input v-model="editForm.name" placeholder="客户姓名" /></el-form-item>
      <el-form-item label="性别"><el-radio-group v-model="editForm.gender">
        <el-radio :label="1">男</el-radio><el-radio :label="2">女</el-radio><el-radio :label="0">未知</el-radio>
      </el-radio-group></el-form-item>
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
      <el-button type="primary" :loading="editLoading" @click="handleEditSave">保存修改</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { InfoFilled } from '@element-plus/icons-vue'
import { getCustomer, updateCustomer, getRemarks, addRemark, toPool, toMustFollow, lockCustomer, markImportant, blacklist, getAllOptions, getCustomerAssignHistory } from '../../api'

const props = defineProps({ visible: Boolean, customerId: Number })
const emits = defineEmits(['close', 'updated'])

const detail = ref({})
const quals = ref({})
const remarks = ref([])
const memoRemarks = computed(() => remarks.value.filter(r => r.remark_type === 2))
const remarkText = ref('')
const remarkLoading = ref(false)
const remarkNewStatus = ref(null)
const options = ref({ statusMap: {}, loanTypeMap: {}, sources: [] })
const activeInfoTab = ref('basic')
const activeRightTab = ref('remark')

// 分配历史
const loadingAssign = ref(false)
const assignHistory = ref([])

// 编辑弹窗
const editVisible = ref(false)
const editLoading = ref(false)
const editForm = reactive({ name:'', gender:0, city:'', age:0, loan_type:1, apply_amount:0, source:'' })

const infoTabs = [
  { key: 'basic', label: '基本信息' },
  { key: 'identity', label: '身份信息' },
  { key: 'estate', label: '房产信息' },
  { key: 'vehicle', label: '车产信息' },
  { key: 'insurance', label: '保单/社保' },
  { key: 'credit', label: '信用信息' },
  { key: 'liabilities', label: '负债情况' },
  { key: 'needs', label: '需求信息' },
  { key: 'all', label: '全部信息' },
]

const rightTabs = [
  { key: 'remark', label: '客户跟踪' },
  { key: 'memo', label: '备忘记录' },
  { key: 'call', label: '通话录音' },
  { key: 'assign', label: '分配记录' },
]

const quickRemarks = [
  '未接', '不需要了', '通话中', '拒接', '接了就挂', '无法接通',
  '用户正忙', '贷款即挂', '空号', '停机', '关机', '外地号码',
  '现在不方便接听', '不是本人申请', '微信待通过', '已发短信', '已加微信'
]

const remarkTip = '1、户籍地在哪  2、上班还是做生意  3、工资多少/营业执照多长时间  4、是否有社保和公积金  5、自己和配偶是否有房车和保单  6、负债和征信情况  7、初步判断可以做哪些银行  8、预约什么时候上门'
const remarkTypeMap = { 0: '跟进', 1: '主管点评', 2: '备忘' }
const remarkTagType = { 0: '', 1: 'warning', 2: 'success' }
const poolTypeMap = { 1: '我的客户', 2: '再分配', 3: '公共池', 4: '必跟进' }

const hasEstate = computed(() => !!(quals.value?.real_estate?.type || quals.value?.real_estate?.property_type))
const hasVehicle = computed(() => !!(quals.value?.vehicle?.type))
const hasInsurance = computed(() => !!(quals.value?.insurance?.company || quals.value?.insurance?.type))

// 嵌套字段读取
const detailQ = (path) => {
  if (!path || !quals.value) return null
  return path.split('.').reduce((obj, key) => (obj || {})[key], quals.value) || null
}

// 月负债合计
const totalLiabilities = computed(() => {
  const l = quals.value?.liabilities || {}
  const total = (l.mortgage_monthly || 0) + (l.car_loan_monthly || 0) + (l.online_loan_monthly || 0) + (l.other_monthly || 0)
  return total.toLocaleString()
})

const fmt = (t) => t ? String(t).replace('T', ' ').substring(0, 16) : '—'

// 加载数据
const loadDetail = async () => {
  try {
    const res = await getCustomer(props.customerId)
    detail.value = res
    quals.value = res.qualifications || {}
    options.value = { statusMap: res._statusMap || {}, loanTypeMap: res._loanTypeMap || {}, sources: res._sources || [] }
  } catch (e) { ElMessage.error('加载失败') }
}

const loadRemarks = async () => {
  try {
    const res = await getRemarks(props.customerId)
    remarks.value = res.items || []
  } catch (e) {}
}

const loadAssignHistory = async () => {
  loadingAssign.value = true
  try {
    const res = await getCustomerAssignHistory(props.customerId)
    assignHistory.value = res.items || []
  } catch (e) { assignHistory.value = [] }
  finally { loadingAssign.value = false }
}

watch(() => props.visible, async (v) => {
  if (v && props.customerId) {
    await loadDetail()
    await loadRemarks()
    activeInfoTab.value = 'basic'
    activeRightTab.value = 'remark'
    remarkText.value = ''
    remarkNewStatus.value = null
    editVisible.value = false
  }
}, { immediate: true })

watch(() => props.customerId, async (newId) => {
  if (newId && props.visible) {
    await loadDetail()
    await loadRemarks()
    activeInfoTab.value = 'basic'
    activeRightTab.value = 'remark'
    remarkText.value = ''
    remarkNewStatus.value = null
  }
})

// 保存字段
const saveField = async (field) => {
  try {
    await updateCustomer(props.customerId, { [field]: detail.value[field] })
    ElMessage.success('已保存')
  } catch (e) { ElMessage.error('保存失败') }
}

const saveQuals = async () => {
  try { await updateCustomer(props.customerId, { qualifications: quals.value }); ElMessage.success('已保存') }
  catch (e) { ElMessage.error('保存失败') }
}

// 操作
const toggleImportant = async () => {
  try {
    await markImportant(props.customerId)
    detail.value.is_important = detail.value.is_important ? 0 : 1
    ElMessage.success(detail.value.is_important ? '已标记为重要' : '已取消重要')
  } catch (e) { ElMessage.error('操作失败') }
}

const toggleLock = async () => {
  try {
    await lockCustomer(props.customerId)
    detail.value.is_locked = detail.value.is_locked ? 0 : 1
    ElMessage.success(detail.value.is_locked ? '已锁定' : '已解锁')
  } catch (e) { ElMessage.error('操作失败') }
}

const handleToPool = async () => {
  try {
    await ElMessageBox.confirm('确定将此客户加入公共池？', '提示')
    await toPool(props.customerId)
    ElMessage.success('已加入公共池')
    emits('close')
  } catch (e) {}
}

const handleToMustFollow = async () => {
  try {
    await toMustFollow(props.customerId)
    ElMessage.success('已加入必跟进')
    emits('close')
  } catch (e) { ElMessage.error('操作失败') }
}

const handleBlacklist = async () => {
  try {
    await ElMessageBox.confirm(detail.value.is_blacklisted ? '确定移除黑名单？' : '确定拉黑此客户？', '提示')
    await blacklist(props.customerId)
    detail.value.is_blacklisted = detail.value.is_blacklisted ? 0 : 1
    ElMessage.success(detail.value.is_blacklisted ? '已拉黑' : '已移除黑名单')
  } catch (e) {}
}

// 快捷备注
const applyQuickRemark = (r) => { remarkText.value = r }

// 提交备注
const submitRemark = async () => {
  if (!remarkText.value.trim()) return ElMessage.warning('请输入备注内容')
  remarkLoading.value = true
  try {
    const data = { content: remarkText.value, remark_type: 0 }
    if (remarkNewStatus.value !== null) data.new_status = remarkNewStatus.value
    await addRemark(props.customerId, data)
    ElMessage.success('备注已提交')
    remarkText.value = ''
    remarkNewStatus.value = null
    await loadRemarks()
    emits('updated')
  } catch (e) { ElMessage.error('提交失败') }
  finally { remarkLoading.value = false }
}

// 编辑客户
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
    await updateCustomer(props.customerId, data)
    ElMessage.success('保存成功')
    editVisible.value = false
    await loadDetail()
  } catch (e) { ElMessage.error('保存失败') }
  finally { editLoading.value = false }
}
</script>

<style scoped>
/* 对话框自适应高度 */
.customer-detail-modal :deep(.el-dialog__body) {
  padding: 0;
  overflow: hidden;
}

.cdm-wrap {
  height: calc(92vh - 54px);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 顶部操作栏 */
.cdm-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 14px;
  background: linear-gradient(135deg, #fff5f8 0%, #fff 100%);
  border-bottom: 1px solid #FCE4EC;
  flex-shrink: 0;
  gap: 8px;
  flex-wrap: wrap;
}
.cdm-header-left { display: flex; align-items: center; gap: 4px; flex-wrap: wrap; }
.cdm-header-right { display: flex; align-items: center; gap: 4px; flex-wrap: wrap; }

/* 主内容区 */
.cdm-body {
  flex: 1;
  display: flex;
  overflow: hidden;
  min-height: 0;
}

/* 左侧信息区 */
.cdm-left {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border-right: 1px solid #f0f0f0;
  min-width: 0;
}

/* Tab导航（水平排列） */
.cdm-info-tabs {
  display: flex;
  border-bottom: 2px solid #FCE4EC;
  background: #fff5f8;
  flex-shrink: 0;
  overflow-x: auto;
}
.cdm-info-tabs::-webkit-scrollbar { height: 0; }
.cdm-info-tab {
  padding: 8px 14px;
  cursor: pointer;
  font-size: 13px;
  color: #888;
  white-space: nowrap;
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  transition: all 0.15s;
}
.cdm-info-tab:hover { color: #E91E63; }
.cdm-info-tab.active { color: #E91E63; border-bottom-color: #E91E63; font-weight: 600; }

/* 信息内容区 */
.cdm-info-area {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
}
.info-section {}
.info-group-title {
  font-size: 12px; font-weight: 600; color: #E91E63;
  padding: 6px 0 4px; border-bottom: 1px dashed #fce4ec; margin-bottom: 6px;
}
.info-row {
  display: flex;
  align-items: center;
  padding: 5px 0;
  font-size: 13px;
  border-bottom: 1px solid #f9f9f9;
}
.info-row.total-debt { border-top: 1px dashed #FCE4EC; margin-top: 4px; padding-top: 8px; }
.info-label { color: #888; width: 90px; flex-shrink: 0; font-size: 12px; }
.info-value { color: #333; flex: 1; }

/* 右侧备注区 */
.cdm-right {
  flex: 0 0 300px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.cdm-right-tabs {
  display: flex;
  border-bottom: 2px solid #FCE4EC;
  background: #fff5f8;
  flex-shrink: 0;
}
.cdm-right-tab {
  padding: 8px 14px;
  cursor: pointer;
  font-size: 13px;
  color: #888;
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  transition: all 0.15s;
}
.cdm-right-tab:hover { color: #E91E63; }
.cdm-right-tab.active { color: #E91E63; border-bottom-color: #E91E63; font-weight: 600; }

.cdm-remark-area {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.quick-btns { display: flex; flex-wrap: wrap; gap: 4px; }
.quick-btn {
  font-size: 12px;
  padding: 3px 8px;
  height: auto;
  border-radius: 4px;
  color: #E91E63;
  border-color: #FCE4EC;
  background: #fff5f8;
}
.quick-btn:hover { background: #FCE4EC; color: #C2185B; }

.remark-tip {
  font-size: 11px;
  color: #E6A23C;
  background: #fdf6ec;
  padding: 6px 8px;
  border-radius: 4px;
  line-height: 1.6;
  display: flex;
  gap: 4px;
  align-items: flex-start;
}

.ability-row { display: flex; align-items: center; gap: 6px; }

.remark-status-row { display: flex; align-items: center; gap: 8px; }

.remark-input-area {
  background: #fafafa;
  padding: 8px;
  border-radius: 6px;
  border: 1px solid #f0f0f0;
}

.remark-list { flex: 1; overflow-y: auto; }
.remark-item { padding: 8px 0; border-bottom: 1px solid #f5f5f5; }
.remark-item-header { display: flex; align-items: center; gap: 6px; margin-bottom: 4px; }
.remark-item-advisor { font-size: 12px; color: #333; font-weight: 500; }
.remark-item-time { font-size: 11px; color: #aaa; margin-left: auto; }
.remark-item-content { font-size: 13px; color: #555; line-height: 1.5; }

.cdm-call-area { padding: 12px; }
.cdm-assign-area { padding: 12px; overflow-y: auto; }
.assign-item { padding: 8px 0; border-bottom: 1px solid #f5f5f5; }
.assign-time { font-size: 11px; color: #aaa; margin-bottom: 4px; }
.assign-content { font-size: 13px; display: flex; align-items: center; flex-wrap: wrap; }
</style>
