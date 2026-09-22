"""cord.py - the headless preparation (docs/TODO.md §Q 4f; docs/WALKING.md): the ventral nerve cord alone (brain_cord.npz, from
scripts/build_cord.py), no eye, no body, no world. the walking command (DNg100, Bidaye 2020's decapitated-fly experiment) driven at
a dose on the cord's own descending neurons, the cord's tonic floor on (the leg proprioceptors under standing load), every leg motor
neuron logged per frame (10 ms) to <out>.cells.npz in the format experiments/gait.py reads. a seventh of the whole fly: the place
to sweep the variables of the leg row (depression, the constant, the dose) before confirming in him.

    uv run python world/cord.py --seconds 30 --walk 100 --std off --out world/cord/ctl.npz
    uv run python experiments/gait.py world/cord/ctl.npz
"""
import os, sys, argparse, time, numpy as np
sys.path.insert(0, "ref/flybrain/scripts"); sys.path.insert(0, "world"); sys.path.insert(0, "src")
from flysim import Params
from fastlif import FastFlyBrain
from fly_afterlife.receptors import Registry, ReceptorClass, Scaled, tonic_floor, select

ap = argparse.ArgumentParser()
ap.add_argument("--out", required=True); ap.add_argument("--seconds", type=float, default=30.0); ap.add_argument("--seed", type=int, default=0)
ap.add_argument("--brain", default="brain_cord.npz")
ap.add_argument("--wsyn-m", type=float, default=0.185, help="mV per synapse (the male default of record)")
ap.add_argument("--noise", type=float, default=0.15, help="membrane noise, mV per step (the default of record)")
ap.add_argument("--integrate", default="exact")
ap.add_argument("--walk", type=float, default=100.0, help="Hz on the walking command's descending neurons (0 = the cord at rest)")
ap.add_argument("--walk-dn", default="DNg100")
ap.add_argument("--std", default="off", help="short-term depression: off | pair (the DNg33 pair, the default of record in the whole fly) | all")
ap.add_argument("--std-u", type=float, default=None, help="override the engine's release fraction u (default: the engine's)")
ap.add_argument("--std-tau", type=float, default=None, help="override the engine's recovery tau, ms")
ap.add_argument("--floor", dest="floor", action="store_true", default=True); ap.add_argument("--no-floor", dest="floor", action="store_false")
ap.add_argument("--leg-load-hz", type=float, default=15.0, help="the floor's rate on the leg proprioceptors (standing load)")
ap.add_argument("--silence", default="", help="comma-separated types whose threshold is put out of reach (no effect on driven cells)")
ap.add_argument("--log-types", default="", help="comma-separated types to log per frame (default: every leg motor neuron type)")
ap.add_argument("--warmup", type=float, default=2.0, help="seconds before the walking command comes on (the cord at rest under the floor)")
args = ap.parse_args()
fps, CH = 100, 10; SPF = 1000 // fps; t0 = time.time()

M = FastFlyBrain(args.brain, seed=args.seed, params=Params(mv_per_synapse=args.wsyn_m, noise=args.noise)); M.integrate = args.integrate
mty = M.type.astype(str); mns = M.side.astype(str)
print(f"{args.brain}: {M.N} cells; engine {type(M).__name__}, {args.integrate}, w {args.wsyn_m} mV, noise {args.noise}")

if args.std != "off":   # the same block as pair.py (09-21)
    _mask = np.ones(M.N, bool) if args.std == "all" else (mty == "DNg33")
    M._std_mask = _mask; M._std_x = np.ones(M.N, np.float32); M.std_on = True
    if args.std_u is not None: M.p.std_u = float(args.std_u)
    if args.std_tau is not None: M.p.std_tau_rec_ms = float(args.std_tau)
    print(f"short-term depression on {int(_mask.sum())} cells ({args.std}); u {M.p.std_u}, tau {M.p.std_tau_rec_ms} ms")

REG = Registry()
if args.walk > 0:
    WALK = np.flatnonzero(((mty == args.walk_dn) | np.char.startswith(mty, args.walk_dn + "_")) & (M.sc.astype(str) == "descending_neuron"))
    REG.add(ReceptorClass(f"walk_{args.walk_dn}", WALK, Scaled(args.walk), lambda st: float(st.get("walk_gain", 1.0)), source="Bidaye 2020: the walking DN driven in a decapitated fly"))
else: WALK = np.zeros(0, np.int64)
_fl = tonic_floor(M, REG) if args.floor else []
for rc in _fl:
    if rc.name == "floor_leg_proprio": rc.transducer.hz = args.leg_load_hz
print(REG.table())

M.driven[:] = False
for cl in M.SENSORY_CLASSES: M.driven[M.cls == cl] = True
if len(_fl): M.driven[np.unique(np.concatenate([rc.cells for rc in _fl]))] = True
if len(WALK): M.driven[WALK] = True
M._driven_idx = np.flatnonzero(M.driven); M.reset()
if args.silence:
    _sil = np.flatnonzero(np.isin(mty, [x for x in args.silence.split(",") if x])); M.v_th[_sil] = np.float32(1e6); print(f"silenced {len(_sil)} cells of {args.silence} (driven cells unaffected)")

if args.log_types: _lt = [x for x in args.log_types.split(",") if x]
else:
    from fly_afterlife.receptors import annotations
    a = annotations(); _lt = sorted(set(a.loc[(a["superclass"] == "vnc_motor") & a["subclass"].isin(["fl", "ml", "hl"]), "type"].dropna().astype(str)))
LC = np.flatnonzero(np.isin(mty, _lt)); print(f"logging {len(LC)} cells of {len(_lt)} types")

n_frames = int(round(args.seconds * fps)); FR = np.zeros((n_frames, len(LC)), np.int16); ALL = np.zeros(n_frames, np.int32)
state = {"walk_gain": 0.0}
for f in range(n_frames):
    t = f / fps; state["walk_gain"] = 1.0 if t >= args.warmup else 0.0
    REG.apply(M, state, t, 1.0 / fps)
    acc = np.zeros(M.N, np.int32)
    for _ in range(SPF): M.step(); acc[M.last_idx] += 1
    FR[f] = acc[LC]; ALL[f] = acc.sum()
    if f % (10 * fps) == 0 and f: print(f"t={t:5.1f}s  cord {ALL[f - 10 * fps:f].mean() * fps / M.N:.2f} Hz/cell  leg MN {FR[f - 10 * fps:f].mean() * fps:.2f} Hz/cell  ({time.time() - t0:.0f}s)")

nc = n_frames // CH; counts = FR[:nc * CH].reshape(nc, CH, -1).sum(1)
os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
np.savez_compressed(args.out.replace(".npz", "") + ".cells.npz", cells=LC, bodyId=M.bodyId[LC], type=mty[LC], side=mns[LC], counts=counts.astype(np.int32),
                    pose_chunk=np.zeros((nc, 3), np.float32), frames=FR, pose_frame=np.zeros((n_frames, 3), np.float32), cord_hz=ALL.astype(np.int32))
np.savez_compressed(args.out, fps=fps, chunk=CH, cord_spikes=ALL, args=np.array(str(vars(args))))
w = FR[int(args.warmup * fps):]; print(f"done in {time.time() - t0:.0f}s: after the warm-up, cord {ALL[int(args.warmup * fps):].mean() * fps / M.N:.2f} Hz/cell, leg MN {w.mean() * fps:.2f} Hz/cell, {int((w.mean(0) * fps > 1).sum())} of {len(LC)} leg MNs above 1 Hz")
print("wrote", args.out.replace(".npz", "") + ".cells.npz")
