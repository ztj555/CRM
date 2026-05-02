<template>
  <div>
    <!-- 顶部客户数 + 工具栏按钮 -->
    <div class="page-header">
      <div class="header-left">
        <h3>我的客户</h3>
        <!-- 客户数上限提示 -->
        <div class="limit-bar" v-if="customerCount.count > 0">
          <span>我的客户：<b>{{ customerCount.count }}</b> 条</span>
          <span style="margin-left:12px;color:#888">剩余可分配：<b :style="{color: customerCount.near_limit ? '#E6A23C' : '#67C23A'}">{{ customerCount.limit - customerCount.count }}</b> 条</span>
          <el-progress :percentage="Math.round(customerCount.count / customerCount.limit * 100)"
            :color="customerCount.at_limit ? '#F56C6C' : customerCount.near_limit ? '#E6A23C' : '#67C23A'"
            :stroke-width="8" style="width:160px; margin-left:12px" />
          <el-tag v-if="customerCount.at_limit" type="danger" size="small" style="margin-left:8px">已达上限</el-tag>
          <el-tag v-else-if="customerCount.near_limit" type="warning" size="small" style="margin-left:8px">接近上限</el-tag>
        </div>
      </div>
      <div class="header-right">
        <!-- 快捷工具按钮 -->
        <el-button size="small" @click="loadData(1)" title="刷新">
          <Refresh /> 刷新
        </el-button>
        <el-button size="small" @click="checkPhoneDialogVisible = true" title="号码查重">
          <Search /> 号码查重
        </el-button>
        <el-button size="small" @click="openActivateDialog()" :type="activateDialogVisible ? 'success' : ''" title="激活客户">
          <el-icon><CircleCheck /></el-icon> 激活客户
        </el-button>
        <el-button size="small" @click="openTeamImportantDialog()" :type="teamImportantDialogVisible ? 'danger' : ''" title="团队重要客户">
          <el-icon><Star /></el-icon> 团队重要客户
        </el-button>
        <el-button size="small" @click="showReminderDialog()" title="设置备忘提醒">
          <Bell /> 备忘提醒
        </el-button>
        <el-button size="small" @click="params.important = 1; loadData(1)" :type="params.important === 1 ? 'danger' : ''" title="我的重要客户">
          <Star /> 我的重要客户
        </el-button>
        <el-button size="small" @click="showSupervisorReviewDialog()" :type="reviewDialogVisible ? 'warning' : ''" title="主管点评">
          <Comment /> 主管点评
        </el-button>
        <el-button size="small" @click="params.repay_status = 1; loadData(1)" :type="params.repay_status === 1 ? 'primary' : ''" title="待还款客户">
          <Wallet /> 待还款
        </el-button>
        <el-button size="small" @click="openTransferDialog()" title="查看客户转移记录">
          <el-icon><Connection /></el-icon> 转移记录
        </el-button>
        <el-divider direction="vertical" style="margin: 0 6px" />
        <el-button type="primary" size="small" @click="addVisible = true">
          <Plus/> 添加客户
          <el-tag v-if="customerCount.near_limit" :type="customerCount.at_limit ? 'danger' : 'warning'" size="small" style="margin-left:4px">
            {{ customerCount.count }}/{{ customerCount.limit }}
          </el-tag>
        </el-button>
      </div>
    </div>

    <!-- 搜索栏 -->
    <el-card style="margin:12px 0; padding: 0">
      <!-- 基础筛选行 -->
      <el-form inline @submit.prevent="loadData(1)" style="padding: 12px 12px 0">
        <el-form-item label="关键词">
          <el-input v-model="params.keyword" placeholder="请输入" clearable style="width:140px">
            <template #prepend>
              <el-select v-model="params.kw_type" style="width:90px" :clearable="false">
                <el-option label="综合" value="" />
                <el-option label="手机" value="phone" />
                <el-option label="姓名" value="name" />
                <el-option label="ID" value="id" />
              </el-select>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="selectedStatuses" multiple clearable collapse-tags placeholder="全部状态" style="width:130px" size="small">
            <el-option v-for="(name,val) in options.statusMap" :key="val" :label="name" :value="Number(val)" />
          </el-select>
        </el-form-item>
        <el-form-item label="星级">
          <el-select v-model="selectedStars" multiple clearable collapse-tags placeholder="全部星级" style="width:110px" size="small">
            <el-option v-for="n in 7" :key="n-1" :label="(n-1)+'星'" :value="n-1" />
          </el-select>
        </el-form-item>
        <el-form-item label="贷款类型">
          <el-select v-model="params.loan_type" clearable placeholder="全部" style="width:110px">
            <el-option v-for="(name,val) in options.loanTypeMap" :key="val" :label="name" :value="Number(val)" />
          </el-select>
        </el-form-item>
        <el-form-item label="来源">
          <el-select v-model="selectedSources" multiple clearable collapse-tags placeholder="来源" style="width:140px" size="small">
            <el-option v-for="s in options.sources || []" :key="s" :label="s" :value="s" />
          </el-select>
        </el-form-item>
        <el-form-item label="锁定">
          <el-select v-model="params.locked" clearable placeholder="全部" style="width:80px">
            <el-option label="已锁定" :value="1" /><el-option label="未锁定" :value="0" />
          </el-select>
        </el-form-item>
        <el-form-item label="重要">
          <el-select v-model="params.important" clearable placeholder="全部" style="width:80px">
            <el-option label="重要" :value="1" /><el-option label="普通" :value="0" />
          </el-select>
        </el-form-item>
        <el-form-item label="数据类型">
          <el-select v-model="params.data_type" clearable placeholder="全部" style="width:110px">
            <el-option label="全部数据" :value="0" />
            <el-option label="原始数据" :value="1" />
            <el-option label="再分配" :value="2" />
          </el-select>
        </el-form-item>
        <el-form-item label="还款状态">
          <el-select v-model="params.repay_status" clearable placeholder="全部" style="width:100px">
            <el-option label="全部" :value="-1" />
            <el-option label="待还款" :value="1" />
            <el-option label="已还款" :value="2" />
            <el-option label="无贷款件" :value="0" />
          </el-select>
        </el-form-item>
        <el-form-item><el-button type="primary" @click="loadData(1)"><Search/> 搜索</el-button></el-form-item>
        <el-form-item><el-button @click="resetParams">重置</el-button></el-form-item>
        <el-form-item>
          <el-button text :type="showAdvanced ? 'primary' : 'default'" @click="showAdvanced = !showAdvanced">
            <span v-if="activeFilterCount > 0" class="filter-badge">{{ activeFilterCount }}</span>
            {{ showAdvanced ? '收起高级' : '高级筛选' }}
            <el-icon><ArrowUp v-if="showAdvanced"/><ArrowDown v-else/></el-icon>
          </el-button>
        </el-form-item>
      </el-form>

      <!-- 高级筛选区域 -->
      <div v-show="showAdvanced" class="advanced-filter">
        <el-divider style="margin: 0 0 12px" />

        <!-- 第1行：年龄范围 + 婚姻状况 + 城市 + 时间类型 -->
        <div class="filter-row">
          <div class="filter-group">
            <span class="filter-label">年龄</span>
            <el-input-number v-model="params.age_min" :min="0" :max="100" size="small" style="width:80px" />&nbsp;~&nbsp;
            <el-input-number v-model="params.age_max" :min="0" :max="100" size="small" style="width:80px" />
          </div>
          <div class="filter-group" style="margin-left: 16px">
            <span class="filter-label">婚姻</span>
            <el-radio-group v-model="params.marital_status" size="small">
              <el-radio-button :value="-1">不限</el-radio-button>
              <el-radio-button :value="0">未婚</el-radio-button>
              <el-radio-button :value="1">已婚有孩</el-radio-button>
              <el-radio-button :value="2">已婚无孩</el-radio-button>
              <el-radio-button :value="3">离异</el-radio-button>
            </el-radio-group>
          </div>
          <div class="filter-group" style="margin-left: 16px">
            <span class="filter-label">城市</span>
            <el-select v-model="params.city" clearable filterable placeholder="选择城市" size="small" style="width:130px">
              <el-option v-for="c in options.cityList || []" :key="c" :label="c" :value="c" />
            </el-select>
          </div>
          <div class="filter-group" style="margin-left: 16px">
            <span class="filter-label">时间类型</span>
            <el-radio-group v-model="params.time_type" size="small">
              <el-radio-button value="created">进系统时间</el-radio-button>
              <el-radio-button value="remark">备注时间</el-radio-button>
              <el-radio-button value="apply">实际申请时间</el-radio-button>
            </el-radio-group>
          </div>
          <div class="filter-group" style="margin-left: 16px">
            <span class="filter-label">时间范围</span>
            <el-radio-group v-model="quickDate" size="small" @change="onQuickDateChange">
              <el-radio-button :value="0">自定义</el-radio-button>
              <el-radio-button :value="1">今日</el-radio-button>
              <el-radio-button :value="2">昨天</el-radio-button>
              <el-radio-button :value="3">最近7天</el-radio-button>
              <el-radio-button :value="4">本月</el-radio-button>
              <el-radio-button :value="5">上月</el-radio-button>
            </el-radio-group>
            <el-date-picker
              v-model="dateRange" type="daterange" range-separator="至" start-placeholder="开始"
              value-format="YYYY-MM-DD" size="small" style="width: 240px; margin-left:8px"
              @change="onDateChange"
            />
          </div>
        </div>

        <!-- 第2行：未备注天数 + 备注关键词 + 贷款条件 -->
        <div class="filter-row">
          <div class="filter-group">
            <span class="filter-label">未备注超过</span>
            <el-input-number v-model="params.no_remark_days" :min="0" :max="365" size="small" style="width: 100px" />
            <span style="color:#888; margin-left:4px">天</span>
          </div>
          <div class="filter-group" style="margin-left: 16px">
            <span class="filter-label">备注关键词</span>
            <el-input v-model="params.remark_keyword" placeholder="搜索备注内容" clearable size="small" style="width:160px" />
          </div>
          <div class="filter-group" style="margin-left: 16px">
            <span class="filter-label">数据类型</span>
            <el-radio-group v-model="params.data_type" size="small">
              <el-radio-button :value="0">全部</el-radio-button>
              <el-radio-button :value="1">原始数据</el-radio-button>
              <el-radio-button :value="2">再分配数据</el-radio-button>
            </el-radio-group>
          </div>
        </div>

        <!-- 第3行：贷款条件（房/车/社保/公积金/企业主/代发工资） -->
        <div class="filter-row">
          <div class="filter-group">
            <span class="filter-label">房产</span>
            <el-radio-group v-model="params.has_house" size="small">
              <el-radio-button :value="-1">不限</el-radio-button>
              <el-radio-button :value="1">有</el-radio-button>
              <el-radio-button :value="0">无</el-radio-button>
            </el-radio-group>
          </div>
          <div class="filter-group" style="margin-left: 16px">
            <span class="filter-label">车产</span>
            <el-radio-group v-model="params.has_car" size="small">
              <el-radio-button :value="-1">不限</el-radio-button>
              <el-radio-button :value="1">有</el-radio-button>
              <el-radio-button :value="0">无</el-radio-button>
            </el-radio-group>
          </div>
          <div class="filter-group" style="margin-left: 16px">
            <span class="filter-label">社保</span>
            <el-radio-group v-model="params.has_social_security" size="small">
              <el-radio-button :value="-1">不限</el-radio-button>
              <el-radio-button :value="1">有</el-radio-button>
              <el-radio-button :value="0">无</el-radio-button>
            </el-radio-group>
          </div>
          <div class="filter-group" style="margin-left: 16px">
            <span class="filter-label">公积金</span>
            <el-radio-group v-model="params.has_housing_fund" size="small">
              <el-radio-button :value="-1">不限</el-radio-button>
              <el-radio-button :value="1">有</el-radio-button>
              <el-radio-button :value="0">无</el-radio-button>
            </el-radio-group>
          </div>
          <div class="filter-group" style="margin-left: 16px">
            <span class="filter-label">企业主</span>
            <el-radio-group v-model="params.has_enterprise" size="small">
              <el-radio-button :value="-1">不限</el-radio-button>
              <el-radio-button :value="1">有</el-radio-button>
              <el-radio-button :value="0">无</el-radio-button>
            </el-radio-group>
          </div>
          <div class="filter-group" style="margin-left: 16px">
            <span class="filter-label">代发工资</span>
            <el-radio-group v-model="params.has_salary_payment" size="small">
              <el-radio-button :value="-1">不限</el-radio-button>
              <el-radio-button :value="1">有</el-radio-button>
              <el-radio-button :value="0">无</el-radio-button>
            </el-radio-group>
          </div>
          <div class="filter-group" style="margin-left: 16px">
            <span class="filter-label">保单</span>
            <el-radio-group v-model="params.has_insurance" size="small">
              <el-radio-button :value="-1">不限</el-radio-button>
              <el-radio-button :value="1">有</el-radio-button>
              <el-radio-button :value="0">无</el-radio-button>
            </el-radio-group>
          </div>
          <div class="filter-group" style="margin-left: 16px">
            <span class="filter-label">信用卡</span>
            <el-radio-group v-model="params.has_credit_card" size="small">
              <el-radio-button :value="-1">不限</el-radio-button>
              <el-radio-button :value="1">有</el-radio-button>
              <el-radio-button :value="0">无</el-radio-button>
            </el-radio-group>
          </div>
        </div>

        <!-- 第4行：备注次数 + 备注历史 + 资质关键词 + 标签 -->
        <div class="filter-row">
          <div class="filter-group">
            <span class="filter-label">备注次数</span>
            <el-input-number v-model="params.remark_count_min" :min="0" size="small" style="width:90px" />&nbsp;~&nbsp;
            <el-input-number v-model="params.remark_count_max" :min="0" size="small" style="width:90px" />
          </div>
          <div class="filter-group" style="margin-left: 16px">
            <span class="filter-label">最近备注</span>
            <el-radio-group v-model="params.remark_history" size="small">
              <el-radio-button :value="-1">不限</el-radio-button>
              <el-radio-button :value="0">今天</el-radio-button>
              <el-radio-button :value="3">3天内</el-radio-button>
              <el-radio-button :value="7">7天内</el-radio-button>
              <el-radio-button :value="30">30天内</el-radio-button>
            </el-radio-group>
          </div>
          <div class="filter-group" style="margin-left: 16px">
            <span class="filter-label">资质关键词</span>
            <el-input v-model="params.qual_keyword" placeholder="搜索资质信息" clearable size="small" style="width:180px" />
          </div>
          <div class="filter-group" style="margin-left: 16px">
            <span class="filter-label">标签</span>
            <el-select v-model="params.tag" clearable placeholder="按标签筛选" size="small" style="width:140px">
              <el-option v-for="t in options.tagList || []" :key="t" :label="t" :value="t" />
            </el-select>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 表格 -->
    <el-card>
      <!-- 快捷操作工具栏 -->
      <div class="table-toolbar">
        <div style="display:flex; align-items:center; gap:10px; flex-wrap:wrap">
          <span style="color:#888; font-size:13px">共 <b style="color:#E91E63">{{ total }}</b> 条</span>
          <!-- 批量操作区 -->
          <template v-if="selectedRows.length > 0">
            <el-tag type="danger" size="small">已选 {{ selectedRows.length }} 条</el-tag>
            <el-button size="small" type="warning" @click="batchStatusVisible = true">
              <el-icon><Edit /></el-icon> 批量改状态
            </el-button>
            <el-button size="small" type="info" @click="batchToPool">
              <el-icon><Upload /></el-icon> 批量转公共池
            </el-button>
            <el-button v-if="isManager" size="small" type="primary" @click="batchAssignVisible = true">
              <el-icon><User /></el-icon> 批量分配
            </el-button>
            <el-button size="small" @click="selectedRows = []; $refs.tableRef.clearSelection()">
              取消选择
            </el-button>
          </template>
        </div>
        <div class="toolbar-right">
          <span class="filter-label" style="margin-right:4px">排序</span>
          <el-select v-model="params.sort_field" size="small" style="width:130px; margin-right:6px" @change="loadData(1)">
            <el-option label="创建时间" value="created_at" />
            <el-option label="最后备注时间" value="last_remark_at" />
            <el-option label="申请额度" value="apply_amount" />
            <el-option label="星级" value="star_level" />
          </el-select>
          <el-select v-model="params.sort_order" size="small" style="width:80px" @change="loadData(1)">
            <el-option label="降序" value="desc" />
            <el-option label="升序" value="asc" />
          </el-select>
        </div>
      </div>

      <el-table ref="tableRef" :data="customers" v-loading="loading" @row-click="openDetail" row-class-name="clickable-row" :stripe="true" size="small" @selection-change="handleSelectionChange">
        <el-table-column type="selection" width="38" @click.stop />
        <el-table-column label="ID" prop="id" width="65" />
        <el-table-column label="姓名" width="85">
          <template #default="{row}">
            <span :style="{color: row.is_important ? '#F56C6C' : ''}">{{ row.name || '—' }}</span>
            <el-tag v-if="row.is_important" type="danger" size="small" style="margin-left:2px">重要</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="性别" prop="genderText" width="45" />
        <el-table-column label="城市" prop="city" width="65" v-if="!hiddenColumns.includes('city')" />
        <el-table-column label="年龄" prop="age" width="45" v-if="!hiddenColumns.includes('age')" />
        <el-table-column label="状态" width="82">
          <template #default="{row}"><el-tag size="small" :type="statusTagType[row.status]">{{ row.statusText }}</el-tag></template>
        </el-table-column>
        <el-table-column label="星级" width="55">
          <template #default="{row}"><span style="color:#E6A23C">★</span>{{ row.star_level }}</template>
        </el-table-column>
        <el-table-column label="额度" prop="apply_amount" width="60" v-if="!hiddenColumns.includes('apply_amount')">
          <template #default="{row}">{{ row.apply_amount ? row.apply_amount + '万' : '—' }}</template>
        </el-table-column>
        <el-table-column label="房" width="38">
          <template #default="{row}">
            <el-tag size="small" :type="row.qualifications?.has_house ? 'success' : 'info'" style="padding:0 4px">{{ row.qualifications?.has_house ? '✓' : '—' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="车" width="38">
          <template #default="{row}">
            <el-tag size="small" :type="row.qualifications?.has_car ? 'success' : 'info'" style="padding:0 4px">{{ row.qualifications?.has_car ? '✓' : '—' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="保单" width="38">
          <template #default="{row}">
            <el-tag size="small" :type="row.qualifications?.has_insurance ? 'success' : 'info'" style="padding:0 4px">{{ row.qualifications?.has_insurance ? '✓' : '—' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="社保" width="38">
          <template #default="{row}">
            <el-tag size="small" :type="row.qualifications?.social_security ? 'success' : 'info'" style="padding:0 4px">{{ row.qualifications?.social_security ? '✓' : '—' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="公积金" width="38">
          <template #default="{row}">
            <el-tag size="small" :type="row.qualifications?.housing_fund ? 'success' : 'info'" style="padding:0 4px">{{ row.qualifications?.housing_fund ? '✓' : '—' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="企业主" width="38">
          <template #default="{row}">
            <el-tag size="small" :type="row.qualifications?.has_enterprise ? 'warning' : 'info'" style="padding:0 4px">{{ row.qualifications?.has_enterprise ? '✓' : '—' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="芝麻分" width="65" v-if="!hiddenColumns.includes('zhima_score')">
          <template #default="{row}">{{ row.qualifications?.zhima_score || '—' }}</template>
        </el-table-column>
        <el-table-column label="信用卡" width="65" v-if="!hiddenColumns.includes('credit_card')">
          <template #default="{row}">{{ row.qualifications?.credit_card ? row.qualifications.credit_card + '万' : '—' }}</template>
        </el-table-column>
        <el-table-column label="备注摘要" min-width="120" show-overflow-tooltip>
          <template #default="{row}">{{ row.last_remark || '—' }}</template>
        </el-table-column>
        <el-table-column label="最后备注" width="130">
          <template #default="{row}">{{ fmt(row.last_remark_at) }}</template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div style="margin-top:12px; display:flex; justify-content:space-between; align-items:center">
        <div style="display:flex; align-items:center; gap:8px">
          <span style="color:#888; font-size:13px">共 <b style="color:#E91E63">{{ total }}</b> 条</span>
          <span style="color:#888; font-size:13px">每页</span>
          <el-select v-model="params.page_size" size="small" style="width:80px" @change="loadData(1)">
            <el-option :label="10" :value="10" /><el-option :label="20" :value="20" />
            <el-option :label="50" :value="50" /><el-option :label="100" :value="100" /><el-option :label="200" :value="200" />
          </el-select>
        </div>
        <el-pagination background layout="prev,pager,next" :total="total" :page-size="params.page_size" v-model:current-page="params.page" @current-change="loadData" />
      </div>
    </el-card>

    <!-- 添加客户 -->
    <el-dialog v-model="addVisible" title="添加客户" width="500px">
      <el-form :model="addForm" label-width="80px">
        <el-form-item label="手机号" required>
          <el-input v-model="addForm.phone" placeholder="必填" @blur="handlePhoneBlur"
            :class="{'phone-duplicate': phoneCheckResult}" style="width:100%" />
          <div v-if="phoneCheckResult" style="color:#E6A23C; font-size:12px; margin-top:4px">
            ⚠️ 此号码已存在（客户：{{ phoneCheckResult.customer_name || phoneCheckResult.customer_id }}），请勿重复添加
          </div>
        </el-form-item>
        <el-form-item label="姓名"><el-input v-model="addForm.name" placeholder="选填" /></el-form-item>
        <el-form-item label="性别"><el-radio-group v-model="addForm.gender"><el-radio :label="1">男</el-radio><el-radio :label="2">女</el-radio></el-radio-group></el-form-item>
        <el-form-item label="城市"><el-input v-model="addForm.city" /></el-form-item>
        <el-form-item label="年龄"><el-input-number v-model="addForm.age" :min="18" :max="100" /></el-form-item>
        <el-form-item label="贷款类型">
          <el-select v-model="addForm.loan_type" style="width:100%">
            <el-option v-for="(n,v) in options.loanTypeMap" :key="v" :label="n" :value="Number(v)" />
          </el-select>
        </el-form-item>
        <el-form-item label="申请额度"><el-input-number v-model="addForm.apply_amount" :min="0" :step="1" :precision="2" /></el-form-item>
        <el-form-item label="来源">
          <el-select v-model="addForm.source" style="width:100%" filterable allow-create clearable placeholder="选择或输入">
            <el-option v-for="s in options.sources" :key="s" :label="s" :value="s" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addVisible=false">取消</el-button>
        <el-button type="primary" :loading="addLoading" @click="handleAdd">确认添加</el-button>
      </template>
    </el-dialog>

    <!-- 号码查重对话框 -->
    <el-dialog v-model="checkPhoneDialogVisible" title="号码查重" width="440px">
      <el-form label-width="80px">
        <el-form-item label="手机号" required>
          <el-input v-model="checkPhoneInput" placeholder="输入手机号查询" clearable maxlength="11" @keyup.enter="doCheckPhone"
            style="width:100%">
            <template #append>
              <el-button @click="doCheckPhone" :loading="checkPhoneLoading">查询</el-button>
            </template>
          </el-input>
        </el-form-item>
      </el-form>
      <!-- 查重结果 -->
      <div v-if="checkPhoneResult" class="check-result" :class="checkPhoneResult.exists ? 'result-found' : 'result-clear'">
        <template v-if="checkPhoneResult.exists">
          <div style="color:#F56C6C; font-weight:bold; margin-bottom:8px">⚠️ 手机号已存在</div>
          <div style="font-size:13px">客户ID：<b>{{ checkPhoneResult.customer_id }}</b></div>
          <div style="font-size:13px">客户姓名：<b>{{ checkPhoneResult.customer_name || '未填写' }}</b></div>
          <div style="font-size:13px">当前状态：<el-tag size="small">{{ checkPhoneResult.statusText || '未知' }}</el-tag></div>
          <div style="margin-top:10px">
            <el-button type="primary" size="small" @click="gotoCustomer(checkPhoneResult.customer_id)">查看详情</el-button>
          </div>
        </template>
        <template v-else>
          <div style="color:#67C23A; font-weight:bold">✅ 该手机号在系统中不存在，可以添加</div>
        </template>
      </div>
    </el-dialog>

    <!-- 备忘提醒对话框 -->
    <el-dialog v-model="reminderDialogVisible" title="设置备忘提醒" width="460px">
      <el-form label-width="80px">
        <el-form-item label="选择客户" required>
          <el-select v-model="reminderForm.customer_id" filterable clearable placeholder="搜索客户姓名/手机" style="width:100%"
            :disabled="!!reminderForm.customer_id">
            <el-option v-for="c in customers" :key="c.id" :label="`${c.name || '未命名'}(${c.phone || ''})`" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="提醒内容" required>
          <el-input v-model="reminderForm.content" type="textarea" :rows="3" placeholder="例：下午3点电话跟进，确认贷款意愿" maxlength="200" show-word-limit />
        </el-form-item>
        <el-form-item label="提醒时间" required>
          <el-date-picker v-model="reminderForm.reminder_at" type="datetime" placeholder="选择提醒时间" value-format="YYYY-MM-DDTHH:mm:ss" style="width:100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="reminderDialogVisible=false">取消</el-button>
        <el-button type="primary" :loading="reminderLoading" @click="doCreateReminder">确认</el-button>
      </template>
    </el-dialog>

    <!-- 主管点评对话框 -->
    <el-dialog v-model="reviewDialogVisible" title="主管点评" width="500px">
      <div style="margin-bottom:12px">
        <span style="color:#888; font-size:13px">对下属 </span>
        <el-select v-model="reviewForm.advisor_id" size="small" style="width:140px" placeholder="选择顾问">
          <el-option v-for="u in teamUsers" :key="u.id" :label="u.real_name" :value="u.id" />
        </el-select>
        <span style="color:#888; font-size:13px"> 的今日工作进行点评</span>
      </div>
      <el-input v-model="reviewForm.content" type="textarea" :rows="4" placeholder="输入点评内容..." maxlength="500" show-word-limit />
      <template #footer>
        <el-button @click="reviewDialogVisible=false">取消</el-button>
        <el-button type="warning" :loading="reviewLoading" @click="doSubmitReview">提交点评</el-button>
      </template>
    </el-dialog>

    <!-- 转移记录对话框 -->
    <el-dialog v-model="transferDialogVisible" title="客户转移记录" width="680px">
      <div v-if="transferLoading" style="text-align:center;padding:40px">
        <el-icon class="is-loading" style="font-size:32px;color:#E91E63"><Loading /></el-icon>
      </div>
      <el-table v-else :data="transferHistory" size="small" stripe>
        <el-table-column label="时间" width="150">
          <template #default="{row}">{{ fmt(row.assigned_at) }}</template>
        </el-table-column>
        <el-table-column label="客户姓名" width="100">
          <template #default="{row}">
            <span class="transfer-customer" @click="goToCustomer(row.customer_id)">{{ row.customer_name || '—' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="手机" width="120">
          <template #default="{row}">{{ row.customer_phone || '—' }}</template>
        </el-table-column>
        <el-table-column label="转移方向" min-width="150">
          <template #default="{row}">
            <span style="color:#888">{{ row.from_name || '系统' }}</span>
            <span style="color:#E6A23C;margin:0 4px">→</span>
            <span style="color:#333;font-weight:500">{{ row.to_name || '未知' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="类型" width="80">
          <template #default="{row}">
            <el-tag size="small" :type="row.pool_type === 2 ? 'warning' : row.pool_type === 3 ? 'danger' : 'success'">
              {{ row.pool_type_text }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="60">
          <template #default="{row}">
            <el-tag size="small" :type="row.status === 1 ? 'success' : 'info'">{{ row.status === 1 ? '有效' : '失效' }}</el-tag>
          </template>
        </el-table-column>
      </el-table>
      <div style="margin-top:12px;text-align:right">
        <el-pagination
          small background layout="prev,pager,next"
          :total="transferTotal" :page-size="50"
          v-model:current-page="transferPage"
          @current-change="loadTransferHistory"
        />
      </div>
    </el-dialog>
    <!-- 批量改状态弹窗 -->
    <el-dialog v-model="batchStatusVisible" title="批量修改状态" width="360px">
      <div style="margin-bottom:12px; color:#888; font-size:13px">已选择 <b style="color:#E91E63">{{ selectedRows.length }}</b> 个客户，将统一修改为：</div>
      <el-select v-model="batchStatus" placeholder="选择目标状态" style="width:100%">
        <el-option v-for="(name,val) in options.statusMap" :key="val" :label="name" :value="Number(val)" />
      </el-select>
      <template #footer>
        <el-button @click="batchStatusVisible=false">取消</el-button>
        <el-button type="primary" :loading="batchLoading" @click="doBatchStatus">确认修改</el-button>
      </template>
    </el-dialog>

    <!-- 批量分配弹窗（主管） -->
    <el-dialog v-model="batchAssignVisible" title="批量分配客户" width="400px">
      <div style="margin-bottom:12px; color:#888; font-size:13px">将 <b style="color:#E91E63">{{ selectedRows.length }}</b> 个客户分配给：</div>
      <el-select v-model="batchAssignAdvisor" placeholder="选择目标顾问" style="width:100%" filterable>
        <el-option v-for="u in teamUsers" :key="u.id" :label="u.real_name" :value="u.id" />
      </el-select>
      <el-radio-group v-model="batchAssignPoolType" style="margin-top:12px">
        <el-radio :value="1">分配为我的客户</el-radio>
        <el-radio :value="2">分配为再分配</el-radio>
      </el-radio-group>
      <template #footer>
        <el-button @click="batchAssignVisible=false">取消</el-button>
        <el-button type="primary" :loading="batchLoading" @click="doBatchAssign">确认分配</el-button>
      </template>
    </el-dialog>

    <!-- 激活客户对话框 -->
    <el-dialog v-model="activateDialogVisible" title="激活客户" width="800px">
      <div style="margin-bottom:12px; color:#666; font-size:13px">
        以下是被您标记为无效/黑名单的客户，选择后可重新激活
      </div>
      <el-table :data="inactiveCustomers" border size="small" max-height="400" v-loading="activateLoading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="姓名" width="100" />
        <el-table-column prop="phone" label="手机号" width="130" />
        <el-table-column prop="status" label="当前状态" width="100">
          <template #default="{ row }">
            <el-tag type="danger" size="small">{{ options.statusMap[row.status] || '状态' + row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="last_remark_at" label="最后备注" />
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button type="success" size="small" @click="doActivateCustomer(row)">激活</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div v-if="inactiveCustomers.length === 0 && !activateLoading" style="text-align:center; color:#999; padding:20px">
        暂无非激活客户
      </div>
    </el-dialog>

    <!-- 团队重要客户对话框 -->
    <el-dialog v-model="teamImportantDialogVisible" title="团队重要客户" width="900px">
      <div style="margin-bottom:12px; color:#666; font-size:13px">
        团队所有重要客户（3星及以上）
      </div>
      <el-table :data="teamImportantCustomers" border size="small" max-height="450" v-loading="teamImportantLoading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="姓名" width="100" />
        <el-table-column prop="phone" label="手机号" width="130" />
        <el-table-column prop="star_level" label="星级" width="80">
          <template #default="{ row }">
            <el-rate :model-value="row.star_level || 0" disabled text-color="#ff9900" size="small" />
          </template>
        </el-table-column>
        <el-table-column prop="advisor_name" label="归属顾问" width="100" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            {{ options.statusMap[row.status] || '状态' + row.status }}
          </template>
        </el-table-column>
        <el-table-column prop="last_remark_at" label="最后备注" />
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="goCustomerDetail(row)">查看</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div v-if="teamImportantCustomers.length === 0 && !teamImportantLoading" style="text-align:center; color:#999; padding:20px">
        暂无团队重要客户
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, inject } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getCustomers, getAllOptions, createCustomer, checkPhone, getMyCustomerCount, createReminder, getTeam, getRemarks, addRemark, getTransferHistory, getSettings,
  updateCustomer, getInactiveCustomers, activateCustomer, getTeamImportantCustomers } from '../../api'
import { Connection, Loading, Edit, Upload, User, CircleCheck } from '@element-plus/icons-vue'
import { Star, Refresh, Search, Bell, Wallet, Close } from '@element-plus/icons-vue'

// 从 Layout 注入打开详情的方法
const openCustomerDetail = inject('openCustomerDetail', null)
const setAllCustomerIds = inject('setAllCustomerIds', null)
const isManager = computed(() => JSON.parse(localStorage.getItem('user') || '{}').role >= 2)

const customers = ref([])
const total = ref(0)
const loading = ref(false)
const addVisible = ref(false)
const addLoading = ref(false)
const options = ref({ statusMap: {}, loanTypeMap: {}, sources: [], tagList: [] })

// 高级筛选展开
const showAdvanced = ref(false)
const selectedStatuses = ref([])
const selectedStars = ref([])
const selectedSources = ref([])
const dateRange = ref(null)
const quickDate = ref(0)  // 0=自定义,1=今日,2=昨天,3=最近7天,4=本月,5=上月

const params = reactive({
  keyword:'', status:-1, star:-1, loan_type:-1, locked:-1, important:-1, repay_status:-1,
  source:'', start_date:'', end_date:'', remark_keyword:'',
  no_remark_days:0, time_type:'created', data_type:0,
  has_house:-1, has_car:-1, has_social_security:-1, has_housing_fund:-1, has_enterprise:-1,
  has_salary_payment:-1, has_insurance:-1, has_credit_card:-1,
  qual_keyword:'', tag:'',
  remark_count_min:0, remark_count_max:0, remark_history:-1,
  page:1, page_size:20, sort_field:'created_at', sort_order:'desc'
})

// 计算激活的筛选器数量
const activeFilterCount = computed(() => {
  let count = 0
  if (params.keyword) count++
  if (params.status !== -1) count++
  if (params.star !== -1) count++
  if (params.loan_type !== -1) count++
  if (params.locked !== -1) count++
  if (params.important === 1) count++
  if (params.repay_status !== -1) count++
  if (selectedStatuses.value.length > 0) count++
  if (selectedStars.value.length > 0) count++
  if (selectedSources.value.length > 0) count++
  if (quickDate.value > 0) count++
  if (dateRange.value && dateRange.value.length === 2 && quickDate.value === 0) count++
  if (params.no_remark_days > 0) count++
  if (params.remark_keyword) count++
  if (params.has_house !== -1) count++
  if (params.has_car !== -1) count++
  if (params.has_social_security !== -1) count++
  if (params.has_housing_fund !== -1) count++
  if (params.has_enterprise !== -1) count++
  if (params.has_salary_payment !== -1) count++
  if (params.has_insurance !== -1) count++
  if (params.has_credit_card !== -1) count++
  if (params.remark_count_min > 0) count++
  if (params.remark_count_max > 0) count++
  if (params.remark_history !== -1) count++
  if (params.qual_keyword) count++
  if (params.tag) count++
  if (params.data_type !== 0) count++
  if (params.time_type !== 'created') count++
  return count
})

const statusTagType = {0:'',1:'success',2:'info',3:'warning',4:'warning',5:'',6:'',7:'success',8:'success',9:'danger',10:'',11:'info',12:'danger',13:'danger',14:'danger',15:'',16:'danger',17:'danger',18:''}

const fmt = (t) => t ? t.replace('T',' ').substring(0,16) : '—'

const onDateChange = (val) => {
  if (val && val.length === 2) {
    params.start_date = val[0]
    params.end_date = val[1]
    quickDate.value = 0  // 切换为自定义
  } else {
    params.start_date = ''
    params.end_date = ''
  }
}

const onQuickDateChange = (val) => {
  if (val === 0) return  // 自定义，不处理
  const now = new Date()
  let start, end
  if (val === 1) { // 今日
    start = new Date(now.getFullYear(), now.getMonth(), now.getDate())
    end = now
  } else if (val === 2) { // 昨天
    const yest = new Date(now)
    yest.setDate(yest.getDate() - 1)
    start = new Date(yest.getFullYear(), yest.getMonth(), yest.getDate())
    end = new Date(yest.getFullYear(), yest.getMonth(), yest.getDate(), 23, 59, 59)
  } else if (val === 3) { // 最近7天
    start = new Date(now)
    start.setDate(start.getDate() - 6)
    start = new Date(start.getFullYear(), start.getMonth(), start.getDate())
    end = now
  } else if (val === 4) { // 本月
    start = new Date(now.getFullYear(), now.getMonth(), 1)
    end = now
  } else if (val === 5) { // 上月
    start = new Date(now.getFullYear(), now.getMonth() - 1, 1)
    end = new Date(now.getFullYear(), now.getMonth(), 0, 23, 59, 59)
  }
  params.start_date = start.toISOString().slice(0, 10)
  params.end_date = end.toISOString().slice(0, 10)
  dateRange.value = [params.start_date, params.end_date]
}

const loadData = async (page = params.page) => {
  params.page = page
  loading.value = true
  try {
    const p = { ...params }
    if (p.status < 0) delete p.status
    if (p.star < 0) delete p.star
    if (p.loan_type < 0) delete p.loan_type
    if (p.locked < 0) delete p.locked
    if (p.important < 0) delete p.important
    if (!p.remark_keyword) delete p.remark_keyword
    if (p.no_remark_days <= 0) delete p.no_remark_days
    if (!p.start_date) delete p.start_date
    if (!p.end_date) delete p.end_date
    if (p.has_house < 0) delete p.has_house
    if (p.has_car < 0) delete p.has_car
    if (p.has_social_security < 0) delete p.has_social_security
    if (p.has_housing_fund < 0) delete p.has_housing_fund
    if (p.has_enterprise < 0) delete p.has_enterprise
    if (p.has_salary_payment < 0) delete p.has_salary_payment
    if (!p.qual_keyword) delete p.qual_keyword
    if (!p.tag) delete p.tag
    if (p.data_type === 0) delete p.data_type
    if (p.has_insurance < 0) delete p.has_insurance
    if (p.has_credit_card < 0) delete p.has_credit_card
    if (p.remark_count_min <= 0) delete p.remark_count_min
    if (p.remark_count_max <= 0) delete p.remark_count_max
    if (p.remark_history === -1) delete p.remark_history
    if (p.time_type === 'created') delete p.time_type
    if (p.status === -1) delete p.status
    if (selectedStatuses.value.length > 0) {
      p.status_list = selectedStatuses.value.join(',')
    }
    if (selectedStars.value.length > 0) {
      p.star_list = selectedStars.value.join(',')
    }
    if (selectedSources.value.length > 0) {
      p.sources = selectedSources.value.join(',')
    } else {
      delete p.sources
    }
    // 删除旧的单值 source
    delete p.source

    const res = await getCustomers(p)
    customers.value = res.items
    total.value = res.total
    // 通知 Layout 更新客户ID列表（用于上一位/下一位导航）
    if (setAllCustomerIds) setAllCustomerIds(res.items.map(c => c.id))
  } catch(e) { ElMessage.error(e.detail || '加载失败') }
  finally { loading.value = false }
}

const resetParams = () => {
  Object.assign(params, {
    keyword:'', status:-1, star:-1, loan_type:-1, locked:-1, important:-1, repay_status:-1,
    source:'', start_date:'', end_date:'', remark_keyword:'',
    no_remark_days:0, time_type:'created', data_type:0, page:1,
    has_house:-1, has_car:-1, has_social_security:-1, has_housing_fund:-1, has_enterprise:-1,
    has_salary_payment:-1, has_insurance:-1, has_credit_card:-1,
    qual_keyword:'', tag:'',
    remark_count_min:0, remark_count_max:0, remark_history:-1,
    sort_field:'created_at', sort_order:'desc'
  })
  selectedStatuses.value = []
  selectedStars.value = []
  selectedSources.value = []
  dateRange.value = null
  quickDate.value = 0
  loadData(1)
}

const addForm = reactive({ phone:'', name:'', gender:0, city:'', age:0, loan_type:1, apply_amount:0, source:'' })

// 客户数量上限
const customerCount = ref({ count: 0, limit: 400, near_limit: false, at_limit: false })

// 隐藏列设置
const hiddenColumns = ref([])

const loadCustomerCount = async () => {
  try {
    const r = await getMyCustomerCount()
    customerCount.value = r
  } catch(e) { /* ignore */ }
}
loadCustomerCount()

// 手机号查重（添加客户时）
const phoneCheckResult = ref(null)  // {exists, customer_id, customer_name, status}

const handlePhoneBlur = async () => {
  if (!addForm.phone || addForm.phone.length < 11) { phoneCheckResult.value = null; return }
  try {
    const r = await checkPhone(addForm.phone)
    phoneCheckResult.value = r.exists ? r : null
  } catch(e) { phoneCheckResult.value = null }
}

// ====== 号码查重对话框 ======
const checkPhoneDialogVisible = ref(false)
const checkPhoneInput = ref('')
const checkPhoneLoading = ref(false)
const checkPhoneResult = ref(null)

const doCheckPhone = async () => {
  if (!checkPhoneInput.value || checkPhoneInput.value.length < 11) { ElMessage.warning('请输入正确的手机号'); return }
  checkPhoneLoading.value = true
  try {
    const r = await checkPhone(checkPhoneInput.value)
    checkPhoneResult.value = r.exists ? { ...r, statusText: options.value.statusMap?.[r.status] || '' } : r
  } catch(e) { ElMessage.error('查询失败') }
  finally { checkPhoneLoading.value = false }
}

const gotoCustomer = (id) => {
  checkPhoneDialogVisible.value = false
  if (openCustomerDetail) openCustomerDetail(id, checkPhoneResult.value?.customer_name || String(id))
}

// ====== 备忘提醒对话框 ======
const reminderDialogVisible = ref(false)
const reminderForm = reactive({ customer_id: null, content: '', reminder_at: '' })
const reminderLoading = ref(false)

const showReminderDialog = (prefillId = null) => {
  reminderForm.customer_id = prefillId
  reminderForm.content = ''
  reminderForm.reminder_at = ''
  reminderDialogVisible.value = true
}

const doCreateReminder = async () => {
  if (!reminderForm.customer_id) return ElMessage.warning('请选择客户')
  if (!reminderForm.content.trim()) return ElMessage.warning('请输入提醒内容')
  if (!reminderForm.reminder_at) return ElMessage.warning('请选择提醒时间')
  reminderLoading.value = true
  try {
    await createReminder(reminderForm)
    ElMessage.success('提醒已设置')
    reminderDialogVisible.value = false
  } catch(e) { ElMessage.error(e.detail || '设置失败') }
  finally { reminderLoading.value = false }
}

// ====== 主管点评对话框 ======
const reviewDialogVisible = ref(false)
const reviewForm = reactive({ advisor_id: null, content: '' })
const reviewLoading = ref(false)
const teamUsers = ref([])

const showSupervisorReviewDialog = async () => {
  if (teamUsers.value.length === 0) {
    try { const r = await getTeam(); teamUsers.value = r || [] } catch(e) {}
  }
  reviewForm.advisor_id = null
  reviewForm.content = ''
  reviewDialogVisible.value = true
}

// ====== 转移记录对话框 ======
const transferDialogVisible = ref(false)
const transferHistory = ref([])
const transferLoading = ref(false)
const transferTotal = ref(0)
const transferPage = ref(1)

const openTransferDialog = async () => {
  transferDialogVisible.value = true
  transferPage.value = 1
  await loadTransferHistory()
}

const loadTransferHistory = async (page = 1) => {
  transferPage.value = page
  transferLoading.value = true
  try {
    const res = await getTransferHistory({ page, page_size: 50 })
    transferHistory.value = res.items || []
    transferTotal.value = res.total || 0
  } catch(e) { ElMessage.error('加载转移记录失败') }
  finally { transferLoading.value = false }
}

const goToCustomer = (id) => {
  transferDialogVisible.value = false
  if (openCustomerDetail) openCustomerDetail(id, String(id))
}

// ====== 激活客户对话框 ======
const activateDialogVisible = ref(false)
const inactiveCustomers = ref([])
const activateLoading = ref(false)

const openActivateDialog = async () => {
  activateDialogVisible.value = true
  activateLoading.value = true
  try {
    const r = await getInactiveCustomers({ page: 1, page_size: 50 })
    inactiveCustomers.value = r.items || []
  } catch(e) { ElMessage.error('加载非激活客户失败') }
  finally { activateLoading.value = false }
}

const doActivateCustomer = async (row) => {
  try {
    await activateCustomer(row.id)
    ElMessage.success(`客户 ${row.name || row.id} 已激活`)
    // 从列表中移除
    inactiveCustomers.value = inactiveCustomers.value.filter(c => c.id !== row.id)
    loadData(1)
  } catch(e) { ElMessage.error(e.detail || '激活失败') }
}

// ====== 团队重要客户对话框 ======
const teamImportantDialogVisible = ref(false)
const teamImportantCustomers = ref([])
const teamImportantLoading = ref(false)

const openTeamImportantDialog = async () => {
  if (!isManager.value) {
    return ElMessage.warning('仅主管及以上可查看团队重要客户')
  }
  teamImportantDialogVisible.value = true
  teamImportantLoading.value = true
  try {
    const r = await getTeamImportantCustomers({ page: 1, page_size: 50 })
    teamImportantCustomers.value = r.items || []
  } catch(e) { ElMessage.error('加载团队重要客户失败') }
  finally { teamImportantLoading.value = false }
}

const goCustomerDetail = (row) => {
  teamImportantDialogVisible.value = false
  if (openCustomerDetail) openCustomerDetail(row.id, row.name)
}

const doSubmitReview = async () => {
  if (!reviewForm.advisor_id) return ElMessage.warning('请选择要点评的顾问')
  if (!reviewForm.content.trim()) return ElMessage.warning('请输入点评内容')
  reviewLoading.value = true
  try {
    // 主管点评写入到该顾问的第一个客户备注中（remark_type=1）
    // 找到该顾问的第一个客户
    const r = await getCustomers({ advisor_id: reviewForm.advisor_id, page: 1, page_size: 1, status: -1 })
    if (r.items && r.items.length > 0) {
      await addRemark(r.items[0].id, { content: reviewForm.content, remark_type: 1 })
      ElMessage.success('点评已提交')
    } else {
      ElMessage.warning('该顾问暂无客户可点评')
    }
    reviewDialogVisible.value = false
  } catch(e) { ElMessage.error(e.detail || '提交失败') }
  finally { reviewLoading.value = false }
}

const handleAdd = async () => {
  if (!addForm.phone) return ElMessage.warning('请输入手机号')
  // 检查上限
  if (customerCount.value.at_limit) {
    return ElMessage.error(`您已达到客户上限（${customerCount.value.limit}条），无法添加新客户`)
  }
  // 检查重复
  if (phoneCheckResult.value) {
    return ElMessage.warning('此手机号已存在，请勿重复添加')
  }
  addLoading.value = true
  try {
    await createCustomer(addForm)
    ElMessage.success('添加成功')
    addVisible.value = false
    Object.assign(addForm, { phone:'', name:'', gender:0, city:'', age:0, loan_type:1, apply_amount:0, source:'' })
    phoneCheckResult.value = null
    loadData(1)
    loadCustomerCount()
  } catch(e) { ElMessage.error(e.detail || e || '添加失败') }
  finally { addLoading.value = false }
}

// 打开客户详情：使用 Layout 注入方法，在右侧面板打开
const openDetail = (row) => {
  if (openCustomerDetail) {
    openCustomerDetail(row.id, row.name)
  }
}

// ====== 批量操作 ======
const tableRef = ref(null)
const selectedRows = ref([])
const batchStatusVisible = ref(false)
const batchAssignVisible = ref(false)
const batchLoading = ref(false)
const batchStatus = ref(0)
const batchAssignAdvisor = ref(null)
const batchAssignPoolType = ref(1)

const handleSelectionChange = (rows) => {
  selectedRows.value = rows
}

const doBatchStatus = async () => {
  if (!selectedRows.value.length) return
  batchLoading.value = true
  try {
    const res = await fetch('/api/customers/batch-status', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${localStorage.getItem('token')}` },
      body: JSON.stringify({ customer_ids: selectedRows.value.map(r => r.id), status: batchStatus.value })
    })
    const d = await res.json()
    ElMessage.success(`已批量修改 ${d.updated} 个客户状态`)
    batchStatusVisible.value = false
    selectedRows.value = []
    tableRef.value?.clearSelection()
    loadData(1)
  } catch(e) { ElMessage.error('批量操作失败') }
  finally { batchLoading.value = false }
}

const batchToPool = async () => {
  if (!selectedRows.value.length) return
  await ElMessageBox.confirm(`确定将选中的 ${selectedRows.value.length} 个客户批量移入公共池？`, '批量转公共池', { type: 'warning' })
  batchLoading.value = true
  try {
    const res = await fetch('/api/customers/batch-to-pool', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${localStorage.getItem('token')}` },
      body: JSON.stringify({ customer_ids: selectedRows.value.map(r => r.id) })
    })
    const d = await res.json()
    ElMessage.success(`已将 ${d.moved} 个客户移入公共池`)
    selectedRows.value = []
    tableRef.value?.clearSelection()
    loadData(1)
  } catch(e) { ElMessage.error('批量操作失败') }
  finally { batchLoading.value = false }
}

const doBatchAssign = async () => {
  if (!batchAssignAdvisor.value) return ElMessage.warning('请选择目标顾问')
  batchLoading.value = true
  try {
    const res = await fetch('/api/customers/batch-assign', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${localStorage.getItem('token')}` },
      body: JSON.stringify({ customer_ids: selectedRows.value.map(r => r.id), advisor_id: batchAssignAdvisor.value, pool_type: batchAssignPoolType.value })
    })
    const d = await res.json()
    ElMessage.success(`已分配 ${d.assigned} 个客户`)
    batchAssignVisible.value = false
    selectedRows.value = []
    tableRef.value?.clearSelection()
    loadData(1)
  } catch(e) { ElMessage.error('批量分配失败') }
  finally { batchLoading.value = false }
}

// ===================== 资质字段显示 =====================
const getQ = (row, key) => row?.qualifications?.[key]
const hasBool = (v) => v ? '✓' : '—'
const hasTag = (v) => v ? 'success' : 'info'
const hasText = (v) => v ? '有' : '无'

onMounted(async () => {
  const opts = await getAllOptions()
  options.value = opts
  loadData()
  loadCustomerCount()
  // 加载隐藏列设置
  try {
    const s = await getSettings()
    hiddenColumns.value = s.hidden_columns || []
  } catch(e) {}
})
</script>

<style scoped>
:deep(.clickable-row) { cursor: pointer; }
:deep(.clickable-row:hover) { background: #f0f9ff !important; }

.advanced-filter {
  padding: 0 12px 14px;
}

.filter-row {
  display: flex;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 10px;
}

.filter-row:last-child { margin-bottom: 0; }

.filter-group {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.filter-label {
  font-size: 13px;
  color: #666;
  white-space: nowrap;
  min-width: 56px;
  font-weight: 500;
}

.status-check-group {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

:deep(.el-checkbox-button__inner) {
  padding: 4px 10px;
  font-size: 12px;
  border-radius: 4px;
}

.table-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}

.toolbar-right {
  display: flex;
  align-items: center;
}

.filter-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  background: #E91E63;
  color: white;
  border-radius: 50%;
  font-size: 11px;
  margin-right: 4px;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 0;
  flex-wrap: wrap;
  gap: 10px;
}

.page-header h3 {
  margin: 0;
  font-size: 18px;
  color: #303133;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.limit-bar {
  display: flex;
  align-items: center;
  font-size: 13px;
  color: #606266;
  background: #f5f7fa;
  padding: 4px 12px;
  border-radius: 16px;
  border: 1px solid #ebeef5;
}

.limit-bar b { color: #303133; }

.check-result {
  margin-top: 12px;
  padding: 14px;
  border-radius: 6px;
  font-size: 13px;
}

.result-found {
  background: #fef0f0;
  border: 1px solid #fde2e2;
}

.result-clear {
  background: #f0f9eb;
  border: 1px solid #e1f3d8;
  color: #67C23A;
  font-weight: bold;
}

.transfer-customer {
  color: #E91E63;
  cursor: pointer;
  font-weight: 500;
}
.transfer-customer:hover { text-decoration: underline; }
</style>
