# Active Goal Slice

Status: active
Last updated: 2026-06-26
Policy: `goal.policy.md`

## Current Slice

Start the next bounded repo-quality slice from `main` after the accepted
coordination-policy branch stack has been consolidated. Use a read-first pass
to find one narrow stale-doc, state-baton, or modularity cleanup candidate, then
make the smallest safe edit with matching local validation.

This closeout branch,
`campaign/20260626T124649Z-branch-consolidation-repo-quality/coordination-branch-closeout-001`,
continues accepted coordination integration commit
`286fad8a5f5175150d1d148b06d8309c29656ea3` only to remove completed
pre-acceptance wording and prepare this next executable baton.

## Current Truth

- The coordination policy/state integration on
  `origin/campaign/20260626T024429Z-public-primary-coordination/integration-001`
  was accepted at commit `286fad8a5f5175150d1d148b06d8309c29656ea3`.
- Coordination contracts in `coordination/` are now the durable policy for
  coordinator, worker, reviewer, integration, acceptance, path-ownership,
  resource-lease, report, and local-log boundaries.
- The public repo remains the primary collaboration repo for source, docs,
  tools, tests, RE notes, wave notes, state batons, agent reports, readiness
  notes, and compact proof summaries that are non-secret and non-payload.
- Hard payloads remain outside git and outside release ZIPs: game executables,
  copied runtime output, arbitrary saves/options, raw proof logs, screenshots or
  frame dumps, full Ghidra databases, secrets, `.env*`, local config, caches,
  and build/package output. Use `LOCAL_LAB_OVERLAY.md` for local-only placement.
- WinUI 3 remains the primary user-facing app. AppCore remains the shared
  correctness layer for saves, options, patch planning, media/catalog support,
  and safe-copy workflows. The C# CLI and Python tooling remain support lanes.
- Online multiplayer is still not player-ready. Host/Join remains disabled
  until distinct-endpoint command-source proof and source-bound copied-runtime
  causality proof are both accepted.
- Runtime audible music output is still not proven. Static RE closure is not
  runtime, gameplay, visual, online, rebuild, or no-noticeable-difference proof.
- Installed game files and original `BEA.exe` remain read-only.

## Evidence Pointers

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
- Canonical state batons: `developer_agent_state.json` and
  `documentation_agent_state.json`.

## Next Executable Work

1. Start from the consolidated `main` branch with a clean status and current
   branch truth; if `main` moved after this baton, re-read the changed docs and
   state before editing.
2. Run a read-first stale-doc/state/modularity scan with `rg` over the front
   door docs, state batons, roadmap/release pointers, and the recent Windowed &
   Mods modularity readiness notes.
3. Select one narrow path family with clear ownership: a stale docs/state
   cleanup, or a small Windowed & Mods presentation-helper modularity follow-up
   only if the code lease is clear and current files still justify it.
4. Preserve existing product behavior unless a concrete, bounded bug is found
   and documented before editing.
5. Validate with the docs/state gates for documentation-only work, and add the
   relevant WinUI/AppCore gates before claiming any code or UI behavior change.
6. Update the state batons to the resulting current truth and rewrite this file
   to the next safe executable slice after verified closeout.

## Stop Conditions

- Any step would mutate the installed game folder or original `BEA.exe`.
- Any tracked file would add hard payloads, raw proof logs, screenshots/frame
  dumps, copied executable output, full Ghidra databases, secrets, `.env*`,
  build output, package output, or local runtime caches.
- Any claim would promote online readiness, runtime audio proof, gameplay
  parity, visual parity, release readiness, or rebuild parity beyond evidence.
- Ownership or resource leasing is unclear for a planned write.
- Required validation fails without a bounded explanation and correction path.
