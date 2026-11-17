# Onslaught Toolkit: agent guide

Status: active — the single instruction file for this repository; `CLAUDE.md` only points here
Last updated: 2026-11-17
Summary: what this repository holds, which documents own its state, and the evidence, data and licensing rules
that apply here.

This repository, called the Toolkit in its guides, holds the Onslaught Companion app (its project folder is still
named OnslaughtToolkit.Godot), its lore and tools; the retired WinUI app also carried the Toolkit name
([CHANGELOG.md](CHANGELOG.md)). If guide files exist above this checkout on your machine, follow them too.
Contributors start with [CONTRIBUTING.md](CONTRIBUTING.md#where-to-contribute) and the
[README](README.MD#build-and-run); no maintainer guide or private checkout is required. The ground rules, reference
routing and definition of done below apply to everyone; "Tool outcomes and user holds" and the maintainer-workspace
notes concern the maintainer's own agent tooling.

## What this is

A preservation project for *Battle Engine Aquila* (2003). This public repository holds the companion (`companion/`,
Onslaught Companion), a frozen copy of the game documentation (`reverse-engineering/`, whose home is
[onslaught-preservation](https://github.com/dlprentice/onslaught-preservation)), our tools, and a pointer page where the
rebuild stood (it is developed in [onslaught-godot](https://github.com/dlprentice/onslaught-godot)). [`GOAL.md`](GOAL.md)
states the outcomes, [`PROGRAM.md`](PROGRAM.md) the work queue and [`CURRENT_CAPABILITIES.md`](CURRENT_CAPABILITIES.md)
what is demonstrated; the full context is in [MAINTAINER-AGENT-PRACTICE.md](MAINTAINER-AGENT-PRACTICE.md).

## Checkouts and branches

Public fork setup uses [CONTRIBUTING.md](CONTRIBUTING.md). Contributor checks need no local-lab inputs and none of the
maintainer's workspace described under "Maintainer-only workspace" below ([README](README.MD#build-and-run)).

- `main` is the integration branch; a lane (a topic branch) merges into it when its own gate passes. Lane branches
  start from the flattened `main` (the history was flattened into a single root; see the commit titled Describe the
  repository after the history flatten); never merge a pre-flatten branch or resurrect its plans.

### Maintainer-only workspace

- The maintainer's working checkout may sit on slow external storage, and it holds the canonical `local-lab/`. Give
  such a checkout light I/O only: do builds, test runs, captures and worktrees in a clone on a fast internal disk and
  point it at the canonical lab ([LOCAL_LAB_OVERLAY.md](LOCAL_LAB_OVERLAY.md)). Worktrees never receive a copied
  corpus. Where the checkout and the clone are on a given machine is in the ignored `local-data/` notes.
- Which clone and reference folders this machine uses is in the ignored `local-data/rebuild-env.sh` and the private
  notes, never in a tracked file.

## Project progress and documentation

Report experiments, integrated source, released packages and real-player/platform acceptance separately; a passing
synthetic test, a branch or a byte match is evidence within its stated scope, not automatic feature completion.
Preserve historical evidence rather than creating competing live status files, and report failures and open gaps
without invented percentages. A handoff is a dated continuity snapshot, not a second roadmap: check current refs, claims
and evidence before relying on it. Which document owns which state:
[MAINTAINER-AGENT-PRACTICE.md](MAINTAINER-AGENT-PRACTICE.md#project-progress-and-documentation).

## Tool outcomes and user holds

Record consequential tool outcomes in existing private notes, keeping observations separate from interpretations;
fresh evidence can correct an interpretation without erasing the original observation
([how](MAINTAINER-AGENT-PRACTICE.md#recording-tool-outcomes)).

- **Safety denial:** keep its stated scope and reason. Do not obtain the denied outcome through another tool, wrapper
  or helper. Continue only with a materially safer permitted alternative or the supported review process. A task-level
  safety stop follows its actual notice and its supported way to resume.
- **Failed call without a reason:** it proves neither approval nor a permanent ban. An already-authorized harmless
  check may be retried once. If it fails again, record the unresolved failure and finish independent authorized work,
  without repeated status loops and without changing the request to get around a restriction. Check effects before
  repeating any mutation.
- **Failed status read:** the task's state is unknown. A returned task handle shows the task was accepted, not that it
  finished: check that task or await its result rather than starting a duplicate. A helper that cannot see the caller's
  result does not make that result invalid, and is no reason for duplicate work or interruption. Report required checks
  that could not be observed as limits, never as passes.
- **User hold:** keep it until the user explicitly releases that scope. Resuming the general goal, elapsed time,
  delegation or a successful tool call does not release a narrower hold.

## Ground rules

- Game/save writes require an informed user choice and a verified recovery copy before overwriting original data, and
  never happen while the game runs. The companion's `GameInstaller` (`companion/OnslaughtToolkit.Godot/Files/GameWrites.cs`; the
  [companion README](companion/OnslaughtToolkit.Godot/README.md) describes its mechanism) is the model. Never manufacture an
  "original" from an already modified file, and never destroy career data as a side effect.
- The pristine specimen `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup` (SHA-256 `74154bfa…`) is the
  byte-measurement baseline: read it, never write it. The lab folder's `BEA.exe` (`e1436ef7…`) is patched. Every
  byte or address finding names the specimen it was read from, with its hash; measure the exact selected file
  before making a new claim about any other copy.
- Do not synthesize `.bes` saves. Start from a real baseline and preserve length, reserved fields and unknown bytes.
  `tests_shared/fixtures/gold_career_save.bin` is the one tracked save.
- Never track retail binaries or assets, converted retail material, arbitrary saves, raw debugger logs, bulky
  captures, Ghidra databases or backups, decompiler output, decomp source, credentials or `.env*`.
  Never quote original-game bytes or a private machine path in live text. `npm run test:safety` enforces both; what
  it checks and its reviewed exceptions are in [VALIDATION.md](VALIDATION.md).
- Every behaviour claim cites a capture, byte comparison, focused test, or pinned source file and line. Decompiler
  output, a plausible name or a model's opinion proves nothing; the decompilation is the naming authority, cited by
  function, never quoted. Static evidence establishes identities and structures; only controlled runtime evidence
  establishes causality and values. Write unknowns as open questions with the cheapest falsifier.
- Ghidra is retired as an authority. The working project `local-lab/ghidra-projects/BEA/BEA.gpr` and the cold copies
  kept outside this checkout (the ignored local notes say where) stay untouched (restore a copy, never open one in place; opening without
  `-readOnly` can roll its `db.NNNNN` version). Nothing Ghidra-derived returns to this repository.
- `local-lab/` and `local-data/` are real ignored directories inside this checkout. Never run `git clean` here
  (`-x`/`-X` would erase the lab) and never stage them; add paths explicitly. Before calling anything in them stale,
  grep the tooling and tests, not only the docs: a 2026-08-06 cleanup deleted inputs whose identities were pinned in
  tooling. Retention belongs to `local-lab/INDEX.md` and the machine's deletion queue.
- Licensing: the rebuild is GPL and may adapt the pinned GPL source in `references/Onslaught` and the decompilation's
  simulation (recorded per unit in [`rebuild/PROVENANCE.md`](https://github.com/dlprentice/onslaught-godot/blob/main/rebuild/PROVENANCE.md)
  in onslaught-godot, where it is developed); it consumes locally materialized retail data but never
  contains retail executables, decompiler output or separately licensed material. All project code is GPL-3.0-only and
  documentation and lore are CC BY-SA 4.0, as `REUSE.toml` maps them; contributions come in under the same terms
  ([CONTRIBUTING.md](CONTRIBUTING.md#licensing-of-contributions), which also lists kept third-party notices). None of it
  merges with private retail material into one licensing boundary.
- The rebuild's determinism contract is in
  [MAINTAINER-AGENT-PRACTICE.md](MAINTAINER-AGENT-PRACTICE.md#the-rebuilds-determinism-contract) and onslaught-godot;
  missing references, empty selections and new skips are not passes.
- No telemetry: nothing in this repository collects or sends usage data. A network feature names exactly what it
  contacts and why, and reads only public data.
- C# only, built in code: no `.gd` files, no editor-authored scenes or resources (a `.tscn` only as a one-node entry
  wrapper), shader source in C# strings, one production owner per subsystem. Repository tooling stays Python.
- Reviews by other agents or models are optional input to reproduce, not authority. Every agent call names its model and
  effort by role, as rule 12 of the maintainer's machine guide says; that rule overrides historical model
  assignments and the frozen review protocol's "strongest available setting". Hosted reviewers never receive retail material or
  secrets. Hosted CI and release automation are outside this phase; release claims need the selected platform's validation; Linux evidence alone does not establish
  Windows behaviour.

## Reference routing

- Source layout and dependencies: [PROJECT-INDEX.md](PROJECT-INDEX.md); setup and commands:
  [README.MD](README.MD#build-and-run) and [package.json](package.json); which gate applies:
  [VALIDATION.md](VALIDATION.md).
- The rebuild's setup and contracts (`README.md`, `PARITY.md`, `PROVENANCE.md`, `DETERMINISM.md`): its `rebuild/`
  folder in [onslaught-godot](https://github.com/dlprentice/onslaught-godot); the companion's workflows and validation
  limits: its [README](companion/OnslaughtToolkit.Godot/README.md).
- Current game documentation: [onslaught-preservation](https://github.com/dlprentice/onslaught-preservation); the local
  [RE-INDEX.md](reverse-engineering/RE-INDEX.md) routes the frozen copy. Archived Ghidra and campaign records: the
  private historical maintainer archive.
- Ignored evidence and data: `local-lab/AGENTS.md` and `local-data/AGENTS.md` when working there.
- Documentation headers: [DOCUMENTATION.md](DOCUMENTATION.md); contributions: [CONTRIBUTING.md](CONTRIBUTING.md);
  security: [SECURITY.md](SECURITY.md).

## Definition of done

1. The smallest gate that could falsify the change passed: docs → `git diff --check` and `npm run test:docs`; added
   files → `npm run test:safety`; tool changes → the affected `_tests.py` cases; rebuild changes are not made here (`rebuild/` is a pointer page): send them to onslaught-godot, as [CONTRIBUTING.md](CONTRIBUTING.md) describes; companion → `npm test`, run from the repository root (the root `package.json` defines it; `companion/` has none).
2. A new or edited tracked `.md` has `Status:`, `Last updated:` (or `Date:`) and `Summary:` (or `Verdict:`) in its
   header and no volatile counts. `tools/doc_header_backlog.txt` may only shrink.
3. Stage only the scoped paths, commit plainly and push the working branch to your fork, then open a PR as
   [CONTRIBUTING.md](CONTRIBUTING.md) describes. Maintainers use the established integration route. Commits here are
   public: keep the Co-Authored-By line, add no session-link line, and describe the change itself, not which agent or role made it.

## Gotchas

- `BEA.exe` writes `setuphistory.txt` and `cardid.txt` into its working directory: launch a copy from its own
  folder. Linux Steam's install is `~/.local/share/Steam/steamapps/common/Battle Engine Aquila/`.
- `tools/check_installed_game_claims.py` bans standing promises about the installed game (for example that it is
  never modified); describe the backup rule instead.
- `.worktrees/` and `.claude/worktrees/` are ignored because a broad `git add -A` has twice swept unrelated work into
  a commit.
