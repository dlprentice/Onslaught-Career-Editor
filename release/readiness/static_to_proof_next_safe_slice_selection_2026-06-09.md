# Static-To-Proof Next Safe Slice Selection Readiness Note

Status: complete next safe slice selection, not runtime proof
Date: 2026-06-09
Scope: `static-to-proof-next-safe-slice-selection`
Completed slice token: `Static-To-Proof Rebuild Transition Next Safe Slice Selection Proof Plan`
Parent slice token: `MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Runtime Message Display Observation Public-Safe Result Summary Proof Plan`
Selected child lane: `World / Thing / Spawn Static-To-Rebuild Contract Crosswalk Proof Plan`

This slice selects a public-safe static child lane after the Level100 public-safe result summary deferred private-frame review pending an explicit operator arm. It performs no private-frame review, no row observation, no BEA launch, no screenshot or frame capture, no OCR, no raw dialogue handling, no source-selection proof, no native input, no debugger work, no Godot work, no Ghidra mutation, no executable patching, and no rebuild/no-noticeable-difference proof.

Machine-checkable evidence:

- Public proof: `reverse-engineering/binary-analysis/static-to-proof-next-safe-slice-selection.md`
- Schema: `reverse-engineering/binary-analysis/static-to-proof-next-safe-slice-selection.v1.json`
- Focused probe: `tools/static_to_proof_next_safe_slice_selection_probe.py`
- Selected source proof: `reverse-engineering/binary-analysis/world-thing-spawn-copied-corpus-schema-proof.md`
- Selected source proof: `reverse-engineering/binary-analysis/world-thing-spawn-spawner-handoff-static-proof.md`
- Selected source proof: `reverse-engineering/binary-analysis/world-thing-spawn-getthingref-object-reference-static-proof.md`

Representative tokens:

- `selectionStatus=static-to-proof-next-safe-slice-selection-complete-world-thing-spawn-rebuild-contract-crosswalk-selected`
- `selectedChildLane=World / Thing / Spawn Static-To-Rebuild Contract Crosswalk Proof Plan`
- `selectedChildScope=world-thing-spawn-static-to-rebuild-contract-crosswalk`
- `consultCount=2`
- `candidateCount=4`
- `selectedCandidateRank=1`
- `selectedSourceProofCount=3`
- `selectionFalseGuardCount=19`
- `selectionZeroCounterCount=12`
- `publicLeakCheck=PASS`
- `privateFrameReviewDeferred=true`
- `blockedByMissingExplicitOperatorArm=true`
- `futureReviewRequiresExplicitOperatorArm=true`
- `sourceObservedRows=0`
- `sourceRuntimeObservationRows=0`
- `sourceRowStatusChangedCount=0`
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
- `latestGhidraBackupClass=verified-static-backup-redacted`

Selected source evidence:

- Copied-corpus schema: `574` raw `GetThingRef`, `70` raw `SpawnThing`, `644` total raw rows, `436` unique object-reference rows, `447` spawn-preserving rows, and selected `training-target-spawn-family` with `34` raw `SpawnThing` rows.
- Spawner handoff: `8` static handoff layers, `12` field-role labels, `DAT_008553f4`, `0x0050f970 CWorldPhysicsManager__CreateSpawner`, `0x004e3c60 CSpawnerThng__DoSpawn`, `CUnit__VFunc08_InitAndAddToWorld`, and `0x004fc3a0 CUnit__SetSpawnCooldownState3`.
- GetThingRef object-reference: selected `training-target-zone-getthingref-family`, `9` raw `GetThingRef` rows, `8` unique object-reference rows, `1` duplicate call row, `9` empty-spawner rows, and `4` linkage layers.

What this proves:

- The active next safe slice selection completed without continuing the blocked Level100 private-frame observation path.
- The selected next child lane is a static, public-safe, implementation-facing World / Thing / Spawn crosswalk.
- The selected lane has enough existing public-safe source proofs to start a rebuild-facing contract without runtime or private proof.

What remains unproven:

- Runtime object identity.
- Runtime `SpawnThing` and `GetThingRef`.
- Runtime MissionScript execution, runtime world loading, runtime spawner behavior, live loose-MSL loading, and packed-resource script selection.
- Exact descriptor/VM/object-code/world/thing/spawner/Unit layouts.
- Source-selection observation, runtime message display, visual QA, executable patching behavior, Godot parity, rebuild parity, and no-noticeable-difference parity.

Latest verified Ghidra backup remains Wave1219: `latestGhidraBackupClass=verified-static-backup-redacted`. This slice performs no Ghidra mutation and requires no new Ghidra backup.
