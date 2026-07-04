# MissionScript / IScript Static Contract Readiness Note

Status: static contract extraction complete, not runtime proof
Date: 2026-06-08
Scope: `missionscript-iscript-static-contract`

This readiness note records the first child lane after the completed MissionScript / IScript proof plan (`missionscript-iscript-proof-plan.md`): an implementation-facing static contract extraction for the command registry, IScript handlers, VM/datatype/opcode core, event/object-code lifecycle, game/career bridge, thing/spawn/object-reference bridge, and loose MSL corpus boundaries.

This is not a new static re-audit wave, not a Ghidra mutation, not a runtime test, not a mission execution proof, not a live loose-MSL loading proof, not a save/career mutation proof, not a screenshot/capture proof, not a native input proof, not a BEA patch, not a Godot slice, and not a rebuild parity claim.

Current static closeout remains unchanged:

- Static Ghidra function-quality closure: `6411/6411 = 100.00%`.
- Static debt: `0 / 0 / 0`.
- Expanded post-100 static surface: `1560/1560 = 100.00%`.
- Active current-risk focused accounting: `1179/1179 = 100.00%`.
- Remaining active focused work: `0`.
- Wave911 focused remains historical-retired/non-reconstructable at `812/1408 = 57.67%`.

Static source evidence:

- Wave903 (`missionscript-static-review-wave903`): `169` selected MissionScript family rows, all commented and signature-clean after queue closure `6113/6113 = 100.00%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260526-095411_post_wave903_missionscript_static_review_verified`.
- Wave1189 (`wave1189-missionscript-bytecode-iscript-current-risk-review`): `7` MissionScript bytecode/IScript current-risk rows, with `CAsmInstruction__SpawnFromOpcode` context only because Wave1120 already accounted it. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-164704_post_wave1189_missionscript_bytecode_iscript_current_risk_review_verified`.
- Wave1208 (`wave1208-cbooldatatype-current-risk-review`): `CBoolDataType__Equals`, `CBoolDataType__NotEquals`, and `CBoolDataType__Assign` reviewed with no mutation. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260607-040938_post_wave1208_cbooldatatype_current_risk_review_verified`.

Representative contract anchors:

| Surface | Static anchor |
| --- | --- |
| Command registry | `ScriptCommandRegistry__InitBuiltins`, `144` contiguous `0x40`-byte command descriptor records, `0x0064ce50`, `0x0064f210`, `FollowWaypointWait`, `IsOverWater`, `PostEvent`, `SpawnThing`, `SetSlotSave`, `LevelWon` |
| IScript handlers | `49` `IScript__*` functions, including `IScript__ScheduleEvent`, `IScript__SetSlotSave`, `IScript__LevelWon`, `IScript__GetThingRef`, `IScript__SpawnThing`, `IScript__SetGoodieState`, and `IScript__GetGoodieState` |
| VM/datatype/opcode | `37` datatype rows, `19` instruction/opcode rows, `CScriptObjectCode__Run`, `CAsmInstruction__SpawnFromOpcode`, `CInstructionOP_PLUS__VFunc_00_0052e180`, `CInstructionOP_MINUS__VFunc_00_0052e1d0`, `CInstructionOP_MULTIPLY__VFunc_00_0052e220`, `CInstructionOP_DIVIDE__VFunc_00_0052e270`, `CInstructionOP_CMP__VFunc_00_0052e330`, `0x0052e180`, `0x0052e1d0`, `0x0052e220`, `0x0052e270`, `0x0052e330`, `CBoolDataType__Equals`, `CBoolDataType__NotEquals`, `CBoolDataType__Assign` |
| Event/object-code | `22` `CScriptObjectCode`, `13` `CScriptEventNB`, `7` `CMissionScriptObjectCode`, `5` `CEventFunction`, `CScriptEventNB__PostEvent`, `CMissionScriptObjectCode__LoadAsync`, `CMissionScriptObjectCode__ClearFields_Thunk` |
| Thing/spawn/corpus | `mission-thing-usage.md`, `57` level rows, `418` `GetThingRef`, `18` `SpawnThing`, `436` total thing/spawn refs, `95` level rows, `795` loose event-name counts |

Current child command-effect proof carried by this contract: `missionscript-goodie-state-command-effect-static-proof.md` and `missionscript-goodie-state-command-effect.v1.json` record the MissionScript Goodie State Command-Effect bridge for `SetGoodieState`, `GetGoodieState`, `IScript__SetGoodieState`, `IScript__GetGoodieState`, `g_Career_mGoodies[index-1]`, `0x00662564`, true-view save Goodie base `0x1F46`, `300` Goodie entries, script index N maps to save Goodie index N-1, and `AddScore` as descriptor/name context only.

Next suggested static child lane after this contract is `World / Thing / Spawn / Object-Reference Bridge Proof Plan`, because MissionScript `GetThingRef` / `SpawnThing`, world loading, `CWorldPhysicsManager` factories, `CThing` lifecycle, Unit/BattleEngine spawn use, and mesh/resource dependencies converge there. That future slice must remain copied/app-owned and static-to-proof planned before any runtime mission execution.

No runtime MissionScript execution, runtime command effects, runtime event outcomes, runtime mission objectives, level win/loss, score, slot, goodie, spawn, message, HUD, camera, AI, object-control behavior, live loose-MSL loading, packed-resource script selection, exact command descriptor schema, exact VM/datatype/opcode/object-code layout, exact source-body identity, BEA patching behavior, visual QA, Godot parity, rebuild parity, or no-noticeable-difference parity claim is made.
