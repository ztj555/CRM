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

  const pages = [
    // 左侧菜单
    ['我的客户', 'https://guwen.zhudaicms.com/manage/kefu_clients/index.html'],
    ['再分配客户', 'https://guwen.zhudaicms.com/manage/kefu_againclientslist/index.html'],
    ['公共池客户', 'https://guwen.zhudaicms.com/manage/kefu_clientsggc/index.html'],
    ['必跟进客户', 'https://guwen.zhudaicms.com/manage/kefu_bigenjin/index.html'],
    ['在审件管理', 'https://guwen.zhudaicms.com/manage/kefu_trialclients/index.html'],
    ['业绩排行榜', 'https://guwen.zhudaicms.com/manage/kefu_rankinglist/index.html?brand=1833'],
    // Tab2 工作
    ['日志报表', 'https://guwen.zhudaicms.com/manage/kefu_reportformlist/index.html'],
    ['工作简报', 'https://guwen.zhudaicms.com/manage/kefu_dailysimple/index.html'],
    ['数据统计', 'https://guwen.zhudaicms.com/manage/kefu_statistics/stars_zhanbi.html'],
    ['创收分析', 'https://guwen.zhudaicms.com/manage/kefu_trialclients/gobank_zhanbi.html'],
    ['绩效目标', 'https://guwen.zhudaicms.com/manage/kefu_clients/performance_target.html'],
    // Tab3 团队
    ['团队客户', 'https://guwen.zhudaicms.com/manage/kefu_tuanduiclients/index.html'],
    ['团队管理', 'https://guwen.zhudaicms.com/manage/kefu_underling/index.html'],
    ['离职数据分配', 'https://guwen.zhudaicms.com/manage/kefu_dimissionlist/index.html'],
    ['通话管理', 'https://guwen.zhudaicms.com/manage/call_manager/teamlists.html'],
    // 工具栏
    ['公告', 'https://guwen.zhudaicms.com/manage/kefu_dailysimple/notice.html'],
    ['档案信息', 'https://guwen.zhudaicms.com/manage/kefu_account/info.html'],
    ['修改密码', 'https://guwen.zhudaicms.com/manage/kefu_account/editpassword.html'],
    ['发布公告', 'https://guwen.zhudaicms.com/manage/gonggao/publishgonggao.html'],
    ['发布滚动条', 'https://guwen.zhudaicms.com/manage/gonggao/addxiaoxi.html'],
    ['系统设置', 'https://guwen.zhudaicms.com/manage/kefu_account/setting.html'],
    // 客户详情页（随机找一个客户ID）
    ['客户详情-1', 'https://guwen.zhudaicms.com/manage/kefu_clients/edit_client_info.html?id=1'],
    ['客户详情-5', 'https://guwen.zhudaicms.com/manage/kefu_clients/edit_client_info.html?id=5'],
  ];

  const outFile = 'c:/Users/10517/WorkBuddy/20260429105535/screenshots/admin_all_pages_text.txt';
  FS.writeFileSync(outFile, '');

  for (const [name, url] of pages) {
    try {
      await p.goto(url, {timeout:15000, waitUntil:'domcontentloaded'});
      await p.waitForTimeout(2000);
      await p.screenshot({path: 'screenshots/admin_' + name + '.png', fullPage: false});
      const text = await p.evaluate(() => document.body ? document.body.innerText.substring(0, 3000) : 'N/A');
      const html = await p.evaluate(() => document.body ? document.body.innerHTML.substring(0, 5000) : '');
      console.log('[' + name + '] ' + url);
      console.log('  文字: ' + text.replace(/\n+/g, ' | ').substring(0, 200));
      FS.appendFileSync(outFile, '=== ' + name + ' | ' + url + ' ===\n' + text + '\n\n');
    } catch(e) {
      console.log('[' + name + '] 失败: ' + e.message.substring(0, 100));
    }
  }

  await b.close();
  console.log('\n全部页面探索完成，已保存到 admin_all_pages_text.txt');
})().catch(e => console.error('错误:', e.message));