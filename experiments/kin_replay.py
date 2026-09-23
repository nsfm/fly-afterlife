"""kin_replay.py - KINEMATIC REPLAY: a real fly's recorded leg angles, replayed by position control on OUR body (09-23, the natural yardstick
beside the puppet, TODO 4o). a reference for what a real fly's legs do on this body, NEVER a result: no neuron is involved.

the recording: flygym's own "replaying experimental recordings" example (flygym 2.1 tutorial 2, flygym_demo.spotlight_data.MotionSnippet):
spotlight_behavior_clip.npz in the installed flygym_demo package, trial 20250613-fly1b-012, frames 1033-1693 of the raw recording, 660 frames
at 330 Hz (2.0 s), 6 legs x 7 DOFs = 42 joint angles (thorax-coxa pitch / roll / yaw, coxa-trochanterfemur pitch / roll, femur-tibia pitch,
tibia-tarsus1 pitch), from the Spotlight closed-loop tracker on an UNTETHERED, freely walking fly, 3D pose by PoseForge from one camera and
joint angles by SeqIKPy inverse kinematics (Wang-Chen, Stimpfling, Azcorra & Ramdya 2026, bioRxiv 10.64898/2026.03.11.711180). the angles
are in the YAW_PITCH_ROLL axis order (the example's skeleton) and SeqIKPy's global sign convention (right-leg roll / yaw flipped here, as
MotionSnippet does).

what is done to it, in order (every step a choice, printed):
  1. the axis order: our body is PITCH_ROLL_YAW (body_loop.py's skeleton). with --axis-order pry (the default) each thorax-coxa orientation
     is re-expressed in our order by fitting our three coxa angles to the recorded coxa's orientation (forward kinematics of two compiled
     models, as flygym.utils.pose_conversion does it for the neutral pose), bounded to the body's own coxa limits (neutral +-45 deg), several
     starts per frame; the residual (foot position error of the fit) is printed per leg. the middle coxae sit next to this order's gimbal
     lock (neutral roll 101 deg), so some recorded orientations cannot be reached inside the limits; that error is the body's, and is
     reported. --axis-order ypr builds the body in the recording's own order instead (a control; everything else identical).
  2. smoothing and upsampling as MotionSnippet: Savitzky-Golay (30 ms, order 3), cubic interpolation to the physics step (0.1 ms).
  3. looping: 2 s of recording, 10 s of replay: the clip is cut at the frame (in its last fifth) whose pose is closest to frame 0 and
     looped, the last --blend-ms crossfaded linearly into the first. the seam's size is printed.
  4. position control: each physics step, torque = clip(kp x (target - angle), +-forcerange) on the 42 actuated DOFs, through the same
     motor actuators body_loop.py uses; this is MuJoCo's position actuator law (kv 0) as flygym's example builds it (ActuatorType.POSITION,
     kp 150), applied by hand so the model build is body_loop.py's exactly. kp 150 (the example's), forcerange 60 (body_loop.py's clip;
     the example's default is 30).

the body, as body_loop.py builds it on the honest stack: NeuroMechFly, LEGS_ONLY joints, the springs --stiffness sourced (20 nN.m/rad),
limit_joints' ranges and the stiff limit solref, motor actuators on LEGS_ACTIVE_ONLY at +-60, the pads (gain 1) switched by the tarsal
contact force net of the pads (--adhesion contact --load-from tarsi), FlatGroundWorld at 0.5 mm, --start-pose feet (0.5 s on the springs
with no torque and no pad), then a 2 s warm-up (the targets ramp from the settled pose to the replay's first frame over 0.5 s, then hold),
then the replay from 2.0 s. saved: the arrays body_loop.py saves under the same names (thorax, quat, leg_force, knee, ground,
tarsal_force, other_leg_force, body_force, stand3, joints, joint_names, args) plus target (deg, per 10 ms, the actuated DOFs' targets in
all-DOF order, nan elsewhere), and an empty <out>.cells.npz so experiments/leg_pairs.py reads it (no neurons: pools print nan).

    uv run python experiments/kin_replay.py --out world/body/loop/kin_replay            (real speed)
    uv run python experiments/kin_replay.py --out world/body/loop/kin_replay_slow --playback-speed 0.2
"""
import os, sys, json, argparse, time, warnings, numpy as np
import mujoco as mj
from flygym.utils.math import Rotation3D
from flygym.compose import NeuroMechFly, FlatGroundWorld, ActuatorType, KinematicPosePreset
from flygym.anatomy import JointPreset, ActuatedDOFPreset, Skeleton, AxisOrder
from flygym import Simulation
from kin_clip import load_clip, loop_targets, clip_columns, target_at, position_law   # (09-23) the clip, the refit, the loop and the law, shared with body_loop.py --kin-drive

