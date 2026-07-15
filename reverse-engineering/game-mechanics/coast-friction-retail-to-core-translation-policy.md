# Retail → Core translation policy (coast / friction)

Status: **draft — blocked on dual-accept**  
Depends on: coast half-life dual-accept (not landed)

## Measured retail input (pending)

Release half-life (ms for speed to fall to ≤50% of hold cruise) from path
samples after control release.

## Planned translation (not yet authorized)

| Parameter | Planned default |
|-----------|-----------------|
| Tick model | Core fixed 30 Hz |
| Map | friction / coast model TBD from half-life |
| Non-claim | Source `mWalkFriction=0.9` is not Core authority |

## Explicit non-claims

- Draft only; Core still uses instantaneous stop on input release today.
