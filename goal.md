# Active Goal Slice

Status: active
Last updated: 2026-06-28
Policy: `goal.policy.md`

## Current Slice

The storage-conscious PatchBench routing-guard wave is integrated on `main`.
The integrated change adds shared reflected WinUI helper-output loading in
UiTests, guards `BinaryPatchesPage` online-readiness rendering through
`PatchBenchOnlineReadinessText`, documents storage hygiene boundaries, and
refreshes canonical state without treating local campaign paths or worker
worktrees as durable public truth.

Before any later write, re-read live git truth and target files. Do not treat
local campaign reports, local worktree paths, or unmerged worker commits as
durable public evidence.

## Current Truth

- `OnslaughtCareerEditor.UiTests/ReflectedWinUiTestSupport.cs` now centralizes
  reflected WinUI assembly loading, sibling DLL resolution, stale-build checks,
  public static helper invocation, and string-property reading for helper-output
  tests.
- `OnslaughtCareerEditor.UiTests/PatchBenchOnlineReadinessTextTests.cs` uses the
  shared reflected loader for `PatchBenchOnlineReadinessText.Build` and
  `BuildCompanionSession` DTO/model output checks.
- `OnslaughtCareerEditor.UiTests/PatchBenchOnlineReadinessRoutingGuardTests.cs`
  now guards that `BinaryPatchesPage` collects service state before calling
  `PatchBenchOnlineReadinessText.Build` and `BuildCompanionSession`, assigns the
  mapped text-state properties to the expected controls, and does not assign
  inline string literals in those render paths.
- The routing guard preserves the repaired exact-token assertions: missing
  service or helper tokens fail exact-count checks before order comparison.
- PatchBench button labels and click handlers are guarded against premature
  Host/Join, matchmaking, online-ready, netplay, or online-action wording while
  technical boundary text remains allowed.
- `LOCAL_LAB_OVERLAY.md` now documents storage hygiene and retention: disposable
  campaign/build/package scratch can be cleaned after final reports and accepted
  findings are preserved, scratch devices are temporary rather than durable sole
  storage, and Ghidra/proof pruning requires manifest classification.
- Public-safe storage closeout summary: old local campaign scratch cleanup
  removed 10.926 GiB. Drive free-space readings moved from C: 225.514 GiB to
  237.191 GiB, D: stayed 398.235 GiB, F: stayed 119.242 GiB, G: stayed
  90.251 GiB, and H: stayed 245.474 GiB.
- Ghidra backup retention was report-only: about 142.295 GiB of backup material
  remains retained pending per-family manifest/provenance review. The live
  Ghidra project remains do-not-touch.
- Proof archive retention was report-only: about 270.438 GiB of raw proof roots
  remains retained pending manifest/hash comparison. Unknown H: containers
  remain do-not-touch.
- Future runtime/proof recommendation is a private Music Audible Output Live
  Bundle lane after repo/storage closeout and explicit runtime-proof leasing.
  Original-binary online proof remains a later distinct-endpoint and
  source-bound copied-runtime causality rung.
- Online multiplayer is still not player-ready. Host/Join remains disabled
  until distinct-endpoint command-source proof and source-bound copied-runtime
  causality proof are both accepted.
- Static RE closure is not runtime, gameplay, visual, online, rebuild, or
  no-noticeable-difference proof.
- Hard payloads remain outside git and release ZIPs: game executables, copied
  executables, copied runtime output, arbitrary saves/options, raw proof logs,
  screenshots or frame dumps, full Ghidra databases, secrets, `.env*`, local
  runtime caches, and build/package output.
- Installed game files and original `BEA.exe` remain read-only.
- No release, tag, package, signing, installer, announcement, hosted workflow,
  or publication action is part of this integration.

## Evidence Pointers

- Routing guard tests:
  `OnslaughtCareerEditor.UiTests/PatchBenchOnlineReadinessRoutingGuardTests.cs`
- Shared reflected WinUI test support:
  `OnslaughtCareerEditor.UiTests/ReflectedWinUiTestSupport.cs`
- DTO helper-output tests:
  `OnslaughtCareerEditor.UiTests/PatchBenchOnlineReadinessTextTests.cs`
- PatchBench presentation helper:
  `OnslaughtCareerEditor.WinUI/Helpers/PatchBenchOnlineReadinessText.cs`
- PatchBench text-state records:
  `OnslaughtCareerEditor.WinUI/Models/PatchBenchOnlineReadinessTextState.cs`
  and
  `OnslaughtCareerEditor.WinUI/Models/PatchBenchOnlineCompanionSessionTextState.cs`
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
   `OnslaughtCareerEditor.WinUI/Pages/BinaryPatchesPage.xaml.cs`,
   `OnslaughtCareerEditor.WinUI/Helpers/PatchBenchOnlineReadinessText.cs`, and
   the PatchBench UiTests before editing.
2. Add one compact PatchBench/BinaryPatchesPage modularity slice: extract another
   presentation-only text builder from page orchestration where it reduces
   real duplication, then cover the boundary with focused UiTests that preserve
   existing user-facing wording and non-claims.
3. Keep the slice scoped to presentation/testability only: do not move
   `OnlineMultiplayerReadinessService` behavior, enable Host/Join or online
   actions, change AppCore semantics, patch catalog rows, byte patch data,
   launch behavior, safe-copy manifests/signatures, runtime proof, release
   packaging, Ghidra material, installed game files, or original `BEA.exe`.
4. A separate later local-maintenance baton can address stale prunable Git
   worktree metadata and proof-archive manifest/hash comparison. That work must
   start with dry-run evidence, avoid branch deletion unless separately
   authorized, and must not mutate proof/Ghidra/game/runtime material without
   explicit manifest authority.
5. Runtime-proof work should wait until the repo/product slice is closed or
   explicitly paused and a private proof-root retention plan is leased.

## Stop Conditions

- Any step would mutate the installed game folder or original `BEA.exe`.
- Any tracked file would add hard payloads, raw proof logs, screenshots/frame
  dumps, copied executable output, full Ghidra databases, secrets, `.env*`,
  build output, package output, or local runtime caches.
- Any claim would promote online readiness, runtime audio proof, gameplay
  parity, visual parity, release readiness, release publication, rebuild parity,
  or no-noticeable-difference parity beyond evidence.
- Ownership or resource leasing is unclear for a planned write.
- Required validation fails without a bounded explanation and correction path.
