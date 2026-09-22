"""leg_loop.py - the first loop: the headless cord and FlyMimic's left front leg in one process, at a millisecond.

the cord (brain_cord.npz, as world/cord.py: the floor's cord rows, the walking command on named descending neurons) drives the leg's
fifteen Hill-type muscles through the twitch kernel of experiments/leg_replay.py, and the leg's joint state drives the cord's own
sensory cells for that leg:
  position -> the femoral chordotonal organ's claw cells (Mamiya 2018: tonic, monotonic in tibia angle; extension-tuned SNpp50 fire
              more as the tibia extends, flexion-tuned SNpp51 as it flexes; rates (E): 0-100 Hz over the 60 deg either side of 90)
  velocity -> the hook cells (Mamiya 2018: directional, velocity-flat 100-800 deg/s; SNpp39 flexion, SNpp41 extension, an assignment (E);
              rate (E): 100 Hz x clip(|omega| / 300 deg/s))
  load     -> the treadmill (world/cord.py's: the leg's other proprioceptors loaded in stance, unloaded in swing, on a fixed clock),
              until there is a floor. `--treadmill 0` = the floor's constant load.
the sensory side of this leg is thin: the left front leg is the worst-traced leg in the volume (E_table_male.md: 1 extension-tuned
claw cell, 4 flexion-tuned, 3 + 2 hook cells) - noted in the record with every result.

arms: --loop off (a live replay: the cord never hears the leg) | position | position+treadmill | treadmill (load only, no position).

    uv run python experiments/leg_loop.py --walk 100 --walk-dn DNg100 --loop position --treadmill 5 --seconds 20 --out world/cord/loop/pos_tm5
"""
import os, sys, argparse, time, numpy as np
sys.path.insert(0, "ref/flybrain/scripts"); sys.path.insert(0, "world"); sys.path.insert(0, "src")
from flysim import Params
from fastlif import FastFlyBrain
from fly_afterlife.receptors import Registry, ReceptorClass, Scaled, Hold, Transducer, tonic_floor, annotations
import mujoco as mj
from flygym.compose import build_musculoskeletal_simulation, ActuatorType, DEFAULT_SCENE_CAMERA

ap = argparse.ArgumentParser()
ap.add_argument("--out", required=True); ap.add_argument("--seconds", type=float, default=20.0); ap.add_argument("--seed", type=int, default=11)
ap.add_argument("--wsyn-m", type=float, default=0.185); ap.add_argument("--noise", type=float, default=0.15)
ap.add_argument("--walk", type=float, default=100.0); ap.add_argument("--walk-dn", default="DNg100")
ap.add_argument("--std", default="off"); ap.add_argument("--leg-load-hz", type=float, default=15.0)
ap.add_argument("--treadmill", type=float, default=0.0, help="step Hz of the load clock on this leg's load cells (0 = constant load)"); ap.add_argument("--treadmill-duty", type=float, default=0.5)
ap.add_argument("--loop", default="position", help="off | position | position+treadmill | treadmill")
ap.add_argument("--claw-hz", type=float, default=100.0); ap.add_argument("--hook-hz", type=float, default=100.0); ap.add_argument("--hook-vel", type=float, default=300.0)
ap.add_argument("--sat", type=float, default=10.0); ap.add_argument("--alpha", type=float, default=1.2); ap.add_argument("--gain", type=float, default=1.0)
ap.add_argument("--warmup", type=float, default=2.0); ap.add_argument("--no-video", action="store_true"); ap.add_argument("--fps", type=int, default=25)
args = ap.parse_args(); t0 = time.time()
use_pos = "position" in args.loop; use_tm = ("treadmill" in args.loop) and args.treadmill > 0

# ---- the cord
M = FastFlyBrain("brain_cord.npz", seed=args.seed, params=Params(mv_per_synapse=args.wsyn_m, noise=args.noise)); M.integrate = "exact"
mty = M.type.astype(str); mns = M.side.astype(str); mbid = M.bodyId
if args.std != "off":
    _mask = np.ones(M.N, bool) if args.std == "all" else (mty == "DNg33") if args.std == "pair" else np.isin(mty, args.std.split(","))
    M._std_mask = _mask; M._std_x = np.ones(M.N, np.float32); M.std_on = True
REG = Registry()
_wd = [x for x in args.walk_dn.split(",") if x]; WALK = np.flatnonzero(np.isin(mty, _wd) & (M.sc.astype(str) == "descending_neuron")) if args.walk > 0 else np.zeros(0, np.int64)
if len(WALK): REG.add(ReceptorClass("walk", WALK, Scaled(args.walk), lambda st: st["walk_gain"]))
_fl = tonic_floor(M, REG)
for rc in _fl:
    if rc.name == "floor_leg_proprio": rc.transducer.hz = args.leg_load_hz
