# MissionScript Goodie State / Save AppCore Boundary-Corpus Fixture Matrix Proof

Status: complete AppCore boundary/corpus fixture matrix, not runtime proof
Last updated: 2026-06-09
Scope: `missionscript-goodie-state-save-appcore-boundary-corpus-fixture-matrix`

This proof extends the clean-room AppCore MissionScript Goodie state/save codec from the runtime-readiness gate into an in-memory boundary and corpus fixture matrix. It runs no BEA process, reads no private save evidence, writes no copied files, mutates no Ghidra project, patches no executable, starts no Godot work, and wires no product UI.

Machine-checkable artifact:

- [missionscript-goodie-state-save-appcore-boundary-corpus-fixture-matrix.v1.json](missionscript-goodie-state-save-appcore-boundary-corpus-fixture-matrix.v1.json)

Decision tokens:

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
- `previousCleanRoomXunitCaseCount=249`
- `storageVectorCaseCount=300`
- `displayableRoundTripCaseCount=233`
- `reservedMutationRejectionCaseCount=67`
- `displayableBoundaryStateMatrixCaseCount=32`
- `invalidRawStateCaseCount=3`
- `goodieStorageEntryCount=300`
- `displayableGoodieCount=233`
- `reservedPreserveEntryCount=67`
- `goodieStorageBytes=1200`
- `goodieStorageEndExclusive=0x23F6`
- `scriptIndexRange=1..300`
- `displayableScriptIndexRange=1..233`
- `reservedScriptIndexRange=234..300`
- `saveGoodieIndexRange=0..299`
- `stateValueRange=0..3`
- `boundaryScriptIndices=1,2,51,53,68,71,232,233`
- `boundaryStateValues=0,1,2,3`
- `boundaryOffsets=0x1F46,0x1F4A,0x200E,0x2016,0x2052,0x205E,0x22E2,0x22E6`
- `knownCopiedBaselineScriptIndices=1,51,53,68,71,233`
- `knownCopiedBaselineChangedOffsets=0x1F46,0x200E,0x2016,0x2052,0x205E,0x22E6`
- `allStorageScriptIndicesVectorized=true`
- `allDisplayableScriptIndicesRoundTrip=true`
- `allReservedScriptIndicesRejected=true`
- `allReservedRejectionsLeaveBufferUnchanged=true`
- `allBoundaryStatesRoundTrip=true`
- `allBoundaryStatesRestoreToUnknownBaseline=true`
- `invalidRawStateRejected=true`
- `invalidMixedBatchLeavesBufferUnchanged=true`
- `wrongSizeRejected=true`
- `wrongVersionRejected=true`
- `fileIoPerformed=false`
- `copiedFileMutationPerformed=false`
- `sourceBaselineRead=false`
- `privateArtifactMaterialized=false`
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

## Corpus

| Corpus row | Count | Evidence |
| --- | ---: | --- |
| Prior clean-room codec cases | `249` | Existing in-memory AppCore coverage: selected static seed vectors, state labels, selected six-index mutation/readback, idempotent/unknown roundtrip, invalid input rejection, invalid mixed batch preservation, and all `1..233` displayable script-index roundtrips. |
| Storage vector matrix | `300` | Every MissionScript Goodie script index `1..300` maps to save index `script_index - 1`, true-view offset `0x1F46 + (script_index - 1) * 4`, and correct displayable/reserved classification. |
| Reserved mutation rejection matrix | `67` | Every reserved script index `234..300` rejects displayable mutation and leaves the in-memory buffer unchanged. |
| Displayable boundary state matrix | `32` | Boundary/corpus script indices `1`, `2`, `51`, `53`, `68`, `71`, `232`, and `233` roundtrip state values `0`, `1`, `2`, and `3`, then restore to the unknown baseline. |
| Invalid raw state matrix | `3` | Script indices `1`, `234`, and `300` reject raw state `4` during readback. |

The test matrix keeps the established one-based MissionScript index mapping, true-view offset base `0x1F46`, `300` stored Goodie entries, `233` displayable entries, and `67` reserved entries. The selected copied-baseline corpus from the prior harness remains explicit: script indices `1`, `51`, `53`, `68`, `71`, and `233`; changed offsets `0x1F46`, `0x200E`, `0x2016`, `0x2052`, `0x205E`, and `0x22E6`; `unexpectedDiffCount=0`; `legacyTrapHitCount=0`.

## Validation

Command:

```powershell
dotnet test OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo --filter MissionScriptGoodieStateSaveCodecTests
```

Result:

- `Passed: 651`
- `Failed: 0`
- `Skipped: 0`
- Preview SDK informational message: `NETSDK1057`

## Claim Boundary

This proves the clean-room AppCore in-memory codec maps all Goodie storage indices, rejects reserved mutation across the full reserved range, roundtrips displayable boundary states, rejects invalid raw states, and preserves the current static/copy-before-write claim boundary for the Goodie state/save path.

It does not prove runtime MissionScript execution, runtime command effects, runtime Goodie mutation, runtime save/load/defaultoptions behavior, runtime Goodies wall behavior, runtime score behavior, live loose-MSL loading, packed-resource script selection, source selection, private-frame review, screenshot/frame interpretation, native input, debugger behavior, installed game mutation, original executable mutation, copied-file boundary corpus behavior, product UI behavior, Ghidra mutation, executable patching, Godot parity, rebuild implementation, rebuild parity, or no-noticeable-difference parity.
