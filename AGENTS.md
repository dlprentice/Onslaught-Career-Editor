# Onslaught Toolkit: agent guide

Status: active — the single instruction file for this repository; `CLAUDE.md` only points here
Last updated: 2026-10-15 (decomp done and private; Godot rebuild parked; Ghidra and RE machinery moved to a private archive; WinUI removed)
Summary: active development authority, evidence and data protections, task-specific reference routing,
and proportional completion checks.

Read this before changing anything. Read `~/AGENTS.md`, `~/Projects/AGENTS.md` and
`~/Projects/game-dev/AGENTS.md` explicitly when automatic discovery stops at this Git root;
this repository guide is more specific and wins here.

## What this is

A preservation project for *Battle Engine Aquila* (2003). Since 2026-10-15 (David):

- **The decompilation is done and private.** The byte-matching decompilation (`dlprentice/bea-decomp`, checkout
  `~/Projects/game-dev/bea-decomp`, 5,482 of 5,482 functions) is the reverse-engineering authority. It is planned
  for publication as "Onslaught CE" (GPL-3.0 source and binaries, no game files) once its native port plays like
  retail.
- **The native source port is in progress and private**, in `bea-decomp`, for Windows and Linux.
- **The companion is active and public**: the Godot .NET toolkit for careers, saves, backups, settings, music and
  lore, in this repository.
- **The Godot rebuild is parked**; `rebuild/` on main is its parked state and stays as reference.

This public repository holds the companion, documentation of the game (formats, behaviours, findings as prose and
specs), our own tools, the AppCore patching core the companion's mod manager will build on, and the parked rebuild.
It does not hold the Ghidra database, decompiler output, retail binaries or data, or the decomp source: the tracked
Ghidra checkpoint, `developer_state.json` and the Ghidra/TTD/campaign machinery moved on 2026-10-15 to the private
repository `dlprentice/onslaught-re-archive` (clone `~/Projects/game-dev/onslaught-re-archive`), which also keeps the
decompiler passages scrubbed from public documents. The WinUI shell, its UI tests and the CLI were removed the same
day. The public history was flattened to a single root afterwards; the full earlier history (every old branch,
tag and pull-request head) is in the private RE archive as a verified bundle and under `refs/old/*`.
[`GOAL.md`](GOAL.md) states the outcomes, [`PROGRAM.md`](PROGRAM.md) is the work queue and
[`CURRENT_CAPABILITIES.md`](CURRENT_CAPABILITIES.md) says what is demonstrated today.

Linux owns development and native Godot execution. The companion is a C# application built in code on Godot 4.8
dev6 .NET (`godot48-mono`) and owns its file-safety source. No local Windows validation environment exists (the
Windows VM was retired unbuilt); Linux evidence does not establish Windows behaviour. While David uses the desktop,
continue code and noninteractive checks; wait for him to announce availability before live input or visible
launches. Any agent may work here, Claude Code included; subagents and peer sessions follow machine rule 12
(disjoint scopes in their own worktrees; the lead integrates).

## Lanes

`main` is the integration branch; a lane merges into it only when its own checks pass.

| Lane | Branch | Checkout | State |
| --- | --- | --- | --- |
| Companion | `claude/companion-csharp-20260925` | `.worktrees/companion-csharp-20260925` | Active. C# only and built in code: no GDScript, one-node entry scene. The sidebar is Home, Your career (a Summary with a campaign map, Goodies, Edit career, Cheats), Your game (Game settings, Backups), Extras (Music & voices, Lore) and Advanced, folded away. Every game write is a choice in one dialog, made after a verified backup and never while the game runs; automatic backups; it catches up when the game closes. A mod manager built on the AppCore patching core, including patching the installed `BEA.exe`, is a later phase. Windows execution, a human click-through and listening to the audio remain. |
| Game documentation and tools | `main` (short branches merged into it) | any checkout | Formats, mechanics, saves, assets, function notes and contracts under `reverse-engineering/`, and the tools under `tools/`. New findings come from the decompilation and are written as prose and specs, never as decompiler output. |
| Decompilation and native port | private | `~/Projects/game-dev/bea-decomp` | Decompilation done (5,482/5,482); native source port in progress. Its own README and guide govern it; nothing from it is copied here. |
| Rebuild (parked) | `rebuild/` on main (old tag `archive/godot-rebuild-20260926` in the private RE archive) | none | Parked 2026-10-15 by David: the faithful cross-platform game is now the native source port of the byte-matching decompilation (bea-decomp); any later remake forks that port. At the tag the Godot rebuild is C# and built in code; it wins Level 100 through its player-input surface with a deterministic tape and builds World 110 in Core from retail data (not playable in its host). Its last gate (`npm run check:rebuild`) passed at the tag. `rebuild/` stays on main as reference; no further work is planned. |

The former reverse-engineering lane (`codex/retail-re-20260919`, Ghidra) and the former rebuild lane and its
checkout (`codex/godot-editor-48-20260919`, `.worktrees/godot-editor-48-20260919`) no longer exist as working
lanes. `rebuild/` on main is the parked rebuild (identical to its old tag except the parked documents and the
root-marker test fix); its gate `npm run check:rebuild` last passed at the tag and has not been rerun on main
(`export BEA_LOCAL_LAB=$REPO/local-lab` first).

To resume the companion, work in its checkout (`REPO=~/Projects/game-dev/Onslaught-Career-Editor`), then
`git pull` and `git merge main`: `npm run build` and `npm test`; `npm run capture:companion-godot` renders every
screen at two sizes through `godot-offscreen` (add `-- --beside-gpu-jobs` to render beside an NVIDIA job, queued on
the shared iGPU lock); `npm run dev` opens a window. Keep Godot headless unless David has released the desktop.

