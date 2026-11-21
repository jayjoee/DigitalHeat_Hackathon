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

function draw(frame) {
  if (!frame || previousFrame === frame.index) return;
  previousFrame = frame.index;
  activeFrame = frame;
  frameStarted = performance.now();
  const bytes = atob(frame.pixels);
  const image = rasterContext.createImageData(raster.width, raster.height);
  for (let i = 0; i < bytes.length; i++) {
    const level = bytes.charCodeAt(i);
    image.data.set([level, level, level, 255], i * 4);
  }
  rasterContext.putImageData(image, 0, 0);
  schedulePaint();
  get("image-note").textContent = "Bild " + (frame.index + 1) +
    (frame.boxes.some(box => box[2]) ? " · Tablette fehlt" : " · Vollständig");
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
      context.strokeStyle = missing ? "#ff7267" : "#8ae8ba";
      context.lineWidth = missing ? 5 : 3;
      context.strokeRect((x - 22) * sx, (y - 22) * sy, 44 * sx, 44 * sy);
      if (missing) {
        context.fillStyle = "#ff7267";
        context.fillRect((x - 22) * sx, (y + 13) * sy, 44 * sx, 9 * sy);
        context.fillStyle = "#201516";
        context.font = "bold 17px system-ui";
        context.textAlign = "center";
        context.fillText("FEHLT", x * sx, (y + 20) * sy);
      }
    }
    if (fraction < 1) schedulePaint();
  }
}

async function refresh() {
  const response = await fetch("/status");
  if (!response.ok) throw Error("Anzeige nicht erreichbar.");
  const data = await response.json();
  const done = data.job?.next ?? 0;
  get("site").textContent = data.site;
  get("state").textContent = data.state;
  get("count").textContent = done + " / " + data.total;
  const percent = Math.round(100 * done / data.total);
  get("progress").setAttribute("aria-valuemax", data.total);
  get("progress").setAttribute("aria-valuenow", done);
  get("progress-fill").style.width = percent + "%";
  get("percent").textContent = percent + " %";
  get("rejects").textContent = (data.job?.rejects ?? 0) + " Packungen beanstandet";
  get("recent").textContent = data.recent.length ? "Hier geprüft · " + data.recent.join(", ") : "";
  get("start").hidden = !data.control || data.state !== "bereit";
  get("move").hidden = !data.control || !["rechnet", "Übergabe offen"].includes(data.state);
  get("move").disabled = requestActive || done === 0;
  get("start").disabled = requestActive;
  get("start").onclick = () => send("/start", data.csrf);
  get("move").onclick = () => send("/move", data.csrf);
  const running = data.state === "rechnet";
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
