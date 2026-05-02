<template>
  <div>
    <div class="page-header">
      <h3>数据统计</h3>
      <div style="display:flex;gap:8px;align-items:center">
        <el-radio-group v-model="mode" size="small" @change="onModeChange">
          <el-radio-button value="daily">按日</el-radio-button>
          <el-radio-button value="monthly">按月</el-radio-button>
        </el-radio-group>
        <el-select v-model="dateRangeType" size="small" style="width:130px" @change="onDateRangeChange">
          <el-option value="today" label="今日" />
          <el-option value="yesterday" label="昨日" />
          <el-option value="last7" label="最近7天" />
          <el-option value="last30" label="最近30天" />
          <el-option value="thisMonth" label="本月" />
          <el-option value="lastMonth" label="上月" />
          <el-option value="custom" label="自定义" />
        </el-select>
        <el-date-picker v-if="dateRangeType === 'custom'" v-model="customRange" type="daterange" size="small" range-separator="至" start-placeholder="开始" end-placeholder="结束" value-format="YYYY-MM-DD" style="width:220px" />
        <el-button size="small" @click="onTabChange(activeTab)"><Refresh /> 刷新</el-button>
      </div>
    </div>

    <!-- 子导航 -->
    <el-tabs v-model="activeTab" @tab-change="onTabChange" class="stats-tabs">
      <el-tab-pane label="①数据日统计" name="daily-stats" />
      <el-tab-pane label="②来源统计" name="source-stats" />
      <el-tab-pane label="③社融统计" name="social-media" />
      <el-tab-pane label="④API对接" name="api-stats" />
      <el-tab-pane label="⑤登录日志" name="login-logs" />
      <el-tab-pane label="⑥导入日志" name="import-logs" />
      <el-tab-pane label="⑦短信日志" name="sms-logs" />
      <el-tab-pane label="⑧操作日志" name="operation-logs" />
      <el-tab-pane label="⑨转移日志" name="transfer-logs" />
      <el-tab-pane label="⑩扫码统计" name="visit-scan" />
      <el-tab-pane label="⑪备注统计" name="remark-counts" />
      <el-tab-pane label="⑫我的备注" name="my-remarks" />
      <el-tab-pane label="⑬公共池预警" name="upcoming-pool" />
      <el-tab-pane label="⑭顾问新数据" name="new-customer-stats" />
    </el-tabs>

    <!-- ==================== Tab1: 数据日统计 ==================== -->
    <div v-if="activeTab === 'daily-stats'">
      <el-table :data="dailyStats" v-loading="loadingDS" size="small" border stripe>
        <el-table-column label="日期" prop="date" width="110" fixed="left" />
        <el-table-column label="新申请量" prop="new_apply_count" width="100" />
        <el-table-column label="已受理" prop="new_accepted" width="80" />
        <el-table-column label="待跟进" prop="new_pending" width="80" />
        <el-table-column label="0星" prop="new_star0" width="70" />
        <el-table-column label="1星" prop="new_star1" width="70" />
        <el-table-column label="2星" prop="new_star2" width="70" />
        <el-table-column label="可贷点占比" prop="new_lendable_rate" width="100" />
        <el-table-column label="3星" prop="new_star3" width="70" />
        <el-table-column label="4星" prop="new_star4" width="70" />
        <el-table-column label="5星" prop="new_star5" width="70" />
        <el-table-column label="3星以上占比" prop="new_star3plus_rate" width="110" />
        <el-table-column label="捣乱申请" prop="new_spam" width="90" />
        <el-table-column label="再分配数" prop="reassign_count" width="100" />
        <el-table-column label="R-已受理" prop="re_accepted" width="80" />
        <el-table-column label="R-待跟进" prop="re_pending" width="80" />
      </el-table>
      <div style="margin-top:12px;color:#888;font-size:13px">共 {{ dailyStats.length }} 条记录</div>
    </div>

    <!-- ==================== Tab2: 来源统计 ==================== -->
    <div v-if="activeTab === 'source-stats'">
      <div style="margin-bottom:12px;display:flex;gap:8px;align-items:center;flex-wrap:wrap">
        <el-input v-model="srcKw" placeholder="来源名称" size="small" style="width:160px" clearable @change="loadSourceDetail" />
        <el-button size="small" @click="loadSourceDetail"><Refresh /> 刷新</el-button>
        <el-tag type="info" size="small">共 {{ sourceDetail.length }} 个来源渠道</el-tag>
      </div>
      <el-table :data="sourceDetail" v-loading="loadingSD" size="small" border stripe>
        <el-table-column label="来源渠道" prop="source" min-width="160" fixed="left" />
        <el-table-column label="客户总量" prop="total" width="100" sortable />
        <el-table-column label="城市数" prop="city_count" width="80" />
        <el-table-column label="3星以上" prop="star3plus" width="100" sortable />
        <el-table-column label="0星(低质)" prop="star0" width="100" sortable />
        <el-table-column label="3星以上占比" prop="star3plus_rate" width="120">
          <template #default="{row}">
            <el-progress :percentage="row.star3plus_rate" :color="row.star3plus_rate >= 30 ? '#67C23A' : row.star3plus_rate >= 15 ? '#E6A23C' : '#F56C6C'" :stroke-width="6" style="width:90px" />
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- ==================== Tab3: 社融统计 ==================== -->
    <div v-if="activeTab === 'social-media'">
      <el-table :data="socialMedia" v-loading="loadingSM" size="small" border stripe>
        <el-table-column label="社融来源" prop="source" width="180" fixed="left" />
        <el-table-column label="城市" prop="city" width="120" />
        <el-table-column label="客户数" prop="count" width="100" sortable />
      </el-table>
    </div>

    <!-- ==================== Tab4: API对接 ==================== -->
    <div v-if="activeTab === 'api-stats'">
      <el-table :data="apiStats" v-loading="loadingAPI" size="small" border stripe>
        <el-table-column label="API来源" prop="source" min-width="160" fixed="left" />
        <el-table-column label="总数据量" prop="count" width="120" sortable />
        <el-table-column label="活跃天数" prop="active_days" width="120" />
      </el-table>
      <el-empty v-if="!loadingAPI && !apiStats.length" description="暂无API来源数据" :image-size="80" style="margin-top:40px" />
    </div>

    <!-- ==================== Tab5: 顾问登录日志 ==================== -->
    <div v-if="activeTab === 'login-logs'">
      <div style="margin-bottom:12px;display:flex;gap:8px;align-items:center;flex-wrap:wrap">
        <el-input v-model="loginFilters.username" placeholder="顾问账号" size="small" style="width:130px" clearable />
        <el-select v-model="loginFilters.status" placeholder="登录状态" size="small" style="width:120px" clearable>
          <el-option :value="1" label="成功" />
          <el-option :value="0" label="失败" />
        </el-select>
        <el-date-picker v-model="loginFilters.daterange" type="daterange" size="small" range-separator="至" start-placeholder="开始" end-placeholder="结束" value-format="YYYY-MM-DD" style="width:220px" />
        <el-button size="small" type="primary" @click="loadLoginLogs(1)">搜索</el-button>
        <el-button size="small" @click="loginFilters={username:'',status:null,daterange:null};loadLoginLogs(1)">重置</el-button>
      </div>
      <el-table :data="loginLogs" v-loading="loadingLL" size="small" border stripe>
        <el-table-column label="时间" prop="created_at" width="160">
          <template #default="{row}">{{ fmt(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="顾问" prop="username" width="120" />
        <el-table-column label="IP地址" prop="ip" width="140" />
        <el-table-column label="设备" prop="device" min-width="160" show-overflow-tooltip />
        <el-table-column label="状态" prop="status" width="80">
          <template #default="{row}">
            <el-tag :type="row.status === 1 ? 'success' : 'danger'" size="small">{{ row.status === 1 ? '成功' : '失败' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="备注" prop="msg" min-width="120" show-overflow-tooltip />
      </el-table>
      <el-pagination background layout="total,prev,pager,next" :total="loginLogsTotal" v-model:current-page="loginPage" @current-change="loadLoginLogs" style="margin-top:12px" />
    </div>

    <!-- ==================== Tab6: Excel导入日志 ==================== -->
    <div v-if="activeTab === 'import-logs'">
      <div style="margin-bottom:12px;display:flex;gap:8px;align-items:center;flex-wrap:wrap">
        <el-input v-model="importFilters.username" placeholder="顾问账号" size="small" style="width:130px" clearable />
        <el-input v-model="importFilters.source" placeholder="来源" size="small" style="width:130px" clearable />
        <el-select v-model="importFilters.status" placeholder="状态" size="small" style="width:120px" clearable>
          <el-option :value="0" label="进行中" />
          <el-option :value="1" label="成功" />
          <el-option :value="2" label="失败" />
        </el-select>
        <el-date-picker v-model="importFilters.daterange" type="daterange" size="small" range-separator="至" start-placeholder="开始" end-placeholder="结束" value-format="YYYY-MM-DD" style="width:220px" />
        <el-button size="small" type="primary" @click="loadImportLogs(1)">搜索</el-button>
        <el-button size="small" @click="importFilters={username:'',source:'',status:null,daterange:null};loadImportLogs(1)">重置</el-button>
      </div>
      <el-table :data="importLogs" v-loading="loadingIL" size="small" border stripe>
        <el-table-column label="时间" prop="created_at" width="160">
          <template #default="{row}">{{ fmt(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="顾问" prop="username" width="100" />
        <el-table-column label="文件名" prop="file_name" min-width="180" show-overflow-tooltip />
        <el-table-column label="来源" prop="source" width="130" />
        <el-table-column label="总行数" prop="total_rows" width="80" />
        <el-table-column label="成功" prop="success_rows" width="80">
          <template #default="{row}"><span style="color:#67C23A">{{ row.success_rows }}</span></template>
        </el-table-column>
        <el-table-column label="失败" prop="fail_rows" width="80">
          <template #default="{row}"><span style="color:#F56C6C">{{ row.fail_rows }}</span></template>
        </el-table-column>
        <el-table-column label="状态" prop="status" width="90">
          <template #default="{row}">
            <el-tag :type="row.status === 1 ? 'success' : row.status === 2 ? 'danger' : 'info'" size="small">
              {{ ['','成功','失败','进行中'][row.status] || '进行中' }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination background layout="total,prev,pager,next" :total="importLogsTotal" v-model:current-page="importPage" @current-change="loadImportLogs" style="margin-top:12px" />
    </div>

    <!-- ==================== Tab7: 短信发送日志 ==================== -->
    <div v-if="activeTab === 'sms-logs'">
      <div style="margin-bottom:12px;display:flex;gap:8px;align-items:center;flex-wrap:wrap">
        <el-input v-model="smsFilters.username" placeholder="顾问账号" size="small" style="width:130px" clearable />
        <el-input v-model="smsFilters.customer_name" placeholder="客户姓名" size="small" style="width:130px" clearable />
        <el-select v-model="smsFilters.sms_type" placeholder="短信类型" size="small" style="width:130px" clearable>
          <el-option value="提醒短信" label="提醒短信" />
          <el-option value="营销短信" label="营销短信" />
          <el-option value="生日祝福" label="生日祝福" />
        </el-select>
        <el-select v-model="smsFilters.status" placeholder="发送状态" size="small" style="width:120px" clearable>
          <el-option :value="1" label="成功" />
          <el-option :value="0" label="失败" />
        </el-select>
        <el-date-picker v-model="smsFilters.daterange" type="daterange" size="small" range-separator="至" start-placeholder="开始" end-placeholder="结束" value-format="YYYY-MM-DD" style="width:220px" />
        <el-button size="small" type="primary" @click="loadSmsLogs(1)">搜索</el-button>
        <el-button size="small" @click="smsFilters={username:'',customer_name:'',sms_type:'',status:null,daterange:null};loadSmsLogs(1)">重置</el-button>
      </div>
      <el-table :data="smsLogs" v-loading="loadingSL" size="small" border stripe>
        <el-table-column label="时间" prop="created_at" width="160">
          <template #default="{row}">{{ fmt(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="顾问" prop="username" width="100" />
        <el-table-column label="客户" prop="customer_name" width="100" />
        <el-table-column label="手机号" prop="customer_phone" width="130" />
        <el-table-column label="短信类型" prop="sms_type" width="100" />
        <el-table-column label="内容" prop="content" min-width="200" show-overflow-tooltip />
        <el-table-column label="状态" prop="status" width="80">
          <template #default="{row}">
            <el-tag :type="row.status === 1 ? 'success' : 'danger'" size="small">{{ row.status === 1 ? '成功' : '失败' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="失败原因" prop="error_msg" width="120" show-overflow-tooltip />
      </el-table>
      <el-pagination background layout="total,prev,pager,next" :total="smsLogsTotal" v-model:current-page="smsPage" @current-change="loadSmsLogs" style="margin-top:12px" />
    </div>

    <!-- ==================== Tab8: 顾问操作日志 ==================== -->
    <div v-if="activeTab === 'operation-logs'">
      <div style="margin-bottom:12px;display:flex;gap:8px;align-items:center;flex-wrap:wrap">
        <el-input v-model="opFilters.username" placeholder="顾问账号" size="small" style="width:130px" clearable />
        <el-select v-model="opFilters.action" placeholder="操作类型" size="small" style="width:150px" clearable>
          <el-option v-for="a in opActionList" :key="a" :value="a" :label="a" />
        </el-select>
        <el-date-picker v-model="opFilters.daterange" type="daterange" size="small" range-separator="至" start-placeholder="开始" end-placeholder="结束" value-format="YYYY-MM-DD" style="width:220px" />
        <el-button size="small" type="primary" @click="loadOperationLogs(1)">搜索</el-button>
        <el-button size="small" @click="opFilters={username:'',action:'',target_type:'',daterange:null};loadOperationLogs(1)">重置</el-button>
      </div>
      <el-table :data="operationLogs" v-loading="loadingOL" size="small" border stripe>
        <el-table-column label="时间" prop="created_at" width="160">
          <template #default="{row}">{{ fmt(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="顾问" prop="username" width="110" />
        <el-table-column label="操作类型" prop="action" width="110">
          <template #default="{row}">
            <el-tag size="small" type="info">{{ row.action }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="对象类型" prop="target_type" width="90" />
        <el-table-column label="对象" prop="target_name" width="120" show-overflow-tooltip />
        <el-table-column label="详情" prop="detail" min-width="200" show-overflow-tooltip />
        <el-table-column label="IP" prop="ip" width="130" />
      </el-table>
      <el-pagination background layout="total,prev,pager,next" :total="opLogsTotal" v-model:current-page="opPage" @current-change="loadOperationLogs" style="margin-top:12px" />
    </div>

    <!-- ==================== Tab9: 客户转移日志 ==================== -->
    <div v-if="activeTab === 'transfer-logs'">
      <div style="margin-bottom:12px;display:flex;gap:8px;align-items:center;flex-wrap:wrap">
        <el-input v-model="tfFilters.customer_name" placeholder="客户姓名" size="small" style="width:130px" clearable />
        <el-input v-model="tfFilters.from_name" placeholder="原顾问" size="small" style="width:130px" clearable />
        <el-input v-model="tfFilters.to_name" placeholder="新顾问" size="small" style="width:130px" clearable />
        <el-date-picker v-model="tfFilters.daterange" type="daterange" size="small" range-separator="至" start-placeholder="开始" end-placeholder="结束" value-format="YYYY-MM-DD" style="width:220px" />
        <el-button size="small" type="primary" @click="loadTransferLogs(1)">搜索</el-button>
        <el-button size="small" @click="tfFilters={customer_name:'',from_name:'',to_name:'',daterange:null};loadTransferLogs(1)">重置</el-button>
      </div>
      <el-table :data="transferLogs" v-loading="loadingTL" size="small" border stripe>
        <el-table-column label="时间" prop="created_at" width="160">
          <template #default="{row}">{{ fmt(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="客户姓名" prop="customer_name" width="100" fixed="left" />
        <el-table-column label="手机号" prop="customer_phone" width="130" />
        <el-table-column label="原顾问" prop="from_user_name" width="100">
          <template #default="{row}"><span style="color:#F56C6C">{{ row.from_user_name }}</span></template>
        </el-table-column>
        <el-table-column label="新顾问" prop="to_user_name" width="100">
          <template #default="{row}"><span style="color:#67C23A">{{ row.to_user_name }}</span></template>
        </el-table-column>
        <el-table-column label="操作人" prop="operator_name" width="100" />
        <el-table-column label="原因" prop="reason" width="120" />
      </el-table>
      <el-pagination background layout="total,prev,pager,next" :total="transferLogsTotal" v-model:current-page="tfPage" @current-change="loadTransferLogs" style="margin-top:12px" />
    </div>

    <!-- ==================== Tab10: 上门扫码统计 ==================== -->
    <div v-if="activeTab === 'visit-scan'">
      <div style="margin-bottom:12px;display:flex;gap:8px;align-items:center;flex-wrap:wrap">
        <el-input v-model="vsFilters.advisor_name" placeholder="顾问姓名" size="small" style="width:130px" clearable />
        <el-input v-model="vsFilters.customer_name" placeholder="客户姓名" size="small" style="width:130px" clearable />
        <el-select v-model="vsFilters.sign_type" placeholder="类型" size="small" style="width:120px" clearable>
          <el-option value="上门" label="上门" />
          <el-option value="签约" label="签约" />
        </el-select>
        <el-date-picker v-model="vsFilters.daterange" type="daterange" size="small" range-separator="至" start-placeholder="开始" end-placeholder="结束" value-format="YYYY-MM-DD" style="width:220px" />
        <el-button size="small" type="primary" @click="loadVisitScan(1)">搜索</el-button>
        <el-button size="small" @click="vsFilters={advisor_name:'',customer_name:'',sign_type:'',daterange:null};loadVisitScan(1)">重置</el-button>
      </div>
      <el-table :data="visitScan" v-loading="loadingVS" size="small" border stripe>
        <el-table-column label="时间" prop="created_at" width="160">
          <template #default="{row}">{{ fmt(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="顾问" prop="advisor_name" width="100" />
        <el-table-column label="客户" prop="customer_name" width="100" />
        <el-table-column label="手机号" prop="customer_phone" width="130" />
        <el-table-column label="类型" prop="sign_type" width="80">
          <template #default="{row}">
            <el-tag :type="row.sign_type === '签约' ? 'success' : 'warning'" size="small">{{ row.sign_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="扫码码" prop="visit_code" width="130" />
        <el-table-column label="银行" prop="bank_name" min-width="120" />
      </el-table>
      <el-pagination background layout="total,prev,pager,next" :total="visitScanTotal" v-model:current-page="vsPage" @current-change="loadVisitScan" style="margin-top:12px" />
    </div>

    <!-- ==================== Tab11: 备注数量日统计 ==================== -->
    <div v-if="activeTab === 'remark-counts'">
      <el-table :data="remarkCounts" v-loading="loadingRC" size="small" border stripe>
        <el-table-column label="日期" prop="date" width="110" />
        <el-table-column label="备注总数" prop="total_remarks" width="100" sortable />
        <el-table-column label="有备注客户数" prop="customers_with_remark" width="130" />
        <el-table-column label="人均备注数" prop="avg_remarks" width="110" />
        <el-table-column label="未备注客户数" prop="customers_no_remark" width="130" />
      </el-table>
    </div>

    <!-- ==================== Tab12: 我的备注记录 ==================== -->
    <div v-if="activeTab === 'my-remarks'">
      <el-table :data="myRemarks" v-loading="loadingMR" size="small" border stripe>
        <el-table-column label="时间" prop="created_at" width="155">
          <template #default="{row}">{{ fmt(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="客户" prop="customer_name" width="100" />
        <el-table-column label="类型" prop="remark_type_text" width="100">
          <template #default="{row}">
            <el-tag size="small" :type="row.remark_type === 1 ? 'warning' : row.remark_type === 2 ? 'info' : ''">
              {{ row.remark_type_text }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" prop="status_at_remark" width="90">
          <template #default="{row}">{{ statusMap[row.status_at_remark] || '状态'+row.status_at_remark }}</template>
        </el-table-column>
        <el-table-column label="备注内容" prop="content" min-width="250" show-overflow-tooltip />
      </el-table>
      <el-pagination background layout="prev,pager,next" :total="myRemarksTotal" v-model:current-page="mrPage" @current-change="loadMyRemarks" style="margin-top:12px" />
    </div>

    <!-- ==================== Tab13: 即将抓入公共池 ==================== -->
    <div v-if="activeTab === 'upcoming-pool'">
      <el-alert type="warning" :closable="false" style="margin-bottom:12px">
        以下客户已超过设定的未跟进天数，即将被系统自动抓入公共池，请及时跟进！
      </el-alert>
      <el-table :data="upcomingPool" v-loading="loadingUP" size="small" border stripe>
        <el-table-column label="客户ID" prop="id" width="80" />
        <el-table-column label="姓名" prop="name" width="90" />
        <el-table-column label="手机" prop="phone" width="120" />
        <el-table-column label="归属顾问" prop="advisor_name" width="100" />
        <el-table-column label="星级" width="80">
          <template #default="{row}">
            <el-rate :model-value="row.star_level || 0" disabled text-color="#ff9900" size="small" />
          </template>
        </el-table-column>
        <el-table-column label="最后备注" width="155">
          <template #default="{row}">{{ fmt(row.last_remark_at) }}</template>
        </el-table-column>
        <el-table-column label="未跟进天数" width="100">
          <template #default="{row}">
            <el-tag :type="row.no_remark_days >= 20 ? 'danger' : row.no_remark_days >= 15 ? 'warning' : 'info'" size="small">
              {{ row.no_remark_days }}天
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="{row}">
            <el-button size="small" type="primary" @click="$emit('openDetail', row.id, row.name)">查看</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- ==================== Tab14: 顾问新数据统计 ==================== -->
    <div v-if="activeTab === 'new-customer-stats'">
      <el-table :data="newCustStats" v-loading="loadingNS" size="small" border stripe>
        <el-table-column label="顾问" prop="advisor_name" width="120" fixed="left" />
        <el-table-column label="新分配数" prop="new_count" width="100" sortable />
        <el-table-column label="已跟进数" prop="contacted_count" width="100" sortable />
        <el-table-column label="跟进率" prop="contact_rate" width="100">
          <template #default="{row}">
            <el-progress :percentage="row.contact_rate" :color="row.contact_rate >= 80 ? '#67C23A' : row.contact_rate >= 50 ? '#E6A23C' : '#F56C6C'" :stroke-width="6" style="width:80px" />
          </template>
        </el-table-column>
        <el-table-column label="3星以上" prop="star3plus_count" width="100" sortable />
        <el-table-column label="高意向占比" prop="high_intent_rate" width="110">
          <template #default="{row}">
            <span :style="{color: row.high_intent_rate >= 20 ? '#67C23A' : row.high_intent_rate >= 10 ? '#E6A23C' : '#909399'}">
              {{ row.high_intent_rate }}%
            </span>
          </template>
        </el-table-column>
      </el-table>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import { fmt } from '../utils/format'
import api from '../api'
import {
  getStatsDaily, getStatsRemarkCounts, getStatsMyRemarks,
  getStatsUpcomingPool, getStatsNewCustomerStats,
  getLoginLogs, getOperationLogs, getOperationActionList,
  getTransferLogs, getImportLogs, getSmsLogs,
  getVisitScanLogs, getSourceDetailStats, getSocialMediaStats, getApiSourceStats
} from '../api'

defineEmits(['openDetail'])

const activeTab = ref('daily-stats')
const mode = ref('daily')
const dateRangeType = ref('last30')
const customRange = ref(null)

// 状态对照
const statusMap = {
  0: '待跟进', 1: '已联系', 2: '有意向', 3: '待签约',
  4: '已签约', 5: '已放款', 6: '无意向', 7: '已拒绝',
  8: '暂时不需要', 9: '再联系', 10: '空号/错号',
  11: '无需求', 12: '无贷款资质', 13: '已上门', 14: '已签意向',
  15: '上门未签', 16: '已交定金', 17: '黑名单'
}

// ==================== Tab1: 数据日统计 ====================
const loadingDS = ref(false)
const dailyStats = ref([])
const loadDailyStats = async () => {
  loadingDS.value = true
  try {
    const res = await getStatsDaily({ mode: mode.value })
    dailyStats.value = res.items || res || []
  } finally { loadingDS.value = false }
}

// ==================== Tab2: 来源统计 ====================
const loadingSD = ref(false)
const sourceDetail = ref([])
const srcKw = ref('')
const loadSourceDetail = async () => {
  loadingSD.value = true
  try {
    const res = await getSourceDetailStats({ source: srcKw.value })
    sourceDetail.value = res.items || []
  } finally { loadingSD.value = false }
}

// ==================== Tab3: 社融统计 ====================
const loadingSM = ref(false)
const socialMedia = ref([])
const loadSocialMedia = async () => {
  loadingSM.value = true
  try {
    const res = await getSocialMediaStats({})
    socialMedia.value = res.items || []
  } finally { loadingSM.value = false }
}

// ==================== Tab4: API对接 ====================
const loadingAPI = ref(false)
const apiStats = ref([])
const loadApiStats = async () => {
  loadingAPI.value = true
  try {
    const res = await getApiSourceStats({})
    apiStats.value = res.items || []
  } finally { loadingAPI.value = false }
}

// ==================== Tab5: 登录日志 ====================
const loadingLL = ref(false)
const loginLogs = ref([])
const loginLogsTotal = ref(0)
const loginPage = ref(1)
const loginFilters = ref({ username: '', status: null, daterange: null })
const loadLoginLogs = async (page = 1) => {
  loginPage.value = page
  loadingLL.value = true
  try {
    const params = { page, page_size: 20 }
    if (loginFilters.value.username) params.username = loginFilters.value.username
    if (loginFilters.value.status !== null && loginFilters.value.status !== '') params.status = loginFilters.value.status
    if (loginFilters.value.daterange && loginFilters.value.daterange.length === 2) {
      params.start_date = loginFilters.value.daterange[0]
      params.end_date = loginFilters.value.daterange[1]
    }
    const res = await getLoginLogs(params)
    loginLogs.value = res.items || []
    loginLogsTotal.value = res.total || 0
  } finally { loadingLL.value = false }
}

// ==================== Tab6: 导入日志 ====================
const loadingIL = ref(false)
const importLogs = ref([])
const importLogsTotal = ref(0)
const importPage = ref(1)
const importFilters = ref({ username: '', source: '', status: null, daterange: null })
const loadImportLogs = async (page = 1) => {
  importPage.value = page
  loadingIL.value = true
  try {
    const params = { page, page_size: 20 }
    if (importFilters.value.username) params.username = importFilters.value.username
    if (importFilters.value.source) params.source = importFilters.value.source
    if (importFilters.value.status !== null && importFilters.value.status !== '') params.status = importFilters.value.status
    if (importFilters.value.daterange && importFilters.value.daterange.length === 2) {
      params.start_date = importFilters.value.daterange[0]
      params.end_date = importFilters.value.daterange[1]
    }
    const res = await getImportLogs(params)
    importLogs.value = res.items || []
    importLogsTotal.value = res.total || 0
  } finally { loadingIL.value = false }
}

// ==================== Tab7: 短信日志 ====================
const loadingSL = ref(false)
const smsLogs = ref([])
const smsLogsTotal = ref(0)
const smsPage = ref(1)
const smsFilters = ref({ username: '', customer_name: '', sms_type: '', status: null, daterange: null })
const loadSmsLogs = async (page = 1) => {
  smsPage.value = page
  loadingSL.value = true
  try {
    const params = { page, page_size: 20 }
    if (smsFilters.value.username) params.username = smsFilters.value.username
    if (smsFilters.value.customer_name) params.customer_name = smsFilters.value.customer_name
    if (smsFilters.value.sms_type) params.sms_type = smsFilters.value.sms_type
    if (smsFilters.value.status !== null && smsFilters.value.status !== '') params.status = smsFilters.value.status
    if (smsFilters.value.daterange && smsFilters.value.daterange.length === 2) {
      params.start_date = smsFilters.value.daterange[0]
      params.end_date = smsFilters.value.daterange[1]
    }
    const res = await getSmsLogs(params)
    smsLogs.value = res.items || []
    smsLogsTotal.value = res.total || 0
  } finally { loadingSL.value = false }
}

// ==================== Tab8: 操作日志 ====================
const loadingOL = ref(false)
const operationLogs = ref([])
const opLogsTotal = ref(0)
const opPage = ref(1)
const opActionList = ref([])
const opFilters = ref({ username: '', action: '', target_type: '', daterange: null })
const loadOperationLogs = async (page = 1) => {
  opPage.value = page
  loadingOL.value = true
  try {
    const params = { page, page_size: 20 }
    if (opFilters.value.username) params.username = opFilters.value.username
    if (opFilters.value.action) params.action = opFilters.value.action
    if (opFilters.value.target_type) params.target_type = opFilters.value.target_type
    if (opFilters.value.daterange && opFilters.value.daterange.length === 2) {
      params.start_date = opFilters.value.daterange[0]
      params.end_date = opFilters.value.daterange[1]
    }
    const res = await getOperationLogs(params)
    operationLogs.value = res.items || []
    opLogsTotal.value = res.total || 0
  } finally { loadingOL.value = false }
}

// ==================== Tab9: 转移日志 ====================
const loadingTL = ref(false)
const transferLogs = ref([])
const transferLogsTotal = ref(0)
const tfPage = ref(1)
const tfFilters = ref({ customer_name: '', from_name: '', to_name: '', daterange: null })
const loadTransferLogs = async (page = 1) => {
  tfPage.value = page
  loadingTL.value = true
  try {
    const params = { page, page_size: 20 }
    if (tfFilters.value.customer_name) params.customer_name = tfFilters.value.customer_name
    if (tfFilters.value.from_name) params.from_name = tfFilters.value.from_name
    if (tfFilters.value.to_name) params.to_name = tfFilters.value.to_name
    if (tfFilters.value.daterange && tfFilters.value.daterange.length === 2) {
      params.start_date = tfFilters.value.daterange[0]
      params.end_date = tfFilters.value.daterange[1]
    }
    const res = await getTransferLogs(params)
    transferLogs.value = res.items || []
    transferLogsTotal.value = res.total || 0
  } finally { loadingTL.value = false }
}

// ==================== Tab10: 上门扫码统计 ====================
const loadingVS = ref(false)
const visitScan = ref([])
const visitScanTotal = ref(0)
const vsPage = ref(1)
const vsFilters = ref({ advisor_name: '', customer_name: '', sign_type: '', daterange: null })
const loadVisitScan = async (page = 1) => {
  vsPage.value = page
  loadingVS.value = true
  try {
    const params = { page, page_size: 20 }
    if (vsFilters.value.advisor_name) params.advisor_name = vsFilters.value.advisor_name
    if (vsFilters.value.customer_name) params.customer_name = vsFilters.value.customer_name
    if (vsFilters.value.sign_type) params.sign_type = vsFilters.value.sign_type
    if (vsFilters.value.daterange && vsFilters.value.daterange.length === 2) {
      params.start_date = vsFilters.value.daterange[0]
      params.end_date = vsFilters.value.daterange[1]
    }
    const res = await getVisitScanLogs(params)
    visitScan.value = res.items || []
    visitScanTotal.value = res.total || 0
  } finally { loadingVS.value = false }
}

// ==================== Tab11: 备注数量日统计 ====================
const loadingRC = ref(false)
const remarkCounts = ref([])
const loadRemarkCounts = async () => {
  loadingRC.value = true
  try {
    const res = await getStatsRemarkCounts({ mode: mode.value })
    remarkCounts.value = res.items || res || []
  } finally { loadingRC.value = false }
}

// ==================== Tab12: 我的备注记录 ====================
const loadingMR = ref(false)
const myRemarks = ref([])
const myRemarksTotal = ref(0)
const mrPage = ref(1)
const loadMyRemarks = async (page = 1) => {
  mrPage.value = page
  loadingMR.value = true
  try {
    const res = await getStatsMyRemarks({ page })
    myRemarks.value = res.items || []
    myRemarksTotal.value = res.total || 0
  } finally { loadingMR.value = false }
}

// ==================== Tab13: 即将抓入公共池 ====================
const loadingUP = ref(false)
const upcomingPool = ref([])
const loadUpcomingPool = async () => {
  loadingUP.value = true
  try {
    const res = await getStatsUpcomingPool()
    upcomingPool.value = res.items || res || []
  } finally { loadingUP.value = false }
}

// ==================== Tab14: 顾问新数据统计 ====================
const loadingNS = ref(false)
const newCustStats = ref([])
const loadNewCustomerStats = async () => {
  loadingNS.value = true
  try {
    const res = await getStatsNewCustomerStats()
    newCustStats.value = res.items || res || []
  } finally { loadingNS.value = false }
}

// ==================== 加载操作类型列表 ====================
const loadOpActionList = async () => {
  try {
    const res = await getOperationActionList()
    opActionList.value = res.items || []
  } catch(e) { opActionList.value = [] }
}

// ==================== Tab切换 ====================
const onTabChange = (tab) => {
  if (tab === 'daily-stats') loadDailyStats()
  else if (tab === 'source-stats') loadSourceDetail()
  else if (tab === 'social-media') loadSocialMedia()
  else if (tab === 'api-stats') loadApiStats()
  else if (tab === 'login-logs') loadLoginLogs(1)
  else if (tab === 'import-logs') loadImportLogs(1)
  else if (tab === 'sms-logs') loadSmsLogs(1)
  else if (tab === 'operation-logs') { loadOpActionList(); loadOperationLogs(1) }
  else if (tab === 'transfer-logs') loadTransferLogs(1)
  else if (tab === 'visit-scan') loadVisitScan(1)
  else if (tab === 'remark-counts') loadRemarkCounts()
  else if (tab === 'my-remarks') loadMyRemarks(1)
  else if (tab === 'upcoming-pool') loadUpcomingPool()
  else if (tab === 'new-customer-stats') loadNewCustomerStats()
}

const onModeChange = () => {
  if (activeTab.value === 'daily-stats') loadDailyStats()
  else if (activeTab.value === 'remark-counts') loadRemarkCounts()
}

const onDateRangeChange = () => {
  // 日期范围筛选在各个API中体现
}

onMounted(() => {
  loadDailyStats()
  loadOpActionList()
})
</script>

<style scoped>
.stats-tabs :deep(.el-tabs__item) {
  font-size: 12px;
  padding: 0 12px;
}
</style>
