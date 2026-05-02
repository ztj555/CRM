<template>
  <div class="cp-page">
    <!-- 顶部操作栏（原系统风格） -->
    <div class="cp-header">
      <div class="cp-header-left">
        <el-tag type="info" size="small">ID: {{ detail.id }}</el-tag>
        <el-tag v-if="detail.is_important" type="danger" size="small" style="margin-left:4px">重要</el-tag>
        <el-tag v-if="detail.is_locked" type="warning" size="small" style="margin-left:4px">🔒 锁定</el-tag>
        <el-tag v-if="detail.is_blacklisted" type="danger" size="small" style="margin-left:4px">🚫 黑名单</el-tag>
        <el-tag v-if="detail.source" type="info" size="small" style="margin-left:8px">{{ detail.source }}</el-tag>
      </div>
      <div class="cp-header-right">
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
        <el-dropdown trigger="click" @command="handleQuickMemo">
          <el-button size="small" type="info">
            备忘新增 <el-icon><ArrowDown /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="quick">快捷备忘</el-dropdown-item>
              <el-dropdown-item command="detail">详细备注</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
        <el-button size="small" type="danger" @click="toBlacklist" :disabled="detail.is_blacklisted">拉黑</el-button>
        <el-button size="small" type="warning" @click="handleToPool">加入公共池</el-button>
        <el-button size="small" type="success" @click="handleToMustFollow">加入必跟进</el-button>
        <el-button size="small" @click="openEdit">编辑</el-button>
        <el-button size="small" type="info" @click="emits('close')" style="margin-left:8px">关闭</el-button>
        <el-button size="small" text type="primary" @click="emits('prev')" title="上一位">▲</el-button>
        <el-button size="small" text type="primary" @click="emits('next')" title="下一位">▼</el-button>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="cp-body" v-loading="!detail.id">
      <!-- 左侧信息区 -->
      <div class="cp-left">
        <!-- Tab导航 -->
        <div class="cp-tabs">
          <div
            v-for="t in infoTabs"
            :key="t.key"
            class="cp-tab"
            :class="{ active: activeInfoTab === t.key }"
            @click="activeInfoTab = t.key"
          >{{ t.label }}</div>
        </div>

        <!-- 9大信息分类内容 -->
        <div class="cp-info-area">
          <!-- 基本信息 -->
          <div v-show="activeInfoTab === 'basic'" class="info-section">
            <div class="info-row"><span class="info-label">姓名</span><span class="info-value">{{ detail.name || '—' }}</span></div>
            <div class="info-row"><span class="info-label">手机</span><span class="info-value">{{ detail.phone || '—' }}</span></div>
            <div class="info-row"><span class="info-label">性别</span><span class="info-value">{{ {0:'未知',1:'男',2:'女'}[detail.gender] || '—' }}</span></div>
            <div class="info-row"><span class="info-label">城市</span><span class="info-value">{{ detail.city || '—' }}</span></div>
            <div class="info-row"><span class="info-label">年龄</span><span class="info-value">{{ detail.age || '—' }}</span></div>
            <div class="info-row"><span class="info-label">婚姻</span><span class="info-value">{{ detailQ('marriage') || '—' }}</span></div>
            <div class="info-row"><span class="info-label">申请额度</span><span class="info-value">{{ detail.apply_amount ? detail.apply_amount + '万' : '—' }}</span></div>
            <div class="info-row"><span class="info-label">贷款类型</span><span class="info-value">{{ options.loanTypeMap[detail.loan_type] || '—' }}</span></div>
            <div class="info-row"><span class="info-label">来源</span><span class="info-value">{{ detail.source || '—' }}</span></div>
            <div class="info-row"><span class="info-label">申请时间</span><span class="info-value">{{ fmt(detail.created_at) }}</span></div>
          </div>

          <!-- 身份信息 -->
          <div v-show="activeInfoTab === 'identity'" class="info-section">
            <div class="info-row"><span class="info-label">居住省市</span><span class="info-value">{{ detailQ('province') || '—' }}</span></div>
            <div class="info-row"><span class="info-label">学历</span><span class="info-value">{{ detailQ('education') || '—' }}</span></div>
            <div class="info-row"><span class="info-label">学历类型</span><span class="info-value">{{ detailQ('edu_type') || '—' }}</span></div>
            <div class="info-row"><span class="info-label">是否有企业</span><span class="info-value">{{ detailQ('has_enterprise') ? '是' : '否' }}</span></div>
            <div class="info-row"><span class="info-label">职业</span><span class="info-value">{{ detailQ('occupation') || '—' }}</span></div>
            <div class="info-row"><span class="info-label">工资发放</span><span class="info-value">{{ detailQ('salary_issue') || '—' }}</span></div>
            <div class="info-row"><span class="info-label">营业执照年限</span><span class="info-value">{{ detailQ('biz_years') || '—' }}</span></div>
          </div>

          <!-- 房产信息 -->
          <div v-show="activeInfoTab === 'house'" class="info-section">
            <div class="info-row"><span class="info-label">房产状况</span><span class="info-value">{{ hasVal(detailQ('has_house')) }}</span></div>
            <div class="info-row" v-if="detailQ('has_house')"><span class="info-label">房屋类型</span><span class="info-value">{{ detailQ('house_type') || '—' }}</span></div>
            <div class="info-row" v-if="detailQ('has_house')"><span class="info-label">房产省市</span><span class="info-value">{{ detailQ('house_province') || '—' }}</span></div>
            <div class="info-row" v-if="detailQ('has_house')"><span class="info-label">抵押状态</span><span class="info-value">{{ detailQ('house_mortgage') || '—' }}</span></div>
            <div class="info-row" v-if="detailQ('has_house')"><span class="info-label">是否按揭</span><span class="info-value">{{ hasBool(detailQ('house_loan')) }}</span></div>
          </div>

          <!-- 车产信息 -->
          <div v-show="activeInfoTab === 'car'" class="info-section">
            <div class="info-row"><span class="info-label">车产状况</span><span class="info-value">{{ hasVal(detailQ('has_car')) }}</span></div>
            <div class="info-row" v-if="detailQ('has_car')"><span class="info-label">车辆类型</span><span class="info-value">{{ detailQ('car_type') || '—' }}</span></div>
            <div class="info-row" v-if="detailQ('has_car')"><span class="info-label">按揭/全款</span><span class="info-value">{{ hasBool(detailQ('car_loan')) }}</span></div>
            <div class="info-row" v-if="detailQ('has_car')"><span class="info-label">使用年限</span><span class="info-value">{{ detailQ('car_years') ? detailQ('car_years') + '年' : '—' }}</span></div>
            <div class="info-row" v-if="detailQ('has_car')"><span class="info-label">车辆价值</span><span class="info-value">{{ detailQ('car_value') ? detailQ('car_value') + '万' : '—' }}</span></div>
          </div>

          <!-- 保单社保公积金 -->
          <div v-show="activeInfoTab === 'insurance'" class="info-section">
            <div class="info-row"><span class="info-label">保单情况</span><span class="info-value">{{ hasVal(detailQ('has_insurance')) }}</span></div>
            <div class="info-row" v-if="detailQ('has_insurance')"><span class="info-label">保险公司</span><span class="info-value">{{ detailQ('insurance_company') || '—' }}</span></div>
            <div class="info-row" v-if="detailQ('has_insurance')"><span class="info-label">保单状态</span><span class="info-value">{{ detailQ('insurance_status') || '—' }}</span></div>
            <div class="info-row"><span class="info-label">社保</span><span class="info-value">{{ hasBool(detailQ('social_security')) }}</span></div>
            <div class="info-row"><span class="info-label">公积金</span><span class="info-value">{{ hasBool(detailQ('housing_fund')) }}</span></div>
          </div>

          <!-- 信用信息 -->
          <div v-show="activeInfoTab === 'credit'" class="info-section">
            <div class="info-row"><span class="info-label">微粒贷额度</span><span class="info-value">{{ detailQ('weilidai') || '—' }}</span></div>
            <div class="info-row"><span class="info-label">近6月查询</span><span class="info-value">{{ detailQ('credit_query') || '—' }}</span></div>
            <div class="info-row"><span class="info-label">当前贷款笔数</span><span class="info-value">{{ detailQ('loan_count') || '—' }}</span></div>
            <div class="info-row"><span class="info-label">信用卡额度</span><span class="info-value">{{ detailQ('credit_card') ? detailQ('credit_card') + '万' : '—' }}</span></div>
            <div class="info-row"><span class="info-label">征信等级</span><span class="info-value">{{ detailQ('credit_level') || '—' }}</span></div>
          </div>

          <!-- 负债情况 -->
          <div v-show="activeInfoTab === 'liabilities'" class="info-section">
            <div class="info-row"><span class="info-label">房贷</span><span class="info-value">{{ detailQ('debt_house') ? detailQ('debt_house') + '元/月' : '无' }}</span></div>
            <div class="info-row"><span class="info-label">车贷</span><span class="info-value">{{ detailQ('debt_car') ? detailQ('debt_car') + '元/月' : '无' }}</span></div>
            <div class="info-row"><span class="info-label">网贷</span><span class="info-value">{{ detailQ('debt_net') ? detailQ('debt_net') + '元/月' : '无' }}</span></div>
            <div class="info-row"><span class="info-label">其他负债</span><span class="info-value">{{ detailQ('debt_other') ? detailQ('debt_other') + '元/月' : '无' }}</span></div>
            <div class="info-row total-debt"><span class="info-label">月负债合计</span><span class="info-value" style="color:#E91E63;font-weight:bold">{{ monthDebt }}元/月</span></div>
          </div>

          <!-- 需求信息 -->
          <div v-show="activeInfoTab === 'needs'" class="info-section">
            <div class="info-row"><span class="info-label">贷款用途</span><span class="info-value">{{ detailQ('loan_use') || '—' }}</span></div>
            <div class="info-row"><span class="info-label">期望期限</span><span class="info-value">{{ detailQ('loan_term') || '—' }}</span></div>
            <div class="info-row"><span class="info-label">紧迫程度</span><span class="info-value">{{ detailQ('urgency') || '—' }}</span></div>
            <div class="info-row"><span class="info-label">说明</span><span class="info-value">{{ detailQ('need_desc') || '—' }}</span></div>
          </div>

          <!-- 全部信息 -->
          <div v-show="activeInfoTab === 'all'" class="info-section">
            <div class="info-group-title">基本信息</div>
            <div class="info-row"><span class="info-label">姓名</span><span class="info-value">{{ detail.name || '—' }}</span></div>
            <div class="info-row"><span class="info-label">手机</span><span class="info-value">{{ detail.phone || '—' }}</span></div>
            <div class="info-row"><span class="info-label">性别/年龄</span><span class="info-value">{{ {0:'未知',1:'男',2:'女'}[detail.gender] }} / {{ detail.age || '—' }}岁</span></div>
            <div class="info-row"><span class="info-label">城市/婚姻</span><span class="info-value">{{ detail.city || '—' }} / {{ detailQ('marriage') || '—' }}</span></div>
            <div class="info-row"><span class="info-label">申请额度</span><span class="info-value">{{ detail.apply_amount ? detail.apply_amount + '万' : '—' }} ({{ options.loanTypeMap[detail.loan_type] }})</span></div>
            <div class="info-row"><span class="info-label">来源</span><span class="info-value">{{ detail.source || '—' }}</span></div>
            <div class="info-group-title">资产资质</div>
            <div class="info-row"><span class="info-label">房产</span><span class="info-value">{{ hasVal(detailQ('has_house')) }}</span></div>
            <div class="info-row"><span class="info-label">车产</span><span class="info-value">{{ hasVal(detailQ('has_car')) }}</span></div>
            <div class="info-row"><span class="info-label">保单</span><span class="info-value">{{ hasVal(detailQ('has_insurance')) }}</span></div>
            <div class="info-row"><span class="info-label">社保/公积金</span><span class="info-value">{{ hasBool(detailQ('social_security')) }} / {{ hasBool(detailQ('housing_fund')) }}</span></div>
            <div class="info-row"><span class="info-label">企业主</span><span class="info-value">{{ hasBool(detailQ('has_enterprise')) }}</span></div>
            <div class="info-row"><span class="info-label">微粒贷/信用卡</span><span class="info-value">{{ detailQ('weilidai') || '—' }} / {{ detailQ('credit_card') ? detailQ('credit_card')+'万' : '—' }}</span></div>
            <div class="info-row"><span class="info-label">月负债合计</span><span class="info-value" style="color:#E91E63">{{ monthDebt }}元/月</span></div>
            <div class="info-row"><span class="info-label">芝麻分</span><span class="info-value">{{ detailQ('zhima_score') || '—' }}</span></div>
            <div class="info-row"><span class="info-label">征信等级</span><span class="info-value">{{ detailQ('credit_level') || '—' }}</span></div>
          </div>
        </div>
      </div>

      <!-- 右侧备注区 -->
      <div class="cp-right">
        <!-- 子Tab：客户跟踪 / 通话录音 / 分配记录 -->
        <div class="cp-right-tabs">
          <div
            v-for="t in rightTabs"
            :key="t.key"
            class="cp-right-tab"
            :class="{ active: activeRightTab === t.key }"
            @click="activeRightTab = t.key; if(t.key==='assign') loadAssignHistory()"
          >{{ t.label }}</div>
        </div>

        <!-- 客户跟踪（默认） -->
        <div v-show="activeRightTab === 'remark'" class="cp-remark-area">
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

          <!-- 备注后状态 -->
          <div class="remark-status-row">
            <span class="info-label">备注后状态</span>
            <el-select v-model="remarkNewStatus" size="small" style="width:120px">
              <el-option label="不变" :value="null" />
              <el-option v-for="(n,v) in options.statusMap" :key="v" :label="n" :value="Number(v)" />
            </el-select>
          </div>

          <!-- 备注输入 -->
          <div class="remark-input-area">
            <el-input
              v-model="remarkText"
              type="textarea"
              :rows="3"
              :placeholder="'输入跟进备注...'"
              resize="none"
            />
            <div style="margin-top:8px; display:flex; justify-content:space-between; align-items:center">
              <span style="font-size:12px; color:#888">{{ remarkText.length }}/200</span>
              <el-button type="primary" size="small" :loading="remarkLoading" @click="submitRemark">
                提交备注
              </el-button>
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
        <div v-show="activeRightTab === 'memo'" class="cp-remark-area">
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
        <div v-show="activeRightTab === 'call'" class="cp-call-area">
          <el-empty description="通话录音功能需对接第三方通话系统" :image-size="80" />
          <div style="padding:12px; font-size:13px; color:#888">
            当前显示placeholder，待对接点拨通等通话系统后自动展示录音记录。
          </div>
        </div>

        <!-- 分配记录 -->
        <div v-show="activeRightTab === 'assign'" class="cp-assign-area" v-loading="loadingAssign">
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

  <!-- 编辑客户弹窗 -->
  <el-dialog v-model="editVisible" title="编辑客户" width="480px">
    <el-form :model="editForm" label-width="80px">
      <el-form-item label="姓名"><el-input v-model="editForm.name" placeholder="客户姓名" /></el-form-item>
      <el-form-item label="性别"><el-radio-group v-model="editForm.gender"><el-radio :label="1">男</el-radio><el-radio :label="2">女</el-radio><el-radio :label="0">未知</el-radio></el-radio-group></el-form-item>
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

  <!-- 备忘新增对话框 -->
  <el-dialog v-model="memoDialogVisible" :title="memoDialogMode === 'quick' ? '快捷备忘' : '详细备忘'" width="460px">
    <el-form label-width="80px">
      <el-form-item label="备忘内容" required>
        <el-input v-model="memoText" type="textarea" :rows="memoDialogMode === 'quick' ? 2 : 4"
          :placeholder="memoDialogMode === 'quick' ? '输入备忘内容...' : '输入详细备注（建议包含：户籍地、工作情况、资产情况、负债征信、预判可做银行、预约时间等...）'"
          maxlength="500" show-word-limit />
      </el-form-item>
      <el-form-item v-if="memoDialogMode === 'detail'" label="状态">
        <el-select v-model="remarkNewStatus" size="small" style="width:140px">
          <el-option label="不变" :value="null" />
          <el-option v-for="(n,v) in options.statusMap" :key="v" :label="n" :value="Number(v)" />
        </el-select>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="memoDialogVisible=false">取消</el-button>
      <el-button type="success" :loading="memoLoading" @click="submitMemo">确认</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { inject } from 'vue'
