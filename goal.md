# Active Goal Slice

Status: active
Last updated: 2026-06-28
Policy: `goal.policy.md`

## Current Slice

The PatchBench online-readiness helper wave is integrated on `main`. It accepts
the presentation-only helper/model extraction, the public-state evidence sanity
repair, and the rebuild/spec roadmap-index follow-up as one canonical
integration.

Before any later write, re-read live git truth and target files. The accepted
worker commits below are merge parents of this integration; do not treat
unmerged local campaign commits or local campaign paths as durable public truth.

## Current Truth

- Accepted merge parent `98b9465108b6cf92cd6dcf325bab4a159c5c8ac9` extracts
  PatchBench online-readiness and companion-session presentation text into
  `PatchBenchOnlineReadinessText` plus small text-state records.
- Accepted merge parent `ba3a22ead9d83692a2199e1288d8f363ec30eb6e` repairs
  public state pointers so tracked state no longer depends on older local-only
  worker/source commit hashes.
- Accepted merge parent `b675a2fe817fdac50740d0f04b5bc0fdc61d05d3` indexes
  `roadmap/static-to-proof-rebuild-transition-backlog.md` from
  `roadmap/ROADMAP-INDEX.md`.
- The PatchBench helper is presentation-only. `BinaryPatchesPage` still owns
  `OnlineMultiplayerReadinessService` calls and UI control assignment.
- The helper formats existing DTO/status text only. AppCore receipt
  construction, patch planning, byte patch data, patch catalog rows, launch
  arguments, safe-copy manifests/signatures, process decisions, music behavior,
  Host/Join availability, online readiness, runtime proof, and release
  packaging are unchanged.
- Online multiplayer is still not player-ready. Host/Join remains disabled
  until distinct-endpoint command-source proof and source-bound copied-runtime
  causality proof are both accepted.
- The public state/hash repair is documentation/state-only; it does not change
  product behavior, runtime proof, release packaging, Ghidra material, hard
  payload posture, installed game files, or original `BEA.exe`.
- The roadmap-index fix is docs-only and does not claim rebuild parity, visual
  parity, gameplay proof, runtime proof, or no-noticeable-difference proof.
- The repaired path-ownership incident from the helper worker remains a
  non-blocking integration note: the accidental canonical static-test edit was
  reverted by that worker before integration, and canonical `main` was verified
  clean before this merge.
- Cross-review note to preserve: the next substantive PatchBench helper change
  should add representative DTO-based helper-output tests that fail on omitted,
  swapped, or boundary-losing text-state fields.
- Hard payloads remain outside git and release ZIPs: game executables, copied
  executables, copied runtime output, arbitrary saves/options, raw proof logs,
  screenshots or frame dumps, full Ghidra databases, secrets, `.env*`, local
  runtime caches, and build/package output.
- Runtime audible music output is still not proven. Static RE closure is not
  runtime, gameplay, visual, online, rebuild, or no-noticeable-difference
  proof.
- Installed game files and original `BEA.exe` remain read-only.
- No release, tag, package, signing, installer, announcement, hosted workflow,
  or publication action is part of this integration.

## Evidence Pointers

- Accepted merge parents for this integration:
  `98b9465108b6cf92cd6dcf325bab4a159c5c8ac9`,
  `ba3a22ead9d83692a2199e1288d8f363ec30eb6e`, and
  `b675a2fe817fdac50740d0f04b5bc0fdc61d05d3`.
- Prior public integration commits remain accepted evidence for the wrapper,
  state-slimming, and PatchBench static online-button guard work:
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
   `OnslaughtCareerEditor.WinUI/Helpers/PatchBenchOnlineReadinessText.cs`,
   the related text-state records, and the relevant `WinUiProductLaneTests`
   guards before editing.
2. Add focused representative DTO-based tests for
   `PatchBenchOnlineReadinessText.Build` and `BuildCompanionSession` so helper
   output fails when fields are omitted, swapped, or lose Host/Join unavailable
   and online non-claim boundaries.
3. Keep the slice test/helper-output scoped: do not move
   `OnlineMultiplayerReadinessService` behavior, enable Host/Join or online
   actions, change AppCore semantics, patch catalog rows, byte patch data,
   launch behavior, safe-copy manifests/signatures, runtime proof, release
   packaging, Ghidra material, installed game files, or original `BEA.exe`.
4. After that test slice, a safe docs/checker follow-up is a compact
   rebuild-front-door chain map that aliases long static-to-proof slice names to
   short proof files and the current selected active scope.

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
