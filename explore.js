async function run(page) {
  const frames = page.frames();
  const f = frames.find(fr => fr.url().includes('kefu_clients/index'));
  if (!f) { console.log('no frame found'); return; }
  
  // Get table rows
  const rows = await f.$$('.layui-table tbody tr');
  console.log('table rows:', rows.length);
  
  // Click first row to open detail
  if (rows.length > 0) {
    await rows[0].click();
    await page.waitForTimeout(2500);
    
    // Check for popup/modal in the main page
    const mainLayer = await page.$('.layui-layer');
    console.log('main layer:', mainLayer ? 'found' : 'not found');
    
    // Check in iframe
    const frameLayer = await f.$('.layui-layer');
    console.log('frame layer:', frameLayer ? 'found' : 'not found');
    
    if (frameLayer) {
      const text = await frameLayer.innerText();
      console.log('DETAIL:', text.substring(0, 2000));
    }
    
    // Also check all layers
    const allLayers = await f.$$('.layui-layer');
    console.log('all layers in frame:', allLayers.length);
    
    // Try getting all visible elements with content
    const bodyText = await f.evaluate(() => {
      const layer = document.querySelector('.layui-layer');
      return layer ? layer.innerText.substring(0, 3000) : 'no layer';
    });
    console.log('body layer text:', bodyText);
  }
}
module.exports = run;
