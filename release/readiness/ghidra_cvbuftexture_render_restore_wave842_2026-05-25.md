# Ghidra CVBufTexture Render Restore Wave842 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-25
Scope: `cvbuftexture-render-restore-wave842`

Wave842 CVBufTexture render restore saved signature/comment/tag hardening for `0x0050ab60 CVBufTexture__RenderAndRestoreStateFlag4`. The pass made no rename, no function-boundary change, and no executable-byte change.

Representative anchors:

| Address / area | Evidence |
| --- | --- |
| `0x0050ab60 CVBufTexture__RenderAndRestoreStateFlag4` | Saved as `void __stdcall CVBufTexture__RenderAndRestoreStateFlag4(void * dynamic_context, int unused_zero_arg, int enable_dynamic_flag_source)`. |
| `0x0053e77d CDXEngine__Render` | Sole xref; caller pushes dynamic context from `[EBP+0x470]`, zero, and zero-extended byte `DAT_009c7c56`. |
| Body ABI | `RET 0xc`; reads stack arg1 into `ECX`, ignores stack arg2, tests stack arg3, and forwards that nonzero result into `CVBufTexture__RenderDynamicUnitPass`. |
| Render-state path | Calls `CVBufTexture__SetStateCacheModeByFlag(1)` before and after the dynamic-unit pass; if `DAT_0089ce54 bit 4` is set, calls `RenderState__Set0x89_Zero`. |

Read-back evidence:

- `ApplyCVBufTextureRenderRestoreWave842.java dry`: `updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0`
- `ApplyCVBufTextureRenderRestoreWave842.java apply`: `READBACK_OK`, `updated=1 skipped=0 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0`
- `ApplyCVBufTextureRenderRestoreWave842.java final dry`: `updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 1 metadata row, 1 tag row, 1 xref row, 261 instruction-window rows, 521 target-deep instruction rows, 71 xref-site instruction rows, 1 target decompile row, and 10 context metadata/tag/decompile rows.
- Queue after Wave842: 6098 total functions, 5666 commented, 432 commentless, 0 exact-undefined signatures, 0 `param_N` signatures, comment-backed proxy `5666/6098 = 92.92%`, strict clean-signature proxy `5666/6098 = 92.92%`.
- Next raw commentless row: `0x0050b030 OID__TraceLineAndSelectBestTargetHit`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260525-035851_post_wave842_cvbuftexture_render_restore_verified`, 19 files, 171838343 bytes, `DiffCount=0`.

What this proves:

- The target function exists in the saved Ghidra project.
- The saved signature/comment/tags match the observed retail ABI and render-state wrapper evidence.
- The sole caller, local body, post-decompile signature, queue telemetry, and verified backup were read back after apply.

What remains unproven:

- Exact source function identity.
- Dynamic-pass parameter semantics beyond observed stack forwarding.
- Exact render-state table/layout semantics.
- Runtime rendering behavior.
- BEA patching behavior.
- Rebuild parity.
