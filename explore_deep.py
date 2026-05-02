"""
深度探索原CRM所有子页面 - 直接访问iframe内容
"""
import asyncio
import json
import os
from playwright.async_api import async_playwright

USERNAME = "18335162275"
PASSWORD = "123456"
VERIFY_CODE = "2110"

SCREENSHOT_DIR = "C:/Users/10517/WorkBuddy/20260429105535/screenshots/crm_explore"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

all_results = {}

async def explore_iframe_page(context, url, name, label):
    """新开一个标签页访问iframe内容"""
    page = await context.new_page()
    try:
        await page.goto(url)
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(2)
        
        current_url = page.url
        if 'login' in current_url:
            print(f"  [{label}] 需要重新登录，跳过")
            await page.close()
            return None
        
        await page.screenshot(path=f"{SCREENSHOT_DIR}/{name}.png", full_page=True)
        
        # 获取详细内容
        data = await page.evaluate("""
        () => {
            // 文本内容
            const text = document.body?.innerText || '';
            
            // 所有按钮/操作
            const buttons = new Set();
            ['button', '.btn', '.layui-btn', 'a.btn', '.action-btn'].forEach(sel => {
                document.querySelectorAll(sel).forEach(el => {
                    const t = el.textContent.trim();
                    if (t && t.length < 30) buttons.add(t);
                });
            });
            
            // 表格标题
            const headers = [];
            document.querySelectorAll('th, .layui-table-col-special').forEach(el => {
                const t = el.textContent.trim();
                if (t && t.length < 20) headers.push(t);
            });
            
            // 筛选条件/标签
            const filters = new Set();
            ['select option', '.layui-form-select dd', '[class*="filter"]', '[class*="search"]'].forEach(sel => {
                document.querySelectorAll(sel).forEach(el => {
                    const t = el.textContent.trim();
                    if (t && t.length < 20) filters.add(t);
                });
            });
            
            // 标签页
            const tabs = [];
            ['.layui-tab-title li', '.tab-nav li', '[class*="tab"] li', 'ul.tabs li'].forEach(sel => {
                document.querySelectorAll(sel).forEach(el => {
                    const t = el.textContent.trim();
                    if (t && t.length < 20) tabs.push(t);
                });
            });
            
            // 所有链接
            const links = [];
            document.querySelectorAll('a[href]').forEach(el => {
                const href = el.getAttribute('href') || '';
                const text = el.textContent.trim();
                if (href && text && !href.startsWith('#') && text.length < 30) {
                    links.push({text, href});
                }
            });
            
            // 表单字段
            const formFields = [];
            document.querySelectorAll('label, .layui-form-label, [class*="label"]').forEach(el => {
                const t = el.textContent.trim();
                if (t && t.length < 20 && !t.includes('\\n')) formFields.push(t);
            });
            
            return {
                text_preview: text.slice(0, 2000),
                buttons: [...buttons],
                headers,
                filters: [...filters],
                tabs: [...new Set(tabs)],
                links: [...new Map(links.map(l => [l.text, l])).values()].slice(0, 30),
                formFields: [...new Set(formFields)],
                title: document.title
            };
        }
        """)
        
        all_results[name] = {
            'url': url,
            'label': label,
            **data
        }
        
        print(f"\n{'='*50}")
        print(f"[{label}]")
        print(f"  按钮: {data['buttons'][:15]}")
        print(f"  表头: {data['headers'][:15]}")
        print(f"  标签页: {data['tabs']}")
        print(f"  表单字段: {data['formFields'][:15]}")
        if data['links']:
            print(f"  链接: {[l['text'] for l in data['links'][:10]]}")
        
        await page.close()
        return data
        
    except Exception as e:
        print(f"  [{label}] 错误: {e}")
        await page.close()
        return None

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        
        # 先登录获取session
        login_page = await context.new_page()
        await login_page.goto("https://guwen.zhudaicms.com/manage/index/login")
        await login_page.wait_for_load_state("networkidle")
        await login_page.fill('#kefu_number', USERNAME)
        await login_page.fill('#kefu_password', PASSWORD)
        await login_page.fill('#smscode', VERIFY_CODE)
        await login_page.click('button.login-button')
        await login_page.wait_for_load_state("networkidle")
        await asyncio.sleep(3)
        print(f"登录状态: {login_page.url}")
        await login_page.close()
        
        # 探索所有子页面（iframe内容URL）
        pages_to_explore = [
            # 客户管理
            ("clients_list", "https://guwen.zhudaicms.com/manage/kefu_clients/index.html", "我的客户列表"),
            ("clients_pool_public", "https://guwen.zhudaicms.com/manage/kefu_clients/index.html?pool_type=3", "公共池客户"),
            ("clients_reassign", "https://guwen.zhudaicms.com/manage/kefu_clients/index.html?pool_type=2", "再分配客户"),
            ("clients_important", "https://guwen.zhudaicms.com/manage/kefu_clients/important.html", "重要客户"),
            ("clients_follow_today", "https://guwen.zhudaicms.com/manage/kefu_clients/follow.html", "今日跟进"),
            ("clients_add", "https://guwen.zhudaicms.com/manage/kefu_clients/add_client.html", "新增客户"),
            ("client_detail", "https://guwen.zhudaicms.com/manage/kefu_clients/edit_client_info.html", "客户详情"),
            ("clients_remind", "https://guwen.zhudaicms.com/manage/kefu_clients/remind.html", "备忘提醒"),
            ("clients_transfer", "https://guwen.zhudaicms.com/manage/kefu_clients/transfer_log.html", "转移记录"),
            ("clients_number_check", "https://guwen.zhudaicms.com/manage/kefu_clients/number_check.html", "号码查重"),
            # 贷款件
            ("loan_list", "https://guwen.zhudaicms.com/manage/loan_case/index.html", "贷款件列表"),
            ("loan_add", "https://guwen.zhudaicms.com/manage/loan_case/add.html", "新增贷款件"),
            # 数据统计
            ("stats_main", "https://guwen.zhudaicms.com/manage/kefu_clients/stats.html", "数据统计"),
            ("stats_team2", "https://guwen.zhudaicms.com/manage/kefu_clients/team_stats.html", "团队统计"),
            # 系统设置/团队
            ("system_settings", "https://guwen.zhudaicms.com/manage/settings/index.html", "系统设置"),
            ("team_manage", "https://guwen.zhudaicms.com/manage/kefu/index.html", "顾问管理"),
            ("dept_manage", "https://guwen.zhudaicms.com/manage/dept/index.html", "部门管理"),
            # 公告
            ("notice_manage", "https://guwen.zhudaicms.com/manage/notice/index.html", "公告管理"),
            # 绩效
            ("performance_manage", "https://guwen.zhudaicms.com/manage/performance/index.html", "绩效管理"),
            # 数据导入
            ("data_import", "https://guwen.zhudaicms.com/manage/kefu_clients/import.html", "数据导入"),
            ("data_export", "https://guwen.zhudaicms.com/manage/kefu_clients/export.html", "数据导出"),
            # 日志
            ("logs_main", "https://guwen.zhudaicms.com/manage/logs/index.html", "系统日志"),
        ]
        
        for name, url, label in pages_to_explore:
            await explore_iframe_page(context, url, name, label)
            await asyncio.sleep(0.5)
        
        # 保存
        with open(f"{SCREENSHOT_DIR}/deep_results.json", "w", encoding="utf-8") as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)
        
        print(f"\n\n===完整探索完成，结果已保存===")
        await browser.close()

asyncio.run(main())
