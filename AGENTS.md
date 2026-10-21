# Onslaught Toolkit: agent guide

Status: active — the single instruction file for this repository; `CLAUDE.md` only points here
Last updated: 2026-10-21 (lean rewrite: durable rules and routing only; lane state lives in the documents it routes to)
Summary: what this repository holds, which documents own its state, and the evidence, data and licensing rules
that apply here.

The machine and category guides (`~/AGENTS.md`, `~/Projects/AGENTS.md`, `~/Projects/game-dev/AGENTS.md`) apply;
this guide adds only what is specific to this repository.

## What this is

A preservation project for *Battle Engine Aquila* (2003). This public repository holds:

- the **Godot rebuild** (`rebuild/`): a C# reimplementation on Godot 4.8 dev6 .NET, 1:1 with retail from startup to
  exit, with level 100 playable to completion. `OnslaughtRebuild.Parity` is the simulation owner and
  `OnslaughtRebuild.Host` the presentation owner; the earlier `OnslaughtRebuild.Core`, `Client` and `Godot` projects
  are reference material, not a second production simulation;
- the **companion** (`companion/`): the Godot .NET toolkit for careers, saves, backups, settings, music and lore,
  with the AppCore patching core its mod manager will build on;
- documentation of the game (formats, behaviours, contracts) and our own tools.

Elsewhere: the byte-matching decompilation and the native source port are the private `dlprentice/bea-decomp`
(`~/Projects/game-dev/bea-decomp`), the reverse-engineering authority. The Ghidra checkpoint, the RE campaign
machinery, scrubbed decompiler passages and the full pre-flatten history are in the private
`dlprentice/onslaught-re-archive`. [`GOAL.md`](GOAL.md) states the outcomes, [`PROGRAM.md`](PROGRAM.md) the work
queue, [`CURRENT_CAPABILITIES.md`](CURRENT_CAPABILITIES.md) what is demonstrated, and
[`rebuild/PARITY.md`](rebuild/PARITY.md) the rebuild's milestones and measured parity.

## Checkouts and branches

- `main` is the integration branch; a lane merges into it when its own gate passes. Lane branches start from the
  flattened `main`; never merge a pre-flatten branch or resurrect its plans.
- The familiar checkout `~/Projects/game-dev/Onslaught-Career-Editor` physically lives on Archive B
  (`/srv/archive-b/Onslaught-Career-Editor`, a USB drive, bind-mounted). It holds the canonical `local-lab/`.
  Give it light I/O only: do builds, test runs, captures and worktrees in a clone on the internal disk and point it at
  the canonical lab ([LOCAL_LAB_OVERLAY.md](LOCAL_LAB_OVERLAY.md)). Worktrees never receive a copied corpus.
- Which branch and clone each lane uses right now is recorded in `rebuild/README.md` (rebuild) and the companion's
  own README, not here.

## Ground rules

- Game/save writes require an informed user choice and a verified recovery copy before overwriting original data;
  `BinaryPatchEngine.AuthorizeInstalledGameWrite` in AppCore is the model. Never manufacture an "original" from an
  already modified file, and never destroy career data as a side effect.
- The pristine specimen `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup` (SHA-256 `74154bfa…`) is the
  byte-measurement baseline: read it, never write it. The lab folder's `BEA.exe` (`e1436ef7…`) is patched. Every
  byte or address finding names the specimen it was read from, with its hash; measure the exact selected file
  before making a new claim about any other copy.
- Do not synthesize `.bes` saves. Start from a real baseline and preserve length, reserved fields and unknown bytes.
  `tests_shared/fixtures/gold_career_save.bin` is the one tracked save.
- Never track retail binaries or assets, converted retail material, arbitrary saves, raw debugger logs, bulky
  captures, Ghidra databases or backups, decompiler output, decomp source, credentials or `.env*`.
  `npm run test:safety` enforces the boundary; a small registered set of the app's own screenshots is the one
  allowance (`reverse-engineering/project-meta/attribution.md`, `tools/check_registered_screenshots.py`).
- Every behaviour claim cites a capture, byte comparison, focused test, or pinned source file and line. Decompiler
  output, a plausible name or a model's opinion proves nothing; the decompilation is the naming authority, cited by
  function, never quoted. Static evidence establishes identities and structures; only controlled runtime evidence
  establishes causality and values. Write unknowns as open questions with the cheapest falsifier.
