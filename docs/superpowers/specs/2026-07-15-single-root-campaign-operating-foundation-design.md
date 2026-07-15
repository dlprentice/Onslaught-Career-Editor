# Single-Root Campaign Operating Foundation Design

Status: maintainer-approved design
Date: 2026-07-15

## Goal

Replace the legacy coordinator/worker/lease-first campaign ceremony with a
single-root operating model that can run the durable Battle Engine Aquila
reconstruction goal unattended. Preserve the safety properties that matter:
exact target identity, serialized shared resources, bounded evidence claims,
private payload containment, rollback, validation, cleanup, and honest
blockers.

The durable reconstruction objective remains unchanged. This design changes
how authority and coordination are supplied, not what the campaign is trying
to accomplish.

## Selected Approach

Use **single root with an optional coordination overlay**.

The active root task is the normal implementation, integration, validation,
state, version-control, and acceptance owner. Subagents and external consults
are bounded advisers by default and are used when their independence or
specialization adds value. A subagent may receive a non-overlapping write task
only through an explicit root assignment. Persistent coordinator, worker,
integration, acceptance, worktree, and lease roles activate only when root
deliberately creates genuinely concurrent writers or a shared-resource wave.
Only the current root exercises consequential standing mutation, publication,
external-action, and acceptance authority; an assigned writer receives only
its explicit write scope.
Exactly one task may claim root. Ambiguous dual-root state makes consequential
mutation/publication read-only until the baton and current task ownership name
one root.

Machine-resource ownership is an execution-safety mechanism, not a human
permission gate. Root serializes BEA, debugger, Ghidra, native desktop, build,
and publication actions; verifies process/path/hash/start/window/module or
project/backup identity as applicable; uses invocation-owned ignored roots;
and proves cleanup. An unknown competing owner is not terminated. Root either
waits, safely disambiguates, or advances an independent slice.
After a crash or handoff, a successor root verifies the baton, prior-owner
absence, and relevant process/project/publication state before reclaiming a
resource; claims never expire merely because time passed. Push/publication
succession also re-reads exact remote identities before acting.

## Standing Campaign Authority

The maintainer has supplied standing authority for in-scope campaign work:

- normal source, tests, documentation, state, and harness changes;
- commits and pushes to the configured project repository without force-push;
- copied-runtime launches, controlled input, debugger attachment, read-process
  memory, and process-memory mutation;
- patching and mutation of copied executables and copied profiles;
- live Ghidra inspection, mutation, save, and read-back with verified complete
  backup and rollback discipline;
- bounded cleanup of processes, copied profiles, build/test output, and ignored
  proof roots created and owned by the current action or separately verified as
  disposable before that action through an action receipt/provenance identifier
  and exact allowed path class; unknown crash debris remains retained;
- tags, releases, publication, and project-scoped external actions when a
  campaign slice calls for them, the exact target/artifact is known, applicable
  gates pass, and evidence supports the published claim.

Copied-runtime/executable/process mutation proves path/hash/process-image copy
identity before action. Standing external actions are closed to configured
repository/project surfaces and a slice-named exact target: non-force Git,
issue/PR/project metadata, unused tag/release/publication identity creation,
additive verified-artifact publication, and established project-channel
announcements. Billing/spend, credentials, account/provider administration,
unrelated deployment, and novel audiences are not aliases for this authority.

Standing authority removes repeated approval requests. It does not remove
preflight identity, attempt caps, arm gates, backups, validation, rollback,
evidence boundaries, or cleanup receipts. It also does not require a release
or external action when that action has no objective-aligned value.
The maintainer intentionally classifies evidence-gated creation of configured-
project tags, releases, publications, and project-scoped external actions as
standing-authorized rather than fresh destructive actions; later deletion,
replacement, history rewriting, or withdrawal is evaluated separately.
Standing creation requires an unused identity and never moves a tag, replaces
an existing artifact, retargets published identity, or withdraws prior truth.

## Fresh Authorization Boundaries

Fresh maintainer authority remains required for:

- spending or any action that can incur a charge; and
- genuinely destructive or irreversible operations beyond normal cleanup,
  including force-push/history rewriting, deletion of ambiguous or
  irreplaceable proof or backup material, broad storage pruning, or destructive
  changes outside an invocation-owned disposable root.

The following remain prohibited by the repository contract rather than merely
approval-gated:

- writing, patching, renaming, or otherwise mutating the installed Steam game
  or original `BEA.exe`;
- tracking or publishing proprietary game payloads, raw private evidence, or
  secrets; and
- promoting Host/Join, retail parity, or other evidence-dependent claims before
  their acceptance criteria are met.

When a requested target is novel or ambiguous, root must identify the exact
repository, account, channel, audience, artifact, or host before acting. That
is target verification, not a return to lease ceremony.

## Blocker Semantics

A blocked slice does not block the durable campaign while another safe,
authorized, material slice exists. Root records the exact skipped blocker and
continues according to `goal.campaign.md` priority. The whole goal is marked
blocked only when no meaningful authorized work remains or every useful path
needs unavailable human input, spending authority, or destructive authority.

Missing coordinator records, worker leases, redundant acceptance roles, or a
separately enumerated runtime baton are not blockers for single-root work
already covered by standing authority.

The existing shield-live blocker is therefore obsolete as an authority
blocker. The live measurement itself remains pending: exactly two copied-target
attempts, no third attempt, and no public behavior contract if either attempt
fails.

## Durable Document Shape

The rewrite will:

1. Make `goal.policy.md` the concise authority and single-root operating
   contract.
2. Keep `coordination/` as an optional concurrency overlay instead of deleting
   its useful collision and reporting guidance.
3. Replace the time-boxed canonical slash prompt with the maintainer-approved
   durable goal text, unchanged, and point its separate-authorization clause to
   `goal.policy.md`.
4. Align contributor and campaign references so they do not imply that normal
   root work needs coordinator lanes, isolated worktrees, or human-issued
   resource leases.
5. Resolve the skipped shield authority blocker in `goal.md` without claiming
   a runtime attempt or shield value, and retain the current M2.3 slice.
6. Add a deterministic policy-consistency test that catches reintroduction of
   the obsolete single-root lease requirement or loss of the retained safety
   boundaries.

## Rejected Approaches

### Patch only `goal.md`

Rejected because the blocker would recur: `goal.policy.md`, the slash prompt,
and coordination documents would still require the missing ceremony.

### Delete `coordination/`

Rejected because path ownership, shared-resource collision, and acceptance
guidance remains useful when root intentionally creates concurrent writers.
The problem is unconditional activation, not the existence of the overlay.

### Keep structured batons but auto-generate them

Rejected because this preserves authorization theater. Machine-generated
receipts should prove target identity and cleanup; they should not pretend to
grant authority already supplied by the maintainer.

## Verification

The rewrite is documentation/policy behavior with one deterministic checker.
Acceptance requires:

- a RED test against the legacy foundation and GREEN after the rewrite;
- the focused policy-consistency test;
- current documentation-command and public-core link checks;
- hard-payload safety and repository hygiene checks;
- `git diff --check`;
- independent normal and adversarial review proportionate to the policy and
  authority change; and
- confirmation that no BEA, debugger, Ghidra, release, or external action was
  performed while rewriting the foundation.

## Nonclaims

- This rewrite does not execute the pending shield attempts or any other
  campaign slice.
- It does not prove a retail behavior, change deterministic Core, enable
  Host/Join, or publish a release.
- Standing release authority is not release readiness and does not weaken
  artifact, provenance, validation, or claim gates.
- Single-root ownership does not permit overwriting unrelated dirty work.
