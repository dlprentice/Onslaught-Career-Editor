# Ghidra CTexture Debug Bindings Tail Wave687 Readiness

Date: 2026-05-21

Wave687 CTexture debug bindings tail saved static Ghidra metadata for eight adjacent CTexture/CDXTexture debug chunk, binding cleanup, constant-stream materialization, symbol hash-table, and parser-state destructor rows.

Tag anchor: `ctexture-debug-bindings-tail-wave687`

Read-back anchors:

- `0x0058eefb CTexture__ParseDebugChunkAndRelocateBindings`
- `0x0058f577 CTexture__Dtor_ReleaseParserState_DeleteOnFlag`
- Next queue head: `0x0058f593 CTexture__ReadParserTerminalToken`

## Evidence

- `ApplyCTextureDebugBindingsTailWave687.java` dry/apply/final-dry completed through headless Ghidra with `REPORT: Save succeeded`.
- Dry summary: `updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=8 varargs=0 missing=0 bad=0`.
- Apply summary: `updated=8 skipped=0 renamed=0 would_rename=0 signature_updated=8 varargs=0 missing=0 bad=0`.
- Final dry summary: `updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=0 varargs=0 missing=0 bad=0`.
- Post exports verified `8` metadata rows, `8` tag rows, `14` xref rows, `584` instruction rows, and `8` clean decompile rows.
- Pre-state evidence includes the same focused exports and candidate exports covering `13` adjacent CTexture/CDXTexture debug-chunk, binding, symbol-table, parser-state, token-reader, parser-build, and reduction rows before the final eight-row tranche was selected.
- Verified backup: `G:\GhidraBackups\BEA_20260521-111832_post_wave687_ctexture_debug_bindings_tail_verified`, `19` files, `164727687` bytes, `DiffCount=0`.

## Queue Delta

Post-Wave687 queue telemetry:

- Total functions: `6098`
- Commented functions: `3934`
- Commentless functions: `2164`
- Exact-undefined signatures: `1216`
- `param_N` signatures: `387`
- Comment-backed proxy: `3934/6098 = 64.51%`
- Strict clean-signature proxy: `3884/6098 = 63.69%`

## Boundaries

This proves saved static Ghidra name/signature/comment/tag metadata only. Exact DBGU/debug chunk schema, binding-record layout, compile-context field names, symbol-node class, payload-record layout, parser-state class identity, runtime texture compiler behavior, BEA patching, and rebuild parity remain unproven.
