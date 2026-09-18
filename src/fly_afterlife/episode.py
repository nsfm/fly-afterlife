"""
episode: the one chunk loop. render -> physics -> optic lobe -> receptors -> brains -> effectors -> log.

    ep = Episode(fps=100, chunk=10, eye=eye, room=room, him=m, her=her, brains=(M, F), readouts=(RM, RF),
                 registries=(REG, REGF), front_end=flyvis_chunk, rest=rest, effectors=(steer, pace, hers, songdet))
    ep.run(seconds)
    ep.save(path, **scene_meta)

this first version is world/pair.py's loop verbatim (same order, same expressions, same rng
consumption, same npz keys) so the oracle check passes. the per_frame / per_chunk namespaces,
threaded brains and per-millisecond drive come after (docs/ARCHITECTURE.md).
"""
from __future__ import annotations
import time
import numpy as np


class Episode:
    def __init__(self, fps, chunk, eye, room, him, her, brains, readouts, registries, front_end, rest, effectors, lam=0.8, log_every=50, on_chunk=None, threads=True):
        """room: any world with scene(bodies) / step_frame(m, f, fps) / contacts (Room, Drum). her: a Body or None.
        effectors: (steer, pace, her_steer or None, song or None). on_chunk(ep, c, cntM): optional per-chunk hook."""
        self.on_chunk = on_chunk; self.threads = threads
        from concurrent.futures import ThreadPoolExecutor; self.pool = ThreadPoolExecutor(max_workers=1)
        self.fps, self.CH, self.SPF = fps, chunk, 1000 // fps
        self.eye, self.room, self.m, self.her = eye, room, him, her
        self.M, self.F = brains; self.RM, self.RF = readouts; self.REG, self.REGF = registries
        self.front_end, self.rest, self.LAM, self.log_every = front_end, rest, lam, log_every
        self.steer, self.pace, self.hers, self.songdet = effectors
        self.female = self.F is not None
        self.solo = self.her is None                      # single fly: no second pose, no smells, no her-steering
        self.LUM, self.POSE, self.POSE2, self.TOUCH, self.TKIND = [], [], [], [], []
        self.log = {f"m_{k}": [] for k in self.RM} | ({f"f_{k}": [] for k in self.RF} if self.female else {}) | {"dist": [], "song": [], "v_m": [], "v_f": []}

    # ---- the pieces of one chunk
    def render_and_move(self):
        """CH frames: render his eye, log poses, step the world. returns (lum, touched_m, kind_m, touched_f)."""
        CH, m, her = self.CH, self.m, self.her
        lum = np.zeros((CH, self.eye.n), np.float32); touched_m = [None] * CH; touched_f = [None] * CH; kind_m = [0] * CH
        for f in range(CH):
            lum[f] = self.eye.render(self.room.scene([] if self.solo else [her]), pos=(m.x, m.y, 0.5), heading_deg=m.h); self.POSE.append((m.x, m.y, m.h))
            if not self.solo: self.POSE2.append((her.x, her.y, her.h))
            self.room.step_frame(m, her, self.fps)
            touched_m[f] = m.touched; kind_m[f] = m.kind; touched_f[f] = None if self.solo else her.touched
            self.TOUCH.append(touched_m[f]); self.TKIND.append(kind_m[f])
        return lum, touched_m, kind_m, touched_f

    def smells(self):
        """chunk-constant odours at the antennae: fly odour from her to him, cVA from him to her, exp(-d / LAM).
        (the chemo brief says plumes are intermittent and ORNs divide by a running mean: next version.)"""
        m, her, LAM = self.m, self.her, self.LAM
        if self.solo: return
        aL, aR = m.antennae()
        if self.female:
            cL, cR = float(np.exp(-np.hypot(*(aL - [her.x, her.y])) / LAM)), float(np.exp(-np.hypot(*(aR - [her.x, her.y])) / LAM)); self.M.smell_bilateral(left={"flyodour": cL}, right={"flyodour": cR})
            bL, bR = her.antennae(); dL, dR = float(np.exp(-np.hypot(*(bL - [m.x, m.y])) / LAM)), float(np.exp(-np.hypot(*(bR - [m.x, m.y])) / LAM)); self.F.smell_bilateral(left={"cVA": dL}, right={"cVA": dR})

    def drive_and_step(self, a, touched_m, kind_m, touched_f, singing):
        """CH frames of receptor drive and SPF brain steps each; returns per-chunk readout counts (cntM, cntF)."""
        CH, fps, m = self.CH, self.fps, self.m
        accM = np.zeros(self.M.N, np.int32); accF = np.zeros(self.F.N, np.int32) if self.female else None
        for f in range(CH):
            t_f = (len(self.POSE) - CH + f) / fps
            st_ = {"a": a, "rest": self.rest, "f": f, "tm": touched_m[f], "kind": kind_m[f], "pace": float(np.clip(m.v / 0.45, 0, 1)), "t_chunk_end": len(self.POSE) / fps, "tf": touched_f[f], "singing": singing}
            if hasattr(self.room, "temperature"):
                px, py, ph = self.POSE[len(self.POSE) - CH + f]; hr = np.radians(ph); fwd = np.array([np.cos(hr), np.sin(hr)]); left = np.array([-np.sin(hr), np.cos(hr)])
                aL_ = np.array([px, py]) + 0.1 * fwd + 0.15 * left; aR_ = np.array([px, py]) + 0.1 * fwd - 0.15 * left
                st_["T_L"] = self.room.temperature(float(aL_[0]), float(aL_[1])); st_["T_R"] = self.room.temperature(float(aR_[0]), float(aR_[1]))
                if hasattr(self.room, "odour"):
                    oL = self.room.odour(float(aL_[0]), float(aL_[1]), t_f); oR = self.room.odour(float(aR_[0]), float(aR_[1]), t_f)
                    st_["odour_L"] = oL; st_["odour_R"] = oR
                if hasattr(self.room, "humidity"): st_["humidity"] = self.room.humidity(float(px), float(py))
                if hasattr(self.room, "wind"): st_["wind_rel"] = float((np.degrees(np.arctan2(-self.room.wind[1], -self.room.wind[0])) - ph + 180) % 360 - 180)   # where the wind comes FROM, relative to his heading (+ = from his left)
                st_["taste"] = getattr(m, "taste", None)
            self.REG.apply(self.M, st_, t_f, 1.0 / fps)
            if self.female: self.REGF.apply(self.F, st_, t_f, 1.0 / fps)
            if self.female and self.threads:   # the two brains are independent within a chunk: step them in parallel (numba kernels release the GIL)
                def _run(B, acc):
                    for _ in range(self.SPF): B.step(); acc[B.last_idx] += 1
                fut = self.pool.submit(_run, self.F, accF); _run(self.M, accM); fut.result()
            else:
                for _ in range(self.SPF):
                    self.M.step(); accM[self.M.last_idx] += 1
                    if self.female: self.F.step(); accF[self.F.last_idx] += 1
        self.last_accM = accM   # per-cell counts for effectors that read motor patterns (legs.LegSteering)
        cntM = {k: int(accM[r].sum()) for k, r in self.RM.items()}
        cntF = {k: int(accF[r].sum()) for k, r in self.RF.items()} if self.female else {}
        return cntM, cntF

    # ---- the loop
    def run(self, seconds: float):
        T = int(seconds * self.fps); t0 = time.time(); m, her, log = self.m, self.her, self.log
        for c in range(T // self.CH):
            lum, touched_m, kind_m, touched_f = self.render_and_move()
            a = self.front_end(lum)
            dist = np.hypot(m.x - her.x, m.y - her.y) if self.female else np.inf
            self.smells()
            singing = (bool(self.songdet.hist) and len(self.songdet.hist) >= 5 and (log["song"] and log["song"][-1]) and dist < 0.4) if self.songdet is not None else False
            cntM, cntF = self.drive_and_step(a, touched_m, kind_m, touched_f, singing)
            m.h += (self.steer.step(cntM, any(touched_m), self.last_accM) if getattr(self.steer, "needs_cells", False) else self.steer.step(cntM, any(touched_m)))
            m.v = self.pace.step(cntM)
            if self.female and self.hers is not None: her.h += self.hers.step(cntF, touched_f)
            song = self.songdet.step(cntM["pIP10"]) if (self.songdet is not None and "pIP10" in cntM) else False
            log["song"].append(song and self.female and dist < 0.4); log["dist"].append(dist); log["v_m"].append(m.v); log["v_f"].append(0.0 if self.solo else her.v)
            if self.on_chunk is not None: self.on_chunk(self, c, cntM)
            for k in self.RM: log[f"m_{k}"].append(cntM[k])
            for k in self.RF: log[f"f_{k}"].append(cntF[k])
            if c % self.log_every == self.log_every - 1 and self.solo:
                print(f"t={(c+1)/10:5.1f}s  heading {m.h:+7.1f}  pos ({m.x:+.2f},{m.y:+.2f})  ({time.time()-t0:.0f}s)", flush=True)
            elif c % self.log_every == self.log_every - 1:
                print(f"t={(c+1)/10:5.1f}s  him ({m.x:+.2f},{m.y:+.2f}) {m.h:+6.0f}  her ({her.x:+.2f},{her.y:+.2f})  dist {dist:4.2f}  pC1 {sum(log['m_pC1'][-50:])} pIP10 {sum(log['m_pIP10'][-50:])} LC10a {sum(log['m_LC10a'][-50:])} | her pC1 {sum(log['f_pC1'][-50:]) if self.female else '-'} vpoEN {sum(log['f_vpoEN'][-50:]) if self.female else '-'} | contacts {self.room.contacts} songs {sum(log['song'])} | pace him {m.v:.2f} her {her.v:.2f} m/s  ({time.time()-t0:.0f}s)", flush=True)
            self.LUM.append((np.clip(lum, 0, 1) * 255).astype(np.uint8))
        return self

    # ---- output (the viewer's schema; per_frame / per_chunk namespaces are the next change)
    def save(self, path: str, posts=None, walls: dict | None = None, her_albedo: float | None = None, body_r: float = 0.08, her_r: float | None = None, fov: float = 150.0, extra: dict | None = None):
        CH, eye, log, POSE = self.CH, self.eye, self.log, self.POSE; Tn = len(POSE)
        out = dict(fps=self.fps, chunk=CH, lum=np.concatenate(self.LUM), pose=np.array(POSE, np.float32), fov=fov, contacts=self.room.contacts, sky=self.room.sky, ground=self.room.ground,
                   az=np.degrees(np.arctan2(eye.dir0[:, 1], eye.dir0[:, 0])).astype(np.float32), el=np.degrees(np.arcsin(np.clip(eye.dir0[:, 2], -1, 1))).astype(np.float32), side=eye.side,
                   touch=np.array([{"L": 1, "R": 2, "B": 3}.get(t_, 0) for t_ in self.TOUCH], np.int8), touch_kind=np.array(self.TKIND, np.int8), body_r=body_r, heading_chunk=np.array([p[2] for p in POSE[::CH]]),
                   **{f"n_{k}": np.repeat(np.array(v, np.int16), CH)[:Tn] for k, v in log.items() if k not in ("dist", "song", "v_m", "v_f")}, v_m=np.repeat(np.array(log["v_m"], np.float32), CH)[:Tn], v_f=np.repeat(np.array(log["v_f"], np.float32), CH)[:Tn], dist=np.repeat(np.array(log["dist"], np.float32), CH)[:Tn], song=np.repeat(np.array(log["song"], np.int8), CH)[:Tn])
        if not self.solo: out["pose2"] = np.array(self.POSE2, np.float32)
        if posts is not None: out["objects"] = posts; out["pillars"] = True; out["pillar_height"] = getattr(self.room, "pillar_height", 1.5)
        if walls is not None: out["walls"] = np.array([walls['half'], walls['height'], walls['albedo']], np.float32)
        if her_albedo is not None: out["her_albedo"] = her_albedo
        if her_r is not None: out["her_r"] = her_r
        if extra: out.update(extra)
        np.savez_compressed(path, **out)
        print("wrote", path, f"contacts {self.room.contacts}, song chunks {sum(log['song'])}, mean dist {np.mean(log['dist']):.2f}")
