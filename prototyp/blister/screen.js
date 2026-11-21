const get = id => document.getElementById(id);
const canvas = get("frame");
const context = canvas.getContext("2d");
const raster = document.createElement("canvas");
raster.width = 240;
raster.height = 144;
const rasterContext = raster.getContext("2d");
let previousFrame;
let requestActive = false;

function draw(frame) {
  if (!frame || previousFrame === frame.index) return;
  previousFrame = frame.index;
  const bytes = atob(frame.pixels);
  const image = rasterContext.createImageData(raster.width, raster.height);
  for (let i = 0; i < bytes.length; i++) {
    const level = bytes.charCodeAt(i);
    image.data.set([level, level, level, 255], i * 4);
  }
  rasterContext.putImageData(image, 0, 0);
  context.drawImage(raster, 0, 0, canvas.width, canvas.height);
  context.lineWidth = 3;
  for (const [x, y, missing] of frame.boxes) {
    context.strokeStyle = missing ? "#ff7267" : "#8ae8ba";
    context.strokeRect(2 * x - 43, 2 * y - 43, 86, 86);
  }
  get("image-note").textContent = "Bild " + (frame.index + 1) +
    (frame.boxes.some(box => box[2]) ? " · Tablette fehlt" : " · Vollständig");
}

async function refresh() {
  const response = await fetch("/status");
  if (!response.ok) throw Error("Anzeige nicht erreichbar.");
  const data = await response.json();
  const done = data.job?.next ?? 0;
  get("site").textContent = data.site;
  get("state").textContent = data.state;
  get("count").textContent = done + " / " + data.total;
  get("progress").max = data.total;
  get("progress").value = done;
  get("rejects").textContent = (data.job?.rejects ?? 0) + " Packungen beanstandet";
  get("recent").textContent = data.recent.length ? "Hier geprüft · " + data.recent.join(", ") : "";
  get("start").hidden = !data.control || data.state !== "bereit";
  get("move").hidden = !data.control || !["rechnet", "Übergabe offen"].includes(data.state);
  get("move").disabled = requestActive || done === 0;
  get("start").disabled = requestActive;
  get("start").onclick = () => send("/start", data.csrf);
  get("move").onclick = () => send("/move", data.csrf);
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
    get("state").textContent = "Verbindung unterbrochen";
    get("start").disabled = get("move").disabled = true;
  } finally {
    setTimeout(poll, 350);
  }
}
poll();
