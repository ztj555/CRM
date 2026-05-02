<template>
  <div>
    <div class="page-header">
      <h3>系统设置</h3>
    </div>

    <el-card style="margin:12px 0">
      <!-- Tab导航 -->
      <div class="settings-tabs">
        <div
          v-for="tab in tabs"
          :key="tab.key"
          class="settings-tab"
          :class="{ active: activeTab === tab.key }"
          @click="activeTab = tab.key"
        >
          <el-icon><component :is="tab.icon" /></el-icon>
          {{ tab.label }}
        </div>
      </div>

      <!-- Tab1: 个人信息 -->
      <div v-show="activeTab === 'info'" class="tab-content">
        <div class="info-avatar-section">
          <div class="avatar-preview">
            <div class="avatar-circle">{{ user?.real_name?.charAt(0) || '管' }}</div>
          </div>
          <div class="avatar-info">
            <h4>{{ user?.real_name }}</h4>
            <p style="color:#888; font-size:13px; margin-top:4px">
              <el-tag size="small" type="danger">{{ roleText }}</el-tag>
              <span style="margin-left:8px">账号：{{ user?.username }}</span>
            </p>
          </div>
        </div>

        <el-divider />

        <el-form :model="infoForm" label-width="100px" style="max-width:500px">
          <el-form-item label="姓名">
            <el-input v-model="infoForm.real_name" />
          </el-form-item>
          <el-form-item label="账号">
            <el-input :model-value="user?.username" disabled />
          </el-form-item>
          <el-form-item label="角色">
            <el-tag type="danger">{{ roleText }}</el-tag>
          </el-form-item>
          <el-form-item label="所属部门">
            <el-input :model-value="user?.dept_name || '杭州一区-一区二部2'" disabled />
          </el-form-item>
          <el-form-item label="日分配上限">
            <el-input-number v-model="infoForm.daily_quota" :min="0" :max="500" />
            <span style="color:#888; font-size:12px; margin-left:8px">条/天</span>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :loading="infoSaving" @click="saveInfo">保存信息</el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- Tab2: 修改密码 -->
      <div v-show="activeTab === 'password'" class="tab-content">
        <el-form :model="pwdForm" :rules="pwdRules" ref="pwdFormRef" label-width="110px" style="max-width:450px">
          <el-form-item label="原密码" prop="oldPassword">
            <el-input v-model="pwdForm.oldPassword" type="password" show-password placeholder="请输入原密码" />
          </el-form-item>
          <el-form-item label="新密码" prop="newPassword">
            <el-input v-model="pwdForm.newPassword" type="password" show-password placeholder="请输入新密码（6位以上）" />
          </el-form-item>
          <el-form-item label="确认新密码" prop="confirmPassword">
            <el-input v-model="pwdForm.confirmPassword" type="password" show-password placeholder="请再次输入新密码" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :loading="pwdSaving" @click="handleChangePwd">确认修改</el-button>
            <el-button @click="pwdForm = { oldPassword:'', newPassword:'', confirmPassword:'' }">重置</el-button>
          </el-form-item>
        </el-form>

        <el-alert
          title="密码安全提示"
          type="info"
          :closable="false"
          style="margin-top:16px; max-width:450px; border-radius:8px"
          show-icon
        >
          <template #default>
            密码长度不能少于6位，建议使用字母+数字组合，定期更换密码可以提高账户安全。
          </template>
        </el-alert>
      </div>

      <!-- Tab3: 系统设置 -->
      <div v-show="activeTab === 'system'" class="tab-content">
        <el-form label-width="160px" style="max-width:700px">
          <el-form-item label="接受新数据">
            <el-switch
              v-model="settings.accept_new_data"
              :active-value="1"
              :inactive-value="0"
              @change="saveSettings"
            />
            <div class="setting-tip">
              开启后，系统会为您自动分配新客户。关闭则暂停接收新客户分配。
            </div>
          </el-form-item>

          <el-divider content-position="left">隐藏客户列表列</el-divider>
          <div class="setting-tip" style="margin-bottom:12px">
            选中的列将在「我的客户」列表中隐藏，方便顾问只关注关心的数据。
          </div>

          <el-checkbox-group v-model="hiddenCols">
            <el-row :gutter="16">
              <el-col :span="8" v-for="col in colOptions" :key="col.value">
                <el-checkbox :label="col.value" style="height:36px">{{ col.label }}</el-checkbox>
              </el-col>
            </el-row>
          </el-checkbox-group>

          <el-form-item style="margin-top:16px">
            <el-button type="primary" @click="saveSettings">保存设置</el-button>
            <el-button @click="hiddenCols = []">重置</el-button>
          </el-form-item>

          <!-- 管理员全局设置 -->
          <template v-if="isManager">
            <el-divider content-position="left">登录安全</el-divider>
            <el-form-item label="晚上10:30后登录">
              <el-radio-group v-model="sysSettings.night_login_allowed">
                <el-radio :value="1">允许登录</el-radio>
                <el-radio :value="0">禁止登录</el-radio>
              </el-radio-group>
              <div class="setting-tip">注意：公司负责人不受此限制，主管和顾问受控制</div>
            </el-form-item>
            <el-form-item label="IP白名单登录">
              <el-switch v-model="sysSettings.ip_whitelist_open" :active-value="1" :inactive-value="0" />
              <div class="setting-tip">开启后，仅白名单IP可登录系统</div>
            </el-form-item>
            <el-form-item v-if="sysSettings.ip_whitelist_open" label="白名单IP列表">
              <el-input v-model="ipWhitelistText" type="textarea" :rows="3" placeholder="每行一个IP，如 192.168.1.100" />
            </el-form-item>
            <el-form-item label="顾问手机登录">
              <el-switch v-model="sysSettings.mobile_login_allowed" :active-value="1" :inactive-value="0" />
            </el-form-item>

            <el-divider content-position="left">接待开关权限</el-divider>
            <el-form-item label="区长可关闭接客">
              <el-switch v-model="sysSettings.district_manager_can_close_jieke" :active-value="1" :inactive-value="0" />
            </el-form-item>
            <el-form-item label="主管可关闭接客">
              <el-switch v-model="sysSettings.manager_can_close_jieke" :active-value="1" :inactive-value="0" />
            </el-form-item>
            <el-form-item label="顾问可关闭接客">
              <el-switch v-model="sysSettings.advisor_can_close_jieke" :active-value="1" :inactive-value="0" />
            </el-form-item>
            <el-form-item label="新顾问默认接受数据">
              <el-switch v-model="sysSettings.accept_new_data_default" :active-value="1" :inactive-value="0" />
            </el-form-item>

            <el-divider content-position="left">数据可见性</el-divider>
            <el-form-item label="手机号隐私保护">
              <el-select v-model="sysSettings.phone_privacy_mode" style="width:240px">
                <el-option :value="0" label="都不加*" />
                <el-option :value="1" label="顾问手机号加*" />
                <el-option :value="2" label="主管手机号加*" />
                <el-option :value="3" label="主管+顾问都加*" />
              </el-select>
            </el-form-item>
            <el-form-item label="区长看来源">
              <el-switch v-model="sysSettings.district_manager_see_source" :active-value="1" :inactive-value="0" />
            </el-form-item>
            <el-form-item label="主管看来源">
              <el-switch v-model="sysSettings.manager_see_source" :active-value="1" :inactive-value="0" />
            </el-form-item>
            <el-form-item label="顾问看来源">
              <el-switch v-model="sysSettings.advisor_see_source" :active-value="1" :inactive-value="0" />
            </el-form-item>
            <el-form-item label="允许拉黑客户">
              <el-switch v-model="sysSettings.allow_blacklist" :active-value="1" :inactive-value="0" />
            </el-form-item>

            <el-divider content-position="left">公共池与排行榜</el-divider>
            <el-form-item label="公共池可见性">
              <el-select v-model="sysSettings.pool_visible_level" style="width:240px">
                <el-option :value="0" label="所有人可见" />
                <el-option :value="1" label="仅主管可见" />
                <el-option :value="2" label="仅区长可见" />
              </el-select>
            </el-form-item>
            <el-form-item label="自动抓取到公共池">
              <el-switch v-model="sysSettings.pool_auto_fetch_open" :active-value="1" :inactive-value="0" />
              <div class="setting-tip">开启后，长时间未跟进的客户将被自动抓入公共池</div>
            </el-form-item>
            <el-form-item label="排行榜可见性">
              <el-select v-model="sysSettings.ranking_visible_level" style="width:240px">
                <el-option :value="0" label="所有人可见" />
                <el-option :value="1" label="仅主管可见" />
                <el-option :value="2" label="仅区长可见" />
              </el-select>
            </el-form-item>
            <el-form-item label="排行榜显示创收金额">
              <el-switch v-model="sysSettings.ranking_show_money" :active-value="1" :inactive-value="0" />
            </el-form-item>
            <el-form-item label="排行榜仅看本部门">
              <el-switch v-model="sysSettings.ranking_only_department" :active-value="1" :inactive-value="0" />
            </el-form-item>

            <el-divider content-position="left">客户数量上限</el-divider>
            <el-form-item label="客户上限开关">
              <el-switch v-model="sysSettings.client_toplimit_open" :active-value="1" :inactive-value="0" />
            </el-form-item>
            <template v-if="sysSettings.client_toplimit_open">
              <el-form-item label="顾问上限">
                <el-input-number v-model="sysSettings.client_toplimit_advisor" :min="50" :max="2000" :step="50" />
                <span class="setting-tip" style="margin-left:8px">条</span>
              </el-form-item>
              <el-form-item label="一级主管上限">
                <el-input-number v-model="sysSettings.client_toplimit_manager_lv1" :min="50" :max="2000" :step="50" />
                <span class="setting-tip" style="margin-left:8px">条</span>
              </el-form-item>
              <el-form-item label="二级主管上限">
                <el-input-number v-model="sysSettings.client_toplimit_manager_lv2" :min="50" :max="2000" :step="50" />
                <span class="setting-tip" style="margin-left:8px">条</span>
              </el-form-item>
            </template>

            <el-divider content-position="left">客户状态属性</el-divider>
            <div class="setting-tip" style="margin-bottom:12px">选中的状态将在系统中启用，未选中的状态不会出现在状态选择器中</div>
            <el-checkbox-group v-model="enabledStatuses">
              <el-row :gutter="16">
                <el-col :span="8" v-for="s in allStatuses" :key="s.value">
                  <el-checkbox :label="s.value" style="height:32px">{{ s.label }}</el-checkbox>
                </el-col>
              </el-row>
            </el-checkbox-group>

            <el-form-item style="margin-top:20px">
              <el-button type="warning" @click="saveSysSettings">保存全局设置</el-button>
            </el-form-item>
          </template>
        </el-form>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, Setting } from '@element-plus/icons-vue'
