# Active Goal Slice

Status: active
Last updated: 2026-06-27
Policy: `goal.policy.md`

## Current Slice

The post-wave closeout and PatchBench maintainability commits are integrated on
`main`. The next executable slice is a small WinUI validation-wrapper short-path
guard/docs follow-up for the Windows App SDK/XAML compiler long-path failure
mode.

Before any later write, re-read live git truth and target files. Exact commit
hashes below are accepted evidence for this integration, not standing future
main truth.

## Current Truth

- Accepted closeout commit `3fb96d4e09df1cc9712e39a325e4f3500bb7ea9e`
  reconciles `goal.md`, `developer_agent_state.json`, and
  `documentation_agent_state.json` for the previous modularity wave and removes
  stale local-campaign path/pending-push wording.
- Accepted PatchBench commit `b000fa0be85d99e479a9d885af1ef5acd35e4aaf`
  hardens a static WinUI guard so literal `Button Content` labels cannot expose
  Host/Join, matchmaking, or online action wording before the required proof and
  promotion gates exist.
- The PatchBench change is test-only. AppCore receipt construction, patch
  planning, byte patch data, patch catalog rows, launch arguments, safe-copy
  manifests/signatures, process decisions, music behavior, Host/Join
  availability, online readiness, runtime proof, and release packaging are
  unchanged.
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

- Accepted integration evidence commits:
  `3fb96d4e09df1cc9712e39a325e4f3500bb7ea9e` and
  `b000fa0be85d99e479a9d885af1ef5acd35e4aaf`.
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
   `tools/winui_primary_lane_validation.py`, `tools/README.md`, and
   `release/readiness/PUBLIC_SIGNOFF_COMMANDS.md` before editing.
2. Keep the follow-up limited to the WinUI primary-lane validation wrapper
   preserving or clearly warning about intentional short invocation roots for
   Windows App SDK/XAML compiler long-path failures, plus a small documentation
   note if useful.
3. Do not change package scripts, product behavior, AppCore semantics, patch
   catalog rows, byte patch data, launch behavior, safe-copy
   manifests/signatures, runtime proof, release packaging, Host/Join, online
   readiness, Ghidra material, installed game files, or original `BEA.exe`.
4. Run focused wrapper self-tests or direct command-equivalent validation plus
   docs/state gates before claiming the follow-up slice.

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
