# Ghidra InfantryUnit Lifecycle Boundary Wave1076 Readiness Note

Status: complete static mutation/read-back evidence
Date: 2026-06-02
Scope: `infantryunit-lifecycle-boundary-wave1076`

Wave1076 recovered and saved six previously missing Ghidra function boundaries from the CInfantryUnit primary vtable at `0x005e2730`. The pass created the six function objects, saved bounded signatures, saved comments/tags, and made no executable-byte change, BEA launch, runtime/game-file mutation, or installed-game mutation.

Evidence summary:

| Address | Evidence |
| --- | --- |
| `0x00488f10 CInfantryUnit__VFunc38_HandleHitOrDispatchHit` | Vtable slot 38 at `0x005e27c8` DATA-xrefs the raw entry; body ends at `0x00488f5c RET 0x8` before `0x00488f60`. |
| `0x00488f80 CInfantryUnit__VFunc34_CreateCollisionSphereWithAttachmentRadius` | Vtable slot 34 at `0x005e27b8` DATA-xrefs the raw entry; body ends at `0x0048902f RET 0x4` before `0x00489040`. |
| `0x00489090 CInfantryUnit__VFunc59_SelectAnimationMode` | Vtable slot 59 at `0x005e281c` DATA-xrefs the raw entry; body ends at `0x004892af RET 0xc` before `0x004892c0`. |
| `0x004892c0 CInfantryUnit__VFunc65_UpdateMotionAnimationState` | Vtable slot 65 at `0x005e2834` DATA-xrefs the raw entry; body ends at `0x0048964d RET` before `0x00489650`. |
| `0x00489650 CInfantryUnit__VFunc39_HandleCollisionDamageReaction` | Vtable slot 39 at `0x005e27cc` DATA-xrefs the raw entry; body ends at `0x00489b36 RET 0x10` before `0x00489b40`. |
| `0x00489b40 CInfantryUnit__VFunc49_HandleDeathPickupAndEffects` | Vtable slot 49 at `0x005e27f4` DATA-xrefs the raw entry; body ends at `0x00489dde RET` before `0x00489de0`. |

Read-back evidence:

- Primary pre exports verified `10` metadata rows, `10` tag rows, `12` xref rows, `281` instruction rows, and `10` decompile rows.
- Context exports verified `15` metadata rows, `701` instruction rows, and `15` decompile rows.
- CInfantryUnit vtable export verified `384` rows before mutation and `96` rows after mutation.
- Candidate pre-state verified `6` diagnose rows, `6` missing metadata rows, `6` DATA xref rows, `1014` instruction-window rows, `2214` wide instruction-window rows, and `6` missing decompile rows.
- Apply dry: `updated=6 skipped=0 created=0 would_create=6 renamed=0 would_rename=0 signature_updated=6 comment_only_updated=6 missing=0 bad=0`.
- Apply: `updated=6 skipped=0 created=6 would_create=0 renamed=0 would_rename=0 signature_updated=6 comment_only_updated=0 missing=0 bad=0`.
- Final dry: `updated=0 skipped=6 created=0 would_create=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`.
- Post exports verified `6` metadata rows, `6` tag rows, `6` xref rows, `1121` function-body instruction rows, `6` decompile rows, and `96` post vtable-slot rows.
- Queue closure is now `6254/6254 = 100.00%`, with `0` commentless functions, `0` exact-undefined signatures, and `0` `param_N` signatures.
- Wave911 focused re-audit progress remains `812/1408 = 57.67%`.
- Expanded static surface progress advances to `1365/1560 = 87.50%`.
- Wave911 top-500 risk-ranked coverage remains `500/500 = 100.00%`.
- Verified backup: `G:\GhidraBackups\BEA_20260602-065500_post_wave1076_infantryunit_lifecycle_boundary_verified`, `19` files, `174754695` bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- The loaded Ghidra project now has saved function objects at the six Wave1076 CInfantryUnit vtable entries.
- The saved names, signatures, comments, and tags read back for all six functions.
- The functions are tied to the CInfantryUnit primary vtable `0x005e2730` through DATA xrefs at `0x005e27b8`, `0x005e27c8`, `0x005e27cc`, `0x005e27f4`, `0x005e281c`, and `0x005e2834`.
- The recovered function bodies stay bounded and do not absorb adjacent existing function entries.

What remains separate proof:

- Exact source virtual names.
- Concrete CInfantryUnit/CUnitAI/layout semantics.
- Runtime infantry behavior.
- BEA patching behavior.
- Gameplay outcomes.
- Rebuild parity.

Next candidate note: continue with read-only review first from the remaining expanded static re-audit surface.

Probe token anchor: Wave1076; infantryunit-lifecycle-boundary-wave1076; 0x00488f10 CInfantryUnit__VFunc38_HandleHitOrDispatchHit; 0x00488f80 CInfantryUnit__VFunc34_CreateCollisionSphereWithAttachmentRadius; 0x00489090 CInfantryUnit__VFunc59_SelectAnimationMode; 0x004892c0 CInfantryUnit__VFunc65_UpdateMotionAnimationState; 0x00489650 CInfantryUnit__VFunc39_HandleCollisionDamageReaction; 0x00489b40 CInfantryUnit__VFunc49_HandleDeathPickupAndEffects; 0x005e2730; 0x005e27b8; 0x005e27c8; 0x005e27cc; 0x005e27f4; 0x005e281c; 0x005e2834; 812/1408 = 57.67%; 1365/1560 = 87.50%; 500/500 = 100.00%; 6254/6254 = 100.00%; G:\GhidraBackups\BEA_20260602-065500_post_wave1076_infantryunit_lifecycle_boundary_verified; boundary recovery.
