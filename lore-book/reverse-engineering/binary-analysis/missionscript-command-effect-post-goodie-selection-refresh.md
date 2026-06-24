# MissionScript Command-Effect Post-Goodie Selection Refresh Proof Plan

Status: complete post-Goodie command-effect selection refresh, not runtime proof
Last updated: 2026-06-09
Scope: `missionscript-command-effect-post-goodie-selection-refresh`

This result closes the stale post-Goodie routing loop after the completed MissionScript Goodie State / Save AppCore Copied-Baseline Boundary Corpus Harness Proof. The prior selected vector/range helper fixture and the Goodie/save chain are both complete, so this refresh selects the next unfinished non-runtime MissionScript command-effect fixture family from the original ranking.

Machine-checkable artifact:

- [missionscript-command-effect-post-goodie-selection-refresh.v1.json](missionscript-command-effect-post-goodie-selection-refresh.v1.json)

Selection tokens:

- `selectionRefreshStatus=missionscript-command-effect-post-goodie-selection-refresh-complete-cutscene-camera-position-selected`
- `previousSlice=MissionScript Goodie State / Save AppCore Copied-Baseline Boundary Corpus Harness Proof`
- `selectedChildLane=MissionScript Cutscene Pan-Camera / Position Command-Effect Deterministic Fixture Proof Plan`
- `selectedChildScope=missionscript-cutscene-pan-camera-position-deterministic-fixture-proof-plan`
- `completedFamilyCount=3`
- `remainingFamilyCount=6`
- `selectedOriginalRank=3`
- `selectedRemainingRank=1`
- `completedFamilies=slot-bitset-save,vector-range-helpers,goodie-state-save`
- `remainingFamilies=cutscene-camera-position,objective-outcome,message-audio-console,hud-variable-display,thing-value-engine-helper,player-state-score`
- `selectionFalseGuardCount=31`
- `selectionZeroCounterCount=18`
- `publicLeakCheck=PASS`

Guard tokens:

- `runtimeExecution=false`
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
- `productUiWired=false`
- `rebuildImplementation=false`
- `runtimeMissionScriptExecutionProven=false`
- `runtimeCommandEffectsProven=false`
- `runtimeCameraSwitchingProven=false`
- `runtimeCutscenePlaybackProven=false`
- `runtimeVisibleCameraOutputProven=false`
- `runtimeObjectIdentityProven=false`
- `runtimeObjectLookupByNameProven=false`
- `liveLooseMslLoading=false`
- `packedResourceScriptSelectionProven=false`
- `exactCommandDescriptorLayoutProven=false`
- `exactCommandArityProven=false`
- `exactArgumentTypeSchemaProven=false`
- `exactCPositionDataTypeLayoutProven=false`
- `exactCPanCameraLayoutProven=false`
- `exactCBSplineLayoutProven=false`
- `rebuildParityProven=false`
- `noNoticeableDifferenceParityProven=false`
- `runtimeObservationRows=0`
- `missionScriptRuntimeEvidenceRows=0`
- `runtimeCommandEffectRows=0`
- `runtimeCameraRows=0`
- `privateFrameRowsObserved=0`
- `beProcessesAfterSelection=0`

This is not a runtime proof wave, camera playback proof, visual QA wave, BEA launch, screenshot/frame capture, private-frame review, source-selection proof, native-input run, debugger attachment, Godot project, Ghidra mutation, executable patch, product UI wiring, rebuild implementation, rebuild parity proof, or no-noticeable-difference parity proof.

## Static Closeout Context

| Track | Current |
| --- | --- |
| Static Ghidra function-quality closure | `6411/6411 = 100.00%` |
| Commentless / exact-undefined / `param_N` debt | `0 / 0 / 0` |
| Expanded post-100 static surface | `1560/1560 = 100.00%` |
| Active current-risk focused accounting | `1179/1179 = 100.00%` |
| Remaining active focused work | `0` |
| Latest verified Ghidra backup | `latestGhidraBackupClass=verified-static-backup-redacted` |

This refresh does not change `static-reaudit-progress.json`, `static-reaudit-current-risk-ledger.json`, the Ghidra database, executable bytes, copied profiles, private artifacts, or the current percentages.

## Completed Chain Accounting

The completed chains are now accounted as complete rather than reselected:

| Family | Terminal proof |
| --- | --- |
| `slot-bitset-save` | [MissionScript Slot Bitset/Save AppCore Copied-Baseline Boundary Corpus Harness Proof](missionscript-slot-bitset-save-appcore-copied-baseline-boundary-corpus-harness-proof.md) |
| `vector-range-helpers` | [MissionScript Vector/Range Command-Effect Deterministic Helper Fixture Proof Plan](missionscript-vector-range-deterministic-helper-fixture-proof-plan.md) |
| `goodie-state-save` | [MissionScript Goodie State / Save AppCore Copied-Baseline Boundary Corpus Harness Proof](missionscript-goodie-state-save-appcore-copied-baseline-boundary-corpus-harness-proof.md) |

