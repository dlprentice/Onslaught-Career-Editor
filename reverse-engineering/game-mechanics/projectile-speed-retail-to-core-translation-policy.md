# Retail → Core translation policy (projectile speed)

Status: **draft — blocked on dual-accept**  
Depends on: projectile path-speed dual-accept (not landed)

## Measured retail input (pending)

Steady projectile path speed from tracked entity samples under fire.

## Planned translation (not yet authorized)

| Parameter | Planned default |
|-----------|-----------------|
| Tick model | Core fixed 30 Hz |
| Map | milli-retail units/tick like walker/jet speeds |
| Core candidate | `ProjectileSpeedPerTick` |

## Explicit non-claims

- Draft only; no Core constant change authorized.
- Source/default projectile speed is not dual-accepted retail truth.
- Entity pointer chain not yet sampler-wired.
