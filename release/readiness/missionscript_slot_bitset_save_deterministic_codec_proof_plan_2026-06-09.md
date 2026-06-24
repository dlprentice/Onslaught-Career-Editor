# MissionScript Slot Bitset/Save Deterministic Codec Proof Plan Readiness

Status: complete deterministic codec proof plan, not copied-file or runtime proof
Date: 2026-06-09
Scope: `missionscript-slot-bitset-save-deterministic-codec`

This slice completes the deterministic child lane selected by the MissionScript Slot Bitset/Save Rebuild Fixture Proof Plan. It proves pure slot bitset math and true-view offset calculation for the selected `slot-bitset-save` fixture without reading private baselines, writing copied files, launching BEA, mutating Ghidra, patching an executable, or starting Godot work.

Artifacts:

- `reverse-engineering/binary-analysis/missionscript-slot-bitset-save-deterministic-codec-proof-plan.md`
- `reverse-engineering/binary-analysis/missionscript-slot-bitset-save-deterministic-codec-proof-plan.v1.json`
- `tools/missionscript_slot_bitset_save_deterministic_codec_proof_plan_probe.py`

Key tokens:

- `slotBitsetSaveDeterministicCodecProofPlanStatus=missionscript-slot-bitset-save-deterministic-codec-proof-plan-complete-pure-codec-not-runtime-proof`
- `previousSlice=MissionScript Slot Bitset/Save Rebuild Fixture Proof Plan`
- `selectedNextSlice=MissionScript Slot Bitset/Save Copied-File Byte-Diff Proof Plan`
- `selectedFixtureFamily=slot-bitset-save`
- `selectedFixturePath=slot-bitset-save-core-handler-and-career-bridge`
- `sourceProofCount=4`
- `descriptorEntryCount=3`
- `handlerAnchorCount=3`
- `helperAnchorCount=3`
- `deterministicBitsetVectorCount=5`
- `publicCorpusNumericSeedCount=2`
- `selectedLooseCorpusRows=18`
- `selectedLevelRows=6`
- `selectedCommandCounts=GetSlot:6/SetSlot:8/SetSlotSave:4`
- `usedSlotDwords=8`
- `reservedSlotStorageDwords=32`
- `slotStorageDwords=32`
- `slotStorageBytes=128`
- `falseGuardCount=40`
- `zeroCounterCount=29`
- `publicLeakCheck=PASS`
- `latestGhidraBackupClass=verified-static-backup-redacted`
- `copiedFileMutation=false`
- `sourceBaselineRead=false`
- `privateArtifactMaterialized=false`
- `saveSynthesis=false`

Codec authority:

| Surface | Evidence |
| --- | --- |
| Descriptor table | `0x0052ff30 ScriptCommandRegistry__InitBuiltins`, table `0x0064ce50`, stride `64`, declared slots `144`. |
| Descriptor rows | `SetSlot` index `122` at `0x0064ecd0`, `GetSlot` index `123` at `0x0064ed10`, `SetSlotSave` index `132` at `0x0064ef50`. |
| IScript handlers | `0x005338d0 IScript__SetSlot`, `0x00533900 IScript__SetSlotSave`, `0x005339a0 IScript__GetSlotBitValue`. |
| Helpers | `0x0046d3a0 CGame__SetSlot`, `0x0046d410 CGame__GetSlot`, `0x004214e0 CCareer__SetSlot`. |
| Save true view | `file_offset = 0x0002 + career_offset`, `careerSlotsBase=0x240A`, `careerSlotsEndExclusive=0x248A`. |

Deterministic vectors:

| Slot | Dword | Bit | Mask | Dword range | LE byte offset | LE byte mask |
| ---: | ---: | ---: | --- | --- | --- | --- |
| `0` | `0` | `0` | `0x00000001` | `0x240A-0x240D` | `0x240A` | `0x01` |
| `31` | `0` | `31` | `0x80000000` | `0x240A-0x240D` | `0x240D` | `0x80` |
| `32` | `1` | `0` | `0x00000001` | `0x240E-0x2411` | `0x240E` | `0x01` |
| `61` | `1` | `29` | `0x20000000` | `0x240E-0x2411` | `0x2411` | `0x20` |
| `62` | `1` | `30` | `0x40000000` | `0x240E-0x2411` | `0x2411` | `0x40` |

Storage boundary: the save reserves `mSlots[32]` (`reservedSlotStorageDwords=32`, `slotStorageBytes=128`) from `0x240A` through `0x2489`, but the static helper range is `0..255`; deterministic helper-addressable slots use dwords `0..7` (`usedSlotDwords=8`). Dwords `8..31` are reserved/preserved storage for this proof.

Combined seed gate:

- Slots `61` and `62` share `0x240E-0x2411`.
- `combinedMask=0x60000000`
- `littleEndianByteOffset=0x2411`
- `littleEndianByteMask=0x60`
- `comparisonMode=little-endian dword XOR mask subset, not single-byte expectation`
- `unexpectedDiffCount=0`
- `legacyTrapHitCount=0`

The next child lane, `MissionScript Slot Bitset/Save Copied-File Byte-Diff Proof Plan`, must require copied real baselines, fixed `10004` byte size, version `0x4BD1`, no save synthesis, full little-endian dword comparison for `0x240E-0x2411`, file size/version preservation, and explicit unrelated-range preservation before any private baseline is touched.

What this proves:

- Pure deterministic codec math for slots `0`, `31`, `32`, `61`, and `62`.
- True-view save dword offsets for those vectors.
- Public numeric seed combination `0x60000000` in little-endian dword range `0x240E-0x2411`.
- The copied-file byte-diff lane has a bounded mask/preservation gate before any private baseline is read.

What remains unproven:

- Runtime MissionScript execution.
- Runtime command effects.
- Runtime slot persistence.
- Runtime save/load behavior.
- Tutorial progression, Level500 branch behavior, or Fenrir state behavior.
- Live loose-MSL loading or packed-resource script selection.
- Copied-file mutation, source-baseline read, private artifact materialization, or save synthesis.
- Ghidra mutation, executable patching, Godot work, rebuild implementation, rebuild parity, or no-noticeable-difference parity.
