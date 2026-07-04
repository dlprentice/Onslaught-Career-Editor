# Ghidra D3D State/Cache Core Wave849 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-25
Scope: `d3d-state-cache-core-wave849`

Wave849 D3D state/cache core saved comments, tags, one bounded name correction, and six signature corrections for thirteen important Direct3D device, render-state cache, and texture-resource connector rows from `0x00513640 CEngine__GetConstant32` through `0x00513a10 CEngine__CreateTextureUnchecked`. The pass made one rename, no function-boundary changes, and no executable-byte changes.

Representative anchors:

| Address | Saved state | Evidence |
| --- | --- | --- |
| `0x00513640 CEngine__GetConstant32` | `int __cdecl CEngine__GetConstant32(void)` | Returns constant `0x20`; xrefs include `CDXTexture__Deserialize`, `CDXTexture__LoadTextureFromFile_Core`, and `CTextureSequence__EnsureLoaded`. |
| `0x00513650 CEngine__PrintGraphicsCardInfo` | `void __cdecl CEngine__PrintGraphicsCardInfo(void)` | `cg_whatami`/`con_whatami` style graphics-card report; prints `Graphics card info`, description, driver, driver version, and pure/impure device strings. |
| `0x00513730 CEngine__MarkDeviceResetPending` | `void __cdecl CEngine__MarkDeviceResetPending(void)` | `CD3DApplication__MsgProc` caller; writes the lost/reset state globals `0x008a9acc`, `0x008a9ac0`, and `0x008a956c`. |
| `0x00513760 CEngine__TextureFormatField32FD4ToIndex` | `int __fastcall CEngine__TextureFormatField32FD4ToIndex(void * this)` | Renamed from stale `CEngine__ReleaseField32FD4`; loads `this+0x32fd4`, calls `CEngine__TextureFormatD3DToIndex`, and callers use `EAX` as a texture-format index. |
| `0x00513770 CEngine__DeviceCall68_CheckError` | `int __thiscall CEngine__DeviceCall68_CheckError(void * this, int arg2, int arg3, int arg4, int arg5, int arg6)` | Dispatches device vtable slot `0x68`, returns HRESULT-like value, and logs `D3D Error!` plus `HResultToString` on failure. |
| `0x005137d0 CEngine__DeviceCall6C` | `int __thiscall CEngine__DeviceCall6C(void * this, int arg2, int arg3, int arg4, int arg5, int arg6)` | Dispatches device vtable slot `0x6c`; `CIBuffer`, landscape index-buffer, and `CDXMeshVB` callers test `EAX`. |
| `0x00513800 IUnknown__ReleaseIfNonNull_ReturnZero` | `int __stdcall IUnknown__ReleaseIfNonNull_ReturnZero(void * obj)` | Releases non-null COM-style object via vtable slot `8` and returns zero. |
| `0x00513820 D3DStateCache__SetStateCached` | `void __stdcall D3DStateCache__SetStateCached(int state_slot, int state_id, int value)` | Cached vtable slot `0x10c` helper over `DAT_008557f0`; 419 xref rows across console, HUD, frontend, landscape, mesh, particle, water, and CDXEngine render paths. |
| `0x00513870 D3DStateCache__SetStateRaw` | `void __stdcall D3DStateCache__SetStateRaw(int state_slot, int state_id, int value)` | Raw vtable slot `0x10c` helper that writes the cache and always calls the device. |
| `0x005138b0 D3DStateCache__SetState114Cached` | `void __stdcall D3DStateCache__SetState114Cached(int state_slot, int state_id, uint value)` | Cached vtable slot `0x114` helper with state `6`, `8`, and `10` capability/clamp policy. |
| `0x00513930 D3DStateCache__SetState114Raw` | `void __stdcall D3DStateCache__SetState114Raw(int state_slot, int state_id, uint value)` | Raw slot `0x114` policy helper with 192 xref rows across frontend, HUD, CDXEngine, landscape, imposter, particle, water, and tree render paths. |
| `0x005139a0 CEngine__CreateTextureOrFatal` | `int __thiscall CEngine__CreateTextureOrFatal(void * this, int arg2, int arg3, int arg4, int arg5, int arg6, int arg7, int arg8)` | Device vtable slot `0x5c` texture-create wrapper; on failure prints `Create texture failed: %s` and calls `FatalError_LocalizedStringId(0, 0xca, -1)`. |
| `0x00513a10 CEngine__CreateTextureUnchecked` | `int __thiscall CEngine__CreateTextureUnchecked(void * this, int arg2, int arg3, int arg4, int arg5, int arg6, int arg7, int arg8)` | Unchecked device vtable slot `0x5c` texture-create wrapper; `CDXTexture`, `CUMTexture`, and texture-sequence callers test `EAX`. |

Read-back evidence:

- `ApplyD3DStateCacheCoreWave849.java dry`: `updated=0 skipped=13 renamed=0 would_rename=1 signature_updated=6 comment_only_updated=13 missing=0 bad=0`
- `ApplyD3DStateCacheCoreWave849.java apply`: `updated=13 skipped=0 renamed=1 would_rename=1 signature_updated=6 comment_only_updated=13 missing=0 bad=0`
- `ApplyD3DStateCacheCoreWave849.java final dry`: `updated=0 skipped=13 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: `13` metadata rows, `13` tag rows, `765` xref rows, `637` instruction rows, and `13` decompile rows.
- Additional read-only evidence: `19` context metadata rows, `19` context decompile rows, `76` release-field xref-site instruction rows, `208` return-use xref-site instruction rows, and graphics-card/texture/D3D error string dumps.
- Queue after Wave849: `6098` total functions, `5691` commented, `407` commentless, `0` exact-undefined signatures, `0` `param_N`, comment-backed proxy `5691/6098 = 93.33%`, strict clean-signature proxy `5691/6098 = 93.33%`.
- Next raw commentless row: `0x00513a80 PlatformInput__GetKeyState3Core`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260525-073710_post_wave849_d3d_state_cache_core_verified`, `19` files, `171936647` bytes, `DiffCount=0`.

What this proves:

- The thirteen target rows exist in the saved Ghidra project with the Wave849 comments, tags, and signatures above.
- The stale `CEngine__ReleaseField32FD4` label was corrected to `CEngine__TextureFormatField32FD4ToIndex` from static caller/use evidence.
- The rows are static connector infrastructure for Direct3D device calls, render-state cache policy, texture creation, texture-format mapping, and COM-style resource release.

What remains unproven:

- Exact Direct3D enum names and concrete field names.
- Exact adapter, cache, texture-resource, and device-interface layouts.
- Runtime D3D device/reset/texture/render behavior.
- BEA patching behavior.
- Rebuild parity.
