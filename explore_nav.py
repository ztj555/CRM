"""
通过iframe导航探索CRM系统
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

async def explore_in_frame(page, iframe_url, name, label):
    """修改主页中的iframe src来探索不同页面"""
    try:
        # 修改iframe的src
        await page.evaluate(f"""
        () => {{
            const iframe = document.querySelector('iframe');
            if (iframe) iframe.src = '{iframe_url}';
        }}
        """)
        await asyncio.sleep(3)
        
        # 获取iframe内容
        frames = page.frames
        target_frame = None
        for frame in frames:
            if 'index.html' not in frame.url or iframe_url.split('/')[-1] in frame.url:
                if frame.url != page.url and 'login' not in frame.url:
                    target_frame = frame
        
        # 找包含内容的frame
        for frame in frames:
            if frame.url and frame.url != page.url:
                frame_url = frame.url
                print(f"  Frame URL: {frame_url}")
                
                if 'login' not in frame_url:
                    data = await frame.evaluate("""
                    () => {
                        const text = document.body?.innerText || '';
                        
                        const buttons = new Set();
                        document.querySelectorAll('button, .layui-btn, a.btn').forEach(el => {
                            const t = el.textContent.trim();
                            if (t && t.length < 30 && t.length > 0) buttons.add(t);
                        });
                        
                        const headers = [];
                        document.querySelectorAll('th').forEach(el => {
                            const t = el.textContent.trim();
                            if (t) headers.push(t);
                        });
                        
                        const tabs = [];
                        document.querySelectorAll('.layui-tab-title li, .tab li, [class*="tab-item"]').forEach(el => {
                            const t = el.textContent.trim();
                            if (t && t.length < 20) tabs.push(t);
                        });
                        
                        const labels = [];
                        document.querySelectorAll('label, .layui-form-label').forEach(el => {
                            const t = el.textContent.trim();
                            if (t && t.length < 20) labels.push(t);
                        });
                        
                        return {
                            text: text.slice(0, 1500),
                            buttons: [...buttons],
                            headers,
                            tabs,
                            labels: [...new Set(labels)]
                        };
                    }
                    """)
                    
                    all_results[name] = {'url': frame_url, 'label': label, **data}
                    print(f"\n[{label}] {frame_url}")
                    print(f"  按钮: {data['buttons'][:10]}")
                    print(f"  表头: {data['headers'][:10]}")
                    print(f"  标签页: {data['tabs'][:10]}")
                    print(f"  字段: {data['labels'][:10]}")
                    
                    # 截图
                    await frame.locator('body').screenshot(path=f"{SCREENSHOT_DIR}/{name}.png")
                    return data
        
        print(f"  [{label}] 未找到有效frame")
        return None
        
    except Exception as e:
        print(f"  [{label}] 错误: {e}")
        return None

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
        
        # 获取cookie
        cookies = await context.cookies()
        print(f"Cookies: {[c['name'] for c in cookies]}")
        
        # 通过左侧菜单点击来导航
        # 先获取主页的完整HTML来理解菜单结构
        html = await page.content()
        
        # 保存主页HTML以便分析
        with open(f"{SCREENSHOT_DIR}/main_page.html", "w", encoding="utf-8") as f:
            f.write(html)
        
        # 截主页全屏
        await page.screenshot(path=f"{SCREENSHOT_DIR}/main_home.png", full_page=True)
        
        # 分析左侧菜单
        menu_data = await page.evaluate("""
        () => {
            const result = {
                navItems: [],
                leftNav: [],
                topNav: [],
                allText: document.body.innerText.slice(0, 3000)
            };
            
            // 顶部导航
            document.querySelectorAll('.top-nav li, .header-nav li, .nav-top li').forEach(el => {
                const t = el.textContent.trim();
                if (t && t.length < 20) result.topNav.push(t);
            });
            
            // 左侧菜单
            document.querySelectorAll('.left-nav li, .side-nav li, .sidebar-menu li, .nav-menu li, .menu-list li').forEach(el => {
                const t = el.textContent.trim();
                const a = el.querySelector('a');
                const href = a?.href || a?.getAttribute('href') || '';
                if (t && t.length < 30) result.leftNav.push({text: t, href});
            });
            
            // 通用菜单查找
            document.querySelectorAll('li[class*="menu"], li[class*="nav"], [onclick*="loadPage"], [onclick*="iframe"]').forEach(el => {
                const t = el.textContent.trim();
                const onclick = el.getAttribute('onclick') || '';
                if (t) result.navItems.push({text: t.slice(0,30), onclick});
            });
            
            return result;
        }
        """)
        print(f"\n菜单分析:")
        print(f"  顶部: {menu_data['topNav']}")
        print(f"  左侧: {menu_data['leftNav'][:20]}")
        print(f"  navItems: {menu_data['navItems'][:20]}")
        print(f"\n主页文本:\n{menu_data['allText'][:1000]}")
        all_results['menu'] = menu_data
        
        # 找出所有可点击的导航元素
        click_elements = await page.evaluate("""
        () => {
            const items = [];
            // 找有onclick的元素
            document.querySelectorAll('[onclick]').forEach(el => {
                const t = el.textContent.trim();
                const onclick = el.getAttribute('onclick');
                if (t && t.length < 30 && onclick) {
                    items.push({text: t, onclick, tag: el.tagName, className: el.className.slice(0,50)});
                }
            });
            // 找href是html的链接
            document.querySelectorAll('a[href*=".html"]').forEach(el => {
                const t = el.textContent.trim();
                const href = el.href;
                if (t && t.length < 30) {
                    items.push({text: t, href, tag: 'A'});
                }
            });
            return items;
        }
        """)
        print(f"\n可点击元素: {json.dumps(click_elements[:30], ensure_ascii=False, indent=2)}")
        all_results['clickable'] = click_elements
        
        # 保存结果
        with open(f"{SCREENSHOT_DIR}/nav_analysis.json", "w", encoding="utf-8") as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)
        
        await browser.close()

asyncio.run(main())
