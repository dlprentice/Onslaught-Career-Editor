# Ghidra PhysicsScript Unit / Weapon Value Tranche - 2026-05-12

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 live correction closeout:** Historical record; `0x00433390` comment correction. The original text below remains provenance rather than current semantic authority. It is superseded only where confirmed. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); final per-address decisions and exact before/after metadata are in `reverse-engineering/binary-analysis/ghidra-reviewed-correction-decisions-2026-07-13.jsonl` and `reverse-engineering/binary-analysis/ghidra-reviewed-correction-plan-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Status: GREEN static Ghidra correction evidence.

## Scope

This wave continued the saved-Ghidra re-audit immediately after the type-2/unit value factory and inspected the adjacent unit/weapon value region. Fresh metadata, decompile, xref, instruction, and tag read-back selected `17` tightly scoped targets and deliberately excluded the broader `0x00433390` `CComponentBasedOn__CopyFrom` routine for a later separate pass.

The wave saved names, signatures, comments, and tags for:

- Unit value destructors and unit-data apply/load slots.
- Shared `CPhysicsUnitValue` and `CPhysicsWeaponValue` destructor wrappers.
- The type-3/weapon value factory signature/comment boundary.
- The weapon charge-level load slot and weapon icon-name apply slot.

No new function boundary was created in this tranche.

## Corrected Labels

| Address | Saved name | Evidence summary |
| --- | --- | --- |
| `0x00432a50` | `CUnitAlligence__scalar_deleting_dtor` | Scalar-deleting wrapper around the unit-alligence destructor; spelling retained from current binary/source-adjacent evidence. |
| `0x00432a70` | `CUnitAlligence__dtor` | Destructor body that deletes the child value pointer at `+0x8` and restores the base value vtable. |
| `0x00432c00` | `CUnitSoundMaterial__ApplyToUnitData` | Applies the rounded scalar value into the unit data/init-like `+0xe4` field. |
| `0x00432c70` | `CUnitMaxLegsLifted__ApplyToUnitData` | Applies the rounded scalar value into the unit data/init-like `+0x140` field. |
| `0x00432cc0` | `CPhysicsUnitValue__dtor_base` | Base `CPhysicsUnitValue` destructor body. |
| `0x00432f70` | `CUnitNavMap__LoadFromMemBuffer` | Reads a child statement type and dispatches `CreateStatementType14`. |
| `0x00432fa0` | `CUnitNavMap__scalar_deleting_dtor` | Scalar-deleting wrapper around `CUnitNavMap__dtor`. |
| `0x00432fc0` | `CUnitNavMap__dtor` | Destructor body that deletes the child statement pointer at `+0x8`. |
| `0x004330b0` | `CUnitBehaviour__LoadFromMemBuffer` | Reads a child statement type and dispatches `CreateStatementType12`. |
| `0x004330e0` | `CUnitBehaviour__scalar_deleting_dtor` | Scalar-deleting wrapper around `CUnitBehaviour__dtor`. |
| `0x00433100` | `CUnitBehaviour__dtor` | Destructor body that deletes the child statement pointer at `+0x8`. |
| `0x00434100` | `CPhysicsUnitValue__scalar_deleting_dtor` | Shared scalar-deleting wrapper used by many unit value vtables. |
| `0x00434300` | `CPhysicsScriptStatements__CreateStatementType3` | Type-3/weapon value factory over observed value ids `0x74` through `0x81`. |
| `0x00434770` | `CWeaponChargeLevel__LoadFromMemBuffer` | Loads a charge-level scalar and weapon value name string. |
| `0x004347a0` | `CPhysicsWeaponValue__dtor_base` | Base `CPhysicsWeaponValue` destructor body. |
| `0x00434a80` | `CPhysicsWeaponValue__scalar_deleting_dtor` | Shared scalar-deleting wrapper used by weapon value vtables. |
| `0x00434f20` | `CWeaponIconName__ApplyToWeaponByName` | Searches the weapon list by name and replaces the matching record icon string. |

## Evidence

- `ApplyPhysicsScriptUnitWeaponValueTranche.java` dry run accepted all `17` targets with `bad=0`.
- `ApplyPhysicsScriptUnitWeaponValueTranche.java` apply reported `updated=17`, `renamed=16`, `missing=0`, `bad=0`, with `REPORT: Save succeeded`.
- Final read-back verified `17/17` metadata rows, `17/17` decompile exports, `99` xref rows, `7497` instruction rows, and `17/17` tag rows.
- `cmd.exe /c npm run test:ghidra-physics-script-unit-weapon-value-tranche` passed against the saved read-back artifacts.
- The refreshed whole-database queue reports `5904` functions, `927` commented functions, `4977` commentless functions, `1981` undefined signatures, and `2187` `param_N` signatures.
- The actual live Ghidra project backup after the saved mutation is `[maintainer-local-ghidra-backup-root]\BEA_20260512_082037_post_wave334_verified` with `19` files, `152210311` bytes, and `DiffCount=0`.

## Claim Boundary

This is saved static Ghidra name/signature/comment/tag evidence only. It does not prove exact source body identity, complete concrete class layouts, local variable recovery, structure typing, runtime physics-script behavior, weapon behavior, BEA launch, game patching, asset or save mutation, or rebuild parity.

Raw machine-readable proof remains under ignored `subagents/ghidra-static-reaudit/physics-script-unit-values-wave334/current/`.