import { ElMessage } from 'element-plus'
import { InfoFilled, ArrowDown } from '@element-plus/icons-vue'
import { getCustomer, updateCustomer, getRemarks, addRemark, toPool, toMustFollow, lockCustomer, markImportant, blacklist, getAllOptions, getCustomerAssignHistory } from '../../api'

const props = defineProps({
  customerId: { type: [Number, String], required: true },
  customerName: { type: String, default: '' }
})
const emits = defineEmits(['close', 'prev', 'next', 'updated'])

const openCustomerDetail = inject('openCustomerDetail')

const detail = ref({})
const remarks = ref([])
const memoRemarks = computed(() => remarks.value.filter(r => r.remark_type === 2))
const remarkText = ref('')
const remarkLoading = ref(false)
const remarkNewStatus = ref(null)
const loadingAssign = ref(false)
const assignHistory = ref([])
const options = ref({ statusMap: {}, loanTypeMap: {}, sources: [] })

// 备忘新增
const memoDialogVisible = ref(false)
const memoDialogMode = ref('quick')
const memoText = ref('')
const memoLoading = ref(false)

const handleQuickMemo = (mode) => {
  memoDialogMode.value = mode
  memoText.value = ''
  memoDialogVisible.value = true
}

const submitMemo = async () => {
  if (!memoText.value.trim()) return ElMessage.warning('请输入备忘内容')
  memoLoading.value = true
  try {
    const data = {
      content: memoText.value,
      remark_type: 2  // 备忘类型
    }
    if (memoDialogMode.value === 'detail' && remarkNewStatus.value !== null) {
      data.new_status = remarkNewStatus.value
    }
    await addRemark(props.customerId, data)
    ElMessage.success('备忘已添加')
    memoDialogVisible.value = false
    memoText.value = ''
    await loadDetail()
  } catch (e) { ElMessage.error(e.detail || '添加失败') }
  finally { memoLoading.value = false }
}

