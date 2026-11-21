const get = id => document.getElementById(id);
const canvas = get("frame");
const context = canvas.getContext("2d");
const raster = document.createElement("canvas");
raster.width = 240;
raster.height = 144;
const rasterContext = raster.getContext("2d");
let previousFrame;
let requestActive = false;

let activeFrame;
let frameStarted;
let isRunning = false;
let animationPending = false;
const reducedMotion = matchMedia("(prefers-reduced-motion: reduce)");
const scanDuration = 650;

const statusLabels = {
  bereit: "Bereit zum Start",
  rechnet: "Prüfung läuft",
  "Übergabe läuft": "Haus pausiert · Checkpoint unterwegs",
  "Übergabe offen": "Bestätigung ausstehend",
  übergeben: "Haus pausiert · ans Sportbad übergeben",
  fertig: "Prüfung abgeschlossen",
};

function draw(frame) {
  if (!frame || previousFrame === frame.index) return;
  previousFrame = frame.index;
  activeFrame = frame;
  frameStarted = performance.now();
  const bytes = atob(frame.pixels);
  const image = rasterContext.createImageData(raster.width, raster.height);
  for (let i = 0; i < bytes.length; i++) {
    const level = bytes.charCodeAt(i);
    image.data.set([level, level + 6, level + 10, 255], i * 4);
  }
  rasterContext.putImageData(image, 0, 0);
  get("empty-camera").hidden = true;
  get("image-title").textContent = "Packung " + (frame.index + 1);
  setVerdict("Prüfbild wird eingeblendet", "scan", "Die Markierungen zeigen das Ergebnis der Pixelprüfung.");
  schedulePaint();
}

function setVerdict(label, result, note) {
  get("verdict").textContent = label;
  get("verdict").dataset.result = result;
  get("image-note").textContent = note;
}

function schedulePaint() {
  if (animationPending) return;
  animationPending = true;
  requestAnimationFrame(animate);
}

function animate(now) {
  animationPending = false;
  if (activeFrame) {
    const fraction = !isRunning || reducedMotion.matches
      ? 1 : Math.min(1, Math.max(0, (now - frameStarted) / scanDuration));
    const sx = canvas.width / raster.width;
    const sy = canvas.height / raster.height;
    context.drawImage(raster, 0, 0, canvas.width, canvas.height);
    if (fraction < 1) {
      const scanX = fraction * canvas.width;
      context.fillStyle = "#111b1c99";
      context.fillRect(scanX, 0, canvas.width - scanX, canvas.height);
      context.fillStyle = "#8ae8ba";
      context.fillRect(scanX, 0, 4, canvas.height);
    }
    for (const [x, y, missing] of activeFrame.boxes) {
      if (x / raster.width > fraction) continue;
      if (missing) {
        context.strokeStyle = "#ff7267";
        context.lineWidth = 4;
        context.strokeRect((x - 21) * sx, (y - 22) * sy, 42 * sx, 44 * sy);
        context.fillStyle = "#ff7267";
        context.fillRect((x - 21) * sx, (y + 12) * sy, 42 * sx, 10 * sy);
        context.fillStyle = "#201516";
        context.font = "bold 19px system-ui";
        context.textAlign = "center";
        context.fillText("FEHLT", x * sx, (y + 20) * sy);
      } else {
        context.fillStyle = "#8ae8ba";
        context.beginPath();
        context.arc((x + 15) * sx, (y - 16) * sy, 4.5, 0, 2 * Math.PI);
        context.fill();
      }
    }
    if (fraction < 1) {
      schedulePaint();
    } else {
      const missing = activeFrame.boxes.flatMap((box, index) => box[2] ? [index + 1] : []);
      const filled = activeFrame.boxes.length - missing.length;
      const note = filled + " von " + activeFrame.boxes.length + " Fächern befüllt";
      setVerdict(missing.length ? "Beanstandet" : "Vollständig",
        missing.length ? "reject" : "pass",
        missing.length ? note + " · Fehlt in " + (missing.length === 1 ? "Fach " : "den Fächern ") +
          missing.join(", ") : note);
    }
  }
}

