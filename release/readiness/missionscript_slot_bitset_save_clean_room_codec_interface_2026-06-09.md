# MissionScript Slot Bitset/Save Clean-Room Codec Interface Readiness Note

Status: clean-room AppCore codec interface complete, not runtime proof
Date: 2026-06-09
Scope: `missionscript-slot-bitset-save-clean-room-codec-interface`

This slice completes the clean-room AppCore interface child lane selected by the MissionScript slot bitset/save copied-file byte-diff proof. It adds `OnslaughtCareerEditor.AppCore/MissionScriptSlotBitsetSaveCodec.cs` and `OnslaughtCareerEditor.AppCore.Tests/MissionScriptSlotBitsetSaveCodecTests.cs` as a pure in-memory buffer codec and focused xUnit proof.

Proof artifact: MissionScript Slot Bitset/Save Clean-Room Codec Interface Proof, backed by `missionscript-slot-bitset-save-clean-room-codec-interface.v1.json`.

Evidence anchors:

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

Validation:

- `dotnet test OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo --filter MissionScriptSlotBitsetSaveCodecTests`: `Passed! - Failed: 0, Passed: 9, Skipped: 0, Total: 9`

What this proves:

- The slot bitset/save fixture has a clean-room AppCore pure-buffer codec interface.
- The interface reproduces static vector math for slots `0`, `31`, `32`, `61`, and `62`.
- The interface reproduces the slots `61`/`62` dword mask expectation `0x60000000` over `0x240E-0x2411` without file I/O.
- Focused tests cover idempotent set and clear roundtrip behavior on an in-memory codec buffer.

What remains unproven:

- Runtime MissionScript execution.
- Runtime command effects.
- Runtime slot persistence.
- Runtime save/load behavior.
- Runtime defaultoptions behavior.
- Tutorial progression.
- Live loose-MSL loading.
- Packed-resource script selection.
- Copied-file AppCore harness behavior.
- Installed-game mutation.
- Product UI behavior.
- Ghidra mutation.
- Executable patching.
- Godot parity.
- Rebuild implementation.
- Rebuild parity.
- No-noticeable-difference parity.
