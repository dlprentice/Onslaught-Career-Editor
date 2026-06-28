# Active Goal Slice

Status: active
Last updated: 2026-06-28
Policy: `goal.policy.md`

## Current Slice

The WinUI validation-wrapper diagnostic, state-baton slimming, and PatchBench
runtime online-button guard public integration commits are on `main`. The next
executable slice is a small BinaryPatchesPage/PatchBench presentation-helper
slice for online-readiness text.

Before any later write, re-read live git truth and target files. Public `main`
integration commits below are durable pointers for this state; local worker
source commits were acceptance evidence only.

## Current Truth

- Public main commit `726e71009d7b5dac9256cfe6917c6f0ecca529cb` adds a
  warning-only WinUI validation-wrapper long-path diagnostic plus matching docs.
- Public main commit `b028cbffcb056a722d71dca3fed4483ca9d48bc1` slims the live
  state batons to concise current-state pointers.
- Public main commit `6c26f5c74a73fb31f09051de1807653f26fa26ee` hardens the
  PatchBench static guard against future runtime `PatchBench...Button.Content`
  Host/Join, matchmaking, online-play, or netplay labels.
- Public main commit `5854f5b4c0d5e56cdd1dd6f2a185fd3cf8a40009` reconciles the
  integrated state batons after those changes.
- The PatchBench guard change is test-only. AppCore receipt construction,
  patch planning, byte patch data, patch catalog rows, launch arguments,
  safe-copy manifests/signatures, process decisions, music behavior, Host/Join
  availability, online readiness, runtime proof, and release packaging are
  unchanged.
- The WinUI validation-wrapper follow-up is accepted and closed for this
  integration. It remains diagnostic-only and does not change package scripts or
  product behavior.
- Patch catalog accounting remains 20 visible options: 9 stable and 11
  experimental; 29/29 catalog rows have target specimen identity and policy
  metadata.
- The public repo remains the primary collaboration repo for source, docs,
  tools, tests, RE notes, wave notes, state batons, agent reports, readiness
  notes, and compact proof summaries that are non-secret and non-payload.
- Hard payloads remain outside git and release ZIPs: game executables, copied
  executables, copied runtime output, arbitrary saves/options, raw proof logs,
  screenshots or frame dumps, full Ghidra databases, secrets, `.env*`, local
  runtime caches, and build/package output.
- Online multiplayer is still not player-ready. Host/Join remains disabled
  until distinct-endpoint command-source proof and source-bound copied-runtime
  causality proof are both accepted.
- Runtime audible music output is still not proven. Static RE closure is not
  runtime, gameplay, visual, online, rebuild, or no-noticeable-difference
  proof.
- Installed game files and original `BEA.exe` remain read-only.
- No release, tag, package, signing, installer, announcement, hosted workflow,
  or publication action is part of this integration.

## Evidence Pointers

- Accepted public main integration commits for this state:
  `726e71009d7b5dac9256cfe6917c6f0ecca529cb`,
  `b028cbffcb056a722d71dca3fed4483ca9d48bc1`,
  `6c26f5c74a73fb31f09051de1807653f26fa26ee`, and
  `5854f5b4c0d5e56cdd1dd6f2a185fd3cf8a40009`.
- Coordination contracts: `coordination/README.md`,
  `coordination/WORKSTREAM_CONTRACT.md`,
  `coordination/REPORT_CONTRACT.md`, and
  `coordination/RESOURCE_LEASES.md`.
- Product and contributor boundaries: `AGENTS.md`, `CONTRIBUTING.md`,
  `SECURITY.md`, `COLLABORATION.md`, and `LOCAL_LAB_OVERLAY.md`.
- Current feature/release truth: `CURRENT_CAPABILITIES.md`,
  `README.RELEASE.md`, and `release/readiness/PUBLIC_SIGNOFF_COMMANDS.md`.
- Static RE and roadmap truth: `reverse-engineering/RE-INDEX.md` and
  `roadmap/ROADMAP-INDEX.md`.
- Canonical state batons: `developer_agent_state.json`,
  `documentation_agent_state.json`, and `re_orchestrator_state.json`.

## Next Executable Work

1. Verify live `HEAD`, `origin/main`, and remote `refs/heads/main`, then inspect
   `OnslaughtCareerEditor.WinUI/Pages/BinaryPatchesPage.xaml.cs` and the
   relevant `WinUiProductLaneTests` guards before editing.
2. Extract online-readiness presentation text from
   `RenderOnlineMultiplayerReadiness` and
   `RenderOnlineCompanionSessionReadiness` into a small presentation
   helper/model.
3. Keep the slice presentation-only: do not move
   `OnlineMultiplayerReadinessService` behavior, enable Host/Join or online
   actions, change AppCore semantics, patch catalog rows, byte patch data,
   launch behavior, safe-copy manifests/signatures, runtime proof, release
   packaging, Ghidra material, installed game files, or original `BEA.exe`.
4. Run focused PatchBench/WinUI tests plus the relevant docs/repo safety gates
   before claiming the helper/model slice.

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
