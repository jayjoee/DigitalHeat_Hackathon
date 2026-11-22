// Record the two real runs behind the film, with timestamps.
//   node tools/capture-runs.js <runs-dir> [live|handoff]
// live:    every status change that src/scheduler/live.py writes while it controls a real Vina process
// handoff: screen recording (retina) of both screens of prototyp/docking_demo.py
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const { spawn, execFileSync } = require('child_process');
const fs = require('fs'), path = require('path');
const REPO = process.env.DIGITALHEAT_REPO || path.resolve(__dirname, '..', '..', '..');
const OUT = path.resolve(process.argv[2]), only = process.argv[3];
const sleep = ms => new Promise(r => setTimeout(r, ms));
const SEC_PER_HOUR = 1.70;

async function live() {
  const dir = path.join(OUT, 'live');
  fs.rmSync(dir, { recursive: true, force: true }); fs.mkdirSync(dir, { recursive: true });
  const since = Date.now() / 1000, states = [];
  let log = '', done = false, last = '';
  const child = spawn('python3', ['-B', 'src/scheduler/live.py', '--tag', '2025-03-07', '--server', '8', '--sekunden', String(SEC_PER_HOUR), '--job', 'docking', '--arbeitsordner', path.join(dir, 'work')], { cwd: REPO });
  child.stdout.on('data', d => log += d); child.stderr.on('data', d => log += d);
  child.on('exit', () => done = true);
  try {
    while (!done) {
      try {
        const raw = fs.readFileSync(path.join(REPO, 'dashboard/live.json'), 'utf8');
        const L = JSON.parse(raw);
        if (L.aktualisiert > since && raw !== last) { last = raw; const { stunden, ...state } = L; states.push({ t: L.aktualisiert, L: state }); }
      } catch { /* not written yet */ }
      await sleep(10);
    }
  } finally {
    if (child.exitCode === null) child.kill('SIGINT');
    // live.py overwrites a tracked result file; keep the committed version.
    execFileSync('git', ['-C', REPO, 'checkout', '--', 'daten/ergebnisse/live_docking_2025-03-07.json']);
  }
  fs.writeFileSync(path.join(dir, 'states.json'), JSON.stringify(states, null, 1));
  fs.writeFileSync(path.join(dir, 'run.log'), log);
  console.log(log);
  const t0 = states[0].t;
  let prev = '';
  for (const { t, L } of states) {
    const s = `${L.prozess}`;
    if (s !== prev || /T(14|21|22)/.test(L.jetzt?.zeit || '')) console.log((t - t0).toFixed(2), L.jetzt?.zeit, L.prozess, L.jetzt?.speicher_kwh, L.jetzt?.bedarf_kwh, L.texte_fertig);
    prev = s;
  }
}

async function handoff() {
  const dir = path.join(OUT, 'handoff');
  fs.rmSync(dir, { recursive: true, force: true }); fs.mkdirSync(dir, { recursive: true });
  const demo = spawn('python3', ['-B', '-u', 'prototyp/docking_demo.py', 'demo'], { cwd: REPO });
  let browser;
  try {
    await new Promise((resolve, reject) => {
      let out = '';
      demo.stdout.on('data', d => { out += d; if (out.includes(':8083') && out.includes(':8093')) resolve(); });
      demo.on('exit', () => reject(new Error('demo stopped: ' + out)));
      setTimeout(() => reject(new Error('demo timeout: ' + out)), 20000);
    });
    browser = await chromium.launch({ channel: 'chromium' });
    const screens = [];
    for (const [name, port] of [['house', 8083], ['pool', 8093]]) {
      const ctx = await browser.newContext({ viewport: { width: 900, height: 820 }, deviceScaleFactor: 2, bypassCSP: true });
      const page = await ctx.newPage();
      await page.goto(`http://127.0.0.1:${port}/`);
      await page.addStyleTag({ content: `main{max-width:none;padding:16px 20px} main>header,main>h1,.intro,#recent{display:none}
        .heat dl{grid-template-columns:repeat(2,1fr)} .heat dl>div:nth-child(n+3){display:none}
        .layout{grid-template-columns:1.05fr 1fr} .rangliste li{font-size:18px}` });
      fs.mkdirSync(path.join(dir, name));
      screens.push({ name, page, frames: [] });
    }
    await sleep(1500);
    const t0 = Date.now();
    let click = null;
    const until = () => Date.now() - t0 < 36000;
    await Promise.all([
      ...screens.map(async s => {
        while (until()) {
          const t = (Date.now() - t0) / 1000;
          const file = `${String(s.frames.length).padStart(4, '0')}.jpg`;
          await s.page.screenshot({ path: path.join(dir, s.name, file), type: 'jpeg', quality: 88, scale: 'device' });
          const info = await s.page.evaluate(() => [count.textContent, state.textContent, handoff.textContent].map(String));
          s.frames.push({ t, file, info });
          await sleep(60);
        }
      }),
      (async () => { await sleep(400); await screens[0].page.click('#start'); click = (Date.now() - t0) / 1000; })(),
    ]);
    fs.writeFileSync(path.join(dir, 'frames.json'), JSON.stringify({ click, screens: Object.fromEntries(screens.map(s => [s.name, s.frames])) }));
    console.log('click', click);
    for (const s of screens) {
      let prev = '';
      for (const f of s.frames) { const k = f.info.join(' | '); if (k !== prev) console.log(s.name, f.t.toFixed(2), k); prev = k; }
      console.log(s.name, (s.frames.length / 36).toFixed(1), 'fps');
    }
  } finally {
    if (browser) await browser.close();
    demo.kill('SIGINT');
  }
}

(async () => {
  if (!only || only === 'live') await live();
  if (!only || only === 'handoff') await handoff();
})().catch(e => { console.error(e); process.exit(1) });
