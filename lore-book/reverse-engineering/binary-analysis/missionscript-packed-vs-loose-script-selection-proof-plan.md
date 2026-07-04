# MissionScript Packed-vs-Loose Script Selection Proof Plan

Status: static proof plan complete, not runtime proof
Last updated: 2026-06-08
Scope: `missionscript-packed-vs-loose-script-selection`
Public proof anchor: `missionscript-packed-vs-loose-script-selection-proof-plan.md`

This proof-plan slice closes the first MissionScript source-selection boundary after the completed command descriptor, VM/datatype/opcode, event/object-code lifecycle, slot, objective/outcome, message/audio, Goodie-state, cutscene camera, vector/range, thing-value/engine-helper, HUD/display, player-state/score, selected `SpawnThing`, and selected `GetThingRef` static bridges. It separates four inputs that were previously easy to blur:

Follow-up static-to-proof boundary: the MissionScript Level100 Tutorial Runtime Harness Boundary Proof Plan is recorded at `missionscript-level100-tutorial-runtime-harness-boundary-proof-plan.md`, backed by `missionscript-level100-tutorial-runtime-harness-boundary.v1.json`. That slice is runtime-harness boundary proof plan complete, not runtime proof, and moves the active child lane to MissionScript Level100 Tutorial Copied-Profile Runtime Observation Boundary Planning Proof Plan.

- Loose MissionScript corpus/reference evidence.
- Narrow packed-resource literal-token scan evidence.
- Static object-code/path-buffer load anchors in the retail binary.
- Future copied/app-owned runtime proof requirements.

Machine-checkable schema: `missionscript-packed-vs-loose-script-selection.v1.json`.

Follow-up Level100 walkthrough result: MissionScript Level100 Tutorial Static Event/Command Walkthrough Proof Plan, `missionscript-level100-tutorial-static-walkthrough-proof-plan.md`, backed by `missionscript-level100-tutorial-static-walkthrough.v1.json`. Status: static walkthrough proof plan complete, not runtime proof. It uses this source-selection boundary as context while mapping `level100`, `LevelScript.msl`, `25` `.msl` files, `24` extras, `1469` parsed MSL lines, `26` unique event names, `34` handler declarations, `41` `PostEvent` callsites, `Destroyed Friendly Building` versus `Friendly Building Destroyed`, objectives `_100_OBJECTIVE_1` through `_100_OBJECTIVE_4`, slot/message/HUD/thing/spawn rows, and static MissionScript anchors (`0x005383c0 IScript__ScheduleEvent`, `0x00538b70 CScriptEventNB__PostEvent`, `0x0052fda0 CEventFunction__Execute`, `0x00539a60 CScriptObjectCode__CallEventDirect`, `0x00539b00 CScriptObjectCode__Run`, `0x0064ce50`, `144`, `0x0052ea40`, `0x0052ec60`, `0x00539dc0 CMissionScriptObjectCode__StartLoadAsync`, `0x00539ca0 CMissionScriptObjectCode__LoadAsync`, `this+0x20`, `this+0x124`, and `CDXMemBuffer__InitFromFile`) without claiming live loose-MSL loading or packed-vs-loose script selection proof.

Follow-up Level100 text/speaker result: MissionScript Level100 Tutorial Text/Speaker Resolution Static Proof Plan, `missionscript-level100-tutorial-text-speaker-resolution-proof-plan.md`, backed by `missionscript-level100-tutorial-text-speaker-resolution.v1.json`. Status: static text/speaker resolution proof plan complete, not runtime proof. It uses this source-selection boundary as context while resolving `English.txt` `52`, `Global.txt` `0`, level-local `text.stf` `0`, shared `text/english.txt` `241`, shared `text/global.txt` `2`, shared `text/text.stf` `2571`, `43` unique message tokens, `6` help tokens, `_100_OBJECTIVE_1` through `_100_OBJECTIVE_4`, `LOSE_TUTORIAL_BROKE`, speakers `P_TATIANA`, `P_KRAMER`, and `P_TECHNICIAN`, generated-only tokens including `TUTORIAL_13_MOD`, `TUTORIAL_DODGE_MOD`, `TUTORIAL_THROTTLE_MOD`, `HELP_FIRE`, `HELP_RETRO`, `HELP_TRANSFORM`, `HELP_WEAPON_SELECT`, `HELP_ZOOM_IN`, and `HELP_ZOOM_OUT`, `68/68` relevant static tokens resolved, and `0 missing` without claiming runtime text/audio behavior or live script-source selection proof.

