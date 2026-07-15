# Fire cooldown scalar (M2.1) — scaffold landed

Status: **scaffold landed** (offline unit-tested); live dual-accept pending  
Tools: `tools/battleengine_fire_cooldown_scaffold.py`  
Tests: `tools/battleengine_fire_cooldown_scaffold_test.py`

Analyzes inter-fire intervals from ordered fire-edge ticks. Does **not**
authorize Core `FireCooldownTicks` from source defaults alone.
