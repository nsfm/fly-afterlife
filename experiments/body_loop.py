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
from fastlif import FastFlyBrain, SYN_TAU_HELP, SYN_REV_HELP, SYN_REV_HOLD_HELP, PIC_HELP
from fly_afterlife.receptors import Registry, ReceptorClass, Scaled, Transducer, tonic_floor
from fly_afterlife.size import add_size_args, apply_size
import mujoco as mj
from flygym.utils.math import Rotation3D
from flygym.compose import NeuroMechFly, FlatGroundWorld, ActuatorType, KinematicPosePreset
from flygym.anatomy import JointPreset, ActuatedDOFPreset, Skeleton, AxisOrder
from flygym import Simulation

ap = argparse.ArgumentParser()
ap.add_argument("--log-x", default="", help="extra cell types logged at 1 ms into the cells file as x_ms / x_type / x_bodyId (09-23, the movement-senses read); off by default, no effect on the run")
ap.add_argument("--freeze-mn", type=float, default=0.0, help="hold every muscle activation (torque and grip) at its value at this many seconds, and stop feeding spikes into it (09-23, the control for the per-leg five-hertz bouts: the cord out of the loop); 0 = off")
ap.add_argument("--silence", default="", help="comma-separated types whose threshold is put out of reach (no effect on driven cells); as in world/cord.py")
ap.add_argument("--mn-poisson", default="", help="the review's control (09-23): feed the muscle map Poisson spike trains at each leg motor neuron's own mean rate taken from this run's .cells.npz (after its warm-up), instead of the cord's spikes; the cord still runs and is logged, the body never sees it. if the lifts survive, the body sets the rhythm")
ap.add_argument("--puppet", default="", help="THE PUPPET BASELINE (nate 09-23, TODO 4o; a labelled puppet, NEVER a result): tripod:F_HZ:DUTY. the muscle map ignores the cord (which still runs and is logged, as --mn-poisson) and is fed scripted Poisson spike trains on each leg's own mapped motor neurons: tripod groups lf rm lh / rf lm rh in antiphase at F_HZ, DUTY the stance fraction (phase 0..DUTY stance, then swing), from the warm-up's end (nothing before it); in swing the levators (levate +) and promotors (protract +) at --puppet-swing-hz, in stance the depressors (levate -), remotors (protract -) and tibia extensors (flex -) at --puppet-stance-hz, every spike through the same f_w, K, --mn-force and actuator clip as a cord spike. every printed line and the saved args carry PUPPET; '' = off. tripod2:F_HZ:DUTY:OFFSET (09-23, refined once against the KINEMATIC REPLAY, experiments/kin_replay.py): the same tripod groups (B at +0.5) with a per-segment phase offset inside the group, OFFSET = F/M/H in cycles (leg phase = t x F_HZ + group + offset), and the stance duty per leg, DUTY = one value, F/M/H, or lf/lm/lh/rf/rm/rh; within each leg's swing the tibia flexors (flex +) and the levators fire in the first 40 %% of swing, the protractors in the middle 60 %% (20-80 %%), and in stance the depressors, remotors and tibia extensors, as tripod")
ap.add_argument("--puppet-swing-hz", type=float, default=100.0, help="--puppet: the scripted rate per swing-set motor neuron during its leg's swing (a chosen number)")
ap.add_argument("--puppet-stance-hz", type=float, default=50.0, help="--puppet: the scripted rate per stance-set motor neuron during its leg's stance (a chosen number)")
ap.add_argument("--out", required=True); ap.add_argument("--seconds", type=float, default=20.0); ap.add_argument("--seed", type=int, default=11)
ap.add_argument("--wsyn-m", type=float, default=0.185); ap.add_argument("--noise", type=float, default=0.15)
ap.add_argument("--walk", type=float, default=100.0); ap.add_argument("--walk-dn", default="DNg100"); ap.add_argument("--std", default="off"); ap.add_argument("--mirror", default="off")
ap.add_argument("--leg-load-hz", type=float, default=15.0); ap.add_argument("--loop", default="position+load", help="off | position | load | position+load")
ap.add_argument("--claw-hz", type=float, default=100.0); ap.add_argument("--hook-hz", type=float, default=100.0); ap.add_argument("--hook-vel", type=float, default=300.0)
ap.add_argument("--slow-hz", type=float, default=0.0, help="the standing-tonus stand-in: the 93 smallest leg MNs held at this rate x their leg's load (0 = off)")
ap.add_argument("--slow-mv", type=float, default=0.0, help="the standing-tonus stand-in as an ADDED CURRENT (the review's F0 fix, 09-22): the stance muscles' motor neurons get a tonic current of this many mV x their leg's load on the engine's ext path, on top of every synapse the cord sends them (13.6 mV ~ 60 Hz alone). --slow-hz is the withdrawn form (it marked the cells driven and REPLACED the cord); kept for the record, do not use")
ap.add_argument("--claw-labels", default="50ext", help="which claw type is extension-tuned: 50ext (SNpp50, the E_table label) | 50flex (SNpp51 extension-tuned, the review's reading of the wiring: Lee 2025's rule); unsourced either way, so both are run")
ap.add_argument("--senses", default="v1", choices=["v1", "v2"], help="the body's senses: v1 (the runs of record: the whole 580-cell floor at --leg-load-hz, the load row on every leg proprioceptor that is not claw or hook, the claw from the knee's angle away from the model's neutral pose) | v2 (campaign item 6, 09-22; world/leg_senses.npz): the floor and each leg's load row on campaniform + untyped only; club / hook / unclassified chordotonal held at 0 under the floor (the hooks still by velocity); the claw from |femur-tibia angle - 90 deg| / 60 deg (Mamiya 2018: tonic in angle, silent near 90), the flexion side on the flexion-tuned class as --claw-labels names it; the hair plates from the thorax-coxa pitch angle (--hp-hz); the leg's tactile cells on foot contact (--tactile-frac, --tactile-hz). hair plates and claw / hook ride on --loop position, load and tactile on --loop load")
ap.add_argument("--hp-hz", type=float, default=30.0, help="--senses v2: the hair plates' rate at the coxa's joint limit, rising linearly from 0 at the coxa's neutral (thorax-coxa pitch; the limit is limit_joints' +-45 deg). UNSOURCED: a chosen number (life: 0 inside the working range, 20-60 Hz near the limits, Pratt 2026; the linear ramp over the whole half-range is ours)")
ap.add_argument("--tactile-frac", type=float, default=0.25, help="--senses v2: the fraction of each leg's tactile cells driven while its foot is on the ground (a fixed random subset, seeded by --seed; the map cannot tell tarsal bristles from the rest). UNSOURCED: a chosen number")
ap.add_argument("--tactile-hz", type=float, default=20.0, help="--senses v2: the tactile rate while the foot's contact force is over the pads' threshold (0.05 uN, as pad_on), 5x for the first 30 ms after touchdown (the onset burst), 0 off the ground. UNSOURCED: chosen rates (Corfas & Dudai 1990 give an onset burst and a plateau for bristles, no adult leg bristle has a recorded rate under walking contact)")
ap.add_argument("--slow-set", default="size", help="which cells the standing-tonus stand-in holds: stance_all (every motor neuron of the stance muscles regardless of size: the load-scaled tonus of docs/ASK.md (a), a stand-in for the slow-unit reflex on cells the size rule calls fast, labelled) | size (the 93 smallest leg MNs: measured to be the accessory flexors, a flexion tonus) | extensor (the stance muscles' motor neurons below the median input size, per leg: sternotrochanter, trochanter extensor, tibia extensor, pleural remotor, sternal posterior rotator; the standing tonus as life has it, on the slow members of the anti-gravity muscles (E))")
ap.add_argument("--load-deriv", type=float, default=0.0, help="a rate-sensitive term on the load signal (the campaniform brief, Szczecinski 2021: campaniforms report dF/dt as well as F): the load rows and the stance tonus get clip(F/F_stand + G x dF/dt x 50 ms / F_stand, 0, 2), so unloading a leg cuts its stance drive before the load is gone and loading it adds; 0 = off (E)")
ap.add_argument("--cocon", type=float, default=0.0, help="co-contraction: the swing muscles' motor neurons (trochanter flexors, tibia flexors, promotors, anterior rotators) held at this fraction of the stance tonus rate x load, so each joint is stiff mid-range instead of driven to its limit (standing in life is co-contraction; nate 09-22: the front legs are struts); 0 = extensors only")
ap.add_argument("--adhesion", default="ltm", help="how the feet grip: ltm (the long tendon muscles' motor neurons, the honest hookup; unwired in this file, so never on) | contact (a labelled stand-in for the pulvilli's passive adhesion: a loaded foot sticks, an unloaded one releases; Ramdya lab convention: adhesion during stance) | off")
ap.add_argument("--adhesion-gain", type=float, default=1.0, help="adhesion force per foot in the model's uN (flygym's default actuator gain 1; a fly's pads hold several body weights)")
ap.add_argument("--dn-playback", default="", help="drive the cord's descending neurons with the brain's own descending output as a recording: a whole-fly run's <run>.cells.npz with every DN type logged per chunk (100 ms); each DN cell in the cord is held at its own measured rate in that chunk, chunk by chunk (the headless preparation with the real channels; nate 09-22: not a head, a recording of one). replaces --walk / --walk-dn")
ap.add_argument("--playback-start", type=float, default=2.0, help="seconds into the recording to start (after its warm-up)")
ap.add_argument("--edge-scale", default="", help="as in world/cord.py: TYPES:FACTOR, the synapses among the named types scaled (the published rhythm loop DNg100,IN17A001,INXXX466,IN16B036:3 rings at 25 Hz under the 400 Hz dose)")
ap.add_argument("--drive", default="", help="as in world/cord.py: TYPE:HZ,TYPE:HZ, named types held at a rate; rows after the floor and the body's senses, so they override on those cells; the driven cells' membranes are gated (driven); printed. a labelled diagnostic (09-23, campaign item 7: the commissurals AN19B009 / IN19B005 driven beyond the command)")
ap.add_argument("--cell-delay", default="", help="as in world/cord.py: TYPES:MS, a per-cell conduction delay on the named cells (the ring slows from 25 Hz to 10 with 12 ms on the loop's three cells)")
ap.add_argument("--syn-tau", default="", help="as in world/cord.py: " + SYN_TAU_HELP)
ap.add_argument("--syn-rev", default="", help="as in world/cord.py: " + SYN_REV_HELP)
ap.add_argument("--syn-rev-hold", default="ach", help="as in world/cord.py: " + SYN_REV_HOLD_HELP)
ap.add_argument("--pic", default="", help="as in world/cord.py: " + PIC_HELP)
ap.add_argument("--log-v", default="", help="as in world/cord.py: comma-separated types whose mean membrane (mV re rest) is logged per ms as v_ms / v_types in <out>.cells.npz; off by default")
ap.add_argument("--graded", default="", help="graded (non-spiking) units as in world/cord.py: PREFIXES:GAIN[:V1] or random:N:GAIN")
add_size_args(ap)   # --size-gain --size-thr --size-noise --size-clip --size-from, as in world/cord.py (src/fly_afterlife/size.py, one block for both)
ap.add_argument("--slow-init", type=float, default=0.0, help="set him down standing: for this many seconds after the warm-up the load term is clamped to at least standing (F_stand) on every leg, so the load reflex and the stand-in start engaged; then the body's own load. an initial condition, labelled (0 = off)")
STIFF_SOURCED = 2e-8 / 1e-9   # 2e-8 N.m/rad in the model's torque unit (g.mm^2/s^2 = 1e-3 kg x 1e-6 m^2 / s^2 = 1e-9 N.m = nN.m): 20 nN.m/rad
def _stiffness(x): return STIFF_SOURCED if x == "sourced" else float(x)
ap.add_argument("--gain", type=float, default=42.0); ap.add_argument("--sat", type=float, default=10.0); ap.add_argument("--alpha", type=float, default=1.2)
ap.add_argument("--stiffness", type=_stiffness, default=None, help="the joints' passive spring in nN.m/rad (the model's unit: g.mm^2/s^2 = nN.m). default None = flygym's 10, the number every clip of record ran on (it does not hold NeuroMechFly's neutral pose: he sinks onto his hind coxae, docs/REVIEW_PHYSICS.md P2). 'sourced' = 20: leg_biomech.md B5 (Wang et al. 2025 bioRxiv 2025.04.29.651225, the T1 femur-tibia, the smaller reading of their ambiguous unit, uncertain to ~50x) gives 2 x 10^-8 N.m/rad; 1 nN.m = 10^-9 N.m, so 2e-8 N.m/rad = 2e-8 / 1e-9 = 20 nN.m/rad = 20 model units. on this body 20 stands him on his feet with no muscle (the review's sweep), against the paper's headline that passive force cannot (P3); so 'sourced' is the printed number, not a check of it. 0.14 = 10 / 70 is derived (E), not measured")
ap.add_argument("--load-from", default="leg", choices=["leg", "tarsi"], help="the per-leg force the load rows, the tactile rows and the pads read (09-23, docs/REVIEW_PHYSICS.md P1): leg (the runs of record: flygym's per-leg contact sensor, the whole leg's subtree from the coxa down, a vector norm with friction, so a coxa on the floor reads as a loaded foot) | tarsi (the vertical ground reaction on tarsus1-5 only, summed per leg; tarsus5 carries the claw and pad, the model has no pretarsus segment). either way net of the pad's pull; leg_force in the .npz stays the leg sensor's")
ap.add_argument("--hind-map", default="v1", choices=["v1", "v2"], help="the hind legs' motor-neuron-to-DOF table (09-23, the review's P4 / P5): v1 (the runs of record: the front leg's type map on the measured roles; the hind 'protract' role is coxa yaw, the hind coxa pitch gets no cord torque; MNhl01/02/29/59/60/62/64/87/88 unmapped) | v2: the hind 'protract' role (every promotor / remotor / rotator class) moves to the hind coxa PITCH, sign by its measured fore-aft action (results/body_dof_signs.json: + pitch moves the foot 0.367 mm back and 0.505 mm up per unit, so protraction = - pitch, which also presses the foot down), and the unnamed hind cells get leg_biomech.md A2's recommended action: MNhl62 promotor (high), MNhl29 remotor (high), MNhl01 / MNhl02 trochanter depressors (medium-high), MNhl60 / MNhl64 tarsus depressors (low, (E)); MNhl59 (low: anterior rotator by cos 0.36 only), MNhl87 / 88 (none), Tergotr. and Fe reductor stay unmapped, as A2 says. the adductor stays on coxa yaw. printed at startup")
ap.add_argument("--start-pose", default="neutral", choices=["neutral", "feet"], help="where the run starts (09-23, the review's P2): neutral (the runs of record: spawned in NeuroMechFly's neutral pose, which is not a six-foot stance: the hind feet lowest, the middle 0.155 mm and the front ~0.30 mm up; he falls and settles during the warm-up with the cord already driving) | feet: before the warm-up, 0.5 s of physics under gravity on the arm's own springs with no muscle and no pad, then the run starts from that settled pose. (lowering the spawn cannot put six feet down: the neutral feet are not level)")
ap.add_argument("--mn-force", default="uniform", choices=["uniform", "azevedo"], help="force per spike by motor neuron class (09-23; docs/physiology/force_per_spike.md): uniform (the runs of record: every mapped MN's spike scaled by the size proxy f_w = (S / S_max of its leg-role group)^--alpha) | azevedo (Azevedo et al. 2020 eLife 9:e56754, fig 4, the female front-leg tibia flexor: ~10 / ~1 / 0.013 uN per spike for fast / intermediate / slow, so 1 : 0.1 : 0.0013 with fast at today's --gain; the class from the input-synapse third of the 'Ti flexor MN' pool, the same thirds as --pic smallflex and the graded size CSV, small = slow; the measured factor REPLACES f_w on those cells; every other mapped MN keeps f_w x 1.0, a stated default, counted at startup). the slow class's own slow kinetics (no twitch, force still rising at 500 ms) are not modelled here: same kernel, measured gain (--twitch azevedo gives them their own)")
ap.add_argument("--twitch", default="uniform", choices=["uniform", "azevedo"], help="the muscle's time course per spike by motor neuron class (09-23; docs/physiology/force_per_spike.md): uniform (the runs of record: every motor neuron's spike adds the one twitch kernel, K = e^-t/20 - e^-t/7, peak 1, 120 ms) | azevedo: the slow class gets the slow unit's time course (Azevedo 2020 fig 4C: no resolvable twitch, force still rising at 500 ms), a first-order low-pass of its spike train with tau --slow-tau; the intermediate and fast classes keep the sourced twitch (fast and intermediate share it, fig 4A/B). NORMALISATION: a slow spike's force-time integral = the cell's per-spike factor (under --mn-force azevedo the class's 0.0013; under uniform its f_w) x the twitch's integral (sum K = 35.05 ms of peak), so the mean force at a given rate is today's and only its time course changes: a slow cell at 30 Hz gives a smooth, small, sustained pull instead of a train of 20 ms twitches. which cells are slow: the --mn-force azevedo rule (the small input-synapse third of the 'Ti flexor MN' pool, pooled over the cord); every pool without a class keeps the twitch, counted at startup. built as one low-pass state per DOF, updated per ms (exact by linearity: every slow cell shares tau), no per-spike cost")
ap.add_argument("--slow-tau", type=float, default=300.0, help="--twitch azevedo: the slow unit's low-pass time constant in ms (E; bracketed 200-500 from fig 4C: force not peaked at 500 ms, release ~100 ms; force_per_spike.md section 1)")
ap.add_argument("--tethered", action="store_true", help="the tethered preparation (nate, 09-22: propped up): the thorax fixed in space, the legs free, no floor and no load; the position loop still closes"); ap.add_argument("--gravity", type=float, default=1.0, help="scale on gravity (0.1 = a tenth of his weight; a graded prop-up, diagnostic)")
ap.add_argument("--walk-ramp", type=float, default=0.0, help="the command rises linearly over this many seconds after the warm-up instead of stepping on in one ms (nate 09-22: the fling at the 2 s mark; a walking bout's descending drive ramps in life, Aymanns 2022, Sapkal 2024 ramped their light)");
ap.add_argument("--warmup", type=float, default=2.0); ap.add_argument("--no-video", action="store_true"); ap.add_argument("--fps", type=int, default=25); ap.add_argument("--playback-speed", type=float, default=1.0, help="native slow motion (09-23, nate): the renderer samples a frame every (1 / fps) x playback_speed of simulated time, so 0.25 at 30 fps is a frame every 8.3 ms and the clip plays at a quarter speed; 1.0 = real time (the default)")
args = ap.parse_args(); t0 = time.time(); use_pos = "position" in args.loop; use_load = "load" in args.loop
if args.puppet:   # (TODO 4o) the puppet must be impossible to mistake for a result: every printed line carries PUPPET, and the saved args say so
    import builtins; _bprint = builtins.print
    def _pprint(*a, **k):
        s = (k.get("sep") if k.get("sep") is not None else " ").join(str(x) for x in a)
        _bprint("\n".join("PUPPET | " + ln for ln in s.split("\n")), **{kk: vv for kk, vv in k.items() if kk != "sep"})
    builtins.print = _pprint
    _pk = args.puppet.split(":")[0]; assert _pk in ("tripod", "tripod2"), "--puppet: tripod:F_HZ:DUTY or tripod2:F_HZ:DUTY:OFFSET"
    if _pk == "tripod":
        _pk, _pf, _pd = args.puppet.split(":"); PUP_F = float(_pf); PUP_DUTY = float(_pd)
        args.PUPPET = f"PUPPET: a scripted tripod at {PUP_F:g} Hz, duty {PUP_DUTY:g}, swing {args.puppet_swing_hz:g} Hz / stance {args.puppet_stance_hz:g} Hz per MN; the cord does NOT drive the body; not a result"
    else:   # (09-23) tripod2: per-leg duty, per-segment offset, the swing split flexors + levators (first 40 %) / protractors (middle 60 %)
        _pk, _pf, _pd, _po = args.puppet.split(":"); PUP_F = float(_pf); _dv = [float(x) for x in _pd.split("/")]; _ov = [float(x) for x in _po.split("/")]
        assert len(_dv) in (1, 3, 6) and len(_ov) == 3, "tripod2:F_HZ:DUTY:OFFSET, DUTY one value, F/M/H or six legs, OFFSET F/M/H"
        PUP_DUTY6 = np.array(_dv * 6 if len(_dv) == 1 else _dv * 2 if len(_dv) == 3 else _dv); PUP_OFF3 = dict(zip("fmh", _ov)); PUP_DUTY = float(PUP_DUTY6.mean())
        args.PUPPET = (f"PUPPET: a scripted tripod2 at {PUP_F:g} Hz, stance duty lf lm lh rf rm rh {'/'.join(f'{x:g}' for x in PUP_DUTY6)}, segment offsets F/M/H {_po} cycles, swing = flexors + levators 0-40 % then protractors 20-80 %, "
                       f"swing {args.puppet_swing_hz:g} Hz / stance {args.puppet_stance_hz:g} Hz per MN; the cord does NOT drive the body; not a result")
    print(args.PUPPET)

