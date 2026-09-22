"""build_cord.py - the headless preparation's brain: the ventral nerve cord cut out of brain_whole.npz.

keeps every cell whose superclass lives in the cord (vnc_intrinsic, vnc_sensory, vnc_motor, vnc_efferent, vnc_endocrine, the
ascending neurons and sensory ascending cells, whose somas are in the cord) plus the descending neurons, kept as the inputs they
are in a decapitated fly (Bidaye 2020: their axons are still in the cord and can be driven; their brain inputs are cut). every
edge with both ends kept survives, with its weight and the presynaptic sign. same keys as brain_whole.npz, so the engine loads it
unchanged.

    uv run python scripts/build_cord.py            -> brain_cord.npz
"""
import numpy as np
from collections import Counter

KEEP = {"vnc_intrinsic", "vnc_sensory", "vnc_motor", "vnc_efferent", "vnc_endocrine", "vnc_tbc", "vnc_sensory_tbc",
        "ascending_neuron", "sensory_ascending", "sensory_ascending_tbc", "efferent_ascending",
        "descending_neuron", "descending_neuron_tbc", "sensory_descending", "efferent_descending"}
B = np.load("brain_whole.npz", allow_pickle=True); sc = B["sc"].astype(str)
keep = np.isin(sc, list(KEEP)); idx = np.flatnonzero(keep); new = -np.ones(len(sc), np.int64); new[idx] = np.arange(len(idx))
pre, post = B["pre"], B["post"]; em = keep[pre] & keep[post]
out = {k: B[k][idx] for k in ("bodyId", "type", "cls", "sc", "side", "nt", "sign")}
out["pre"] = new[pre[em]].astype(np.int32); out["post"] = new[post[em]].astype(np.int32); out["w"] = B["w"][em]
np.savez_compressed("brain_cord.npz", **out)
print(f"brain_cord.npz: {len(idx)} of {len(sc)} cells, {int(em.sum())} of {len(pre)} edges ({B['w'][em].sum() / B['w'].sum() * 100:.1f} % of synapses)")
print("by superclass:", Counter(sc[idx]).most_common())
dn = np.flatnonzero(sc[idx] == "descending_neuron"); print(f"descending neurons kept as inputs: {len(dn)}; their cut brain inputs: {int((keep[post] & ~keep[pre]).sum())} edges dropped from the brain side")