TAG = "KINEMATIC REPLAY"
ap = argparse.ArgumentParser()
ap.add_argument("--out", required=True)
ap.add_argument("--replay-seconds", type=float, default=10.0, help="seconds of replay after the warm-up (the run is --warmup + this)")
ap.add_argument("--warmup", type=float, default=2.0, help="seconds between the feet-down settle and the replay (the readers start at 2.0 / 2.1 s)")
ap.add_argument("--axis-order", default="pry", choices=["pry", "ypr"], help="pry: body_loop.py's skeleton, the recording re-expressed in it (default) | ypr: the recording's own order (a control)")
ap.add_argument("--kp", type=float, default=150.0, help="position gain in nN.m/rad (the model's torque unit; flygym's example: 150)")
ap.add_argument("--forcerange", type=float, default=60.0, help="torque clip per DOF (body_loop.py's actuator clip)")
ap.add_argument("--blend-ms", type=float, default=30.0, help="the loop seam's linear crossfade")
ap.add_argument("--stiffness", default="sourced", help="the joints' springs: sourced = 20 nN.m/rad (body_loop.py's honest stack), or a number")
ap.add_argument("--no-video", action="store_true"); ap.add_argument("--fps", type=int, default=25); ap.add_argument("--playback-speed", type=float, default=1.0)
args = ap.parse_args(); t0 = time.time()
STIFF = 2e-8 / 1e-9 if args.stiffness == "sourced" else float(args.stiffness)
args.KINEMATIC_REPLAY = (f"{TAG}: the Spotlight clip (flygym_demo spotlight_behavior_clip.npz, untethered fly, 330 Hz) replayed by position control, "
                         f"kp {args.kp:g}, clip {args.forcerange:g}, axis order {args.axis_order}; no neurons; a reference, not a result")
import builtins; _bprint = builtins.print
def print(*a, **k): _bprint("\n".join(f"{TAG} | " + ln for ln in " ".join(str(x) for x in a).split("\n")), **k)
print(args.KINEMATIC_REPLAY)
warnings.filterwarnings("ignore", message="Compiling a fly model")
LEG6 = ["lf", "lm", "lh", "rf", "rm", "rh"]
ORDER = AxisOrder.PITCH_ROLL_YAW if args.axis_order == "pry" else AxisOrder.YAW_PITCH_ROLL

# ---- the recording (steps 0-3 in experiments/kin_clip.py)
A, FPS, DPL, FIT, CLIP = load_clip("spotlight", args.axis_order, print=print)
dt_phys = 1e-4; n_ms = int(round((args.warmup + args.replay_seconds) * 1000))
TGT, n_rep, (E, nb, n0) = loop_targets(A, FPS, args.blend_ms, args.replay_seconds, dt_phys, print=print)

# ---- the body, as body_loop.py builds it
def limit_joints(jm, neutral_of):   # body_loop.py's, verbatim in effect
    for dof, j in jm.items():
        n = f"{dof.parent.name}->{dof.child.name}:{dof.axis.value}"; c = dof.child.name.split("_", 1)[1]
        span = 70.0 if c == "tibia" else 50.0 if (c == "trochanterfemur" and dof.axis.value == "pitch") else 45.0 if c in ("coxa", "trochanterfemur") else 40.0
        ref = float(neutral_of.get(n, 0.0)); j.range = (ref - np.radians(span), ref + np.radians(span)); j.limited = 1
fly = NeuroMechFly(); skel = Skeleton(axis_order=ORDER, joint_preset=JointPreset.LEGS_ONLY)
jm = fly.add_joints(skel, KinematicPosePreset.NEUTRAL, stiffness=STIFF); dofs = ActuatedDOFPreset.LEGS_ACTIVE_ONLY.filter(fly.get_jointdofs_order())
_pl = fly.get_pose_lookup(KinematicPosePreset.NEUTRAL); neutral_of = {"{}->{}:{}".format(*k.split("-")): float(v) for k, v in _pl.items() if k.count("-") == 2}
limit_joints(jm, neutral_of)
fly.add_actuators(dofs, ActuatorType.MOTOR, forcerange=(-60.0, 60.0)); adh = fly.add_leg_adhesion(gain=1.0)
if not args.no_video: fly.add_tracking_camera("trackcam")
world = FlatGroundWorld(); world.add_fly(fly, (0.0, 0.0, 0.5), Rotation3D(format="quat", values=(1, 0, 0, 0))); sim = Simulation(world); m = sim.mj_model; d = sim.mj_data
m.jnt_solref[:, 0] = 0.002; m.jnt_solimp[:, 0] = 0.99; m.jnt_solimp[:, 1] = 0.999   # body_loop.py's stiff joint limits
assert abs(m.opt.timestep - dt_phys) < 1e-12, m.opt.timestep
all_dofs = fly.get_jointdofs_order(); dof_name = lambda x: f"{x.parent.name}->{x.child.name}:{x.axis.value}"; all_idx = {dof_name(x): i for i, x in enumerate(all_dofs)}
act_all = np.array([all_idx[dof_name(x)] for x in dofs])
col = clip_columns(dofs, DPL); TGT = TGT[:, col]
lo_ = np.array([jm[x].range[0] for x in dofs]); hi_ = np.array([jm[x].range[1] for x in dofs]); out_ = (TGT < lo_) | (TGT > hi_)
print(f"the body: {ORDER.name}, springs {STIFF:g} nN.m/rad, limits as body_loop.py, {len(dofs)} actuated DOFs by position (kp {args.kp:g}, clip +-{args.forcerange:g}), pads on tarsal contact; "
      f"targets outside the joint limits: {out_.mean() * 100:.1f} % of samples (" + ", ".join(f"{dof_name(dofs[i])} {out_[:, i].mean() * 100:.0f}%" for i in np.flatnonzero(out_.mean(0) > 0.01)) + ")")
