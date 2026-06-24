# Ghidra CWeapon Construction / Teardown Wave550 Readiness Note

Date: 2026-05-18

## Scope

Wave550 hardened two static Ghidra functions:

| Address | Saved symbol |
| --- | --- |
| `0x00505e00` | `void * __thiscall CWeapon__ctor_base(void * this, void * weapon_data, int create_context)` |
| `0x00505f90` | `void __fastcall CWeapon__DetachFromSetAndShutdownMonitor(void * this)` |

## Evidence

- `CWorldPhysicsManager__CreateWeaponByIndex` allocates `0xb0` bytes, pushes the caller context/type value and selected weapon data, moves the allocation into `ECX`, and calls `CWeapon__ctor_base`; `RET 0x8` proves two explicit stack arguments after `this`.
- `CWeapon__ctor_base` installs transient table `0x005d8824`, then CWeapon table `0x005dfc94`, initializes the embedded `+0x14` two-node array, stores `weapon_data` at `+0xa4`, stores the second caller value at `+0xa8`, seeds a zero-Euler `Mat34` into `+0x30`, initializes distance/profile state, selects an initial `DAT_008553ec` profile entry, and returns `this`.
- The current CWeapon table dump at `0x005dfc94` resolves slot 0 to `CWeapon__HandleFireBurstEvent`, slot 1 to `CWeapon__scalar_deleting_dtor`, slot 2 to `CMonitor__Shutdown_Core`, and slot 3 to `VFuncSlot_03_0044a830`.
- `CWeapon__DetachFromSetAndShutdownMonitor` is called by `CWeapon__scalar_deleting_dtor`; it checks embedded set/list cell `+0x2c`, removes `this+0x2c` from the owner set when linked, destroys the two `+0x14` global-list nodes with `CParticleManager__RemoveFromGlobalList_Thunk`, and calls `CMonitor__Shutdown(this)`.

## Read-Back

- Dry: `updated=0 skipped=2 renamed=0 would_rename=1 missing=0 bad=0`.
- Apply: `updated=2 skipped=0 renamed=1 would_rename=0 missing=0 bad=0`.
- Verify dry: `updated=0 skipped=2 renamed=0 would_rename=0 missing=0 bad=0`.
- Ghidra save reported `REPORT: Save succeeded`.
- Post exports verified `2` metadata rows, `2` tag rows, `2` xref rows, `514` target instruction rows, `482` caller instruction rows, `2` decompile exports, and `4` CWeapon vtable rows.
- Focused probe: `py -3 tools\ghidra_equipment_weapon_lifecycle_wave550_probe.py --check` PASS.
- npm wrapper: `cmd.exe /c npm run test:ghidra-equipment-weapon-lifecycle-wave550` PASS.
- Queue refresh: PASS with `6089` total functions, `2661` commented, `3428` commentless, `1535` exact-undefined signatures, and `1281` `param_N` signatures.
- Backup: `G:\GhidraBackups\BEA_20260518-125548_post_wave550_equipment_weapon_lifecycle_verified`, `19` files, `159353735` bytes, `MissingCount=0`, `ExtraCount=0`, `HashDiffCount=0`.

## Not Proven

- Exact source constructor identity or exact source `CWeapon` body names.
- Concrete `CWeapon`, `CEquipment`, profile, set/list, or monitor layout and field names/types.
- Runtime weapon construction, firing, targeting, or teardown behavior.
- Complete CWeapon vtable ownership/slot semantics.
- BEA patching or rebuild parity.