# ---- the cord
M = FastFlyBrain("brain_cord.npz", seed=args.seed, params=Params(mv_per_synapse=args.wsyn_m, noise=args.noise)); M.integrate = "exact"
mty = M.type.astype(str); mns = M.side.astype(str); mbid = M.bodyId; pos = {int(b): i for i, b in enumerate(mbid)}
if args.mirror != "off":
    from fly_afterlife.wiring import mirror_normalise; print("mirror:", mirror_normalise(M, scope=args.mirror))
if args.std != "off":
    _mask = np.ones(M.N, bool) if args.std == "all" else (mty == "DNg33") if args.std == "pair" else np.isin(mty, args.std.split(",")); M._std_mask = _mask; M._std_x = np.ones(M.N, np.float32); M.std_on = True
if args.syn_tau: print(M.set_syn_tau(args.syn_tau))   # (09-22, campaign item 2)
if args.syn_rev: print(M.set_syn_rev(args.syn_rev, args.syn_rev_hold))   # (09-22, campaign item 2b; after --syn-tau)
if args.pic: print(M.set_pic(args.pic))   # (09-23, campaign item 4) the persistent inward current on named cells; the set is read from the brain file
if args.cell_delay:
    _dt_, _dms = args.cell_delay.rsplit(":", 1); _dsteps = max(1, int(round(float(_dms) / M.p.dt))); _base = max(1, int(round(M.p.syn_delay_ms / M.p.dt)))
    M._cell_delay = np.full(M.N, _base, np.int64); M._cell_delay[np.isin(mty, _dt_.split(","))] = _dsteps; M._dly_max = int(M._cell_delay.max()); M.delay_on = True; print(f"cell delay: {_dt_} at {_dms} ms")