roles = json.load(open("results/body_dof_signs.json"))["roles"]
if args.axis_order == "pry": knee_idx = {l: all_idx[roles[l]["flex"]["dof"]] for l in LEG6}; knee_sign = {l: roles[l]["flex"]["sign"] for l in LEG6}
else: knee_idx = {l: all_idx[f"{l}_trochanterfemur->{l}_tibia:pitch"] for l in LEG6}; knee_sign = {l: 1.0 for l in LEG6}
knee_neutral = {l: float(np.degrees(neutral_of.get(dof_name(all_dofs[knee_idx[l]]), 0.0))) for l in LEG6}
weight = m.body_mass.sum() * abs(m.opt.gravity[2]); print(f"weight {weight:.2f} uN")
segs = [s.name for s in fly.get_bodysegs_order()]; thorax = segs.index("c_thorax")
TARS = [np.array([segs.index(f"{l}_tarsus{i}") for i in range(1, 6)]) for l in LEG6]
OTHL = [np.array([i for i, s_ in enumerate(segs) if s_.startswith(l + "_") and "_tarsus" not in s_]) for l in LEG6]
NONLEG = np.array([i for i, s_ in enumerate(segs) if not any(s_.startswith(l + "_") for l in LEG6)])
if not args.no_video: sim.set_renderer([c for c in [mj.mj_id2name(m, mj.mjtObj.mjOBJ_CAMERA, i) for i in range(m.ncam)] if "trackcam" in c][0], camera_res=(480, 640), playback_speed=args.playback_speed, output_fps=args.fps)
sim.reset(); spm = int(round(0.001 / m.opt.timestep))
sim.set_actuator_inputs("nmf", ActuatorType.MOTOR, np.zeros(len(dofs))); sim.set_leg_adhesion_states("nmf", np.zeros(6, bool))
for _ in range(int(round(0.5 / m.opt.timestep))): sim.step()   # --start-pose feet: 0.5 s on the springs, no torque, no pad
_cf0 = np.asarray(sim.get_bodysegment_contact_forces("nmf", segs)); q_set = np.asarray(sim.get_joint_angles("nmf"))[act_all].copy()
print(f"feet-down settle (0.5 s, no torque): thorax z {sim.get_body_positions('nmf')[thorax][2]:.3f} mm, tarsi {np.round([_cf0[TARS[i], 2].sum() for i in range(6)], 2)} uN")

