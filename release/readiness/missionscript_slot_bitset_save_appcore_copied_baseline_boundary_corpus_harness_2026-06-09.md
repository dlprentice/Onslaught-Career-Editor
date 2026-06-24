# MissionScript Slot Bitset/Save AppCore Copied-Baseline Boundary Corpus Harness Readiness Note

Status: complete copied-baseline boundary corpus harness proof, not runtime proof
Date: 2026-06-09
Scope: `missionscript-slot-bitset-save-appcore-copied-baseline-boundary-corpus-harness`

Wave summary:

- `MissionScript Slot Bitset/Save AppCore Copied-Baseline Boundary Corpus Harness Proof`
- `slotBitsetSaveAppCoreCopiedBaselineBoundaryCorpusHarnessStatus=missionscript-slot-bitset-save-appcore-copied-baseline-boundary-corpus-harness-complete-copied-real-baseline-boundary-corpus-not-runtime-proof`
- `previousSlice=MissionScript Slot Bitset/Save AppCore Boundary-Slot Corpus Proof`
- `selectedNextSlice=Save / Options Byte-Preservation AppCore Implementation Contract Proof Plan`
- `toolProjectPath=tools/MissionScriptSlotBitsetSaveHarness/MissionScriptSlotBitsetSaveHarness.csproj`
- `appCoreCodecPath=OnslaughtCareerEditor.AppCore/MissionScriptSlotBitsetSaveCodec.cs`
- `interfaceKind=AppCore codec boundary corpus applied by proof-only copied-baseline harness`
- `appCoreCodecUsed=true`
- `manualSlotDwordWriteInHarness=false`
- `appCoreCodecFileIo=false`
- `harnessFileIo=true`
- `productUiWired=false`
- `sourceBaselineRead=true`
- `privateArtifactMaterialized=true`
- `copiedArtifactCount=6`
- `sampleBoundaryArtifactCount=4`
- `sourcePathsPublic=false`
- `sourceHashesPublic=false`
- `artifactPathsPublic=false`
- `artifactHashesPublic=false`
- `rawBeforeAfterDwordsPublic=false`
- `rawBoundaryPairXorMasksPublic=false`
- `rawSaveSlotStatePublic=false`
- `copyBeforeWrite=true`
- `sourceAndOutputPathsDistinct=true`
- `sourceToNewBaselineDiffCount=0`
- `sourceUnchanged=true`
- `expectedSize=10004`
- `versionWord=0x4BD1`
- `trueViewRule=file_offset = 0x0002 + career_offset`
- `existingSeedVectorCaseCount=5`
- `boundaryPairMaskCaseCount=8`
- `singleSlotCopiedBaselineRoundTripCaseCount=256`
- `copiedBaselineHarnessCaseCount=264`
- `boundaryPairMask=0x80000001`
- `boundaryPairExpectedSetXorMode=(~baselineDword) & mask`
- `boundaryVectorSlots=63,64,224,255`
- `boundaryPairDwordOffsets=0x240A,0x240E,0x2412,0x2416,0x241A,0x241E,0x2422,0x2426`
- `allBoundaryPairMasksMatch=true`
- `allBoundaryPairSetXorMatchesBaselineState=true`
- `allBoundaryPairRestoresToBaseline=true`
- `allValidSlotsRoundTrip=true`
- `toggleTouchesOnlyExpectedByteForAllValidSlots=true`
- `toggleIdempotentForAllValidSlots=true`
- `restoreToBaselineForAllValidSlots=true`
- `crossDwordMaskRejected=true`
- `slot256Rejected=true`
- `wrongSizeRejected=true`
- `wrongVersionRejected=true`
- `baselineToNoopDiffCount=0`
- `reservedSlotTailAfterUsedDwordsUnchangedForAllValidSlots=true`
- `postSlotFieldsThroughPreOptionsUnchangedForAllValidSlots=true`
- `optionsEntriesUnchangedForAllValidSlots=true`
- `optionsTailUnchangedForAllValidSlots=true`
- `unexpectedLegacyTrapHitCount=0`
- `unexpectedDiffCount=0`
- `saveSynthesis=false`
- `runtimeExecution=false`
- `beLaunch=false`
- `ghidraMutation=false`
- `executablePatching=false`
- `godotWork=false`
- `rebuildImplementation=false`
- `runtimeObservationRows=0`
- `missionScriptRuntimeEvidenceRows=0`
- `runtimeCommandEffectRows=0`
- `runtimeSaveRows=0`
- `publicLeakCheck=PASS`

Evidence:

- Public proof: `reverse-engineering/binary-analysis/missionscript-slot-bitset-save-appcore-copied-baseline-boundary-corpus-harness-proof.md`
- Public schema: `reverse-engineering/binary-analysis/missionscript-slot-bitset-save-appcore-copied-baseline-boundary-corpus-harness.v1.json`
- Focused probe: `tools/missionscript_slot_bitset_save_appcore_copied_baseline_boundary_corpus_harness_probe.py`
- Harness project: `tools/MissionScriptSlotBitsetSaveHarness/MissionScriptSlotBitsetSaveHarness.csproj`

What this proves:

- The proof-only C# harness applies the AppCore MissionScript slot-bitset/save boundary corpus to a copied real career baseline.
- The copied-baseline boundary pairs use baseline-aware set-XOR comparison instead of assuming bits are initially clear.
- All 256 valid saved slots toggle through AppCore against copied-baseline bytes, touch only the expected little-endian byte, and restore to baseline.
- The no-op copy, sample boundary artifacts, non-target slot tail, post-slot fields, options entries, options tail, and legacy trap offsets match the byte-preservation contract.

What remains unproven:

- Runtime MissionScript execution.
- Runtime command effects.
- Runtime slot persistence.
- Runtime save/load/defaultoptions behavior.
- Source selection, private-frame review, screenshot/frame interpretation, native input, or debugger behavior.
- Installed-game mutation, product UI behavior, Ghidra mutation, executable patching, or Godot parity.
- Rebuild implementation, rebuild parity, or no-noticeable-difference parity.
