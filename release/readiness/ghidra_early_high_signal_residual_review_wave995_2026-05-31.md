# Ghidra Early High-Signal Residual Review Wave995 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-31
Scope: `early-high-signal-residual-review-wave995`

Wave995 re-audited selected Wave364 early-high-signal residual rows after the Wave900-Wave994 recheck gate. The pass saved one comment/tag correction at `0x00441e50 CDebugMarkers__Shutdown`, replacing stale Wave364 wording that said the body frees through `OID__FreeObject` with current instruction evidence showing a direct call to `CDXMemoryManager__Free` at `0x00549220` with memory-manager context `0x009c3df0`. It made no rename, no signature change, no function-boundary change, no executable-byte change, no BEA launch, runtime proof, or game-file mutation.

Reviewed targets and context:

| Address | Evidence |
| --- | --- |
| `0x00440b70 CDamage__ctor_clear_head_and_init_flag` | Wave364 damage owner correction still holds; clears damage-object head state and the `+0x1588c` initialization/sentinel field. |
| `0x00441490 CDXEngine__UpdateWrappedThingPositionsAndDistance` | CDXEngine render context; walks the world/debug render list, updates camera-relative distance, wraps positions, samples terrain height, and forwards mapwho position when present. |
| `0x004416e0 CConsole__ResetStatusHistoryBuffer` | Console status-history reset; already rechecked by Wave937, included as adjacent Wave364 residual context. |
| `0x004419e0 CConsole__RenderStatusHistoryOverlay` | Console status-history render path; already rechecked by Wave937, included as adjacent Wave364 residual context. |
| `0x00441e50 CDebugMarkers__Shutdown` | Saved Wave995 correction: `CGame__ShutdownRestartLoop` calls the helper; the body unlinks markers from `DAT_0066ffb0` and frees each marker directly through `CDXMemoryManager__Free`. |
| `0x00441ea0 CDebugMarkers__Render` | CDXEngine render context; walks debug markers, applies world matrices/default texture, renders debug volumes, projects labels, and draws text. |
| `0x004422d0 CDebugMarker__ctor` | Called from `CSoundManager__UpdateStatus`; inserts a marker into global marker head `DAT_0066ffb0`, seeds default transform/color/text state, and keeps sound-manager marker ownership as caller context only. |
| `0x00442380 CDebugMarker__UnlinkFromGlobalList` | Called from `CSoundManager__UpdateStatus` and `CSoundEvent__DestructorBody`; unlinks a marker before caller-side free. |

Read-back evidence:

- `ApplyEarlyHighSignalResidualWave995.java dry`: `updated=0 skipped=1 comment_only_updated=1 tags_added=5 missing=0 bad=0`
- `ApplyEarlyHighSignalResidualWave995.java apply`: `updated=1 skipped=0 comment_only_updated=1 tags_added=5 missing=0 bad=0`
- `ApplyEarlyHighSignalResidualWave995.java final dry`: `updated=0 skipped=1 comment_only_updated=0 tags_added=0 missing=0 bad=0`
- Post exports: `8` metadata rows, `8` tag rows, `10` xref rows, `586` body-instruction rows, and `8` decompile rows.
- Queue after Wave995: `6222` total functions, `6222` commented, `0` commentless, `0` exact-undefined signatures, `0` `param_N`, static closure `6222/6222 = 100.00%`.
- Wave911 focused re-audit progress: `464/1408 = 32.95%`.
- Expanded static surface progress: `569/1478 = 38.50%`.
- Verified backup: `G:\GhidraBackups\BEA_20260531-073718_post_wave995_early_high_signal_residual_review_verified`, `19` files, `173869959` bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- The reviewed function rows exist in the saved Ghidra project with the expected names and signatures.
- `0x00441e50 CDebugMarkers__Shutdown` now has the saved Wave995 comment and tags `early-high-signal-residual-review-wave995`, `wave995-readback-verified`, `comment-corrected`, `allocator-corrected`, and `wave364-normalized`.
- Instruction evidence at `0x00441e81` and `0x00441e86` supports the direct `CDXMemoryManager__Free` correction.
- Static xrefs preserve the CGame shutdown, CDXEngine render, and SoundManager debug-marker caller context.

What remains unproven:

- Runtime marker behavior.
- Exact debug-marker manager layout.
- Exact source-body identity.
- BEA patching behavior.
- Rebuild parity.
