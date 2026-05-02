const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const SCREENSHOT_DIR = 'C:/Users/10517/WorkBuddy/20260429105535/screenshots/compare';

// Ensure directory exists
if (!fs.existsSync(SCREENSHOT_DIR)) {
  fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
}

const BASE_URL = 'https://guwen.zhudaicms.com';
const ACCOUNT = '19883890925';
const PASSWORD = '123456';

async function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function login(page, smsCode) {
  await page.goto(`${BASE_URL}/manage/index/index.html`, { waitUntil: 'networkidle', timeout: 30000 });
  await page.waitForTimeout(1000);
  
  await page.fill('#kefu_number', ACCOUNT);
  await page.fill('#smscode', smsCode);
  await page.fill('#kefu_password', PASSWORD);
  await page.click('.login-button');
  
  await page.waitForTimeout(3000);
  
  const currentUrl = page.url();
  console.log('After login URL:', currentUrl);
  return !currentUrl.includes('index.html') && !currentUrl.includes('login');
}

async function getLeftMenuItems(page) {
  return await page.evaluate(() => {
    // Find all sidebar menu items
    const menuItems = [];
    const elements = document.querySelectorAll('.sidebar-menu li, .nav-item, .menu-item, .left-menu li, aside li, .menu a, .sidebar a, [class*="menu"] a, [class*="nav"] a');
    elements.forEach(el => {
      const text = el.innerText.trim();
      const href = el.querySelector('a')?.href || '';
      if (text && text.length < 50) {
        menuItems.push({ text, href });
      }
    });
    return menuItems;
  });
}

