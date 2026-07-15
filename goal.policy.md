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

Continuously reconstruct and enhance Battle Engine Aquila through one
evidence-backed, product-coupled portfolio. Research is valuable when it makes
a product decision possible; it is not a substitute for delivering the named
consumer. The portfolio has three shipping outcomes:

| Product outcome | Durable purpose |
|---|---|
| **WinUI Community** | Keep the WinUI Toolkit the community front door for preservation, safe-copy workflows, saves/options, patches/mods, local content, reconstruction discovery, and public releases. |
| **Playable Reconstruction** | Grow the deterministic Core and its clients into a playable, evidence-backed, RE-informed original-code reconstruction through consumer-complete vertical increments. |
| **Retail Enhancement** | Deliver meaningful tools, safe copied-target patches and mods, and evidence-gated progress toward original-game multiplayer. |

Static analysis, pinned source, copied-runtime observation, lore, asset
research, documentation, and harnesses are **supporting inputs**. They may be
necessary evidence or infrastructure, but their counts and completion are not
the portfolio's primary outcomes.

**Original-game multiplayer** is a strategic epic inside Retail Enhancement,
not a released capability. WinUI community release work remains a first-class
outcome when the exact artifact, claim, gates, and audience are ready.

The public repository is the primary collaboration and day-to-day working
tree. Track source, tests, tools, public-safe RE notes, state batons, readiness
notes, and compact proof summaries when they help contributors understand,
use, or continue the products.

### Reconstruction terminology

In this project, reconstruction means rebuilding game systems in new original
code from bounded binary, runtime, source-reference, and asset evidence while
keeping proprietary code and payloads out of the implementation and public
artifacts. The active implementation is an **evidence-backed, RE-informed original-code reconstruction**.
It is not parity-complete and is **not a strict clean-room implementation** because current implementers have seen
source and decompilation-derived material. A separately staffed unexposed
specification/implementation/acceptance process may pursue that narrower label
later; it is not required to keep building this reconstruction now.

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

## Product-Coupled Slice Contract

Every Current Slice records these fields before consequential implementation:

- **primary outcome:** WinUI Community, Playable Reconstruction, or Retail
  Enhancement;
- **user outcome:** what a player, modder, contributor, or maintainer can do or
  understand after the slice;
- **evidence question:** the smallest uncertainty that must be resolved;
- **exact consumer:** the code path, product surface, patch row, import path,
  or release artifact that will consume the result;
- **acceptance:** executable, deterministic, native, copied-runtime, visual, or
  release evidence that proves the consumer works;
- **non-claims:** nearby conclusions the evidence does not support; and
- **next link:** the immediate product increment or dependency that follows.

No second consecutive research-only slice may be selected unless a concrete
dependency makes another evidence step necessary. The baton must name that
dependency, the blocked exact consumer, and why a product implementation would
otherwise be unsafe or misleading. Absent that dependency, **every two accepted slices**
must contain at least one **user-observable result**. This is
a course-correction rule, not a quota for shallow UI or ceremonial work.

For this rule, evidence-debt, contract-only, checker-only, documentation-only,
and harness-only slices are research-only unless the same slice lands the
named consumer and its acceptance evidence. A user-observable result changes a
named path that a player, modder, or community user can invoke in WinUI, the
playable reconstruction, or a copied retail profile. Operator-only proof UI,
receipts, test-count growth, disabled chrome, and release-note wording do not
qualify by themselves.

The result must demonstrably complete or materially improve the named user
task through end-to-end consumer acceptance. Navigation-only shells, no-op
commands, inert scaffolds, and output with no usable effect do not qualify.

A behavior contract does not by itself land a product milestone. It may close
an evidence prerequisite or prevent a dangerous misimplementation, but the
milestone stays in progress until its named consumer and proportional
acceptance evidence land. Research/checker/documentation work that has no
credible exact consumer moves to backlog instead of becoming the next slice.

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

This policy records the maintainer's explicit standing decisions; it does not
manufacture authority merely by being read or by a goal being resumed. Every
use still depends on the still-current user scope, the named action family,
and the exact verified target. A later user instruction can narrow, revoke, or
supersede that standing authority.

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
publication remain prohibited rather than approval-gated. **Host/Join remains disabled**
until its distinct-endpoint and source-bound causality gates are
accepted. Standing online or publication authority cannot substitute for those
product-evidence gates.

## Technical Direction

- Steam static evidence can establish bounded released-code identity and
  structure; controlled copied-runtime evidence establishes observed causality,
  behavior, and measured values.
- WinUI 3 remains the community front door and released Windows toolkit. It is
  expected to discover, configure, launch, and explain reconstruction and
  retail-enhancement workflows as those consumers become ready. Electron,
  WPF, and the old Python GUI/CLI remain archived/reference-only.
- Python remains active for RE, validation, and local lab tooling.
- `rebuild/OnslaughtRebuild.Core` owns deterministic simulation truth. Godot is
  a presentation/input adapter over Core, not evidence of retail behavior.
- The active rebuild is evidence-backed, RE-informed original code, not
  parity-complete and not a strict clean-room implementation. It is separate
  by architecture and license but belongs to the shared product strategy.
- User-owned retail assets may be extracted or imported through local-only
  workflows. Proprietary payloads remain ignored/local and are never bundled
  into source or community releases.
- WinUI may discover, configure, and launch the separately licensed rebuild;
  GPL reconstruction code/artifacts retain their GPL obligations, while no
  proprietary retail bytes enter the GPL source tree or either release.
- Historical proof plans are evidence, not current authority. Prefer executable
  code, focused tests, bounded contracts, or one exact blocker over recursive
  readiness/checklist chains.

## Loop Contract

Read order for each campaign cycle: **policy → campaign → baton → applicable
AGENTS → slice-local evidence**.

For each slice:

1. Record the primary outcome, user outcome, evidence question, exact consumer,
   acceptance, non-claims, and next link in the active baton.
2. Check repository identity, current tip, dirty paths, and the active baton.
3. Read the directly relevant source, policy, provenance, and proof boundary.
4. Make focused changes without overwriting unrelated work.
5. Add or extend a proportional automated harness when behavior or a durable
   operating contract changes.
6. Run the smallest gate set that proves the consumer and disclose skipped proof
   classes.
7. Update public-safe docs/state only to verified truth; keep raw evidence
   ignored/local.
8. Commit and push a green wave when useful. Never force-push.
9. Leave `goal.md` with the next safe executable Current Slice and continue
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

“No meaningful authorized product work remains” is true only after root has
walked every tier of the consumer-first picker and recorded an exact blocker,
owner, next action, and reopen condition for every remaining material item.
One blocked slice, one unavailable runtime, or one exhausted evidence path is
never sufficient while another safe product consumer remains actionable.
