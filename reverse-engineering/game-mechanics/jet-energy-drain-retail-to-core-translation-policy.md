# Retail → Core translation policy (jet energy drain)

Status: **accepted (2026-07-14) for the retail measurement; SUPERSEDED 2026-07-28
for the Core mapping**  
Depends on: [jet-energy-drain-scalar-response-v1.md](jet-energy-drain-scalar-response-v1.md)

> **SUPERSEDED 2026-07-28 — the Core mapping only.** The Status line above
> previously read `Status: **accepted** (2026-07-14)` with nothing else.
> `JetEnergyDrainPerTick` no longer exists in
> `rebuild/OnslaughtRebuild.Core/`; a flat scalar was replaced by the
> thruster-interpolated pair
> `JetMinimumEnergyDrainMicroPerRetailTick = 5_000` /
> `JetMaximumEnergyDrainMicroPerRetailTick = 12_000`
> (`SimulationConstants.cs:346-377`), read from the shipped
> `mMinAirEnergyCost 0.005` / `mMaxAirEnergyCost 0.012` bytes. **The retail
> `energy-p02` measurement below is not withdrawn** and remains this document's
> point.

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

~~`WalkerEnergyRegenerationPerTick` remains provisional until a dual-accepted
walker regen measurement lands.~~

**SUPERSEDED 2026-07-28.** That sentence is quoted above rather than deleted. It
is no longer true: Core carries `WalkerEnergyRegenerationPerTick = 33`
(`rebuild/OnslaughtRebuild.Core/SimulationConstants.cs:318-345`), derived from
`references/Onslaught/BattleEngineWalkerPart.cpp:374-388` and the shipped byte
`mGroundEnergyIncrease 0.05` (record 3 "Aquila Prototype" @`0x2d2` of
`data/battle engine configurations.dat`, SHA-256 `58722b12…`, 1,514 bytes) — a
shipped-data derivation, not a dual-accepted runtime measurement. See
[`energy-retail-to-core-translation-policy.md`](energy-retail-to-core-translation-policy.md),
corrected the same day. The Core authorization above for
`JetEnergyDrainPerTick` is likewise superseded; see the block under the Status
line at the head of this document.

## Acceptance checklist

1. [x] Policy marked **accepted**
2. [x] v1 dual-accept is authority for retail drain numbers
3. [x] Source `mEnergy` / air-cost defaults rejected as Core authority
   — **scoped 2026-07-28:** this rejects the `CBattleEngineData::Initialise()`
   defaults (`BattleEngineDataManager.cpp:30`, air costs `0.1`/`0.3` at
   `:77-78`). It does **not** reject the *shipped* air-cost bytes
   (`0.005`/`0.012`), which are what Core now reads and which outrank both this
   pair and the source defaults.
4. [x] No claim that Core re-proves retail
