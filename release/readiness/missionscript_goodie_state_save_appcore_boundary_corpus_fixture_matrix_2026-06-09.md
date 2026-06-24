# MissionScript Goodie State / Save AppCore Boundary-Corpus Fixture Matrix Proof

Status: complete AppCore boundary/corpus fixture matrix, not runtime proof
Date: 2026-06-09
Scope: `missionscript-goodie-state-save-appcore-boundary-corpus-fixture-matrix`

This readiness note records the non-runtime AppCore fixture-matrix proof after the MissionScript Goodie State / Save Runtime-Proof Readiness Gate. It does not run BEA, launch a copied profile, read private save evidence, write copied files, patch an executable, mutate Ghidra, wire product UI, start Godot work, or implement a rebuild.

Machine-checkable artifact: `missionscript-goodie-state-save-appcore-boundary-corpus-fixture-matrix.v1.json`.

Required decision tokens:

- `missionScriptGoodieStateSaveAppCoreBoundaryCorpusFixtureMatrixStatus=missionscript-goodie-state-save-appcore-boundary-corpus-fixture-matrix-complete-651-appcore-cases-not-runtime-proof`
- `proofName=missionscript-goodie-state-save-appcore-boundary-corpus-fixture-matrix-proof.md`
- `previousSlice=MissionScript Goodie State / Save Runtime-Proof Readiness Gate`
- `selectedNextSlice=MissionScript Goodie State / Save AppCore Copied-Baseline Boundary Corpus Harness Proof Plan`
- `selectedFixtureFamily=goodie-state-save`
- `selectedFixturePath=goodie-state-save-index-state-byte-preservation`
- `appCoreCodecPath=OnslaughtCareerEditor.AppCore/MissionScriptGoodieStateSaveCodec.cs`
- `appCoreTestPath=OnslaughtCareerEditor.AppCore.Tests/MissionScriptGoodieStateSaveCodecTests.cs`
- `interfaceKind=pure AppCore in-memory buffer codec`
- `dotnetFilter=MissionScriptGoodieStateSaveCodecTests`
- `xunitTestCaseCount=651`
- `passed=true`
- `storageVectorCaseCount=300`
- `displayableRoundTripCaseCount=233`
- `reservedMutationRejectionCaseCount=67`
- `displayableBoundaryStateMatrixCaseCount=32`
- `invalidRawStateCaseCount=3`
- `scriptIndexRange=1..300`
- `displayableScriptIndexRange=1..233`
- `reservedScriptIndexRange=234..300`
- `boundaryScriptIndices=1,2,51,53,68,71,232,233`
- `boundaryOffsets=0x1F46,0x1F4A,0x200E,0x2016,0x2052,0x205E,0x22E2,0x22E6`
- `allStorageScriptIndicesVectorized=true`
- `allDisplayableScriptIndicesRoundTrip=true`
- `allReservedScriptIndicesRejected=true`
- `allReservedRejectionsLeaveBufferUnchanged=true`
- `allBoundaryStatesRoundTrip=true`
- `allBoundaryStatesRestoreToUnknownBaseline=true`
- `invalidRawStateRejected=true`
- `runtimeExecution=false`
- `beLaunch=false`
- `ghidraMutation=false`
- `executablePatching=false`
- `godotWork=false`
- `rebuildImplementation=false`
- `runtimeObservationRows=0`
- `missionScriptRuntimeEvidenceRows=0`
- `runtimeCommandEffectRows=0`
- `runtimeGoodieStateRows=0`
- `runtimeSaveRows=0`
- `runtimeDefaultOptionsRows=0`
- `publicLeakCheck=PASS`

Validation:

- `dotnet test OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo --filter MissionScriptGoodieStateSaveCodecTests`
- `Passed: 651`
- `Failed: 0`
- `Skipped: 0`

The selected follow-up is `MissionScript Goodie State / Save AppCore Copied-Baseline Boundary Corpus Harness Proof Plan`, a copied-real-baseline child lane. Runtime proof remains deferred and requires a separate explicit arm.

Claim boundary: this proves only the pure in-memory AppCore boundary/corpus fixture matrix for Goodie state/save indexing and state values. Runtime MissionScript execution, runtime command effects, runtime Goodie mutation, runtime save/load/defaultoptions behavior, runtime Goodies wall behavior, runtime score behavior, source selection, private-frame review, copied-file boundary corpus behavior, product UI behavior, Ghidra mutation, executable patching, Godot parity, rebuild implementation, rebuild parity, and no-noticeable-difference parity remain separate proof.
