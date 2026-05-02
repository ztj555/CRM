"""
全面探索原CRM系统功能 - 以主管理员身份登录
"""
import asyncio
import json
import os
from playwright.async_api import async_playwright

BASE_URL = "https://guwen.zhudaicms.com/manage/index"
USERNAME = "18335162275"
PASSWORD = "123456"
VERIFY_CODE = "2110"

SCREENSHOT_DIR = "C:/Users/10517/WorkBuddy/20260429105535/screenshots/crm_explore"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

results = {}

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()
        
        # 1. 登录
        print("=== 登录 ===")
        await page.goto(f"{BASE_URL}/login")
        await page.wait_for_load_state("networkidle")
        await page.screenshot(path=f"{SCREENSHOT_DIR}/01_login.png")
        
        # 填写登录表单
        try:
            await page.fill('input[name="username"], input[placeholder*="账号"], input[placeholder*="手机"]', USERNAME)
            await page.fill('input[name="password"], input[type="password"]', PASSWORD)
            # 验证码
            vc_input = page.locator('input[placeholder*="验证码"], input[name="verifycode"], input[name="yzm"]')
            if await vc_input.count() > 0:
                await vc_input.fill(VERIFY_CODE)
            await page.screenshot(path=f"{SCREENSHOT_DIR}/01b_login_filled.png")
            await page.click('button[type="submit"], .login-btn, input[type="submit"]')
            await page.wait_for_load_state("networkidle")
            await asyncio.sleep(2)
        except Exception as e:
            print(f"登录异常: {e}")
        
        await page.screenshot(path=f"{SCREENSHOT_DIR}/02_after_login.png")
        print(f"当前URL: {page.url}")
        
        # 2. 获取主页面结构
        print("=== 分析主页面 ===")
        content = await page.content()
        title = await page.title()
        print(f"页面标题: {title}")
        
        # 获取所有菜单项
        menu_items = await page.evaluate("""
        () => {
            const menus = [];
            // 查找各种可能的菜单选择器
            const selectors = [
                '.nav li', '.menu li', '.sidebar li', '.aside li',
                'nav li', 'aside li', '.left-nav li', '.side-menu li',
                '[class*="menu"] li', '[class*="nav"] li', '[id*="menu"] li',
                '.layui-nav li', '.layui-menu li'
            ];
            
            for (const sel of selectors) {
                const els = document.querySelectorAll(sel);
                if (els.length > 0) {
                    els.forEach(el => {
                        const text = el.textContent.trim();
                        const link = el.querySelector('a')?.href || '';
                        if (text && text.length < 30) {
                            menus.push({selector: sel, text, link});
                        }
                    });
                    break;
                }
            }
            return menus.slice(0, 50);
        }
        """)
        print(f"菜单项: {json.dumps(menu_items, ensure_ascii=False, indent=2)}")
        results['menus'] = menu_items
        
        # 3. 截图并探索各主要页面
        pages_to_explore = [
            ("index", "/index/index.html", "主页"),
            ("clients", "/kefu_clients/index.html", "客户列表"),
            ("client_pool", "/kefu_clients/pool.html", "客户池"),
            ("loan_cases", "/loan_case/index.html", "贷款件"),
            ("stats", "/stats/index.html", "统计"),
            ("team", "/team/index.html", "团队"),
            ("settings", "/settings/index.html", "设置"),
            ("report", "/report/index.html", "报表"),
            ("performance", "/performance/index.html", "绩效"),
            ("logs", "/logs/index.html", "日志"),
            ("notice", "/notice/index.html", "公告"),
            ("follow", "/follow/index.html", "跟进"),
        ]
        
        for name, path, label in pages_to_explore:
            try:
                url = f"https://guwen.zhudaicms.com/manage{path}"
                print(f"\n=== 探索: {label} ({url}) ===")
                await page.goto(url)
                await page.wait_for_load_state("networkidle")
                await asyncio.sleep(1)
                
                # 截图
                await page.screenshot(path=f"{SCREENSHOT_DIR}/{name}.png", full_page=True)
                
                # 获取页面文本内容
                text = await page.evaluate("() => document.body.innerText")
                print(f"{label} 内容: {text[:300]}")
                results[name] = {'url': url, 'text': text[:500], 'title': await page.title()}
                
            except Exception as e:
                print(f"{label} 探索失败: {e}")
                results[name] = {'error': str(e)}
        
        # 4. 回到主页，详细分析菜单结构
        print("\n=== 详细分析主菜单 ===")
        await page.goto("https://guwen.zhudaicms.com/manage/index/index.html")
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(2)
        await page.screenshot(path=f"{SCREENSHOT_DIR}/main_full.png", full_page=True)
        
        # 获取所有链接
        links = await page.evaluate("""
        () => {
            const links = [];
            document.querySelectorAll('a[href]').forEach(a => {
                const href = a.href;
                const text = a.textContent.trim();
                if (text && href && !href.startsWith('javascript') && text.length < 50) {
                    links.push({text, href});
                }
            });
            return [...new Map(links.map(l => [l.text, l])).values()].slice(0, 100);
        }
        """)
        print(f"所有链接: {json.dumps(links, ensure_ascii=False, indent=2)}")
        results['all_links'] = links
        
        # 5. 如果是iframe布局，尝试进入iframe
        frames = page.frames
        print(f"\niframes数量: {len(frames)}")
        for i, frame in enumerate(frames):
            try:
                frame_url = frame.url
                if frame_url and frame_url != page.url and 'about:blank' not in frame_url:
                    print(f"Frame {i}: {frame_url}")
                    frame_content = await frame.evaluate("() => document.body?.innerText?.slice(0, 200)")
                    print(f"Frame内容: {frame_content}")
                    results[f'frame_{i}'] = {'url': frame_url, 'content': frame_content}
            except Exception as e:
                print(f"Frame {i} 错误: {e}")
        
        # 保存结果
        with open(f"{SCREENSHOT_DIR}/results.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print("\n=== 探索完成 ===")
        await browser.close()

asyncio.run(main())
