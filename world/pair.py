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
ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); ap.add_argument("--seconds", type=float, default=30.0); ap.add_argument("--seed", type=int, default=0); ap.add_argument("--integrate", default="exact", help="exact: the linear system stepped exactly as Shiu 2024's Brian2 method=linear (default since 09-19 10:50; the synaptic peak on the analytic curve); euler: forward Euler at dt 1 ms (flysim, the record before it; the peak 16 pct low; oracle v1 pins it)"); ap.add_argument("--numpy-engine", action="store_true", help="use the original numpy LIF step instead of the numba one (same spikes, slower)"); ap.add_argument("--thermo", default="rest", help="off: thermo cells silent (the record); rest: cells at their 25 C rates, no field (the control); field: warm corner 33 C; field2: warm 33 C + cold corner 10 C; field2x: hot 40 C + cold 10 C"); ap.add_argument("--bristle", default="adapting", help="hold: 150 Hz while touched (the record); adapting: 200 Hz onset, tau 30 ms, 20 Hz plateau, half the patch (mechanosensation brief)"); ap.add_argument("--wind", default="on", help="garden: wind on Johnston's organ (JO-C/E, equalised 132 per side): off | on"); ap.add_argument("--wind-gate", default="none", help="none: wind drives JO whenever it blows (open-loop result); odour: only while a fruit whiff is present at either antenna (a labelled stand-in for the central gate)"); ap.add_argument("--start", default=None, help="garden: his start as x,y,heading (default -0.5,-0.5,35: upwind of the fruit, no odour on him). 2.26,-0.94,90 puts him one metre downwind inside the plume, facing crosswind"); ap.add_argument("--no-plume", action="store_true", help="garden: the fruit has no odour (the control for the plume)"); ap.add_argument("--fruit-tone", default="dark", help="garden: dark (the record) or litter (the fruit takes the floor's mean tone: invisible, the control for vision)"); ap.add_argument("--arena-radius", type=float, default=2.8, help="the open-field dish (docs/BENCHMARKS.md): 2.8 sim m = 4.2 cm (Soibam 2012 / opynfield 8.4 cm); 1.67 = the 5.0 cm dish"); ap.add_argument("--goal", type=float, default=None, help="a goal heading in world degrees (the stand-in for menotaxis, 09-18 night): FC2 cells (the goal in the fan-shaped body; Mussells Pires 2024) driven by column with a von Mises bump at the goal, the column-to-heading offset read from PFL3's own glomerulus / column labels; PFL3 compares it with the ring's bump (Delta7) and projects to LAL and DNa02. needs --ring"); ap.add_argument("--goal-wind", type=float, default=0.0, help="anemotaxis through the compass (09-19): while a fruit whiff is on either antenna (C > 0.02), the goal heading becomes upwind (where the wind comes from), held for this many seconds after the last whiff (the surge); with no odour the goal is the wandering one. a stand-in for the wind-direction representation next to the goal in the central complex (Currier 2020); labelled. 0 = off"); ap.add_argument("--goal-switch", type=float, default=0.0, help="seconds of continuous contact (a wall, the rim, a stalk) after which the goal yields and a new heading is drawn from the half-circle facing away from the wall (Green 2019: menotaxis headings are held for minutes and then switched; a wall is a reason; a fly leaving a wall turns away from it). 0 = a fixed goal. labelled (09-19)"); ap.add_argument("--goal-hz", type=float, default=100.0, help="FC2 peak Hz at the goal column (40 left PFL3 silent; 100 makes it compare, 23:40)"); ap.add_argument("--pfl2-walk", action="store_true", help="PFL2's mean membrane as the walking command's gain (Westeinde 2024: PFL2 drives forward walking when heading matches the goal): gain = clip((v - v_behind) / (v_ahead - v_behind)), the two ends measured in calibration with the goal ahead and behind; labelled (09-19)"); ap.add_argument("--pfl2-floor", type=float, default=0.15, help="the walking gain when fully off-goal"); ap.add_argument("--goal-null", default="on", help="the comparator's null point (PFL3 membrane L-R with the goal ahead, subtracted as the channel's baseline): on | off. off with --mirror PFL3,PFL2, whose pair normalisation removes the bias the null was for (14:50: with both, the null itself became a bias)"); ap.add_argument("--goal-wheel-v", type=float, default=0.0, help="deg per chunk per mV of PFL3 mean membrane L-R (a graded readout of the comparator, fixed baseline; PFL3 is graded in life and its spikes here are too sparse, 09-19). 0 = off"); ap.add_argument("--goal-ema", type=float, default=50.0, help="chunks of smoothing on the goal channel (five seconds: PFL3 spikes are sparse and the error is sustained)"); ap.add_argument("--goal-wheel", type=float, default=0.0, help="deg per net PFL3 spike per chunk read as a third wheel channel (PFL3 L-R through the running baseline): the comparator's output onto the body, one cell upstream of DNa02, which the cord's hole holds one-sided. 0 = logged only"); ap.add_argument("--ring", action="store_true", help="the compass stand-in (garden; 09-18 night): ExR1 held at --ring-exr Hz so EPG sit near threshold; the 215 ring neurons with real output onto EPG given field azimuths tiling the circle (von Mises, kappa 2) and fired by the sun at that azimuth relative to his heading; their synapses onto the wedge that should hold the bump weakened (wiring.ring_map: the plastic map of Kim 2019 / Fisher 2019, imposed). PEN, Delta7, PFL are his. labelled."); ap.add_argument("--ring-exr", type=float, default=200.0, help="ExR1 Hz (the sweep of 22:10: 100 -> no bump; 200 -> a bump at EPG 3 Hz; 400 -> 8 Hz, blurred)"); ap.add_argument("--ring-er", type=float, default=20.0, help="peak Hz of a ring neuron with the sun in its field (60 over-inhibits the ring)"); ap.add_argument("--uv-gain", type=float, default=None, help="Hz per unit activity for the UV retina's rows (default = --drive-gain); a labelled gain on the anterior visual pathway, tested 21:40"); ap.add_argument("--uv-photo", action="store_true", help="drive his own R7 (UV retina) and R8 (green) as Poisson receptors by column. kept for the record: photoreceptors are histaminergic, so spikes on them INHIBIT their targets (R7 -> MeTu3c -3, Dm8 -6), and a silent LIF cell cannot be released from inhibition; it quietened MeTu3c (21:35). the graded route is --uv"); ap.add_argument("--uv", action="store_true", help="the UV retina (garden): the world rendered in UV albedos with a sun disc (garden.scene_uv), through a second flyvis whose Mi15 drives his Mi15 cells by column: the anterior visual pathway (Mi15 -> MeTu -> TuBu -> ER) that anchors the compass; a luminance stand-in for R7, labelled (09-18)"); ap.add_argument("--world", default="room", help="room (the record), arena (the open-field dish, docs/BENCHMARKS.md) or garden (docs/GARDEN.md: textured floor, grass, leaves, stone, fruit with a plume and sugar, puddle, sun, rim)"); ap.add_argument("--floor", dest="floor", action="store_true", default=True, help="the tonic floor: every typed sense at its physiological resting rate (receptors.FLOOR), the world modulating (default since 09-17 18:27)"); ap.add_argument("--floor-drop", default="", help="comma-separated floor rows to leave out (floor_ORN, floor_ORN_DA1, floor_GRN, floor_hot, floor_cool, floor_hygro, floor_JO, floor_leg_proprio): the ablation of 09-18"); ap.add_argument("--no-floor", dest="floor", action="store_false", help="the silent brain: the record before 09-17 evening"); ap.add_argument("--pillar-height", type=float, default=1.5, help="pillar height in m standing on the floor (1.5 = the fix of 09-17 17:15; 1e6 = the infinite cylinders every run before it saw)"); ap.add_argument("--brake-dn", default="DNg105", help="the halting population the brake rows drive: DNg105 (halts the woken cord below standing against the walking command; default since 09-18 14:15) or AN19A018 (the record before it; halts the silent cord only)"); ap.add_argument("--stop-at-fruit", type=float, default=0.0, help="Hz on the brake population while sugar is on his tarsi (garden): the first piece of a feeding state, labelled; 0 = off"); ap.add_argument("--feeding", type=float, default=0.0, help="seconds sugar on the tarsi latches the feeding state (brake held on --brake-dn at --feed-brake Hz, withdrawal reflex silenced); 0 = no state"); ap.add_argument("--feed-brake", type=float, default=100.0); ap.add_argument("--satiety", type=float, default=0.0, help="seconds of feeding to fill satiety (ends feeding; taste no longer latches); 0 = none"); ap.add_argument("--satiety-tau", type=float, default=180.0); ap.add_argument("--log-types", default="", help="comma-separated cell types whose per-cell spike counts per chunk are saved to <out>.cells.npz (the compass: EPG,EPGt,PEN_a(PEN1),PEN_b(PEN2),PFL3,PFL2,Delta7)"); ap.add_argument("--log-frames", action="store_true", help="with --log-types: also save the logged cells' counts per frame (10 ms) to <out>.cells.npz as frames (n_frames x n_cells) with pose_frame, for motor patterns faster than a chunk (the leg probe, 09-21)"); ap.add_argument("--log-pre", default="", help="log, per chunk and per cell, the k strongest presynaptic partners of this type's L and R cells (e.g. DNa02) to <out>.pre.npz"); ap.add_argument("--log-pre-k", type=int, default=40); ap.add_argument("--mirror", default="off", help="mirror normalisation of bilateral pairs' input weights (src/fly_afterlife/wiring.py): off (the record) | all | vnc | a comma-separated list of types (e.g. PFL3,PFL2: the comparator pair, whose right cells carry 13 pct less traced excitation, 09-19). labelled: left-right count differences taken as tracing, not biology"); ap.add_argument("--stop-at-her", type=float, default=0.0, help="Hz on the brake (AN19A018, Sapkal 2024 BRK) while he is in contact with her; 0 = off. labelled: the stop is part of the courtship sequence in life"); ap.add_argument("--walk-dn", default="DNg100", help="the descending type the walking command drives: DNg100 (BDN2: 1,870 direct leg-MN synapses; walks the woken cord as a dose; default since 09-18 11:30) or DNp09 (the record before it; inert under the tonic floor)"); ap.add_argument("--pace-k", type=float, default=1.0, help="fixed pace rule: v = v_min + v_range x clip((leg MN - standing) / (k x standing)); 1 = twice the standing tonus is full speed (default since 09-18 11:30, standing measured in the floor after a warm-up); 4 = the record before it (degenerate: standing was 0)"); ap.add_argument("--walk", type=float, default=0.0, help="Hz of tonic drive on DNp09 (both sides), the forward-walking command (Bidaye 2020). 0 = none (the record); ~100 Hz makes the cord walk (09-17 12:50). labelled: in life the command is state-dependent"); ap.add_argument("--effector", default="wheel", help="wheel: the DNa02 running-baseline wheel (the record); legs: DNa02 wheel + the leg model's yaw (src/fly_afterlife/legs.py), touch reflex separate"); ap.add_argument("--legmn", default="leg", help="leg: the 373 leg motor neurons (MN subclass fl/ml/hl; leg_motor brief); all: every vnc_motor cell (699, incl. abdominal, wing, haltere, neck, jump: the record before 09-17 12:40)"); ap.add_argument("--reflex-sign", type=float, default=1.0, help="+1: the 09-16 convention (more right-leg spikes = left turn); -1: the drum's empirical sign (10:17, more right-leg spikes = right turn)"); ap.add_argument("--steer-ema", type=float, default=10.0, help="chunks of smoothing on the wheel's net signal (10 = one second, default since 09-18 16:10; 3 = the record before it: heading noise 42-56 deg/s rms)"); ap.add_argument("--wheel", default="HS", help="steering population for the running-baseline wheel: DNa02 (the record; one live cell under the floor), HS (the horizontal system, HSN/HSE/HSS per side, the flow-balance signal that drives DNa02 in life; both sides alive; drum 3/3 at gain +0.5, 09-18 15:12), or legMN (the cord)"); ap.add_argument("--wheel-gain", type=float, default=None, help="gain for --wheel legMN (default -0.3 deg per net spike per chunk: more right-leg drive = left turn)"); ap.add_argument("--dn-gain", type=float, default=0.0, help="gain of a second steering channel reading all descending neurons L-R through a running baseline (0 = off). 0.5 = 7 deg/chunk for the 8 C antennal asymmetry of the warm corner"); ap.add_argument("--steer", default="fixed", help="fixed: standing DNa02 offset subtracted (the record); running: per-side running baseline (adopted 09-17)"); ap.add_argument("--pace", default="state", help="fixed: v from the leg-MN rate against the standing tonus (k = --pace-k; the record); running: against his own running mean (09-17; retired 09-18: its fixed point made him walk at 0.275 whatever the cord did); state: standing / walking with a threshold and hysteresis on the smoothed rate (09-18, DeAngelis 2019 bimodal velocity)"); ap.add_argument("--wsyn-m", type=float, default=0.275, help="his mV per synapse. 0.275 = Shiu 2024 fit on FlyWire (ssTEM); FIB-SEM detects ~1.49x more synapses (Plaza 2025) -> 0.185 is the corrected value (docs/physiology/vision_motor_courtship.md)"); ap.add_argument("--wsyn-f", type=float, default=0.45, help="her mV per synapse (0.45 was the KC-sparsity calibration on the fixed build; the odour test of 22:55 says 0.275)"); ap.add_argument("--her-albedo", type=float, default=0.1, help="her body tone (0.1 dark; 0.5 = invisible against this room, the control)"); ap.add_argument("--proprio", type=float, default=0.0, help="peak Hz for his six legs of proprioceptors (leg-nerve cells only, world/legs.npz): tripod gait at 10 Hz, each leg in its stance half-cycle, scaled by pace, plus a 15 pct tonic load term; 0 = silent (was always silent)"); ap.add_argument("--deterministic", action="store_true", help="torch deterministic algorithms for flyvis: same seed -> same run, bit for bit (default GPU kernels differ at 1e-6 per call, which flips Poisson draws); costs ~+130 ms per chunk")
ap.add_argument("--antennae", default="real", choices=["wide", "real"], help="antenna tip geometry, the sample points for odour, warmth and humidity. wide: the original, 0.1 m ahead and 0.15 m to each side (4.5 mm apart at 15 mm per sim m, twelve times a fly's). real: at the front of the head and 0.35 mm apart (0.08 / 0.012 m; head ~0.7 mm wide, Gaudry 2013 / Taisz 2023 for what a fly can do with that spacing) (09-19)")
ap.add_argument("--wind-sated", default="on", choices=["off", "on"], help="the plume does not set the wind goal while the feeding state is full (Root 2011; 09-19: without it he stands against the fruit after eating, pushed upwind into it)")
ap.add_argument("--ocelli", default="on", choices=["off", "on"], help="the ocellar stand-in (garden; 09-19): OCG / OCC driven at --ocelli-hz x (1 - sky light) per side, the left cells from the left and median ocelli, the right from the right and median. the photoreceptors are not in the volume; the L-neuron sign is from life; graded in life")
ap.add_argument("--taste-hold", default=None, choices=["sugar", "water"], help="TEST STIMULUS (09-19): hold this taste on his tarsi every frame regardless of where he stands, to ask what his wiring does with it; not a sense, never a default")
ap.add_argument("--sugar-cells", default="legacy", choices=["legacy", "tarsal", "labellar"], help="which cells the sugar row drives (09-19 taste brief): legacy = the 719 LgLG* + claw_tpGRN of the record (the wrong key: local leg cells and labellar pegs); tarsal = LgLG4 + LgAG2 (54, labelled sugar, Tastekin 2026); labellar = LB3c (23)")
ap.add_argument("--sugar-hz", type=float, default=26.0, help="the sugar row's rate while sugar is on him (26 = the record; Shiu 2024's MN9 needs 30+, ~80%% of max at 100)")
ap.add_argument("--ocelli-hz", type=float, default=40.0, help="the ocellar interneurons' rate in the dark (a chosen number; 0 in full sun)")
ap.add_argument("--ocelli-light", type=float, default=None, help="TEST CONTROL (09-19): hold the sky light every ocellus sees at this value instead of the garden's, so the channel fires at a constant rate; separates a tonic push from a light effect")
ap.add_argument("--climb", default="on", choices=["off", "on"], help="garden (09-21): on = the fruit and the stone are domes he walks up (feet follow the surface, the eye rises, tarsi on the fruit taste sugar, no push-out, no touch); off = colliders he is pushed off (the record before 09-21)")
ap.add_argument("--tilt", default="on", choices=["off", "on"], help="garden (09-21): his body pitches and rolls with the slope under his feet; the eye rotates with the head; gravity deflects the antennae onto JO-C/E (--tilt-jo); the leg load splits front / back and side to side (--tilt-load)")
ap.add_argument("--tilt-jo", type=float, default=1.0, help="gravity's weight on the JO wind rows relative to a full wind (Kamikouchi 2009: JO-C/E carry gravity; rate estimate E)")
ap.add_argument("--tilt-load", type=float, default=0.5, help="fraction by which the standing leg load shifts to the downhill legs at 90 deg of slope (E)")
ap.add_argument("--noise", type=float, default=0.15, help="membrane noise, mV per step (the flybrain engine's default 0.15, the record; 0 = the noiseless network: a diagnostic for self-igniting loops, 09-21)")
ap.add_argument("--cool-rest", type=float, default=95.0, help="the cooling cells' resting rate, Hz (Budelli 2019: ~95, temperature-independent; the record). a dose flag (09-21): the wing motor artefact is fed by it")
ap.add_argument("--leg-load-hz", type=float, default=15.0, help="the standing load on the leg-nerve proprioceptors, Hz (the floor's 15 is an estimate; a dose flag, 09-21: does a proper standing signal quiet the wings?)")
ap.add_argument("--hot-r25", type=float, default=37.0, help="the hot cells' rate at 25 C, Hz (Budelli 2019: 37; the record). a dose flag (09-21)")
ap.add_argument("--reset-before-run", action="store_true", help="DIAGNOSTIC (09-21): reset the LIF state to rest after the setup calibrations (which drive bristles and command cells) and before the run, to ask whether a loop was lit by the setup")
ap.add_argument("--silence", default="", help="DIAGNOSTIC (09-21): comma-separated cell types whose threshold is set out of reach for the run (an in-silico lesion; never a default)")
ap.add_argument("--refrac-freeze", action="store_true", help="Shiu 2024's second difference from this engine (TODO 5b): the synaptic conductance does not decay during the refractory period. opt-in until measured (09-21)")
ap.add_argument("--std", default="pair", choices=["off", "pair", "sensory", "all"], help="short-term synaptic depression (the engine's Tsodyks-Markram-style rule: u 0.08 per spike, recovery 480 ms; sources under audit, 09-21): off = the record; pair = on the DNg33 pair's output synapses only (the minimal labelled correction that unlocks the flight motor); all = every cell (physiology, a refreeze)")
ap.add_argument("--labellum-hz", type=float, default=200.0, help="the labellar sugar cells' rate while the labellum is on the food (09-21; a ripe fruit: ~100-150 Hz)")
ap.add_argument("--feed-read", default="mn9", choices=["latch", "mn9"], help="how feeding is decided (09-21): latch = sugar on the tarsi latches it (the record, a stand-in); mn9 = read from his proboscis motor neurons firing (MN9 above --mn9-thr), i.e. his own wiring")
ap.add_argument("--mn9-thr", type=float, default=3.0, help="Hz per MN9 cell over the last chunk that counts as feeding")
ap.add_argument("--model", default="flow/0000/000"); ap.add_argument("--no-female", action="store_true"); ap.add_argument("--gain", type=float, default=3.0); ap.add_argument("--drive-gain", type=float, default=150.0)
args = ap.parse_args(); fps, CH = 100, 10; rng = np.random.default_rng(args.seed)
g = np.load("seam/eye_geom.npz"); eye = Eye("seam/eye_geom.npz")
posts = np.array([(0.0, 1.6, 0.35, 0.85), (0.0, -1.6, 0.35, 0.85)], np.float32)   # pillars pale (0.85): she is the only dark thing in the room
WALLS = dict(half=2.0, height=1.0, albedo=0.6)   # the room: 4 x 4 m, walls 1 m tall, lighter than the floor, darker than the sky   # pillars: floor-to-sky cylinders, bark-dark
# ---- flyvis (his eye): src/fly_afterlife/frontend.py, the block that used to be here
from fly_afterlife.frontend import FlyvisFrontEnd, TYPES as types
fe = FlyvisFrontEnd(args.model, geom="seam/eye_geom.npz", fps=fps, chunk=CH, deterministic=args.deterministic); flyvis_chunk = fe.chunk; eyemap = fe.eyemap
UV_TYPES = ["Mi15", "L5", "Mi1"]   # the UV retina's graded ON cells (flyvis) onto his own: Mi15 -> MeTu3c; L5 and Mi1 -> Dm2 -> MeTu1 (the wiring, 21:35; Dm2's excitation is L5 +2.1 and Mi1 +1.7 per cell)
fe_uv = FlyvisFrontEnd(args.model, geom="seam/eye_geom.npz", fps=fps, chunk=CH, deterministic=args.deterministic, types=UV_TYPES) if args.uv else None
# ---- his brain
Brain = FlyBrain if args.numpy_engine else FastFlyBrain
M = Brain("brain_whole.npz", seed=args.seed, params=Params(mv_per_synapse=args.wsyn_m, noise=args.noise)); M.integrate = args.integrate; M.refrac_freeze = bool(args.refrac_freeze)
if args.std != "off":   # 09-21: the DNg33 pair is bistable without depression (docs/SEAM.md); the kick bench: depression on the pair alone unlocks it
    _mask = np.ones(M.N, bool) if args.std == "all" else (M.type.astype(str) == "DNg33")
    if args.std == "sensory":   # the engine's own populations (visual, mechano, olfactory, gustatory, VPN, ALPN: the sensory encoding fix, Budelli 2019 for the phasic thermosensors) plus the pair
        _mask = _mask.copy()
        for _nm in ("visual", "mechano", "olfactory", "gustatory", "VPN", "ALPN"):
            _idx = M.pop.get(_nm) if hasattr(M, "pop") else None
            if _idx is not None and len(_idx): _mask[np.asarray(_idx)] = True
        _mask |= np.isin(M.cls.astype(str), ["thermosensory", "hygrosensory"]) | np.char.startswith(M.type.astype(str), "TRN_") | np.char.startswith(M.type.astype(str), "HRN_")
    M._std_mask = _mask; M._std_x = np.ones(M.N, np.float32); M.std_on = True; print(f"short-term depression on {int(_mask.sum())} cells ({args.std})")
