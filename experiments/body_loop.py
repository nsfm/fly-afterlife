"""body_loop.py - the loop on six legs: the headless cord and the NeuroMechFly body in one process at 1 ms (§Q 4e stage 3).

the cord drives the body as experiments/body_six.py does (the type-name map to measured joint roles, the twitch kernel, force by
synapse size, the derived torque), and the body drives the cord's own leg sensory cells, per leg:
  knee angle    -> the femoral chordotonal organ's claw cells (SNpp50 extension-tuned, SNpp51 flexion-tuned; 0-100 Hz over 60 deg (E))
  knee velocity -> the hook cells (SNpp39 flexion / SNpp41 extension; 100 Hz at 300 deg/s (E))
  load          -> the leg's other proprioceptors (hair plates, campaniforms, the untyped): rate = load_hz x clip(F / F_stand), F the leg's
                   ground contact force from the body, F_stand = the body's weight / 6 (E; the campaniform brief says dF/dt bursts: next)
the standing tonus stand-in (docs/ASK.md, option a; off unless --slow-hz > 0): the 93 smallest leg motor neurons (under 178 input
synapses, the slow units by the size rule, which the file leaves without wiring) held at --slow-hz x clip(F / F_stand) on their leg: a
labelled gap in the map, with the load coming from the body. everything else is his.
arms: --loop off | position | load | position+load; --slow-hz for the stand-in; --stiffness 0.14 for the measured springs.

    uv run python experiments/body_loop.py --walk 100 --loop position+load --stiffness 0.14 --seconds 20 --out world/body/loop/posload
"""
import os, sys, json, argparse, time, numpy as np
sys.path.insert(0, "ref/flybrain/scripts"); sys.path.insert(0, "world"); sys.path.insert(0, "src")
from flysim import Params
from fastlif import FastFlyBrain
from fly_afterlife.receptors import Registry, ReceptorClass, Scaled, Transducer, tonic_floor
import mujoco as mj
from flygym.utils.math import Rotation3D
from flygym.compose import NeuroMechFly, FlatGroundWorld, ActuatorType, KinematicPosePreset
from flygym.anatomy import JointPreset, ActuatedDOFPreset, Skeleton, AxisOrder
from flygym import Simulation

