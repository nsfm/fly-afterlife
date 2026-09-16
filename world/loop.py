"""
loop.py - the closed loop, generalised. the fly's DNa02 turn him; the world re-renders from where he is.

    uv run python world/loop.py --mode drum|bar|walk|blind --seed 0 --seconds 20 --out world/x.npz [--bar-az 60]

modes
  drum   striped drum, programme as closedloop.py (regression test)
  bar    one dark vertical bar (15 deg wide, +-30 deg tall, 0.2) on an even 0.6 field, fixed in the
         world at --bar-az deg from his initial heading. fixation = his heading turning to put it ahead.
  walk   the arena of posts (episode.py's world, bright ball too). he walks at 0.3 m/s along his
         heading; DNa02 steers. hits (within radius+0.05 of a post) are logged; he passes through.
  blind  as walk but the retina is held at rest (no visual drive): heading noise only. the control.
every 100 ms chunk: render 10 frames of both retinas -> flyvis per eye (state carried) -> LIF
(v2 seam, common rest from a 1 s warm-up on the first frame) -> DNa02 R-L, EMA 3 chunks ->
yaw = 3 deg/spike (right = right turn) clipped +-12 deg/chunk.
"""
import os, sys, argparse, time, numpy as np, torch
sys.path.insert(0, "seam"); sys.path.insert(0, "ref/flybrain/scripts")
os.environ.setdefault("FLYVIS_ROOT_DIR", "/home/nate/code/fly-afterlife/flyvis_data")
from omma import Eye, Scene
ap = argparse.ArgumentParser(); ap.add_argument("--mode", required=True); ap.add_argument("--out", required=True); ap.add_argument("--seconds", type=float, default=20.0)
ap.add_argument("--model", default="flow/0000/000"); ap.add_argument("--gain", type=float, default=3.0); ap.add_argument("--smooth", type=float, default=3.0)
ap.add_argument("--drive-gain", type=float, default=150.0); ap.add_argument("--seed", type=int, default=0); ap.add_argument("--bar-az", type=float, default=60.0)
ap.add_argument("--speed", type=float, default=0.3); ap.add_argument("--tag", default=""); ap.add_argument("--touch", action="store_true", help="posts are solid: on contact he is held at the surface and the leg bristles on the touched side fire (150 Hz) into the LIF"); ap.add_argument("--body", type=float, default=0.05); ap.add_argument("--rest-sub", action="store_true", help="subtract the DNa02 R-L resting offset measured over a 2 s still-world warm-up (with visual drive) at the wheel"); ap.add_argument("--leg-gain", type=float, default=30.0, help="deg per chunk per unit leg-motor asymmetry (R-L)/(R+L), rest asymmetry subtracted; more left-leg drive = right turn"); ap.add_argument("--world-seed", type=int, default=1); args = ap.parse_args()
fps, CH = 100, 10; g = np.load("seam/eye_geom.npz"); eye = Eye("seam/eye_geom.npz"); rng = np.random.default_rng(args.world_seed)
# ---- world
posts = [(x, y, 0.2, 0.05) for x, y in rng.uniform(-2.5, 2.5, size=(8, 2)) if np.hypot(x + 2.0, y) > 0.8]
objects = np.array(posts + [(1.5, 1.0, 0.25, 1.0)], np.float32) if args.mode in ("walk", "blind") else np.zeros((0, 4), np.float32)
spheres = [(np.array([x, y, 0.5]), r, a) for x, y, r, a in objects]
drum = dict(period_deg=30.0, phase_deg=0.0, lo=0.2, hi=0.8, half_height_deg=30.0)
bar = dict(width_deg=15.0, az_world=args.bar_az, lo=0.2, bg=0.6, half_height_deg=30.0)
def scene_at(t):
    if args.mode == "drum":
        w = 0.0; acc = 0.0
        for sec, rate in [(2, 0), (4, 30), (1, 0), (4, -30), (1, 0)]:
            if t < acc + sec: w = rate; break
            acc += sec
        return Scene(drum=dict(drum, phase_deg=scene_at.phase)), w
    if args.mode == "bar":
        # a bar is a drum with one stripe: emulate with a drum of period 360 whose 'lo' stripe is 15 deg wide -> custom
        return Scene(sky=bar["bg"], ground=bar["bg"], horizon_soft=1e-3, spheres=[], drum=dict(period_deg=360.0, phase_deg=bar["az_world"], lo=bar["lo"], hi=bar["bg"], half_height_deg=bar["half_height_deg"], bar_width=bar["width_deg"])), 0.0
    return Scene(spheres=spheres), 0.0
