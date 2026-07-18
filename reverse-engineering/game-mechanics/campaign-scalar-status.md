# Retail scalar status

This is the small implementation-facing summary. The owning measurement and
translation documents in this directory retain provenance and uncertainty.

## Mapped into Core

| Scalar | Core constant | Accepted pair |
| --- | --- | --- |
| Walker forward | `WalkerSpeedPerTick = 100` | p27 |
| Jet forward | `JetSpeedPerTick = 381` | jet-p06 |
| Walker body yaw | `WalkerLookYawRateMilliRadPerTick = 3` | turn-p02 |
| Walker strafe | `WalkerStrafeSpeedPerTick = 101` | strafe-p02 |
| Jet energy drain | `JetEnergyDrainPerTick = 17` | energy-p02 |
| Walker-to-jet raw state interval | `WalkerToJetTransitionTicks = 16` | Level 100 control + two repeats |

## Observed, not implemented

Jet-to-walker timing and the relationship between raw state changes, visual
animation, and camera/control settling have not been measured. The retired
xform-p03 148-tick conversion used unmatched endpoints and is not a Core
constant.

Energy regeneration, shield behavior, fire cadence, projectile motion,
coast/friction, acceleration, and camera behavior remain provisional or absent.
