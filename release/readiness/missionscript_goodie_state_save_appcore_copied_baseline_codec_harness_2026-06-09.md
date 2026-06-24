# MissionScript Goodie State / Save AppCore Copied-Baseline Codec Harness Readiness Note

Status: complete AppCore copied real-baseline byte-preservation proof
Date: 2026-06-09
Scope: `missionscript-goodie-state-save-appcore-copied-baseline-codec-harness`

This readiness note records the public-safe MissionScript Goodie State / Save AppCore Copied-Baseline Codec Harness Proof. The proof-only C# harness applies `OnslaughtCareerEditor.AppCore/MissionScriptGoodieStateSaveCodec.cs` to copied real baseline buffers and records byte-preservation/readback facts without exposing private source paths, hashes, artifact names, or raw save bytes.

Schema: `missionscript-goodie-state-save-appcore-copied-baseline-codec-harness.v1.json`

Previous slice: MissionScript Goodie State / Save Clean-Room Codec Interface Proof.

Selected next slice: MissionScript Goodie State / Save Runtime-Proof Readiness Gate Plan.

Readiness tokens:

- missionscript-goodie-state-save-appcore-copied-baseline-codec-harness-complete-appcore-copied-real-baseline-byte-preservation-not-runtime-proof
- toolProjectPath=tools/MissionScriptGoodieStateSaveCodecHarness/MissionScriptGoodieStateSaveCodecHarness.csproj
- appCoreCodecPath=OnslaughtCareerEditor.AppCore/MissionScriptGoodieStateSaveCodec.cs
- interfaceKind=AppCore Goodie codec applied by proof-only copied-baseline harness
- appCoreCodecUsed=true
- appCorePatcherUsed=false
- manualGoodieDwordWriteInHarness=false
- appCoreCodecFileIo=false
- harnessFileIo=true
- productUiWired=false
- sourceBaselineRead=true
- privateArtifactMaterialized=true
- copiedArtifactCount=7
- sourcePathsPublic=false
- sourceHashesPublic=false
- artifactPathsPublic=false
- artifactHashesPublic=false
- rawSaveBytesPublic=false
- copiedDefaultOptionsValidationOnly=true
- copyBeforeWrite=true
- sourceAndOutputPathsDistinct=true
- careerSourceToInputDiffCount=0
- defaultOptionsSourceToInputDiffCount=0
- careerSourceUnchanged=true
- defaultOptionsSourceUnchanged=true
- expectedSize=10004
- versionWord=0x4BD1
- trueViewGoodieBase=0x1F46
- goodieStorageEntryCount=300
- displayableGoodieCount=233
- reservedPreserveEntryCount=67
- fileSizePreserved=true
- versionWordPreserved=true
- scriptIndexing=1-based
- mappingFormula=save_goodie_index = script_index - 1
- offsetFormula=0x1F46 + (script_index - 1) * 4
- reservedWritePolicy=displayable-only-default-rejects-reserved
- scriptIndices=1,51,53,68,71,233
- saveGoodieIndices=0,50,52,67,70,232
- changedOffsets=0x1F46,0x200E,0x2016,0x2052,0x205E,0x22E6
- unexpectedDiffCount=0
- legacyTrapHitCount=0
- targetReadbackMismatchCount=0
- careerNoopDiffCount=0
- defaultOptionsNoopDiffCount=0
- patchToIdempotentDiffCount=0
- roundtripToBaselineDiffCount=0
- nonTargetGoodiesUnchanged=true
- reservedGoodiesUnchanged=true
- killCountersUnchanged=true
- techSlotsUnchanged=true
- optionsEntriesUnchanged=true
- optionsTailUnchanged=true
- reservedIndex234Rejected=true
- invalidState4Rejected=true
- emptyOverrideRejected=true
- invalidMixedBatchLeavesBufferUnchanged=true
- wrongSizeRejected=true
- wrongVersionRejected=true
- saveSynthesis=false
- defaultoptionsMutation=false
- runtimeExecution=false
- runtimeGoodieStateMutationProven=false
- runtimeSaveBehaviorProven=false
- ghidraMutation=false
- executablePatching=false
- godotWork=false
- productUiWired=false
- rebuildImplementation=false

This proves the AppCore copied-baseline Goodie codec harness boundary only. Runtime MissionScript execution, runtime command effects, runtime Goodie state mutation, runtime save/load behavior, runtime defaultoptions behavior, runtime Goodies wall behavior, runtime score behavior, product UI behavior, Ghidra mutation, executable patching, Godot parity, rebuild implementation, rebuild parity, and no-noticeable-difference parity remain separate proof.

Follow-up child lane: MissionScript Goodie State / Save Runtime-Proof Readiness Gate Plan.
