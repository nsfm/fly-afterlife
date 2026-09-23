"""hill_legs.py - FlyMimic's Hill-type leg muscles on the six legs of the NeuroMechFly body, for experiments/body_loop.py --muscles hill (09-23).

what flygym 2.1 ships (read from the package, 09-23): ONE muscle-driven leg. `flygym.compose.MusculoskeletalFly` wraps FlyMimic's MJCF
`assets/model/musculoskeletal/best_combined_arm_damping_stiff_cvt3.xml` (Ozdil, Ning, Phelps, Wang-Chen, Elisha, Blanke, Ijspeert & Ramdya,
ICLR 2026, arXiv 2509.06426; converted from OpenSim Millard2012EquilibriumMuscle by MyoConverter): a thorax-anchored fly with no free joint,
no adhesion, no ground contact sensors; 7 hinges on the LEFT FRONT leg driven by 15 Hill-type muscles on spatial tendons; the right front leg
locked by equality constraints; the middle and hind legs are rigid meshes with no joints. the FlyMimic repository (scratchpad clone) has the
same 15 muscles in every variant and in its OpenSim source. so there are no muscles for five of the six legs, and the musculoskeletal fly
cannot stand or walk. this module therefore transplants the front leg's muscle set onto our body, one rule for every leg, stated below.

per muscle, FROM THE MODEL (nothing of ours): MuJoCo's muscle actuator (dyntype / gaintype / biastype = muscle) with FlyMimic's own
  gainprm = biasprm = (range0, range1, F_max, scale, lmin, lmax, vmax, fpmax, fvmax): the operating range of normalised length, the peak
    isometric force (uN in the model's g-mm-s units; PCSA x 28 mN/mm^2 then NSGA-II fit to walking and grooming kinematics), the active
    force-length curve on [lmin, lmax] = [0, 2], vmax = 10 optimal lengths / s, the passive force at lmax (fpmax, per muscle, fitted), the
    lengthening force ceiling fvmax = 1.4 (OpenSim's mammalian defaults for the curves; the paper: no Drosophila force-length or
    force-velocity curve exists);
  dynprm = (tau_act, tau_deact) = (0.1 ms, 0.4 ms): MuJoCo's first-order excitation -> activation (Millard 2013 form: tau_act x (0.5 + 1.5 a)
    rising, tau_deact / (0.5 + 1.5 a) falling), the numbers FlyMimic ships (its class default says 10 / 40 ms; every muscle overrides it
    to 0.1 / 0.4 ms). leg_biomech.md B6: ~85x faster than Azevedo's 8.5 ms half-rise, because FlyMimic's input is a continuous activation;
  lengthrange (the tendon length over the leg's range of motion) -> the optimal fibre length L0 = (lr1 - lr0) / (range1 - range0) and the
    tendon slack, both unchanged here.
per muscle, CHOSEN (E), one rule each, printed at startup:
  (E1) transmission: a joint transmission on the ONE degree of freedom that body_loop.py's torque path gives the muscle's motor-neuron pool
       (the measured role table, results/body_dof_signs.json, --hind-map as given), with gear = the moment arm. FlyMimic's tendons are spatial
       and cross 1-3 hinges; here each is linearised: |moment arm| = |d(tendon length) / d(angle)| of FlyMimic's tendon about the front
       leg's hinge for that role (coxa pitch for protract / retract, coxa roll for adduct, trochanter pitch for levate / depress, tibia pitch
       for flex / extend), central difference at FlyMimic's own default pose (its keyframe). the other hinges' arms are dropped.
       --hill-arm norm instead takes the norm of the arm over the three hinges of that joint (coxa yaw / pitch / roll; trochanter yaw /
       pitch / roll; the tibia has one), the muscle's whole leverage at the joint placed on the role's DOF: the variant for the middle and
       hind legs, whose coxa axes are not the front leg's (the sternal anterior rotator, their only promotor, is a yaw rotator on the
       front leg: 0.0057 mm about pitch, 0.084 about yaw).
  (E2) sign: the torque path's role sign for the pool (the measured action on OUR body). on the front leg FlyMimic's own moment-arm signs
       agree with it for all 15 muscles (checked and printed: pitch conventions coincide, +pitch = remotion / depression / flexion in both).
  (E3) length: the muscle's normalised fibre length at OUR neutral pose (KinematicPosePreset.NEUTRAL) equals its length in FlyMimic's
       default pose (lengthrange shifted by one constant); away from neutral it changes by gear x angle.
  (E4) serial homology and mirroring: every leg gets the front leg's muscle parameters (FlyMimic's middle and hind legs are annotated
       with 7 / 8 muscles in the paper but not optimised and not shipped); right legs by the role table's measured signs.
  (E5) a muscle is built on a leg only where the file has a motor neuron for it (e.g. the tergopleural promotors exist on the front legs only;
       the other legs promote with the sternal anterior rotator, leg_biomech.md A3).
  (E6) the hind cells --hind-map v2 names (leg_biomech.md A2): MNhl62 -> the sternal anterior rotator (cos 0.79), MNhl29 -> the sternal
       posterior rotator (cos 0.69), MNhl01 / MNhl02 -> the sterno-tergo-trochanter extensors (their named match, Sternotrochanter MN).
not transplanted (no FlyMimic muscle): the tarsal levator / depressor pools (they stay on the torque kernel, labelled), the grip (the pads'
ltm, unchanged), the femur reductor and the jump muscle (unmapped, as in the torque path).
"""
import numpy as np
import mujoco as mj

