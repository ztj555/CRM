<template>
  <div class="cd-page" v-loading="loading">

    <!-- 区域1：上方表单内容区 -->
    <div class="cd-main">
      <div class="cd-info-content">
        <!-- 胶囊Tab栏 -->
        <div class="cd-tab-bar">
          <div
            v-for="t in infoTabs" :key="t.key"
            class="cd-tab"
            :class="{ active: activeInfoTab === t.key }"
            @click="activeInfoTab = t.key"
          >{{ t.label }}</div>
        </div>

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
        <div v-show="activeInfoTab === 'identity'" class="cd-info-grid">
          <div class="grid-item"><span class="grid-label">户籍</span><span class="grid-value">{{ detailQ('huji_city') || '—' }}</span></div>
          <div class="grid-item"><span class="grid-label">婚姻</span><span class="grid-value">{{ detailQ('marriage') || '—' }}</span></div>
          <div class="grid-item"><span class="grid-label">学历</span><span class="grid-value">{{ detailQ('education') || '—' }}</span></div>
          <div class="grid-item"><span class="grid-label">职业</span><span class="grid-value">{{ detailQ('occupation') || '—' }}</span></div>
          <div class="grid-item"><span class="grid-label">月收入</span><span class="grid-value">{{ detailQ('salary_amount') || '—' }}</span></div>
          <div class="grid-item"><span class="grid-label">收入方式</span><span class="grid-value">{{ detailQ('income_type') || '—' }}</span></div>
        </div>
        <div v-show="activeInfoTab === 'estate'" class="cd-info-grid">
          <div class="grid-item"><span class="grid-label">房产状况</span><span class="grid-value" :class="hasEstate ? 'val-yes' : 'val-no'">{{ hasEstate ? '有' : '无' }}</span></div>
          <template v-if="hasEstate">
            <div class="grid-item"><span class="grid-label">房屋类型</span><span class="grid-value">{{ detailQ('real_estate.type') || '—' }}</span></div>
            <div class="grid-item"><span class="grid-label">房屋面积</span><span class="grid-value">{{ detailQ('real_estate.area') ? detailQ('real_estate.area') + 'm²' : '—' }}</span></div>
            <div class="grid-item"><span class="grid-label">市场估值</span><span class="grid-value">{{ detailQ('real_estate.market_value') ? detailQ('real_estate.market_value') + '万' : '—' }}</span></div>
            <div class="grid-item"><span class="grid-label">抵押状态</span><span class="grid-value">{{ detailQ('real_estate.mortgage_status') || '—' }}</span></div>
            <div class="grid-item"><span class="grid-label">房屋性质</span><span class="grid-value">{{ detailQ('real_estate.property_type') || '—' }}</span></div>
            <div class="grid-item grid-item--full"><span class="grid-label">房产地址</span><span class="grid-value">{{ detailQ('real_estate.address') || '—' }}</span></div>
          </template>
        </div>
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
        <div v-show="activeInfoTab === 'credit'" class="cd-info-grid">
          <div class="grid-item"><span class="grid-label">征信等级</span><span class="grid-value">{{ detailQ('credit.credit_grade') || '—' }}</span></div>
          <div class="grid-item"><span class="grid-label">信用卡额度</span><span class="grid-value">{{ detailQ('credit.credit_limit') ? detailQ('credit.credit_limit') + '万' : '—' }}</span></div>
          <div class="grid-item"><span class="grid-label">近6月查询</span><span class="grid-value">{{ detailQ('credit.query_count') || '—' }}</span></div>
          <div class="grid-item"><span class="grid-label">微粒贷额度</span><span class="grid-value">{{ detailQ('credit.weili_amount') || '—' }}</span></div>
          <div class="grid-item"><span class="grid-label">网贷平台数</span><span class="grid-value">{{ detailQ('credit.online_loan_count') || '—' }}</span></div>
          <div class="grid-item"><span class="grid-label">是否有逾期</span><span class="grid-value">{{ {0:'无',1:'偶尔',2:'较多'}[detailQ('credit.has_overdue')] || '—' }}</span></div>
        </div>
        <div v-show="activeInfoTab === 'liabilities'" class="cd-info-grid">
          <div class="grid-item"><span class="grid-label">信用卡已用</span><span class="grid-value">{{ detailQ('liabilities.credit_card_used') ? detailQ('liabilities.credit_card_used') + '万' : '无' }}</span></div>
          <div class="grid-item"><span class="grid-label">房贷月还款</span><span class="grid-value">{{ detailQ('liabilities.mortgage_monthly') ? detailQ('liabilities.mortgage_monthly') + '元/月' : '无' }}</span></div>
          <div class="grid-item"><span class="grid-label">车贷月还款</span><span class="grid-value">{{ detailQ('liabilities.car_loan_monthly') ? detailQ('liabilities.car_loan_monthly') + '元/月' : '无' }}</span></div>
          <div class="grid-item"><span class="grid-label">网贷月还款</span><span class="grid-value">{{ detailQ('liabilities.online_loan_monthly') ? detailQ('liabilities.online_loan_monthly') + '元/月' : '无' }}</span></div>
          <div class="grid-item"><span class="grid-label">其他月还款</span><span class="grid-value">{{ detailQ('liabilities.other_monthly') ? detailQ('liabilities.other_monthly') + '元/月' : '无' }}</span></div>
          <div class="grid-item grid-item--total"><span class="grid-label">月负债合计</span><span class="grid-value val-total">{{ totalLiabilities }}元/月</span></div>
        </div>
        <div v-show="activeInfoTab === 'needs'" class="cd-info-grid">
          <div class="grid-item"><span class="grid-label">贷款用途</span><span class="grid-value">{{ detailQ('needs.purpose') || '—' }}</span></div>
          <div class="grid-item"><span class="grid-label">期望期限</span><span class="grid-value">{{ detailQ('needs.expect_term') || '—' }}</span></div>
          <div class="grid-item"><span class="grid-label">紧迫程度</span><span class="grid-value">{{ detailQ('needs.urgency') || '—' }}</span></div>
          <div class="grid-item grid-item--full"><span class="grid-label">其他说明</span><span class="grid-value">{{ detailQ('needs.description') || '—' }}</span></div>
        </div>
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

    <!-- 区域3：下方操作区（主操作区域） -->
    <div class="cd-sidebar">
      <!-- 当前状态 -->
      <div class="sd-block">
        <div class="sd-block-title">当前状态</div>
        <div class="sd-status-row">
          <el-tag size="small">{{ options.statusMap[detail.status] || '未知' }}</el-tag>
          <span class="sd-phone">{{ detail.phone || '—' }}</span>
        </div>
      </div>
      <!-- 操作栏（原顶部栏，移到此处） -->
      <div class="sd-block">
        <div class="sd-topbar-left" style="margin-bottom:6px">
          <span class="cd-id">ID: {{ detail.id }}</span>
          <span class="cd-name">{{ detail.name || '未知客户' }}</span>
          <el-tag v-if="detail.is_important" type="danger" size="small" effect="plain">重要</el-tag>
          <el-tag v-if="detail.is_locked" type="warning" size="small" effect="plain">锁定</el-tag>
          <el-tag v-if="detail.is_blacklisted" type="info" size="small" effect="plain">黑名单</el-tag>
          <el-tag v-if="detail.source" size="small" effect="plain">{{ detail.source }}</el-tag>
          <el-tag v-if="detail.city" size="small" effect="plain">{{ detail.city }}</el-tag>
        </div>
        <div class="sd-topbar-right" style="display:flex;align-items:center;gap:4px;flex-wrap:wrap">
          <el-button size="small" :disabled="!canNavigatePrev" @click="doNavigate('prev')" title="上一位客户" style="margin-right:4px">
            <el-icon><ArrowLeft /></el-icon>上一位
          </el-button>
          <el-button size="small" :disabled="!canNavigateNext" @click="doNavigate('next')" title="下一位客户">
            下一位<el-icon><ArrowRight /></el-icon>
          </el-button>
          <span class="cd-lbl" style="margin-left:8px">星级</span>
          <el-rate v-model="detail.star_level" :max="6" size="small" void-color="#ccc" @change="saveField('star_level')" style="margin-right:6px" />
          <span class="cd-lbl">状态</span>
          <el-select v-model="detail.status" size="small" style="width:100px;margin-right:4px" @change="saveField('status')">
            <el-option v-for="(n,v) in options.statusMap" :key="v" :label="n" :value="Number(v)" />
          </el-select>
          <el-button size="small" :type="detail.is_important ? 'danger' : ''" plain @click="toggleImportant">{{ detail.is_important ? '取消' : '重要' }}</el-button>
          <el-button size="small" :type="detail.is_locked ? 'warning' : ''" plain @click="toggleLock">{{ detail.is_locked ? '解锁' : '锁定' }}</el-button>
          <el-button size="small" plain @click="openEdit">编辑</el-button>
          <el-button size="small" type="warning" plain @click="handleToPool">公池</el-button>
          <el-button size="small" type="success" plain @click="handleToMustFollow">必跟</el-button>
          <el-button size="small" :type="detail.is_blacklisted ? 'info' : 'danger'" plain @click="handleBlacklist">{{ detail.is_blacklisted ? '移除' : '拉黑' }}</el-button>
          <el-button v-if="props.customerId" size="small" @click="emit('close')">关闭面板</el-button>
        </div>
      </div>
      <!-- 快捷备注 -->
      <div class="sd-block">
        <div class="sd-block-title">快捷备注<span class="sd-tip">（点击快速填入，再补充细节）</span></div>
        <div class="sd-quick-tags">
          <span v-for="r in quickRemarks" :key="r" class="sd-quick-tag" @click="applyQuickRemark(r)">{{ r }}</span>
        </div>
      </div>
      <!-- 新增跟进 -->
      <div class="sd-block">
        <div class="sd-block-title">新增跟进记录</div>
        <div class="sd-remark-tip">
          💡 提示：记录客户意向、拒贷原因、资金需求、下一步动作等关键信息
        </div>
        <el-input v-model="remarkText" type="textarea" :rows="3" :maxlength="200" show-word-limit placeholder="记录跟进内容，如：客户想贷30万，征信良好，需要3天内批复..." resize="none" class="sd-textarea" />
        <div class="sd-remark-bottom">
          <span class="sd-lbl">备注后状态</span>
          <el-select v-model="remarkNewStatus" size="small" clearable placeholder="不变" class="sd-status-select">
            <el-option v-for="(n,v) in options.statusMap" :key="v" :label="n" :value="Number(v)" />
          </el-select>
        </div>
        <el-button type="danger" size="small" class="sd-submit-btn" :loading="remarkLoading" @click="submitRemark">确定提交</el-button>
      </div>
      <!-- 历史记录Tab：备忘 / 顾问记录 / 主管点评 -->
      <div class="sd-block sd-history-block">
        <div class="sd-tab-bar">
          <div v-for="t in rightTabs" :key="t.key" class="sd-tab" :class="{ active: activeRightTab === t.key }" @click="onRightTabClick(t.key)">{{ t.label }}</div>
        </div>
        <!-- 备忘 -->
        <div v-show="activeRightTab === 'memo'" class="sd-history-list">
          <div v-if="!memoRemarks.length" class="sd-empty">暂无备忘记录</div>
          <div v-for="(r, index) in memoRemarks" :key="r.id" class="sd-history-item sd-item-memo">
            <div class="sd-history-header">
              <span class="sd-remark-index">{{ index + 1 }}.</span>
              <el-tag size="small" type="success">备忘</el-tag>
              <span class="sd-history-advisor">{{ r.advisor_name_with_title || (r.advisor_name + '顾问') || '顾问' }}</span>
              <span class="sd-history-time">{{ r.formatted_time || fmt(r.created_at) }}</span>
            </div>
            <div class="sd-history-content">{{ r.content }}</div>
          </div>
        </div>
        <!-- 顾问跟进记录 -->
        <div v-show="activeRightTab === 'remark'" class="sd-history-list">
          <div v-if="!advisorRemarks.length" class="sd-empty">暂无顾问跟进记录</div>
          <div v-for="(r, index) in advisorRemarks" :key="r.id" class="sd-history-item sd-item-advisor">
            <div class="sd-history-header">
              <span class="sd-remark-index">{{ index + 1 }}.</span>
              <span class="sd-remark-status">{{ r.statusText || '待跟进' }}</span>
              <span class="sd-history-advisor">{{ r.advisor_name_with_title || (r.advisor_name + '顾问') || '顾问' }}</span>
              <span class="sd-history-time">{{ r.formatted_time || fmt(r.created_at) }}</span>
            </div>
            <div class="sd-history-content">{{ r.content }}</div>
          </div>
        </div>
        <!-- 主管点评 -->
        <div v-show="activeRightTab === 'supervisor'" class="sd-history-list">
          <div v-if="!supervisorRemarks.length" class="sd-empty">暂无主管点评记录</div>
          <div v-for="(r, index) in supervisorRemarks" :key="r.id" class="sd-history-item sd-item-supervisor">
            <div class="sd-history-header">
              <span class="sd-remark-index">{{ index + 1 }}.</span>
              <el-tag size="small" type="warning">主管点评</el-tag>
              <span class="sd-history-advisor">{{ r.advisor_name_with_title || (r.advisor_name + '顾问') || '主管' }}</span>
              <span class="sd-history-time">{{ r.formatted_time || fmt(r.created_at) }}</span>
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
              <el-tag size="small" style="margin-left:4px">{{ poolTypeMap[a.pool_type] || a.pool_type }}</el-tag>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 编辑弹窗 -->
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
import { ref, reactive, computed, watch, onMounted, inject } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getCustomer, updateCustomer, getRemarks, addRemark, toPool, toMustFollow, lockCustomer, markImportant, blacklist, getAllOptions, getCustomerAssignHistory } from '../../api'

