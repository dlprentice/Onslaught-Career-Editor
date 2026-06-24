# MissionScript Goodie State / Save AppCore Copied-Baseline Boundary Corpus Harness Proof

Status: complete copied-baseline boundary corpus harness proof, not runtime proof
Last updated: 2026-06-09
Scope: `missionscript-goodie-state-save-appcore-copied-baseline-boundary-corpus-harness`

This proof applies the AppCore MissionScript Goodie state/save boundary corpus to copied real career/defaultoptions baselines through a proof-only C# harness. It extends the prior in-memory boundary corpus into copied-baseline byte-preservation evidence without exposing private source paths, artifact paths, hashes, raw save bytes, or private artifact contents.

Machine-checkable artifact:

- [missionscript-goodie-state-save-appcore-copied-baseline-boundary-corpus-harness.v1.json](missionscript-goodie-state-save-appcore-copied-baseline-boundary-corpus-harness.v1.json)

Proof tokens:

- `MissionScript Goodie State / Save AppCore Copied-Baseline Boundary Corpus Harness Proof`
- `missionscript-goodie-state-save-appcore-copied-baseline-boundary-corpus-harness-complete-copied-real-baseline-boundary-corpus-not-runtime-proof`
- `previousSlice=MissionScript Goodie State / Save AppCore Boundary-Corpus Fixture Matrix Proof`
- `selectedNextSlice=MissionScript Command-Effect Post-Goodie Selection Refresh Proof Plan`
- `selectedFixtureFamily=goodie-state-save`
- `selectedFixturePath=goodie-state-save-index-state-byte-preservation`
- `toolProjectPath=tools/MissionScriptGoodieStateSaveBoundaryCorpusHarness/MissionScriptGoodieStateSaveBoundaryCorpusHarness.csproj`
- `appCoreCodecPath=OnslaughtCareerEditor.AppCore/MissionScriptGoodieStateSaveCodec.cs`
- `interfaceKind=AppCore Goodie codec boundary corpus applied by proof-only copied-baseline harness`
- `appCoreCodecUsed=true`
- `appCorePatcherUsed=false`
- `manualGoodieDwordWriteInHarness=false`
- `appCoreCodecFileIo=false`
- `harnessFileIo=true`
- `productUiWired=false`
- `sourceBaselineRead=true`
- `privateArtifactMaterialized=true`
- `copiedArtifactCount=12`
- `sampleBoundaryArtifactCount=8`
- `sourcePathsPublic=false`
- `sourceHashesPublic=false`
- `artifactPathsPublic=false`
- `artifactHashesPublic=false`
- `rawSaveBytesPublic=false`
- `copiedDefaultOptionsValidationOnly=true`
- `copyBeforeWrite=true`
- `sourceAndOutputPathsDistinct=true`
- `careerSourceToInputDiffCount=0`
- `defaultOptionsSourceToInputDiffCount=0`
- `careerSourceUnchanged=true`
- `defaultOptionsSourceUnchanged=true`
- `expectedSize=10004`
- `versionWord=0x4BD1`
- `trueViewGoodieBase=0x1F46`
- `goodieStorageEntryCount=300`
- `displayableGoodieCount=233`
- `reservedPreserveEntryCount=67`
- `goodieStorageEndExclusive=0x23F6`
- `storageVectorCopiedBaselineReadCaseCount=300`
- `displayableCopiedBaselineRoundTripCaseCount=233`
- `reservedCopiedBaselineRejectionCaseCount=67`
- `boundaryStateCopiedBaselineMatrixCaseCount=32`
- `copiedBaselineBoundaryCorpusCaseCount=632`
- `boundaryScriptIndices=1,2,51,53,68,71,232,233`
- `boundaryOffsets=0x1F46,0x1F4A,0x200E,0x2016,0x2052,0x205E,0x22E2,0x22E6`
- `allStorageScriptIndicesReadFromCopiedBaseline=true`
- `allDisplayableCopiedBaselineRoundTrip=true`
- `toggleTouchesOnlyExpectedByteForAllDisplayable=true`
- `allReservedCopiedBaselineRejectionsLeaveBufferUnchanged=true`
- `allBoundaryStatesRoundTripOnCopiedBaseline=true`
- `targetReadbackMismatchCount=0`
- `unexpectedDiffCount=0`
- `legacyTrapHitCount=0`
- `careerNoopDiffCount=0`
- `defaultOptionsNoopDiffCount=0`
- `nonTargetGoodiesUnchangedForAllDisplayableRoundTrips=true`
- `reservedGoodiesUnchangedForAllDisplayableRoundTrips=true`
- `killCountersUnchangedForAllDisplayableRoundTrips=true`
- `techSlotsUnchangedForAllDisplayableRoundTrips=true`
- `optionsEntriesUnchangedForAllDisplayableRoundTrips=true`
- `optionsTailUnchangedForAllDisplayableRoundTrips=true`
- `invalidScriptIndex0Rejected=true`
- `invalidScriptIndex301Rejected=true`
- `reservedScriptIndex234Rejected=true`
- `invalidState4Rejected=true`
- `invalidStateUintMaxRejected=true`
- `emptyOverrideRejected=true`
- `invalidMixedBatchLeavesBufferUnchanged=true`
- `wrongSizeRejected=true`
- `wrongVersionRejected=true`
- `saveSynthesis=false`
- `defaultoptionsMutation=false`
- `runtimeExecution=false`
- `beLaunch=false`
- `ghidraMutation=false`
- `executablePatching=false`
- `godotWork=false`
- `productUiWired=false`
- `rebuildImplementation=false`
- `runtimeObservationRows=0`
- `missionScriptRuntimeEvidenceRows=0`
- `runtimeCommandEffectRows=0`
- `runtimeGoodieStateRows=0`
- `runtimeSaveRows=0`
- `runtimeDefaultOptionsRows=0`
- `publicLeakCheck=PASS`

