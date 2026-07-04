# MissionScript / IScript Proof Plan Readiness Note

Status: proof plan complete, not runtime proof
Date: 2026-06-08
Scope: `missionscript-iscript-proof-plan`

This readiness note records a public-safe static-to-proof planning slice for MissionScript / IScript. It is not a new static re-audit wave, not a runtime test, not a mission execution proof, not a live loose-MSL loading proof, not a save/career mutation proof, not a screenshot/capture proof, not a native input proof, not a BEA patch, not a Godot slice, and not a rebuild parity claim.

Primary static source: `missionscript-static-review-2026-05-26.md`. The plan records static authorities, child proof lanes, copied/app-owned guardrails, layout unknowns, script-corpus boundaries, and stop conditions before any executable proof work can start.

Current static closeout remains unchanged:

- Static Ghidra function-quality closure: `6411/6411 = 100.00%`.
- Static debt: `0 / 0 / 0`.
- Expanded post-100 static surface: `1560/1560 = 100.00%`.
- Active current-risk focused accounting: `1179/1179 = 100.00%`.
- Remaining active focused work: `0`.
- Wave911 focused remains historical-retired/non-reconstructable at `812/1408 = 57.67%`.

Static source evidence:

- Wave903 (`missionscript-static-review-wave903`): `169` selected MissionScript family rows, all commented and signature-clean after queue closure `6113/6113 = 100.00%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260526-095411_post_wave903_missionscript_static_review_verified`.
- Wave1189 (`wave1189-missionscript-bytecode-iscript-current-risk-review`): `7` MissionScript bytecode/IScript current-risk rows: `CInstructionOP_PLUS__VFunc_00_0052e180`, `CInstructionOP_MINUS__VFunc_00_0052e1d0`, `CInstructionOP_MULTIPLY__VFunc_00_0052e220`, `CInstructionOP_DIVIDE__VFunc_00_0052e270`, `CInstructionOP_CMP__VFunc_00_0052e330`, `IScript__Constructor`, and `CMissionScriptObjectCode__ClearFields_Thunk`; `CAsmInstruction__SpawnFromOpcode` was context only because Wave1120 already accounted it. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-164704_post_wave1189_missionscript_bytecode_iscript_current_risk_review_verified`.
- Wave1208 (`wave1208-cbooldatatype-current-risk-review`): `CBoolDataType__Equals`, `CBoolDataType__NotEquals`, and `CBoolDataType__Assign` reviewed with no mutation. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260607-040938_post_wave1208_cbooldatatype_current_risk_review_verified`.
- Script command registry: `ScriptCommandRegistry__InitBuiltins` writes `144` contiguous `0x40`-byte command descriptor records from `0x0064ce50` through `0x0064f210`.
- IScript handler family: `49` `IScript__*` functions, including `IScript__ScheduleEvent`, `IScript__SetSlotSave`, and `IScript__LevelWon`.
- VM/datatype/opcode surface: `37` datatype rows and `19` instruction/opcode rows, including `CBoolDataType__Equals`, `CBoolDataType__NotEquals`, and `CBoolDataType__Assign`.
- Event/object-code surface: `22` `CScriptObjectCode`, `13` `CScriptEventNB`, `7` `CMissionScriptObjectCode`, and `5` `CEventFunction` rows.
- Loose MSL index surface: `95` level rows, `795` loose event-name counts, `115` primary-complete calls, `42` secondary-complete calls, `102` primary-failed calls, `79` level-won calls, `13` level-lost calls, plus slot, thing/spawn, and message usage indexes.

Representative anchors:

| Surface | Static anchor |
| --- | --- |
| Command registry | `ScriptCommandRegistry__InitBuiltins`, `144` descriptor records, `0x0064ce50`, `0x0064f210`, `FollowWaypointWait`, `IsOverWater`, `PostEvent`, `SpawnThing` |
| IScript handlers | `IScript__ScheduleEvent`, `IScript__SetSlotSave`, `IScript__LevelWon`, `IScript__GetThingRef`, `IScript__SpawnThing`, `IScript__SetGoodieState`, `IScript__GetGoodieState` |
| VM/datatype/opcode | `CScriptObjectCode__Run`, `CVM`, `CAsmInstruction`, `CInstructionOP_CALL`, `CInstructionOP_RETURN`, `0x0052e180`, `0x0052e1d0`, `0x0052e220`, `0x0052e270`, `0x0052e330`, `script_state+0x218`, `script_object_code+0x68`, `CBoolDataType__Equals`, `CBoolDataType__Assign` |
| Event/object-code | `CScriptEventNB__PostEvent`, `CEventFunction`, `CMissionScriptObjectCode__LoadAsync`, `CStatementChain` |
| Game/career bridge | `CCareer__SetSlot`, `CGame__SetSlot`, `CGame__GetSlot`, `GetSlot`, `SetSlot`, `SetSlotSave`, `GetGoodieState`, `SetGoodieState`, `AddScore` |
| Corpus references | `mission-scripts-index.md`, `mission-events-index.md`, `mission-slot-usage.md`, `mission-thing-usage.md`, `mission-message-usage.md`, `level100`, `level500`, `level731`, `level742`, `level901` |

Proof-plan boundaries:

- The plan is limited to future copied-profile, copied-script, copied-resource, copied-file, or app-owned artifact-root work.
- Any future proof must select one child lane at a time: command descriptor schema, IScript command effect, VM/datatype/opcode behavior, event/object-code lifecycle, loose MSL corpus linkage, mission outcome/event path, slot/goodie/career bridge, thing/spawn/object-reference bridge, or message/objective/HUD command behavior.
- Any future proof must keep runtime mission loading, save/career mutation, input, audio/message/HUD output, and gameplay outcomes as separate claim lanes.
- Any future proof must record whether inputs are loose copied retail data, packed resource data, sanitized fixtures, or generated app-owned data.
- Any future proof must stop on installed-game mutation need, live loose-script ambiguity, packed-vs-loose resource ambiguity, private asset leakage risk, unexpected save/options mutation, unscoped native input, broad mission-simulation scope creep, event-name mismatch, or exact-layout ambiguity.

No runtime MissionScript execution, runtime command effects, runtime event outcomes, runtime mission objectives, level win/loss, score, slot, goodie, spawn, message, HUD, camera, AI, object-control behavior, live loose-MSL loading, packed-resource script selection, exact command descriptor schema, exact VM/datatype/opcode/object-code layout, exact source-body identity, BEA patching behavior, visual QA, Godot parity, rebuild parity, or no-noticeable-difference parity claim is made.
