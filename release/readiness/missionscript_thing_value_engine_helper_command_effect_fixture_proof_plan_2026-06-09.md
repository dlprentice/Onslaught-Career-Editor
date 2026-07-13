# MissionScript Thing Value / Engine Helper Command-Effect Fixture Proof Plan Readiness Note

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 semantic revalidation:** Historical record; `0x00535560` comment correction. The original text below remains provenance rather than current semantic authority. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); exact records are in `reverse-engineering/binary-analysis/ghidra-full-reaudit-corrections-2026-07-13.json` and `reverse-engineering/binary-analysis/ghidra-targeted-revalidation-corrections-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Status: complete static thing/engine dispatch table, not runtime proof
Date: 2026-06-09
Scope: `missionscript-thing-value-engine-helper-command-effect-fixture`

This readiness note records the public-safe static fixture proof for the MissionScript Thing Value / Engine Helper command-effect lane after the completed MissionScript HUD / Display Command-Effect Fixture Proof Plan. The proof is backed by `missionscript-thing-value-engine-helper-command-effect-fixture-proof-plan.md`, `missionscript-thing-value-engine-helper-command-effect-fixture-proof-plan.v1.json`, and the focused probe `tools/missionscript_thing_value_engine_helper_command_effect_fixture_proof_plan_probe.py`.

Readiness tokens:

- `missionScriptThingValueEngineHelperCommandEffectFixtureProofPlanStatus=missionscript-thing-value-engine-helper-command-effect-fixture-proof-plan-complete-static-thing-engine-dispatch-table-not-runtime-proof`
- `previousSlice=MissionScript HUD / Display Command-Effect Fixture Proof Plan`
- `selectedNextSlice=MissionScript Player-State / Score Command-Effect Fixture Proof Plan`
- `selectedFixtureFamily=thing-value-engine-helper`
- `selectedFixturePath=thing-vfunc-engine-unit-helper-dispatch-table`
- `descriptorIndices=41/98/99/138/140/141`
- `descriptorRecordCount=6`
- `descriptorContextCaseCount=6`
- `handlerDispatchCaseCount=6`
- `thingVfuncDispatchCaseCount=3`
- `engineHelperDispatchCaseCount=2`
- `unitHelperDispatchCaseCount=1`
- `getterSlotCount=3`
- `dispatchTargetCount=6`
- `deterministicFixtureCaseCount=6`
- `totalStaticCommandStepCount=6`
- `effectAssertionCount=18`
- `directNonCommentLooseMslRows=27`
- `commandWithCorpusRows=5`
- `zeroCorpusCommandCount=1`
- `disableWeaponCallRows=15`
- `enableFlightModeCallRows=1`
- `disableSpawnerCallRows=2`
- `setNameCallRows=4`
- `teleportOrientationCallRows=5`
- `setWindVectorCallRows=0`
- `wave582InstructionRows=534`
- `wave582VtableRows=32`
- `fixtureSelectionOriginalRank=8`
- `falseGuardCount=58`
- `zeroCounterCount=44`
- `publicLeakCheck=PASS`
- `latestGhidraBackupClass=verified-static-backup-redacted`

Guard tokens:

- `runtimeExecution=false`
- `beLaunch=false`
- `sourcePathsPublic=false`
- `rawMslRowsPublic=false`
- `liveLooseMslLoading=false`
- `packedResourceScriptSelectionProven=false`
- `privateFrameReviewPerformed=false`
- `ghidraMutation=false`
- `godotWork=false`
- `rebuildImplementation=false`
- `runtimeObservationRows=0`
- `missionScriptRuntimeEvidenceRows=0`
- `runtimeCommandEffectRows=0`
- `runtimeThingBehaviorRows=0`
- `beProcessesAfterFixture=0`

Static dispatch anchors:

- `0x00534fb0 IScript__SetThingValueViaVFunc198_FromArg`
- `0x00534fe0 IScript__SetThingValueViaVFunc19C_FromArg`
- `0x00535010 IScript__SetThingValueViaEngineHelper4FE390_FromArg`
- `0x00535040 IScript__SetThingValueViaEngineHelper4FE3F0_FromArg`
- `0x00535530 IScript__SetThingFloatViaVFunc1C8_FromArg`
- `0x00535560 IScript__SetThingRefViaCUnitHelper4FD830_FromArg`
- Getter slots `+0x38`, `+0x34`, and `+0x30`
- Vfunc slots `+0x198`, `+0x19c`, and `+0x1c8`
- Helpers `CEngine__EnableThingByNameFlag`, `CEngine__DisableThingByNameFlag`, and `CUnit__SetFactionForHierarchy`
- Commands `DisableWeapon`, `EnableFlightMode`, `DisableSpawner`, `SetName`, `TeleportOrientation`, and `SetWindVector`

What this proves:

- The static fixture table has six bounded dispatch cases derived from the completed static Thing Value / Engine Helper schema.
- Aggregate command-token counts are preserved without publishing private loose-MSL rows.
- The fixture has no runtime, launch, Ghidra mutation, patch, Godot, product UI, rebuild, rebuild parity, or no-noticeable-difference claim.

What remains separate:

- Runtime MissionScript execution and runtime command effects.
- Runtime object identity and object lookup by name.
- Runtime thing, weapon, flight-mode, spawner, name, orientation, wind, or unit-faction behavior.
- Live loose-MSL loading and packed-resource script selection.
- Exact descriptor, datatype, thing, vfunc, enum, and source-body identity.
- Visual QA, Godot parity, executable patching, rebuild implementation, rebuild parity, and no-noticeable-difference parity.
