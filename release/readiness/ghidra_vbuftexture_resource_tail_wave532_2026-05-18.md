# Ghidra VBufTexture Resource Tail Wave532 Readiness

Status: ready for public-safe release notes
Date: 2026-05-18
Scope: saved static Ghidra metadata for VBufTexture resource cleanup, refcount, and pool trimming helpers.

## Scope

Wave532 hardened six adjacent VBufTexture/resource-tail helpers using static retail Ghidra evidence only. The pass preserved existing names and corrected signatures, comments, and tags for resource refcount decrement, screen-effect texture lookup, end-level/shutdown cleanup, and post-render/restart/shutdown VB/IB pool trimming.

| Address | Saved state | Evidence |
| --- | --- | --- |
| `0x00501310` | `void __fastcall CDXEngine__DecrementResourceRefCount(void * resource)` | ECX-only helper decrements the resource/CVBufTexture field at `+0x60`; callsites are release/render/debug paths that balance the `CVBufTexture__GetOrCreate` increment path. |
| `0x00501320` | `void __cdecl CScreenFx__FindTexture(char * texture_name, int texture_find_arg)` | Caller-cleaned `RET C3` and `CScreenFx__LoadZoomTextures` callsites prove two stack arguments; the body forwards to `CTexture__FindTexture`, adjusts the texture-side counter, and ensures `CVBufTexture__GetOrCreate(texture,0)`. |
| `0x00501360` | `void __cdecl CWaypoint__CleanupEndLevelVBufTextures(void)` | No-argument global helper reached from frontend/end-level cleanup; walks list head `0x00854e00`, frees zero-refcount entries, and emits end-of-level leak/no-leak `DebugTrace` text. |
| `0x00501450` | `void __cdecl CVBufTexture__ClearOut(void)` | No-argument shutdown helper called from `CLTShell__ShutdownRuntimeAndReleaseResources` after `CVertexShader__ClearOut`; frees zero-refcount list entries and reports shutdown resource leaks. |
| `0x00501540` | `void __cdecl CDXEngine__ResizeLargestIdleVertexBuffer(void)` | No-argument post-render helper gated by byte `0x00633d2c`; scans non-persistent entries, selects the largest vertex-buffer shrink opportunity, and calls `CVBufTexture__ResizeVertexBuffer`. |
| `0x005015c0` | `void __cdecl CEngine__TrimVbIbPoolCapacitiesPow2(void)` | No-argument helper reached from `CGame` restart, `CDXEngine` post-render, and `CEngine` shutdown; rounds current vertex/index cursors to `0x400`-based powers of two and shrinks oversized VB/IB capacities. |

## Evidence

- Mutation script: `tools/ApplyVBufTextureResourceTailWave532.java`
- Probe script: `tools/ghidra_vbuftexture_resource_tail_wave532_probe.py`
- Evidence root: `subagents/ghidra-static-reaudit/wave532-vbuftexture-resource-tail-00501310/`
- Dry summary: `updated=0 skipped=6 missing=0 bad=0`
- Apply summary: `updated=6 skipped=0 missing=0 bad=0`
- Verify-dry summary: `updated=0 skipped=6 missing=0 bad=0`
- Read-back rows: `6` metadata rows, `6` tag rows, `25 target xref rows`, `2646` instruction rows, `6` target decompile exports, and `525` representative callsite instruction rows.
- Focused probe: `py -3 tools\ghidra_vbuftexture_resource_tail_wave532_probe.py --check` -> `PASS`
- NPM probe: `npm run test:ghidra-vbuftexture-resource-tail-wave532` -> `PASS`
- Queue probe: `py -3 tools\ghidra_static_reaudit_queue_probe.py --check` -> `PASS`
- Verified backup: `G:\GhidraBackups\BEA_20260518-045906_post_wave532_vbuftexture_resource_tail_verified` with `19` files, `159091591` bytes, `MissingCount=0`, `ExtraCount=0`, and `HashDiffCount=0`.

## Queue Impact

Fresh queue after Wave532:

- Function objects: 6083
- Functions with comments: 2581
- Commentless functions: 3502
- Exact `undefined` signatures: 1555
- Signatures still using `param_N` names: 1324
- Comment-backed telemetry: `2581/6083 = 42.43%`
- Strict clean-signature telemetry: `2527/6083 = 41.54%`

These are queue telemetry only, not certification and not a milestone.

## Boundaries

This is static retail Ghidra evidence only. Runtime cleanup behavior, runtime screen-effect behavior, runtime pool trimming cadence, exact texture/CVBufTexture/CVBuffer/CIBuffer/list layouts, local-variable recovery, BEA patching, and rebuild parity remain unproven.
