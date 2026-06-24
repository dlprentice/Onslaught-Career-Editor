# MissionScript Command-Effect Rebuild Interface Rollup Readiness Note

Status: complete static rollup, not runtime proof
Date: 2026-06-09
Scope: `missionscript-command-effect-rebuild-interface-rollup`

This readiness note records a public-safe static rollup that consolidates nine completed MissionScript command-effect proof/schema families into one rebuild-facing interface vocabulary. It does not run BEA, load MissionScripts at runtime, inspect private frames, mutate Ghidra, patch an executable, create a Godot project, or implement a rebuild.

Parent slice: `World / Thing / Spawn Static-To-Rebuild Contract Crosswalk Proof Plan`
Public proof path: `missionscript-command-effect-rebuild-interface-rollup.md`
Public schema path: `missionscript-command-effect-rebuild-interface-rollup.v1.json`
Proof title: `MissionScript Command-Effect Rebuild Interface Rollup Proof Plan`

Representative anchors:

| Family | Anchors |
| --- | --- |
| Slot bitset / save | `SetSlot`, `GetSlot`, `SetSlotSave`, `CGame__SetSlot`, `CGame__GetSlot`, `CCareer__SetSlot`. |
| Objective / outcome | `PrimaryObjectiveComplete`, `SecondaryObjectiveComplete`, `PrimaryObjectiveFailed`, `SecondaryObjectiveFailed`, `LevelLost`, `LevelLostString`, `LevelWon`. |
| Message / audio / console | `PlaySample`, `PrintText`, `AddMessage`, `PlayCharMessage`, `PlayCharMessageWait`, `PlayPCharMessage`, `PlayPCharMessageWait`, `SwitchMessagesOn`, `SwitchMessagesOff`, `AddHelpMessage`. |
| HUD / variable display | `HighlightHudPart`, `UnHighlightHudPart`, `InitVariable`, `SetVariable`, `ShutdownVariable`. |
| Goodie state / save | `SetGoodieState`, `GetGoodieState`, `g_Career_mGoodies`, true-view `0x1F46`, and the `AddScore` alias boundary. |
| Player-state / score | `AddScore`, `ToggleCockpit`, `SetStealth`, `CBattleEngine__HandleCloak`. |
| Cutscene camera / position | `CreatePosition`, `Goto3PointPanCamera`, `Goto4PointPanCamera`, `GotoPlayerCamera`, `CPositionDataType`, `CPanCamera`. |
| Vector / range helpers | `IScript__GetVectorLength`, `IScript__CheckValueInRange`, `IScript__GetVectorX`, `IScript__GetVectorY`, `IScript__GetVectorZ`. |
| Thing value / engine helper | `DisableWeapon`, `EnableFlightMode`, `DisableSpawner`, `SetName`, `TeleportOrientation`, `SetWindVector`. |

Readiness accounting:

- `rollupStatus=missionscript-command-effect-rebuild-interface-rollup-complete-static-interface-contract-not-runtime-proof`
- `missionScriptCommandEffectRebuildInterfaceRollupStatus=missionscript-command-effect-rebuild-interface-rollup-complete-static-interface-contract-not-runtime-proof`
- `selectedSourceProofCount=9`
- `sourceProofCount=9`
- `descriptorSchemaCount=1`
- `commandEffectSchemaCount=9`
- `sourceSchemaCount=10`
- `sourceMirrorPairCount=20`
- `commandFamilyCount=9`
- `descriptorDeclaredSlots=144`
- `descriptorStrideBytes=64`
- `descriptorSlotsWithAssignments=144`
- `descriptorObservedNameAssignments=143`
- `descriptorNamedRecordCount=129`
- `descriptorSelectedExampleCount=12`
- `descriptorRecordCount=52`
- `uniqueDescriptorTokenCount=48`
- `duplicateDescriptorTokenCount=4`
- `notClaimedTokenTotal=165`
- `sourceClaimsCount=29`
- `uniqueEvidenceWaveCount=16`
- `interfaceRowCount=9`
- `rollupTrueGuardCount=7`
- `falseGuardCount=60`
- `zeroCounterCount=25`
- `publicLeakCheck=PASS`
- `latestGhidraBackupClass=verified-static-backup-redacted`
- `selectedNextSlice=MissionScript Command-Effect Rebuild Fixture Selection Proof Plan`

What this proves:

- The nine completed MissionScript command-effect static proof families can be referenced as one implementation-facing rebuild interface rollup.
- Descriptor accounting is machine-checkable: the descriptor schema declares `144` slots, and `52` command-effect descriptor records collapse to `48` unique descriptor/name tokens with four deliberate duplicate descriptor indices: `33 HighlightHudPart`, `34 UnHighlightHudPart`, `84 AddScore`, and `105 LevelLostString`.
- The result is public-safe and static-only.

What remains unproven:

- Runtime MissionScript execution.
- Runtime command effects, event outcomes, HUD/message/audio output, Goodie/save mutation, score/stealth/cockpit behavior, camera behavior, vector/range behavior, or thing-helper behavior.
- Live loose-MSL loading or packed-resource script selection.
- Exact descriptor layout, command arity, datatype layout, handler mapping, or source-body identity.
- BEA patching behavior, visual QA, Godot parity, rebuild implementation, rebuild parity, or no-noticeable-difference parity.
