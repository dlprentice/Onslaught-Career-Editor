# Onslaught Toolkit: agent guide

Status: active — the single instruction file for this repository; `CLAUDE.md` only points here
Last updated: 2026-09-12 (conditional reference routing; preservation and phase boundaries retained)
Summary: active development authority, evidence and data protections, task-specific reference routing,
and proportional completion checks.

Read this before changing anything. Read `~/AGENTS.md`, `~/Projects/AGENTS.md` and
`~/Projects/game-dev/AGENTS.md` explicitly when automatic discovery stops at this Git root;
this repository guide is more specific and wins here.

## What this is

A preservation project for *Battle Engine Aquila* (2003) with three coequal outcomes: reverse the retail game so it
can be understood, patched and modded; rebuild it in Godot at 1:1 behavioral parity; and ship a Godot toolkit
companion for Linux and Windows for careers, saves, safe copies, patches and media. RE feeds the rebuild,
the rebuild exposes the next retail questions, and both make safe app features possible.
[`GOAL.md`](GOAL.md) states the standing outcomes,
[`PROGRAM.md`](PROGRAM.md) is the work queue, [`CURRENT_CAPABILITIES.md`](CURRENT_CAPABILITIES.md) says what is
proven today. David's September 6 direction keeps this repository and consolidates
implementation responsibilities; older Blazor/Uno and repository-split recommendations
in `~/Projects/game-dev/PLAN.md` are superseded.

David replaced the WinUI 3 development lane with the Godot companion on September 6.
Keep the existing WinUI/AppCore source as migration material. After the completed
baseline report, David authorized the first Godot Save Lab workflow. Existing Windows
release procedures describe the retained implementation, not a queued WinUI release.

Linux owns development and native Godot execution. The rebuild now has Linux build/run/smoke/capture
commands, and the companion has a native Save Lab shell backed by portable AppCore. The complete player
walkthrough and Save Lab UI write/reopen acceptance remain unfinished; read `CURRENT_CAPABILITIES.md`.
The full legacy AppCore suite, WinUI, Windows-targeted CLI and portable ZIP retain Windows dependencies.
David retired the never-built Windows VM and its installer media on September 12. No local Windows
validation environment is provisioned; Linux evidence does not establish Windows behavior.
While David uses the desktop, continue code/RE and noninteractive checks;
wait for him to announce availability before resuming live input or visible launches.

David resumed scoped development on September 6 after accepting the baseline and
assessment. The active phase covers native Linux Godot launch/input/audio/capture,
the complete player-input Level 100 route, targeted RE, the first Godot Save Lab
workflow, and real World 110 construction/transition. Refactor and consolidate where
these deliverables require it; keep the three standing outcomes. The former storage
hold is retained as history in `developer_state.json`; it does not block this phase.
Do not recreate Windows VM staging without a new Windows-validation task. Ghidra changes still require the preservation workflow
and an exact declared cohort. External archive reconciliation and historical recovery
investigation remain outside this repository's development scope. Use native subagents;
do not use Claude Code during this phase.

## Ground rules

- Game/save writes require an informed user choice and a verified recovery copy before overwriting original
  data; `BinaryPatchEngine.AuthorizeInstalledGameWrite` in AppCore is the model. Never manufacture an
  "original" from an already modified file, and never destroy career data as a side effect.
