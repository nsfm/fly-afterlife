"""body_signs.py - measure, not assume: which way each of the six-legged body's leg joints moves the foot. the fly hangs in zero gravity
at its neutral pose; each actuated joint gets +5 / -5 torque for 200 ms; the difference between the two cancels the joint springs' passive drift; the tarsus tip's displacement (forward, lateral toward the midline, up) and
the change in tip-to-coxa distance say what that joint does. roles per leg: protract = the ThC joint with the largest forward swing (sign
so that + is forward); levate = CTr pitch (sign so that + lifts the foot); flex = FTi pitch (sign so that + shortens tip-to-coxa);
tarsus-levate = TiTa pitch (sign so that + lifts the tip); adduct = the ThC joint with the largest medial swing. -> results/body_dof_signs.json
"""
import json, numpy as np, mujoco as mj
from flygym.utils.math import Rotation3D
from flygym.compose import NeuroMechFly, FlatGroundWorld, ActuatorType, KinematicPosePreset
from flygym.anatomy import JointPreset, ActuatedDOFPreset, Skeleton, AxisOrder
from flygym import Simulation
def build():
    fly = NeuroMechFly(); skel = Skeleton(axis_order=AxisOrder.PITCH_ROLL_YAW, joint_preset=JointPreset.LEGS_ONLY)
    fly.add_joints(skel, KinematicPosePreset.NEUTRAL); dofs = ActuatedDOFPreset.LEGS_ACTIVE_ONLY.filter(fly.get_jointdofs_order())
    fly.add_actuators(dofs, ActuatorType.MOTOR); fly.add_leg_adhesion()
    world = FlatGroundWorld(); world.add_fly(fly, (0.0, 0.0, 3.0), Rotation3D(format="quat", values=(1, 0, 0, 0)))
    sim = Simulation(world); return sim, fly, dofs
sim, fly, dofs = build(); m = sim.mj_model; d = sim.mj_data; m.opt.gravity[:] = 0
segs = [s.name for s in fly.get_bodysegs_order()]; si = {n: i for i, n in enumerate(segs)}
def tip(leg): P = sim.get_body_positions("nmf"); return P[si[f"{leg}_tarsus5"]].copy(), P[si[f"{leg}_coxa"]].copy()
LEGS = ["lf", "lm", "lh", "rf", "rm", "rh"]; out = {}
for k, dof in enumerate(dofs):
    leg = dof.child.name[:2]; name = f"{dof.parent.name}->{dof.child.name}:{dof.axis.value}"
    res = {}
    for sgn in (+1.0, -1.0):
        sim.reset(); m.opt.gravity[:] = 0; t0, c0 = tip(leg); u = np.zeros(len(dofs)); u[k] = 5.0 * sgn
        for _ in range(2000): sim.set_actuator_inputs("nmf", ActuatorType.MOTOR, u); sim.step()
        t1, c1 = tip(leg); dl = (t1 - c1) - (t0 - c0); dist0 = np.linalg.norm(t0 - c0); dist1 = np.linalg.norm(t1 - c1)
        res[sgn] = dict(fwd=float(dl[0]), lat=float(-dl[1] if leg[0] == "l" else dl[1]), up=float(dl[2]), dshort=float(dist0 - dist1))
    out[name] = dict(leg=leg, joint=f"{dof.parent.name.split('_', 1)[1] if '_' in dof.parent.name else dof.parent.name}-{dof.child.name.split('_', 1)[1]}", axis=dof.axis.value, k=k, plus=res[1.0], minus=res[-1.0])
    print(f"{name:52s} +/- diff: fwd {(res[1.0]['fwd'] - res[-1.0]['fwd']) / 2:+.3f} lat {(res[1.0]['lat'] - res[-1.0]['lat']) / 2:+.3f} up {(res[1.0]['up'] - res[-1.0]['up']) / 2:+.3f} short {(res[1.0]['dshort'] - res[-1.0]['dshort']) / 2:+.3f}")
for n, v in out.items(): v['delta'] = {k: (v['plus'][k] - v['minus'][k]) / 2 for k in v['plus']}   # the springs' passive drift cancels in the difference
# roles per leg
roles = {}
for leg in LEGS:
    thc = {n: v for n, v in out.items() if v["leg"] == leg and v["joint"].startswith("thorax-")}; ctr = {n: v for n, v in out.items() if v["leg"] == leg and "coxa-" in v["joint"] and "trochanterfemur" in v["joint"]}
    fti = {n: v for n, v in out.items() if v["leg"] == leg and "trochanterfemur-" in v["joint"]}; tita = {n: v for n, v in out.items() if v["leg"] == leg and "tibia-" in v["joint"]}
    def pick(cands, key, want_pos=True):
        best = max(cands.items(), key=lambda kv: abs(kv[1]["delta"][key])); n, v = best; s = 1.0 if v["delta"][key] > 0 else -1.0; return dict(dof=n, k=v["k"], sign=s, size=abs(v["delta"][key]))
    roles[leg] = dict(protract=pick(thc, "fwd"), adduct=pick(thc, "lat"), levate=pick({n: v for n, v in ctr.items() if v["axis"] == "pitch"} or ctr, "up"),
                      flex=pick({n: v for n, v in fti.items() if v["axis"] == "pitch"} or fti, "dshort"), tarsus_levate=pick({n: v for n, v in tita.items() if v["axis"] == "pitch"} or tita, "up"))
    print(leg, {r: (v["dof"].split(":")[0].split("->")[1] + ":" + v["dof"].split(":")[1], v["sign"], round(v["size"], 3)) for r, v in roles[leg].items()})
json.dump(dict(dofs=[str(x) for x in dofs], measured=out, roles=roles), open("results/body_dof_signs.json", "w"), indent=1); print("wrote results/body_dof_signs.json")
