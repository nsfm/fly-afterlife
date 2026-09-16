import sys, time; sys.path.insert(0, 'ref/flybrain/scripts')
import numpy as np
from flysim import FlyBrain
t0=time.time(); b = FlyBrain('brain_whole.npz'); print('loaded', b.N, 'neurons', b.n_edges, 'edges in', round(time.time()-t0,1),'s')
mot = np.where(b.sc == 'cb_motor')[0]; ty = b.type.astype(str)
print('cb_motor types:', sorted(set(ty[mot])))
def motor_rates(r):
    rates = r.rates; out={}
    for t in sorted(set(ty[mot])):
        out[t]=float(rates[mot[ty[mot]==t]].mean())
    return out
b.reset(); t0=time.time(); base = b.run(500); print('500ms baseline in', round(time.time()-t0,1),'s; mean rate', round(base.mean_rate,3))
b.reset(); b.taste(1.0); sweet = b.run(500); print('sweet mean rate', round(sweet.mean_rate,3))
b.reset(); b.taste(0.0); b.taste(-1.0); bitter = b.run(500); print('bitter mean rate', round(bitter.mean_rate,3))
br, sr, bir = motor_rates(base), motor_rates(sweet), motor_rates(bitter)
print(f"{'motor':10s} {'base':>7s} {'sweet':>7s} {'bitter':>7s}")
for t in br: print(f"{t:10s} {br[t]:7.1f} {sr[t]:7.1f} {bir[t]:7.1f}")
print('\ntop DN actions on sweet:', sweet.top_actions(8))
print('top DN actions on bitter:', bitter.top_actions(8))
