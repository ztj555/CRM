const {chromium} = require('playwright');
const FS = require('fs');
const CHROME = 'C:/Users/10517/AppData/Local/ms-playwright/chromium-1217/chrome-win64/chrome.exe';

(async () => {
  const b = await chromium.launch({executablePath: CHROME, args:['--no-sandbox','--disable-dev-shm-usage','--disable-gpu']});
  const ctx = await b.newContext({viewport:{width:1440,height:900}});
  const p = await ctx.newPage();

  // 登录
  await p.goto('https://guwen.zhudaicms.com/manage/index/login', {timeout:20000});
  await p.fill('#kefu_number', '18335162275');
  await p.fill('#kefu_password', '123456');
  await p.fill('#smscode', '8295');
  await p.evaluate(() => chklogin_kefu());
  await p.waitForURL('**/index.html', {timeout:10000}).catch(()=>{});
  await p.waitForTimeout(2000);
  console.log('已登录:', p.url());

  // 查看主页iframe结构
  const frames = p.frames();
  console.log('Frames数量:', frames.length);
  for (const f of frames) {
    console.log('Frame:', f.url().substring(0, 120));
  }

  // 获取所有链接
  const links = await p.evaluate(() => {
    return Array.from(document.querySelectorAll('a[href]')).map(a => ({
      href: a.href,
      text: a.innerText.trim().substring(0, 50)
    })).filter(l => l.href.includes('manage')).slice(0, 50);
  });
  console.log('所有manage链接:');
  for (const l of links) {
    console.log('  ' + l.text + ' -> ' + l.href);
  }

  await b.close();
})().catch(e => console.error('错误:', e.message));
