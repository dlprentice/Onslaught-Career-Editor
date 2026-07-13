# IScript.cpp - Mission Scripting Interface

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 live correction closeout:** 7 confirmed-apply records referenced in this document. Current live Ghidra reflects confirmed rows only; older conflicting text below is superseded only where confirmed. Use the [closeout](../ghidra-full-reaudit-closeout-2026-07-13.md); final per-address decisions and exact before/after metadata are in `reverse-engineering/binary-analysis/ghidra-reviewed-correction-decisions-2026-07-13.jsonl` and `reverse-engineering/binary-analysis/ghidra-reviewed-correction-plan-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Wave1189 current-risk update: Wave1189 (`wave1189-missionscript-bytecode-iscript-current-risk-review`) re-read and normalized comments/tags for `IScript__Constructor` plus adjacent MissionScript bytecode operator context as part of `7 MissionScript bytecode/IScript current-risk rows`. `CAsmInstruction__SpawnFromOpcode already accounted by Wave1120` and was not counted again. Static closure remains `6411/6411 = 100.00%` with `0 / 0 / 0` debt; Wave1108 current focused accounting is `808/1179 = 68.53%`; current focused candidates: 1169; live regenerated current focused candidates: 1169; remaining active focused work: 371; current risk candidates: 6166; fresh Ghidra export; comment/tag normalization; `updated=7 skipped=0`; `comment_only_updated=7`; `tags_added=63`; final dry updated=0 skipped=7; no rename; no signature change; no function-boundary change; no executable-byte change; Codex read-only consults used; no Cursor/Composer. `IScript__Constructor` is called by `CComplexThing__SetScript` and binds owner/script linkage through vtable 0x005e4f08, `script_object_code+0x68`, and local listener/state initialization; related operator anchors are `CInstructionOP_PLUS__VFunc_00_0052e180`, `CInstructionOP_MINUS__VFunc_00_0052e1d0`, `CInstructionOP_MULTIPLY__VFunc_00_0052e220`, `CInstructionOP_DIVIDE__VFunc_00_0052e270`, `CInstructionOP_CMP__VFunc_00_0052e330`, `CScriptObjectCode__GetTop`, datatype vtable slot +0x04, datatype vtable slot +0x08, datatype vtable slot +0x0c, datatype vtable slot +0x10, datatype vtable slot +0x18, and `script_state+0x218`; HUD teardown context includes `CMissionScriptObjectCode__ClearFields_Thunk` and `CHud__ShutDown`. Fresh exports verified `7 xref rows`, `208 instruction rows`, and `7 decompile rows`. Backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-164704_post_wave1189_missionscript_bytecode_iscript_current_risk_review_verified`; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction. Static clean-room target: rebuild-grade static contracts as a rebuild-grade specification for a future clean-room implementation aiming at no noticeable difference; exact IScript/CMonitor concrete layouts, exact source-body identity, runtime MissionScript behavior, runtime HUD/script teardown behavior, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof. Probe token anchor: Wave1189; wave1189-missionscript-bytecode-iscript-current-risk-review; 808/1179 = 68.53%; 7 MissionScript bytecode/IScript current-risk rows; current focused candidates: 1169; live regenerated current focused candidates: 1169; remaining active focused work: 371; current risk candidates: 6166; fresh Ghidra export; comment/tag normalization; updated=7 skipped=0; comment_only_updated=7; tags_added=63; final dry updated=0 skipped=7; no rename; no signature change; no function-boundary change; no executable-byte change; Codex read-only consults used; no Cursor/Composer; CAsmInstruction__SpawnFromOpcode already accounted by Wave1120; CInstructionOP_PLUS__VFunc_00_0052e180; CInstructionOP_MINUS__VFunc_00_0052e1d0; CInstructionOP_MULTIPLY__VFunc_00_0052e220; CInstructionOP_DIVIDE__VFunc_00_0052e270; CInstructionOP_CMP__VFunc_00_0052e330; IScript__Constructor; CMissionScriptObjectCode__ClearFields_Thunk; CScriptObjectCode__GetTop; CComplexThing__SetScript; CHud__ShutDown; datatype vtable slot +0x04; datatype vtable slot +0x08; datatype vtable slot +0x0c; datatype vtable slot +0x10; datatype vtable slot +0x18; script_state+0x218; script_object_code+0x68; vtable 0x005e4f08; 0 / 0 / 0; 6411/6411 = 100.00%; 7 xref rows; 208 instruction rows; 7 decompile rows; [maintainer-local-ghidra-backup-root]\BEA_20260606-164704_post_wave1189_missionscript_bytecode_iscript_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction; rebuild-grade static contracts; no noticeable difference; rebuild-grade specification.

> Source: `[maintainer-local-source-export-root]\MissionScript\IScript.cpp`
> Debug string address: `0x0064fa40`
> Last updated: 2026-06-01

## Overview

IScript.cpp implements the mission scripting interface for Battle Engine Aquila. This file contains script instruction handlers that provide high-level game functionality to the MSL (Mission Script Language) system.

The functions in this file are called by the script interpreter to execute commands like creating cameras, playing sounds, getting object references, and manipulating vectors.

## Wave1074 PrintText Boundary Recovery

Wave1074 (`script-text-console-boundary-wave1074`, `wave1074-readback-verified`) recovered and saved `0x00537c40 IScript__PrintText` as a previously missing Ghidra function boundary. Fresh registry evidence ties `0x0064d220 s_PrintText_0064f984` and handler field `0x0064d250` to the raw entry. The saved signature is `void __stdcall IScript__PrintText(void * script_args, void * unused_state, void * out_result)`.

The pre-state was `INSTRUCTION_NO_FUNCTION`; post read-back keeps a tight body from `0x00537c40` through `0x00537c69 RET 0xc` and does not absorb the next raw command at `0x00537c70`. Static body evidence reads `script_args[0]`, calls `CText__GetStringById`, then calls `CConsole__Printf` with `%w` from `0x0064fda4`. Queue closure is `6247/6247 = 100.00%`; Wave911 focused progress remains `812/1408 = 57.67%`; expanded static surface progress advances to `1358/1560 = 87.05%`; top-500 coverage remains `500/500 = 100.00%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260602-052830_post_wave1074_script_text_console_boundary_verified`.

Runtime MissionScript dispatch behavior, runtime console/log behavior, exact command descriptor schema, exact script datatype/object layouts, exact source-body identity, BEA patching, gameplay outcomes, and rebuild parity remain separate proof. Probe token anchor: Wave1074; script-text-console-boundary-wave1074; 0x00537c40 IScript__PrintText; s_PrintText_0064f984; 0x0064d220; 0x0064d250; 0x00537c69; 0x00537c70; CText__GetStringById; CConsole__Printf; %w; 812/1408 = 57.67%; 1358/1560 = 87.05%; 500/500 = 100.00%; 6247/6247 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260602-052830_post_wave1074_script_text_console_boundary_verified; boundary recovery.

## Wave1064 SetThing Command Bridge Re-Audit

Wave1064 (`iscript-setthing-command-bridge-wave1064`) re-read the existing SetThing command bridge handlers with no mutation. Primary evidence covers `0x00534fb0 IScript__SetThingValueViaVFunc198_FromArg`, `0x00534fe0 IScript__SetThingValueViaVFunc19C_FromArg`, `0x00535010 IScript__SetThingValueViaEngineHelper4FE390_FromArg`, `0x00535040 IScript__SetThingValueViaEngineHelper4FE3F0_FromArg`, `0x00535530 IScript__SetThingFloatViaVFunc1C8_FromArg`, and `0x00535560 IScript__SetThingRefViaCUnitHelper4FD830_FromArg`. The rows remain registered by `0x0052ff30 ScriptCommandRegistry__InitBuiltins`; static xrefs tie the helper bridge to `0x004fd830 CUnit__SetFactionForHierarchy`, `0x004fe390 CEngine__EnableThingByNameFlag`, and `0x004fe3f0 CEngine__DisableThingByNameFlag`.

