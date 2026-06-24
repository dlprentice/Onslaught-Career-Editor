# MissionScript HUD / Display Command-Effect Fixture Proof Plan Readiness

Status: complete static HUD/variable display effect table, not runtime proof
Date: 2026-06-09
Scope: `missionscript-hud-display-command-effect-fixture`

Artifacts:

- `reverse-engineering/binary-analysis/missionscript-hud-display-command-effect-fixture-proof-plan.md`
- `reverse-engineering/binary-analysis/missionscript-hud-display-command-effect-fixture-proof-plan.v1.json`
- `tools/missionscript_hud_display_command_effect_fixture_proof_plan_probe.py`

Key tokens:

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

Static anchors:

| Surface | Evidence |
| --- | --- |
| Descriptors | `HighlightHudPart`, `UnHighlightHudPart`, `InitVariable`, `SetVariable`, and `ShutdownVariable` at `0x0064d690`, `0x0064d6d0`, `0x0064e110`, `0x0064e150`, and `0x0064e190`. |
| Raw entries | `&LAB_00535d70`, `&LAB_00535e60`, `&LAB_00536210`, `&LAB_00536230`, and `&LAB_00536260`. |
| HUD context | `CHud__SetHudComponent`, `CHud__RenderOverlayForViewpoint`, and `CHudComponent__RenderPass`. |
| World-text context | `CWorld__PushWorldTextSlot`, `CWorld__UpdateWorldTextSlotTiming`, `CWorld__ClearWorldTextSlot`, and `CWorld__GetWorldTextSlotTimerValue`. |

Fixture matrix:

- Six HUD part toggle fixture rows.
- Six variable display lifecycle fixture rows.
- Five descriptor context rows.

What this proves:

- Static HUD part enum fixture planning for `HighlightHudPart` / `UnHighlightHudPart`.
- Static variable display lifecycle fixture planning for `InitVariable` / `SetVariable` / `ShutdownVariable`.
- Static descriptor, HUD/frontend, and world-text context for clean-room HUD/display planning.

What remains unproven:

- Runtime MissionScript execution.
- Runtime command effects.
- Runtime HUD behavior, HUD highlighting, visible HUD flashing, variable display, variable lifecycle, message overlay behavior, render ordering, or runtime text lookup.
- Live loose-MSL loading, packed-resource script selection, handler-body semantics, static call paths into `CHud`, exact descriptor/arity/type/HUD/component/variable/world-text layouts, source-selection observation, private-frame review, visual QA, Godot parity, Ghidra mutation, executable patching, product UI behavior, rebuild implementation, rebuild parity, or no-noticeable-difference parity.
