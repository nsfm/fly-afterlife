"""leg_replay.py - the first body: his cord's left front leg, through FlyMimic's fifteen Hill-type muscles (Özdil 2026, vendored in
flygym 2.1), on the musculoskeletal tethered preparation. a readout, not a loop: the cord's per-frame motor neuron spikes (a cord.py or
pair.py run with --log-frames) become muscle activations through a twitch kernel and are played into the body; the body's joint angles
are recorded and a video rendered. nothing feeds back yet (§Q 4e stage 1 / 2 on one leg).

the map (docs/physiology/leg_biomech.md §A; the type names of the table to FlyMimic's muscle names):
  Tergopleural/Pleural promotor MN -> tergopleural_promotor_a + _b + pleural_promotor      Pleural remotor/abductor MN -> pleural_remotor_and_abductor
  Sternal anterior rotator MN -> sternal_anterior_rotator     Sternal posterior rotator MN -> sternal_posterior_rotator     Sternal adductor MN -> sternal_adductor
  Tr flexor MN -> trochanter_flexor_a + _b     Acc. tr flexor MN -> accesory_trochanter_flexor     Sternotrochanter MN -> sterno-tergo-trochanter_extensor_a + _b
  Tr extensor MN -> trochanter_extensor     Ti flexor MN + Acc. ti flexor MN -> Tibia_flex     Ti extensor MN -> Tibia_extensor
  unmapped (no muscle or joint in FlyMimic): ltm, ltm1, ltm2, Ta depressor / levator, Fe reductor, Tergotr. (the jump muscle)
the kernel (§B, Azevedo 2020, (D)/(E)): a difference of exponentials, tau_rise 7 ms, tau_decay 20 ms, peak at ~21 ms, normalised to 1 per
spike for the largest motor neuron of a muscle; force per spike by input-synapse size, f = (S / S_max) ** 1.2 within the muscle; the
muscle's activation = clip(sum over its MNs of f_i x (K * spikes_i) / SAT, 0, 1) with SAT = 10 spike-equivalents (force saturates at ~10
spikes). spikes are at the log's 10 ms frames, placed at the frame's start (a coarse first pass; the twitch is longer than a frame).

    uv run python experiments/leg_replay.py world/cord/ctl_s11.npz --seconds 10 --out world/cord/video/ctl
"""
import sys, os, argparse, numpy as np
sys.path.insert(0, "src")
ap = argparse.ArgumentParser(); ap.add_argument("run"); ap.add_argument("--seconds", type=float, default=10.0); ap.add_argument("--start", type=float, default=2.0, help="seconds into the log to start (after the cord's warm-up)")
ap.add_argument("--out", required=True); ap.add_argument("--sat", type=float, default=10.0); ap.add_argument("--alpha", type=float, default=1.2); ap.add_argument("--gain", type=float, default=1.0, help="a global scale on activation (1 = the kernel as stated)")
ap.add_argument("--no-video", action="store_true"); ap.add_argument("--fps", type=int, default=25)
args = ap.parse_args()

C = np.load(args.run.replace(".npz", "") + ".cells.npz", allow_pickle=True); ty = C["type"].astype(str); side = C["side"].astype(str); bid = C["bodyId"]; FR = C["frames"].astype(np.float64)
lm = np.load("world/legmn.npz"); wb = np.load("brain_whole.npz", allow_pickle=True); wbid = wb["bodyId"]; fl_L = set(int(wbid[i]) for i in lm["fl_L"])
LF = np.array([int(b) in fl_L for b in bid]); print(f"left front leg: {LF.sum()} motor neurons in the log")
# input-synapse size per cell from the whole brain (the same cells)
pos = {int(b): i for i, b in enumerate(wbid)}; S = np.zeros(len(bid))
post = wb["post"]; w = wb["w"].astype(float); insyn = np.bincount(post, weights=w, minlength=len(wbid))
for j, b in enumerate(bid): S[j] = insyn[pos[int(b)]]
MAP = {"Tergopleural/Pleural promotor MN": ["LFC_tergopleural_promotor_a", "LFC_tergopleural_promotor_b", "LFC_pleural_promotor"], "Pleural remotor/abductor MN": ["LFC_pleural_remotor_and_abductor"],
       "Sternal anterior rotator MN": ["LFC_sternal_anterior_rotator"], "Sternal posterior rotator MN": ["LFC_sternal_posterior_rotator"], "Sternal adductor MN": ["LFC_sternal_adductor"],
       "Tr flexor MN": ["LFF_trochanter_flexor_a", "LFF_trochanter_flexor_b"], "Acc. tr flexor MN": ["LFF_accesory_trochanter_flexor"], "Sternotrochanter MN": ["LFF_sterno-tergo-trochanter_extensor_a", "LFF_sterno-tergo-trochanter_extensor_b"],
       "Tr extensor MN": ["LFF_trochanter_extensor"], "Ti flexor MN": ["LFTibia_flex_93434"], "Acc. ti flexor MN": ["LFTibia_flex_93434"], "Ti extensor MN": ["LFTibia_extensor_93932"]}