if args.edge_scale:
    _et, _ef = args.edge_scale.rsplit(":", 1); _em = np.isin(mty, _et.split(",")); _src = np.repeat(np.arange(M.N), np.diff(M._out_ptr)); _sel = _em[_src] & _em[M._out_tgt]
    M._out_w[_sel] *= np.float32(float(_ef)); print(f"edge scale: {int(_sel.sum())} synapses among {_et} x {_ef}")
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
    def __init__(self, key, source="body_loop: a rate from the body (E)"): self.key = key; self.source = source
    def step(self, stim, t, dt): return float(stim)
sens = {}
if args.senses == "v1":   # the runs of record, unchanged
  for leg in LEG6:
    cells = np.array([pos[int(wbid[i])] for i in legs[SENS[leg]] if int(wbid[i]) in pos], np.int64)
    of = lambda types: cells[np.isin(mty[cells], types)]
    sens[leg] = dict(claw_e=of(["SNpp50"]), claw_f=of(["SNpp51"]), hook_f=of(["SNpp39"]), hook_e=of(["SNpp41"]), load=cells[~np.isin(mty[cells], ["SNpp50", "SNpp51", "SNpp39", "SNpp41"])])
    if use_pos:
        for k in ("claw_e", "claw_f", "hook_f", "hook_e"):
            if len(sens[leg][k]): REG.add(ReceptorClass(f"{k}_{leg}", sens[leg][k], Rate(k), (lambda kk: (lambda st: st[kk]))(f"{k}_{leg}")))
    if use_load and len(sens[leg]["load"]): REG.add(ReceptorClass(f"load_{leg}", sens[leg]["load"], Rate("load"), (lambda kk: (lambda st: st[kk]))(f"load_{leg}")))
  print("sensory cells per leg:", {l: {k: len(v) for k, v in sens[l].items()} for l in LEG6})
