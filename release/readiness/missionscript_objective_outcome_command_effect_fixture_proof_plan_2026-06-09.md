# MissionScript Objective/Outcome Command-Effect Fixture Proof Plan Readiness

Status: complete static objective/outcome effect table, not runtime proof
Date: 2026-06-09
Scope: `missionscript-objective-outcome-command-effect-fixture`

Artifacts:

- `reverse-engineering/binary-analysis/missionscript-objective-outcome-command-effect-fixture-proof-plan.md`
- `reverse-engineering/binary-analysis/missionscript-objective-outcome-command-effect-fixture-proof-plan.v1.json`
- `tools/missionscript_objective_outcome_command_effect_fixture_proof_plan_probe.py`

Key tokens:

- `missionScriptObjectiveOutcomeCommandEffectFixtureProofPlanStatus=missionscript-objective-outcome-command-effect-fixture-proof-plan-complete-static-objective-outcome-effect-table-not-runtime-proof`
- `previousSlice=MissionScript Cutscene Pan-Camera / Position Command-Effect Deterministic Fixture Proof Plan`
- `selectedNextSlice=MissionScript Message/Audio Command-Effect Fixture Proof Plan`
- `selectedFixtureFamily=objective-outcome`
- `selectedFixturePath=objective-state-and-level-result-effect-table`
- `descriptorIndices=7/8/82/83/86/87/105`
- `descriptorRecordCount=7`
- `objectiveHandlerCount=4`
- `outcomeHandlerCount=3`
- `handlerAnchorCount=7`
- `objectiveStateValueSet=1/2`
- `objectiveStorageFormulaCount=4`
- `levelOutcomeCallCount=3`
- `integerGetterSlot=+0x30`
- `wave580MetadataRows=6`
- `wave585MetadataRows=5`
- `wave1049MetadataRows=10`
- `eventCorpusLevelRows=95`
- `eventCorpusEventCount=795`
- `eventCorpusObjectiveIds=36`
- `eventCorpusPrimaryComplete=115`
- `eventCorpusSecondaryComplete=42`
- `eventCorpusPrimaryFailed=102`
- `eventCorpusLevelWon=79`
- `eventCorpusLevelLost=13`
- `messageCorpusLevelRows=67`
- `messageCorpusLevelLostFamily=110`
- `messageCorpusLevelWonFamily=71`
- `plannedObjectiveEffectCaseCount=4`
- `plannedOutcomeEffectCaseCount=3`
- `deterministicFixtureCaseCount=7`
- `integerSeedCount=9`
- `effectAssertionCount=11`
- `falseGuardCount=43`
- `zeroCounterCount=32`
- `publicLeakCheck=PASS`
- `latestGhidraBackupClass=verified-static-backup-redacted`
- `runtimeExecution=false`
- `beLaunch=false`
- `sourceBaselineRead=false`
- `privateArtifactMaterialized=false`
- `copiedFileMutation=false`
- `ghidraMutation=false`
- `godotWork=false`
- `rebuildImplementation=false`
- `runtimeObservationRows=0`
- `missionScriptRuntimeEvidenceRows=0`
- `runtimeCommandEffectRows=0`
- `runtimeObjectiveRows=0`
- `runtimeOutcomeRows=0`
- `beProcessesAfterFixture=0`

Static anchors:

| Surface | Evidence |
| --- | --- |
| Descriptors | `LevelLost` / `0x0064d010`, `LevelWon` / `0x0064d050`, `PrimaryObjectiveComplete` / `0x0064e2d0`, `SecondaryObjectiveComplete` / `0x0064e310`, `PrimaryObjectiveFailed` / `0x0064e3d0`, `SecondaryObjectiveFailed` / `0x0064e410`, and `LevelLostString` / `0x0064e890`. |
| Objective handlers | `0x005343e0 IScript__PrimaryObjectiveComplete`, `0x00534410 IScript__SecondaryObjectiveComplete`, `0x00534440 IScript__PrimaryObjectiveFailed`, and `0x00534470 IScript__SecondaryObjectiveFailed`. |
| Objective storage | `DAT_008a9ae0`, `DAT_008a9adc`, `DAT_008a9b30`, and `DAT_008a9b2c`; objective states `1` and `2`. |
| Outcome handlers | `0x005381a0 IScript__LevelLost`, `0x005381c0 IScript__LevelLostString`, and `0x005381e0 IScript__LevelWon`; bridge calls to `CGame__DeclareLevelLost` and `CGame__DeclareLevelWon`. |
| End-level context | `CGame__FillOutEndLevelData`, `CCareer__Update`, and `CEndLevelData__IsAllSecondaryObjectivesComplete`. |

Fixture matrix:

- Four objective effect fixture rows: complete/fail across primary and secondary objective arrays.
- Three outcome effect fixture rows: `LevelWon`, `LevelLost`, and `LevelLostString`.
- Seven deterministic fixture rows total with nine finite integer seeds and eleven static effect assertions.

What this proves:

- Static objective state/text write fixture planning for `PrimaryObjectiveComplete`, `SecondaryObjectiveComplete`, `PrimaryObjectiveFailed`, and `SecondaryObjectiveFailed`.
- Static level-result call skeleton fixture planning for `LevelWon`, `LevelLost`, and `LevelLostString`.
- Static corpus/accounting preservation for objective/outcome event counts and message-family counts.

What remains unproven:

- Runtime MissionScript execution.
- Runtime command effects.
- Runtime objective UI, level outcome, save, or career behavior.
- Live loose-MSL loading, packed-resource script selection, exact descriptor/arity/type/layout details, source-selection observation, private-frame review, visual QA, Godot parity, Ghidra mutation, executable patching, product UI behavior, rebuild implementation, rebuild parity, or no-noticeable-difference parity.
