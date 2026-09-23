"""kin_clip.py - the recorded clip and the position law, shared by experiments/kin_replay.py (KINEMATIC REPLAY) and experiments/body_loop.py
--kin-drive (KIN-DRIVE): one copy of the code, so the two cannot drift. kin_replay.py's docstring says what each step is and why; in brief:

  load_clip      the recording (flygym_demo's spotlight_behavior_clip.npz, or another file of the same layout), SeqIKPy's right-leg roll / yaw
                 flipped to flygym's convention, and (axis order pry) each thorax-coxa orientation refit into our PITCH_ROLL_YAW order within
                 the body's coxa limits (neutral +-45 deg), the residuals printed per leg
  loop_targets   Savitzky-Golay (30 ms, order 3), the loop cut at the pose closest to frame 0 in the last fifth, the seam crossfaded, tiled,
                 cubic-upsampled to the physics step: (n_rep, 42) targets in the recording's (leg, dof) order
  clip_columns   the recording's column for each actuated DOF of the body
  target_at      the target at physics step s of ms: before w0 a linear ramp from the settled pose to the first frame over `ramp` ms, then hold;
                 from w0 the replay
  position_law   torque = clip(kp x (target - angle), +-forcerange): MuJoCo's position actuator law (kv 0), applied by hand on motor actuators
  swing_from_foot  (--kin-drive only) the imposed swing per ms and leg from the feet's motion relative to the thorax
"""
import numpy as np
import mujoco as mj
from scipy.signal import savgol_filter
from scipy.interpolate import interp1d
from scipy.optimize import least_squares
from importlib.resources import files
from flygym.compose import NeuroMechFly, KinematicPosePreset
from flygym.anatomy import JointPreset, Skeleton, AxisOrder

LEG6 = ["lf", "lm", "lh", "rf", "rm", "rh"]
SPOTLIGHT = files("flygym_demo.spotlight_data") / "assets/spotlight_behavior_clip.npz"


def clip_path(name):
    """'spotlight' (or '') = flygym_demo's Spotlight clip; anything else is a path to an .npz of the same layout."""
    return SPOTLIGHT if name in ("", "spotlight") else name


def _jname(l, p, c, ax): return f"{'c_thorax' if p == 'thorax' else l + '_' + p}-{l}_{c}-{ax}"


def _compiled(order):
    f = NeuroMechFly(); f.add_joints(Skeleton(axis_order=order, joint_preset=JointPreset.LEGS_ONLY), KinematicPosePreset.NEUTRAL); m, d = f.compile()
    return m, d, {mj.mj_id2name(m, mj.mjtObj.mjOBJ_JOINT, i): int(m.jnt_qposadr[i]) for i in range(m.njnt)}