Fresh exports verified primary `6/6/6/94/6` and context `12/12/14/2856/12` rows for metadata/tags/xrefs/instructions/decompile. Queue closure remains `6246/6246 = 100.00%`; Wave911 focused progress remains `812/1408 = 57.67%`; expanded static surface progress advances to `1199/1560 = 76.86%`; top-500 coverage remains `500/500 = 100.00%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-225655_post_wave1064_iscript_setthing_command_bridge_verified`. Runtime MissionScript dispatch/argument behavior, exact command descriptor schema, full script-corpus coverage, exact source identity, BEA patching, gameplay outcomes, and rebuild parity remain separate proof. Probe token anchor: Wave1064; iscript-setthing-command-bridge-wave1064; 0x00534fb0 IScript__SetThingValueViaVFunc198_FromArg; 0x00534fe0 IScript__SetThingValueViaVFunc19C_FromArg; 0x00535010 IScript__SetThingValueViaEngineHelper4FE390_FromArg; 0x00535040 IScript__SetThingValueViaEngineHelper4FE3F0_FromArg; 0x00535530 IScript__SetThingFloatViaVFunc1C8_FromArg; 0x00535560 IScript__SetThingRefViaCUnitHelper4FD830_FromArg; 0x004fd830 CUnit__SetFactionForHierarchy; 0x004fe390 CEngine__EnableThingByNameFlag; 0x004fe3f0 CEngine__DisableThingByNameFlag; 812/1408 = 57.67%; 1199/1560 = 76.86%; 500/500 = 100.00%; 6246/6246 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260601-225655_post_wave1064_iscript_setthing_command_bridge_verified; no mutation.

## Wave1049 Objective / Slot Bridge Re-Audit

