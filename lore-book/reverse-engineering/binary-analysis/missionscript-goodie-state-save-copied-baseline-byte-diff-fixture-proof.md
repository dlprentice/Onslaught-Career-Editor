# MissionScript Goodie State / Save Copied-Baseline Byte-Diff Fixture Proof

Status: copied real-baseline AppCore byte-diff fixture proof complete, not runtime proof
Last updated: 2026-06-09
Scope: `missionscript-goodie-state-save-copied-baseline-byte-diff-fixture-proof`

This proof completes the copied-baseline child lane selected by the [MissionScript Goodie State / Save Command-Effect Fixture Proof Plan](missionscript-goodie-state-save-command-effect-fixture-proof-plan.md). It uses a proof-only C# harness to call AppCore `BesFilePatcher.PatchGoodieStates` against copied real `.bes` and validation-only `defaultoptions.bea` baselines in ignored private evidence, then publishes only sanitized public counts, offset labels, and pass/fail booleans.

Machine-checkable artifact:

- [missionscript-goodie-state-save-copied-baseline-byte-diff-fixture-proof.v1.json](missionscript-goodie-state-save-copied-baseline-byte-diff-fixture-proof.v1.json)

Proof tokens:

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

## Static Closeout Context

| Track | Current |
| --- | --- |
| Static Ghidra function-quality closure | `6411/6411 = 100.00%` |
| Commentless / exact-undefined / `param_N` debt | `0 / 0 / 0` |
| Expanded post-100 static surface | `1560/1560 = 100.00%` |
| Active current-risk focused accounting | `1179/1179 = 100.00%` |
| Remaining active focused work | `0` |
| Latest verified Ghidra backup | `latestGhidraBackupClass=verified-static-backup-redacted` |

This proof does not change the Ghidra database, the static RE percentages, executable bytes, or any tracked/private source save.

## Harness Result

| Check | Result |
| --- | --- |
| Harness surface | `toolProjectPath=tools/MissionScriptGoodieStateSaveHarness/MissionScriptGoodieStateSaveHarness.csproj`; `appCorePatcherPath=OnslaughtCareerEditor.AppCore/BesFilePatcher.cs`. |
| AppCore service | `appCoreService=BesFilePatcher.PatchGoodieStates`; `patcherInputIndexClass=zero-based-save-goodie-index`. |
| Index mapping | `scriptIndexSaveIndexDisambiguated=true`; `scriptIndices=1,51,53,68,71,233`; `saveGoodieIndices=0,50,52,67,70,232`. |
| Container shape | `expectedSize=10004`; `versionWord=0x4BD1`; `trueViewGoodieBase=0x1F46`; mapping formula `save_goodie_index = script_index - 1`; offset formula `file_offset = 0x1F46 + save_goodie_index * 4`. |
| Provenance guard | `copyBeforeWrite=true`; `sourceAndOutputPathsDistinct=true`; `sourceBaselineBeforeAfterDiffCount=0`; `copiedRealBesBaselineUsed=true`; `copiedDefaultOptionsValidationOnly=true`. |
| Target byte diff | `changedOffsets=0x1F46,0x200E,0x2016,0x2052,0x205E,0x22E6`; `unexpectedDiffCount=0`; `legacyTrapHitCount=0`; `targetReadbackMismatchCount=0`. |
| No-op / idempotent / roundtrip | `careerNoopDiffCount=0`; `defaultOptionsNoopDiffCount=0`; `idempotentDiffCount=0`; `roundtripToBaselineDiffCount=0`. |
| Preservation | `reservedGoodiesUnchanged=true`; `killCountersUnchanged=true`; `techSlotsUnchanged=true`; `optionsEntriesUnchanged=true`; `optionsTailUnchanged=true`. |
| Rejection guards | `reservedIndexRejection=true`; `invalidStateRejection=true`; `inPlaceRejection=true`; `emptyOverrideRejection=true`. |
| Public-safety guards | `sourcePathsPublic=false`; `sourceHashesPublic=false`; `artifactPathsPublic=false`; `artifactHashesPublic=false`; `rawSaveBytesPublic=false`; `patchResultMessagePublic=false`. |

## Claim Boundary

This proves AppCore `PatchGoodieStates` can apply selected Goodie state dwords to a copied real career baseline, translate one-based MissionScript Goodie indices into zero-based save Goodie indices before patching, leave defaultoptions validation-only, and preserve checked non-target save ranges.

It does not prove runtime MissionScript execution, runtime command effects, runtime Goodie state mutation, runtime save/load behavior, runtime defaultoptions behavior, runtime Goodies wall behavior, runtime score behavior, live loose-MSL loading, packed-resource script selection, installed-game mutation, product UI behavior, Ghidra mutation, executable patching, Godot parity, rebuild implementation, rebuild parity, or no-noticeable-difference parity.
