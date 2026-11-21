const get = id => document.getElementById(id);
let requestActive = false;
const num = new Intl.NumberFormat("en-GB", {maximumFractionDigits: 2});

const statusLabels = {
  bereit: "Ready to start",
  rechnet: "Screening in progress",
  "Übergabe läuft": "House paused · sending checkpoint",
  "Übergabe offen": "Awaiting confirmation",
  übergeben: "House paused · sports pool screening",
  zurückgegeben: "Sports pool paused · returned to house",
  fertig: "Screening complete",
};

const moleculeNames = {
  Koffein: "Caffeine", Nikotin: "Nicotine", Zimtaldehyd: "Cinnamaldehyde", Lidocain: "Lidocaine",
};
const groups = {
  Alltag: "Everyday compound", Medikament: "Medicine",
  "Kinasehemmer (Leukämie)": "Kinase inhibitor (leukaemia)",
  "Kinasehemmer (Lunge)": "Kinase inhibitor (lung)",
  "Kinasehemmer (Niere/Leber)": "Kinase inhibitor (kidney/liver)",
  "Kinasehemmer (Niere)": "Kinase inhibitor (kidney)",
  "Kinasehemmer (Brust)": "Kinase inhibitor (breast)",
};
const moleculeName = name => moleculeNames[name] ?? name;
const groupLabel = group => groups[group] ?? group;

function showItem(item, starkKcal) {
  if (!item) return;
  get("image-title").textContent = "Molecule " + (item.index + 1);
  get("mol-name").textContent = moleculeName(item.name);
  get("mol-gruppe").textContent = groupLabel(item.gruppe);
  get("energie-wert").textContent = num.format(item.energie);
  const fraction = Math.min(1, Math.max(0, -item.energie / 15));
  get("energie-fill").style.width = (fraction * 100).toFixed(0) + "%";
  get("energie-fill").style.background = item.stark ? "var(--mint)" : "#5c7a80";
  get("verdict").textContent = item.stark ? "Strong hit" : "Binds";
  get("verdict").dataset.result = item.stark ? "pass" : "";
  get("image-note").textContent = item.stark
    ? moleculeName(item.name) + " has a strong predicted fit (≤ " + starkKcal + " kcal/mol)."
    : moleculeName(item.name) + " has a weaker predicted fit.";
}

function showRanking(data, done) {
  const liste = get("rangliste");
  const fertig = (data.molekuele || []).slice(0, done)
    .map((m, i) => ({...m, nr: i + 1}))
    .sort((a, b) => a.energie - b.energie).slice(0, 5);
  if (!fertig.length) {
    liste.innerHTML = '<li><span class="pos"></span><span>None yet</span><span class="e"></span></li>';
    return;
  }
  liste.innerHTML = fertig.map((m, i) =>
    `<li class="${m.energie <= data.stark_kcal ? "stark" : ""}"><span class="pos">${i + 1}</span>`
    + `<span>${moleculeName(m.name)}</span><span class="e">${num.format(m.energie)} kcal/mol</span></li>`).join("");
}

function showRoute(data, done) {
  get("route-house").removeAttribute("aria-current");
  get("route-pool").removeAttribute("aria-current");
  get("route-arrow").textContent = data.return_at ? "←" : "→";
  if (data.job) {
    const atHouse = data.return_at || (data.control && data.state !== "übergeben");
    get(atHouse ? "route-house" : "route-pool").setAttribute("aria-current", "step");
  }
  let handoff = "";
  if (data.return_at) {
    handoff = "House needs heat again · resuming at molecule " + data.return_at;
  } else if (data.state === "übergeben") {
    handoff = "The house draws heat from storage while screening runs at the sports pool.";
  } else if (data.state === "Übergabe läuft") {
    handoff = "Tank full · checkpoint after molecule " + done + " is being sent.";
  } else if (data.state === "Übergabe offen") {
    handoff = "The house is paused. You can resend the same checkpoint.";
  } else if (data.resumed_after > 0) {
    handoff = "Received from house · starting at molecule " + (data.resumed_after + 1);
  } else if (!data.control) {
    handoff = "Waiting for the checkpoint from the house.";
  } else if (data.state === "rechnet") {
    handoff = "The sports pool takes over when the house tank fills.";
  }
  get("handoff").textContent = handoff;
  const local = data.local_ranges.reduce((count, [first, last]) => count + last - first + 1, 0);
  const ranges = data.local_ranges.map(([first, last]) => first === last ? String(first) : first + "–" + last);
  get("recent").textContent = local
    ? "Tested here · " + local + (local === 1 ? " molecule" : " molecules") + " (no. " + ranges.join(", ") + ")"
    : "Tested here · no molecules yet";
}

function showHeat(heat) {
  get("heat-time").textContent = heat.time.slice(11, 16);
  get("outdoor").textContent = num.format(heat.outside_c) + " °C outdoors";
  get("heat-power").textContent = num.format(heat.heat_kw) + " kW";
  get("heat-forward").textContent = heat.forward_c == null ? "–" : heat.forward_c + " °C";
  get("heat-room-target").textContent = num.format(heat.room_target_c) + " °C";
  get("heat-tank").textContent = num.format(heat.tank_kwh) + " kWh";
  get("tank-capacity").textContent = "of " + num.format(heat.tank_max_kwh) + " kWh capacity";
}

async function refresh() {
  const response = await fetch("/status");
  if (!response.ok) throw Error("Screen is unavailable.");
  const data = await response.json();
  const done = data.job?.next ?? 0;
  const stark = data.job?.rejects ?? 0;
  get("site").textContent = data.site;
  get("schloss").textContent = data.schloss;
  let state = statusLabels[data.state];
  if (!data.control && data.state === "bereit") state = "Waiting for the house";
  if (data.heat.scheduled_pause) state = "Docking paused · router has paused compute";
  if (data.sync_pending) state = "House paused · waiting for the sports pool connection";
  get("state").textContent = state;
  get("count").textContent = done + " / " + data.total;
  const percent = Math.round(100 * done / data.total);
  get("progress").setAttribute("aria-valuemax", data.total);
  get("progress").setAttribute("aria-valuenow", done);
  get("progress-fill").style.width = percent + "%";
  get("percent").textContent = percent + " %";
  get("rejects").textContent = stark;
  get("passed").textContent = done;
  showRoute(data, done);
  showRanking(data, done);
  showHeat(data.heat);
  if (data.item) showItem(data.item, data.stark_kcal);
  get("start").hidden = !data.control || data.state !== "bereit";
  get("move").hidden = !data.control || data.state !== "Übergabe offen";
  get("move").disabled = requestActive || done === 0;
  get("start").disabled = requestActive;
  get("start").onclick = () => send("/start", data.csrf);
  get("move").onclick = () => send("/move", data.csrf);
}

async function send(path, csrf) {
  if (requestActive) return;
  requestActive = true;
  get("start").disabled = get("move").disabled = true;
  get("error").textContent = "";
  try {
    const response = await fetch(path, {method: "POST", headers: {
      "Content-Type": "application/json", "X-DigitalHeat-CSRF": csrf
    }, body: "{}"});
    if (!response.ok) throw Error((await response.json()).error);
  } catch (error) {
    get("error").textContent = error.message;
  } finally {
    requestActive = false;
  }
}

async function poll() {
  try {
    await refresh();
  } catch {
    get("state").textContent = "Connection lost";
    get("start").disabled = get("move").disabled = true;
  } finally {
    setTimeout(poll, 350);
  }
}
poll();
