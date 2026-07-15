# Retail → Core translation policy (energy drain/regen)

Status: **draft — blocked on dual-accept**  
Depends on: energy rate dual-accept (not landed)

## Measured retail input (pending)

Jet thrust-hold drain and/or walker ground regen rates from receipt-bound
`--measure energy` pairs. Offset hypothesis: `BattleEngine+0xFC` float.

## Planned translation (not yet authorized)

| Parameter | Planned default |
|-----------|-----------------|
| Tick model | Core fixed 30 Hz |
| Map | \( e_\mathrm{tick} = \mathrm{round}(r_\mathrm{retail} \cdot s / 30) \) with scale \(s\) TBD |
| Core candidates | `JetEnergyDrainPerTick`, `WalkerEnergyRegenerationPerTick` |

## Explicit non-claims

- This draft does **not** authorize changing Core energy constants.
- Source config defaults (`mEnergy=2.5`, regen `0.01`, air costs) are not dual-accepted retail rates.
- Offset `0xFC` is steam-static hypothesis until live drain/regen correlation.

## Checklist

1. [ ] Live dual-accept pair (jet drain preferred)
2. [ ] Public v1 JSON contract
3. [ ] Accept this policy
4. [ ] Map Core constants + goldens/tests