def load_clip(clip, axis_order="pry", print=print):
    """steps 0-1: returns A (frames, 6, 7) in radians, in the body's axis order when axis_order == 'pry'; FPS; DPL (the per-leg dof tuples);
    FIT (the refit's residual arrays, {} for ypr); the clip's path."""
    CLIP = clip_path(clip)
    Z = np.load(str(CLIP), allow_pickle=True); A = Z["joint_angles"].astype(float).copy(); FPS = float(Z["data_fps"]); DPL = [tuple(x) for x in Z["dofs_per_leg"].tolist()]; ZL = Z["legs"].tolist()
    assert ZL == LEG6, ZL
    for li, l in enumerate(LEG6):   # SeqIKPy's global convention -> flygym's anatomical one (MotionSnippet._apply_global2anatomical)
        if l[0] == "r":
            for k, (_, _, ax) in enumerate(DPL):
                if ax in ("roll", "yaw"): A[:, li, k] *= -1
    print(f"the recording: {CLIP.name if hasattr(CLIP, 'name') else CLIP}, trial {Z['experiment_trial']}, frames {Z['framerange_in_raw_recording'].tolist()} of the raw recording, {len(A)} frames at {FPS:g} Hz ({len(A) / FPS:.2f} s), {A.shape[1] * A.shape[2]} angles")
    if axis_order != "pry": return A, FPS, DPL, {}, CLIP
    # step 1: re-express each thorax-coxa orientation in our order, bounded to our coxa limits
    my, dy, Jy = _compiled(AxisOrder.YAW_PITCH_ROLL); mp, dp, Jp = _compiled(AxisOrder.PITCH_ROLL_YAW)
    bid = lambda m, n: mj.mj_name2id(m, mj.mjtObj.mjOBJ_BODY, n)
    dy.qpos[:] = my.key_qpos[0]; dp.qpos[:] = mp.key_qpos[0]; rng = np.random.default_rng(0)
    AX = ("pitch", "roll", "yaw"); qn = {l: np.array([mp.key_qpos[0][Jp[f"c_thorax-{l}_coxa-{a}"]] for a in AX]) for l in LEG6}; qprev = {l: qn[l].copy() for l in LEG6}
    B = np.zeros((len(A), 6, 7)); ferr = np.zeros((len(A), 6)); aerr = np.zeros((len(A), 6))
    for fr in range(len(A)):
        for li, l in enumerate(LEG6):
            for k, (p, c, ax) in enumerate(DPL):
                dy.qpos[Jy[_jname(l, p, c, ax)]] = A[fr, li, k]
                if p != "thorax": dp.qpos[Jp[_jname(l, p, c, ax)]] = A[fr, li, k]; B[fr, li, k] = A[fr, li, k]
        mj.mj_kinematics(my, dy)
        for li, l in enumerate(LEG6):
            cb = bid(mp, f"{l}_coxa"); tgt = dy.xmat[bid(my, f"{l}_coxa")].reshape(3, 3).copy(); ad = [Jp[f"c_thorax-{l}_coxa-{a}"] for a in AX]
            def res(q):
                dp.qpos[ad] = q; mj.mj_kinematics(mp, dp); return np.concatenate([(dp.xmat[cb].reshape(3, 3) - tgt).ravel(), 1e-4 * (q - qn[l])])
            lo, hi = qn[l] - np.radians(45), qn[l] + np.radians(45); best = None
            for k0, x0 in enumerate([qprev[l], qn[l]] + [lo + (hi - lo) * u for u in rng.random((6, 3))]):
                s_ = least_squares(res, np.clip(x0, lo + 1e-6, hi - 1e-6), bounds=(lo, hi), xtol=1e-10, ftol=1e-10)
                if best is None or s_.cost < best.cost - 1e-12: best = s_
                if k0 >= 1 and best.cost < 1e-8: break
            qprev[l] = best.x; dp.qpos[ad] = best.x; B[fr, li, :3] = best.x
            R_ = dp.xmat[cb].reshape(3, 3).T @ tgt; aerr[fr, li] = np.degrees(np.arccos(np.clip((np.trace(R_) - 1) / 2, -1, 1)))
        mj.mj_kinematics(mp, dp)
        ferr[fr] = [np.linalg.norm(dp.xpos[bid(mp, f"{l}_tarsus5")] - dy.xpos[bid(my, f"{l}_tarsus5")]) * 1000 for l in LEG6]
    print("step 1, the recording in our PITCH_ROLL_YAW order (the thorax-coxa angles fitted to the recorded coxa orientation, bounded to neutral +-45 deg):")
    print("  coxa orientation error, deg: median " + " ".join(f"{l} {v:.1f}" for l, v in zip(LEG6, np.median(aerr, 0))) + "; p95 " + " ".join(f"{l} {v:.1f}" for l, v in zip(LEG6, np.percentile(aerr, 95, 0))))
    print("  the foot (tarsus5 origin) off the recording's, um: median " + " ".join(f"{l} {v:.0f}" for l, v in zip(LEG6, np.median(ferr, 0))) + "; p95 " + " ".join(f"{l} {v:.0f}" for l, v in zip(LEG6, np.percentile(ferr, 95, 0))) + "; frames exact (< 1 um) " + " ".join(f"{l} {v * 100:.0f}%" for l, v in zip(LEG6, (ferr < 1).mean(0))))
    return B, FPS, DPL, dict(coxa_err_deg=aerr, foot_err_um=ferr), CLIP


