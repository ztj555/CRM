# MEMORY.md

## 用户信息
- **账号**：19883890925
- **登录用户**：徐钰蓉，储备主管，杭州一区-一区二部2
- **系统**：融鑫汇-客户管理系统（客帮手）

## 项目目标
- 依据融鑫汇CRM开发高度类似的局域网CRM系统
- 目标规模：50万客户库 + 20名员工并发使用
- 倾向分步开发（先MVP后完善），避免一次性需求过多

## 系统信息
- **原CRM URL**：https://guwen.zhudaicms.com/manage/index/index.html
- **原CRM账号**：19883890925，密码：123456
- **验证码**：每日更新，链接：https://www2.zhudaicms.com/important/get_guding_yzm.html

## 新CRM系统（局域网版）- 开发中

### 技术栈
- **前端**：Vue 3 + Vite + Element Plus + ECharts
- **后端**：Python FastAPI + SQLAlchemy
- **数据库**：SQLite（零配置，crm.db在项目根目录）
- **认证**：JWT（python-jose）+ bcrypt
- **Node.js路径**：`C:\node-v20.18.0-win-x64\node.exe`
- **Python路径**：`C:\Users\10517\.workbuddy\binaries\python\versions\3.13.12\python.exe`

### 文件结构
- `backend/main.py` — FastAPI后端主文件
- `backend/requirements.txt` — Python依赖
- `crm-frontend/` — Vue 3前端项目（已npm install）
- `启动全部.bat` — 一键启动前后端
- `启动后端.bat` — 单独启动后端（8080）
- `启动前端.bat` — 单独启动前端（5173）
- `停止全部.bat` — 一键停止所有服务
- `crm.db` — SQLite数据库文件（启动后自动创建）

### 默认账号
- admin / admin123（管理员）
- test1 / 123456、test2 / 123456、test3 / 123456（顾问）

## 开发进度（2026-04-30）- 全部功能补齐完成

### 数据库表
- departments（部门）
- users（用户）
- customers（客户）
- customer_assignments（客户分配）
- customer_remarks（客户备注）
- customer_reminders（客户备忘提醒）【新增2026-04-30】
- loan_cases（贷款件）
- performance_targets（绩效目标）

### 关键技术注意事项
- SQLite主键必须用Integer不能用BigInteger（自增依赖）
- SQLAlchemy 2.x用`cascade="all, delete-orphan"`（不用cascade_all）
- 所有模型需有`to_dict()`方法用于API序列化
- Python启动时中文输出需处理Windows GBK编码（启动脚本已加chcp 65001）
- 前后端分离，前端代理/api到8080端口
- CustomerUpd支持phone字段更新（含重复检查）
- pool_type: 1=我的客户 2=再分配 3=公共池 4=必跟进

## 深度探索新发现（2026-04-29）
- 客户详情页URL：/manage/kefu_clients/edit_client_info.html?id={ID}
- 客户详情9大信息分类（基本/身份/房产/车产/保单/信用/负债/需求/全部）
- 18个快捷备注按钮（未接/拒接/空号/停机等）
- 备注提示词（引导顾问记录8个要点）
- 完整状态枚举17+种
- 系统设置：接受新数据开关 + 隐藏客户属性（10列）

## 产出文件
- `融鑫汇CRM系统功能分析文档.md` - 完整功能分析
- `CRM系统可行性分析报告.md` - 可行性分析（50w客户/20人/5阶段）
- `screenshots/` - 截图目录

## 开发进度（2026-04-30）- 4项功能全部完成

### 1. 客户详情抽屉（CustomerDetail.vue）
- 9大Tab分类：基本/身份/房产/车产/保单/信用/负债/需求/全部
- 18个快捷备注按钮（未接/拒接/空号/停机等）
- 顶部操作栏：星级评分 + 状态选择 + 重要/锁定标记
- 布局：`.main-content { display:flex }` 横向布局 + `.detail-body` + `.remark-panel`
- 备注区新增"备注后状态"下拉，提交备注时同步更新客户状态
- 月负债合计实时计算（房贷+车贷+网贷+其他）
- quals初始化包含所有子对象

### 2. 离职人员数据分配（Team.vue Tab3）
- 真实后端：`GET /api/team/offboard` 返回离职用户+客户数
- 一键转移：`POST /api/team/reassign-all` 失效原分配并新建pool_type=2分配
- 恢复在职：`PUT /api/users/{uid}/status` status=1
- 卡片布局：头像+客户数+接收顾问选择器+转移按钮
- 切换到offboard Tab时自动加载离职列表

### 3. 日志报表增强（Logs.vue）
- 团队日报卡片：`GET /api/stats/team-daily`，今日跟进数
- 主管点评弹窗：选择备注行 → 写点评 → remark_type=1
- CSV导出：`GET /api/stats/remarks/export` StreamingResponse + UTF-8 BOM
- 日志列表：支持按顾问/日期范围/备注类型过滤，字段含customer_id便于打开详情
- 点击客户名打开CustomerDetail抽屉

### 4. 数据统计完善（Dashboard.vue）
- 来源分布饼图：`GET /api/stats/source-dist`，带图例滚动
- 状态分布柱状图：`GET /api/stats/status-dist`（带status字段）
- 使用 `echarts.getInstanceByDom()` 避免重复初始化
- 本月统计grid卡片+el-progress进度条（目标对比）

### 后端API变更
- `GET /api/stats/source-dist` - 来源分布（管理员看团队，顾问看自己）
- `GET /api/stats/status-dist` - 状态分布（返回status编号）
- `GET /api/stats/team-daily` - 团队当日跟进统计
- `GET /api/stats/remarks` - 日志列表（支持remark_type过滤）
- `GET /api/stats/remarks/export` - CSV导出（StreamingResponse UTF-8 BOM）
- `GET /api/team/offboard` - 离职用户列表（含customer_count）
- `POST /api/team/reassign-all` - 批量转移客户
- `PUT /api/users/{uid}/status` - 启用/禁用用户
- `add_remark()` 新增 `new_status: Optional[int]` 字段支持备注同时改状态
- `get_remarks()` JOIN User 返回 advisor_name
