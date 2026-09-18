"""
pair.py - two flies in one room. the male (MaleCNS, flyvis eye, touch) and the female (FlyWire, W_syn 0.5,
no eye) walk the same arena, each on its own descending neurons.

    uv run python world/pair.py --seconds 30 --out world/pair0.npz [--no-female]  (control: him alone)

senses between them (labelled, all through named receptors):
  he sees her: a dark sphere r=0.15 at eye height (albedo 0.1) in his raytraced retina.
  he smells her: fly odour (methyl laurate, Or47b -> ORN_VA1v) and female cuticular cue (Or88a -> ORN_VA1d),
     concentration exp(-d / 0.8) at each antenna, bilateral.
  she smells him: cVA (Or67d -> ORN_DA1), same law.
  touch: both, leg bristles (his VNC bristles; her 'mechanosensory' class) on the contacted side.
  song: if his pIP10 fires above its running mean + 2 sd in a chunk and she is within 0.4 m, that chunk is
     a song bout: her Johnston's organ (JO-*, mechanosensory) is driven at 100 Hz.
steering: his DNa02 (vision; efference off; rest-sub) when free; while his bristles are pressed (wall, pillar, her) the leg-MN asymmetry steers alone, gain calibrated so the bristle-evoked asymmetry is worth 6 deg/chunk; hers DNa02 + heading noise, turn-away on contact
  (sd 15 deg/s). both walk at 0.3 / 0.15 m/s. readouts per chunk: his pC1 (all P1 types), pIP10, mAL, LC10a,
  DNa02 L/R; her pC1a-e, vpoEN, ORN_DA1, DNa02 L/R; distance, contacts, song bouts.
"""
import os, sys, argparse, time, numpy as np, torch
sys.path.insert(0, "seam"); sys.path.insert(0, "ref/flybrain/scripts"); sys.path.insert(0, "world")
os.environ.setdefault("FLYVIS_ROOT_DIR", "/home/nate/code/fly-afterlife/flyvis_data")
from omma import Eye, Scene
from flysim import FlyBrain, Params
from fastlif import FastFlyBrain   # numba step, verified spike-for-spike against flysim (world/fastlif.py)
ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); ap.add_argument("--seconds", type=float, default=30.0); ap.add_argument("--seed", type=int, default=0); ap.add_argument("--numpy-engine", action="store_true", help="use the original numpy LIF step instead of the numba one (same spikes, slower)"); ap.add_argument("--thermo", default="off", help="off: thermo cells silent (the record); rest: cells at their 25 C rates, no field (the control); field: warm corner 33 C; field2: warm 33 C + cold corner 10 C; field2x: hot 40 C + cold 10 C"); ap.add_argument("--bristle", default="adapting", help="hold: 150 Hz while touched (the record); adapting: 200 Hz onset, tau 30 ms, 20 Hz plateau, half the patch (mechanosensation brief)"); ap.add_argument("--wind", default="off", help="garden: wind on Johnston's organ (JO-C/E, equalised 132 per side): off | on"); ap.add_argument("--wind-gate", default="none", help="none: wind drives JO whenever it blows (open-loop result); odour: only while a fruit whiff is present at either antenna (a labelled stand-in for the central gate)"); ap.add_argument("--start", default=None, help="garden: his start as x,y,heading (default -0.5,-0.5,35: upwind of the fruit, no odour on him). 2.26,-0.94,90 puts him one metre downwind inside the plume, facing crosswind"); ap.add_argument("--no-plume", action="store_true", help="garden: the fruit has no odour (the control for the plume)"); ap.add_argument("--fruit-tone", default="dark", help="garden: dark (the record) or litter (the fruit takes the floor's mean tone: invisible, the control for vision)"); ap.add_argument("--world", default="room", help="room (the record) or garden (docs/GARDEN.md: textured floor, grass, leaves, stone, fruit with a plume and sugar, puddle, sun, rim)"); ap.add_argument("--floor", dest="floor", action="store_true", default=True, help="the tonic floor: every typed sense at its physiological resting rate (receptors.FLOOR), the world modulating (default since 09-17 18:27)"); ap.add_argument("--floor-drop", default="", help="comma-separated floor rows to leave out (floor_ORN, floor_ORN_DA1, floor_GRN, floor_hot, floor_cool, floor_hygro, floor_JO, floor_leg_proprio): the ablation of 09-18"); ap.add_argument("--no-floor", dest="floor", action="store_false", help="the silent brain: the record before 09-17 evening"); ap.add_argument("--pillar-height", type=float, default=1.5, help="pillar height in m standing on the floor (1.5 = the fix of 09-17 17:15; 1e6 = the infinite cylinders every run before it saw)"); ap.add_argument("--brake-dn", default="AN19A018", help="the halting population the brake rows drive: AN19A018 (the record; halts the silent cord, cannot halt DNg100 on the woken one) or DNg105 (halts the woken cord below standing against the walking command, 09-18 13:15)"); ap.add_argument("--stop-at-fruit", type=float, default=0.0, help="Hz on the brake population while sugar is on his tarsi (garden): the first piece of a feeding state, labelled; 0 = off"); ap.add_argument("--feeding", type=float, default=0.0, help="seconds sugar on the tarsi latches the feeding state (brake held on --brake-dn at --feed-brake Hz, withdrawal reflex silenced); 0 = no state"); ap.add_argument("--feed-brake", type=float, default=100.0); ap.add_argument("--satiety", type=float, default=0.0, help="seconds of feeding to fill satiety (ends feeding; taste no longer latches); 0 = none"); ap.add_argument("--satiety-tau", type=float, default=180.0); ap.add_argument("--stop-at-her", type=float, default=0.0, help="Hz on the brake (AN19A018, Sapkal 2024 BRK) while he is in contact with her; 0 = off. labelled: the stop is part of the courtship sequence in life"); ap.add_argument("--walk-dn", default="DNg100", help="the descending type the walking command drives: DNg100 (BDN2: 1,870 direct leg-MN synapses; walks the woken cord as a dose; default since 09-18 11:30) or DNp09 (the record before it; inert under the tonic floor)"); ap.add_argument("--pace-k", type=float, default=1.0, help="fixed pace rule: v = v_min + v_range x clip((leg MN - standing) / (k x standing)); 1 = twice the standing tonus is full speed (default since 09-18 11:30, standing measured in the floor after a warm-up); 4 = the record before it (degenerate: standing was 0)"); ap.add_argument("--walk", type=float, default=0.0, help="Hz of tonic drive on DNp09 (both sides), the forward-walking command (Bidaye 2020). 0 = none (the record); ~100 Hz makes the cord walk (09-17 12:50). labelled: in life the command is state-dependent"); ap.add_argument("--effector", default="wheel", help="wheel: the DNa02 running-baseline wheel (the record); legs: DNa02 wheel + the leg model's yaw (src/fly_afterlife/legs.py), touch reflex separate"); ap.add_argument("--legmn", default="leg", help="leg: the 373 leg motor neurons (MN subclass fl/ml/hl; leg_motor brief); all: every vnc_motor cell (699, incl. abdominal, wing, haltere, neck, jump: the record before 09-17 12:40)"); ap.add_argument("--reflex-sign", type=float, default=1.0, help="+1: the 09-16 convention (more right-leg spikes = left turn); -1: the drum's empirical sign (10:17, more right-leg spikes = right turn)"); ap.add_argument("--wheel", default="DNa02", help="steering population for the running-baseline wheel: DNa02 (the record) or legMN (the cord decides: leg-MN L-R asymmetry, the touch reflex's convention, gain negative)"); ap.add_argument("--wheel-gain", type=float, default=None, help="gain for --wheel legMN (default -0.3 deg per net spike per chunk: more right-leg drive = left turn)"); ap.add_argument("--dn-gain", type=float, default=0.0, help="gain of a second steering channel reading all descending neurons L-R through a running baseline (0 = off). 0.5 = 7 deg/chunk for the 8 C antennal asymmetry of the warm corner"); ap.add_argument("--steer", default="fixed", help="fixed: standing DNa02 offset subtracted (the record); running: per-side running baseline (adopted 09-17)"); ap.add_argument("--pace", default="state", help="fixed: v from the leg-MN rate against the standing tonus (k = --pace-k; the record); running: against his own running mean (09-17; retired 09-18: its fixed point made him walk at 0.275 whatever the cord did); state: standing / walking with a threshold and hysteresis on the smoothed rate (09-18, DeAngelis 2019 bimodal velocity)"); ap.add_argument("--wsyn-m", type=float, default=0.275, help="his mV per synapse. 0.275 = Shiu 2024 fit on FlyWire (ssTEM); FIB-SEM detects ~1.49x more synapses (Plaza 2025) -> 0.185 is the corrected value (docs/physiology/vision_motor_courtship.md)"); ap.add_argument("--wsyn-f", type=float, default=0.45, help="her mV per synapse (0.45 was the KC-sparsity calibration on the fixed build; the odour test of 22:55 says 0.275)"); ap.add_argument("--her-albedo", type=float, default=0.1, help="her body tone (0.1 dark; 0.5 = invisible against this room, the control)"); ap.add_argument("--proprio", type=float, default=0.0, help="peak Hz for his six legs of proprioceptors (leg-nerve cells only, world/legs.npz): tripod gait at 10 Hz, each leg in its stance half-cycle, scaled by pace, plus a 15 pct tonic load term; 0 = silent (was always silent)"); ap.add_argument("--deterministic", action="store_true", help="torch deterministic algorithms for flyvis: same seed -> same run, bit for bit (default GPU kernels differ at 1e-6 per call, which flips Poisson draws); costs ~+130 ms per chunk")
ap.add_argument("--model", default="flow/0000/000"); ap.add_argument("--no-female", action="store_true"); ap.add_argument("--gain", type=float, default=3.0); ap.add_argument("--drive-gain", type=float, default=150.0)
args = ap.parse_args(); fps, CH = 100, 10; rng = np.random.default_rng(args.seed)
g = np.load("seam/eye_geom.npz"); eye = Eye("seam/eye_geom.npz")
posts = np.array([(0.0, 1.6, 0.35, 0.85), (0.0, -1.6, 0.35, 0.85)], np.float32)   # pillars pale (0.85): she is the only dark thing in the room
WALLS = dict(half=2.0, height=1.0, albedo=0.6)   # the room: 4 x 4 m, walls 1 m tall, lighter than the floor, darker than the sky   # pillars: floor-to-sky cylinders, bark-dark
# ---- flyvis (his eye): src/fly_afterlife/frontend.py, the block that used to be here
from fly_afterlife.frontend import FlyvisFrontEnd, TYPES as types
fe = FlyvisFrontEnd(args.model, geom="seam/eye_geom.npz", fps=fps, chunk=CH, deterministic=args.deterministic); flyvis_chunk = fe.chunk; eyemap = fe.eyemap
# ---- his brain
Brain = FlyBrain if args.numpy_engine else FastFlyBrain
M = Brain("brain_whole.npz", seed=args.seed, params=Params(mv_per_synapse=args.wsyn_m)); mty = M.type.astype(str); mns = M.side.astype(str); mcls = M.cls.astype(str)
groups = fe.groups(M)
RM = {}
_lm = np.load("world/legmn.npz"); LEGMN_SEL = (M.sc == "vnc_motor") if args.legmn == "all" else np.isin(np.arange(M.N), _lm["leg"])
for name, sel in [("DNa02", mty == "DNa02"), ("pC1", np.char.startswith(mty, "pC1")), ("pIP10", mty == "pIP10"), ("mAL", np.char.startswith(mty, "mAL")), ("LC10a", mty == "LC10a"), ("ORN_VA1v", mty == "ORN_VA1v"), ("legMN", LEGMN_SEL), ("DN", M.sc == "descending_neuron")]:
    for s in "LR": RM[f"{name}_{s}"] = np.flatnonzero(sel & (mns == s))
    if name in ("pC1", "pIP10", "mAL", "LC10a"): RM[name] = np.flatnonzero(sel)