ap = argparse.ArgumentParser()
ap.add_argument("--out", required=True); ap.add_argument("--seconds", type=float, default=20.0); ap.add_argument("--seed", type=int, default=11)
ap.add_argument("--wsyn-m", type=float, default=0.185); ap.add_argument("--noise", type=float, default=0.15)
ap.add_argument("--walk", type=float, default=100.0); ap.add_argument("--walk-dn", default="DNg100"); ap.add_argument("--std", default="off"); ap.add_argument("--mirror", default="off")
ap.add_argument("--leg-load-hz", type=float, default=15.0); ap.add_argument("--loop", default="position+load", help="off | position | load | position+load")
ap.add_argument("--claw-hz", type=float, default=100.0); ap.add_argument("--hook-hz", type=float, default=100.0); ap.add_argument("--hook-vel", type=float, default=300.0)
ap.add_argument("--slow-hz", type=float, default=0.0, help="the standing-tonus stand-in: the 93 smallest leg MNs held at this rate x their leg's load (0 = off)")
ap.add_argument("--slow-set", default="size", help="which cells the standing-tonus stand-in holds: stance_all (every motor neuron of the stance muscles regardless of size: the load-scaled tonus of docs/ASK.md (a), a stand-in for the slow-unit reflex on cells the size rule calls fast, labelled) | size (the 93 smallest leg MNs: measured to be the accessory flexors, a flexion tonus) | extensor (the stance muscles' motor neurons below the median input size, per leg: sternotrochanter, trochanter extensor, tibia extensor, pleural remotor, sternal posterior rotator; the standing tonus as life has it, on the slow members of the anti-gravity muscles (E))")
ap.add_argument("--load-deriv", type=float, default=0.0, help="a rate-sensitive term on the load signal (the campaniform brief, Szczecinski 2021: campaniforms report dF/dt as well as F): the load rows and the stance tonus get clip(F/F_stand + G x dF/dt x 50 ms / F_stand, 0, 2), so unloading a leg cuts its stance drive before the load is gone and loading it adds; 0 = off (E)")
ap.add_argument("--cocon", type=float, default=0.0, help="co-contraction: the swing muscles' motor neurons (trochanter flexors, tibia flexors, promotors, anterior rotators) held at this fraction of the stance tonus rate x load, so each joint is stiff mid-range instead of driven to its limit (standing in life is co-contraction; nate 09-22: the front legs are struts); 0 = extensors only")
ap.add_argument("--adhesion", default="ltm", help="how the feet grip: ltm (the long tendon muscles' motor neurons, the honest hookup; unwired in this file, so never on) | contact (a labelled stand-in for the pulvilli's passive adhesion: a loaded foot sticks, an unloaded one releases; Ramdya lab convention: adhesion during stance) | off")
ap.add_argument("--adhesion-gain", type=float, default=1.0, help="adhesion force per foot in the model's uN (flygym's default actuator gain 1; a fly's pads hold several body weights)")
ap.add_argument("--dn-playback", default="", help="drive the cord's descending neurons with the brain's own descending output as a recording: a whole-fly run's <run>.cells.npz with every DN type logged per chunk (100 ms); each DN cell in the cord is held at its own measured rate in that chunk, chunk by chunk (the headless preparation with the real channels; nate 09-22: not a head, a recording of one). replaces --walk / --walk-dn")
ap.add_argument("--playback-start", type=float, default=2.0, help="seconds into the recording to start (after its warm-up)")
ap.add_argument("--graded", default="", help="graded (non-spiking) units as in world/cord.py: PREFIXES:GAIN[:V1] or random:N:GAIN")
ap.add_argument("--slow-init", type=float, default=0.0, help="set him down standing: for this many seconds after the warm-up the load term is clamped to at least standing (F_stand) on every leg, so the load reflex and the stand-in start engaged; then the body's own load. an initial condition, labelled (0 = off)")
ap.add_argument("--gain", type=float, default=42.0); ap.add_argument("--sat", type=float, default=10.0); ap.add_argument("--alpha", type=float, default=1.2); ap.add_argument("--stiffness", type=float, default=None)
ap.add_argument("--tethered", action="store_true", help="the tethered preparation (nate, 09-22: propped up): the thorax fixed in space, the legs free, no floor and no load; the position loop still closes"); ap.add_argument("--gravity", type=float, default=1.0, help="scale on gravity (0.1 = a tenth of his weight; a graded prop-up, diagnostic)")
ap.add_argument("--warmup", type=float, default=2.0); ap.add_argument("--no-video", action="store_true"); ap.add_argument("--fps", type=int, default=25)
args = ap.parse_args(); t0 = time.time(); use_pos = "position" in args.loop; use_load = "load" in args.loop

# ---- the cord
M = FastFlyBrain("brain_cord.npz", seed=args.seed, params=Params(mv_per_synapse=args.wsyn_m, noise=args.noise)); M.integrate = "exact"
mty = M.type.astype(str); mns = M.side.astype(str); mbid = M.bodyId; pos = {int(b): i for i, b in enumerate(mbid)}
if args.mirror != "off":
    from fly_afterlife.wiring import mirror_normalise; print("mirror:", mirror_normalise(M, scope=args.mirror))
if args.std != "off":
    _mask = np.ones(M.N, bool) if args.std == "all" else (mty == "DNg33") if args.std == "pair" else np.isin(mty, args.std.split(",")); M._std_mask = _mask; M._std_x = np.ones(M.N, np.float32); M.std_on = True
