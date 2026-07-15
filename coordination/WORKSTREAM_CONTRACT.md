# Workstream Contract

Status: optional concurrency overlay
Last updated: 2026-07-15

## Applicability

This contract applies only after root explicitly activates a coordinated wave
with concurrent writers, recurring automation, or separate integration and
acceptance roles. It does not apply to ordinary single-root work, bounded
read-only subagents, or consults.

Activation names the owner of each write set and shared resource, the
integration owner, stop conditions, and the expected handoff. It supplements
normal repository guidance and never relaxes payload, evidence, installed-game,
destructive-action, spending, or release-quality boundaries.

## Ownership Rules

- One path family has one active write owner.
- One shared machine resource has one active owner.
- Unknown or contested ownership means read-only.
- A writer verifies repository, branch/worktree, base, allowed paths, forbidden
  paths, and dirty state before editing.
- A writer never resets, cleans, stashes, discards, or overwrites work it did
  not create.
- Review-only roles do not edit tracked files.
- The integration owner serializes overlapping commits and canonical state.

High-collision families are exclusive when multiple writers are active:

- `goal.md`, `goal.policy.md`, `AGENTS.md`, `CONTRIBUTING.md`, and
  `coordination/`;
- canonical state JSON and shared readiness/front-door documents;
- `package.json` and central validation scripts;
- patch/profile catalogs and shared AppCore services;
- shared WinUI pages, helpers, and UI tests; and
- release packaging, publication, and proof tooling.

Different intended outcomes do not make overlapping semantic owners safe to
edit concurrently. Serialize the work or assign one writer.

## Assignment Shape

A concurrent write assignment should name only what another role needs to
avoid collisions and accept the result:

- concise objective and claim boundary;
- base, branch/worktree when used, allowed paths, and forbidden paths;
- path/resource claims and expected release condition;
- directly relevant repository truth and required files;
- focused validation and stop conditions;
- required diff/patch handoff; a non-root writer does not commit under ambient
  campaign authority;
- integration owner and any risk-shaped independent review; and
- terminal result: advancement, exact blocker, or no accepted change.

Subagents advise unless root explicitly assigns a bounded non-overlapping write
set. No persistent lane is created for routine formatting, validation, review,
or follow-through.

## Canonical State

While multiple writers are active, the integration owner alone prepares the
proposed reconciliation for:

- `goal.md` and campaign priorities;
- canonical implementation/documentation state;
- shared readiness/front-door claims; and
- cross-slice evidence boundaries.

Other writers report proposed deltas. The current root reviews and writes the
final integration/state commit. After the wave ends, normal single-root
ownership resumes and no lease-release ceremony is required beyond confirming
that no competing writer or owned process remains.

## Stop Conditions

A coordinated writer stops and routes to root/integration when:

- base, target, write set, or resource ownership does not match the assignment;
- target paths contain unknown overlapping changes;
- a shared resource is owned by another operation;
- installed Steam/original `BEA.exe` mutation would be required;
- a hard payload, secret, private evidence, or generated output would enter
  tracked source;
- a claim would exceed its static, runtime, visual, rebuild, online, or release
  evidence;
- validation cannot establish the assigned contract; or
- the required operation needs spending or genuinely destructive authority not
  granted under `goal.policy.md`.

An unknown process is never killed merely to free a resource claim.

## Review And Acceptance

Root chooses review proportional to consequence, uncertainty, scope, and claim
risk. Independent normal/adversarial review is especially useful for broad
policy, security, destructive, release, runtime-mutation, or contested work.
External consults remain sanitized, read-only, and advisory.

The number of reviewers or consults is not itself acceptance evidence. A named
integration owner may prepare reconciliation, but the current root alone owns
final judgment, commits/pushes, resolves material findings, and records
unavailable evidence honestly. Transferring those powers requires an explicit
root handoff followed by the successor checks in `goal.policy.md`.

## Authority

This contract allocates concurrent ownership; it does not grant action
authority. Standing campaign authority and fresh-authorization boundaries come
from `goal.policy.md` and newer direct maintainer instructions. Resource claims,
worktrees, worker assignments, and review output cannot expand those
boundaries.
