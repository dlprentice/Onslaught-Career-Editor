# Ghidra TerrainGuide Vtable Review Wave1078 Readiness Note

Status: complete static mutation/read-back evidence
Date: 2026-06-02
Scope: `terrainguide-vtable-review-wave1078`

Wave1078 re-audited the TerrainGuide vtable surface after Wave544 and Wave1077, recovered one previously unresolved TerrainGuide slot-3 function boundary, and saved a conservative name/signature/comment/tag treatment. The pass created one function object and made no executable-byte change, BEA launch, runtime/game-file mutation, or installed-game mutation.

Recovered boundary:

| Address | Evidence |
| --- | --- |
| `0x004f1ee0 CTerrainGuide__VFunc03_UpdateGuidanceState_004f1ee0` | TerrainGuide vtable `0x005df4ec` slot `3` at `0x005df4f8` DATA-xrefs this body. The body uses ECX as the guide object, reads owner at `this+0x18`, checks owner flag byte `+0x2c` bit `0x4` for early owner-vtable dispatch at `+0x100`, otherwise updates owner `+0x14c` vector lanes and owner `+0x120` heading, calls helper `0x004fde10`, and later dispatches owner vtable `+0x1bc`. |

Read-back evidence:

- Pre TerrainGuide vtable export verified `16` slot rows and showed slot `3` at `0x005df4f8` pointing to `0x004f1ee0` as `NO_FUNCTION_AT_POINTER`.
- Pre target exports verified `7` metadata rows with one missing target (`0x004f1ee0`), `6` tag rows, `94` xref rows, `791` instruction-window rows, and `6` decompile rows.
- Wide instruction export around `0x004f1ee0` verified `277` rows and showed the slot-3 body returns before the adjacent `0x004f2120` global-reset stub and the existing `0x004f2140 CText__ResetCoreFields`.
- Apply dry: `updated=1 skipped=0 created=0 would_create=1 renamed=0 would_rename=0 signature_updated=1 comment_updated=1 tag_updated=1 missing=0 bad=0`.
- Apply: `updated=1 skipped=0 created=1 would_create=0 renamed=0 would_rename=0 signature_updated=1 comment_updated=1 tag_updated=1 missing=0 bad=0`.
- Final dry: `updated=0 skipped=1 created=0 would_create=0 renamed=0 would_rename=0 signature_updated=0 comment_updated=0 tag_updated=0 missing=0 bad=0`.
- Post exports verified `1` metadata row, `1` tag row, `1` xref row, `170` function-body instruction rows, `1` decompile row, and `16` post vtable-slot rows.
- Post vtable export now resolves TerrainGuide vtable `0x005df4ec` slot `3` to `0x004f1ee0 CTerrainGuide__VFunc03_UpdateGuidanceState_004f1ee0`.
- Queue closure is now `6261/6261 = 100.00%`, with `0` commentless functions, `0` exact-undefined signatures, `0` `param_N` signatures, `0` uncertain-owner names, and `0` legacy weak names.
- Wave911 focused re-audit progress remains `812/1408 = 57.67%`.
- Expanded static surface progress advances to `1372/1560 = 87.95%`.
- Wave911 top-500 risk-ranked coverage remains `500/500 = 100.00%`.
- Verified backup: `G:\GhidraBackups\BEA_20260602-082337_post_wave1078_terrainguide_vtable_review_verified`, `19` files, `174754695` bytes, `DiffCount=0`.

What this proves:

- The loaded Ghidra project now has a saved function object for TerrainGuide vtable slot `3`.
- The saved name, signature, comment, and tags read back for `0x004f1ee0`.
- The recovered slot is tied to the TerrainGuide vtable through a DATA xref from `0x005df4f8`.
- The function-quality export remains closed at 100% after the saved boundary expanded the function-object surface.

What remains separate proof:

- Exact source virtual name.
- Concrete TerrainGuide/vector/owner layout semantics.
- Runtime terrain-guidance behavior.
- BEA patching behavior.
- Gameplay outcomes.
- Rebuild parity.

Next candidate note: continue read-only first from the remaining expanded static re-audit surface, with TerrainGuide slot `10` / adjacent table context still recorded as not proven to be a function boundary.

Probe token anchor: Wave1078; terrainguide-vtable-review-wave1078; 0x004f1ee0 CTerrainGuide__VFunc03_UpdateGuidanceState_004f1ee0; 0x005df4ec; 0x005df4f8; 0x004f2120; 0x004f2140 CText__ResetCoreFields; 812/1408 = 57.67%; 1372/1560 = 87.95%; 500/500 = 100.00%; 6261/6261 = 100.00%; G:\GhidraBackups\BEA_20260602-082337_post_wave1078_terrainguide_vtable_review_verified; boundary recovery.
