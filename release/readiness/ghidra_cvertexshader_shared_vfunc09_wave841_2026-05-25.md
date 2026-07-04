# Ghidra CVertexShader Shared VFunc09 Wave841 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-25
Scope: `cvertexshader-shared-vfunc09-wave841`

Wave841 Shared Default/False VFunc09 saved a bounded signature/comment/tag hardening for `0x005019c0 VFuncSlot_09_005019c0`. The function is a shared default/false virtual stub, not disposable filler: its body is `XOR EAX,EAX; RET`, and post-readback evidence ties it to frontend-development direct calls plus multiple RTTI-backed vtable owner rows. The pass made no rename, no function-boundary change, and no executable-byte change.

Representative anchors:

| Address / area | Evidence |
| --- | --- |
| `0x005019c0 VFuncSlot_09_005019c0` | Saved as `int __cdecl VFuncSlot_09_005019c0(void)` with `cvertexshader-shared-vfunc09-wave841` and `wave841-readback-verified` tags. |
| Body | Instruction export shows `XOR EAX,EAX; RET`, so the stub returns zero without reading ECX or stack arguments. |
| Direct calls | Four direct frontend-development callsites: `0x00458662`, `0x00458a46`, `0x00458d32`, and `0x00458d4f`; callsite exports show callers immediately test `EAX` as a boolean/result gate. |
| DATA slots | Xref export shows `26 DATA pointer slots`; RTTI candidate resolution produced `36` valid vtable bases and `49 RTTI-backed owner/slot rows` pointing at the stub. |
| Owner examples | `CControllerDefinition` slot 7, `CVertexShader` slots 1 and 4, `CDXTrees` slot 1, plus destroyable segment/component, motion-controller, `CVBuffer`, `CVertexShaderMenu`, CDX frontend/media/render helpers, and `CDXTexture` owner rows. |
| Deferred boundary | `CVertexShader` vtable slot 2 at `0x00501a10` remains an unrecovered no-function-at-pointer boundary from prior CVertexShader work. |

Read-back evidence:

- `ApplyCVertexShaderSharedVFunc09Wave841.java dry`: `updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0`
- `ApplyCVertexShaderSharedVFunc09Wave841.java apply`: `updated=1 skipped=0 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0`
- `ApplyCVertexShaderSharedVFunc09Wave841.java final dry`: `updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: `1` metadata row, `1` tag row, `30` xref rows, `229` instruction-window rows, `481` target-deep instruction rows, `580` callsite instruction rows, `462` RTTI candidate rows, `864` vtable-slot rows, and `1` target decompile row.
- Queue after Wave841: `6098` total functions, `5665` commented, `433` commentless, `0` exact-undefined signatures, `0` `param_N` signatures, comment-backed proxy `5665/6098 = 92.90%`, strict clean-signature proxy `5665/6098 = 92.90%`.
- The commentless high-signal, signature, and name-confidence queues remain empty.
- Next raw commentless row: `0x0050ab60 CVBufTexture__RenderAndRestoreStateFlag4`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260525-032940_post_wave841_cvertexshader_shared_vfunc09_verified`, `19` files, `171838343` bytes, `DiffCount=0`.

What this proves:

- The saved Ghidra row exists with `int __cdecl VFuncSlot_09_005019c0(void)`.
- The saved comment and tags include `cvertexshader-shared-vfunc09-wave841` and `wave841-readback-verified`.
- Static retail evidence supports treating this row as shared default/false virtual infrastructure used by several vtable families and frontend-development call paths.

What remains unproven:

- Exact source virtual method names.
- Caller-specific semantics beyond the observed false/default boolean result behavior.
- Concrete class layouts for every RTTI-backed owner row.
- Runtime behavior.
- BEA patching behavior.
- Rebuild parity.
