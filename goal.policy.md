# Goal Policy

Status: active public-primary charter
Last updated: 2026-07-14

This file is the durable charter for repo `/goal` loops. It should change
rarely.

| File | Role |
|------|------|
| **This file** (`goal.policy.md`) | Rarely changing charter, boundaries, loop contract |
| [`goal.campaign.md`](goal.campaign.md) | Durable multi-lane milestone map; update on milestone land/block |
| [`goal.md`](goal.md) | Mutable baton: current slice, progress, closed ledger |
| [`roadmap/goals/full-rebuild-campaign-slash-goal.md`](roadmap/goals/full-rebuild-campaign-slash-goal.md) | Canonical long-running `/goal` text |

## Long-Horizon Charter

Preserve and reverse engineer Battle Engine Aquila / Onslaught, keep the WinUI 3
product lane primary for current user-facing tooling, and turn static/runtime
evidence into practical tooling, patches, mods, asset workflows, online-play
research, and an executable RE-informed original-code rebuild. Preserve a
separately staffed strict clean-room path as a future option rather than
mislabeling exposed implementation work.

The public repository is now the primary collaboration and day-to-day working
repo. The goal is not a sparse export. Track source, tools, tests, docs, RE
notes, wave notes, state batons, agent reports, readiness notes, and compact
proof summaries when they help contributors understand or continue the project.

### Multi-slice campaign mode

When the active `/goal` points at the full reconstruction campaign (see
`roadmap/goals/full-rebuild-campaign-slash-goal.md`), agents **must not** treat
a single slice as the entire goal. They:

1. Execute one bounded Current Slice from `goal.md`.
2. Close with `ADVANCEMENT` or well-formed `BLOCKED_*`.
3. **Select the next slice themselves** using `goal.campaign.md` priority order.
4. Rewrite `goal.md` Current Slice for resume.
5. Continue until campaign exit criteria, a human pause, or a blocker that truly
   needs operator authority (runtime lease, release, paid spend, Steam-adjacent
   risk, or exhausted retries).

Agents may choose work across **RE**, **rebuild**, **WinUI 3**, **lore**, and
**test harnesses**. Prefer measurement-before-Core for retail-derived behavior.
Build or extend durable harnesses with each land. Keep lab storage bounded
(safe-copy while running; strip bulky trees after closeout).

## Hard Payload Boundary

Keep these out of git and out of app release ZIPs unless a later explicit legal
and technical decision changes the rule:

- actual Battle Engine Aquila executables, DLLs, archives, media, manuals,
  extracted asset payloads, and local save/options payloads other than the
  tracked `tests_shared/fixtures/gold_career_save.bin` regression fixture
- copied game profiles, copied executable/runtime output, screenshots/frame
  dumps, raw CDB logs, and bulky generated runtime proof captures
- full Ghidra project databases/backups
- secrets, `.env*`, credentials, tokens, local config, and machine-only runtime
  caches
- build/test/package outputs

Represent those areas with source code, scripts, schemas, docs, hashes, compact
proof summaries, and reproducible checkers instead of shipping the payloads.

## Authority Boundaries

- Keep the installed Steam game folder and original `BEA.exe` read-only.
- Use copied profiles, copied executables, app-owned artifact roots, or local
  proof roots for mutation, runtime proof, generated outputs, screenshots,
  frames, caches, and test saves.
- Codex root remains final owner of edits, validation, state updates, commits,
  pushes, publication, and acceptance.
- Each substantive objective or related release batch requires one bounded
  normal/adversarial review envelope under the global Codex multi-agent lane
  contract before terminal acceptance. Under the current direct user policy,
  every new or resumed Codex-owned worker uses `gpt-5.6-sol` at medium effort by
  default; harder work may raise the supported Sol effort. Do not fall back to
  Terra or Luna, and do not lower or change this route without a newer direct
  user instruction.
  Bounded external normal/adversarial consults use the canonical read-only
  posture when the required sandbox and authentication are available. Trivial lookups, formatting, and
  routine follow-through inside an accepted envelope do not create recursive
  consult loops. If an external prompt cannot be safely bounded, record
  `CONSULT_BOUNDARY:<lane>:<reason>` and use focused Codex-owned review. If a
  required lane is unavailable, record
  `CONSULT_UNAVAILABLE:<lane>:<reason>` with the exact failure. Refresh the
  envelope only when target, scope, mutation class, authority, trust boundary,
  or acceptance evidence materially changes.
