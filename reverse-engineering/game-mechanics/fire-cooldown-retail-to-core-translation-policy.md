# Retail → Core translation policy (fire cooldown)

Status: **draft — blocked on dual-accept**  
Depends on: fire cooldown dual-accept (not landed)

## Measured retail input (pending)

Median inter-fire interval under receipt-bound fire hold, preferably via energy
drop edges at `BattleEngine+0xFC` and/or projectile spawn edges.

## Planned translation (not yet authorized)

| Parameter | Planned default |
|-----------|-----------------|
| Tick model | Core fixed 30 Hz |
| Map | \( t = \mathrm{round}(\mathrm{ms} \cdot 30 / 1000) \) |
| Core candidate | `FireCooldownTicks` |

## Explicit non-claims

- Draft only; no Core constant change authorized.
- Source/default `FireCooldownTicks=6` is not dual-accepted retail truth.