// 编辑客户
const editVisible = ref(false)
const editLoading = ref(false)
const editForm = reactive({ name:'', gender:0, city:'', age:0, loan_type:1, apply_amount:0, source:'' })

const openEdit = () => {
  const d = detail.value
  Object.assign(editForm, {
    name: d.name || '', gender: d.gender || 0, city: d.city || '',
    age: d.age || 0, loan_type: d.loan_type || 1, apply_amount: d.apply_amount || 0, source: d.source || ''
  })
  editVisible.value = true
}

const handleEditSave = async () => {
  if (!editForm.name && !editForm.city && !editForm.age) {
    ElMessage.warning('请至少填写一个要修改的字段')
    return
  }
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
  } catch (e) { ElMessage.error(e.detail || '保存失败') }
  finally { editLoading.value = false }
}

const activeInfoTab = ref('basic')
const activeRightTab = ref('remark')

const infoTabs = [
  { key: 'basic', label: '基本信息' },
  { key: 'identity', label: '身份信息' },
  { key: 'house', label: '房产信息' },
  { key: 'car', label: '车产信息' },
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

// 获取资质字段
const detailQ = (key) => detail.value?.qualifications?.[key]
const hasVal = (v) => v ? (typeof v === 'boolean' ? (v ? '有' : '无') : v) : '无'
const hasBool = (v) => v ? '有' : '无'
const monthDebt = computed(() => {
  const q = detail.value?.qualifications || {}
  const total = (Number(q.debt_house) || 0) + (Number(q.debt_car) || 0) + (Number(q.debt_net) || 0) + (Number(q.debt_other) || 0)
  return total.toLocaleString()
})

const fmt = (t) => t ? String(t).replace('T', ' ').substring(0, 16) : '—'

// 加载客户详情
const loadDetail = async () => {
  try {
    const res = await getCustomer(props.customerId)
    detail.value = res
    options.value = { statusMap: res._statusMap || {}, loanTypeMap: res._loanTypeMap || {}, sources: res._sources || [] }
    // 通知父组件更新名字
    if (res.name) emits('updated', res.name)
    // 加载备注
    const r = await getRemarks(props.customerId)
    remarks.value = r.items || []
  } catch (e) { ElMessage.error('加载失败') }
}

// 加载选项
const loadOptions = async () => {
  try {
    const allOpts = await getAllOptions()
    options.value = allOpts
  } catch (e) {}
}

// 加载分配历史
const loadAssignHistory = async () => {
  loadingAssign.value = true
  try {
    const res = await getCustomerAssignHistory(props.customerId)
    assignHistory.value = res.items || []
  } catch (e) { assignHistory.value = [] }
  finally { loadingAssign.value = false }
}

// 保存字段
const saveField = async (field) => {
  try {
    await updateCustomer(props.customerId, { [field]: detail.value[field] })
    ElMessage.success('已保存')
  } catch (e) { ElMessage.error('保存失败') }
}

// 切换重要
const toggleImportant = async () => {
  try {
    await markImportant(props.customerId)
    detail.value.is_important = detail.value.is_important ? 0 : 1
    ElMessage.success(detail.value.is_important ? '已标记为重要' : '已取消重要')
  } catch (e) { ElMessage.error('操作失败') }
}

// 切换锁定
const toggleLock = async () => {
  try {
    await lockCustomer(props.customerId)
    detail.value.is_locked = detail.value.is_locked ? 0 : 1
    ElMessage.success(detail.value.is_locked ? '已锁定' : '已解锁')
  } catch (e) { ElMessage.error('操作失败') }
}

// 加入公共池
const handleToPool = async () => {
  try {
    await toPool(props.customerId)
    ElMessage.success('已加入公共池')
    emits('close')
  } catch (e) { ElMessage.error('操作失败') }
}

// 加入必跟进
const handleToMustFollow = async () => {
  try {
    await toMustFollow(props.customerId)
    ElMessage.success('已加入必跟进')
    emits('close')
  } catch (e) { ElMessage.error('操作失败') }
}

// 拉黑
const toBlacklist = async () => {
  try {
    await blacklist(props.customerId)
    detail.value.is_blacklisted = 1
    ElMessage.success('已拉黑')
  } catch (e) { ElMessage.error('操作失败') }
}

// 应用快捷备注
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
    await loadDetail()
  } catch (e) { ElMessage.error('提交失败') }
  finally { remarkLoading.value = false }
}

