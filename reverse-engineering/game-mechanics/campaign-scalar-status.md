# Retail scalar status

This is the small implementation-facing summary. Retail observation remains
authority; Core agreement does not re-prove retail.

## Mapped into Core

| Scalar | Core constant | Evidence |
| --- | --- | --- |
| Level 100 walker translation | acceleration `33`, retention `0.7884`, cap `100` milli-units/tick | clean control + two fresh repeats |
| ~~Jet forward~~ | ~~`JetSpeedPerTick = 381`~~ | ~~jet-p06~~ — **SUPERSEDED 2026-07-28, see below** |
| Jet forward (envelope) | `JetMinimumSpeedPerTick = 200` / `JetMaximumSpeedPerTick = 600` | shipped bytes — `SimulationConstants.cs:125-129` |
| Level 100 walker body yaw | input `10,444` micro-rad/tick, retention `0.861774` | clean control + two fresh repeats |
| ~~Jet energy drain~~ | ~~`JetEnergyDrainPerTick = 17`~~ | ~~energy-p02~~ — **SUPERSEDED 2026-07-28, see below** |
| Jet energy drain (envelope) | `JetMinimumEnergyDrainMicroPerRetailTick = 5_000` / `JetMaximumEnergyDrainMicroPerRetailTick = 12_000` | shipped bytes — `SimulationConstants.cs:346-377` |
| Walker energy regeneration | `WalkerEnergyRegenerationPerTick = 33` | shipped byte + source — `SimulationConstants.cs:318-345` |
| Walker-to-jet raw state interval | `WalkerToJetTransitionTicks = 16` | Level 100 control + two repeats |

**SUPERSEDED 2026-07-28 — two of these constants no longer exist in Core, and the
model changed shape, not merely value.** The two struck rows above previously
read, unqualified:

> | Jet forward | `JetSpeedPerTick = 381` | jet-p06 |
> | Jet energy drain | `JetEnergyDrainPerTick = 17` | energy-p02 |

`grep -rn 'JetSpeedPerTick\|JetEnergyDrainPerTick' rebuild/OnslaughtRebuild.Core/`
returns nothing. Both symbols survive only in a stale build-output copy under
`rebuild/OnslaughtRebuild.Core.Tests/bin/Release/net8.0/core-source/`, which is
an artefact and not the tree.

What replaced them, and why the change is substantive:

- A single flat scalar became a **thruster-interpolated envelope**. Jet speed is
  now two ends, `200`/`600`, from `mMinAirVelocity 0.3` / `mMaxAirVelocity 0.9`
  (`rebuild/OnslaughtRebuild.Core/SimulationConstants.cs:125-129`). Jet energy
  drain is likewise two ends, `5_000`/`12_000` micro-retail per retail tick, from
  `mMinAirEnergyCost 0.005` (`0x3BA3D70A`) / `mMaxAirEnergyCost 0.012`
  (`0x3C449BA6`), interpolated by thruster value (`SimulationConstants.cs:346-377`).
- **The authority moved.** `jet-p06` and `energy-p02` are copied-runtime pairs
  taken at level 850. The replacements are read out of shipped data: record 3
  "Aquila Prototype" @`0x2d2` of `data/battle engine configurations.dat`,
  SHA-256 `58722b12a04cae97ad2163acb2cc2c1699f95a0688318bd8a86696714d94454a`,
  1,514 bytes (re-hashed for this correction on 2026-07-28 against
  `local-lab/safe-copy-bea-pristine/data/`).

**Unchanged by this correction:** the three walker rows and the transition row
all still verify against the current tree — `WalkerAccelerationPerTick = 33`
(`:52`), `WalkerVelocityRetentionNumerator = 7_884` (`:53`),
`WalkerMaximumSpeedPerTick = 100` (`:55`), `WalkerYawInputMicroRadPerTick = 10_444`
(`:251`), `WalkerYawRetentionNumerator = 861_774` (`:252`),
`WalkerToJetTransitionTicks = 16` (`:316`). Nothing in the observation sections
below is withdrawn; the retail measurements they record stand, and only the
Core-side mapping of the two jet rows changed. The retail jet measurement itself
is still recorded at
[`jet-forward-scalar-response-v1.md`](jet-forward-scalar-response-v1.md).

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

**AMENDED 2026-07-28, in the energy-regeneration clause only.** Walker energy
regeneration is no longer provisional: Core carries
`WalkerEnergyRegenerationPerTick = 33`
(`rebuild/OnslaughtRebuild.Core/SimulationConstants.cs:318-345`), derived from
`references/Onslaught/BattleEngineWalkerPart.cpp:374-388` together with the
shipped byte `mGroundEnergyIncrease 0.05` in the record cited above. The rest of
that sentence — shield behavior and non-Level-100 movement configurations —
stands unchanged.
