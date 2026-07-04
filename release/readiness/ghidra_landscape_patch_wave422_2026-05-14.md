# Ghidra Landscape Patch Wave422 Static Correction

Date: 2026-05-14

## Summary

Wave422 saved a focused static-Ghidra correction for four landscape patch / terrain vertex-buffer helpers. The pass corrected stale owner labels around `0x0048f180`, `0x0048f1e0`, `0x0048f210`, and `0x0048f320`, then hardened signatures, comments, and tags using retail binary read-back, xrefs, decompile context, instruction exports, and the `0x005e5114` vtable-adjacent export.

This is public-safe saved static retail-binary evidence. It is not runtime terrain rendering proof, not GPU upload proof, not complete `CDXPatch` / `CLandscapeTexture` / `CVBuffer` layout recovery, not local-variable/type recovery, not complete vtable recovery, and not rebuild parity.

## Saved Ghidra Changes

| Address | Saved state | Evidence boundary |
| --- | --- | --- |
| `0x0048f180` | `CLandscapeTexture__InvalidateTileMaskOrRefreshAll` | Corrected from stale `CDXLandscape__InvalidateTileMaskOrRefreshAll`; marks `+0x2c`, fills optional update buffer `+0x40/+0x44` with `0xff`, or calls `CLandscapeTexture__UpdateTileRange` for full range `0..63`. |
| `0x0048f1e0` | `CDXPatch__CreateGridVertexBuffer` | Corrected from stale `CDXPatchManager__Create`; `RET 0x4` supports one stack argument, stores `grid_step` at `+0x44`, computes `(grid_step+1)^2`, clears patch fields, sets slot marker `+0x3c = 0xffff`, and calls `CVBuffer__Create` with `0x14`-byte vertices and flags `0x102`. |
| `0x0048f210` | `CDXPatch__RebuildHeightGridVertexBuffer` | Corrected from stale `CLandscapeVB__RebuildHeightGridVertexBuffer`; calls `CVBuffer__Lock`, walks the square grid from start X/Z fields with step `+0x34`, samples `CWorld__GetHeightSamplePacked16`, writes `0x14`-byte vertex rows, calls `CVBuffer__Unlock`, and marks `+0x40`. |
| `0x0048f320` | `CDXPatch__RestoreAndRebuildIfDirty` | Corrected from stale `CLandscapeVB__VFunc_01_0048f320`; vtable `0x005e5114` slot 1 dispatches here, calls `CVBuffer__Restore`, rebuilds via `CDXPatch__RebuildHeightGridVertexBuffer` when `+0x40` is nonzero, and returns the restore result. |

Stuart's current source snapshot does not contain matching `DXPatchManager.cpp` / `LandscapeTexture.cpp` bodies for these retail PC/DirectX terrain helpers, so this tranche relies on Steam retail Ghidra read-back. Source remains useful architecture evidence where present, but the saved Ghidra database is the authority for these names, signatures, comments, and tags.

## Validation

- Focused probe tests passed: `py -3 tools\ghidra_landscape_patch_wave422_probe_test.py`.
- Python compile check passed for the Wave422 probe and tests.
- Pre-apply package-script probe failed as expected because the post-apply/read-back artifacts did not exist yet.
- Headless dry run: `updated=0 skipped=4 created=0 would_create=0 renamed=0 would_rename=4 missing=0 bad=0`.
- Headless apply: `updated=4 skipped=0 created=0 would_create=0 renamed=4 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`.
- A follow-up comment refresh re-applied the same four saved targets with exact `CVBuffer__Lock` / `CVBuffer__Unlock` wording; it reported `updated=4 skipped=0 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Read-back exports verified `4` metadata rows, `4` tag rows, `7` xref rows, `484` instruction rows, `4` decompile exports, and `32` vtable-adjacent rows.
- Focused probe passed through npm: `cmd.exe /c npm run test:ghidra-landscape-patch-wave422`.
- Full static queue refreshed to `6043` functions, `1667` commented functions, `4376` commentless functions, `1861` undefined signatures, and `1813` `param_N` signatures.
- Current confirmation proxies are telemetry only: comment-backed `1667/6043 = 27.59%`; strict clean-signature `1604/6043 = 26.54%`.
- Actual live Ghidra project backup was verified at `[maintainer-local-ghidra-backup-root]\BEA_20260514_160133_post_wave422_landscape_patch_verified` with `19` files, `155159431` bytes, `HashDiffCount=0`, and `MissingCount=0`.

## Not Proven

- Runtime terrain rendering is not proven.
- Runtime GPU upload / vertex-buffer restore behavior is not proven.
- Complete concrete `CDXPatch`, `CDXPatchManager`, `CLandscapeTexture`, and `CVBuffer` layouts are not proven.
- Exact local-variable names and recovered Ghidra data types remain open.
- The `0x005e5114` vtable-adjacent export remains provisional; it includes checked slots and `NO_FUNCTION_AT_POINTER` rows, not complete vtable recovery.
- BEA was not launched, patched, or debugged in this wave.
- This does not prove rebuild parity or game-behavior equivalence.
