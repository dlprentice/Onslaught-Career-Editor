# Tools Surface Map

Status: public-primary orientation note
Last updated: 2026-07-11

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

`npm run test:winui-primary-lane` runs `tools/winui_primary_lane_validation.py`
from the resolved repo/worktree root. On Windows, the wrapper warns when that
root is long enough that Windows App SDK/XAML compiler intermediate paths may be
fragile. The warning is diagnostic only: retry path-length diagnostics involving
generated XAML or intermediate compiler paths from a shorter clone/worktree
before classifying them, but treat unrelated build and test failures as real
failures.

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

## Generated Asset Export Safety

The pinned Onslaught/AYA provenance, build, format, test, and license inventory
is recorded in
`reverse-engineering/source-code/reference-submodule-audit-2026-07-12.md`.
Output-safety tests protect destination handling; they do not substitute for a
tracked end-to-end synthetic legacy importer/DDS/FBX fixture or prove exporter
format completeness.

`export_game_assets.py` writes only to a local output root that is physically
separate from the selected game tree. It validates every required source before
creating that root, holds source and output directory chains without following
reparse points, accepts only the current Python interpreter and the `dotnet`
resolved from `PATH`, and rescans the output around each child step.

`BeaAssetExportHarness` reads the tracked public AYA/FBX reference behavior but
does not give a third-party path writer a publishable output file. It builds FBX
and PNG bytes in memory, creates each final staged file through an exclusive
identity-held handle, requires the exact expected file/directory tree, and
copies from those handles into native same-directory atomic replacements. Its
self-test covers hardlink placement, concurrent writer rejection, output-root
identity, exact-handle publication, and game-tree rejection. Acceptance also
included a synthetic model smoke for FBX parsing, PNG output, final texture
paths, and staging cleanup without using game payloads.

`safe_generated_output.py` supplies the equivalent guarded writer for Python
inventory, language, video, and catalog producers. Those producers hold their
source inputs, write through native temporary handles, flush, rename the exact
handle, and verify the committed identity rather than trusting a temporary path.
Writable output directories use a transient delete-on-close guard installed
while a strict directory handle is held; this prevents an empty leased directory
from being converted in place to a reparse point without blocking normal child
publication. Guards disappear once another held output entry keeps the directory
nonempty and leave no catalog/package payload.

New file content is written only after the temporary identity is marked
POSIX-delete-pending and reports zero links. If a watcher creates an alias before
quarantine, the operation stops before writing. Disposition is cleared only
after bytes are final, so a hostile same-user hardlink created in the remaining
commit window can retain only the final bytes and forces commit rejection. It is
equivalent to copying a completed output; containment from that same-user action
is not a claimed security boundary.

`export_asset_catalog.py` emits one canonical
`<bundle>/asset_catalog/catalog.json` with schema `2` and the
`bundle-root-relative` path contract. Catalog JSON files use the same guarded
writer. `npm test` runs the generated-output guards and producer self-tests
before the product build/test gates. Keep the generated bundle ignored/local;
these safeguards do not make extracted game assets suitable for Git or release
packaging and do not make a multi-file export batch transactional.

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
