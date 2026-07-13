# Goal Policy

Status: active public-primary charter
Last updated: 2026-07-11

This file is the durable charter for repo `/goal` loops. It should change
rarely. The mutable current slice lives in `goal.md`.

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

Use `goal.md` as the current mutable baton:

1. Pick one bounded slice that advances the charter.
2. Read current repo evidence before acting.
3. Prefer read-only inspection and generated/exported evidence before mutation.
4. Make focused changes.
5. Validate with targeted and broad-enough local gates.
6. Update docs/state/evidence/accounting.
7. Rewrite `goal.md` to the next safe executable slice after a green closeout.
8. Commit/push the green wave when authorized.

Every automation, worker, or `/goal` cycle must close with exactly one primary
deliverable:

- `ADVANCEMENT`: an accepted bounded source, docs, checker, proof-plan, policy,
  state, RE map, Ghidra/static-analysis, integration, or push artifact under a
  named evidence class. Acceptance must come from a different lane, integration
  owner, acceptance owner, or human gate; the producing lane cannot self-accept
  terminal success.
- `BLOCKED_<root-cause-slug>_<yyyymmdd-hhmm>`: a well-formed blocker record
  with `code`, `evidence`, `prior_attempt`, `owner`, `next_action`,
  `retry_after` no later than 24 hours, and `duplicate_check`. Repeating the
  same blocker without a new attempt or owner escalation is not progress.

Hygiene-only activity such as status checks, re-reading files, mirror refresh,
or validation gates does not count as advancement unless it removes a named
blocker and records the next real advancement slice it unblocked. If no concrete
advancement is available, record a well-formed blocker instead of widening
scope or repeating status work.

Do not mark a broad goal complete unless the actual charter requirements are
proven complete. If the current work is only a slice, close the slice and
continue.
