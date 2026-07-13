# Ghidra CVBufTexture Render Wave531 Readiness

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 semantic revalidation:** Historical record; `0x00500e70` comment correction; `0x00500fa0` comment correction; `0x005010e0` comment correction. The original text below remains provenance rather than current semantic authority. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); exact records are in `reverse-engineering/binary-analysis/ghidra-full-reaudit-corrections-2026-07-13.json` and `reverse-engineering/binary-analysis/ghidra-targeted-revalidation-corrections-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Status: ready for public-safe release notes
Date: 2026-05-18
Scope: saved static Ghidra metadata for CVBufTexture render-tail, reset, release, and get-or-create helpers.

## Scope

Wave531 hardened eight adjacent CVBufTexture render-tail helpers using static retail Ghidra evidence only. The pass preserved existing names and corrected signatures, comments, and tags for batch-list rendering, global release of unlocked transient buffers, indexed/non-indexed draw helpers, reset, and texture-backed get-or-create behavior.

| Address | Saved state | Evidence |
| --- | --- | --- |
| `0x00500d10` | `void __cdecl CVBufTexture__RenderBatchList(void * batch_list)` | Caller-cleaned `RET C3` and CMeshRenderer callsites prove one batch-list pointer argument; the body walks 0x24-byte records by priority 0..5 and calls `CVBufTexture__Render(reset_after_render=1)`. |
| `0x00500d60` | `void __cdecl CVBufTexture__ReleaseAllUnlocked(void)` | No-argument global helper called from `CDXEngine__PostRender`; it walks global list `0x00854e00`, skips persistent entries, unlocks active buffers, emits leftover warnings, and clears cursors. |
| `0x00500e70` | `void __thiscall CVBufTexture__Render(void * this, int reset_after_render)` | `RET 0x4`; unlocks VB/IB state, invokes texture render hooks, applies render state, binds stream/index buffers, draws indexed primitives, and optionally resets cursors/toggles double-buffer state. |
| `0x00500f80` | `void __thiscall CVBufTexture__Reset(void * this)` | ECX-only reset helper preserves last nonzero vertex byte count, clears vertex/index byte cursors, and toggles the active vertex-buffer slot when global double-buffering is enabled. |
| `0x00500fa0` | `void __thiscall CVBufTexture__RenderIndexed(void * this, int reset_after_render, int vertex_count_override, int primitive_count_override)` | `RET 0x0c`; derives zero count overrides, sets FVF/render state, validates the D3D device when enabled, draws indexed primitives, reports validation failures, and optionally resets. |
| `0x005010e0` | `void __thiscall CVBufTexture__RenderIndexedNoValidate(void * this, int reset_after_render, int vertex_count_override, int primitive_count_override)` | `RET 0x0c`; shares the indexed bind/draw/reset path while skipping the ValidateDevice branch and broader render-state setup. |
| `0x005011c0` | `void __thiscall CVBufTexture__RenderNonIndexed(void * this, int reset_after_render, int primitive_count_override)` | `RET 0x8`; unlocks active vertex state, derives zero primitive override from `CVBufTexture__GetVertexPrimitiveCount`, binds stream source, calls Direct3D `DrawPrimitive`, and optionally resets. |
| `0x00501280` | `void * __cdecl CVBufTexture__GetOrCreate(void * texture, int force_new)` | Caller-cleaned `RET C3`; reuses cached texture field `+0x140` or matching global-list entry when `force_new` is zero, otherwise allocates a new `0x68`-byte CVBufTexture. |

## Evidence

- Mutation script: `tools/ApplyCVBufTextureRenderWave531.java`
- Probe script: `tools/ghidra_cvbuftexture_render_wave531_probe.py`
- Evidence root: `subagents/ghidra-static-reaudit/wave531-cvbuftexture-render-00500d10/`
- Dry summary: `updated=0 skipped=8 missing=0 bad=0`
- Apply summary: `updated=8 skipped=0 missing=0 bad=0`
- Verify-dry summary: `updated=0 skipped=8 missing=0 bad=0`
- Read-back rows: `8` metadata rows, `8` tag rows, `39 target xref rows`, `3528` instruction rows, `8` target decompile exports, `8` context decompile exports, and `230` representative callsite instruction rows.
- Focused probe: `py -3 tools\ghidra_cvbuftexture_render_wave531_probe.py --check` -> `PASS`
- NPM probe: `npm run test:ghidra-cvbuftexture-render-wave531` -> `PASS`
- Queue probe: `py -3 tools\ghidra_static_reaudit_queue_probe.py --check` -> `PASS`
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260518-043303_post_wave531_cvbuftexture_render_verified` with `19` files, `159091591` bytes, `MissingCount=0`, `ExtraCount=0`, and `HashDiffCount=0`.

## Queue Impact

Fresh queue after Wave531:

- Function objects: 6083
- Functions with comments: 2575
- Commentless functions: 3508
- Exact `undefined` signatures: 1555
- Signatures still using `param_N` names: 1326
- Comment-backed telemetry: `2575/6083 = 42.33%`
- Strict clean-signature telemetry: `2521/6083 = 41.44%`

These are queue telemetry only, not certification and not a milestone.

## Boundaries

This is static retail Ghidra evidence only. Runtime rendering behavior, runtime device-loss behavior, exact texture/CVBufTexture/CVBuffer/CIBuffer layouts, Direct3D state semantics, local-variable recovery, BEA patching, and rebuild parity remain unproven.
