# Shared Resource Claims

Status: optional concurrency overlay
Last updated: 2026-07-15

This file retains its historical name for links, but a “lease” is now a local
resource claim used only to prevent concurrent collisions. It does not grant or
withhold action authority.

In normal single-root operation, the active root action owns the resource it is
using and records enough process/project/artifact identity to prove ownership
and cleanup. No separate lease form, coordinator approval, expiration block, or
worker lane is required.

A claim has no automatic time-based expiry. After a crash or root handoff, a
successor verifies the repository baton, prior owner absence, resource identity,
and relevant process/project/publication state before reclaiming it. Ambiguous
ownership remains read-only. Push/publication succession also requires exact
remote branch/tag/release/artifact read-back so a vanished local process cannot
hide an in-flight external completion.

When root deliberately activates concurrent work, only one operation may claim
each collision-prone resource at a time:

- `interactive-winui-desktop`;
- `native-uia`;
- `bea-runtime`;
- `cdb-debugger`;
- `audio-loopback`;
- `live-ghidra-project`;
- `local-proof-archive-write`;
- `storage-retention-or-cleanup`;
- `release-package-build`;
- `release-publication-or-account-action`;
- `spend-action`;
- `canonical-state-update`; and
- `main-branch-integration`.

Unknown process or resource ownership means do not mutate, reuse, terminate, or
delete it. Root may identify the owner safely, wait, or choose an independent
slice.

## Optional Claim Record

For an activated multi-writer wave, a short ignored/local activation record is
required and captures:

- campaign or wave label;
- resource and owner;
- repository/worktree when relevant;
- purpose and acquisition time;
- identity receipt or proof root;
- expected release/cleanup check; and
- release time and terminal state.

The record is collision control, not an authority baton. Exact local process,
project, proof, and storage paths remain private.

## Cleanup And Serialization

- BEA, debugger, and audio work is serialized and ends with an identity-bound
  relevant-process census.
- Native UIA/visual work is serialized when it shares the interactive desktop.
- Live Ghidra writes are serialized and retain complete backup, read-back, and
  rollback evidence.
- Storage cleanup never deletes ambiguous or irreplaceable evidence under a
  normal-cleanup claim.
- Broad .NET builds/tests run serially when contention can create false
  failures.
- Release package builds and publication actions confirm exact artifact,
  commit, repository/account, and output identity before mutation.
- No operation terminates an unknown process or reuses another operation's
  proof root.

Normal cleanup covers only processes, copied profiles, build/test output, and
ignored evidence roots created and owned by the current action or separately
verified as disposable before the action through an action receipt/provenance
identifier and exact allowed path class. Pre-existing, unknown, retained, or
shared profiles, artifacts, proof, Ghidra material, crash debris, and output are
never normal-cleanup targets. A successor does not inherit a prior action's
disposable set merely by reclaiming the resource. Spending and genuinely
destructive operations remain fresh-authorization boundaries under
`goal.policy.md`.

Publication authority, release readiness, evidence acceptance, and destructive
authority do not come from a resource claim. Conversely, standing authority in
`goal.policy.md` does not allow two owners to mutate the same resource
concurrently.