if args.graded:
    parts = args.graded.split(":")
    if parts[0] == "random": n_ = int(parts[1]); g_ = float(parts[2]); rng_ = np.random.default_rng(args.seed + 7); cand = np.flatnonzero(np.char.startswith(mty, "IN")); gc = np.sort(rng_.choice(cand, n_, replace=False)); label = f"random {n_}"
    else: pref = parts[0].split(","); g_ = float(parts[1]); gc = np.flatnonzero(np.any([np.char.startswith(mty, p_) for p_ in pref], axis=0)); label = ",".join(pref)
    v1 = float(parts[-1]) if len(parts) > (3 if parts[0] == "random" else 2) else float(M.p.v_thresh)
    M.graded_on = True; M._graded_cells = gc.astype(np.int64); M.graded_gain = g_; M.graded_v0 = 0.0; M.graded_v1 = v1; M._graded_idx = np.zeros(0, np.int64); M._graded_scale = np.zeros(0, np.float32); M.v_th[gc] = np.float32(1e6)
    print(f"graded units: {len(gc)} cells ({label}), gain {g_} per ms at v = {v1} mV")
REG = Registry(); PB = None
if args.dn_playback:
    _C = np.load(args.dn_playback.replace(".npz", "") + ".cells.npz", allow_pickle=True); _cnt = _C["counts"].astype(np.float32) * 10.0   # Hz per cell per 100 ms chunk
    _idx = np.array([pos.get(int(b_), -1) for b_ in _C["bodyId"]]); _ok = _idx >= 0; PB = dict(cells=_idx[_ok], hz=_cnt[:, _ok], n=_cnt.shape[0]); WALK = PB["cells"]
    class Playback(Transducer):
        def __init__(self): self.source = "the brain's descending output, recorded from the whole fly (a recording, not a head)"
        def step(self, stim, t, dt): return stim
    REG.add(ReceptorClass("dn_playback", PB["cells"], Playback(), lambda st: st["dn_hz"]))
    print(f"descending playback: {len(PB['cells'])} of {len(_idx)} logged DN cells found in the cord; {PB['n'] / 10:.0f} s recorded; mean rate {_cnt[:, _ok].mean():.1f} Hz per cell")
else:
    _wd = args.walk_dn.split(","); WALK = np.flatnonzero(np.isin(mty, _wd) & (M.sc.astype(str) == "descending_neuron")) if args.walk > 0 else np.zeros(0, np.int64)
    if len(WALK): REG.add(ReceptorClass("walk", WALK, Scaled(args.walk), lambda st: st["walk_gain"]))
_fl = tonic_floor(M, REG)
for rc in _fl:
    if rc.name == "floor_leg_proprio": rc.transducer.hz = args.leg_load_hz
wb = np.load("brain_whole.npz", allow_pickle=True); wbid = wb["bodyId"]; legs = np.load("world/legs.npz"); lm = np.load("world/legmn.npz")
LEG6 = ["lf", "lm", "lh", "rf", "rm", "rh"]; SENS = {"lf": "L1", "lm": "L2", "lh": "L3", "rf": "R1", "rm": "R2", "rh": "R3"}
class Rate(Transducer):
    def __init__(self, key): self.key = key; self.source = "body_loop: a rate from the body (E)"
    def step(self, stim, t, dt): return float(stim)
sens = {}
for leg in LEG6:
    cells = np.array([pos[int(wbid[i])] for i in legs[SENS[leg]] if int(wbid[i]) in pos], np.int64)
    of = lambda types: cells[np.isin(mty[cells], types)]
    sens[leg] = dict(claw_e=of(["SNpp50"]), claw_f=of(["SNpp51"]), hook_f=of(["SNpp39"]), hook_e=of(["SNpp41"]), load=cells[~np.isin(mty[cells], ["SNpp50", "SNpp51", "SNpp39", "SNpp41"])])
    if use_pos:
        for k in ("claw_e", "claw_f", "hook_f", "hook_e"):
            if len(sens[leg][k]): REG.add(ReceptorClass(f"{k}_{leg}", sens[leg][k], Rate(k), (lambda kk: (lambda st: st[kk]))(f"{k}_{leg}")))
    if use_load and len(sens[leg]["load"]): REG.add(ReceptorClass(f"load_{leg}", sens[leg]["load"], Rate("load"), (lambda kk: (lambda st: st[kk]))(f"load_{leg}")))