import { getSettings, updateSettings, changePassword, updateUser, getMe } from '../api'

const route = useRoute()
const user = computed(() => JSON.parse(localStorage.getItem('user') || '{}'))
const roleText = computed(() => ({ 0:'负责人', 1:'区长', 2:'部长', 3:'二级主管', 4:'主管', 5:'顾问', 6:'学徒' }[user.value.role] || '顾问'))
const isManager = computed(() => user.value.role <= 4)

const activeTab = ref('info')
const tabs = [
  { key: 'info', label: '个人信息', icon: 'User' },
  { key: 'password', label: '修改密码', icon: 'Lock' },
  { key: 'system', label: '系统设置', icon: 'Setting' }
]

// 个人信息
const infoForm = reactive({
  real_name: '',
  daily_quota: 50
})
const infoSaving = ref(false)

const saveInfo = async () => {
  if (!infoForm.real_name.trim()) return ElMessage.warning('姓名不能为空')
  infoSaving.value = true
  try {
    const data = { real_name: infoForm.real_name }
    if (infoForm.daily_quota !== undefined) data.daily_quota = infoForm.daily_quota
    const updated = await updateUser(user.value.id, data)
    // 更新本地存储的用户信息
    const stored = JSON.parse(localStorage.getItem('user') || '{}')
    Object.assign(stored, { real_name: updated.real_name, daily_quota: updated.daily_quota })
    localStorage.setItem('user', JSON.stringify(stored))
    ElMessage.success('个人信息已保存')
  } catch(e) {
    ElMessage.error(e.detail || '保存失败')
  } finally {
    infoSaving.value = false
  }
}

