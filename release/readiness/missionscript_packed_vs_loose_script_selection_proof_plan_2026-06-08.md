# MissionScript Packed-vs-Loose Script Selection Proof Plan Readiness Note

Status: static proof plan complete, not runtime proof
Date: 2026-06-08
Scope: `missionscript-packed-vs-loose-script-selection`

This readiness note records the public-safe static proof plan at `reverse-engineering/binary-analysis/missionscript-packed-vs-loose-script-selection-proof-plan.md`, backed by `reverse-engineering/binary-analysis/missionscript-packed-vs-loose-script-selection.v1.json`.

Static closeout remains unchanged:

- Static Ghidra function-quality closure: `6411/6411 = 100.00%`.
- Static debt: `0 / 0 / 0`.
- Expanded post-100 static surface: `1560/1560 = 100.00%`.
- Active current-risk focused accounting: `1179/1179 = 100.00%`.
- Remaining active focused work: `0`.
- Latest verified Ghidra backup: `[maintainer-local-ghidra-backup-root]\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified`.

Evidence summarized:

| Surface | Static evidence |
| --- | --- |
| Loose corpus | `733` loose `.msl` files in the current Goodie corpus report, `32` literal Goodie-state calls, `0` target hits for script indices `72`, `73`, and `74`, `95` level rows, and `795` loose event-name counts; loose corpus/reference evidence only. |
| Packed resource literal scan | `301` top-level packed AYA archives checked by the current inflater, `0` inflate errors, `0` literal Goodie API/token hits, and `0` target hits for indices `72`, `73`, and `74`. |
| Object-code load anchors | `0x00539dc0 CMissionScriptObjectCode__StartLoadAsync` copies the path to `this+0x20` and stores size at `this+0x124`; `0x00539ca0 CMissionScriptObjectCode__LoadAsync` calls `CDXMemBuffer__InitFromFile` using `this+0x20` and buffer state at `this+0x1c` / `this+0x124`. |
| Lifecycle dependencies | `script_object_code+0x68`, `DAT_00855190`, `DAT_0089c590`, `IScript__ScheduleEvent`, `CScriptEventNB__PostEvent`, `CEventFunction__Execute`, `CScriptObjectCode__CallEvent`, `CScriptObjectCode__CallEventDirect`, and `CScriptObjectCode__Run`. |

What this proves:

- Loose corpus/reference evidence, packed-resource literal scan evidence, static object-code load anchors, and future runtime source-selection proof requirements are now separated in a public-safe plan.
- The checked packed-resource scan is bounded to top-level inflated AYA archive literal Goodie API/token scan only.
- The saved Ghidra load anchors prove a path-buffer async load shape.

What this does not prove:

- Runtime MissionScript execution.
- Runtime command effects.
- Runtime event outcomes.
- Live loose-MSL loading.
- Packed-vs-loose script selection.
- Compiled bytecode equivalence.
- All packed scripts absent.
- Exact object-code layout.
- Exact async-cache layout.
- Exact source identity.
- BEA patching behavior.
- Visual QA.
- Godot parity.
- Rebuild parity.
- No-noticeable-difference parity.

Stop conditions for later proof:

- Stop on installed-game or original executable mutation need.
- Stop on private asset/path leakage risk.
- Stop if static evidence cannot distinguish source-selection precedence.
- Stop if a packed-resource literal scan would be treated as compiled-bytecode equivalence.
- Stop if live mission execution is needed before copied/app-owned guardrails exist.

Completed child slice: `MissionScript Level100 Tutorial Text/Speaker Resolution Static Proof Plan`.

Next selected static-to-proof slice: `MissionScript Level100 Tutorial Runtime Harness Boundary Proof Plan`.
