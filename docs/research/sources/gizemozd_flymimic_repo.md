# GitHub repo notes — gizemozd/FlyMimic (VERIFIED 2026-09-21/22)

All facts here were read from the GitHub REST API and from `raw.githubusercontent.com`
files on the `main` branch.

## Existence and metadata (GitHub API `/repos/gizemozd/FlyMimic`)

- Exists, **public**, not a fork, not archived.
- Description: "An imitation learning environment for musculoskeletal modeling of
  Drosophila melanogaster"
- Homepage: https://gizemozd.github.io/fly_mimic/
- License: **Apache-2.0** (SPDX string `Apache-2.0`; LICENSE file is the standard
  Apache License Version 2.0, January 2004 text)
- created_at 2025-08-09; pushed_at 2026-03-27; ~5 stars; default branch `main`; size ~35 MB.

## Physics engine and pins (`pyproject.toml`)

```
name = "FlyMimic", version = "0.1.0", license = Apache-2.0, requires-python >=3.10
dependencies: stable-baselines3, dm_control==1.0.30, mujoco==3.3.2, lxml,
              tensorboard, hydra-core, numpy, torch, wandb
extras: viz = matplotlib/imageio/imageio-ffmpeg ; dev = black/pytest
```
So: **MuJoCo pinned to 3.3.2, dm_control pinned to 1.0.30**; stable-baselines3 and
torch unpinned. Config is Hydra. Author email in pyproject: pgizemozdil@gmail.com.

## File layout (full `git/trees/main?recursive=1`, not truncated)

```
.gitignore  .pre-commit-config.yaml  LICENSE  README.md  pyproject.toml
docs/kr_vs_ppo.gif
flymimic/__init__.py
flymimic/assets/mocap/{qpos,qvel,xipos,xivel}/{0001.npy,0002.npy}
flymimic/assets/models/best_combined_arm_cvt3.xml
flymimic/assets/models/best_combined_arm_damping_cvt3.xml
flymimic/assets/models/best_combined_arm_damping_stiff_cvt3.xml
flymimic/assets/models/best_combined_arm_stiff_cvt3.xml
flymimic/assets/models/best_combined_cvt3.xml
flymimic/assets/models/best_combined_cvt3_torque.xml
flymimic/assets/models/meshes/stl/*.stl   (~70 STLs, whole fly body) + stl.zip
flymimic/assets/models/opensim/best_combined.osim
flymimic/assets/models/opensim/best_combined_full.osim
flymimic/assets/models/opensim/best_combined_full.pdf
flymimic/config/{eval_config,train_arm,train_arm_damp,train_arm_damp_stiff,
                 train_arm_stiff,train_torque}.yaml
flymimic/envs/dmcontrol_wrapper.py
flymimic/evaluation/evaluate_rollout.py
flymimic/tasks/fly/{__init__.py,mocap_tracking_muscle.py,mocap_tracking_torque.py}
flymimic/train/{train_muscle.py,train_torque.py}
flymimic/utils/read_tensorboard.py
logs/demo_model.zip
scripts/{eval_rollout.py,retrain_models.sh,train_muscle.py,train_one_seed.sh,
         train_seeds.sh,train_torque.py}
tests/{test_assets.py,test_play_mode_rewards.py}
```

Note: the **OpenSim `.osim` source models ship here too** (`best_combined.osim`,
`best_combined_full.osim`), despite the README pointing elsewhere for OpenSim work.

## MJCF filenames and what differs between them (VERIFIED by diffing the `<default>` joint line)

| file | joint defaults | actuators |
|---|---|---|
| `best_combined_arm_cvt3.xml` | `armature=0.0005 damping=0.0` | 15 muscle |
| `best_combined_arm_damping_cvt3.xml` | `armature=0.0005 damping=0.02` | 15 muscle |
| `best_combined_arm_stiff_cvt3.xml` | `armature=0.0005 stiffness=0.4` | 15 muscle |
| `best_combined_arm_damping_stiff_cvt3.xml` | `armature=0.0005 stiffness=0.4 damping=0.02` | 15 muscle |
| `best_combined_cvt3.xml` | `armature=0.0005 damping=0.02` | 15 muscle |
| `best_combined_cvt3_torque.xml` | `armature=0.0005 stiffness=0.4 damping=0.02` | 7 `<motor>` joint torques, `gear=0.5`, per-joint ctrlranges |

"cvt3" presumably = converted, 3-DoF CTr. The four `arm_*` files are exactly the
passive-property ablation of paper Figure 5.

## MJCF header / engine settings (`best_combined_arm_damping_stiff_cvt3.xml`)

