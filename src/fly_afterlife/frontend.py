"""
frontend: the graded optic lobe in front of the spiking brain. flyvis today; the transplant later.

    fe = FlyvisFrontEnd(model="flow/0000/000", geom="seam/eye_geom.npz", fps=100, chunk=10, deterministic=False)
    a = fe.chunk(lum)                      # {(side, type): (CH, n_cells)} activity, state carried between chunks
    rest = fe.rest(render_chunk)           # common rest from 10 still chunks (last 5 averaged)
    groups = fe.groups(brain)              # {(type, side): (brain cell indices, flyvis column index)} for the seam

the seam's convention (docs/SEAM.md "orientation, decided"): flyvis column (u, v) from the eye's
(sx, sy) by v = round(sx), u = round(-sy - v/2); front at flyvis image-right; T4/T5 activity minus
rest, clipped at 0, times a gain, is the Poisson rate on the brain's own T4/T5 cells. this module
is pair.py's flyvis block verbatim.
"""
from __future__ import annotations
import os
import numpy as np
import torch

TYPES = ["T4a", "T4b", "T4c", "T4d", "T5a", "T5b", "T5c", "T5d"]


class FlyvisFrontEnd:
    def __init__(self, model="flow/0000/000", geom="seam/eye_geom.npz", fps=100, chunk=10, deterministic=False, root="/home/nate/code/fly-afterlife/flyvis_data", types=None):
        self.types = list(types) if types is not None else list(TYPES)   # the flyvis cell types this instance hands over (T4/T5 by default; Mi15 for the UV retina, 09-18)
        os.environ.setdefault("FLYVIS_ROOT_DIR", root)
        if deterministic: os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8"); torch.use_deterministic_algorithms(True)
        import flyvis
        from flyvis import NetworkView
        self.flyvis = flyvis; self.fps, self.CH = fps, chunk
        self.net = NetworkView(model).init_network(); self.net.eval()
        lattice = sorted({(u, v) for u in range(-15, 16) for v in range(max(-15, -15 - u), min(15, 15 - u) + 1)}); self.idx_of = {uv: i for i, uv in enumerate(lattice)}
        ntype = self.net.connectome.nodes.type[:].astype(str); self.tix = {t: np.flatnonzero(ntype == t) for t in self.types}
        self.g = np.load(geom); self.eyemap = {}
        for s in "LR":
            k = np.flatnonzero(self.g["side"] == s); v = np.rint(+self.g["sx"][k]).astype(int); u = np.rint(-self.g["sy"][k] - v / 2.0).astype(int)
            col = np.array([self.idx_of.get((int(a), int(b)), -1) for a, b in zip(u, v)]); ok = col >= 0; self.eyemap[s] = (k[ok], col[ok])
        self.state = {"L": None, "R": None}

    def chunk(self, lum_chunk: np.ndarray) -> dict:
        out = {}
        for s in "LR":
            k, col = self.eyemap[s]; movie = np.full((1, self.CH, 1, 721), 0.5, np.float32); movie[0, :, 0, col] = lum_chunk[:, k].T
            with torch.no_grad(): st = self.net.simulate(torch.tensor(movie, device=self.flyvis.device), dt=1 / self.fps, initial_state=self.state[s], as_states=True)
            self.state[s] = st[-1]; act = torch.stack([x.nodes.activity[0] for x in st]).cpu().numpy()
            for t in self.types: out[(s, t)] = act[:, self.tix[t]]
        return out

    def rest(self, render_chunk, chunks=10, keep_from=5) -> dict:
        """common rest: run `chunks` still chunks, average the activity of the last ones. carries state."""
        acc = {}
        for c in range(chunks):
            a = self.chunk(render_chunk())
            if c >= keep_from:
                for k_, v_ in a.items(): acc.setdefault(k_, []).append(v_)
        return {k_: np.concatenate(v_).mean(0) for k_, v_ in acc.items()}

    def groups(self, brain, columns="seam/t4t5_columns.npz", types=None) -> dict:
        """{(type, side): (brain cell indices, flyvis column index per cell)} for the brain's T4/T5 cells with a known column."""
        cols = np.load(columns); g = self.g
        gkey = {(str(s), int(a), int(h)): i for i, (s, a, h) in enumerate(zip(g["side"], g["hex1"], g["hex2"]))}
        gi = np.array([gkey.get((str(s), int(a), int(h)), -1) for s, a, h in zip(cols["side"], cols["hex1"], cols["hex2"])])   # -1: a hex column the eye geometry has no direction for (columns_all reaches some); dropped below
        groups = {}
        for s in "LR":
            k, col = self.eyemap[s]; colmap = dict(zip(k.tolist(), col.tolist()))
            for t in (types or self.types):
                kk = (cols["type"] == t) & (cols["side"] == s); hx = np.array([colmap.get(int(i), -1) for i in gi[kk]]); ok = hx >= 0; groups[(t, s)] = (cols["idx"][kk][ok], hx[ok])
        return groups