# this leg's sensory cells, by bodyId through world/legs.npz (indexes brain_whole)
wb = np.load("brain_whole.npz", allow_pickle=True); wbid = wb["bodyId"]; legs = np.load("world/legs.npz"); lm = np.load("world/legmn.npz")
pos = {int(b): i for i, b in enumerate(mbid)}
L1 = np.array([pos[int(wbid[i])] for i in legs["L1"] if int(wbid[i]) in pos], np.int64)
def of(types): return L1[np.isin(mty[L1], types)]
CLAW_E, CLAW_F, HOOK_F, HOOK_E = of(["SNpp50"]), of(["SNpp51"]), of(["SNpp39"]), of(["SNpp41"])
LOAD = L1[~np.isin(mty[L1], ["SNpp50", "SNpp51", "SNpp39", "SNpp41"])]
print(f"left front leg sensory cells in the cord: {len(L1)}; claw extension {len(CLAW_E)}, claw flexion {len(CLAW_F)}, hook flexion {len(HOOK_F)}, hook extension {len(HOOK_E)}, the rest (load and unknown) {len(LOAD)}")
class Rate(Transducer):
    def __init__(self, key): self.key = key; self.source = "leg_loop: a rate from the body's joint state (E)"
    def step(self, stim, t, dt): return float(stim)
if use_pos:
    for nm, cells, key in (("claw_ext", CLAW_E, "claw_e"), ("claw_flex", CLAW_F, "claw_f"), ("hook_flex", HOOK_F, "hook_f"), ("hook_ext", HOOK_E, "hook_e")):
        if len(cells): REG.add(ReceptorClass(nm, cells, Rate(key), (lambda k: (lambda st: st[k]))(key)))
if use_tm:
    class StanceLoad(Transducer):
        def __init__(self, hz, f, duty): self.hz, self.f, self.duty = hz, f, duty; self.source = "the treadmill: load in stance, none in swing (stand-in)"
        def step(self, stim, t, dt): return self.hz if ((self.f * t) % 1.0) < self.duty else 0.0
    REG.add(ReceptorClass("treadmill_L1", LOAD, StanceLoad(args.leg_load_hz, args.treadmill, args.treadmill_duty), lambda st: True))
M.driven[:] = False
for cl in M.SENSORY_CLASSES: M.driven[M.cls == cl] = True
for rc in REG.classes: M.driven[rc.cells] = True
M._driven_idx = np.flatnonzero(M.driven); M.reset()

# ---- the leg
sim, fly = build_musculoskeletal_simulation(); mm = sim.mj_model; d = sim.mj_data; muscles = list(fly.muscle_names); mi = {n: i for i, n in enumerate(muscles)}
fl_L = set(int(wbid[i]) for i in lm["fl_L"]); LF = np.array([pos[b] for b in fl_L if b in pos], np.int64)
MAP = {"Tergopleural/Pleural promotor MN": ["LFC_tergopleural_promotor_a", "LFC_tergopleural_promotor_b", "LFC_pleural_promotor"], "Pleural remotor/abductor MN": ["LFC_pleural_remotor_and_abductor"],
       "Sternal anterior rotator MN": ["LFC_sternal_anterior_rotator"], "Sternal posterior rotator MN": ["LFC_sternal_posterior_rotator"], "Sternal adductor MN": ["LFC_sternal_adductor"],
       "Tr flexor MN": ["LFF_trochanter_flexor_a", "LFF_trochanter_flexor_b"], "Acc. tr flexor MN": ["LFF_accesory_trochanter_flexor"], "Sternotrochanter MN": ["LFF_sterno-tergo-trochanter_extensor_a", "LFF_sterno-tergo-trochanter_extensor_b"],
       "Tr extensor MN": ["LFF_trochanter_extensor"], "Ti flexor MN": ["LFTibia_flex_93434"], "Acc. ti flexor MN": ["LFTibia_flex_93434"], "Ti extensor MN": ["LFTibia_extensor_93932"]}
insyn = np.bincount(M._out_tgt, weights=np.abs(M._out_w), minlength=M.N) / M.p.mv_per_synapse
cells_of = {n: [] for n in muscles}
for j in LF:
    for n in MAP.get(mty[j], []): cells_of[n].append(int(j))
f_w = np.zeros(M.N)
for n, js in cells_of.items():
    if js:
        smax = max(insyn[js]) or 1.0
        for j in js: f_w[j] = max(f_w[j], (insyn[j] / smax) ** args.alpha)
KL = 120; tk = np.arange(KL); K = np.exp(-tk / 20.0) - np.exp(-tk / 7.0); K /= K.max()
mus_of_cell = {j: [mi[n] for n in MAP.get(mty[j], [])] for j in LF}
jn = [mj.mj_id2name(mm, mj.mjtObj.mjOBJ_JOINT, i) for i in range(mm.njnt)]; J_TIB = jn.index("joint_LFTibia_pitch"); J_TRO = jn.index("joint_LFTrochanter_pitch")
steps_per_ms = int(round(0.001 / mm.opt.timestep))
if not args.no_video: sim.set_renderer(DEFAULT_SCENE_CAMERA, camera_res=(480, 640), playback_speed=1.0, output_fps=args.fps)
sim.reset()

