# Active Goal Slice

Status: active
Last updated: 2026-06-26
Policy: `goal.policy.md`

## Current Slice

Run the next repo-quality baton verification from the accepted hash-closeout and
wording-classification evidence. Start read-only: confirm live `main`, state
batons, and front-door docs still align before any edit. If drift is proven,
make only the smallest docs/state baton correction; otherwise produce a concise
no-change report.

## Current Truth

- Public `main`, `origin/main`, and live remote `refs/heads/main` were verified
  at `c5dfae7c7108a89fd861cb286b3e9d03e3a17d85` before integrating the accepted
  hash-closeout commit `f5ab519b8393eb12197fa4d591d466e6517b79f7`. Future
  writes must re-read live git truth first.
- The wording classification found no clearly stale non-validation
  public-candidate or curated-export wording requiring a docs edit.
- Coordination contracts in `coordination/` are the durable policy for
  coordinator, worker, reviewer, integration, acceptance, path-ownership,
  resource-lease, report, and local-log boundaries.
- The public repo remains the primary collaboration repo for source, docs,
  tools, tests, RE notes, wave notes, state batons, agent reports, readiness
  notes, and compact proof summaries that are non-secret and non-payload.
- Hard payloads remain outside git and outside release ZIPs: game executables,
  copied executables, copied runtime output, arbitrary saves/options, raw proof
  logs, screenshots or frame dumps, full Ghidra databases, secrets, `.env*`,
  local runtime caches, and build/package output. Use `LOCAL_LAB_OVERLAY.md` for
  local-only placement.
- WinUI 3 remains the primary user-facing app. AppCore remains the shared
  correctness layer for saves, options, patch planning, media/catalog support,
  and safe-copy workflows. The C# CLI and Python tooling remain support lanes.
- Online multiplayer is still not player-ready. Host/Join remains disabled
  until distinct-endpoint command-source proof and source-bound copied-runtime
  causality proof are both accepted.
- Runtime audible music output is still not proven. Static RE closure is not
  runtime, gameplay, visual, online, rebuild, or no-noticeable-difference proof.
- Installed game files and original `BEA.exe` remain read-only.
- No product source, product tests, package scripts, patch catalogs, release
  artifacts, AppCore, WinUI, CLI, runtime/proof scripts, Ghidra content, game
  files, installed game folder, or original `BEA.exe` changed in the accepted
  repo-quality closeout evidence.
- No release was built, published, signed, pushed as a package, or announced.
- No Host/Join, online readiness, runtime audio, gameplay, visual, rebuild, or
  no-noticeable-difference claim changed.

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

1. Start from clean `main`; fetch or otherwise verify `HEAD`, `origin/main`, and
   live remote `refs/heads/main` before writing.
2. Re-read `goal.md`, `developer_agent_state.json`,
   `documentation_agent_state.json`, and `re_orchestrator_state.json`; confirm
   there are no stale consolidated-main hash references and no accidental
   reopening of the completed wording-classification slice.
3. Re-read front-door public repo docs only if git or baton truth moved since
   the last closeout evidence; treat the wording classification as no-op
   evidence unless a new concrete stale claim is proven.
4. If a state/docs mismatch is proven, make the smallest correction in
   `goal.md`, `developer_agent_state.json`, or `documentation_agent_state.json`;
   leave `re_orchestrator_state.json` untouched unless RE orchestration truth
   actually changed.
5. Validate edits with JSON parsing for edited state files, stale-hash scan,
   `git diff --check`, `npm run test:doc-commands`,
   `npm run test:repo-hygiene`, `npm run test:public-allowlist`, and
   `npm run test:hard-payload-safety`; run `npm run test:md-links` only if
   Markdown links change.
6. Stop with a no-change report if no mismatch is proven.

## Stop Conditions

- Any step would mutate the installed game folder or original `BEA.exe`.
- Any tracked file would add hard payloads, raw proof logs, screenshots/frame
  dumps, copied executable output, full Ghidra databases, secrets, `.env*`,
  build output, package output, or local runtime caches.
- Any claim would promote online readiness, runtime audio proof, gameplay
  parity, visual parity, release readiness, or rebuild parity beyond evidence.
- Ownership or resource leasing is unclear for a planned write.
- Required validation fails without a bounded explanation and correction path.
