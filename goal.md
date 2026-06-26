# Active Goal Slice

Status: active
Last updated: 2026-06-26
Policy: `goal.policy.md`

## Current Slice

Start the first bounded repo-quality wave from consolidated `main` by
classifying remaining legacy public-candidate and curated-export wording in
front-door and release-readiness docs. Keep it read-first and path-scoped; edit
only if the classification proves one clearly stale non-validation wording issue
with a safe docs-only correction.

## Current Truth

- Public `main` and `origin/main` are consolidated at commit
  `7e0f856c216c14bc538c55b1c6f6df99509f585a`.
- Coordination contracts in `coordination/` are the durable policy for
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

1. Start from clean consolidated `main`; if `main` moved after
   `7e0f856c216c14bc538c55b1c6f6df99509f585a`, re-read changed docs and state
   before editing.
2. Read and classify legacy public-candidate and curated-export wording in
   `RELEASE_SCOPE_AND_TEST_COMMANDS.md`, `README.RELEASE.md`, `tools/README.md`,
   `roadmap/repo-structure-and-archive-map.md`, and the public package/reference
   files under `release/readiness/`.
3. Preserve active validation-template, allowlist, and release-accounting names
   when wording is intentional compatibility rather than stale product truth.
4. If one clearly stale non-validation wording issue is found, make the smallest
   docs-only correction in that path family; otherwise produce a concise
   no-change classification report for the next write slice.
5. Validate any docs edit with `npm run test:doc-commands`,
   `npm run test:md-links`, `npm run test:public-allowlist`,
   `npm run test:repo-hygiene`, and `git diff --check`.
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
