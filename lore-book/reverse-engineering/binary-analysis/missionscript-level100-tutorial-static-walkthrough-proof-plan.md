# MissionScript Level100 Tutorial Static Event/Command Walkthrough Proof Plan

Status: static walkthrough proof plan complete, not runtime proof
Last updated: 2026-06-08
Scope: `missionscript-level100-tutorial-static-walkthrough`
Public proof anchor: `missionscript-level100-tutorial-static-walkthrough-proof-plan.md`

This proof-plan slice converts the completed MissionScript command descriptor, VM/datatype/opcode, event/object-code lifecycle, command-effect, selected `SpawnThing`, selected `GetThingRef`, and packed-vs-loose source-selection planning into a single mission-level static walkthrough for `level100`, the tutorial mission. It is intended to make the static RE usable for later copied/app-owned runtime or clean-room slices without claiming that runtime behavior has already been proven.

Follow-up static-to-proof boundary: the MissionScript Level100 Tutorial Runtime Harness Boundary Proof Plan is recorded at `missionscript-level100-tutorial-runtime-harness-boundary-proof-plan.md`, backed by `missionscript-level100-tutorial-runtime-harness-boundary.v1.json`. That slice is runtime-harness boundary proof plan complete, not runtime proof, and moves the active child lane to MissionScript Level100 Tutorial Copied-Profile Runtime Observation Boundary Planning Proof Plan.

Machine-checkable schema: `missionscript-level100-tutorial-static-walkthrough.v1.json`.

This plan does not launch BEA, mutate Ghidra, mutate the installed game, patch an executable, capture screenshots, drive native input, execute scripts, load a live mission, start Godot work, or claim runtime MissionScript execution, runtime command effects, runtime event outcomes, live loose-MSL loading, packed-vs-loose script selection, runtime Level100 mission outcome, runtime objective UI, runtime message/audio output, runtime HUD flashing, runtime object identity, runtime `SpawnThing` behavior, runtime `GetThingRef` lookup behavior, exact descriptor/datatype/object-code layout, BEA patching behavior, visual QA, rebuild parity, or no-noticeable-difference parity.

## Static Authority

Current static closeout remains unchanged:

- Static Ghidra function-quality closure: `6411/6411 = 100.00%`.
- Static debt: `0 / 0 / 0` commentless, exact-undefined, and `param_N` rows.
- Expanded post-100 static surface: `1560/1560 = 100.00%`.
- Active current-risk focused accounting: `1179/1179 = 100.00%`.
- Remaining active focused work: `0`.
- Latest verified Ghidra backup: `G:\GhidraBackups\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified`.

Primary static and corpus sources:

- `missionscript-iscript-proof-plan.md`
- `missionscript-iscript-static-contract.md`
- `missionscript-packed-vs-loose-script-selection-proof-plan.md`
- `missionscript-event-object-code-lifecycle-proof.md`
- `missionscript-command-descriptor-schema-proof.md`
- `missionscript-vm-datatype-opcode-schema-proof.md`
- `missionscript-slot-command-effect-static-proof.md`
- `missionscript-objective-outcome-command-effect-static-proof.md`
- `missionscript-message-audio-command-effect-static-proof.md`
- `missionscript-hud-display-command-effect-static-proof.md`
- `missionscript-thing-value-engine-helper-command-effect-static-proof.md`
- `missionscript-player-state-score-command-effect-static-proof.md`
- `world-thing-spawn-spawner-handoff-static-proof.md`
- `world-thing-spawn-getthingref-object-reference-static-proof.md`
- `../game-assets/mission-scripts-index.md`
- `../game-assets/mission-events-index.md`
- `../game-assets/mission-thing-usage.md`
- `../game-assets/mission-slot-usage.md`
- `../game-assets/mission-message-usage.md`
- `../game-assets/mission-message-usage-callsites-1.md`
- `../game-assets/mission-speaker-index.md`

## Level100 Corpus Surface

The `level100` tutorial corpus is treated as loose corpus/reference evidence only. Raw game files remain private/release-deny; this public proof records aggregate and token-level facts only.