# ---- the run: body_loop.py's per-ms bookkeeping, the torque per physics step
P = np.zeros((n_ms, 3), np.float32); Q = np.zeros((n_ms, 4), np.float32); FL = np.zeros((n_ms, 6), np.float32); KA = np.zeros((n_ms, 6), np.float32)
JA = np.zeros((n_ms // 10 + 1, len(all_dofs)), np.float32); TA = np.full((n_ms // 10 + 1, len(all_dofs)), np.nan, np.float32)
FT = np.zeros((n_ms, 6)); FO = np.zeros((n_ms, 6)); FB = np.zeros(n_ms); FTN = np.zeros((n_ms, 6), np.float32); BODYF = np.zeros((n_ms // 10 + 1, 2), np.float32)
pad_on = np.zeros(6, bool); w0 = int(args.warmup * 1000); ramp = min(500, w0); sat = np.zeros(len(dofs))
for ms in range(n_ms):
    ang = np.asarray(sim.get_joint_angles("nmf")); knee = np.array([(np.degrees(ang[knee_idx[l]]) - knee_neutral[l]) * knee_sign[l] for l in LEG6])
    found, forces, *_ = sim.get_ground_contact_info("nmf"); F = np.linalg.norm(np.asarray(forces), axis=1); F = np.maximum(F - 1.0 * pad_on, 0.0)
    _cf = np.asarray(sim.get_bodysegment_contact_forces("nmf", segs)); FT[ms] = [_cf[TARS[i], 2].sum() for i in range(6)]; FO[ms] = [_cf[OTHL[i], 2].sum() for i in range(6)]; FB[ms] = np.abs(_cf[NONLEG, 2]).sum()
    FTN[ms] = np.maximum(FT[ms] - 1.0 * pad_on, 0.0); KA[ms] = knee; FL[ms] = F
    pad_on = FTN[ms] > 0.05; sim.set_leg_adhesion_states("nmf", pad_on)   # --adhesion contact --load-from tarsi
    if ms % 10 == 0: JA[ms // 10] = np.degrees(ang)
    for s in range(spm):
        tgt = target_at(TGT, q_set, ms, s, spm, w0, ramp, n_rep)
        if s == 0 and ms % 10 == 0: TA[ms // 10, act_all] = np.degrees(tgt)
        q = np.asarray(sim.get_joint_angles("nmf"))[act_all]; u, uc = position_law(args.kp, args.forcerange, tgt, q); sat += (np.abs(u) >= args.forcerange) & (ms >= w0)
        sim.set_actuator_inputs("nmf", ActuatorType.MOTOR, uc); sim.step()
    P[ms] = sim.get_body_positions("nmf")[thorax]; Q[ms] = sim.get_body_rotations("nmf")[thorax]
    if ms % 10 == 0:
        _cf = np.asarray(sim.get_bodysegment_contact_forces("nmf", segs)); BODYF[ms // 10] = (float(F.sum()), float(np.abs(_cf[NONLEG, 2]).sum()))
    if not args.no_video: sim.render_as_needed()
    if ms % 2000 == 0 and ms: print(f"t={ms / 1000:5.1f}s thorax z {P[ms, 2]:.2f}  x {P[ms, 0]:+.2f}  tarsi {np.round(FTN[ms], 1)}  ({time.time() - t0:.0f}s)")
os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True); nfr = n_ms // 10
np.savez_compressed(args.out + ".cells.npz", cells=np.zeros(0, np.int64), bodyId=np.zeros(0, np.int64), type=np.zeros(0, "<U1"), side=np.zeros(0, "<U1"), counts=np.zeros((nfr // 10, 0), np.int32), frames=np.zeros((nfr, 0), np.int16), note=np.array(f"{TAG}: no neurons"))
np.savez_compressed(args.out + ".npz", thorax=P, quat=Q, leg_force=FL, knee=KA, ground=BODYF[:nfr], tarsal_force=FTN, other_leg_force=FO.astype(np.float32), body_force=FB.astype(np.float32),
                    stand3=np.stack([FTN.sum(1), FO.sum(1), FB], 1)[::10][:nfr].astype(np.float32), joints=JA[:nfr], target=TA[:nfr], joint_names=np.array([dof_name(x) for x in all_dofs]), args=np.array(str(vars(args))),
                    replay_loop=np.array([E, nb, n0]), **FIT)
ach = JA[w0 // 10: nfr][:, act_all]; tar = TA[w0 // 10: nfr][:, act_all]; te = np.abs(ach - tar)
print(f"tracking after {args.warmup:g} s: |achieved - target| median {np.median(te):.1f} deg, p95 {np.percentile(te, 95):.1f}; achieved sd / target sd over the 42 DOFs {np.median(ach.std(0) / np.maximum(tar.std(0), 1e-6)):.2f} (median); torque at the clip {sat.sum() / (len(dofs) * args.replay_seconds * 1e4) * 100:.1f} % of DOF-steps")
_ft = FTN[w0:].sum(1).mean(); _fo = np.nanmean(FO[w0:].sum(1)); _fb = np.nanmean(FB[w0:])
print(f"standing? feet {_ft:.2f} / other leg segments {_fo:.2f} / body {_fb:.2f} uN of {weight:.2f}; per-leg tarsal load {np.round(FTN[w0:].mean(0), 2)}")
v = np.linalg.norm(np.diff(P[w0:, :2], axis=0), axis=1) * 1000; print(f"done in {time.time() - t0:.0f}s; thorax z mean {P[w0:, 2].mean():.2f}, |v| {v.mean():.1f} mm/s, net x {P[-1, 0] - P[w0, 0]:+.2f} mm, y {P[-1, 1] - P[w0, 1]:+.2f} mm")
if not args.no_video: sim.renderer.save_video(args.out + ".mp4"); print("video", args.out + ".mp4")
print("wrote", args.out + ".npz")
