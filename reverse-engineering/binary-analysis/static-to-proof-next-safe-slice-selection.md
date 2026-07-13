# Static-To-Proof Next Safe Slice Selection Proof Plan

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 semantic revalidation:** `0x0050b9c0` signature/comment correction. Older conflicting text below is superseded for these rows. Use the [closeout](ghidra-full-reaudit-closeout-2026-07-13.md); exact records are in `reverse-engineering/binary-analysis/ghidra-full-reaudit-corrections-2026-07-13.json` and `reverse-engineering/binary-analysis/ghidra-targeted-revalidation-corrections-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Status: complete next safe slice selection, not runtime proof
Last updated: 2026-06-09
Scope: `static-to-proof-next-safe-slice-selection`

This result closes the active Static-To-Proof Rebuild Transition Next Safe Slice Selection Proof Plan after the MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Runtime Message Display Observation Public-Safe Result Summary Proof Plan deferred private-frame review pending an explicit operator arm.

Machine-checkable artifact:

- [static-to-proof-next-safe-slice-selection.v1.json](static-to-proof-next-safe-slice-selection.v1.json)

Selection tokens:

- `selectionStatus=static-to-proof-next-safe-slice-selection-complete-world-thing-spawn-rebuild-contract-crosswalk-selected`
- `selectedChildLane=World / Thing / Spawn Static-To-Rebuild Contract Crosswalk Proof Plan`
- `selectedChildScope=world-thing-spawn-static-to-rebuild-contract-crosswalk`

Guard tokens:

- `runtimeExecution=false`
- `beLaunch=false`
- `screenshotCapture=false`
- `privateFrameReviewPerformed=false`
- `sourceSelectionObserved=false`
- `nativeInput=false`
- `debuggerAttachment=false`
- `godotWork=false`
- `ghidraMutation=false`
- `rebuildImplementation=false`
- `rebuildParityProven=false`
- `noNoticeableDifferenceParityProven=false`
- `missionScriptRuntimeEvidenceRows=0`
- `runtimeObservationRows=0`
- `beProcessesAfterSelection=0`

This is not a runtime proof wave, private-frame review, row observation, BEA launch, screenshot or frame capture, OCR pass, raw dialogue publication, source-selection proof, native-input run, debugger attachment, Godot project, Ghidra mutation, executable patch, rebuild implementation, rebuild parity proof, or no-noticeable-difference parity proof.

## Static Closeout Context

| Track | Current |
| --- | --- |
| Static Ghidra function-quality closure | `6411/6411 = 100.00%` |
| Commentless / exact-undefined / `param_N` debt | `0 / 0 / 0` |
| Expanded post-100 static surface | `1560/1560 = 100.00%` |
| Active current-risk focused accounting | `1179/1179 = 100.00%` |
| Remaining active focused work | `0` |
| Latest verified Ghidra backup | `latestGhidraBackupClass=verified-static-backup-redacted` |

This selection does not change `static-reaudit-progress.json`, `static-reaudit-current-risk-ledger.json`, or the current percentages.

## Parent Blocker

The completed [Level100 message public-safe result summary](level100-message-public-safe-result-summary.md) remains a deferred state summary only:

- `directLevel100RuntimeMessageDisplayObservationPublicSafeResultSummaryStatus=direct-level100-runtime-message-display-observation-public-safe-result-summary-complete-private-frame-review-deferred`
- `publicSummaryOnly=true`
- `sourceChecklistRowsMaterialized=9`
- `sourceNotRunRows=9`
- `sourceUnobservedRows=9`
- `sourceObservedRows=0`
- `sourceRuntimeObservationRows=0`
- `sourceRowStatusChangedCount=0`
- `privateFrameReviewDeferred=true`
- `blockedByMissingExplicitOperatorArm=true`
- `futureReviewRequiresExplicitOperatorArm=true`
- `runtimeMessageDisplayProven=false`
- `sourceSelectionProven=false`

Because there is no explicit operator arm for private-frame review, this selection intentionally leaves the Level100 observation chain parked and chooses a non-private static child lane.

## Candidate Ranking

| Rank | Candidate lane | Decision | Rationale |
| ---: | --- | --- | --- |
| `1` | `World / Thing / Spawn Static-To-Rebuild Contract Crosswalk Proof Plan` | selected | Best safety/value balance: existing copied-corpus, spawner handoff, and GetThingRef proofs can be consolidated into an implementation-facing object/spawn contract without BEA launch, private frames, OCR, Ghidra mutation, or Godot work. |
| `2` | `MissionScript Command-Effect Rebuild Interface Rollup Proof Plan` | deferred | High rebuild value, but broader and more coupled to command-effect families; better after the object/spawn crosswalk makes the world handoff concrete. |
| `3` | `Save / Options Byte-Preservation Implementation Contract Proof Plan` | deferred | Very safe and useful for AppCore, but less connected to the currently blocked Level100 object/spawn/message path. |
| `4` | `PhysicsScript Parser/Rebuild Contract Extension Proof Plan` | deferred | Useful static parser work, but lower priority than consolidating object-reference and spawn handoff contracts already selected from MissionScript. |

Consult accounting:

- `consultCount=2`
- `candidateCount=4`
- `selectedCandidateRank=1`
- `selectedSourceProofCount=3`
- `selectionFalseGuardCount=19`
- `selectionZeroCounterCount=12`
- `publicLeakCheck=PASS`

## Selected Source Evidence

The selected child lane is grounded in three completed public-safe source proof families:

| Source proof | Key evidence |
| --- | --- |
| [World / Thing / Spawn Copied-Corpus Schema Proof](world-thing-spawn-copied-corpus-schema-proof.md) | `574` raw `GetThingRef` rows, `70` raw `SpawnThing` rows, `644` total raw rows, `418` unique `GetThingRef` object-reference rows, `18` unique `SpawnThing` object-reference rows, `436` unique total rows, `447` spawn-preserving unique rows, selected `training-target-spawn-family` with `34` raw `SpawnThing` rows. |
| [World / Thing / Spawn Spawner Handoff Static Proof](world-thing-spawn-spawner-handoff-static-proof.md) | `8` static handoff layers, selected `training-target-spawn-family`, `DAT_008553f4`, `0x0050f970 CWorldPhysicsManager__CreateSpawner`, `0x004e3c60 CSpawnerThng__DoSpawn`, and `12` static field-role labels. |
| [World / Thing / Spawn GetThingRef Object-Reference Static Proof](world-thing-spawn-getthingref-object-reference-static-proof.md) | Selected `training-target-zone-getthingref-family` with `9` raw `GetThingRef` rows, `8` unique object-reference rows, `1` duplicate call row, `9` empty-spawner rows, and `4` static linkage layers. |

The selected crosswalk should preserve these anchors: `mission-thing-usage.md`, `world-thing-spawn-copied-corpus-schema.v1.json`, `world-thing-spawn-spawner-handoff-static.v1.json`, `world-thing-spawn-getthingref-object-reference-static.v1.json`, `IScript__SpawnThing`, `IScript__GetThingRef`, `CThingPtrDataType`, `ScriptCommandRegistry__InitBuiltins`, `0x005392a0 CScriptObjectCode__CollectSpawnThings`, opcode `0x18`, `CWorldMeshList__Add`, `0x0050b9c0 CWorld__LoadWorld`, `0x0050dcb0 CWorld__SpawnInitialThings`, `0x0050df80 CWorldPhysicsManager__CreateThingByType`, `0x0048c650 InitThing__CreateThingByType`, `CThing__InitRenderThingFromInitMeshName`, `0x004e3c60 CSpawnerThng__DoSpawn`, `0x00511440 CWorldPhysicsManager__IsSpawnerThingTypeAllowedByName`, `CUnit__VFunc08_InitAndAddToWorld`, `CWorld__AddUnitToOccupancyGridAndRebuildShadows_Thunk`, and `0x004fc3a0 CUnit__SetSpawnCooldownState3`.

## Stop Conditions

The selected child lane must stop or defer if it needs any of the following:

- BEA launch or process observation.
- Screenshot/frame capture or private-frame review.
- OCR, exact visible text identity, raw dialogue publication, per-frame token identity, or per-frame speaker identity.
- Runtime MissionScript execution or Level100 source-selection observation.
- Native input, debugger attachment, executable patching, Godot project work, or Ghidra mutation.
- Runtime object identity, runtime `SpawnThing`, runtime `GetThingRef`, runtime world loading, runtime spawner behavior, live loose-MSL loading, packed-resource script selection, exact layouts, rebuild implementation, rebuild parity, or no-noticeable-difference parity.

## What This Proves

- The active next safe slice selection completed without continuing the blocked Level100 private-frame observation path.
- The selected next child lane is a static, public-safe, implementation-facing World / Thing / Spawn crosswalk.
- The selected lane has enough existing public-safe source proofs to start a rebuild-facing contract without runtime or private proof.

## Not Claimed

This does not prove runtime object identity, runtime `SpawnThing`, runtime `GetThingRef`, runtime MissionScript execution, runtime world loading, runtime spawner behavior, live loose-MSL loading, packed-resource script selection, exact descriptor/VM/object-code/world/thing/spawner/Unit layouts, source-selection observation, runtime message display, visual QA, executable patching behavior, Godot parity, rebuild parity, or no-noticeable-difference parity.
