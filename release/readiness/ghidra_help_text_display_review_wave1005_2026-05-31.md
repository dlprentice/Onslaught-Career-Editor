# Ghidra HelpTextDisplay Review Wave1005 Readiness Note

Status: complete read-only static read-back evidence
Date: 2026-05-31
Scope: `help-text-display-review-wave1005`

Wave1005 re-read the HelpTextDisplay lifecycle, queue, and render rows after Wave1004's HUD render-body review. The pass made no Ghidra mutation, no rename, no signature change, no function-boundary change, and no executable-byte change.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x0047fab0 CHelpTextDisplay__ctor` | Saved signature `void * __thiscall CHelpTextDisplay__ctor(void * this)`; xref from `0x0046c769 CGame__InitRestartLoop`; body clears two queued-message slots and installs the HelpTextDisplay vtable. |
| `0x0047fad0 CHelpTextDisplay__scalar_deleting_dtor` | Saved signature `void * __thiscall CHelpTextDisplay__scalar_deleting_dtor(void * this, byte flags)`; DATA ref `0x005dbdf8`; wrapper restores the vtable and conditionally frees through the OID allocator. |
| `0x0047fb00 CHelpTextDisplay__QueueMessageWithTimestamp` | Saved signature `void __thiscall CHelpTextDisplay__QueueMessageWithTimestamp(void * this, void * message)`; call xref `0x00533b5d`; body fills one of two message slots, stamps the global timestamp, and logs the overflow path when both slots are occupied. |
| `0x0047fb50 CHelpTextDisplay__RenderQueuedMessages` | Saved signature `void __fastcall CHelpTextDisplay__RenderQueuedMessages(void * this)`; call xref `0x00487b83 CHud__RenderOverlayForViewpoint`; body uses age/fade handling, calls `0x00465a20 TextLayout__WrapWideTextToFixedLines`, and dispatches through `0x00465710 CDXFont__DrawTextDynamic`. |
| `0x004659a0 CDXFont__DrawTextScaledWithShadow` | Saved signature `int __thiscall CDXFont__DrawTextScaledWithShadow(void * this, float x, float y, uint packed_argb, short * text, uint flags, float depth_z, float x_scale, float y_scale)`; 43 xrefs remain broad frontend/game/HUD/message/menu text-render callers; decompile still performs alpha-only `x+1/y+1` shadow draw then foreground draw through `CDXFont__DrawTextScaled`. |

Context rows: `0x00465710 CDXFont__DrawTextDynamic`, `0x00465a20 TextLayout__WrapWideTextToFixedLines`, `0x0048f620 CLevelBriefingLog__Render`, and `0x0053ecc0 CDXEngine__PostRender`.

Read-back evidence:

- Target exports: 5 metadata rows, 5 tag rows, 47 xref rows, 232 body-instruction rows, and 5 decompile rows.
- Context exports: 4 metadata rows, 4 decompile rows, and 1252 body-instruction rows.
- Verified backup: `G:\GhidraBackups\BEA_20260531-132023_post_wave1005_help_text_display_review_verified`, 19 files, 173869959 bytes, `DiffCount=0`, `HashDiffCount=0`.
- Queue closure remains `6223/6223 = 100.00%` with 0 commentless functions, 0 exact-undefined signatures, and 0 `param_N` signatures.
- Wave911 focused re-audit progress remains `485/1408 = 34.45%`.
- Expanded static surface progress advances to `659/1478 = 44.59%`.
- Wave911 top-500 risk-ranked coverage advances to `384/500 = 76.80%`.

What this proves:

- The saved Ghidra project still has bounded HelpTextDisplay lifecycle, queue, render, and CDXFont text-render metadata.
- The Wave397 owner corrections for HelpTextDisplay and the Wave801 CDXFont owner correction remain coherent against fresh metadata, tags, xrefs, instructions, and decompile output.
- The direct HelpTextDisplay render dependency is `CDXFont__DrawTextDynamic`; `CDXFont__DrawTextScaledWithShadow` is a related Wave801 top-500 text-render dependency, not the direct HelpTextDisplay draw call.

What remains unproven:

- Runtime help-text behavior.
- Runtime text rendering or visible UI output.
- Exact source-body identity.
- Concrete HelpTextDisplay, CDXFont, text-layout, HUD, or frontend layout identity beyond the saved static evidence.
- BEA patching behavior.
- Rebuild parity.
