# Ghidra Particle/Token/Landscape Wave420 Static Correction

Date: 2026-05-14

## Summary

Wave420 saved a focused static-Ghidra correction for five queue-head rendering/archive-adjacent helpers. The pass corrected the caller-owned `0x0048ddd0` label from `CParticleSet__OpenRead` to `CDXMemBuffer__OpenReadMode11`, hardened `CTokenArchive__ReadLine`, recovered the true three-argument shape of `CDXEngine__FormatCubeTextureFilename`, hardened the `CDXLandscape__ClearPendingHudMarkerHandle` constructor helper, and hardened `CLandscapeIB__CreateIndexBuffer`.

This is public-safe saved static retail-binary evidence. It is not runtime particle loading proof, not texture-render proof, not landscape-render proof, not complete class-layout recovery, not local-variable/type recovery, and not rebuild parity.

## Saved Ghidra Changes

| Address | Saved state | Evidence boundary |
| --- | --- | --- |
| `0x0048ddd0` | `CDXMemBuffer__OpenReadMode11` | Corrected the old caller-owned ParticleSet label. ECX is the `CDXMemBuffer` receiver, the single stack argument is the filename, and the helper calls `CDXMemBuffer__InitFromFile` with mode/context `0x11, 1, 0`. |
| `0x0048de00` | `CTokenArchive__ReadLine` | Hardened the two-argument `__stdcall` signature. The helper reads into a caller-provided line buffer through `DXMemBuffer__ReadLine`, then strips one trailing LF byte when present. |
| `0x0048de30` | `CDXEngine__FormatCubeTextureFilename` | Hardened the true three-argument `__cdecl` signature. The body formats one Kempy cube texture path, masks `cube_index` to one byte, and selects one of five suffix strings by `suffix_index`. |
| `0x0048de90` | `CDXLandscape__ClearPendingHudMarkerHandle` | Hardened the `__thiscall` constructor helper. The constructor passes the `CDXLandscape +0x8` marker-owner subobject in ECX; the helper clears global pending marker handle `0x0067a7d0` and returns the same pointer. |
| `0x0048df20` | `CLandscapeIB__CreateIndexBuffer` | Hardened the `__thiscall` signature/comment. The body covers cached index-data copying and generated grid/edge-stitch index-buffer creation paths. |

Stuart's source snapshot did not include direct source files for these checked helper bodies, so this tranche relies on retail binary read-back, xrefs, callsites, constants, and existing function context. Source remains useful architecture evidence where present, but the Steam retail Ghidra database is the authority for these saved function boundaries, names, signatures, comments, and tags.

## Validation

- Initial headless dry run before the first apply: `updated=0 skipped=5 created=0 would_create=0 renamed=0 would_rename=1 missing=0 bad=0`.
- The first apply caught one `__thiscall` read-back nuance on `0x0048de90` after four changes had saved; the script was corrected to use the Ghidra `this` parameter shape and rerun serially.
- Final headless dry run: `updated=0 skipped=5 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`.
- Final headless apply: `updated=5 skipped=0 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Read-back exports verified `5` metadata rows, `5` tag rows, `5` xref rows, `945` instruction rows, and `5` decompile exports.
- Focused probe tests passed: `py -3 tools\ghidra_particle_token_landscape_wave420_probe_test.py`.
- Focused probe passed through npm: `cmd.exe /c npm run test:ghidra-particle-token-landscape-wave420`.
- Python compile check passed for the Wave420 probe and tests.
- Full static queue refreshed to `6043` functions, `1649` commented functions, `4394` commentless functions, `1875` undefined signatures, and `1817` `param_N` signatures.
- Current confirmation proxies are telemetry only: comment-backed `1649/6043 = 27.29%`; strict comment-plus-clean-signature `1586/6043 = 26.25%`.
- Actual live Ghidra project backup was verified at `G:\GhidraBackups\BEA_20260514_150540_post_wave420_particle_token_landscape_verified` with `19` files, `155126663` bytes, `HashDiffCount=0`, and `MissingCount=0`.

## Not Proven

- Runtime particle archive loading is not proven.
- Runtime TokenArchive parser coverage is not proven.
- Runtime Kempy cube texture loading or rendering is not proven.
- Runtime HUD marker lifetime behavior is not proven.
- Runtime landscape index-buffer rendering is not proven.
- Complete concrete class layouts are not proven.
- Exact local-variable names and recovered Ghidra data types remain open.
- BEA was not launched, patched, or debugged in this wave.
- This does not prove rebuild parity or game-behavior equivalence.