else:   # --senses v2 (campaign item 6, 09-22): every row from world/leg_senses.npz by bodyId, every chosen rate labelled
    from fly_afterlife.receptors import Hold
    from fly_afterlife.leg_senses import leg_cells, union, counts
    LS = leg_cells(mbid); U = "(campaign item 6, 09-22; rate unsourced)"
    _cs = union(LS, ("campaniform", "untyped")); _quiet = union(LS, ("club", "hook_39", "hook_41", "co_unclassified"))
    for rc in _fl:
        if rc.name == "floor_leg_proprio":
            _old = rc.cells; rc.cells = _cs; rc.transducer.source = rc.source = f"the standing floor on the leg's campaniform + untyped cells only (leg_senses.npz; {len(np.intersect1d(_cs, _old))} of them in the old 580) at --leg-load-hz {U}"
    REG.classes.insert(len(_fl), ReceptorClass("floor_leg_quiet", _quiet, Hold(0.0, source="club / hook / unclassified chordotonal held at 0 under the floor: silent in a motionless leg (the hooks' velocity rows below override) (campaign item 6, 09-22)"), lambda st: True))
    for leg in LEG6:
        sens[leg] = dict(claw_e=LS[leg]["claw_50"], claw_f=LS[leg]["claw_51"], hook_f=LS[leg]["hook_39"], hook_e=LS[leg]["hook_41"], hp=LS[leg]["hair_plate"],
                         load=np.union1d(LS[leg]["campaniform"], LS[leg]["untyped"]).astype(np.int64))
        _t = LS[leg]["tactile"]; _n = int(round(args.tactile_frac * len(_t)))
        sens[leg]["tact"] = np.sort(np.random.default_rng([args.seed, 6, LEG6.index(leg)]).choice(_t, _n, replace=False)).astype(np.int64) if _n else np.zeros(0, np.int64)
        SRC = dict(claw_e=f"SNpp50: --claw-hz x |femur-tibia - 90 deg| / 60 deg on the side --claw-labels gives it (null at 90: Mamiya 2018) {U}", claw_f=f"SNpp51: as SNpp50, the other side of 90 deg {U}",
                   hook_f=f"SNpp39: flexion velocity, --hook-hz at --hook-vel {U}", hook_e=f"SNpp41: extension velocity, --hook-hz at --hook-vel {U}",
                   hp=f"hair plates 45 + 52 + xx: --hp-hz x |coxa pitch - neutral| / (limit - neutral) {U}", load=f"campaniform + untyped: --leg-load-hz x load (F / F_stand) {U}",
                   tact=f"tactile, a seeded {args.tactile_frac} of the leg's cells: --tactile-hz on contact, x5 for the first 30 ms {U}")
        for k in (("claw_e", "claw_f", "hook_f", "hook_e", "hp") if use_pos else ()) + (("load", "tact") if use_load else ()):
            if len(sens[leg][k]): REG.add(ReceptorClass(f"{k}_{leg}", sens[leg][k], Rate(k, SRC[k]), (lambda kk: (lambda st: st[kk]))(f"{k}_{leg}")))
    print("--senses v2: the leg map (world/leg_senses.npz) per leg:\n" + counts(LS, ("tactile", "claw_50", "claw_51", "hook_39", "hook_41", "club", "co_unclassified", "hair_plate", "campaniform", "untyped")))
    print("--senses v2: the rows per leg:\n" + "\n".join(f"  {k:6s} " + " ".join(f"{l} {len(sens[l][k]):4d}" for l in LEG6) for k in sens["lf"]) + f"\n  floor_leg_proprio {len(_cs)} cells (was {len(_old)}), floor_leg_quiet {len(_quiet)} cells at 0")
    print(REG.table())
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
    if args.cocon > 0 and args.slow_mv == 0:
        SWING = ("Tr flexor MN", "Acc. tr flexor MN", "Ti flexor MN", "Acc. ti flexor MN", "Tergopleural/Pleural promotor MN", "Sternal anterior rotator MN")
        for leg in LEG6:
            cells = np.array([j for j in LEGMN if mty[j] in SWING and legof[j] == leg], np.int64)
            if len(cells): REG.add(ReceptorClass(f"cocon_{leg}", cells, Rate("cocon"), (lambda kk: (lambda st: st[kk]))(f"cocon_{leg}"), source="co-contraction stand-in (09-22): the swing muscles at a fraction of the stance tonus; labelled"))
        print(f"co-contraction: the swing muscles at {args.cocon} x the stance tonus")
SLOW_BY_LEG = {leg: np.array([j for j in SLOW if legof[j] == leg], np.int64) for leg in LEG6}
SWING = ("Tr flexor MN", "Acc. tr flexor MN", "Ti flexor MN", "Acc. ti flexor MN", "Tergopleural/Pleural promotor MN", "Sternal anterior rotator MN")
SWING_BY_LEG = {leg: np.array([j for j in LEGMN if mty[j] in SWING and legof[j] == leg], np.int64) for leg in LEG6}
if args.slow_mv > 0: print(f"standing tonus as a current: {sum(len(v) for v in SLOW_BY_LEG.values())} stance MNs at {args.slow_mv} mV x load" + (f"; co-contraction: the swing MNs at {args.cocon} x that" if args.cocon > 0 else ""))
if args.drive:   # (09-23, campaign item 7) as in world/cord.py: after every other row, so it overrides; gated below with every REG row
    from fly_afterlife.receptors import Hold
    for item in args.drive.split(","):
        t_, hz_ = item.split(":"); cells_ = np.flatnonzero(mty == t_)
        REG.add(ReceptorClass(f"drive_{t_}", cells_, Hold(float(hz_)), lambda st: True, source="body_loop.py --drive: a named type held at a rate (diagnostic)")); print(f"drive: {t_} ({len(cells_)} cells) at {hz_} Hz")
apply_size(M, args)   # (campaign item 3, 09-23) as in world/cord.py; here after insyn is read above, so the motor force weights (f_w) and the slow set stay the file's synapse counts and the size terms change excitability only
M.driven[:] = False
for cl in M.SENSORY_CLASSES: M.driven[M.cls == cl] = True
for rc in REG.classes: M.driven[rc.cells] = True
if args.silence:
    _sil = np.flatnonzero(np.isin(mty, [x for x in args.silence.split(',') if x])); M.v_th[_sil] = np.float32(1e6); print(f"silenced {len(_sil)} cells of {args.silence} (driven cells unaffected)")
M._driven_idx = np.flatnonzero(M.driven); M.reset()

# ---- the body
ROLE = {"Tergopleural/Pleural promotor MN": ("protract", +1), "Sternal anterior rotator MN": ("protract", +1), "Pleural remotor/abductor MN": ("protract", -1), "Sternal posterior rotator MN": ("protract", -1),
        "Tr flexor MN": ("levate", +1), "Acc. tr flexor MN": ("levate", +1), "Sternotrochanter MN": ("levate", -1), "Tr extensor MN": ("levate", -1),
        "Ti flexor MN": ("flex", +1), "Acc. ti flexor MN": ("flex", +1), "Ti extensor MN": ("flex", -1),
        "Ta levator MN": ("tarsus_levate", +1), "MNml81": ("tarsus_levate", +1), "MNhl65": ("tarsus_levate", +1), "Ta depressor MN": ("tarsus_levate", -1),
        "Sternal adductor MN": ("adduct", +1), "ltm MN": ("grip", +1), "ltm1-tibia MN": ("grip", +1), "ltm2-femur MN": ("grip", +1)}
