# Ghidra D3D Shader/Input Tail Wave850 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-25
Scope: `d3d-shader-input-tail-wave850`

Wave850 D3D shader/input tail saved comments, tags, one bounded name/signature correction, and signature/comment treatments for thirteen important controller-input, Direct3D state-policy, shader-binding, shader-create, draw-indexed, buffer-lifetime, and COM release connector rows from `0x00513a80 PlatformInput__GetKeyState3Core` through `0x00514010 IUnknown__ReleaseAndNull`. The pass made one rename, no function-boundary changes, and no executable-byte changes.

Representative anchors:

| Address | Saved state | Evidence |
| --- | --- | --- |
| `0x00513a80 PlatformInput__GetKeyState3Core` | `bool __thiscall PlatformInput__GetKeyState3Core(void * this, int key)` | Source-reference `PCController`/`PCPlatform` `KeyOn` path; returns the byte at `this+0x332e4+key`. |
| `0x00513a90 PlatformInput__GetKeyOnceCore` | `bool __thiscall PlatformInput__GetKeyOnceCore(void * this, int key)` | Source-reference `KeyOnce` path; reads/clears `this+0x331e4+key` and records consumed keys through queue global `0x00855424`. |
| `0x00513b60 D3DStateCache__ForceSlotMode4or5` | `void __stdcall D3DStateCache__ForceSlotMode4or5(int state_slot)` | Writes forced mode `4` or `5` into `DAT_008557f4[state_slot*0x1e]`, then calls device vtable slot `0x10c`. |
| `0x00513c70 CEngine__DrawIndexedPrimitives` | `void __thiscall CEngine__DrawIndexedPrimitives(void * this, int primitive_type, int arg2, int arg3, int arg4, int arg5)` | Source-reference `D3D_DrawIndexedPrimitive`; calls device vtable slot `0x148` with `MinIndex` forced to `0`; observed callers do not consume `EAX` immediately. |
| `0x00513ca0 CEngine__SetVertexShadersEnabled` | `int __thiscall CEngine__SetVertexShadersEnabled(void * this, uchar enabled)` | Updates shader-path global `DAT_00889070`, clears cached shader-object/handle globals, and returns the first device-call result. |
| `0x00513d20 D3DBufferRegistry__MoveToFreeList` | `void __stdcall D3DBufferRegistry__MoveToFreeList(int buffer_node)` | Moves a node from active list `DAT_00889074` to free list `DAT_00889078`; xrefs include `CFastVB` and bitmap-font resource paths. |
| `0x00513e00 CEngine__DeviceCall118_WithZeroOut` | `void __fastcall CEngine__DeviceCall118_WithZeroOut(void * this)` | Passes a zeroed stack output dword to device vtable slot `0x118`; callers include message-box, landscape, mesh, VBufTexture, and water paths. |
| `0x00513e20 CEngine__SetShaderObject` | `void __thiscall CEngine__SetShaderObject(void * this, void * shader_obj)` | Binds a shader object by caching `DAT_0088906c`, sending `CVertexShader__GetVertexDeclarationToken(shader_obj)` to slot `0x164`, sending `shader_obj+0x28` to slot `0x170`, then disabling the legacy shader path. |
| `0x00513e90 CEngine__SetVertexShaderHandleCached` | `void __thiscall CEngine__SetVertexShaderHandleCached(void * this, int shader_handle)` | Cached vertex-shader handle setter; skips device slot `0x164` when `DAT_00889068` already matches. |
| `0x00513ec0 CEngine__SetVertexShaderHandleRaw` | `void __thiscall CEngine__SetVertexShaderHandleRaw(void * this, int shader_handle)` | Raw handle setter; clears shader-object cache `DAT_0088906c`, sends zero to slot `0x170`, sends the handle to slot `0x164`, then disables the legacy shader path. |
| `0x00513f20 CEngine__CreatePixelShaderFromText` | `int __thiscall CEngine__CreatePixelShaderFromText(void * this, char * shader_text, void * release_after_create)` | Compiles shader text through `CVertexShader__CompileScriptWithDirectiveParser`, raises localized fatal `0xd2` on compile failure, calls device slot `0x1a8`, releases local resources, returns the device result, and exits with `RET 0x8`. |
| `0x00513ff0 CEngine__DeviceCall16C_CreateVertexShaderLike` | `int __thiscall CEngine__DeviceCall16C_CreateVertexShaderLike(void * this, int unused_arg1, int arg2, int arg3, int unused_arg4)` | Bounded rename from `CEngine__DeviceCall16C_Arg2Arg3`; forwards only caller arg2/arg3 to device vtable slot `0x16c`, returns device `EAX`, exits with `RET 0x10`, and all callsites test the result. |
| `0x00514010 IUnknown__ReleaseAndNull` | `void __stdcall IUnknown__ReleaseAndNull(void * * object_ptr)` | Releases `*object_ptr` through COM vtable slot `8` when non-null, writes null back, and returns with `RET 0x4`. |

Read-back evidence:

- `ApplyD3DShaderInputTailWave850.java dry`: `updated=0 skipped=13 renamed=0 would_rename=1 signature_updated=1 comment_only_updated=13 missing=0 bad=0`
- `ApplyD3DShaderInputTailWave850.java apply`: `updated=13 skipped=0 renamed=1 would_rename=1 signature_updated=1 comment_only_updated=13 missing=0 bad=0`
- `ApplyD3DShaderInputTailWave850.java final dry`: `updated=0 skipped=13 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: `13` metadata rows, `13` tag rows, `74` xref rows, `637` instruction rows, and `13` decompile rows.
- Additional read-only evidence: `18` context metadata rows, `18` context decompile rows, `1998` xref-site instruction rows, and `1937` target-long instruction rows.
- Queue after Wave850: `6098` total functions, `5704` commented, `394` commentless, `0` exact-undefined signatures, `0` `param_N`, comment-backed proxy `5704/6098 = 93.54%`, strict clean-signature proxy `5704/6098 = 93.54%`.
- Next raw commentless row: `0x005140e0 CDXEngine__CaptureAviFrame`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260525-081702_post_wave850_d3d_shader_input_tail_verified`, `19` files, `171969415` bytes, `DiffCount=0`.

What this proves:

- The thirteen target rows exist in the saved Ghidra project with the Wave850 comments, tags, and signatures above.
- `0x00513ff0` has a bounded shader-create-context name/signature correction and is no longer treated as a void/no-result wrapper.
- The rows are important static connector infrastructure for input state, Direct3D draw/state dispatch, shader mode/object/handle binding, pixel/vertex shader creation, buffer-list lifetime, and COM-style resource release.

What remains unproven:

- Exact Direct3D interface version and exact COM method names.
- Concrete key-state, shader-object, buffer-node, and device/cache layouts.
- Runtime input, rendering, shader compilation, shader creation, and resource lifetime behavior.
- BEA patching behavior.
- Rebuild parity.