LEG6 = ["lf", "lm", "lh", "rf", "rm", "rh"]
# FlyMimic's 15 actuators, their role in body_loop.py's table (role, +1 agonist / -1 antagonist), and the FlyMimic hinge for the role
MUSCLE_ROLE = {
    "LFC_tergopleural_promotor_a": ("protract", +1), "LFC_tergopleural_promotor_b": ("protract", +1), "LFC_pleural_promotor": ("protract", +1),
    "LFC_sternal_anterior_rotator": ("protract", +1), "LFC_pleural_remotor_and_abductor": ("protract", -1), "LFC_sternal_posterior_rotator": ("protract", -1),
    "LFC_sternal_adductor": ("adduct", +1),
    "LFF_trochanter_flexor_a": ("levate", +1), "LFF_trochanter_flexor_b": ("levate", +1), "LFF_accesory_trochanter_flexor": ("levate", +1),
    "LFF_sterno-tergo-trochanter_extensor_a": ("levate", -1), "LFF_sterno-tergo-trochanter_extensor_b": ("levate", -1), "LFF_trochanter_extensor": ("levate", -1),
    "LFTibia_flex_93434": ("flex", +1), "LFTibia_extensor_93932": ("flex", -1)}
JOINT_HINGES = {"protract": ("joint_LFCoxa_yaw", "joint_LFCoxa_pitch", "joint_LFCoxa_roll"), "adduct": ("joint_LFCoxa_yaw", "joint_LFCoxa_pitch", "joint_LFCoxa_roll"),
                "levate": ("joint_LFTrochanter_yaw", "joint_LFTrochanter_pitch", "joint_LFTrochanter_roll"), "flex": ("joint_LFTibia_pitch",)}
ROLE_HINGE = {"protract": "joint_LFCoxa_pitch", "adduct": "joint_LFCoxa_roll", "levate": "joint_LFTrochanter_pitch", "flex": "joint_LFTibia_pitch"}
# motor-neuron type -> FlyMimic muscles (experiments/leg_replay.py's map, leg_biomech.md F.4a; + the hind cells of --hind-map v2, (E6))
MUSCLES_OF_TYPE = {
    "Tergopleural/Pleural promotor MN": ["LFC_tergopleural_promotor_a", "LFC_tergopleural_promotor_b", "LFC_pleural_promotor"],
    "Pleural remotor/abductor MN": ["LFC_pleural_remotor_and_abductor"], "Sternal anterior rotator MN": ["LFC_sternal_anterior_rotator"],
    "Sternal posterior rotator MN": ["LFC_sternal_posterior_rotator"], "Sternal adductor MN": ["LFC_sternal_adductor"],
    "Tr flexor MN": ["LFF_trochanter_flexor_a", "LFF_trochanter_flexor_b"], "Acc. tr flexor MN": ["LFF_accesory_trochanter_flexor"],
    "Sternotrochanter MN": ["LFF_sterno-tergo-trochanter_extensor_a", "LFF_sterno-tergo-trochanter_extensor_b"], "Tr extensor MN": ["LFF_trochanter_extensor"],
    "Ti flexor MN": ["LFTibia_flex_93434"], "Acc. ti flexor MN": ["LFTibia_flex_93434"], "Ti extensor MN": ["LFTibia_extensor_93932"],
    "MNhl62": ["LFC_sternal_anterior_rotator"], "MNhl29": ["LFC_sternal_posterior_rotator"],
    "MNhl01": ["LFF_sterno-tergo-trochanter_extensor_a", "LFF_sterno-tergo-trochanter_extensor_b"], "MNhl02": ["LFF_sterno-tergo-trochanter_extensor_a", "LFF_sterno-tergo-trochanter_extensor_b"]}
