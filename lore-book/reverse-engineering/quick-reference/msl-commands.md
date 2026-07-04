Status: active quick reference
Last updated: 2026-04-29
Source: migrated from archived Codex Onslaught skills during the skill clean-slate pass.
Summary: MSL command and mission scripting verb lookup.
# MSL Command Reference

Wave903 (`missionscript-static-review-wave903`) links this quick reference to the static binary command-dispatch review after queue closure `6113/6113 = 100.00%`: `ScriptCommandRegistry__InitBuiltins`, `144` command descriptor records from `0x0064ce50` through `0x0064f210`, `IScript__ScheduleEvent`, `IScript__SetSlotSave`, `IScript__LevelWon`, `CScriptObjectCode__Run`, `CScriptEventNB__PostEvent`, `CMissionScriptObjectCode__LoadAsync`, and `795` loose MSL event-name counts are reviewed as a static-coherent MissionScript/IScript core. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260526-095411_post_wave903_missionscript_static_review_verified`.

Static-to-proof planning for command descriptor, IScript handler, VM/datatype/opcode, event/object-code, and loose MSL corpus lanes is `../binary-analysis/missionscript-iscript-proof-plan.md`, with the implementation-facing child contract at `../binary-analysis/missionscript-iscript-static-contract.md`, the completed object-reference bridge lane at `../binary-analysis/world-thing-spawn-object-reference-proof-plan.md`, the completed copied-corpus object-reference schema lane at `../binary-analysis/world-thing-spawn-copied-corpus-schema-proof.md`, the completed `SpawnThing` spawner handoff lane at `../binary-analysis/world-thing-spawn-spawner-handoff-static-proof.md` / `../binary-analysis/world-thing-spawn-spawner-handoff-static.v1.json`, the completed `GetThingRef` target-zone object-reference lane at `../binary-analysis/world-thing-spawn-getthingref-object-reference-static-proof.md` / `../binary-analysis/world-thing-spawn-getthingref-object-reference-static.v1.json`, the completed descriptor inventory at `../binary-analysis/missionscript-command-descriptor-schema-proof.md` / `../binary-analysis/missionscript-command-descriptor-schema.v1.json`, the completed VM/datatype/opcode inventory at `../binary-analysis/missionscript-vm-datatype-opcode-schema-proof.md` / `../binary-analysis/missionscript-vm-datatype-opcode-schema.v1.json`, the completed event/object-code lifecycle map at `../binary-analysis/missionscript-event-object-code-lifecycle-proof.md` / `../binary-analysis/missionscript-event-object-code-lifecycle.v1.json`, and the completed MissionScript Slot Command-Effect map at `../binary-analysis/missionscript-slot-command-effect-static-proof.md` / `../binary-analysis/missionscript-slot-command-effect.v1.json`; runtime command effects, runtime event outcomes, runtime object identity, runtime object lookup by name, runtime slot persistence, live loose-MSL loading, and exact layouts remain separate proof.

World / Thing / Spawn GetThingRef Object-Reference Static Proof status: static GetThingRef object-reference proof complete, not runtime proof. The selected `training-target-zone-getthingref-family` preserves `9` raw selected `GetThingRef` rows, `8` selected unique object-reference rows, `8` selected unique file/thing rows, `1` duplicate-call row, and `9` empty-spawner rows through `IScript__GetThingRef`, `CThingPtrDataType`, `0x0052ff30`, `0x0064ce50`, and `0x0064f210` as static anchors only.

MissionScript Objective/Outcome Command-Effect static proof is now recorded at `../binary-analysis/missionscript-objective-outcome-command-effect-static-proof.md` / `../binary-analysis/missionscript-objective-outcome-command-effect.v1.json`. It maps `PrimaryObjectiveComplete`, `SecondaryObjectiveComplete`, `PrimaryObjectiveFailed`, `SecondaryObjectiveFailed`, `LevelWon`, `LevelLost`, and `LevelLostString` through IScript handlers, CGame/Career/EndLevelData anchors, event corpus counts, and separate message corpus counts. Runtime command effects, runtime objective UI, runtime level outcomes, runtime save/career behavior, live loose-MSL loading, exact layouts, patching, Godot, rebuild parity, and no-noticeable-difference parity remain separate proof.

MissionScript Message/Audio Command-Effect static proof is now recorded at `../binary-analysis/missionscript-message-audio-command-effect-static-proof.md` / `../binary-analysis/missionscript-message-audio-command-effect.v1.json`. It maps `PlayCharMessage`, `PlayCharMessageWait`, `PlayPCharMessage`, `PlayPCharMessageWait`, `SwitchMessagesOn`, `SwitchMessagesOff`, `AddHelpMessage`, `PrintText`, and `AddMessage` descriptor/name evidence through `IScript__PlaySound*`, `IScript__PrintText`, `CMessage__ctor_base`, `CMessageBox__InsertQueuedMessageSortedAndMaybeAdvance`, `CMessageBox__StartVoiceOrFallbackTextReveal`, `1365 PlayCharMessage`, `7 AddHelpMessage`, `1553 detailed message rows`, `11 speakers`, and `499 unique message tokens`. Runtime command effects, runtime message display, voice/audio playback, HUD output, queue ordering, live loose-MSL loading, exact layouts, patching, Godot, rebuild parity, and no-noticeable-difference parity remain separate proof.

MissionScript Goodie State Command-Effect static proof is now recorded at `../binary-analysis/missionscript-goodie-state-command-effect-static-proof.md` / `../binary-analysis/missionscript-goodie-state-command-effect.v1.json`. It maps `SetGoodieState`, `GetGoodieState`, `IScript__SetGoodieState`, `IScript__GetGoodieState`, `g_Career_mGoodies[index-1]`, `0x00662564`, true-view save Goodie base `0x1F46`, `300` Goodie entries, and script index N maps to save Goodie index N-1. `AddScore` is descriptor/name context only. Runtime command effects, runtime Goodie state mutation, runtime save behavior, runtime Goodies wall behavior, live loose-MSL loading, exact layouts, patching, Godot, rebuild parity, and no-noticeable-difference parity remain separate proof.

MissionScript Cutscene Pan-Camera / Position Command-Effect static proof is now recorded at `../binary-analysis/missionscript-cutscene-pan-camera-position-command-effect-static-proof.md` / `../binary-analysis/missionscript-cutscene-pan-camera-position-command-effect.v1.json`. It maps `CreatePosition`, `Goto3PointPanCamera`, `Goto4PointPanCamera`, `CPositionDataType`, `0x0064de90`, `0x0064ea90`, `0x005e4da4`, `0x00533b70 IScript__Create3PointPanCamera`, `0x00533eb0 IScript__Create4PointPanCamera`, `CGame__SetCurrentCamera`, `CPanCamera`, `CBSpline`, `DAT_0083d9c0`, `GetThingRef("Fenrir")`, `level741`, `level742`, and `6 cutscene Fenrir GetThingRef rows`. Runtime MissionScript execution, command effects, camera switching, cutscene playback, visible camera output, live loose-MSL loading, exact layouts, patching, Godot, rebuild parity, and no-noticeable-difference parity remain separate proof.

MissionScript Vector/Range Command-Effect static proof is now recorded at `../binary-analysis/missionscript-vector-range-command-effect-static-proof.md` / `../binary-analysis/missionscript-vector-range-command-effect.v1.json`. It maps `IScript__GetVectorLength`, `IScript__CheckValueInRange`, `IScript__GetVectorX`, `IScript__GetVectorY`, `IScript__GetVectorZ`, vector getter slot `+0x44`, float getter slot `+0x34`, float result vtable `0x005e4ea4`, bool vtable context `0x005e4d50`, component offsets `+0`, `+4`, and `+8`, and no direct non-comment loose-MSL rows for the handler family. Runtime MissionScript execution, command effects, vector/range behavior, live loose-MSL loading, exact layouts, patching, Godot, rebuild parity, and no-noticeable-difference parity remain separate proof.

MissionScript Thing Value / Engine Helper Command-Effect static proof is now recorded at `../binary-analysis/missionscript-thing-value-engine-helper-command-effect-static-proof.md` / `../binary-analysis/missionscript-thing-value-engine-helper-command-effect.v1.json`. It maps `DisableWeapon`, `EnableFlightMode`, `DisableSpawner`, `SetName`, `TeleportOrientation`, and `SetWindVector` descriptor context through Wave582 handlers `IScript__SetThingValueViaVFunc198_FromArg`, `IScript__SetThingValueViaVFunc19C_FromArg`, `IScript__SetThingValueViaEngineHelper4FE390_FromArg`, `IScript__SetThingValueViaEngineHelper4FE3F0_FromArg`, `IScript__SetThingFloatViaVFunc1C8_FromArg`, and `IScript__SetThingRefViaCUnitHelper4FD830_FromArg`; getter slots `+0x38`, `+0x34`, and `+0x30`; thing vfunc slots `+0x198`, `+0x19c`, and `+0x1c8`; helpers `CEngine__EnableThingByNameFlag`, `CEngine__DisableThingByNameFlag`, and `CUnit__SetFactionForHierarchy`; and loose-MSL counts `15 DisableWeapon`, `1 EnableFlightMode`, `2 DisableSpawner`, `4 SetName`, `5 TeleportOrientation`, and `0 SetWindVector`. Runtime MissionScript execution, command effects, thing behavior, live loose-MSL loading, exact layouts, patching, Godot, rebuild parity, and no-noticeable-difference parity remain separate proof.

MissionScript HUD / Display Command-Effect static proof is now recorded at `../binary-analysis/missionscript-hud-display-command-effect-static-proof.md` / `../binary-analysis/missionscript-hud-display-command-effect.v1.json`. It maps `HighlightHudPart`, `UnHighlightHudPart`, `InitVariable`, `SetVariable`, and `ShutdownVariable` descriptor rows `33/34/75/76/77`; raw entries `&LAB_00535d70`, `&LAB_00535e60`, `&LAB_00536210`, `&LAB_00536230`, and `&LAB_00536260`; loose-MSL counts `13 / 13 / 77 / 146 / 26`; HUD anchors `CHud__SetHudComponent`, `CHud__RenderOverlayForViewpoint`, `CHudComponent__RenderPass`; and CWorld world-text anchors `CWorld__PushWorldTextSlot`, `CWorld__UpdateWorldTextSlotTiming`, `CWorld__ClearWorldTextSlot`, and `CWorld__GetWorldTextSlotTimerValue`. Runtime MissionScript execution, runtime HUD behavior, visible HUD flashing, runtime variable display, message overlay behavior, render ordering, live loose-MSL loading, exact layouts, patching, Godot, rebuild parity, and no-noticeable-difference parity remain separate proof.

MissionScript Player-State / Score Command-Effect static proof is now recorded at `../binary-analysis/missionscript-player-state-score-command-effect-static-proof.md` / `../binary-analysis/missionscript-player-state-score-command-effect.v1.json`. It maps `AddScore`, `ToggleCockpit`, and `SetStealth` descriptor/corpus/source context: descriptor rows `84/136/137`; raw entries `IScript__Unk_00534410`, `&LAB_00533950`, and `&LAB_00533980`; the `0x00534410 IScript__SecondaryObjectiveComplete` alias boundary; loose-MSL counts `15 / 0 / 10`; file counts `12 / 0 / 4`; `CGame::IncScore`; `CBattleEngine::ToggleCockpit`; and `CBattleEngine__HandleCloak`. Runtime score behavior, cockpit behavior, stealth behavior, weapon-fire/stealth interaction, live loose-MSL loading, packed-vs-loose script selection, exact layouts, patching, Godot, rebuild parity, and no-noticeable-difference parity remain separate proof.

## Contents
- [Mission Outcome](#mission-outcome)
- [Object References](#object-references)
- [Entity Control](#entity-control)
- [Spawning](#spawning)
- [Dialog](#dialog)
- [Career Integration](#career-integration)
- [Distance/Position](#distanceposition)
- [Timing](#timing)
- [Control Flow](#control-flow)
- [Events](#events)
- [Thing Types](#thing-types)

## Mission Outcome

```msl
LevelWon();
LevelLostString(TEXT_CONSTANT);
PrimaryObjectiveComplete(num, TEXT);
PrimaryObjectiveFailed(num, TEXT);
SecondaryObjectiveComplete(num, TEXT);
SecondaryObjectiveFailed(num, TEXT);
```

## Object References

```msl
player = GetPlayer(1);
thing = GetThingRef("Object Name");
component = GetComponent(index);
```

## Entity Control

```msl
thing.Activate();
thing.Deactivate();
thing.Shutdown();
thing.SetVulnerable(TRUE/FALSE);
thing.SetObjective();
thing.UnsetObjective();
thing.EnableWeapon("Weapon Name");
thing.DisableWeapon("Weapon Name");
thing.EnableFlightMode();
thing.DisableFlightMode();
health = thing.GetHealth();
thing.SetHealth(value);
SetAIState(AI_OFF/AI_ON/AI_NORMAL/AI_DEFENSIVE);
```

## Spawning

```msl
thing.SpawnThing("Unit Type", "Spawner", count, "Name");
```

## Dialog

```msl
PlayCharMessage(CHARACTER, MSG, delay);
PlayCharMessageWait(CHARACTER, MSG, delay);
AddHelpMessage(HELP_CONSTANT);
```

## Characters

| Constant | Character |
|----------|-----------|
| P_TATIANA | Tatiana |
| P_KRAMER | Commander |
| P_RADAR | Radar op |
| P_TECHNICIAN | Tech |
| P_SURT | Surt |
| P_CARVER | Carver |

## Career Integration

```msl
GetSlot(SLOT_CONSTANT)         // Returns bool
SetSlot(SLOT, TRUE);           // Session only
SetSlotSave(SLOT, TRUE);       // Persists
GetGoodieState(id);
SetGoodieState(id, GOODIE_NEW);
AddScore(points);
```

## Tech Slots

| Slot | Constant |
|------|----------|
| 61 | SLOT_500_ROCKET |
| 62 | SLOT_500_SUB |
| 63-66 | SLOT_TUTORIAL_1-4 |

## Distance/Position

```msl
dist = thing1.GetDistToObj(thing2);
pos = CreatePosition(x, y, z);
thing.Teleport(position);
```

## Timing

```msl
Pause(seconds);
GameTime();
```

## Counting

```msl
count = GetNumUnits(BEHAVIOUR, ALLEGIANCE);
ratio = GetRatioBattleLineNodes(ALLEGIANCE);
// Note: FRIENDLY_ALLIGENCE (typo preserved)
```

## Control Flow

```msl
if (cond) { } else { }
switch(var) { case 0: { } }
while(cond) { }
for(n = 1; n <= 10; n = n + 1) { }
do_once { }  // Execute once only
```

## Events

```msl
event("Event Name") { }
PostEvent("Event Name");
```

## Thing Types

| Constant | Value |
|----------|-------|
| THING_TYPE_BATTLE_ENGINE | 8 |
| THING_TYPE_UNIT | 16 |
| THING_TYPE_MECH | 2049 |
| THING_TYPE_INFANTRY | 16384 |
| THING_TYPE_NAVAL | 32768 |