```xml
<mujoco model="template">
  <!-- This model has been converted from an OpenSim model. Model conversion by
       MyoConverter https://github.com/MyoHub/myoconverter. This model is licensed
       under Apache 2.0. -->
  <compiler angle="radian" autolimits="true"/>
  <option timestep="1e-04" gravity="0 0 -9801"/>
  <size njmax="1000" nconmax="400" nkey="1" nuser_jnt="1"/>
```
Gravity `-9801` ⇒ length unit is **mm** (mesh `scale="1000 1000 1000"` on the STLs).
Muscle default class:
```xml
<default class="muscle">
  <general ctrllimited="true" ctrlrange="0 1"
           dyntype="muscle" gaintype="muscle" biastype="muscle"
           dynprm="0.01 0.04 0 0 0 0 0 0 0 0"
           gainprm="0.75 1.05 -1 200 0.5 1.6 1.5 1.3 1.2 0"
           biasprm="0.75 1.05 -1 200 0.5 1.6 1.5 1.3 1.2 0"/>
</default>
```
⇒ **native MuJoCo Hill-type muscle actuators confirmed.**

## Only ONE leg is muscled (VERIFIED)

All 15 actuators and all 15 spatial tendons carry the `LF` (left front) prefix. The
right foreleg has joints but they are welded shut by `<equality>` joint constraints
named `joint_RF*_locked` with `polycoef="0 0 0 0 0"`. Mid/hind legs and wings are
present as rigid mesh bodies with no joints at all. The whole-body STL set is
NeuroMechFly's, but only the left foreleg moves.

## Gym env and default controller (VERIFIED by reading the code)

- `flymimic/envs/dmcontrol_wrapper.py` defines `DMControlGymWrapper(gym.Env)` —
  a **gymnasium** wrapper around a dm_control env, flattening the obs dict to a Box.
  So: dm_control task + thin Gym adapter, not a standalone Gym env package.
- `flymimic/tasks/fly/mocap_tracking_muscle.py` — `MoCapTask(base.Task)` with a
  `Physics` subclass exposing `qpos`, `qvel` (÷10, clipped ±10), `xpos`,
  `femur_loc`/`tibia_loc`/`tarsus_loc`/`claw_loc` (LFFemur, LFTibia, LFTarsus1,
  LFTarsus5), `muscle_lengths` (`data.actuator_length`), `muscle_velocities`
  (`data.actuator_velocity`, clipped ±100), `muscle_activations` (`data.act`),
  `muscle_forces` (`data.actuator_force`/1000, clipped ±10). Defaults
  `joint_ids=[0..6]`, `body_ids=[21,22,23,27]`.
- `mocap_tracking_torque.py` is the torque-actuated counterpart.
- Default controller: **PPO from Stable-Baselines3** (`train_muscle.py` /
  `train_torque.py`, Hydra configs). Example config `train_arm_damp_stiff.yaml`:
  `tot_ts: 30000000`, `xml_name: best_combined_arm_damping_stiff_cvt3`,
  ReLU policy, `learning_rate: 1e-5`, `n_steps: 2048`, `batch_size: 64`,
  `n_epochs: 10`, eval every 5000 steps over 20 episodes.
  (Note the config says 30M total timesteps while the paper reports 15M — recorded as found.)
- `logs/demo_model.zip` (~10 MB) is a shipped pretrained policy; further trained models
  are on Dropbox per the README.

## README highlights

- States the repo covers **only the imitation-learning experiments** and ships
  "MuJoCo models converted from OpenSim". For "the original muscle model development
  and parameter optimization in OpenSim" it points to
  **https://github.com/gizemozd/neuromechfly-muscles**.
  → **That repo 404s** (checked `gizemozd/neuromechfly-muscles`,
  `NeLy-EPFL/neuromechfly-muscles`, `NeLy-EPFL/NeuroMechFly-muscles`: all "Not Found").
  It is private or was never published. The OpenSim development code is therefore
  **not publicly available**; only the resulting `.osim` files are, inside FlyMimic.
- BibTeX in README:
  ```
  @inproceedings{ozdil2026musculoskeletal,
    title={Musculoskeletal simulation of limb movement biomechanics in Drosophila melanogaster},
    author={Ozdil, Pembe Gizem and Ning, Chuanfang and Phelps, Jasper S and
            Wang-Chen, Sibo and Elisha, Guy and Ijspeert, Auke and Ramdya, Pavan},
    booktitle={The Fourteenth International Conference on Learning Representations},
    year={2026}
  }
  ```
  (7 authors — Blanke omitted relative to arXiv v2.)
- Install: conda python=3.10, `pip install -e .`. Quick start
  `python scripts/train_muscle.py`, `python scripts/eval_rollout.py`.

## Related repos by the same author (GitHub API)

- `gizemozd/fly_mimic` — created 2026-02-23, no description, no license: the GitHub
  Pages source for the project website.
- `gizemozd/myoconverter` — a fork/copy of MyoHub's MyoConverter (Apache-2.0).
- `gizemozd/neuromechfly-muscles` — **does not exist publicly**.
