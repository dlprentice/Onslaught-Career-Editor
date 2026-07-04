# Ghidra CGamut / Frustum-Culling Correction Tranche - 2026-05-13

Status: public-safe static RE evidence

## Summary

Wave 383 hardened four saved Ghidra targets in the `CGamut` / frustum-culling cluster. The pass used serialized headless dry/apply/read-back, then refreshed the whole-database quality queue and backed up the live Ghidra project to `[maintainer-local-backup-volume]`.

This is static retail-binary evidence only. It does not prove runtime frustum-culling behavior, visual rendering, imposter rendering, terrain culling, exact source body recovery, concrete `CGamut` layout recovery, local-variable typing, BEA launch behavior, game patching, or rebuild parity.

## Saved Targets

| Address | Saved signature | Evidence boundary |
| --- | --- | --- |
| `0x004741b0` | `void * __thiscall CGamut__Init(void * this, int init_arg)` | Called from `CEngine__Init`; sets grid/cell fields, allocates height and visibility buffers, and registers the gamut console variables. |
| `0x00474260` | `void __fastcall CGamut__Destroy(void * this)` | Called from `CEngine__Shutdown`; frees and clears the height buffer and the CGamut visibility buffer. |
| `0x004742a0` | `void __thiscall CGamut__ComputePlanes(void * this, float * frustum_corners)` | Called from `CGamut__Calculate`; performs the large plane/rasterization body over frustum-corner input. |
| `0x00476a20` | `void __thiscall CGamut__Calculate(void * this, float * view_matrix, float depth, float width_scale, float height_scale, float * camera_pos)` | Called from `CDXEngine__Render`; honors `cg_gamutlocked`, stores camera position, builds frustum corners, calls `CGamut__ComputePlanes`, and fills the visibility buffer from height ranges. |

`CGamut__Calculate` argument names are conservative. The callsite proves receiver, matrix pointer, stack float/value arguments, and camera-position pointer shape, but exact source names and full semantics remain provisional.

## Validation

| Check | Result |
| --- | --- |
| `tools/ApplyGamutWave383.java` dry run | PASS; `updated=0 skipped=4 renamed=0 would_rename=0 missing=0 bad=0`; `REPORT: Save succeeded`. |
| `tools/ApplyGamutWave383.java` apply run | PASS; `updated=4 skipped=0 renamed=0 would_rename=0 missing=0 bad=0`; `REPORT: Save succeeded`. |
| Metadata/decompile/xref/instruction/callsite/tag read-back | PASS; `4` metadata rows, `4` decompile exports, `4` xref rows, `484` instruction rows, `196` callsite-instruction rows, and `4` tag rows. |
| `py -3 tools\ghidra_gamut_wave383_probe_test.py` | PASS; unit tests `2/2`. |
| `cmd.exe /c npm run test:ghidra-gamut-wave383` | PASS; focused probe status `PASS`, `4` targets, `4` xref evidence hits, `8` instruction evidence hits, and `15` callsite evidence hits. |
| `py -3 -m py_compile tools\ghidra_gamut_wave383_probe.py tools\ghidra_gamut_wave383_probe_test.py` | PASS. |
| `cmd.exe /c npm run test:ghidra-static-reaudit-queue` | PASS; `6026` total functions, `1414` commented functions, `4612` commentless functions, `1935` undefined signatures, and `1917` `param_N` signatures. |
| Live Ghidra project backup | PASS; `[maintainer-local-ghidra-backup-root]\BEA_20260513_171430_post_wave383_gamut_verified`, `19` files, `153717639` bytes, `HashDiffCount=0`. |

Current confirmation proxies are telemetry only: comment-backed `1414/6026 = 23.46%`, strict clean-signature `1352/6026 = 22.43%`. They are not milestones and do not mark the RE campaign complete.

## Not Proven

- Runtime frustum-culling, visibility-grid, imposter, terrain-culling, or rendering behavior.
- Exact source body recovery for `gcgamut.cpp`; the Stuart source tree currently lacks this source body.
- Concrete `CGamut` structure layout, local variable types, or final argument semantics for every stack value.
- BEA launch behavior, patching behavior, packaged-app behavior, or rebuildable gameplay parity.
