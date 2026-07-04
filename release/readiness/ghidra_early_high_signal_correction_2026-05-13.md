# Ghidra Early High-Signal Correction - 2026-05-13

Status: GREEN public-safe saved-Ghidra evidence

## Summary

Serialized headless Ghidra dry/apply/read-back corrected `8` early high-signal saved functions after focused metadata, decompile, xref, instruction, tag, and source/caller-context review.

This pass corrected stale owner labels across damage, console/status-history, debug-marker, and sound-manager-adjacent helpers, hardened signatures/comments/tags, refreshed the whole-database quality queue, and backed up the actual live Ghidra project to `[maintainer-local-backup-volume]`.

## Targets

| Address | Saved state | Evidence summary |
| --- | --- | --- |
| `0x00440b70` | `CDamage__ctor_clear_head_and_init_flag` | Corrected from stale `CUnitAI__ResetPrimaryAndTailSentinels`; clears the damage-object head and initializes the `+0x1588c` flag/sentinel used before `CDamage__Init`. |
| `0x00441490` | `CDXEngine__UpdateWrappedThingPositionsAndDistance` | Signature hardened to camera-coordinate arguments; updates wrapped positions, distance at `+0x80`, shadow-height context, and mapwho position state from `CDXEngine__Render`. |
| `0x004416e0` | `CConsole__ResetStatusHistoryBuffer` | Corrected from stale `CUnit__ResetPerSlotCooldownTables`; resets 30 status-history text slots and the `+0x9e4` / `+0x9e8` ring-buffer fields. |
| `0x004419e0` | `CConsole__RenderStatusHistoryOverlay` | Corrected from stale frontend-cheat wording; renders up to six recent status-history lines through `Text__AsciiToWideScratch` and `CDXFont__DrawText`. |
| `0x00441e50` | `CDebugMarkers__Shutdown` | Corrected from stale `CGame__FreeObjectIfPresent`; frees the global debug-marker list head passed by reference from `CGame__ShutdownRestartLoop`. |
| `0x00441ea0` | `CDebugMarkers__Render` | Corrected from broad DXEngine debug-text wording; renders debug marker volume/text context and ensures the default mesh texture path. |
| `0x004422d0` | `CDebugMarker__ctor` | Corrected from stale `CSoundManager__SoundEventNode__Ctor`; constructs a debug-marker object, installs defaults, and links into `DAT_0066ffb0`. |
| `0x00442380` | `CDebugMarker__UnlinkFromGlobalList` | Corrected from stale sound-event-node unlink wording; unlinks one debug marker from the global `DAT_0066ffb0` singly-linked list. |

## Validation

- Headless dry run: `targets=8 updated=0 skipped=8 failed=0`.
- Headless apply: `targets=8 updated=8 skipped=0 failed=0`, with `REPORT: Save succeeded`.
- Read-back exports: `8` metadata rows, `8` decompile exports, `10` xref rows, `792` focused instruction rows, and `8` tag rows.
- Focused probe: `PASS`; `10` xref evidence hits, `8` instruction evidence hits, `0` stale name hits, `0` stale signature hits, and `0` overclaim hits.
- Whole-database refresh: `6008` functions, `1258` commented functions, `4750` commentless functions, `1948` `undefined` signatures, and `2011` `param_N` signatures.
- Current confirmation proxies are telemetry only: comment-backed `1258/6008 = 20.94%`; strict clean-signature `1196/6008 = 19.91%`. The `20%` value is not a milestone.
- Actual live Ghidra backup: `[maintainer-local-ghidra-backup-root]\BEA_20260513_061308_post_wave364_early_high_signal_verified`, verified at `19` files, `153160583` bytes, and `HashDiffCount=0`.

## Claim Boundary

This proves saved static retail Ghidra names, signatures, comments, tags, selected xrefs, and selected instruction/decompile read-back for the `8` listed targets.

It does not prove exact Stuart-source method identity for every corrected target, concrete class/global layouts, local variables/types, runtime console/debug-marker/sound behavior, BEA launch behavior, game patching, or rebuild parity. It also does not make the project `20% complete`; the target remains as close to `100%` evidence-grade static RE as possible.
