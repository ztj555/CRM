"""
调试登录页面
"""
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()
        
        await page.goto("https://guwen.zhudaicms.com/manage/index/login")
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(2)
        
        await page.screenshot(path="C:/Users/10517/WorkBuddy/20260429105535/screenshots/crm_explore/debug_login.png")
        
        # 获取所有输入框和按钮
        elements = await page.evaluate("""
        () => {
            const result = {inputs: [], buttons: [], forms: []};
            document.querySelectorAll('input').forEach(el => {
                result.inputs.push({
                    type: el.type, name: el.name, placeholder: el.placeholder,
                    id: el.id, className: el.className.slice(0,50)
                });
            });
            document.querySelectorAll('button, [class*="btn"], [class*="login"]').forEach(el => {
                result.buttons.push({
                    tag: el.tagName, text: el.textContent.trim().slice(0,30),
                    id: el.id, className: el.className.slice(0,80),
                    type: el.getAttribute('type')
                });
            });
            return result;
        }
        """)
        print("页面元素:", elements)
        
        # 获取完整HTML
        html = await page.content()
        # 找到关键部分
        import re
        form_match = re.search(r'<form[^>]*>.*?</form>', html, re.DOTALL)
        if form_match:
            print("\n表单HTML:", form_match.group()[:2000])
        else:
            # 找login相关
            for keyword in ['login', 'submit', 'btn', 'verify']:
                matches = re.findall(f'<[^>]*{keyword}[^>]*>[^<]*<[^>]*>', html, re.IGNORECASE)
                if matches:
                    print(f"\n{keyword}相关:", matches[:5])
        
        await browser.close()

asyncio.run(main())
