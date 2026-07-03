# Career Progression Static Bridge Consult Record

Status: accepted after consult-driven checker and wording fixes
Date: 2026-07-03
Scope: `career-progression-static-bridge-contract`

This record covers the high-throughput consult pass required before accepting
the career progression static bridge slice. External lanes received only a
sanitized bundle containing the public slice files, a brief, and validation
summary. Authority-bearing files, state batons, coordination contracts,
AGENTS, secrets, logs, caches, local proof roots, private runtime files, hard
payloads, and raw manifests were not sent.

## Consult Bundle

Allowed review files:

- `reverse-engineering/binary-analysis/career-progression-static-bridge-contract.md`
- `lore-book/reverse-engineering/binary-analysis/career-progression-static-bridge-contract.md`
- `tools/career_progression_static_bridge_contract_probe.py`
- `reverse-engineering/binary-analysis/_index.md`
- `lore-book/reverse-engineering/binary-analysis/_index.md`
- `roadmap/rebuild-front-door-chain-map.md`
- `package.json`

The temp workspace path is intentionally redacted below as `<sanitized-temp>`.

## Lane Outcomes

| Lane | Tool / command form | Result | Notes |
| --- | --- | --- | --- |
| Codex normal | `multi_agent_v1.spawn_agent(agent_type=docs_auditor, reasoning_effort=high)` | `ACCEPT_WITH_NOTES` | No blockers. Confirmed proof class, mirror parity, registration, and non-claims. Noted that the checker name implied tracked Markdown while implementation also accepted untracked Markdown. |
| Codex adversarial | `multi_agent_v1.spawn_agent(agent_type=docs_auditor, reasoning_effort=high)` | initial `BLOCKED`; follow-up `ACCEPT_WITH_NOTES` | Blocker: `tools/career_progression_static_bridge_contract_probe.py` used `git ls-files --cached --others --exclude-standard -- *.md`, allowing untracked Markdown as link evidence. Fix removed `--others`; follow-up accepted with note that consult prompt snapshots are not canonical evidence. |
| Cursor normal | `cursor-agent --print --mode ask --model composer-2.5-fast --workspace <sanitized-temp> --trust <prompt>` | initial exit `1`; retry exit `0`, `ACCEPT_WITH_NOTES` | Initial failure: `RetriableError: [unavailable] getaddrinfo ENOTFOUND agentn.global.api5.cursor.sh`. Retry after DNS resolution succeeded. Notes were non-blocking wording/readability concerns. |
| Cursor adversarial | `cursor-agent --print --mode ask --model composer-2.5-fast --workspace <sanitized-temp> --trust <prompt>` | initial exit `1`; retry exit `0`, `ACCEPT_WITH_NOTES` | Initial failure: `RetriableError: [unavailable] getaddrinfo ENOTFOUND agentn.global.api5.cursor.sh`. Retry succeeded and flagged wording/checker hardening notes addressed below. |
| Grok normal | `grok --model grok-build --cwd <sanitized-temp> --disable-web-search --no-subagents --max-turns 4 --output-format plain --single <prompt>`; retry with `--prompt-file` | initial exit `1`; prompt-file retry exit `1`; final retry exit `0`, `ACCEPT` | Initial failure: sanitized bundle was not a git repo and Grok hit `read_file` tool errors/max turns. Prompt-file retry with `--max-turns 1` also hit max turns. Final retry used a git-initialized sanitized bundle and `--max-turns 6`; it accepted. |
| Grok adversarial | `grok --model grok-build --cwd <sanitized-temp> --disable-web-search --no-subagents --max-turns 4 --output-format plain --single <prompt>`; retry with `--prompt-file` | initial exit `1`; prompt-file retry exit `1`; final retry exit `0`, `ACCEPT_WITH_NOTES` | Initial failure: sanitized bundle was not a git repo and Grok hit `read_file` tool errors/max turns. Prompt-file retry with `--max-turns 1` also hit max turns. Final retry used a git-initialized sanitized bundle and `--max-turns 6`; notes converged with Cursor wording concerns. |

## Consult-Driven Fixes

- `tools/career_progression_static_bridge_contract_probe.py` now enumerates
  Markdown link targets with `git ls-files --cached -- *.md`; untracked
  Markdown can no longer satisfy the checker.
- `career-progression-static-bridge-contract.md` and its lore mirror now say
  `copied-baseline byte-preservation fixture context` instead of implying
  AppCore support.
- The same contract now routes `CGame` vocabulary to `static outcome bridge
  docs` and keeps live MissionScript command effects in the higher-authority
  column.
- `roadmap/rebuild-front-door-chain-map.md` now says the row organizes
  `static save, career, and mission-outcome vocabulary`, not mission-outcome
  evidence.
- The exit gate now says `hard-payload safety`.

## Root Acceptance

After the fixes, the blocking Codex adversarial issue was resolved and all six
required lanes either accepted the final slice or accepted it with non-blocking
notes. No runtime proof, BEA/CDB launch, live Ghidra mutation, destructive
cleanup, release publication, account/provider action, or paid spend occurred.