Wave1049 (`endlevel-objective-progression-review-wave1049`) re-read the MissionScript objective handlers and slot bridge context with no mutation. Primary evidence covers `0x005343e0 IScript__PrimaryObjectiveComplete`, `0x00534410 IScript__SecondaryObjectiveComplete`, `0x00534440 IScript__PrimaryObjectiveFailed`, and `0x00534470 IScript__SecondaryObjectiveFailed`, which write objective text/state arrays consumed by CGame/END_LEVEL_DATA. Context keeps `IScript__SetSlot`, `IScript__SetSlotSave`, and `IScript__GetSlotBitValue` tied to `CGame__SetSlot`, `CGame__GetSlot`, and `CCareer__SetSlot`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-134936_post_wave1049_endlevel_objective_progression_review_verified`. Runtime mission-script dispatch/argument behavior, complete mission-script corpus coverage, exact command descriptor schema, concrete value/layout identity, BEA patching, gameplay outcomes, and rebuild parity remain separate proof.

## Wave864 Script Command Registry Read-Back

Wave864 script command registry static read-back (`script-command-registry-wave864`, `wave864-readback-verified`) saved the comment, tags, and `void __cdecl ScriptCommandRegistry__InitBuiltins(void)` signature for `0x0052ff30 ScriptCommandRegistry__InitBuiltins`. Probe token anchor: `Wave864 script command registry`; `script-command-registry-wave864`; `0x0052ff30 ScriptCommandRegistry__InitBuiltins`; `void __cdecl ScriptCommandRegistry__InitBuiltins(void)`; `144 contiguous 0x40-byte command descriptor records`; `s_FollowWaypointWait_0064fa14`; `s_IsOverWater_0064f234`; `IScript__ScheduleEvent`; `IScript__SetSlotSave`; `SetStealth`; `0x0053df40 CDXEngine__RenderTexturedBeamQuad`; `5810/6105 = 95.17%`; `[maintainer-local-ghidra-backup-root]\BEA_20260525-153044_post_wave864_script_command_registry_verified`.

Static evidence shows the initializer writes 144 contiguous 0x40-byte command descriptor records from `0x0064ce50` through `0x0064f210`, with name-field assignments from `s_FollowWaypointWait_0064fa14` to `s_IsOverWater_0064f234`. The saved table includes mission command names such as `PostEvent`, `PlaySample`, `GetThingRef`, `GetVectorLength` / `Magnitude`, `Goto3PointPanCamera`, `SetGoodieState`, `SetSlotSave`, `SetStealth`, and `ToggleCockpit`, and stores handler fields including `IScript__ScheduleEvent`, `IScript__IsFriendly`, `IScript__PlaySound`, `IScript__Create3PointPanCamera`, `IScript__SetGoodieState`, and `IScript__SetSlotSave` plus many still-anonymous `LAB_...` handlers.

Static-to-proof follow-up: `world-thing-spawn-getthingref-object-reference-static-proof.md` and `world-thing-spawn-getthingref-object-reference-static.v1.json` complete static GetThingRef object-reference proof complete, not runtime proof, for the selected `training-target-zone-getthingref-family`. The slice preserves `9` raw selected `GetThingRef` rows, `8` selected unique object-reference rows, `8` selected unique file/thing rows, `1` duplicate-call row, `9` empty-spawner rows, `IScript__GetThingRef`, `CThingPtrDataType`, `0x0052ff30`, `0x0064ce50`, and `0x0064f210` as static corpus/descriptor/datatype anchors only; runtime object identity and runtime object lookup by name remain separate proof.

Queue after Wave864: `6105` total, `5810` commented, `295` commentless, `0` exact-undefined signatures, `0` `param_N`, strict proxy `5810/6105 = 95.17%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260525-153044_post_wave864_script_command_registry_verified`. Exact command descriptor schema, full command semantics, runtime MissionScript dispatch/argument behavior, source identity, BEA patching, and rebuild parity remain deferred.

2026-06-08 descriptor schema proof: `missionscript-command-descriptor-schema-proof.md` and `missionscript-command-descriptor-schema.v1.json` rebuild the finite command descriptor inventory from the saved `ScriptCommandRegistry__InitBuiltins` decompile. The schema accounts for `144` declared `0x40`-stride slots from `0x0064ce50` through `0x0064f210`, `144` slots with observed assignments, `143` observed name-field assignments, first observed name `FollowWaypointWait`, last observed name `IsOverWater`, and selected examples including `SpawnThing`, `PostEvent`, `LevelWon`, `SetSlotSave`, `ToggleCockpit`, and `SetStealth`. The final declared slot remains explicitly marked as lacking an observed name-field write; exact descriptor field layout, exact arity, runtime command dispatch, command effects, and rebuild parity remain separate proof.

2026-06-08 VM/datatype/opcode schema proof: `missionscript-vm-datatype-opcode-schema-proof.md` and `missionscript-vm-datatype-opcode-schema.v1.json` preserve the static interpreter-side context for these handlers: `0x0052d3d0 CAsmInstruction__SpawnFromOpcode`, `0x0052ec60 CDataType__CreateFromType`, `0x00539b00 CScriptObjectCode__Run`, `0x0052ea40 CAsmInstruction__ExecuteCall`, `script_state+0x218`, and `script_object_code+0x68`. The schema records the opcode/datatype/VM bridge that reaches the command descriptor table, but it does not prove runtime command effects, exact descriptor/VM/datatype/opcode layouts, or rebuild parity.

2026-06-08 event/object-code lifecycle schema proof: `missionscript-event-object-code-lifecycle-proof.md` and `missionscript-event-object-code-lifecycle.v1.json` now preserve the static IScript-side event lifecycle around `IScript__Constructor` and `IScript__ScheduleEvent`. The schema records the `script_object_code+0x68` owner back-pointer, `PostEvent(event_name)` ingress, the `0x0c`-byte scheduled-event payload, `DAT_00855190`, `DAT_0089c590`, `CScriptEventNB__PostEvent`, `CEventFunction__Execute`, `CScriptObjectCode__CallEvent`, `CScriptObjectCode__CallEventDirect`, descriptor dependency `0x0064ce50`, and `795` loose event-name counts as corpus context. This is static lifecycle accounting only, not runtime event dispatch/outcome, exact IScript/event-payload layout, live loose-MSL loading, patch, Godot, rebuild, or no-noticeable-difference proof.

2026-06-08 MissionScript Slot Command-Effect static proof: `missionscript-slot-command-effect-static-proof.md` and `missionscript-slot-command-effect.v1.json` preserve the static slot bridge for `SetSlot`, `GetSlot`, and `SetSlotSave`: descriptor slots `0x0064ecd0`, `0x0064ed10`, and `0x0064ef50`; handlers `IScript__SetSlot`, `IScript__SetSlotSave`, and `IScript__GetSlotBitValue`; game helpers `CGame__SetSlot` and `CGame__GetSlot`; persistent helper `CCareer__SetSlot`; runtime slot storage `CGame+0x308`; save true-view slot base `0x240A`; `6 slot-using level rows`; `18 detailed slot call rows`; `6 GetSlot`; `8 SetSlot`; and `4 SetSlotSave`. This is static command-effect bridge accounting only, not runtime command effects, runtime save behavior, runtime slot persistence, live loose-MSL loading, patch, Godot, rebuild, or no-noticeable-difference proof.

2026-06-08 MissionScript Objective/Outcome Command-Effect static proof: `missionscript-objective-outcome-command-effect-static-proof.md` and `missionscript-objective-outcome-command-effect.v1.json` preserve the static objective/outcome bridge for `PrimaryObjectiveComplete`, `SecondaryObjectiveComplete`, `PrimaryObjectiveFailed`, `SecondaryObjectiveFailed`, `LevelWon`, `LevelLost`, and `LevelLostString`: descriptor slots `0x0064e2d0`, `0x0064e310`, `0x0064e3d0`, `0x0064e410`, `0x0064d050`, `0x0064d010`, and `0x0064e890`; handlers `IScript__PrimaryObjectiveComplete`, `IScript__SecondaryObjectiveComplete`, `IScript__PrimaryObjectiveFailed`, `IScript__SecondaryObjectiveFailed`, `IScript__LevelWon`, `IScript__LevelLost`, and `IScript__LevelLostString`; primary/secondary objective text/state arrays; CGame/Career/EndLevelData bridge anchors `CGame__FillOutEndLevelData`, `CGame__DeclareLevelWon`, `CGame__DeclareLevelLost`, `CCareer__Update`, and `CEndLevelData__IsAllSecondaryObjectivesComplete`; event corpus counts `115 primary-complete`, `42 secondary-complete`, `102 primary-failed`, `79 LevelWon`, and `13 LevelLost`; and separate message corpus counts `110 LevelLost-family` and `71 LevelWon-family`. This is static command-effect bridge accounting only, not runtime command effects, runtime objective UI, runtime level outcomes, runtime save/career behavior, live loose-MSL loading, patch, Godot, rebuild, or no-noticeable-difference proof.

2026-06-08 MissionScript Message/Audio Command-Effect static proof: `missionscript-message-audio-command-effect-static-proof.md` and `missionscript-message-audio-command-effect.v1.json` preserve the static message/audio bridge for descriptor/name evidence `PlayCharMessage`, `PlayCharMessageWait`, `PlayPCharMessage`, `PlayPCharMessageWait`, `SwitchMessagesOn`, `SwitchMessagesOff`, `AddHelpMessage`, `PrintText`, and `AddMessage`; Wave584 body anchors `IScript__PlaySound`, `IScript__PlaySoundWithCallback`, `IScript__PlaySoundWithFade`, `IScript__PlaySoundWithPriority`, and `IScript__PlaySoundWithFadeAndPriority`; Wave1074 `IScript__PrintText`; and MessageBox context `CMessage__ctor_base`, `CMessageBox__InsertQueuedMessageSortedAndMaybeAdvance`, and `CMessageBox__StartVoiceOrFallbackTextReveal`. Loose corpus counts are `1365 PlayCharMessage`, `7 AddHelpMessage`, `1553 detailed message rows`, `11 speakers`, and `499 unique message tokens`. This is static descriptor/body/corpus bridge accounting only, not runtime message display, voice/audio playback, HUD output, queue ordering, exact descriptor/message layout, patch, Godot, rebuild, or no-noticeable-difference proof.

2026-06-08 MissionScript Goodie State Command-Effect static proof: `missionscript-goodie-state-command-effect-static-proof.md` and `missionscript-goodie-state-command-effect.v1.json` preserve the static Goodie-state bridge for descriptor/name evidence `SetGoodieState` and `GetGoodieState`; handlers `IScript__SetGoodieState` and `IScript__GetGoodieState`; storage bridge `g_Career_mGoodies[index-1]`, `0x00662564`, true-view save Goodie base `0x1F46`, `300` Goodie entries, and script index N maps to save Goodie index N-1; and `AddScore` as descriptor/name context only. This is static descriptor/body/save bridge accounting only, not runtime command effects, runtime Goodie state mutation, runtime save behavior, runtime Goodies wall behavior, live loose-MSL loading, exact descriptor/CCareer layout, patch, Godot, rebuild, or no-noticeable-difference proof.

2026-06-08 MissionScript Cutscene Pan-Camera / Position Command-Effect static proof: `missionscript-cutscene-pan-camera-position-command-effect-static-proof.md` and `missionscript-cutscene-pan-camera-position-command-effect.v1.json` preserve the static cutscene camera bridge for descriptor/name evidence `CreatePosition`, `Goto3PointPanCamera`, `Goto4PointPanCamera`, and `GotoPlayerCamera`; datatype evidence `CPositionDataType`, `0x005e4da4`, and value getter slot `+0x44`; Wave580 handler bodies `0x00533b70 IScript__Create3PointPanCamera` and `0x00533eb0 IScript__Create4PointPanCamera`; body anchors `CGame__SetCurrentCamera`, `CPanCamera`, `CBSpline`, and `DAT_0083d9c0`; and loose corpus anchors `GetThingRef("Fenrir")`, `level741`, `level742`, and `6 cutscene Fenrir GetThingRef rows`. This is static descriptor/datatype/body/corpus bridge accounting only, not runtime MissionScript execution, command effects, camera switching, cutscene playback, visible camera output, live loose-MSL loading, exact descriptor/datatype/camera layouts, patch, Godot, rebuild, or no-noticeable-difference proof.

2026-06-08 MissionScript Vector/Range Command-Effect static proof: `missionscript-vector-range-command-effect-static-proof.md` and `missionscript-vector-range-command-effect.v1.json` preserve the static vector/range value-helper bridge for Wave581 handlers `0x005345d0 IScript__GetVectorLength`, `0x005347b0 IScript__CheckValueInRange`, `0x00534b80 IScript__GetVectorX`, `0x00534c10 IScript__GetVectorY`, and `0x00534ca0 IScript__GetVectorZ`; datatype getter slots `+0x44` and `+0x34`; float result vtable `0x005e4ea4`; bool vtable context `0x005e4d50`; component offsets `+0`, `+4`, and `+8`; and raw descriptor context rows including `0x0064e850`, `0x0064e890`, and `0x0064e950`. A copied loose-MSL scan found no direct non-comment loose-MSL rows for the handler family. This is static descriptor/datatype/body accounting only, not runtime MissionScript execution, command effects, vector/range behavior, live loose-MSL loading, exact descriptor/datatype/vector layouts, patch, Godot, rebuild, or no-noticeable-difference proof.

2026-06-08 MissionScript Thing Value / Engine Helper Command-Effect static proof: `missionscript-thing-value-engine-helper-command-effect-static-proof.md` and `missionscript-thing-value-engine-helper-command-effect.v1.json` preserve the static thing-value/engine-helper bridge for Wave582 handlers `0x00534fb0 IScript__SetThingValueViaVFunc198_FromArg`, `0x00534fe0 IScript__SetThingValueViaVFunc19C_FromArg`, `0x00535010 IScript__SetThingValueViaEngineHelper4FE390_FromArg`, `0x00535040 IScript__SetThingValueViaEngineHelper4FE3F0_FromArg`, `0x00535530 IScript__SetThingFloatViaVFunc1C8_FromArg`, and `0x00535560 IScript__SetThingRefViaCUnitHelper4FD830_FromArg`; guard `+0x34 & 0x10`; getter slots `+0x38`, `+0x34`, and `+0x30`; thing vfunc slots `+0x198`, `+0x19c`, and `+0x1c8`; helpers `CEngine__EnableThingByNameFlag`, `CEngine__DisableThingByNameFlag`, and `CUnit__SetFactionForHierarchy`; descriptor commands `DisableWeapon`, `EnableFlightMode`, `DisableSpawner`, `SetName`, `TeleportOrientation`, and `SetWindVector`; and loose-MSL counts `15 DisableWeapon`, `1 EnableFlightMode`, `2 DisableSpawner`, `4 SetName`, `5 TeleportOrientation`, and `0 SetWindVector`. This is static descriptor/body/corpus bridge accounting only, not runtime MissionScript execution, command effects, thing behavior, live loose-MSL loading, exact descriptor/datatype/thing layouts, patch, Godot, rebuild, or no-noticeable-difference proof.

2026-06-08 MissionScript HUD / Display Command-Effect static proof: `missionscript-hud-display-command-effect-static-proof.md` and `missionscript-hud-display-command-effect.v1.json` preserve the static HUD/display bridge for descriptor rows `33 HighlightHudPart`, `34 UnHighlightHudPart`, `75 InitVariable`, `76 SetVariable`, and `77 ShutdownVariable`; descriptor addresses `0x0064d690`, `0x0064d6d0`, `0x0064e110`, `0x0064e150`, and `0x0064e190`; raw entries `&LAB_00535d70`, `&LAB_00535e60`, `&LAB_00536210`, `&LAB_00536230`, and `&LAB_00536260`; loose-MSL counts `13 / 13 / 77 / 146 / 26`; HUD anchors `CHud__SetHudComponent`, `CHud__RenderOverlayForViewpoint`, `CHudComponent__RenderPass`; and CWorld anchors `CWorld__PushWorldTextSlot`, `CWorld__UpdateWorldTextSlotTiming`, `CWorld__ClearWorldTextSlot`, and `CWorld__GetWorldTextSlotTimerValue`. This is static descriptor/corpus/context bridge accounting only, not runtime MissionScript execution, runtime HUD behavior, visible HUD flashing, runtime variable display, live loose-MSL loading, exact descriptor/datatype/HUD layouts, patch, Godot, rebuild, or no-noticeable-difference proof.

2026-06-08 MissionScript Player-State / Score Command-Effect static proof: `missionscript-player-state-score-command-effect-static-proof.md` and `missionscript-player-state-score-command-effect.v1.json` preserve the static player-state/score bridge for descriptor rows `84 AddScore`, `136 ToggleCockpit`, and `137 SetStealth`; descriptor addresses `0x0064e350`, `0x0064f050`, and `0x0064f090`; raw entries `IScript__Unk_00534410`, `&LAB_00533950`, and `&LAB_00533980`; the `0x00534410 IScript__SecondaryObjectiveComplete` alias boundary; copied loose-MSL counts `15 / 0 / 10` across `12 / 0 / 4` files; and source/static context `CGame::IncScore`, `CBattleEngine::ToggleCockpit`, and `CBattleEngine__HandleCloak`. This is static descriptor/name/corpus context only, not runtime score behavior, cockpit behavior, stealth behavior, weapon-fire/stealth interaction, live loose-MSL loading, exact descriptor/datatype/player-state layouts, patch, Godot, rebuild, or no-noticeable-difference proof.

## Wave926 IScript Lifecycle Re-Audit

Wave926 static re-audit (`iscript-lifecycle-review-wave926`) re-reviewed the IScript lifecycle pair with fresh read-only metadata, tags, xrefs, instructions, and decompile. No Ghidra mutation was needed. Probe token anchor: `Wave926`; `iscript-lifecycle-review-wave926`; `0x005333b0 IScript__Constructor`; `0x00533450 IScript__Destructor`; `CComplexThing__SetScript`; `IScript__ScalarDeletingDestructor`; `98/1408 = 6.96%`; `6113/6113 = 100.00%`; `[maintainer-local-ghidra-backup-root]\BEA_20260527-224500_post_wave926_iscript_lifecycle_review_verified`.

Fresh read-back confirmed:

| Address | Saved signature | Fresh xref evidence |
| --- | --- | --- |
| `0x005333b0` | `void * __thiscall IScript__Constructor(void * this, void * owner_complex_thing, void * script_object_code)` | `0x004f42a8` call from `CComplexThing__SetScript`; constructs the 0x3c-byte mission-script object, installs vtable `0x005e4f08`, stores owner/script pointers, and writes the back-pointer at `script_object_code+0x68`. |
| `0x00533450` | `void __thiscall IScript__Destructor(void * this)` | `0x00533433` call from `IScript__ScalarDeletingDestructor`; releases `this+0x0c`, walks and clears the listener/state set at `this+0x28`, and calls `CMonitor__Shutdown`. |

Evidence counts: `2` metadata rows, `2` tag rows, `2` xref rows, `95` function-body instruction rows, and `2` decompile rows. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260527-224500_post_wave926_iscript_lifecycle_review_verified`, `19` files, `173247367` bytes, `DiffCount=0`.