const allCustomerIds = inject('allCustomerIds', ref([]))
const navigateCustomer = inject('navigateCustomer', null)

const canNavigatePrev = computed(() => {
  if (!allCustomerIds.value.length || !customerId.value) return false
  const idx = allCustomerIds.value.indexOf(Number(customerId.value))
  return idx > 0
})
const canNavigateNext = computed(() => {
  if (!allCustomerIds.value.length || !customerId.value) return false
  const idx = allCustomerIds.value.indexOf(Number(customerId.value))
  return idx >= 0 && idx < allCustomerIds.value.length - 1
})

const doNavigate = (dir) => {
  if (!navigateCustomer) return
  navigateCustomer(dir)
}

const props = defineProps({
  customerId: { type: [Number, String], default: null }
})
const emit = defineEmits(['close', 'updated'])

const route = useRoute()
const router = useRouter()

const customerId = computed(() => {
  if (props.customerId != null) return Number(props.customerId)
  return Number(route.query.id) || Number(route.params.id) || null
})

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
  { key: 'memo', label: '备忘' },
  { key: 'remark', label: '顾问记录' },
  { key: 'supervisor', label: '主管点评' },
  { key: 'assign', label: '分配记录' },
]

const quickRemarks = [
  '未接', '拒接', '空号', '停机', '关机', '无法接通',
  '不需要了', '通话中', '接了就挂', '用户正忙',
  '贷款即挂', '外地号码', '现在不方便', '不是本人',
  '微信待通过', '已加微信', '已发短信',
]

