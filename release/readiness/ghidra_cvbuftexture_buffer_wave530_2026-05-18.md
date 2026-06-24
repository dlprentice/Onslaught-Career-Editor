# Ghidra CVBufTexture Buffer Wave530 Readiness

Status: ready for public-safe release notes
Date: 2026-05-18
Scope: saved static Ghidra metadata for CVBufTexture construction, format setup, resize, lock/unlock, append/reserve, and primitive-count helpers.

## Scope

Wave530 hardened fifteen adjacent CVBufTexture buffer-management helpers using static retail Ghidra evidence only. The pass preserved existing names and corrected signatures, comments, and tags across constructor/destructor, vertex/index buffer configuration, buffer resize, direct-write reservation, append helpers, and primitive-count helpers.

| Address | Saved state | Evidence |
| --- | --- | --- |
| `0x005003f0` | `void __thiscall CVBufTexture__CVBufTexture(void * this, void * texture)` | `RET 0x4` proves one texture pointer after ECX; the constructor clears buffer/list/cursor fields, links the object into `0x00854e00`, and stores the texture pointer. |
| `0x00500460` | `void __thiscall CVBufTexture__dtor(void * this)` | ECX-only destructor unlocks any active vertex/index locks, releases CVBuffer/CIBuffer slots, unlinks the object from the global list, and clears owned pointers. |
| `0x00500540` | `void __thiscall CVBufTexture__SetVBFormat(void * this, int fvf_format, int usage_flags, int vertex_stride, int primitive_type, int pool_mode)` | `RET 0x14` proves five stack arguments; the body stores VB format fields, masks `usage_flags` with `0xfffffdf7`, and forces pool mode 1 when hardware VP is disabled. |
| `0x00500590` | `void __thiscall CVBufTexture__SetIBFormat(void * this, int index_format, int usage_flags, int reserved, int pool_mode)` | `RET 0x10` proves four stack arguments; the third is preserved in the call ABI but not consumed by the recovered body. |
| `0x005005d0` | `void __thiscall CVBufTexture__SetPersist(void * this)` | ECX-only helper marks persist byte `+0x5c`. |
| `0x005005e0` | `void __thiscall CVBufTexture__ResizeVertexBuffer(void * this, int required_bytes)` | `RET 0x4`; rounds nonzero requests up from `0x400`, allocates CVBuffer storage, creates the new buffer, copies existing bytes when present, and releases the old slot. |
| `0x005007f0` | `void __thiscall CVBufTexture__ResizeIndexBuffer(void * this, int required_bytes)` | `RET 0x4`; mirrors the vertex path for CIBuffer storage and copies existing index bytes when present. |
| `0x005009c0` | `void __thiscall CVBufTexture__UnlockVB(void * this)` | ECX-only helper unlocks the active CVBuffer and clears vertex lock state at `+0x10` / `+0x38`. |
| `0x005009f0` | `void __thiscall CVBufTexture__UnlockIB(void * this)` | ECX-only helper unlocks the active CIBuffer and clears index lock state at `+0x2c` / `+0x3c`. |
| `0x00500a10` | `int __thiscall CVBufTexture__AddVertices(void * this, void * vertices, int vertex_count)` | `RET 0x8`; grows and locks the vertex buffer when needed, copies `vertex_count * stride` bytes, advances the byte cursor, and returns the starting vertex index. |
| `0x00500ac0` | `void __thiscall CVBufTexture__AddIndices(void * this, void * indices, int index_count)` | `RET 0x8`; grows and locks the index buffer when needed, copies `index_count * 2` bytes, and advances the index-byte cursor. |
| `0x00500b40` | `void * __thiscall CVBufTexture__GetIndexPtr(void * this, int index_count)` | `RET 0x4`; reserves `index_count * 2` bytes and returns the old index cursor pointer. |
| `0x00500bb0` | `int __thiscall CVBufTexture__GetVertexPtr(void * this, void * * out_vertex_ptr, int vertex_count)` | `RET 0x8`; reserves `vertex_count * stride` bytes, writes the raw pointer to `out_vertex_ptr`, and returns the starting vertex index. |
| `0x00500c50` | `int __thiscall CVBufTexture__GetIndexPrimitiveCount(void * this)` | ECX-only primitive-count helper over index byte cursor `+0x34` and primitive type `+0x50`. |
| `0x00500cb0` | `int __thiscall CVBufTexture__GetVertexPrimitiveCount(void * this)` | ECX-only primitive-count helper over vertex byte cursor `+0x1c`, stride `+0x54`, and primitive type `+0x50`. |

## Evidence

- Mutation script: `tools/ApplyCVBufTextureBufferWave530.java`
- Probe script: `tools/ghidra_cvbuftexture_buffer_wave530_probe.py`
- Evidence root: `subagents/ghidra-static-reaudit/wave530-cvbuftexture-buffer-005003f0/`
- Dry summary: `updated=0 skipped=15 missing=0 bad=0`
- Apply summary: `updated=15 skipped=0 missing=0 bad=0`
- Verify-dry summary: `updated=0 skipped=15 missing=0 bad=0`
- Read-back rows: `15` metadata rows, `15` tag rows, `109 target xref rows`, `1815` instruction rows, `15` target decompile exports, `22` context decompile exports, and `481` representative callsite instruction rows.
- Focused probe: `py -3 tools\ghidra_cvbuftexture_buffer_wave530_probe.py --check`
- NPM probe: `npm run test:ghidra-cvbuftexture-buffer-wave530`
- Queue probe: `py -3 tools\ghidra_static_reaudit_queue_probe.py --check`

## Queue Impact

Fresh queue after Wave530:

- Function objects: 6083
- Functions with comments: 2567
- Commentless functions: 3516
- Exact `undefined` signatures: 1563
- Signatures still using `param_N` names: 1326
- Comment-backed telemetry: `2567/6083 = 42.20%`
- Strict clean-signature telemetry: `2513/6083 = 41.31%`

These are queue telemetry only, not certification and not a milestone.

## Backup

Verified backup:

- Path: `G:\GhidraBackups\BEA_20260518-040132_post_wave530_cvbuftexture_buffer_verified`
- Files: 19
- Bytes: 159058823
- MissingCount: 0
- ExtraCount: 0
- HashDiffCount: 0

## Boundaries

This is static retail Ghidra evidence only. Runtime rendering behavior, runtime device-loss behavior, exact texture/CVBufTexture/CVBuffer/CIBuffer layouts, local-variable recovery, exact Direct3D pool semantics, BEA patching, and rebuild parity remain unproven.
