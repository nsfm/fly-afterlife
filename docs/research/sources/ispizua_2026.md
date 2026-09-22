# Ispizua et al. 2026 — whole-body 3D kinematics

**Citation.** Ispizua JI, Abe ETT, Yan J, Othayoth R, Sawtelle S, Atkins F, Shiozaki HM, Meier NR, Wong J, Tran T, Mori C, Voigts J, Stern DL, Brunton BW, Tuthill JC, Johnson RE (2026). "Whole-body 3D kinematics of freely behaving *Drosophila*." bioRxiv, posted 2026-05-04. DOI 10.64898/2026.05.03.722293. PMID 42146626.
URL: https://www.biorxiv.org/content/10.64898/2026.05.03.722293v2
Author list VERIFIED against the NCBI record.

Extraction: automated reads of the v1 and v2 full texts **[V-fetch]**.

## Method
- **Seven synchronised high-speed cameras with telecentric lenses at 800 fps.**
- Hybrid 2D/3D deep network tracking **50 keypoints** (legs, wings, head, thorax, abdomen; all leg joints except the middle/hind leg coxa-thorax joint), refined by an inverse-kinematics retarget onto a biomechanical body model.
- Tracking accuracy: **2.02 ± 1.04 pixels (24.8 ± 12.8 µm)** in v1; v2 quotes mean error **18.2 ± 8.5 µm**, ≈2–3% of femur length (**femur ≈ 0.72 mm**).
- Dataset: v1 reports 22 flies (13M, 9F) and 372 running bouts (~135,000 frame-sets); **v2 reports 53 flies and 2,213 running bouts (~654,000 frame-sets)**. Courtship: 11 pairs.

## The locomotion claim
- **Flies perform "grounded running" across their full speed range, without transitioning between discrete gaits.**
- Evidence: **"height and speed peaked in phase, at both alternating tripod peaks, across the full range of locomotor speeds"** — in-phase CoM height and forward speed is the running signature; walking would have them out of phase.
- **"no 'floating' phase where all leg tips are suspended off the ground"** — hence *grounded* running.
- "Both the mean phase and distribution width remain fairly unchanged across speed tertiles."
- Speed: **up to 40 mm/s**, with **stepping frequencies exceeding 20 Hz**.
- Coordination: tripod grouping (L1/R2/L3 and R1/L2/R3) more stereotyped at high speed; at low speed "trajectories became less regular and phase offsets were more variable"; hind legs show weaker coupling at low speeds.

## Courtship (incidental)
Male modulates body pitch to track the female's vertical position, with a **median angular offset of 23.2°**.

## Data
- Curated 3D kinematics dataset: link given in the preprint as **https://bit.ly/3UWoXBF**
- Code: https://github.com/elliottabe/3d_tracking_ik , https://github.com/elliottabe/3d_tracking_dataset , https://github.com/moments-behavior

## Could not verify
Duty-factor values, stance/swing durations in ms, per-joint angle ranges in degrees, numeric leg phase offsets, body pitch/roll ranges, and the dataset licence. Figure 2c holds the joint-angle distributions but the numbers are not printed in the text. **Worth a direct PDF read** — this is the newest and largest fly kinematics dataset and would settle several open items in `C_kinematics.md`.
