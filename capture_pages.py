"""
对每个功能页面单独截图
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

all_data = {}

async def capture_frame(context, url, name, label):
    """用独立context截图"""
    page = await context.new_page()
    try:
        await page.goto(url)
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(2)
        
        # 检查是否是真实内容还是被重定向
        cur_url = page.url
        if 'login' in cur_url and url != cur_url:
            print(f"  [{label}] 重定向到登录页，跳过")
            await page.close()
            return
        
        await page.screenshot(path=f"{SCREENSHOT_DIR}/{name}.png", full_page=True)
        
        data = await page.evaluate("""
        () => {
            const text = document.body?.innerText || '';
            const buttons = new Set();
            document.querySelectorAll('button, .layui-btn, .btn').forEach(el => {
                const t = el.textContent.trim();
                if (t && t.length < 30) buttons.add(t);
            });
            const headers = [];
            document.querySelectorAll('th').forEach(el => {
                const t = el.textContent.trim();
                if (t && t.length < 20) headers.push(t);
            });
            const tabs = new Set();
            document.querySelectorAll('.layui-tab-title li').forEach(el => {
                const t = el.textContent.trim();
                if (t) tabs.add(t);
            });
            const labels = new Set();
            document.querySelectorAll('label, .layui-form-label').forEach(el => {
                const t = el.textContent.trim();
                if (t && t.length < 25) labels.add(t);
            });
            return {
                text: text.slice(0, 2000),
                buttons: [...buttons].slice(0, 20),
                headers: [...new Set(headers)].slice(0,20),
                tabs: [...tabs].slice(0,10),
                labels: [...labels].slice(0,20)
            };
        }
        """)
        
        all_data[name] = {'url': cur_url, 'label': label, **data}
        print(f"\n[{label}] {cur_url}")
        print(f"  按钮: {data['buttons'][:8]}")
        print(f"  表头: {data['headers'][:8]}")
        print(f"  标签: {data['tabs'][:5]}")
        if data['text']:
            print(f"  文本预览: {data['text'][:200]}")
        
    except Exception as e:
        print(f"  [{label}] 错误: {e}")
    finally:
        await page.close()

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        
        # 登录
        login_page = await context.new_page()
        await login_page.goto("https://guwen.zhudaicms.com/manage/index/login")
        await login_page.wait_for_load_state("networkidle")
        await login_page.fill('#kefu_number', USERNAME)
        await login_page.fill('#kefu_password', PASSWORD)
        await login_page.fill('#smscode', VERIFY_CODE)
        await login_page.click('button.login-button')
        await login_page.wait_for_load_state("networkidle")
        await asyncio.sleep(3)
        print(f"登录: {login_page.url}")
        await login_page.close()
        
        # 直接访问各功能页面（在同一context内）
        pages = [
            ("https://guwen.zhudaicms.com/manage/kefu_clients/index.html", "pg_clients", "我的客户"),
            ("https://guwen.zhudaicms.com/manage/kefu_clients/index.html?pool_type=3", "pg_pool_public", "公共池"),
            ("https://guwen.zhudaicms.com/manage/kefu_clients/index.html?pool_type=2", "pg_reassign", "再分配"),
            ("https://guwen.zhudaicms.com/manage/kefu_clients/index.html?pool_type=4", "pg_follow_must", "必跟进"),
            ("https://guwen.zhudaicms.com/manage/loan_case/index.html", "pg_loan", "在审件管理"),
            ("https://guwen.zhudaicms.com/manage/kefu_clients/performance_ranking.html", "pg_ranking", "业绩排行榜"),
            ("https://guwen.zhudaicms.com/manage/kefu_dailysimple/index.html", "pg_logs", "日志报表"),
            ("https://guwen.zhudaicms.com/manage/kefu_dailysimple/simple.html", "pg_simple", "工作简报"),
            ("https://guwen.zhudaicms.com/manage/kefu_clients/stats.html", "pg_stats", "数据统计"),
            ("https://guwen.zhudaicms.com/manage/kefu_clients/income_stats.html", "pg_income", "创收分析"),
            ("https://guwen.zhudaicms.com/manage/kefu_clients/team_clients.html", "pg_team_clients", "团队客户"),
            ("https://guwen.zhudaicms.com/manage/kefu/index.html", "pg_team", "团队管理"),
            ("https://guwen.zhudaicms.com/manage/kefu_clients/offboard.html", "pg_offboard", "离职人数据"),
            ("https://guwen.zhudaicms.com/manage/phone/index.html", "pg_phone", "通话管理"),
            ("https://guwen.zhudaicms.com/manage/kefu_clients/performance_target.html", "pg_perf_target", "绩效目标"),
            ("https://guwen.zhudaicms.com/manage/kefu_dailysimple/notice.html", "pg_notice", "公告"),
            ("https://guwen.zhudaicms.com/manage/kefu_account/info.html", "pg_profile", "个人中心"),
            ("https://guwen.zhudaicms.com/manage/kefu_account/editpassword.html", "pg_password", "修改密码"),
            ("https://guwen.zhudaicms.com/manage/gonggao/publishgonggao.html", "pg_pub_notice", "发布公告"),
            ("https://guwen.zhudaicms.com/manage/gonggao/addxiaoxi.html", "pg_ticker", "发布滚动条"),
            ("https://guwen.zhudaicms.com/manage/kefu_account/setting.html", "pg_settings", "系统设置"),
            ("https://guwen.zhudaicms.com/manage/kefu_clients/edit_client_info.html", "pg_client_detail", "客户详情"),
        ]
        
        for url, name, label in pages:
            await capture_frame(context, url, name, label)
        
        # 保存
        with open(f"{SCREENSHOT_DIR}/page_data.json", "w", encoding="utf-8") as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)
        print(f"\n完成！结果保存至 {SCREENSHOT_DIR}/page_data.json")
        
        await browser.close()

asyncio.run(main())
