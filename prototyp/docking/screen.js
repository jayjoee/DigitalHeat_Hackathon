const get = id => document.getElementById(id);
let requestActive = false;
const num = new Intl.NumberFormat("de-CH", {maximumFractionDigits: 2});

const statusLabels = {
  bereit: "Bereit zum Start",
  rechnet: "Screening läuft",
  "Übergabe läuft": "Haus pausiert · Checkpoint unterwegs",
  "Übergabe offen": "Bestätigung ausstehend",
  übergeben: "Haus pausiert · Sportbad dockt",
  zurückgegeben: "Sportbad pausiert · zurück ans Haus",
  fertig: "Screening abgeschlossen",
};

function showItem(item, starkKcal) {
  if (!item) return;
  get("image-title").textContent = "Molekül " + (item.index + 1);
  get("mol-name").textContent = item.name;
  get("mol-gruppe").textContent = item.gruppe;
  get("energie-wert").textContent = num.format(item.energie);
  const fraction = Math.min(1, Math.max(0, -item.energie / 15));
  get("energie-fill").style.width = (fraction * 100).toFixed(0) + "%";
  get("energie-fill").style.background = item.stark ? "var(--mint)" : "#5c7a80";
  get("verdict").textContent = item.stark ? "Starker Treffer" : "Bindet";
  get("verdict").dataset.result = item.stark ? "pass" : "";
  get("image-note").textContent = item.stark
    ? item.name + " passt sehr gut in die Bindetasche (≤ " + starkKcal + " kcal/mol)."
    : item.name + " bindet schwächer.";
}

function showRanking(data, done) {
  const liste = get("rangliste");
  const fertig = (data.molekuele || []).slice(0, done)
    .map((m, i) => ({...m, nr: i + 1}))
    .sort((a, b) => a.energie - b.energie).slice(0, 5);
  if (!fertig.length) {
    liste.innerHTML = '<li><span class="pos"></span><span>noch keiner</span><span class="e"></span></li>';
    return;
  }
  liste.innerHTML = fertig.map((m, i) =>
    `<li class="${m.energie <= data.stark_kcal ? "stark" : ""}"><span class="pos">${i + 1}</span>`
    + `<span>${m.name}</span><span class="e">${num.format(m.energie)} kcal/mol</span></li>`).join("");
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
    handoff = "Haus braucht wieder Wärme · Rückkehr ab Molekül " + data.return_at;
  } else if (data.state === "übergeben") {
    handoff = "Das Haus nutzt gespeicherte Wärme, während das Sportbad dockt.";
  } else if (data.state === "Übergabe läuft") {
    handoff = "Speicher voll · Prüfstand nach Molekül " + done + " wird gesendet.";
  } else if (data.state === "Übergabe offen") {
    handoff = "Das Haus pausiert. Ihr könnt denselben Prüfstand erneut senden.";
  } else if (data.resumed_after > 0) {
    handoff = "Vom Haus übernommen · weiter ab Molekül " + (data.resumed_after + 1);
  } else if (!data.control) {
    handoff = "Wartet auf den Prüfstand aus dem Haus.";
  } else if (data.state === "rechnet") {
    handoff = "Bei vollem Hausspeicher übernimmt das Sportbad.";
  }
  get("handoff").textContent = handoff;
  const local = data.local_ranges.reduce((count, [first, last]) => count + last - first + 1, 0);
  const ranges = data.local_ranges.map(([first, last]) => first === last ? String(first) : first + "–" + last);
  get("recent").textContent = local
    ? "Hier getestet · " + local + (local === 1 ? " Molekül" : " Moleküle") + " (Nr. " + ranges.join(", ") + ")"
    : "Hier getestet · noch kein Molekül";
}

function showHeat(heat) {
  get("heat-time").textContent = heat.time.slice(11, 16) + " Uhr";
  get("outdoor").textContent = num.format(heat.outside_c) + " °C draussen";
  get("heat-power").textContent = num.format(heat.heat_kw) + " kW";
  get("heat-forward").textContent = heat.forward_c == null ? "–" : heat.forward_c + " °C";
  get("heat-room-target").textContent = num.format(heat.room_target_c) + " °C";
  get("heat-tank").textContent = num.format(heat.tank_kwh) + " kWh";
  get("tank-capacity").textContent = "von " + num.format(heat.tank_max_kwh) + " kWh Kapazität";
}

async function refresh() {
  const response = await fetch("/status");
  if (!response.ok) throw Error("Anzeige nicht erreichbar.");
  const data = await response.json();
  const done = data.job?.next ?? 0;
  const stark = data.job?.rejects ?? 0;
  get("site").textContent = data.site;
  get("schloss").textContent = data.schloss;
  let state = statusLabels[data.state];
  if (!data.control && data.state === "bereit") state = "Wartet auf das Haus";
  if (data.heat.scheduled_pause) state = "Docking pausiert · Router gibt keine Rechenzeit frei";
  if (data.sync_pending) state = "Haus pausiert · warte auf die Verbindung zum Sportbad";
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
    get("state").textContent = "Verbindung unterbrochen";
    get("start").disabled = get("move").disabled = true;
  } finally {
    setTimeout(poll, 350);
  }
}
poll();
