import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000
})

api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  r => r.data,
  err => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/'
    }
    return Promise.reject(err.response?.data || err.message)
  }
)

// ===================== 认证 =====================
export const login = (data) => api.post('/auth/login', data)
export const getMe = () => api.get('/auth/me')
export const changePassword = (oldPwd, newPwd) => {
  const params = new URLSearchParams()
  params.append('old', oldPwd)
  params.append('new_password', newPwd)
  return api.post('/auth/password', params)
}

// ===================== 客户 =====================
export const getCustomers = (params) => api.get('/customers', { params })
export const getCustomer = (id) => api.get(`/customers/${id}`)
export const createCustomer = (data) => api.post('/customers', data)
export const updateCustomer = (id, data) => api.put(`/customers/${id}`, data)
export const deleteCustomer = (id) => api.delete(`/customers/${id}`)
export const getAllOptions = () => api.get('/customers/all-options')

// ===================== 备注 =====================
export const getRemarks = (cid, page = 1) => api.get(`/customers/${cid}/remarks`, { params: { page } })
export const addRemark = (cid, data) => api.post(`/customers/${cid}/remarks`, data)

// ===================== 客户池 =====================
export const toPool = (cid) => api.post(`/customers/${cid}/to-pool`)
export const toMustFollow = (cid) => api.post(`/customers/${cid}/to-must-follow`)
export const fromPool = (cid) => api.post(`/customers/${cid}/from-pool`)
export const lockCustomer = (cid) => api.post(`/customers/${cid}/lock`)
export const markImportant = (cid) => api.post(`/customers/${cid}/important`)
export const blacklist = (cid) => api.post(`/customers/${cid}/blacklist`)
export const getPool = (params) => api.get('/pool', { params })
export const getPoolCount = () => api.get('/pool/count')
export const getImportantPool = (params) => api.get('/important-pool', { params })

// ===================== 在审件 =====================
export const getLoanCases = (params) => api.get('/loan-cases', { params })
export const createLoanCase = (data) => api.post('/loan-cases', data)
export const updateCaseStage = (lid, stage, amount) => {
  const data = new URLSearchParams()
  data.append('stage', stage)
  data.append('amount', amount)
  return api.post(`/loan-cases/${lid}/stage`, data)
}

// ===================== 统计（数据统计页面）=====================
export const getStatsDaily = (params) => api.get('/stats/daily-stats', { params })
export const getStatsRemarkCounts = (params) => api.get('/stats/remark-counts', { params })
export const getStatsMyRemarks = (params) => api.get('/stats/my-remarks', { params })
export const getStatsUpcomingPool = () => api.get('/stats/upcoming-pool')
export const getStatsNewCustomerStats = () => api.get('/stats/new-customer-stats')

// ===================== 统计 =====================
export const getDashboard = () => api.get('/stats/dashboard')
export const getMonthlyStats = (month) => api.get('/stats/monthly', { params: { month } })

// ===================== 团队 =====================
export const getTeamCustomers = (params) => api.get('/team/customers', { params })
export const teamAssign = (customerId, toUserId) => {
  const data = new URLSearchParams()
  data.append('customer_id', customerId)
  data.append('to_user_id', toUserId)
  return api.post('/team/assign', data)
}
export const getTeam = () => api.get('/users/team')
export const getTeamMembers = (params) => api.get('/team/members', { params })
export const updateTeamMember = (uid, body) => api.put(`/users/${uid}`, body)

// ===================== 部门和用户 =====================
export const getDepts = () => api.get('/departments')
export const getDeptMembers = (deptId) => api.get(`/departments/${deptId}/members`)
export const getUsers = () => api.get('/users')

// ===================== 设置 =====================
export const getSettings = () => api.get('/settings')
export const updateSettings = ({ accept_new_data, hidden_columns }) => {
  const data = new URLSearchParams()
  if (accept_new_data !== undefined) data.append('accept_new_data', accept_new_data)
  if (hidden_columns) data.append('hidden_columns', hidden_columns)
  return api.put('/settings', data)
}

// ===================== 用户管理 =====================
export const createUser = (body) => api.post('/users', body)
export const updateUser = (uid, body) => api.put(`/users/${uid}`, body)
export const setUserStatus = (uid, status) => {
  const data = new URLSearchParams()
  data.append('status', status)
  return api.put(`/users/${uid}/status`, data)
}

// ===================== 离职管理 =====================
export const getOffboardUsers = () => api.get('/team/offboard')
export const reassignAllCustomers = (fromId, toId) => {
  const data = new URLSearchParams()
  data.append('from_user_id', fromId)
  data.append('to_user_id', toId)
  return api.post('/team/reassign-all', data)
}

// ===================== 统计 =====================
export const getSourceDist = () => api.get('/stats/source-dist')
export const getStatusDist = () => api.get('/stats/status-dist')
export const getTeamDaily = (date) => api.get('/stats/team-daily', { params: date ? { target_date: date } : {} })

// ===================== 系统 =====================
export const getSystemInfo = () => api.get('/system/info')

// ===================== 客户详情 =====================
export const getCustomerAssignHistory = (cid) => api.get(`/customers/${cid}/assign-history`)

// ===================== 转移记录 =====================
export const getTransferHistory = (params) => api.get('/transfer-history', { params })

// ===================== 号码查重 =====================
export const checkPhone = (phone) => api.get('/customers/check-phone', { params: { phone } })

// ===================== 客户数量上限 =====================
export const getMyCustomerCount = () => api.get('/customers/my-count')

// ===================== 提醒 =====================
export const getUpcomingReminders = () => api.get('/reminders/upcoming')
export const createReminder = (data) => api.post('/reminders', data)
export const markReminderDone = (rid) => api.put(`/reminders/${rid}/done`)
export const deleteReminder = (rid) => api.delete(`/reminders/${rid}`)

// ===================== 数据统计页面 - 扩展API =====================
export const getLoginLogs = (params) => api.get('/stats/login-logs', { params })
export const getOperationLogs = (params) => api.get('/stats/operation-logs', { params })
export const getOperationActionList = () => api.get('/stats/operation-logs/actions')
export const getTransferLogs = (params) => api.get('/stats/transfer-logs', { params })
export const getImportLogs = (params) => api.get('/stats/import-logs', { params })
export const getSmsLogs = (params) => api.get('/stats/sms-logs', { params })
export const getVisitScanLogs = (params) => api.get('/stats/visit-scan', { params })
export const getVisitScanSummary = (params) => api.get('/stats/visit-scan/summary', { params })
export const getSourceDetailStats = (params) => api.get('/stats/source-detail', { params })
export const getSocialMediaStats = (params) => api.get('/stats/social-media', { params })
export const getApiSourceStats = (params) => api.get('/stats/api-list', { params })

// ===================== 激活客户 =====================
export const getInactiveCustomers = (params) => api.get('/customers-ina‑ive', { params })
export const activateCustomer = (id) => api.put(`/customers/${id}/activate`)

// ===================== 团队重要客户 =====================
export const getTeamImportantCustomers = (params) => api.get('/team/important-customers', { params })

export default api