mty = M.type.astype(str); mns = M.side.astype(str); mcls = M.cls.astype(str)
if args.mirror != "off":
    from fly_afterlife.wiring import mirror_normalise; print("mirror normalisation:", mirror_normalise(M, scope=(args.mirror.split(",") if "," in args.mirror or args.mirror.startswith("PFL") else args.mirror)))
groups = fe.groups(M)
groups_uv = fe_uv.groups(M, columns="seam/columns_all.npz", types=UV_TYPES) if fe_uv is not None else {}; groups_all = {**groups, **groups_uv}
if groups_uv: print("UV retina ->", {k: len(v[0]) for k, v in groups_uv.items()})
PHOTO = {}   # his own photoreceptors driven by column from the retinas (09-18): R7 from the UV retina, R8 from the green one. labelled: Poisson stand-ins for graded receptors
GOAL = None
if args.goal is not None:
    import re as _re2, pyarrow.feather as _F2
    _ta2 = _F2.read_table("data/body-annotations-male-cns-v1.0-minconf-0.5.feather", columns=["bodyId", "instance"]); _inst2 = dict(zip(_ta2.column("bodyId").to_pylist(), _ta2.column("instance").to_pylist()))
    def _wedge_of(name):
        _m = _re2.search(r"_([LR])(\d)_", name)
        return (float((int(_m.group(2)) - 1) * 45) if _m.group(1) == "L" else float((8 - int(_m.group(2))) * 45)) if _m else None
    def _col_of(name):
        _m = _re2.search(r"_C(\d+)", name); return (float((int(_m.group(1)) - 1) * 40) if _m else None)   # nine fan-shaped-body columns, 40 deg each
    _offs = []
    for _i in np.flatnonzero(mty == "PFL3"):
        _n = str(_inst2.get(int(M.bodyId[_i]), "")); _w_, _c_ = _wedge_of(_n), _col_of(_n)
        if _w_ is not None and _c_ is not None: _offs.append(np.exp(1j * np.radians(_c_ - _w_)))
    _delta = float(np.degrees(np.angle(np.mean(_offs)))) if _offs else 0.0   # the column frame minus the wedge frame, from PFL3's own anatomy
    _fc2 = np.flatnonzero(np.char.startswith(mty, "FC2")); _cols = np.array([_col_of(str(_inst2.get(int(M.bodyId[_i]), ""))) for _i in _fc2], dtype=object)
    _ok = np.array([c is not None for c in _cols]); _fc2 = _fc2[_ok]; _cols = _cols[_ok].astype(float)
    _goal_col = (args.goal + _delta) % 360.0; _stim = np.exp(2.0 * (np.cos(np.radians(_cols - _goal_col)) - 1.0))
    GOAL = dict(cells=_fc2, stim=_stim.astype(np.float32), delta=_delta, deg=float(args.goal), cols=_cols.astype(np.float32))
    print(f"goal stand-in: {len(_fc2)} FC2 cells by column; column frame - wedge frame = {_delta:+.0f} deg (from {len(_offs)} PFL3 cells); goal {args.goal:.0f} deg -> column angle {_goal_col:.0f}")
