# Goal Policy

Status: active public-primary charter
Last updated: 2026-07-15

This file is the durable charter for repository `/goal` loops. It should change
rarely.

| File | Role |
|------|------|
| **This file** (`goal.policy.md`) | Rarely changing charter, authority, boundaries, loop contract |
| [`goal.campaign.md`](goal.campaign.md) | Durable milestone map and next-slice priority |
| [`goal.md`](goal.md) | Mutable baton: current slice, progress, resolved/skipped blockers |
| [`roadmap/goals/full-rebuild-campaign-slash-goal.md`](roadmap/goals/full-rebuild-campaign-slash-goal.md) | Canonical long-running `/goal` text |

## Long-Horizon Charter

Preserve and reverse engineer Battle Engine Aquila / Onslaught, keep the WinUI
3 product lane primary for current user-facing tooling, and turn bounded static
and copied-runtime evidence into practical tooling, patches, mods, asset
workflows, online-play research, and an executable RE-informed original-code
rebuild. Preserve a separately staffed strict clean-room path as a future
option rather than mislabeling exposed implementation work.

The public repository is the primary collaboration and day-to-day working
tree. Track source, tests, tools, public-safe RE notes, state batons, readiness
notes, and compact proof summaries when they help contributors understand or
continue the project.

## Single-Root Default

The active Codex root task is the normal owner of implementation, integration,
validation, state updates, version control, and final acceptance. It works in
the active repository checkout, preserves unrelated dirty work, and serializes
overlapping mutations.

Exactly one task is the current root. If two tasks could plausibly claim root
ownership, neither performs a consequential mutation, push, publication, or
external action until the repository baton and current user/task ownership
identify one root; safe read-only work may continue.

Only the currently active root task exercises standing campaign authority for
consequential runtime, Ghidra, version-control, release/publication, or external
actions. A root-created writer receives only its explicit bounded write scope;
it does not inherit ambient mutation, publication, account, or acceptance
authority.

Subagents and external consults are bounded advisers by default. Root uses them
when independent judgment, adversarial review, or domain specialization adds
material value. Root may explicitly assign a bounded non-overlapping write task
to a subagent, but does not create persistent worker lanes merely to satisfy
ceremony.

Shared-machine ownership is an execution-safety mechanism, not a permission
gate. Root serializes BEA, debugger, live Ghidra, native desktop, broad build,
and publication actions; verifies the exact process, path, hash, start time,
window/module, project, backup, artifact, or external target as applicable; and
records bounded cleanup. Root never terminates an unknown process or overwrites
unknown work. It can wait, disambiguate safely, or advance another independent
slice.

The contracts under [`coordination/`](coordination/README.md) are an optional
coordination overlay. Root activates them only for deliberately concurrent
writers, recurring automation, independent acceptance roles, or a shared-
resource wave that needs durable handoffs. Ordinary single-root work does not
require a coordinator, isolated worker worktree, resource lease, worker report,
or separate integration owner.

Resource claims do not expire merely because time passes. After a crash or task
handoff, a successor root re-reads the repository baton and verifies that the
prior root no longer owns a relevant process, project write, proof publication,
or external action before reclaiming it. Unknown ownership remains read-only;
the successor advances another slice rather than guessing or killing an
unknown process. Before a successor pushes or publishes, it also reads back the
exact remote branch, tag, release, artifact, and publication identity to reject
an absent-owner-but-still-completing prior action.

## Multi-Slice Campaign Mode

The durable reconstruction campaign is not one slice. Root:

1. Executes one bounded Current Slice from `goal.md`.
2. Closes it with a verified advancement or an exact skipped blocker.
3. Selects the next safe slice using `goal.campaign.md` priority.
4. Rewrites `goal.md` into resume-ready state.
5. Continues until campaign exit criteria, a human pause, or no meaningful
   authorized work remains.

A blocked slice does not block the whole campaign while another safe,
authorized, material slice exists. Missing coordinator records, worker leases,
redundant acceptance roles, or a separately enumerated runtime baton are not
blockers for work covered by the standing campaign authority below.

Prefer measurement before Core for retail-derived behavior: bounded static
analysis and authorized copied-runtime observation produce an accepted public-
safe behavior contract before retail-derived deterministic implementation.
Build or extend the smallest durable behavioral, visual, capture/replay, or
regression harness that can replace subjective verification.

## Hard Payload Boundary

The installed Steam game and original `BEA.exe` remain immutable. Use copied
profiles, copied executables, app-owned artifact roots, and ignored local proof
roots for runtime, debugger, patch, mutation, screenshot, cache, and test-save
work.

Proprietary evidence remains local. Do not track or publish actual game
executables, DLLs, archives, media, manuals, extracted assets, copied profiles,
arbitrary saves/options, screenshots/frame dumps, raw debugger logs, bulky
runtime captures, full Ghidra databases/backups, secrets, credentials, local
config, or build output. The tracked immutable regression fixture
`tests_shared/fixtures/gold_career_save.bin` remains the narrow save exception.

Represent private areas with original source, schemas, scripts, hashes, compact
summaries, and reproducible checkers rather than shipping their payloads.

Classify local material before cleanup:

- **immutable:** installed game/original executable and other protected inputs;
- **retained/shared:** live Ghidra projects, verified backups, proof archives,
  user data, reusable copied profiles, and any artifact with ambiguous
  ownership;
- **action-owned disposable:** an item created and owned by the current action
  or separately verified as disposable before that action starts through an
  action receipt/provenance identifier and exact allowed path class.