TACT_M = {s_: np.flatnonzero((mcls == "mechanosensory_tactile") & (mns == s_)) for s_ in "LR"}
_legs = np.load("world/legs.npz"); LEGS = {k: _legs[k] for k in _legs.files}; STEP_HZ = 10.0   # his six legs' proprioceptors by entry nerve (ProLN/MesoLN/MetaLN) x root side; haltere, wing, abdominal sensors stay silent
TRIPOD = {"L1": 0.0, "R2": 0.0, "L3": 0.0, "R1": 0.5, "L2": 0.5, "R3": 0.5}   # alternating tripods, half a cycle apart
_sp = np.load("world/ppk23_split.npz"); PPK_F = np.flatnonzero(np.isin(M.bodyId, _sp["F"])); PPK_M = np.flatnonzero(np.isin(M.bodyId, _sp["M"]))   # contact-pheromone leg neurons, F- and M-responsive by wiring; both fire on contact in life (Kallman 2015), P1 weighs them
TAP_HZ = 60.0; TAP_MS = 300.0
# ---- the receptor registry (src/fly_afterlife/receptors.py): every drive in the loop is a row here, applied in this order
from fly_afterlife.receptors import Registry, ReceptorClass, Hold, Adapting, Scaled, TapBurst, GaitLeg, HotCells, CoolingCells, WeberFechner
REG = Registry()
for (t, s), (idx, hx) in groups.items():
    REG.add(ReceptorClass(f"T4T5_{t}_{s}", idx, Scaled(args.drive_gain), (lambda st, t=t, s=s, hx=hx: (st["a"][(s, t)][st["f"]] - st["rest"][(s, t)])[hx]), source="seam v2"))
