"""body_six.py - the six-legged body (NeuroMechFly v2, flygym 2.1) on a floor, driven by his cord's motor neurons: a replay (stage 1-2 of §Q 4e).

every leg motor neuron in a per-frame log (cord.py or pair.py with --log-frames) is mapped by its type name to a muscle group, the group to
a joint of its leg and a direction, and the group's activation (the twitch kernel of experiments/leg_replay.py: rise 7 ms, decay 20 ms,
force by input-synapse size, saturation 10 spike-equivalents) becomes a torque on that joint: torque = gain x (agonist - antagonist).
the joint and the direction per role were MEASURED on the body (experiments/body_signs.py -> results/body_dof_signs.json: which joint
swings the foot forward, lifts it, shortens the leg), not assumed. roles and their muscle groups:
  protract: promotors + sternal anterior rotator  vs  retract: pleural remotor + sternal posterior rotator
  levate:   trochanter flexor + accessory          vs  depress: sternotrochanter + trochanter extensor
  flex:     tibia flexor + accessory               vs  extend:  tibia extensor
  tarsus levate: Ta levator (+ MNml81 / MNhl65 by serial set, brief §A)  vs  tarsus depress: Ta depressor
  adduct:   sternal adductor (one-sided)
  grip:     the long tendon muscles (ltm, ltm1, ltm2) -> the leg's adhesion actuator (the claw / retractor unguis), on while they fire
  unmapped: femur reductor (the trochanter-femur joint is fused in this body), the jump muscle
the body's joint springs are flygym's defaults (stiffness 10, damping 0.5), which hold the neutral pose with no torque: NOT the measured
passive stiffness (Wang 2025: ~70x too weak to stand); `--stiffness` sets it, and the honest arm is the one where he has to hold himself up.

    uv run python experiments/body_six.py world/cord/ctl_s11.npz --seconds 5 --out world/body/ctl
"""
import os, sys, json, argparse, time, numpy as np
ap = argparse.ArgumentParser(); ap.add_argument("run"); ap.add_argument("--seconds", type=float, default=5.0); ap.add_argument("--start", type=float, default=2.0)
ap.add_argument("--out", required=True); ap.add_argument("--gain", type=float, default=42.0, help="torque (nN m = the model's g mm^2/s^2) per unit activation: 42 = ten spike-equivalents at 4.2 nN m per fast spike (Azevedo 2020, brief B1: one fast spike ~ one body weight, 10 uN, at the tibia), a derivation not a fit; the actuators clip at +-60")
ap.add_argument("--sat", type=float, default=10.0); ap.add_argument("--alpha", type=float, default=1.2); ap.add_argument("--stiffness", type=float, default=None, help="joint spring stiffness (default: flygym's 10)")
ap.add_argument("--no-adhesion", action="store_true"); ap.add_argument("--no-video", action="store_true"); ap.add_argument("--fps", type=int, default=25); ap.add_argument("--camera", default="track")
args = ap.parse_args(); t0 = time.time()
import mujoco as mj
from flygym.utils.math import Rotation3D
from flygym.compose import NeuroMechFly, FlatGroundWorld, ActuatorType, KinematicPosePreset
from flygym.anatomy import JointPreset, ActuatedDOFPreset, Skeleton, AxisOrder
from flygym import Simulation

C = np.load(args.run.replace(".npz", "") + ".cells.npz", allow_pickle=True); ty = C["type"].astype(str); bid = C["bodyId"]; FR = C["frames"].astype(np.float64)
lm = np.load("world/legmn.npz"); wb = np.load("brain_whole.npz", allow_pickle=True); wbid = wb["bodyId"]; legof = {}
for g, L in (("fl", "f"), ("ml", "m"), ("hl", "h")):
    for s in "LR":
        for i in lm[f"{g}_{s}"]: legof[int(wbid[i])] = s.lower() + L
leg = np.array([legof.get(int(b), "") for b in bid]); print(f"{(leg != '').sum()} leg motor neurons in the log")
post = wb["post"]; w = wb["w"].astype(float); insyn = np.bincount(post, weights=w, minlength=len(wbid)); pos = {int(b): i for i, b in enumerate(wbid)}; S = np.array([insyn[pos[int(b)]] for b in bid])
ROLE = {"Tergopleural/Pleural promotor MN": ("protract", +1), "Sternal anterior rotator MN": ("protract", +1), "Pleural remotor/abductor MN": ("protract", -1), "Sternal posterior rotator MN": ("protract", -1),
        "Tr flexor MN": ("levate", +1), "Acc. tr flexor MN": ("levate", +1), "Sternotrochanter MN": ("levate", -1), "Tr extensor MN": ("levate", -1),
        "Ti flexor MN": ("flex", +1), "Acc. ti flexor MN": ("flex", +1), "Ti extensor MN": ("flex", -1),
        "Ta levator MN": ("tarsus_levate", +1), "MNml81": ("tarsus_levate", +1), "MNhl65": ("tarsus_levate", +1), "Ta depressor MN": ("tarsus_levate", -1),
        "Sternal adductor MN": ("adduct", +1), "ltm MN": ("grip", +1), "ltm1-tibia MN": ("grip", +1), "ltm2-femur MN": ("grip", +1)}