print("sensory cells per leg:", {l: {k: len(v) for k, v in sens[l].items()} for l in LEG6})
# the leg motor neurons, their legs, the small (slow) quarter
legof = {}
for g, L in (("fl", "f"), ("ml", "m"), ("hl", "h")):
    for s in "LR":
        for i in lm[f"{g}_{s}"]:
            if int(wbid[i]) in pos: legof[pos[int(wbid[i])]] = s.lower() + L
LEGMN = np.array(sorted(legof)); insyn = np.bincount(M._out_tgt, weights=np.abs(M._out_w), minlength=M.N) / M.p.mv_per_synapse
q25 = np.quantile(insyn[LEGMN], 0.25); SLOW = LEGMN[insyn[LEGMN] < q25]
if args.slow_set == "stance_all":
    STANCE = ("Sternotrochanter MN", "Tr extensor MN", "Ti extensor MN", "Pleural remotor/abductor MN", "Sternal posterior rotator MN"); SLOW = np.array([j for j in LEGMN if mty[j] in STANCE], np.int64)
if args.slow_set == "extensor":
    STANCE = ("Sternotrochanter MN", "Tr extensor MN", "Ti extensor MN", "Pleural remotor/abductor MN", "Sternal posterior rotator MN"); q50 = np.quantile(insyn[LEGMN], 0.5)
    SLOW = np.array([j for j in LEGMN if mty[j] in STANCE and insyn[j] < q50], np.int64)
if args.slow_hz > 0:
    for leg in LEG6:
        cells = np.array([j for j in SLOW if legof[j] == leg], np.int64)
        if len(cells): REG.add(ReceptorClass(f"slow_{leg}", cells, Rate("slow"), (lambda kk: (lambda st: st[kk]))(f"slow_{leg}"), source="the standing-tonus stand-in (docs/ASK.md a): slow units held at a load-scaled rate; labelled"))
    print(f"standing-tonus stand-in ({args.slow_set}): {len(SLOW)} leg MNs at {args.slow_hz} Hz x load; types {sorted(set(mty[SLOW]))}")
    if args.cocon > 0:
        SWING = ("Tr flexor MN", "Acc. tr flexor MN", "Ti flexor MN", "Acc. ti flexor MN", "Tergopleural/Pleural promotor MN", "Sternal anterior rotator MN")
        for leg in LEG6:
            cells = np.array([j for j in LEGMN if mty[j] in SWING and legof[j] == leg], np.int64)
            if len(cells): REG.add(ReceptorClass(f"cocon_{leg}", cells, Rate("cocon"), (lambda kk: (lambda st: st[kk]))(f"cocon_{leg}"), source="co-contraction stand-in (09-22): the swing muscles at a fraction of the stance tonus; labelled"))
        print(f"co-contraction: the swing muscles at {args.cocon} x the stance tonus")
M.driven[:] = False
for cl in M.SENSORY_CLASSES: M.driven[M.cls == cl] = True
for rc in REG.classes: M.driven[rc.cells] = True
M._driven_idx = np.flatnonzero(M.driven); M.reset()

# ---- the body
ROLE = {"Tergopleural/Pleural promotor MN": ("protract", +1), "Sternal anterior rotator MN": ("protract", +1), "Pleural remotor/abductor MN": ("protract", -1), "Sternal posterior rotator MN": ("protract", -1),
        "Tr flexor MN": ("levate", +1), "Acc. tr flexor MN": ("levate", +1), "Sternotrochanter MN": ("levate", -1), "Tr extensor MN": ("levate", -1),
        "Ti flexor MN": ("flex", +1), "Acc. ti flexor MN": ("flex", +1), "Ti extensor MN": ("flex", -1),
        "Ta levator MN": ("tarsus_levate", +1), "MNml81": ("tarsus_levate", +1), "MNhl65": ("tarsus_levate", +1), "Ta depressor MN": ("tarsus_levate", -1),
        "Sternal adductor MN": ("adduct", +1), "ltm MN": ("grip", +1), "ltm1-tibia MN": ("grip", +1), "ltm2-femur MN": ("grip", +1)}
