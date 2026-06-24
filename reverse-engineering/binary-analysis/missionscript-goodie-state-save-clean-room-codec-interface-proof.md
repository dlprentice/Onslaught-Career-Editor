# MissionScript Goodie State / Save Clean-Room Codec Interface Proof

Status: complete pure AppCore buffer codec proof, not runtime proof
Date: 2026-06-09
Scope: `missionscript-goodie-state-save-clean-room-codec-interface-proof`

This slice converts the completed MissionScript Goodie State / Save copied-baseline byte-diff evidence into a clean-room-facing AppCore buffer codec. It adds `OnslaughtCareerEditor.AppCore/MissionScriptGoodieStateSaveCodec.cs` and `OnslaughtCareerEditor.AppCore.Tests/MissionScriptGoodieStateSaveCodecTests.cs`.

Result token: missionScriptGoodieStateSaveCleanRoomCodecInterfaceProofStatus=missionscript-goodie-state-save-clean-room-codec-interface-proof-complete-pure-appcore-buffer-codec-not-runtime-proof.

Schema: `missionscript-goodie-state-save-clean-room-codec-interface-proof.v1.json`

Previous slice: MissionScript Goodie State / Save Copied-Baseline Byte-Diff Fixture Proof.

Interface facts:

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

Representative vectors:

| Script index | Save Goodie index | True-view dword | Role |
| ---: | ---: | --- | --- |
| `1` | `0` | `0x1F46` | First displayable Goodie. |
| `51` | `50` | `0x200E` | Known Goodie-state script call. |
| `53` | `52` | `0x2016` | Known Goodie-state script call. |
| `68` | `67` | `0x2052` | Known race Goodie-state script call. |
| `71` | `70` | `0x205E` | Known race Goodie-state script call. |
| `233` | `232` | `0x22E6` | Last displayable Goodie. |
| `234` | `233` | `0x22EA` | First reserved/preserve Goodie; rejected for mutation by default. |
| `300` | `299` | `0x23F2` | Last reserved/preserve Goodie; rejected for mutation by default. |

Validation:

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
- publicLeakCheck=PASS

Guardrails:

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

What this proves:

- A public-safe AppCore codec can validate the BEA career-save container size/version and map one-based MissionScript Goodie script indices to zero-based save Goodie indices.
- The codec computes true-view Goodie offsets with `0x1F46 + (script_index - 1) * 4`.
- The codec reads and writes state values `0..3` for displayable Goodies, rejects reserved Goodies for mutation by default, and rejects invalid containers/states.
- The batch writer validates the whole batch before mutation so an invalid mixed batch leaves the buffer unchanged.

What remains unproven:

- Runtime MissionScript execution.
- Runtime command effects.
- Runtime Goodie state mutation.
- Runtime save/load behavior.
- Runtime defaultoptions behavior.
- Runtime Goodies wall behavior.
- Runtime score behavior.
- Product UI behavior.
- Ghidra mutation.
- Executable patching behavior.
- Godot parity.
- Rebuild implementation.
- Rebuild parity.
- No-noticeable-difference parity.

Follow-up child lane: MissionScript Goodie State / Save AppCore Copied-Baseline Codec Harness Proof Plan.