- The pristine specimen (`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256 `74154bfa…`)
  is the byte-measurement baseline: read it, never write
  it. Every byte or address finding names the specimen it was read from, with its hash. The lab folder's
  `BEA.exe` is patched. The Linux Steam executable matched the pristine hash on September 6; measure the
  exact selected file before making a new claim. Old Windows-install descriptions are not Linux identities.
- Do not synthesize `.bes` saves. Start from a real baseline and preserve length, reserved fields and unknown
  bytes. `tests_shared/fixtures/gold_career_save.bin` is the one tracked save.
- Never track retail binaries or assets, converted retail material, arbitrary saves, raw debugger logs, bulky
  captures, Ghidra backups or alternate projects, credentials or `.env*`; `npm run test:safety` enforces the
  boundary. A small registered set of the app's own screenshots is the one allowance
  (`reverse-engineering/project-meta/attribution.md`, checked by `tools/check_registered_screenshots.py`).
- Every behavior claim cites a capture, byte comparison, focused test, or pinned source file and line. Decompiler
  output, a plausible name or a model's opinion proves nothing. Static evidence establishes identities and
  structures; only controlled runtime evidence establishes causality and values. Write unknowns as open questions
  with the cheapest falsifier, never as guessed names.
- `developer_state.json` → `current_re_authority` owns the campaign generation, READY/reducer pins and the verify
  command. Do not copy those values into prose (`tools/doc_current_authority_check.py` rejects it) and run
  complete-RE verification only through `current_re_authority.verify`.
- Ghidra has exactly two homes on this laptop plus one cold copy: the tracked checkpoint
  `reverse-engineering/ghidra/` (`db.18634`, never opened for writing), the working project
  `local-lab/ghidra-projects/BEA/BEA.gpr` (Ghidra 12.1.3, the only writable one), and
  `/srv/archive-a/onslaught-ghidra-cold/` (dated copies, verified cohort PRE/POST backups and the sealed
  historical package; restore a copy, never open it in place). Read the measured working version and
  latest correction in `developer_state.json` → `current_re_authority.latestLiveGhidraState`.
  Necessary semantic work must have an exact mutation plan; its
  declared cohort proceeds through the promotion gate in `reverse-engineering/ghidra/README.md` without
  another permission request for each ordinary gate. An open Ghidra MCP connection is access, not permission
  to invent a different mutation scope.
- `local-lab/` and `local-data/` are real writable directories inside this checkout, ignored by Git, not
  symlinks or separately mounted recovery views. The complete checkout physically resides at
  `/srv/archive-b/Onslaught-Career-Editor`; the familiar Projects path bind-mounts the same files.
  `~/ProjectData` is gone and stays gone. Carry out the approved organization plan under `~/AGENTS.md`:
  exact moves, hash-proven duplicate retirement and routing repairs do not need another batch-number reply.
  Record targets, evidence and outcomes in `~/Work/storage-migration-2026-08-29/DELETE-QUEUE.md`; preserve
  unique work and explicit KEEP holds, and ask about uncertain/last-copy loss or genuinely new scope. A
  2026-08-06 cleanup deleted frozen campaign inputs whose identities were pinned in tooling, so before calling
  anything stale, grep the tooling and tests, not only the docs.
- Never run `git clean` at the repository root (`-x`/`-X` would erase the lab) and never stage the lab with a broad
  `git add`; add paths explicitly. Preserve unrelated work in a dirty tree and make the smallest change that closes
  the contract.
- The rebuild is GPL: it may adapt the pinned GPL source in `references/Onslaught` and consume locally materialized
  retail data; retail executables, decompiler output and separately licensed material stay out of it
  (`rebuild/PROVENANCE.md`). `OnslaughtRebuild.Core` stays deterministic and free of presentation, filesystem,
  clock, process, network and GPU APIs.
  Using Godot for the companion does not merge MIT application code, GPL rebuild code
  and private retail material into one licensing boundary.
- Reviews by other agents or models are optional and follow `reverse-engineering/REVIEW-PROTOCOL.md`: read-only
  lanes, reports are input to reproduce rather than authority, and hosted reviewers never receive retail material
  or secrets.
- Reuse existing tooling and records; avoid duplicate test frameworks, broad routine matrices and new status
  or handoff files. Add a focused test when a real behavioral gap needs one. Hosted CI and release automation
  are outside this phase. Use a branch or repo-local `.worktrees/` when useful;
  David retired the blanket main-only restriction on 2026-09-06. Worktrees use the canonical lab explicitly
  and never receive a copied corpus. Keep scoped work pushed to `dlprentice/Onslaught-Career-Editor`;
  normal commits and pushes are authorized. Release claims require the selected platform's validation.
- Root commands use `python` (3.14) and forward-slash paths; Windows-only scripts fail fast here through
  `tools/require_windows_host.py`. Drive letters in old receipts are history, not routing.

## Reference routing

Read the relevant owner for the task, rather than every lane's references:

- Source layout and dependencies: [PROJECT-INDEX.md](PROJECT-INDEX.md). Setup and command reference:
  [README.MD](README.MD#build-and-run). [package.json](package.json) owns command definitions;
  [VALIDATION.md](VALIDATION.md) selects the applicable gate.
- Rebuild setup, assembly ownership and runtime modes: [rebuild/README.md](rebuild/README.md).
  Consult [PROVENANCE.md](rebuild/PROVENANCE.md) when admitting evidence, porting source or handling assets;
  [DETERMINISM.md](rebuild/DETERMINISM.md) for simulation, fixed-step, snapshot or trace changes;
  [PARITY.md](rebuild/PARITY.md) when carrying retail behavior contracts or assessing parity claims.
- Retail evidence: [RE-INDEX.md](reverse-engineering/RE-INDEX.md); Ghidra mutation:
  [the promotion gate](reverse-engineering/ghidra/README.md); reviews:
  [REVIEW-PROTOCOL.md](reverse-engineering/REVIEW-PROTOCOL.md).
- Ignored evidence and data: read the applicable `local-lab/AGENTS.md` or `local-data/AGENTS.md`
  when working there, and relevant index sections when locating evidence or checking retention/recovery.
  [LOCAL_LAB_OVERLAY.md](LOCAL_LAB_OVERLAY.md) owns canonical-lab routing for clones/worktrees.
- Documentation headers: [DOCUMENTATION.md](DOCUMENTATION.md); contributions:
  [CONTRIBUTING.md](CONTRIBUTING.md); security: [SECURITY.md](SECURITY.md);
  retained Windows release procedures: [README.RELEASE.md](README.RELEASE.md).

## Definition of done

1. The smallest gate that could falsify the change passed: docs → `git diff --check` and `npm run test:docs`;
   anything that adds files → `npm run test:safety`; tool changes → affected cases in the corresponding
   `_tests.py`; Core or Client → affected tests in the matching project, using `VALIDATION.md`.
   Run broader suites, including the expensive `tools/run_tool_tests.py`, only when affected scope requires
   them. Documentation-only edits do not require game, Core/Client, companion or legacy tool suites.
2. A new or edited tracked `.md` has `Status:`, `Last updated:` (or `Date:`), and `Summary:` (or `Verdict:`)
   in its header block, has no volatile generation numbers, and is not added to
   `tools/doc_header_backlog.txt`.
3. Evidence claims name their specimen, capture or test; anything unproven is written as an open question.
4. Review `git status`, preserve unrelated changes, and stage only the scoped tracked paths, never
   `local-lab/` or `local-data/`. Commit with a plain message and push the working branch, then continue
   the remaining authorized work rather than stopping after a substep.

## Gotchas learned the hard way

- `tools/lab_quarantine.py` still targets `H:\graveyard\lab-quarantine`; its stage, restore and purge actions must
  not run on this machine. The 2026-08-06 loss was a `Remove-Item -Force` on inputs whose identities were pinned
  in tooling and tests.
- The gen32 attestor requires the retired `~/ProjectData/Onslaught/local-lab` path to stay absent and pins its
  output owner to `local-data/host-attestations`; do not "fix" either path.
- Opening a Ghidra project without `-readOnly` can roll its `db.NNNNN` version even when a script refused.
  Measure the version, never quote it.
- The retained lab game is `local-lab/safe-copy-bea-pristine/`; its `BEA.exe` (`e1436ef7…`) is patched.
  Linux Steam is under `~/.local/share/Steam/steamapps/common/Battle Engine Aquila/` on this host.
  Launch an experimental copy from its own directory. The storage owner's September 6 receipts retire
  the proven Archive A safe-copy twin and both B-side mirrors; they do not establish a whole-lab backup
  or resolve historical ignored-data recovery. Current retention details belong to `local-lab/INDEX.md`
  and the migration deletion queue, not assumptions about folder names.
- `BEA.exe` writes `setuphistory.txt` and `cardid.txt` into its working directory, so launch a copy from its own
  folder; both names are ignored in case a launcher forgets.
- `tools/doc_header_backlog.txt` may only shrink. Never add a file to it to silence a header failure.
- `tools/check_installed_game_claims.py` bans standing promises about the installed game (for example that it is
  never modified); the app can patch an installed game after a verified backup, so describe the backup rule
  instead.
- `.claude/worktrees/` and `.worktrees/` are ignored because a broad `git add -A` has twice swept unrelated work
  into a commit.
