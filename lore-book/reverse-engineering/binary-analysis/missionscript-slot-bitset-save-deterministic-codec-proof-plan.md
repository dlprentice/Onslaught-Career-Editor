# MissionScript Slot Bitset/Save Deterministic Codec Proof Plan

Status: complete deterministic codec proof plan, not copied-file or runtime proof
Last updated: 2026-06-09
Scope: `missionscript-slot-bitset-save-deterministic-codec`

This proof completes the deterministic child lane selected by the [MissionScript Slot Bitset/Save Rebuild Fixture Proof Plan](missionscript-slot-bitset-save-rebuild-fixture-proof-plan.md). It proves pure slot bitset math and true-view save offset calculation for the selected `slot-bitset-save` fixture without reading private baselines, writing copied files, launching BEA, mutating Ghidra, patching an executable, or starting Godot work.

Machine-checkable artifact:

- [missionscript-slot-bitset-save-deterministic-codec-proof-plan.v1.json](missionscript-slot-bitset-save-deterministic-codec-proof-plan.v1.json)

Proof tokens:

- `slotBitsetSaveDeterministicCodecProofPlanStatus=missionscript-slot-bitset-save-deterministic-codec-proof-plan-complete-pure-codec-not-runtime-proof`
- `selectedFixtureFamily=slot-bitset-save`
- `selectedFixturePath=slot-bitset-save-core-handler-and-career-bridge`
- `previousSlice=MissionScript Slot Bitset/Save Rebuild Fixture Proof Plan`
- `selectedNextSlice=MissionScript Slot Bitset/Save Copied-File Byte-Diff Proof Plan`
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

Guard tokens:

- `copiedFileMutation=false`
- `copiedFileWritePerformed=false`
- `sourceBaselineRead=false`
- `privateArtifactMaterialized=false`
- `saveSynthesis=false`
- `runtimeExecution=false`
- `runtimeMissionScriptExecutionProven=false`
- `runtimeCommandEffectsProven=false`
- `runtimeSlotPersistenceProven=false`
- `runtimeSaveBehaviorProven=false`
- `runtimeSaveLoadBehaviorProven=false`
- `beLaunch=false`
- `newLaunch=false`
- `screenshotCapture=false`
- `privateFrameReviewPerformed=false`
- `rowObservation=false`
- `sourceSelectionObserved=false`
- `nativeInput=false`
- `debuggerAttachment=false`
- `godotWork=false`
- `ghidraMutation=false`
- `executablePatching=false`
- `rebuildImplementation=false`
- `rebuildParityProven=false`
- `noNoticeableDifferenceParityProven=false`
- `runtimeObservationRows=0`
- `missionScriptRuntimeEvidenceRows=0`
- `runtimeCommandEffectRows=0`
- `runtimeSlotEvidenceRows=0`
- `runtimeSaveRows=0`
- `copiedFileMutationRows=0`
- `copiedFileDiffRows=0`
- `copiedFileWriteRows=0`
- `sourceBaselineReadRows=0`
- `privateArtifactRows=0`
- `byteDiffRows=0`
- `saveCodecWriteRows=0`
- `beProcessesAfterCodec=0`

This is not a runtime MissionScript execution proof, runtime command-effect proof, runtime slot-persistence proof, runtime save/load proof, tutorial progression proof, Level500 branch proof, Fenrir state proof, live loose-MSL loading proof, packed-resource script-selection proof, private-frame review, row observation, BEA launch, screenshot or frame capture, OCR pass, raw dialogue publication, source-selection proof, native-input run, debugger attachment, Godot project, Ghidra mutation, executable patch, copied-file mutation, source-baseline read, private artifact materialization, save synthesis, rebuild implementation, rebuild parity proof, or no-noticeable-difference parity proof.

## Static Closeout Context

| Track | Current |
| --- | --- |
| Static Ghidra function-quality closure | `6411/6411 = 100.00%` |
| Commentless / exact-undefined / `param_N` debt | `0 / 0 / 0` |
| Expanded post-100 static surface | `1560/1560 = 100.00%` |
| Active current-risk focused accounting | `1179/1179 = 100.00%` |
| Remaining active focused work | `0` |
| Latest verified Ghidra backup | `latestGhidraBackupClass=verified-static-backup-redacted` |

This proof does not change `static-reaudit-progress.json`, `static-reaudit-current-risk-ledger.json`, or the current percentages.

## Codec Authority

| Surface | Deterministic authority |
| --- | --- |
| Descriptor table | `0x0052ff30 ScriptCommandRegistry__InitBuiltins` initializes descriptor table `0x0064ce50` with stride `64` and `144` declared slots. |
| Descriptor rows | `SetSlot` descriptor index `122` at `0x0064ecd0`, `GetSlot` descriptor index `123` at `0x0064ed10`, and `SetSlotSave` descriptor index `132` at `0x0064ef50`. |
| IScript handlers | `0x005338d0 IScript__SetSlot`, `0x00533900 IScript__SetSlotSave`, and `0x005339a0 IScript__GetSlotBitValue`. |
| Runtime-slot helpers | `0x0046d3a0 CGame__SetSlot` and `0x0046d410 CGame__GetSlot` compute `slot >> 5` and `1 << (slot & 31)` against `CGame+0x308`. |
| Persistent helper | `0x004214e0 CCareer__SetSlot` is the static persistent-slot helper reached by `IScript__SetSlotSave`; runtime persistence and save-write behavior remain separate proof. |
| True-view save model | `file_offset = 0x0002 + career_offset`; `careerSlotsBase=0x240A`; `careerSlotsEndExclusive=0x248A`; `usedSlotDwords=8` for helper range `0..255`; `reservedSlotStorageDwords=32`; `slotStorageBytes=128`. |