if args.proprio > 0:
    for leg_, idx_ in LEGS.items(): REG.add(ReceptorClass(f"proprio_{leg_}", idx_, GaitLeg(args.proprio, TRIPOD[leg_], STEP_HZ), lambda st: (st["pace"], st["t_chunk_end"])))
for s_ in "LR": REG.add(ReceptorClass(f"bristle_{s_}", TACT_M[s_], Hold(150.0) if args.bristle == "hold" else Adapting(), (lambda st, s_=s_: st["tm"] == "B" or st["tm"] == s_)))
REG.add(ReceptorClass("ppk_F", PPK_F, TapBurst(TAP_HZ, TAP_MS), lambda st: st["kind"] == 2)); REG.add(ReceptorClass("ppk_M", PPK_M, TapBurst(TAP_HZ, TAP_MS), lambda st: st["kind"] == 2))
if args.walk > 0: WALK = np.flatnonzero(((mty == args.walk_dn) | np.char.startswith(mty, args.walk_dn + "_")) & (M.sc == "descending_neuron")); REG.add(ReceptorClass(f"walk_{args.walk_dn}", WALK, Hold(args.walk), lambda st: True, source="Bidaye 2020 (DNp09) / Sapkal 2024 (BDN2 = DNg100); the command as a tonic drive, labelled"))
BRK = np.flatnonzero((mty == args.brake_dn) | np.char.startswith(mty, args.brake_dn + "_"))
if args.stop_at_her > 0: REG.add(ReceptorClass("brake_at_her", BRK, Hold(args.stop_at_her), lambda st: st["kind"] == 2, source="Sapkal 2024 (halting); driven on contact with her, labelled"))
if args.feeding > 0: REG.add(ReceptorClass("brake_feeding", BRK, Hold(args.feed_brake), lambda st: bool(st.get("feeding", False)), source="the feeding state holds the halt (09-18)"))
if args.stop_at_fruit > 0: REG.add(ReceptorClass("brake_at_fruit", BRK, Hold(args.stop_at_fruit), lambda st: st.get("taste") == "sugar", source="halting while sugar is on the tarsi: the stop of feeding, labelled (09-18)"))
if args.world == "garden":   # the garden's senses: the fruit's plume on the fruit-odour ORNs, humidity on the hygro cells, sugar on the leg GRNs at the fruit
    FRUIT_ORN = {s_: np.flatnonzero(np.isin(mty, ["ORN_DM1", "ORN_VA2", "ORN_DM4", "ORN_DM2", "ORN_DM5"]) & (mns == s_)) for s_ in "LR"}   # Or42b, Or92a, Or59b, Or22a, Or85a: the fruit / vinegar set (Hallem & Carlson 2006)
    for s_ in "LR": REG.add(ReceptorClass(f"fruit_ORN_{s_}", FRUIT_ORN[s_], WeberFechner(), (lambda st, s_=s_: st.get("odour_" + s_, {}).get("fruit", 0.0))))
    DRY = np.flatnonzero(mty == "HRN_VP4"); MOIST = np.flatnonzero(mty == "HRN_VP5")
    REG.add(ReceptorClass("dry_cells", DRY, Scaled(40.0), lambda st: 0.25 + 0.75 * (1.0 - st.get("humidity", 0.4)), source="chemo brief s.5: dry cells rise as RH falls, non-adapting, tens of Hz (E)"))
    REG.add(ReceptorClass("moist_cells", MOIST, Scaled(40.0), lambda st: 0.25 + 0.75 * st.get("humidity", 0.4), source="chemo brief s.5: moist cells rise with RH (E)"))
    LEG_GRN = np.flatnonzero(np.char.startswith(mty, "LgLG") | (mty == "claw_tpGRN"))
    REG.add(ReceptorClass("sugar_at_fruit", LEG_GRN, Hold(26.0), lambda st: st.get("taste") == "sugar", source="chemo brief s.3: sugar GRNs ~65 Hz at 100 mM x ~40% of tarsal GRNs being sugar-tuned (E; the leg GRN types carry no sugar / bitter label)"))
    print(f"garden senses: fruit ORNs {len(FRUIT_ORN['L'])}/{len(FRUIT_ORN['R'])}, dry {len(DRY)}, moist {len(MOIST)}, leg GRNs {len(LEG_GRN)}")
    if args.wind == "on":   # the wind on his antennae: the windward side's JO-C/E fire more (Yorozu 2009); populations equalised (203 L / 132 R typed: a tracing asymmetry)
        _joce = {s_: np.flatnonzero(np.array([t.startswith("JO-C") or t.startswith("JO-E") for t in mty]) & (mns == s_)) for s_ in "LR"}; _nmin = min(len(_joce["L"]), len(_joce["R"])); _r0 = np.random.default_rng(0)
        JOW = {s_: np.sort(_r0.choice(_joce[s_], _nmin, replace=False)) for s_ in "LR"}
        def _wind_stim(st, s_):
            rel = st.get("wind_rel", 0.0); lat = max(0.0, np.sin(np.radians(rel))) if s_ == "L" else max(0.0, -np.sin(np.radians(rel))); head = 0.5 * max(0.0, np.cos(np.radians(rel)))
            gate = 1.0 if args.wind_gate == "none" else (1.0 if (st.get("odour_L", {}).get("fruit", 0.0) > 0.02 or st.get("odour_R", {}).get("fruit", 0.0) > 0.02) else 0.0)
            return (0.25 + 0.75 * (lat + head)) * gate    # -> Scaled(20): 5 Hz floor-ish in still air is the floor row; wind adds up to 20 Hz on the windward side
        for s_ in "LR": REG.add(ReceptorClass(f"wind_JO_{s_}", JOW[s_], Scaled(20.0), (lambda st, s_=s_: _wind_stim(st, s_)), source="Yorozu 2009 (JO C/E wind); rate estimate (E); equalised populations (09-18)"))
        print(f"wind on JO: {_nmin} cells per side, gate {args.wind_gate}")
