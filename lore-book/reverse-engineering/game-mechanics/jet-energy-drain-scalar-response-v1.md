# Jet energy drain scalar response v1

Status: **dual-accepted** (pair `energy-p02`, 2026-07-14)  
Schema: `battleengine-jet-energy-drain-scalar-response.v1`  
JSON: [jet-energy-drain-scalar-response-v1.json](jet-energy-drain-scalar-response-v1.json)

## Claim

Under receipt-bound jet thrust hold (pair runner `--measure energy --vehicle jet`),
the hypothesized `BattleEngine+0xFC` float shows a **negative** steady energy
rate (drain). Two fresh accepted attempts form a stable envelope.

| Attempt | Steady rate (energy units/s) | Receipt (prefix) |
|---------|------------------------------|------------------|
| 1 | −0.4972 | `554f0f00…` |
| 2 | −0.5366 | `6ac3473d…` |
| Envelope | [−0.5625, −0.4713] | — |

## Method

- Level 850 / configuration 2 safe-copy launch; morph to jet; Q thrust hold.
- Sample BE+0xFC at ~10 ms QPC polls during hold; analyze with
  `tools/battleengine_energy_scaffold.py` (`expect_negative=True`).
- Pair envelope via `materialize_energy_pair_envelope`.

## Non-claims

See JSON `nonclaims`. Walker regen was **not** measured in this pair.