RING = None
if args.ring:
    import re as _re, pyarrow.feather as _F
    from fly_afterlife.wiring import ring_map
    _ta = _F.read_table("data/body-annotations-male-cns-v1.0-minconf-0.5.feather", columns=["bodyId", "instance"]); _inst = dict(zip(_ta.column("bodyId").to_pylist(), _ta.column("instance").to_pylist()))
    _epg = np.flatnonzero(mty == "EPG"); _wedge = {}
    for _i in _epg:
        _m = _re.search(r"_([LR])(\d)", str(_inst.get(int(M.bodyId[_i]), "")))
        if _m: _wedge[int(_i)] = float((int(_m.group(2)) - 1) * 45) if _m.group(1) == "L" else float((8 - int(_m.group(2))) * 45)
    _src = np.repeat(np.arange(M.N), np.diff(M._out_ptr)); _er = np.flatnonzero(np.char.startswith(mty, "ER")); _wt = np.zeros(M.N)
    _mm = np.isin(_src, _er) & np.isin(M._out_tgt, _epg); np.add.at(_wt, _src[_mm], -M._out_w[_mm]); _ring_cells = np.flatnonzero(_wt > 20)
    _rho = (np.arange(len(_ring_cells)) * 360.0 / len(_ring_cells)); _sun_az = float(np.degrees(np.arctan2(0.3, 0.6)))   # the garden's sun (garden.sun_dir)
    _n = ring_map(M, _ring_cells, _rho, _wedge, _sun_az); RING = dict(cells=_ring_cells, rho=np.radians(_rho), sun_az=_sun_az)
    print(f"ring stand-in: {len(_ring_cells)} ring neurons with fields tiling the circle, {_n} ER->EPG edges notched; ExR1 at {args.ring_exr} Hz; sun azimuth {_sun_az:.1f}")
