# MissionScript Event / Object-Code Lifecycle Readiness Note

Status: static event/object-code lifecycle schema proof complete, not runtime proof
Date: 2026-06-08
Scope: `missionscript-event-object-code-lifecycle`

This readiness note records the public-safe static proof result for [MissionScript Event / Object-Code Lifecycle Proof](../../reverse-engineering/binary-analysis/missionscript-event-object-code-lifecycle-proof.md), backed by `missionscript-event-object-code-lifecycle.v1.json`.

Static closeout remains unchanged: `6411/6411 = 100.00%`, `0 / 0 / 0`, `1560/1560 = 100.00%`, `1179/1179 = 100.00%`, and remaining active focused work `0`. Latest verified Ghidra backup remains `[maintainer-local-ghidra-backup-root]\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified`.

Evidence anchors:

| Surface | Anchor |
| --- | --- |
| Script owner link | `0x005333b0 IScript__Constructor`, `script_object_code+0x68`. |
| Scheduled event ingress | `0x005383c0 IScript__ScheduleEvent`, `DAT_00855190`, `DAT_0089c590`. |
| Listener posting | `0x00538b70 CScriptEventNB__PostEvent`. |
| Event callback execution | `0x0052fda0 CEventFunction__Execute`. |
| Object-code calls | `0x00539990 CScriptObjectCode__CallEvent`, `0x00539a60 CScriptObjectCode__CallEventDirect`, `0x00539b00 CScriptObjectCode__Run`. |
| Async object-code loading | `0x00539dc0 CMissionScriptObjectCode__StartLoadAsync`, `0x00539ca0 CMissionScriptObjectCode__LoadAsync`. |
| Teardown | `0x00539f40 CMissionScriptObjectCode__ClearFields`, `0x004f7440 CMissionScriptObjectCode__FreeObjectIfPresent`. |
| Descriptor dependency | Completed descriptor schema table at `0x0064ce50`. |
| Loose corpus context | `795` event-name counts in `mission-events-index.md`. |

Evidence counts: Wave546 `1` metadata row; Wave577 `5`; Wave585 `5`; Wave586 `13`; Wave587 `22`; Wave588 `6`; Wave926 `2`; Wave1189 `7`. This slice used saved static exports and did not mutate Ghidra.

What this proves:

- The static event/object-code lifecycle is mapped from saved retail Ghidra evidence.
- The lifecycle spans IScript owner linkage, scheduled event payload creation, listener registration/posting, event callback execution, object-code event calls, async object-code loading, and teardown.
- The machine-checkable schema and focused probe preserve exact row counts, core function anchors, corpus context counts, and claim boundaries.

What remains unproven:

- Runtime MissionScript execution.
- Runtime event outcomes or command effects.
- Runtime opcode behavior.
- Live loose-MSL loading or packed-resource script selection.
- Exact event payload, listener, object-code, async-cache, VM, or source layouts.
- BEA patching behavior, visual QA, Godot parity, rebuild parity, or no-noticeable-difference parity.