scene_at.phase = 0.0
# a narrow bar: patch Scene.shade's drum branch to honour bar_width (stripe only within [phase, phase+width])
import omma
_shade = omma.Scene.shade
def shade_bar(self, origin, d):
    if self.drum is not None and "bar_width" in self.drum:
        dr = self.drum; lum = np.full(len(d), dr["hi"], np.float32); az = np.degrees(np.arctan2(d[:, 1], d[:, 0])); elv = np.degrees(np.arcsin(np.clip(d[:, 2], -1, 1)))
        rel = (az - dr["phase_deg"] + 180.0) % 360.0 - 180.0; inbar = (np.abs(rel) < dr["bar_width"] / 2) & (np.abs(elv) < dr["half_height_deg"])
        return np.where(inbar, dr["lo"], lum).astype(np.float32)
    return _shade(self, origin, d)
omma.Scene.shade = shade_bar
# ---- flyvis
import flyvis
from flyvis import NetworkView
net = NetworkView(args.model).init_network(); net.eval()
lattice = sorted({(u, v) for u in range(-15, 16) for v in range(max(-15, -15 - u), min(15, 15 - u) + 1)}); idx_of = {uv: i for i, uv in enumerate(lattice)}
ntype = net.connectome.nodes.type[:].astype(str); types = ["T4a", "T4b", "T4c", "T4d", "T5a", "T5b", "T5c", "T5d"]; tix = {t: np.flatnonzero(ntype == t) for t in types}
eyemap = {}
for s in "LR":
    k = np.flatnonzero(g["side"] == s); v = np.rint(+g["sx"][k]).astype(int); u = np.rint(-g["sy"][k] - v / 2.0).astype(int)
    col = np.array([idx_of.get((int(a), int(b)), -1) for a, b in zip(u, v)]); ok = col >= 0; eyemap[s] = (k[ok], col[ok])
state = {"L": None, "R": None}
def flyvis_chunk(lum_chunk):
    out = {}
    for s in "LR":
        k, col = eyemap[s]; movie = np.full((1, CH, 1, 721), 0.5, np.float32); movie[0, :, 0, col] = lum_chunk[:, k].T
        with torch.no_grad(): st = net.simulate(torch.tensor(movie, device=flyvis.device), dt=1 / fps, initial_state=state[s], as_states=True)
        state[s] = st[-1]; act = torch.stack([x.nodes.activity[0] for x in st]).cpu().numpy()
        for t in types: out[(s, t)] = act[:, tix[t]]
    return out
# ---- LIF
from flysim import FlyBrain
b = FlyBrain("brain_whole.npz", seed=args.seed); ty = b.type.astype(str); ns = b.side.astype(str)
cols = np.load("seam/t4t5_columns.npz"); gkey = {(str(s), int(a), int(h)): i for i, (s, a, h) in enumerate(zip(g["side"], g["hex1"], g["hex2"]))}
gi = np.array([gkey[(str(s), int(a), int(h))] for s, a, h in zip(cols["side"], cols["hex1"], cols["hex2"])])
groups = {}
for s in "LR":
    k, col = eyemap[s]; colmap = dict(zip(k.tolist(), col.tolist()))
    for t in types:
        kk = (cols["type"] == t) & (cols["side"] == s); hx = np.array([colmap.get(int(i), -1) for i in gi[kk]]); ok = hx >= 0; groups[(t, s)] = (cols["idx"][kk][ok], hx[ok])
