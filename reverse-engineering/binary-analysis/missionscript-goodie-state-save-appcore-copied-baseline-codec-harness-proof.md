# MissionScript Goodie State / Save AppCore Copied-Baseline Codec Harness Proof

Status: complete AppCore copied real-baseline byte-preservation proof, not runtime proof
Date: 2026-06-09
Scope: `missionscript-goodie-state-save-appcore-copied-baseline-codec-harness`

This slice applies the clean-room-facing `MissionScriptGoodieStateSaveCodec` to copied real career/defaultoptions baselines through a proof-only C# harness. It proves the AppCore codec can drive the selected Goodie-state byte changes and readbacks on copied baseline buffers while preserving non-target bytes and rejection boundaries.

Result token: missionscript-goodie-state-save-appcore-copied-baseline-codec-harness-complete-appcore-copied-real-baseline-byte-preservation-not-runtime-proof.

Previous slice: MissionScript Goodie State / Save Clean-Room Codec Interface Proof.

Selected next slice: MissionScript Goodie State / Save Runtime-Proof Readiness Gate Plan.

Schema: `missionscript-goodie-state-save-appcore-copied-baseline-codec-harness.v1.json`

Implementation facts:

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

Provenance facts:

- copyBeforeWrite=true
- sourceAndOutputPathsDistinct=true
- careerSourceToInputDiffCount=0
- defaultOptionsSourceToInputDiffCount=0
- careerSourceUnchanged=true
- defaultOptionsSourceUnchanged=true

Container facts:

- expectedSize=10004
- versionWord=0x4BD1
- trueViewGoodieBase=0x1F46
- goodieStorageEntryCount=300
- displayableGoodieCount=233
- reservedPreserveEntryCount=67
- fileSizePreserved=true
- versionWordPreserved=true

Operation facts:

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

Preservation and rejection facts:

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

Guardrails:

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

What this proves:

- The proof-only harness uses the AppCore `MissionScriptGoodieStateSaveCodec` directly, not `BesFilePatcher.PatchGoodieStates`.
- One-based MissionScript Goodie script indices map to zero-based save Goodie indices through the AppCore codec.
- Six selected displayable Goodie dwords change only at the expected true-view offsets.
- AppCore codec readback confirms all selected target states after mutation.
- Copied source preservation, no-op, idempotent, roundtrip, reserved Goodie, kill counter, tech slot, options entry, options tail, and rejection guards satisfy the byte-preservation contract.

What remains unproven:

- Runtime MissionScript execution.
- Runtime command effects.
- Runtime Goodie state mutation.
- Runtime save/load behavior.
- Runtime defaultoptions behavior.
- Runtime Goodies wall behavior.
- Runtime score behavior.
- Installed game mutation.
- Product UI behavior.
- Ghidra mutation.
- Executable patching.
- Godot parity.
- Rebuild implementation.
- Rebuild parity.
- No-noticeable-difference parity.

Follow-up child lane: MissionScript Goodie State / Save Runtime-Proof Readiness Gate Plan.
