# Wave1137 PhysicsScript Weapon Bridge Current-Risk Review

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 semantic revalidation:** `0x0042f5f0` → `WeaponDefinition__CreateAndRegisterByName` (was `CWeapon__CreateAndRegisterByName`); `0x00437fe0` comment correction. Older conflicting text below is superseded for these rows. Use the [closeout](ghidra-full-reaudit-closeout-2026-07-13.md); exact records are in `reverse-engineering/binary-analysis/ghidra-full-reaudit-corrections-2026-07-13.json` and `reverse-engineering/binary-analysis/ghidra-targeted-revalidation-corrections-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Status: complete static read-only evidence
Date: 2026-06-05
Tag: `wave1137-physics-script-weapon-bridge-current-risk-review`

Wave1137 accounts for `10 rows` from the Wave1108 current focused continuity denominator as a PhysicsScript weapon/weapon-mode bridge current-risk cluster. It advances Wave1108 current focused accounting to `214/1179 = 18.15%` with current focused candidates: 1178, live regenerated current focused candidates: 1178, and remaining active focused work: 965.

Static closure remains `6410/6410 = 100.00%`; expanded post-100 static surface remains `1560/1560 = 100.00%`; Wave911 focused remains `812/1408 = 57.67%`; Wave911 top-500 risk-ranked remains `500/500 = 100.00%`; static debt remains `0 / 0 / 0`.

This was a fresh Ghidra export plus read-only review. It made no mutation: no rename, signature, comment, tag, function-boundary, executable-byte, BEA launch, installed-game, or runtime-file mutation.

## Primary Rows

| Address | Static read-back evidence |
| --- | --- |
| `0x0040d0f0 CWeaponStatement__UsesBallisticArcNoLocks` | Called by `CUnit__ComputeMinBallisticTravelDistance`, `CUnit__ComputeMaxBallisticTravelDistance`, `OID__CanFireAtTarget_BallisticArcA`, `OID__UpdateAimTransformAndAttachTargetReader`, and `CBattleEngine__GetLaunchPosition`; returns true when projectile gravity is non-zero and lock-style fields `+0x50/+0x6c` are clear. |
| `0x0042f2b0 CUnitStatement__LoadFromMemBuffer` | DATA load-slot xref `0x005d9884`; reads the statement name from `CDXMemBuffer`, creates the first `CPhysicsUnitValueList` node, dispatches `CreateStatementType2` children or skips unknown serialized payload bytes, and recurses when the terminator permits. |
| `0x0042f780 CWeaponStatement__LoadFromMemBuffer` | DATA load-slot xref `0x005d985c`; reads the statement name from `CDXMemBuffer`, creates the first `CPhysicsWeaponValueList` node, dispatches `CreateStatementType3` children or skips unknown serialized payload bytes, and recurses through the value list. |
| `0x0042f8a0 CPhysicsWeaponValueList__LoadFromMemBuffer` | Called by `CWeaponStatement__LoadFromMemBuffer` and recursively by itself; reads child statement type/serialized size, dispatches `CreateStatementType3` load slot `+0xc` when available, or skips unknown payload bytes. |
| `0x0042fca0 CWeaponModeStatement__LoadFromMemBuffer` | DATA load-slot xref `0x005d9870`; reads the statement name from `CDXMemBuffer`, creates the first `CPhysicsWeaponModeValueList` node, dispatches `CreateStatementType4` children or skips unknown serialized payload bytes, and recurses through the value list. |
| `0x0042fdc0 CPhysicsWeaponModeValueList__LoadFromMemBuffer` | Called by `CWeaponModeStatement__LoadFromMemBuffer` and recursively by itself; reads child statement type/serialized size, dispatches `CreateStatementType4` load slot `+0xc` when available, or skips unknown payload bytes. |
| `0x00435010 CPhysicsScriptStatements__CreateStatementType4` | Type-4/weapon-mode value factory; called by the weapon-mode statement/value-list loaders, allocates weapon-mode value objects for ids `0x1` through `0x26`, and returns null for unknown ids. |
| `0x004359c0 CPhysicsWeaponModeValue__dtor_base` | Called by `CPhysicsWeaponModeValue__scalar_deleting_dtor`; restores/installs the `CPhysicsWeaponModeValue` vtable and supersedes the Wave336 constructor-base wording. |
| `0x00437080 CPhysicsWeaponModeValue__scalar_deleting_dtor` | DATA vtable xrefs beginning at `0x005d9f94`; calls `CPhysicsWeaponModeValue__dtor_base`, optionally frees `this` via `OID__FreeObject` when flags bit 0 is set, and returns `this`. |
| `0x00437fe0 CPhysicsRoundValue__SetOwnedAuxStringAt0C` | Called from `0x00437f6a`; frees `this+0xc` and copies `sourceString` into new `WorldPhysicsManager` allocation storage tagged `0x23c`. |

## Context Rows

These rows were re-read as context and are not newly counted primary rows:

- context `0x0042e950 CPhysicsScript__Load`
- context `0x0042eb90 CPhysicsScript__CreateStatement`
- context `0x0042f3d0 CPhysicsUnitValueList__LoadFromMemBuffer`
- context `0x0042f570 CPhysicsScriptStatement__dtor`
- context `0x0042f5b0 CWeaponStatement__CreateWeaponAndRecurse`
- context `0x0042f5f0 CWeaponStatement__Create`
- context `0x0042fa40 CWeaponModeStatement__CreateWeaponModeAndRecurse`
- context `0x0042fa80 CWeaponModeStatement__Create`
- context `0x00430210 CRoundStatement__LoadFromMemBuffer`
- context `0x00430330 CPhysicsRoundValueList__LoadFromMemBuffer`
- context `0x00434300 CPhysicsScriptStatements__CreateStatementType3`
- context `0x00437490 CPhysicsScriptStatements__CreateStatementType5`
- context `0x00438050 CPhysicsRoundValue__SetOwnedValueStringAt08`

## Evidence Counts

| Export | Rows |
| --- | ---: |
| Primary metadata | 10 |
| Primary tags | 10 |
| Primary xrefs | 57 |
| Primary instructions | 1048 |
| Primary decompile index | 10 |
| Context metadata | 13 |
| Context tags | 13 |
| Context xrefs | 29 |
| Context instructions | 1407 |
| Context decompile index | 13 |

Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-122130_post_wave1137_physics_script_weapon_bridge_review_verified`; `19` files, `175967111` bytes, `DiffCount=0`, `HashDiffCount=0`.