roles = json.load(open("results/body_dof_signs.json"))["roles"]
HIND = ("lh", "rh"); ROLE_H = ROLE
if args.hind_map == "v2":   # (09-23, the review's P4) the hind protract role on the coxa pitch by its measured fore-aft action; A2's unnamed hind cells added
    _meas = json.load(open("results/body_dof_signs.json"))["measured"]
    for _l in HIND:
        _d = f"c_thorax->{_l}_coxa:pitch"; _mm = _meas[_d]; roles[_l]["protract"] = dict(dof=_d, k=_mm["k"], sign=float(np.sign(_mm["delta"]["fwd"])), size=abs(_mm["delta"]["fwd"]), up=_mm["delta"]["up"])
    ROLE_H = dict(ROLE, **{"MNhl62": ("protract", +1), "MNhl29": ("protract", -1), "MNhl01": ("levate", -1), "MNhl02": ("levate", -1), "MNhl60": ("tarsus_levate", -1), "MNhl64": ("tarsus_levate", -1)})
    HIND_SRC = {"MNhl62": "A2 promotor, high", "MNhl29": "A2 remotor, high", "MNhl01": "A2 Tr depressor, med-high", "MNhl02": "A2 Tr depressor, med-high", "MNhl60": "A2 Ta depressor, low (E)", "MNhl64": "A2 Ta depressor, low (E)",
                "MNhl59": "unmapped: A2 low (ant. rotator by cos 0.36)", "MNhl87": "unmapped: A2 none", "MNhl88": "unmapped: A2 none", "Tergotr. MN": "unmapped (as v1)", "Fe reductor MN": "unmapped (as v1)"}
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
knee_neutral = {leg: float(np.degrees(neutral_of.get(roles[leg]["flex"]["dof"], 0.0))) for leg in LEG6}
if args.senses == "v2":   # (campaign item 6, 09-22) the claw's null and the hair plates' range
    # the knee: the model's femur-tibia pitch is 0 with the tibia in line with the femur and grows with flexion (knee_sign +1 on every leg), so the
    # femur-tibia angle as Mamiya 2018 measure it (180 = straight) is 180 - the model's angle (checked on the model's geometry: 0 -> 179.6 deg,
    # 90 -> 90.4). the absolute model angle is knee_neutral + knee x knee_sign (= degrees(ang[knee_idx]); knee_neutral 78 / 103 / 101 deg front /
    # middle / hind, i.e. femur-tibia 102 / 77 / 79), so flexion past the claw's null is k90 = (knee_neutral + knee x knee_sign - 90) x knee_sign
    # = knee + (knee_neutral - 90) x knee_sign: at the neutral pose the front legs sit 12 deg on the EXTENSION side of 90, the middle and hind 13 / 11
    # on the flexion side.
    knee90 = {leg: (knee_neutral[leg] - 90.0) * knee_sign[leg] for leg in LEG6}
    cx_idx = {leg: all_idx[f"c_thorax->{leg}_coxa:pitch"] for leg in LEG6}; cx_n = {leg: float(neutral_of.get(f"c_thorax->{leg}_coxa:pitch", 0.0)) for leg in LEG6}
    _jr = {f"{d_.parent.name}->{d_.child.name}:{d_.axis.value}": (float(j_.range[0]), float(j_.range[1])) for d_, j_ in jm.items()}; cx_rng = {leg: _jr[f"c_thorax->{leg}_coxa:pitch"] for leg in LEG6}
    print("--senses v2: femur-tibia at neutral " + ", ".join(f"{l} {180 - knee_neutral[l]:.0f}" for l in LEG6) + " deg (claw null 90); coxa pitch neutral / limits " + ", ".join(f"{l} {np.degrees(cx_n[l]):.0f} [{np.degrees(cx_rng[l][0]):.0f}, {np.degrees(cx_rng[l][1]):.0f}]" for l in LEG6) + " deg")
cell_dof = {}; cell_sgn = {}; grip_of = {}; groups = {}
for j in LEGMN:
    _R = ROLE_H if legof[j] in HIND else ROLE
    if mty[j] not in _R: continue
    role, ag = _R[mty[j]]
    if role == "grip": grip_of[j] = legof[j]; continue
    r = roles[legof[j]][role]; cell_dof[j] = r["k"]; cell_sgn[j] = r["sign"] * ag; groups.setdefault((legof[j], role, ag), []).append(j)
f_w = {}
for key, js in groups.items():
    smax = max(insyn[js]) or 1.0
    for j in js: f_w[j] = (insyn[j] / smax) ** args.alpha if insyn[j] > 0 else 0.1
if args.hind_map == "v2":
    _dofn = [dof_name(x) for x in dofs]
    print("--hind-map v2: the hind legs' motor neurons -> DOF (sign: the torque sign on the DOF = the measured role sign x agonist / antagonist; f_w before --mn-force)")
    print("  leg  type                            n  role           DOF                                   sign  f_w          source")
    for _l in HIND:
        for _t in sorted(set(mty[[j for j in LEGMN if legof[j] == _l]])):
            _js = [j for j in LEGMN if legof[j] == _l and mty[j] == _t]
            if _t in ROLE_H and ROLE_H[_t][0] != "grip":
                _ro, _ag = ROLE_H[_t]; _r = roles[_l][_ro]
                print(f"  {_l}   {_t:30s} {len(_js):2d}  {_ro:14s} {_dofn[_r['k']]:37s} {int(_r['sign'] * _ag):+d}   {min(f_w[j] for j in _js):.3f}-{max(f_w[j] for j in _js):.3f}  {HIND_SRC.get(_t, 'as v1' if _ro != 'protract' else 'v1 class, moved to pitch')}")
            elif _t in ROLE_H: print(f"  {_l}   {_t:30s} {len(_js):2d}  grip (the pads' ltm, as v1)")
            else: print(f"  {_l}   {_t:30s} {len(_js):2d}  -              no torque                                         {HIND_SRC.get(_t, 'unmapped')}")
MNF = {"slow": 0.013 / 10.0, "intermediate": 1.0 / 10.0, "fast": 1.0}   # (09-23) Azevedo 2020 fig 4: uN per spike over the fast spike's ~10 uN
def mn_classes():   # (09-23) the tibia flexor pool by input-synapse third (the file's counts, as --pic smallflex ranks it): {cell: slow | intermediate | fast}, mapped cells only; shared by --mn-force and --twitch
    tp = np.flatnonzero(mty == "Ti flexor MN"); tp = tp[np.argsort(insyn[tp], kind="stable")]; out = {}
    for cl, th in zip(("slow", "intermediate", "fast"), np.array_split(tp, 3)):
        for j in th:
            if int(j) in cell_dof: out[int(j)] = cl
    return tp, out
if args.mn_force == "azevedo":   # the measured factor in place of the size proxy
    _tp, MN_CLASS = mn_classes()
    _fw0 = {j: f_w[j] for j in MN_CLASS}
    for j, _cl in MN_CLASS.items(): f_w[j] = MNF[_cl]
    print(f"--mn-force azevedo (Azevedo 2020 eLife fig 4, female T1 tibia flexor: 10 / 1 / 0.013 uN per spike): 'Ti flexor MN' by input-synapse third of {len(_tp)} cells; torque per unit activation = --gain {args.gain} x factor (fast = today's reference)")
    print("  leg  class         n  factor   synapses     f_w it replaces")
    for leg in LEG6:
        for _cl in ("slow", "intermediate", "fast"):
            _js = [j for j, c_ in MN_CLASS.items() if c_ == _cl and legof[j] == leg]
            if _js: print(f"  {leg}   {_cl:12s} {len(_js):2d}  {MNF[_cl]:.4f}   {int(min(insyn[_js])):5d}-{int(max(insyn[_js])):5d}  {min(_fw0[j] for j in _js):.4f}-{max(_fw0[j] for j in _js):.4f}")
    _dflt = [j for j in cell_dof if j not in MN_CLASS]
    print(f"  no measurement: {len(_dflt)} mapped leg MNs keep f_w x 1.0 (the stated default; types {len(set(mty[_dflt]))}, e.g. Acc. ti flexor {sum(mty[j] == 'Acc. ti flexor MN' for j in _dflt)}, Ti extensor {sum(mty[j] == 'Ti extensor MN' for j in _dflt)}); {len(grip_of)} grip MNs unchanged")
KL = 120; tk = np.arange(KL); K = np.exp(-tk / 20.0) - np.exp(-tk / 7.0); K /= K.max()
TW = None
if args.twitch == "azevedo":   # (09-23) the slow class on a first-order low-pass: per spike a jump of A_j, decaying by D per ms, so its force-time integral is A_j / (1 - D) = f_w[j] x sum(K) / sat, the twitch's
    _tp2, _cls2 = mn_classes(); _D = float(np.exp(-1.0 / args.slow_tau)); _slow = sorted(j for j, c_ in _cls2.items() if c_ == "slow")
    TW = dict(D=_D, s=np.zeros(len(dofs)), A={j: f_w[j] * K.sum() / args.sat * (1.0 - _D) for j in _slow})
    _ss = f_w[_slow[0]] * K.sum() / args.sat * args.gain if _slow else 0.0
    print(f"--twitch azevedo: {len(_slow)} slow 'Ti flexor MN' cells (the small input-synapse third of {len(_tp2)}) on a low-pass, tau {args.slow_tau:.0f} ms (E), one state per DOF; integral per spike = factor x the twitch's {K.sum():.1f} ms "
          f"(factor {min((f_w[j] for j in _slow), default=0):.4f}-{max((f_w[j] for j in _slow), default=0):.4f}); per leg " + " ".join(f"{l} {sum(legof[j] == l for j in _slow)}" for l in LEG6))
    print(f"  keep the twitch: {sum(c_ != 'slow' for c_ in _cls2.values())} intermediate / fast 'Ti flexor MN' (sourced kernel); {len([j for j in cell_dof if j not in _cls2])} mapped MNs of pools without a class (the twitch, unmeasured); {len(grip_of)} grip MNs")
    _tr = np.zeros(3000); _tr[::33] = 1.0; _fk = np.convolve(_tr, K)[:3000]; _fl = np.zeros(3000); _x = 0.0
    for _i in range(3000): _x = _x * _D + _tr[_i] * K.sum() * (1.0 - _D); _fl[_i] = _x
    _rp = lambda f: (f[2000:].max() - f[2000:].min()) / f[2000:].mean() * 100
    print(f"  a slow cell at 30 Hz (regular train): mean torque {_ss * 30 / 1000:.4f} nN.m at the first slow cell's factor, the same under either kernel; peak-to-trough {_rp(_fl):.0f} % of the mean on the low-pass vs {_rp(_fk):.0f} % on the twitch")
