# Coordination Overlay

Status: active when explicitly invoked
Last updated: 2026-07-15

This directory is the optional concurrency overlay for Onslaught Toolkit work.
The normal campaign model is one active implementation owner owning edits,
integration, validation, state, version control, consequential actions, and
acceptance in the main checkout. That owner may be the current root task or one
explicitly designated sole sequential worker supervised by its parent task.

Single-writer work does not require a coordinator, worker lane, isolated
worktree, lease record, worker report, separate integration owner, or separate
acceptance owner. A supervising parent plus one sole implementation worker is
single-writer work: the parent steers and reports but does not mutate or accept
parallel campaign work. The implementation owner uses ordinary repository
safety, serializes shared resources, and preserves unrelated dirty work.

The active implementation owner explicitly activates this overlay only when it
deliberately creates:

- two or more concurrent writers;
- a recurring automation wave;
- an independent acceptance role with a durable handoff; or
- collision-prone shared-resource work whose ownership cannot remain implicit
  in the active root operation.

Activation should name the participating roles, write sets, shared resources,
integration owner, stop conditions, and which contracts in this directory
apply in one ignored/local activation record before an additional writer edits.
Do not infer activation from the existence of subagents, a long-running goal,
a review request, a supervising parent plus sole worker, or access to multiple
worktrees.

## Implementation Owner And Optional Roles

- **Active implementation owner (default):** owns the active slice, edits,
  integration, shared state, validation, commits/pushes, consequential actions,
  and final acceptance. It may be the root task or one explicitly designated
  sole sequential worker.
- **Supervising task (optional compact topology):** steers, interrupts, and
  reports while its sole worker executes. It does not become a concurrent
  writer or acceptance lane.
- **Subagents/consults (default):** bounded read-only advisers. An additional
  write assignment creates concurrency and therefore activates this overlay.
- **Coordinator (optional):** routes an explicitly activated multi-writer wave
  and does not compete with its writers.
- **Write worker (optional):** sole writer for the assigned path/resource set.
- **Integration preparer (optional):** proposes integration order, conflict
  resolution, and canonical-state reconciliation after writers finish. The
  active implementation owner writes and accepts the final commit.
- **Acceptance reviewer (optional):** independently attacks an integrated
  result when consequence or uncertainty warrants it; final acceptance remains
  with the active implementation owner.

Unknown write or process ownership remains read-only. No task terminates an
unknown process, deletes unknown artifacts, or overwrites another writer's
changes.

## Durable And Local State

Durable public-safe policy and accepted truth stay in tracked source:

- [`AGENTS.md`](../AGENTS.md) for repository routing and boundaries;
- [`goal.policy.md`](../goal.policy.md) for the normal operating and authority
  model;
- [`goal.campaign.md`](../goal.campaign.md) for campaign priorities;
- [`goal.md`](../goal.md) for the mutable current-slice baton;
- [`CONTRIBUTING.md`](../CONTRIBUTING.md) for contributor gates;
- [`LOCAL_LAB_OVERLAY.md`](../LOCAL_LAB_OVERLAY.md) for private payload and
  evidence roots.

Volatile coordination state remains ignored/local when the overlay is active:

- thread/session identifiers;
- temporary write and resource claims;
- process identities and private proof paths;
- raw reports, prompts, logs, and tool transcripts;
- disposable worktrees and scratch artifacts.

Sanitize accepted findings into ordinary source, tests, contracts, docs, or
state. Do not make local coordination records the only durable source of truth.

## Overlay Contracts

- [WORKSTREAM_CONTRACT.md](WORKSTREAM_CONTRACT.md) defines concurrent write
  ownership and integration boundaries.
- [RESOURCE_LEASES.md](RESOURCE_LEASES.md) defines optional shared-resource
  claims and collision safety. A claim never grants or withholds action
  authority.
- [REPORT_CONTRACT.md](REPORT_CONTRACT.md) defines reports for activated
  multi-role waves; ordinary single-writer slices use normal handoff/state
  updates.
- [AUTOMATION_STORAGE_GHIDRA_POSTURE.md](AUTOMATION_STORAGE_GHIDRA_POSTURE.md)
  preserves bounded automation, storage, evidence, and Ghidra safety rules.

Standing and fresh action authority comes only from
[`goal.policy.md`](../goal.policy.md) plus a newer direct maintainer instruction
or explicit campaign-owner delegation, not from this overlay.
