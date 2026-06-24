# MissionScript Goodie State / Save Clean-Room Codec Interface Readiness Note

Status: complete pure AppCore buffer codec proof
Date: 2026-06-09
Scope: `missionscript-goodie-state-save-clean-room-codec-interface-proof`

This readiness note records the public-safe MissionScript Goodie State / Save Clean-Room Codec Interface Proof for MissionScript Goodie state/save mapping. It adds `OnslaughtCareerEditor.AppCore/MissionScriptGoodieStateSaveCodec.cs` and focused xUnit coverage in `OnslaughtCareerEditor.AppCore.Tests/MissionScriptGoodieStateSaveCodecTests.cs`.

Schema: `missionscript-goodie-state-save-clean-room-codec-interface-proof.v1.json`

Previous slice: MissionScript Goodie State / Save Copied-Baseline Byte-Diff Fixture Proof.

Readiness tokens:

- missionScriptGoodieStateSaveCleanRoomCodecInterfaceProofStatus=missionscript-goodie-state-save-clean-room-codec-interface-proof-complete-pure-appcore-buffer-codec-not-runtime-proof
- interfaceKind=pure AppCore in-memory buffer codec
- appCoreCodecPath=OnslaughtCareerEditor.AppCore/MissionScriptGoodieStateSaveCodec.cs
- appCoreTestPath=OnslaughtCareerEditor.AppCore.Tests/MissionScriptGoodieStateSaveCodecTests.cs
- appCoreCodecUsed=true
- appCorePatcherUsed=false
- publicMethodCount=10
- expectedFileSize=10004
- versionWord=0x4BD1
- trueViewGoodieBase=0x1F46
- goodieStorageEntryCount=300
- displayableGoodieCount=233
- reservedPreserveEntryCount=67
- goodieStorageBytes=1200
- goodieStorageEndExclusive=0x23F6
- scriptIndexing=1-based
- mappingFormula=save_goodie_index = script_index - 1
- offsetFormula=0x1F46 + (script_index - 1) * 4
- scriptIndexRange=1..300
- displayableScriptIndexRange=1..233
- saveGoodieIndexRange=0..299
- displayableSaveGoodieIndexRange=0..232
- reservedScriptIndexRange=234..300
- reservedWritePolicy=displayable-only-default-rejects-reserved
- stateValueRange=0..3
- dotnetFilter=MissionScriptGoodieStateSaveCodecTests
- xunitTestCaseCount=249
- testMethodCount=7
- allDisplayableScriptIndexCaseCount=233
- changedOffsets=0x1F46,0x200E,0x2016,0x2052,0x205E,0x22E6
- invalidMixedBatchLeavesBufferUnchanged=true
- allDisplayableScriptIndicesRoundTrip=true
- allDisplayableScriptIndicesTouchOnlyExpectedDwordStart=true
- reservedIndexRejection=true
- invalidStateRejection=true
- wrongSizeRejected=true
- wrongVersionRejected=true
- emptyBatchRejected=true
- fileIoPerformed=false
- harnessFileIo=false
- copiedFileMutationPerformed=false
- sourceBaselineRead=false
- privateArtifactMaterialized=false
- syntheticBesFileWritten=false
- defaultoptionsGoodieMutation=false
- runtimeExecution=false
- beLaunch=false
- ghidraMutation=false
- executablePatching=false
- godotWork=false
- productUiWired=false
- rebuildImplementation=false
- publicLeakCheck=PASS

This proves the pure AppCore in-memory Goodie codec interface only. Runtime MissionScript execution, runtime command effects, runtime Goodie state mutation, runtime save/load behavior, runtime defaultoptions behavior, runtime Goodies wall behavior, runtime score behavior, product UI behavior, executable patching, Godot parity, rebuild implementation, rebuild parity, and no-noticeable-difference parity remain separate proof.

Follow-up child lane: MissionScript Goodie State / Save AppCore Copied-Baseline Codec Harness Proof Plan.
