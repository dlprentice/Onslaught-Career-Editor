# Ghidra PhysicsScript Manager Lifecycle Review Wave1019

Status: complete read-only static read-back evidence
Date: 2026-05-31
Scope: `physics-script-manager-lifecycle-review-wave1019`

Wave1019 re-read five `CPhysicsScript.cpp` manager lifecycle/load/factory rows with no mutation. Primary anchors are `0x0042e880 CPhysicsScript__Create`, `0x0042e8f0 CPhysicsScript__Destroy`, `0x0042e950 CPhysicsScript__Load`, `0x0042ea60 CPhysicsScript__Update`, and `0x0042eb90 CPhysicsScript__CreateStatement`.

Read-back evidence:

- Target exports: 5 metadata rows, 5 tag rows, 5 xref rows, 321 body-instruction rows, and 5 decompile rows.
- Context exports: 8 metadata rows, 19 xref rows, 776 body-instruction rows, and 8 decompile rows.
- Context anchors: `0x0042f570 CPhysicsScriptStatement__dtor`, `0x0042f2b0 CUnitStatement__LoadFromMemBuffer`, `0x00430210 CRoundStatement__LoadFromMemBuffer`, `0x004306e0 CSpawnerStatement__LoadFromMemBuffer`, `0x00431a10 CPhysicsHazardValueList__LoadFromMemBuffer`, `0x00430510 CSpawnerData__CreateAndRegisterByName`, `0x0043e630 CFlexArray__SkipBytesFromMemBuffer`, and `0x0043abd0 CExplosionBasedOn__ApplyToExplosionByName`.
- Queue closure remains `6238/6238 = 100.00%`.
- Wave911 focused re-audit progress advances to `523/1408 = 37.14%`.
- Expanded static surface progress advances to `752/1493 = 50.37%`.
- Wave911 top-500 risk-ranked coverage advances to `452/500 = 90.40%`.
- Verified backup: `G:\GhidraBackups\BEA_20260531-211749_post_wave1019_physics_script_manager_lifecycle_review_verified`, 19 files, 173968263 bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- The saved names, signatures, comments, and tags for the selected `CPhysicsScript` manager lifecycle/load/factory rows remain coherent with fresh static Ghidra metadata, tags, xrefs, instructions, and decompile evidence.
- The static call/xref spine ties `CWorldPhysicsManager__ReloadDefaultPhysicsAndBattleEngineData` to `CPhysicsScript__Load`, `CPhysicsScript__Update`, and `CPhysicsScript__Destroy`; ties `CPhysicsScript__Load` to `CPhysicsScript__Create` and `CPhysicsScript__CreateStatement`; and keeps the unknown-statement skip path tied to `CFlexArray__SkipBytesFromMemBuffer`.
- No rename, signature change, comment change, tag change, function-boundary change, executable-byte change, BEA launch, or runtime/game-file mutation was needed.

What remains separate proof:

- Runtime physics-script behavior.
- Exact statement and value-list layouts.
- Exact source-body identity.
- MSL/file-format completeness.
- BEA patching behavior.
- Rebuild parity.

Probe token anchor: Wave1019; physics-script-manager-lifecycle-review-wave1019; 0x0042e880 CPhysicsScript__Create; 0x0042e8f0 CPhysicsScript__Destroy; 0x0042e950 CPhysicsScript__Load; 0x0042ea60 CPhysicsScript__Update; 0x0042eb90 CPhysicsScript__CreateStatement; 523/1408 = 37.14%; 752/1493 = 50.37%; 452/500 = 90.40%; 6238/6238 = 100.00%; G:\GhidraBackups\BEA_20260531-211749_post_wave1019_physics_script_manager_lifecycle_review_verified; no mutation.