roles = json.load(open("results/body_dof_signs.json"))["roles"]
def limit_joints(jm, neutral_of):
    """joint ranges about the neutral pose, (E): knee +-70 deg, trochanter pitch +-50, coxa +-45, tarsus +-40 (the brief's C gives measured
    ranges per joint from Karashchuk 2021; these are the coarse first cut). the body ships its hinges unlimited, and a torqued unlimited hinge winds up."""
    import numpy as _np
    for dof, j in jm.items():
        n = f"{dof.parent.name}->{dof.child.name}:{dof.axis.value}"; c = dof.child.name.split("_", 1)[1]
        span = 70.0 if c == "tibia" else 50.0 if (c == "trochanterfemur" and dof.axis.value == "pitch") else 45.0 if c in ("coxa", "trochanterfemur") else 40.0
        ref = float(neutral_of.get(n, 0.0)); j.range = (ref - _np.radians(span), ref + _np.radians(span)); j.limited = 1
fly = NeuroMechFly(); skel = Skeleton(axis_order=AxisOrder.PITCH_ROLL_YAW, joint_preset=JointPreset.LEGS_ONLY)
jm = fly.add_joints(skel, KinematicPosePreset.NEUTRAL, **({} if args.stiffness is None else dict(stiffness=args.stiffness))); dofs = ActuatedDOFPreset.LEGS_ACTIVE_ONLY.filter(fly.get_jointdofs_order())
_pl = fly.get_pose_lookup(KinematicPosePreset.NEUTRAL) if hasattr(fly, 'get_pose_lookup') else {}
neutral_of = {"{}->{}:{}".format(*k.split("-")): float(v) for k, v in (_pl.items() if isinstance(_pl, dict) else []) if k.count("-") == 2}
limit_joints(jm, neutral_of)
fly.add_actuators(dofs, ActuatorType.MOTOR, forcerange=(-60.0, 60.0)); adh = fly.add_leg_adhesion(gain=args.adhesion_gain)
if not args.no_video: fly.add_tracking_camera("trackcam")
from flygym.compose import TetheredWorld
world = TetheredWorld() if args.tethered else FlatGroundWorld(); world.add_fly(fly, (0.0, 0.0, 2.0 if args.tethered else 0.5), Rotation3D(format="quat", values=(1, 0, 0, 0))); sim = Simulation(world); m = sim.mj_model; d = sim.mj_data
m.opt.gravity[2] *= args.gravity
m.jnt_solref[:, 0] = 0.002; m.jnt_solimp[:, 0] = 0.99; m.jnt_solimp[:, 1] = 0.999   # stiff joint limits: the defaults (20 ms, 0.95) let a full torque spin a knee through 1,600 deg (09-22); this holds it within ~8 deg. a solver setting, not physiology
all_dofs = fly.get_jointdofs_order(); dof_name = lambda x: f"{x.parent.name}->{x.child.name}:{x.axis.value}"; all_idx = {dof_name(x): i for i, x in enumerate(all_dofs)}
knee_idx = {leg: all_idx[roles[leg]["flex"]["dof"]] for leg in LEG6}; knee_sign = {leg: roles[leg]["flex"]["sign"] for leg in LEG6}
cell_dof = {}; cell_sgn = {}; grip_of = {}; groups = {}
for j in LEGMN:
    if mty[j] not in ROLE: continue
    role, ag = ROLE[mty[j]]
    if role == "grip": grip_of[j] = legof[j]; continue
    r = roles[legof[j]][role]; cell_dof[j] = r["k"]; cell_sgn[j] = r["sign"] * ag; groups.setdefault((legof[j], role, ag), []).append(j)
f_w = {}
for key, js in groups.items():
    smax = max(insyn[js]) or 1.0
    for j in js: f_w[j] = (insyn[j] / smax) ** args.alpha if insyn[j] > 0 else 0.1