def loop_targets(A, FPS, blend_ms, replay_seconds, dt_phys, print=print):
    """steps 2-3: smooth (MotionSnippet), loop, upsample. returns TGT (n_rep, 42) in the recording's (leg, dof) order, n_rep, (E, nb, n0)."""
    w_ = int(0.03 * FPS); w_ += 1 - (w_ % 2); As = savgol_filter(A, window_length=w_, polyorder=3, axis=0).reshape(len(A), -1)
    n0 = len(As); cand = np.arange(int(0.8 * n0), n0); dist = np.sqrt(((As[cand] - As[0]) ** 2).mean(1)); E = int(cand[np.argmin(dist)])
    nb = max(1, int(round(blend_ms / 1000 * FPS))); Lp = As[:E].copy(); wgt = np.linspace(0, 1, nb + 2)[1:-1, None]; Lp[E - nb:] = (1 - wgt) * As[E - nb:E] + wgt * As[:nb]
    print(f"step 3, the loop: cut at frame {E} of {n0} ({E / FPS * 1000:.0f} ms), pose distance to frame 0 {np.degrees(dist.min()):.1f} deg rms over the 42 angles (the clip's own frame-to-frame step is {np.degrees(np.sqrt((np.diff(As, axis=0) ** 2).mean(1)).mean()):.1f}); the last {nb} frames ({nb / FPS * 1000:.0f} ms) crossfaded into the first")
    n_rep = int(round(replay_seconds / dt_phys))
    reps = int(np.ceil(replay_seconds * FPS / len(Lp))) + 2; Tl = np.tile(Lp, (reps, 1)); tg = np.arange(len(Tl)) / FPS
    TGT = interp1d(tg, Tl, kind="cubic", axis=0)(np.arange(n_rep) * dt_phys)   # (n_rep, 42), recording order (leg, dof)
    return TGT, n_rep, (E, nb, n0)


def clip_columns(dofs, DPL):
    """the recording's (leg, dof) column for each actuated DOF."""
    col = []
    for x in dofs:
        l = x.child.name.split("_")[0]; p = "thorax" if x.parent.name == "c_thorax" else x.parent.name.split("_", 1)[1]; c = x.child.name.split("_", 1)[1]
        col.append(LEG6.index(l) * 7 + DPL.index((p, c, x.axis.value)))
    return np.array(col)


def target_at(TGT, q_set, ms, s, spm, w0, ramp, n_rep):
    """the target at physics sub-step s of millisecond ms (TGT already in the actuated DOFs' order)."""
    if ms < w0: return q_set + (TGT[0] - q_set) * min(1.0, (ms + s / spm) / ramp)
    return TGT[min((ms - w0) * spm + s, n_rep - 1)]


def position_law(kp, forcerange, tgt, q):
    """returns (u, the clipped torque): u = kp x (target - angle), clipped at +-forcerange."""
    u = kp * (tgt - q); return u, np.clip(u, -forcerange, forcerange)


def swing_from_foot(fx, w0, smooth_ms=9, min_ms=10):
    """the imposed swing per ms and leg (int8, 1 = swing) from fx (n_ms, 6), each foot's x in the thorax's frame (+x = forward, mm): the foot
    moving forward relative to the thorax (its x velocity over a smooth_ms centred mean > 0), then any run of either state shorter than
    min_ms flipped to its neighbours' state (the physics' tracking jitter); 0 before w0 (the warm-up has no replay)."""
    n, L = fx.shape; out = np.zeros((n, L), np.int8); k = np.ones(smooth_ms) / smooth_ms
    for i in range(L):
        v = np.convolve(np.gradient(fx[:, i].astype(float)), k, "same"); sw = v > 0
        sw[:w0] = False
        changed = True
        while changed:
            changed = False; edges = np.flatnonzero(np.diff(sw[w0:].astype(np.int8))) + w0 + 1; b = np.concatenate([[w0], edges, [n]])
            lens = np.diff(b)
            for j in np.argsort(lens, kind="stable"):
                if lens[j] >= min_ms: break
                if b[j] == w0 or b[j + 1] == n: continue
                sw[b[j]:b[j + 1]] = ~sw[b[j]]; changed = True; break
        out[:, i] = sw
    return out