if args.uv_photo:
    _cu = np.load("seam/columns_uv.npz"); _gk = {(str(s_), int(a_), int(h_)): i for i, (s_, a_, h_) in enumerate(zip(g["side"], g["hex1"], g["hex2"]))}
    for fam, retina in (("R7", "lum_uv"), ("R8", "lum")):
        for s_ in "LR":
            kk = np.char.startswith(_cu["type"].astype(str), fam) & (_cu["side"].astype(str) == s_) & ~np.char.startswith(_cu["type"].astype(str), fam + "d")   # the dorsal rim (R7d / R8d) stays at rest: no polarisation in this eye
            gi_ = np.array([_gk.get((s_, int(a_), int(h_)), -1) for a_, h_ in zip(_cu["hex1"][kk], _cu["hex2"][kk])]); ok_ = gi_ >= 0
            PHOTO[(fam, s_)] = (_cu["idx"][kk][ok_].astype(int), gi_[ok_], retina)
    print("photoreceptors by column:", {k: len(v[0]) for k, v in PHOTO.items()})
RM = {}
_lm = np.load("world/legmn.npz"); LEGMN_SEL = (M.sc == "vnc_motor") if args.legmn == "all" else np.isin(np.arange(M.N), _lm["leg"])
for name, sel in [("DNa02", mty == "DNa02"), ("DNa01", mty == "DNa01"), ("DNb06", mty == "DNb06"), ("DNg13", mty == "DNg13"), ("IN12B014", mty == "IN12B014"), ("HS", np.char.startswith(mty, "HS")), ("PFL3", mty == "PFL3"), ("pC1", np.char.startswith(mty, "pC1")), ("pIP10", mty == "pIP10"), ("mAL", np.char.startswith(mty, "mAL")), ("LC10a", mty == "LC10a"), ("ORN_VA1v", mty == "ORN_VA1v"), ("legMN", LEGMN_SEL), ("DN", M.sc == "descending_neuron")]:
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
if GOAL is not None: REG.add(ReceptorClass("goal_FC2", GOAL["cells"], Scaled(args.goal_hz), lambda st: GOAL["stim"], source="the goal in the fan-shaped body as a bump over FC2 columns (stand-in for menotaxis; Mussells Pires 2024; 09-18)"))
if RING is not None:
    REG.add(ReceptorClass("ring_ExR1", np.flatnonzero(mty == "ExR1"), Hold(args.ring_exr), lambda st: True, source="ExR1 as the ring's tonic excitation (stand-in, 09-18)"))
    REG.add(ReceptorClass("ring_ER", RING["cells"], Scaled(args.ring_er), (lambda st: np.exp(2.0 * (np.cos(np.radians(RING["sun_az"] - st["heading"]) - RING["rho"]) - 1.0)) if st.get("heading") is not None else 0.0), source="ring neurons fired by the sun at their field azimuth (von Mises, kappa 2); the map imposed (Kim 2019; Fisher 2019)"))
for (fam, s_), (idx_, gi_, retina_) in PHOTO.items():
    REG.add(ReceptorClass(f"{fam}_{s_}", idx_, Scaled(args.drive_gain), (lambda st, gi_=gi_, retina_=retina_: (st[retina_][gi_] if st.get(retina_) is not None else 0.0)), source="his own R7 (UV retina) / R8 (green retina) by column; Poisson stand-ins for graded photoreceptors (09-18)"))
for (t, s), (idx, hx) in groups_all.items():
    REG.add(ReceptorClass((f"UV_{t}_{s}" if (t, s) in groups_uv else f"T4T5_{t}_{s}"), idx, Scaled((args.uv_gain if (args.uv_gain is not None and (t, s) in groups_uv) else args.drive_gain)), (lambda st, t=t, s=s, hx=hx: (st["a"][(s, t)][st["f"]] - st["rest"][(s, t)])[hx]), source="seam v2"))
if args.proprio > 0:
    for leg_, idx_ in LEGS.items(): REG.add(ReceptorClass(f"proprio_{leg_}", idx_, GaitLeg(args.proprio, TRIPOD[leg_], STEP_HZ), lambda st: st["pace"]))   # 09-21: the frame's own time (the chunk-end time made the 10 Hz sine a constant per leg: chunk ends fall on the period))
