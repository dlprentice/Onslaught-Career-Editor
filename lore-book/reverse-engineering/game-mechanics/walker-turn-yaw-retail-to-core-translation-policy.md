# Retail → Core translation policy (walker Look/Left yaw rate)

Status: **accepted** (2026-07-14)  
Depends on: [walker-turn-yaw-scalar-response-v1.md](walker-turn-yaw-scalar-response-v1.md)

## Measured retail input

From `battleengine-walker-turn-yaw-scalar-response.v1` (pair `turn-p02`):

- Steady yaw rate \( \omega_r \in [0.0816, 0.0997] \) rad/s (mid ≈ 0.09066)
- Rate source: absolute value of hypothesized `BattleEngine+0x278` store during Look/Left hold

## Translation

| Parameter | Accepted default |
|-----------|------------------|
| Tick model | Core fixed 30 Hz |
| Angle unit | integer **milli-radians** (1000 = 1 rad) |
| Map | \( \omega_\mathrm{tick} = \mathrm{round}(\omega_r \cdot 1000 / 30) \) |
| Envelope band | \( \omega_\mathrm{tick} \in [3, 3] \) for the measured envelope |
| Accepted Core constant | **`WalkerLookYawRateMilliRadPerTick = 3`** |

## Core use

This constant **authorizes** a milli-radian-per-tick Look/Left scale in Core.
`SimInput.LookX` integrates `WalkerLookYawRateMilliRadPerTick` into continuous
milli-rad yaw and eight-way snaps `FacingX`/`FacingZ` for fire aim. Idle
`LookX` preserves move-axis facing snaps so existing tapes/goldens stay
stable. Core agreement does not re-prove retail.

## Checklist

1. [x] Policy accepted  
2. [x] v1 dual-accept projection is authority for retail numbers  
3. [x] Source `mGroundTurnRate=1.5` explicitly rejected as Core authority  
4. [x] No claim that Core re-proves retail  
