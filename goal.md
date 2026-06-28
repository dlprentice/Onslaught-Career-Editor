# Active Goal Slice

Status: active
Last updated: 2026-06-28
Policy: `goal.policy.md`

## Current Slice

The PatchBench DTO helper-output and rebuild front-door chain-map wave is
accepted for canonical integration on `main`. The integrated change adds focused
helper-output tests, adds the rebuild chain map, refreshes current state batons,
and removes tracked front-door examples that exposed literal local campaign or
maintainer-private roots.

Before any later write, re-read live git truth and target files. Do not treat
local campaign reports, local worktree paths, or unmerged worker commits as
durable public truth.

## Current Truth

- `OnslaughtCareerEditor.UiTests/PatchBenchOnlineReadinessTextTests.cs` now
  exercises `PatchBenchOnlineReadinessText.Build` and
  `BuildCompanionSession` with DTO/model inputs that preserve Host/Join
  unavailable wording, online non-claims, command-source-only readiness, gamepad
  preflight wording, and topology boundaries.
- The helper-output tests reflect the built WinUI helper assembly and fail
  clearly when the assembly is missing or stale relative to the helper/model
  source files. They do not move product behavior into tests and do not claim
  launch-plan sanitization.
- `roadmap/rebuild-front-door-chain-map.md` is now the compact static-closure
  to proof-class routing map, and `roadmap/ROADMAP-INDEX.md` points to it.
- `coordination/README.md` no longer carries a literal local campaign-root
  example, and `release/readiness/PUBLIC_SIGNOFF_COMMANDS.md` uses a
  placeholder for the private-root signoff command.
- `LOCAL_LAB_OVERLAY.md` still intentionally documents maintainer-local Ghidra
  descriptors as local-only overlay exceptions. Those paths are not campaign
  truth and are not release payloads.
- The PatchBench helper remains presentation-only. `BinaryPatchesPage` still
  owns `OnlineMultiplayerReadinessService` calls and UI control assignment.
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

- DTO helper-output tests:
  `OnslaughtCareerEditor.UiTests/PatchBenchOnlineReadinessTextTests.cs`
- PatchBench presentation helper:
  `OnslaughtCareerEditor.WinUI/Helpers/PatchBenchOnlineReadinessText.cs`
- PatchBench text-state records:
  `OnslaughtCareerEditor.WinUI/Models/PatchBenchOnlineReadinessTextState.cs`
  and
  `OnslaughtCareerEditor.WinUI/Models/PatchBenchOnlineCompanionSessionTextState.cs`
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
   `OnslaughtCareerEditor.UiTests/PatchBenchOnlineReadinessTextTests.cs` before
   editing.
2. Add one bounded BinaryPatchesPage/PatchBench test-hardening slice: introduce
   a small shared UiTests helper for reflected WinUI helper-output loading and
   add a focused guard that `BinaryPatchesPage` still routes online-readiness
   presentation through `PatchBenchOnlineReadinessText` without reintroducing
   inline Host/Join or online-ready wording.
3. Keep the slice test/modularity scoped: do not move
   `OnlineMultiplayerReadinessService` behavior, enable Host/Join or online
   actions, change AppCore semantics, patch catalog rows, byte patch data,
   launch behavior, safe-copy manifests/signatures, runtime proof, release
   packaging, Ghidra material, installed game files, or original `BEA.exe`.
4. After that hardening slice, the next safe repo-quality follow-up is a
   compact PatchBench/BinaryPatchesPage modularity slice that separates another
   presentation-only text builder from page orchestration with equivalent
   boundary tests.

## Stop Conditions

- Any step would mutate the installed game folder or original `BEA.exe`.
- Any tracked file would add hard payloads, raw proof logs, screenshots/frame
  dumps, copied executable output, full Ghidra databases, secrets, `.env*`,
  build output, package output, or local runtime caches.
- Any claim would promote online readiness, runtime audio proof, gameplay
  parity, visual parity, release readiness, release publication, or rebuild
  parity beyond evidence.
- Ownership or resource leasing is unclear for a planned write.
- Required validation fails without a bounded explanation and correction path.
