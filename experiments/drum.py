"""
drum.py - the optomotor drum on the new stack (Drum world + single-fly Episode).

    uv run python experiments/drum.py --seed 0 --out world/drum_s0.npz [--model flow/0000/000] [--wsyn 0.275] [--deterministic]

the drum turns (still 2 s, left 30 deg/s 4 s, still 1 s, right 30 deg/s 4 s, still 1 s); the fly turns in
place from his own DNa02 (right minus left, fixed rest offset subtracted, EMA 3 chunks, 3 deg per net
spike, clipped 12 deg per chunk). the score is his heading rate in each phase of the programme:
following = the drum's sign in both moving phases. this replaces world/loop.py --mode drum --rest-sub,
whose recorded result on flyvis model 000 was following both ways (docs/SEAM.md "he moves").
"""
import sys, argparse, json, numpy as np
sys.path.insert(0, "seam"); sys.path.insert(0, "ref/flybrain/scripts"); sys.path.insert(0, "world"); sys.path.insert(0, "src")
ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); ap.add_argument("--seed", type=int, default=0); ap.add_argument("--seconds", type=float, default=12.0)
ap.add_argument("--model", default="flow/0000/000"); ap.add_argument("--gain", type=float, default=3.0); ap.add_argument("--drive-gain", type=float, default=150.0)
ap.add_argument("--wsyn", type=float, default=0.275); ap.add_argument("--deterministic", action="store_true"); ap.add_argument("--rest-chunks", type=int, default=20); ap.add_argument("--steer", default="fixed", help="fixed: one standing DNa02 offset subtracted (the record); running: per-side running baseline, tau 2 s (vision brief)"); ap.add_argument("--tau", type=float, default=20.0); args = ap.parse_args()
from omma import Eye
from flysim import Params
from fastlif import FastFlyBrain
from fly_afterlife.frontend import FlyvisFrontEnd
from fly_afterlife.receptors import Registry, ReceptorClass, Scaled
from fly_afterlife.body import Body
from fly_afterlife.world import Drum
from fly_afterlife.effectors import Steering, RunningBaselineSteering, dna02_rest_offset
from fly_afterlife.episode import Episode
fps, CH = 100, 10
eye = Eye("seam/eye_geom.npz"); fe = FlyvisFrontEnd(args.model, fps=fps, chunk=CH, deterministic=args.deterministic)
# ---- the brain, driven at T4/T5 through the seam
b = FastFlyBrain("brain_whole.npz", seed=args.seed, params=Params(mv_per_synapse=args.wsyn)); ty = b.type.astype(str); ns = b.side.astype(str)
groups = fe.groups(b)
b.driven[:] = False
for cl in b.SENSORY_CLASSES: b.driven[b.cls == cl] = True
for t, (idx, _) in groups.items(): b.driven[idx] = True
b._driven_idx = np.flatnonzero(b.driven); b.reset(); b.drive_hz[:] = 0; b.g[:] = 0; b.refrac[:] = 0; SPF = int(round(1000 / fps / b.p.dt))
RM = {}
for name, sel in [("DNa02", ty == "DNa02"), ("HS", np.char.startswith(ty, "HS")), ("legMN", b.sc == "vnc_motor"), ("DN", b.sc == "descending_neuron"), ("pIP10", ty == "pIP10")]:
    for s in "LR": RM[f"{name}_{s}"] = np.flatnonzero(sel & (ns == s))
    RM[name] = np.flatnonzero(sel)
REG = Registry()
for (t, s), (idx, hx) in groups.items():
    REG.add(ReceptorClass(f"T4T5_{t}_{s}", idx, Scaled(args.drive_gain), (lambda st, t=t, s=s, hx=hx: (st["a"][(s, t)][st["f"]] - st["rest"][(s, t)])[hx]), source="seam v2"))
# ---- world and body
drum = Drum(); m = Body("him", 0.0, 0.0, 0.0, 0.08, v=0.0)
def render_chunk(): return np.stack([eye.render(drum.scene([]), pos=(m.x, m.y, 0.5), heading_deg=m.h) for _ in range(CH)])
# ---- calibration: common rest, settle, DNa02 rest offset with vision on (the fixed offset the wheel subtracts)
rest = fe.rest(render_chunk)
for _ in range(500): b.step()
def drive_frame(a, f):
    for (t, s), (idx, hx) in groups.items(): b.drive_hz[idx] = args.drive_gain * np.clip((a[(s, t)][f] - rest[(s, t)])[hx], 0, 1)
rest_net = dna02_rest_offset(b, RM, drive_frame, lambda: fe.chunk(render_chunk()), CH, SPF, chunks=args.rest_chunks); print(f"DNa02 rest offset (R-L per chunk) {rest_net:+.2f}")
class Still:
    def step(self, cnt): return 0.0
steer = Steering(gain=args.gain, rest_net=rest_net, leg_gain=0.0) if args.steer == "fixed" else RunningBaselineSteering(gain=args.gain, leg_gain=0.0, tau=args.tau)
# ---- run
ep = Episode(fps=fps, chunk=CH, eye=eye, room=drum, him=m, her=None, brains=(b, None), readouts=(RM, {}), registries=(REG, Registry()), front_end=fe.chunk, rest=rest, effectors=(steer, Still(), None, None), log_every=20)
ep.run(args.seconds)
# drum phase per frame, as the Drum computed it
ph = []; p_ = 0.0; d2 = Drum()
for fr in range(len(ep.POSE)): p_ += d2.rate(fr / fps) / fps; ph.append(p_)
ep.save(args.out, extra=dict(mode="drum", drum_period=drum.period_deg, drum_lo=drum.lo, drum_hi=drum.hi, drum_half_height=drum.half_height_deg, drum_phase=np.array(ph, np.float32)))
# ---- score: heading rate per programme phase (deg/s, + = left), drum rate alongside
hd = np.array([p[2] for p in ep.POSE]); t_edges = np.cumsum([0] + [s for s, _ in drum.programme]); rows = []
for (sec, rate), t0_, t1_ in zip(drum.programme, t_edges[:-1], t_edges[1:]):
    i0, i1 = int(t0_ * fps), min(int(t1_ * fps), len(hd) - 1); hr = (hd[i1] - hd[i0]) / max((i1 - i0) / fps, 1e-9); rows.append(dict(t0=float(t0_), t1=float(t1_), drum=rate, heading_rate=float(hr)))
    print(f"  {t0_:4.0f}-{t1_:4.0f} s  drum {rate:+5.0f} deg/s   heading {hr:+7.1f} deg/s")
moving = [r for r in rows if r["drum"] != 0]; follows = all(np.sign(r["heading_rate"]) == np.sign(r["drum"]) for r in moving)
print("follows both ways:", follows); json.dump(dict(rows=rows, follows=follows, rest_net=rest_net, seed=args.seed, model=args.model, wsyn=args.wsyn, steer=args.steer, tau=args.tau), open(args.out.replace(".npz", ".json"), "w"), indent=1)