cls_ = b.cls.astype(str); TACT = {s_: np.flatnonzero((cls_ == "mechanosensory_tactile") & (ns == s_)) for s_ in "LR"}
R = {}
for name, sel in [("HS", np.char.startswith(ty, "HS")), ("DNa02", ty == "DNa02"), ("DNa", np.char.startswith(ty, "DNa")), ("DN", b.sc == "descending_neuron"), ("LPLC2", ty == "LPLC2"), ("GF", ty == "DNp01"), ("legMN", b.sc == "vnc_motor")]:
    for s in "LR": R[f"{name}_{s}"] = np.flatnonzero(sel & (ns == s))
b.driven[:] = False
for cl in b.SENSORY_CLASSES: b.driven[b.cls == cl] = True
for t, (idx, _) in groups.items(): b.driven[idx] = True
b._driven_idx = np.flatnonzero(b.driven); b.reset(); b.drive_hz[:] = 0; b.g[:] = 0; b.refrac[:] = 0; SPF = int(round(1000 / fps / b.p.dt))
# ---- warm-up on the first frame
x, y, heading = (-2.0, 0.0, 0.0) if args.mode in ("walk", "blind") else (0.0, 0.0, 0.0)
def render_frames(n, sc, pos, hd): return np.stack([eye.render(sc, pos=pos, heading_deg=hd) for _ in range(n)])
acc = {}
for c in range(10):
    sc, _ = scene_at(0.0); a = flyvis_chunk(render_frames(CH, sc, (x, y, 0.5), heading))
    if c >= 5:
        for k_, v_ in a.items(): acc.setdefault(k_, []).append(v_)
rest = {k_: np.concatenate(v_).mean(0) for k_, v_ in acc.items()}
for _ in range(500): b.step()
leg_rest = 0.0; rest_net = 0.0
if args.rest_sub:
    sc0, _ = scene_at(0.0); rl = rr = 0; nch = 20
    for c in range(nch):
        a0 = flyvis_chunk(render_frames(CH, sc0, (x, y, 0.5), heading))
        for f in range(CH):
            for (tt, s_), (idx, hx) in groups.items(): b.drive_hz[idx] = args.drive_gain * np.clip((a0[(s_, tt)][f] - rest[(s_, tt)])[hx], 0, 1)
            for _ in range(SPF):
                spk = b.step(); rl += int(spk[R["DNa02_L"]].sum()); rr += int(spk[R["DNa02_R"]].sum())
    rest_net = (rr - rl) / nch; print(f"DNa02 resting offset (R-L per chunk): {rest_net:+.2f}  (L {rl}, R {rr} over {nch} chunks)")