SHORT = {m: "tibia_flexor" if m.startswith("LFTibia_flex") else "tibia_extensor" if m.startswith("LFTibia_ext") else m.split("_", 1)[1] for m in MUSCLE_ROLE}


def flymimic_table():
    """FlyMimic's 15 muscles as shipped in flygym 2.1: parameters, the tendon length at the model's default pose and its moment arms."""
    import warnings
    from flygym.compose.fly.musculoskeletal import MusculoskeletalFly, DEFAULT_MUSCULOSKELETAL_XML
    with warnings.catch_warnings():
        warnings.simplefilter("ignore"); fm = MusculoskeletalFly(); m = fm.mjcf_root.compile()
    d = mj.MjData(m); mj.mj_resetDataKeyframe(m, d, 0); mj.mj_forward(m, d)
    jn = [mj.mj_id2name(m, mj.mjtObj.mjOBJ_JOINT, i) for i in range(m.njnt)]; q0 = d.qpos.copy(); out = {}
    for a in range(m.nu):
        n = mj.mj_id2name(m, mj.mjtObj.mjOBJ_ACTUATOR, a)
        if m.actuator_dyntype[a] != mj.mjtDyn.mjDYN_MUSCLE: continue
        t = m.actuator_trnid[a, 0]; L = float(d.ten_length[t]); arm = {}
        for h in sorted(set(sum(JOINT_HINGES.values(), ()))):
            i = m.jnt_qposadr[jn.index(h)]; d.qpos[:] = q0; d.qpos[i] += 1e-4; mj.mj_forward(m, d); lp = float(d.ten_length[t])
            d.qpos[:] = q0; d.qpos[i] -= 1e-4; mj.mj_forward(m, d); arm[h] = (lp - float(d.ten_length[t])) / 2e-4
        d.qpos[:] = q0; mj.mj_forward(m, d)
        g = m.actuator_gainprm[a, :10].copy(); lr = m.actuator_lengthrange[a].copy(); L0 = (lr[1] - lr[0]) / (g[1] - g[0])
        out[n] = dict(gainprm=g, biasprm=m.actuator_biasprm[a, :10].copy(), dynprm=m.actuator_dynprm[a, :10].copy(), lr=lr, L=L, L0=L0, LT=lr[0] - g[0] * L0,
                      arm=arm, ctrlrange=m.actuator_ctrlrange[a].copy())
    return out, str(DEFAULT_MUSCULOSKELETAL_XML), dict(zip(jn, np.round(q0[:len(jn)], 4)))