if args.thermo != "off":   # his arista thermosensors, sampled at each antenna tip (VP1m / VP1l left out: labels under audit, Marin 2020)
    HOT = {s_: np.flatnonzero((mty == "TRN_VP2") & (mns == s_)) for s_ in "LR"}; COOL = {s_: np.flatnonzero(np.isin(mty, ["TRN_VP3a", "TRN_VP3b"]) & (mns == s_)) for s_ in "LR"}
    for s_ in "LR":
        REG.add(ReceptorClass(f"hot_{s_}", HOT[s_], HotCells(), (lambda st, s_=s_: st["T_" + s_])))
        REG.add(ReceptorClass(f"cool_{s_}", COOL[s_], CoolingCells(), (lambda st, s_=s_: st["T_" + s_])))
    print(f"thermo cells: hot L {len(HOT['L'])} R {len(HOT['R'])}, cooling L {len(COOL['L'])} R {len(COOL['R'])}; mode {args.thermo}")
if args.floor:
    from fly_afterlife.receptors import tonic_floor
    _fl = tonic_floor(M, REG)
    if args.floor_drop: _drop = set(args.floor_drop.split(",")); REG.classes = [rc for rc in REG.classes if rc.name not in _drop]; _fl = [rc for rc in _fl if rc.name not in _drop]; print(f"floor rows dropped: {sorted(_drop)}")
    _flc = np.unique(np.concatenate([rc.cells for rc in _fl])); M.driven[_flc] = True; M._driven_idx = np.flatnonzero(M.driven); print(f"tonic floor: {len(_fl)} rows, {len(_flc)} cells")
