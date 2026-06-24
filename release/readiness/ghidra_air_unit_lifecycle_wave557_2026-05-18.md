# Ghidra Air-Unit Lifecycle / CreateSquad Wave557 Readiness Note

Date: 2026-05-18

## Scope

Wave557 saved static Ghidra name/signature/comment/tag hardening for 25 adjacent air-unit lifecycle and squad-factory targets:

| Address | Saved state |
| --- | --- |
| `0x0050ed60` | `void * __thiscall CBomber__scalar_deleting_dtor(void * this, byte delete_flags)` |
| `0x0050ed80` | `void * __fastcall CBigAirUnit__ctor_base(void * this)` |
| `0x0050ee10` | `void * __thiscall CGroundAttackAircraft__scalar_deleting_dtor(void * this, byte delete_flags)` |
| `0x0050ee30` | `void * __thiscall CInfantryUnit__scalar_deleting_dtor(void * this, byte delete_flags)` |
| `0x0050ee50` | `void * __thiscall CCarrier__scalar_deleting_dtor(void * this, byte delete_flags)` |
| `0x0050ee70` | `void * __thiscall CDropship__scalar_deleting_dtor(void * this, byte delete_flags)` |
| `0x0050eeb0` | `void * __thiscall CPlane__scalar_deleting_dtor(void * this, byte delete_flags)` |
| `0x0050eed0` | `void * __thiscall CDiveBomber__scalar_deleting_dtor(void * this, byte delete_flags)` |
| `0x0050eef0` | `void * __thiscall CCarver__scalar_deleting_dtor(void * this, byte delete_flags)` |
| `0x0050ef10` | `void * __thiscall CFenrir__scalar_deleting_dtor(void * this, byte delete_flags)` |
| `0x0050ef30` | `void __fastcall CCarrier__Destructor(void * this)` |
| `0x0050efa0` | `void __fastcall CBomber__ClearPtrSetsRemoveFromGlobalListAndDestruct(void * this)` |
| `0x0050f010` | `void * __thiscall CBigAirUnit__scalar_deleting_dtor(void * this, byte delete_flags)` |
| `0x0050f030` | `void __fastcall CBigAirUnit__Destructor(void * this)` |
| `0x0050f0a0` | `void * __fastcall CAirUnit__ctor_base(void * this)` |
| `0x0050f130` | `void __fastcall CGroundAttackAircraft__Destructor_VFunc01(void * this)` |
| `0x0050f1a0` | `void __fastcall CInfantryUnit__Destructor_VFunc01(void * this)` |
| `0x0050f1f0` | `void __fastcall CDropship__Destructor_VFunc01(void * this)` |
| `0x0050f260` | `void __fastcall CPlane__Destructor_VFunc01(void * this)` |
| `0x0050f2d0` | `void __fastcall CDiveBomber__Destructor_VFunc01(void * this)` |
| `0x0050f340` | `void __fastcall CCarver__Destructor_VFunc01(void * this)` |
| `0x0050f3b0` | `void __fastcall CFenrir__Destructor_VFunc01(void * this)` |
| `0x0050f420` | `void * __thiscall CAirUnit__scalar_deleting_dtor(void * this, byte delete_flags)` |
| `0x0050f440` | `void __fastcall CAirUnit__ClearPtrSetsRemoveFromGlobalListAndDestruct(void * this)` |
| `0x0050f4b0` | `void * __cdecl CWorldPhysicsManager__CreateSquad(int squad_type)` |

## Evidence

- `ApplyAirUnitLifecycleWave557.java` dry: `updated=0 skipped=25 renamed=0 would_rename=13 missing=0 bad=0`.
- Apply: `updated=25 skipped=0 renamed=13 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Final verify dry: `updated=0 skipped=25 renamed=0 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Read-back artifacts under `subagents/ghidra-static-reaudit/wave557-air-unit-lifecycle-0050ed60/`: `25` metadata rows, `25` tag rows, `36` xref rows, `2026` target instruction rows, `25` target decompile exports, and vtable slot-1 read-back for all covered aircraft/infantry tables.
- Focused probe: `py -3 tools\ghidra_air_unit_lifecycle_wave557_probe.py --check` PASS.
- NPM probe: `cmd.exe /c npm run test:ghidra-air-unit-lifecycle-wave557` PASS.
- Queue refresh: `cmd.exe /c npm run test:ghidra-static-reaudit-queue` PASS after fresh `ExportFunctionQualitySnapshot.java` export.

## Queue Telemetry

Fresh post-Wave557 queue:

| Metric | Value |
| --- | ---: |
| Function objects | 6089 |
| Functions with comments | 2728 |
| Commentless functions | 3361 |
| Exact `undefined` signatures | 1524 |
| Signatures still using `param_N` | 1226 |
| Comment-backed proxy | `2728/6089 = 44.80%` |
| Strict comment-plus-clean-signature proxy | `2674/6089 = 43.92%` |

These are queue telemetry only, not completion claims.

## Backup

Post-wave verified Ghidra backup:

```text
G:\GhidraBackups\BEA_20260518-162900_post_wave557_air_unit_lifecycle_verified
Files: 19
Bytes: 159615879
MissingCount: 0
ExtraCount: 0
HashDiffCount: 0
```

## Not Proven

Exact aircraft/infantry class layouts, source virtual names, allocator ownership beyond observed scalar-delete paths, concrete squad-type enum names, runtime aircraft destruction/spawn/squad behavior, BEA patching, and rebuild parity remain unproven.
