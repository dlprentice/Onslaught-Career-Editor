# Ghidra CDXTexture Catch Bridge Wave679 Readiness Note

Date: 2026-05-21

## Scope

Wave679 CDXTexture catch bridge saved static Ghidra metadata for two adjacent CPU-feature/EH rows: `0x00589200 Catch@00589200` and `0x0058920c CDXTexture__DetectCpuSimdFlags`.

The pass used the `cdxtexture-catch-bridge-wave679` and `wave679-readback-verified` tags. It made no renames, no function-boundary changes, no executable-byte changes, and no runtime exception or CPU-dispatch claim. Only `0x00589200 Catch@00589200` received a signature hardening; `0x0058920c CDXTexture__DetectCpuSimdFlags` kept its existing signature because Ghidra still models it as a split continuation with an unknown calling-convention warning.

## Evidence

- Dry/apply/final dry summaries:
  - `updated=0 skipped=2 renamed=0 would_rename=0 signature_updated=1 missing=0 bad=0`
  - `updated=2 skipped=0 renamed=0 would_rename=0 signature_updated=1 missing=0 bad=0`
  - `updated=0 skipped=2 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`
- Post exports verified `2` metadata rows, `2` tag rows, `2` xref rows, `98` instruction rows, and `2` clean decompile rows.
- Context exports verified `4` metadata rows, `4` tag rows, `64` xref rows, `244` instruction rows, and `4` clean decompile rows across `0x005890f1`, `0x00589200`, `0x0058920c`, and `0x0058926b`.
- Queue after Wave679: `6098` total, `3841` commented, `2257` commentless, `1216` exact-undefined signatures, `478` `param_N` signatures, strict clean-signature proxy `3791/6098 = 62.17%`.
- Next queue head: `0x00589367 CTexture__ReleaseIncludeNodeTreeRecursive`.
- Verified Ghidra backup: `[maintainer-local-ghidra-backup-root]\BEA_20260521-073516_post_wave679_cdxtexture_catch_bridge_verified`, `19` files, `164367239` bytes, `DiffCount=0`.

## Boundaries

Wave679 proves saved static retail Ghidra name/signature/comment/tag evidence for the observed compiler catch/unwind landing pad and the adjacent Ghidra-split CPU SIMD flag continuation. Exact MSVC EH model, exception-table layout, split-boundary ownership, feature-bit names, OS feature gating, runtime exception behavior, runtime dispatch policy, BEA patching, and rebuild parity remain deferred.

Probe anchors: `Wave679 CDXTexture catch bridge`, `cdxtexture-catch-bridge-wave679`, `0x00589200 Catch@00589200`, `0x0058920c CDXTexture__DetectCpuSimdFlags`, `0x00589367 CTexture__ReleaseIncludeNodeTreeRecursive`.
