# MissionScript Slot Bitset/Save Rebuild Fixture Proof Plan Readiness Note

Status: complete proof plan, not runtime proof
Date: 2026-06-09
Scope: `missionscript-slot-bitset-save-rebuild-fixture-proof-plan`

MissionScript Slot Bitset/Save Rebuild Fixture Proof Plan turns the selected `slot-bitset-save` fixture into a deterministic codec child-lane plan. It is public-safe static planning only.

Previous slice: MissionScript Command-Effect Rebuild Fixture Selection Proof Plan.
Machine-checkable artifact: `missionscript-slot-bitset-save-rebuild-fixture-proof-plan.v1.json`.

Readiness anchors:

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

Selected anchors:

| Surface | Evidence |
| --- | --- |
| Descriptor table | `0x0052ff30 ScriptCommandRegistry__InitBuiltins`, table `0x0064ce50`, stride `64`, and `144` declared slots. |
| Descriptor rows | `SetSlot` index `122` at `0x0064ecd0`, `GetSlot` index `123` at `0x0064ed10`, and `SetSlotSave` index `132` at `0x0064ef50`. |
| IScript handlers | `0x005338d0 IScript__SetSlot`, `0x00533900 IScript__SetSlotSave`, and `0x005339a0 IScript__GetSlotBitValue`. |
| Helpers | `0x0046d3a0 CGame__SetSlot`, `0x0046d410 CGame__GetSlot`, and `0x004214e0 CCareer__SetSlot`. |
| Save true view | `file_offset = 0x0002 + career_offset`, `mSlots[0]` at `0x240A`, and no copied-file mutation in this slice. |
| Public numeric seeds | `SetSlot(61)` and `SetSlot(62)` are the public loose-MSL numeric seeds. |

Deterministic child-lane vectors:

| Slot | Dword index | Bit index | Mask | True-view dword offset |
| ---: | ---: | ---: | --- | --- |
| `0` | `0` | `0` | `0x00000001` | `0x240A` |
| `31` | `0` | `31` | `0x80000000` | `0x240A` |
| `32` | `1` | `0` | `0x00000001` | `0x240E` |
| `61` | `1` | `29` | `0x20000000` | `0x240E` |
| `62` | `1` | `30` | `0x40000000` | `0x240E` |

Deferred byte-diff guard: a later copied-file slot proof must compare the little-endian dword at `0x240E-0x2411`, not assume only byte `0x240E` changes. Slot `61` must stay within dword XOR mask `0x20000000`; slot `62` must stay within dword XOR mask `0x40000000`; any copied-file write proof must keep `unexpectedDiffCount=0`, `legacyTrapHitCount=0`, file size preserved, version word preserved, and unrelated ranges unchanged.

Guard tokens:

- `runtimeExecution=false`
- `runtimeMissionScriptExecutionProven=false`
- `runtimeCommandEffectsProven=false`
- `runtimeSlotPersistenceProven=false`
- `runtimeSaveBehaviorProven=false`
- `runtimeSaveLoadBehaviorProven=false`
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

Validation expectation:

- Focused probe: `npm run test:missionscript-slot-bitset-save-rebuild-fixture-proof-plan`
- Parent fixture-selection probe: `npm run test:missionscript-command-effect-fixture-selection`
- Slot source probe: `npm run test:missionscript-slot-command-effect-static`
- Save copied-file probe: `npm run test:save-options-controller-byte-preservation-copied-file`
- Transition backlog probe: `npm run test:static-to-proof-transition-backlog`

What this proves:

- The selected MissionScript slot fixture has a deterministic child-lane plan.
- The next child lane can begin with pure bitset and true-view offset math.
- Copied-file mutation and runtime proof remain deferred.

What remains unproven:

- Runtime MissionScript execution.
- Runtime command effects.
- Runtime slot persistence.
- Runtime save/load behavior.
- Runtime tutorial progression, Level500 branch behavior, or Fenrir state behavior.
- Live loose-MSL loading or packed-resource script selection.
- Source-selection observation, private-frame review, visual QA, Godot parity, executable patching behavior, copied-file mutation, save synthesis, rebuild implementation, rebuild parity, or no-noticeable-difference parity.