## Deterministic Codec Model

The proof recomputes every row from these formulas:

- `slotRange=0..255`
- `usedSlotDwords=8`
- `reservedSlotStorageDwords=32`
- `slotStorageDwords=32`
- `slotStorageBytes=128`
- `dwordIndex=slot >> 5`
- `bitIndex=slot & 31`
- `bitMask=1 << (slot & 31)`
- `trueViewDwordOffset=0x240A + (4 * (slot >> 5))`
- `littleEndianByteOffset=trueViewDwordOffset + ((slot & 31) >> 3)`
- `littleEndianByteMask=1 << ((slot & 31) & 7)`

| Slot | Source class | Dword index | Bit index | Dword mask | Dword range | LE byte offset | LE byte mask | Zero-dword bytes after set |
| ---: | --- | ---: | ---: | --- | --- | --- | --- | --- |
| `0` | derived boundary vector | `0` | `0` | `0x00000001` | `0x240A-0x240D` | `0x240A` | `0x01` | `01 00 00 00` |
| `31` | derived boundary vector | `0` | `31` | `0x80000000` | `0x240A-0x240D` | `0x240D` | `0x80` | `00 00 00 80` |
| `32` | derived boundary vector | `1` | `0` | `0x00000001` | `0x240E-0x2411` | `0x240E` | `0x01` | `01 00 00 00` |
| `61` | public loose-MSL `SetSlot(61)` seed | `1` | `29` | `0x20000000` | `0x240E-0x2411` | `0x2411` | `0x20` | `00 00 00 20` |
| `62` | public loose-MSL `SetSlot(62)` seed | `1` | `30` | `0x40000000` | `0x240E-0x2411` | `0x2411` | `0x40` | `00 00 00 40` |

Slot storage note: the save buffer reserves `mSlots[32]` (`reservedSlotStorageDwords=32`, `slotStorageBytes=128`) from `0x240A` through `0x2489`, but the static helper range is `0..255`, so deterministic helper-addressable slots use only dwords `0..7` (`usedSlotDwords=8`). Dwords `8..31` are reserved/preserved storage for this proof.

## Combined Seed Vector

Public loose-MSL numeric seeds `SetSlot(61)` and `SetSlot(62)` share dword index `1` and true-view dword range `0x240E-0x2411`.

| Slots | Dword index | Bit indices | Combined mask | Dword range | LE byte offset | LE byte mask | Zero-dword bytes after set |
| --- | ---: | --- | --- | --- | --- | --- | --- |
| `61, 62` | `1` | `29, 30` | `0x60000000` | `0x240E-0x2411` | `0x2411` | `0x60` | `00 00 00 60` |

The byte-diff rule for a later copied-file proof is `little-endian dword XOR mask subset, not single-byte expectation`. The deterministic codec records `allowedDwordXorMask=0x60000000`, `slot61Mask=0x20000000`, `slot62Mask=0x40000000`, `unexpectedDiffCount=0`, and `legacyTrapHitCount=0` as future gates only.

## Deferred Copied-File Proof Gate

The selected next child lane is `MissionScript Slot Bitset/Save Copied-File Byte-Diff Proof Plan`. That lane may touch a copied real baseline only after it records the following gates:

| Gate | Required value |
| --- | --- |
| `requiresCopiedRealBaseline` | `true` |
| `saveSynthesisAllowed` | `false` |
| `expectedSize` | `10004` / `0x2714` |
| `versionWord` | `0x4BD1` |
| `trueViewRule` | `file_offset = 0x0002 + career_offset` |
| `allowedDwordRange` | `0x240E-0x2411` |
| `allowedDwordXorMask` | `0x60000000` |
| `comparisonMode` | `little-endian dword XOR mask subset, not single-byte expectation` |
| `fileSizePreserved` | `true` |
| `versionWordPreserved` | `true` |
| `unexpectedDiffCount` | `0` |
| `legacyTrapHitCount` | `0` |

Preservation ranges for the later lane:

- `0x23F6-0x2409 kill counters and pre-slot tail`
- `0x240A-0x240D slot dword 0 unless explicitly selected`
- `0x2412-0x2489 remaining slot dwords unless explicitly selected`
- `0x248A-0x24BD post-slot fields through pre-options`
- `0x24BE-0x26BD options entries`
- `0x26BE-0x2713 options tail`
- `reserved Goodies 233-299`
- `legacy trap offsets 0x23A4, 0x22D4, 0x240C`

## Claim Boundary

This proves pure deterministic slot bitset codec math for slots `0`, `31`, `32`, `61`, and `62`; true-view save dword offsets for those vectors; the combined public numeric seed mask `0x60000000` in little-endian dword range `0x240E-0x2411`; and the guard shape for a later copied-file byte-diff lane.

It does not prove runtime MissionScript execution, runtime command effects, runtime slot persistence, runtime save/load behavior, runtime tutorial progression, Level500 branch behavior, Fenrir state behavior, live loose-MSL loading, packed-resource script selection, exact descriptor layout, exact arity, exact argument type schema, exact CGame layout, exact CCareer layout, copied-file mutation, source-baseline read, private artifact materialization, save synthesis, BEA patching behavior, visual QA, Godot parity, Ghidra mutation, executable patching, rebuild implementation, rebuild parity, or no-noticeable-difference parity.
