"""
replay.py - a local replay viewer whose human view is rendered by HIS raytracer (seam/omma.py), not a second
implementation. serves one episode npz on localhost; the page scrubs frames and asks for each human-view frame
as it needs it (0.5 ms per frame through the compiled kernel).

    uv run python world/replay.py world/garden/solo_s3.npz [--port 8765] [--fov 150] [--size 640x320]

what it shows: the human view (pinhole camera at his eye, same primitives, same luminance, same clipping), his
retina (the saved luminance, as in the artifact viewer), the map with the world's colour texture where there is
one, and the neural traces. the JavaScript raytracer in viewer_template.html is retired for anything but the plain
room; this is the reference view.
"""
import sys, io, json, argparse, base64, threading
import numpy as np
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
sys.path.insert(0, "seam"); sys.path.insert(0, "src")
from omma import Scene

ap = argparse.ArgumentParser(); ap.add_argument("npz"); ap.add_argument("--port", type=int, default=8765); ap.add_argument("--fov", type=float, default=150.0); ap.add_argument("--size", default="640x320"); args = ap.parse_args()
W, H = (int(v) for v in args.size.split("x"))
E = np.load(args.npz, allow_pickle=True); pose = E["pose"]; pose2 = E["pose2"] if "pose2" in E.files else None; lum = E["lum"]; fps = int(E["fps"]); n = len(pose)
world = str(E["world"]) if "world" in E.files else "room"
her_r = float(E["her_r"]) if "her_r" in E.files else 0.12; her_alb = float(E["her_albedo"]) if "her_albedo" in E.files else 0.1
FLY_W = np.array([0.20, 0.70, 0.10])

def scene_at(i):
    """rebuild the Scene for frame i from what the episode saved (the same call the eye made)."""
    sph = [(np.array([pose2[i][0], pose2[i][1], 0.5]), her_r, her_alb)] if pose2 is not None else []
    if world == "garden":
        rgb = E["floor_rgb"].astype(np.float32) / 255.0; tex = (rgb @ FLY_W).astype(np.float32); half = float(E["floor_half"])
        st = E["stone"]; fr = E["fruit"]; pu = E["puddle"]; sph += [(np.array([st[0], st[1], st[2]]), float(st[3]), float(st[4])), (np.array([fr[0], fr[1], fr[2]]), float(fr[3]), float(fr[4]))]
        return Scene(sky=0.85, ground=0.35, spheres=sph, pillars=[tuple(map(float, g)) for g in E["grass"]], walls=dict(half=half, height=0.3, albedo=0.5), floor=dict(tex=tex, half=half),
                     discs=[tuple(map(float, l)) for l in E["leaves"]] + [tuple(map(float, pu))], sun=dict(dir=(0.6, 0.3, 0.74), boost=0.3, k=10))
    walls = E["walls"] if "walls" in E.files else None; posts = E["objects"] if "objects" in E.files else np.zeros((0, 4))
    return Scene(sky=float(E["sky"]), ground=float(E["ground"]), spheres=sph, pillars=[tuple(map(float, p)) for p in posts], walls=(dict(half=float(walls[0]), height=float(walls[1]), albedo=float(walls[2])) if walls is not None else None), pillar_height=float(E["pillar_height"]) if "pillar_height" in E.files else 1.5)

fov = np.radians(args.fov); fx = np.tan(fov / 2); fy = fx * H / W
u = (np.arange(W) + 0.5) / W * 2 - 1; v = 1 - (np.arange(H) + 0.5) / H * 2; U, V = np.meshgrid(u, v)
RAYS0 = np.stack([np.ones_like(U), -U * fx, V * fy], -1).reshape(-1, 3); RAYS0 /= np.linalg.norm(RAYS0, axis=1, keepdims=True)
_cache = {}; _lock = threading.Lock()
def render(i):
    if i in _cache: return _cache[i]
    with _lock:
        if i in _cache: return _cache[i]
        return _render(i)
