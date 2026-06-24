# MissionScript Command-Effect Rebuild Fixture Selection Proof Plan

Status: complete fixture selection, not runtime proof
Last updated: 2026-06-09
Scope: `missionscript-command-effect-fixture-selection`

This result selects the first narrow MissionScript command-effect fixture path after the completed [MissionScript Command-Effect Rebuild Interface Rollup Proof Plan](missionscript-command-effect-rebuild-interface-rollup.md).

Machine-checkable artifact:

- [missionscript-command-effect-fixture-selection.v1.json](missionscript-command-effect-fixture-selection.v1.json)

Selection tokens:

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

This is not a runtime MissionScript execution proof, runtime command-effect proof, runtime slot-persistence proof, runtime save/load proof, tutorial progression proof, Level500 branch proof, Fenrir state proof, live loose-MSL loading proof, packed-resource script-selection proof, private-frame review, row observation, BEA launch, screenshot or frame capture, OCR pass, raw dialogue publication, source-selection proof, native-input run, debugger attachment, Godot project, Ghidra mutation, executable patch, rebuild implementation, rebuild parity proof, or no-noticeable-difference parity proof.

## Static Closeout Context

| Track | Current |
| --- | --- |
| Static Ghidra function-quality closure | `6411/6411 = 100.00%` |
| Commentless / exact-undefined / `param_N` debt | `0 / 0 / 0` |
| Expanded post-100 static surface | `1560/1560 = 100.00%` |
| Active current-risk focused accounting | `1179/1179 = 100.00%` |
| Remaining active focused work | `0` |
| Latest verified Ghidra backup | `latestGhidraBackupClass=verified-static-backup-redacted` |

This fixture selection does not change `static-reaudit-progress.json`, `static-reaudit-current-risk-ledger.json`, or the current percentages.

## Selected Fixture Path

The selected first fixture family is `slot-bitset-save`, specifically `slot-bitset-save-core-handler-and-career-bridge`.

| Surface | Selected static evidence |
| --- | --- |
| Descriptor rows | `SetSlot` descriptor index `122`, `GetSlot` descriptor index `123`, and `SetSlotSave` descriptor index `132`. |
| IScript handlers | `0x005338d0 IScript__SetSlot`, `0x00533900 IScript__SetSlotSave`, and `0x005339a0 IScript__GetSlotBitValue`. |
| Runtime helpers | `0x0046d3a0 CGame__SetSlot` and `0x0046d410 CGame__GetSlot`, using `slot>>5` and `1<<(slot&31)` against `CGame+0x308`. |
| Persistent bridge | `0x004214e0 CCareer__SetSlot` is called by `IScript__SetSlotSave`; the copied-file save schema anchors `mSlots[0]` at true-view file offset `0x240A`. |
| Public loose-MSL corpus | `6` slot-using level rows and `18` detailed call rows: `6 GetSlot`, `8 SetSlot`, and `4 SetSlotSave` calls across `level100`, `level500`, `level731`, `level732`, `level741`, and `level742`. |
| Deterministic numeric fixture seeds | `SetSlot(61)` and `SetSlot(62)` provide public numeric slot seeds; slot `61` maps to dword index `1`, bit index `29`, mask `0x20000000`, and true-view slot dword offset `0x240E`, while slot `62` maps to dword index `1`, bit index `30`, mask `0x40000000`, and true-view slot dword offset `0x240E`. Symbolic `SLOT_TUTORIAL_1..4`, `n`, and `n + 29` remain corpus vocabulary until a later proof resolves them safely. |

The future fixture proof should begin with the bitset math and copied-file true-view slot codec. It should not start with live mission execution.

## Candidate Ranking

