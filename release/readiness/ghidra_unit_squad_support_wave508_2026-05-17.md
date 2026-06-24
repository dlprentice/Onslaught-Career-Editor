# Ghidra Unit / Squad Support Wave508 Readiness Note

Date: 2026-05-17

## Summary

Wave508 saved static Ghidra names, signatures, comments, and tags for 20 adjacent unit/squad support helpers. The tranche includes 7 renames and focuses on small predicates/wrappers plus CSquad/CSquadNormal constructor, destructor, init, member-removal, formation, and target-refresh helpers.

This is static retail Ghidra evidence only. It does not prove exact Unit, CSquad, CSquadNormal, CSphere, CComplexThing, support-profile, member-list, faction enum, event, collision, render, or formation layouts. It also does not prove runtime AI behavior, runtime collision/render behavior, BEA launch behavior, game patching, or rebuild parity remain unproven.

## Targets

| Address | Saved signature |
| --- | --- |
| `0x004e43d0` | `bool __fastcall CUnit__CanProvideSupportNow(void * this)` |
| `0x004e4420` | `bool __fastcall CUnit__IsInBlockedSupportState(void * this)` |
| `0x004e4480` | `bool __thiscall CUnit__IsSupportTargetMaskCompatible(void * this, void * target)` |
| `0x004e4d70` | `void __thiscall CSphere__VFunc02_ResolveCollisionAsCylinder(void * this, void * collision_arg0, void * collision_arg1, void * collision_arg2, int collision_flags)` |
| `0x004e5da0` | `void * __thiscall CSquad__Constructor(void * this)` |
| `0x004e5e50` | `void * __thiscall SharedComplexThing__ScalarDeletingDestructor(void * this, byte flags)` |
| `0x004e65b0` | `void __fastcall CSquad__VFunc02_RemoveFromGlobalLists(void * this)` |
| `0x004e65e0` | `void __thiscall CSquad__HandleEvent(void * this, void * event)` |
| `0x004e6660` | `void __fastcall CUnit__ResetDamageCooldownTimer(void * this)` |
| `0x004e6680` | `bool __thiscall CSquadNormal__IsFactionCompatible(void * this, int candidate_faction_state)` |
| `0x004e66e0` | `void __fastcall CUnit__RenderWithIdentityWorldAndShadowProbe(void * this)` |
| `0x004e6870` | `void * __thiscall CSquadNormal__Constructor(void * this)` |
| `0x004e6ac0` | `void * __thiscall CSquadNormal__ScalarDeletingDestructor(void * this, byte flags)` |
| `0x004e6ae0` | `void __fastcall CSquadNormal__Destructor(void * this)` |
| `0x004e6bb0` | `void __thiscall CSquadNormal__Init(void * this, void * init)` |
| `0x004e6f70` | `void __thiscall CSquadNormal__RemoveMember(void * this, void * member)` |
| `0x004e6ff0` | `void __thiscall CSquadNormal__SyncFromLeaderUnit(void * this, void * leader_unit)` |
| `0x004e7cf0` | `bool __fastcall CSquadNormal__UpdateFormationAdvanceScale(void * this)` |
| `0x004e7f40` | `bool __fastcall CSquadNormal__IsLeaderNearFormationCentroid(void * this)` |
| `0x004e8100` | `void __fastcall CSquadNormal__ScheduleTargetReaderRefresh(void * this)` |

## Evidence

- `CUnit__IsSupportTargetMaskCompatible` corrects the stale `CSquadNormal__IsTargetMaskCompatible` owner label. The checked body reads CUnit-style support fields at `this+0x3f4`, `this+0x3d0`, `this+0x3d8`, and `this+0x3f0`, then tests `target+0x34`.
- `CSphere__VFunc02_ResolveCollisionAsCylinder` corrects the generic vfunc-slot label. The body builds a temporary cylinder descriptor with vtable `0x005d88cc`, sphere radius at `this+0x14`, and delegates to the cylinder collision helper.
- `SharedComplexThing__ScalarDeletingDestructor` corrects a shared wrapper slot. The read-back shows several DATA xrefs, including the CSquad table slot, so the saved name stays owner-neutral.
- CSquad table read-back verifies `CSquad__HandleEvent`, `SharedComplexThing__ScalarDeletingDestructor`, and `CSquad__VFunc02_RemoveFromGlobalLists` at vtable `0x005def1c` slots `0`, `1`, and `2`.
- CSquadNormal table read-back verifies `CSquadNormal__ScalarDeletingDestructor`, `CSquadNormal__Init`, and `CSquadNormal__SyncFromLeaderUnit` at vtable `0x005df0f4` slots `1`, `9`, and `68`.
- `CSquadNormal__ScheduleTargetReaderRefresh` keeps the target-selection relationship to `CSquadNormal__SelectBestEngagementTarget` and event `4000` bounded to static Ghidra evidence.
- Larger or weaker-owner bodies from the same read-only export were intentionally deferred: `0x004e5e70`, `0x004e6610`, `0x004e66d0`, and `0x004e7110`.

Artifacts are under `subagents/ghidra-static-reaudit/wave508-unit-squad-support-004e43d0/`.

## Verification

- `ApplyUnitSquadSupportWave508.java` dry: `updated=0 skipped=20 renamed=0 would_rename=7 missing=0 bad=0`.
- `ApplyUnitSquadSupportWave508.java` apply: `updated=20 skipped=0 renamed=7 would_rename=0 missing=0 bad=0`.
- `ApplyUnitSquadSupportWave508.java` verify dry: `updated=0 skipped=20 renamed=0 would_rename=0 missing=0 bad=0`.
- All three mutation passes reported `REPORT: Save succeeded`.
- Post-readback exports verified `20` metadata rows, `20` tag rows, `43` xref rows, `2580` instruction rows, `20` decompile exports, and `320` vtable-slot rows.
- `py -3 tools\ghidra_unit_squad_support_wave508_probe.py --check` passed.
- `npm run test:ghidra-unit-squad-support-wave508` passed.
- Queue refresh passed and reports `6078` functions, `2348` commented, `3730` commentless, `1631` exact-undefined signatures, and `1463` `param_N` signatures.
- Current telemetry proxies are comment-backed `2348/6078 = 38.63%` and strict comment-plus-clean-signature `2294/6078 = 37.74%`; these are progress telemetry only, not completion certification.
- Ghidra project backup verified at `G:\GhidraBackups\BEA_20260517-165658_post_wave508_unit_squad_support_verified` with `19` files, `158141319` bytes, `MissingCount=0`, `ExtraCount=0`, and `HashDiffCount=0`.

## Not Proven

- Runtime support/deploy, squad AI, faction/formation, collision, render, or target-refresh behavior.
- Exact source-body identity for the checked helpers.
- Concrete structure layouts, enum names, member-list node types, or event contracts.
- BEA launch behavior, game patching behavior, or rebuild parity.