// 修改密码
const pwdFormRef = ref()
const pwdForm = reactive({ oldPassword: '', newPassword: '', confirmPassword: '' })
const pwdSaving = ref(false)
const pwdRules = {
  oldPassword: [{ required: true, message: '请输入原密码', trigger: 'blur' }],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== pwdForm.newPassword) callback(new Error('两次输入的密码不一致'))
        else callback()
      },
      trigger: 'blur'
    }
  ]
}

const handleChangePwd = async () => {
  const valid = await pwdFormRef.value?.validate().catch(() => false)
  if (!valid) return
  pwdSaving.value = true
  try {
    await changePassword(pwdForm.oldPassword, pwdForm.newPassword)
    ElMessage.success('密码修改成功，请重新登录')
    pwdForm.oldPassword = ''
    pwdForm.newPassword = ''
    pwdForm.confirmPassword = ''
    setTimeout(() => {
      localStorage.clear()
      window.location.href = '/'
    }, 1500)
  } catch(e) {
    ElMessage.error(e.detail || '修改失败')
  } finally {
    pwdSaving.value = false
  }
}

// 系统设置
const settings = ref({ accept_new_data: 1 })
const hiddenCols = ref([])
const colOptions = [
  { label:'ID', value:'id' }, { label:'性别', value:'gender' }, { label:'年龄', value:'age' },
  { label:'城市', value:'city' }, { label:'保单', value:'insurance' },
  { label:'社保', value:'social_security' }, { label:'公积金', value:'housing_fund' },
  { label:'信用卡', value:'credit_card' }, { label:'企业主', value:'is_entrepreneur' },
  { label:'贷款类型', value:'loan_type' }
]

