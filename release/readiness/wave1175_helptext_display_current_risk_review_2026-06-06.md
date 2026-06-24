# Wave1175 HelpTextDisplay Current-Risk Review Readiness

Status: complete static read-only evidence
Date: 2026-06-06
Scope: `wave1175-helptext-display-current-risk-review`

Wave1175 accounts for `3 HelpTextDisplay current-risk rows` from the Wave1108 current-risk denominator. Fresh serialized Ghidra exports verified the selected rows and found no Ghidra mutation warranted.

| Address | Saved row | Read-back evidence |
| --- | --- | --- |
| `0x0047fab0` | `CHelpTextDisplay__ctor` | Call xref `0x0046c769 CGame__InitRestartLoop`; clears two queued-message active slots, installs `PTR_CHelpTextDisplay__scalar_deleting_dtor_005dbdf8`, and returns `this`. |
| `0x0047fb00` | `CHelpTextDisplay__QueueMessageWithTimestamp` | Call xref `0x00533b5d`; writes message pointer, timestamp `DAT_00672fd0`, and active flag into one of two queue slots, with overflow logging through `CConsole__Printf`. |
| `0x0047fb50` | `CHelpTextDisplay__RenderQueuedMessages` | Call xref `0x00487b83 CHud__RenderOverlayForViewpoint`; wraps through `TextLayout__WrapWideTextToFixedLines`, measures/draws through `CDXFont__GetTextExtent` and `CDXFont__DrawTextDynamic`, and expires old queue slots. |

Fresh evidence:

- `3` metadata rows, `3` tag rows, `3 xref rows`, `169 instruction rows`, and `3` decompile rows.
- Logs reported `targets=3 found=3 missing=0`, `rows=3 missing=0`, `Wrote 3 rows`, `Wrote 169 function-body instruction rows`, and `targets=3 dumped=3 missing=0 failed=0`.
- Verified backup: `G:\GhidraBackups\BEA_20260606-082238_post_wave1175_helptext_display_current_risk_review_verified`, `19` files, `176065415` bytes, `DiffCount=0`, `HashDiffCount=0`.
- Current-risk accounting moved from `680/1179 = 57.68%` to `683/1179 = 57.93%`; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 496; current risk candidates: 6166.

Mutation status: read-only review; no rename, no signature change, no comment/tag change, no function-boundary change, no executable-byte change, no BEA launch, no installed-game mutation, no save mutation, and no runtime-file mutation.

Prior context: Wave397 `help-hive-wave397` corrected older HelpTextDisplay owner evidence, and Wave1005 `help-text-display-review-wave1005` re-read the broader HelpTextDisplay set.

Boundary: runtime HelpText behavior, runtime HUD/text rendering behavior, exact HelpTextDisplay/HUD/font/text-layout layouts, exact source-body identity, BEA patching behavior, visual QA, gameplay outcomes, and rebuild parity remain separate proof.

Probe token anchor: Wave1175; wave1175-helptext-display-current-risk-review; 683/1179 = 57.93%; 3 HelpTextDisplay current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 496; current risk candidates: 6166; fresh Ghidra export; read-only review; no mutation; Codex root final judgment; 0 / 0 / 0; 6411/6411 = 100.00%; 3 xref rows; 169 instruction rows; CHelpTextDisplay__ctor; CHelpTextDisplay__QueueMessageWithTimestamp; CHelpTextDisplay__RenderQueuedMessages; CGame__InitRestartLoop; CHud__RenderOverlayForViewpoint; TextLayout__WrapWideTextToFixedLines; CDXFont__DrawTextDynamic; Wave397; help-hive-wave397; Wave1005; help-text-display-review-wave1005; G:\GhidraBackups\BEA_20260606-082238_post_wave1175_helptext_display_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.
