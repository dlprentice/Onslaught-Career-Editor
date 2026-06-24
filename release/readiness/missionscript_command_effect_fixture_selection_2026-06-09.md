# MissionScript Command-Effect Fixture Selection Readiness Note

Status: complete fixture selection, not runtime proof
Date: 2026-06-09
Scope: `missionscript-command-effect-fixture-selection`

The MissionScript Command-Effect Rebuild Fixture Selection Proof Plan selects `slot-bitset-save` as the first narrow command-effect fixture path after the completed MissionScript Command-Effect Rebuild Interface Rollup Proof Plan. The public schema artifact is `missionscript-command-effect-fixture-selection.v1.json`.

Readiness anchors:

- `fixtureSelectionStatus=missionscript-command-effect-fixture-selection-complete-slot-bitset-save-selected`
- `selectedFixtureFamily=slot-bitset-save`
- `selectedFixturePath=slot-bitset-save-core-handler-and-career-bridge`
- `selectedChildLane=MissionScript Slot Bitset/Save Rebuild Fixture Proof Plan`
- `selectedCandidateRank=1`
- `candidateFamilyCount=9`
- `selectedSourceProofCount=3`
- `selectedDescriptorEntryCount=3`
- `selectedLooseCorpusRows=18`
- `selectedLevelRows=6`
- `selectedCommandCounts=GetSlot:6/SetSlot:8/SetSlotSave:4`
- `slotRange=0..255`
- `slotStorageDwords=32`
- `runtimeSlotArray=CGame+0x308`
- `careerSlotsBase=0x240A`
- `falseGuardCount=34`
- `zeroCounterCount=25`
- `publicLeakCheck=PASS`
- `latestGhidraBackupClass=verified-static-backup-redacted`

Selected fixture evidence:

| Surface | Static evidence |
| --- | --- |
| Descriptor rows | `SetSlot` index `122`, `GetSlot` index `123`, and `SetSlotSave` index `132`. |
| IScript handlers | `0x005338d0 IScript__SetSlot`, `0x00533900 IScript__SetSlotSave`, and `0x005339a0 IScript__GetSlotBitValue`. |
| CGame helpers | `0x0046d3a0 CGame__SetSlot`, `0x0046d410 CGame__GetSlot`, range `0..255`, `slot >> 5`, `1 << (slot & 31)`, and runtime bitset storage at `CGame+0x308`. |
| Persistent subcase | `SetSlotSave` also bridges to `0x004214e0 CCareer__SetSlot`; copied-file true-view slot base is `0x240A`. |
| Public corpus | `6` level rows and `18` detailed call rows: `6 GetSlot`, `8 SetSlot`, and `4 SetSlotSave` calls across `level100`, `level500`, `level731`, `level732`, `level741`, and `level742`. |
| Numeric seeds | `SetSlot(61)` and `SetSlot(62)` map to dword index `1`, bit masks `0x20000000` and `0x40000000`, and true-view offset `0x240E`. |

Deferred families:

- `message-audio-console` is explicitly deferred because it carries private-frame, text/OCR, queue-ordering, voice/audio, and runtime-display risk.
- `player-state-score` is deferred because of the `AddScore` handler-body conflict plus cockpit, stealth, and weapon-fire/stealth risk.
- `goodie-state-save`, `objective-outcome`, `hud-variable-display`, `cutscene-camera-position`, `vector-range-helpers`, and `thing-value-engine-helper` remain available later with separate guardrails.

Guard tokens:

- `runtimeExecution=false`
- `runtimeMissionScriptExecutionProven=false`
- `runtimeCommandEffectsProven=false`
- `runtimeSlotPersistenceProven=false`
- `runtimeSaveBehaviorProven=false`
- `runtimeTutorialProgressionProven=false`
- `runtimeLevel500BranchProven=false`
- `runtimeFenrirStateProven=false`
- `beLaunch=false`
- `newLaunch=false`
- `screenshotCapture=false`
- `privateFrameReviewPerformed=false`
- `rowObservation=false`
- `exactTextOcrPerformed=false`
- `rawDialoguePublished=false`
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
- `beProcessesAfterSelection=0`

Validation expectation:

- Focused probe: `npm run test:missionscript-command-effect-fixture-selection`
- Parent rollup probe: `npm run test:missionscript-command-effect-rebuild-interface-rollup`
- Slot source probe: `npm run test:missionscript-slot-command-effect-static`
- Save copied-file probe: `npm run test:save-options-controller-byte-preservation-copied-file`

What this proves:

- The first MissionScript command-effect rebuild fixture path is selected from the completed static interface rollup.
- The selected fixture is `slot-bitset-save`, with `SetSlot`/`GetSlot` as the core bitset fixture and `SetSlotSave` as a separate persistence subcase.
- The next child lane has concrete static evidence requirements and stop conditions before any runtime, Godot, patching, or rebuild implementation.

What remains unproven:

- Runtime MissionScript execution.
- Runtime command effects.
- Runtime slot persistence.
- Runtime save/load behavior.
- Runtime tutorial progression, Level500 branch behavior, or Fenrir state behavior.
- Live loose-MSL loading or packed-resource script selection.
- Source-selection observation, private-frame review, visual QA, Godot parity, executable patching behavior, rebuild implementation, rebuild parity, or no-noticeable-difference parity.
