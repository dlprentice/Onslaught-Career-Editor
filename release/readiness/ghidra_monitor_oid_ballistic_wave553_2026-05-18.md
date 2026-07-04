# Ghidra Monitor / OID Ballistic Wave553 Readiness Note

Date: 2026-05-18

## Scope

Wave553 hardened eight static Ghidra functions across the monitor tracked-render path and OID/CUnit/BattleEngine projectile-ballistic range helpers:

| Address | Saved symbol |
| --- | --- |
| `0x005078f0` | `void __thiscall CMonitor__UpdateTrackedRenderPair(void * this, int update_projected_volume)` |
| `0x00507ab0` | `int __thiscall OID__CanFireAtTarget_BallisticArcA(void * this, void * target_unit, int ballistic_context)` |
| `0x005088b0` | `int __thiscall OID__CanFireAtTarget_BallisticArcB(void * this, void * target_unit)` |
| `0x00509140` | `void __thiscall OID__UpdateAimTransformAndAttachTargetReader(void * this, void * target_reader, void * target_transform)` |
| `0x005094b0` | `double __thiscall OID__SolveBallisticPitchToTarget(void * this, float target_x, float target_y, float target_z, float target_w)` |
| `0x005096a0` | `double __thiscall CUnit__ComputeMinBallisticTravelDistance(void * this, float target_x, float target_y, float target_z, float target_w)` |
| `0x005099a0` | `double __thiscall CUnit__ComputeMaxBallisticTravelDistance(void * this, float target_x, float target_y, float target_z, float target_w)` |
| `0x00509c80` | `double __thiscall CBattleEngine__ComputeProjectileMetricFromTargetProfile(void * this, float target_x, float target_y, float target_z, float target_w)` |

## Evidence

- `0x005078f0` has two callers: `CMonitor__UpdateMovementTransitionAndEffects` pushes `1`, and `CBattleEngineWalkerPart__Move` pushes `0`; `RET 0x4` proves one explicit `update_projected_volume` flag after `ECX`.
- `0x00507ab0`, `0x005088b0`, and `0x00509140` had phantom stack parameters removed by focused callsite and return-cleanup evidence. The `0x00509140` body uses the transform vector for aim state and then registers `target_reader` through `CGenericActiveReader__SetReader`, while exact higher-level wrapper argument order remains unresolved.
- The vector-target helpers at `0x005094b0`, `0x005096a0`, `0x005099a0`, and `0x00509c80` all end with `RET 0x10`; callsites copy four dwords, with the first three carrying `target_x`, `target_y`, and `target_z`, and the fourth retained as vector-convention context.
- `CUnit__ComputeMinBallisticTravelDistance` and `CUnit__ComputeMaxBallisticTravelDistance` return profile fields `+0x74` and `+0x78` on non-ballistic statements and derive ballistic travel ranges from target height, launch speed, gravity, and pitch-window fields otherwise.
- `CBattleEngine__ComputeProjectileMetricFromTargetProfile` forwards active ballistic profiles to `CUnit__ComputeMaxBallisticTravelDistance`; otherwise it selects a target/profile entry through `DAT_008553ec` and returns observed projectile metric fields or speed/range products.

## Read-Back

- Dry: `updated=0 skipped=8 renamed=0 would_rename=0 missing=0 bad=0`.
- Apply: `updated=8 skipped=0 renamed=0 would_rename=0 missing=0 bad=0`.
- Verify dry: `updated=0 skipped=8 renamed=0 would_rename=0 missing=0 bad=0`.
- Ghidra save reported `REPORT: Save succeeded`.
- Post exports verified `8` metadata rows, `8` tag rows, `22` xref rows, `1448` focused target instruction rows, `4968` full target instruction rows, `330` focused callsite instruction rows, `8` target decompile exports, and `15` caller decompile exports.
- Focused probe: `py -3 tools\ghidra_monitor_oid_ballistic_wave553_probe.py --check` PASS.
- npm wrapper: `cmd.exe /c npm run test:ghidra-monitor-oid-ballistic-wave553` PASS.
- Queue refresh: PASS with `6089` total functions, `2672` commented, `3417` commentless, `1535` exact-undefined signatures, and `1270` `param_N` signatures.
- Backup: `[maintainer-local-ghidra-backup-root]\BEA_20260518-142523_post_wave553_monitor_oid_ballistic_verified`, `19` files, `159386503` bytes, `MissingCount=0`, `ExtraCount=0`, `HashDiffCount=0`.

## Not Proven

- Exact source method/class identity for these helpers.
- Concrete Monitor/OID/CUnit/BattleEngine/profile/target/vector/list layouts.
- Exact boolean contracts, metric meanings, field names, or higher-level wrapper argument order.
- Runtime targeting/projectile/render behavior, BEA launch behavior, game patching, or rebuild parity.