- Ghidra is retired as an authority. The working project `local-lab/ghidra-projects/BEA/BEA.gpr` and the cold copies
  in `/srv/archive-a/onslaught-ghidra-cold/` stay untouched (restore a copy, never open one in place; opening without
  `-readOnly` can roll its `db.NNNNN` version). Nothing Ghidra-derived returns to this repository.
- `local-lab/` and `local-data/` are real ignored directories inside this checkout. Never run `git clean` here
  (`-x`/`-X` would erase the lab) and never stage them; add paths explicitly. Before calling anything in them stale,
  grep the tooling and tests, not only the docs: a 2026-08-06 cleanup deleted inputs whose identities were pinned in
  tooling. Retention belongs to `local-lab/INDEX.md` and the machine's deletion queue.
- Licensing: the rebuild is GPL and may adapt the pinned GPL source in `references/Onslaught` and the decompilation's
  simulation (recorded per unit in `rebuild/PROVENANCE.md`); it consumes locally materialized retail data but never
  contains retail executables, decompiler output or separately licensed material. The companion is MIT. Neither
  merges with private retail material into one licensing boundary.
- The rebuild's simulation (`OnslaughtRebuild.Parity`) is deterministic given its inputs: the tape, the retail data
  and options files it reads as the game does, and the virtual clock. It never reads wall time, locale, environment or
  thread scheduling, and it has no presentation, process, network or GPU dependency (the earlier `Core`'s stricter
  contract is [DETERMINISM.md](rebuild/DETERMINISM.md)). Tests compare it with recorded references Present by
  Present; missing references, empty selections and new skips are not passes.
- C# only, built in code: no `.gd` files, no editor-authored scenes or resources (a `.tscn` only as a one-node entry
  wrapper), shader source in C# strings, one production owner per subsystem. Repository tooling stays Python.
- Reviews by other agents or models are optional input to reproduce, not authority
  ([REVIEW-PROTOCOL.md](reverse-engineering/REVIEW-PROTOCOL.md)); hosted reviewers never receive retail material
  or secrets. Hosted CI and release automation are outside this phase; release claims need the selected platform's
  validation (no local Windows environment exists, so Linux evidence does not establish Windows behaviour).

## Reference routing

- Source layout and dependencies: [PROJECT-INDEX.md](PROJECT-INDEX.md); setup and commands:
  [README.MD](README.MD#build-and-run) and [package.json](package.json); which gate applies:
  [VALIDATION.md](VALIDATION.md).
- Rebuild: [rebuild/README.md](rebuild/README.md) (setup, assemblies, parity harness, reference environment),
  [PARITY.md](rebuild/PARITY.md), [PROVENANCE.md](rebuild/PROVENANCE.md), [DETERMINISM.md](rebuild/DETERMINISM.md).
- Game documentation: [RE-INDEX.md](reverse-engineering/RE-INDEX.md). Archived Ghidra and campaign records: the
  private `onslaught-re-archive`.
- Ignored evidence and data: `local-lab/AGENTS.md` and `local-data/AGENTS.md` when working there.
- Documentation headers: [DOCUMENTATION.md](DOCUMENTATION.md); contributions: [CONTRIBUTING.md](CONTRIBUTING.md);
  security: [SECURITY.md](SECURITY.md).

## Definition of done

1. The smallest gate that could falsify the change passed: docs → `git diff --check` and `npm run test:docs`; added
   files → `npm run test:safety`; tool changes → the affected `_tests.py` cases; rebuild code → the affected Parity
   tests, then the Parity suite and Host build as `rebuild/README.md` describes; companion → its `npm test`.
2. A new or edited tracked `.md` has `Status:`, `Last updated:` (or `Date:`) and `Summary:` (or `Verdict:`) in its
   header and no volatile counts. `tools/doc_header_backlog.txt` may only shrink.
3. Stage only the scoped paths, commit plainly and push the working branch.

## Gotchas

- `BEA.exe` writes `setuphistory.txt` and `cardid.txt` into its working directory: launch a copy from its own
  folder. Linux Steam's install is `~/.local/share/Steam/steamapps/common/Battle Engine Aquila/`.
- `tools/check_installed_game_claims.py` bans standing promises about the installed game (for example that it is
  never modified); describe the backup rule instead.
- `.worktrees/` and `.claude/worktrees/` are ignored because a broad `git add -A` has twice swept unrelated work into
  a commit.