# ---- loop
T = int(args.seconds * fps); LUM, POSE, PHASE, TOUCH = [], [], [], []; log = {k: [] for k in R}; hits = 0; ema = 0.0; t0 = time.time(); bearing = []
for c in range(T // CH):
    t = c * CH / fps; sc, w = scene_at(t); lum = np.zeros((CH, eye.n), np.float32)
    for f in range(CH):
        if args.mode == "drum": scene_at.phase += w / fps; sc = Scene(drum=dict(drum, phase_deg=scene_at.phase))
        lum[f] = eye.render(sc, pos=(x, y, 0.5), heading_deg=heading) if args.mode != "blind" else np.full(eye.n, 0.5, np.float32)
        POSE.append((x, y, heading)); PHASE.append(scene_at.phase if args.mode == "drum" else (bar["az_world"] if args.mode == "bar" else 0.0))
        if args.mode in ("walk", "blind"):
            x += args.speed / fps * np.cos(np.radians(heading)); y += args.speed / fps * np.sin(np.radians(heading))
            touched = None
            for ox, oy, r_, _ in objects:
                dd = np.hypot(x - ox, y - oy)
                if dd < r_ + args.body:
                    hits += 1
                    if args.touch:
                        x, y = ox + (x - ox) / max(dd, 1e-6) * (r_ + args.body), oy + (y - oy) / max(dd, 1e-6) * (r_ + args.body)   # held at the surface
                        brg = (np.degrees(np.arctan2(oy - y, ox - x)) - heading + 180) % 360 - 180
                        touched = "L" if brg > 8 else ("R" if brg < -8 else "B")
                    break
            TOUCH.append(touched)
    LUM.append((np.clip(lum, 0, 1) * 255).astype(np.uint8))
    a = flyvis_chunk(lum) if args.mode != "blind" else None; cnt = {k: 0 for k in R}
    for f in range(CH):
        if a is not None:
            for (tt, s), (idx, hx) in groups.items(): b.drive_hz[idx] = args.drive_gain * np.clip((a[(s, tt)][f] - rest[(s, tt)])[hx], 0, 1)
        if args.touch:
            tch = TOUCH[c * CH + f] if c * CH + f < len(TOUCH) else None
            for s_ in "LR": b.drive_hz[TACT[s_]] = 150.0 if (tch == "B" or tch == s_) else 0.0
        for _ in range(SPF):
            spk = b.step()
            for k, r in R.items(): cnt[k] += int(spk[r].sum())
    net_ = cnt["DNa02_R"] - cnt["DNa02_L"] - rest_net; ema += (net_ - ema) / max(args.smooth, 1.0)
    yaw = float(np.clip(args.gain * ema, -12, 12)) * -1
    if args.touch:
        asym = (cnt["legMN_R"] - cnt["legMN_L"]) / max(cnt["legMN_R"] + cnt["legMN_L"], 1)
        touched_chunk = any(TOUCH[c * CH + f] for f in range(CH) if c * CH + f < len(TOUCH))
        if not touched_chunk: leg_rest += (asym - leg_rest) / 20.0          # running baseline from untouched chunks
        else: yaw += float(np.clip(args.leg_gain * (asym - leg_rest), -12, 12))   # more right-leg drive -> left turn (+heading); only while touching
    heading += yaw
    for k in R: log[k].append(cnt[k])
    if args.mode == "bar": bearing.append(((bar["az_world"] - heading + 180) % 360) - 180)
    if c % 50 == 49: print(f"t={t+0.1:5.1f}s heading {heading:+7.1f}" + (f"  touches L/R/both {TOUCH.count(chr(76))}/{TOUCH.count(chr(82))}/{TOUCH.count(chr(66))}" if args.touch else "") + (f"  bar bearing {bearing[-1]:+6.1f}" if bearing else "") + (f"  pos ({x:+.2f},{y:+.2f}) hits {hits}" if args.mode in ('walk', 'blind') else "") + f"  DNa02 L/R {sum(log['DNa02_L'][-50:])}/{sum(log['DNa02_R'][-50:])}  ({time.time()-t0:.0f}s)", flush=True)
Tn = len(POSE); per_frame = {f"n_{k}": np.repeat(np.array(log[k], np.int16), CH)[:Tn] for k in R}
extra = {}
if args.mode == "drum": extra = dict(drum_period=drum["period_deg"], drum_lo=drum["lo"], drum_hi=drum["hi"], drum_half_height=drum["half_height_deg"], drum_phase=np.array(PHASE, np.float32))
if args.mode == "bar": extra = dict(bar_width=bar["width_deg"], bar_lo=bar["lo"], bar_bg=bar["bg"], bar_half_height=bar["half_height_deg"], bar_az=np.array(PHASE, np.float32), bearing=np.array(bearing, np.float32))
touch_side = np.array([{"L": 1, "R": 2, "B": 3}.get(t_, 0) for t_ in TOUCH], np.int8) if TOUCH else np.zeros(0, np.int8)
np.savez_compressed(args.out, fps=fps, chunk=CH, mode=args.mode, touch=touch_side, lum=np.concatenate(LUM), pose=np.array(POSE, np.float32), objects=objects, fov=150.0, hits=hits,
                    az=np.degrees(np.arctan2(eye.dir0[:, 1], eye.dir0[:, 0])).astype(np.float32), el=np.degrees(np.arcsin(np.clip(eye.dir0[:, 2], -1, 1))).astype(np.float32), side=eye.side,
                    heading_chunk=np.array([p[2] for p in POSE[::CH]]), **per_frame, **{f"ncells_{k}": len(v) for k, v in R.items()}, **extra)
print("wrote", args.out, f"hits={hits}" if args.mode in ("walk", "blind") else "")
