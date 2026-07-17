# Campaign scalar status (human front door)

This summary is maintained directly from the accepted scalar policy documents
in this directory; retired generated status reports are available in Git
history.

## Dual-accepted → Core

| Scalar | Core constant | Pair |
|--------|---------------|------|
| Walker forward | `WalkerSpeedPerTick=100` | p27 |
| Jet forward | `JetSpeedPerTick=381` | jet-p06 |
| Walker Look/Left yaw | `WalkerLookYawRateMilliRadPerTick=3` | turn-p02 |
| Walker strafe | `WalkerStrafeSpeedPerTick=101` | strafe-p02 |
| Walker→jet morph settle | `MorphToJetSettleTicks=148` | xform-p03 |
| Jet energy drain | `JetEnergyDrainPerTick=17` | energy-p02 |

## Scaffold / offset / draft (live dual-accept pending)

| System | Offset hyp | Harness |
|--------|------------|---------|
| Walker energy regen | BE+0xFC | not dual-accepted yet (provisional Core) |
| Shield regen/drain | BE+0x100 | input-free live sampler + paired scaffold; no live pair yet |
| Fire cooldown | energy-drop edges | fire scaffold |
| Projectile speed | entity TBD | projectile scaffold |
| Coast / friction | path release half-life | coast scaffold |
| Camera look | body/camera orientation | camera look scaffold |

## Live measure modes pending dual-accept

| Mode | Vehicle | Module |
|------|---------|--------|
| shield | walker | `battleengine_shield_scaffold` |

The shield mode is wired for receipt-bound, neutral-control, input-free
observation with symmetric energy/shield correlation and input-not-owned
cleanup. This is runner readiness only, not a retail shield-rate claim.

## Offline-only harness catalog

| Mode | Module |
|------|--------|
| coast | `battleengine_coast_friction_measurement` |
| camera-look | `battleengine_camera_look_measurement` |
| fire-cooldown | `battleengine_fire_cooldown_scaffold` |
| projectile-speed | `battleengine_projectile_speed_scaffold` |

## Live prep (shield next)

- Jet energy live checklist closed (energy-p02 dual-accept).
- Next: shield dual-accept at BE+0x100 (walker).