const saveSettings = async () => {
  try {
    await updateSettings({
      accept_new_data: settings.value.accept_new_data,
      hidden_columns: JSON.stringify(hiddenCols.value)
    })
    ElMessage.success('设置已保存')
  } catch(e) {
    ElMessage.error('保存失败')
  }
}

// 系统级设置（主管可见）
const sysSettings = reactive({
  night_login_allowed: 0,
  accept_new_data_default: 1,
  district_manager_can_close_jieke: 1,
  manager_can_close_jieke: 1,
  advisor_can_close_jieke: 0,
  phone_privacy_mode: 0,
  district_manager_see_source: 1,
  manager_see_source: 1,
  advisor_see_source: 0,
  allow_blacklist: 1,
  pool_visible_level: 0,
  pool_auto_fetch_open: 0,
  ranking_visible_level: 0,
  ranking_show_money: 1,
  ranking_only_department: 0,
  client_toplimit_open: 0,
  client_toplimit_advisor: 400,
  client_toplimit_manager_lv1: 500,
  client_toplimit_manager_lv2: 600,
  ip_whitelist_open: 0,
  mobile_login_allowed: 1,
})
const ipWhitelistText = ref('')
const enabledStatuses = ref([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18])
const allStatuses = [
  { value: 0, label: '待跟进' }, { value: 1, label: '有意向' }, { value: 2, label: '未接通' },
  { value: 3, label: '预约上门' }, { value: 4, label: '已上门' }, { value: 5, label: '已受理' },
  { value: 6, label: '待签约' }, { value: 7, label: '已签约' }, { value: 8, label: '银行已放款' },
  { value: 9, label: '银行已拒绝' }, { value: 10, label: '审核中' }, { value: 11, label: '无意向' },
  { value: 12, label: '贷款资质不符' }, { value: 13, label: '捣乱申请' }, { value: 14, label: '重复申请' },
  { value: 15, label: '外地申请' }, { value: 16, label: '停机' }, { value: 17, label: '空号' },
  { value: 18, label: '外地号码' },
]

const saveSysSettings = async () => {
  try {
    const payload = { ...sysSettings }
    payload.enabled_statuses = enabledStatuses.value
    if (sysSettings.ip_whitelist_open) {
      payload.ip_whitelist_list = ipWhitelistText.value.split('\n').map(s => s.trim()).filter(Boolean)
    }
    const token = localStorage.getItem('token')
    const res = await fetch('/api/settings/system', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
      body: JSON.stringify(payload)
    })
    if (!res.ok) throw new Error('保存失败')
    ElMessage.success('全局设置已保存')
  } catch(e) {
    ElMessage.error('保存全局设置失败')
  }
}

onMounted(async () => {
  // URL参数切换Tab
  if (route.query.tab) {
    activeTab.value = route.query.tab
  }

  // 加载设置
  try {
    const s = await getSettings()
    settings.value.accept_new_data = s.accept_new_data
    hiddenCols.value = s.hidden_columns || []
  } catch(e) {}

  // 加载系统设置（主管）
  if (isManager.value) {
    try {
      const token = localStorage.getItem('token')
      const res = await fetch('/api/settings/system', {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (res.ok) {
        const data = await res.json()
        Object.keys(sysSettings).forEach(k => {
          if (data[k] !== undefined) sysSettings[k] = data[k]
        })
        if (data.enabled_statuses) enabledStatuses.value = data.enabled_statuses
        if (data.ip_whitelist_list) ipWhitelistText.value = data.ip_whitelist_list.join('\n')
      }
    } catch(e) {}
  }

  // 填充个人信息
  infoForm.real_name = user.value.real_name || ''
  infoForm.daily_quota = user.value.daily_quota || 50
})
</script>

<style scoped>
.settings-tabs {
  display: flex;
  border-bottom: 2px solid #FCE4EC;
  margin-bottom: 24px;
}
.settings-tab {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 20px;
  cursor: pointer;
  font-size: 14px;
  color: #888;
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  transition: all 0.2s;
}
.settings-tab:hover { color: #E91E63; }
.settings-tab.active {
  color: #E91E63;
  border-bottom-color: #E91E63;
  font-weight: 600;
}
.tab-content { padding: 8px 0; }

.info-avatar-section {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 16px;
}
.avatar-preview {}
.avatar-circle {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: linear-gradient(135deg, #E91E63, #F48FB1);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 28px;
  font-weight: bold;
}
.avatar-info h4 { margin: 0; font-size: 18px; color: #333; }

.setting-tip {
  color: #888;
  font-size: 12px;
  margin-top: 4px;
  line-height: 1.6;
}
</style>
