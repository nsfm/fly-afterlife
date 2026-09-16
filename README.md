# fly-afterlife

a whole male fruit fly CNS (MaleCNS v1.0, janelia + google, released 2026-09-03,
CC-BY 4.0), running as a leaky integrate-and-fire network on this laptop.
162,517 neurons, 6.1M connections at weight>=5. the fly fits in 29MB.

## what's here

- `data/` - the three feather files the sim needs (1.1GB; the other 22GB of the
  release is per-synapse coordinates, anatomy not dynamics). not committed.
- `brain_whole.npz` - our build of the whole CNS from those files
  (`ref/flybrain/scripts/build_creature.py --whole`). not committed.
- `ref/flybrain` - TheMrRaGe's LIF engine + 1600-line FINDINGS.md. read the
  findings before touching parameters; every trap in there cost someone a day.
- `ref/Drosophila_brain_model` - shiu et al. 2024 (nature), the source of the
  membrane/synapse constants.
- `ref/doomfly` - the one that went viral. for reference on how others wired i/o.
- `smoke.py` - sugar vs bitter on the tongue, read the proboscis motor neurons.

## smoke result (2026-09-15)

loads in 1.2s. 500ms of brain time runs in 0.7s on CPU (0.7x real time).

| motor neuron | base | sweet | bitter |
|---|---|---|---|
| MN9 (rostrum protractor, "proboscis out") | 1 | 92 | 0 |
| MN11D/V (pharyngeal pump) | 0 | 154 / 96 | 0 |
| MN10, MN4b | 0 | 102 / 108 | 0 |

sugar -> proboscis extension + pumping; bitter -> nothing. matches shiu et al.

## io surface (what we can wire a situation to)

in: 53 olfactory receptor types (odours are defined over TYPES, not cells),
sweet/bitter gustatory sets, mechano, thermo, hygro, 1,348 photoreceptor
cartridges (crude luminance only - T4/T5 motion is dark in this model),
dopamine reward (PAM, 316 cells) / punishment (PPL1, 24 cells) by compartment.

out: 1,310 descending neurons (480 types; DNa family = steering, DNp01 =
giant fiber escape), 107 head motor neurons (proboscis, pharynx), 708 VNC
motor neurons (legs, wings).

learning: 33,496 KC->MBON synapses, dopamine-gated depression. verified in
FINDINGS.md to reach the descending neurons and the motor neurons.
