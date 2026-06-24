# MissionScript Event / Object-Code Lifecycle Proof

Status: static event/object-code lifecycle schema proof complete, not runtime proof
Last updated: 2026-06-08
Scope: `missionscript-event-object-code-lifecycle`

This proof converts saved retail Ghidra evidence from Wave546, Wave577, Wave585, Wave586, Wave587, Wave588, Wave926, and Wave1189 into a machine-checkable MissionScript event/object-code lifecycle map at `missionscript-event-object-code-lifecycle.v1.json`. It is the next MissionScript child lane after the completed command descriptor and VM/datatype/opcode schema results.

Level100 tutorial follow-up static maps now include `missionscript-level100-tutorial-static-walkthrough-proof-plan.md` / `missionscript-level100-tutorial-static-walkthrough.v1.json` for the event/command walkthrough and the MissionScript Level100 Tutorial Text/Speaker Resolution Static Proof Plan at `missionscript-level100-tutorial-text-speaker-resolution-proof-plan.md` / `missionscript-level100-tutorial-text-speaker-resolution.v1.json` for static text/speaker resolution. The text/speaker slice resolves `English.txt` `52`, `Global.txt` `0`, level-local `text.stf` `0`, shared `text/text.stf` `2571`, `43` message tokens, `6` help tokens, `_100_OBJECTIVE_1` through `_100_OBJECTIVE_4`, `LOSE_TUTORIAL_BROKE`, speakers `P_TATIANA`, `P_KRAMER`, and `P_TECHNICIAN`, `68/68` relevant static tokens resolved, and `0 missing`; runtime text/audio behavior, live loose-MSL loading, event outcomes, visual QA, patching, Godot, rebuild parity, and no-noticeable-difference parity remain separate proof.

Level100 tutorial runtime-harness boundary is recorded in the MissionScript Level100 Tutorial Runtime Harness Boundary Proof Plan at `missionscript-level100-tutorial-runtime-harness-boundary-proof-plan.md` / `missionscript-level100-tutorial-runtime-harness-boundary.v1.json`. Status: runtime-harness boundary proof plan complete, not runtime proof; it defines copied/app-owned future-proof artifacts, source-selection observation boundaries, stop conditions, and public/private separation without launching BEA, patching, screenshots, native input, Godot, or runtime claims.

Static closeout remains unchanged:

- Static Ghidra function-quality closure: `6411/6411 = 100.00%`.
- Static debt: `0 / 0 / 0` commentless, exact-undefined, and `param_N` rows.
- Expanded post-100 static surface: `1560/1560 = 100.00%`.
- Active current-risk focused accounting: `1179/1179 = 100.00%`.
- Remaining active focused work: `0`.
- Latest verified Ghidra backup remains `G:\GhidraBackups\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified`.

## Schema Result

| Surface | Static result |
| --- | --- |
| Script owner link | `0x005333b0 IScript__Constructor` stores owner/script pointers, writes the script back-pointer at `script_object_code+0x68`, and initializes the listener/state set at `this+0x28`. |
| Scheduled event ingress | `0x005383c0 IScript__ScheduleEvent` is the registered `PostEvent(event_name)` handler. It allocates a `0x0c`-byte payload, links it through `DAT_00855190`, and schedules `CEventManager__AddEvent_AtTime(...,2000,&DAT_0089c590,-1.0,0,payload,0)`. |
| Listener registration/posting | `0x00538960 CScriptEventNB__RegisterEventListener` and `0x00538b70 CScriptEventNB__PostEvent` match names through string/datatype getter evidence, preserve the no-listener warning path, mark matched listener entries, and call `CEventFunction__Execute`. |
| Event callback execution | `0x0052fda0 CEventFunction__Execute` walks event-parameter wrappers, stages up to the observed local 10-slot array, and calls `CScriptObjectCode__CallEventDirect`. |
| Object-code event call | `0x00539990 CScriptObjectCode__CallEvent` looks up event instruction pointers from `script_object_code+0x14+event_index*4`, pushes parameters, and calls `CScriptObjectCode__Run`. |
| Direct object-code call | `0x00539a60 CScriptObjectCode__CallEventDirect` pushes supplied parameters, writes the instruction pointer at runtime state `+0x214`, and calls `CScriptObjectCode__Run`. |
| VM dependency | `0x00539b00 CScriptObjectCode__Run` remains a dependency already accounted by `missionscript-vm-datatype-opcode-schema-proof.md`; this slice does not re-claim runtime VM/opcode behavior. |
| Async object-code loading | `0x00539dc0 CMissionScriptObjectCode__StartLoadAsync` waits for the worker, copies the filename to `this+0x20`, stores buffer size at `this+0x124`, and starts the worker; `0x00539ca0 CMissionScriptObjectCode__LoadAsync` creates a `CDXMemBuffer` and initializes it from the stored path. |
| Teardown | `0x00539f40 CMissionScriptObjectCode__ClearFields` and `0x004f7440 CMissionScriptObjectCode__FreeObjectIfPresent` clear the field block, free object-code pointer slots, and null released fields. |