weight = m.body_mass.sum() * abs(m.opt.gravity[2]); F_stand = max(weight / 6.0, 1e-6); print(f"gravity x{args.gravity}: weight {weight:.2f} uN, F_stand {F_stand:.2f}")
segs = [s.name for s in fly.get_bodysegs_order()]; thorax = segs.index("c_thorax")
TARS = [np.array([segs.index(f"{l}_tarsus{i}") for i in range(1, 6)]) for l in LEG6]   # (09-23, P1) the feet: tarsus1-5 (tarsus5 carries the claw and pad; no pretarsus segment in the model)
OTHL = [np.array([i for i, s_ in enumerate(segs) if s_.startswith(l + "_") and "_tarsus" not in s_]) for l in LEG6]   # coxa, trochanter-femur, tibia
if not args.no_video: sim.set_renderer([c for c in [mj.mj_id2name(m, mj.mjtObj.mjOBJ_CAMERA, i) for i in range(m.ncam)] if "trackcam" in c][0], camera_res=(480, 640), playback_speed=args.playback_speed, output_fps=args.fps)
sim.reset(); steps_per_ms = int(round(0.001 / m.opt.timestep))
if args.start_pose == "feet":   # (09-23, P2) settle on the springs with no muscle, then start from there
    sim.set_actuator_inputs("nmf", ActuatorType.MOTOR, np.zeros(len(dofs)))
    if adh: sim.set_leg_adhesion_states("nmf", np.zeros(6, bool))
    _z = []
    for _s in range(int(round(0.5 / m.opt.timestep))):
        sim.step()
        if _s % 10 == 0: _z.append(float(sim.get_body_positions("nmf")[thorax][2]))
    _cf0 = np.asarray(sim.get_bodysegment_contact_forces("nmf", segs))
    print(f"--start-pose feet: settled 0.5 s on the springs ({'flygym default 10' if args.stiffness is None else args.stiffness}) with no muscle: thorax z {_z[-1]:.3f} mm (moved {abs(_z[-1] - _z[-50]) * 1000:.1f} um in the last 50 ms); "
          f"tarsi per leg {np.round([_cf0[TARS[i], 2].sum() for i in range(6)], 2)} uN, other leg segments {np.round([_cf0[OTHL[i], 2].sum() for i in range(6)], 2)} uN (lf lm lh rf rm rh)")
def leg_forces():
    """ground contact force magnitude per leg (model force units = uN), legs ordered lf lm lh rf rm rh (fly.get_legs_order())."""
    if args.tethered: return np.zeros(6)
    found, forces, *_ = sim.get_ground_contact_info("nmf"); return np.linalg.norm(np.asarray(forces), axis=1)