signs = json.load(open("results/body_dof_signs.json")); roles = signs["roles"]
# the body
fly = NeuroMechFly(); skel = Skeleton(axis_order=AxisOrder.PITCH_ROLL_YAW, joint_preset=JointPreset.LEGS_ONLY)
kw = {} if args.stiffness is None else dict(stiffness=args.stiffness)
fly.add_joints(skel, KinematicPosePreset.NEUTRAL, **kw); dofs = ActuatedDOFPreset.LEGS_ACTIVE_ONLY.filter(fly.get_jointdofs_order())
fly.add_actuators(dofs, ActuatorType.MOTOR, forcerange=(-60.0, 60.0)); adh = fly.add_leg_adhesion() if not args.no_adhesion else {}
if not args.no_video: fly.add_tracking_camera("trackcam")   # a camera that follows the thorax (must be added before the world compiles)
world = FlatGroundWorld(); world.add_fly(fly, (0.0, 0.0, 0.5), Rotation3D(format="quat", values=(1, 0, 0, 0))); sim = Simulation(world); m = sim.mj_model; d = sim.mj_data
dof_names = [f"{x.parent.name}->{x.child.name}:{x.axis.value}" for x in dofs]; di = {n: i for i, n in enumerate(dof_names)}
# per cell: (dof index, signed weight) and force weight by size within (leg, role, side)
cell_dof = np.full(len(bid), -1); cell_sgn = np.zeros(len(bid)); grip_leg = np.full(len(bid), "", dtype=object); f_w = np.zeros(len(bid)); groups = {}
for j in range(len(bid)):
    if not leg[j] or ty[j] not in ROLE: continue
    role, ag = ROLE[ty[j]]
    if role == "grip": grip_leg[j] = leg[j]; groups.setdefault((leg[j], "grip"), []).append(j); continue
    r = roles[leg[j]][role]; cell_dof[j] = r["k"]; cell_sgn[j] = r["sign"] * ag; groups.setdefault((leg[j], role, ag), []).append(j)
for key, js in groups.items():
    smax = max(S[js]) or 1.0
    for j in js: f_w[j] = (S[j] / smax) ** args.alpha if S[j] > 0 else 0.1
mapped = int((cell_dof >= 0).sum()) + int((grip_leg != "").sum()); print(f"mapped {mapped} of {(leg != '').sum()} leg MNs to joints ({int((grip_leg != '').sum())} to grip); unmapped types: {sorted(set(ty[(leg != '') & (cell_dof < 0) & (grip_leg == '')]))}")
# activations at 1 ms
KL = 120; tk = np.arange(KL); K = np.exp(-tk / 20.0) - np.exp(-tk / 7.0); K /= K.max()
f0 = int(args.start * 100); nfr = int(args.seconds * 100); FRw = FR[f0:f0 + nfr]; nms = nfr * 10
torque = np.zeros((len(dofs), nms + KL)); grip = {l: np.zeros(nms + KL) for l in ("lf", "lm", "lh", "rf", "rm", "rh")}
for j in range(len(bid)):
    if cell_dof[j] < 0 and grip_leg[j] == "": continue
    sp = np.flatnonzero(FRw[:, j] > 0)
    for fidx in sp:
        k = int(FRw[fidx, j]); a = k * f_w[j] * K / args.sat
        if grip_leg[j] != "": grip[grip_leg[j]][fidx * 10: fidx * 10 + KL] += a
        else: torque[cell_dof[j], fidx * 10: fidx * 10 + KL] += cell_sgn[j] * a
torque = np.clip(args.gain * torque[:, :nms], -60, 60); print("torque per dof over the window: mean |t|", np.round(np.abs(torque).mean(1), 2).tolist()[:14], "...")
# run
os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
if not args.no_video:
    cams = [mj.mj_id2name(m, mj.mjtObj.mjOBJ_CAMERA, i) for i in range(m.ncam)]; cam = [c for c in cams if "trackcam" in c][0]; print("cameras:", cams, "-> using", cam)
    sim.set_renderer(cam, camera_res=(480, 640), playback_speed=1.0, output_fps=args.fps)
sim.reset(); steps_per_ms = int(round(0.001 / m.opt.timestep)); segs = [s.name for s in fly.get_bodysegs_order()]; thorax = segs.index("c_thorax")
P = np.zeros((nms, 3), np.float32); Q = np.zeros((nms, 4), np.float32); legs6 = ["lf", "lm", "lh", "rf", "rm", "rh"]
for ms in range(nms):
    sim.set_actuator_inputs("nmf", ActuatorType.MOTOR, torque[:, ms])
    if adh: sim.set_leg_adhesion_states("nmf", np.array([grip[l][ms] > 0.05 for l in legs6])) if hasattr(sim, "set_leg_adhesion_states") else None
    for _ in range(steps_per_ms): sim.step()
    P[ms] = sim.get_body_positions("nmf")[thorax]; Q[ms] = sim.get_body_rotations("nmf")[thorax]
    if not args.no_video: sim.render_as_needed()
    if ms % 1000 == 0: print(f"t={ms / 1000:.1f}s thorax {np.round(P[ms], 2)} ({time.time() - t0:.0f}s)")
np.savez_compressed(args.out + ".npz", thorax=P, quat=Q, torque=torque.astype(np.float32), dofs=np.array(dof_names), args=np.array(str(vars(args))))
w_, x_, y_, z_ = Q[:, 0], Q[:, 1], Q[:, 2], Q[:, 3]; yaw = np.degrees(np.arctan2(2 * (w_ * z_ + x_ * y_), 1 - 2 * (y_ ** 2 + z_ ** 2))); print(f"heading (yaw) start {yaw[0]:+.0f} end {yaw[-1]:+.0f} deg; net turn {((yaw[-1] - yaw[0] + 180) % 360) - 180:+.0f} deg")
print(f"done in {time.time() - t0:.0f}s: thorax start {np.round(P[0], 2)} end {np.round(P[-1], 2)}; travelled {np.linalg.norm(P[-1, :2] - P[0, :2]):.2f} mm; height min {P[:, 2].min():.2f} max {P[:, 2].max():.2f}")
if not args.no_video: sim.renderer.save_video(args.out + ".mp4"); print("video", args.out + ".mp4")
