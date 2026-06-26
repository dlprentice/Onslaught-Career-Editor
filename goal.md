# Active Goal Slice

Status: active
Last updated: 2026-06-26
Policy: `goal.policy.md`

## Current Slice

Complete the coordination-policy bootstrap integration and fresh read-only
acceptance for the public-primary coordination campaign. After acceptance, use
the `coordination/` contracts to serialize the next bounded product worker: a
read-first Windowed & Mods safe-copy canceled/failed/restored/source-changed
status copy and receipt `No Host/Join` fallback guard inspection.

## Current Truth

- The public repo remains the primary collaboration repo for source, docs,
  tools, tests, RE notes, wave notes, state batons, agent reports, readiness
  notes, and compact proof summaries that are non-secret and non-payload.
- Coordination policy bootstrap commit `2622b030` is integrated on
  `campaign/20260626T024429Z-public-primary-coordination/integration-001`.
  It adds durable public-safe coordination contracts for coordinator, worker,
  reviewer, integration, acceptance, path ownership, resource leases, and
  local campaign reports.
- This bootstrap is documentation/state policy only. It does not change product
  source, product tests, runtime behavior, patch semantics, launch behavior,
  safe-copy behavior, release packaging, Host/Join readiness, runtime proof, or
  Ghidra state.
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

1. Complete fresh read-only acceptance of the coordination-policy integration
   before broad write fanout.
2. Release the integration/state lease only after validation and acceptance
   evidence are recorded in the local campaign reports.
3. Assign exactly one writer for any `BinaryPatchesPage.xaml.cs`,
   `PatchBench*`, or focused PatchBench test changes in the next product slice.
4. Inspect safe-copy canceled/failed/restored/source-changed status copy and the
   defensive receipt `No Host/Join` fallback before choosing a helper extraction
   or guard-hardening edit.
5. Keep patch rows, byte changes, copied-profile launch behavior, safe-copy
   manifests/signatures, music replacement behavior, online/readiness gates,
   runtime proof, release packaging, and installed-game mutation rules out of
   the product slice unless a concrete bug is found and documented.

## Stop Conditions

- Any step would mutate the installed game folder or original `BEA.exe`.
- Any tracked file would add hard payloads, raw proof logs, screenshots/frame
  dumps, copied executable output, full Ghidra databases, secrets, `.env*`,
  build output, package output, or local runtime caches.
- Any claim would promote online readiness, runtime audio proof, gameplay
  parity, visual parity, release readiness, or rebuild parity beyond evidence.
- Ownership or resource leasing is unclear for a planned write.
- Required validation or fresh acceptance fails without a bounded explanation
  and correction path.
