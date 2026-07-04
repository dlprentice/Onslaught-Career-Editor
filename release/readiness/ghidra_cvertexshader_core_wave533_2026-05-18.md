# Ghidra CVertexShader Core Wave533 Readiness

Status: ready for public-safe release notes
Date: 2026-05-18
Scope: saved static Ghidra metadata for CVertexShader lifecycle, factory, declaration-token, render-state constants, and refcount helpers.

## Scope

Wave533 hardened eight adjacent CVertexShader core helpers using static retail Ghidra evidence only. The pass corrected the scalar-deleting destructor wrapper/body names, preserved the conservative slot-3 virtual label, and replaced weak signatures/comments/tags for constructor, factory, declaration-token, constant-upload, and refcount paths.

| Address | Saved state | Evidence |
| --- | --- | --- |
| `0x00501800` | `void * __thiscall CVertexShader__CVertexShader(void * this)` | Constructor installs vtable `0x005dfbc4`, clears shader/resource fields, initializes the base path, links into `0x00854e68`, and seeds type/version field `+0x2c` to `9`. |
| `0x00501890` | `void * __thiscall CVertexShader__scalar_deleting_dtor(void * this, byte delete_flags)` | Corrected stale vfunc slot-0 label; `RET 0x4` proves delete flags after ECX, and bit 0 gates `CDXMemoryManager__Free`. |
| `0x005018b0` | `void __thiscall CVertexShader__dtor(void * this)` | Corrected stale scalar-deleting-dtor body label; unlinks from shader/device lists, releases `+0x28`, and frees constant/source/blob buffers. |
| `0x00501b60` | `int __thiscall CVertexShader__VFunc_03_00501b60(void * this)` | Vtable slot 3 releases the device shader-like pointer at `+0x28`, clears it, and returns `0`; exact source virtual name remains deferred. |
| `0x00501ba0` | `int __thiscall CVertexShader__GetVertexDeclarationToken(void * this)` | Maps type/version field `+0x2c` to Direct3D declaration tokens; `CEngine__SetShaderObject` forwards the token to the device call. |
| `0x00501cd0` | `void __thiscall CVertexShader__ApplyRenderStateShaderConstants(void * this)` | Uploads projection/view/render-state constants through Direct3D device vtable `+0x178`, delegates to custom constants when `+0x34` is set, and applies the CVBufTexture texture-transform thunk. |
| `0x00502060` | `void * __cdecl CVertexShader__Create(char * shader_name, int shader_id, int shader_type, void * compiled_blob, int compiled_blob_size, int load_flags)` | Factory searches the global shader cache by blob or name/id, allocates `0x5c` bytes on miss, loads/copies shader data, and increments live refcount `+0x30`. |
| `0x00502290` | `void __thiscall CVertexShader__DecrementLiveReferenceCount(void * this)` | ECX-only release helper decrements live refcount `+0x30`; xrefs include render-state replacement, landscape shutdown, mesh VB release, and atmospherics release. |

## Evidence

- Mutation script: `tools/ApplyCVertexShaderCoreWave533.java`
- Probe script: `tools/ghidra_cvertexshader_core_wave533_probe.py`
- Evidence root: `subagents/ghidra-static-reaudit/wave533-cvertexshader-core-00501800/`
- Dry summary: `updated=0 skipped=8 renamed=0 would_rename=2 missing=0 bad=0`
- Apply summary: `updated=8 skipped=0 renamed=2 would_rename=0 missing=0 bad=0`
- Verify-dry summary: `updated=0 skipped=8 renamed=0 would_rename=0 missing=0 bad=0`
- Read-back rows: `8` metadata rows, `8` tag rows, `23 target xref rows`, `4808` instruction rows, `8` target decompile exports, `483` representative callsite instruction rows, and `8` vtable-slot rows.
- Focused probe: `py -3 tools\ghidra_cvertexshader_core_wave533_probe.py --check` -> `PASS`
- NPM probe: `npm run test:ghidra-cvertexshader-core-wave533` -> `PASS`
- Queue probe: `py -3 tools\ghidra_static_reaudit_queue_probe.py --check` -> `PASS`
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260518-052432_post_wave533_cvertexshader_core_verified` with `19` files, `159124359` bytes, `MissingCount=0`, `ExtraCount=0`, and `HashDiffCount=0`.

## Queue Impact

Fresh queue after Wave533:

- Function objects: 6083
- Functions with comments: 2589
- Commentless functions: 3494
- Exact `undefined` signatures: 1553
- Signatures still using `param_N` names: 1318
- Comment-backed telemetry: `2589/6083 = 42.56%`
- Strict clean-signature telemetry: `2532/6083 = 41.62%`

These are queue telemetry only, not certification and not a milestone.

## Boundaries

This is static retail Ghidra evidence only. Runtime shader behavior, runtime Direct3D behavior, exact CVertexShader/CShaderBase/device-object layouts, local-variable recovery, BEA patching, and rebuild parity remain unproven. Vtable slot 2 at `0x00501a10` and raw caller boundaries `0x0055512a` / `0x0055b3e3` remain deferred.
