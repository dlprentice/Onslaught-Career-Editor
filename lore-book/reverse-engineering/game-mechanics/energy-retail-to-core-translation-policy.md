# Retail → Core translation policy (energy drain/regen)

Status: **partial — jet drain accepted; walker regen still provisional**  
Jet drain: see [jet-energy-drain-retail-to-core-translation-policy.md](jet-energy-drain-retail-to-core-translation-policy.md)  
Depends on: [jet-energy-drain-scalar-response-v1.md](jet-energy-drain-scalar-response-v1.md)

## Jet drain (accepted)

| Parameter | Value |
|-----------|-------|
| Dual-accept | pair `energy-p02` |
| Mid rate | ≈ −0.5169 retail energy units/s |
| Core | `JetEnergyDrainPerTick = 17` (milli-energy @ 30 Hz) |

## Walker regen (provisional)

Not measured by energy-p02. `WalkerEnergyRegenerationPerTick` stays provisional.
Do **not** invent from source `mGroundEnergyIncrease=0.01`.

## Offset

`BattleEngine+0xFC` remains the working energy float hypothesis, now
dual-accept-correlated for jet thrust drain only.
