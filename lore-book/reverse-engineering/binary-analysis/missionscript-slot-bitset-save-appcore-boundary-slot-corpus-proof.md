# MissionScript Slot Bitset/Save AppCore Boundary-Slot Corpus Proof

Status: complete AppCore boundary-slot corpus proof, not runtime proof
Last updated: 2026-06-09
Scope: `missionscript-slot-bitset-save-appcore-boundary-slot-corpus`

This proof extends the clean-room AppCore MissionScript slot bitset/save codec from the prior 61/62 copied-baseline seed into an in-memory boundary and exhaustive valid-slot corpus. It runs no BEA process, reads no private save evidence, mutates no copied file, and performs no Ghidra or executable work.

Machine-checkable artifact:

- [missionscript-slot-bitset-save-appcore-boundary-slot-corpus.v1.json](missionscript-slot-bitset-save-appcore-boundary-slot-corpus.v1.json)

Decision tokens:

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

## Corpus

| Corpus row | Count | Evidence |
| --- | ---: | --- |
| Existing static seed vectors | `5` | Slots `0`, `31`, `32`, `61`, and `62` still prove the core vector math and the copied-file seed mask `0x60000000`. |
| Boundary dword pairs | `8` | First/last slot pair in every used saved slot dword: `0/31`, `32/63`, `64/95`, `96/127`, `128/159`, `160/191`, `192/223`, and `224/255`; each pair builds mask `0x80000001` in the expected true-view dword. |
| Exhaustive valid-slot roundtrip | `256` | Every valid saved slot `0..255` sets exactly its expected little-endian byte, reads back true, is idempotent on repeated set, clears back to baseline, reads false after clear, and preserves the save container header. |

Focused boundary vector slots from the consult are explicitly covered: `boundaryVectorSlots=63,64,224,255`. Slot `63` is dword `1`, bit `31`, byte `0x2411`, mask `0x80000000`; slot `64` is dword `2`, bit `0`, byte `0x2412`, mask `0x00000001`; slot `224` is dword `7`, bit `0`, byte `0x2426`, mask `0x00000001`; slot `255` is dword `7`, bit `31`, byte `0x2429`, mask `0x80000000`. Cross-dword mask construction remains rejected: `crossDwordMaskRejected=true`.

The valid-slot corpus covers the eight used saved slot dwords at true-view ranges `0x240A-0x240D`, `0x240E-0x2411`, `0x2412-0x2415`, `0x2416-0x2419`, `0x241A-0x241D`, `0x241E-0x2421`, `0x2422-0x2425`, and `0x2426-0x2429`. The broader reserved slot storage still runs through `0x248A`, but this proof does not claim runtime use of the reserved 24 dwords after the first 8 used dwords.

## Validation

Command:

```powershell
dotnet test OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo --filter MissionScriptSlotBitsetSaveCodecTests
```

Result:

- `Passed: 273`
- `Failed: 0`
- `Skipped: 0`
- Preview SDK informational message: `NETSDK1057`

## Claim Boundary

This proves the clean-room AppCore in-memory codec maps and roundtrips every valid saved MissionScript slot bit index `0..255` under the current static contract, including dword-boundary pair masks and per-slot byte-touch behavior.

It does not prove runtime MissionScript execution, runtime command effects, runtime slot persistence, runtime save/load/defaultoptions behavior, copied-file boundary corpus behavior, source selection, private-frame review, screenshot/frame interpretation, native input, debugger behavior, product UI behavior, Ghidra mutation, executable patching, Godot parity, rebuild implementation, rebuild parity, or no-noticeable-difference parity.
