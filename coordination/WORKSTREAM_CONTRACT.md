# Workstream Contract

Status: active
Last updated: 2026-07-11

This contract applies when a coordinator assigns independent workers,
reviewers, an integration owner, and an acceptance reviewer across one campaign.
It supplements normal repo guidance; it does not relax payload, safety, release,
or installed-game rules.

## Ownership Rules

- One path family has one active write owner.
- One shared machine resource has one active owner.
- Unknown ownership means read-only.
- A worker must verify branch, worktree, base commit, allowed paths, forbidden
  paths, and dirty state before editing.
- A worker must not reset, clean, stash, discard, or overwrite work it did not
  create.
- A worker must not write directly to the coordinator checkout.
- A worker must not broaden scope because a nearby file is convenient.
- A review or acceptance thread must not edit tracked files.

High-collision path families are exclusive by default:

- `goal.md`, `goal.policy.md`, `AGENTS.md`, `CONTRIBUTING.md`, and this
  `coordination/` contract
- `developer_agent_state.json`, `documentation_agent_state.json`, and
  `re_orchestrator_state.json`
- `CURRENT_CAPABILITIES.md`, shared release/readiness indexes, and release
  front-door docs
- `package.json` and central validation scripts
- `patches/` catalogs and profile catalogs
- `OnslaughtCareerEditor.WinUI/Pages/BinaryPatchesPage.xaml*`
- `OnslaughtCareerEditor.WinUI/Helpers/PatchBench*.cs` and related
  presentation models
- shared `OnslaughtCareerEditor.AppCore/` services
- shared `OnslaughtCareerEditor.UiTests/` files
- release packaging/probe scripts

Do not assume two tasks are independent merely because their intended product
outcomes differ. If they need the same large file or semantic owner, serialize
them.

## Worker Duties

Each write worker receives a self-contained assignment that names:

- worker ID and concise persistent goal
- base commit, branch, and worktree
- allowed and forbidden paths
- claimed path and resource leases
- current repo truth relevant to the slice
- required files to read before editing
- claim boundary and explicit non-claims
- focused and broad-enough validation gates
- review-envelope reference and any required refresh trigger, or explicit
  `CONSULT_UNAVAILABLE` / `CONSULT_BOUNDARY` records for missing lanes
- report paths and commit authority
- stop conditions and integration dependencies
- terminal record: exactly one of `ADVANCEMENT` or `BLOCKED_*`
- acceptance owner or review lane separate from the producing worker

For automation, storage, Ghidra/headless, proof-retention, or campaign-posture
work, the assignment must also cite
[AUTOMATION_STORAGE_GHIDRA_POSTURE.md](AUTOMATION_STORAGE_GHIDRA_POSTURE.md)
and say whether the slice is real project advancement or hygiene-only.

The worker parent thread is the writer. Subagents advise unless explicitly
assigned an isolated non-overlapping write task.

## Canonical State

Workers do not all edit canonical state batons during a campaign wave. They
record recommended state/docs updates in their local reports. The integration
thread owns one coherent reconciliation pass for:

- `goal.md`
- `developer_agent_state.json`
- `documentation_agent_state.json`
- shared readiness/front-door docs
- cross-slice claim boundaries and next work

Non-integration workers may recommend these updates in local reports, but do
not write or commit them. Only the integration owner writes canonical state for
the campaign wave.

Recurring automation writers must re-read canonical state and leases immediately
before editing or committing if another active lane may have changed them. If
the state epoch, base commit, lease owner, or active slice changed since the
assignment was read, stop and route to the coordinator or integration owner.

## Stop Conditions

Stop and escalate when:

- target branch/worktree/base commit does not match assignment
- target paths are dirty with changes the worker did not make
- ownership is unclear or contested
- a needed resource lease is unavailable
- a change would mutate the installed Steam folder or original `BEA.exe`
- a change would add hard payloads, arbitrary saves/options, raw proof logs,
  screenshots/frame dumps, copied executables, full Ghidra databases, secrets,
  `.env*`, build output, or local runtime caches
- a claim would exceed evidence, especially around online readiness, runtime
  audio, gameplay parity, release packaging, or static RE proof
- validation cannot be run and no bounded fallback evidence is available
- a lane cannot produce an accepted `ADVANCEMENT` or well-formed `BLOCKED_*`
  closeout record
- required consults are unavailable for privileged, release, runtime, live
  Ghidra mutation, destructive cleanup, account/provider, or paid-spend work

## Advancement Boundary

A worker cycle must end in exactly one of `ADVANCEMENT` or a well-formed
`BLOCKED_*` record. A worker may report real project advancement only when a
bounded source, docs, checker, proof-plan, policy, or state change has been
accepted under a named evidence class. Hygiene-only work such as status checks,
storage inventory, re-reading, mirror refresh, or passing validation gates is
useful but must be labeled as hygiene-only unless it removes a named blocker
and names the next advancement slice.

Hygiene-only slices may run only to clear a named blocker or preserve an active
claim boundary. They must name the blocked lane or next executable advancement
slice they unblock. The producing lane cannot self-accept its own advancement
claim.

A `BLOCKED_*` record must include `code`, `evidence`, `prior_attempt`, `owner`,
`next_action`, `retry_after` no later than 24 hours, and `duplicate_check`.
Unresolved adversarial blocker findings also force a blocked terminal record
unless the coordinator or integration owner records an explicit override.

## Substantive Work And Authority

Treat a coherent product, source, test, tooling, docs, state, or policy
objective as substantive when its scope, behavior, authority, trust boundary,
or acceptance evidence needs independent judgment. RE maps, Ghidra/headless,
proof, storage, release, runtime, account, spend, disputed, broad, or
high-collision work is substantive.

Each substantive objective or related release batch gets one review envelope
under the global Codex multi-agent lane contract. Codex-owned normal/adversarial
subagents inherit the parent effort by default or use an explicit task-specific
supported effort override. The envelope also includes bounded external
normal/adversarial consults when the required read-only
sandbox and authentication are available. Routine implementation, validation,
formatting, and state follow-through inside that envelope do not recursively
launch new reviews. If a lane is unavailable or unsafe to brief, record the
exact reason and the focused Codex-root verification or
coordinator/integration-owner override used to continue.

Runtime proof, live Ghidra mutation, destructive cleanup, release,
external-account action, and spend require a structured baton authority naming
the action family, allowed and forbidden commands, leases, proof/storage root
policy, validation gates, cleanup/rollback, expiration, and spend cap when
applicable.
