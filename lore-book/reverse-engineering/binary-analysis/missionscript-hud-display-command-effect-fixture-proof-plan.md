# MissionScript HUD / Display Command-Effect Fixture Proof Plan

Status: complete static HUD/variable display effect table, not runtime proof
Last updated: 2026-06-09
Scope: `missionscript-hud-display-command-effect-fixture`

This proof completes the HUD/display child lane selected after the [MissionScript Message/Audio Command-Effect Fixture Proof Plan](missionscript-message-audio-command-effect-fixture-proof-plan.md). It converts the completed HUD/display static command-effect map into a finite fixture table for clean-room planning without launching BEA, publishing private source rows, reading private baselines, writing copied files, mutating Ghidra, starting Godot work, wiring product UI, or implementing a rebuild. The selected follow-up is the MissionScript Thing Value / Engine Helper Command-Effect Fixture Proof Plan.

Machine-checkable artifact:

- [missionscript-hud-display-command-effect-fixture-proof-plan.v1.json](missionscript-hud-display-command-effect-fixture-proof-plan.v1.json)

Proof tokens:

- `missionScriptHudDisplayCommandEffectFixtureProofPlanStatus=missionscript-hud-display-command-effect-fixture-proof-plan-complete-static-hud-variable-display-effect-table-not-runtime-proof`
- `previousSlice=MissionScript Message/Audio Command-Effect Fixture Proof Plan`
- `selectedNextSlice=MissionScript Thing Value / Engine Helper Command-Effect Fixture Proof Plan`
- `selectedFixtureFamily=hud-variable-display`
- `selectedFixturePath=hud-part-variable-display-effect-table`
- `descriptorIndices=33/34/75/76/77`
- `descriptorRecordCount=5`
- `descriptorContextCaseCount=5`
- `hudConstantCount=6`
- `variableTypeCount=6`
- `plannedHudPartToggleCaseCount=6`
- `plannedVariableLifecycleCaseCount=6`
- `deterministicFixtureCaseCount=12`
- `hudCommandStepCount=12`
- `variableCommandStepCount=18`
- `totalStaticCommandStepCount=30`
- `effectAssertionCount=30`
- `duplicateDescriptorBoundaryCount=2`
- `highlightHudPartCallRows=13`
- `unhighlightHudPartCallRows=13`
- `initVariableCallRows=77`
- `setVariableCallRows=146`
- `shutdownVariableCallRows=26`
- `hudStaticAnchorCount=9`
- `worldTextAnchorCount=5`
- `falseGuardCount=50`
- `zeroCounterCount=37`
- `publicLeakCheck=PASS`
- `latestGhidraBackupClass=verified-static-backup-redacted`

Guard tokens:

- `runtimeExecution=false`
- `beLaunch=false`
- `sourcePathsPublic=false`
- `rawMslRowsPublic=false`
- `privateFrameReviewPerformed=false`
- `exactTextOcrPerformed=false`
- `rawDialoguePublished=false`
- `ghidraMutation=false`
- `godotWork=false`
- `rebuildImplementation=false`
- `runtimeObservationRows=0`
- `missionScriptRuntimeEvidenceRows=0`
- `runtimeCommandEffectRows=0`
- `runtimeHudRows=0`
- `runtimeVariableDisplayRows=0`
- `beProcessesAfterFixture=0`

## Static Authority

| Surface | Evidence |
| --- | --- |
| Descriptor context | Five HUD/display descriptor rows: `33 HighlightHudPart` at `0x0064d690`, `34 UnHighlightHudPart` at `0x0064d6d0`, `75 InitVariable` at `0x0064e110`, `76 SetVariable` at `0x0064e150`, and `77 ShutdownVariable` at `0x0064e190`. Raw entry anchors are `&LAB_00535d70`, `&LAB_00535e60`, `&LAB_00536210`, `&LAB_00536230`, and `&LAB_00536260`. |
| HUD enum surface | Six public HUD part constants are modeled as static enum cases: `HUD_HEALTH_BAR`, `HUD_ENERGY_BAR`, `HUD_COMPASS`, `HUD_BATTLE_LINE_MAP`, `HUD_RADAR`, and `HUD_CURRENT_WEAPON`. |
| Variable enum surface | Six public variable display type constants are modeled as static enum cases: `VARIABLE_NUMBER`, `VARIABLE_NUMBER_AND_THRESHOLD`, `VARIABLE_TIMER`, `VARIABLE_PERCENTAGE`, `VARIABLE_PERCENTAGE_AND_THRESHOLD`, and `VARIABLE_TIME`. |
| Loose corpus context | Static command-token counts are `13` `HighlightHudPart`, `13` `UnHighlightHudPart`, `77` `InitVariable`, `146` `SetVariable`, and `26` `ShutdownVariable`, with file counts `2 / 2 / 41 / 45 / 18`. |
| HUD/static context | `CHud__SetHudComponent`, `CHud__RenderOverlayForViewpoint`, `CHudComponent__RenderPass`, and related HUD render/component anchors remain static planning context only. |
| World-text context | `CWorld__PushWorldTextSlot`, `CWorld__UpdateWorldTextSlotTiming`, `CWorld__ClearWorldTextSlot`, `CWorld__GetWorldTextSlotTimerValue`, and `DAT_00855090` remain adjacent static display context only. |

## Fixture Matrix

The focused probe recomputes twelve finite fixture cases from the static schema:

| Case class | Count | Static effect |
| --- | ---: | --- |
| HUD part toggle | 6 | Each HUD part constant maps to a static `HighlightHudPart` / `UnHighlightHudPart` descriptor-pair case. |
| Variable lifecycle | 6 | Each variable type constant maps to a static `InitVariable` / `SetVariable` / `ShutdownVariable` lifecycle case with finite text/value/threshold seeds. |
| Descriptor context | 5 | The raw descriptor entries remain context rows, not handler-body or runtime-effect proof. |

The fixture intentionally models the aggregate argument surface, not visible HUD behavior. Source paths and raw MSL rows are not published in this fixture plan. The raw descriptor entries are preserved because handler-body semantics, exact descriptor layout, exact arity, exact argument type schema, and any static call path into `CHud` or `CWorld` helpers remain unproven.

## Claim Boundary

This proves a static HUD/display fixture table for six HUD part toggle cases, six variable display lifecycle cases, and five descriptor context rows, tied to saved descriptor slots, public enum constants, loose command-token counts, HUD/static anchors, and world-text context.

It does not prove runtime MissionScript execution, runtime command effects, runtime HUD behavior, runtime HUD highlighting, visible HUD flashing, runtime variable display, runtime variable lifecycle, message overlay behavior, render ordering, runtime text lookup, live loose-MSL loading, packed-resource script selection, handler-body semantics, a static call path from descriptor raw entries into `CHud` functions, exact command descriptor layout, exact command arity, exact argument type schema, exact HUD layout, exact HUD component layout, exact variable display layout, exact world-text layout, source-selection observation, private-frame review, visual QA, Godot parity, Ghidra mutation, executable patching, product UI behavior, rebuild implementation, rebuild parity, or no-noticeable-difference parity.
