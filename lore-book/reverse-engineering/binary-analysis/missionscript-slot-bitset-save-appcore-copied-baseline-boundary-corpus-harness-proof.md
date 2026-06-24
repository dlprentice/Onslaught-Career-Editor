# MissionScript Slot Bitset/Save AppCore Copied-Baseline Boundary Corpus Harness Proof

Status: complete copied-baseline boundary corpus harness proof, not runtime proof
Last updated: 2026-06-09
Scope: `missionscript-slot-bitset-save-appcore-copied-baseline-boundary-corpus-harness`

This proof applies the AppCore MissionScript slot bitset/save boundary corpus to a copied real career baseline through the proof-only C# harness. It extends the prior in-memory boundary corpus into copied-baseline byte-preservation evidence without exposing private source paths, artifact paths, hashes, raw dwords, raw save slot state, or private artifact contents.

Machine-checkable artifact:

- [missionscript-slot-bitset-save-appcore-copied-baseline-boundary-corpus-harness.v1.json](missionscript-slot-bitset-save-appcore-copied-baseline-boundary-corpus-harness.v1.json)

Proof tokens:

- `slotBitsetSaveAppCoreCopiedBaselineBoundaryCorpusHarnessStatus=missionscript-slot-bitset-save-appcore-copied-baseline-boundary-corpus-harness-complete-copied-real-baseline-boundary-corpus-not-runtime-proof`
- `previousSlice=MissionScript Slot Bitset/Save AppCore Boundary-Slot Corpus Proof`
- `selectedNextSlice=Save / Options Byte-Preservation AppCore Implementation Contract Proof Plan`
- `selectedFixtureFamily=slot-bitset-save`
- `selectedFixturePath=slot-bitset-save-core-handler-and-career-bridge`
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

## Copied-Baseline Corpus

| Check | Result |
| --- | --- |
| Harness surface | `toolProjectPath=tools/MissionScriptSlotBitsetSaveHarness/MissionScriptSlotBitsetSaveHarness.csproj`; `appCoreCodecPath=OnslaughtCareerEditor.AppCore/MissionScriptSlotBitsetSaveCodec.cs`. |
| AppCore use | `appCoreCodecUsed=true`; `manualSlotDwordWriteInHarness=false`; the harness calls AppCore set/readback helpers instead of reimplementing slot writes. |
| Private evidence boundary | `sourceBaselineRead=true`; `privateArtifactMaterialized=true`; public schema keeps `sourcePathsPublic=false`, `sourceHashesPublic=false`, `artifactPathsPublic=false`, `artifactHashesPublic=false`, `rawBoundaryPairXorMasksPublic=false`, and `rawSaveSlotStatePublic=false`. |
| Copied artifacts | `copiedArtifactCount=6`: copied baseline, no-op copy, and four boundary-vector samples. Only the counts and sanitized contract are public. |
| Container shape | Copied career save remains `expectedSize=10004`, `versionWord=0x4BD1`, with `trueViewRule=file_offset = 0x0002 + career_offset`. |
| Boundary pairs | `boundaryPairMaskCaseCount=8`; offsets `0x240A`, `0x240E`, `0x2412`, `0x2416`, `0x241A`, `0x241E`, `0x2422`, and `0x2426`; each uses `boundaryPairMask=0x80000001`. |
| Baseline-aware compare | `boundaryPairExpectedSetXorMode=(~baselineDword) & mask`; `allBoundaryPairSetXorMatchesBaselineState=true`; this avoids assuming copied baseline bits are initially clear. |
| Exhaustive copied-baseline roundtrip | `singleSlotCopiedBaselineRoundTripCaseCount=256`; `allValidSlotsRoundTrip=true`; `toggleTouchesOnlyExpectedByteForAllValidSlots=true`; `toggleIdempotentForAllValidSlots=true`; `restoreToBaselineForAllValidSlots=true`. |
| Preservation | `baselineToNoopDiffCount=0`; `reservedSlotTailAfterUsedDwordsUnchangedForAllValidSlots=true`; `postSlotFieldsThroughPreOptionsUnchangedForAllValidSlots=true`; `optionsEntriesUnchangedForAllValidSlots=true`; `optionsTailUnchangedForAllValidSlots=true`; `unexpectedLegacyTrapHitCount=0`; `unexpectedDiffCount=0`. |

The copied-baseline corpus deliberately does not publish raw before/after dwords or raw slot state from the private save. The public claim is the AppCore/harness contract: the measured private run matched expected container, provenance, byte-touch, baseline-aware XOR, no-op, restoration, and preservation guards.

## Claim Boundary

This proves the proof-only C# harness can apply the AppCore MissionScript slot bitset/save boundary corpus to a copied real career baseline, materialize private copied artifacts, preserve checked non-target ranges, and read/restore valid slot bits through AppCore.

It does not prove runtime MissionScript execution, runtime command effects, runtime slot persistence, runtime save/load behavior, runtime defaultoptions behavior, source selection, private-frame review, screenshot or frame interpretation, native input, debugger behavior, installed game mutation, product UI behavior, Ghidra mutation, executable patching, Godot parity, rebuild implementation, rebuild parity, or no-noticeable-difference parity.
