# Report Contract

Status: active
Last updated: 2026-06-29

Worker, review, integration, and acceptance reports are campaign-control
artifacts first. Write them to the local campaign root unless an integration
owner sanitizes a durable finding into ordinary repo docs, state batons, or
readiness notes.

## Worker Report Fields

A write worker report must include:

- worker ID
- thread/session ID if known for local campaign coordination only
- persistent goal
- slice and claim boundary
- base commit
- branch and worktree
- allowed paths and forbidden paths
- resource leases used
- files changed
- commit, patch/diff handoff, or no-commit authorization status
- specialist consults
- adversarial review
- findings accepted
- findings rejected with reason
- exact validation commands and results
- claims proven
- explicit non-claims
- hard-payload boundary confirmation
- installed-game/original-`BEA.exe` mutation confirmation
- process cleanup result
- remaining risks
- integration notes
- state/docs updates recommended to the integrator
- terminal status
- lease-release confirmation

### Consult Evidence

Every worker report must include a `Consult Evidence` entry. If no consults
were mandated, record `NO_MANDATED_CONSULTS`. When an assignment requires
specific consult lanes, the report must list each required lane separately,
including Codex specialist review, Codex adversarial review, and any named
external model consults. For assignments that require Cursor consults, record
the `cursor-agent composer-2.5-fast` and `cursor-agent gemini-3.1-pro` outcomes
separately from the Codex reviews.

The consult entry must include a brief non-sensitive task-scope summary,
accepted consult findings, rejected consult findings with reasons, unresolved
dissent, and any `CONSULT_UNAVAILABLE` reason when a required consult tool,
model, authentication state, or safety boundary prevents the consult. Unresolved
blocking dissent prevents terminal success unless the report records the
coordinator or integration-owner override rationale. Do not paste raw prompts,
raw logs, local paths, active campaign IDs, secrets, private proof artifacts, or
full local campaign reports into tracked docs or public summaries.

A worker cannot claim complete while validation failures are hidden, a required
report is missing, a forbidden path changed, a resource lease remains active,
the commit/diff/no-commit status is unidentified, a hard payload or secret was
added, or its claim exceeds its evidence.

Local campaign reports may include active thread or session IDs when needed for
coordination. Tracked repo summaries and readiness notes should not copy those
reports wholesale. Sanitize out active IDs, raw prompts, raw logs, private proof
paths, local payload paths, secrets, credentials, screenshots/frame dumps, raw
CDB logs, copied executable output, and full Ghidra database paths unless an
existing public policy explicitly allows the specific non-secret reference.

## Review Finding Fields

Read-only reviewers report findings with:

- severity
- owner
- exact file, path, or evidence reference
- why it matters
- required correction
- acceptance criterion

Reviewers should separate blockers from non-blocking improvements. A reviewer
does not become a competing writer.

## Integration Report Fields

The integration thread reports:

- accepted and rejected worker commits
- merge or rebase order
- conflicts and resolutions
- canonical state/docs updates
- cross-slice claim reconciliation
- validation commands and results
- process cleanup result when relevant
- remaining risks and next executable slice
- final integrated commit
- lease-release confirmation

## Acceptance Report Fields

The fresh read-only acceptance thread reports:

- decision: accepted, accepted with explicit blockers, or rejected
- evidence reviewed
- ownership and resource-collision checks
- payload/security boundary checks
- installed-game/original-`BEA.exe` mutation check
- validation evidence check
- stale state/docs check
- finite correction list if rejected

Acceptance does not publish releases, enable Host/Join, promote runtime claims,
or mutate repo state.
