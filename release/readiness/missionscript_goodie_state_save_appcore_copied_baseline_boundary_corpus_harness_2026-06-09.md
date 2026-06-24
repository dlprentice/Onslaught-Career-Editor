# MissionScript Goodie State / Save AppCore Copied-Baseline Boundary Corpus Harness Readiness

Status: complete copied-baseline boundary corpus harness proof, not runtime proof
Date: 2026-06-09
Scope: `missionscript-goodie-state-save-appcore-copied-baseline-boundary-corpus-harness`

This readiness note records the public-safe closeout for `MissionScript Goodie State / Save AppCore Copied-Baseline Boundary Corpus Harness Proof`.

Artifacts:

- `reverse-engineering/binary-analysis/missionscript-goodie-state-save-appcore-copied-baseline-boundary-corpus-harness-proof.md`
- `reverse-engineering/binary-analysis/missionscript-goodie-state-save-appcore-copied-baseline-boundary-corpus-harness.v1.json`
- `tools/MissionScriptGoodieStateSaveBoundaryCorpusHarness/MissionScriptGoodieStateSaveBoundaryCorpusHarness.csproj`
- `tools/missionscript_goodie_state_save_appcore_copied_baseline_boundary_corpus_harness_probe.py`

Proof tokens:

- `missionscript-goodie-state-save-appcore-copied-baseline-boundary-corpus-harness-complete-copied-real-baseline-boundary-corpus-not-runtime-proof`
- `previousSlice=MissionScript Goodie State / Save AppCore Boundary-Corpus Fixture Matrix Proof`
- `selectedNextSlice=MissionScript Command-Effect Post-Goodie Selection Refresh Proof Plan`
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

What this proves:

- The proof-only C# harness applies the AppCore Goodie state/save codec to copied real baselines across the boundary/corpus matrix.
- The copied-baseline corpus covers `300` storage reads, `233` displayable roundtrips, `67` reserved mutation rejections, and `32` boundary state matrix cases.
- No-op, non-target Goodies, reserved Goodies, kill counters, tech slots, options entries, options tail, readback, and legacy trap guards satisfy the public-safe byte-preservation contract.

What remains unproven:

- Runtime MissionScript execution.
- Runtime command effects.
- Runtime Goodie state mutation.
- Runtime save/load/defaultoptions behavior.
- Runtime Goodies wall behavior.
- Runtime score behavior.
- Product UI behavior.
- Ghidra mutation.
- Executable patching.
- Godot parity.
- Rebuild implementation.
- Rebuild parity.
- No-noticeable-difference parity.
