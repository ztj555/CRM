const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const SCREENSHOT_DIR = 'C:/Users/10517/WorkBuddy/20260429105535/screenshots/compare';

// Ensure directory exists
if (!fs.existsSync(SCREENSHOT_DIR)) {
  fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
}

async function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function main() {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 }
  });
  const page = await context.newPage();

  let allFindings = [];

  function saveScreenshot(name) {
    const filepath = path.join(SCREENSHOT_DIR, name);
    page.screenshot({ path: filepath, fullPage: false });
    console.log(`Screenshot saved: ${filepath}`);
    return filepath;
  }

  async function snapshot(label) {
    try {
      await page.waitForTimeout(500);
      const content = await page.content();
      return content.substring(0, 3000);
    } catch(e) {
      return `Error: ${e.message}`;
    }
  }

  try {
    // Step 1: Open login page
    console.log('Opening login page...');
    await page.goto('https://guwen.zhudaicms.com/manage/index/index.html', { waitUntil: 'networkidle', timeout: 30000 });
    await page.waitForTimeout(2000);
    saveScreenshot('old_login_page.png');

    // Get login form fields
    const loginSnapshot = await page.evaluate(() => {
      const inputs = document.querySelectorAll('input');
      const forms = document.querySelectorAll('form');
      return {
        inputs: Array.from(inputs).map(i => ({ type: i.type, name: i.name, id: i.id, placeholder: i.placeholder })),
        forms: forms.length,
        pageText: document.body.innerText.substring(0, 500)
      };
    });
    console.log('Login page snapshot:', JSON.stringify(loginSnapshot, null, 2));

    // Save captcha image
    try {
      const captchaImg = await page.$('img[src*="yzm"], img[src*="captcha"], img[src*="code"], input[name="captcha"] ~ img, input[name="yzm"] ~ img, #yzm, #captcha, .captcha img, .code img');
      if (captchaImg) {
        const src = await captchaImg.getAttribute('src');
        console.log('Captcha image src:', src);
      }
    } catch(e) {
      console.log('Could not find captcha img:', e.message);
    }

    // Find all inputs
    const allInputs = await page.evaluate(() => {
      return Array.from(document.querySelectorAll('*')).filter(el => {
        return el.tagName === 'INPUT' || el.tagName === 'BUTTON';
      }).map(el => ({
        tag: el.tagName,
        type: el.type,
        name: el.name,
        id: el.id,
        class: el.className,
        placeholder: el.placeholder,
        text: el.innerText
      }));
    });
    console.log('All inputs/buttons:', JSON.stringify(allInputs, null, 2));

    console.log('\n=== Please provide the captcha code ===');
    console.log('Captcha URL: https://www2.zhudaicms.com/important/get_guding_yzm.html');
    console.log('Please provide the captcha code to continue...');

  } catch (e) {
    console.error('Error:', e.message);
  } finally {
    // await browser.close();
  }
}

main();
