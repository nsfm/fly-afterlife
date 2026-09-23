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
ap.add_argument("--dt", type=float, default=1.0, help="the engine tick in ms (1.0 = the record; the membrane is exact at any dt, the events are quantised to it; nate 09-22)")
ap.add_argument("--walk", type=float, default=100.0, help="Hz on the walking command's descending neurons (0 = the cord at rest)")
ap.add_argument("--walk-dn", default="DNg100")
ap.add_argument("--walk-side", default="", help="drive the command's cells on one side only: L | R (the steering test, 09-22)")
ap.add_argument("--std", default="off", help="short-term depression: off | pair (the DNg33 pair, the default of record in the whole fly) | all")
ap.add_argument("--std-u", type=float, default=None, help="override the engine's release fraction u (default: the engine's)")
ap.add_argument("--std-tau", type=float, default=None, help="override the engine's recovery tau, ms")
ap.add_argument("--floor", dest="floor", action="store_true", default=True); ap.add_argument("--no-floor", dest="floor", action="store_false")
ap.add_argument("--leg-load-hz", type=float, default=15.0, help="the floor's rate on the leg proprioceptors (standing load)")
ap.add_argument("--silence", default="", help="comma-separated types whose threshold is put out of reach (no effect on driven cells)")
ap.add_argument("--log-ms", action="store_true", help="also log the logged cells per engine step (1 ms) as ms_counts in <out>.cells.npz (a 25 Hz rhythm is 4 bins at the 10 ms frame)")
ap.add_argument("--log-types", default="", help="comma-separated types to log per frame (default: every leg motor neuron type)")
ap.add_argument("--warmup", type=float, default=2.0, help="seconds before the walking command comes on (the cord at rest under the floor)")
ap.add_argument("--pulse", default="", help="the command with a time course: HZ[:DUTY] square-wave gating of the walking command (e.g. 3:0.5); in life the command is never a steady rate; a diagnostic")
ap.add_argument("--shock", default="", help="the frankenstein arm (nate, 09-22): SECONDS:HZ, every descending neuron driven at HZ for SECONDS after the warm-up, then the command alone; does the jolt leave the cord elsewhere")
ap.add_argument("--graded", default="", help="graded (non-spiking) units: TYPE-PREFIXES:GAIN[:V1], e.g. IN13A,IN13B:0.1 : the named cells never spike; each ms they deliver GAIN x clip(v / V1, 0, 1) of a spike to their targets (V1 default = the threshold, 7 mV). non-spiking local interneurons are the substrate of insect leg pattern generation (Buschges 1995; Bassler & Buschges 1998); which fly hemilineages are graded is not established (E): a sweep, with a random set as the control. 'random:N:GAIN' grades N random cord interneurons")
ap.add_argument("--size-gain", type=float, default=0.0, help="size-scaled excitability, the input-resistance form (the review of 09-22; Pugliese 2026: gain and threshold scaled by cell size were necessary for the rhythm; Azevedo 2020: Rin 150 / 300 / 700 MOhm for fast / intermediate / slow MNs): every synapse onto cell i is scaled by (S_med / S_i)^A, S_i the cell's total input synapses (the size proxy this file has), S_med the median over the cord's neurons; a small cell gets a bigger PSP per synapse. 0 = off (E; sweep A)")
ap.add_argument("--size-thr", type=float, default=0.0, help="size-scaled excitability, the threshold form: v_th_i = 7 mV x (S_i / S_med)^B; a small cell sits closer to threshold (Azevedo 2020: slow MNs rest 20 mV nearer threshold than fast). 0 = off (E; sweep B)")
ap.add_argument("--size-clip", type=float, default=4.0, help="clip on both size factors")
ap.add_argument("--edge-scale", default="", help="scale the synapses among a named set of types: TYPES:FACTOR (e.g. DNg100,IN17A001,INXXX466,IN16B036:1.49 = the published rhythm loop at Pugliese 2026's LIF weight, 0.275 mV, the rest of the cord at 0.185; the review's item 5; a labelled stand-in with a source)")
ap.add_argument("--cell-delay", default="", help="per-cell conduction delay, TYPES:MS: the named cells' output reaches their targets after MS instead of the engine's 1.8 (effective 3) ms. axonal delays in the cord are real and unmeasured per cell (E); the ring's period is the loop's delays (3 x 3 ms + rise = 40 ms, 25 Hz), so this asks whether a slower loop rings at the band a leg follows")
ap.add_argument("--mirror", default="off", help="mirror normalisation of bilateral pairs' input weights (src/fly_afterlife/wiring.py; the labelled tracing correction of 09-19): off | all | vnc (motor, IN, AN, SN types) | a comma-separated type list")
ap.add_argument("--treadmill", type=float, default=0.0, help="the headless treadmill (a labelled stand-in, 09-21): step frequency in Hz at which each leg's proprioceptors (world/legs.npz, by bodyId) are loaded in stance (--leg-load-hz) and UNLOADED (0 Hz) in swing, in two alternating tripods (L1 R2 L3 / R1 L2 R3), --treadmill-duty of the cycle in stance; 0 = off (the floor's constant load). asks whether unloading alone releases swing")
ap.add_argument("--treadmill-duty", type=float, default=0.5)
ap.add_argument("--adapt", default="", help="spike-frequency adaptation on every cell, B:TAU (mV per spike, ms), e.g. 1:200; off by default. an intrinsic current the LIF lacks (docs/SEAM.md \"the switch\"), constants (E) swept, labelled")
ap.add_argument("--rebound", default="", help="post-inhibitory rebound on every cell, G:TAU (mV of push per mV of hyperpolarisation, ms), e.g. 1:100; off by default; labelled")
ap.add_argument("--drive", default="", help="drive named sensory / descending types at a rate: TYPE:HZ,TYPE:HZ (e.g. SNpp50:50, the extension-tuned FeCO claw cells); rows after the floor and the treadmill, so they override on those cells; a labelled diagnostic")
args = ap.parse_args()
fps, CH = 100, 10; SPF = int(round(1000 / fps / args.dt)); t0 = time.time()

