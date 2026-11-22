// The whole film as a function of time: frame(t) poses camera, scene, panels and slides for voice second t.
// Cues come from the word timings of the narration.
(() => {
const A = window.FILM, V = window.__v;
const { THREE, S, HAUS, camera, KNOTEN, el } = V;
const FW = 1920, FH = 1080;
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const mix = (a, b, p) => a + (b - a) * p;
const ease = x => { x = clamp(x); return x * x * x * (x * (6 * x - 15) + 10); };
const ramp = (t, a, b) => ease((t - a) / (b - a));
const span = (t, a, b, i = .5, o = .5) => Math.min(ramp(t, a - i * .35, a + i * .65), 1 - ramp(t, b - o * .5, b + o * .5));
const $ = (s, root = document) => root.querySelector(s);
const $$ = (s, root = document) => [...root.querySelectorAll(s)];

// ---------- cues from the spoken words
// The timeline below is written in seconds of the v2 narration. The current narration is laid onto it at sentence starts
// that both share; recorded runs use the real seconds, so that they keep their true speed.
const norm = s => s.toLowerCase().replace(/[^a-z0-9]/g, '');
const END = A.words[A.words.length - 1].end, END0 = 305.6;
const PAIRS = (() => {
  const sentences = ws => ws.reduce((out, w, i) => {
    if (i === 0 || (/[.?!]$/.test(ws[i - 1].text) && ws[i - 1].text !== 'p.m.')) out.push({ t: w.start, s: '' });
    out[out.length - 1].s += w.text + ' '; return out;
  }, []);
  const a = sentences(A.base), b = sentences(A.words), out = [[0, 0]];
  const same = ['Over a year', 'On energy alone', 'That assumes', 'When the tank is full', 'Then, as the evening', 'To plan ahead', 'Equipping one', 'If every hour', 'Our next step', 'Then it adds', 'The router sends', 'With only'];
  for (const n of b) {
    const key = same.find(k => n.s.startsWith(k)), o = a.find(x => key ? x.s.startsWith(key) : x.s === n.s);
    if (o && o.t > out[out.length - 1][1] && n.t > out[out.length - 1][0]) out.push([n.t, o.t]);
  }
  out.push([END, END0]); return out;
})();
function linear(T) {
  if (T <= 0) return T;
  if (T >= END) return END0 + T - END;
  let i = 0; while (PAIRS[i + 1][0] <= T) i++;
  const [a, b] = PAIRS[i], [c, d] = PAIRS[i + 1];
  return b + (T - a) * (d - b) / (c - a);
}
function toOld(T) { let s = 0; for (let k = -6; k <= 6; k++) s += linear(T + k * .1); return s / 13; }
function toNew(t) { let a = -2, b = END + 4; for (let k = 0; k < 24; k++) { const m = (a + b) / 2; if (toOld(m) < t) a = m; else b = m; } return (a + b) / 2; }
const WORDS = A.words.map(w => ({ ...w, start: toOld(w.start), n: norm(w.text) })).filter(w => w.n);
function cue(phrase, after = 0) {
  const p = phrase.split(/\s+/).map(norm).filter(Boolean);
  for (let i = 0; i <= WORDS.length - p.length; i++)
    if (WORDS[i].start >= after - .05 && p.every((x, k) => WORDS[i + k].n === x)) return WORDS[i].start;
  throw new Error('cue not found: ' + phrase);
}
const C = {};
for (const [key, phrase, after = 0] of [
  ['digital', "DigitalHeat"], ['older', 'older'], ['oil', 'still heat with'], ['replace', 'replace that boiler'], ['stove', 'wood stove as backup'], ['litres', 'that saves'],
  ['k93', 'ninety-three percent'], ['k5', 'five kilowatt-hours', 22], ['k52', 'fifty-two percent'], ['k0', 'finish every urgent'], ['k23', 'twenty-three Swiss'],
  ['flex', 'unlimited docking work'], ['idle', 'idle power', 38], ['k905', 'ninety point five'],
  ['how', 'So how does it work'], ['queue', 'shared job queue'], ['main', 'Our main job'],
  ['dock', 'molecular docking for pharma'], ['canp', 'can pause and, in'], ['nodl', 'has no deadline'], ['micro', 'Urgent microscopy'], ['nopause', "can't pause and"], ['due', 'due within two'], ['hour', 'Every hour'], ['must', 'must start now'], ['flexj', 'Then it adds'],
  ['cap', 'heat demand and the free'], ['waits', 'Everything else waits'], ['router', 'heat router decides'], ['first', 'homes come first'], ['take', 'the pool takes'],
  ['jan', "Let's go into"], ['cold', 'below minus five'], ['eight', 'all eight servers'], ['eighty', 'eighty percent'], ['seventy', 'seventy percent'], ['rest', 'wood stove', 90],
  ['march', "Now it's the seventh"], ['real', 'this job is real'], ['laptop', "It's molecular"], ['ticker', 'live ticker'], ['sched', 'same scheduler code'],
  ['watch', 'watch the tank'], ['two', 'At two'], ['limit', 'reaches its limit'], ['freeze', 'immediately freezes'], ['keeps', 'keeps all its progress'], ['carries', 'carries on'],
  ['move', 'work can also move'], ['may', "Here's a day"], ['starts', 'starts in the house'], ['saves', 'saves a checkpoint'], ['picks', 'It picks up'], ['nine', 'molecule nine'],
  ['summer', 'That flexibility'], ['july', 'On the fifteenth of July'], ['twelve', 'twelve kilowatt-hours'],
  ['one', 'One server is enough'], ['send', 'router sends docking'], ['fifty', 'fifty modelled'], ['needs', 'needs enough jobs'], ['loses', 'loses money'],
  ['plan', 'To plan ahead'], ['sixh', 'six hours ahead'], ['boost', 'gradient boosting'], ['weather', 'weather forecasts'], ['time', 'time', 194], ['season', 'season', 194], ['past', 'past demand'],
  ['unseen', 'never seen'], ['ten', 'ten percent lower'], ['experiment', 'planning experiment'], ['almost', 'saved almost'], ['steer', "doesn't steer"], ['lever', 'big lever'],
  ['customers', 'For customers'], ['noon', 'at noon'], ['wx', 'weather forecast', 216], ['copy', 'run a copy'], ['margin', 'safety margin'], ['n91', 'ninety-one percent'],
  ['pay', 'does it pay off'], ['n290', 'two hundred and ninety'], ['free', 'gets the heat for free'], ['target', 'If every hour'], ['n35', 'thirty-five thousand'], ['anchor', 'anchor customer'], ['payback', 'With interest included'], ['years', 'three point three'], ['five', 'After five years'], ['only', 'With only'],
  ['n66', 'sixty-six percent'], ['bottle', "Heat isn't"], ['demand', 'paying demand'], ['confirmed', 'no customer has confirmed'],
  ['open', "That's why"], ['rdock', 'The docking process'], ['rpause', 'the pause', 260], ['rcheck', 'the checkpoint transfer'], ['replay', 'The scores and routing'], ['simh', 'Homes', 266], ['simr', 'revenue'],
  ['pilot', 'Our next step'], ['phome', 'one home', 275], ['pserv', 'two servers'], ['pwinter', 'one winter'], ['pchf', 'eighty-one thousand'],
  ['msales', 'sales', 281], ['mprice', 'prices', 281], ['mhw', 'hardware costs'], ['midle', 'idle power', 281], ['mrel', 'reliability'], ['thresh', 'threshold'],
  ['hold', 'If they all hold'], ['ifnot', 'If not'], ['world', 'The world will'], ['endcard', 'DigitalHeat', 300],
]) C[key] = cue(phrase, after);

// ---------- DOM
document.body.insertAdjacentHTML('beforeend', A.panels);
const film = $('#film');

// Slides keep the team's format; a shadow root keeps their CSS apart from the dashboard's.
const src = new DOMParser().parseFromString(A.slides, 'text/html');
const css = src.querySelector('style').textContent.replace(':root', ':host').replace(/\bbody\s*{/g, '.deck{') + `
  .deck { position: absolute; inset: 0; }
  .board { position: absolute; left: 0; top: 0; width: 1920px; height: 1080px; transform-origin: 0 0; overflow: hidden; }
  .board > section { position: absolute; left: 0; top: 0; transform-origin: 0 0; }
  .kpi { transform-origin: center; }
  .mark { padding: 1px 2px; margin: 0 -2px; }
  .end { background: #051c2c; }
`;
function host(id) {
  const root = $(id).attachShadow({ mode: 'open' });
  root.innerHTML = `<style>${css}</style><div class="deck"></div>`;
  return root;
}
const deckRoot = host('#f-deck'), endRoot = host('#f-end');
const BOARDS = ['01-key-figures', '08-economics', '09-evidence', '10-pilot'].map(id => {
  const b = document.createElement('div'); b.className = 'board';
  b.append(document.importNode(src.getElementById(id), true));
  $('.deck', deckRoot).append(b);
  return { b, sec: b.firstElementChild };
});
$('.deck', endRoot).append(document.importNode(src.getElementById('11-end'), true));
function markText(root, text) {
  const w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
  for (let n; (n = w.nextNode());) {
    const k = n.textContent.indexOf(text);
    if (k < 0) continue;
    const r = document.createRange(); r.setStart(n, k); r.setEnd(n, k + text.length);
    const s = document.createElement('span'); s.className = 'mark'; r.surroundContents(s);
    return s;
  }
  throw new Error('slide text not found: ' + text);
}
const [SK, SE, SV, SP] = BOARDS.map(b => b.sec);

// marker wipes: [element, start, end]
const MARKS = [
  [markText(SK, 'Eight servers cover 93%'), C.k93 - 1.6, 22.4],
  [markText($('.foot', SK), 'with unlimited docking work'), C.flex, 38],
  [markText($('.foot', SK), '0 W when paused'), cue('zero power'), 38],
  [markText($('.foot', SK), '230 W idle'), C.idle, 45],
  [markText($('.foot', SK), '90.5% coverage'), C.k905, 45],
  [markText(SE, 'the household gets the heat for free'), C.free, C.target],
  [markText($('.band', SE), 'below 66% of hours sold, the model does not pay off'), C.n66, 258],
  [markText($('.band', SE), 'demand is the bottleneck'), C.demand, 258],
  [markText($('.foot', SE), 'No customer has confirmed prices or volumes'), C.confirmed, 258],
  [markText(SV, 'computing process and its control are real'), C.open, 275],
  [markText(SE, 'pays for itself in 3.3 years'), C.payback, C.five],
  [markText($('.scope', SP), 'one former oil-heated home'), C.phome, 298],
  [markText($('.scope', SP), '2 liquid-cooled servers'), C.pserv, 298],
  [markText($('.scope', SP), 'October to March'), C.pwinter, 298],
  [markText($('.scope', SP), '81,500 Swiss francs (CHF)'), C.pchf, 298],
  [markText(SP, 'scales to 20 homes'), cue('we scale to'), 298],
  [markText($('.band', SP), 'scale only if all thresholds hold'), C.hold, 298],
  [markText($('.band', SP), 'otherwise stop or adapt, and move or resell the servers'), C.ifnot, 298],
];

// highlighted blocks: [element, windows, kind]
const k6 = $$('.six .kpi', SK), k4 = $$('.four .kpi', SE), timeline = $$('table.timeline tr', SE);
const cols = $$('.col', SV), rows = $$('table.pilot tr', SP).slice(1);
const BLOCKS = [
  [k6[0], [[cue('eight servers', 18), C.k93]], 'kpi', k6], [k6[1], [[C.k93, C.k5]], 'kpi', k6], [k6[2], [[C.k5, C.k52]], 'kpi', k6],
  [k6[3], [[C.k52, C.k0]], 'kpi', k6], [k6[4], [[C.k0, 29.8]], 'kpi', k6], [k6[5], [[cue('On energy alone'), 34]], 'kpi', k6],
  [timeline[1], [[C.n290, C.free]], 'row'],
  [k4[0], [[C.target, C.payback]], 'kpi', k4], [k4[1], [[C.payback, C.five]], 'kpi', k4], [k4[2], [[C.five, C.only]], 'kpi', k4], [k4[3], [[C.only, C.n66]], 'kpi', k4],
  [timeline[5], [[C.years, C.five]], 'row'], [timeline[6], [[C.five, C.only]], 'row'],
  [cols[0].querySelectorAll('li')[0], [[C.rdock, C.rpause]], 'li'], [cols[0].querySelectorAll('li')[1], [[C.rpause, C.rcheck]], 'li'],
  [cols[0].querySelectorAll('li')[2], [[C.rcheck, C.replay]], 'li'],
  [cols[0], [[C.rdock, C.replay]], 'col', cols], [cols[1], [[C.replay, C.simh]], 'col', cols], [cols[2], [[C.simh, C.pilot - .3]], 'col', cols],
  [cols[2].querySelectorAll('li')[0], [[C.simh, C.simr]], 'li'], [cols[2].querySelectorAll('li')[2], [[C.simr, cue('real Basel weather')]], 'li'],
  [rows[0], [[C.msales, C.mprice]], 'row'], [rows[1], [[C.mprice, C.mhw]], 'row'], [rows[2], [[C.mhw, C.midle]], 'row'],
  [rows[3], [[C.midle, C.mrel]], 'row'], [rows[4], [[C.mrel, C.thresh]], 'row'],
  ...rows.map((r, n) => [r.children[2], [[C.thresh + n * .16, C.ifnot]], 'cell']),
];
$('h1', SK).style.height = $('h1', SE).style.height = '140px';

// ---------- titles, badges, notes
const add = (cls, html) => { const d = document.createElement('div'); d.className = 'fx ' + cls; d.innerHTML = html; film.insertBefore(d, $('#f-deck')); return d; };
const TITLES = [
  [C.older, 11.7, 'Older Basel homes, heated with oil or gas'], [C.replace, 17.2, 'Our servers replace the boiler'],
  [45.1, 49.0, 'One heat router, 20 homes and a sports pool'], [C.router, 80.7, 'The heat router decides where each job runs'],
  [81.6, 98.2, '15 January: heat around the clock'], [C.march, 138.6, '7 March: the scheduler controls a real job'],
  [163.6, 184.3, '15 July: the work follows the heat'],
].map(([a, b, h]) => [a, b, add('f-title', h)]);
const BADGES = [
  [C.older, 17.2, 'Illustration in the case model'], [45.5, 49.0, 'Simulation with real 2025 Basel weather'], [C.router + .3, 80.7, 'Simulation with real 2025 Basel weather'],
  [82, 98.2, 'Simulation: shutdown model, real 2025 Basel weather'], [C.real, 138.6, 'Recorded run · Real: docking process, pause and resume · Simulated: house, heat and servers'],
  [164, 184.3, 'Simulation: shutdown model'],
].map(([a, b, h]) => [a, b, add('f-badge', h)]);
const NOTES = [
  [C.stove, C.litres, '<b>Wood stove</b>existing backup for the coldest weather', ''],
  [C.litres, 17.2, '<b>≈ 3,700 litres</b>of heating oil saved per year in an oil-heated reference home', 'good'],
  [C.cold, C.eight, '<b>Below −5 °C</b>outside in the early morning', ''],
  [C.eight, C.eighty, '<b>8 of 8 servers</b>compute around the clock', 'good'],
  [C.eighty, C.seventy, '<b>80% recovered</b>of server power as heat in the water (assumed)', ''],
  [C.seventy, C.rest, '<b>About 70%</b>of the whole day’s demand from servers', ''],
  [C.rest, 98.2, '<b>Wood stove</b>supplies the rest', 'warn'],
  [C.laptop, C.ticker, '<b>Our laptop plays server 8</b>AutoDock Vina really runs on it, against a leukaemia target. House, heat and all 8 servers are simulated', 'good'],
  [C.ticker, C.sched, '<b>Live ticker</b>counts every result of the real process', 'good'],
  [C.sched, C.watch, '<b>Same scheduler code</b>as the yearly balance', 'good'],
  [C.watch, C.two, '<b>The tank charges</b>as the day warms up', ''],
  [C.limit, C.freeze, '<b>14:00 · 35 kWh</b>the tank is full', ''],
  [C.freeze, C.keeps, '<b>Process frozen</b>the operating system stops it (SIGSTOP)', 'warn'],
  [C.keeps, 133, '<b>Nothing is lost</b>8 molecules done, progress kept', 'good'],
  [cue('very same process'), 138.4, '<b>Same process carries on</b>22:00, resumed where it stopped (SIGCONT)', 'good'],
  [C.twelve, C.one, '<b>12 kWh all day</b>the home needs hot water only', ''],
  [C.one, C.send, '<b>1 server on</b>7 stand by', 'good'],
  [C.fifty, C.needs, '<b>50 modelled servers</b>help heat St. Jakob pool', 'good'],
  [C.needs, C.loses, '<b>Needs enough jobs</b>the pool only helps if there is work', ''],
  [C.loses, 184.5, '<b>Limited demand: a loss</b>for the fleet, even with the pool', 'warn'],
].map(([a, b, h, c]) => [a, b, add('f-note ' + c, h)]);

$('#f-question').innerHTML = WORDS.filter(w => w.start < C.digital - .4 && norm(w.text) !== 'were').map(w => `<span>${w.text}</span>`).join('');
const qWords = WORDS.filter(w => w.start < C.digital - .4 && norm(w.text) !== 'were');

// ---------- scheduler illustration
const JOBS = [['Docking', 'no deadline', 1], ['Microscopy', 'due 2 h', 0], ['Docking', 'no deadline', 2], ['Docking', 'no deadline', 3], ['Docking', 'no deadline', -1], ['Docking', 'no deadline', -2]]
  .map(([name, due, slot], n) => {
    const d = document.createElement('div'); d.className = 'f-chip' + (slot === 0 ? ' must' : ''); d.innerHTML = `${name}<br>${due}`;
    $('#s-stage').append(d);
    const at = slot === 0 ? C.must : slot > 0 ? [C.flexj, C.flexj + .7, C.cap][slot - 1] : C.waits + (-slot - 1) * .25;
    return { d, from: [n * 128, 34], to: slot >= 0 ? [8 + slot * 127, 176] : [(-slot - 1) * 128, 308], at };
  });

// ---------- ML drawing
const svgTree = `<svg viewBox="0 0 124 96"><g fill="none" stroke="#5d7690" stroke-width="3"><path d="M62 14L32 48M62 14L92 48M32 48L16 82M32 48L48 82M92 48L76 82M92 48L108 82"/></g>${
  [[62, 14], [32, 48], [92, 48], [16, 82], [48, 82], [76, 82], [108, 82]].map(([x, y]) => `<circle cx="${x}" cy="${y}" r="8" fill="#00a9f4"/>`).join('')}</svg>`;
$('#m-model').insertAdjacentHTML('beforeend', svgTree.repeat(3));
{
  const r = V.CL.ml.reihen, i0 = r.findIndex(x => x[0] >= '11-06T09'), pts = r.slice(i0, i0 + 40);
  const top = Math.max(...pts.flatMap(x => [x[1], x[2]])) * 1.12;
  const line = k => pts.map((x, n) => `${n ? 'L' : 'M'}${6 + n * 744 / (pts.length - 1)} ${156 - x[k] / top * 142}`).join('');
  $('#m-chart').innerHTML = `<svg viewBox="0 0 756 168"><path d="M4 158H752" stroke="#ccc"/><path d="${line(1)}" fill="none" stroke="#a9a9a9" stroke-width="5" pathLength="1" class="act"/><path d="${line(2)}" fill="none" stroke="#2251ff" stroke-width="3.5" pathLength="1" class="pred"/></svg><small><b style="color:#888">━</b> modelled demand &nbsp; <b style="color:#2251ff">━</b> ML forecast &nbsp; · 40 consecutive test samples from November</small>`;
}

// ---------- additions to the scene
const boiler = new THREE.Group();
{
  const M = (c, o = {}) => new THREE.MeshStandardMaterial({ color: c, roughness: .55, metalness: .25, ...o });
  const part = (geo, m, x, y, z) => { const p = new THREE.Mesh(geo, m); p.position.set(x, y, z); boiler.add(p); return p; };
  part(new THREE.BoxGeometry(1.5, 1.9, 1.2), M('#a8473a', { emissive: new THREE.Color('#7a1f12'), emissiveIntensity: .35 }), 0, 1, 0);
  part(new THREE.BoxGeometry(.9, .5, .06), M('#191919'), 0, .7, .63);
  part(new THREE.ConeGeometry(.16, .4, 12), new THREE.MeshBasicMaterial({ color: '#ff7a1a' }), 0, .7, .69);
  part(new THREE.CylinderGeometry(.13, .13, 1.1, 14), M('#555b66'), .4, 2.45, -.2);
  part(new THREE.CylinderGeometry(.62, .62, 2.1, 22), M('#6e7480'), -1.7, 1.12, 0);
  boiler.position.set(.1, -3.12, 8.3); boiler.visible = false;
  V.scene.add(boiler);
}
const boilerLabel = V.label('Oil or gas boiler', .1, -.5, 9, 'warn');
V.STRAHLEN.ml.tubeMat.visible = false; V.STRAHLEN.ml.pts.visible = false;   // the forecast does not steer the router
V.labels.domElement.style.zIndex = 1;
const tempLabels = HAUS.flatMap(h => h.tempLabels);
const sceneLabels = $$('.label').concat([]), cards = Object.entries(KNOTEN).map(([name, k]) => [name, k.div]);

// ---------- camera: target, offset, horizontal shift of the subject (px)
const R = KNOTEN.router.pos, TR = [27, -4.3];
const CAM = [
  [0, [.5, -2.1, 6], [4.6, .9, 6.6], 0], [3.6, [.2, -1.4, 6.5], [3.5, 1.9, 11.8], 0], [7.6, [0, 2.2, 7], [-4.5, 5.2, 25], 0],
  [10.4, [0, -.4, 7.5], [-1.2, 3, 17], 0], [12.9, [-.3, -1.7, 7], [.4, 1.9, 12], 0], [15.8, [-2.6, .2, 7.2], [3, 1.9, 9.5], 0],
  [18.2, [0, 1.2, 7], [2, 4.2, 21], 0], [35, [1, 3, 5], [2, 5, 26], 0],
  [42.6, [3.5, 10.6, 0], [1, 3.6, 27], 0], [46.6, [9.5, 5.4, 0], [.5, 9.5, 52], 0], [50.5, [-4.2, 9.8, 0], [2, 2.6, 29], 430],
  [57, [-3.4, 9.2, .5], [4, 3.6, 31], 430], [63, [-.8, 7.6, 1], [3, 5, 35], 430], [72.6, [.6, 7, 1.5], [-1, 5.6, 33], 430],
  [75.4, [5, 8.6, .5], [0, 5, 34], 0], [77.8, [4.4, 6.2, 3], [-3.5, 6.5, 36], 0], [80.2, [14, 5.4, 1], [1, 8.5, 42], 0],
  [83.6, [0, 1, 7], [1.5, 4, 20], 250], [86.6, [-1, -1.6, 6], [.8, 1.9, 12], 170], [90.4, [1.6, -1.4, 7.6], [2.2, 2, 12.6], 260],
  [93.6, [.2, .3, 7], [1.6, 3, 17], 260], [96.6, [-2.2, .4, 7.2], [2.6, 1.9, 10.5], 170],
  [99.6, [.6, -.6, 7], [-1.2, 3, 17], 250], [104.6, [1.5, -1.8, 6.2], [.9, 1.5, 9], 250], [109.4, [1.1, -1.1, 7.5], [1.7, 2.4, 14], 250],
  [114, [1.6, -1.2, 7.6], [-.8, 2.2, 13.4], 250], [118.6, [2.2, -1.5, 8.2], [1.4, 1.4, 11.2], 210], [123.2, [1.4, -1.6, 7.6], [.5, 1.5, 11.6], 210],
  [127.2, [.8, -1.7, 6.8], [.9, 1.4, 10.8], 210], [132.6, [1.2, -1.1, 7.6], [-.2, 2.2, 13.8], 230], [136.4, [.9, -1.6, 6.4], [.5, 1.4, 10.6], 200],
  [139.9, [1.55, -1.9, 5.9], [.1, .4, 2.7], 0], [146, [1.55, -1.9, 5.9], [.5, .6, 3.2], 0], [157, [TR[0] - 2, 1.2, TR[1] - .6], [.6, .8, 4.2], 0],
  [161.4, [TR[0] - 2, 1.1, TR[1] - .4], [.8, 1.2, 5.2], 0], [164.4, [15.5, 3, 2.5], [1, 9.5, 37], 120], [167.2, [.4, -.7, 7], [.2, 2.8, 15], 240],
  [170.8, [-1.2, -1.6, 6.2], [1, 1.5, 11.4], 190], [174, [15, 3.2, 2], [.4, 8.6, 35], 120], [177, [27, 1, .6], [-3, 5.6, 19], 250],
  [180.6, [27, 1, 1], [-6, 8, 24], 250], [184, [19, 7, 0], [-1, 8, 36], 0],
  [187.6, [14, 11.4, 0], [.2, 2.4, 22], 470], [200, [14.3, 11.5, 0], [-1.4, 2.2, 21], 470], [212, [15, 11.3, 0], [.8, 2.4, 22.5], 470],
  [216.6, [24.5, 11.5, 0], [0, 2.4, 22], 470], [227, [24.6, 11.6, 0], [-1.4, 1.6, 18], 470], [229.6, [24.5, 11.4, 0], [0, 2, 20], 0],
  [294, [1, 1.4, 7], [1.5, 2.6, 15], 0], [298, [3, 2.6, 5.6], [2.5, 5.4, 27], 0], [302.5, [8.4, 4.6, 0], [1, 9.6, 49], 0], [306.2, [9, 5, 0], [0, 10.4, 54], 0],
].map(([t, a, o, s]) => [t, ...a, ...o, s]);

// monotone cubic: smooth through every key, no overshoot
function spline(keys) {
  const n = keys.length, dim = keys[0].length - 1, m = keys.map(() => new Array(dim).fill(0));
  for (let d = 1; d <= dim; d++) for (let i = 1; i < n - 1; i++) {
    const h0 = keys[i][0] - keys[i - 1][0], h1 = keys[i + 1][0] - keys[i][0];
    const s0 = (keys[i][d] - keys[i - 1][d]) / h0, s1 = (keys[i + 1][d] - keys[i][d]) / h1;
    if (s0 * s1 > 0) { const w1 = 2 * h1 + h0, w2 = h1 + 2 * h0; m[i][d - 1] = (w1 + w2) / (w1 / s0 + w2 / s1); }
  }
  return t => {
    if (t <= keys[0][0]) return keys[0].slice(1);
    if (t >= keys[n - 1][0]) return keys[n - 1].slice(1);
    let i = 0; while (keys[i + 1][0] <= t) i++;
    const h = keys[i + 1][0] - keys[i][0], x = (t - keys[i][0]) / h, x2 = x * x, x3 = x2 * x;
    return m[i].map((mi, d) => (2 * x3 - 3 * x2 + 1) * keys[i][d + 1] + (x3 - 2 * x2 + x) * h * mi + (-2 * x3 + 3 * x2) * keys[i + 1][d + 1] + (x3 - x2) * h * m[i + 1][d]);
  };
}
const camAt = spline(CAM);

// ---------- model time: the day glides at a fixed hour, so the sun never flickers
const dayIndex = d => S.zeit.findIndex(z => z.startsWith(d)) / 24;
const CLOCK = [
  [0, '01-15', 17.2], [17, '01-15', 20.4], [39.5, '01-15', 22], [41.5, '05-08', 8], [81, '05-08', 16.8], [83.2, '01-15', 1.2],
  [86.6, '01-15', 3.7], [98, '01-15', 23], [98.9, '03-07', 0], [160, '03-07', 23.6], [161.9, '07-15', 8], [185, '07-15', 17.5],
  [219, '07-15', 18], [293, '07-15', 18.4], [295, '01-15', 17.4], [306.2, '01-15', 19.5],
].map(([t, d, h]) => [t, dayIndex(d), h]);
function modelTime(t) {
  let i = 0; while (i < CLOCK.length - 2 && CLOCK[i + 1][0] <= t) i++;
  const [a, d0, h0] = CLOCK[i], [b, d1, h1] = CLOCK[i + 1], p = clamp((t - a) / (b - a));
  return Math.round(mix(d0, d1, ease(p))) * 24 + (d0 === d1 ? mix(h0, h1, p) : mix(h0, h1, ease(p)));
}

// ---------- recorded runs, shifted onto the voice
const states = A.live, pauseAt = states.find(s => s.L.prozess === 'pausiert').t;
const liveShift = toNew(C.two + .95) - pauseAt;
function liveAt(t) {
  let found = null;
  for (const s of states) { if (s.t + liveShift <= t) found = s.L; else break; }
  return found && found.aktiv ? found : null;
}
let liveNow = null;
window.fetch = async () => liveNow
  ? { ok: true, json: async () => ({ ...liveNow, aktualisiert: Date.now() / 1000 }) }
  : { ok: false };
const H = A.handoff, RECV = C.picks - .25, HAND_SHIFT = toNew(RECV) - H.screens.pool.find(f => f.info[2].includes('Received')).t;
const handFrame = (name, t) => { let found = H.screens[name][0]; for (const f of H.screens[name]) { if (f.t <= t - HAND_SHIFT) found = f; else break; } return found; };

// ---------- helpers
const project = p => { const v = p.clone().project(camera); return [(v.x + 1) / 2 * FW, (1 - v.y) / 2 * FH]; };
function show(node, op, transform) {
  node.style.visibility = op > .004 ? 'visible' : 'hidden';
  node.style.opacity = op;
  if (transform !== undefined) node.style.transform = transform;
}
// a panel fades and slides in briefly, then stands still
const panelIn = (node, t, a, b) => {
  const i = ramp(t, a, a + .6), o = ramp(t, b - .5, b);
  show(node, i * (1 - o), i < 1 ? `translateX(${(1 - i) * 120}px)` : 'none');
};
// zoom a board out of a point of the scene: p = 0 is that point, p = 1 full frame
function grow(node, p, [x, y], radius = true) {
  x = clamp(x, 180, FW - 180); y = clamp(y, 140, FH - 140);
  const s = Math.pow(.07, 1 - p);
  node.style.transform = `translate(${mix(x, 0, (s - .07) / .93) - FW * .035 * (1 - (s - .07) / .93)}px, ${mix(y, 0, (s - .07) / .93) - FH * .035 * (1 - (s - .07) / .93)}px) scale(${s})`;
  node.style.borderRadius = radius ? `${(1 - p) * 110}px` : '';
  show(node, clamp(p * 5));
}
// orbs of work: [second, from, to]
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);
const P = { h1: V3(-1, -.6, 7), h2: V3(11, -.6, 7), bad: V3(TR[0] - 1, 2, TR[1]) };
const nb = n => V3(-15 + (n % 6) * 3.4, .4, -11 - (n % 2) * 1.3);
const FLIGHTS = [];
for (let n = 0; n < 5; n++) FLIGHTS.push([48 + n * .5, V3(-13.5, 17, .4), KNOTEN.pool.pos]);
for (let n = 0; n < 7; n++) FLIGHTS.push([C.router + .2 + n * .28, KNOTEN.pool.pos, R]);
for (let n = 0; n < 9; n++) FLIGHTS.push([C.first + n * .14, R, [P.h1, P.h2, nb(n)][n % 3]]);
for (let n = 0; n < 9; n++) FLIGHTS.push([C.take + n * .22, R, P.bad]);
for (let n = 0; n < 16; n++) FLIGHTS.push([C.send + n * .34, n % 3 === 0 ? R : n % 3 === 1 ? P.h1 : nb(n), P.bad]);

const jetzt = el('jetzt'), zeit = el('zeit'), kopf = el('kopf'), liveDot = $('#live i');
const row = id => el(id).parentElement;
const ROWS = [
  ['j-on', [[C.eight, C.eighty], [C.freeze, C.keeps], [C.one, C.send], [cue('very same process'), 138.4]]],
  ['j-deck', [[C.seventy, C.rest]]], ['j-oel', [[C.rest, 98.2]]], ['j-sp', [[C.watch, C.freeze]]],
  ['j-bed', [[cue('house needs less heat'), 121], [C.twelve, C.one]]], ['j-bad-z', [[C.send, 184]]],
];
function groups(list) {
  let g = 0;
  for (const e of jetzt.children) {
    const cut = e.classList.contains('trenn');
    if (cut) g++;
    e.classList.toggle('off', !list.includes(g) || cut || e.id === 'modell' || e.classList.contains('legende'));
  }
}
let prevT = null, groupKey = '', skip = false;
const render = V.composer.render.bind(V.composer);
V.composer.render = () => { if (!skip) render(); };
dispatchEvent(new Event('resize'));
V.panelAuf(true); V.setCloud(true);

// ---------- one frame
window.__cues = { pairs: PAIRS, cues: Object.fromEntries(Object.entries(C).map(([k, v]) => [k, +toNew(v).toFixed(2)])), pause: toNew(C.two + .95), resume: states.find(s => s.t > pauseAt && s.L.prozess !== 'pausiert').t + liveShift, recv: toNew(RECV) };
window.__frame = async T => {
  const t = toOld(T);
  window.__vt = T * 1000;
  for (const [at, from, to] of FLIGHTS) if (prevT !== null && prevT < at && at <= t) V.flug(from, to);
  prevT = t;

  liveNow = liveAt(T);
  V.time(modelTime(t));
  await V.pruefeLive();

  // scene
  const c = camAt(t), breathe = Math.sin(t * .23);
  camera.position.set(c[0] + c[3] + breathe * .12, c[1] + c[4] + Math.sin(t * .17) * .05, c[2] + c[5]);
  V.controls.target.set(c[0], c[1], c[2]);
  camera.setViewOffset(FW, FH, c[6], 0, FW, FH);
  const old = ramp(t, C.oil - .9, C.oil + .5) * (1 - ramp(t, C.replace, C.replace + 1.3));
  boiler.visible = old > .01;
  boiler.scale.setScalar(Math.max(.001, old));
  boiler.position.y = -3.12 + ramp(t, C.replace, C.replace + 1.3) * 1.4;
  boilerLabel.style.opacity = old * old;
  HAUS[0].racks.forEach((r, k) => {
    const gone = ramp(t, C.oil - 1.2 + k * .05, C.oil - .3 + k * .05) * (1 - ramp(t, C.replace + .3 + k * .12, C.replace + 1.1 + k * .12));
    r.g.scale.y = Math.max(.001, 1 - gone); r.g.visible = gone < .995;
  });

  // how much of the frame the slides cover
  const s1in = ramp(t, 17.05, 18.1), s1out = ramp(t, 42.9, 44.0);
  const sIn = ramp(t, C.pay - .9, C.pay + .2), sOut = ramp(t, 296.4, 297.6);
  const keyP = s1in * (1 - s1out), deckP = sIn * (1 - sOut);
  const pan = ramp(t, C.open - .7, C.open + .2) + ramp(t, C.pilot - .6, C.pilot + .3);
  const still = Math.abs(pan - Math.round(pan)) < .0001;
  skip = keyP > .99999 || (deckP > .99999 && still) || ramp(t, C.endcard - 1.0, C.endcard - .1) > .99999;
  V.tick();
  camera.updateMatrixWorld();

  // labels of the scene
  const cloudOn = Math.max(span(t, 44, 80.4, .8, .8), span(t, 184.6, 227.6, .8, .8));
  for (const [name, div] of cards) div.style.opacity = cloudOn * (name === 'router' ? 1 - span(t, 49.6, 73.6, .6, .8) : 1) * ((name === 'ml' || name === 'zusage') && t < 80.5 ? 0 : 1);
  const clean = Math.max(1 - ramp(t, 4.4, 6.2), span(t, 139, 163.3, .5, .5), ramp(t, 301, 302.6));
  const wide = Math.max(span(t, 45, 49.4), span(t, 75, 81.4), span(t, 173.6, 184.2));
  for (const d of sceneLabels) if (d !== boilerLabel) d.style.opacity = (1 - clean) * (d.textContent.startsWith('House 0') ? span(t, 173.6, 184.2) : t > 74 && t < 81.5 && d.textContent.includes('more houses') ? 0 : wide);
  const temps = Math.max(span(t, 85, 98), span(t, 167, 172.6)) * .9;
  for (const d of tempLabels) d.style.opacity = temps;

  // dashboard furniture
  const key = t < 163 ? '0' : t < C.send + .5 ? '0' : '2';
  if (key !== groupKey) { groups([+key]); groupKey = key; }
  const jp = Math.max(span(t, 83.4, 98, .9, .7), span(t, 99.5, 138.4, .9, .7), span(t, 166, C.send + .4, .8, .5), span(t, C.send + .9, 184, .8, .7));
  show(jetzt, jp, `translateX(${(1 - jp) * 110}px)`);
  const tl = Math.max(span(t, 81.6, 138.4, .8, .7), span(t, 162.6, 184.4, .8, .7));
  show(zeit, tl, `translateY(${(1 - tl) * 80}px)`);
  for (const [id, wins] of ROWS) {
    const p = Math.max(...wins.map(([a, b]) => span(t, a, b, .35, .4))), r = row(id);
    r.style.background = `rgba(255,138,61,${p * .25})`;
    r.style.boxShadow = p > .01 ? `inset 0 0 0 ${p * 2.5}px rgba(255,160,90,.95)` : 'none';
  }
  const lp = span(t, C.real, 138.4, .5, .5);
  const punch = Math.max(span(t, C.ticker, C.sched, .4, .6), span(t, C.freeze, C.keeps + 1, .3, .6), span(t, C.carries, 138.4, .4, .4));
  show(kopf, lp);
  el('live').style.borderColor = `rgba(255,${Math.round(93 + 130 * punch)},${Math.round(74 + 70 * punch)},1)`;
  liveDot.style.opacity = liveNow && liveNow.prozess === 'läuft' ? .62 + .38 * Math.cos(T * 2 * Math.PI) : 1;
  liveDot.style.background = liveNow && liveNow.prozess !== 'läuft' ? '#ffc857' : '#ff5d4a';

  // opening
  const qOut = ramp(t, C.digital - 1.0, C.digital - .3);
  show($('#f-question'), 1 - qOut, `translateY(${-qOut * 50}px)`);
  [...$('#f-question').children].forEach((s, n) => {
    const p = ramp(t, qWords[n].start - .12, qWords[n].start + .22);
    s.style.opacity = .12 + .88 * p; s.style.transform = `translateY(${(1 - p) * 10}px)`;
  });
  const br = span(t, C.digital - .35, C.older + .15, .6, .6);
  show($('#f-brand'), br, `scale(${.9 + .1 * br})`);

  for (const [a, b, d] of TITLES) { const p = span(t, a, b, .7, .5); show(d, p, `translateX(${(1 - p) * -70}px)`); }
  for (const [a, b, d] of BADGES) { const p = span(t, a, b, .7, .5); show(d, p, `translateX(${(1 - p) * -50}px)`); }
  for (const [a, b, d] of NOTES) { const p = span(t, a + .05, b - .1, .4, .3); show(d, p, `translateY(${(1 - p) * 26}px)`); }
  for (const [node, at, pos] of [['#f-tag1', C.first, V3(0, 8.4, 8.5)], ['#f-tag2', C.take, V3(TR[0], 6.4, TR[1])]]) {
    const p = span(t, at, 81.2, .5, .5), [x, y] = project(pos);
    show($(node), p, `translate(${clamp(x, 220, FW - 360)}px,${clamp(y, 250, 900)}px) translate(-50%,-50%) scale(${.6 + .4 * p})`);
  }

  // mechanism panels
  panelIn($('#p-queue'), t, C.queue - .6, C.hour + .3);
  for (const d of $('#q-grid').children) {
    const col = +(d.dataset.col || 0), r = +(d.dataset.row || 0);
    const w = !r ? (col === 1 ? [C.canp, C.nodl] : col === 2 ? [C.nodl, C.micro] : [C.main, C.dock])
      : r === 1 ? (col === 1 ? [C.canp, C.micro] : col === 2 ? [C.nodl, C.micro] : [C.dock, C.micro])
      : (col === 1 ? [C.nopause, C.hour] : col === 2 ? [C.due, C.hour] : [C.micro, C.hour]);
    const p = span(t, w[0], w[1], .35, .4);
    d.style.background = p > .01 ? `color-mix(in srgb, #cfe3ff ${p * 100}%, ${d.classList.contains('h') ? '#e6ebf5' : '#f2f2f2'})` : '';
    d.style.boxShadow = p > .01 ? `inset 0 0 0 4px rgba(34,81,255,${p})` : 'none';
  }
  const dm = ramp(t, C.dock - .15, C.dock + .3);
  $('#q-demo').style.opacity = .2 + .8 * dm;
  $('#q-demo').style.background = dm > .5 ? '#2251ff' : '#051c2c';
  panelIn($('#p-sched'), t, C.hour, C.router + .35);
  $$('.f-step', $('#p-sched')).forEach((d, n) => {
    const p = span(t, [C.must - .5, C.flexj, C.waits][n], [C.flexj, C.waits, C.router][n], .4, .4);
    d.style.background = `rgb(${mix(242, 207, p)},${mix(242, 227, p)},${mix(242, 255, p)})`;
  });
  for (const j of JOBS) {
    // jobs change place by fading, nothing travels
    const p = clamp((t - j.at) / .7), [x, y] = p < .5 ? j.from : j.to;
    j.d.style.opacity = Math.abs(1 - 2 * p);
    j.d.style.transform = `translate(${x}px,${y}px)`;
  }
  const cap = span(t, C.cap, C.router, .4);
  $('#s-cap').style.opacity = .3 + .7 * cap; $('#s-run').style.borderColor = `rgba(255,138,61,${.55 + .45 * cap})`;

  panelIn($('#p-ml'), t, C.plan, C.customers + .5);
  [...$('#m-in').children].forEach((d, n) => {
    const at = [C.weather, C.time, C.season, C.past][n], p = ramp(t, at - .1, at + .35);
    d.style.opacity = .22 + .78 * p;
  });
  $('#m-model').style.opacity = .35 + .65 * ramp(t, C.boost - .2, C.boost + .4);
  $$('#m-model svg').forEach((s, n) => {
    const p = ramp(t, C.boost + n * .5, C.boost + .6 + n * .5);
    s.style.opacity = p;
  });
  for (const [cls, a] of [['.act', C.sixh - .6], ['.pred', C.past]]) {
    const p = $('#m-chart ' + cls); p.style.opacity = ramp(t, a, a + .8);
  }
  $$('.m-err').forEach((d, n) => {
    const p = ramp(t, n ? C.ten - .3 : C.unseen - .4, n ? C.ten + .7 : C.unseen + .6);
    d.style.opacity = p; $('i', d).style.width = `${[250, 250 * .531 / .593][n]}px`;
  });
  $$('.m-row').forEach((d, n) => {
    const p = ramp(t, [C.experiment, C.steer, C.lever][n] - .1, [C.experiment, C.steer, C.lever][n] + .4);
    d.style.opacity = p;
  });
  panelIn($('#p-day'), t, C.customers + .5, C.pay - .2);
  $$('.d-step').forEach((d, n) => {
    const at = [C.noon, C.copy, C.margin], p = ramp(t, at[n] - .15, at[n] + .4), h = span(t, at[n], [at[1], at[2], C.n91][n], .4, .4);
    d.style.opacity = .18 + .82 * p;
    d.style.boxShadow = h > .01 ? `inset 0 0 0 4px rgba(34,81,255,${h})` : 'none';
  });
  const dr = ramp(t, C.n91 - .2, C.n91 + .5);
  show($('#d-result'), dr);

  // the handover: zoom through server 8, out through a pool rack
  const hIn = ramp(t, 140.5, 141.9), hOut = ramp(t, 162.3, 163.5), hp = hIn * (1 - hOut), hand = $('#f-hand');
  if (hp > .001) {
    grow(hand, hp, project(t < 151 ? HAUS[0].racks[7].g.position.clone().add(V3(0, 1, .46)) : V3(TR[0] - 3.2, 1.2, TR[1] - .8)));
    $('#h-board').style.transform = 'none';
    const loads = [];
    for (const name of ['house', 'pool']) {
      const img = $('#h-' + name), url = `/__film/runs/handoff/${name}/${handFrame(name, T).file}`;
      if (img.getAttribute('src') !== url) { img.src = url; loads.push(img.decode()); }
    }
    await Promise.all(loads);
    show($('#h-packet'), span(t, C.saves, C.nine + .4, .4, .5), 'none');
    show($('#h-wire'), 0);
    const r1 = span(t, C.nine - .8, C.summer - .5, .4, .4), r2 = 0;
    Object.assign($('#h-ring-state').style, { left: '1448px', top: '434px', width: '398px', height: '78px' });
    Object.assign($('#h-ring-rank').style, { left: '1448px', top: '707px', width: '398px', height: '74px' });
    show($('#h-ring-state'), r1); show($('#h-ring-rank'), r2);
  } else show(hand, 0);
  const hb = span(t, C.may, 162.4, .6, .5);
  show(handBadge, hb, `translateY(${(1 - hb) * 30}px)`);

  // slides
  BOARDS.forEach(({ b, sec }, n) => {
    const p = n === 0 ? keyP : deckP, idx = n - 1, frac = pan - Math.floor(pan);
    if (p < .001 || (n > 0 && Math.abs(idx - pan) >= 1)) { show(b, 0); return; }
    if (p < .99999) {
      const anchor = n === 0 ? (t < 30 ? V3(0, 2, 8) : R) : (t < 260 ? KNOTEN.zusage.pos : V3(0, 2, 8));
      grow(b, p, project(anchor));
    } else {
      const x = n === 0 ? 0 : (idx - pan) * 1920;
      b.style.transform = x ? `translateX(${x}px)` : 'none';
      b.style.borderRadius = '0';
      show(b, 1);
    }
    sec.style.transform = 'none';
  });
  for (const [m, a, b] of MARKS) m.style.backgroundColor = `rgba(0,169,244,${.32 * ramp(t, a - .1, a + .3) * (1 - ramp(t, b, b + .4))})`;
  const active = BLOCKS.map(([, w]) => Math.max(...w.map(([a, b]) => span(t, a, b, .35, .4))));
  BLOCKS.forEach(([node, , kind, peers], n) => {
    const p = active[n];
    const others = peers ? Math.max(...BLOCKS.map((b, k) => b[3] === peers ? active[k] : 0)) : 0;
    if (kind === 'kpi') {
      node.style.background = `rgba(34,81,255,${p * .13})`;
      node.style.boxShadow = p > .001 ? `0 0 0 10px rgba(34,81,255,${p * .13})` : 'none';
    } else if (kind === 'row') {
      for (const td of node.children) td.style.background = p > .01 ? `rgba(0,169,244,${p * .28})` : '';
    } else if (kind === 'cell') {
      if (p > .01) node.style.background = `rgba(34,81,255,${p * .2})`;
      node.style.color = p > .5 ? '#2251ff' : '';
    } else if (kind === 'li') {
      node.style.background = `rgba(0,169,244,${p * .24})`;
    }
    if (peers) node.style.opacity = 1 - .55 * clamp(others - p);
  });
  for (const k of [...k4].filter(k => !BLOCKS.some(b => b[0] === k)))
    k.style.opacity = 1 - .55 * Math.max(...BLOCKS.map((b, n) => b[3] === k4 ? active[n] : 0));

  // end card over the moving scene
  const e = ramp(t, C.endcard - 1.0, C.endcard - .1), end = $('#f-end');
  show(end, e);
  const sec = $('section', endRoot), big = $('.big', sec), say = $('.say', sec), line = $('.line', sec);
  line.style.width = '124px';
  line.style.opacity = ramp(t, C.endcard, C.endcard + .5);
  say.style.opacity = ramp(t, cue('useful computing', 300) - .1, cue('useful computing', 300) + .4);
  big.style.opacity = ramp(t, C.endcard - .6, C.endcard + .2);

  document.body.getBoundingClientRect();
};
const handBadge = add('f-badge', 'Real: checkpoint transfer over TLS · Replayed: Vina scores and routing · Simulated: heat');
film.append(handBadge);
Object.assign(handBadge.style, { top: 'auto', bottom: '28px', zIndex: 2 });
})();