print(REG.table()); REGF = Registry()   # a tap is a burst: ~60 Hz cap (Weiss 2011 GRN ceiling), ~300 ms, not a 150 Hz hold (docs/physiology/chemo_thermo_hygro.md)
RM["ppkF"] = PPK_F; RM["DNp09"] = np.flatnonzero(np.char.startswith(mty, "DNp09")); RM["MDN"] = np.flatnonzero(np.char.startswith(mty, "MDN")); RM["legMN"] = np.flatnonzero(LEGMN_SEL)
M.define_odor("flyodour", n_channels=1, seed=0); M._odor_map["flyodour"] = {"ORN_VA1v": 1.0, "ORN_VA1d": 0.6}
M.driven[:] = False
for cl in M.SENSORY_CLASSES: M.driven[M.cls == cl] = True
for t, (idx, _) in groups.items(): M.driven[idx] = True
if args.walk > 0: M.driven[WALK] = True   # the command cells must be in the driven set (after the sensory reset above)
if args.stop_at_her > 0: M.driven[BRK] = True
M._driven_idx = np.flatnonzero(M.driven); M.reset(); SPF = int(round(1000 / fps / M.p.dt))
# ---- her brain
RF = {}
if not args.no_female:
    F = Brain("brain_female2.npz", seed=args.seed + 100, balance_hemispheres=False, params=Params(mv_per_synapse=args.wsyn_f)); fty = F.type.astype(str); fns = F.side.astype(str); fcls = F.cls.astype(str)
    RF = {}
    for name, sel in [("DNa02", fty == "DNa02"), ("pC1", np.char.startswith(fty, "pC1")), ("vpoEN", fty == "vpoEN"), ("ORN_DA1", fty == "ORN_DA1"), ("JO", np.char.startswith(fty, "JO")), ("DN", F.sc == "descending_neuron")]:
        for s in "LR": RF[f"{name}_{s}"] = np.flatnonzero(sel & (fns == s))
        RF[name] = np.flatnonzero(sel)
    JO = RF["JO"]; TACT_F = {s_: np.flatnonzero((fcls == "mechanosensory") & ~np.char.startswith(fty, "JO") & (fns == s_)) for s_ in "LR"}
    for s_ in "LR": REGF.add(ReceptorClass(f"her_bristle_{s_}", TACT_F[s_], Hold(150.0), (lambda st, s_=s_: st["tf"] == "B" or st["tf"] == s_)))
    REGF.add(ReceptorClass("her_JO", JO, Hold(100.0), lambda st: st["singing"])); print(REGF.table())
    F.define_odor("cVA", n_channels=1, seed=0); F._odor_map["cVA"] = {"ORN_DA1": 1.0}
    F.driven[:] = False
    for cl in F.SENSORY_CLASSES: F.driven[F.cls == cl] = True
    F._driven_idx = np.flatnonzero(F.driven); F.reset()
    RF["DNp09"] = np.flatnonzero(np.char.startswith(fty, "DNp09")); RF["MDN"] = np.flatnonzero(np.char.startswith(fty, "MDN"))
    print(f"her readouts: pC1 {len(RF['pC1'])}, vpoEN {len(RF['vpoEN'])}, ORN_DA1 {len(RF['ORN_DA1'])}, JO {len(JO)}, DNa02 {len(RF['DNa02_L'])}/{len(RF['DNa02_R'])}")
