# Active Goal Slice

Status: active
Last updated: 2026-06-29
Policy: `goal.policy.md`

## Current Slice

The projection/storage/consult integration wave has accepted two narrow tracked
changes:

- a docs-only PatchBench primitive projection contract for future
  receipt/source-summary presentation helper work
- a test-only static guard hardening for `PatchBenchLaunchPresetText` routing
  and literal reintroduction

The next executable product slice is receipt presentation boundary tests: add
focused primitive-state/helper-boundary tests that reject AppCore receipt DTOs,
raw paths, `File`/`Directory`/`Path`, service/process/launch/catalog tokens,
proof IDs, and Host/Join action strings in PatchBench presentation helpers.
Do not extract receipt display formatting until those tests exist and pass.
Do not extract source-summary helpers until path/redaction projection is
explicitly tested.

## Current Truth

- `roadmap/patchbench-primitive-projection-contract.md` is accepted as a
  design-only primitive presentation contract. It is not extraction approval,
  behavior movement, AppCore ownership movement, or runtime proof.
- Future PatchBench presentation helpers may receive only display-safe primitive
  or primitive-record values: strings, booleans, counts, small enums, nullable
  primitive fields, and sanitized display lists.
- `BinaryPatchesPage` still owns page projection, File/Path checks, service
  calls, UI assignment, operation-log text, `AppStatusService` updates, launch
  option tuples, selected-state mutation, matching logic, launch argument
  construction, safe-copy launch planning, process control, patch/catalog
  semantics, source-summary decisions, Host/Join fallback ownership, online
  claim boundaries, and runtime-proof boundaries.
- AppCore still owns receipt truth, receipt construction, patch planning,
  copied-profile safety, save/options correctness, and any core redaction or
  behavior contracts.
- `PatchBenchLaunchPresetText` owns launch/control preset automation names and
  status-message text as a presentation-only helper.
- `WinUiProductLaneTests` now includes static test-only guards against
  reintroducing canonical launch-preset status literals into
  `BinaryPatchesPage` and against drifting the expected launch-preset
  button-to-helper visual bindings.
- The launch-preset hardening is static presentation-boundary test coverage.
  It is not runtime/UIA proof and does not change launch argument construction,
  selected-state logic, safe-copy planning, process control, AppCore behavior,
  user-visible product behavior, Host/Join availability, online readiness,
  runtime proof, release readiness, or publication posture.
- Storage taxonomy remains read-only/no-delete. High-confidence deletion
  candidates are 0, deletion performed is false, and authorized reclaimed
  storage is 0 GiB.
- Future medium/low storage values are non-authorized logical review ceilings
  only. They are not reclaimable storage, not unique physical-size estimates,
  and not deletion budgets.
- Runtime proof remains private pre-arm readiness only. No live execution, BEA
  launch, CDB attach, audio capture, proof archive write, copied executable
  mutation, Ghidra mutation/read-back, installed-game mutation, original
  `BEA.exe` mutation, runtime audible-output proof, all-cue proof, release
  readiness, gameplay proof, rebuild proof, or parity proof is claimed.
- Public runtime flags remain `readyToRunLiveAttempt=false`,
  `liveArmAllowed=false`, `runtimeAudibleOutputProof=false`, and
  `preArmReadiness.status=prearm-readiness-not-proven`.
- Early consult-evidence smoke ran before terminal worker reports existed and
  is superseded by the integration audit of terminal worker/reviewer reports.
  Accepted non-trivial reports for this wave include the required six-lane
  Codex/Cursor normal and adversarial consult matrix.
- Recovery and superseded outputs are not accepted canonical evidence. The
  canonical projection design is the reviewed roadmap note integrated here; the
  late duplicate projection recovery output is rejected as duplicate evidence.
  The launch-preset recovery lane is superseded with no accepted output.
- Online multiplayer remains not player-ready. Host/Join stays disabled or
  unavailable until distinct-endpoint command-source proof and source-bound
  copied-runtime causality proof are both accepted.
- Static RE closure is not runtime, gameplay, visual, online, rebuild, or
  no-noticeable-difference proof.
- Hard payloads remain outside git and release ZIPs: game executables, copied
  executables, copied runtime output, arbitrary saves/options, raw proof logs,
  screenshots or frame dumps, full Ghidra databases, secrets, `.env*`, local
  runtime caches, build output, and package output.
- Installed game files and original `BEA.exe` remain read-only.
- No release, tag, package, signing, installer, announcement, hosted workflow,
  or publication action is part of this integration.

## Evidence Pointers

- Primitive projection contract:
  `roadmap/patchbench-primitive-projection-contract.md`
- Roadmap index:
  `roadmap/ROADMAP-INDEX.md`
- Launch/control preset presentation helper:
  `OnslaughtCareerEditor.WinUI/Helpers/PatchBenchLaunchPresetText.cs`
- Launch/control preset helper-output tests:
  `OnslaughtCareerEditor.UiTests/PatchBenchLaunchPresetTextTests.cs`
- PatchBench static product-lane guards:
  `OnslaughtCareerEditor.UiTests/WinUiProductLaneTests.cs`
- PatchBench page orchestration:
  `OnslaughtCareerEditor.WinUI/Pages/BinaryPatchesPage.xaml.cs`
- Runtime pre-arm readiness note:
  `release/readiness/winui_music_live_bundle_prearm_readiness_2026-06-29.md`
- Storage hygiene boundary:
  `LOCAL_LAB_OVERLAY.md`
- Coordination contracts:
  `coordination/README.md`, `coordination/WORKSTREAM_CONTRACT.md`,
  `coordination/REPORT_CONTRACT.md`, and `coordination/RESOURCE_LEASES.md`
- Canonical state batons:
  `developer_agent_state.json`, `documentation_agent_state.json`, and
  `re_orchestrator_state.json`

## Next Executable Work

1. For PatchBench modularity, add the boundary tests required by the primitive
   projection contract before extracting any receipt display helper. These
   tests should reject AppCore receipt DTOs, raw paths,
   `File`/`Directory`/`Path`, service/process/launch/catalog tokens, proof IDs,
   and Host/Join action strings in PatchBench presentation helpers.
2. Keep receipt construction, File/Path/I/O, launch planning, process control,
   catalog semantics, Host/Join fallback, and online/runtime proof boundaries
   out of presentation helpers.
3. For storage, do only read-only manifest/hash/reference work until a future
   task records explicit deletion authority, candidate-specific retained
   alternatives, dry-run evidence, consults, rollback/quarantine plan, and
   independent acceptance.
4. For runtime music proof, the only safe next baton is private pre-arm
   readiness under separate explicit authority. Do not issue a live arm phrase
   or run BEA/CDB/audio/live proof from this public baton.

## Stop Conditions

- Any step would mutate the installed game folder or original `BEA.exe`.
- Any tracked file would add hard payloads, raw proof logs, screenshots/frame
  dumps, copied executable output, full Ghidra databases, secrets, `.env*`,
  build output, package output, local runtime caches, raw local proof paths, raw
  manifests, thread IDs, or local campaign/worktree paths.
- Any claim would promote online readiness, Host/Join availability, runtime
  audio proof, gameplay parity, visual parity, release readiness, release
  publication, rebuild parity, or no-noticeable-difference parity beyond
  accepted evidence.
- Storage work would move, quarantine, delete, or reclaim material without the
  required future authority and candidate-specific evidence.
- Required validation fails without a bounded explanation and correction path.