const remarkTypeMap = { 0: '跟进', 1: '主管点评', 2: '备忘' }
const remarkTagType = { 0: '', 1: 'warning', 2: 'success' }
const poolTypeMap = { 1: '我的客户', 2: '再分配', 3: '公共池', 4: '必跟进' }

const hasEstate = computed(() => !!(quals.value?.real_estate?.type || quals.value?.real_estate?.property_type))
const hasVehicle = computed(() => !!(quals.value?.vehicle?.type))
const hasInsurance = computed(() => !!(quals.value?.insurance?.company || quals.value?.insurance?.type))
const memoRemarks = computed(() => remarks.value.filter(r => r.remark_type === 2))
const advisorRemarks = computed(() => remarks.value.filter(r => r.remark_type === 0))
const supervisorRemarks = computed(() => remarks.value.filter(r => r.remark_type === 1))
const onRightTabClick = (key) => {
  activeRightTab.value = key
  if (key === 'assign') loadAssignHistory()
}

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
  try { const res = await getRemarks(customerId.value); remarks.value = res.items || [] } catch (e) {}
}

const loadAssignHistory = async () => {
  loadingAssign.value = true
  try { const res = await getCustomerAssignHistory(customerId.value); assignHistory.value = res.items || [] }
  catch (e) { assignHistory.value = [] }
  finally { loadingAssign.value = false }
}