This plan does not launch BEA, mutate Ghidra, mutate the installed game, patch an executable, capture screenshots, drive native input, execute scripts, load a live mission, start Godot work, or claim runtime MissionScript execution, runtime command effects, runtime event outcomes, live loose-MSL loading, packed-vs-loose script selection, compiled bytecode equivalence, exact object-code layout, exact async-cache layout, exact source identity, BEA patching behavior, visual QA, rebuild parity, or no-noticeable-difference parity.

## Static Authority

Current static closeout remains unchanged:

- Static Ghidra function-quality closure: `6411/6411 = 100.00%`.
- Static debt: `0 / 0 / 0` commentless, exact-undefined, and `param_N` rows.
- Expanded post-100 static surface: `1560/1560 = 100.00%`.
- Active current-risk focused accounting: `1179/1179 = 100.00%`.
- Remaining active focused work: `0`.
- Latest verified Ghidra backup: `[maintainer-local-ghidra-backup-root]\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified`.

Primary static and corpus sources:

- `missionscript-iscript-proof-plan.md`
- `missionscript-iscript-static-contract.md`
- `missionscript-event-object-code-lifecycle-proof.md`
- `missionscript-event-object-code-lifecycle.v1.json`
- `functions/ScriptObjectCode.cpp.md`
- `../game-assets/msl-scripting.md`
- `../game-assets/mission-scripts-index.md`
- `../game-assets/mission-events-index.md`
- `../game-assets/mission-slot-usage.md`
- `../game-assets/mission-thing-usage.md`
- `../game-assets/mission-message-usage.md`
- `release/readiness/goodies_packed_script_probe_2026-05-07.md`

## Loose Corpus Evidence

The loose MissionScript corpus is useful as a public implementation reference, but it remains loose corpus/reference evidence only until copied/app-owned proof establishes live loading or source selection.

Current bounded counts:

| Surface | Count / anchor |
| --- | --- |
| Loose `.msl` files scanned by the current Goodie corpus report | `733` |
| Literal Goodie state calls in that loose scan | `32` |
| Target script indices for Goodies 71-73 reachability check | `72`, `73`, `74` |
| Target hits for script indices 72-74 | `0` |
| Mission-script level rows in the loose script index | `95` |
| Loose event-name counts in the event index | `795` |
| Primary-complete / secondary-complete / primary-failed / level-won / level-lost calls | `115 / 42 / 102 / 79 / 13` |
| Example high-value levels | `level100` has `25` MSL files; `level500` has `24`; `level741` has `17`; `level742` has `19` |

The key interpretation is conservative: these files describe a shipped loose reference corpus and are excellent clean-room planning material, but they are not live loose-MSL loading proof.

## Packed Resource Literal Scan

The current packed-resource evidence is intentionally narrow. `release/readiness/goodies_packed_script_probe_2026-05-07.md` records a static token probe that inflated top-level packed AYA resource archives and searched for literal Goodie-state API/token evidence:

```text
packed resource Goodie calls: archives=301 inflateErrors=0 tokenFiles=0 calls=0 target72to74=0
```

For this proof plan, that means:

- `301` top-level packed AYA resource archives were checked by the current inflater.
- `0` inflate errors were recorded.
- `0` literal Goodie API/token hits were found in the checked packed-resource scan.
- The scan narrows literal text-token divergence for Goodie-state API calls.
- The scan is top-level inflated AYA archive literal Goodie API/token scan only.

It does not prove packed scripts are absent, compiled bytecode equivalence, indirect script selection, runtime-generated script behavior, or packed-vs-loose script selection.

## Object-Code Load Anchors

The static retail binary supports a path-buffer async load shape, not a runtime source-selection claim.

| Anchor | Static evidence | Boundary |
| --- | --- | --- |
| `0x00539dc0 CMissionScriptObjectCode__StartLoadAsync` | Waits for the current worker, copies `filename` into `this+0x20`, stores `buffer_size` at `this+0x124`, then calls `CBinkOpenThread__StartAsync`. | Path-buffer async start anchor only; not proof of loose-vs-packed source selection or loaded runtime path. |
| `0x00539ca0 CMissionScriptObjectCode__LoadAsync` | Closes prior buffer at `this+0x1c`, allocates `CDXMemBuffer`, applies size from `this+0x124`, calls `CDXMemBuffer__InitFromFile` on `this+0x20`, and clears the first path byte before return. | Path-buffer load anchor only; not proof of runtime MissionScript execution or source precedence. |
| `0x00539f40 CMissionScriptObjectCode__ClearFields` and `0x004f7440 CMissionScriptObjectCode__FreeObjectIfPresent` | Clear/free object-code or HUD field-block pointer slots. | Static teardown anchor only; exact object-code and async-cache layouts remain unproven. |