for s_ in "LR": REG.add(ReceptorClass(f"bristle_{s_}", TACT_M[s_], Hold(150.0) if args.bristle == "hold" else Adapting(), (lambda st, s_=s_: st["tm"] == "B" or st["tm"] == s_)))
REG.add(ReceptorClass("ppk_F", PPK_F, TapBurst(TAP_HZ, TAP_MS), lambda st: st["kind"] == 2)); REG.add(ReceptorClass("ppk_M", PPK_M, TapBurst(TAP_HZ, TAP_MS), lambda st: st["kind"] == 2))
if args.walk > 0: WALK = np.flatnonzero(((mty == args.walk_dn) | np.char.startswith(mty, args.walk_dn + "_")) & (M.sc == "descending_neuron")); REG.add(ReceptorClass(f"walk_{args.walk_dn}", WALK, Scaled(args.walk), lambda st: float(st.get("walk_gain", 1.0)), source="Bidaye 2020 (DNp09) / Sapkal 2024 (BDN2 = DNg100); the command as a tonic drive, labelled"))
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
    SUGAR_SETS = {"legacy": (np.char.startswith(mty, "LgLG") | (mty == "claw_tpGRN")),                      # 719: 669 local leg cells + 50 labellar taste pegs (09-17; the wrong key, docs/physiology/taste_per.md)
                  "tarsal": np.isin(mty, ["LgLG4", "LgAG2"]),                                                   # 54: Gr64f+Ir56b tarsal sugar (43) + Gr61a ascending appetitive (11), Tastekin 2026
                  "labellar": (mty == "LB3c")}                                                                   # 23: Gr64f labellar sugar (Shiu 2024's extension result used labellar GRNs)
    LEG_GRN = np.flatnonzero(SUGAR_SETS[args.sugar_cells])
    if args.sugar_cells == "legacy":   # the record's row (the wrong key: docs/physiology/taste_per.md); kept for comparison
        pass
    LAB_GRN = np.flatnonzero(mty == "LB3c")   # 09-21: the labellar sugar cells fire when the labellum is on the food (standing still on the fruit), at the food's rate
    REG.add(ReceptorClass("sugar_labellum", LAB_GRN, Hold(args.labellum_hz), lambda st: st.get("labellum") == "sugar", source="Gr64f labellar GRNs (LB3c, Tastekin 2026) at ~100-150 Hz on a ripe fruit (Gr5a ~100-150 Hz at 100-500 mM sucrose); the labellum-on-food condition is a geometry stand-in (09-21)"))
    REG.add(ReceptorClass("sugar_at_fruit", LEG_GRN, Hold(args.sugar_hz), lambda st: st.get("taste") == "sugar", source="chemo brief s.3: sugar GRNs ~65 Hz at 100 mM x ~40% of tarsal GRNs being sugar-tuned (E; the leg GRN types carry no sugar / bitter label)"))
    print(f"garden senses: fruit ORNs {len(FRUIT_ORN['L'])}/{len(FRUIT_ORN['R'])}, dry {len(DRY)}, moist {len(MOIST)}, leg GRNs {len(LEG_GRN)}")
    if args.wind == "on":   # the wind on his antennae: the windward side's JO-C/E fire more (Yorozu 2009); populations equalised (203 L / 132 R typed: a tracing asymmetry)
        _joce = {s_: np.flatnonzero(np.array([t.startswith("JO-C") or t.startswith("JO-E") for t in mty]) & (mns == s_)) for s_ in "LR"}; _nmin = min(len(_joce["L"]), len(_joce["R"])); _r0 = np.random.default_rng(0)
        JOW = {s_: np.sort(_r0.choice(_joce[s_], _nmin, replace=False)) for s_ in "LR"}
        def _wind_stim(st, s_):
            rel = st.get("wind_rel", 0.0); lat = max(0.0, np.sin(np.radians(rel))) if s_ == "L" else max(0.0, -np.sin(np.radians(rel))); head = 0.5 * max(0.0, np.cos(np.radians(rel)))
            if args.tilt == "on":   # gravity on the aristae (09-21): roll deflects the downhill antenna as a side wind would, pitch both as a head or tail wind
                rl_, pt_ = np.radians(st.get("roll", 0.0)), np.radians(st.get("pitch", 0.0))
                lat += args.tilt_jo * (max(0.0, -np.sin(rl_)) if s_ == "L" else max(0.0, np.sin(rl_))); head += args.tilt_jo * 0.5 * abs(np.sin(pt_)); lat = min(lat, 1.0); head = min(head, 0.5)
            gate = 1.0 if args.wind_gate == "none" else (1.0 if (st.get("odour_L", {}).get("fruit", 0.0) > 0.02 or st.get("odour_R", {}).get("fruit", 0.0) > 0.02) else 0.0)
            return (0.25 + 0.75 * (lat + head)) * gate    # -> Scaled(20): 5 Hz floor-ish in still air is the floor row; wind adds up to 20 Hz on the windward side
        for s_ in "LR": REG.add(ReceptorClass(f"wind_JO_{s_}", JOW[s_], Scaled(20.0), (lambda st, s_=s_: _wind_stim(st, s_)), source="Yorozu 2009 (JO C/E wind); rate estimate (E); equalised populations (09-18)"))
        print(f"wind on JO: {_nmin} cells per side, gate {args.wind_gate}")
if args.thermo != "off":   # his arista thermosensors, sampled at each antenna tip (VP1m / VP1l left out: labels under audit, Marin 2020)
    HOT = {s_: np.flatnonzero((mty == "TRN_VP2") & (mns == s_)) for s_ in "LR"}; COOL = {s_: np.flatnonzero(np.isin(mty, ["TRN_VP3a", "TRN_VP3b"]) & (mns == s_)) for s_ in "LR"}
    for s_ in "LR":
        REG.add(ReceptorClass(f"hot_{s_}", HOT[s_], HotCells(r25=args.hot_r25), (lambda st, s_=s_: st["T_" + s_])))
        REG.add(ReceptorClass(f"cool_{s_}", COOL[s_], CoolingCells(rest_hz=args.cool_rest), (lambda st, s_=s_: st["T_" + s_])))
    print(f"thermo cells: hot L {len(HOT['L'])} R {len(HOT['R'])}, cooling L {len(COOL['L'])} R {len(COOL['R'])}; mode {args.thermo}")
OCE = None
if args.ocelli == "on":   # the ocellar stand-in (09-19): light level per ocellus into the interneurons, with the sign of life
    from fly_afterlife.receptors import OcellarL
    OCE = {s_: np.flatnonzero((np.char.startswith(mty, "OCG") | np.char.startswith(mty, "OCC")) & (mns == s_)) for s_ in "LR"}
    for s_, k_ in (("L", "left"), ("R", "right")):
        REG.add(ReceptorClass(f"ocelli_{s_}", OCE[s_], OcellarL(dark_hz=args.ocelli_hz), (lambda st, k_=k_: (args.ocelli_light if args.ocelli_light is not None else (0.5 * (st["ocelli"]["median"] + st["ocelli"][k_]) if "ocelli" in st else 1.0)))))
    print(f"ocelli: OCG / OCC L {len(OCE['L'])} R {len(OCE['R'])} cells at {args.ocelli_hz:.0f} Hz in the dark")
if args.floor:
    from fly_afterlife.receptors import tonic_floor
    _fl = tonic_floor(M, REG)
    if args.floor_drop: _drop = set(args.floor_drop.split(",")); REG.classes = [rc for rc in REG.classes if rc.name not in _drop]; _fl = [rc for rc in _fl if rc.name not in _drop]; print(f"floor rows dropped: {sorted(_drop)}")
    if args.tilt == "on":   # the leg load on a slope (09-21): the floor's 15 Hz on the leg proprioceptors shifts toward the downhill legs
        _legp = [rc for rc in _fl if rc.name == "floor_leg_proprio"]
        if _legp:
            from fly_afterlife.receptors import select as _select
            _lp = _legp[0]
            for seg_, nv_ in (("fl", "ProLN"), ("ml", "MesoLN"), ("hl", "MetaLN")):
                for s_ in "LR":
                    cells_ = np.intersect1d(_lp.cells, _select(M, cls="mechanosensory_proprioceptive", entry_nerve=[nv_], side=s_))
                    if cells_.size == 0: continue
                    def _load(st, seg_=seg_, s_=s_):
                        pt_, rl_ = np.radians(st.get("pitch", 0.0)), np.radians(st.get("roll", 0.0))
                        fb_ = {"fl": -1.0, "ml": 0.0, "hl": 1.0}[seg_] * np.sin(pt_)          # nose up: the hind legs bear more
                        lr_ = (-1.0 if s_ == "L" else 1.0) * np.sin(rl_)                       # left side up: the right legs bear more
                        return 0.5 * max(0.0, 1.0 + args.tilt_load * (fb_ + lr_))   # x Scaled(2 x the standing load): the flat rate on the flat, up to double on the downhill legs, 0 on the uphill
                    REG.add(ReceptorClass(f"load_{seg_}_{s_}", cells_, Scaled(2.0 * args.leg_load_hz), _load, source="standing load shifted by the slope (E; hair plates / campaniforms under load, mechano brief s.2)"))
    for rc in _fl:
        if rc.name == "floor_cool": rc.transducer.hz = args.cool_rest   # the dose flag reaches the floor's row too (09-21)
        if rc.name == "floor_hot": rc.transducer.hz = args.hot_r25
        if rc.name == "floor_leg_proprio": rc.transducer.hz = args.leg_load_hz
    _flc = np.unique(np.concatenate([rc.cells for rc in _fl])); M.driven[_flc] = True; M._driven_idx = np.flatnonzero(M.driven); print(f"tonic floor: {len(_fl)} rows, {len(_flc)} cells")