# ---- the loop, 1 ms
n_ms = int(args.seconds * 1000); drive = np.zeros((len(muscles), n_ms + KL)); ang = np.zeros((n_ms, mm.njnt), np.float32); act_log = np.zeros((n_ms, len(muscles)), np.float32)
LFMN = np.array(sorted(LF)); spk_ms = np.zeros((n_ms, len(LFMN)), np.int8); sens_log = np.zeros((n_ms, 4), np.float32)
state = {"walk_gain": 0.0, "claw_e": 0.0, "claw_f": 0.0, "hook_f": 0.0, "hook_e": 0.0}; prev_tib = None
for ms in range(n_ms):
    t = ms / 1000.0; state["walk_gain"] = 1.0 if t >= args.warmup else 0.0
    # the leg's state -> the cord's sensory rates
    tib = float(np.degrees(d.qpos[J_TIB])); om = 0.0 if prev_tib is None else (tib - prev_tib) * 1000.0; prev_tib = tib
    state["claw_e"] = args.claw_hz * float(np.clip((tib - 90.0) / 60.0, 0, 1)); state["claw_f"] = args.claw_hz * float(np.clip((90.0 - tib) / 60.0, 0, 1))
    state["hook_f"] = args.hook_hz * float(np.clip(-om / args.hook_vel, 0, 1)); state["hook_e"] = args.hook_hz * float(np.clip(om / args.hook_vel, 0, 1))
    sens_log[ms] = (state["claw_e"], state["claw_f"], state["hook_f"], state["hook_e"])
    REG.apply(M, state, t, 0.001); M.step(); idx = M.last_idx
    # the cord's spikes -> the muscles
    if idx.size:
        hit = idx[np.isin(idx, LFMN)]
        for j in hit:
            for k in mus_of_cell[int(j)]: drive[k, ms: ms + KL] += f_w[j] * K
        spk_ms[ms, np.searchsorted(LFMN, hit)] = 1
    act = np.clip(args.gain * drive[:, ms] / args.sat, 1e-4, 1.0); act_log[ms] = act
    sim.set_actuator_inputs("nmf", ActuatorType.MUSCLE, act)
    for _ in range(steps_per_ms): sim.step()
    ang[ms] = d.qpos[:mm.njnt]
    if not args.no_video: sim.render_as_needed()
    if ms % 5000 == 0 and ms: print(f"t={t:5.1f}s  tibia {tib:6.1f} deg  LF MN {spk_ms[ms - 5000:ms].mean() * 1000:.2f} Hz/cell  ({time.time() - t0:.0f}s)")

os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
w0 = int(args.warmup * 1000); deg = np.degrees(ang)
# per-frame counts in the gait_score format (10 ms), this leg's motor neurons
nfr = n_ms // 10; frames = spk_ms[:nfr * 10].reshape(nfr, 10, -1).sum(1).astype(np.int16)
np.savez_compressed(args.out + ".cells.npz", cells=LFMN, bodyId=mbid[LFMN], type=mty[LFMN], side=mns[LFMN], counts=frames.reshape(nfr // 10, 10, -1).sum(1).astype(np.int32) if nfr >= 10 else frames,
                    pose_chunk=np.zeros((max(nfr // 10, 1), 3), np.float32), frames=frames, pose_frame=np.zeros((nfr, 3), np.float32))
np.savez_compressed(args.out + ".npz", joints=np.array(jn), angles_deg=deg, act=act_log, muscles=np.array(muscles), sens=sens_log, args=np.array(str(vars(args))))
hz = spk_ms[w0:].mean(0) * 1000; flex = np.array([("Ti flexor" in t_) or ("Acc. ti flexor" in t_) for t_ in mty[LFMN]]); ext = mty[LFMN] == "Ti extensor MN"
x = deg[w0:, J_TIB] - deg[w0:, J_TIB].mean(); F = np.abs(np.fft.rfft(x * np.hanning(len(x)))) ** 2; fr = np.fft.rfftfreq(len(x), 0.001); band = (fr >= 0.5) & (fr <= 25); pk = np.argmax(F[band])
print(f"done in {time.time() - t0:.0f}s ({args.seconds / max(time.time() - t0, 1e-9):.2f}x real time). after the warm-up: LF MN {hz.mean():.2f} Hz/cell, tibia flexors {hz[flex].mean():.2f}, extensors {hz[ext].mean():.2f}; "
      f"tibia {deg[w0:, J_TIB].min():.0f}-{deg[w0:, J_TIB].max():.0f} deg (sd {deg[w0:, J_TIB].std():.1f}), trochanter sd {deg[w0:, J_TRO].std():.1f}; tibia-angle spectral peak {fr[band][pk]:.1f} Hz x{F[band][pk] / max(np.median(F[band]), 1e-12):.0f} the band median; "
      f"claw cells drove mean {sens_log[w0:, 0].mean():.0f} / {sens_log[w0:, 1].mean():.0f} Hz, hook {sens_log[w0:, 2].mean():.0f} / {sens_log[w0:, 3].mean():.0f}")
if not args.no_video: sim.renderer.save_video(args.out + ".mp4"); print("video", args.out + ".mp4")
print("wrote", args.out + ".npz")
