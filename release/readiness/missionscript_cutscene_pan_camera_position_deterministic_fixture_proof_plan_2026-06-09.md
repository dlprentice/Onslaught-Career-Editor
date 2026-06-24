# MissionScript Cutscene Pan-Camera / Position Command-Effect Deterministic Fixture Proof Plan Readiness

Status: complete static finite camera-plan fixture proof, not runtime proof
Date: 2026-06-09
Scope: `missionscript-cutscene-pan-camera-position-deterministic-fixture`

Artifacts:

- `reverse-engineering/binary-analysis/missionscript-cutscene-pan-camera-position-deterministic-fixture-proof-plan.md`
- `reverse-engineering/binary-analysis/missionscript-cutscene-pan-camera-position-deterministic-fixture-proof-plan.v1.json`
- `tools/missionscript_cutscene_pan_camera_position_deterministic_fixture_proof_plan_probe.py`

Key tokens:

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

Static anchors:

| Surface | Evidence |
| --- | --- |
| Descriptors | `CreatePosition` / `0x0064de90`, `Goto3PointPanCamera` / `0x0064ea90`, `Goto4PointPanCamera` / `0x0064ead0`, and `GotoPlayerCamera` / `0x0064eb10`. |
| Position datatype | `CPositionDataType`, type id `6`, vtable `0x005e4da4`, size `20`, payload reads `+0x04/+0x08/+0x0c`, and value getter `+0x44`. |
| Handler/context | `0x00533b70 IScript__Create3PointPanCamera`, `0x00533eb0 IScript__Create4PointPanCamera`, `0x00416d10 CBSpline__ctor`, `0x004198d0 CPanCamera__ctor`, and `0x004705e0 CGame__SetCurrentCamera`. |
| Corpus | `GetThingRef context only`, `Fenrir`, three `CreatePosition` payloads, and `durationSeconds=15.0`. |

Fixture matrix:

- Three finite `CreatePosition` fixture rows.
- One finite static `Goto3PointPanCamera` camera-plan skeleton.
- Two context-only descriptor rows: `Goto4PointPanCamera` and `GotoPlayerCamera`.

What this proves:

- Finite `CreatePosition` payload preservation for three public Fenrir cutscene positions.
- A static camera-plan skeleton for `Goto3PointPanCamera(Fenrir, pos1, pos2, pos3, 15.0)`.
- Bounded source/static anchors for `CBSpline`, `CPanCamera`, and `CGame__SetCurrentCamera` without runtime or visual claims.

What remains unproven:

- Runtime MissionScript execution.
- Runtime command effects.
- Runtime camera switching, cutscene playback, or visible camera output.
- Runtime object identity or object lookup.
- Live loose-MSL loading or packed-resource script selection.
- Exact descriptor/datatype/camera/spline layout, `Goto4PointPanCamera` or `GotoPlayerCamera` runtime mapping, rebuild parity, or no-noticeable-difference parity.
