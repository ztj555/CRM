"""
全面探索原CRM系统功能 - 修复版
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

results = {}

async def explore_page(page, name, label):
    """截图并获取页面结构"""
    await asyncio.sleep(1.5)
    await page.screenshot(path=f"{SCREENSHOT_DIR}/{name}.png", full_page=True)
    
    # 获取文本内容
    text = await page.evaluate("() => document.body?.innerText || ''")
    url = page.url
    
    # 获取所有按钮和操作元素
    actions = await page.evaluate("""
    () => {
        const items = [];
        ['button', 'a', '[class*="btn"]', '[class*="tab"]', 'th', '.layui-tab-title li'].forEach(sel => {
            document.querySelectorAll(sel).forEach(el => {
                const t = el.textContent.trim();
                if (t && t.length < 30 && t.length > 0) items.push(t);
            });
        });
        return [...new Set(items)].slice(0, 80);
    }
    """)
    
    # 获取表格列名
    headers = await page.evaluate("""
    () => {
        const ths = [];
        document.querySelectorAll('th, .layui-table th, thead td').forEach(el => {
            const t = el.textContent.trim();
            if (t) ths.push(t);
        });
        return ths;
    }
    """)
    
    # 获取表单字段
    fields = await page.evaluate("""
    () => {
        const fields = [];
        document.querySelectorAll('label, .form-label, .layui-form-label').forEach(el => {
            const t = el.textContent.trim();
            if (t && t.length < 20) fields.push(t);
        });
        return [...new Set(fields)];
    }
    """)
    
    result = {
        'url': url, 
        'text_preview': text[:1000],
        'actions': actions,
        'table_headers': headers,
        'form_fields': fields
    }
    results[name] = result
    print(f"\n{'='*50}")
    print(f"[{label}] {url}")
    print(f"操作按钮: {actions[:20]}")
    print(f"表格列: {headers}")
    print(f"表单字段: {fields}")
    return result

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()
        
        # ===== 登录 =====
        print("=== 登录 ===")
        await page.goto("https://guwen.zhudaicms.com/manage/index/login")
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(1)
        
        await page.fill('#kefu_number', USERNAME)
        await page.fill('#kefu_password', PASSWORD)
        await page.fill('#smscode', VERIFY_CODE)
        await page.screenshot(path=f"{SCREENSHOT_DIR}/01_login_filled.png")
        
        await page.click('button.login-button')
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(3)
        
        print(f"登录后URL: {page.url}")
        await page.screenshot(path=f"{SCREENSHOT_DIR}/02_after_login.png", full_page=True)
        
        # 检查是否登录成功
        if 'login' in page.url.lower():
            text = await page.evaluate("() => document.body.innerText")
            print(f"登录失败，页面内容: {text[:300]}")
        else:
            print("登录成功！")
        
        # ===== 分析主页面/菜单 =====
        print("\n=== 主页分析 ===")
        
        # 检查是否有iframe
        frames = page.frames
        print(f"Frame数量: {len(frames)}")
        for i, frame in enumerate(frames):
            print(f"Frame {i}: {frame.url}")
        
        # 截主页全图
        await page.screenshot(path=f"{SCREENSHOT_DIR}/03_main.png", full_page=True)
        
        # 获取所有菜单和链接
        nav_links = await page.evaluate("""
        () => {
            const links = [];
            // 找所有导航链接
            const selectors = [
                '.layui-nav a', '.nav a', '.menu a', '.sidebar a', 
                '.aside a', 'nav a', '[class*="menu"] a', '[class*="nav"] a',
                '.left-nav a', '.side-nav a'
            ];
            for (const sel of selectors) {
                const els = document.querySelectorAll(sel);
                if (els.length > 2) {
                    els.forEach(el => {
                        const text = el.textContent.trim();
                        const href = el.href || el.getAttribute('href') || '';
                        if (text && text.length < 25) {
                            links.push({text, href, selector: sel});
                        }
                    });
                }
            }
            if (links.length === 0) {
                // 退回找所有a标签
                document.querySelectorAll('a').forEach(el => {
                    const text = el.textContent.trim();
                    const href = el.href || '';
                    if (text && text.length < 25 && href && !href.includes('javascript')) {
                        links.push({text, href});
                    }
                });
            }
            return [...new Map(links.map(l => [l.text, l])).values()].slice(0, 100);
        }
        """)
        print(f"导航链接: {json.dumps(nav_links, ensure_ascii=False, indent=2)}")
        results['nav_links'] = nav_links
        
        # ===== 探索核心页面 =====
        # 客户管理相关
        pages = [
            # (名称, URL路径, 标签)
            ("main", "index/index.html", "主页仪表盘"),
            ("clients_index", "kefu_clients/index.html", "客户列表"),
            ("clients_pool", "kefu_clients/pool.html", "公共池"),
            ("clients_reassign", "kefu_clients/reassign.html", "再分配"),
            ("clients_important", "kefu_clients/important.html", "重要客户"),
            ("clients_follow", "kefu_clients/follow.html", "跟进中"),
            ("clients_add", "kefu_clients/add.html", "新增客户"),
            ("loan_index", "loan_case/index.html", "贷款件列表"),
            ("loan_add", "loan_case/add.html", "新增贷款件"),
            ("stats_index", "stats/index.html", "数据统计"),
            ("stats_team", "stats/team.html", "团队统计"),
            ("stats_personal", "stats/personal.html", "个人统计"),
            ("report_index", "report/index.html", "报表"),
            ("report_daily", "report/daily.html", "日报"),
            ("report_weekly", "report/weekly.html", "周报"),
            ("team_index", "team/index.html", "团队管理"),
            ("team_members", "team/members.html", "成员管理"),
            ("team_dept", "team/dept.html", "部门管理"),
            ("notice_index", "notice/index.html", "公告"),
            ("notice_list", "notice/list.html", "公告列表"),
            ("settings_index", "settings/index.html", "系统设置"),
            ("settings_data", "settings/data.html", "数据设置"),
            ("kefu_index", "kefu/index.html", "顾问管理"),
            ("admin_index", "admin/index.html", "管理员"),
            ("performance_index", "performance/index.html", "绩效"),
            ("task_index", "task/index.html", "任务"),
            ("follow_up", "follow_up/index.html", "跟进记录"),
            ("reminder_index", "reminder/index.html", "提醒"),
        ]
        
        for name, path, label in pages:
            try:
                url = f"https://guwen.zhudaicms.com/manage/{path}"
                await page.goto(url)
                await page.wait_for_load_state("networkidle")
                await explore_page(page, name, label)
            except Exception as e:
                print(f"{label} 失败: {e}")
                results[name] = {'error': str(e)}
        
        # ===== 尝试找真实菜单结构 =====
        print("\n=== 回主页，分析实际菜单 ===")
        await page.goto("https://guwen.zhudaicms.com/manage/index/index.html")
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(2)
        
        # 获取完整的HTML以分析菜单结构
        html = await page.content()
        
        # 查找layui的iframe结构
        import re
        iframes = re.findall(r'<iframe[^>]*src=["\']([^"\']+)["\'][^>]*>', html)
        print(f"iframes: {iframes}")
        
        # 查找所有href
        hrefs = re.findall(r'href=["\']([^"\']+)["\']', html)
        manage_hrefs = [h for h in hrefs if 'manage' in h or '.html' in h]
        print(f"manage相关链接: {manage_hrefs[:30]}")
        
        results['iframes'] = iframes
        results['manage_hrefs'] = manage_hrefs[:30]
        
        # 如果是layui的frame布局，进入main frame
        main_frame = None
        for frame in page.frames:
            if frame.url and 'login' not in frame.url and frame.url != page.url:
                main_frame = frame
                print(f"找到主Frame: {frame.url}")
                
                frame_links = await frame.evaluate("""
                () => {
                    const links = [];
                    document.querySelectorAll('a').forEach(el => {
                        const text = el.textContent.trim();
                        const href = el.href || el.getAttribute('href') || '';
                        if (text && href) links.push({text: text.slice(0,30), href});
                    });
                    return [...new Map(links.map(l => [l.text, l])).values()].slice(0, 80);
                }
                """)
                print(f"Frame链接: {json.dumps(frame_links, ensure_ascii=False, indent=2)}")
                results['main_frame_links'] = frame_links
        
        # 保存结果
        with open(f"{SCREENSHOT_DIR}/results.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\n结果已保存到 {SCREENSHOT_DIR}/results.json")
        
        await browser.close()

asyncio.run(main())
