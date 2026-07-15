# Campaign scalar status (human front door)

Machine report: `npm run report:battleengine-campaign-scalar-status`

## Dual-accepted → Core

| Scalar | Core constant | Pair |
|--------|---------------|------|
| Walker forward | `WalkerSpeedPerTick=100` | p27 |
| Jet forward | `JetSpeedPerTick=381` | jet-p06 |
| Walker Look/Left yaw | `WalkerLookYawRateMilliRadPerTick=3` | turn-p02 |
| Walker strafe | `WalkerStrafeSpeedPerTick=101` | strafe-p02 |
| Walker→jet morph settle | `MorphToJetSettleTicks=148` | xform-p03 |

## Scaffold / offset / draft (live dual-accept pending)

| System | Offset hyp | Harness |
|--------|------------|---------|
| Energy drain/regen | BE+0xFC | `measure=energy` + energy scaffold |
| Shield regen/drain | BE+0x100 | shield scaffold |
| Fire cooldown | energy-drop edges | fire scaffold |
| Projectile speed | entity TBD | projectile scaffold |
| Coast / friction | path release half-life | coast scaffold |
| Camera look | body/camera orientation | camera look scaffold |

## Offline harness catalog (not MEASURE_MODES yet)

Machine: `tools/battleengine_measure_mode_catalog.py` → `OFFLINE_HARNESS_ROWS`

| Mode | Module |
|------|--------|
| coast | `battleengine_coast_friction_measurement` |
| camera-look | `battleengine_camera_look_measurement` |
| fire-cooldown | `battleengine_fire_cooldown_scaffold` |
| projectile-speed | `battleengine_projectile_speed_scaffold` |
| shield-rate | `battleengine_shield_scaffold` |

## Live prep

- Public checklist: [energy-live-dual-accept-checklist.md](energy-live-dual-accept-checklist.md)
- Copied profile (ignored): `GameProfiles/marathon-energy-jet-01`
- Private readiness: `local-proofs/wt/energy-live-readiness.md`
