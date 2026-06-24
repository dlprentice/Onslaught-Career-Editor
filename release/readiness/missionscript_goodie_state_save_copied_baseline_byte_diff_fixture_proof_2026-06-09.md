# MissionScript Goodie State / Save Copied-Baseline Byte-Diff Fixture Proof Readiness

Status: complete copied real-baseline AppCore byte-diff fixture proof
Date: 2026-06-09
Scope: `missionscript-goodie-state-save-copied-baseline-byte-diff-fixture-proof`

The MissionScript Goodie State / Save Copied-Baseline Byte-Diff Fixture Proof is recorded at `reverse-engineering/binary-analysis/missionscript-goodie-state-save-copied-baseline-byte-diff-fixture-proof.md` and `reverse-engineering/binary-analysis/missionscript-goodie-state-save-copied-baseline-byte-diff-fixture-proof.v1.json`.

Readiness tokens:

- `missionScriptGoodieStateSaveCopiedBaselineByteDiffFixtureProofStatus=missionscript-goodie-state-save-copied-baseline-byte-diff-fixture-proof-complete-copied-real-baseline-appcore-byte-diff-not-runtime-proof`
- `previousSlice=MissionScript Goodie State / Save Command-Effect Fixture Proof Plan`
- `selectedFixtureFamily=goodie-state-save`
- `selectedFixturePath=goodie-state-save-index-state-byte-preservation`
- `selectedNextSlice=MissionScript Goodie State / Save Clean-Room Codec Interface Proof Plan`
- `toolProjectPath=tools/MissionScriptGoodieStateSaveHarness/MissionScriptGoodieStateSaveHarness.csproj`
- `appCorePatcherPath=OnslaughtCareerEditor.AppCore/BesFilePatcher.cs`
- `appCoreService=BesFilePatcher.PatchGoodieStates`
- `patcherInputIndexClass=zero-based-save-goodie-index`
- `scriptIndexSaveIndexDisambiguated=true`
- `copiedRealBesBaselineUsed=true`
- `copiedDefaultOptionsValidationOnly=true`
- `acceptedFixturesDerivedFromCopiedBaselines=true`
- `privateArtifactMaterialized=true`
- `sourcePathsPublic=false`
- `sourceHashesPublic=false`
- `artifactPathsPublic=false`
- `artifactHashesPublic=false`
- `rawSaveBytesPublic=false`
- `patchResultMessagePublic=false`
- `copyBeforeWrite=true`
- `sourceAndOutputPathsDistinct=true`
- `sourceBaselineBeforeAfterDiffCount=0`
- `expectedSize=10004`
- `versionWord=0x4BD1`
- `trueViewGoodieBase=0x1F46`
- `scriptIndices=1,51,53,68,71,233`
- `saveGoodieIndices=0,50,52,67,70,232`
- `changedOffsets=0x1F46,0x200E,0x2016,0x2052,0x205E,0x22E6`
- `unexpectedDiffCount=0`
- `legacyTrapHitCount=0`
- `targetReadbackMismatchCount=0`
- `careerNoopDiffCount=0`
- `defaultOptionsNoopDiffCount=0`
- `idempotentDiffCount=0`
- `roundtripToBaselineDiffCount=0`
- `reservedGoodiesUnchanged=true`
- `killCountersUnchanged=true`
- `techSlotsUnchanged=true`
- `optionsEntriesUnchanged=true`
- `optionsTailUnchanged=true`
- `reservedIndexRejection=true`
- `invalidStateRejection=true`
- `inPlaceRejection=true`
- `emptyOverrideRejection=true`
- `syntheticAuthorityBufferUsed=false`
- `defaultoptionsGoodieMutation=false`
- `runtimeExecution=false`
- `runtimeGoodieStateMutationProven=false`
- `runtimeSaveBehaviorProven=false`
- `ghidraMutation=false`
- `executablePatching=false`
- `godotWork=false`
- `productUiWired=false`
- `rebuildImplementation=false`

What this proves:

- AppCore `BesFilePatcher.PatchGoodieStates` can patch selected Goodie state dwords in a copied real career save baseline.
- The harness keeps MissionScript script indices and zero-based save Goodie indices disambiguated before patching.
- The observed byte diffs stay inside the selected true-view Goodie dword offsets.
- Defaultoptions is validation/no-op only in this lane.
- Source baselines, reserved Goodies, kill counters, tech slots, options entries, options tail, idempotent patching, and roundtrip restore satisfy the byte-preservation contract.

What remains unproven:

- Runtime MissionScript execution.
- Runtime command effects.
- Runtime Goodie state mutation.
- Runtime save/load/defaultoptions behavior.
- Runtime Goodies wall behavior.
- Runtime score behavior.
- Ghidra mutation, executable patch behavior, Godot parity, rebuild implementation, rebuild parity, and no-noticeable-difference parity.