KL = 120; tk = np.arange(KL); K = np.exp(-tk / 20.0) - np.exp(-tk / 7.0); K /= K.max()
weight = m.body_mass.sum() * abs(m.opt.gravity[2]); F_stand = max(weight / 6.0, 1e-6); print(f"gravity x{args.gravity}: weight {weight:.2f} uN, F_stand {F_stand:.2f}")
segs = [s.name for s in fly.get_bodysegs_order()]; thorax = segs.index("c_thorax")
if not args.no_video: sim.set_renderer([c for c in [mj.mj_id2name(m, mj.mjtObj.mjOBJ_CAMERA, i) for i in range(m.ncam)] if "trackcam" in c][0], camera_res=(480, 640), playback_speed=1.0, output_fps=args.fps)
sim.reset(); steps_per_ms = int(round(0.001 / m.opt.timestep))
def leg_forces():
    """ground contact force magnitude per leg (model force units = uN), legs ordered lf lm lh rf rm rh (fly.get_legs_order())."""
    if args.tethered: return np.zeros(6)
    found, forces, *_ = sim.get_ground_contact_info("nmf"); return np.linalg.norm(np.asarray(forces), axis=1)

# ---- the loop
n_ms = int(args.seconds * 1000); torque = np.zeros((len(dofs), n_ms + KL)); grip = {l: np.zeros(n_ms + KL) for l in LEG6}
P = np.zeros((n_ms, 3), np.float32); Q = np.zeros((n_ms, 4), np.float32); FL = np.zeros((n_ms, 6), np.float32); KA = np.zeros((n_ms, 6), np.float32)
JA = np.zeros((n_ms // 10 + 1, len(all_dofs)), np.float32)
spk = np.zeros((n_ms // 10 + 1, len(LEGMN)), np.int16); lpos = {int(j): i for i, j in enumerate(LEGMN)}
state = {"walk_gain": 0.0}; prev_knee = None; force_ok = True; Fsm = np.zeros(6); prevF = np.zeros(6)
for ms in range(n_ms):
    t = ms / 1000.0; state["walk_gain"] = 1.0 if t >= args.warmup else 0.0
    if PB is not None:
        ch = int((args.playback_start + max(t - args.warmup, 0.0)) * 10) if t >= args.warmup else -1; state["dn_hz"] = PB["hz"][min(ch, PB["n"] - 1)] if ch >= 0 else np.zeros(len(PB["cells"]), np.float32)
    ang = sim.get_joint_angles("nmf"); knee = np.array([np.degrees(ang[knee_idx[l]]) * knee_sign[l] for l in LEG6]); om = np.zeros(6) if prev_knee is None else (knee - prev_knee) * 1000.0; prev_knee = knee
    F = leg_forces() if (use_load or args.slow_hz > 0) else np.zeros(6)
    if np.isnan(F).any(): F = np.zeros(6); force_ok = False
    Fsm = F if ms == 0 else 0.8 * Fsm + 0.2 * F; dF = (Fsm - prevF) * 1000.0 if ms else np.zeros(6); prevF = Fsm.copy()
    for i, leg in enumerate(LEG6):
        k = knee[i]; state[f"claw_e_{leg}"] = args.claw_hz * float(np.clip((-k) / 60.0, 0, 1)); state[f"claw_f_{leg}"] = args.claw_hz * float(np.clip(k / 60.0, 0, 1))   # + = flexion by the measured sign
        state[f"hook_f_{leg}"] = args.hook_hz * float(np.clip(om[i] / args.hook_vel, 0, 1)); state[f"hook_e_{leg}"] = args.hook_hz * float(np.clip(-om[i] / args.hook_vel, 0, 1))
        ld = float(np.clip(F[i] / F_stand + args.load_deriv * dF[i] * 0.05 / F_stand, 0, 2))
        if args.slow_init > 0 and t < args.warmup + args.slow_init: ld = max(ld, 1.0)
        state[f"load_{leg}"] = args.leg_load_hz * ld; state[f"slow_{leg}"] = args.slow_hz * ld; state[f"cocon_{leg}"] = args.cocon * args.slow_hz * ld
    KA[ms] = knee; FL[ms] = F
    if ms % 10 == 0: JA[ms // 10] = np.degrees(ang)
    REG.apply(M, state, t, 0.001); M.step(); idx = M.last_idx
    if idx.size:
        hit = idx[np.isin(idx, LEGMN)]
        for j in hit:
            j = int(j); spk[ms // 10, lpos[j]] += 1
            if j in grip_of: grip[grip_of[j]][ms: ms + KL] += f_w.get(j, 0.1) * K / args.sat
            elif j in cell_dof: torque[cell_dof[j], ms: ms + KL] += cell_sgn[j] * f_w[j] * K / args.sat
    tq = np.clip(args.gain * torque[:, ms], -60, 60); sim.set_actuator_inputs("nmf", ActuatorType.MOTOR, tq)
    if adh and args.adhesion == "ltm": sim.set_leg_adhesion_states("nmf", np.array([grip[l][ms] > 0.05 for l in LEG6]))
    elif adh and args.adhesion == "contact": sim.set_leg_adhesion_states("nmf", F > 0.05)
    elif adh: sim.set_leg_adhesion_states("nmf", np.zeros(6, bool))
    for _ in range(steps_per_ms): sim.step()
    P[ms] = sim.get_body_positions("nmf")[thorax]; Q[ms] = sim.get_body_rotations("nmf")[thorax]
    if not args.no_video: sim.render_as_needed()
    if ms % 5000 == 0 and ms: print(f"t={t:5.1f}s thorax z {P[ms, 2]:.2f}  legs F {np.round(F, 1)}  knees {np.round(knee, 0)}  ({time.time() - t0:.0f}s)")
os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
nfr = n_ms // 10; frames = spk[:nfr]
np.savez_compressed(args.out + ".cells.npz", cells=LEGMN, bodyId=mbid[LEGMN], type=mty[LEGMN], side=mns[LEGMN], counts=frames[: (nfr // 10) * 10].reshape(nfr // 10, 10, -1).sum(1).astype(np.int32), pose_chunk=np.zeros((nfr // 10, 3), np.float32), frames=frames, pose_frame=np.zeros((nfr, 3), np.float32))
w_, x_, y_, z_ = Q[:, 0], Q[:, 1], Q[:, 2], Q[:, 3]; yaw = np.degrees(np.arctan2(2 * (w_ * z_ + x_ * y_), 1 - 2 * (y_ ** 2 + z_ ** 2)))
np.savez_compressed(args.out + ".npz", thorax=P, quat=Q, leg_force=FL, knee=KA, joints=JA[: n_ms // 10], joint_names=np.array([dof_name(x) for x in all_dofs]), args=np.array(str(vars(args))))
w0 = int(args.warmup * 1000); v = np.linalg.norm(np.diff(P[w0:, :2], axis=0), axis=1) * 1000; hz = frames[w0 // 10:].mean(0) * 100
flex = np.array([("Ti flexor" in t_) or ("Acc. ti flexor" in t_) for t_ in mty[LEGMN]]); ext = mty[LEGMN] == "Ti extensor MN"
print(f"done in {time.time() - t0:.0f}s ({args.seconds / (time.time() - t0):.2f}x real time); contact forces {'read' if force_ok else 'UNAVAILABLE (load rows got 0)'}; after the warm-up: leg MN {hz.mean():.2f} Hz/cell, flexors {hz[flex].mean():.2f}, extensors {hz[ext].mean():.2f}; "
      f"thorax height mean {P[w0:, 2].mean():.2f} (min {P[w0:, 2].min():.2f}), speed {v.mean():.1f} mm/s, net turn {((yaw[-1] - yaw[w0] + 180) % 360) - 180:+.0f} deg; leg forces mean {np.round(FL[w0:].mean(0), 1)} (F_stand {F_stand:.2f}); knee sd {np.round(KA[w0:].std(0), 0)}")
if not args.no_video: sim.renderer.save_video(args.out + ".mp4"); print("video", args.out + ".mp4")
print("wrote", args.out + ".npz")
