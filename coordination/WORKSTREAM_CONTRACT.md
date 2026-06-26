# Workstream Contract

Status: active
Last updated: 2026-06-26

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
- required consult/review, or explicit none with rationale
- report paths and commit authority
- stop conditions and integration dependencies

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
