# Ghidra Level Briefing Render Wave808 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-24
Scope: `level-briefing-render-wave808`

Wave808 level-briefing render saved a one-row owner/name/signature/comment/tag correction for `0x0048f620`, replacing stale `CDXEngine__RenderPostMissionOverlayAndMenu` with `CLevelBriefingLog__Render`. Exact anchor: `0x0048f620 CLevelBriefingLog__Render`. The pass made no function-boundary changes and no executable-byte changes.

| Address | Saved state | Evidence |
| --- | --- | --- |
| `0x0048f620` | `void __thiscall CLevelBriefingLog__Render(void * this, void * viewport)` | `CDXEngine__PostRender` callsite `0x0053ee12` loads `ECX` from `DAT_008a9d94`, `0x0053ee18` pushes the viewport/render context, and `0x0053ee19` calls this function. The callee moves `ECX` to `EDI` and exits with `RET 0x4`. Stuart-source context in `references/Onslaught/DXEngine.cpp` calls `GAME.GetLevelBriefingLog()->Render(viewport)` between `GAME.GetMessageLog()->Render(viewport)` and `GAME.GetPauseMenu()->Render()`. |

Read-back evidence:

- `ApplyLevelBriefingRenderWave808.java dry`: `updated=0 skipped=1 renamed=0 would_rename=1 signature_updated=1 comment_only_updated=0 missing=0 bad=0`
- `ApplyLevelBriefingRenderWave808.java apply`: `updated=1 skipped=0 renamed=1 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0`
- `ApplyLevelBriefingRenderWave808.java final dry`: `updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 1 metadata row, 1 tag row, 1 xref row, 1201 instruction rows, 1 decompile row, 86 post-callsite instruction rows, and 1 post-caller decompile row.
- Queue after Wave808: 6098 total, 5583 commented, 515 commentless, 0 exact-undefined signatures, 0 `param_N`, comment-backed proxy `5583/6098 = 91.55%`, strict clean-signature proxy `5583/6098 = 91.55%`.
- Next raw commentless row: `0x004901e0 MathMatrix3x4__AssignFromEightScalars`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260524-113054_post_wave808_level_briefing_render_verified`, 19 files, 171314055 bytes, `DiffCount=0`.

What this proves:

- The saved Ghidra function row exists at `0x0048f620`.
- The saved name is `CLevelBriefingLog__Render`.
- The saved signature is `void __thiscall CLevelBriefingLog__Render(void * this, void * viewport)`.
- The saved comment and tags include `level-briefing-render-wave808` and `wave808-readback-verified`.
- The source-aligned owner correction is supported by the saved caller/callsite/decompile/read-back evidence.

What remains unproven:

- Exact concrete `CLevelBriefingLog` layout.
- Exact level/result text-table semantics.
- Runtime level briefing/post-mission overlay behavior.
- BEA patching behavior.
- Rebuild parity.
