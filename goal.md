# Active Goal Slice

Status: active
Last updated: 2026-06-26
Policy: `goal.policy.md`

## Current Slice

Close the PR-ready modularity wave integration from the short integration path.
The accepted worker commits are limited to the GitHub PR handoff template and
PatchBench safe-copy presentation-helper/status-copy guard. Reconcile state
batons, run the assigned local gates, and push to `main` only if validation is
green and `origin/main` still equals the assigned base.

## Current Truth

- Integration base: `ab90daa299beff655552899a71372678878af1ea`.
- Accepted worker commit `3af7d18bd2ae16e9c0e18070f593c80765f0bb1c` updates
  `.github/PULL_REQUEST_TEMPLATE.md` with explicit lane/scope, validation,
  private/public boundary, state baton, installed-game/original-`BEA.exe`
  mutation, and remaining-risk fields.
- Accepted worker commit `931af99e8de62ffa5d7c4fc90b8b7a047a0d8b93`
  centralizes PatchBench safe-copy canceled/failed/restored/source-changed
  status copy and the No Host/Join receipt fallback copy in
  `PatchBenchSafeCopyOutcomeText`, with static guard coverage.
- Patch catalog accounting is current at 20 visible options: 9 stable and 11
  experimental; 29/29 catalog rows have target specimen identity and policy
  metadata.
- The PatchBench integration is presentation-only. AppCore receipt
  construction, patch planning, byte patch data, patch catalog rows, launch
  arguments, safe-copy manifests/signatures, process decisions, music behavior,
  Host/Join availability, online readiness, runtime proof, and release
  packaging are unchanged.
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
- No release has been built, published, signed, packaged, tagged, pushed as a
  package, or announced by this integration.

## Evidence Pointers

- Campaign reports:
  `C:\Users\david\source\.codex-campaigns\Onslaught-Career-Editor\20260626T204205Z-pr-ready-modularity-wave\reports\collaboration-pr-readiness-001.md`,
  `C:\Users\david\source\.codex-campaigns\Onslaught-Career-Editor\20260626T204205Z-pr-ready-modularity-wave\reports\winui-patchbench-status-guard-001.md`,
  and
  `C:\Users\david\source\.codex-campaigns\Onslaught-Career-Editor\20260626T204205Z-pr-ready-modularity-wave\reports\repo-quality-adversarial-review-001.md`.
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

1. Finish the assigned integration validation from `C:\otk-int-20260626`.
2. If validation and remote-base checks pass, commit the integrated result and
   push `HEAD:main` under the campaign integration authority.
3. Fast-forward the canonical checkout only after the remote push succeeds and
   the canonical checkout is clean on `main`.
4. After this wave lands, use a read-only acceptance/follow-up slice: verify
   live `main`, `origin/main`, state batons, and the integration reports before
   any edit.
5. Keep any next product behavior work separate from this integration; run
   WinUI/AppCore gates before claiming UI or behavior changes.

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