- Runtime proof, live Ghidra mutation/read-back, destructive cleanup,
  release/publication, account/provider action, and paid spend require explicit
  baton authority naming the action family, allowed commands, forbidden
  commands, resource leases, proof/storage root policy, validation gates,
  cleanup/rollback, expiration, and maximum spend if applicable. Absence of any
  field means no authority.
- Coordinated multi-thread campaigns use the additional contract in
  [coordination/README.md](coordination/README.md): the coordinator is a control
  plane, workers own only leased scopes in isolated worktrees, reviewers and
  acceptance are read-only, and the integration owner performs canonical
  merge/state/docs reconciliation after leases release.

## Technical Direction

- Static Ghidra closure remains rebuild-grade contract input, not automatic
  runtime proof.
- Runtime, visual, patch, mod, online, and rebuild proofs must stay bounded to
  their evidence.
- WinUI 3 remains the current primary Windows product lane unless a later
  explicit strategy change replaces it.
- Electron, WPF, and old Python GUI/CLI lanes stay archived/reference-only.
- Python remains active for RE/tooling/lab support.
- `rebuild/OnslaughtRebuild.Core` is the active deterministic simulation lane.
  Godot .NET is the promoted visual-client direction for the rebuild and must
  remain an adapter over Core. Blazor Hybrid, Tauri, and other alternatives are
  not parallel implementation lanes unless an evidence-backed decision changes
  the architecture.
- Historical proof plans are evidence, not implementation authority. Do not
  create recursive readiness/checklist/proof-plan chains when executable code,
  a focused test, or one plainly documented blocked dependency is the more
  direct artifact.

## Loop Contract

Read order for every `/goal` cycle: **policy → campaign → baton → path AGENTS**.

Use `goal.md` as the current mutable baton:

1. Pick one bounded slice that advances the campaign (self-select via
   `goal.campaign.md` when the durable campaign goal is active).
2. Read current repo evidence before acting.
3. Prefer read-only inspection and generated/exported evidence before mutation.
4. Make focused changes; add/extend a regression harness when behavior lands.
5. Validate with targeted and broad-enough local gates.
6. Update docs/state/evidence/accounting; update campaign milestone status when
   a milestone lands or blocks.
7. Rewrite `goal.md` Current Slice to the **next** safe executable unit after a
   green closeout (do not leave an empty “suggested candidates only” baton).
8. Commit/push the green wave when the active `/goal` text and this policy
   authorize it (no hard payloads; no force-push; no release/tag unless the
   goal explicitly names that family).

Every automation, worker, or `/goal` cycle must close with exactly one primary
deliverable:

- `ADVANCEMENT`: an accepted bounded source, docs, checker, proof-plan, policy,
  state, RE map, Ghidra/static-analysis, integration, harness, or push artifact
  under a named evidence class. For campaign mode, dual-accept measurement,
  landed Core+goldens, or product gate green counts as cycle advancement;
  **campaign-complete** still requires exit criteria in `goal.campaign.md` plus
  human or integration acceptance.
- `BLOCKED_<root-cause-slug>_<yyyymmdd-hhmm>`: a well-formed blocker record
  with `code`, `evidence`, `prior_attempt`, `owner`, `next_action`,
  `retry_after` no later than 24 hours, and `duplicate_check`. Repeating the
  same blocker without a new attempt or owner escalation is not progress.

Hygiene-only activity such as status checks, re-reading files, mirror refresh,
or validation gates does not count as advancement unless it removes a named
blocker and records the next real advancement slice it unblocked. If no concrete
advancement is available, record a well-formed blocker instead of widening
scope or repeating status work.

Do not mark the **campaign** complete unless `goal.campaign.md` exit criteria
are met. If the current work is only a slice, close the slice, advance the
baton, and continue.
