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
from http.server import HTTPServer, BaseHTTPRequestHandler
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
_cache = {}
def render(i):
    if i in _cache: return _cache[i]
    x, y, h = pose[i]; hr = np.radians(h); R = np.array([[np.cos(hr), -np.sin(hr), 0], [np.sin(hr), np.cos(hr), 0], [0, 0, 1]])
    img = scene_at(i).shade(np.array([x, y, 0.5]), RAYS0 @ R.T).reshape(H, W)
    out = (np.clip(img, 0, 1) * 255).astype(np.uint8); _cache[i] = out
    if len(_cache) > 400: _cache.pop(next(iter(_cache)))
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
<style>body{margin:0;background:#0b0e14;color:#d8dee9;font:14px system-ui;padding:12px}.row{display:flex;gap:12px;flex-wrap:wrap}canvas{background:#000;border-radius:4px}#c{width:min(100%,__W__px)}h2{font:600 13px system-ui;margin:8px 0 4px;color:#9aa3b2}input[type=range]{width:100%}</style>
<div class=row><div><h2>human view: his raytracer, pinhole __FOV__ deg</h2><img id=hv width=__W__ height=__H__ style="border-radius:4px;background:#000"></div>
<div><h2>his retina</h2><canvas id=ret width=560 height=280></canvas></div></div>
<div class=row><div><h2>map</h2><canvas id=map width=420 height=420></canvas></div><div style="flex:1;min-width:320px"><h2>traces</h2><canvas id=tr width=700 height=260></canvas></div></div>
<input id=s type=range min=0 max=__N1__ value=0><div id=info></div><button id=play>play</button>
<script>
const M = __META__; const $ = id => document.getElementById(id); let f = 0, playing = false;
const az = M.az, el = M.el, side = M.side; const rc = $('ret').getContext('2d'), mc = $('map').getContext('2d'), tc = $('tr').getContext('2d');
let floorImg = null; if (M.floor_png) { floorImg = new Image(); floorImg.src = M.floor_png; }
const half = M.garden ? M.garden.half : (M.walls ? M.walls[0] : 2.5); const S = 420 / (2 * half + 0.4); const W2 = (x, y) => [210 + x * S, 210 - y * S];
async function show(i) { f = i; $('hv').src = '/frame/' + i; const r = await fetch('/retina/' + i); const l = new Uint8Array(await r.arrayBuffer());
  rc.fillStyle = '#000'; rc.fillRect(0, 0, 560, 280); for (let k = 0; k < l.length; k++) { const x = 280 - az[k] / 190 * 280, y = 140 - el[k] / 95 * 140; rc.fillStyle = `rgb(${l[k]},${l[k]},${l[k]})`; rc.fillRect(x - 1.5, y - 1.5, 3, 3); }
  drawMap(i); drawTraces(i); $('s').value = i; $('info').textContent = `frame ${i} / ${M.n}  t = ${(i / M.fps).toFixed(2)} s  heading ${M.pose[i][2].toFixed(0)}`; }
function drawMap(i) { mc.fillStyle = '#0b0e14'; mc.fillRect(0, 0, 420, 420); const [a, b] = W2(-half, half), [c, d] = W2(half, -half);
  if (floorImg && floorImg.complete) mc.drawImage(floorImg, a, b, c - a, d - b); mc.strokeStyle = 'rgba(200,190,170,.7)'; mc.strokeRect(a, b, c - a, d - b);
  if (M.garden) { const g = M.garden; for (const [x, y, z, r] of g.leaves) { const [px, py] = W2(x, y); mc.fillStyle = 'rgba(60,120,40,.35)'; mc.beginPath(); mc.arc(px, py, r * S, 0, 7); mc.fill(); }
    for (const [x, y, r] of g.grass) { const [px, py] = W2(x, y); mc.fillStyle = '#2a5a1a'; mc.beginPath(); mc.arc(px, py, 3, 0, 7); mc.fill(); }
    for (const [o, col] of [[g.stone, '#a09a90'], [g.fruit, '#9a1a1a'], [g.puddle, 'rgba(51,68,102,.8)']]) { const [px, py] = W2(o[0], o[1]); mc.fillStyle = col; mc.beginPath(); mc.arc(px, py, o[3] * S, 0, 7); mc.fill(); }
    const [sx, sy] = W2(g.sunspot[0], g.sunspot[1]); mc.fillStyle = 'rgba(255,208,112,.25)'; mc.beginPath(); mc.arc(sx, sy, g.sunspot[2] * S, 0, 7); mc.fill(); }
  else for (const o of M.objects) { const [px, py] = W2(o[0], o[1]); mc.fillStyle = o[3] > 0.5 ? '#f2efe6' : '#2a2f3a'; mc.beginPath(); mc.arc(px, py, o[2] * S, 0, 7); mc.fill(); }
  mc.strokeStyle = 'rgba(226,166,59,.6)'; mc.beginPath(); for (let k = 0; k <= i; k += 2) { const [px, py] = W2(M.pose[k][0], M.pose[k][1]); k ? mc.lineTo(px, py) : mc.moveTo(px, py); } mc.stroke();
  const [hx, hy] = W2(M.pose[i][0], M.pose[i][1]); mc.fillStyle = '#e2a63b'; mc.beginPath(); mc.arc(hx, hy, 5, 0, 7); mc.fill(); const hr = M.pose[i][2] * Math.PI / 180; mc.strokeStyle = '#e2a63b'; mc.beginPath(); mc.moveTo(hx, hy); mc.lineTo(hx + 14 * Math.cos(hr), hy - 14 * Math.sin(hr)); mc.stroke();
  if (M.pose2) { const [qx, qy] = W2(M.pose2[i][0], M.pose2[i][1]); mc.fillStyle = '#e07a9a'; mc.beginPath(); mc.arc(qx, qy, 5, 0, 7); mc.fill(); }
  if (M.touch && M.touch[i]) { mc.strokeStyle = (M.touch_kind && M.touch_kind[i] === 2) ? '#e07a9a' : 'rgba(154,163,178,.9)'; mc.lineWidth = 2; mc.beginPath(); mc.arc(hx, hy, 9, 0, 7); mc.stroke(); mc.lineWidth = 1; } }
function drawTraces(i) { tc.fillStyle = '#0b0e14'; tc.fillRect(0, 0, 700, 260); const keys = Object.keys(M.traces); const n = keys.length; const step = Math.max(1, Math.floor(M.n / 2000)); const cols = ['#e2a63b', '#7ab8ff', '#9be29b', '#e07a9a', '#c9a0ff', '#ffd070', '#7fd0d0', '#ff9e7a', '#aaa'];
  keys.forEach((k, j) => { const v = M.traces[k]; const mx = Math.max(1, ...v); const y0 = j * (260 / n), hgt = 260 / n - 4; tc.strokeStyle = cols[j % cols.length]; tc.beginPath(); v.forEach((val, x) => { const px = x / v.length * 700, py = y0 + hgt - val / mx * hgt; x ? tc.lineTo(px, py) : tc.moveTo(px, py); }); tc.stroke(); tc.fillStyle = cols[j % cols.length]; tc.fillText(k + ' (max ' + mx + ')', 4, y0 + 11); });
  const px = (i / step) / Math.max(1, Math.floor(M.n / step)) * 700; tc.strokeStyle = '#fff'; tc.beginPath(); tc.moveTo(px, 0); tc.lineTo(px, 260); tc.stroke(); }
$('s').oninput = e => show(+e.target.value); $('play').onclick = () => { playing = !playing; $('play').textContent = playing ? 'pause' : 'play'; (async function loop() { while (playing && f < M.n - 3) { await show(f + 3); await new Promise(r => setTimeout(r, 30)); } })(); };
show(0);
</script>"""

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_GET(self):
        p = self.path
        if p.startswith("/frame/"): body = png(render(int(p[7:]))); ct = "image/png"
        elif p.startswith("/retina/"): body = LUM[int(p[8:])].tobytes(); ct = "application/octet-stream"
        else: body = PAGE.replace("__META__", json.dumps(meta)).replace("__W__", str(W)).replace("__H__", str(H)).replace("__FOV__", str(int(args.fov))).replace("__N1__", str(n - 1)).encode(); ct = "text/html; charset=utf-8"
        self.send_response(200); self.send_header("Content-Type", ct); self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)

print(f"replay: {args.npz} ({n} frames, {world}) at http://localhost:{args.port}/   (ctrl-c to stop)"); render(0)
HTTPServer(("127.0.0.1", args.port), Handler).serve_forever()
