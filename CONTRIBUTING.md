# Contributing

Status: active — the contributor entry point
Last updated: 2026-11-06 (where to contribute across the public repositories, first-hour checks and commit messages)
Summary: which public repository takes which kind of work, what a first contribution needs and runs, what a focused
change looks like here, what must never be added to the repository, and which checks a change owes.

This public repository holds Onslaught Companion for the original game and Onslaught CE, the lore, our tools, a
frozen copy of the game documentation (`reverse-engineering/`) and a frozen copy of the Godot rebuild.
[GOAL.md](GOAL.md) states the direction and [PROGRAM.md](PROGRAM.md) the work queue. Keep changes focused and use
existing records and validation.

## Where to contribute

This is the one place that says which repository takes which kind of work; the other public repositories'
`CONTRIBUTING.md` files link here.

Everyone contributes the same way: fork the repository that owns the work, make a branch and open a pull request.
No invitation, collaborator access or private repository is needed. The maintainer reviews and merges pull requests,
and no response time is promised. Branches on the upstream repositories are the maintainer's working branches, not
contribution targets.

| Your work is about | It belongs in | How it is taken |
| --- | --- | --- |
| Playing Onslaught CE, its bugs, Linux and Windows issues, network play, the launcher and updates | [onslaught-ce](https://github.com/dlprentice/onslaught-ce) | Generated repository: open issues and pull requests there as usual. The maintainer imports accepted work into the working source and it returns in the next export, with credit. |
| The byte-matching decompilation: functions, tools, matching notes | [onslaught-decomp](https://github.com/dlprentice/onslaught-decomp) | Generated repository, same import route. Matching work needs your own copy of the game plus the compiler and SDK inputs its guide names. |
| The Godot rebuild | [onslaught-godot](https://github.com/dlprentice/onslaught-godot) | Edited directly: pull requests are reviewed and merged there. |
| How the game works: file formats, saves, mechanics, levels, engine | [onslaught-preservation](https://github.com/dlprentice/onslaught-preservation) | Edited directly. It uses onslaught-decomp's function names. |
| The Companion (saves, backups, settings, lore, music) and the program's goals and plan ([GOAL.md](GOAL.md), [PROGRAM.md](PROGRAM.md)) | This repository, [Onslaught-Career-Editor](https://github.com/dlprentice/Onslaught-Career-Editor) | Edited directly. The Companion's features are moving into Onslaught CE, so new feature work belongs in CE. |

Two trees in this repository are frozen copies: `rebuild/` (rebuild work goes to onslaught-godot) and
`reverse-engineering/` (documentation goes to onslaught-preservation). The forks
[dlprentice/Onslaught](https://github.com/dlprentice/Onslaught) and
[dlprentice/AYAResourceExtractor](https://github.com/dlprentice/AYAResourceExtractor) are pinned references, not
contribution targets.

Report security problems as each repository's `SECURITY.md` says. Each repository's `REUSE.toml` says which licence
covers which files, and a contribution comes in under the same terms as the files it changes.

A generated repository (onslaught-ce, onslaught-decomp) takes pull requests like any other, but its upstream `main`
is regenerated from the maintainer's working source, so an accepted change reaches it through the next export rather
than by merging the pull request itself.

## Your first hour

What you need depends on what you change. None of it needs an invitation, a private repository or the maintainer's
computer, and there is no hosted CI: the checks below are yours to run, and the pull request form asks you to report
them.

| You are changing | You need | Run before the pull request |
| --- | --- | --- |
| Text, links or lore (Markdown) | Git and Python 3.12 or newer; no game, Godot or .NET | `git diff --check`, `python3 tools/md_link_check.py --check-only`, `python3 tools/doc_header_check.py` |
| Python tools under `tools/` | The above; NumPy or Pillow for some suites | The affected `python3 tools/<name>_tests.py` ([the tools guide](tools/README.md#python-prerequisites) says which suites need NumPy, Pillow or your own copy of the game) |
| The Companion (`companion/`) | Linux x86-64 or WSL2, then `python tools/companion_toolchain.py setup`; no game for the authored tests | `npm run build` and `npm test`, or the Python equivalents in the [README](README.MD#public-setup) |
| Anything that reads or writes the game | Your own licensed copy of *Battle Engine Aquila* | The affected check ([`VALIDATION.md`](VALIDATION.md) selects it), run on a copy, never on your only install |
| Any new or edited file | Nothing more | `python3 tools/public_allowlist_safety_check.py --include-submodules` |

Steps:

1. Fork this repository and clone your fork with its public reference submodules, which the link and safety checks
   follow: `git clone --recurse-submodules https://github.com/<your-account>/Onslaught-Career-Editor.git`. In an
   existing clone, run `git submodule update --init --recursive` once.
2. Create a branch from upstream `main`: `git switch -c my-change`.
3. Make one focused change. A new or edited Markdown file needs the `Status:`, `Last updated:` and `Summary:` header
   that [`DOCUMENTATION.md`](DOCUMENTATION.md) describes; `tools/doc_header_check.py` enforces it.
4. Run the checks for your kind of change from the table, and keep their output.
5. Push the branch to your fork and open a pull request against `dlprentice/Onslaught-Career-Editor`. Fill in the
   [pull request form](.github/PULL_REQUEST_TEMPLATE.md): what changed, the exact commands you ran, the checks you
   could not run and why.

Commit messages describe the change itself. Leave out session or chat links, private paths and anything copied from the
game. A `Co-Authored-By` trailer is welcome when someone else wrote part of the change.

Corrections to the frozen game documentation in `reverse-engineering/` go to
[onslaught-preservation](https://github.com/dlprentice/onslaught-preservation); a pull request here may change only the
tool-owned files that [`RE-INDEX.md`](reverse-engineering/RE-INDEX.md) lists.

## Start here

Fork this public repository, clone your fork and create a branch from upstream `main`. People and automated agents
use the same route: commit scoped changes, push to your fork and open a pull request against
`dlprentice/Onslaught-Career-Editor`. No collaborator invitation, private repository or maintainer computer is needed
to prepare a proposal. The available validation depends on the inputs described below; list unavailable checks in the PR.

1. Read [`README.MD`](README.MD) and only the owning README or evidence files for your change. [`AGENTS.md`](AGENTS.md)
   is the guide automated agents read; its project rules (ground rules, reference routing, definition of done) apply to
   everyone, and its sections on tool outcomes, user holds and the maintainer's workspace concern the maintainer's own tooling.
2. Follow [Build and run](README.MD#build-and-run) on your own machine. Record the upstream commit, branch,
   existing edits and reference pins, then build and run the affected baseline checks before editing.
3. Preserve unrelated work. Keep recorded reference pins unchanged unless this PR intentionally updates one;
   explain that update and retain its licence, provenance and relevant checks.
4. Implement a focused change in its owning source files. Ordinary feature development does not require
   maintainer pre-approval; discuss large or overlapping changes in a public issue so contributors can coordinate.
5. Repeat the affected checks, inspect fresh output when appearance or behavior matters, and distinguish new
   failures from baseline failures. Commit scoped paths, push your branch to your fork, and open the PR with the
   problem, change, checks and remaining limits.

No game installation is required to test ordinary documentation changes. The full documentation and safety gates
need the existing pinned public reference submodules, including links into their source. Initialize them once with
`git submodule update --init --recursive`; keep both recorded pins rather than replacing them with an upstream's
latest commit. With the [public prerequisites](README.MD#build-and-run) installed, run:

```bash
npm run test:docs
npm run test:safety
```

After public toolchain setup, `npm test` runs the Companion's C# contract and tooling checks without opening a
window or requiring a game installation. The [Companion build guide](companion/OnslaughtToolkit.Godot/README.md#build-test-capture-run-and-export)
owns the setup and commands. Documentation and selected authored Python checks need no Godot installation.
`npm run test:companion-tools` checks the setup and runner with authored inputs; it does not replace the C# gate.
Checks against your installed game require your own licensed copy. If recorded references or a platform are
unavailable, name the missing checks in the PR; maintainers complete required acceptance before integration.

`npm run dev` launches the Companion when that toolchain is configured. This repository provisions no Windows host;
Linux checks do not establish Windows behaviour. Native workflow checks are separate from build, static or headless evidence.

Root [`package.json`](package.json) is the command authority. Do not duplicate
its command list in new documents.

## Licensing of contributions

Inbound = outbound: by opening a pull request you agree that your contribution is
licensed under the same terms as the paths it changes, as [`REUSE.toml`](REUSE.toml) and any
per-file SPDX line state them: code GPL-3.0-only ([`LICENSE`](LICENSE)), documentation and lore
CC BY-SA 4.0 ([`LICENSES/CC-BY-SA-4.0.txt`](LICENSES/CC-BY-SA-4.0.txt)). Contribute only work you
have the right to license this way; credit quoted or third-party material and keep its notice.
<!-- REUSE-IgnoreStart -->
New code files start with an `SPDX-License-Identifier: GPL-3.0-only` comment.
<!-- REUSE-IgnoreEnd -->

## Ownership

- The companion owns its career codec, file safety, game text, lore and every screen.
- The rebuild's simulation, `OnslaughtRebuild.Parity`, is deterministic given its inputs (the tape, the
  retail data and options files it reads as the game does, and the virtual clock) and has no presentation,
  process, network or GPU dependency; `OnslaughtRebuild.Host` owns presentation. The earlier
  `OnslaughtRebuild.Core` is reference material.
- `lore/` is the canonical public lore/history source. Corrections to it are made here; the record of what it used to say
  wrongly is [`history/lore-errata.md`](https://github.com/dlprentice/onslaught-preservation/blob/main/history/lore-errata.md)
  in onslaught-preservation.
- `reverse-engineering/` is a frozen copy of the game documentation, which is now maintained in
  [onslaught-preservation](https://github.com/dlprentice/onslaught-preservation) (see "Game documentation and the
  rebuild" below). What is written here keeps static, runtime and source-reference claims distinct.

## Product changes

Keep primary workflows understandable without lab knowledge. Use clear action
labels, explicit target paths, visible success/error state, keyboard focus,
accessible names, and sufficient contrast. Mutating actions must state whether
they write a selected file, a copy, or an app-owned profile.

Do not expose Host/Join as available, represent a generated catalog as bundled
game content, claim reconstruction parity, or turn research controls into a
normal-user promise without corresponding proven behavior.

## Files and retail inputs

Never commit retail binaries, arbitrary saves, copied executables, Ghidra databases or
backups, decompiler output, decomp source, debugger logs, private captures, credentials, or
`.env*` files.
Use the ignored locations described in [`LOCAL_LAB_OVERLAY.md`](LOCAL_LAB_OVERLAY.md)
for retail inputs, extraction, conversions, and experiments. Do not commit or
package retail game assets or derived copies. Contribute the smallest exact
recipe a current product or rebuild path consumes, with credits, provenance,
and third-party terms intact.

Screenshots are treated separately, because a picture of the game running is a
new work rather than one of the game's files. A few chosen ones may be tracked
and shipped for this project's own surfaces; bulk capture directories may not.
[`AGENTS.md`](AGENTS.md) carries the conditions, and anything tracked under that
allowance is listed in
[`reverse-engineering/project-meta/attribution.md`](reverse-engineering/project-meta/attribution.md).

File extensions are not provenance. Small project-authored or specifically
developer-provided assets may be committed in their owning source path when
their origin, license, and attribution are clear. The rebuild materialization
owners are reserved for local retail-derived outputs; large opaque additions
require a reviewed hash exception in the existing public-safety check.

Save edits must start from a real baseline and preserve unknown bytes. An
installed executable may be changed only when its owner explicitly chooses it
and the write path has already made and verified a pre-write backup; otherwise
use a verified copy. The pristine specimen is never a mutation target. The
full three-principle contract is [`AGENTS.md`](AGENTS.md); this is the
contributor-facing summary, not a second owner.
Exporters must require explicit local inputs and a separate local output root.

## Game documentation and the rebuild

Game findings (file formats, saves, mechanics, levels, engine) are written in
[onslaught-preservation](https://github.com/dlprentice/onslaught-preservation), the one home of the game
documentation; read its [CONTRIBUTING.md](https://github.com/dlprentice/onslaught-preservation/blob/main/CONTRIBUTING.md)
first. Do not add or edit findings in `reverse-engineering/`: it is a frozen copy, and
[`RE-INDEX.md`](reverse-engineering/RE-INDEX.md) names the commit it is frozen at and the few tool-owned files that
still change. Documents about this repository's own tools, the companion and the lore stay here. Wherever a document
is written, new findings come from the byte-matching decompilation or controlled observation; write them as prose and
specs, cite the function or capture, and never paste decompiler output. Retain raw or bulky proof locally; commit
only the smallest public-safe evidence a document needs, and state what it does not prove.

`rebuild/` is a frozen copy: rebuild changes belong in [onslaught-godot](https://github.com/dlprentice/onslaught-godot). For the record, read
[`rebuild/PROVENANCE.md`](rebuild/PROVENANCE.md) and [`rebuild/README.md`](rebuild/README.md): GPL-compatible source adaptation and locally materialized
user-supplied retail data are permitted; retail executable or decompiler text and separately licensed
third-party material are not.

## Validation

Use [`VALIDATION.md`](VALIDATION.md) to choose checks. Typical focused commands
are:

```bash
npm run test:docs
npm run test:safety
npm test
```

Do not run a root aggregate merely for ceremony.