| Rank | Candidate fixture family | Decision | Rationale |
| ---: | --- | --- | --- |
| `1` | `slot-bitset-save` | selected | Best safety/value balance: finite descriptor set, exact handler/helper anchors, bounded `0..255` bitset math, public numeric corpus seeds, and a compatible copied-file byte-preservation lane. |
| `2` | `vector-range-helpers` | deferred | Good pure-helper candidate, but less directly connected to persistent state and has several descriptor-index placeholder tokens that are less readable as a first user-facing fixture. |
| `3` | `cutscene-camera-position` | deferred | Useful for rebuild planning, but quickly tempts runtime camera-switching and visual-output claims. |
| `4` | `objective-outcome` | deferred | Important, but tightly coupled to mission outcome/runtime event behavior and career progression claims. |
| `5` | `goodie-state-save` | deferred | Save-adjacent, but descriptor index `84 AddScore` overlaps the player-state/score family and should not be the first fixture. |
| `6` | `message-audio-console` | deferred | High rebuild value, but carries private-frame, text/OCR, queue-ordering, voice/audio, and runtime-display risk. |
| `7` | `hud-variable-display` | deferred | Useful UI command surface, but visual HUD behavior proof would be easy to overclaim. |
| `8` | `thing-value-engine-helper` | deferred | Effectful engine/object commands need runtime object-identity and thing-state guardrails first. |
| `9` | `player-state-score` | deferred | Attractive gameplay surface, but `AddScore` handler-body conflict, cockpit behavior, stealth behavior, and weapon-fire/stealth claims make it a poor first fixture. |

## Future Evidence Requirements

The selected child lane, `MissionScript Slot Bitset/Save Rebuild Fixture Proof Plan`, should require these rows before any runtime or rebuild implementation claim:

| Row | Requirement | Boundary |
| --- | --- | --- |
| `descriptor-fixture` | Reconfirm descriptor indices `122`, `123`, and `132` from `missionscript-command-descriptor-schema.v1.json` and `missionscript-slot-command-effect.v1.json`. | Static descriptor proof only. |
| `handler-fixture` | Preserve handler/helper anchors `0x005338d0`, `0x00533900`, `0x005339a0`, `0x0046d3a0`, `0x0046d410`, and `0x004214e0`. | Static handler bridge only. |
| `bitset-fixture` | Encode `slot>>5` and `1<<(slot&31)` for selected public numeric seeds, starting with `61` and `62`. | Pure bitset model only; not runtime `CGame` proof. |
| `copied-file-fixture` | If file bytes are exercised, use copied real save/options baselines only and write through true-view `mSlots` at `0x240A`. | Copied-file codec proof only; not runtime save/load. |
| `corpus-fixture` | Keep `level100`, `level500`, `level731`, `level732`, `level741`, and `level742` corpus rows public-safe and aggregate. | Loose corpus vocabulary only; not packed-resource selection. |
| `stop-fixture` | Stop if the proof needs live MissionScript execution, runtime mission selection, source-selection observation, screenshots, private frame review, native input, debugger attachment, Godot, Ghidra mutation, executable patching, or installed-game mutation. | Defer instead of broadening. |

## What This Proves

- The first MissionScript command-effect rebuild fixture path has been selected from the completed static interface rollup.
- `slot-bitset-save` is the safest first fixture family because it has a small descriptor set, exact static handlers/helpers, deterministic bitset math, public numeric corpus seeds, and compatible copied-file true-view guardrails.
- The future child lane has explicit evidence requirements and stop conditions before runtime, Godot, patching, or rebuild implementation begins.

## Not Claimed

This does not prove runtime MissionScript execution, runtime command effects, runtime slot persistence, runtime save/load behavior, runtime tutorial progression, Level500 branch behavior, Fenrir state behavior, live loose-MSL loading, packed-resource script selection, exact descriptor layout, exact arity, exact argument type schema, exact `CGame` layout, exact `CCareer` layout, runtime defaultoptions behavior, runtime menu behavior, source-selection observation, private-frame review, visual QA, Godot parity, executable patching behavior, rebuild implementation, rebuild parity, or no-noticeable-difference parity.
