# Ghidra CVertexShader Lifecycle Review Wave961

Status: bounded static mutation PASS
Date: 2026-05-28
Tag: `cvertexshader-lifecycle-review-wave961`

Wave961 re-reviewed the CVertexShader lifecycle/device-creation slice after static export-contract closure. The wave saved one bounded Ghidra mutation: it recovered the missing CVertexShader vtable slot-2 function boundary at `0x00501a10` as `CVertexShader__VFunc_02_00501a10`. The saved name is a conservative vtable-slot label, not a source method identity claim. The pass made no executable-byte change and did not launch BEA.

## Scope

Primary Wave911 candidate and mutation target:

| Address | Saved name | Result |
| --- | --- | --- |
| `0x00501890` | `CVertexShader__scalar_deleting_dtor` | Live Wave533 scalar-deleting destructor evidence still holds; no mutation needed. |
| `0x00501a10` | `CVertexShader__VFunc_02_00501a10` | Boundary recovered from CVertexShader vtable `0x005dfbc4 slot 2`; pre-vtable export reported `NO_FUNCTION_AT_POINTER`, post-vtable export reports `OK`. |

Context anchors re-read: `0x005016b0 InitShaderCapabilityFlagsAndCVar`, `0x00501730 CVertexShader__ClearOut`, `0x00501800 CVertexShader__CVertexShader`, `0x005018b0 CVertexShader__dtor`, `0x005019c0 VFuncSlot_09_005019c0`, `0x005019d0 CVertexShader__QueryDeviceCapsAndSetGlobalSupportFlag`, `0x00501b60 CVertexShader__VFunc_03_00501b60`, `0x00501ba0 CVertexShader__GetVertexDeclarationToken`, `0x00501cd0 CVertexShader__ApplyRenderStateShaderConstants`, `0x00502060 CVertexShader__Create`, `0x00502290 CVertexShader__DecrementLiveReferenceCount`, `0x005022a0 CVertexShader__LoadFromFile`, `0x00502420 CVertexShader__CompileShader`, `0x005027f0 CVertexShader__LoadCompiledShaderBlobFromVSOFile`, `0x00502920 CVertexShader__ApplyCustomRenderStateShaderConstants`, `0x00503ac0 CVertexShader__BuildAndCreateRenderInfoShader`, `0x00503dd0 CVertexShader__AppendDeclarationNamesToDebugString`, `0x00503f90 CVertexShader__Clone`, `0x005042f0 CVertexShader__DeserializeAll`, `0x00512ca0 CShaderBase__Init`, `0x00512cc0 CShaderBase__UnlinkFromRenderObjectLists`, `0x00513e20 CEngine__SetShaderObject`, `0x00513e90 CEngine__SetVertexShaderHandleCached`, `0x00513ec0 CEngine__SetVertexShaderHandleRaw`, `0x00513f20 CEngine__CreatePixelShaderFromText`, and `0x00513ff0 CEngine__DeviceCall16C_CreateVertexShaderLike`.

## Evidence

Fresh serialized Ghidra exports under `subagents/ghidra-static-reaudit/wave961-cvertexshader-lifecycle-review`:

- Pre-mutation exports: `27` metadata rows, `27` tag rows, `106` xref rows, `2835` around-address instruction rows, `3239` function-body instruction rows, `27` decompile-index rows, `12` vtable rows, and `122` slot-2 probe instruction rows.
- Pre-vtable slot evidence: `0x005dfbc4 slot 2` pointed to `0x00501a10` with `NO_FUNCTION_AT_POINTER`.
- Mutation dry/apply/final dry: `updated=0 skipped=0 created=0 would_create=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`, then `updated=1 skipped=0 created=1 would_create=0 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0`, then `updated=0 skipped=1 created=0 would_create=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Comment-refinement dry/apply/final dry: `comment_only_updated=1`, then `updated=1 ... comment_only_updated=1`, then clean final dry with `updated=0 skipped=1 ... missing=0 bad=0`.
- Post-mutation exports: `28` metadata rows, `28` tag rows, `107` xref rows, `2940` around-address instruction rows, `3355` function-body instruction rows, `28` decompile-index rows, and `12` vtable rows.

Representative anchors:

| Evidence | Anchor |
| --- | --- |
| Vtable slot-2 before recovery | `0x005dfbc4 slot 2 -> 0x00501a10`, `NO_FUNCTION_AT_POINTER`. |
| Vtable slot-2 after recovery | `0x005dfbc4 slot 2 -> 0x00501a10 CVertexShader__VFunc_02_00501a10`, `OK`. |
| Function start follows the caps helper | `0x005019d0 CVertexShader__QueryDeviceCapsAndSetGlobalSupportFlag` returns at `0x00501a08`; recovered body starts at `0x00501a10`. |
| Device caps and shader-support gate | `0x00501a10 MOV EAX, [0x00888c8c]`; `0x00501a38 CMP ... 0xfffe0101`; `DAT_00854e6c`. |
| Compiled-blob create path | `0x00501a88 CALL 0x00513ff0 CEngine__DeviceCall16C_CreateVertexShaderLike`; failure path returns `0x80004005`. |
| Named `.vso` fallback path | `0x00501b23 CALL 0x005027f0 CVertexShader__LoadCompiledShaderBlobFromVSOFile`; failure path returns `0x80004005`. |
| Engine vertex-shader enable toggle | `0x00501a53` and `0x00501b4c` call `CEngine__SetVertexShadersEnabled`. |

Verified Ghidra backup:

```text
[maintainer-local-ghidra-backup-root]\BEA_20260528-125650_post_wave961_cvertexshader_lifecycle_review_verified
```

Backup summary: `19` files, `173542279` bytes, `DiffCount=0`.

Wave911 focused re-audit progress after Wave961: `306/1408 = 21.73%`.
Static export-contract function-quality closure remains `6152/6152 = 100.00%`.

Probe anchor: Wave961; cvertexshader-lifecycle-review-wave961; 0x00501890 CVertexShader__scalar_deleting_dtor; 0x00501a10 CVertexShader__VFunc_02_00501a10; 0x005dfbc4 slot 2; NO_FUNCTION_AT_POINTER; CEngine__DeviceCall16C_CreateVertexShaderLike; CVertexShader__LoadCompiledShaderBlobFromVSOFile; 0x80004005; 0xfffe0101; DAT_00854e6c; DAT_00888c8c; 306/1408 = 21.73%; 6152/6152 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260528-125650_post_wave961_cvertexshader_lifecycle_review_verified; function-boundary recovery.

## Boundary

This wave proves only saved static retail Ghidra evidence for the CVertexShader slot-2 boundary and its observed device-create/load branches. Exact source virtual name, exact `CVertexShader` / `CShaderBase` layout, runtime shader compile/load/bind behavior, graphics-driver behavior, BEA patching, and rebuild parity remain separate proof.
