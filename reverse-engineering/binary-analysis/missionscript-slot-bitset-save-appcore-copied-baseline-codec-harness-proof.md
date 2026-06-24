# MissionScript Slot Bitset/Save AppCore Copied-Baseline Codec Harness Proof

Status: AppCore copied-baseline codec harness proof complete, not runtime proof
Last updated: 2026-06-09
Scope: `missionscript-slot-bitset-save-appcore-copied-baseline-codec-harness`

This proof completes the AppCore copied-baseline child lane selected by the [MissionScript Slot Bitset/Save Clean-Room Codec Interface Proof](missionscript-slot-bitset-save-clean-room-codec-interface-proof.md). It uses a proof-only C# harness to apply the pure AppCore `MissionScriptSlotBitsetSaveCodec` to a copied real career baseline in private evidence, then publishes a sanitized public schema without source paths, source hashes, artifact paths, artifact hashes, raw before/after dwords, runtime launch, product UI wiring, Ghidra mutation, executable patching, Godot work, or save synthesis.

Machine-checkable artifact:

- [missionscript-slot-bitset-save-appcore-copied-baseline-codec-harness.v1.json](missionscript-slot-bitset-save-appcore-copied-baseline-codec-harness.v1.json)

Proof tokens:

- `slotBitsetSaveAppCoreCopiedBaselineCodecHarnessStatus=missionscript-slot-bitset-save-appcore-copied-baseline-codec-harness-complete-appcore-copied-real-baseline-byte-preservation-not-runtime-proof`
- `previousSlice=MissionScript Slot Bitset/Save Clean-Room Codec Interface Proof`
- `selectedFixtureFamily=slot-bitset-save`
- `selectedFixturePath=slot-bitset-save-core-handler-and-career-bridge`
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

## Static Closeout Context

| Track | Current |
| --- | --- |
| Static Ghidra function-quality closure | `6411/6411 = 100.00%` |
| Commentless / exact-undefined / `param_N` debt | `0 / 0 / 0` |
| Expanded post-100 static surface | `1560/1560 = 100.00%` |
| Active current-risk focused accounting | `1179/1179 = 100.00%` |
| Remaining active focused work | `0` |
| Latest verified Ghidra backup | `latestGhidraBackupClass=verified-static-backup-redacted` |

This proof does not change `static-reaudit-progress.json`, `static-reaudit-current-risk-ledger.json`, or the static RE percentages.

## Harness Result

| Check | Result |
| --- | --- |
| Harness surface | `toolProjectPath=tools/MissionScriptSlotBitsetSaveHarness/MissionScriptSlotBitsetSaveHarness.csproj`; `appCoreCodecPath=OnslaughtCareerEditor.AppCore/MissionScriptSlotBitsetSaveCodec.cs`. |
| AppCore use | `appCoreCodecUsed=true`; `manualSlotDwordWriteInHarness=false`; the harness calls AppCore set/readback helpers instead of reimplementing the slot dword write. |
| Container shape | Copied career save remains `expectedSize=10004`, `versionWord=0x4BD1`, with `trueViewRule=file_offset = 0x0002 + career_offset`. |
| Provenance guard | `copyBeforeWrite=true`; `sourceAndOutputPathsDistinct=true`; `sourceToNewBaselineDiffCount=0`; `sourceUnchanged=true`. |
| Target slots | `slots=61,62`; dword index `1`; `allowedDwordRange=0x240E-0x2411`. |
| Target masks | `slot61Mask=0x20000000`; `slot62Mask=0x40000000`; combined `allowedDwordXorMask=0x60000000`. |
| Set operation | `observedDwordXorMask=0x60000000`; `baselineToSetChangedOffsets=0x2411`; `unexpectedDiffCount=0`; `legacyTrapHitCount=0`. |
| AppCore readback | `slot61AfterSet=true`; `slot62AfterSet=true`; `slot61AfterClear=false`; `slot62AfterClear=false`. |
| No-op copy | `baselineToNoopDiffCount=0`. |
| Idempotent set | `setToIdempotentDiffCount=0`. |
| Clear roundtrip | `clearToBaselineDiffCount=0`. |
| Preservation | `slotDword0Unchanged=true`; remaining slot storage after the target dword unchanged; post-slot fields unchanged; `optionsEntriesUnchanged=true`; `optionsTailUnchanged=true`. |

The comparison mode remains `little-endian dword XOR mask subset, not single-byte expectation`.

## Claim Boundary

This proves the proof-only C# harness can apply the AppCore MissionScript slot-bitset/save codec to a copied real career baseline, materialize private copied artifacts, preserve the checked non-target ranges, and read back the target slot state through AppCore.

It does not prove runtime MissionScript execution, runtime command effects, runtime slot persistence, runtime save/load behavior, runtime defaultoptions behavior, tutorial progression, live loose-MSL loading, packed-resource script selection, installed-game mutation, product UI behavior, Ghidra mutation, executable patching, Godot parity, rebuild implementation, rebuild parity, or no-noticeable-difference parity.