print(REG.table()); REGF = Registry()   # a tap is a burst: ~60 Hz cap (Weiss 2011 GRN ceiling), ~300 ms, not a 150 Hz hold (docs/physiology/chemo_thermo_hygro.md)
RM["ppkF"] = PPK_F; RM["DNp09"] = np.flatnonzero(np.char.startswith(mty, "DNp09")); RM["MDN"] = np.flatnonzero(np.char.startswith(mty, "MDN")); RM["legMN"] = np.flatnonzero(LEGMN_SEL)
M.define_odor("flyodour", n_channels=1, seed=0); M._odor_map["flyodour"] = {"ORN_VA1v": 1.0, "ORN_VA1d": 0.6}
M.driven[:] = False
for cl in M.SENSORY_CLASSES: M.driven[M.cls == cl] = True
for t, (idx, _) in groups_all.items(): M.driven[idx] = True
for (fam, s_), (idx_, _, _) in PHOTO.items(): M.driven[idx_] = True
if RING is not None: M.driven[RING["cells"]] = True; M.driven[mty == "ExR1"] = True
if GOAL is not None: M.driven[GOAL["cells"]] = True
if args.walk > 0: M.driven[WALK] = True   # the command cells must be in the driven set (after the sensory reset above)
if OCE is not None: M.driven[np.concatenate([OCE["L"], OCE["R"]])] = True
if args.stop_at_her > 0 or args.stop_at_fruit > 0 or args.feeding > 0: M.driven[BRK] = True   # (13:40: only --stop-at-her marked them; the fruit brake and the feeding latch drove cells the engine never drew)
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
if args.antennae == "real": m.ant_ahead, m.ant_half = BODY, 0.012; her.ant_ahead, her.ant_half = HER_R, 0.012   # 09-19: a fly's antennae are ~0.35 mm apart at the front of the head
room = Room(half=WALLS["half"], height=WALLS["height"], albedo=WALLS["albedo"], sky=0.8, ground=0.4, posts=list(posts), pillar_height=args.pillar_height)
if args.world == "arena":
    from fly_afterlife.arena import Arena
    room = Arena(radius=args.arena_radius, height=0.47, albedo=0.6, sky=0.8, ground=0.4); m.x, m.y, m.h = (0.0, 0.0, 0.0) if args.start is None else tuple(float(v) for v in args.start.split(",")); her.present = False
if args.world == "garden":
    from fly_afterlife.garden import Garden
    room = Garden(seed=args.seed); m.x, m.y, m.h = (-0.5, -0.5, 35.0) if args.start is None else tuple(float(v) for v in args.start.split(",")); her.x, her.y, her.h = 1.2, 0.3, 180.0
    room.climb = args.climb == "on"; room.tilt = args.tilt == "on" and room.climb
    if args.taste_hold:   # the test stimulus: taste imposed after the world's contacts each frame
        _sf0 = room.step_frame
        def _sf_hold(m_, f_, fps_): _sf0(m_, f_, fps_); m_.taste = args.taste_hold
        room.step_frame = _sf_hold
    if args.no_plume: room.odour = lambda x, y, t, sources=None, rng=None: {"fruit": 0.0}
    if args.fruit_tone == "litter": fx_, fy_, fz_, fr_, _ = room.fruit; room.fruit = (fx_, fy_, fz_, fr_, float(room.tex.mean()))   # posts stay float32 rows: the oracle's arithmetic
THERMO_FIELDS = {"field": [dict(base=25.0, x=1.5, y=1.5, dT=8.0, sigma=0.8)],                                                     # a warm corner, 33 C at the centre
                 "field2": [dict(base=25.0, x=1.5, y=1.5, dT=8.0, sigma=0.8), dict(x=-1.5, y=-1.5, dT=-15.0, sigma=0.8)],           # warm corner 33 C + cold corner 10 C (nate, 09-17 evening)
                 "field2x": [dict(base=25.0, x=1.5, y=1.5, dT=15.0, sigma=0.8), dict(x=-1.5, y=-1.5, dT=-15.0, sigma=0.8)]}        # hot corner 40 C + cold corner 10 C: the extremes
if args.thermo in THERMO_FIELDS: room.thermal = THERMO_FIELDS[args.thermo]
# warm-up: flyvis state + T4/T5 rest on the still scene; LIF rest
def see_chunk():
    """one still chunk through both front ends: the green retina to T4/T5, and with --uv the UV retina to Mi15."""
    a_ = flyvis_chunk(np.stack([eye.render(room.scene([her]), pos=(m.x, m.y, 0.5), heading_deg=m.h) for _ in range(CH)]))
    if fe_uv is not None and hasattr(room, "scene_uv"): a_ = dict(a_); a_.update(fe_uv.chunk(np.stack([eye.render(room.scene_uv([her]), pos=(m.x, m.y, 0.5), heading_deg=m.h) for _ in range(CH)])))
    return a_
acc = {}
for c in range(10):
    a = see_chunk()
    if c >= 5:
        for k_, v_ in a.items(): acc.setdefault(k_, []).append(v_)
rest = {k_: np.concatenate(v_).mean(0) for k_, v_ in acc.items()}
for _ in range(500):
    M.step()
    if not args.no_female: F.step()
# calibrations (src/fly_afterlife/effectors.py): the same standing loops, once per run
from fly_afterlife.effectors import Steering, RunningBaselineSteering, MultiWheelSteering, Pace, RunningPace, StatePace, FeedingState, HerSteering, SongDetector, dna02_rest_offset, standing_baselines, reflex_gain, apply_tonic, TONIC_SKIP
def render_chunk(): return see_chunk()
def drive_frame(a, f):
    for (t, s), (idx, hx) in groups_all.items(): M.drive_hz[idx] = args.drive_gain * np.clip((a[(s, t)][f] - rest[(s, t)])[hx], 0, 1)
TONIC = (lambda t_: apply_tonic(REG, M, t_, 1.0 / fps, skip=TONIC_SKIP + ("UV_", "R7_", "R8_", "ring_ER")))   # the standing brain: floor, command, thermal cells at 25 C (09-18)
def TONIC_STAND(t_):   # standing = the floor without the walking command (10:31: with it, the pace reference rose with the dose; 10:55: the cells kept their drive when the row was skipped)
    apply_tonic(REG, M, t_, 1.0 / fps, skip=TONIC_SKIP + ("walk_", "UV_", "R7_", "R8_", "ring_ER"))
    if args.walk > 0: M.drive_hz[WALK] = 0.0
_tonic_rows = [rc for rc in REG.classes if not rc.name.startswith(TONIC_SKIP)]
for f_ in range(2 * fps if _tonic_rows else 0):   # warm-up (only when tonic rows exist, so the oracle's silent brain is untouched): two seconds under the tonic rows before any calibration (10:55: the floor's settling transient was being measured as standing: 51 / 82 / 106 / 58 per chunk for one seed)
    TONIC(f_ / fps)
    for _ in range(SPF): M.step()
