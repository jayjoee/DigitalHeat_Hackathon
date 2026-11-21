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
  bereit: "Ready to start",
  rechnet: "Inspection in progress",
  "Übergabe läuft": "House paused · sending checkpoint",
  "Übergabe offen": "Awaiting confirmation",
  übergeben: "House paused · sports pool inspecting",
  zurückgegeben: "Sports pool paused · returned to house",
  fertig: "Inspection complete",
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
  get("image-title").textContent = "Pack " + (frame.index + 1);
  setVerdict("Displaying inspection image", "scan", "The markers show which pockets passed inspection.");
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
        context.fillText("MISSING", x * sx, (y + 20) * sy);
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
      const note = filled + " of " + activeFrame.boxes.length + " pockets filled";
      setVerdict(missing.length ? "Rejected" : "Complete",
        missing.length ? "reject" : "pass",
        missing.length ? note + " · Missing from " + (missing.length === 1 ? "pocket " : "pockets ") +
          missing.join(", ") : note);
    }
  }
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
    handoff = "House needs heat again · resuming at pack " + data.return_at;
  } else if (data.state === "übergeben") {
    handoff = "The house draws heat from storage while the sports pool computes.";
  } else if (data.state === "Übergabe läuft") {
    handoff = "Tank full · checkpoint after pack " + done + " is being sent.";
  } else if (data.state === "Übergabe offen") {
    handoff = "The house is paused. You can resend the same checkpoint.";
  } else if (data.resumed_after > 0) {
    handoff = "Received from house · starting at pack " + (data.resumed_after + 1);
  } else if (!data.control) {
    handoff = "Waiting for the checkpoint from the house.";
  } else if (data.state === "rechnet") {
    handoff = "The sports pool takes over when the house tank fills.";
  }
  get("handoff").textContent = handoff;
  const local = data.local_ranges.reduce((count, [first, last]) => count + last - first + 1, 0);
  const ranges = data.local_ranges.map(([first, last]) => first === last ? String(first) : first + "–" + last);
  get("recent").textContent = local
    ? "Inspected here · " + local + (local === 1 ? " pack" : " packs") + " (no. " + ranges.join(", ") + ")"
    : "Inspected here · no packs yet";
}

const heatNumber = new Intl.NumberFormat("en-GB", {maximumFractionDigits: 2});

function showHeat(heat) {
  get("heat-time").textContent = heat.time.slice(11, 16);
  get("outdoor").textContent = heatNumber.format(heat.outside_c) + " °C outdoors";
  get("heat-power").textContent = heatNumber.format(heat.heat_kw) + " kW";
  get("heat-forward").textContent = heat.forward_c == null ? "–" : heat.forward_c + " °C";
  get("heat-room-target").textContent = heatNumber.format(heat.room_target_c) + " °C";
  get("heat-tank").textContent = heatNumber.format(heat.tank_kwh) + " kWh";
  get("tank-capacity").textContent = "of " + heatNumber.format(heat.tank_max_kwh) + " kWh capacity";
}

async function refresh() {
  const response = await fetch("/status");
  if (!response.ok) throw Error("Screen is unavailable.");
  const data = await response.json();
  const done = data.job?.next ?? 0;
  const rejects = data.job?.rejects ?? 0;
  get("site").textContent = data.site;
  let state = statusLabels[data.state];
  if (!data.control && data.state === "bereit") state = "Waiting for the house";
  if (data.heat.scheduled_pause) state = "Inspection paused · router has paused compute";
  if (data.sync_pending) state = "House paused · waiting for the sports pool connection";
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
    get("state").textContent = "Connection lost";
    get("start").disabled = get("move").disabled = true;
  } finally {
    setTimeout(poll, 350);
  }
}
poll();
