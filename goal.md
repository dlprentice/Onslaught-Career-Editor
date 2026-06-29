# Active Goal Slice

Status: active
Last updated: 2026-06-29
Policy: `goal.policy.md`

## Current Slice

The PatchBench launch-preset presentation and consult-contract integration wave
is accepted on `main` at `04e03e92` (`Record launch preset integration state`).
Final acceptance evidence confirms the commit stack `0c9e6f8c`, `6f423ef3`,
and `04e03e92` with `origin/main` and remote `refs/heads/main` at the reviewed
commit. The accepted worker changes extract launch/control preset automation
names and status-message text into `PatchBenchLaunchPresetText` as a
presentation-only helper, and update the report contract so mandated consult
evidence is explicit and public-safe. The prior music live-bundle
fail-closed/pre-arm truth remains unchanged.

Before any later write, re-read live git truth and target files. Do not treat
local campaign reports, local worktree paths, raw manifests, or unmerged worker
commits as durable public evidence.

## Current Truth

- Music live-bundle readiness tooling is public-safe, fail-closed, and pre-arm
  only. Producer coverage can be complete, but the public gate does not
  authorize a live arm, BEA launch, CDB attach, audio capture, or runtime proof.
- The gate now reports `producerCoverageComplete=true`,
  `readyToRunLiveAttempt=false`, `liveArmAllowed=false`, and
  `runtimeAudibleOutputProof=false`, with
  `preArmReadiness.status=prearm-readiness-not-proven`.
- The armed executor requires a private accepted
  `winui-safe-copy-music-audible-output-live-bundle-prearm-readiness.v1` JSON
  through `--prearm-readiness-json` before it can call the live bundle runner.
  That artifact is a private pre-arm authority/lease/readiness contract, not a
  public proof artifact or an audible-output proof by itself.
- Read-only music follow-up adds no runtime proof. Future prompts must treat
  producer coverage as schema/producer coverage only, pre-arm permission as
  permission to attempt only, public gate root arguments as non-proof, and
  executor receipts/stdout as private artifacts.
- The top-level music live-bundle gate `status` is value-locked after
  adversarial review; proof-like status text is rejected by the gate validator.
- No runtime music proof exists from this wave. Do not claim audible output,
  gameplay behavior, source-bound runtime causality, all-cue coverage, online
  readiness, release readiness, rebuild parity, or no-noticeable-difference
  parity from this slice.
- Consult compliance is scoped: recent inspected June 29 non-trivial worker
  outputs had no clear skipped Cursor lane, but report-shape and
  sanitized-context evidence gaps mean there is no blanket campaign-wide
  compliance claim.
- Ghidra/proof storage taxonomy remains read-only/no-delete. Current
  high-confidence deletion candidate count is 0, current authorized reclaimed
  storage is 0 GiB, and no storage deletion or mutation was performed. Future
  storage work is manifest/hash/provenance review only until separately
  authorized.
- `PatchBenchLaunchPresetText` is now the compact PatchBench presentation seam
  for launch/control preset automation names and status-message text. Defer
  receipt/source-summary helpers until a primitive projection design is
  accepted.
- `coordination/REPORT_CONTRACT.md` now requires explicit `Consult Evidence`
  entries for mandated Codex specialist, Codex adversarial, `cursor-agent
  composer-2.5-fast`, and `cursor-agent gemini-3.1-pro` lanes, including
  accepted/rejected findings, unresolved dissent, and `CONSULT_UNAVAILABLE`
  reasons without raw prompt, raw log, local path, active campaign ID, secret,
  private proof artifact, or full local report leakage into tracked docs.
- `PatchBenchSafeCopyOutcomeText` owns the safe-copy music replacement status
  messages used for default, not-ready, progress, staged, restore, and failure
  states. The helper remains presentation-only and accepts primitive string/bool
  state for the moved status copy.
- `PatchBenchLaunchPresetText` owns the launch/control preset automation names
  and status-message text. The helper remains presentation-only and returns
  primitive strings plus `PatchBenchSelectedChoiceState`.
- `BinaryPatchesPage` still owns service calls, orchestration, UI control
  assignment, operation-log text, `AppStatusService` status updates, launch
  option tuples, selected-state mutation, matching logic, launch argument
  construction, safe-copy launch planning, and process control. The music and
  launch-preset status-line assignments now route through presentation helpers
  without changing AppCore behavior, patch catalogs, byte data, launch behavior,
  safe-copy manifests/signatures, or process control.
- `PatchBenchSafeCopyOutcomeTextTests` and `PatchBenchLaunchPresetTextTests`
  assert exact reflected helper output for the moved presentation states.
  `WinUiProductLaneTests` guards page routing, helper boundaries, and the
  absence of the previous inline status literals.
- The previous PatchBench online-readiness routing guard remains in force:
  `BinaryPatchesPage` collects service state before calling
  `PatchBenchOnlineReadinessText.Build` and `BuildCompanionSession`, maps text
  state to expected controls, and avoids inline literal assignments in those
  render paths.
- PatchBench button labels and click handlers remain guarded against premature
  Host/Join, matchmaking, online-ready, netplay, or online-action wording while
  technical boundary text remains allowed.
- Storage-retention inventory was partial-bounded and metadata-only. It is not
  deletion authorization.
- Ghidra backup retention deleted 0 files. All reviewed Ghidra backup/live/
  unknown rows were retained because the pool lacked safe family/supersession
  proof and no deletion approval was recorded.
- Proof archive retention deleted 0 files. All reviewed proof-related rows were
  retained because the pool was partial-bounded, metadata-only, and not proven
  stale, duplicate, superseded, or independent of current claims.
