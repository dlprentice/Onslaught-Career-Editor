# Ghidra PhysicsScript Statement Lifetime Wave947 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-28
Scope: `physics-statement-lifetime-wave947`

Wave947 PhysicsScript statement lifetime review recovered eleven vtable-backed function boundaries in the `CPhysicsScriptStatements.cpp` unit/weapon value area and saved names, signatures, comments, and tags with `physics-statement-lifetime-wave947` and `wave947-readback-verified`. The pass made no executable-byte change and did not launch BEA.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x00432a20 CUnitAlligence__LoadFromMemBuffer` | Vtable `0x005d9d28` slot 3 / DATA xref `0x005d9d34`; reads a child value type, calls `CPhysicsScriptStatements__CreateStatementType13`, and stores the child value at `this+0x8`. |
| `0x00432ac0 CPhysicsUnitValue__base_vtable_scalar_deleting_dtor` | Base vtable `0x005d9e54` slot 0; compact scalar-deleting destructor wrapper that restores the base vtable and optionally calls `OID__FreeObject`. |
| `0x004347b0 CPhysicsWeaponValue__base_vtable_scalar_deleting_dtor` | Base vtable `0x005d9f80` slot 0; compact scalar-deleting destructor wrapper distinct from the shared weapon-value wrapper at `0x00434a80`. |
| `0x00432bd0 CUnitImportance__ApplyToUnitData` | Vtable `0x005d9cec` slot 1 / DATA xref `0x005d9cf0`; copies the value at `this+0x8` to unit/init-like field `+0xf8`. |
| `0x00432c60 CUnitStandingLegPlacementArea__ApplyToUnitData` | Vtable `0x005d9c24` slot 1 / DATA xref `0x005d9c28`; copies the value at `this+0x8` to unit/init-like field `+0x150`. |
| `0x00432f10 CUnitStrafeChange__ApplyToUnitData` | Vtable `0x005d9bac` slot 1 / DATA xref `0x005d9bb0`; copies the value at `this+0x8` to unit/init-like field `+0x180`. |
| `0x00432f50 CUnitNavMap__ApplyToUnitData` | Vtable `0x005d9b98` slot 1 / DATA xref `0x005d9b9c`; applies a child value through vtable slot `+0x4` and writes the result to unit/init-like field `+0xfc`. |
| `0x00433010 CUnitBehaviour__ApplyToUnitData` | Vtable `0x005d9d50` slot 1 / DATA xref `0x005d9d54`; applies a child behavior id to field `+0xe0` and maps selected ids into related field `+0xfc`. |
| `0x00433150 CUnitUse__ApplyToUnitData` | Vtable `0x005d9d64` slot 1 / DATA xref `0x005d9d68`; passes `this+0x8`, unit/init-like `+0x108`, and `this+0x208` into helper `0x005119e0`. |
| `0x00434930 CWeaponConsumption__ApplyToWeaponByName` | Vtable `0x005d9f30` slot 1 / DATA xref `0x005d9f34`; searches global weapon list `DAT_008553e8` by weapon name and applies the value payload. |
| `0x00434de0 CWeaponVersusAir__ApplyToWeaponByName` | Vtable `0x005d9e68` slot 1 / DATA xref `0x005d9e6c`; searches global weapon list `DAT_008553e8` by weapon name and applies the value payload. |

Read-back evidence:

- `ApplyPhysicsStatementLifetimeWave947.java dry`: `updated=0 skipped=0 created=0 would_create=11 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 bad=0`
- `ApplyPhysicsStatementLifetimeWave947.java apply`: `updated=11 skipped=0 created=11 would_create=0 renamed=0 would_rename=0 signature_updated=11 comment_only_updated=0 bad=0`
- `ApplyPhysicsStatementLifetimeWave947.java final dry`: `updated=0 skipped=11 created=0 would_create=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 bad=0`
- Pre exports: 30 metadata rows, 30 tag rows, 50 xref rows, 3009 instruction rows, 30 decompile rows, 13 focused vtables with 104 rows, and 90 typed PhysicsScript-adjacent vtables with 360 rows.
- Post exports: 11 metadata rows, 11 tag rows, 11 xref rows, 221 instruction rows, 11 decompile rows, focused vtable re-export with 104 rows, and typed vtable re-export with 360 rows.
- Queue after Wave947: 6150 total functions, 6150 commented, 0 commentless, 0 exact-undefined signatures, 0 `param_N`, comment-backed and strict clean-signature proxy `6150/6150 = 100.00%`.
- Wave911 focused re-audit progress after Wave947: `243/1408 = 17.26%`.
- Verified backup: `G:\GhidraBackups\BEA_20260528-070755_post_wave947_physics_statement_lifetime_review_verified`, 19 files, 173542279 bytes, `DiffCount=0`.

What this proves:

- The eleven target rows are now function objects in the saved Ghidra project.
- The saved signatures, comments, and tags were read back from the saved Ghidra database.
- The target boundaries are tied to observed PhysicsScript vtable slots and DATA xrefs in the retail binary.
- Static export-contract function-quality closure remains `6150/6150 = 100.00%`.

What remains unproven:

- Exact source method names.
- Concrete class layouts and target unit/weapon record schemas.
- Runtime PhysicsScript parsing, lifetime, and apply behavior.
- BEA patching behavior.
- Rebuild parity.
