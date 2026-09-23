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
DNS = np.isin(sc, ["descending_neuron", "descending_neuron_tbc"]); BRAINSIDE = DNS | np.isin(sc, ["ascending_neuron", "sensory_ascending", "sensory_ascending_tbc", "efferent_ascending", "sensory_descending", "efferent_descending"])
drop = em & DNS[post] & BRAINSIDE[pre]; n_dn_in = int(B["w"][drop].sum()); em = em & ~drop   # v2 (09-22, the positive control's finding): the cut kept the brain's synapses onto its descending neurons. a cord-intrinsic or cord-sensory cell cannot reach the brain, so its synapse onto a DN is in the cord and stays; a DN or ascending cell can be presynaptic in either, and the file does not say where, so those edges onto DNs are dropped (the fix tested in the rate model; Pugliese's vncRoisOnly matrix gives DNg100 +0 / -84 inputs, v1 had +2,300 / -3,900). a labelled approximation of "synapses inside the cord's ROIs"
out = {k: B[k][idx] for k in ("bodyId", "type", "cls", "sc", "side", "nt", "sign")}
out["pre"] = new[pre[em]].astype(np.int32); out["post"] = new[post[em]].astype(np.int32); out["w"] = B["w"][em]
np.savez_compressed("brain_cord.npz", **out)
print(f"brain_cord.npz: {len(idx)} of {len(sc)} cells, {int(em.sum())} of {len(pre)} edges ({B['w'][em].sum() / B['w'].sum() * 100:.1f} % of synapses)")
print(f"v2: {n_dn_in} synapses onto descending neurons from descending / ascending cells dropped (the brain-side inputs v1 kept)")
print("by superclass:", Counter(sc[idx]).most_common())
dn = np.flatnonzero(sc[idx] == "descending_neuron"); print(f"descending neurons kept as inputs: {len(dn)}; their cut brain inputs: {int((keep[post] & ~keep[pre]).sum())} edges dropped from the brain side")
