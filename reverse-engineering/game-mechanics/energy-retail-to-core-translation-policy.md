# Retail → Core translation policy (energy drain/regen)

Status: **SUPERSEDED 2026-07-28 for both halves of the Core mapping** — the
retail `energy-p02` measurement stands; walker regen is no longer provisional.
Jet drain: see [jet-energy-drain-retail-to-core-translation-policy.md](jet-energy-drain-retail-to-core-translation-policy.md).
Depends on: [jet-energy-drain-scalar-response-v1.md](jet-energy-drain-scalar-response-v1.md)

> **SUPERSEDED 2026-07-28.** The Status line above previously read, in full:
>
> > Status: **partial — jet drain accepted; walker regen still provisional**
>
> Both halves of that are now overtaken, and the walker half had become actively
> misleading. Details in the two sections below; the old text is kept in place.

## Jet drain (accepted)

| Parameter | Value |
|-----------|-------|
| Dual-accept | pair `energy-p02` |
| Mid rate | ≈ −0.5169 retail energy units/s |
| ~~Core~~ | ~~`JetEnergyDrainPerTick = 17` (milli-energy @ 30 Hz)~~ — **SUPERSEDED 2026-07-28** |
| Core | `JetMinimumEnergyDrainMicroPerRetailTick = 5_000` / `JetMaximumEnergyDrainMicroPerRetailTick = 12_000` (`rebuild/OnslaughtRebuild.Core/SimulationConstants.cs:346-377`) |

**SUPERSEDED 2026-07-28 — the Core row only.** The struck row previously read
`JetEnergyDrainPerTick = 17` unqualified.
`grep -rn 'JetEnergyDrainPerTick' rebuild/OnslaughtRebuild.Core/` returns
nothing. A flat scalar was replaced by a thruster-interpolated envelope, read from
the shipped bytes `mMinAirEnergyCost 0.005` / `mMaxAirEnergyCost 0.012` in record
3 "Aquila Prototype" @`0x2d2` of `data/battle engine configurations.dat`
(SHA-256 `58722b12…`, 1,514 bytes). **The retail measurement is unaffected:**
the `energy-p02` dual-accept and its ≈ −0.5169 units/s mid rate stand, and this
document remains the record of them.

## Walker regen (provisional)

> **SUPERSEDED 2026-07-28.** This section previously read, in full:
>
> > Not measured by energy-p02. `WalkerEnergyRegenerationPerTick` stays provisional.
> > Do **not** invent from source `mGroundEnergyIncrease=0.01`.
>
> Two things were wrong with that, in opposite directions.

**Walker regen is no longer provisional.** Core carries
`WalkerEnergyRegenerationPerTick = 33`
(`rebuild/OnslaughtRebuild.Core/SimulationConstants.cs:318-345`), landed under
task #126. It is derived from `references/Onslaught/BattleEngineWalkerPart.cpp:374-388`
(the ground-recharge arm of `CBattleEngineWalkerPart::Move`) together with the
**shipped byte** `mGroundEnergyIncrease = 0.05` at record 3 "Aquila Prototype"
@`0x2d2` of `data/battle engine configurations.dat`
(SHA-256 `58722b12a04cae97ad2163acb2cc2c1699f95a0688318bd8a86696714d94454a`,
1,514 bytes; re-hashed 2026-07-28). The conversion is
`0.05 × 1000 × 20/30 = 33` per Core tick.

**The old prohibition named the wrong number.** `mGroundEnergyIncrease = 0.01f`
is the **constructor default** — `references/Onslaught/BattleEngineDataManager.cpp:76`,
inside `CBattleEngineData::Initialise()` — not a value the shipped data ever
carries for this vehicle. Read literally, "do not invent from source
`mGroundEnergyIncrease=0.01`" forbade exactly the byte-backed derivation Core now
uses, while quoting a figure retail does not use.

**The prohibition is narrowed, not withdrawn.** It stands against the
`Initialise()` default and against any source constant used *in place of* a
shipped byte. It never applied to reading the shipped record itself, which is a
stronger authority than either.

## Offset

`BattleEngine+0xFC` remains the working energy float hypothesis, now
dual-accept-correlated for jet thrust drain only.