watch(() => props.customerId, () => loadDetail(), { immediate: true })

onMounted(() => { loadOptions() })
</script>

<style scoped>
.cp-page {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: white;
  overflow: hidden;
}

/* 顶部操作栏 */
.cp-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  background: linear-gradient(135deg, #fff5f8 0%, #fff 100%);
  border-bottom: 1px solid #FCE4EC;
  flex-shrink: 0;
  gap: 8px;
  flex-wrap: wrap;
}
.cp-header-left { display: flex; align-items: center; gap: 4px; flex-wrap: wrap; }
.cp-header-right { display: flex; align-items: center; gap: 4px; flex-wrap: wrap; }

/* 主体 */
.cp-body {
  flex: 1;
  display: flex;
  overflow: hidden;
}

/* 左侧信息区 */
.cp-left {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border-right: 1px solid #f0f0f0;
  min-width: 0;
}

/* Tab导航 */
.cp-tabs {
  display: flex;
  border-bottom: 2px solid #FCE4EC;
  background: #fff5f8;
  flex-shrink: 0;
  overflow-x: auto;
}
.cp-tabs::-webkit-scrollbar { height: 0; }
.cp-tab {
  padding: 8px 14px;
  cursor: pointer;
  font-size: 13px;
  color: #888;
  white-space: nowrap;
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  transition: all 0.15s;
}
.cp-tab:hover { color: #E91E63; }
.cp-tab.active { color: #E91E63; border-bottom-color: #E91E63; font-weight: 600; }

/* 信息区 */
.cp-info-area {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
}
.info-section { }
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
.cp-right {
  flex: 0 0 280px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.cp-right-tabs {
  display: flex;
  border-bottom: 2px solid #FCE4EC;
  background: #fff5f8;
  flex-shrink: 0;
}
.cp-right-tab {
  padding: 8px 14px;
  cursor: pointer;
  font-size: 13px;
  color: #888;
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  transition: all 0.15s;
}
.cp-right-tab:hover { color: #E91E63; }
.cp-right-tab.active { color: #E91E63; border-bottom-color: #E91E63; font-weight: 600; }

.cp-remark-area {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

/* 快捷按钮 */
.quick-btns {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}
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

/* 备注提示 */
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

.remark-status-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.remark-input-area {
  background: #fafafa;
  padding: 8px;
  border-radius: 6px;
  border: 1px solid #f0f0f0;
}

.remark-list {
  flex: 1;
  overflow-y: auto;
}
.remark-item {
  padding: 8px 0;
  border-bottom: 1px solid #f5f5f5;
}
.remark-item-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 4px;
}
.remark-item-advisor { font-size: 12px; color: #333; font-weight: 500; }
.remark-item-time { font-size: 11px; color: #aaa; margin-left: auto; }
.remark-item-content { font-size: 13px; color: #555; line-height: 1.5; }

/* 通话录音区 */
.cp-call-area { padding: 12px; }

/* 分配记录区 */
.cp-assign-area { padding: 12px; overflow-y: auto; }
.assign-item { padding: 8px 0; border-bottom: 1px solid #f5f5f5; }
.assign-time { font-size: 11px; color: #aaa; margin-bottom: 4px; }
.assign-content { font-size: 13px; display: flex; align-items: center; flex-wrap: wrap; }
</style>
