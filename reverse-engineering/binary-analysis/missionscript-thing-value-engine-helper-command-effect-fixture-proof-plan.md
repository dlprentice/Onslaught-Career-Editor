# MissionScript Thing Value / Engine Helper Command-Effect Fixture Proof Plan

Status: complete static thing/engine dispatch table, not runtime proof
Last updated: 2026-06-09
Scope: `missionscript-thing-value-engine-helper-command-effect-fixture`

This proof completes the Thing Value / Engine Helper child lane selected after the [MissionScript HUD / Display Command-Effect Fixture Proof Plan](missionscript-hud-display-command-effect-fixture-proof-plan.md). It converts the completed Thing Value / Engine Helper static command-effect map into a finite static fixture table for clean-room planning without launching BEA, publishing private loose-MSL rows, reading private baselines, writing copied files, mutating Ghidra, starting Godot work, wiring product UI, or implementing a rebuild. The selected follow-up is the MissionScript Player-State / Score Command-Effect Fixture Proof Plan.

Machine-checkable artifact:

- [missionscript-thing-value-engine-helper-command-effect-fixture-proof-plan.v1.json](missionscript-thing-value-engine-helper-command-effect-fixture-proof-plan.v1.json)

Proof tokens:

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

## Static Authority

| Surface | Evidence |
| --- | --- |
| Descriptor context | Six descriptor rows: `41 SetWindVector`, `98 DisableWeapon`, `99 EnableFlightMode`, `138 TeleportOrientation`, `140 DisableSpawner`, and `141 SetName`. |
| Handler dispatch | Six Wave582 handlers: `0x00534fb0 IScript__SetThingValueViaVFunc198_FromArg`, `0x00534fe0 IScript__SetThingValueViaVFunc19C_FromArg`, `0x00535010 IScript__SetThingValueViaEngineHelper4FE390_FromArg`, `0x00535040 IScript__SetThingValueViaEngineHelper4FE3F0_FromArg`, `0x00535530 IScript__SetThingFloatViaVFunc1C8_FromArg`, and `0x00535560 IScript__SetThingRefViaCUnitHelper4FD830_FromArg`. |
| Getter slots | Static argument getter slots are `+0x38`, `+0x34`, and `+0x30` behind the shared guard `+0x34 & 0x10`. |
| Dispatch targets | Static targets are thing vfunc slots `+0x198`, `+0x19c`, and `+0x1c8`, engine helpers `CEngine__EnableThingByNameFlag` and `CEngine__DisableThingByNameFlag`, and unit helper `CUnit__SetFactionForHierarchy`. |
| Loose corpus context | Aggregate static command-token counts are `15` `DisableWeapon`, `1` `EnableFlightMode`, `2` `DisableSpawner`, `4` `SetName`, `5` `TeleportOrientation`, and `0` `SetWindVector`, for `27` direct non-comment loose-MSL rows across five commands with corpus rows. |
| Wave582 evidence | The source static proof accounts for `6` metadata rows, `6` tag rows, `6` xref rows, `534` instruction rows, `6` decompile rows, and `32` vtable rows. |

## Fixture Matrix

The focused probe recomputes six finite dispatch fixture cases from the static schema:

| Command | Descriptor | Static dispatch model | Boundary |
| --- | ---: | --- | --- |
| `SetWindVector` | `41` | `+0x30` getter into `CUnit__SetFactionForHierarchy` via `0x00535560 IScript__SetThingRefViaCUnitHelper4FD830_FromArg` | Static unit-helper call only; exact enum and runtime wind behavior remain unproven. |
| `DisableWeapon` | `98` | `+0x38` getter into thing vfunc slot `+0x198` via `0x00534fb0 IScript__SetThingValueViaVFunc198_FromArg` | Static vfunc-slot dispatch only; runtime weapon behavior remains unproven. |
| `EnableFlightMode` | `99` | `+0x38` getter into thing vfunc slot `+0x19c` via `0x00534fe0 IScript__SetThingValueViaVFunc19C_FromArg` | Static vfunc-slot dispatch only; runtime flight-mode behavior remains unproven. |
| `TeleportOrientation` | `138` | `+0x34` getter into thing vfunc slot `+0x1c8` via `0x00535530 IScript__SetThingFloatViaVFunc1C8_FromArg` | Static vfunc-slot dispatch only; runtime orientation behavior remains unproven. |
| `DisableSpawner` | `140` | `+0x38` getter into `CEngine__EnableThingByNameFlag` via `0x00535010 IScript__SetThingValueViaEngineHelper4FE390_FromArg` | Static engine-helper call only; the command/helper name pairing is not treated as runtime semantics. |
| `SetName` | `141` | `+0x38` getter into `CEngine__DisableThingByNameFlag` via `0x00535040 IScript__SetThingValueViaEngineHelper4FE3F0_FromArg` | Static engine-helper call only; the command/helper name pairing is not treated as runtime semantics. |

The fixture intentionally models the static dispatch surface, not actual object identity or mission behavior. Source paths and raw loose-MSL rows are not published in this fixture plan. The counterintuitive `DisableSpawner` and `SetName` helper labels are preserved exactly as static anchors and are not normalized into runtime claims.

## Claim Boundary

This proves a static thing-value/engine-helper fixture table for six descriptor context rows, three thing-vfunc dispatch cases, two engine-helper dispatch cases, and one unit-helper dispatch case, tied to saved handler metadata, getter slots, dispatch targets, aggregate command-token counts, and Wave582 evidence counts.

It does not prove runtime MissionScript execution, runtime command effects, runtime thing behavior, runtime `DisableWeapon`, `EnableFlightMode`, `DisableSpawner`, `SetName`, `TeleportOrientation`, or `SetWindVector` behavior, runtime object identity, runtime object lookup by name, runtime thing-state mutation, live loose-MSL loading, packed-resource script selection, exact command descriptor layout, exact command arity, exact argument type schema, exact thing layout, exact thing vfunc semantics, exact unit faction enum, source-selection observation, private-frame review, visual QA, Godot parity, Ghidra mutation, executable patching, product UI behavior, rebuild implementation, rebuild parity, or no-noticeable-difference parity.
