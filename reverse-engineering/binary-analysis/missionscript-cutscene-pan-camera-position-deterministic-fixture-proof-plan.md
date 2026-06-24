# MissionScript Cutscene Pan-Camera / Position Command-Effect Deterministic Fixture Proof Plan

Status: complete static finite camera-plan fixture proof, not runtime proof
Last updated: 2026-06-09
Scope: `missionscript-cutscene-pan-camera-position-deterministic-fixture`

This proof completes the cutscene-camera-position child lane selected by the [MissionScript Command-Effect Post-Goodie Selection Refresh Proof Plan](missionscript-command-effect-post-goodie-selection-refresh.md). It turns the completed static cutscene pan-camera/position evidence into a public-safe deterministic fixture matrix without launching BEA, observing runtime MissionScript execution, reading private baselines, writing copied files, mutating Ghidra, patching an executable, starting Godot work, wiring product UI, or implementing a rebuild.

Machine-checkable artifact:

- [missionscript-cutscene-pan-camera-position-deterministic-fixture-proof-plan.v1.json](missionscript-cutscene-pan-camera-position-deterministic-fixture-proof-plan.v1.json)

Proof tokens:

- `missionScriptCutscenePanCameraPositionDeterministicFixtureProofPlanStatus=missionscript-cutscene-pan-camera-position-deterministic-fixture-proof-plan-complete-static-finite-camera-plan-not-runtime-proof`
- `previousSlice=MissionScript Command-Effect Post-Goodie Selection Refresh Proof Plan`
- `selectedNextSlice=MissionScript Objective/Outcome Command-Effect Fixture Proof Plan`
- `selectedFixtureFamily=cutscene-camera-position`
- `selectedFixturePath=cutscene-position-finite-camera-plan`
- `sourceProofCount=5`
- `descriptorIndices=65/113/114/115`
- `descriptorRecordCount=4`
- `positionDatatypeTypeId=6`
- `positionDatatypeSizeBytes=20`
- `positionPayloadReadCount=3`
- `positionGetterSlot=+0x44`
- `handlerAnchorCount=2`
- `wave580MetadataRows=6`
- `wave580TagRows=6`
- `wave580XrefRows=6`
- `wave580DecompileRows=6`
- `wave580InstructionRows=5454`
- `wave580VtableRows=36`
- `fenrirGetThingRefRowsInSelectedLevels=17`
- `cutsceneFenrirGetThingRefRows=6`
- `plannedPositionCaseCount=3`
- `plannedPositionFloatAssertionCount=9`
- `plannedCameraPlanCaseCount=1`
- `plannedCameraPlanAssertionCount=6`
- `deterministicFixtureCaseCount=4`
- `finiteOnlyCaseCount=4`
- `contextOnlyDescriptorCount=2`
- `falseGuardCount=48`
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
- `runtimeCameraRows=0`
- `beProcessesAfterFixture=0`

## Static Authority

| Surface | Evidence |
| --- | --- |
| Selected lane | The post-Goodie selection refresh chose this lane after slot/save, vector/range, and Goodie/save fixture families completed. |
| Descriptor context | `CreatePosition` index `65` / `0x0064de90`, `Goto3PointPanCamera` index `113` / `0x0064ea90`, `Goto4PointPanCamera` index `114` / `0x0064ead0`, and `GotoPlayerCamera` index `115` / `0x0064eb10`. |
| Position datatype | `CPositionDataType`, type id `6`, vtable `0x005e4da4`, size `20`, payload reads `+0x04/+0x08/+0x0c`, value getter `+0x44`, and open `+0x10` boundary. |
| Handler anchors | `0x00533b70 IScript__Create3PointPanCamera`, `0x00533eb0 IScript__Create4PointPanCamera`, `0x00416d10 CBSpline__ctor`, `0x004198d0 CPanCamera__ctor`, and `0x004705e0 CGame__SetCurrentCamera`. |
| Corpus context | Public Fenrir cutscene example with `GetThingRef context only`, `Fenrir`, three `CreatePosition` triples, and `durationSeconds=15.0`. |

Descriptor rows remain raw static context because the observed row names and raw entries do not justify exact descriptor layout, exact command arity, exact argument type schema, or selected runtime mission usage. `Goto4PointPanCamera` and `GotoPlayerCamera` are intentionally context-only rows in this fixture lane.

## Fixture Matrix

The finite-only matrix is recomputed by the focused probe:

| Case | Command | Payload |
| --- | --- | --- |
| `fenrir-cutscene-pos1` | `CreatePosition` | `[-80.0, 20.0, -30.0]` |
| `fenrir-cutscene-pos2` | `CreatePosition` | `[0.0, 40.0, 60.0]` |
| `fenrir-cutscene-pos3` | `CreatePosition` | `[100.0, 20.0, 40.0]` |
| `fenrir-goto3point-pan-camera` | `Goto3PointPanCamera` | `Fenrir`, `pos1`, `pos2`, `pos3`, `15.0` |

The `CreatePosition` cases assert the three finite float payloads and the observed payload read slots. The `Goto3PointPanCamera` case asserts the static camera-plan skeleton: target label `Fenrir`, three ordered position fixture ids, duration `15.0`, target getter `+0x40`, position getter `+0x44`, duration getter `+0x34`, `CBSpline`, `CPanCamera`, and `CGame__SetCurrentCamera` context.

Excluded numeric and ABI surfaces remain deferred: `NaN`, `infinity`, `signed zero`, `subnormal`, `overflow`, exact x87/CRT rounding parity, allocator failure behavior, exact descriptor layout, exact datatype layout, exact camera layout, and exact camera ABI.

## Claim Boundary

This proves finite `CreatePosition` fixture payloads for the three public Fenrir cutscene positions, one static `Goto3PointPanCamera` camera-plan skeleton linking `Fenrir`, the three position cases, duration `15.0`, and the saved Wave580 handler/context anchors, and the fact that `Goto4PointPanCamera` and `GotoPlayerCamera` remain descriptor-context-only rows in this fixture lane.

It does not prove runtime MissionScript execution, runtime command effects, runtime camera switching, runtime cutscene playback, runtime visible camera output, runtime object identity, runtime object lookup by name, runtime `CreatePosition` behavior, runtime `CPanCamera` behavior, live loose-MSL loading, packed-resource script selection, exact descriptor layout, exact command arity, exact argument type schema, exact `CPositionDataType` layout, exact `CPanCamera` layout, exact `CBSpline` layout, `Goto4PointPanCamera` runtime handler mapping, `GotoPlayerCamera` runtime handler mapping, source-selection observation, private-frame review, visual QA, Godot parity, Ghidra mutation, executable patching, product UI behavior, rebuild implementation, rebuild parity, or no-noticeable-difference parity.
