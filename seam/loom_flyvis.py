"""first contact: run one pretrained flyvis model on a looming dark disc, read T4/T5."""
import os, time, numpy as np, torch
os.environ.setdefault("FLYVIS_ROOT_DIR", "/home/nate/code/fly-afterlife/flyvis_data")
import flyvis
from flyvis import NetworkView
from flyvis.datasets.rendering import eye as eyemod
print("device", flyvis.device, torch.cuda.get_device_name(0) if torch.cuda.is_available() else "")

t0 = time.time()
nv = NetworkView("flow/0000/000")
net = nv.init_network()          # loads best checkpoint
net.eval()
print(f"network loaded in {time.time()-t0:.1f}s; nodes {net.connectome.nodes.type[:].shape[0]}")

# --- stimulus: grey background, dark disc expanding from the centre over 1.0 s, at 100 fps
H = W = 200; fps = 100; T = 150
yy, xx = np.mgrid[0:H, 0:W]; cy, cx = H/2, W/2
frames = np.full((T, H, W), 0.5, np.float32)
for t in range(50, T):
    r = 2 + (t-50) * 0.6            # radius grows ~60 px/s
    frames[t][(yy-cy)**2 + (xx-cx)**2 < r*r] = 0.0
Eye = getattr(eyemod, "BoxEye", None) or [getattr(eyemod, n) for n in dir(eyemod) if n.endswith("Eye")][0]
eye = Eye(extent=15, kernel_size=13)
hexmovie = eye(torch.tensor(frames[None]), hex_sample=True)   # (1, T, 1, 721)
print("hex movie", tuple(hexmovie.shape))

t0 = time.time()
with torch.no_grad():
    act = net.simulate(hexmovie.to(flyvis.device), dt=1/fps, as_layer_activity=True)
print(f"simulated {T} frames in {time.time()-t0:.2f}s; vram peak {torch.cuda.max_memory_allocated()/1e6:.0f} MB")

for ty in ["R1", "L1", "Mi1", "Tm1", "T4a", "T4b", "T4c", "T4d", "T5a", "T5b", "T5c", "T5d"]:
    try:
        a = getattr(act, ty)                 # (1, T, n_columns)
        a = np.asarray(a.squeeze(0))
        pre, loom = a[10:50].mean(), a[80:150].mean()
        print(f"{ty:4s} cols={a.shape[-1]:4d}  pre-loom {pre:+.3f}  during {loom:+.3f}  peak {a.max():+.3f}")
    except Exception as e:
        print(ty, "ERR", type(e).__name__, e); break