Previous completed Ghidra review backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-114652_post_wave1136_pausemenu_current_risk_review_verified`.

Probe token anchor: Wave1137; wave1137-physics-script-weapon-bridge-current-risk-review; 214/1179 = 18.15%; 10 rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 965; PhysicsScript weapon/weapon-mode bridge current-risk cluster; fresh Ghidra export; read-only review; no mutation; 0 / 0 / 0; 0x0040d0f0 CWeaponStatement__UsesBallisticArcNoLocks; 0x0042f2b0 CUnitStatement__LoadFromMemBuffer; 0x0042f780 CWeaponStatement__LoadFromMemBuffer; 0x0042f8a0 CPhysicsWeaponValueList__LoadFromMemBuffer; 0x0042fca0 CWeaponModeStatement__LoadFromMemBuffer; 0x0042fdc0 CPhysicsWeaponModeValueList__LoadFromMemBuffer; 0x00435010 CPhysicsScriptStatements__CreateStatementType4; 0x004359c0 CPhysicsWeaponModeValue__dtor_base; 0x00437080 CPhysicsWeaponModeValue__scalar_deleting_dtor; 0x00437fe0 CPhysicsRoundValue__SetOwnedAuxStringAt0C; context 0x0042e950 CPhysicsScript__Load; context 0x0042eb90 CPhysicsScript__CreateStatement; context 0x0042f3d0 CPhysicsUnitValueList__LoadFromMemBuffer; context 0x0042f570 CPhysicsScriptStatement__dtor; context 0x0042f5b0 CWeaponStatement__CreateWeaponAndRecurse; context 0x0042f5f0 CWeaponStatement__Create; context 0x0042fa40 CWeaponModeStatement__CreateWeaponModeAndRecurse; context 0x0042fa80 CWeaponModeStatement__Create; context 0x00430210 CRoundStatement__LoadFromMemBuffer; context 0x00430330 CPhysicsRoundValueList__LoadFromMemBuffer; context 0x00434300 CPhysicsScriptStatements__CreateStatementType3; context 0x00437490 CPhysicsScriptStatements__CreateStatementType5; context 0x00438050 CPhysicsRoundValue__SetOwnedValueStringAt08; [maintainer-local-ghidra-backup-root]\BEA_20260605-122130_post_wave1137_physics_script_weapon_bridge_review_verified; [maintainer-local-ghidra-backup-root]\BEA_20260605-114652_post_wave1136_pausemenu_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; current risk candidates: 6165; focused threshold `15`; not Wave911 reconstruction; [maintainer-local-ghidra-backup-root]\BEA_20260604-200748_post_wave1100_cmeshpart_load_geometry_review_verified.

## Boundary

This is static Ghidra evidence only. Runtime weapon behavior, runtime weapon-mode behavior, runtime PhysicsScript behavior, serialized file-format completeness, exact concrete layouts, exact source-body identity, BEA patching, gameplay outcomes, visual QA, and rebuild parity remain separate proof.
