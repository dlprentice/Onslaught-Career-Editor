# Tools Surface Map

Status: public-primary orientation note
Last updated: 2026-06-24

`tools/` in this public-primary repo is tracked project tooling for release
checks, AppCore/WinUI smoke helpers, RE support, runtime proof wrappers, and
local lab workflows. Some tools require ignored local overlays such as a user
supplied game install, a local Ghidra project, copied runtime output, or an
external proof root. Do not treat every historical script name as a normal PR
gate or user-facing workflow; use the root `package.json` and active docs as the
current command authority.

## Public Repo Gates

The root `package.json` is the command authority for external contributors.
Start with:

- `npm run test:doc-commands`
- `npm run test:md-links`
- `npm run test:public-allowlist`
- `npm run test:repo-hygiene`
- `npm run test:winui-primary-lane`
- `npm run test:winui-safe-copy-preflight`
- `npm run test:winui-patch-engine-safety`

Use `release/readiness/PUBLIC_SIGNOFF_COMMANDS.md` for the public source and
portable app sign-off sequence.

## Legacy Export Helpers

`tools/export_curated_release_tree.py` remains for legacy/export diagnostics and
release-accounting checks. The normal source-of-truth repo is now this public
checkout, not a tiny generated source candidate.

## Evidence And Maintainer Helpers

Many tools validate bounded evidence, but they are not normal public gates
unless the root `package.json` or an active runbook calls them. Live copied-game
launches, CDB/Ghidra work, second-host networking proof, asset extraction
output, and runtime proof roots remain maintainer-controlled workflows with
separate authorization and safety boundaries.

For bulky live copied-game proof runs, prefer an explicit private artifact root
outside git and keep local machine-specific paths out of public-facing claims
unless they are necessary provenance in a compact proof summary. Raw runtime
artifacts can contain local paths, copied-profile paths, screenshots, CDB logs,
and other bulky proof material; do not commit them. Track compact summaries and
machine-checkable counters instead.

Defender posture: live runtime helpers are maintainer-only and arm-gated. They
may compile a local runner, launch a copied executable, attach CDB, capture
frames, and send scoped input by design. Prefer tracked scripts, narrow
arguments, and one reviewed external proof root instead of inline shell byte
dumps or broad ad hoc scans.

## Agent Skill Routing

Some maintainers have user-local Codex skills that route BEA work into this
tracked tool/docs surface. They are not required for a public clone and should
not be copied from a runtime directory into the repo.

| Local skill | Public source of truth |
| --- | --- |
| `aya-assets` | `reverse-engineering/game-assets/_index.md`, `reverse-engineering/game-assets/extraction-pipeline.md`, `tools/export_game_assets.py`, `tools/export_asset_catalog.py`, `tools/aya_archive_inventory.py` |
| `bea-binary-re` | `reverse-engineering/binary-analysis/GHIDRA-REFERENCE.md`, `reverse-engineering/binary-analysis/ghydra-mcp-runbook.md`, `reverse-engineering/binary-analysis/windbg-cdb-runbook.md`, `patches/README.md`, `patches/catalog/patches.v2.json` |
| `bes-career-save` | `reverse-engineering/save-file/save-format.md`, `reverse-engineering/save-file/struct-layouts.md`, `reverse-engineering/quick-reference/save-structs.md`, `tools/options_entries_decode.py` |
| `onslaught-engine-source` | `references/Onslaught/`, `reverse-engineering/source-code/`, `reverse-engineering/game-mechanics/`, `reverse-engineering/quick-reference/source-key-functions.md` |

If a local skill says something different from tracked repo docs, treat that as
a drift bug. Update the tracked docs or the local skill source after review; do
not rely on untracked runtime state as contributor authority.