# ---- the loop
n_ms = int(args.seconds * 1000); torque = np.zeros((len(dofs), n_ms + KL)); grip = {l: np.zeros(n_ms + KL) for l in LEG6}
P = np.zeros((n_ms, 3), np.float32); Q = np.zeros((n_ms, 4), np.float32); FL = np.zeros((n_ms, 6), np.float32); KA = np.zeros((n_ms, 6), np.float32)
JA = np.zeros((n_ms // 10 + 1, len(all_dofs)), np.float32)
FT = np.zeros((n_ms, 6)); FO = np.zeros((n_ms, 6)); FB = np.zeros(n_ms); FTN = np.zeros((n_ms, 6), np.float32)   # (09-23, P1) tarsal / other-leg vertical reaction per leg, body; FTN = tarsal net of the pads
spk = np.zeros((n_ms // 10 + 1, len(LEGMN)), np.int16); lpos = {int(j): i for i, j in enumerate(LEGMN)}
MNP = None
if args.mn_poisson:
    _R = np.load(args.mn_poisson.replace('.npz', '') + '.cells.npz', allow_pickle=True); _rb = {int(x): i for i, x in enumerate(_R['bodyId'].astype(np.int64))}; _rr = _R['frames'].astype(float)[200:].mean(0) * 100
    MNP = np.array([_rr[_rb[int(mbid[j])]] / 1000.0 if int(mbid[j]) in _rb else 0.0 for j in LEGMN]); _mnp_rng = np.random.default_rng([args.seed, 77]); print(f"mn-poisson: the muscle map fed by Poisson trains at the rates of {args.mn_poisson} (mean {MNP.mean()*1000:.2f} Hz per cell over {len(LEGMN)} cells); the cord's spikes do not reach the body")
PUP = None
if args.puppet:   # (TODO 4o) the scripted tripod's cells: each leg's own mapped motor neurons by role and sign (the map above, --hind-map as given)
    _TRI = {"lf": 0.0, "rm": 0.0, "lh": 0.0, "rf": 0.5, "lm": 0.5, "rh": 0.5}; _SW = (("levate", +1), ("protract", +1)); _ST = (("levate", -1), ("protract", -1), ("flex", -1))
    _pc, _pl, _pk2 = [], [], []
    print(f"the scripted tripod: {PUP_F:g} Hz, duty {PUP_DUTY:g} (stance {PUP_DUTY / PUP_F * 1000:.0f} ms, swing {(1 - PUP_DUTY) / PUP_F * 1000:.0f} ms), groups lf rm lh (phase 0) / rf lm rh (phase 0.5), from {args.warmup:g} s; Poisson trains, rng [seed, 88]")
    _dofn2 = [dof_name(x) for x in dofs]
    for leg in LEG6:
        for kind, sel, hz_ in ((0, _SW, args.puppet_swing_hz), (1, _ST, args.puppet_stance_hz)):
            for ro, ag in sel:
                js = sorted(groups.get((leg, ro, ag), []))
                _pc += js; _pl += [LEG6.index(leg)] * len(js); _pk2 += [kind] * len(js)
                if js: print(f"  {leg} {'swing ' if kind == 0 else 'stance'} {hz_:5.0f} Hz  {ro:8s} {ag:+d} -> {_dofn2[roles[leg][ro]['k']]:36s} {len(js):2d} cells: " + ", ".join(f"{t_} x{int(sum(mty[j] == t_ for j in js))}" for t_ in sorted(set(mty[js]))) + f"; f_w {min(f_w[j] for j in js):.3f}-{max(f_w[j] for j in js):.3f}")
                else: print(f"  {leg} {'swing ' if kind == 0 else 'stance'} {hz_:5.0f} Hz  {ro:8s} {ag:+d} -> no mapped cells")
    if _pk == "tripod2":   # (09-23) rebuild the sets: kind 0 = flexors + levators (swing 0-40 %), 2 = protractors (swing 20-80 %), 1 = stance, as tripod
        _pc, _pl, _pk2 = [], [], []; _W2 = ((0, (("flex", +1), ("levate", +1)), args.puppet_swing_hz, "swing 0-40 %"), (2, (("protract", +1),), args.puppet_swing_hz, "swing 20-80 %"), (1, _ST, args.puppet_stance_hz, "stance"))
        print(f"  tripod2 (replaces the lines above): stance duty " + " ".join(f"{l} {d_:g}" for l, d_ in zip(LEG6, PUP_DUTY6)) + ", offsets " + " ".join(f"{g_.upper()} {v_:g}" for g_, v_ in PUP_OFF3.items()) + f" cycles; per leg swing {np.round((1 - PUP_DUTY6) / PUP_F * 1000).astype(int).tolist()} ms")
        for leg in LEG6:
            for kind, sel, hz_, lab in _W2:
                for ro, ag in sel:
                    js = sorted(groups.get((leg, ro, ag), []))
                    _pc += js; _pl += [LEG6.index(leg)] * len(js); _pk2 += [kind] * len(js)
                    print(f"  {leg} {lab:13s} {hz_:5.0f} Hz  {ro:8s} {ag:+d} -> {_dofn2[roles[leg][ro]['k']]:36s} {len(js):2d} cells" + (": " + ", ".join(f"{t_} x{int(sum(mty[j] == t_ for j in js))}" for t_ in sorted(set(mty[js]))) + f"; f_w {min(f_w[j] for j in js):.3f}-{max(f_w[j] for j in js):.3f}" if js else ""))
        _TRI = {l: _TRI[l] + PUP_OFF3[l[1]] for l in LEG6}
    PUP = dict(cells=np.array(_pc, np.int64), leg=np.array(_pl, np.int64), kind=np.array(_pk2, np.int64), off=np.array([_TRI[l] for l in LEG6]), rng=np.random.default_rng([args.seed, 88]))
    if _pk == "tripod2": PUP["duty"] = PUP_DUTY6
    PUPSW = np.zeros((n_ms, 6), np.int8)   # 1 = the leg's scripted swing this ms
    print(f"{len(PUP['cells'])} motor neurons scripted; the cord's own motor spikes are logged, never felt")
LOGX = np.flatnonzero(np.isin(mty, [x for x in args.log_x.split(',') if x])) if args.log_x else np.zeros(0, np.int64); XMS = np.zeros((n_ms + 1, len(LOGX)), np.int16) if len(LOGX) else None; xpos = np.full(M.N, -1, np.int64); xpos[LOGX] = np.arange(len(LOGX))
if len(LOGX): print(f"log-x: {len(LOGX)} cells of {args.log_x}")
if args.log_v:   # the membrane logger (09-22, campaign item 2b), as in world/cord.py
    _vt = [x for x in args.log_v.split(",") if x]; _vc = [np.flatnonzero(mty == t_) for t_ in _vt]; _vi = np.concatenate(_vc).astype(np.int64); _vg = np.repeat(np.arange(len(_vt)), [len(c_) for c_ in _vc]); _vn = np.maximum(np.bincount(_vg, minlength=len(_vt)), 1)
    VMS = np.zeros((n_ms, len(_vt)), np.float32); print(f"logging the membrane of {len(_vi)} cells of {len(_vt)} types: " + ", ".join(f"{t_} {len(c_)}" for t_, c_ in zip(_vt, _vc)))
else: VMS = None
state = {"walk_gain": 0.0}; prev_knee = None; t_touch = np.full(6, -1e9); was_on = np.zeros(6, bool); force_ok = True; Fsm = np.zeros(6); prevF = np.zeros(6)
NONLEG = np.array([i for i, s_ in enumerate(segs) if not any(s_.startswith(l + "_") for l in LEG6)]); pad_on = np.zeros(6, bool); BODYF = np.zeros((n_ms // 10 + 1, 2), np.float32)   # the feet's and the whole body's ground reaction, per 10 ms (F2)
for ms in range(n_ms):
    t = ms / 1000.0; state["walk_gain"] = (min(1.0, (t - args.warmup) / args.walk_ramp) if args.walk_ramp > 0 else 1.0) if t >= args.warmup else 0.0
    if PB is not None:
        ch = int((args.playback_start + max(t - args.warmup, 0.0)) * 10) if t >= args.warmup else -1; state["dn_hz"] = PB["hz"][min(ch, PB["n"] - 1)] if ch >= 0 else np.zeros(len(PB["cells"]), np.float32)
    ang = sim.get_joint_angles("nmf"); knee = np.array([(np.degrees(ang[knee_idx[l]]) - knee_neutral[l]) * knee_sign[l] for l in LEG6]); om = np.zeros(6) if prev_knee is None else (knee - prev_knee) * 1000.0; prev_knee = knee   # signed flexion FROM NEUTRAL (the review's F1: the centre was lost in the port from leg_loop.py)
    F = FLEG = leg_forces()   # always read (09-23, review R1: with load out of the loop the feet's force was never read, so 'no lifts' in those arms was zero by construction and the pads never engaged; the position+load path is unchanged)
    if adh and args.adhesion == "contact": F = np.maximum(F - args.adhesion_gain * pad_on, 0.0)   # the review's F3: the contact reading includes the pad's pull while it is on
    if np.isnan(F).any(): F = np.zeros(6); force_ok = False
    FLEG = F   # the leg sensor's reading, net of the pads: leg_force and ground keep this meaning whatever --load-from says
    if not args.tethered:   # (09-23, P1) the vertical ground reaction on the feet (tarsus1-5) and on the rest of each leg, per ms
        try:
            _cf = np.asarray(sim.get_bodysegment_contact_forces("nmf", segs)); FT[ms] = [_cf[TARS[i], 2].sum() for i in range(6)]; FO[ms] = [_cf[OTHL[i], 2].sum() for i in range(6)]; FB[ms] = np.abs(_cf[NONLEG, 2]).sum()
        except Exception: FT[ms] = FO[ms] = FB[ms] = np.nan
    Ftar = np.maximum(FT[ms] - args.adhesion_gain * pad_on, 0.0) if (adh and args.adhesion == "contact") else np.maximum(FT[ms], 0.0)
    FTN[ms] = Ftar
    if args.load_from == "tarsi": F = np.nan_to_num(Ftar)
    Fsm = F if ms == 0 else 0.8 * Fsm + 0.2 * F; dF = (Fsm - prevF) * 1000.0 if ms else np.zeros(6); prevF = Fsm.copy()
    for i, leg in enumerate(LEG6):
        k = knee[i] if args.senses == "v1" else knee[i] + knee90[leg]   # v2: flexion past the claw's null at 90 deg femur-tibia (Mamiya 2018), not past the model's neutral
        ext_rate = args.claw_hz * float(np.clip((-k) / 60.0, 0, 1)); flex_rate = args.claw_hz * float(np.clip(k / 60.0, 0, 1))   # + = flexion by the measured sign
        state[f"claw_e_{leg}"], state[f"claw_f_{leg}"] = (ext_rate, flex_rate) if args.claw_labels == "50ext" else (flex_rate, ext_rate)   # the rows are named by TYPE (claw_e = SNpp50); the labels say which rate each type gets
        state[f"hook_f_{leg}"] = args.hook_hz * float(np.clip(om[i] / args.hook_vel, 0, 1)); state[f"hook_e_{leg}"] = args.hook_hz * float(np.clip(-om[i] / args.hook_vel, 0, 1))
        ld = float(np.clip(F[i] / F_stand + args.load_deriv * dF[i] * 0.05 / F_stand, 0, 2))
        if args.slow_init > 0 and t < args.warmup + args.slow_init: ld = max(ld, 1.0)
        state[f"load_{leg}"] = args.leg_load_hz * ld; state[f"slow_{leg}"] = args.slow_hz * ld; state[f"cocon_{leg}"] = args.cocon * args.slow_hz * ld
        if args.senses == "v2":   # (campaign item 6, 09-22) hair plates from the coxa's pitch; touch while the foot is on the ground (pad_on's threshold)
            a_ = float(ang[cx_idx[leg]]); n_ = cx_n[leg]; lo_, hi_ = cx_rng[leg]
            state[f"hp_{leg}"] = args.hp_hz * float(np.clip((a_ - n_) / max(hi_ - n_, 1e-9) if a_ >= n_ else (n_ - a_) / max(n_ - lo_, 1e-9), 0, 1))
            on_ = bool(F[i] > 0.05)
            if on_ and not was_on[i]: t_touch[i] = t
            was_on[i] = on_; state[f"tact_{leg}"] = (args.tactile_hz * (5.0 if (t - t_touch[i]) < 0.030 - 1e-9 else 1.0)) if on_ else 0.0
        if args.slow_mv > 0:
            if len(SLOW_BY_LEG[leg]): M._ext[SLOW_BY_LEG[leg]] = np.float32(args.slow_mv * ld)
            if args.cocon > 0 and len(SWING_BY_LEG[leg]): M._ext[SWING_BY_LEG[leg]] = np.float32(args.cocon * args.slow_mv * ld)
    KA[ms] = knee; FL[ms] = FLEG
    if ms % 10 == 0: JA[ms // 10] = np.degrees(ang)
    REG.apply(M, state, t, 0.001); M.step(); idx = M.last_idx
    if VMS is not None: VMS[ms] = np.bincount(_vg, weights=M.v[_vi], minlength=len(_vt)) / _vn
    if XMS is not None and idx.size:
        xh = xpos[idx]; xh = xh[xh >= 0]
        if xh.size: np.add.at(XMS[ms], xh, 1)
    if TW is not None: TW["s"] *= TW["D"]; torque[:, ms] += TW["s"]   # (--twitch azevedo) the slow cells' low-pass, from the spikes before this ms
    if args.freeze_mn > 0 and ms >= int(args.freeze_mn * 1000):
        if ms == int(args.freeze_mn * 1000): _hold_t = torque[:, ms].copy(); _hold_g = {l: float(grip[l][ms]) for l in LEG6}; print(f"muscles frozen at {args.freeze_mn:.1f} s: torque {np.round(np.abs(_hold_t).max(), 3)} max, grip {np.round(list(_hold_g.values()), 2)}")
        torque[:, ms] = _hold_t
        for l in LEG6: grip[l][ms] = _hold_g[l]
        hit = np.zeros(0, np.int64)
    elif PUP is not None:   # (TODO 4o) the PUPPET: the scripted tripod, the cord's spikes logged only
        if t >= args.warmup:
            if "duty" not in PUP:
                sw = ((((t - args.warmup) * PUP_F + PUP["off"]) % 1.0) >= PUP_DUTY); PUPSW[ms] = sw
                pon_ = np.where(PUP["kind"] == 0, sw[PUP["leg"]], ~sw[PUP["leg"]]); rate_ = np.where(PUP["kind"] == 0, args.puppet_swing_hz, args.puppet_stance_hz) * pon_ / 1000.0
            else:   # tripod2: the swing's own clock s in [0, 1)
                ph_ = ((t - args.warmup) * PUP_F + PUP["off"]) % 1.0; sw = ph_ >= PUP["duty"]; PUPSW[ms] = sw; s_ = np.where(sw, (ph_ - PUP["duty"]) / (1.0 - PUP["duty"]), -1.0)
                sl_ = s_[PUP["leg"]]; pon_ = np.where(PUP["kind"] == 0, (sl_ >= 0) & (sl_ < 0.4), np.where(PUP["kind"] == 2, (sl_ >= 0.2) & (sl_ < 0.8), sl_ < 0))
                rate_ = np.where(PUP["kind"] == 1, args.puppet_stance_hz, args.puppet_swing_hz) * pon_ / 1000.0
            hit = PUP["cells"][PUP["rng"].random(len(PUP["cells"])) < rate_]
        else: hit = np.zeros(0, np.int64)
        if idx.size:
            for j in idx[np.isin(idx, LEGMN)]: spk[ms // 10, lpos[int(j)]] += 1
    elif MNP is not None:
        hit = LEGMN[_mnp_rng.random(len(LEGMN)) < MNP]
        if idx.size:
            for j in idx[np.isin(idx, LEGMN)]: spk[ms // 10, lpos[int(j)]] += 1   # the cord's own motor spikes are still logged
    elif idx.size:
        hit = idx[np.isin(idx, LEGMN)]
        for j in hit: spk[ms // 10, lpos[int(j)]] += 1
    else: hit = np.zeros(0, np.int64)
    for j in hit:   # what the body sees: the cord's spikes, or the Poisson trains, or nothing after a freeze
        j = int(j)
        if j in grip_of: grip[grip_of[j]][ms: ms + KL] += f_w.get(j, 0.1) * K / args.sat
        elif TW is not None and j in TW["A"]: a_ = cell_sgn[j] * TW["A"][j]; TW["s"][cell_dof[j]] += a_; torque[cell_dof[j], ms] += a_   # a slow spike: a jump in the low-pass, felt from this ms
        elif j in cell_dof: torque[cell_dof[j], ms: ms + KL] += cell_sgn[j] * f_w[j] * K / args.sat
    tq = np.clip(args.gain * torque[:, ms], -60, 60); sim.set_actuator_inputs("nmf", ActuatorType.MOTOR, tq)
    if adh and args.adhesion == "ltm": sim.set_leg_adhesion_states("nmf", np.array([grip[l][ms] > 0.05 for l in LEG6]))
    elif adh and args.adhesion == "contact": pad_on = F > 0.05; sim.set_leg_adhesion_states("nmf", pad_on)
    elif adh: sim.set_leg_adhesion_states("nmf", np.zeros(6, bool))
    for _ in range(steps_per_ms): sim.step()
    P[ms] = sim.get_body_positions("nmf")[thorax]; Q[ms] = sim.get_body_rotations("nmf")[thorax]
    if ms % 10 == 0:
        try: _cf = np.asarray(sim.get_bodysegment_contact_forces("nmf", segs)); BODYF[ms // 10] = (float(FLEG.sum()), float(np.abs(_cf[NONLEG, 2]).sum()))   # the feet's load, and the vertical ground reaction on the NON-leg segments (thorax, abdomen, head): a standing fly has none of the second (the review's F2)
        except Exception: BODYF[ms // 10] = (float(FLEG.sum()), np.nan)
    if not args.no_video: sim.render_as_needed()
    if ms % 5000 == 0 and ms: print(f"t={t:5.1f}s thorax z {P[ms, 2]:.2f}  legs F {np.round(FLEG, 1)}  knees {np.round(knee, 0)}  ({time.time() - t0:.0f}s)")
os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
nfr = n_ms // 10; frames = spk[:nfr]
_x = dict(x_ms=XMS[:n_ms], x_type=mty[LOGX], x_bodyId=mbid[LOGX]) if XMS is not None else {}
np.savez_compressed(args.out + ".cells.npz", cells=LEGMN, bodyId=mbid[LEGMN], type=mty[LEGMN], side=mns[LEGMN], counts=frames[: (nfr // 10) * 10].reshape(nfr // 10, 10, -1).sum(1).astype(np.int32), pose_chunk=np.zeros((nfr // 10, 3), np.float32), frames=frames, **_x, pose_frame=np.zeros((nfr, 3), np.float32), **({'v_ms': VMS, 'v_types': np.array(_vt)} if VMS is not None else {}))
w_, x_, y_, z_ = Q[:, 0], Q[:, 1], Q[:, 2], Q[:, 3]; yaw = np.degrees(np.arctan2(2 * (w_ * z_ + x_ * y_), 1 - 2 * (y_ ** 2 + z_ ** 2)))
np.savez_compressed(args.out + ".npz", thorax=P, quat=Q, leg_force=FL, knee=KA, ground=BODYF[: n_ms // 10], tarsal_force=FTN, other_leg_force=FO.astype(np.float32), body_force=FB.astype(np.float32), stand3=np.stack([FTN.sum(1), FO.sum(1), FB], 1)[::10][: n_ms // 10].astype(np.float32), joints=JA[: n_ms // 10], joint_names=np.array([dof_name(x) for x in all_dofs]), args=np.array(str(vars(args))), **({"puppet_swing": PUPSW} if PUP is not None else {}))
w0 = int(args.warmup * 1000); v = np.linalg.norm(np.diff(P[w0:, :2], axis=0), axis=1) * 1000; hz = frames[w0 // 10:].mean(0) * 100
flex = np.array([("Ti flexor" in t_) or ("Acc. ti flexor" in t_) for t_ in mty[LEGMN]]); ext = mty[LEGMN] == "Ti extensor MN"
gb = BODYF[w0 // 10: n_ms // 10]; body_on_floor = float(np.nanmean(gb[:, 1])); _ft = FTN[w0:].sum(1).mean(); _fo = np.nanmean(FO[w0:].sum(1)); _fb = np.nanmean(FB[w0:])
print(f"standing? feet (tarsus1-5, net of the pads) {_ft:.2f} uN, other leg segments (coxa / trochanter-femur / tibia) {_fo:.2f} uN ({_fo / weight * 100:.0f} %: the coxa share), body (thorax / abdomen / head) {_fb:.2f} uN of {weight:.2f}; per-leg tarsal load {np.round(FTN[w0:].mean(0), 2)}, other leg segments {np.round(np.nanmean(FO[w0:], 0), 2)} (lf lm lh rf rm rh); load rows from {args.load_from}, hind map {args.hind_map}, start {args.start_pose}")
print(f"standing? the body (thorax / abdomen / head) rests on the floor with {body_on_floor:.1f} uN of {weight:.1f} ({body_on_floor / weight * 100:.0f} % of his weight; 0 = standing on his feet); the feet carry {gb[:, 0].mean():.1f} uN net of the pads")
print(f"done in {time.time() - t0:.0f}s ({args.seconds / (time.time() - t0):.2f}x real time); contact forces {'read' if force_ok else 'UNAVAILABLE (load rows got 0)'}; after the warm-up: leg MN {hz.mean():.2f} Hz/cell, flexors {hz[flex].mean():.2f}, extensors {hz[ext].mean():.2f}; "
      f"thorax height mean {P[w0:, 2].mean():.2f} (min {P[w0:, 2].min():.2f}), speed {v.mean():.1f} mm/s, net turn {((yaw[-1] - yaw[w0] + 180) % 360) - 180:+.0f} deg; leg forces mean {np.round(FL[w0:].mean(0), 1)} (F_stand {F_stand:.2f}); knee sd {np.round(KA[w0:].std(0), 0)}")
if not args.no_video: sim.renderer.save_video(args.out + ".mp4"); print("video", args.out + ".mp4")
print("wrote", args.out + ".npz")
