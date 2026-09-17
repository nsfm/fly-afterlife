"""classical odour conditioning on the female, open loop. usage: --reward A|B|none --seed N --trials 8. 'none' = reward delivered alone (no odour) between presentations: the unpaired control."""
import sys, argparse, json, numpy as np; sys.path.insert(0, "ref/flybrain/scripts")
from flysim import FlyBrain, Params
ap = argparse.ArgumentParser(); ap.add_argument("--reward", default="A"); ap.add_argument("--seed", type=int, default=0); ap.add_argument("--trials", type=int, default=8); ap.add_argument("--wsyn", type=float, default=0.5); a = ap.parse_args()
b = FlyBrain("brain_female2.npz", seed=a.seed, balance_hemispheres=False, params=Params(mv_per_synapse=a.wsyn)); ty = b.type.astype(str); cls_ = b.cls.astype(str)
b.define_odor("A", n_channels=12, seed=7); b.define_odor("B", n_channels=12, seed=11); b.enable_plasticity(); b.enable_compartments(); pam = sorted(t for t in b._da_by_type if t.startswith("PAM"))
R = {"MBON": np.flatnonzero(cls_ == "MBON"), "DN": np.flatnonzero(b.sc == "descending_neuron")}
def present(odour, reward=False, ms=800, learn=True):
    b.reset(); b.drive_hz[:] = 0; b.g[:] = 0; b.refrac[:] = 0
    for _ in range(300): b.step()
    if odour: b.smell_bilateral(left={odour: 1.0}, right={odour: 1.0})
    cnt = {k: 0 for k in R}
    for i in range(ms):
        if reward and i >= 200:
            b.taste(1.0)
            for t in pam: b.stimulate_type(t, 200.0, mv=45.0)
        spk = b.step()
        if learn: b.learn()
        for k, r in R.items(): cnt[k] += int(spk[r].sum())
    b.taste(0.0); b.drive_hz[b.pop["gustatory"]] = 0.0
    for t in pam: b.stimulate_type(t, 0.0)
    b.smell_bilateral(left={}, right={}); return cnt
w0 = b._out_w[b._plastic].copy()
pre = {o: present(o, learn=False) for o in "AB"}
for trial in range(a.trials):
    if a.reward == "A": present("A", reward=True); present("B")
    elif a.reward == "B": present("A"); present("B", reward=True)
    else: present("A"); present(None, reward=True); present("B")
post = {o: present(o, learn=False) for o in "AB"}
fr = b._out_w[b._plastic] / np.maximum(w0, 1e-9)
out = {"reward": a.reward, "seed": a.seed, "weights_mean": float(fr.mean()), "depressed": int((fr < 0.9).sum()), "pre": pre, "post": post,
       "MBON_A/B": (pre["A"]["MBON"] / max(pre["B"]["MBON"], 1), post["A"]["MBON"] / max(post["B"]["MBON"], 1)), "DN_A/B": (pre["A"]["DN"] / max(pre["B"]["DN"], 1), post["A"]["DN"] / max(post["B"]["DN"], 1))}
print(f"reward {a.reward} seed {a.seed}: weights {out['weights_mean']:.4f}, depressed {out['depressed']};  MBON A {pre['A']['MBON']}->{post['A']['MBON']}  B {pre['B']['MBON']}->{post['B']['MBON']};  DN A {pre['A']['DN']}->{post['A']['DN']}  B {pre['B']['DN']}->{post['B']['DN']};  DN A/B {out['DN_A/B'][0]:.2f} -> {out['DN_A/B'][1]:.2f}")
json.dump(out, open(f"world/cond_{a.reward}_s{a.seed}.json", "w"))