M = FastFlyBrain(args.brain, seed=args.seed, params=Params(mv_per_synapse=args.wsyn_m, noise=args.noise * (args.dt ** 0.5), dt=args.dt)); M.integrate = args.integrate
mty = M.type.astype(str); mns = M.side.astype(str)
print(f"{args.brain}: {M.N} cells; engine {type(M).__name__}, {args.integrate}, w {args.wsyn_m} mV, noise {args.noise}")

if args.std != "off":   # the same block as pair.py (09-21)
    _mask = np.ones(M.N, bool) if args.std == "all" else (mty == "DNg33") if args.std == "pair" else np.isin(mty, args.std.split(","))   # all | pair | a comma-separated type list (the inhibitor pools, 09-21 night)
    M._std_mask = _mask; M._std_x = np.ones(M.N, np.float32); M.std_on = True
    if args.std_u is not None: M.p.std_u = float(args.std_u)
    if args.std_tau is not None: M.p.std_tau_rec_ms = float(args.std_tau)
    print(f"short-term depression on {int(_mask.sum())} cells ({args.std}); u {M.p.std_u}, tau {M.p.std_tau_rec_ms} ms")

if args.adapt:
    b_, tau_ = (float(x) for x in args.adapt.split(":")); M.adapt_on = True; M.adapt_b = b_; M.adapt_tau = tau_; M._adapt_a = np.zeros(M.N, np.float32); print(f"adaptation: b {b_} mV per spike, tau {tau_} ms")
if args.rebound:
    g_, tau_ = (float(x) for x in args.rebound.split(":")); M.rebound_on = True; M.rebound_g = g_; M.rebound_tau = tau_; M._reb_r = np.zeros(M.N, np.float32); print(f"rebound: g {g_}, tau {tau_} ms")
if args.mirror != "off":
    from fly_afterlife.wiring import mirror_normalise; print("mirror normalisation:", mirror_normalise(M, scope=(args.mirror.split(",") if "," in args.mirror else args.mirror)))
if args.graded:
    parts = args.graded.split(":")
    if parts[0] == "random": n_ = int(parts[1]); g_ = float(parts[2]); rng_ = np.random.default_rng(args.seed + 7); cand = np.flatnonzero(np.char.startswith(mty, "IN")); gc = np.sort(rng_.choice(cand, n_, replace=False)); label = f"random {n_}"
    else: pref = parts[0].split(","); g_ = float(parts[1]); gc = np.flatnonzero(np.any([np.char.startswith(mty, p_) for p_ in pref], axis=0)); label = ",".join(pref)
    v1 = float(parts[-1]) if len(parts) > (3 if parts[0] == "random" else 2) else float(M.p.v_thresh)
    M.graded_on = True; M._graded_cells = gc.astype(np.int64); M.graded_gain = g_; M.graded_v0 = 0.0; M.graded_v1 = v1; M._graded_idx = np.zeros(0, np.int64); M._graded_scale = np.zeros(0, np.float32); M.v_th[gc] = np.float32(1e6)
    print(f"graded units: {len(gc)} cells ({label}), gain {g_} per ms at v = {v1} mV")
