# Save / Options Byte-Preservation AppCore Implementation Contract Proof

Status: complete copied-real-baseline AppCore service proof, not runtime proof
Date: 2026-06-09

This slice proves the AppCore save/options implementation contract against copied real baselines from prior private evidence. It is a non-runtime, public-safe bridge from static save/options contracts and copied-file byte proofs into rebuild-facing AppCore service behavior.

Evidence schema: [save-options-byte-preservation-appcore-implementation-contract.v1.json](save-options-byte-preservation-appcore-implementation-contract.v1.json)

Core result tokens:

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

Container and true-view anchors:

- expectedSize=10004
- versionWord=0x4BD1
- slotCodecExpectedSize=10004
- slotCodecVersionWord=0x4BD1
- trueViewRule=file_offset = 0x0002 + career_offset
- careerSlotsBase=0x240A
- careerSlotsEndExclusive=0x248A

AppCore service proof:

- appCoreServiceProofCaseCount=8
- SaveEditorService.PatchSave
- ConfigurationEditorService.PatchConfiguration
- BesFilePatcher.AnalyzeSave
- MissionScriptSlotBitsetSaveCodec

Career service results:

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

Configuration service results:

- soundVolumeChangedOffsets=0x248E,0x248F,0x2490,0x2491
- optionsEntriesCopyChangedOffsets=0x24BE
- optionsTailCopyChangedOffsets=0x26BE
- copiedInPlacePatchAllowedOnlyInProofRoot=true
- copiedInPlaceBackupCreated=true
- copiedInPlaceBackupMatchesPrePatch=true
- copiedInPlaceChangedOffsets=0x2492,0x2493,0x2494,0x2495

Slot codec alignment:

- slot61ChangedOffsets=0x2411
- slotCodecFileIo=false

Negative guards:

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

What this proves:

- AppCore career-save patching can perform a copied-baseline lower-24 Aircraft kill edit while preserving the metadata byte and non-target ranges.
- AppCore common save patching rejects options-like inputs and in-place career output.
- AppCore configuration patching can perform copied-baseline sound-volume, options-entry, options-tail, and copied in-place backup flows with bounded byte ranges.
- MissionScript slot-bitset codec container constants remain aligned with the broader AppCore save patcher.

What remains separate:

- Runtime save/load behavior.
- Runtime defaultoptions boot behavior.
- Runtime menu behavior.
- Runtime controller remap/input behavior.
- Runtime Goodies wall behavior.
- Runtime MissionScript execution.
- Installed game mutation or original executable mutation.
- Product UI behavior.
- Ghidra mutation.
- Executable patching.
- Godot parity.
- Rebuild implementation, rebuild parity, and no-noticeable-difference parity.
