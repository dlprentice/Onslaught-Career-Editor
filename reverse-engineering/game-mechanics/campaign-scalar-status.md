# Retail scalar status

This is the small implementation-facing summary. Retail observation remains
authority; Core agreement does not re-prove retail.

## Mapped into Core

| Scalar | Core constant | Evidence |
| --- | --- | --- |
| Level 100 walker translation | acceleration `33`, retention `0.7884`, cap `100` milli-units/tick | clean control + two fresh repeats |
| Jet forward | `JetSpeedPerTick = 381` | jet-p06 |
| Level 100 walker body yaw | input `10,444` micro-rad/tick, retention `0.861774` | clean control + two fresh repeats |
| Jet energy drain | `JetEnergyDrainPerTick = 17` | energy-p02 |
| Walker-to-jet raw state interval | `WalkerToJetTransitionTicks = 16` | Level 100 control + two repeats |

## Level 100 walker observation

The canonical Steam specimen
`74154BFAE14DDC8ECB87A0766F5BC381C7B7F1AB334ED7A753040EDA1E1E7750`
was resolved through AppCore into fresh owned copies. Each launched only with
`-res 1600 900 -skipfmv -level 100`; Forward, Movement/Left, and Look/Left were
written to the copied `defaultoptions.bea`. The observer waited for Level 100's
own `player.Activate()` rather than bypassing the training script.

A no-input control remained stationary. Two uninterrupted 2 ms read-only runs
then repeated the same stable 20 Hz updates:

- Input-to-first-update initiation was 18-35 ms across Forward, Movement/Left,
  and Look/Left in the two phase-offset runs.
- Forward and strafe speed: `0 -> 0.07 -> 0.119 -> 0.15` retail units/update.
- Released translation: each stable value was exactly `previous * 0.7`.
- Look input added `0.0226667` rad before each yaw integration.
- Released yaw velocity was exactly `previous * 0.8`; held body turning tends
  toward about `2.2667` rad/s.

Steam RVA `+0x4a9d3c` supplies the player-one root, whose `+0x1c` member is the
active BattleEngine. The released chain identifies BattleEngine position at
`+0x1c/+0x20/+0x24`, velocity at `+0x7c/+0x80/+0x84`, body yaw at `+0x114`,
raw state at `+0x260`, and yaw velocity at `+0x278`; raw walker state is `2`.
Retail bodies at `0x00412d80`, `0x00413160`, `0x00413760`, and `0x00407a50`
match the observed forward/strafe injection, cap/friction, yaw integration, and
decay order. Stuart's `BattleEngineWalkerPart.cpp` and `BattleEngine.cpp`
corroborate that architecture.

Core keeps the observed 3.0-unit/s cap and maps the 20 Hz retention factors to
30 Hz as `0.7^(2/3)` and `0.8^(2/3)`. This establishes one flat-ground Level
100 handling slice, not terrain response, dash behavior, camera parity, jet
handling, or a universal configuration profile.

The same clean Level 100 start held yaw `0.509829998` and horizontal forward
column `(-0.488029, 0.872827)` across five uninterrupted samples. Steam
`CBattleEngineWalkerPart__Forward` (`0x00412d80`) and
`CBattleEngineWalkerPart__StrafeLeft` (`0x00413160`) build their velocity
vectors from the current yaw before adding them to the Battle Engine. Core now
uses that continuous local-to-world basis with integer fixed-point trig; its
first authored-start forward acceleration is `(-16, 29)` milli-units/tick.
Analog input response, diagonals, dash behavior, and jet movement remain outside
this bounded mapping.

## Observed, not implemented

Jet-to-walker timing and the relationship between raw state changes, visual
animation, and camera/control settling have not been measured. The retired
xform-p03 148-tick conversion used unmatched endpoints and is not a Core
constant.

At the Level 100 authored start, repeated copied-runtime input establishes the
walker's `1/117`-radian vertical input, `0.8` pitch-velocity retention, and
absolute held-input endpoints `+0.5321228` and `-1.0911411..-1.0912496`. The
same BattleEngine yaw/pitch predicts two player-owned Pulse Cannon unit vectors
within `0.00119` per component. Core consumes this bounded attached-view aim;
terrain-relative pitch limits, mouse scaling, emitter origin, auto-aim, and
vertical target collision remain absent. Energy regeneration, shield behavior,
and non-Level-100 movement configurations remain provisional or absent.
