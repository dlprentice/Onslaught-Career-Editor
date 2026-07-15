# Projectile speed scalar plan

Status: **scaffold landed** (`tools/battleengine_projectile_speed_scaffold.py`);
live dual-accept pending  
npm: `npm run test:battleengine-projectile-speed-scaffold`

Core `ProjectileSpeedPerTick` remains provisional until dual-accept.

## Harness

- Path-speed analysis of a tracked projectile entity samples.
- `materialize_projectile_pair_envelope` for two accepted attempts.
- Nonclaims: entity tracking and dual-accept required; source defaults alone are
  not Core authority.

## Live next

1. Discover projectile entity pointer chain (separate from player BE).
2. Sample position series under fire hold / burst.
3. Dual-accept pair → contract → Core mapping.
