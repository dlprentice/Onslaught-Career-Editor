# Active Goal Baton

Status: **ACTIVE** (time-boxed marathon until local 10:00 tomorrow)  
Last updated: 2026-07-15  
Policy: [`goal.policy.md`](goal.policy.md)  
Campaign map: [`goal.campaign.md`](goal.campaign.md)  
Slash prompt: [`roadmap/goals/full-rebuild-campaign-slash-goal.md`](roadmap/goals/full-rebuild-campaign-slash-goal.md)  
Integration baseline: pending push (builds on `23f8cd02`)  
**STOP:** local 2026-07-15 10:00 (see implementer stop-datetime.txt)

## Closed ledger

| Slice | Result | Artifacts |
|-------|--------|-----------|
| Walker forward | landed | v2; `WalkerSpeedPerTick=100` |
| Jet thrust | landed | v1; `JetSpeedPerTick=381` |
| Look/Left yaw | landed | v1; `WalkerLookYawRateMilliRadPerTick=3` |
| Strafe Movement/Left | landed | v1; `WalkerStrafeSpeedPerTick=101` |
| **M1.5 transform morph settle dual-accept** | **landed** | xform-p03; v1; `MorphToJetSettleTicks=148` |
| Energy rate scaffold | landed (offline) | `battleengine_energy_scaffold.py` |
| Projectile speed scaffold | landed (offline) | `battleengine_projectile_speed_scaffold.py` |

## Current Slice

**ID:** `M2.2-shield-or-energy-live-or-M3-camera`  
**Lane:** RE measurement or harness  
**Objective:** Prefer live energy drain dual-accept if energy offset is
discoverable quickly; else offline shield scaffold + WinUI honesty docs, or
camera/look contract candidate from existing RE notes. No reopen closed scalars.

## Progress — time-box marathon (this session)

### ADVANCEMENT M1.5 live transform xform-p03
`--measure transform`; morph request stamp before handshake; dual-accept
latency envelope **[4670, 5170] ms**; Core `MorphToJetSettleTicks=148`.

### ADVANCEMENT energy scaffold
Pure drain/regen rate analyzer + unit tests.

### ADVANCEMENT projectile speed scaffold
Pure projectile path-speed analyzer + unit tests.

## Resume checklist
- [ ] Continue until STOP wall clock  
- [ ] Next: energy live or shield/camera harness  
