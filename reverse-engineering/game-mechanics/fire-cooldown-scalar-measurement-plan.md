# Fire cooldown scalar (M2.1) — scaffold landed

Status: **scaffold landed** (offline unit-tested); live dual-accept pending  
Tools: `tools/battleengine_fire_cooldown_scaffold.py`  
Tests: `tools/battleengine_fire_cooldown_scaffold_test.py`  
npm: `npm run test:battleengine-fire-cooldown-scaffold`

Analyzes inter-fire intervals from ordered fire-edge ticks. Does **not**
authorize Core `FireCooldownTicks` from source defaults alone.

## Energy-drop edge detector

`fire_edges_from_energy_drops((tick, energy)…)` converts a receipt-bound
`BattleEngine+0xFC` series into fire edges when energy drops by ≥ `min_drop`.
This is the preferred live correlation once a fire-hold input path exists
(Space/fire is not yet in the Q-only pair runner).

## Live dual-accept plan

1. Bind fire input under receipt-bound pair (new measure mode or secondary key).
2. Sample energy at 0xFC (and optional projectile spawn if discovered).
3. Two-attempt median inter-fire ms envelope → contract → Core.
