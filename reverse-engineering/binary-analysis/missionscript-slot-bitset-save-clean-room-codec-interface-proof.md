# MissionScript Slot Bitset/Save Clean-Room Codec Interface Proof

Status: clean-room AppCore codec interface complete, not runtime proof
Last updated: 2026-06-09
Scope: `missionscript-slot-bitset-save-clean-room-codec-interface`

This proof completes the static interface child lane selected by the [MissionScript Slot Bitset/Save Copied-File Byte-Diff Proof](missionscript-slot-bitset-save-copied-file-byte-diff-proof.md). It turns the deterministic slot bitset model and copied-file byte-diff result into a small AppCore clean-room codec contract without wiring product UI, touching installed game files, reading private copied baselines, writing `.bes` files, launching BEA, mutating Ghidra, patching executables, starting Godot, or claiming runtime MissionScript behavior.

Machine-checkable artifact:

- [missionscript-slot-bitset-save-clean-room-codec-interface.v1.json](missionscript-slot-bitset-save-clean-room-codec-interface.v1.json)

Implementation anchors:

- `OnslaughtCareerEditor.AppCore/MissionScriptSlotBitsetSaveCodec.cs`
- `OnslaughtCareerEditor.AppCore.Tests/MissionScriptSlotBitsetSaveCodecTests.cs`

Proof tokens:

- `slotBitsetSaveCleanRoomCodecInterfaceStatus=missionscript-slot-bitset-save-clean-room-codec-interface-complete-appcore-pure-buffer-contract-not-runtime-proof`
- `previousSlice=MissionScript Slot Bitset/Save Copied-File Byte-Diff Proof`
- `selectedFixtureFamily=slot-bitset-save`
- `selectedFixturePath=slot-bitset-save-core-handler-and-career-bridge`
- `selectedNextSlice=MissionScript Slot Bitset/Save AppCore Copied-Baseline Codec Harness Proof Plan`
- `appCoreCodecPath=OnslaughtCareerEditor.AppCore/MissionScriptSlotBitsetSaveCodec.cs`
- `appCoreTestPath=OnslaughtCareerEditor.AppCore.Tests/MissionScriptSlotBitsetSaveCodecTests.cs`
- `interfaceKind=pure AppCore in-memory buffer codec`
- `productUiWired=false`
- `fileIoPerformed=false`
- `copiedFileMutationPerformed=false`
- `sourceBaselineRead=false`
- `privateArtifactMaterialized=false`
- `expectedFileSize=10004`
- `versionWord=0x4BD1`
- `trueViewRule=file_offset = 0x0002 + career_offset`
- `careerSlotsBase=0x240A`
- `careerSlotsEndExclusive=0x248A`
- `interfaceOperationCount=8`
- `usedSlotDwords=8`
- `reservedSlotStorageDwords=32`
- `slotStorageBytes=128`
- `slotRange=0..255`
- `publicMethodCount=6`
- `deterministicBitsetVectorCount=5`
- `copiedFileSourceProofCount=1`
- `publicLeakCheck=PASS`
- `combinedMask=0x60000000`
- `observedDwordXorMask=0x60000000`
- `baselineToSetChangedOffsets=0x2411`
- `xunitTestCaseCount=9`
- `inMemoryCodecBufferOnly=true`
- `syntheticBesFileWritten=false`
- `runtimeExecution=false`
- `beLaunch=false`
- `ghidraMutation=false`
- `executablePatching=false`
- `godotWork=false`
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

This proof does not change `static-reaudit-progress.json`, `static-reaudit-current-risk-ledger.json`, or the static RE percentages.

## Codec Contract

The AppCore codec exposes a pure in-memory buffer contract for the slot bitset surface:

| Contract row | Value |
| --- | --- |
| Container | `expectedFileSize=10004`, `versionWord=0x4BD1` |
| True-view rule | `file_offset = 0x0002 + career_offset` |
| Slot storage | `careerSlotsBase=0x240A`, `careerSlotsEndExclusive=0x248A`, `slotStorageBytes=128` |
| Slot range | `slotRange=0..255`, `usedSlotDwords=8`, `reservedSlotStorageDwords=32` |
| Slot vector math | `dwordIndexExpression=slot >> 5`, `bitIndexExpression=slot & 31`, `bitMaskExpression=1 << (slot & 31)` |
| True-view offset math | `trueViewOffsetExpression=0x240A + (4 * (slot >> 5))` |
| Interface operations | `interfaceOperationCount=8`: slot-to-dword, slot-to-bit, dword-mask, true-view-offset, read-bit, set-bit, clear-bit, apply-mask-preserving-non-target-bits |
| Public methods | `IsValidCareerSaveContainer`, `GetVector`, `BuildSingleDwordMask`, `GetSlot`, `SetSlot`, `SetSlotsInSingleDword` |

The interface deliberately rejects out-of-range slot numbers and invalid container shape instead of silently widening the claim.

## Test Result

Focused AppCore validation passed:

```text
dotnet test OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo --filter MissionScriptSlotBitsetSaveCodecTests
Passed! - Failed: 0, Passed: 9, Skipped: 0, Total: 9
```

The tests cover:

- static vectors for slots `0`, `31`, `32`, `61`, and `62`
- combined slots `61`/`62` mask `0x60000000` in range `0x240E-0x2411`
- in-memory set touching only byte `0x2411` on a clean codec buffer
- idempotent set behavior
- clear roundtrip behavior
- invalid slot/container guards

## Claim Boundary

This proves the MissionScript slot-bitset/save fixture now has a clean-room AppCore pure-buffer codec interface that reproduces the static vector math and the copied-file dword-mask expectation without file I/O.

It does not prove runtime MissionScript execution, runtime command effects, runtime slot persistence, runtime save/load behavior, runtime defaultoptions behavior, tutorial progression, live loose-MSL loading, packed-resource script selection, copied-file AppCore harness behavior, installed-game mutation, product UI behavior, Ghidra mutation, executable patching, Godot parity, rebuild implementation, rebuild parity, or no-noticeable-difference parity.