## Copied-Baseline Corpus

| Check | Result |
| --- | --- |
| Harness surface | `toolProjectPath=tools/MissionScriptGoodieStateSaveBoundaryCorpusHarness/MissionScriptGoodieStateSaveBoundaryCorpusHarness.csproj`; `appCoreCodecPath=OnslaughtCareerEditor.AppCore/MissionScriptGoodieStateSaveCodec.cs`. |
| AppCore use | `appCoreCodecUsed=true`; `appCorePatcherUsed=false`; `manualGoodieDwordWriteInHarness=false`; `appCoreCodecFileIo=false`. |
| Private evidence boundary | `sourceBaselineRead=true`; `privateArtifactMaterialized=true`; public schema keeps `sourcePathsPublic=false`, `sourceHashesPublic=false`, `artifactPathsPublic=false`, `artifactHashesPublic=false`, and `rawSaveBytesPublic=false`. |
| Copied artifacts | `copiedArtifactCount=12`: copied career/defaultoptions baselines, no-op copies, and eight boundary-index sample artifacts. Only counts and sanitized contract facts are public. |
| Container shape | Copied career/defaultoptions containers remain `expectedSize=10004`, `versionWord=0x4BD1`, `trueViewGoodieBase=0x1F46`, and `goodieStorageEndExclusive=0x23F6`. |
| Storage read corpus | `storageVectorCopiedBaselineReadCaseCount=300`; `allStorageScriptIndicesReadFromCopiedBaseline=true`; `allStorageStateValuesWithinKnownRange=true`. |
| Displayable roundtrip corpus | `displayableCopiedBaselineRoundTripCaseCount=233`; `allDisplayableCopiedBaselineRoundTrip=true`; `toggleTouchesOnlyExpectedByteForAllDisplayable=true`; `toggleIdempotentForAllDisplayable=true`; `restoreToBaselineForAllDisplayable=true`. |
| Reserved rejection corpus | `reservedCopiedBaselineRejectionCaseCount=67`; `allReservedCopiedBaselineRejectionsLeaveBufferUnchanged=true`. |
| Boundary state matrix | `boundaryStateCopiedBaselineMatrixCaseCount=32`; `boundaryScriptIndices=1,2,51,53,68,71,232,233`; `boundaryOffsets=0x1F46,0x1F4A,0x200E,0x2016,0x2052,0x205E,0x22E2,0x22E6`; `allBoundaryStatesRoundTripOnCopiedBaseline=true`; `allBoundaryStatesRestoreToBaseline=true`. |
| Preservation | `careerNoopDiffCount=0`; `defaultOptionsNoopDiffCount=0`; `nonTargetGoodiesUnchangedForAllDisplayableRoundTrips=true`; `reservedGoodiesUnchangedForAllDisplayableRoundTrips=true`; `killCountersUnchangedForAllDisplayableRoundTrips=true`; `techSlotsUnchangedForAllDisplayableRoundTrips=true`; `optionsEntriesUnchangedForAllDisplayableRoundTrips=true`; `optionsTailUnchangedForAllDisplayableRoundTrips=true`; `unexpectedDiffCount=0`; `legacyTrapHitCount=0`. |

The copied-baseline corpus deliberately does not publish private paths, artifact hashes, raw dwords, raw save bytes, or private artifact contents. The public claim is the AppCore/harness contract: the measured private run matched expected container, provenance, corpus, byte-touch, no-op, restoration, rejection, and preservation guards.

## Claim Boundary

This proves the proof-only C# harness can apply the AppCore MissionScript Goodie state/save boundary corpus to copied real baselines, read all stored Goodie states, roundtrip every displayable Goodie index, reject every reserved Goodie mutation, roundtrip selected boundary states, preserve checked non-target ranges, and keep source baselines unchanged.

It does not prove runtime MissionScript execution, runtime command effects, runtime Goodie state mutation, runtime save/load behavior, runtime defaultoptions behavior, runtime Goodies wall behavior, runtime score behavior, source selection, private-frame review, screenshot or frame interpretation, native input, debugger behavior, installed game mutation, product UI behavior, Ghidra mutation, executable patching, Godot parity, rebuild implementation, rebuild parity, or no-noticeable-difference parity.
