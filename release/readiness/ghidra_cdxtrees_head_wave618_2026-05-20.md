# Ghidra CDXTrees Head Wave618 Readiness Note

Status: complete
Date: 2026-05-20

## Scope

Wave618 hardened nine contiguous CDXTrees head functions in the saved Ghidra project:

- `0x0055a350 CDXTrees__CDXTrees`
- `0x0055a360 CDXTrees__scalar_deleting_dtor`
- `0x0055a380 CDXTrees__dtor`
- `0x0055a390 CDXTrees__Init`
- `0x0055a3b0 CDXTrees__ReleaseBuffers`
- `0x0055a400 CDXTrees__Reset`
- `0x0055a420 CDXTrees__BuildTreeGeometry`
- `0x0055aa10 CDXTrees__Render`
- `0x0055ae40 CDXTrees__HideTree`

The pass saved signatures, comments, and tags only. It made no function renames, no function-boundary changes, and no executable byte changes.

## Evidence

- Dry/apply/final-dry logs reported `updated=0 skipped=9 renamed=0 would_rename=0 missing=0 bad=0`, then `updated=9 skipped=0 renamed=0 would_rename=0 missing=0 bad=0`, then `updated=0 skipped=9 renamed=0 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Post-state exports verified `9` metadata rows, `9` tag rows, `12` xref rows, `333` context instruction rows, `378` callsite instruction rows, `61` HideTree tail instruction rows, `9` decompile rows, and `16` vtable slot rows.
- The vtable at `0x005e59d8` has slot 0 `CDXTrees__scalar_deleting_dtor`, slot 1 `VFuncSlot_09_005019c0`, slots 2 and 3 `SharedVFunc__ReturnZero_00405930`, and slot 4 `CDXTrees__ReleaseBuffers`; slots 5-15 read back as float/data tail values, not function pointers.
- Backup verified: `[maintainer-local-ghidra-backup-root]\BEA_20260520-025200_post_wave618_cdxtrees_head_verified` with `19` files, `161680263` bytes, and `DiffCount=0`.

## Queue Telemetry

Post-Wave618 queue telemetry:

- Total functions: `6093`
- Commented functions: `3185`
- Commentless functions: `2908`
- Exact `undefined` signatures: `1247`
- `param_N` signatures: `1056`
- Comment-backed proxy: `3185/6093 = 52.27%`
- Strict clean-signature proxy: `3140/6093 = 51.53%`

Delta from Wave617: `+9` commented, `-9` commentless, `-9` exact-undefined signatures, `0` `param_N`, and `+9` strict clean-signature rows.

The next queue head is `0x0055d5e0 DirectSoundCreate8`.

## Boundaries

This is static saved-Ghidra evidence only. Runtime vegetation rendering, runtime tree destruction visibility, exact `CDXTrees`/`CRTTree`/`CVBufTexture`/render-state layouts, exact source-body identity, BEA patching, and rebuild parity remain deferred.
