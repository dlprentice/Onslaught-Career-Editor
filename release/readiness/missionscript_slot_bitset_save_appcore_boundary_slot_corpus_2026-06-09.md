# MissionScript Slot Bitset/Save AppCore Boundary-Slot Corpus Readiness Note

Status: complete AppCore boundary-slot corpus proof, not runtime proof
Date: 2026-06-09
Scope: `missionscript-slot-bitset-save-appcore-boundary-slot-corpus`

Wave summary:

- `MissionScript Slot Bitset/Save AppCore Boundary-Slot Corpus Proof`
- `slotBitsetSaveAppCoreBoundarySlotCorpusStatus=missionscript-slot-bitset-save-appcore-boundary-slot-corpus-complete-273-appcore-cases-not-runtime-proof`
- `previousSlice=MissionScript Slot Bitset/Save Runtime-Proof Readiness Gate`
- `selectedNextSlice=MissionScript Slot Bitset/Save AppCore Copied-Baseline Boundary Corpus Harness Proof Plan`
- `selectedFixtureFamily=slot-bitset-save`
- `selectedFixturePath=slot-bitset-save-core-handler-and-career-bridge`
- `appCoreCodecPath=OnslaughtCareerEditor.AppCore/MissionScriptSlotBitsetSaveCodec.cs`
- `appCoreTestPath=OnslaughtCareerEditor.AppCore.Tests/MissionScriptSlotBitsetSaveCodecTests.cs`
- `interfaceKind=pure AppCore in-memory buffer codec`
- `dotnetFilter=MissionScriptSlotBitsetSaveCodecTests`
- `xunitTestCaseCount=273`
- `passed=true`
- `existingSeedVectorCaseCount=5`
- `boundaryPairMaskCaseCount=8`
- `singleSlotRoundTripCaseCount=256`
- `validSlotRange=0..255`
- `usedSlotDwords=8`
- `slotStorageDwords=32`
- `usedSlotStorageBytes=32`
- `reservedSlotStorageBytes=128`
- `reservedTailBytes=96`
- `firstValidSlot=0`
- `lastValidSlot=255`
- `firstUsedSlotOffset=0x240A`
- `lastUsedSlotOffset=0x2429`
- `reservedStorageEndExclusive=0x248A`
- `boundaryPairMask=0x80000001`
- `boundaryVectorSlots=63,64,224,255`
- `boundaryPairDwordOffsets=0x240A,0x240E,0x2412,0x2416,0x241A,0x241E,0x2422,0x2426`
- `allValidSlotsRoundTrip=true`
- `setSlotIdempotentForAllValidSlots=true`
- `clearRoundTripsForAllValidSlots=true`
- `touchesOnlyExpectedByteForAllValidSlots=true`
- `crossDwordMaskRejected=true`
- `invalidSlotLowerBoundRejected=true`
- `invalidSlotUpperBoundRejected=true`
- `slot256Rejected=true`
- `wrongSizeRejected=true`
- `wrongVersionRejected=true`
- `fileIoPerformed=false`
- `copiedFileMutationPerformed=false`
- `sourceBaselineRead=false`
- `privateArtifactMaterialized=false`
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

Validation:

- `dotnet test OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo --filter MissionScriptSlotBitsetSaveCodecTests`
- Result: `Passed: 273`, `Failed: 0`, `Skipped: 0`

Evidence:

- Public proof: `reverse-engineering/binary-analysis/missionscript-slot-bitset-save-appcore-boundary-slot-corpus-proof.md`
- Public schema: `reverse-engineering/binary-analysis/missionscript-slot-bitset-save-appcore-boundary-slot-corpus.v1.json`
- Focused probe: `tools/missionscript_slot_bitset_save_appcore_boundary_slot_corpus_probe.py`

What this proves:

- The AppCore in-memory codec maps every valid saved MissionScript slot `0..255`.
- Each single-slot set touches only the expected little-endian byte, is idempotent, and clears back to baseline.
- The first/last slot pair in each used saved dword builds mask `0x80000001` at the expected true-view dword offset.

What remains unproven:

- Runtime MissionScript execution.
- Runtime command effects.
- Runtime slot persistence.
- Runtime save/load/defaultoptions behavior.
- Copied-file boundary corpus behavior.
- Source selection, private-frame review, screenshot/frame interpretation, native input, or debugger behavior.
- Installed-game mutation, product UI behavior, Ghidra mutation, executable patching, or Godot parity.
- Rebuild implementation, rebuild parity, or no-noticeable-difference parity.