async function exploreCRM(smsCode) {
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const page = await context.newPage();
  
  let findings = {};
  
  try {
    // Login
    console.log('Logging in...');
    const success = await login(page, smsCode);
    if (!success) {
      console.log('Login failed! Current URL:', page.url());
      const errMsg = await page.evaluate(() => document.getElementById('errormsg')?.innerText || 'Unknown error');
      console.log('Error:', errMsg);
      await browser.close();
      return { success: false, error: errMsg };
    }
    console.log('Login successful!');
    await page.waitForTimeout(2000);
    
    // Save main dashboard screenshot
    await page.screenshot({ path: `${SCREENSHOT_DIR}/old_main_dashboard.png`, fullPage: false });
    console.log('Dashboard screenshot saved');
    
    // === 1. Top announcement bar ===
    console.log('\n--- 1. Top announcement bar ---');
    await page.waitForTimeout(500);
    const announcementBar = await page.evaluate(() => {
      const bar = document.querySelector('.announcement, .notice, .top-notice, [class*="announce"], [class*="notice"], .toptips, .topbar');
      if (bar) {
        return {
          text: bar.innerText.substring(0, 500),
          html: bar.innerHTML.substring(0, 500)
        };
      }
      return null;
    });
    console.log('Announcement bar:', announcementBar);
    await page.screenshot({ path: `${SCREENSHOT_DIR}/old_announcement_bar.png`, fullPage: false });
    findings['announcement_bar'] = announcementBar;
    
    // === 2. Left menu - full list ===
    console.log('\n--- 2. Left menu ---');
    await page.waitForTimeout(500);
    
    // Try different selectors for left menu
    const leftMenuSelectors = [
      '.sidebar-menu li', '.sidebar li', '.left-menu li', '.nav-menu li',
      '[class*="sidebar"] li', 'aside li', '.menu-sidebar li',
      '.el-menu li', '.ant-menu li'
    ];
    
    let leftMenuItems = [];
    for (const selector of leftMenuSelectors) {
      try {
        const items = await page.$$eval(selector, els => els.map(el => ({
          text: el.innerText.trim(),
          href: el.querySelector('a')?.href || '',
          class: el.className
        }))).catch(() => []);
        if (items.length > leftMenuItems.length) {
          leftMenuItems = items;
        }
      } catch(e) {}
    }
    console.log('Left menu items:', JSON.stringify(leftMenuItems, null, 2));
    
    // Try getting full sidebar HTML
    const sidebarHTML = await page.evaluate(() => {
      const sidebar = document.querySelector('.sidebar, aside, .left-menu, [class*="sidebar"]');
      return sidebar ? sidebar.innerHTML.substring(0, 3000) : 'No sidebar found';
    });
    console.log('Sidebar HTML:', sidebarHTML.substring(0, 1000));
    
    await page.screenshot({ path: `${SCREENSHOT_DIR}/old_left_menu.png`, fullPage: false });
    findings['left_menu'] = leftMenuItems;
    
    // === Navigate to "我的客户" (My Customers) page ===
    console.log('\n--- 3. My Customers page ---');
    const menuLink = await page.evaluate(() => {
      const links = Array.from(document.querySelectorAll('a, [onclick], [data-href]'));
      for (const link of links) {
        const text = link.innerText.trim();
        if (text.includes('我的客户') || text.includes('客户管理') || text.includes('我的客户')) {
          return { text, href: link.href || link.getAttribute('onclick') || link.getAttribute('data-href') };
        }
      }
      return null;
    });
    console.log('My Customers link:', menuLink);
    
    if (menuLink) {
      try {
        await page.click(`text=${menuLink.text}`);
        await page.waitForTimeout(2000);
      } catch(e) {
        try {
          await page.goto(menuLink.href || `${BASE_URL}${menuLink.href}`, { waitUntil: 'networkidle', timeout: 15000 });
          await page.waitForTimeout(2000);
        } catch(e2) {}
      }
    }
    
    await page.screenshot({ path: `${SCREENSHOT_DIR}/old_my_customers.png`, fullPage: false });
    
    // Get toolbar buttons
    const toolbarButtons = await page.evaluate(() => {
      return Array.from(document.querySelectorAll('button, [class*="btn"], [class*="button"], [class*="tool"]')).map(el => ({
        text: el.innerText.trim(),
        class: el.className,
        type: el.type
      })).filter(el => el.text);
    });
    console.log('Toolbar buttons:', JSON.stringify(toolbarButtons, null, 2));
    
    // Get search/filter fields
    const searchFields = await page.evaluate(() => {
      const fields = [];
      document.querySelectorAll('input, select, .filter-item, [class*="search"], [class*="filter"]').forEach(el => {
        const text = el.innerText?.trim() || el.placeholder || el.name || '';
        if (text) fields.push({ tag: el.tagName, text, name: el.name, id: el.id });
      });
      return fields;
    });
    console.log('Search fields:', JSON.stringify(searchFields, null, 2));
    
    findings['my_customers'] = { toolbarButtons, searchFields };
    
    // === 4. Customer detail popup ===
    console.log('\n--- 4. Customer detail popup ---');
    // Try to click on a customer row
    const customerRow = await page.evaluate(() => {
      const rows = document.querySelectorAll('tr, .table-row, [class*="row"], tbody tr, .list-item');
      for (const row of rows) {
        const text = row.innerText.trim();
        if (text && text.length > 10 && !text.includes('暂无') && !text.includes('加载')) {
          return { text: text.substring(0, 200) };
        }
      }
      return null;
    });
    console.log('First customer row:', customerRow);
    
    // Try clicking a row
    try {
      const clickableRow = await page.$('tbody tr, tr.clickable, [class*="customer"]:not([class*="header"])');
      if (clickableRow) {
        await clickableRow.click();
        await page.waitForTimeout(2000);
        await page.screenshot({ path: `${SCREENSHOT_DIR}/old_customer_detail_popup.png`, fullPage: false });
        
        // Get tabs in popup
        const tabs = await page.evaluate(() => {
          return Array.from(document.querySelectorAll('.tab, [class*="tab"], .el-tabs__item, [role="tab"]')).map(el => el.innerText.trim());
        });
        console.log('Customer detail tabs:', tabs);
        
        // Get fields in each tab
        const popupFields = await page.evaluate(() => {
          return Array.from(document.querySelectorAll('input, select, [class*="field"], [class*="item"]')).map(el => ({
            tag: el.tagName,
            text: el.innerText?.trim() || '',
            name: el.name || el.id || '',
            type: el.type || ''
          })).filter(el => el.text || el.name);
        });
        console.log('Popup fields:', JSON.stringify(popupFields.slice(0, 30), null, 2));
        
        findings['customer_detail'] = { tabs, popupFields };
        
        // Close popup
        const closeBtn = await page.$('[class*="close"], .popup-close, [aria-label="关闭"]');
        if (closeBtn) await closeBtn.click();
        await page.waitForTimeout(500);
      }
    } catch(e) {
      console.log('Could not click customer row:', e.message);
    }
    
    // === 5. 团队客户 (Team customers) page ===
    console.log('\n--- 5. Team customers page ---');
    const teamLink = await page.evaluate(() => {
      const links = Array.from(document.querySelectorAll('a'));
      for (const link of links) {
        const text = link.innerText.trim();
        if (text.includes('团队客户') || text.includes('团队')) {
          return { text, href: link.href };
        }
      }
      return null;
    });
    console.log('Team customers link:', teamLink);
    
    if (teamLink?.href) {
      await page.goto(teamLink.href, { waitUntil: 'networkidle', timeout: 15000 });
      await page.waitForTimeout(2000);
      await page.screenshot({ path: `${SCREENSHOT_DIR}/old_team_customers.png`, fullPage: false });
      
      const teamFilters = await page.evaluate(() => {
        return Array.from(document.querySelectorAll('input, select, [class*="filter"], [class*="search"], .el-select')).map(el => ({
          tag: el.tagName,
          name: el.name || el.id || '',
          placeholder: el.placeholder || '',
          text: el.innerText?.trim()?.substring(0, 50) || ''
        }));
      });
      console.log('Team customer filters:', JSON.stringify(teamFilters, null, 2));
      
      const teamToolbar = await page.evaluate(() => {
        return Array.from(document.querySelectorAll('button, [class*="btn"]')).map(el => el.innerText.trim()).filter(Boolean);
      });
      console.log('Team toolbar buttons:', teamToolbar);
      
      findings['team_customers'] = { filters: teamFilters, toolbar: teamToolbar };
    }
    
    // === 6. 再分配 (Reallocation) page ===
    console.log('\n--- 6. Reallocation page ---');
    const redistLink = await page.evaluate(() => {
      const links = Array.from(document.querySelectorAll('a'));
      for (const link of links) {
        const text = link.innerText.trim();
        if (text.includes('再分配') || text.includes('重新分配')) {
          return { text, href: link.href };
        }
      }
      return null;
    });
    console.log('Reallocation link:', redistLink);
    
    if (redistLink?.href) {
      await page.goto(redistLink.href, { waitUntil: 'networkidle', timeout: 15000 });
      await page.waitForTimeout(2000);
      await page.screenshot({ path: `${SCREENSHOT_DIR}/old_redistribution.png`, fullPage: false });
      
      const redistFilters = await page.evaluate(() => {
        return Array.from(document.querySelectorAll('input, select, [class*="filter"], [class*="search"]')).map(el => ({
          tag: el.tagName,
          name: el.name || el.id || '',
          placeholder: el.placeholder || '',
          text: el.innerText?.trim()?.substring(0, 50) || ''
        }));
      });
      console.log('Redistribution filters:', JSON.stringify(redistFilters, null, 2));
      findings['redistribution'] = { filters: redistFilters };
    }
    
    // === 7. 公共池 (Public pool) page ===
    console.log('\n--- 7. Public pool page ---');
    const poolLink = await page.evaluate(() => {
      const links = Array.from(document.querySelectorAll('a'));
      for (const link of links) {
        const text = link.innerText.trim();
        if (text.includes('公共池') || text.includes('公海')) {
          return { text, href: link.href };
        }
      }
      return null;
    });
    console.log('Public pool link:', poolLink);
    
    if (poolLink?.href) {
      await page.goto(poolLink.href, { waitUntil: 'networkidle', timeout: 15000 });
      await page.waitForTimeout(2000);
      await page.screenshot({ path: `${SCREENSHOT_DIR}/old_public_pool.png`, fullPage: false });
      
      const poolFilters = await page.evaluate(() => {
        return Array.from(document.querySelectorAll('input, select, [class*="filter"], [class*="search"]')).map(el => ({
          tag: el.tagName,
          name: el.name || el.id || '',
          placeholder: el.placeholder || '',
          text: el.innerText?.trim()?.substring(0, 50) || ''
        }));
      });
      console.log('Public pool filters:', JSON.stringify(poolFilters, null, 2));
      
      const poolNotice = await page.evaluate(() => {
        const notice = document.querySelector('[class*="notice"], [class*="tip"], [class*="alert"], .toptips, .alert-warning, [class*="limited"]');
        return notice?.innerText || null;
      });
      console.log('Public pool notice:', poolNotice);
      
      findings['public_pool'] = { filters: poolFilters, notice: poolNotice };
    }
    
    // === 8. 黑名单 (Blacklist) page ===
    console.log('\n--- 8. Blacklist page ---');
    const blacklistLink = await page.evaluate(() => {
      const links = Array.from(document.querySelectorAll('a'));
      for (const link of links) {
        const text = link.innerText.trim();
        if (text.includes('黑名单') || text.includes('黑名')) {
          return { text, href: link.href };
        }
      }
      return null;
    });
    console.log('Blacklist link:', blacklistLink);
    
    if (blacklistLink?.href) {
      await page.goto(blacklistLink.href, { waitUntil: 'networkidle', timeout: 15000 });
      await page.waitForTimeout(2000);
      await page.screenshot({ path: `${SCREENSHOT_DIR}/old_blacklist.png`, fullPage: false });
      findings['blacklist'] = { found: true };
    } else {
      console.log('Blacklist page NOT found');
      findings['blacklist'] = { found: false };
    }
    
    // === 9. 日志报表 (Log report) page ===
    console.log('\n--- 9. Log report page ---');
    const logLink = await page.evaluate(() => {
      const links = Array.from(document.querySelectorAll('a'));
      for (const link of links) {
        const text = link.innerText.trim();
        if (text.includes('日志报表') || text.includes('日志') || text.includes('报表')) {
          return { text, href: link.href };
        }
      }
      return null;
    });
    console.log('Log report link:', logLink);
    
    if (logLink?.href) {
      await page.goto(logLink.href, { waitUntil: 'networkidle', timeout: 15000 });
      await page.waitForTimeout(2000);
      await page.screenshot({ path: `${SCREENSHOT_DIR}/old_log_report.png`, fullPage: false });
      
      const logContent = await page.evaluate(() => {
        const blocks = document.querySelectorAll('[class*="block"], [class*="card"], [class*="panel"]');
        return Array.from(blocks).map(b => b.innerText.substring(0, 200)).slice(0, 5);
      });
      console.log('Log report content blocks:', logContent);
      findings['log_report'] = { contentBlocks: logContent };
    }
    
    // === 10. 数据统计 (Data statistics) page ===
    console.log('\n--- 10. Data statistics page ---');
    const statsLink = await page.evaluate(() => {
      const links = Array.from(document.querySelectorAll('a'));
      for (const link of links) {
        const text = link.innerText.trim();
        if (text.includes('数据统计') || text.includes('统计')) {
          return { text, href: link.href };
        }
      }
      return null;
    });
    console.log('Data statistics link:', statsLink);
    
    if (statsLink?.href) {
      await page.goto(statsLink.href, { waitUntil: 'networkidle', timeout: 15000 });
      await page.waitForTimeout(2000);
      await page.screenshot({ path: `${SCREENSHOT_DIR}/old_data_statistics.png`, fullPage: false });
      
      const statsTabs = await page.evaluate(() => {
        return Array.from(document.querySelectorAll('[class*="tab"]')).map(el => el.innerText.trim()).filter(Boolean);
      });
      console.log('Data statistics tabs:', statsTabs);
      findings['data_statistics'] = { tabs: statsTabs };
    }
    
    // === 11. 业绩排行榜 (Performance ranking) page ===
    console.log('\n--- 11. Performance ranking page ---');
    const rankingLink = await page.evaluate(() => {
      const links = Array.from(document.querySelectorAll('a'));
      for (const link of links) {
        const text = link.innerText.trim();
        if (text.includes('业绩排行榜') || text.includes('排行') || text.includes('排名')) {
          return { text, href: link.href };
        }
      }
      return null;
    });
    console.log('Performance ranking link:', rankingLink);
    
    if (rankingLink?.href) {
      await page.goto(rankingLink.href, { waitUntil: 'networkidle', timeout: 15000 });
      await page.waitForTimeout(2000);
      await page.screenshot({ path: `${SCREENSHOT_DIR}/old_performance_ranking.png`, fullPage: false });
      
      const rankingContent = await page.evaluate(() => {
        const table = document.querySelector('table');
        if (table) {
          const headers = Array.from(table.querySelectorAll('th')).map(th => th.innerText.trim());
          const rows = Array.from(table.querySelectorAll('tr')).slice(0, 5).map(tr => 
            Array.from(tr.querySelectorAll('td')).map(td => td.innerText.trim())
          );
          return { headers, rows };
        }
        return document.body.innerText.substring(0, 500);
      });
      console.log('Performance ranking content:', JSON.stringify(rankingContent, null, 2));
      findings['performance_ranking'] = { content: rankingContent };
    }
    
    // === 12. 创收分析 (Revenue analysis) page ===
    console.log('\n--- 12. Revenue analysis page ---');
    const revenueLink = await page.evaluate(() => {
      const links = Array.from(document.querySelectorAll('a'));
      for (const link of links) {
        const text = link.innerText.trim();
        if (text.includes('创收分析') || text.includes('创收') || text.includes('收入分析')) {
          return { text, href: link.href };
        }
      }
      return null;
    });
    console.log('Revenue analysis link:', revenueLink);
    
    if (revenueLink?.href) {
      await page.goto(revenueLink.href, { waitUntil: 'networkidle', timeout: 15000 });
      await page.waitForTimeout(2000);
      await page.screenshot({ path: `${SCREENSHOT_DIR}/old_revenue_analysis.png`, fullPage: false });
      
      const revenueContent = await page.evaluate(() => {
        return document.body.innerText.substring(0, 800);
      });
      console.log('Revenue analysis content:', revenueContent);
      findings['revenue_analysis'] = { content: revenueContent };
    }
    
    // === 13. 绩效目标 (Performance goals) page ===
    console.log('\n--- 13. Performance goals page ---');
    const goalLink = await page.evaluate(() => {
      const links = Array.from(document.querySelectorAll('a'));
      for (const link of links) {
        const text = link.innerText.trim();
        if (text.includes('绩效目标') || text.includes('目标')) {
          return { text, href: link.href };
        }
      }
      return null;
    });
    console.log('Performance goals link:', goalLink);
    
    if (goalLink?.href) {
      await page.goto(goalLink.href, { waitUntil: 'networkidle', timeout: 15000 });
      await page.waitForTimeout(2000);
      await page.screenshot({ path: `${SCREENSHOT_DIR}/old_performance_goals.png`, fullPage: false });
      
      const goalsContent = await page.evaluate(() => {
        return document.body.innerText.substring(0, 800);
      });
      console.log('Performance goals content:', goalsContent);
      findings['performance_goals'] = { content: goalsContent };
    }
    
    // === 14. 系统设置 (System settings) page ===
    console.log('\n--- 14. System settings page ---');
    const settingsLink = await page.evaluate(() => {
      const links = Array.from(document.querySelectorAll('a'));
      for (const link of links) {
        const text = link.innerText.trim();
        if (text.includes('系统设置') || text.includes('设置')) {
          return { text, href: link.href };
        }
      }
      return null;
    });
    console.log('System settings link:', settingsLink);
    
    if (settingsLink?.href) {
      await page.goto(settingsLink.href, { waitUntil: 'networkidle', timeout: 15000 });
      await page.waitForTimeout(2000);
      await page.screenshot({ path: `${SCREENSHOT_DIR}/old_system_settings.png`, fullPage: false });
      
      const settingsItems = await page.evaluate(() => {
        return Array.from(document.querySelectorAll('[class*="item"], [class*="setting"], [class*="option"], .menu-item')).map(el => el.innerText.trim()).filter(Boolean);
      });
      console.log('System settings items:', JSON.stringify(settingsItems, null, 2));
      findings['system_settings'] = { items: settingsItems };
    }
    
    // === Save all findings ===
    fs.writeFileSync(`${SCREENSHOT_DIR}/old_crm_findings.json`, JSON.stringify(findings, null, 2));
    console.log('\n\nAll findings saved to old_crm_findings.json');
    
  } catch (e) {
    console.error('Error during exploration:', e.message);
    findings['error'] = e.message;
  } finally {
    await browser.close();
  }
  
  return { success: true, findings };
}

// Run with SMS code from command line
const smsCode = process.argv[2];
if (!smsCode) {
  console.log('Usage: node crm_explore_full.js <sms_code>');
  process.exit(1);
}

exploreCRM(smsCode).then(result => {
  console.log('\n\n=== FINAL RESULTS ===');
  console.log(JSON.stringify(result, null, 2));
}).catch(console.error);
