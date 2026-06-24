# Ghidra Unit/Weapon Gameplay Review Wave943 Readiness

Status: complete read-only static review
Date: 2026-05-28
Scope: `unit-weapon-gameplay-review-wave943`

Wave943 re-reviewed the next six Wave911 focused candidates after Wave942, split into a CUnit gameplay/lifecycle sub-cluster and a CWeapon construction/targeting/charge sub-cluster. Composer 2.5 consult recommended a read-only verification pass unless fresh exports proved stale comment drift; root Codex then ran fresh serialized Ghidra metadata, tag, xref, instruction, decompile, and vtable exports.

The fresh evidence found no Ghidra rename, signature, comment, function-boundary, or tag correction strong enough to justify a mutation. No executable bytes were changed.

Primary targets:

| Address | Saved row | Read-back evidence |
| --- | --- | --- |
| `0x004f6fd0` | `CUnit__RenderWithDistanceFade` | `bool __thiscall` with one `render_flags` stack argument and `RET 0x4`; sole fresh caller is `0x004bfac0 OID__RenderWithState1BOverride`; the saved comment already records the `this+0x48` render-context gate, temporary `0x0063012c` write, nested `CThing__Render`, restore to `0xff`, and handled/not-handled return boundary. |
| `0x004fd230` | `CUnit__SpawnProfileDropPickup` | Register-only CUnit profile-drop helper with fresh Unit/AirUnit/Plane/hit/reset/event/activation xrefs; saved comment already records profile `+0xe8`, `CWorldPhysicsManager__CreatePickup`, side `this+0x138`, position `this+0x1c..0x28`, and pickup init dispatch. |
| `0x00505e00` | `CWeapon__ctor_base` | `void * __thiscall` constructor with `RET 0x8`; fresh caller `0x0050f782 CWorldPhysicsManager__CreateWeaponByIndex`; saved comment already records `0xb0` allocation context, transient base table `0x005d8824`, CWeapon table `0x005dfc94`, `weapon_data` at `+0xa4`, caller context at `+0xa8`, and initial distance/profile setup. |
| `0x005061f0` | `CWeapon__DoesTargetMaskMatchDistanceProfile` | `bool __thiscall` with one `target_unit` argument; fresh callers remain BattleEngine auto-target/nearest-target paths; saved comment already records current weapon in `ECX`, distance bucket from `this+0x60`, `DAT_008553ec` fallback walk, profile mask `+0xa4`, and target mask `target_unit+0x34`. |
| `0x005068f0` | `CWeapon__AdvanceChargeProgressIfAnySlotAssigned` | Register-only current-weapon helper with fresh callers `CGeneralVolume__DispatchMode3BurstProgressAndSpawn` and `CBattleEngineWalkerPart__ChargeWeapon`; saved comment already records assigned-slot scan at weapon-data `+0x10..+0x1c`, charge `weapon+0x60`, and cap constant `DAT_005db358`. |
| `0x0050ee90` | `CUnit__scalar_deleting_dtor` | CUnit scalar-deleting destructor wrapper with `RET 0x4`; fresh DATA refs fan into multiple CUnit-family vtable regions. The saved comment already records the call to `0x004bfe00 CUnit__dtor_base_Thunk_004bfe00`, optional `CDXMemoryManager__Free` when `flags & 1`, and return of `this`. |

Context anchors:

- CUnit lifecycle context: `0x004bfe00 CUnit__dtor_base_Thunk_004bfe00`, `0x004f84e0 CUnit__dtor_base`, `0x004f9490 CUnit__SpawnConfiguredPickupIfAboveWater`, `0x004fd040 CUnit__ResetDeploymentGraphAndScheduleEvent`, `0x004fd140 CUnit__MarkDestroyedAndCleanupLinks`, and `0x004fd3d0 CUnit__IsCandidateSideCompatibleForTargeting`.
- CWeapon/target-profile context: `0x00505f90 CWeapon__DetachFromSetAndShutdownMonitor`, `0x00506350` through `0x00506800` distance-profile accessors, `0x005078b0 ProjectileBurstPreset__GetListEntryIdByIndex`, and `0x00509f70 TargetProfileContext__IsEligibleByDistanceBucketOrRange`.
- Vtable/context snapshots: `0x005dfc94` and `0x005e1510`, 96 slots each. The vtable export shows CWeapon slots including `0x00506930 CWeapon__HandleFireBurstEvent`, `0x00505f70 CWeapon__scalar_deleting_dtor`, and inherited/shared CUnit-family slots; `0x005e1510` preserves the CUnit-family context with `CUnit__ApplyDamage`, `CUnit__MarkDestroyedAndCleanupLinks`, and `CUnit__VFunc64_SpawnConfiguredPickupThreeTimes`.

Fresh read-back evidence:

- Primary exports: 6 metadata rows, 6 tag rows, 37 xref rows, 394 instruction rows, and 6 decompile rows.
- Context exports: 15 metadata rows, 15 tag rows, 133 xref rows, 1171 instruction rows, and 15 decompile rows.
- Vtable export: 192 rows across `0x005dfc94` and `0x005e1510`.
- Verified backup: `G:\GhidraBackups\BEA_20260528-043815_post_wave943_unit_weapon_gameplay_review_verified`, 19 files, 173280135 bytes, `DiffCount=0`.
- Mutation status: read-only review; no dry/apply/final-dry mutation scripts were run because the saved rows already matched the bounded static evidence.

Progress:

- Wave911 focused re-audit progress after Wave943: `186/1408 = 13.21%`.
- Static export-contract function-quality closure remains `6113/6113 = 100.00%`.

Probe token anchor: Wave943; `unit-weapon-gameplay-review-wave943`; `0x004f6fd0 CUnit__RenderWithDistanceFade`; `0x004fd230 CUnit__SpawnProfileDropPickup`; `0x00505e00 CWeapon__ctor_base`; `0x005061f0 CWeapon__DoesTargetMaskMatchDistanceProfile`; `0x005068f0 CWeapon__AdvanceChargeProgressIfAnySlotAssigned`; `0x0050ee90 CUnit__scalar_deleting_dtor`; `0x004bfe00 CUnit__dtor_base_Thunk_004bfe00`; `0x004f84e0 CUnit__dtor_base`; `0x00505f90 CWeapon__DetachFromSetAndShutdownMonitor`; `0x005dfc94`; `0x005e1510`; read-only review; `186/1408 = 13.21%`; `6113/6113 = 100.00%`; `G:\GhidraBackups\BEA_20260528-043815_post_wave943_unit_weapon_gameplay_review_verified`.

What this proves:

- The selected Unit/CWeapon rows remain present in the saved Ghidra project with coherent names, signatures, comments, tags, xrefs, instructions, vtable context, and decompile outputs.
- The CUnit and CWeapon sub-clusters are statically coherent with their prior Wave539/Wave540/Wave545/Wave550/Wave552/Wave460 correction boundaries.

What remains unproven:

- Runtime render fade behavior.
- Runtime pickup/drop behavior.
- Runtime weapon targeting, charge, and fire behavior.
- Exact CUnit, CWeapon, target-profile, pickup, and vtable layouts.
- Exact source-body identity.
- BEA patching behavior.
- Rebuild parity.