| Surface | Static result |
| --- | --- |
| Main script | `LevelScript.msl` |
| Level script inventory | `25` `.msl` files, `24` extras |
| Current local parsed line count | `1469` MSL lines |
| Text files | `English.txt` has `52` token blocks; `Global.txt` and level-local `text.stf` exist; level-local `text.stf` is empty |
| Public script index row | `level100`, `LevelScript.msl`, `25`, `24`, English/Global/text present |
| Public event index row | `26` events, `4` objective IDs, `4` primary-complete, `0` secondary-complete, `0` objective-complete, `4` primary-failed, `1` `LevelWon`, `0` direct `LevelLost` |

The walkthrough preserves file and token names because those are clean-room planning anchors. It does not reproduce raw dialogue text.

## Event Walkthrough

The Level100 event surface has:

- `26` unique declared event names.
- `34` `event("...")` handler declarations because some event names are implemented by multiple object scripts.
- `41` `PostEvent("...")` callsites.
- `26` unique posted event names.
- One exact-string mismatch preserved as evidence, not normalized: `Destroyed Friendly Building` is posted by object scripts, while `Friendly Building Destroyed` is the declared handler in `LevelScript.msl`.

Representative static path:

1. `LevelScript.msl:init`
2. `Reached Target Zone 1`
3. `Reached Firing Range`
4. `Activate Static Targets`
5. `Static Target Destroyed`
6. `Activate Static Targets 2`
7. `Static Target 2 Destroyed`
8. `Activate Moving Targets`
9. `Moving Target Destroyed`
10. `Trainer Attack`
11. `Cease Trainer Attack`
12. `Reached Target Zone 2`
13. `Activate Airborne Targets 1`
14. `Airborne Target 1 Destroyed`
15. `Reached Target Zone 3`
16. `Activate Airborne Targets 2`
17. `Airborne Target 2 Destroyed`
18. `Reached Target Zone 4`
19. `LevelWon`

This is a static event/command walkthrough only. It does not prove that retail executes this exact path, that the loose file is selected at runtime, or that any event outcome occurs in a live game.

## Command Families

| Family | Level100 static rows |
| --- | --- |
| Objective/outcome | `4` `PrimaryObjectiveFailed`, `4` `PrimaryObjectiveComplete`, `1` `LevelWon`, `0` `LevelLost`, `2` `LevelLostString`; objectives `_100_OBJECTIVE_1` through `_100_OBJECTIVE_4` |
| Slot persistence | `4` `GetSlot` calls and `4` `SetSlotSave` calls over `SLOT_TUTORIAL_1` through `SLOT_TUTORIAL_4` |
| Message/audio | `13` `PlayCharMessage`, `32` `PlayCharMessageWait`, `45` combined `PlayCharMessage*`, `6` `AddHelpMessage`, `43` unique message tokens |
| Speakers | `P_TATIANA` `40`, `P_KRAMER` `4`, `P_TECHNICIAN` `1`; public speaker labels live in `mission-speaker-index.md` |
| HUD/display | `7` `HighlightHudPart` and `7` `UnHighlightHudPart` calls over `HUD_COMPASS`, `HUD_RADAR`, `HUD_CURRENT_WEAPON`, `HUD_ENERGY_BAR`, `HUD_HEALTH_BAR`, and `HUD_BATTLE_LINE_MAP` |
| Thing/object refs | `18` raw `GetThingRef` calls, `15` unique names, with the duplicate `Target Zone 4` retained |
| Spawn refs | `20` raw `SpawnThing` calls for `Target Drone`, `Air Trainer`, `Target Tank`, and `Target Truck` through `SpawnerA` / `SpawnerB` where present |
| Player/thing control | `9` `DisableWeapon`, `5` `EnableWeapon`, `1` `DisableFlightMode`, `1` `EnableFlightMode`, `4` `AddScore`, `17` `SetObjective`, `18` `UnsetObjective`, `11` `Activate`, and `16` `Deactivate` calls |

The important boundary is that these are corpus rows tied to existing static command-effect proofs. They do not become runtime command-effect proof merely because the command names and counts are finite.

## Static Binary / Schema Dependencies

The Level100 walkthrough depends on the existing static MissionScript layers:

