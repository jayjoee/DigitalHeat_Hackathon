// Render each slide in slides/slides.html to a 1920x1080 PNG.
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const path = require('path'), dir = path.resolve(__dirname, '..', 'slides');
(async () => {
  const b = await chromium.launch({ channel: 'chromium' });
  const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  await p.goto('file://' + path.join(dir, 'slides.html'));
  for (const id of await p.$$eval('section', s => s.map(x => x.id))) {
    const over = await p.evaluate(i => { const s = document.getElementById(i), n = s.querySelector('.note'); return s.scrollHeight > 1080 || (n && n.getBoundingClientRect().bottom - s.getBoundingClientRect().top > 1060) }, id);
    await p.locator(`[id="${id}"]`).screenshot({ path: path.join(dir, id + '.png') });
    console.log(id, over ? 'OVERFLOW' : 'fits');
  }
  await b.close();
})();
