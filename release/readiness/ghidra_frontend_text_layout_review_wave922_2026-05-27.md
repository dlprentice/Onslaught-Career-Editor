# Ghidra Wave922 frontend text/layout review (2026-05-27)

Status: read-only static review
Date: 2026-05-27
Branch: `main`
Tag: `frontend-text-layout-review-wave922`

## Scope

Wave922 reviewed the shared frontend text/layout cluster from the Wave911 focused correction queue and adjacent Wave376/Wave378 context:

| Address | Saved name | Result |
| --- | --- | --- |
| `0x00465a20` | `TextLayout__WrapWideTextToFixedLines` | Reviewed; no mutation |
| `0x00469c20` | `CFrontEnd__ResolveEpisodeNameTextByIndex` | Reviewed; no mutation |
| `0x00469cf0` | `CFrontEnd__ResolveLevelNameTextIdByCode` | Reviewed; no mutation |
| `0x0046a1f0` | `FrontEndText__GetLevelNameTextAfterCode` | Reviewed; no mutation |
| `0x0046a210` | `FrontEnd__GetBriefingLevelListTextColor` | Reviewed; no mutation |
| `0x0046a220` | `FrontEndText__GetMultiplayerLevelDescriptionByType` | Reviewed; no mutation |
| `0x0046a2a0` | `FrontEndText__GetLocalizedOrFallbackTextByToken` | Reviewed; no mutation |
| `0x0046b1e0` | `FrontEndText__GetAsciiFallbackTextByToken` | Reviewed; no mutation |

## Evidence

Private artifacts:

```text
subagents/ghidra-static-reaudit/wave922-frontend-text-layout-review/metadata.tsv
subagents/ghidra-static-reaudit/wave922-frontend-text-layout-review/tags.tsv
subagents/ghidra-static-reaudit/wave922-frontend-text-layout-review/instructions.tsv
subagents/ghidra-static-reaudit/wave922-frontend-text-layout-review/xrefs.tsv
subagents/ghidra-static-reaudit/wave922-frontend-text-layout-review/decompile/
```

Read-back result:

```text
metadata: 8/8 OK
tags: 8/8 OK
xrefs: 114 rows
instructions: 1553 rows
decompile: 8/8 OK
```

## Review Result

The saved names/signatures/comments remain appropriate for the current evidence. `TextLayout__WrapWideTextToFixedLines` still has broad xrefs from frontend dialogs, language-test rendering, gameplay overlays, help text, briefing logs, and local co-op prompts; the body clears fixed line slots, measures candidate lines through `CDXFont__GetTextExtent`, trims spaces, and returns the line count.

The frontend text-token helpers remain coherent with the prior Wave378 corrections: `FrontEndText__GetLocalizedOrFallbackTextByToken` is a broad frontend resolver rather than a save-game-only helper, and `FrontEndText__GetAsciiFallbackTextByToken` is its shared ASCII fallback path. The multiplayer description, level-name, episode-name, and briefing-color helpers also retain their saved static evidence boundaries.

No Ghidra mutation was performed.

## Backup

Read-only post-wave backup:

```text
G:\GhidraBackups\BEA_20260527-175851_post_wave922_frontend_text_layout_review_verified
files=19
bytes=173247367
```

## Truth boundary

This review confirms static Ghidra coherence for selected frontend text/layout helpers. It does not prove runtime frontend localization, text wrapping, briefing rendering, fallback-toggle behavior, concrete frontend/text layouts, BEA patch behavior, or rebuild parity.

## Next

Continue Wave923 with another focused cluster from Wave911, preferably remaining frontend/render helpers or another stale-owner/source-evidenced family.
