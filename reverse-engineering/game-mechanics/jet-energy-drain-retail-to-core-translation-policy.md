# Retail → Core translation policy (jet energy drain)

Status: **accepted** (2026-07-14)  
Depends on: [jet-energy-drain-scalar-response-v1.md](jet-energy-drain-scalar-response-v1.md)

## Purpose

Separate measured retail jet energy drain rate from deterministic Core
`JetEnergyDrainPerTick`. Core agreement does **not** re-prove retail.

## Measured retail quantities

From `battleengine-jet-energy-drain-scalar-response.v1` (pair `energy-p02`):

- Steady energy rate \( r \in [-0.5625, -0.4713] \) retail energy units / second
  (negative = drain; mid ≈ **−0.5169** u/s)
- Store: hypothesized `BattleEngine+0xFC` float under jet thrust hold

## Translation parameters

| Parameter | Accepted default | Notes |
|-----------|------------------|-------|
| Energy unit | Core integer **milli-energy** units: \(1000\) Core = \(1\) retail energy unit | Same milli convention as motion policies |
| Tick model | Core fixed \(30\) Hz | Core-local |
| Drain map | \( d_\mathrm{tick} = \mathrm{round}(\lvert r \rvert \cdot 1000 / 30) \) | For mid \(\lvert r \rvert \approx 0.5169\): **17** |
| Envelope band | \( d_\mathrm{tick} \in [16, 19] \) for \(\lvert r \rvert \in [0.4713, 0.5625]\) | Accepted default **17** |
| Walker regen | **not mapped** | This pair is jet drain only |

## Core authorization

With status **accepted**, deterministic Core may set
`JetEnergyDrainPerTick = 17` (milli-energy units at 30 Hz ≈ 0.51 retail
energy units/s), citing this policy and schema
`battleengine-jet-energy-drain-scalar-response.v1`.

`WalkerEnergyRegenerationPerTick` remains provisional until a dual-accepted
walker regen measurement lands.

## Acceptance checklist

1. [x] Policy marked **accepted**
2. [x] v1 dual-accept is authority for retail drain numbers
3. [x] Source `mEnergy` / air-cost defaults rejected as Core authority
4. [x] No claim that Core re-proves retail