if args.size_gain > 0 or args.size_thr > 0:
    _S = np.bincount(M._out_tgt, weights=np.abs(M._out_w), minlength=M.N) / M.p.mv_per_synapse; _neur = ~np.isin(M.sc.astype(str), ["vnc_sensory", "sensory_ascending", "sensory_descending", "vnc_sensory_tbc", "sensory_ascending_tbc"]) & (_S > 0)
    _Smed = float(np.median(_S[_neur])); _ratio = np.where(_S > 0, _S / _Smed, 1.0)
    if args.size_gain > 0:
        _f = np.clip(_ratio ** (-args.size_gain), 1.0 / args.size_clip, args.size_clip).astype(np.float32); M._out_w *= _f[M._out_tgt]
        print(f"size gain: synapses onto each cell scaled by (S_med / S)^{args.size_gain} (S_med {_Smed:.0f}); factors {np.round(np.quantile(_f[_neur], [0.05, 0.5, 0.95]), 2)}")
    if args.size_thr > 0:
        _t = np.clip(_ratio ** args.size_thr, 1.0 / args.size_clip, args.size_clip); M.v_th[_neur] = (np.float32(M.p.v_thresh) * _t[_neur]).astype(np.float32)
        print(f"size threshold: v_th = 7 x (S / S_med)^{args.size_thr}; thresholds {np.round(np.quantile(M.v_th[_neur], [0.05, 0.5, 0.95]), 2)} mV")
if args.edge_scale:
    _et, _ef = args.edge_scale.rsplit(":", 1); _em = np.isin(mty, _et.split(",")); _src = np.repeat(np.arange(M.N), np.diff(M._out_ptr)); _sel = _em[_src] & _em[M._out_tgt]
    M._out_w[_sel] *= np.float32(float(_ef)); print(f"edge scale: {int(_sel.sum())} synapses among {_et} x {_ef}")
if args.cell_delay:
    _dt_, _dms = args.cell_delay.rsplit(":", 1); _dsteps = max(1, int(round(float(_dms) / M.p.dt))); _base = max(1, int(round(M.p.syn_delay_ms / M.p.dt)))
    M._cell_delay = np.full(M.N, _base, np.int64); M._cell_delay[np.isin(mty, _dt_.split(","))] = _dsteps; Dmax = int(M._cell_delay.max())
    M._dly_max = Dmax; M.delay_on = True; print(f"cell delay: {int((M._cell_delay == _dsteps).sum())} cells of {_dt_} at {_dms} ms ({_dsteps} steps); the rest {_base} steps")
REG = Registry()
if args.shock:
    _ss, _sh = (float(x) for x in args.shock.split(":")); _alldn = np.flatnonzero(M.sc.astype(str) == "descending_neuron")
    REG.add(ReceptorClass("shock", _alldn, Scaled(_sh), lambda st: float(st.get("shock_gain", 0.0)))); print(f"shock: {len(_alldn)} descending neurons at {_sh} Hz for {_ss} s after the warm-up")
if args.walk > 0:
    _wd = [x for x in args.walk_dn.split(",") if x]; WALK = np.flatnonzero(np.isin(mty, _wd) & (M.sc.astype(str) == "descending_neuron"))
    if args.walk_side: WALK = WALK[mns[WALK] == args.walk_side]   # a comma-separated list: the command as a population (09-21 night)
    print(f"command: {len(WALK)} cells of {_wd} at {args.walk} Hz")
    REG.add(ReceptorClass(f"walk_{args.walk_dn}", WALK, Scaled(args.walk), lambda st: float(st.get("walk_gain", 1.0)), source="Bidaye 2020: the walking DN driven in a decapitated fly"))
else: WALK = np.zeros(0, np.int64)
_fl = tonic_floor(M, REG) if args.floor else []
for rc in _fl:
    if rc.name == "floor_leg_proprio": rc.transducer.hz = args.leg_load_hz
if args.treadmill > 0:   # per-leg load rows after the floor, so they override it on the leg cells
    from fly_afterlife.receptors import Transducer
    class StanceLoad(Transducer):
        def __init__(self, hz, phase, f, duty): self.hz, self.phase, self.f, self.duty = hz, phase, f, duty; self.source = "the headless treadmill: load in stance, none in swing (stand-in)"
        def step(self, stim, t, dt): return self.hz if ((self.f * t - self.phase) % 1.0) < self.duty else 0.0
    _legs = np.load("world/legs.npz"); _wb = np.load("brain_whole.npz", allow_pickle=True)["bodyId"]; _pos = {int(b_): i_ for i_, b_ in enumerate(M.bodyId)}
    TRIPOD = {"L1": 0.0, "R2": 0.0, "L3": 0.0, "R1": 0.5, "L2": 0.5, "R3": 0.5}
    for leg_ in TRIPOD:
        cells_ = np.array([_pos[int(_wb[i_])] for i_ in _legs[leg_] if int(_wb[i_]) in _pos], np.int64)
        REG.add(ReceptorClass(f"treadmill_{leg_}", cells_, StanceLoad(args.leg_load_hz, TRIPOD[leg_], args.treadmill, args.treadmill_duty), lambda st: True))
    print(f"treadmill: {args.treadmill} Hz steps, duty {args.treadmill_duty}, load {args.leg_load_hz} Hz in stance, 0 in swing")