from flygym.compose import build_musculoskeletal_simulation, ActuatorType, DEFAULT_SCENE_CAMERA
from flygym import Renderer
import mujoco as mj
sim, fly = build_musculoskeletal_simulation(); m = sim.mj_model; d = sim.mj_data
muscles = list(fly.muscle_names); mi = {n: i for i, n in enumerate(muscles)}
# per-muscle motor neuron sets and force weights
cells_of = {n: [] for n in muscles}; unmapped = set()
for j in np.flatnonzero(LF):
    if ty[j] in MAP:
        for n in MAP[ty[j]]: cells_of[n].append(j)
    else: unmapped.add(ty[j])
print("unmapped types (no muscle in FlyMimic):", sorted(unmapped))
f_w = np.zeros(len(bid))
for n, js in cells_of.items():
    if js: smax = max(S[js]) if max(S[js]) > 0 else 1.0
    for j in js: f_w[j] = max(f_w[j], (S[j] / smax) ** args.alpha if S[j] > 0 else 0.1)
for n in muscles: print(f"  {n:42s} {len(cells_of[n]):2d} MNs, force weights {np.round(sorted(f_w[cells_of[n]], reverse=True), 2)[:6]}")
# the twitch kernel at 1 ms
t = np.arange(0, 120); K = np.exp(-t / 20.0) - np.exp(-t / 7.0); K /= K.max()
# per-ms activation per muscle over the replay window
f0 = int(args.start * 100); nfr = int(args.seconds * 100); FRw = FR[f0:f0 + nfr]; nms = nfr * 10
drive = np.zeros((len(muscles), nms + len(K)))
for n, js in cells_of.items():
    for j in js:
        sp = np.flatnonzero(FRw[:, j] > 0)
        for fidx in sp:
            k = int(FRw[fidx, j]); drive[mi[n], fidx * 10: fidx * 10 + len(K)] += k * f_w[j] * K   # spikes at the frame's start (10 ms), k of them
act = np.clip(args.gain * drive[:, :nms] / args.sat, 1e-4, 1.0)
print("activation per muscle over the window (mean, max):"); [print(f"  {n:42s} {act[i].mean():.3f} {act[i].max():.3f}") for i, n in enumerate(muscles)]
# the body: 0.1 ms physics, control every 1 ms, render at fps
os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
ren = None
if not args.no_video: sim.set_renderer(DEFAULT_SCENE_CAMERA, camera_res=(480, 640), playback_speed=1.0, output_fps=args.fps); ren = sim.renderer
sim.reset(); jn = [mj.mj_id2name(m, mj.mjtObj.mjOBJ_JOINT, i) for i in range(m.njnt)]; ang = np.zeros((nms, m.njnt)); steps_per_ms = int(round(0.001 / m.opt.timestep))
for ms in range(nms):
    sim.set_actuator_inputs("nmf", ActuatorType.MUSCLE, act[:, ms])
    for _ in range(steps_per_ms): sim.step()
    ang[ms] = d.qpos[:m.njnt]
    if ren is not None: sim.render_as_needed()
np.savez_compressed(args.out + ".npz", joints=np.array(jn), angles_deg=np.degrees(ang).astype(np.float32), act=act.astype(np.float32), muscles=np.array(muscles), ms=np.arange(nms))
deg = np.degrees(ang); print("joint angle ranges over the window (deg, LF joints):")
for i, n in enumerate(jn):
    if n.startswith("joint_LF"): print(f"  {n:26s} min {deg[:, i].min():7.1f} max {deg[:, i].max():7.1f}  sd {deg[:, i].std():5.1f}")
if ren is not None:
    ren.save_video(args.out + ".mp4"); print("video", args.out + ".mp4", "frames", len(ren.frames[DEFAULT_SCENE_CAMERA]) if isinstance(ren.frames, dict) else "?")
print("wrote", args.out + ".npz")