Normal cleanup applies only to action-owned disposable material. It never
deletes an unknown, pre-existing, retained, shared, or immutable item.
Crash debris without a valid action receipt/provenance record is retained until
classified; a successor root does not inherit the prior action's disposable set
merely by taking over the baton.

## Standing Campaign Authority

The maintainer has supplied standing authority for these actions when they are
in scope for the durable campaign and their exact target is known:

- normal source, test, documentation, state, and harness changes;
- commits and pushes to the configured project repository without force-push;
- copied-runtime launches, controlled input, debugger attachment, read-process
  memory, and process-memory mutation;
- patching and mutation of copied executables and copied profiles;
- live Ghidra inspection, mutation, save, and read-back with complete verified
  backup and rollback discipline;
- normal cleanup of processes, copied profiles, build/test output, and ignored
  evidence roots created and owned by the current action or separately verified
  as disposable before the action; and
- tags, releases, publication, and project-scoped external actions when a
  campaign slice calls for them, applicable gates pass, and evidence supports
  the published claim.

Before any copied-runtime, copied-executable, copied-profile, debugger, input,
or process-memory mutation, root resolves path/hash/process-image identity and
proves the target is the intended copy rather than the installed game or
original executable. Identity ambiguity fails closed.

Standing project-scoped external actions are limited to the configured source
repository and its established project surfaces: non-force Git writes,
issue/PR/project metadata actions, creation of unused tag/release/publication
identities, additive publication of the exact verified project artifact, and
project announcements to an already identified project channel/audience. A
current slice must name the exact target and action; “project-scoped” is not an
open alias for billing, spend, credential changes, account/provider
administration, unrelated deployment, or a novel audience.

Standing authority removes repeated approval requests. It does not remove
receipt-bound identity, attempt caps, input ownership, arm gates, backup,
validation, rollback, evidence, cleanup, or final process-census requirements.
It does not make a release necessary, turn release authority into release
readiness, or allow a claim beyond its evidence.

The maintainer explicitly classified evidence-gated tags, releases,
publication, and project-scoped external actions to the configured project
surface as standing-authorized actions for this campaign. Creating them is not
treated as a fresh destructive-authority request. Later deletion, replacement,
history rewriting, or withdrawal can still be genuinely destructive and is
evaluated separately. Standing creation requires an unused exact identity;
moving an existing tag, overwriting/replacing an existing release artifact,
retargeting published identity, or withdrawing published truth requires fresh
destructive authority.

Before an external action, root confirms the configured repository, account,
channel, audience, artifact, commit, or host and the intended action. A novel or
ambiguous external target is clarified before use; target verification is not a
return to coordinator or lease ceremony.

Live Ghidra mutation hard-stops before the first write when the complete backup
or disposable read-only open cannot verify, and stops the batch at the first
apply/read-back mismatch. Continuing without the verified rollback endpoint is
not a standing-authorized shortcut.

## Fresh Authorization Required

Fresh maintainer authority is required for:

- spending or any action that can incur a charge; and
- genuinely destructive or irreversible operations beyond normal cleanup,
  including force-push or history rewriting, deletion of ambiguous or
  irreplaceable proof/backups, broad storage pruning, and destructive changes
  outside an invocation-owned disposable root.

Installed-game/original-executable mutation and proprietary-payload
publication remain prohibited rather than approval-gated. Host/Join remains
disabled until its distinct-endpoint and source-bound causality gates are
accepted. Standing online or publication authority cannot substitute for those
product-evidence gates.

## Technical Direction

- Steam static evidence can establish bounded released-code identity and
  structure; controlled copied-runtime evidence establishes observed causality,
  behavior, and measured values.
- WinUI 3 remains the primary Windows product lane. Electron, WPF, and the old
  Python GUI/CLI remain archived/reference-only.
- Python remains active for RE, validation, and local lab tooling.
- `rebuild/OnslaughtRebuild.Core` owns deterministic simulation truth. Godot is
  a presentation/input adapter over Core, not evidence of retail behavior.
- The active rebuild is RE-informed original code, not parity-complete and not
  a strict clean-room implementation.
- Historical proof plans are evidence, not current authority. Prefer executable
  code, focused tests, bounded contracts, or one exact blocker over recursive
  readiness/checklist chains.

## Loop Contract

Read order for each campaign cycle: **policy → campaign → baton → applicable
AGENTS → slice-local evidence**.

For each slice:

1. Check repository identity, current tip, dirty paths, and the active baton.
2. Read the directly relevant source, policy, provenance, and proof boundary.
3. Make focused changes without overwriting unrelated work.
4. Add or extend a proportional automated harness when behavior or a durable
   operating contract changes.
5. Run the smallest gate set that proves the change and disclose skipped proof
   classes.
6. Update public-safe docs/state only to verified truth; keep raw evidence
   ignored/local.
7. Commit and push a green wave when useful. Never force-push.
8. Leave `goal.md` with the next safe executable Current Slice and continue
   unless the user asked to stop.

Record a blocker with a specific code, evidence, prior attempt, owner, and next
action. A retry time is useful only when time or external state can change the
result; it is not mandatory ceremony. Do not repeat a blocker without new
evidence, and do not elevate one blocked slice to whole-goal `blocked` while an
independent advancement remains.

Do not mark the campaign complete merely because one or several slices landed.
Completion requires the exit criteria in `goal.campaign.md`, verified green
state, a resume-ready backlog/non-claim record, and human or root integration
acceptance.