The unmerged 2026-09-12 C# camera draft is the old tag `archive/camera-core-resume-20260912`, now in the private
RE archive under `refs/old/tags/`. Unique ignored data
from retired worktrees is in `local-data/test-runs/retired-worktrees-20260925/` and
`local-data/test-runs/retired-worktrees-20261015/`.

## Ground rules

- Game/save writes require an informed user choice and a verified recovery copy before overwriting original
  data; `BinaryPatchEngine.AuthorizeInstalledGameWrite` in the AppCore patching core is the model. Never manufacture an
  "original" from an already modified file, and never destroy career data as a side effect.
- The pristine specimen (`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256 `74154bfa…`)
  is the byte-measurement baseline: read it, never write
  it. Every byte or address finding names the specimen it was read from, with its hash. The lab folder's
  `BEA.exe` is patched. The Linux Steam executable matched the pristine hash on September 6; measure the
  exact selected file before making a new claim. Old Windows-install descriptions are not Linux identities.
- Do not synthesize `.bes` saves. Start from a real baseline and preserve length, reserved fields and unknown
  bytes. `tests_shared/fixtures/gold_career_save.bin` is the one tracked save.
- Never track retail binaries or assets, converted retail material, arbitrary saves, raw debugger logs, bulky
  captures, Ghidra databases or backups, decompiler output, decomp source, credentials or `.env*`;
  `npm run test:safety` enforces the boundary and rejects any Ghidra project. A small registered set of the app's own screenshots is the one allowance
  (`reverse-engineering/project-meta/attribution.md`, checked by `tools/check_registered_screenshots.py`).
- Every behavior claim cites a capture, byte comparison, focused test, or pinned source file and line. Decompiler
  output, a plausible name or a model's opinion proves nothing; the byte-matching decompilation is the naming
  authority, cited by function, not quoted. Static evidence establishes identities and
  structures; only controlled runtime evidence establishes causality and values. Write unknowns as open questions
  with the cheapest falsifier, never as guessed names.
- Ghidra is retired as an authority. The tracked checkpoint is in the private RE archive; the working project
  `local-lab/ghidra-projects/BEA/BEA.gpr` and the cold copies in `/srv/archive-a/onslaught-ghidra-cold/` stay where
  they are, untouched (restore a copy, never open one in place). Nothing Ghidra-derived returns to this repository.
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
- Language: C# only, on Godot 4.8 dev6 .NET (David, 2026-09-25: "I want us to go 100% C sharp. No GD script
  whatsoever. No crossover."). No `.gd` files: game code, tools that run inside Godot, checks and capture harnesses
  are C#. Each subsystem has one production owner, never two copies of the same behavior. Everything is built in
  code: no editor-authored scenes or resources (a `.tscn` only as a one-node entry wrapper), and the editor need
  not show the game. Shader source lives in C# strings; repository tooling stays Python. New work adds no GDScript.
- Reviews by other agents or models are optional and follow `reverse-engineering/REVIEW-PROTOCOL.md`: read-only
  lanes, reports are input to reproduce rather than authority, and hosted reviewers never receive retail material
  or secrets.
- Reuse existing tooling and records; avoid duplicate test frameworks, broad routine matrices and new status
  or handoff files. Add a focused test when a real behavioral gap needs one. Hosted CI and release automation
  are outside this phase. Use a branch or repo-local `.worktrees/` when useful;
  David retired the blanket main-only restriction on 2026-09-06. Worktrees use the canonical lab explicitly
  and never receive a copied corpus. Keep scoped work pushed to `dlprentice/Onslaught-Career-Editor`;
  normal commits and pushes are authorized. Release claims require the selected platform's validation.
- Root commands use `python` (3.14) and forward-slash paths. Drive letters in old receipts are history, not routing.

## Reference routing

Read the relevant owner for the task, rather than every lane's references:

- Source layout and dependencies: [PROJECT-INDEX.md](PROJECT-INDEX.md). Setup and command reference:
  [README.MD](README.MD#build-and-run). [package.json](package.json) owns command definitions;
  [VALIDATION.md](VALIDATION.md) selects the applicable gate.
- The parked rebuild's setup, assembly ownership and runtime modes: [rebuild/README.md](rebuild/README.md).
  Consult [PROVENANCE.md](rebuild/PROVENANCE.md) when admitting evidence, porting source or handling assets;
  [DETERMINISM.md](rebuild/DETERMINISM.md) for simulation, fixed-step, snapshot or trace changes;
  [PARITY.md](rebuild/PARITY.md) when carrying retail behavior contracts or assessing parity claims.
- Game documentation: [RE-INDEX.md](reverse-engineering/RE-INDEX.md); reviews:
  [REVIEW-PROTOCOL.md](reverse-engineering/REVIEW-PROTOCOL.md). Archived Ghidra and campaign records: the private
  `dlprentice/onslaught-re-archive`.
- Ignored evidence and data: read the applicable `local-lab/AGENTS.md` or `local-data/AGENTS.md`
  when working there, and relevant index sections when locating evidence or checking retention/recovery.
  [LOCAL_LAB_OVERLAY.md](LOCAL_LAB_OVERLAY.md) owns canonical-lab routing for clones/worktrees.
- Documentation headers: [DOCUMENTATION.md](DOCUMENTATION.md); contributions:
  [CONTRIBUTING.md](CONTRIBUTING.md); security: [SECURITY.md](SECURITY.md).

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

- The 2026-08-06 loss was a `Remove-Item -Force` on inputs whose identities were pinned in tooling and tests;
  the quarantine tool behind it was removed on 2026-10-15. Never recreate it.
- Opening a Ghidra project without `-readOnly` can roll its `db.NNNNN` version even when a script refused.
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
