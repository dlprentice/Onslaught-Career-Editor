# Ghidra CEngine Render Tail Signature Tranche - 2026-05-13

Status: GREEN public-safe saved-Ghidra evidence

## Summary

Serialized headless Ghidra dry/apply/read-back hardened `8` CEngine / CDXEngine / render-tail functions after focused metadata, decompile, xref, instruction, tag, and source-context review.

This pass corrected two stale owner labels, hardened several signatures, added behavior-bounded comments/tags, refreshed the whole-database quality queue, and backed up the actual live Ghidra project to `G:`.

## Targets

| Address | Saved state | Evidence summary |
| --- | --- | --- |
| `0x0044a2d0` | `CEngine__SetupLights` | Corrected from `CDXEngine__UpdateAtmosphericsAndLightMatrices`; source-parity static context includes MAP sun vector normalization, Atmospherics notification, view-vector/light matrix context, and global render-light matrix writes. |
| `0x0044a5f0` | `Vec3__AssignXYZ` | Signature hardened to `void __thiscall Vec3__AssignXYZ(void * this, float x, float y, float z)` with `RET 0xc` and three vector-slot writes. |
| `0x0044a610` | `CEngine__TrackBurstEventFromPreset` | Signature hardened to three stack arguments with `RET 0xc`, engine field context at `+0x470` and `+0x18`, and forwarding to `CEngine__TrackBurstEventIfNearby`. |
| `0x0044a640` | `CDXEngine__SetOverlaySlotVisibilityByPlayerView` | Calling convention corrected from stdcall-style output to thiscall with one `playerView` argument, `RET 0x4`, and overlay/view object context at `this+0x18`. |
| `0x0044a650` | `CDXEngine__SetRenderState_AlphaSpriteNoDepthWrite` | Comment/tag hardening records observed render-state pairs `0x1b=1`, `0x13=5`, `0x14=6`, and `0xe=0`. |
| `0x0044a690` | `RenderState__Set0x89_Zero` | Comment/tag hardening records the narrow `RenderState_Set(0x89, 0)` pattern. |
| `0x0044a6b0` | `CDXEngine__ApplyNavMapConsoleToggle_Thunk` | Signature hardened to five stack arguments with `RET 0x14`, `this+0x10` context, and forwarding to `CDXEngine__InvalidateLandscapeTilesAndPatchSlots`. |
| `0x0044a6e0` | `CEngine__Deserialize` | Corrected from `CResourceAccumulator__DeserializeMapTexListAndLoadMap`; source-parity static context includes `CChunkReader`, ENGN/map-texture count, engine `+0x49c` map-texture array, `CMapTex__Deserialize`, and MAP deserialize/init context. |

## Validation

- Headless dry run: `targets=8 updated=0 skipped=8 failed=0`.
- Headless apply: `targets=8 updated=8 skipped=0 failed=0`, with `REPORT: Save succeeded`.
- Read-back exports: `8` metadata rows, `8` decompile exports, `38` xref rows, `808` focused instruction rows, and `8` tag rows.
- Focused probe: `PASS`; `8` xref evidence hits, `8` instruction evidence hits, `0` stale target-name hits, `0` stale target-signature hits, and `0` overclaim hits.
- Whole-database refresh: `6008` functions, `1243` commented functions, `4765` commentless functions, `1948` `undefined` signatures, and `2019` `param_N` signatures.
- Current confirmation proxies are telemetry only: comment-backed `1243/6008 = 20.69%`; strict clean-signature `1181/6008 = 19.66%`. The `20%` value is not a milestone.
- Actual live Ghidra backup: `G:\GhidraBackups\BEA_20260513_044146_post_wave362_engine_render_tail_verified`, verified at `19` files, `153127815` bytes, and `HashDiffCount=0`.

## Claim Boundary

This proves saved static retail Ghidra names, signatures, comments, tags, selected xrefs, and selected instruction/decompile read-back for the `8` listed targets.

It does not prove exact Stuart-source method identity for every corrected target, concrete class or render-state layouts, local variables/types, runtime render/resource/navmap behavior, BEA launch behavior, game patching, or rebuild parity.
