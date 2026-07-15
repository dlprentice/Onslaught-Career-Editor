# Energy drain/regen scalar plan

Status: **jet drain dual-accepted** (pair `energy-p02`); walker regen still pending  
Public contract: [jet-energy-drain-scalar-response-v1.md](jet-energy-drain-scalar-response-v1.md)  
Policy: [jet-energy-drain-retail-to-core-translation-policy.md](jet-energy-drain-retail-to-core-translation-policy.md)

## Steam-static current-energy offset

| Field | Candidate offset | Evidence class |
|-------|------------------|----------------|
| Current energy float | `BattleEngine+0xFC` | Steam static + dual-accept jet drain correlation |

## Sampler / harness

| Item | Path |
|------|------|
| Offsets | `BATTLE_ENGINE_ENERGY_OFFSET = 0xFC` |
| Offline analysis | `tools/battleengine_energy_scaffold.py` |
| Live measure | `--measure energy --vehicle jet` |
| Dual-accept | pair `energy-p02` under `local-proofs/wt/` (private) |

## Core

- `JetEnergyDrainPerTick = 17` (accepted)
- `WalkerEnergyRegenerationPerTick` remains provisional
