# Ghidra Fatal Error Spine Review Wave998 Readiness Note

Status: complete saved static read-back correction
Date: 2026-05-31
Scope: `fatal-error-spine-review-wave998`

Wave998 re-reviewed the Wave911-focused fatal-error spine around `0x0042c750 FatalError__ExitWithLocalizedPrefix_A` and `0x0042d0b0 FatalError__ExitWithLocalizedPrefix_B`, with `0x0042cfa0 FatalError__ExitProcess` and `0x0042d080 FatalError_LocalizedStringId` as context rows. Fresh metadata, tag, xref, instruction, and decompile exports showed both localized-prefix wrappers unconditionally tail into the already no-return `FatalError__ExitProcess`, so this wave saved no-return signature/comment/tag corrections for the two wrappers.

Primary corrections:

| Address | Saved state | Evidence |
| --- | --- | --- |
| `0x0042c750 FatalError__ExitWithLocalizedPrefix_A` | `noreturn void __stdcall FatalError__ExitWithLocalizedPrefix_A(char * message, int callerContext)` | Builds a 400-byte localized prefix buffer from localization id `0xcc`, separator string `0x00624624`, and caller message text, then calls `0x0042cfa0 FatalError__ExitProcess` at `0x0042c7ef`. Metadata and `RET 0x8` shape still preserve the second stack argument as `callerContext`; current decompile does not prove semantic use by the body. |
| `0x0042d0b0 FatalError__ExitWithLocalizedPrefix_B` | `noreturn void __stdcall FatalError__ExitWithLocalizedPrefix_B(char * message)` | Builds the same localized prefix/message buffer and calls `0x0042cfa0 FatalError__ExitProcess` at `0x0042d14f`. Mesh/resource deserialize xrefs include `0x004aad6c CMesh__Deserialize` and no-function caller `0x0054d2cb`; `RET 0x4` shape preserves one stack argument. |

Context rows:

- `0x0042cfa0 FatalError__ExitProcess` was already saved as `noreturn void __cdecl FatalError__ExitProcess(char * message, int code)`.
- `0x0042d080 FatalError_LocalizedStringId` remains a guard-gated localized-string wrapper with broad D3D/display/buffer/shader/texture/compass/video/memory/atmospherics callers.

Read-back evidence:

- `ApplyFatalErrorSpineWave998.java` dry: `updated=0 skipped=2 no_return_updated=2 comment_only_updated=0 tags_added=12 missing=0 bad=0`
- `ApplyFatalErrorSpineWave998.java` apply: `updated=2 skipped=0 no_return_updated=2 comment_only_updated=0 tags_added=12 missing=0 bad=0`
- `ApplyFatalErrorSpineWave998.java` final dry: `updated=0 skipped=2 no_return_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0`
- Post exports verified `4` metadata rows, `4` tag rows, `71` xref rows, `209` body-instruction rows, and `4` decompile rows.
- Queue closure remains `6222/6222 = 100.00%`.
- Wave911 focused re-audit progress is now `467/1408 = 33.17%`.
- Expanded static surface progress is now `585/1478 = 39.58%`.
- Verified backup: `G:\GhidraBackups\BEA_20260531-091151_post_wave998_fatal_error_spine_review_verified`, `19` files, `173869959` bytes, `DiffCount=0`, `HashDiffCount=0`.

Probe token anchor: Wave998; `fatal-error-spine-review-wave998`; `0x0042c750 FatalError__ExitWithLocalizedPrefix_A`; `noreturn void __stdcall FatalError__ExitWithLocalizedPrefix_A(char * message, int callerContext)`; `0x0042d0b0 FatalError__ExitWithLocalizedPrefix_B`; `noreturn void __stdcall FatalError__ExitWithLocalizedPrefix_B(char * message)`; `0x0042cfa0 FatalError__ExitProcess`; `0x0042d080 FatalError_LocalizedStringId`; `467/1408 = 33.17%`; `585/1478 = 39.58%`; `6222/6222 = 100.00%`; `G:\GhidraBackups\BEA_20260531-091151_post_wave998_fatal_error_spine_review_verified`.

What this proves:

- The two localized fatal wrappers exist in the saved Ghidra project with no-return signatures, Wave998 comments, and `fatal-error-spine-review-wave998` / `wave998-readback-verified` tags.
- The reviewed wrappers unconditionally flow to the already no-return `FatalError__ExitProcess` in the observed static retail body.
- The saved stack-argument shapes remain bounded by metadata/instruction evidence: two arguments for wrapper A and one argument for wrapper B.

What remains unproven:

- Runtime fatal UI/error presentation.
- Exact source-body identity.
- Exact source layout/type identity.
- Full format/resource ownership for every caller.
- BEA patching behavior.
- Rebuild parity.