| Layer | Static anchors |
| --- | --- |
| Descriptor registry | `0x0052ff30 ScriptCommandRegistry__InitBuiltins`, descriptor table `0x0064ce50`, `144` declared slots |
| VM/datatype/opcode | `0x0052ea40 CAsmInstruction__ExecuteCall`, `0x0052ec60 CDataType__CreateFromType`, `0x00539b00 CScriptObjectCode__Run`, `script_state+0x218`, `script_object_code+0x68` |
| Event/object-code lifecycle | `0x005383c0 IScript__ScheduleEvent`, `0x00538b70 CScriptEventNB__PostEvent`, `0x0052fda0 CEventFunction__Execute`, `0x00539a60 CScriptObjectCode__CallEventDirect`, `0x00539b00 CScriptObjectCode__Run` |
| Source-selection boundary | `0x00539dc0 CMissionScriptObjectCode__StartLoadAsync`, `0x00539ca0 CMissionScriptObjectCode__LoadAsync`, `this+0x20`, `this+0x124`, `CDXMemBuffer__InitFromFile` |
| Command-effect bridges | Slot, objective/outcome, message/audio, HUD/display, thing-value/engine-helper, player-state/score, selected `SpawnThing`, and selected `GetThingRef` static proofs |

## Claims

This slice proves:

- Level100 now has a public-safe static walkthrough map tying the loose tutorial corpus to existing MissionScript command, event, VM, and object-reference static schemas.
- Exact event/string token boundaries are preserved, including the `Destroyed Friendly Building` versus `Friendly Building Destroyed` mismatch.
- The walkthrough is strong enough to plan a later copied/app-owned Level100 runtime or rebuild slice without widening static claims into runtime behavior.

This slice does not prove:

- Runtime MissionScript execution.
- Runtime command effects or event outcomes.
- Live loose-MSL loading.
- Packed-vs-loose script selection.
- Runtime Level100 mission outcome.
- Runtime objective UI.
- Runtime message/audio output.
- Runtime HUD flashing.
- Runtime object identity.
- Runtime `SpawnThing` behavior.
- Runtime `GetThingRef` lookup behavior.
- Exact descriptor/datatype/object-code layout.
- BEA patching behavior.
- Visual QA.
- Godot parity.
- Rebuild parity.
- No-noticeable-difference parity.

## Completed Text/Speaker Child Lane

Follow-up MissionScript Level100 Tutorial Text/Speaker Resolution Static Proof Plan is complete at `missionscript-level100-tutorial-text-speaker-resolution-proof-plan.md`, backed by `missionscript-level100-tutorial-text-speaker-resolution.v1.json`. It resolves `English.txt` `52`, `Global.txt` `0`, level-local `text.stf` `0`, shared `text/english.txt` `241`, shared `text/global.txt` `2`, shared `text/text.stf` `2571`, `45` message rows, `43` unique message tokens, `6` help tokens, `_100_OBJECTIVE_1` through `_100_OBJECTIVE_4`, `LOSE_TUTORIAL_BROKE`, speakers `P_TATIANA`, `P_KRAMER`, and `P_TECHNICIAN`, generated-only modifier/help/objective tokens, `68/68` relevant static tokens resolved, and `0 missing`. It remains static text/speaker resolution only, not runtime text/audio behavior, message display, voice/audio playback, speaker portrait behavior, live loose-MSL loading, patching, Godot, rebuild parity, or no-noticeable-difference parity.

## Exit Gate

This planning slice is complete only when:

- This document and `missionscript-level100-tutorial-static-walkthrough.v1.json` have lore-book mirrors.
- `roadmap/static-to-proof-rebuild-transition-backlog.md`, `mapped-systems.md`, `_index.md`, and `RE-INDEX.md` point to this plan.
- MissionScript corpus docs and MissionScript static contract/proof-plan docs point to this plan.
- `release/readiness/missionscript_level100_tutorial_static_walkthrough_proof_plan_2026-06-08.md` records the same claim boundaries.
- `tools/missionscript_level100_tutorial_static_walkthrough_probe.py --check` passes.

## Follow-Up Child Lane

The next selected static-to-proof child lane is `MissionScript Level100 Tutorial Runtime Harness Boundary Proof Plan`. It should stay a planning/boundary slice until it selects copied/app-owned runtime inputs, stop conditions, source-selection constraints, no-mutation rules, expected artifacts, and proof boundaries.