rest_net = dna02_rest_offset(M, RM, drive_frame, render_chunk, CH, SPF, tonic=TONIC); print(f"his DNa02 rest offset {rest_net:+.2f}/chunk")
leg_stand, dn_stand_f = standing_baselines(M, F if not args.no_female else None, RM, RF, drive_frame, render_chunk, CH, SPF, tonic=TONIC_STAND); print(f"pace baselines per chunk: his leg MN {leg_stand:.0f}, her DN {dn_stand_f:.0f}")
leg_gain, asym_side = reflex_gain(M, RM, TACT_M, CH, SPF, kernel=(None if args.bristle == "hold" else Adapting()), fps=fps, tonic=TONIC); leg_gain *= args.reflex_sign; print(f"touch reflex: leg-MN asymmetry (R-L)/(R+L) with left bristles {asym_side['L']:+.3f}, right {asym_side['R']:+.3f} -> gain {leg_gain:.0f} deg per unit asymmetry")
from fly_afterlife.legs import LegModel, LegSteering
PFL3V_NULL = None; PFL2_ENDS = None
if GOAL is not None and (args.goal_wheel_v > 0 or args.pfl2_walk):
    # the comparator's null point (09-19 11:25): PFL3's mean membrane L-R with the goal placed at his current heading (error 0),
    # 20 chunks; subtracted as the channel's fixed baseline. PFL3 L rests ~0.25 mV above R (the left-heavy brain), which is the
    # size of the goal signal itself, so without this the channel steers to where L-R happens to cross zero, 60-100 deg off.
    _cols_goal = np.exp(2.0 * (np.cos(np.radians(_cols - ((m.h + GOAL["delta"]) % 360.0))) - 1.0)).astype(np.float32); _saved = GOAL["stim"]; GOAL["stim"] = _cols_goal
    _pl = np.flatnonzero((mty == "PFL3") & (mns == "L")); _pr = np.flatnonzero((mty == "PFL3") & (mns == "R")); _vl = _vr = 0.0; _n = 0
    for c_ in range(20):
        a_ = render_chunk()
        for f_ in range(CH):
            TONIC((c_ * CH + f_) / 100.0); drive_frame(a_, f_)
            if RING is not None: M.drive_hz[RING["cells"]] = args.ring_er * np.exp(2.0 * (np.cos(np.radians(RING["sun_az"] - m.h) - RING["rho"]) - 1.0))   # the ring neurons need his heading: applied by hand so the bump is present at the null
            for _ in range(SPF): M.step(); _vl += float(M.v[_pl].mean()); _vr += float(M.v[_pr].mean()); _n += 1
    _p2 = np.flatnonzero(mty == "PFL2"); PFL2_ENDS = None
    if args.pfl2_walk:
        _ends = []
        for _ang in (0.0, 180.0):   # the goal ahead, then behind
            GOAL["stim"] = np.exp(2.0 * (np.cos(np.radians(_cols - ((m.h + _ang + GOAL["delta"]) % 360.0))) - 1.0)).astype(np.float32); _v2 = 0.0; _n2 = 0
            for c_ in range(20):
                a_ = render_chunk()
                for f_ in range(CH):
                    TONIC((c_ * CH + f_) / 100.0); drive_frame(a_, f_)
                    if RING is not None: M.drive_hz[RING["cells"]] = args.ring_er * np.exp(2.0 * (np.cos(np.radians(RING["sun_az"] - m.h) - RING["rho"]) - 1.0))
                    for _ in range(SPF): M.step(); _v2 += float(M.v[_p2].mean()); _n2 += 1
            _ends.append(100.0 * _v2 / _n2)
        PFL2_ENDS = tuple(_ends); print(f"PFL2 membrane: goal ahead {PFL2_ENDS[0] / 100:+.2f} mV, behind {PFL2_ENDS[1] / 100:+.2f} mV")
    GOAL["stim"] = _saved
    if args.goal_null != "off": PFL3V_NULL = (100.0 * _vl / _n, 100.0 * _vr / _n); print(f"PFL3 null point (goal ahead): L {PFL3V_NULL[0] / 100:+.2f} mV, R {PFL3V_NULL[1] / 100:+.2f} mV, L-R {(PFL3V_NULL[0] - PFL3V_NULL[1]) / 100:+.3f}")
    else: print("PFL3 null point: off (the pair is mirrored)")
WGAIN = args.gain if args.wheel == "DNa02" else (args.wheel_gain if args.wheel_gain is not None else (0.5 if args.wheel == "HS" else -0.3))   # HS: +0.5 from the drum (15:12); legMN: -0.3 (10:17)
steer = LegSteering(LegModel(M), wheel_gain=args.gain, leg_gain=leg_gain) if args.effector == "legs" else Steering(gain=args.gain, rest_net=rest_net, leg_gain=leg_gain) if args.steer == "fixed" else (RunningBaselineSteering(gain=WGAIN, leg_gain=leg_gain, wheel=args.wheel, ema_n=args.steer_ema) if (args.dn_gain == 0 and args.goal_wheel == 0 and args.goal_wheel_v == 0) else MultiWheelSteering(wheels=[(args.wheel, WGAIN)] + ([("DN", args.dn_gain)] if args.dn_gain > 0 else []) + ([("PFL3", args.goal_wheel, "fixed", args.goal_ema)] if args.goal_wheel > 0 else []) + ([("PFL3v", args.goal_wheel_v / 100.0, "fixed", args.goal_ema, PFL3V_NULL)] if args.goal_wheel_v > 0 else []), leg_gain=leg_gain, ema_n=args.steer_ema))
pace = Pace(leg_stand=leg_stand, k=args.pace_k) if args.pace == "fixed" else (StatePace(leg_stand=leg_stand) if args.pace == "state" else RunningPace()); hers = HerSteering(rng); songdet = SongDetector()
m.v = 0.3; her.v = 0.15
# ---- loop (src/fly_afterlife/episode.py)
from fly_afterlife.episode import Episode
_COMPASS = None
if args.ring:
    _epg_c = np.flatnonzero(mty == "EPG"); _wedge_idx = np.array([int(round(_wedge.get(int(i), -45.0) / 45.0)) % 8 if int(i) in _wedge else -1 for i in _epg_c])
    _COMPASS = dict(cells=_epg_c[_wedge_idx >= 0], wedge=_wedge_idx[_wedge_idx >= 0], rows=[], pfl=[])
    _COMPASS["goal"] = []; _COMPASS["contact_s"] = 0.0; _COMPASS["switches"] = 0; _goal_rng = np.random.default_rng(args.seed + 7)
    def _hook_compass(ep_, c_, cnt_):
        acc_ = ep_.last_accM[_COMPASS["cells"]]; _COMPASS["rows"].append(np.bincount(_COMPASS["wedge"], weights=acc_, minlength=8).astype(np.float32))
        _COMPASS["pfl"].append((float(cnt_.get("PFL3v_L", 0.0)), float(cnt_.get("PFL3v_R", 0.0)), float(getattr(ep_, "walk_gain", 1.0))))
        if GOAL is not None and args.goal_switch > 0:   # the goal yields at a wall
            _b = ep_.m; _room = ep_.room   # at the wall: his body within 2 cm of the boundary (a fly standing against a wall is not pushed by it, so touch events miss him)
            at_wall_ = (np.hypot(_b.x, _b.y) > _room.radius - _b.r - 0.02) if hasattr(_room, "radius") else (max(abs(_b.x), abs(_b.y)) > _room.half - _b.r - 0.02)
            touched_ = at_wall_ or any(x_ is not None for x_ in ep_.TOUCH[-CH:]); _COMPASS["contact_s"] = _COMPASS["contact_s"] + CH / fps if touched_ else 0.0
            if _COMPASS["contact_s"] >= args.goal_switch:
                _inward = float(np.degrees(np.arctan2(-_b.y, -_b.x))) if at_wall_ else float(_goal_rng.uniform(0.0, 360.0))   # away from the wall he is on: the half-circle facing the centre
                GOAL["deg"] = float((_inward + _goal_rng.uniform(-90.0, 90.0)) % 360.0) if at_wall_ else _inward; GOAL["stim"][:] = np.exp(2.0 * (np.cos(np.radians(GOAL["cols"] - ((GOAL["deg"] + GOAL["delta"]) % 360.0))) - 1.0)).astype(np.float32)
                _COMPASS["contact_s"] = 0.0; _COMPASS["switches"] += 1
        if GOAL is not None and args.goal_wind > 0 and hasattr(ep_.room, "wind"):
            _od = getattr(ep_, "_last_odour", None); _whiff = bool(_od is not None and (float(_od[0].get("fruit", 0.0)) > 0.02 or float(_od[1].get("fruit", 0.0)) > 0.02))
            if args.wind_sated == "on" and bool(getattr(getattr(ep_, "state", None), "full", False)): _whiff = False   # the sated fly ignores the food odour (Root 2011: sNPF lowers ORN sensitivity with feeding; 09-19: at the source the whiff never ends, so the goal never released him)
            if _whiff: _COMPASS["surge_until"] = ep_.POSE.__len__() / fps + args.goal_wind
            _upwind = float(np.degrees(np.arctan2(-ep_.room.wind[1], -ep_.room.wind[0]))) % 360.0
            if ep_.POSE.__len__() / fps < _COMPASS.get("surge_until", -1.0):
                if _COMPASS.get("wind_goal") is None: _COMPASS["wind_goal"] = GOAL["deg"]   # remember the wandering goal to return to
                if abs(((GOAL["deg"] - _upwind + 180) % 360) - 180) > 1.0:
                    GOAL["deg"] = _upwind; GOAL["stim"][:] = np.exp(2.0 * (np.cos(np.radians(GOAL["cols"] - ((GOAL["deg"] + GOAL["delta"]) % 360.0))) - 1.0)).astype(np.float32); _COMPASS["surges"] = _COMPASS.get("surges", 0) + 1
            elif _COMPASS.get("wind_goal") is not None:
                GOAL["deg"] = _COMPASS["wind_goal"]; GOAL["stim"][:] = np.exp(2.0 * (np.cos(np.radians(GOAL["cols"] - ((GOAL["deg"] + GOAL["delta"]) % 360.0))) - 1.0)).astype(np.float32); _COMPASS["wind_goal"] = None
        _COMPASS["goal"].append(float(GOAL["deg"]) if GOAL is not None else np.nan)
