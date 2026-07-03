# Resource Leases

Status: active
Last updated: 2026-07-03

Path isolation is not enough. Coordinated campaigns also require exclusive
leases for shared machine resources that can corrupt evidence, collide on the
desktop, or mutate local proof state.

## Exclusive Resources

Only one owner may hold each resource at a time:

- `interactive-winui-desktop`
- `native-uia`
- `bea-runtime`
- `cdb-debugger`
- `audio-loopback`
- `live-ghidra-project`
- `local-proof-archive-write`
- `storage-retention-or-cleanup`
- `release-package-build`
- `release-publication-or-account-action`
- `spend-action`
- `canonical-state-update`
- `main-branch-integration`

Unknown process or lease ownership means stop and escalate. No worker may kill
another worker's process or reuse another worker's proof root.

## Lease Record

The local campaign lease record should capture:

- campaign ID
- resource name
- owner worker/thread ID
- branch and worktree
- purpose
- acquired time
- expected release condition
- validation or cleanup command
- released time and terminal state

Keep the active lease record local/ignored. Fold only sanitized durable lessons
into repo docs or readiness notes.

## Cleanup Expectations

- BEA/CDB/audio proof work is serialized and must verify process cleanup.
- Native UIA and visual-smoke work is serialized when it shares the interactive
  desktop.
- Live Ghidra mutation or read-back is serialized.
- Storage retention, cleanup, and backup-producing work is serialized when it
  can move or delete Ghidra/proof material. The recurring storage sentinel is
  read-only unless a separate owner holds the cleanup lease and explicit
  authority.
- The storage/Ghidra sentinel cadence during active campaigns is every two
  hours. Each pass must verify or unblock one concrete storage posture item, or
  record `BLOCKED_NO_CONCRETE_WORK_AVAILABLE_<yyyymmdd-hhmm>` with checked
  roots, blockers, and next eligible action. A pass that only says "no change"
  is incomplete unless it records that blocker-style evidence.
- Release package builds are serialized when they share output folders or
  package names.
- Broad .NET build/test gates should run serially when contention can produce
  false failures.
- Workers do not terminate unknown processes. If a process blocks work and
  ownership is unclear, stop and ask the coordinator.

Publication remains a separate authority boundary, not a normal resource lease.
No lease authorizes GitHub Release publication, binary ZIP publication, signing,
installer release, Store publication, announcement, push, or capability
promotion. Those actions require separate explicit maintainer authorization.

Runtime proof, live Ghidra mutation/read-back, destructive cleanup,
release/publication, account/provider action, and paid spend require structured
baton authority in addition to any lease. The baton must name action family,
allowed commands, forbidden commands, affected resources, proof/storage root
policy, validation gates, cleanup or rollback plan, expiration, and spend cap
when relevant. A lease without that authority is read-only or no-op.