function showRoute(data, done) {
  const previous = data.resumed_after;
  get("route-house").removeAttribute("aria-current");
  get("route-pool").removeAttribute("aria-current");
  if (data.job) {
    get(data.control && data.state !== "übergeben" ? "route-house" : "route-pool")
      .setAttribute("aria-current", "step");
  }
  let handoff = "";
  if (previous > 0) {
    handoff = "Vom Haus übernommen · Weiter ab Packung " + (previous + 1);
  } else if (data.state === "übergeben") {
    handoff = "Speicher voll · Sportbad übernimmt ab Packung " + (done + 1);
  } else if (data.state === "Übergabe läuft") {
    handoff = "Speicher voll · Prüfstand nach Packung " + done + " wird gesendet.";
  } else if (data.state === "Übergabe offen") {
    handoff = "Das Haus pausiert. Ihr könnt denselben Prüfstand erneut senden.";
  } else if (!data.control) {
    handoff = "Wartet auf den Prüfstand aus dem Haus.";
  } else if (data.state === "rechnet") {
    handoff = "Der Wärme-Router wechselt bei vollem Hausspeicher automatisch zum Sportbad.";
  }
  get("handoff").textContent = handoff;
  const local = done - previous;
  get("recent").textContent = local > 0
    ? "Hier geprüft · " + local + (local === 1 ? " Packung (" : " Packungen (") +
      (local === 1 ? "Nr. " + done : "Nr. " + (previous + 1) + "–" + done) + ")"
    : "Hier geprüft · noch keine Packung";
}

const heatNumber = new Intl.NumberFormat("de-CH", {maximumFractionDigits: 2});

function showHeat(heat) {
  get("heat-time").textContent = heat.time.slice(11, 16) + " Uhr";
  get("outdoor").textContent = heatNumber.format(heat.outside_c) + " °C draussen";
  get("heat-power").textContent = heatNumber.format(heat.heat_kw) + " kW";
  get("heat-forward").textContent = heat.forward_c == null ? "–" : heat.forward_c + " °C";
  get("heat-tank").textContent = heatNumber.format(heat.tank_kwh) + " kWh";
  get("tank-capacity").textContent = "von " + heatNumber.format(heat.tank_max_kwh) + " kWh Kapazität";
}

async function refresh() {
  const response = await fetch("/status");
  if (!response.ok) throw Error("Anzeige nicht erreichbar.");
  const data = await response.json();
  const done = data.job?.next ?? 0;
  const rejects = data.job?.rejects ?? 0;
  get("site").textContent = data.site;
  let state = statusLabels[data.state];
  if (!data.control && data.state === "bereit") state = "Wartet auf das Haus";
  if (data.heat.scheduled_pause) state = "Prüfung pausiert · Router gibt keine Rechenzeit frei";
  get("state").textContent = state;
  get("count").textContent = done + " / " + data.total;
  const percent = Math.round(100 * done / data.total);
  get("progress").setAttribute("aria-valuemax", data.total);
  get("progress").setAttribute("aria-valuenow", done);
  get("progress-fill").style.width = percent + "%";
  get("percent").textContent = percent + " %";
  get("rejects").textContent = rejects;
  get("passed").textContent = done - rejects;
  showRoute(data, done);
  showHeat(data.heat);
  get("start").hidden = !data.control || data.state !== "bereit";
  get("move").hidden = !data.control || data.state !== "Übergabe offen";
  get("move").disabled = requestActive || done === 0;
  get("start").disabled = requestActive;
  get("start").onclick = () => send("/start", data.csrf);
  get("move").onclick = () => send("/move", data.csrf);
  const running = data.state === "rechnet" && !data.heat.scheduled_pause;
  if (running !== isRunning) {
    isRunning = running;
    schedulePaint();
  }
  draw(data.frame);
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
    isRunning = false;
    schedulePaint();
    get("state").textContent = "Verbindung unterbrochen";
    get("start").disabled = get("move").disabled = true;
  } finally {
    setTimeout(poll, 350);
  }
}
poll();
