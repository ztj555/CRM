"""
通过菜单点击完整截图所有功能页面
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

async def get_frame_data(page, frame_url, label):
    """等待并获取特定frame的数据"""
    await asyncio.sleep(2)
    
    # 找iframe
    for frame in page.frames:
        if frame.url and 'login' not in frame.url and frame.url != page.url:
            try:
                data = await frame.evaluate("""
                () => {
                    const text = document.body?.innerText || '';
                    const buttons = new Set();
                    document.querySelectorAll('button, .layui-btn, a.btn, .btn').forEach(el => {
                        const t = el.textContent.trim();
                        if (t && t.length < 30) buttons.add(t);
                    });
                    const headers = [];
                    document.querySelectorAll('th').forEach(el => {
                        const t = el.textContent.trim();
                        if (t) headers.push(t);
                    });
                    const tabs = new Set();
                    document.querySelectorAll('.layui-tab-title li, [class*="tab"] li').forEach(el => {
                        const t = el.textContent.trim();
                        if (t && t.length < 20) tabs.add(t);
                    });
                    const labels = new Set();
                    document.querySelectorAll('label, .layui-form-label, .field-label').forEach(el => {
                        const t = el.textContent.trim();
                        if (t && t.length < 25) labels.add(t);
                    });
                    const selects = new Set();
                    document.querySelectorAll('select option, .layui-select-none').forEach(el => {
                        const t = el.textContent.trim();
                        if (t && t.length < 20) selects.add(t);
                    });
                    return {
                        text: text.slice(0,2000),
                        buttons: [...buttons],
                        headers,
                        tabs: [...tabs],
                        labels: [...labels],
                        selects: [...selects]
                    };
                }
                """)
                return frame.url, data
            except Exception as e:
                pass
    return None, None

async def navigate_and_capture(page, js_call, name, label):
    """执行JS导航并截图"""
    try:
        print(f"\n[{label}] 导航中...")
        await page.evaluate(js_call)
        await asyncio.sleep(2)
        
        # 找到更新的iframe
        for frame in page.frames:
            if frame.url and 'login' not in frame.url and frame.url != page.url:
                frame_url = frame.url
                print(f"  Frame: {frame_url}")
                
                try:
                    # 截iframe截图
                    await frame.locator('body').screenshot(path=f"{SCREENSHOT_DIR}/{name}.png")
                except:
                    await page.screenshot(path=f"{SCREENSHOT_DIR}/{name}.png", full_page=True)
                
                data = await frame.evaluate("""
                () => {
                    const text = document.body?.innerText || '';
                    const buttons = new Set();
                    document.querySelectorAll('button, .layui-btn, a.btn, .btn, [class*="btn"]').forEach(el => {
                        const t = el.textContent.trim();
                        if (t && t.length < 30 && t.length > 0) buttons.add(t);
                    });
                    const headers = [];
                    document.querySelectorAll('th, .field-name, [class*="header"]').forEach(el => {
                        const t = el.textContent.trim();
                        if (t && t.length < 20) headers.push(t);
                    });
                    const tabs = new Set();
                    document.querySelectorAll('.layui-tab-title li, [class*="tab"] li').forEach(el => {
                        const t = el.textContent.trim();
                        if (t && t.length < 20) tabs.add(t);
                    });
                    const labels = new Set();
                    document.querySelectorAll('label, .layui-form-label').forEach(el => {
                        const t = el.textContent.trim();
                        if (t && t.length < 25) labels.add(t);
                    });
                    return {
                        text: text.slice(0,2000),
                        buttons: [...buttons].slice(0,30),
                        headers: [...new Set(headers)],
                        tabs: [...tabs],
                        labels: [...labels].slice(0,30)
                    };
                }
                """)
                
                all_data[name] = {'url': frame_url, 'label': label, **data}
                print(f"  按钮: {data['buttons'][:10]}")
                print(f"  表头: {data['headers'][:10]}")
                print(f"  标签: {data['tabs'][:5]}")
                print(f"  字段: {data['labels'][:10]}")
                return
        
        print(f"  未找到frame，截主页")
        await page.screenshot(path=f"{SCREENSHOT_DIR}/{name}.png", full_page=True)
        
    except Exception as e:
        print(f"  [{label}] 错误: {e}")

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()
        
        # 登录
        await page.goto("https://guwen.zhudaicms.com/manage/index/login")
        await page.wait_for_load_state("networkidle")
        await page.fill('#kefu_number', USERNAME)
        await page.fill('#kefu_password', PASSWORD)
        await page.fill('#smscode', VERIFY_CODE)
        await page.click('button.login-button')
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(3)
        print(f"登录: {page.url}")
        
        # 截主页全图
        await page.screenshot(path=f"{SCREENSHOT_DIR}/00_main_full.png", full_page=True)
        print("主页截图完成")
        
        # 通过Open()函数导航各功能页面
        pages = [
            # (JS调用, 文件名, 标签)
            ("Open('客户列表','/manage/kefu_clients/index.html')", "p_clients", "我的客户"),
            ("Open('公共池','/manage/kefu_clients/index.html?pool_type=3')", "p_pool_public", "公共池"),
            ("Open('再分配','/manage/kefu_clients/index.html?pool_type=2')", "p_reassign", "再分配客户"),
            ("Open('必跟进','/manage/kefu_clients/index.html?pool_type=4')", "p_follow_must", "必跟进客户"),
            ("Open('在审件管理','/manage/loan_case/index.html')", "p_loan", "在审件/贷款件"),
            ("Open('业绩排行榜','/manage/kefu_clients/performance_ranking.html')", "p_ranking", "业绩排行榜"),
            ("Open('日志报表','/manage/kefu_dailysimple/index.html')", "p_logs", "日志报表"),
            ("Open('工作简报','/manage/kefu_dailysimple/simple.html')", "p_brief", "工作简报"),
            ("Open('数据统计','/manage/kefu_clients/stats.html')", "p_stats", "数据统计"),
            ("Open('创收分析','/manage/kefu_clients/income_stats.html')", "p_income", "创收分析"),
            ("Open('团队客户','/manage/kefu_clients/team_clients.html')", "p_team_clients", "团队客户"),
            ("Open('团队管理','/manage/kefu/index.html')", "p_team_manage", "团队管理"),
            ("Open('离职人数据分配','/manage/kefu_clients/offboard.html')", "p_offboard", "离职人数据分配"),
            ("Open('通话管理','/manage/phone/index.html')", "p_phone", "通话管理"),
            ("Open('绩效目标','/manage/kefu_clients/performance_target.html')", "p_performance", "绩效目标"),
            ("Open('公告','/manage/kefu_dailysimple/notice.html')", "p_notice", "公告"),
            ("Open('个人中心','/manage/kefu_account/info.html')", "p_profile", "个人中心"),
            ("Open('修改密码','/manage/kefu_account/editpassword.html')", "p_password", "修改密码"),
            ("Open('发布公告','/manage/gonggao/publishgonggao.html')", "p_pub_notice", "发布公告"),
            ("Open('发布滚动条','/manage/gonggao/addxiaoxi.html')", "p_ticker", "发布滚动条"),
            ("Open('系统设置','/manage/kefu_account/setting.html')", "p_settings", "系统设置"),
            ("Open('档案信息','/manage/kefu_account/info.html')", "p_archive", "档案信息"),
        ]
        
        for js_call, name, label in pages:
            await navigate_and_capture(page, js_call, name, label)
            await asyncio.sleep(1)
        
        # 特别处理：客户详情页
        await navigate_and_capture(
            page,
            "Open('客户详情','/manage/kefu_clients/index.html')",
            "p_clients_view",
            "客户列表详细"
        )
        
        # 截图带有iframe的完整主页
        for frame in page.frames:
            if frame.url and 'login' not in frame.url and frame.url != page.url:
                print(f"\n最终Frame: {frame.url}")
        
        # 保存
        with open(f"{SCREENSHOT_DIR}/full_nav_data.json", "w", encoding="utf-8") as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)
        print(f"\n结果已保存")
        
        await browser.close()

asyncio.run(main())
