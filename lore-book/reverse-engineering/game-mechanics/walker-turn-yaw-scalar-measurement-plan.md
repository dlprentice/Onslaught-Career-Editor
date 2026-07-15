# Walker turn/yaw scalar measurement plan (M1.3)

Status: **landed v1 dual-accept** (2026-07-14, private `turn-p02`)  
Harness: `tools/battleengine_turn_yaw_measurement.py`  
Live path: `run-two --measure turn` (Look/Left=Q, rate_source=`yaw_axis_store`)  
Contract: [walker-turn-yaw-scalar-response-v1.json](walker-turn-yaw-scalar-response-v1.json)  
Policy: [walker-turn-yaw-retail-to-core-translation-policy.md](walker-turn-yaw-retail-to-core-translation-policy.md)  
Core: `WalkerLookYawRateMilliRadPerTick = 3`

## Measured result

Steady Look/Left yaw-axis rate ≈ **0.09066 rad/s** on both accepted attempts
(envelope **[0.0816, 0.0997]** rad/s). Source `mGroundTurnRate=1.5` is rejected
as Core authority.

## Live path notes

- Profile binds Look/Left → Q; Transform still T.
- Observer proves turn on `|BE+0x278| >= 0.05`.
- Analysis uses `rate_source=yaw_axis_store` (store magnitude as rad/s).
- Turn measure must not re-latch VK_UP (that forced Forward contamination).
