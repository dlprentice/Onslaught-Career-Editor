# MissionScript Slot Bitset/Save AppCore Copied-Baseline Codec Harness Readiness Note

Status: complete copied-baseline AppCore harness proof, not runtime proof
Date: 2026-06-09
Scope: `missionscript-slot-bitset-save-appcore-copied-baseline-codec-harness`

Wave summary:

- `MissionScript Slot Bitset/Save AppCore Copied-Baseline Codec Harness Proof`
- `slotBitsetSaveAppCoreCopiedBaselineCodecHarnessStatus=missionscript-slot-bitset-save-appcore-copied-baseline-codec-harness-complete-appcore-copied-real-baseline-byte-preservation-not-runtime-proof`
- `previousSlice=MissionScript Slot Bitset/Save Clean-Room Codec Interface Proof`
- `selectedNextSlice=MissionScript Slot Bitset/Save Runtime-Proof Readiness Gate Plan`
- `toolProjectPath=tools/MissionScriptSlotBitsetSaveHarness/MissionScriptSlotBitsetSaveHarness.csproj`
- `appCoreCodecPath=OnslaughtCareerEditor.AppCore/MissionScriptSlotBitsetSaveCodec.cs`
- `interfaceKind=AppCore codec applied by proof-only copied-baseline harness`
- `appCoreCodecUsed=true`
- `manualSlotDwordWriteInHarness=false`
- `appCoreCodecFileIo=false`
- `harnessFileIo=true`
- `productUiWired=false`
- `sourceBaselineRead=true`
- `privateArtifactMaterialized=true`
- `copiedArtifactCount=5`
- `sourcePathsPublic=false`
- `sourceHashesPublic=false`
- `artifactPathsPublic=false`
- `artifactHashesPublic=false`
- `rawBeforeAfterDwordsPublic=false`
- `copyBeforeWrite=true`
- `sourceAndOutputPathsDistinct=true`
- `sourceToNewBaselineDiffCount=0`
- `sourceUnchanged=true`
- `expectedSize=10004`
- `versionWord=0x4BD1`
- `trueViewRule=file_offset = 0x0002 + career_offset`
- `slots=61,62`
- `allowedDwordRange=0x240E-0x2411`
- `allowedDwordXorMask=0x60000000`
- `observedDwordXorMask=0x60000000`
- `baselineToSetChangedOffsets=0x2411`
- `unexpectedDiffCount=0`
- `legacyTrapHitCount=0`
- `slot61AfterSet=true`
- `slot62AfterSet=true`
- `slot61AfterClear=false`
- `slot62AfterClear=false`
- `baselineToNoopDiffCount=0`
- `setToIdempotentDiffCount=0`
- `clearToBaselineDiffCount=0`
- `slotDword0Unchanged=true`
- `optionsEntriesUnchanged=true`
- `optionsTailUnchanged=true`
- `saveSynthesis=false`
- `runtimeExecution=false`
- `beLaunch=false`
- `ghidraMutation=false`
- `executablePatching=false`
- `godotWork=false`

Evidence:

- Public proof: `reverse-engineering/binary-analysis/missionscript-slot-bitset-save-appcore-copied-baseline-codec-harness-proof.md`
- Public schema: `reverse-engineering/binary-analysis/missionscript-slot-bitset-save-appcore-copied-baseline-codec-harness.v1.json`
- Focused probe: `tools/missionscript_slot_bitset_save_appcore_copied_baseline_codec_harness_probe.py`
- Harness project: `tools/MissionScriptSlotBitsetSaveHarness/MissionScriptSlotBitsetSaveHarness.csproj`

What this proves:

- The proof-only C# harness applies the AppCore MissionScript slot-bitset/save codec to a copied real career baseline.
- The harness uses AppCore set/readback helpers, not a manual slot-dword write.
- The copied baseline, no-op, set, idempotent set, and clear roundtrip artifacts preserve size, version, non-target slot storage, post-slot fields, options entries, options tail, and legacy trap offsets.

What remains unproven:

- Runtime MissionScript execution.
- Runtime command effects.
- Runtime slot persistence.
- Runtime save/load/defaultoptions behavior.
- Tutorial progression or loose/packed script selection.
- Installed-game mutation.
- Product UI behavior.
- Ghidra mutation or executable patching.
- Godot parity.
- Rebuild implementation, rebuild parity, or no-noticeable-difference parity.