print(f"his readouts: pC1 {len(RM['pC1'])}, pIP10 {len(RM['pIP10'])}, mAL {len(RM['mAL'])}, LC10a {len(RM['LC10a'])}, ORN_VA1v {len(RM['ORN_VA1v_L'])}/{len(RM['ORN_VA1v_R'])}")
# ---- world state
from fly_afterlife.body import Body
from fly_afterlife.world import Room
LAM = 0.8; BODY = 0.08; HER_R = 0.12; HER_ALB = args.her_albedo   # his body 16 cm, hers 24 cm; a fly is dark: against a 0.4 floor, 0.6 walls and pale pillars she is the one dark object he can approach
m = Body("him", -1.2, 0.0, 0.0, BODY); her = Body("her", 1.2, 0.3, 180.0, HER_R, albedo=HER_ALB, present=not args.no_female)
room = Room(half=WALLS["half"], height=WALLS["height"], albedo=WALLS["albedo"], sky=0.8, ground=0.4, posts=list(posts), pillar_height=args.pillar_height)
if args.world == "garden":
    from fly_afterlife.garden import Garden
    room = Garden(seed=args.seed); m.x, m.y, m.h = (-0.5, -0.5, 35.0) if args.start is None else tuple(float(v) for v in args.start.split(",")); her.x, her.y, her.h = 1.2, 0.3, 180.0
    if args.no_plume: room.odour = lambda x, y, t, sources=None, rng=None: {"fruit": 0.0}
    if args.fruit_tone == "litter": fx_, fy_, fz_, fr_, _ = room.fruit; room.fruit = (fx_, fy_, fz_, fr_, float(room.tex.mean()))   # posts stay float32 rows: the oracle's arithmetic
