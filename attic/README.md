# attic

superseded scripts, kept for the record (docs/SEAM.md cites them by name). not maintained.

- `closedloop.py` - the first optomotor drum loop; replaced by `world/loop.py --mode drum`.
- `episode.py`, `neural.py` - the first open-loop episode pipeline (arena render -> LIF); replaced by `world/loop.py` and `world/pair.py`.
- `seam.py`, `seam_v1.py` - seam v0/v1 (flyvis -> LIF, one render for both eyes); replaced by `seam/seam_v2.py` (per eye, common rest) and `seam/seam_v3.py` (transplant -> LIF).
- `symmetrize.py` - the mirrored-hemisphere brain (`brain_sym.npz`), shelved.