def build(spec, jm, dof_name, neutral_of, roles, types_on_leg, arm_rule="hinge", print=print):
    """add the muscles to the fly's MjSpec before the world compiles. jm: {JointDOF: MjsJoint}; roles: body_loop.py's per-leg role table
    (with --hind-map applied); types_on_leg: {leg: set of motor-neuron types with a role on that leg}. returns the muscle list (dicts)."""
    FM, xml, pose = flymimic_table(); jel = {dof_name(k): v for k, v in jm.items()}; mus = []
    print(f"--muscles hill: FlyMimic's 15 left-front-leg Hill muscles from {xml.split('site-packages/')[-1]} (flygym 2.1; the only muscles it ships), transplanted by rule (E1-E6, experiments/hill_legs.py)")
    print(f"  the model's default pose (keyframe, rad): " + ", ".join(f"{k.replace('joint_LF', '')} {v:+.3f}" for k, v in pose.items() if k.startswith("joint_LF")))
    print(f"  activation dynamics (the model's): tau_act {FM['LFTibia_flex_93434']['dynprm'][0] * 1e3:.1f} ms, tau_deact {FM['LFTibia_flex_93434']['dynprm'][1] * 1e3:.1f} ms, MuJoCo's muscle dynamics; FL on [lmin, lmax] = [0, 2], vmax 10 L0/s, fvmax 1.4")
    ARM = {n: (abs(FM[n]["arm"][ROLE_HINGE[r]]) if arm_rule == "hinge" else float(np.linalg.norm([FM[n]["arm"][h] for h in JOINT_HINGES[r]]))) for n, (r, _) in MUSCLE_ROLE.items()}
    print(f"  moment arm rule --hill-arm {arm_rule}: " + ("|arm| about the front leg's hinge for the role (E1)" if arm_rule == "hinge" else "the norm of the arm over the joint's hinges, placed on the role's DOF (E1 variant)"))
    print("  muscle                                  role       F_max uN  L0 mm   lnorm@pose  fpmax  arm about the role's hinge, mm   used |arm|  FlyMimic's sign agrees  F_max x |arm| nN.m")
    for n, (role, ag) in MUSCLE_ROLE.items():
        f = FM[n]; h = ROLE_HINGE[role]; a = f["arm"][h]
        # FlyMimic's pitch hinges: + = remotion / depression / flexion, the same sense as our lf table (protract -1, levate -1, flex +1); an agonist's
        # tendon shortens toward its action, so d(length)/d(angle) has the sign of -(its torque sign) = -(role sign x ag) on lf
        agree = np.sign(a) == -np.sign(roles["lf"][role]["sign"] * ag)
        print(f"  {n:40s} {role:8s} {ag:+d}  {f['gainprm'][2]:7.1f}  {f['L0']:.4f}  {(f['L'] - f['LT']) / f['L0']:.3f}      {f['gainprm'][7]:5.2f}  {a:+.4f} ({h.replace('joint_LF', ''):16s})  {ARM[n]:.4f}      {'yes' if agree else 'NO'}                  {f['gainprm'][2] * ARM[n]:6.2f}")
    for leg in LEG6:
        built = []
        for n, (role, ag) in MUSCLE_ROLE.items():
            if not any(n in MUSCLES_OF_TYPE.get(t, []) for t in types_on_leg.get(leg, ())): continue   # (E5)
            f = FM[n]; r = roles[leg][role]; dn = r["dof"]; sgn = float(r["sign"]) * ag; arm = ARM[n]; gear = -sgn * arm   # (E1, E2)
            q0 = float(neutral_of.get(dn, 0.0)); lr = f["lr"] + (gear * q0 - f["L"])   # (E3) actuator length = gear x q; at q0 it is FlyMimic's pose length
            act = spec.add_actuator(); act.name = f"hill-{leg}-{SHORT[n]}"; act.trntype = mj.mjtTrn.mjTRN_JOINT; act.target = jel[dn].name
            act.gear[0] = gear; act.dyntype = mj.mjtDyn.mjDYN_MUSCLE; act.gaintype = mj.mjtGain.mjGAIN_MUSCLE; act.biastype = mj.mjtBias.mjBIAS_MUSCLE
            act.dynprm[:10] = f["dynprm"]; act.gainprm[:10] = f["gainprm"]; act.biasprm[:10] = f["biasprm"]; act.lengthrange[:] = lr
            act.ctrllimited = 1; act.ctrlrange[:] = f["ctrlrange"]; act.forcelimited = 0
            mus.append(dict(name=act.name, leg=leg, muscle=n, role=role, ag=ag, dof=dn, gear=gear, q0=q0)); built.append(SHORT[n])
        print(f"  {leg}: {len(built)} muscles: {', '.join(built)}")
    return mus
