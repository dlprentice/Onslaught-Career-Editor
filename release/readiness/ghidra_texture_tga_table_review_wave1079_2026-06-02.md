# Ghidra Texture/TGA Table Review Wave1079 Readiness Note

Status: complete static mutation/read-back evidence
Date: 2026-06-02
Scope: `texture-tga-table-review-wave1079`

Wave1079 recovered and saved one CTGALoader table-boundary function in the loaded Steam retail Ghidra database. The pass created `0x004f2cc0 CTGALoader__HasNonzeroStatusOut_004f2cc0` as a compact `bool __thiscall` virtual helper reached from CTGALoader vtable `0x005df518` slot `8` at slot address `0x005df538`.

The recovered body reads the constructor-stored status-output pointer at `this+0x118`, returns false when the pointer is null or the pointed dword is zero, and returns true when the pointed dword is nonzero. The post-read body stops at `0x004f2cd7 RET`, before adjacent `0x004f2ce0 CTGALoader__Load`.

Read-back evidence:

- Pre vtable export verified 48 rows across TerrainGuide `0x005df4ec`, CTGALoader `0x005df518`, and CImageLoader `0x005dbedc`; CTGALoader slot `8` was `NO_FUNCTION_AT_POINTER` for `0x004f2cc0`.
- Pre primary exports verified 18 metadata/decompile targets with 17 found and expected missing candidate `0x004f2120`, 18 tag rows, 16 xref rows, and 641 instruction rows.
- Suspect diagnostics verified 10 listing-state rows, 88 around-instruction rows, and 164 xref rows for table/code boundary context.
- `ApplyTextureTgaTableReviewWave1079.java` dry/apply/final dry reported `updated=0 skipped=0 created=0 would_create=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`, then `updated=1 skipped=0 created=1 would_create=0 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0`, then `updated=0 skipped=1 created=0 would_create=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Post exports verified 1 metadata row, 1 tag row, 2 xref rows, 9 function-body instruction rows, 1 decompile row, and 48 post vtable-slot rows.
- Queue closure after Wave1079 is `6262/6262 = 100.00%`; Wave911 focused progress remains `812/1408 = 57.67%`; expanded static re-audit surface advances to `1373/1560 = 88.01%`; top-500 coverage remains `500/500 = 100.00%`.
- Verified backup: `G:\GhidraBackups\BEA_20260602-085858_post_wave1079_texture_tga_table_review_verified`, 19 files, 174754695 bytes, `DiffCount=0`.

What this proves:

- The target function row exists in the saved Ghidra project.
- The saved signature is `bool __thiscall CTGALoader__HasNonzeroStatusOut_004f2cc0(void * this)`.
- The saved tags include `texture-tga-table-review-wave1079` and `wave1079-readback-verified`.
- CTGALoader vtable slot `8` now resolves to the recovered function.
- The observed body is static retail Ghidra evidence tied to listing state, vtable slot, DATA xref, instruction, decompile, and post-export read-back.

What remains separate proof:

- Exact source virtual name.
- Exact status-output field semantics.
- Runtime TGA/image-loading behavior.
- BEA patching behavior.
- Gameplay outcomes.
- Rebuild parity.

Probe token anchor: Wave1079; texture-tga-table-review-wave1079; 0x004f2cc0 CTGALoader__HasNonzeroStatusOut_004f2cc0; 0x005df518; 0x005df538; 0x004f2ce0 CTGALoader__Load; 0x00616dd0; 812/1408 = 57.67%; 1373/1560 = 88.01%; 500/500 = 100.00%; 6262/6262 = 100.00%; G:\GhidraBackups\BEA_20260602-085858_post_wave1079_texture_tga_table_review_verified; boundary recovery.