_CELLS = None
if args.log_types:
    _lt = [x for x in args.log_types.split(",") if x]; _lc = np.flatnonzero(np.isin(mty, _lt)); _CELLS = dict(cells=_lc, counts=[])
    def _hook_cells(ep_, c_, cnt_): _CELLS["counts"].append(ep_.last_accM[_lc].copy())
    print(f"logging {len(_lc)} cells of types {_lt}")
_PRE = None
if args.log_pre:
    _src = np.repeat(np.arange(M.N), np.diff(M._out_ptr)); _tgt = M._out_tgt; _w = M._out_w; _sel = {}
    for s_ in "LR":
        tg = np.flatnonzero((mty == args.log_pre) & (mns == s_)); m_ = np.isin(_tgt, tg); ws = np.zeros(M.N); np.add.at(ws, _src[m_], _w[m_]); order = np.argsort(-np.abs(ws))[:args.log_pre_k]; _sel[s_] = (order, ws[order])
    _cells = np.unique(np.concatenate([_sel["L"][0], _sel["R"][0], np.flatnonzero(mty == args.log_pre)])); _PRE = dict(cells=_cells, counts=[])
    _wL = np.zeros(M.N); _wL[_sel["L"][0]] = _sel["L"][1]; _wR = np.zeros(M.N); _wR[_sel["R"][0]] = _sel["R"][1]
    def _hook(ep_, c_, cnt_): _PRE["counts"].append(ep_.last_accM[_cells].copy())
    print(f"logging {len(_cells)} cells: the {args.log_pre_k} strongest inputs to {args.log_pre} L and R")
_MN9 = np.flatnonzero(mty == "MN9")
def _hook_mn9(ep_, c_, cnt_):   # MN9 rate per cell, smoothed over ~1 s (EMA of 10 chunks): one stray spike in a chunk is not feeding (09-21)
    hz_ = float(ep_.last_accM[_MN9].sum()) / max(1, len(_MN9)) * fps / CH; ep_.mn9_hz = 0.9 * float(getattr(ep_, "mn9_hz", 0.0)) + 0.1 * hz_
_HOOKS = [h for h in (globals().get(n_) for n_ in ("_hook_compass", "_hook_cells", "_hook", "_hook_mn9")) if h is not None]   # each is defined only under its own flag   # 09-19 18:05: ALL that apply, in this order. before, the slot took one hook and --log-types evicted the compass (no goal yield, no wind goal) in any run that logged cells
def _hook_all(ep_, c_, cnt_):
    for h in _HOOKS: h(ep_, c_, cnt_)
if args.silence:   # the in-silico lesion (09-21): the named types cannot spike this run
    _sil = np.flatnonzero(np.isin(mty, [x for x in args.silence.split(",") if x])); M.v_th[_sil] = np.float32(1e6); print(f"silenced {len(_sil)} cells of {args.silence}")
if args.reset_before_run: _nz = int((M.drive_hz != 0).sum()); _ne = int((M._ext != 0).sum()); M.reset(); M.drive_hz[:] = 0.0; M._ext[:] = 0.0; print(f"LIF state reset to rest before the run (diagnostic); drive_hz had {_nz} nonzero cells left by the setup, zeroed; the engine's tonic current _ext was nonzero on {_ne} cells (mean {float(M._ext.mean()):.3f} mV before zeroing), zeroed")
ep = Episode(fps=fps, chunk=CH, eye=eye, room=room, him=m, her=her, brains=(M, F if not args.no_female else None), readouts=(RM, RF), registries=(REG, REGF), front_end=flyvis_chunk, front_end_uv=(fe_uv.chunk if fe_uv is not None else None), rest=rest, effectors=(steer, pace, hers, songdet), lam=LAM, vread=(({"PFL3v": (np.flatnonzero((mty == "PFL3") & (mns == "L")), np.flatnonzero((mty == "PFL3") & (mns == "R")))} | ({"PFL2v": (np.flatnonzero((mty == "PFL2") & (mns == "L")), np.flatnonzero((mty == "PFL2") & (mns == "R")))} if args.pfl2_walk else {})) if (args.goal is not None) else None), walkmod=((lambda cnt: float(np.clip(args.pfl2_floor + (1.0 - args.pfl2_floor) * ((cnt["PFL2v_L"] + cnt["PFL2v_R"]) / 2.0 - PFL2_ENDS[1]) / max(PFL2_ENDS[0] - PFL2_ENDS[1], 1.0), 0.0, 1.0))) if (args.pfl2_walk and GOAL is not None) else None), on_chunk=_hook_all, state=(FeedingState(hold=args.feeding, t_full=args.satiety, tau_sat=args.satiety_tau, read=args.feed_read, mn9_thr=args.mn9_thr) if args.feeding > 0 else None))
if _CELLS and args.log_frames: ep.frame_cells = _lc
ep.run(args.seconds)
if _CELLS: np.savez_compressed(args.out.replace(".npz", "") + ".cells.npz", cells=_CELLS["cells"], bodyId=M.bodyId[_CELLS["cells"]], type=mty[_CELLS["cells"]], side=mns.astype(str)[_CELLS["cells"]], counts=np.array(_CELLS["counts"], np.int32), pose_chunk=np.array(ep.POSE, np.float32)[::CH][:len(_CELLS["counts"])], frames=(np.array(ep.FRAMES, np.int16) if ep.FRAMES else np.zeros((0, len(_lc)), np.int16)), pose_frame=np.array(ep.POSE, np.float32)[:len(ep.FRAMES)]); print("wrote", args.out.replace(".npz", "") + ".cells.npz")
if _PRE: np.savez_compressed(args.out.replace(".npz", "") + ".pre.npz", cells=_PRE["cells"], type=mty[_PRE["cells"]], side=mns.astype(str)[_PRE["cells"]], w_to_L=_wL[_PRE["cells"]], w_to_R=_wR[_PRE["cells"]], counts=np.array(_PRE["counts"], np.int32)); print("wrote", args.out.replace(".npz", "") + ".pre.npz")
if args.world == "garden":
    ep.save(args.out, posts=np.array([[gx, gy, gr, ga] for gx, gy, gr, ga, gh in room.grass], np.float32), walls=dict(half=room.half, height=room.height, albedo=room.albedo), her_albedo=HER_ALB, body_r=BODY, her_r=HER_R,
            extra=dict(world="garden", floor_rgb=room.rgb, floor_half=room.half, grass=np.array(room.grass, np.float32), leaves=np.array(room.leaves, np.float32), stone=np.array(room.stone, np.float32), fruit=np.array(room.fruit, np.float32), puddle=np.array(room.puddle, np.float32), sunspot=np.array(room.sunspot, np.float32), wind=np.array(room.wind, np.float32), sun_dir=np.array(room.sun_dir, np.float32), **({"compass_wedges": np.array(_COMPASS["rows"], np.float32), "compass_pfl": np.array(_COMPASS["pfl"], np.float32), "compass_goal": np.array(_COMPASS["goal"], np.float32), "compass_switches": np.int32(_COMPASS["switches"]), "compass_surges": np.int32(_COMPASS.get("surges", 0)), "compass_sun_az": np.float32(RING["sun_az"])} if _COMPASS else {})))
elif args.world == "arena": ep.save(args.out, posts=np.zeros((0, 4), np.float32), walls=dict(half=room.radius, height=room.height, albedo=room.albedo), her_albedo=HER_ALB, body_r=BODY, her_r=HER_R, extra=dict(world="arena", arena_radius=room.radius))
else: ep.save(args.out, posts=posts, walls=WALLS, her_albedo=HER_ALB, body_r=BODY, her_r=HER_R)