The event/object-code lifecycle schema remains the dependency surface for later mission proof: `IScript__Constructor`, `IScript__ScheduleEvent`, `CScriptEventNB__PostEvent`, `CEventFunction__Execute`, `CScriptObjectCode__CallEvent`, `CScriptObjectCode__CallEventDirect`, `CScriptObjectCode__Run`, `CMissionScriptObjectCode__LoadAsync`, `script_object_code+0x68`, `DAT_00855190`, and `DAT_0089c590`.

## Required Later Proof Lanes

Any later runtime or rebuild slice must choose one lane and produce copied/app-owned evidence:

| Lane | Required evidence before claim |
| --- | --- |
| Copied loose corpus inventory | Copied MissionScripts corpus inventory with casing/path preservation, script count, selected file hashes, and public-safe aggregate output. |
| Copied resource inventory | Copied resource archive inventory for the selected mission/resource set, with no raw private asset dump in public artifacts. |
| Static callsite/path map | Fresh static xref/path-argument map around `CMissionScriptObjectCode__StartLoadAsync` callsites and the selected mission path. |
| Runtime source-selection proof | Copied-profile/app-owned runtime observation only after the selected static lane defines expected artifacts, stop conditions, and reversible logging. |

## Stop Conditions

Stop and record a deferred state instead of widening scope if:

- Installed-game or original executable mutation would be required.
- Private raw assets, private paths, or operator-only proof would enter public artifacts.
- Selection precedence is ambiguous from static evidence.
- The proof would require live mission execution before copied/app-owned guardrails exist.
- A packed-resource literal scan is being treated as compiled-bytecode equivalence.
- Exact object-code, async-cache, or source-body identity would be required for the claim.

## Claims

This slice proves:

- A public-safe static plan now separates loose MissionScript corpus evidence, narrow packed-resource literal scan evidence, object-code load anchors, and future copied/app-owned runtime selection proof requirements.
- The checked loose corpus and top-level inflated packed-resource Goodie token scan are usable bounded inputs for planning.
- The saved Ghidra load anchors prove a path-buffer async load shape.

This slice does not prove:

- Runtime MissionScript execution.
- Runtime command effects or event outcomes.
- Live loose-MSL loading.
- Packed-vs-loose script selection.
- Compiled bytecode equivalence.
- All packed scripts absent.
- Exact object-code, async-cache, descriptor, datatype, or VM layouts.
- BEA patching behavior.
- Visual QA.
- Godot parity.
- Rebuild parity.
- No-noticeable-difference parity.

## Exit Gate

This planning slice is complete only when:

- This document and `missionscript-packed-vs-loose-script-selection.v1.json` have lore-book mirrors.
- `roadmap/static-to-proof-rebuild-transition-backlog.md`, `mapped-systems.md`, `_index.md`, and `RE-INDEX.md` point to this plan.
- `missionscript-iscript-proof-plan.md`, `missionscript-iscript-static-contract.md`, `missionscript-event-object-code-lifecycle-proof.md`, `functions/ScriptObjectCode.cpp.md`, and the MSL corpus docs point to this plan.
- `release/readiness/missionscript_packed_vs_loose_script_selection_proof_plan_2026-06-08.md` records the same claim boundaries.
- `tools/missionscript_packed_vs_loose_script_selection_probe.py --check` passes.

## Follow-Up Child Lane

The MissionScript Level100 Tutorial Text/Speaker Resolution Static Proof Plan is now complete. The next selected static-to-proof child lane is `MissionScript Level100 Tutorial Runtime Harness Boundary Proof Plan`. It must stay a planning/boundary slice until it selects copied/app-owned runtime inputs, source-selection constraints, expected artifacts, and stop conditions without launching BEA, patching an executable, capturing screenshots, driving native input, loading a live mission, starting Godot work, or claiming runtime MissionScript behavior.