THERMO_FIELDS = {"field": [dict(base=25.0, x=1.5, y=1.5, dT=8.0, sigma=0.8)],                                                     # a warm corner, 33 C at the centre
                 "field2": [dict(base=25.0, x=1.5, y=1.5, dT=8.0, sigma=0.8), dict(x=-1.5, y=-1.5, dT=-15.0, sigma=0.8)],           # warm corner 33 C + cold corner 10 C (nate, 09-17 evening)
                 "field2x": [dict(base=25.0, x=1.5, y=1.5, dT=15.0, sigma=0.8), dict(x=-1.5, y=-1.5, dT=-15.0, sigma=0.8)]}        # hot corner 40 C + cold corner 10 C: the extremes
if args.thermo in THERMO_FIELDS: room.thermal = THERMO_FIELDS[args.thermo]
# warm-up: flyvis state + T4/T5 rest on the still scene; LIF rest
acc = {}
for c in range(10):
    a = flyvis_chunk(np.stack([eye.render(room.scene([her]), pos=(m.x, m.y, 0.5), heading_deg=m.h) for _ in range(CH)]))
    if c >= 5:
        for k_, v_ in a.items(): acc.setdefault(k_, []).append(v_)
rest = {k_: np.concatenate(v_).mean(0) for k_, v_ in acc.items()}
for _ in range(500):
    M.step()
    if not args.no_female: F.step()
# calibrations (src/fly_afterlife/effectors.py): the same standing loops, once per run
from fly_afterlife.effectors import Steering, RunningBaselineSteering, MultiWheelSteering, Pace, RunningPace, StatePace, FeedingState, HerSteering, SongDetector, dna02_rest_offset, standing_baselines, reflex_gain, apply_tonic, TONIC_SKIP
def render_chunk(): return flyvis_chunk(np.stack([eye.render(room.scene([her]), pos=(m.x, m.y, 0.5), heading_deg=m.h) for _ in range(CH)]))
def drive_frame(a, f):
    for (t, s), (idx, hx) in groups.items(): M.drive_hz[idx] = args.drive_gain * np.clip((a[(s, t)][f] - rest[(s, t)])[hx], 0, 1)