const saveField = async (field) => {
  try { await updateCustomer(customerId.value, { [field]: detail.value[field] }); ElMessage.success('已保存') }
  catch (e) { ElMessage.error('保存失败') }
}

const saveQuals = async () => {
  try { await updateCustomer(customerId.value, { qualifications: quals.value }); ElMessage.success('已保存') }
  catch (e) { ElMessage.error('保存失败') }
}

const toggleImportant = async () => {
  try {
    await markImportant(customerId.value)
    detail.value.is_important = detail.value.is_important ? 0 : 1
    ElMessage.success(detail.value.is_important ? '已标记重要' : '已取消重要')
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
  try { await toMustFollow(customerId.value); ElMessage.success('已加入必跟进'); router.push('/team-customers') }
  catch (e) { ElMessage.error('操作失败') }
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
/* ===== 整体：垂直Flex，三块纵向排列 ===== */
.cd-page {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #e8e8e8;
  overflow: hidden;
  font-family: 'Microsoft YaHei', 'SimSun', sans-serif;
}

/* 区域2：中间信息栏（固定高度） */
.cd-topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 4px 10px;
  background: #f0f0f0;
  border-bottom: 1px solid #c0c0c0;
  flex-shrink: 0;
  gap: 6px;
  min-height: 38px;
  flex-wrap: wrap;
}
.cd-topbar-left {
  display: flex;
  align-items: center;
  gap: 5px;
  flex-wrap: wrap;
}
.cd-topbar-right {
  display: flex;
  align-items: center;
  gap: 3px;
  flex-wrap: wrap;
}
.cd-id {
  font-size: 11px;
  color: #808080;
  font-weight: 400;
}
.cd-name {
  font-size: 13px;
  font-weight: 700;
  color: #111;
}
.cd-lbl {
  font-size: 11px;
  color: #666;
  margin-right: 2px;
  white-space: nowrap;
}

/* 区域1+3 横向包裹层 */
.cd-body {
  flex: 1;
  display: flex;
  overflow: hidden;
  min-height: 0;
}

/* 区域1：上方表单区（高度自适应内容） */
.cd-main {
  flex: 0 0 auto;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: #fff;
  border-bottom: 1px solid #c0c0c0;
}

/* 胶囊Tab栏 */
.cd-tab-bar {
  display: flex;
  background: #f0f0f0;
  padding: 3px 6px;
  gap: 2px;
  border-bottom: 1px solid #c0c0c0;
  flex-shrink: 0;
  overflow-x: auto;
}
.cd-tab-bar::-webkit-scrollbar { height: 0; }
.cd-tab {
  padding: 4px 14px;
  cursor: pointer;
  font-size: 12px;
  color: #333;
  white-space: nowrap;
  border-radius: 11px;
  background: transparent;
  transition: all 0.15s;
  font-weight: 500;
  border: 1px solid transparent;
}
.cd-tab:hover {
  background: #e0e0e0;
  color: #111;
  border-color: #c0c0c0;
}
.cd-tab.active {
  color: #fff;
  background: #409eff;
  font-weight: 600;
  border-color: #409eff;
}

/* 表单内容区 */
.cd-info-content {
  flex: 1;
  overflow-y: auto;
  padding: 6px;
  background: #fff;
}

/* 密集Grid */
.cd-info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 2px;
  font-size: 12px;
}
.grid-item {
  display: flex;
  min-height: 28px;
  align-items: stretch;
}
.grid-item:nth-child(2n) { border-right: none; }
.grid-item--full {
  grid-column: 1 / -1;
  border-right: none;
}
.grid-item--total {
  grid-column: 1 / -1;
  background: #fff8f0;
}
.grid-section-title {
  grid-column: 1 / -1;
  background: #f5f7fa;
  padding: 3px 8px;
  font-size: 11px;
  font-weight: 700;
  color: #409eff;
  letter-spacing: 1px;
}
.grid-label {
  width: 95px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding: 3px 8px 3px 4px;
  background: #f7f8fa;
  color: #555;
  font-size: 11px;
  font-weight: 600;
  white-space: nowrap;
}
.grid-value {
  flex: 1;
  display: flex;
  align-items: center;
  padding: 3px 8px;
  font-size: 12px;
  color: #222;
  word-break: break-all;
  min-height: 28px;
}
.val-yes { color: #67c23a; font-weight: 600; }
.val-no  { color: #aaa; }
.val-total { color: #e6a23c; font-weight: 700; font-size: 13px; }

/* 区域3：下方主操作区（占满剩余空间，可滚动） */
.cd-sidebar {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  min-height: 0;
  background: #f5f6f8;
}

/* 右侧区块 */
.sd-block {
  padding: 6px 8px;
  border-bottom: 1px solid #d0d0d0;
  background: #fff;
}
.sd-block-title {
  font-size: 11px;
  font-weight: 700;
  color: #333;
  margin-bottom: 4px;
  padding-bottom: 3px;
  border-bottom: 1px solid #e8e8e8;
  letter-spacing: 0.5px;
}
.sd-block-title::before {
  content: '▋';
  color: #409eff;
  font-size: 9px;
  margin-right: 3px;
}
.sd-status-row {
  display: flex;
  align-items: center;
  gap: 6px;
}
.sd-phone {
  font-size: 12px;
  color: #333;
  font-family: 'Courier New', monospace;
  letter-spacing: 0.5px;
}
.sd-quick-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 3px;
}
.sd-quick-tag {
  font-size: 10px;
  cursor: pointer;
  padding: 1px 5px;
  color: #c0392b;
  border: 1px solid #f5c6cb;
  background: #fff5f5;
  transition: all 0.15s;
  white-space: nowrap;
}
.sd-quick-tag:hover {
  background: #ffeaea;
  border-color: #e74c3c;
  color: #a01818;
}
.sd-textarea :deep(.el-textarea__inner) {
  font-size: 12px;
  border-radius: 2px;
  border-color: #c0c0c0;
}
.sd-remark-bottom {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 4px;
}
.sd-lbl {
  font-size: 11px;
  color: #888;
  white-space: nowrap;
}
.sd-status-select {
  width: 100px;
}
.sd-submit-btn {
  width: 100% !important;
  margin-top: 5px;
  border-radius: 2px;
  font-weight: 600;
}
.sd-history-block {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 0;
  border-bottom: none;
  background: #fff;
  min-height: 0;
}
.sd-tab-bar {
  display: flex;
  background: #f0f0f0;
  border-bottom: 1px solid #c0c0c0;
  flex-shrink: 0;
  padding: 0 6px;
  gap: 0;
}
.sd-tab {
  padding: 5px 10px;
  cursor: pointer;
  font-size: 11px;
  color: #555;
  border-bottom: 2px solid transparent;
  margin-bottom: -1px;
  white-space: nowrap;
}
.sd-tab:hover { color: #222; background: #e8e8e8; }
.sd-tab.active { color: #409eff; border-bottom-color: #409eff; font-weight: 600; }

.sd-history-list {
  flex: 1;
  overflow-y: auto;
  padding: 5px 8px;
}
.sd-empty {
  text-align: center;
  color: #ccc;
  font-size: 11px;
  padding: 16px 0;
}
.sd-history-item {
  padding: 4px 0;
  border-bottom: 1px solid #f0f0f0;
}
.sd-history-item:last-child { border-bottom: none; }
.sd-history-header {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-bottom: 2px;
}
.sd-remark-index {
  font-size: 11px;
  font-weight: 700;
  color: #409eff;
  min-width: 20px;
}
.sd-remark-status {
  font-size: 10px;
  color: #e6a23c;
  font-weight: 600;
  margin-right: 4px;
}
.sd-history-advisor {
  font-size: 10px;
  color: #333;
  font-weight: 600;
}
.sd-history-time {
  font-size: 10px;
  color: #ccc;
  margin-left: auto;
}
.sd-history-content {
  font-size: 11px;
  color: #555;
  line-height: 1.4;
  word-break: break-all;
}
.sd-assign-item {
  padding: 4px 0;
  border-bottom: 1px solid #f0f0f0;
}
.sd-assign-time {
  font-size: 10px;
  color: #ccc;
  display: block;
  margin-bottom: 2px;
}
.sd-assign-flow {
  font-size: 11px;
  color: #333;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 2px;
}
.sd-arrow { color: #e6a23c; font-weight: bold; font-size: 12px; }
.sd-tip {
  font-size: 10px;
  color: #999;
  font-weight: 400;
  margin-left: 4px;
}
.sd-remark-tip {
  font-size: 11px;
  color: #e6a23c;
  background: #fdf6ec;
  border: 1px solid #faecd8;
  border-radius: 2px;
  padding: 3px 6px;
  margin-bottom: 4px;
  line-height: 1.4;
}
.sd-item-memo { border-left: 3px solid #67c23a; padding-left: 6px; }
.sd-item-advisor { border-left: 3px solid #409eff; padding-left: 6px; }
.sd-item-supervisor { border-left: 3px solid #e6a23c; padding-left: 6px; }
</style>
