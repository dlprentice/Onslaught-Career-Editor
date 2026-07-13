# Wave1137 PhysicsScript Weapon Bridge Current-Risk Review Readiness Note

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 semantic revalidation:** Historical record; `0x0042f5f0` → `WeaponDefinition__CreateAndRegisterByName` (was `CWeapon__CreateAndRegisterByName`); `0x00437fe0` comment correction. The original text below remains provenance rather than current semantic authority. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); exact records are in `reverse-engineering/binary-analysis/ghidra-full-reaudit-corrections-2026-07-13.json` and `reverse-engineering/binary-analysis/ghidra-targeted-revalidation-corrections-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Status: complete static read-only evidence
Date: 2026-06-05
Scope: `wave1137-physics-script-weapon-bridge-current-risk-review`

Wave1137 accounts for `10 rows` from the Wave1108 current focused continuity denominator as a PhysicsScript weapon/weapon-mode bridge current-risk cluster with fresh Ghidra export evidence. This was a read-only review with no mutation: no rename, no signature change, no comment change, no tag change, no function-boundary change, no executable-byte change, no BEA launch, no installed-game mutation, and no runtime-file mutation.

Primary targets:

| Address | Evidence |
| --- | --- |
| `0x0040d0f0 CWeaponStatement__UsesBallisticArcNoLocks` | Called by CUnit ballistic range helpers, OID aim/fire checks, and `CBattleEngine__GetLaunchPosition`; static evidence gates on projectile gravity and clear lock-style fields at `+0x50/+0x6c`. |
| `0x0042f2b0 CUnitStatement__LoadFromMemBuffer` | DATA load-slot xref `0x005d9884`; reads a statement name from `CDXMemBuffer`, creates `CPhysicsUnitValueList`, dispatches type-2 children, skips unknown payload bytes, and recurses when the terminator permits. |
| `0x0042f780 CWeaponStatement__LoadFromMemBuffer` | DATA load-slot xref `0x005d985c`; reads a weapon statement name, creates `CPhysicsWeaponValueList`, dispatches type-3 children, skips unknown payload bytes, and recurses through the value list. |
| `0x0042f8a0 CPhysicsWeaponValueList__LoadFromMemBuffer` | Called by `CWeaponStatement__LoadFromMemBuffer` and by itself; dispatches `CreateStatementType3` load slot `+0xc` or skips unknown serialized bytes. |
| `0x0042fca0 CWeaponModeStatement__LoadFromMemBuffer` | DATA load-slot xref `0x005d9870`; reads a weapon-mode statement name, creates `CPhysicsWeaponModeValueList`, dispatches type-4 children, skips unknown payload bytes, and recurses through the value list. |
| `0x0042fdc0 CPhysicsWeaponModeValueList__LoadFromMemBuffer` | Called by `CWeaponModeStatement__LoadFromMemBuffer` and by itself; dispatches `CreateStatementType4` load slot `+0xc` or skips unknown serialized bytes. |
| `0x00435010 CPhysicsScriptStatements__CreateStatementType4` | Type-4/weapon-mode value factory; allocates weapon-mode value objects for observed ids `0x1` through `0x26` and returns null for unknown ids. |
| `0x004359c0 CPhysicsWeaponModeValue__dtor_base` | Called by `0x00437080`; destructor body restores/installs the `CPhysicsWeaponModeValue` vtable and supersedes older constructor-base wording. |
| `0x00437080 CPhysicsWeaponModeValue__scalar_deleting_dtor` | DATA vtable xrefs beginning at `0x005d9f94`; wrapper calls `0x004359c0`, optionally frees `this` through `OID__FreeObject` when flags bit 0 is set, and returns `this`. |
| `0x00437fe0 CPhysicsRoundValue__SetOwnedAuxStringAt0C` | Called from `0x00437f6a`; frees `this+0xc` and copies the source string into new `WorldPhysicsManager` allocation storage tagged `0x23c`. |

Context rows re-read for continuity: `0x0042e950 CPhysicsScript__Load`, `0x0042eb90 CPhysicsScript__CreateStatement`, `0x0042f3d0 CPhysicsUnitValueList__LoadFromMemBuffer`, `0x0042f570 CPhysicsScriptStatement__dtor`, `0x0042f5b0 CWeaponStatement__CreateWeaponAndRecurse`, `0x0042f5f0 CWeaponStatement__Create`, `0x0042fa40 CWeaponModeStatement__CreateWeaponModeAndRecurse`, `0x0042fa80 CWeaponModeStatement__Create`, `0x00430210 CRoundStatement__LoadFromMemBuffer`, `0x00430330 CPhysicsRoundValueList__LoadFromMemBuffer`, `0x00434300 CPhysicsScriptStatements__CreateStatementType3`, `0x00437490 CPhysicsScriptStatements__CreateStatementType5`, and `0x00438050 CPhysicsRoundValue__SetOwnedValueStringAt08`.

Evidence counts:

- Primary exports: `10` metadata rows, `10` tag rows, `57` xref rows, `1048` instruction rows, and `10` decompile rows.
- Context exports: `13` metadata rows, `13` tag rows, `29` xref rows, `1407` instruction rows, and `13` decompile rows.
- Static closure remains `6410/6410 = 100.00%`.
- Static debt remains `0 / 0 / 0` for commentless / exact-undefined / `param_N`.
- Expanded post-100 static surface remains `1560/1560 = 100.00%`.
- Wave911 focused remains `812/1408 = 57.67%`.
- Wave911 top-500 risk-ranked remains `500/500 = 100.00%`.
- Wave1108 current focused accounting advances to `214/1179 = 18.15%`.
- Current focused candidates: 1178.
- live regenerated current focused candidates: 1178.
- remaining active focused work: 965.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-122130_post_wave1137_physics_script_weapon_bridge_review_verified`, `19` files, `175967111` bytes, `DiffCount=0`, `HashDiffCount=0`.
- Previous completed Ghidra review backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-114652_post_wave1136_pausemenu_current_risk_review_verified`.

What this proves:

- The ten target function rows exist in the saved Ghidra project with the expected names, signatures, comments, xrefs, instruction exports, and decompile exports.
- Nine of the ten primary rows retain saved static-reaudit tag context; `0x0040d0f0 CWeaponStatement__UsesBallisticArcNoLocks` currently has no saved tag row contents and remains accepted as a read-only observation because its metadata/xrefs/decompile evidence are coherent.
- The PhysicsScript statement load path, weapon/weapon-mode value-list bridge, value factory, destructor, and owned-string helper evidence remains statically coherent with prior PhysicsScript contract waves.
- No mutation was required for these rows.

What remains separate proof:

- Runtime weapon behavior.
- Runtime weapon-mode behavior.
- Runtime PhysicsScript behavior.
- Serialized file-format completeness.
- Exact concrete layouts and exact source-body identity.
- BEA patching behavior.
- Gameplay outcomes.
- Visual QA.
- Rebuild parity.
