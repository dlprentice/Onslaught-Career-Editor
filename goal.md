# Active Goal Slice

Status: active
Last updated: 2026-06-29
Policy: `goal.policy.md`

## Current Slice

The retention/PatchBench integration wave is integrated on `main`. The accepted
PatchBench presentation slice moved safe-copy music replacement status-line copy
out of `BinaryPatchesPage` and into the presentation-only
`PatchBenchSafeCopyOutcomeText` helper, with focused reflected helper-output and
static routing tests. Canonical state now records the storage-retention closeout
as no-delete for Ghidra/proof archives and local-only Git administrative
metadata pruning.

Before any later write, re-read live git truth and target files. Do not treat
local campaign reports, local worktree paths, raw manifests, or unmerged worker
commits as durable public evidence.

## Current Truth

- `PatchBenchSafeCopyOutcomeText` owns the safe-copy music replacement status
  messages used for default, not-ready, progress, staged, restore, and failure
  states. The helper remains presentation-only and accepts primitive string/bool
  state for the moved status copy.
- `BinaryPatchesPage` still owns service calls, orchestration, UI control
  assignment, operation-log text, and `AppStatusService` status updates. The
  music status-line assignments now route through `PatchBenchSafeCopyOutcomeText`
  without changing AppCore behavior, patch catalogs, byte data, launch behavior,
  safe-copy manifests/signatures, or process control.
- `PatchBenchSafeCopyOutcomeTextTests` asserts exact reflected helper output for
  the moved music replacement status states. `WinUiProductLaneTests` guards page
  routing, helper boundaries, and the absence of the previous inline status
  literals.
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
- Future runtime/proof recommendation is a gated private Music Audible Output
  Live Bundle prompt/readiness lane. Prompt authoring can proceed, but live
  execution must stop unless storage closeout, exclusive leases, an empty
  isolated proof root, no preexisting BEA/CDB processes, and capture
  span/flush/decode-window readiness are proven.
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

- Safe-copy music status helper:
  `OnslaughtCareerEditor.WinUI/Helpers/PatchBenchSafeCopyOutcomeText.cs`
- Safe-copy music status helper-output tests:
  `OnslaughtCareerEditor.UiTests/PatchBenchSafeCopyOutcomeTextTests.cs`
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
   the music audible-output readiness docs and tools before editing:
   `tools/run_winui_safe_copy_music_audible_output_live_bundle.py`,
   `tools/winui_safe_copy_music_audible_output_live_bundle_gate.py`,
   `tools/winui_safe_copy_music_audible_output_materializer.py`, and the
   related music capture/correlation checkers.
2. Run one bounded gated Music Audible Output Live Bundle prompt/readiness slice:
   author or harden the fail-closed private prompt/readiness artifact and, where
   useful, add static/self-test coverage for the capture-span/decode-window
   preflight that must stop before any live arm when coverage is not proven.
3. Keep the slice scoped to prompt/readiness and non-live tooling: do not launch
   BEA, attach CDB, capture audio, mutate copied executables, mutate proof
   archives, delete proof/Ghidra material, change AppCore patch behavior, enable
   Host/Join or online actions, package a release, or mutate installed game
   files/original `BEA.exe`.
4. If prompt/readiness work needs private local paths or raw proof material, keep
   them in ignored local artifacts with placeholders in tracked docs/state.
5. A separate later local-maintenance baton can address Ghidra/proof family
   taxonomy, proof-archive manifest/hash comparison, branch cleanup, or scratch
   cleanup. That work must start with dry-run evidence, explicit scope, and
   deletion authority.

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