Evidence rows consumed by the schema:

| Evidence | Count |
| --- | ---: |
| Wave546 metadata rows | `1` |
| Wave577 EventFunction metadata rows | `5` |
| Wave585 IScript level/event metadata rows | `5` |
| Wave586 CScriptEventNB metadata rows | `13` |
| Wave587 CScriptObjectCode metadata rows | `22` |
| Wave588 CMissionScriptObjectCode metadata rows | `6` |
| Wave926 IScript lifecycle metadata rows | `2` |
| Wave1189 context metadata rows | `7` |
| Wave586 instruction rows | `5577` |
| Wave587 instruction rows | `2662` |
| Wave588 instruction rows | `534` |

Loose mission-script corpus context remains reference-only: `mission-events-index.md` records `95` level rows and `795` loose event-name counts. The schema preserves those counts as vocabulary context only, not live loose-MSL loading or packed-resource selection proof.

The descriptor table at `0x0064ce50` remains a dependency through the completed command descriptor schema; this event/object-code slice focuses on the lifecycle after a `PostEvent` command has been statically identified.

## Why This Matters

This gives a clean-room MissionScript planner a bounded event lifecycle instead of scattered wave notes: script ownership, scheduled event payload creation, listener registration/posting, event callback execution, event-table dispatch into object code, async object-code loading, and teardown. It also keeps command-effect families separate, so later work can choose one command family or one copied/app-owned mission proof without accidentally claiming broad MissionScript runtime behavior.

Follow-up script-source selection planning is recorded in [MissionScript Packed-vs-Loose Script Selection Proof Plan](missionscript-packed-vs-loose-script-selection-proof-plan.md), backed by [missionscript-packed-vs-loose-script-selection.v1.json](missionscript-packed-vs-loose-script-selection.v1.json). That child plan keeps `0x00539dc0 CMissionScriptObjectCode__StartLoadAsync`, `0x00539ca0 CMissionScriptObjectCode__LoadAsync`, `this+0x20`, `this+0x124`, and `CDXMemBuffer__InitFromFile` as object-code path-buffer load anchors only, then separates them from loose `.msl` corpus counts and narrow packed-resource literal-token scan evidence. It does not turn this lifecycle proof into live loose-MSL loading or packed-resource script-selection proof.

Level100 tutorial walkthrough planning is recorded in [MissionScript Level100 Tutorial Static Event/Command Walkthrough Proof Plan](missionscript-level100-tutorial-static-walkthrough-proof-plan.md), backed by [missionscript-level100-tutorial-static-walkthrough.v1.json](missionscript-level100-tutorial-static-walkthrough.v1.json). That child plan uses this event/object-code lifecycle surface to bind `level100`, `LevelScript.msl`, `25` `.msl` files, `24` extras, `1469` parsed MSL lines, `26` unique event names, `34` handler declarations, `41` `PostEvent` callsites, the `Destroyed Friendly Building` / `Friendly Building Destroyed` string mismatch, objective/slot/message/HUD/thing/spawn command rows, and the static anchors `0x005383c0 IScript__ScheduleEvent`, `0x00538b70 CScriptEventNB__PostEvent`, `0x0052fda0 CEventFunction__Execute`, `0x00539a60 CScriptObjectCode__CallEventDirect`, `0x00539b00 CScriptObjectCode__Run`, `0x0064ce50`, `144`, `0x0052ea40`, and `0x0052ec60` without claiming runtime event outcomes or command effects.

## Claim Boundary

This proves static event/object-code lifecycle accounting from saved retail Ghidra evidence. It does not prove runtime MissionScript execution, runtime event outcomes, runtime command effects, runtime opcode behavior, live loose-MSL loading, packed-resource script selection, exact event payload layout, exact listener layout, exact object-code layout, exact async-cache layout, exact VM layout, exact source identity, BEA patching behavior, visual QA, Godot parity, rebuild parity, or no-noticeable-difference parity.
