# Wave1175 HelpTextDisplay Current-Risk Review

Status: complete static read-only evidence
Date: 2026-06-06
Scope: `wave1175-helptext-display-current-risk-review`

Wave1175 accounts for `3 HelpTextDisplay current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator with fresh Ghidra export evidence. It is a read-only review with no mutation, no rename, no signature change, no comment/tag change, no function-boundary change, and no executable-byte change.

| Address | Saved row | Static evidence |
| --- | --- | --- |
| `0x0047fab0` | `CHelpTextDisplay__ctor` | `0x0046c769 CGame__InitRestartLoop` call xref; clears two queued-message active slots, installs `PTR_CHelpTextDisplay__scalar_deleting_dtor_005dbdf8`, and returns `this`. |
| `0x0047fb00` | `CHelpTextDisplay__QueueMessageWithTimestamp` | `0x00533b5d` call xref; writes message pointer, global timestamp `DAT_00672fd0`, and active flag into one of two `0x0c`-byte queue slots, with overflow logging through `CConsole__Printf` and `s_ERROR__Added_too_many_messages_t_0062cc38`. |
| `0x0047fb50` | `CHelpTextDisplay__RenderQueuedMessages` | `0x00487b83 CHud__RenderOverlayForViewpoint` call xref; ages/fades two queue slots, wraps text through `TextLayout__WrapWideTextToFixedLines`, uses `CPlatform__Font`, measures with `CDXFont__GetTextExtent`, draws with `CDXFont__DrawTextDynamic`, toggles font field `+0x16c` for controller configs `3` and `4`, and expires old slots. |

Fresh evidence:

- `3` metadata rows, `3` tag rows, `3 xref rows`, `169 instruction rows`, and `3` decompile rows.
- Logs reported `targets=3 found=3 missing=0`, `rows=3 missing=0`, `Wrote 3 rows`, `Wrote 169 function-body instruction rows`, and `targets=3 dumped=3 missing=0 failed=0`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-082238_post_wave1175_helptext_display_current_risk_review_verified`, `19` files, `176065415` bytes, `DiffCount=0`, `HashDiffCount=0`.
- Current-risk accounting moved from `680/1179 = 57.68%` to `683/1179 = 57.93%`; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 496; current risk candidates: 6166.

Prior context: Wave397 `help-hive-wave397` corrected older owner labels to the saved HelpTextDisplay rows, and Wave1005 `help-text-display-review-wave1005` re-read the broader four-row HelpTextDisplay set. A Codex read-only consult returned after Wave1175 target selection and recommended a Mat34/Vec3 owner-neutral cluster for the next candidate lane; Codex root kept Wave1175 on the already-exported HelpTextDisplay evidence and owns final claims.

Boundary: runtime HelpText behavior, runtime HUD/text rendering behavior, exact HelpTextDisplay/HUD/font/text-layout layouts, exact source-body identity, BEA patching behavior, visual QA, gameplay outcomes, and rebuild parity remain separate proof.

Probe token anchor: Wave1175; wave1175-helptext-display-current-risk-review; 683/1179 = 57.93%; 3 HelpTextDisplay current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 496; current risk candidates: 6166; fresh Ghidra export; read-only review; no mutation; Codex root final judgment; 0 / 0 / 0; 6411/6411 = 100.00%; 3 xref rows; 169 instruction rows; CHelpTextDisplay__ctor; CHelpTextDisplay__QueueMessageWithTimestamp; CHelpTextDisplay__RenderQueuedMessages; CGame__InitRestartLoop; CHud__RenderOverlayForViewpoint; TextLayout__WrapWideTextToFixedLines; CDXFont__DrawTextDynamic; Wave397; help-hive-wave397; Wave1005; help-text-display-review-wave1005; [maintainer-local-ghidra-backup-root]\BEA_20260606-082238_post_wave1175_helptext_display_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.
