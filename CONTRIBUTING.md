# Contributing

Status: active — the contributor entry point
Last updated: 2026-11-21 (updated for repurposing into the Onslaught Modding & Content Toolkit; standalone Companion GUI and frozen reverse-engineering copy retired)
Summary: which public repository takes which kind of work, what a first contribution needs and runs, what must never be added to the repository, and which checks a change owes.

This public repository holds the **Onslaught Modding & Content Toolkit**: the JSON Content Catalogue, Content Inventory, format/modding tools (`tools/`), canonical lore (`lore/`, `lore-book/`) and the project overview ([`GOAL.md`](GOAL.md), [`PROGRAM.md`](PROGRAM.md)). Keep changes focused and use the existing validation gates.

## Where to contribute

This is the one place that says which repository takes which kind of work; the other public repositories' `CONTRIBUTING.md` files link here.

Everyone contributes the same way: fork the repository that owns the work, make a branch and open a pull request. No invitation, collaborator access or private repository is needed. Branches on upstream repositories are maintainer working branches, not contribution targets.

Questions and ideas: https://github.com/dlprentice/onslaught-ce/discussions
(Discussions are enabled on `onslaught-ce` only; bugs and scoped requests go to the Issues of the repository that owns the work.)

| Your work is about | It belongs in | How it is taken |
| --- | --- | --- |
| Playing Onslaught CE, bugs, Career/Backups/Mods/Editor UI, launcher and updates | [onslaught-ce](https://github.com/dlprentice/onslaught-ce) | Generated repository: open issues and pull requests as usual; accepted work is imported into maintainer source and published in the next export with credit. |
| The byte-matching decompilation: functions, tools, matching notes | [onslaught-decomp](https://github.com/dlprentice/onslaught-decomp) | Generated repository, same import route. Matching requires your own copy of the game plus the compiler/SDK inputs its guide names. |
| The Godot rebuild | [onslaught-godot](https://github.com/dlprentice/onslaught-godot) | Edited directly: pull requests are reviewed and merged there. |
| How the game works: file formats, saves, mechanics, levels, engine | [onslaught-preservation](https://github.com/dlprentice/onslaught-preservation) | Edited directly. Uses `onslaught-decomp` function names. |
| The JSON Content Catalogue, Content Inventory, format decoders, mod-staging tools, lore and project goals/program ([GOAL.md](GOAL.md), [PROGRAM.md](PROGRAM.md)) | This repository, [Onslaught-Career-Editor](https://github.com/dlprentice/Onslaught-Career-Editor) | Edited directly. The former standalone Companion GUI was retired in favour of Onslaught CE's built-in screens. |

One rule for findings: function identity, naming and matching go to `onslaught-decomp`; behaviour, format and mechanics documentation goes to `onslaught-preservation`. The forks [dlprentice/Onslaught](https://github.com/dlprentice/Onslaught) and [dlprentice/AYAResourceExtractor](https://github.com/dlprentice/AYAResourceExtractor) under `references/` are pinned references, not contribution targets.

Report security problems as each repository's `SECURITY.md` says. Each repository's `REUSE.toml` says which licence covers which files, and a contribution comes in under the same terms as the files it changes. Everyone taking part follows the [Code of Conduct](CODE_OF_CONDUCT.md).

## Your first contribution

None of the authored checks need an invitation, a private repository, Godot, .NET or a game installation, and there is no hosted CI: run the checks locally and report them in your pull request.

| You are changing | You need | Run before the pull request |
| --- | --- | --- |
| Text, links or lore (Markdown) | Git and Python 3.12+ (standard library only) | `git diff --check`, `npm run test:docs` (or `python3 -B tools/md_link_check.py --check-only` and `python3 -B tools/doc_header_check.py`) |
| Python tools or schemas under `tools/` | Git and Python 3.12+ (`numpy`, `Pillow`, `jsonschema` for full suites; see [Python prerequisites](tools/README.md#python-prerequisites)) | The affected `python3 -B tools/<name>_tests.py` and `npm run test:tools` |
| Retail catalogue, inventory or MSL gates | Your own lawfully obtained copy of *Battle Engine Aquila* | `content_catalog_gate.py`, `content_inventory_gate.py` or `msl_gate.py` (read-only against your install; write outputs only to ignored `local-data/`) |
| Any new or edited file | Initialized `references/` submodules | `npm run test:safety` (`python3 -B tools/public_allowlist_safety_check.py --self-test` and `--include-submodules`) |

Steps:

1. Read [`README.MD`](README.MD), [`AGENTS.md`](AGENTS.md) and [`tools/README.md`](tools/README.md) (or the relevant lore/doc owner).
2. Fork this repository and clone with submodules: `git clone --recurse-submodules https://github.com/<your-account>/Onslaught-Career-Editor.git` (or run `git submodule update --init --recursive` in an existing clone). Keep the recorded pins in `references/` unchanged unless intentionally updating a reference.
3. Create a branch from upstream `main`: `git switch -c my-change`. Run the relevant checks before editing to establish your baseline.
4. Make one focused change in the files that own it. Any new or edited Markdown file needs the `Status:`, `Last updated:` and `Summary:` header that [`DOCUMENTATION.md`](DOCUMENTATION.md) specifies (`tools/doc_header_check.py` enforces it). Any new `*_tests.py` file must be registered in `tools/run_tool_tests.py`.
5. Repeat the checks and keep their exact output.
6. Push your branch to your fork and open a pull request against `dlprentice/Onslaught-Career-Editor`, filling in the [pull request template](.github/PULL_REQUEST_TEMPLATE.md).

Commit messages describe the change itself: leave out session/chat links, private paths and retail game bytes. A `Co-Authored-By` trailer is welcome when someone else co-authored the change.

## Licensing of contributions

Inbound = outbound: by opening a pull request you agree that your contribution is licensed under the same terms as the paths it changes, as [`REUSE.toml`](REUSE.toml) and any per-file SPDX line state them: code and schemas GPL-3.0-only ([`LICENSE`](LICENSE)), documentation, format-contract tables and lore CC BY-SA 4.0 ([`LICENSES/CC-BY-SA-4.0.txt`](LICENSES/CC-BY-SA-4.0.txt)). Contribute only work you have the right to license this way; credit quoted or third-party material and keep its notice.
<!-- REUSE-IgnoreStart -->
New code files start with an `SPDX-License-Identifier: GPL-3.0-only` comment.
<!-- REUSE-IgnoreEnd -->

## Files and retail inputs

Never commit retail binaries, game assets, converted copies, generated catalogues/inventories, arbitrary saves, Ghidra databases or backups, decompiler output, decomp source, debugger logs, private captures, credentials or `.env*` files. Use ignored `local-data/` ([`LOCAL_LAB_OVERLAY.md`](LOCAL_LAB_OVERLAY.md)) for local inputs and generated outputs.

- All Toolkit tools must treat the game installation as read-only and write outputs only to explicit output directories outside the game tree (via `tools/safe_generated_output.py`) or stdout.
- Save-related tools must start from real baselines and preserve unknown bytes rather than synthesizing `.bes` saves from scratch.
- `lore/` is the canonical public lore/history source; errata history lives in [onslaught-preservation's `history/lore-errata.md`](https://github.com/dlprentice/onslaught-preservation/blob/main/history/lore-errata.md).

## Validation

Use [`VALIDATION.md`](VALIDATION.md) to pick the smallest gate for your change. For documentation and payload boundary checks, run `npm run test:docs` and `npm run test:safety`; for tool changes, run the affected `*_tests.py` and `npm run test:tools`.
