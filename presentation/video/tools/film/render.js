// Render the film frame by frame from the real 3D dashboard and the recorded runs.
//   node tools/film/render.js stills <dir> <second> [second ...]
//   node tools/film/render.js frames <dir> <first-frame> <after-last-frame>
// Nothing is served: the browser gets every file through request routing.
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const DASH = path.join(process.env.DIGITALHEAT_REPO || path.resolve(ROOT, '..', '..'), 'dashboard');
const FPS = 30, SPEED_TO_ORIGINAL = 305.5997708333333 / 297;   // the v2 timings are on the 297 s track; v4 is real seconds
const BASE = 'http://film.localhost';
const [mode, outArg, ...rest] = process.argv.slice(2), OUT = path.resolve(outArg);
const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json', '.jpg': 'image/jpeg', '.css': 'text/css', '.png': 'image/png' };
const read = f => fs.readFileSync(path.join(ROOT, f), 'utf8');

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const browser = await chromium.launch({ channel: 'chromium', args: ['--force-color-profile=srgb'] });
  try {
    const ctx = await browser.newContext({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
    await ctx.addInitScript(() => {
      // virtual clock: the film decides what time it is
      window.__vt = 0;
      const epoch = 1763800000000;
      performance.now = () => window.__vt;
      Date.now = () => epoch + window.__vt;
      window.requestAnimationFrame = () => 0;
      window.setInterval = () => 0;
      let seed = 7; Math.random = () => ((seed = seed * 16807 % 2147483647) / 2147483647);
    });
    const page = await ctx.newPage(), errors = [];
    page.on('pageerror', e => errors.push(String(e)));
    page.on('console', m => { if (m.type() === 'error' && !m.text().includes('404')) errors.push(m.text()); });
    await ctx.route('**/*', route => {
      const u = new URL(route.request().url());
      if (u.origin !== BASE) return route.abort();
      const film = u.pathname.startsWith('/__film/'), base = film ? ROOT : DASH;
      let file = path.resolve(base, '.' + decodeURIComponent(film ? u.pathname.slice(7) : u.pathname));
      if (!file.startsWith(base)) return route.abort();
      if (u.pathname.endsWith('/')) file = path.join(file, 'index.html');
      if (!fs.existsSync(file)) return route.fulfill({ status: 404, body: '' });
      if (u.pathname !== '/3d/') return route.fulfill({ body: fs.readFileSync(file), contentType: MIME[path.extname(file)] || 'application/octet-stream' });
      // hooks are added to the served page only, not to the repository
      const hook = `animiere();
window.__v = { THREE, S, CL, HAUS, KNOTEN, STRAHLEN, camera, scene, controls, composer, labels, el, label, flug, setCloud, panelAuf, pruefeLive,
  tick: animiere, time: h => { if (!liveStand) zeitH = h; } };
window.__ready = true;
</script>`;
      return route.fulfill({ contentType: 'text/html', body: fs.readFileSync(file, 'utf8').replace('animiere();\n</script>', hook)
        // in close-ups the LED flicker of the dashboard reads as a strobe: slower and softer for the film
        .replace('0.78 + 0.22 * Math.sin(now / (90 + u * 17) + k)', '0.94 + 0.06 * Math.sin(now / (420 + u * 60) + k)') });
    });
    await page.goto(BASE + '/3d/');
    await page.waitForFunction(() => window.__ready, null, { polling: 100 });
    await page.addStyleTag({ content: read('tools/film/film.css') });
    const base = JSON.parse(read('voice-elevenlabs/word-timings.json')).map(w => ({ text: w.text, start: w.start * SPEED_TO_ORIGINAL }));
    const words = JSON.parse(read('voice-elevenlabs/word-timings-v4.json'));
    const live = JSON.parse(read('runs/live/states.json')), t0 = live[0].t;
    await page.evaluate(data => { window.FILM = data }, {
      words, base, live: live.map(s => ({ t: s.t - t0, L: s.L })), handoff: JSON.parse(read('runs/handoff/frames.json')),
      panels: read('tools/film/panels.html'), slides: read('slides/slides.html'),
    });
    await page.addScriptTag({ content: read('tools/film/film.js') });
    if (errors.length) throw new Error(errors.join('\n'));

    const cdp = await ctx.newCDPSession(page);
    const frame = async t => {
      await page.evaluate(x => window.__frame(x), t);
      if (errors.length) throw new Error(`at ${t}: ${errors.join('\n')}`);
    };
    const shot = async (file, quality) => fs.writeFileSync(file,
      Buffer.from((await cdp.send('Page.captureScreenshot', { format: 'jpeg', quality, optimizeForSpeed: true })).data, 'base64'));
    const began = Date.now();
    if (mode === 'stills') {
      fs.writeFileSync(path.join(OUT, 'cues.json'), JSON.stringify(await page.evaluate(() => window.__cues), null, 1));
      for (const s of rest.map(Number)) {
        for (let n = 20; n >= 0; n--) await frame(s - n / FPS);   // pre-roll for particles
        await shot(path.join(OUT, `t${s.toFixed(1).padStart(5, '0')}.jpg`), 88);
      }
    } else {
      const [first, last] = rest.map(Number);
      for (let n = Math.max(0, first - 90); n < first; n++) await frame(n / FPS);
      for (let n = first; n < last; n++) {
        await frame(n / FPS);
        await shot(path.join(OUT, `${String(n).padStart(5, '0')}.jpg`), 94);
        if ((n - first) % 300 === 0) console.log(`frame ${n} of ${first}-${last}, ${((Date.now() - began) / 1000 / (n - first + 1)).toFixed(3)} s per frame`);
      }
    }
    console.log(`done in ${((Date.now() - began) / 1000).toFixed(0)} s`);
  } finally {
    await browser.close();
  }
})().catch(e => { console.error(e); process.exit(1) });