TONIC = (lambda t_: apply_tonic(REG, M, t_, 1.0 / fps))   # the standing brain: floor, command, thermal cells at 25 C (09-18)
def TONIC_STAND(t_):   # standing = the floor without the walking command (10:31: with it, the pace reference rose with the dose; 10:55: the cells kept their drive when the row was skipped)
    apply_tonic(REG, M, t_, 1.0 / fps, skip=TONIC_SKIP + ("walk_",))
    if args.walk > 0: M.drive_hz[WALK] = 0.0
_tonic_rows = [rc for rc in REG.classes if not rc.name.startswith(TONIC_SKIP)]
for f_ in range(2 * fps if _tonic_rows else 0):   # warm-up (only when tonic rows exist, so the oracle's silent brain is untouched): two seconds under the tonic rows before any calibration (10:55: the floor's settling transient was being measured as standing: 51 / 82 / 106 / 58 per chunk for one seed)
    TONIC(f_ / fps)
    for _ in range(SPF): M.step()
rest_net = dna02_rest_offset(M, RM, drive_frame, render_chunk, CH, SPF, tonic=TONIC); print(f"his DNa02 rest offset {rest_net:+.2f}/chunk")
leg_stand, dn_stand_f = standing_baselines(M, F if not args.no_female else None, RM, RF, drive_frame, render_chunk, CH, SPF, tonic=TONIC_STAND); print(f"pace baselines per chunk: his leg MN {leg_stand:.0f}, her DN {dn_stand_f:.0f}")
leg_gain, asym_side = reflex_gain(M, RM, TACT_M, CH, SPF, kernel=(None if args.bristle == "hold" else Adapting()), fps=fps, tonic=TONIC); leg_gain *= args.reflex_sign; print(f"touch reflex: leg-MN asymmetry (R-L)/(R+L) with left bristles {asym_side['L']:+.3f}, right {asym_side['R']:+.3f} -> gain {leg_gain:.0f} deg per unit asymmetry")
from fly_afterlife.legs import LegModel, LegSteering
steer = LegSteering(LegModel(M), wheel_gain=args.gain, leg_gain=leg_gain) if args.effector == "legs" else Steering(gain=args.gain, rest_net=rest_net, leg_gain=leg_gain) if args.steer == "fixed" else (RunningBaselineSteering(gain=(args.gain if args.wheel == "DNa02" else (args.wheel_gain if args.wheel_gain is not None else -0.3)), leg_gain=leg_gain, wheel=args.wheel) if args.dn_gain == 0 else MultiWheelSteering(wheels=[("DNa02", args.gain), ("DN", args.dn_gain)], leg_gain=leg_gain))
pace = Pace(leg_stand=leg_stand, k=args.pace_k) if args.pace == "fixed" else (StatePace(leg_stand=leg_stand) if args.pace == "state" else RunningPace()); hers = HerSteering(rng); songdet = SongDetector()
m.v = 0.3; her.v = 0.15
# ---- loop (src/fly_afterlife/episode.py)
from fly_afterlife.episode import Episode
ep = Episode(fps=fps, chunk=CH, eye=eye, room=room, him=m, her=her, brains=(M, F if not args.no_female else None), readouts=(RM, RF), registries=(REG, REGF), front_end=flyvis_chunk, rest=rest, effectors=(steer, pace, hers, songdet), lam=LAM, state=(FeedingState(hold=args.feeding, t_full=args.satiety, tau_sat=args.satiety_tau) if args.feeding > 0 else None))
ep.run(args.seconds)
if args.world == "garden":
    ep.save(args.out, posts=np.array([[gx, gy, gr, ga] for gx, gy, gr, ga, gh in room.grass], np.float32), walls=dict(half=room.half, height=room.height, albedo=room.albedo), her_albedo=HER_ALB, body_r=BODY, her_r=HER_R,
            extra=dict(world="garden", floor_rgb=room.rgb, floor_half=room.half, grass=np.array(room.grass, np.float32), leaves=np.array(room.leaves, np.float32), stone=np.array(room.stone, np.float32), fruit=np.array(room.fruit, np.float32), puddle=np.array(room.puddle, np.float32), sunspot=np.array(room.sunspot, np.float32), wind=np.array(room.wind, np.float32)))
else: ep.save(args.out, posts=posts, walls=WALLS, her_albedo=HER_ALB, body_r=BODY, her_r=HER_R)
