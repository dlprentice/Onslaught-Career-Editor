# Walker Look/Left yaw-axis rate response (v1)

Status: measured (two accepted copied-runtime attempts)  
Schema: `battleengine-walker-turn-yaw-scalar-response.v1`  
Projection: [walker-turn-yaw-scalar-response-v1.json](walker-turn-yaw-scalar-response-v1.json)  
Private evidence label: `turn-p02`

## Claim boundary

Scalar **walker Look/Left** response measured as the absolute magnitude of the
hypothesized `BattleEngine+0x278` yaw-axis store during a 2.0 s Q hold, with
Look/Left bound to Q on a **copied** `defaultoptions.bea`.

| Metric | Lower | Upper | Units |
|--------|-------|-------|-------|
| Steady yaw rate | 0.0816 | 0.0997 | rad/s |
| Per-attempt steady | ≈ **0.09066** | | rad/s (both accepts identical to float precision) |

## Evidence classes

| Class | Status |
|-------|--------|
| Source hypothesis | `mGroundTurnRate=1.5` is **not** dual-accepted |
| Steam static | `+0x278` yaw-axis write path (ApplyYawInput notes) |
| Copied-runtime | turn-p02 two accepts, receipt-bound |
| Rebuild | See translation policy before Core write |

## Non-claims

See projection JSON. Not jet turn, not strafe, not full facing model.