Re-selecting any of those three families would be accounting churn unless a later slice identifies a concrete missing static contract or a separately armed runtime/proof boundary.

## Candidate Ranking

| Remaining rank | Original rank | Candidate family | Decision | Rationale |
| ---: | ---: | --- | --- | --- |
| `1` | `3` | `cutscene-camera-position` | selected | Next highest original MissionScript fixture family not already completed. It has static descriptor, datatype, handler, and public corpus anchors, and can be kept as deterministic fixture planning without runtime camera switching or visual output claims. |
| `2` | `4` | `objective-outcome` | deferred | Important, but more tightly coupled to mission outcome/runtime event behavior and career progression claims. |
| `3` | `6` | `message-audio-console` | deferred | High rebuild value, but carries private-frame, text/OCR, voice/audio, queue-ordering, and runtime-display risk. |
| `4` | `7` | `hud-variable-display` | deferred | Useful UI command surface, but visible HUD behavior proof would be easy to overclaim. |
| `5` | `8` | `thing-value-engine-helper` | deferred | Effectful object commands need runtime object-identity and thing-state guardrails before implementation-facing proofs. |
| `6` | `9` | `player-state-score` | deferred | `AddScore` handler-body conflict plus cockpit, stealth, and weapon-fire/stealth risks keep it behind safer static fixture work. |

## Selected Source Evidence

| Source proof | Key evidence |
| --- | --- |
| [MissionScript Command-Effect Rebuild Fixture Selection Proof Plan](missionscript-command-effect-fixture-selection.md) | Original candidate family ranking: slot/save rank `1`, vector/range rank `2`, cutscene-camera-position rank `3`, then objective/outcome, Goodie/save, message/audio, HUD/display, thing-value, and player-state/score. |
| [MissionScript Vector/Range Command-Effect Deterministic Helper Fixture Proof Plan](missionscript-vector-range-deterministic-helper-fixture-proof-plan.md) | Completed pure helper fixture proof for vector length, component extraction, and range checks; no runtime proof. |
| [MissionScript Goodie State / Save AppCore Copied-Baseline Boundary Corpus Harness Proof](missionscript-goodie-state-save-appcore-copied-baseline-boundary-corpus-harness-proof.md) | Completed copied-real-baseline AppCore Goodie boundary corpus proof; no runtime proof. |
| [MissionScript Cutscene Pan-Camera / Position Command-Effect Static Proof](missionscript-cutscene-pan-camera-position-command-effect-static-proof.md) | Static descriptor slots `CreatePosition`, `Goto3PointPanCamera`, `Goto4PointPanCamera`, and `GotoPlayerCamera`; `CPositionDataType` type id `6`; Wave580 pan-camera handlers; and public Fenrir cutscene corpus anchors. |

## Selected Child Requirements

The selected child lane should build only a deterministic, public-safe fixture plan from the existing static cutscene-camera proof. It should preserve these anchors:

| Anchor | Requirement |
| --- | --- |
| Descriptor rows | Preserve `CreatePosition` index `65` / `0x0064de90`, `Goto3PointPanCamera` index `113` / `0x0064ea90`, `Goto4PointPanCamera` index `114` / `0x0064ead0`, and `GotoPlayerCamera` index `115` / `0x0064eb10`. |
| Position datatype | Preserve `CPositionDataType`, type id `6`, vtable `0x005e4da4`, size `20`, float payload reads `+0x04/+0x08/+0x0c`, value getter `+0x44`, and the open `+0x10` boundary. |
| Handler bridge | Preserve `0x00533b70 IScript__Create3PointPanCamera`, `0x00533eb0 IScript__Create4PointPanCamera`, target thing getter slot `+0x40`, duration getter `+0x34`, `CBSpline`, `CPanCamera`, and `CGame__SetCurrentCamera` as static context. |
| Public corpus | Preserve the Fenrir cutscene example and the selected `level741`/`level742` cutscene rows as corpus anchors only. |

`Goto4PointPanCamera` and `GotoPlayerCamera` raw descriptor rows as context rows remain in the selected child lane. Do not treat their raw entry values as clean one-to-one runtime handler proof without a later focused proof.

The child lane must stop and defer if it needs runtime MissionScript execution, camera switching, visual output, object identity proof, live loose-MSL loading, packed-vs-loose selection, screenshots/frames, private-output review, native input, debugger attachment, Godot, Ghidra mutation, executable patching, product UI wiring, rebuild implementation, rebuild parity, or no-noticeable-difference parity.

## Boundary

This proves only that the next active non-runtime MissionScript fixture lane has been reselected after completed-chain accounting. It does not prove runtime MissionScript execution, runtime command effects, runtime camera switching, runtime cutscene playback, visible camera output, runtime object identity, runtime object lookup by name, live loose-MSL loading, packed-resource script selection, exact descriptor layout, exact command arity, exact argument type schema, exact `CPositionDataType` layout, exact `CPanCamera` layout, exact `CBSpline` layout, BEA patching behavior, visual QA, Godot parity, rebuild implementation, rebuild parity, or no-noticeable-difference parity.
