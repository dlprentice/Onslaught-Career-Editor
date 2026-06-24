# MissionScript Slot Bitset/Save Rebuild Fixture Proof Plan

Status: complete proof plan, not runtime proof
Last updated: 2026-06-09
Scope: `missionscript-slot-bitset-save-rebuild-fixture-proof-plan`

This proof plan turns the completed [MissionScript Command-Effect Rebuild Fixture Selection Proof Plan](missionscript-command-effect-fixture-selection.md) into a concrete, public-safe slot bitset/save fixture lane. It keeps the selected `slot-bitset-save` family narrow: descriptor rows, IScript handlers, CGame/CCareer helper anchors, deterministic bitset math, and copied-file true-view save boundaries.

Machine-checkable artifact:

- [missionscript-slot-bitset-save-rebuild-fixture-proof-plan.v1.json](missionscript-slot-bitset-save-rebuild-fixture-proof-plan.v1.json)

Plan tokens:

- `slotBitsetSaveFixturePlanStatus=missionscript-slot-bitset-save-rebuild-fixture-proof-plan-complete-deterministic-codec-selected`
- `selectedFixtureFamily=slot-bitset-save`
- `selectedFixturePath=slot-bitset-save-core-handler-and-career-bridge`
- `selectedNextSlice=MissionScript Slot Bitset/Save Deterministic Codec Proof Plan`
- `sourceProofCount=4`
- `descriptorEntryCount=3`
- `handlerAnchorCount=3`
- `helperAnchorCount=3`
- `deterministicBitsetVectorCount=5`
- `publicCorpusNumericSeedCount=2`
- `selectedLooseCorpusRows=18`
- `selectedLevelRows=6`
- `selectedCommandCounts=GetSlot:6/SetSlot:8/SetSlotSave:4`
- `descriptorTableInit=0x0052ff30 ScriptCommandRegistry__InitBuiltins`
- `descriptorTableBase=0x0064ce50`
- `descriptorStrideBytes=64`
- `descriptorDeclaredSlots=144`
- `slotRange=0..255`
- `slotStorageDwords=32`
- `slotStorageBytes=128`
- `runtimeSlotArray=CGame+0x308`
- `careerSlotsBase=0x240A`
- `baseFalseGuardCount=34`
- `addedFixtureFalseGuardCount=6`
- `falseGuardCount=40`
- `baseZeroCounterCount=25`
- `addedFixtureZeroCounterCount=4`
- `zeroCounterCount=29`
- `publicLeakCheck=PASS`
- `latestGhidraBackupClass=verified-static-backup-redacted`

Guard tokens:

- `runtimeExecution=false`
- `runtimeMissionScriptExecutionProven=false`
- `runtimeCommandEffectsProven=false`
- `runtimeSlotPersistenceProven=false`
- `runtimeSaveBehaviorProven=false`
- `runtimeSaveLoadBehaviorProven=false`
- `runtimeTutorialProgressionProven=false`
- `runtimeLevel500BranchProven=false`
- `runtimeFenrirStateProven=false`
- `copiedFileMutation=false`
- `saveSynthesis=false`
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
- `saveCodecWriteRows=0`
- `beProcessesAfterPlan=0`

This is not a runtime MissionScript execution proof, runtime command-effect proof, runtime slot-persistence proof, runtime save/load proof, tutorial progression proof, Level500 branch proof, Fenrir state proof, live loose-MSL loading proof, packed-resource script-selection proof, private-frame review, row observation, BEA launch, screenshot or frame capture, OCR pass, raw dialogue publication, source-selection proof, native-input run, debugger attachment, Godot project, Ghidra mutation, executable patch, copied-file mutation, save synthesis, rebuild implementation, rebuild parity proof, or no-noticeable-difference parity proof.

## Static Closeout Context

| Track | Current |
| --- | --- |
| Static Ghidra function-quality closure | `6411/6411 = 100.00%` |
| Commentless / exact-undefined / `param_N` debt | `0 / 0 / 0` |
| Expanded post-100 static surface | `1560/1560 = 100.00%` |
| Active current-risk focused accounting | `1179/1179 = 100.00%` |
| Remaining active focused work | `0` |
| Latest verified Ghidra backup | `latestGhidraBackupClass=verified-static-backup-redacted` |

This proof plan does not change `static-reaudit-progress.json`, `static-reaudit-current-risk-ledger.json`, or the current percentages.

## Fixture Evidence

