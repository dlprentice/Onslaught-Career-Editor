# Save / Options Byte-Preservation AppCore Implementation Contract Readiness Note

Status: complete AppCore implementation-contract proof, not runtime proof
Date: 2026-06-09

This readiness note records the public-safe closeout for the Save / Options Byte-Preservation AppCore Implementation Contract Proof.

Artifacts:

- Proof: `reverse-engineering/binary-analysis/save-options-byte-preservation-appcore-implementation-contract-proof.md`
- Schema: `reverse-engineering/binary-analysis/save-options-byte-preservation-appcore-implementation-contract.v1.json`
- Harness: `tools/SaveOptionsAppCoreContractHarness/SaveOptionsAppCoreContractHarness.csproj`
- Probe: `tools/save_options_byte_preservation_appcore_implementation_contract_probe.py`

Closeout tokens:

- saveOptionsBytePreservationAppCoreImplementationContractStatus=save-options-byte-preservation-appcore-implementation-contract-complete-copied-real-baseline-services-not-runtime-proof
- previousSlice=MissionScript Slot Bitset/Save AppCore Copied-Baseline Boundary Corpus Harness Proof
- selectedNextSlice=Save / Options Byte-Preservation Runtime-Proof Readiness Gate Plan
- toolProjectPath=tools/SaveOptionsAppCoreContractHarness/SaveOptionsAppCoreContractHarness.csproj
- appCoreSavePatchPath=OnslaughtCareerEditor.AppCore/BesFilePatcher.cs
- saveEditorServicePath=OnslaughtCareerEditor.AppCore/SaveEditorService.cs
- configurationEditorServicePath=OnslaughtCareerEditor.AppCore/ConfigurationEditorService.cs
- slotCodecPath=OnslaughtCareerEditor.AppCore/MissionScriptSlotBitsetSaveCodec.cs
- appCoreServicesUsed=true
- productUiWired=false
- harnessFileIo=true
- privateArtifactMaterialized=true
- copiedArtifactCount=10
- sourcePathsPublic=false
- sourceHashesPublic=false
- artifactPathsPublic=false
- artifactHashesPublic=false
- rawBytesPublic=false
- copyBeforeWrite=true
- sourceAndOutputPathsDistinct=true
- careerSourceUnchanged=true
- defaultOptionsSourceUnchanged=true
- careerSourceToInputDiffCount=0
- defaultOptionsSourceToInputDiffCount=0
- expectedSize=10004
- versionWord=0x4BD1
- slotCodecExpectedSize=10004
- slotCodecVersionWord=0x4BD1
- trueViewRule=file_offset = 0x0002 + career_offset
- careerSlotsBase=0x240A
- careerSlotsEndExclusive=0x248A
- appCoreServiceProofCaseCount=8
- SaveEditorService.PatchSave
- ConfigurationEditorService.PatchConfiguration
- BesFilePatcher.AnalyzeSave
- MissionScriptSlotBitsetSaveCodec
- optionsLikeInputRejected=true
- inPlaceRejected=true
- changedOffsets=0x23F6
- allowedOffsets=0x23F6,0x23F7,0x23F8
- metadataBytePreserved=true
- lower24Changed=true
- legacyTrapHitCount=0
- techSlotsRangeUnchanged=true
- optionsEntriesUnchanged=true
- optionsTailUnchanged=true
- soundVolumeChangedOffsets=0x248E,0x248F,0x2490,0x2491
- optionsEntriesCopyChangedOffsets=0x24BE
- optionsTailCopyChangedOffsets=0x26BE
- copiedInPlacePatchAllowedOnlyInProofRoot=true
- copiedInPlaceBackupCreated=true
- copiedInPlaceBackupMatchesPrePatch=true
- copiedInPlaceChangedOffsets=0x2492,0x2493,0x2494,0x2495
- slot61ChangedOffsets=0x2411
- slotCodecFileIo=false
- saveSynthesis=false
- installedGameMutation=false
- originalExecutableMutation=false
- runtimeExecution=false
- beLaunch=false
- ghidraMutation=false
- executablePatching=false
- godotWork=false
- rebuildImplementation=false
- runtimeSaveLoadProof=false
- runtimeDefaultOptionsProof=false
- publicLeakCheck=PASS

This proves only copied-baseline AppCore implementation-contract behavior. Runtime save/load behavior, runtime defaultoptions boot behavior, runtime menu/controller behavior, runtime Goodies wall behavior, runtime MissionScript execution, installed-game mutation, executable mutation, product UI behavior, Godot parity, rebuild implementation, rebuild parity, and no-noticeable-difference parity remain separate proof.