def _render(i):
    x, y, h = pose[i]; hr = np.radians(h); R = np.array([[np.cos(hr), -np.sin(hr), 0], [np.sin(hr), np.cos(hr), 0], [0, 0, 1]])
    img = scene_at(i).shade(np.array([x, y, 0.5]), RAYS0 @ R.T).reshape(H, W)
    out = png((np.clip(img, 0, 1) * 255).astype(np.uint8)); _cache[i] = out
    return out

def png(gray):
    import zlib, struct
    raw = b"".join(b"\x00" + row.tobytes() for row in gray)
    def chunk(t, d): return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xffffffff)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", gray.shape[1], gray.shape[0], 8, 0, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(raw, 6)) + chunk(b"IEND", b"")

az = np.degrees(np.arctan2(E["az"], 1)) if False else E["az"]; el = E["el"]
meta = dict(n=n, fps=fps, world=world, pose=pose.tolist(), pose2=(pose2.tolist() if pose2 is not None else None), az=az.tolist(), el=el.tolist(), side=[str(s) for s in E["side"]],
            touch=(E["touch"].tolist() if "touch" in E.files else None), touch_kind=(E["touch_kind"].tolist() if "touch_kind" in E.files else None),
            objects=(E["objects"].tolist() if "objects" in E.files else []), walls=(E["walls"].tolist() if "walls" in E.files else None), W=W, H=H,
            traces={k[2:]: E[k][::max(1, n // 2000)].astype(float).tolist() for k in E.files if k.startswith("n_m_") and k[4:] in ("DNa02_L", "DNa02_R", "legMN", "pC1", "pIP10", "DN_L", "DN_R", "HS_L", "HS_R")},
            v_m=E["v_m"][::max(1, n // 2000)].astype(float).tolist() if "v_m" in E.files else None)
if world == "garden":
    meta.update(garden=dict(half=float(E["floor_half"]), grass=E["grass"].tolist(), leaves=E["leaves"].tolist(), stone=E["stone"].tolist(), fruit=E["fruit"].tolist(), puddle=E["puddle"].tolist(), sunspot=E["sunspot"].tolist(), wind=E["wind"].tolist()))
    rgb = E["floor_rgb"]; raw = b"".join(b"\x00" + row.tobytes() for row in rgb)
    import zlib, struct
    def chunk(t, d): return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xffffffff)
    meta["floor_png"] = "data:image/png;base64," + base64.b64encode(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", rgb.shape[1], rgb.shape[0], 8, 2, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(raw, 6)) + chunk(b"IEND", b"")).decode()
LUM = (np.clip(lum, 0, 1) * 255).astype(np.uint8) if lum.dtype != np.uint8 else lum

PAGE = """<!doctype html><meta charset=utf-8><title>replay</title>
<style>body{margin:0;background:#0b0e14;color:#d8dee9;font:14px system-ui;padding:12px}.row{display:flex;gap:12px;flex-wrap:wrap}canvas{background:#000;border-radius:4px}h2{font:600 13px system-ui;margin:8px 0 4px;color:#9aa3b2}input[type=range]{width:100%}.legend{display:flex;gap:10px;flex-wrap:wrap;font-size:12px;color:#9aa3b2;margin:4px 0}.legend i{display:inline-block;width:11px;height:11px;border-radius:50%;vertical-align:-1px;margin-right:4px}button{font:500 13px system-ui;background:#151a24;color:#d8dee9;border:1px solid #2a3140;border-radius:4px;padding:4px 10px;cursor:pointer}</style>
<div class=row><div><h2>human view: his raytracer, pinhole __FOV__ deg</h2><img id=hv width=__W__ height=__H__ style="border-radius:4px;background:#000"></div>
<div><h2>his retina (left of fly = left of panel)</h2><canvas id=ret width=560 height=280></canvas></div></div>
<div class=row><div><h2>map</h2><canvas id=map width=420 height=420></canvas><div class=legend id=legend></div></div><div style="flex:1;min-width:320px"><h2>traces (spikes per chunk, each scaled to its own max)</h2><canvas id=tr width=700 height=260></canvas></div></div>
<input id=s type=range min=0 max=__N1__ value=0><div id=info></div><button id=play>play</button> <button id=slower>slower</button> <button id=faster>faster</button> <span id=speed></span>
<script>
const M = __META__; const $ = id => document.getElementById(id); let f = 0, playing = false, stride = 3;
const az = M.az, el = M.el; const rc = $('ret').getContext('2d'), mc = $('map').getContext('2d'), tc = $('tr').getContext('2d');
let floorImg = null; if (M.floor_png) { floorImg = new Image(); floorImg.src = M.floor_png; }
const half = M.garden ? M.garden.half : (M.walls ? M.walls[0] : 2.5); const S = 420 / (2 * half + 0.4); const W2 = (x, y) => [210 + x * S, 210 - y * S];
// ---- retina: precomputed pixel positions, painted into an ImageData (one putImageData per frame)
const RW = 560, RH = 280; const rimg = rc.createImageData(RW, RH); const rpos = az.map((a, k) => [Math.round(280 - a / 190 * 280), Math.round(140 - el[k] / 95 * 140)]);
function paintRetina(l) { rimg.data.fill(0); for (let i = 3; i < rimg.data.length; i += 4) rimg.data[i] = 255; for (let k = 0; k < l.length; k++) { const [x, y] = rpos[k]; for (let dy = -1; dy <= 1; dy++) for (let dx = -1; dx <= 1; dx++) { const xx = x + dx, yy = y + dy; if (xx < 0 || yy < 0 || xx >= RW || yy >= RH) continue; const o = (yy * RW + xx) * 4; rimg.data[o] = rimg.data[o + 1] = rimg.data[o + 2] = l[k]; } } rc.putImageData(rimg, 0, 0); }
// ---- map: the static world on one offscreen canvas, the path on another that only grows
const base = document.createElement('canvas'); base.width = base.height = 420; const bc = base.getContext('2d');
const pathc = document.createElement('canvas'); pathc.width = pathc.height = 420; const pc = pathc.getContext('2d'); let pathUpTo = 0;
function drawBase() { bc.fillStyle = '#0b0e14'; bc.fillRect(0, 0, 420, 420); const [a, b] = W2(-half, half), [c, d] = W2(half, -half);
  if (floorImg && floorImg.complete && floorImg.naturalWidth) bc.drawImage(floorImg, a, b, c - a, d - b); bc.strokeStyle = 'rgba(200,190,170,.7)'; bc.strokeRect(a, b, c - a, d - b);
  if (M.garden) { const g = M.garden; for (const [x, y, z, r] of g.leaves) { const [px, py] = W2(x, y); bc.fillStyle = 'rgba(60,120,40,.35)'; bc.beginPath(); bc.arc(px, py, r * S, 0, 7); bc.fill(); }
    const [sx, sy] = W2(g.sunspot[0], g.sunspot[1]); bc.fillStyle = 'rgba(255,208,112,.25)'; bc.beginPath(); bc.arc(sx, sy, g.sunspot[2] * S, 0, 7); bc.fill();
    for (const [x, y, r] of g.grass) { const [px, py] = W2(x, y); bc.fillStyle = '#2a5a1a'; bc.beginPath(); bc.arc(px, py, 3, 0, 7); bc.fill(); }
    for (const [o, col] of [[g.stone, '#a09a90'], [g.fruit, '#9a1a1a'], [g.puddle, 'rgba(51,68,102,.85)']]) { const [px, py] = W2(o[0], o[1]); bc.fillStyle = col; bc.beginPath(); bc.arc(px, py, o[3] * S, 0, 7); bc.fill(); }
    const [wx, wy] = W2(-half + 0.4, half - 0.4); bc.strokeStyle = '#fff'; bc.beginPath(); bc.moveTo(wx, wy); bc.lineTo(wx + g.wind[0] * 30, wy - g.wind[1] * 30); bc.stroke(); bc.fillStyle = '#fff'; bc.fillText('wind', wx + 4, wy + 14); }
  else for (const o of M.objects) { const [px, py] = W2(o[0], o[1]); bc.fillStyle = o[3] > 0.5 ? '#f2efe6' : '#2a2f3a'; bc.beginPath(); bc.arc(px, py, o[2] * S, 0, 7); bc.fill(); } }
function extendPath(i) { if (i < pathUpTo) { pc.clearRect(0, 0, 420, 420); pathUpTo = 0; } pc.strokeStyle = 'rgba(226,166,59,.7)'; pc.lineWidth = 1.2; pc.beginPath(); const [sx, sy] = W2(M.pose[pathUpTo][0], M.pose[pathUpTo][1]); pc.moveTo(sx, sy); for (let k = pathUpTo + 1; k <= i; k++) { const [px, py] = W2(M.pose[k][0], M.pose[k][1]); pc.lineTo(px, py); } pc.stroke(); pathUpTo = i; }
function drawMap(i) { mc.drawImage(base, 0, 0); extendPath(i); mc.drawImage(pathc, 0, 0);
  const [hx, hy] = W2(M.pose[i][0], M.pose[i][1]); mc.fillStyle = '#e2a63b'; mc.beginPath(); mc.arc(hx, hy, 5, 0, 7); mc.fill(); const hr = M.pose[i][2] * Math.PI / 180; mc.strokeStyle = '#e2a63b'; mc.beginPath(); mc.moveTo(hx, hy); mc.lineTo(hx + 14 * Math.cos(hr), hy - 14 * Math.sin(hr)); mc.stroke();
  if (M.pose2) { const [qx, qy] = W2(M.pose2[i][0], M.pose2[i][1]); mc.fillStyle = '#e07a9a'; mc.beginPath(); mc.arc(qx, qy, 5, 0, 7); mc.fill(); }
  if (M.touch && M.touch[i]) { mc.strokeStyle = (M.touch_kind && M.touch_kind[i] === 2) ? '#e07a9a' : 'rgba(154,163,178,.9)'; mc.lineWidth = 2; mc.beginPath(); mc.arc(hx, hy, 9, 0, 7); mc.stroke(); mc.lineWidth = 1; } }
// ---- traces: drawn once; only the playhead moves
const trace = document.createElement('canvas'); trace.width = 700; trace.height = 260; const trc = trace.getContext('2d'); const keys = Object.keys(M.traces); const step = Math.max(1, Math.floor(M.n / 2000));
(function () { trc.fillStyle = '#0b0e14'; trc.fillRect(0, 0, 700, 260); const cols = ['#e2a63b', '#7ab8ff', '#9be29b', '#e07a9a', '#c9a0ff', '#ffd070', '#7fd0d0', '#ff9e7a', '#aaa']; const n = keys.length;
  keys.forEach((k, j) => { const v = M.traces[k]; const mx = Math.max(1, ...v); const y0 = j * (260 / n), hgt = 260 / n - 4; trc.strokeStyle = cols[j % cols.length]; trc.beginPath(); v.forEach((val, x) => { const px = x / v.length * 700, py = y0 + hgt - val / mx * hgt; x ? trc.lineTo(px, py) : trc.moveTo(px, py); }); trc.stroke(); trc.fillStyle = cols[j % cols.length]; trc.fillText(k + ' (max ' + mx + ')', 4, y0 + 11); }); })();
function drawTraces(i) { tc.drawImage(trace, 0, 0); const px = (i / step) / Math.max(1, Math.floor(M.n / step)) * 700; tc.strokeStyle = '#fff'; tc.beginPath(); tc.moveTo(px, 0); tc.lineTo(px, 260); tc.stroke(); }
// ---- frames: prefetch ahead
const pre = new Map(); function prefetch(i) { for (let k = i; k < Math.min(M.n, i + 12 * stride); k += stride) if (!pre.has(k)) { const im = new Image(); im.src = '/frame/' + k; pre.set(k, im); if (pre.size > 200) pre.delete(pre.keys().next().value); } }
let RET = null; fetch('/retina_all').then(r => r.arrayBuffer()).then(b => { RET = new Uint8Array(b); show(f); });
async function show(i) { f = i; const im = pre.get(i); $('hv').src = im ? im.src : '/frame/' + i; prefetch(i + stride); if (RET) paintRetina(RET.subarray(i * az.length, (i + 1) * az.length)); else { const r = await fetch('/retina/' + i); paintRetina(new Uint8Array(await r.arrayBuffer())); }
  drawMap(i); drawTraces(i); $('s').value = i; $('info').textContent = `frame ${i} / ${M.n}  t = ${(i / M.fps).toFixed(2)} s  heading ${M.pose[i][2].toFixed(0)} deg`; }
$('legend').innerHTML = (M.garden ? '<span><i style="background:rgba(60,120,40,.7)"></i>leaf overhead (shade beneath: darker, 3 C cooler)</span><span><i style="background:rgba(255,208,112,.6)"></i>sun patch (+6 C)</span><span><i style="background:#2a5a1a"></i>grass stalk</span><span><i style="background:#a09a90"></i>stone</span><span><i style="background:#9a1a1a"></i>fruit (odour plume downwind, sugar on contact)</span><span><i style="background:rgba(51,68,102,.9)"></i>puddle (humid, cooler, water)</span><span>white arrow: wind</span>' : '<span><i style="background:#f2efe6;border:1px solid #666"></i>pillar</span>') + '<span><i style="background:#e2a63b"></i>him (line = heading)</span>' + (M.pose2 ? '<span><i style="background:#e07a9a"></i>her</span>' : '') + '<span><i style="border:2px solid rgba(154,163,178,.9)"></i>touching a wall, rim, stalk or stone</span><span><i style="border:2px solid #e07a9a"></i>touching her</span>';
$('s').oninput = e => show(+e.target.value); $('speed').textContent = 'x' + stride;
$('play').onclick = () => { playing = !playing; $('play').textContent = playing ? 'pause' : 'play'; (async function loop() { while (playing && f < M.n - stride) { const t0 = performance.now(); await show(f + stride); const dt = performance.now() - t0; await new Promise(r => setTimeout(r, Math.max(0, 1000 / M.fps * stride - dt))); } })(); };
$('slower').onclick = () => { stride = Math.max(1, stride - 1); $('speed').textContent = 'x' + stride; }; $('faster').onclick = () => { stride = Math.min(30, stride + 1); $('speed').textContent = 'x' + stride; };
(floorImg ? new Promise(r => { floorImg.onload = r; if (floorImg.complete) r(); }) : Promise.resolve()).then(() => { drawBase(); show(0); });
</script>"""

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_GET(self):
        p = self.path
        if p.startswith("/frame/"): body = render(int(p[7:])); ct = "image/png"
        elif p.startswith("/retina/"): body = LUM[int(p[8:])].tobytes(); ct = "application/octet-stream"
        elif p == "/retina_all": body = LUM.tobytes(); ct = "application/octet-stream"
        else: body = PAGE.replace("__META__", json.dumps(meta)).replace("__W__", str(W)).replace("__H__", str(H)).replace("__FOV__", str(int(args.fov))).replace("__N1__", str(n - 1)).encode(); ct = "text/html; charset=utf-8"
        try:
            self.send_response(200); self.send_header("Content-Type", ct); self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError): pass   # the browser cancelled a prefetch

print(f"replay: {args.npz} ({n} frames, {world}) at http://localhost:{args.port}/   (ctrl-c to stop; frames pre-render in the background)"); render(0)
def prerender():
    for i in range(0, n, 1):
        if i not in _cache: render(i)
threading.Thread(target=prerender, daemon=True).start()
ThreadingHTTPServer(("127.0.0.1", args.port), Handler).serve_forever()