- Stale local Git administrative worktree metadata cleanup pruned 23 stale
  metadata records after dry-run evidence. No branch refs, remote refs, physical
  directories, tracked source, final reports, proof/Ghidra/game/release material,
  hard payloads, or secrets were deleted.
- No tracked storage policy edit was needed. Existing `LOCAL_LAB_OVERLAY.md` and
  coordination policy already state that campaign scratch is disposable only
  after final reports and durable findings are preserved, scratch volumes are
  not durable sole storage, and Ghidra/proof pruning requires manifest
  classification plus retained replacement or summary evidence.
- Fresh storage inventory free-space readings for this wave were C: 239.393 GiB,
  D: 398.235 GiB, F: 119.241 GiB, G: 90.251 GiB, and H: 215.842 GiB. No Ghidra
  or proof archive storage reclamation is claimed.
- Future private live execution must stop unless explicit authority, exclusive
  leases, an empty isolated proof root, no preexisting BEA/CDB processes, and
  capture-span/flush/decode-window readiness are proven in the private pre-arm
  artifact and checked by the executor path.
- Online multiplayer is still not player-ready. Host/Join remains disabled
  until distinct-endpoint command-source proof and source-bound copied-runtime
  causality proof are both accepted.
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

- Music live-bundle pre-arm readiness note:
  `release/readiness/winui_music_live_bundle_prearm_readiness_2026-06-29.md`
- Music live-bundle public gate and tests:
  `tools/winui_safe_copy_music_audible_output_live_bundle_gate.py` and
  `tools/winui_safe_copy_music_audible_output_live_bundle_gate_test.py`
- Music live-bundle executor and tests:
  `tools/run_winui_safe_copy_music_audible_output_live_bundle.py` and
  `tools/run_winui_safe_copy_music_audible_output_live_bundle_test.py`
- Safe-copy music status helper:
  `OnslaughtCareerEditor.WinUI/Helpers/PatchBenchSafeCopyOutcomeText.cs`
- Safe-copy music status helper-output tests:
  `OnslaughtCareerEditor.UiTests/PatchBenchSafeCopyOutcomeTextTests.cs`
- Launch/control preset presentation helper:
  `OnslaughtCareerEditor.WinUI/Helpers/PatchBenchLaunchPresetText.cs`
- Launch/control preset helper-output tests:
  `OnslaughtCareerEditor.UiTests/PatchBenchLaunchPresetTextTests.cs`
- PatchBench page routing/static guard tests:
  `OnslaughtCareerEditor.UiTests/WinUiProductLaneTests.cs`
- PatchBench page orchestration:
  `OnslaughtCareerEditor.WinUI/Pages/BinaryPatchesPage.xaml.cs`
- Online-readiness routing guard tests:
  `OnslaughtCareerEditor.UiTests/PatchBenchOnlineReadinessRoutingGuardTests.cs`
- Shared reflected WinUI test support:
  `OnslaughtCareerEditor.UiTests/ReflectedWinUiTestSupport.cs`
- DTO helper-output tests:
  `OnslaughtCareerEditor.UiTests/PatchBenchOnlineReadinessTextTests.cs`
- PatchBench online-readiness helper:
  `OnslaughtCareerEditor.WinUI/Helpers/PatchBenchOnlineReadinessText.cs`
- Storage hygiene boundary:
  `LOCAL_LAB_OVERLAY.md`
- Rebuild front-door chain map:
  `roadmap/rebuild-front-door-chain-map.md`
- Static-to-proof queue:
  `roadmap/static-to-proof-rebuild-transition-backlog.md`
- Coordination contracts:
  `coordination/README.md`, `coordination/WORKSTREAM_CONTRACT.md`,
  `coordination/REPORT_CONTRACT.md`, and `coordination/RESOURCE_LEASES.md`
- Product and contributor boundaries:
  `AGENTS.md`, `CONTRIBUTING.md`, `SECURITY.md`, `COLLABORATION.md`, and
  `LOCAL_LAB_OVERLAY.md`
- Canonical state batons:
  `developer_agent_state.json`, `documentation_agent_state.json`, and
  `re_orchestrator_state.json`

## Next Executable Work

1. Verify live `HEAD`, `origin/main`, and remote `refs/heads/main`, then inspect
   `BinaryPatchesPage`, existing `PatchBench*Text` helpers, and focused WinUI
   tests before editing.
2. If future launch-preset work touches this surface, optionally harden
   page-routing or literal-reintroduction tests around
   `PatchBenchLaunchPresetText`.
3. Keep all launch option tuples, selection state, matching logic, launch
   argument construction, safe-copy launch planning, service calls, process
   control, patch/catalog semantics, Host/Join/online claims, and runtime proof
   boundaries in `BinaryPatchesPage`.
4. Design a primitive projection contract before safe-copy receipt/source-summary
   helper extraction; do not move behavior or AppCore receipt construction into
   a presentation helper.
5. Treat Ghidra/proof taxonomy, proof manifest/hash comparison, branch cleanup,
   and physical scratch cleanup as separate local-maintenance work requiring
   explicit authority, dry-run evidence, and no-delete/default-retain review.

## Stop Conditions

- Any step would mutate the installed game folder or original `BEA.exe`.
- Any tracked file would add hard payloads, raw proof logs, screenshots/frame
  dumps, copied executable output, full Ghidra databases, secrets, `.env*`,
  build output, package output, local runtime caches, raw local proof paths, or
  raw manifests.
- Any claim would promote online readiness, Host/Join availability, runtime
  audio proof, gameplay parity, visual parity, release readiness, release
  publication, rebuild parity, or no-noticeable-difference parity beyond
  evidence.
- Ownership or resource leasing is unclear for a planned write.
- Required validation fails without a bounded explanation and correction path.
