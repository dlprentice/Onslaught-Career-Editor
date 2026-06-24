# MissionScript Objective/Outcome Command-Effect Fixture Proof Plan

Status: complete static objective/outcome effect table, not runtime proof
Last updated: 2026-06-09
Scope: `missionscript-objective-outcome-command-effect-fixture`

This proof completes the objective/outcome child lane selected after the [MissionScript Cutscene Pan-Camera / Position Command-Effect Deterministic Fixture Proof Plan](missionscript-cutscene-pan-camera-position-deterministic-fixture-proof-plan.md). It converts the completed objective/outcome static command-effect map into a finite fixture table for clean-room planning without launching BEA, reading private baselines, writing copied files, mutating Ghidra, starting Godot work, wiring product UI, or implementing a rebuild. The selected follow-up is the MissionScript Message/Audio Command-Effect Fixture Proof Plan.

Machine-checkable artifact:

- [missionscript-objective-outcome-command-effect-fixture-proof-plan.v1.json](missionscript-objective-outcome-command-effect-fixture-proof-plan.v1.json)

Proof tokens:

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

Guard tokens:

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

## Static Authority

| Surface | Evidence |
| --- | --- |
| Descriptor slots | `LevelLost` index `7` / `0x0064d010`; `LevelWon` index `8` / `0x0064d050`; `PrimaryObjectiveComplete` index `82` / `0x0064e2d0`; `SecondaryObjectiveComplete` index `83` / `0x0064e310`; `PrimaryObjectiveFailed` index `86` / `0x0064e3d0`; `SecondaryObjectiveFailed` index `87` / `0x0064e410`; `LevelLostString` index `105` / `0x0064e890`. |
| Objective handlers | `0x005343e0 IScript__PrimaryObjectiveComplete`, `0x00534410 IScript__SecondaryObjectiveComplete`, `0x00534440 IScript__PrimaryObjectiveFailed`, and `0x00534470 IScript__SecondaryObjectiveFailed` read integer arguments through datatype getter `+0x30`. |
| Objective storage | Primary text/state writes use `DAT_008a9ae0` and `DAT_008a9adc`; secondary text/state writes use `DAT_008a9b30` and `DAT_008a9b2c`; state value `1` is complete and state value `2` is failed. |
| Outcome handlers | `0x005381a0 IScript__LevelLost`, `0x005381c0 IScript__LevelLostString`, and `0x005381e0 IScript__LevelWon` bridge to `CGame__DeclareLevelLost` or `CGame__DeclareLevelWon`. |
| End-level context | `CGame__FillOutEndLevelData`, `CCareer__Update`, and `CEndLevelData__IsAllSecondaryObjectivesComplete` are retained as static context for level-result snapshot/career plumbing. |

## Fixture Matrix

The focused probe recomputes seven finite fixture cases from the static schema:

| Case | Command | Static effect |
| --- | --- | --- |
| `PrimaryObjectiveComplete-objective-0-text-100` | `PrimaryObjectiveComplete` | Write text id `100` to `DAT_008a9ae0 + index*8`; write state `1` to `DAT_008a9adc + index*8`. |
| `SecondaryObjectiveComplete-objective-1-text-200` | `SecondaryObjectiveComplete` | Write text id `200` to `DAT_008a9b30 + index*8`; write state `1` to `DAT_008a9b2c + index*8`. |
| `PrimaryObjectiveFailed-objective-2-text-300` | `PrimaryObjectiveFailed` | Write text id `300` to `DAT_008a9ae0 + index*8`; write state `2` to `DAT_008a9adc + index*8`. |
| `SecondaryObjectiveFailed-objective-3-text-400` | `SecondaryObjectiveFailed` | Write text id `400` to `DAT_008a9b30 + index*8`; write state `2` to `DAT_008a9b2c + index*8`. |
| `LevelWon` | `LevelWon` | Static call skeleton to `CGame__DeclareLevelWon`. |
| `LevelLost` | `LevelLost` | Static call skeleton to `CGame__DeclareLevelLost` with zero message/context arguments. |
| `LevelLostString` | `LevelLostString` | Static call skeleton to `CGame__DeclareLevelLost` with message id seed `500` from getter slot `+0x30`. |

The objective fixture rows assert only finite integer seed handling, text-array/state-array formulas, and observed state values. The outcome fixture rows assert only one call skeleton per command and keep message/text resolution outside this proof.

## Claim Boundary

This proves a static objective/outcome fixture table for four objective state/text write cases and three level-result call skeleton cases, tied to saved descriptor slots, saved handler anchors, and public-safe corpus counts. It also preserves the event corpus counts and message corpus counts as reference accounting.

It does not prove runtime MissionScript execution, runtime command effects, runtime objective state writes, runtime objective UI behavior, runtime level outcome behavior, runtime save behavior, runtime career progression, live loose-MSL loading, packed-resource script selection, exact command descriptor layout, exact command arity, exact argument type schema, exact `CGame` layout, exact `CCareer` layout, exact end-level data layout, objective index bounds, text id resolution, message id resolution, event ordering, mission success/failure criteria, source-selection observation, private-frame review, visual QA, Godot parity, Ghidra mutation, executable patching, product UI behavior, rebuild implementation, rebuild parity, or no-noticeable-difference parity.