This remains static Ghidra evidence only. Runtime mission-script startup behavior, runtime mission-script teardown behavior, exact IScript layout/source identity, listener-node semantics, BEA patching, and rebuild parity remain separate proof.

## Wave1009 Static Shadow Script Command Boundary

Wave1009 static re-audit (`geometry-guide-heightfield-spine-review-wave1009`) recovered `0x00534ac0 ScriptCommand__SampleStaticShadowHeight_00534ac0` as a DATA-backed `ScriptCommandRegistry__InitBuiltins` callback that samples static-shadow height and returns an 8-byte script scalar wrapper allocated from MissionScript.cpp line token `0x2e3`. Queue closure is `6233/6233 = 100.00%`; verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260531-155648_post_wave1009_geometry_guide_heightfield_spine_review_verified`. Runtime MissionScript dispatch/value behavior, exact source method identity, concrete script-value layouts, BEA patching, and rebuild parity remain separate proof.

## Functions (44 listed)

| Address | Name | Purpose |
|---------|------|---------|
| 0x005333b0 | IScript__Constructor | Construct the 0x3c-byte mission-script object for `CComplexThing__SetScript` |
| 0x00533430 | IScript__ScalarDeletingDestructor | Scalar deleting destructor wrapper (`flags&1` frees `this`) |
| 0x00533450 | IScript__Destructor | Tear down the script object, listener/state set, and monitor base |
| 0x00533500 | IScript__CallEvent0AndRegisterNestedListeners | Dispatch event id 0 and register nested `CScriptEventNB` listeners |
| 0x005335a0 | IScript__CallEventId6_OrReset | Dispatch event id 6 or reset when the script VM is shutting down |
| 0x005335d0 | IScript__CreateThingRef | Create a reference to a game object |
| 0x00533660 | IScript__CallEventId5_OrReset | Dispatch event id 5 from destruction/cleanup-adjacent paths or reset |
| 0x00533690 | IScript__CreateThingRefWithSquad | Create thing ref with CRelaxedSquad initialization |
| 0x005337e0 | IScript__CallEventId3_OrReset | Dispatch event id 3 from shutdown/deploy-adjacent paths or reset |
| 0x00533840 | IScript__RestoreSavedStateAndGotoInstruction | Restore a saved script state and resume at the saved instruction cursor |
| 0x005338a0 | IScript__SetPlayerLives | Set per-player lives counters (`SetPlayerLives(player_index,lives)`) |
| 0x005338d0 | IScript__SetSlot | Set a slot bit in the runtime script bitset only (`SetSlot(slot,val)`) |
| 0x00533900 | IScript__SetSlotSave | Set a slot bit and persist it into career save data (`SetSlotSave(slot,val)`) |
| 0x005339a0 | IScript__GetSlotBitValue | Get career slot bit value (tech unlocks) |
| 0x00533a70 | IScript__SetGoodieState | Set `g_Career_mGoodies[index-1]` state (1-based index in scripts) |
| 0x00533aa0 | IScript__GetGoodieState | Get `g_Career_mGoodies[index-1]` state (cutscene/kill goodies) |
| 0x00533b70 | IScript__Create3PointPanCamera | Create camera pan with 3 control points |
| 0x00533eb0 | IScript__Create4PointPanCamera | Create camera pan with 4 control points |
| 0x005345d0 | IScript__GetVectorLength | Calculate vector magnitude (sqrt) |
| 0x005347b0 | IScript__CheckValueInRange | Check if value is within min/max bounds |
| 0x00534b80 | IScript__GetVectorX | Extract X component from vector |
| 0x00534c10 | IScript__GetVectorY | Extract Y component from vector |
| 0x00534ca0 | IScript__GetVectorZ | Extract Z component from vector |
| 0x00534fb0 | IScript__SetThingValueViaVFunc198_FromArg | Dispatch a script-provided value to selected thing vtable slot `+0x198` |
| 0x00534fe0 | IScript__SetThingValueViaVFunc19C_FromArg | Dispatch a script-provided value to selected thing vtable slot `+0x19c` |
| 0x00535010 | IScript__SetThingValueViaEngineHelper4FE390_FromArg | Enable a thing-name flag through the engine helper |
| 0x00535040 | IScript__SetThingValueViaEngineHelper4FE3F0_FromArg | Disable a thing-name flag through the engine helper |
| 0x00535530 | IScript__SetThingFloatViaVFunc1C8_FromArg | Dispatch a script-provided float to selected thing vtable slot `+0x1c8` |
| 0x00535560 | IScript__SetThingRefViaCUnitHelper4FD830_FromArg | Dispatch an integer/faction-like state through `CUnit__SetFactionForHierarchy` |
| 0x00535670 | IScript__GetThingName | Get name string of a game object |
| 0x005357b0 | IScript__GetThingTypeName | Get type/class name of a game object |
| 0x005362a0 | IScript__GetTextWidth | Calculate text width for UI rendering |
| 0x005363e0 | IScript__GetPlayerBattleEngine | Get player's battle engine reference |
| 0x00537410 | IScript__PlaySound | Play sound effect with default settings |
| 0x00537500 | IScript__PlaySoundWithCallback | Play sound with completion callback |
| 0x005375f0 | IScript__PlaySoundWithFade | Play sound with fade-in effect |
| 0x005377e0 | IScript__PlaySoundWithPriority | Play sound with priority level |
| 0x005378e0 | IScript__PlaySoundWithFadeAndPriority | Play sound with fade and priority |
| 0x00537c40 | IScript__PrintText | `PrintText(text_id)`: resolve text id through `CText__GetStringById` and print it through `CConsole__Printf("%w", ...)` |
| 0x00537fd0 | IScript__IsFriendly | Return whether the current script context is friendly (`IsFriendly()`) |
| 0x005381a0 | IScript__LevelLost | Declare the current level LOST (`LevelLost()`) |
| 0x005381c0 | IScript__LevelLostString | Declare the current level LOST with a text id (`LevelLostString(message_id)`) |
| 0x005381e0 | IScript__LevelWon | Declare the current level WON (`LevelWon()`) |
| 0x005383c0 | IScript__ScheduleEvent | Schedule a timed event (2000ms delay) |
| 0x0052ff30 | ScriptCommandRegistry__InitBuiltins | Wave864 built-in command descriptor registry initializer; 144 contiguous 0x40-byte records |

## Key Patterns

### Object Allocation Pattern
All functions use `OID__AllocObject` to create script result objects:
```c
puVar = OID__AllocObject(8, 0x18, "IScript.cpp", lineNumber);
if (puVar != NULL) {
    *puVar = vtable;        // Set vtable pointer
    puVar[1] = returnValue; // Set return value
}
```

### Camera Creation (3/4-Point Pan)
The camera functions create CBSpline objects for smooth camera movement:
- Transform world-space coordinates using thing's local matrix
- Create CSPtrSet lists of control points
- Allocate CBSpline with 3 points and initialize camera path

### Vector Operations
Simple extraction of X/Y/Z components from 12-byte vector structure:
- X at offset 0
- Y at offset 4
- Z at offset 8
- Length uses SQRT(x*x + y*y + z*z)

### Sound System Integration
Sound functions integrate with the sound manager:
- Use `FUN_004f2580` to convert sound enum to resource
- Support priority levels (0-10)
- Support fade effects with 0x3d4ccccd (0.05f) fade rate
- Event ID 0x7d1 (2001) for sound fade event

## Related Global Variables

| Address | Purpose |
|---------|---------|
| 0x0089c7f0 | Script system disabled flag |
| 0x008a9ac0 | Game state (4 = exiting) |
| 0x0089c528 | Last created script object |
| 0x008a9d84 | Sound manager initialized flag |
| 0x008a9d3c | Player array base |
| 0x0089c590 | Sound manager instance |

## VTables Referenced

| Address | Class |
|---------|-------|
| 0x005e4af8 | Script integer/thing ref result |
| 0x005e4b4c | Script thing ref with squad |
| 0x005e4d50 | Script boolean result |
| 0x005e4df8 | Script thing ref (final) |
| 0x005e4ea4 | Script float result |
| 0x005e4f1c | Sound fade state |
| 0x005e4f34 | Scheduled event |

## Error Strings

| Address | String | Function |
|---------|--------|----------|
| 0x0064fa9c | "FATAL ERROR: null thing passed to 'Create3PointPanCamera'" | IScript__Create3PointPanCamera |
| 0x0064fad8 | "FATAL ERROR: null thing passed to 'Create4PointPanCamera'" | IScript__Create4PointPanCamera |
| 0x0064fc3c | "Fatal error: Player %d has no battle engine!!!" | IScript__GetPlayerBattleEngine |
| 0x0064fc6c | "Warning: sorry no player %d returning 1" | IScript__GetPlayerBattleEngine |
| 0x0064fd30 | "_unknown_" | IScript__PlaySound (default sound name) |
| 0x0064fd3c | "SHIT this should never happen" | IScript__PlaySoundWithFade (error case) |

## Calling Convention

Wave578 split the IScript object/event helpers from the later interpreter command handlers. The lifecycle and event helpers at `0x005333b0..0x00533840` are normal retail thiscall-style helpers: `ECX=this`; constructor cleanup is `RET 0x8`; scalar-deleting and thing-ref helpers use `RET 0x4`; register-only event/reset helpers have no stack cleanup. CreateThingRef helpers are IScript thiscall helpers with RET 0x4, not the fixed three-stack-argument script-command ABI.

Later IScript command handlers are called by the MissionScript interpreter using a fixed **3-argument stack ABI** (most return with `ret 0x0c`, i.e. callee pops 12 bytes).

Observed (Steam `BEA.exe`):
- `arg0`: pointers to script argument objects (handlers call virtual getters on these objects)
- `arg1`: often unused (sometimes a state/flags value)
- `arg2`: out-result pointer for commands that return a value (e.g. `IScript__GetSlotBitValue` writes `*out`)

Virtual getters on argument objects (common offsets):
- vtable+`0x30`: integer getter (e.g. `LevelLostString(message_id)`)
- vtable+`0x34`: float getter
- vtable+`0x3c`: byte/bool-like getter (seen in `IScript__SetSlot`)
- vtable+`0x44`: vector getter

Note: many handlers ignore `arg1/arg2` (e.g. `IScript__LevelLost`), so Ghidra may infer fewer parameters even though the call ABI is fixed.

## Wave578 Static Read-Back

Wave578 static read-back hardened the IScript head tranche from `0x005333b0` through `0x00533840`. Saved Ghidra now records:

| Address | Saved signature | Bounded evidence |
| --- | --- | --- |
| `0x005333b0` | `void * __thiscall IScript__Constructor(void * this, void * owner_complex_thing, void * script_object_code)` | Called by `CComplexThing__SetScript` after a 0x3c-byte allocation; initializes CMonitor base/list state, installs vtable `0x005e4f08`, stores owner/script pointers, and writes `script_object_code+0x68` back to `this`. |
| `0x00533430` | `void * __thiscall IScript__ScalarDeletingDestructor(void * this, byte flags)` | Calls `IScript__Destructor`, then frees `this` through `DAT_009c3df0` when `flags&1` is set. |
| `0x00533450` | `void __thiscall IScript__Destructor(void * this)` | Corrected from constructor-like wording; releases `this+0x0c`, walks and releases the `this+0x28` listener/state set, clears it, then calls `CMonitor__Shutdown`. |
| `0x00533500` | `void __thiscall IScript__CallEvent0AndRegisterNestedListeners(void * this)` | Dispatches event id 0 or resets, then walks object-code lists and registers nested `CScriptEventNB` listeners. |
| `0x005335a0` | `void __thiscall IScript__CallEventId6_OrReset(void * this)` | Dispatches event id 6 through `CScriptObjectCode__CallEvent`, or resets when `DAT_008a9ac0 == 4`. |
| `0x005335d0` | `void __thiscall IScript__CreateThingRef(void * this, void * referenced_thing)` | Allocates an 8-byte result object at IScript.cpp line `0x10d`, installs vtable `0x005e4af8`, writes `DAT_0089c528`, and dispatches event id 1. |
| `0x00533660` | `void __thiscall IScript__CallEventId5_OrReset(void * this)` | Dispatches event id 5 from CComplexThing/CUnit death-cleanup-adjacent xrefs, or resets. |
| `0x00533690` | `void __thiscall IScript__CreateThingRefWithSquad(void * this, void * referenced_thing)` | Allocates an 8-byte wrapper at IScript.cpp line `0x11e`, lazily initializes the referenced thing pointer set, switches to vtable `0x005e4df8`, writes `DAT_0089c528`, and dispatches event id 4. |
| `0x005337e0` | `void __thiscall IScript__CallEventId3_OrReset(void * this)` | Dispatches event id 3 from BattleEngine/CUnit/CComplexThing shutdown/deploy-adjacent xrefs, or resets. |
| `0x00533840` | `void __thiscall IScript__RestoreSavedStateAndGotoInstruction(void * this)` | Copies saved script state from `this+0x38`, removes/releases it from the `this+0x28` set, then calls `CScriptObjectCode__GotoInstruction(DAT_0089c7f4)` unless reset is required. |

Read-back evidence: `ApplyIScriptHeadWave578.java` dry/apply/final dry reported `updated=0 skipped=10 renamed=0 would_rename=2 missing=0 bad=0`, then `updated=10 skipped=0 renamed=2 would_rename=0 missing=0 bad=0`, then `updated=0 skipped=10 renamed=0 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`. Post exports verified `10` metadata rows, `10` tag rows, `17` xref rows, `2610` instruction rows, `10` decompile rows, and `288` vtable rows. The current source snapshot does not include a matching `MissionScript/IScript.cpp` implementation body, so no `source-parity` tag was applied. This is static retail evidence only; runtime mission-script behavior remains unproven, and exact IScript/source hierarchy, concrete object/datatype layouts, BEA patching, and rebuild parity remain deferred.

## Wave579 Static Read-Back

Wave579 static read-back hardened the slot/goodie/player-lives command-handler tranche from `0x005338a0` through `0x00533aa0`. Saved Ghidra now records these rows as fixed three-stack-argument script command ABI handlers (`RET 0xc`):

| Address | Saved signature | Bounded evidence |
| --- | --- | --- |
| `0x005338a0` | `void __stdcall IScript__SetPlayerLives(void * script_args, void * unused_state, void * out_result)` | Reads `script_args[0]` and `script_args[1]` through datatype integer getter vtable slot `+0x30`, then calls `CGame__SetPlayerLives(&DAT_008a9a98, player_index, lives)`. |
| `0x005338d0` | `void __stdcall IScript__SetSlot(void * script_args, void * unused_state, void * out_result)` | Reads slot and byte/bool value, then calls `CGame__SetSlot(&DAT_008a9a98, slot, val)`. This updates runtime slot state only. |
| `0x00533900` | `void __stdcall IScript__SetSlotSave(void * script_args, void * unused_state, void * out_result)` | Calls `CGame__SetSlot`, then re-reads slot/value and calls `CCareer__SetSlot(&CAREER, slot, val)` to persist into `CCareer.mSlots`. |
| `0x005339a0` | `void __stdcall IScript__GetSlotBitValue(void * script_args, void * unused_state, void * out_result)` | Allocates an 8-byte bool result at IScript.cpp line `0x17d`, calls `CGame__GetSlot(&DAT_008a9a98, slot)`, installs vtable `0x005e4d50`, and writes the object through `out_result`. |
| `0x00533a70` | `void __stdcall IScript__SetGoodieState(void * script_args, void * unused_state, void * out_result)` | Reads `state` and 1-based script `index`, then writes `dword [index*4 + 0x00662560]`, equivalent to `g_Career_mGoodies[index-1]` because `g_Career_mGoodies` starts at `0x00662564`. |
| `0x00533aa0` | `void __stdcall IScript__GetGoodieState(void * script_args, void * unused_state, void * out_result)` | Allocates an 8-byte int result at IScript.cpp line `0x196`, reads `g_Career_mGoodies[index-1]`, installs vtable `0x005e4af8`, and writes the object through `out_result`. |

Read-back evidence: `ApplyIScriptSlotGoodieWave579.java` dry/apply/final dry reported `updated=0 skipped=6 renamed=0 would_rename=0 missing=0 bad=0`, then `updated=6 skipped=0 renamed=0 would_rename=0 missing=0 bad=0`, then `updated=0 skipped=6 renamed=0 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`. Post exports verified `6` metadata rows, `6` tag rows, `6` xref rows, `1326` instruction rows, `6` decompile rows, and `24` vtable rows. Wave579 separates runtime SetSlot from persistent SetSlotSave/CCareer mSlots and keeps the goodie 1-based-index underflow caveat explicit. This is static retail evidence only; runtime mission-script behavior remains unproven, script corpus coverage is separate evidence, and exact command descriptor/result datatype labels, BEA patching, and rebuild parity remain deferred.

## Wave580 Static Read-Back

Wave580 static read-back hardened the pan-camera and objective command-handler tranche from `0x00533b70` through `0x00534470`. Saved Ghidra now records these rows as fixed three-stack-argument script command ABI handlers (`RET 0xc`):

| Address | Saved signature | Bounded evidence |
| --- | --- | --- |
| `0x00533b70` | `void __stdcall IScript__Create3PointPanCamera(void * script_args, void * unused_state, void * out_result)` | Gets the target thing through datatype vtable slot `+0x40`, reports null thing string `0x0064fa9c`, transforms three vector arguments through the thing matrix or `DAT_0083d9c0`, builds a `CSPtrSet`/`CBSpline`, constructs a `CPanCamera`, and calls `CGame__SetCurrentCamera(&DAT_008a9a98,0,camera,1)`. |
| `0x00533eb0` | `void __stdcall IScript__Create4PointPanCamera(void * script_args, void * unused_state, void * out_result)` | Same pan-camera path with four vector arguments and null thing string `0x0064fad8`; the duration comes from datatype vtable slot `+0x34`. |
| `0x005343e0` | `void __stdcall IScript__PrimaryObjectiveComplete(void * script_args, void * unused_state, void * out_result)` | Reads `text_id` and objective index through datatype vtable slot `+0x30`, writes text to `DAT_008a9ae0 + index*8`, and writes state `1` to `DAT_008a9adc + index*8`. |
| `0x00534410` | `void __stdcall IScript__SecondaryObjectiveComplete(void * script_args, void * unused_state, void * out_result)` | Writes text to `DAT_008a9b30 + index*8` and state `1` to `DAT_008a9b2c + index*8`. |
| `0x00534440` | `void __stdcall IScript__PrimaryObjectiveFailed(void * script_args, void * unused_state, void * out_result)` | Writes text to the primary objective text array and state `2` to `DAT_008a9adc + index*8`. |
| `0x00534470` | `void __stdcall IScript__SecondaryObjectiveFailed(void * script_args, void * unused_state, void * out_result)` | Writes text to the secondary objective text array and state `2` to `DAT_008a9b2c + index*8`. |

Read-back evidence: `ApplyIScriptCameraObjectiveWave580.java` dry/apply/final dry reported `updated=0 skipped=6 renamed=0 would_rename=0 missing=0 bad=0`, then `updated=6 skipped=0 renamed=0 would_rename=0 missing=0 bad=0`, then `updated=0 skipped=6 renamed=0 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`. Post exports verified `6` metadata rows, `6` tag rows, `6` xref rows, `5454` instruction rows, `6` decompile rows, and `36` vtable rows. Queue refresh after Wave580 reports `6093` functions, `2939` commented, `3154` commentless, `1418` exact-undefined signatures, `1127` `param_N` signatures, and next queue head `0x005345d0 IScript__GetVectorLength`. This is static retail evidence only; runtime mission-script behavior remains unproven, runtime mission-objective UI behavior and script corpus coverage remain separate evidence, and exact command descriptor layout, BEA patching, and rebuild parity remain deferred.

## Wave581 Static Read-Back

Wave581 static read-back hardened the vector/range command-handler tranche from `0x005345d0` through `0x00534ca0`. Saved Ghidra now records these rows as fixed three-stack-argument script command ABI handlers (`RET 0xc`):

| Address | Saved signature | Bounded evidence |
| --- | --- | --- |
| `0x005345d0` | `void __stdcall IScript__GetVectorLength(void * script_args, void * unused_state, void * out_result)` | Reads a vector through datatype vtable slot `+0x44`, computes `sqrt(x*x+y*y+z*z)`, allocates a float result at IScript.cpp line `0x283`, installs vtable `0x005e4ea4`, and writes through `out_result`. |
| `0x005347b0` | `void __stdcall IScript__CheckValueInRange(void * script_args, void * unused_state, void * out_result)` | Reads value/min/max through float getter slot `+0x34`, accepts both ascending and descending bound order, allocates a boolean byte result through IScript.cpp lines `0x2a4`/`0x2ab`/`0x2af`, and writes through `out_result`. |
| `0x00534b80` | `void __stdcall IScript__GetVectorX(void * script_args, void * unused_state, void * out_result)` | Reads a vector through slot `+0x44`, copies component offset `+0`, and returns a float result through vtable `0x005e4ea4`. |
| `0x00534c10` | `void __stdcall IScript__GetVectorY(void * script_args, void * unused_state, void * out_result)` | Reads a vector through slot `+0x44`, copies component offset `+4`, and returns a float result through vtable `0x005e4ea4`. |
| `0x00534ca0` | `void __stdcall IScript__GetVectorZ(void * script_args, void * unused_state, void * out_result)` | Reads a vector through slot `+0x44`, copies component offset `+8`, and returns a float result through vtable `0x005e4ea4`. |

Read-back evidence: `ApplyIScriptVectorRangeWave581.java` dry/apply/final dry reported `updated=0 skipped=5 renamed=0 would_rename=0 missing=0 bad=0`, then `updated=5 skipped=0 renamed=0 would_rename=0 missing=0 bad=0`, then `updated=0 skipped=5 renamed=0 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`. Post exports verified `5` metadata rows, `5` tag rows, `5` xref rows, `3545` instruction rows, `5` decompile rows, and `24` vtable rows. Queue refresh after Wave581 reports `6093` functions, `2944` commented, `3149` commentless, `1413` exact-undefined signatures, `1127` `param_N` signatures, and next queue head `0x00534fb0 IScript__SetThingValueViaVFunc198_FromArg`. This is static retail evidence only; runtime mission-script behavior remains unproven, script corpus coverage remains separate evidence, and exact command descriptor layout, exact vector layout naming, BEA patching, and rebuild parity remain deferred.

## Wave582 Static Read-Back

Wave582 static read-back hardened the thing-value command-handler tranche at `0x00534fb0`, `0x00534fe0`, `0x00535010`, `0x00535040`, `0x00535530`, and `0x00535560`. Saved Ghidra now records these rows with the script-context IScript command ABI: `ECX=this` plus three stack arguments, and `RET 0xc` confirms callee cleanup for `script_args`, `unused_state`, and `out_result`.

| Address | Saved signature | Bounded evidence |
| --- | --- | --- |
| `0x00534fb0` | `void __thiscall IScript__SetThingValueViaVFunc198_FromArg(void * this, void * script_args, void * unused_state, void * out_result)` | Checks the argument flag bit `0x10`, reads through datatype getter vtable slot `+0x38`, and dispatches selected thing vtable slot `+0x198`. |
| `0x00534fe0` | `void __thiscall IScript__SetThingValueViaVFunc19C_FromArg(void * this, void * script_args, void * unused_state, void * out_result)` | Same guard/getter pattern, dispatching selected thing vtable slot `+0x19c`. |
| `0x00535010` | `void __thiscall IScript__SetThingValueViaEngineHelper4FE390_FromArg(void * this, void * script_args, void * unused_state, void * out_result)` | Reads a thing name through datatype getter slot `+0x38` and calls `CEngine__EnableThingByNameFlag` through the context engine pointer. |
| `0x00535040` | `void __thiscall IScript__SetThingValueViaEngineHelper4FE3F0_FromArg(void * this, void * script_args, void * unused_state, void * out_result)` | Reads a thing name through datatype getter slot `+0x38` and calls `CEngine__DisableThingByNameFlag` through the context engine pointer. |
| `0x00535530` | `void __thiscall IScript__SetThingFloatViaVFunc1C8_FromArg(void * this, void * script_args, void * unused_state, void * out_result)` | Reads a float through datatype getter slot `+0x34` and dispatches selected thing vtable slot `+0x1c8`. |
| `0x00535560` | `void __thiscall IScript__SetThingRefViaCUnitHelper4FD830_FromArg(void * this, void * script_args, void * unused_state, void * out_result)` | Reads an integer/faction-like state through datatype getter slot `+0x30` and calls `CUnit__SetFactionForHierarchy`. |

Read-back evidence: `ApplyIScriptThingValueWave582.java` dry/apply/final dry reported `updated=0 skipped=6 renamed=0 would_rename=0 missing=0 bad=0`, then `updated=6 skipped=0 renamed=0 would_rename=0 missing=0 bad=0`, then `updated=0 skipped=6 renamed=0 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`. Post exports verified `6` metadata rows, `6` tag rows, `6` xref rows, `534` instruction rows, `6` decompile rows, and `32` vtable rows. Queue refresh after Wave582 reports `6093` functions, `2950` commented, `3143` commentless, `1413` exact-undefined signatures, `1121` `param_N` signatures, and next queue head `0x00535330 CVM__VFunc_01_00535330`. This is static retail evidence only; runtime mission-script behavior remains unproven, script corpus coverage remains separate evidence, and exact command descriptor layout, exact vtable slot semantics, exact faction/state enum naming, BEA patching, and rebuild parity remain deferred.

## Wave584 Static Read-Back

Wave584 static read-back hardened the IScript object/audio command-handler tranche at `0x00535670`, `0x005357b0`, `0x00535fa0`, `0x005362a0`, `0x005363e0`, `0x00536ca0`, `0x00537410`, `0x00537500`, `0x005375f0`, `0x005377e0`, and `0x005378e0`. Saved Ghidra now records these rows with the script-context IScript command ABI: `ECX=this` plus three stack arguments, and `RET 0xc` confirms callee cleanup for `script_args`, `unused_state`, and `out_result`.

| Address | Saved signature | Bounded evidence |
| --- | --- | --- |
| `0x00535670` | `void __thiscall IScript__GetThingName(void * this, void * script_args, void * unused_state, void * out_result)` | Returns an empty `CStringDataType` unless the selected context has flag bit `+0x34 & 0x08`; otherwise calls `CBattleEngine__GetWeaponPhysicsName(context+0x10)` and writes the string result through `out_result`. |
| `0x005357b0` | `void __thiscall IScript__GetThingTypeName(void * this, void * script_args, void * unused_state, void * out_result)` | Same string-result shape, reading the type/name string through the selected context object's `+0x4b0/+0xa8` path before `CStringDataType__InitFromString`. |
| `0x00535fa0` | `void __thiscall IScript__Attack(void * this, void * script_args, void * unused_state, void * out_result)` | Reads a target thing from `script_args[0]` through datatype vtable slot `+0x40`, warns on null target, then routes targeting through either selected object vtable slot `+0x154` or `CUnit__PropagateTargetUnitToHierarchy(context+0x10,target_unit)` depending on observed flag bits. |
| `0x005362a0` | `void __thiscall IScript__GetTextWidth(void * this, void * script_args, void * unused_state, void * out_result)` | Reads a text-slot index through datatype getter slot `+0x30`, calls `CWorld__GetWorldTextSlotTimerValue(&DAT_00855090,slot_index)`, installs float-result vtable `0x005e4ea4`, and writes through `out_result`. |
| `0x005363e0` | `void __thiscall IScript__GetPlayerBattleEngine(void * this, void * script_args, void * unused_state, void * out_result)` | Reads a player index through datatype getter slot `+0x30`, warns/clamps values below one, checks player table `DAT_008a9d3c`, logs the no-battle-engine string when missing, and writes a `CThingPtrDataType` result. |
| `0x00536ca0` | `void __thiscall IScript__TriggerHitEffect(void * this, void * script_args, void * unused_state, void * out_result)` | Gates on selected context flag bit `+0x34 & 0x10`, reads a float through datatype getter slot `+0x34`, and dispatches selected context vtable slot `+0x1ac` with that float. |
| `0x00537410` | `void __thiscall IScript__PlaySound(void * this, void * script_args, void * unused_state, void * out_result)` | When `DAT_008a9d84` is present, seeds the default wide text from string `0x0064fd30`, reads text/float payloads through getter slots `+0x30`/`+0x34`, allocates a CMessage-sized object, and inserts it through `CMessageBox__InsertQueuedMessageSortedAndMaybeAdvance`. |
| `0x00537500` | `void __thiscall IScript__PlaySoundWithCallback(void * this, void * script_args, void * unused_state, void * out_result)` | Reads two text ids and a float payload from `script_args`, preserves the active-reader target when context flag bit `+0x34 & 0x10` is set, then queues a CMessage through the message-box path. |
| `0x005375f0` | `void __thiscall IScript__PlaySoundWithFade(void * this, void * script_args, void * unused_state, void * out_result)` | Creates a fade/tracking object, adds it to the IScript list at `this+0x28`, schedules event `0x7d1` through `CEventManager__GetNextFreeEvent` / `CScheduledEvent__Set`, and queues a message when possible. |
| `0x005377e0` | `void __thiscall IScript__PlaySoundWithPriority(void * this, void * script_args, void * unused_state, void * out_result)` | Reads text ids, a float payload, and priority from `script_args[0..3]`, then queues the message with the observed priority value. |
| `0x005378e0` | `void __thiscall IScript__PlaySoundWithFadeAndPriority(void * this, void * script_args, void * unused_state, void * out_result)` | Combines the fade-event setup with priority message enqueue: text ids from `script_args[0]/[1]`, float payload from `script_args[2]`, priority from `script_args[3]`, event `0x7d1`, and the same message-box insertion path. |

Read-back evidence: `ApplyIScriptObjectAudioWave584.java` dry/apply/final dry reported `updated=0 skipped=11 renamed=0 would_rename=0 missing=0 bad=0`, then `updated=11 skipped=0 renamed=0 would_rename=0 missing=0 bad=0`, then `updated=0 skipped=11 renamed=0 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`. Post exports verified `11` metadata rows, `11` tag rows, `11` xref rows, `4059` instruction rows, `11` decompile rows, and `64` vtable rows. Queue refresh after Wave584 reports `6093` functions, `2963` commented, `3130` commentless, `1404` exact-undefined signatures, `1117` `param_N` signatures, and next queue head `0x00537fd0 CBoolDataType__ctor_like_00537fd0`. This is static retail evidence only; runtime mission-script behavior remains unproven, script corpus coverage remains separate evidence, and exact command descriptor layout, exact audio/message/fade semantics, BEA patching, and rebuild parity remain deferred.

## Wave585 Static Read-Back

Wave585 static read-back hardened the IScript level/event command-handler tranche at `0x00537fd0`, `0x005381a0`, `0x005381c0`, `0x005381e0`, and `0x005383c0`. Saved Ghidra now records `IScript__IsFriendly` with the script-context IScript command ABI (`ECX=this` plus three stack arguments), while the level-result and post-event thunks are fixed three-stack-argument `__stdcall` handlers. Instruction read-back confirms `RET 0xc` on all five rows.

| Address | Saved signature | Bounded evidence |
| --- | --- | --- |
| `0x00537fd0` | `void __thiscall IScript__IsFriendly(void * this, void * script_args, void * unused_state, void * out_result)` | Renamed from `CBoolDataType__ctor_like_00537fd0` because `ScriptCommandRegistry__InitBuiltins` stores `s_IsFriendly_0064f9d4` with this function pointer at command slot `+0x30`. The body checks context flag bit `+0x34 & 0x10` and field `+0x138 == 0`, then allocates a `CEventFunctionParam` boolean result into `out_result`. |
| `0x005381a0` | `void __stdcall IScript__LevelLost(void * script_args, void * unused_state, void * out_result)` | Tiny fixed-ABI thunk for `LevelLost()`: ignores the script-engine arguments, sets `ECX=&DAT_008a9a98`, and calls `CGame__DeclareLevelLost(0,0)` for the no-message non-death loss path. |
| `0x005381c0` | `void __stdcall IScript__LevelLostString(void * script_args, void * unused_state, void * out_result)` | Fixed-ABI handler for `LevelLostString(message_id)`: reads `message_id` through datatype getter slot `+0x30`, pushes `player_died=0`, and calls `CGame__DeclareLevelLost(&DAT_008a9a98,message_id,0)`. |
| `0x005381e0` | `void __stdcall IScript__LevelWon(void * script_args, void * unused_state, void * out_result)` | Tiny fixed-ABI thunk for `LevelWon()`: ignores the script-engine arguments, sets `ECX=&DAT_008a9a98`, and calls `CGame__DeclareLevelWon`. |
| `0x005383c0` | `void __stdcall IScript__ScheduleEvent(void * script_args, void * unused_state, void * out_result)` | Fixed-ABI handler for registered `PostEvent(event_name)`: allocates a 0xc-byte event payload, reads the event name/reference through datatype getter slot `+0x48`, links the payload through `CSPtrSet__AddToHead(&DAT_00855190,item)`, and schedules `CEventManager__AddEvent_AtTime(&EVENT_MANAGER,2000,&DAT_0089c590,-1.0,0,item,0)`. |

Read-back evidence: `ApplyIScriptLevelEventWave585.java` dry/apply/final dry reported `updated=0 skipped=5 renamed=0 would_rename=1 missing=0 bad=0`, then `updated=5 skipped=0 renamed=1 would_rename=0 missing=0 bad=0`, then `updated=0 skipped=5 renamed=0 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`. Post exports verified `5` metadata rows, `5` tag rows, `5` xref rows, `1845` instruction rows, and `5` decompile rows. Queue refresh after Wave585 reports `6093` functions, `2965` commented, `3128` commentless, `1400` exact-undefined signatures, `1116` `param_N` signatures, and next queue head `0x00538470 CScriptEventNB__UpdateWaypointFollowing`. This is static retail evidence only; runtime mission-script behavior remains unproven, script corpus coverage remains separate evidence, and exact command descriptor layout, exact flag/team semantics for `IsFriendly`, exact event payload layout, BEA patching, and rebuild parity remain deferred.

## Integration with CGame Slot Bits

Slot-bit persistence is script-driven:
- `GetSlot(...)` returns `CGame__GetSlot(slot)` (`0x0046d410`) from the runtime slot-bitset at `CGame + 0x308`.
- `SetSlot(slot,val)` calls `CGame__SetSlot(slot,val)` (`0x0046d3a0`) on the runtime slot-bitset (persists into CCareer on LevelWon via END_LEVEL_DATA copy).
- `SetSlotSave(slot,val)` calls `CGame__SetSlot(slot,val)` (`0x0046d3a0`) and also persists the same flag into the career save bitmap via `CCareer__SetSlot(&CAREER, slot, val)` (`0x004214e0`).

Wave803 (`game-slot-helpers-wave803`, `wave803-readback-verified`) saved comments/tags on the underlying `0x0046d3a0 CGame__SetSlot` and `0x0046d410 CGame__GetSlot` rows without renames or signature changes. This is static read-back evidence only; runtime mission-script behavior remains a separate proof lane.

Goodie state manipulation is also script-driven:
- `GetGoodieState(index)` returns `g_Career_mGoodies[index-1]` as a scalar result.
- `SetGoodieState(index, state)` updates `g_Career_mGoodies[index-1]` in-place (scripts use 1-based indices).
- Retail state values are `0..3` (`GOODIE_UNKNOWN/INSTRUCTIONS/NEW/OLD`); see [`reverse-engineering/save-file/goodies-system.md`](../../save-file/goodies-system.md).
- Save-file mapping: goodie array starts at file offset `0x1F46`, so script index `N` maps to `0x1F46 + (N-1)*4`.

2026-05-07 read-back: `ExportFunctionsByAddressDecompile.java` dumped both Goodie state handlers from the local Ghidra project, and `tools/goodies_iscript_readback_probe.py --check` passed. The public-safe verifier confirms the exported `SetGoodieState` decompile writes through the script index path and the exported `GetGoodieState` decompile reads `g_Career_mGoodies[index-1]`. This proves the retail mission-script handlers are a real Goodie state access surface, but not that any current mission script targets Goodies 71-73.

## Notes

1. **Exception Handling**: All functions set up SEH (Structured Exception Handling) frames with Unwind handlers
2. **Memory Safety**: Functions check for NULL allocations before dereferencing
3. **Squad System**: Some thing refs automatically initialize CRelaxedSquad for AI control
4. **Matrix Operations**: Camera functions perform full 3x3 matrix multiplication for coordinate transformation
