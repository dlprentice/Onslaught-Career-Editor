# Goal Policy

Status: active public-primary charter
Last updated: 2026-06-26

This file is the durable charter for repo `/goal` loops. It should change
rarely. The mutable current slice lives in `goal.md`.

## Long-Horizon Charter

Preserve and reverse engineer Battle Engine Aquila / Onslaught, keep the WinUI 3
product lane primary for current user-facing tooling, and turn the
static/rebuild evidence into practical tooling for patches, mods, asset
workflows, runtime proofs, online-play research, and eventual clean-room rebuild
work.

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
- Use bounded normal/adversarial consults for meaningful planning, UI/UX, copy,
  release readiness, repo tidiness, collaboration readiness, and broad/risky
  work when safe and available. If a lane is unavailable, usage-limited, unsafe
  to brief, or disproportionate for tiny/urgent work, record that and continue
  with Codex-root verification.
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
- Godot .NET, Blazor Hybrid, Tauri, and other rebuild/product UI options remain
  evaluation lanes until explicitly promoted.

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

Do not mark a broad goal complete unless the actual charter requirements are
proven complete. If the current work is only a slice, close the slice and
continue.