| Surface | Planned static fixture |
| --- | --- |
| Descriptor table | `0x0052ff30 ScriptCommandRegistry__InitBuiltins` initializes descriptor table `0x0064ce50` with stride `64` and `144` declared slots. |
| Descriptor rows | `SetSlot` descriptor index `122` at `0x0064ecd0`, `GetSlot` descriptor index `123` at `0x0064ed10`, and `SetSlotSave` descriptor index `132` at `0x0064ef50`. |
| IScript handlers | `0x005338d0 IScript__SetSlot`, `0x00533900 IScript__SetSlotSave`, and `0x005339a0 IScript__GetSlotBitValue`. |
| Runtime-slot helpers | `0x0046d3a0 CGame__SetSlot` and `0x0046d410 CGame__GetSlot`, using `slot>>5` and `1<<(slot&31)` against `CGame+0x308`. |
| Persistent helper | `0x004214e0 CCareer__SetSlot` is the static persistent-slot helper reached by `IScript__SetSlotSave`; runtime persistence and save-write behavior remain separate proof. |
| Save true view | The copied-file save proof anchors `mSlots[0]` at true-view file offset `0x240A`, using `file_offset = 0x0002 + career_offset`; this plan performs no copied-file byte edit. |
| Public loose-MSL corpus | `6` slot-using level rows and `18` detailed call rows: `6 GetSlot`, `8 SetSlot`, and `4 SetSlotSave` calls across `level100`, `level500`, `level731`, `level732`, `level741`, and `level742`. |

## Deterministic Bitset Vectors

The next deterministic codec proof should begin with pure slot math, not runtime mission execution. These vectors are derived from `slot >> 5`, `slot & 31`, `1 << (slot & 31)`, and true-view slot dword offset `0x240A + (4 * dwordIndex)`.

| Slot | Source class | Dword index | Bit index | Mask | True-view dword offset |
| ---: | --- | ---: | ---: | --- | --- |
| `0` | derived boundary vector | `0` | `0` | `0x00000001` | `0x240A` |
| `31` | derived boundary vector | `0` | `31` | `0x80000000` | `0x240A` |
| `32` | derived boundary vector | `1` | `0` | `0x00000001` | `0x240E` |
| `61` | public loose-MSL `SetSlot(61)` seed | `1` | `29` | `0x20000000` | `0x240E` |
| `62` | public loose-MSL `SetSlot(62)` seed | `1` | `30` | `0x40000000` | `0x240E` |

Symbolic corpus expressions `SLOT_TUTORIAL_1`, `SLOT_TUTORIAL_2`, `SLOT_TUTORIAL_3`, `SLOT_TUTORIAL_4`, `n`, and `n + 29` remain corpus vocabulary only until a later proof resolves them safely.

## Child-Lane Plan

| Row | Requirement | Boundary |
| --- | --- | --- |
| `descriptor-codec` | Reconfirm `SetSlot`, `GetSlot`, and `SetSlotSave` descriptor indices `122`, `123`, and `132` from tracked descriptor/slot schemas. | Static descriptor proof only. |
| `handler-codec` | Preserve handler/helper anchors `0x005338d0`, `0x00533900`, `0x005339a0`, `0x0046d3a0`, `0x0046d410`, and `0x004214e0`. | Static handler bridge only. |
| `bitset-codec` | Implement deterministic test vectors for slots `0`, `31`, `32`, `61`, and `62`. | Pure codec math only; not runtime `CGame` proof. |
| `true-view-codec` | Compute slot dword offsets from `0x240A + 4 * (slot >> 5)` without writing copied files. | Offset math only; not save/load behavior. |
| `copied-file-gate` | If a later lane writes copied bytes, require copied real baselines, fixed `10004` byte size, version `0x4BD1`, no save synthesis, and explicit byte diff allowlists. | Deferred copied-file proof. |
| `byte-diff-gate` | For later slot `61`/`62` copied-file writes, compare the little-endian dword at `0x240E-0x2411`; do not expect only byte `0x240E` to change. Require the dword XOR mask to stay within `0x20000000` and/or `0x40000000`, `unexpectedDiffCount=0`, `legacyTrapHitCount=0`, file size preserved, version word preserved, and unrelated ranges unchanged. | Deferred copied-file byte-diff proof only. |
| `runtime-stop` | Stop if the proof needs live MissionScript execution, runtime mission selection, source-selection observation, screenshots, private frame review, native input, debugger attachment, Godot, Ghidra mutation, executable patching, copied-file mutation, or installed-game mutation. | Defer instead of broadening. |

## Claim Boundary

This proves the rebuild fixture plan for deterministic MissionScript slot bitset/save codec work. It does not prove runtime MissionScript execution, runtime command effects, runtime slot persistence, runtime save/load behavior, runtime tutorial progression, Level500 branch behavior, Fenrir state behavior, live loose-MSL loading, packed-resource script selection, exact descriptor layout, exact arity, exact argument type schema, exact CGame layout, exact CCareer layout, copied-file mutation, save synthesis, BEA patching behavior, visual QA, Godot parity, rebuild implementation, rebuild parity, or no-noticeable-difference parity.
