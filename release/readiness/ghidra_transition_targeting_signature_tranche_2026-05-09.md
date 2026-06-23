# Ghidra Transition / Targeting Signature Tranche - 2026-05-09

## Summary

This wave reparsed seven transition/targeting-adjacent saved Ghidra functions from the static re-audit queue. Fresh metadata, decompile, xref, instruction, and vtable/RTTI exports showed that several useful working labels still needed stronger source-backed names and tighter signatures. A serial headless dry/apply pass saved seven corrected names/signatures/comments, followed by fresh read-back and a focused probe.

## Corrected Targets

| Address | Previous state | Saved state after correction | Evidence boundary |
| --- | --- | --- | --- |
| `0x0040a580` | `CMonitor__UpdateFlightWalkerTransitionState` | `void __fastcall CBattleEngine__Morph(void * battleEngine)` | Source bridge/name correction: body matches Stuart `CBattleEngine::Morph()` by state gates, special-move lockouts, weapon-charge loss, `BECOME_WALKER` / `BECOME_JET` events, transition animation paths, cockpit/part transition calls, and transform audio hooks. Runtime transform behavior remains unproven. |
| `0x0040ac50` | `CGeneralVolume__IntegrateSlotAccumulators` | `void __thiscall CBattleEngine__Rearm(void * this, float inAmount)` | Source bridge/name correction: `ret 0x4` and decompile body match Stuart `CBattleEngine::Rearm(float inAmount)`, iterating stores, skipping heated stores, adding configuration-scaled amount, and clamping at maximum. Runtime behavior remains unproven. |
| `0x0040acc0` | `CBattleEngine__SelectBestAimTargetAndMaybeQueueEvent` | `void * __thiscall CBattleEngine__CalcUnitOverCrossHair(void * this, void * event, int useMeshCollision, int updateReaders)` | Source bridge/name correction: `ret 0xc` and body match Stuart `CBattleEngine::CalcUnitOverCrossHair(CEvent *, BOOL, BOOL)` with auto-aim trace, mesh/outer-sphere selection, range-filtered unit result, reader update, and event reschedule context. |
| `0x0040b100` | `CGeneralVolume__ctor_zero_fields` | `void __fastcall CGeneralVolume__ctor_base(void * generalVolume)` | Owner/name correction: body writes the `CGeneralVolume` vtable and zeroes `+0x4/+0x8/+0xc`; vtable/RTTI read-back confirms `CGeneralVolume`. This is constructor-boundary evidence only. |
| `0x0040b120` | `CMonitor__UpdateTargetTrackingAimOffsets` | `void __fastcall CBattleEngine__UpdateAutoAim(void * battleEngine)` | Source bridge/name correction: body matches Stuart `CBattleEngine::UpdateAutoAim()`, refreshing current weapon/target reader state, computing predictive/direct yaw-pitch offsets, latching desired offsets, and smoothing with `AngleDifference`. |
| `0x0040b660` | `Math__GetSignedWrappedAngleDelta` | `float __cdecl AngleDifference(float currentAngle, float targetAngle)` | Source bridge/name correction: free math helper matches Stuart `AngleDifference`-style signed wrapped angular delta between two float inputs and is not `CGeneralVolume`-owned in checked caller evidence. |
| `0x0040b6d0` | `CBattleEngine__AcquireTargetWithBallisticConstraints` | `void __thiscall CBattleEngine__HandleAutoAim(void * this, void * event)` | Source bridge/name correction: `ret 0x4` and body match Stuart `CBattleEngine::HandleAutoAim(CEvent *)`, clearing the target reader, honoring the auto-aim gate, scanning candidates, filtering weapon/mount/range/angle/stealth context, confirming line trace, and rescheduling the event. |

## Validation

- Headless dry/apply: `updated=0 skipped=7 missing=0 bad=0`, then `updated=7 skipped=0 missing=0 bad=0`.
- Fresh metadata/decompile read-back: `7/7` targets.
- Fresh xref read-back: `20` rows.
- Fresh instruction read-back: `15407` rows, including `7` checked return-evidence hits.
- Vtable/RTTI read-back: `1` checked `CGeneralVolume` constructor evidence hit.
- Focused probe: `cmd.exe /c npm run test:ghidra-transition-targeting-signature-tranche` passed with `7` renamed targets, `0` `param_N` signature hits, and `0` overclaim hits.
- Refreshed queue probe: `5866` functions, `477` commented functions, `5389` commentless functions, `2076` undefined signatures, and `2474` `param_N` signatures.

## Non-Claims

This is saved Ghidra name/signature/comment refinement only. It does not prove concrete `CGeneralVolume`, `CBattleEngine`, weapon, target-reader, line/collision, or event layouts; local variable names; structure types; Ghidra tags; runtime transform behavior; runtime targeting behavior; BEA launch behavior; game patching; or rebuild parity.