if args.drive:
    from fly_afterlife.receptors import Hold
    for item in args.drive.split(","):
        t_, hz_ = item.split(":"); cells_ = np.flatnonzero(mty == t_)
        REG.add(ReceptorClass(f"drive_{t_}", cells_, Hold(float(hz_)), lambda st: True, source="cord.py --drive: a named type held at a rate (diagnostic)")); print(f"drive: {t_} ({len(cells_)} cells) at {hz_} Hz")
print(REG.table())

M.driven[:] = False
for cl in M.SENSORY_CLASSES: M.driven[M.cls == cl] = True
if len(_fl): M.driven[np.unique(np.concatenate([rc.cells for rc in _fl]))] = True
if len(WALK): M.driven[WALK] = True
for rc in REG.classes:
    if rc.name.startswith("drive_") or rc.name.startswith("treadmill_") or rc.name == "shock": M.driven[rc.cells] = True
M._driven_idx = np.flatnonzero(M.driven); M.reset()
if args.silence:
    _sil = np.flatnonzero(np.isin(mty, [x for x in args.silence.split(",") if x])); M.v_th[_sil] = np.float32(1e6); print(f"silenced {len(_sil)} cells of {args.silence} (driven cells unaffected)")

if args.log_types: _lt = [x for x in args.log_types.split(",") if x]
else:
    from fly_afterlife.receptors import annotations
    a = annotations(); _lt = sorted(set(a.loc[(a["superclass"] == "vnc_motor") & a["subclass"].isin(["fl", "ml", "hl"]), "type"].dropna().astype(str)))
LC = np.flatnonzero(np.isin(mty, _lt)); print(f"logging {len(LC)} cells of {len(_lt)} types")

n_frames = int(round(args.seconds * fps)); FR = np.zeros((n_frames, len(LC)), np.int16); ALL = np.zeros(n_frames, np.int32)
MSC = np.zeros((n_frames * SPF, len(LC)), np.int8) if args.log_ms else None
state = {"walk_gain": 0.0}
for f in range(n_frames):
    t = f / fps; state["walk_gain"] = 1.0 if t >= args.warmup else 0.0
    if args.pulse and t >= args.warmup:
        _ph, _pd = (args.pulse.split(":") + ["0.5"])[:2]; state["walk_gain"] = 1.0 if ((float(_ph) * (t - args.warmup)) % 1.0) < float(_pd) else 0.0
    if args.shock: state["shock_gain"] = 1.0 if args.warmup <= t < args.warmup + float(args.shock.split(":")[0]) else 0.0
    REG.apply(M, state, t, 1.0 / fps)
    acc = np.zeros(M.N, np.int32)
    for k_ in range(SPF):
        M.step(); acc[M.last_idx] += 1
        if MSC is not None and M.last_idx.size: MSC[f * SPF + k_, np.searchsorted(LC, M.last_idx[np.isin(M.last_idx, LC)])] += 1
    FR[f] = acc[LC]; ALL[f] = acc.sum()
    if f % (10 * fps) == 0 and f: print(f"t={t:5.1f}s  cord {ALL[f - 10 * fps:f].mean() * fps / M.N:.2f} Hz/cell  leg MN {FR[f - 10 * fps:f].mean() * fps:.2f} Hz/cell  ({time.time() - t0:.0f}s)")

nc = n_frames // CH; counts = FR[:nc * CH].reshape(nc, CH, -1).sum(1)
os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
np.savez_compressed(args.out.replace(".npz", "") + ".cells.npz", cells=LC, bodyId=M.bodyId[LC], type=mty[LC], side=mns[LC], counts=counts.astype(np.int32),
                    pose_chunk=np.zeros((nc, 3), np.float32), frames=FR, pose_frame=np.zeros((n_frames, 3), np.float32), cord_hz=ALL.astype(np.int32), **({'ms_counts': MSC} if MSC is not None else {}))
np.savez_compressed(args.out, fps=fps, chunk=CH, cord_spikes=ALL, args=np.array(str(vars(args))))
w = FR[int(args.warmup * fps):]; print(f"done in {time.time() - t0:.0f}s: after the warm-up, cord {ALL[int(args.warmup * fps):].mean() * fps / M.N:.2f} Hz/cell, leg MN {w.mean() * fps:.2f} Hz/cell, {int((w.mean(0) * fps > 1).sum())} of {len(LC)} leg MNs above 1 Hz")
print("wrote", args.out.replace(".npz", "") + ".cells.npz")
