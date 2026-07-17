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

## Observed, not implemented

The xform-p03 capture reports roughly 4.92 seconds (148 ticks at 30 Hz) from
walker morph input to its measured settle condition. That interval is retained
as an observation, not a Core constant: its start/end semantics have not been
mapped to the current transition state machine. Core's 15-tick mode lock is
synthetic and must not be described as the retail morph.

Energy regeneration, shield behavior, fire cadence, projectile motion,
coast/friction, acceleration, and camera behavior remain provisional or absent.
