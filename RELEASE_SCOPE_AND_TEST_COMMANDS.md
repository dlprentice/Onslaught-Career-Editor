# Release Scope And Test Commands

Status: active public safety/export gate
Last updated: 2026-06-23

This file defines repo validation and public safety/export gates. WinUI 3 is the primary and only forward-facing GUI product lane. Electron, WPF, and the old Python GUI/CLI app are archived/reference surfaces. The curated public safety/export boundary remains explicit and must not be replaced by a broad repo copy.

## 1. Release Shape

The active product/support repo shape is:

- `OnslaughtCareerEditor.WinUI/**`
- `OnslaughtCareerEditor.AppCore/**`
- `OnslaughtCareerEditor.AppCore.Tests/**`
- `OnslaughtCareerEditor.UiTests/**`
- `OnslaughtCareerEditor.Cli/**`
- `OnslaughtCareerEditor.AppCore.Host/**`
- `OnslaughtCareerEditor.WinUI.slnx`
- `OnslaughtCareerEditor.Release.slnx`
- `patches/**`
- curated public-safe `tools/` subset for package gates and local validation
- curated public RE, lore, roadmap, and public-safe release tooling

Ghidra static RE posture (Steam retail, loaded database):

- Function-quality closure remains **6411/6411 = 100.00%** with static debt `0 / 0 / 0`.
- Wave1220 aggregate static closeout acceptance validates active current-risk focused accounting at **1179/1179 = 100.00%** with remaining active focused work `0`.
- Public static summary front door: `reverse-engineering/public-static-contracts.md`. Private maintainers keep the detailed measurement register in the private tree. Static closeout does not prove runtime behavior, exact layouts, patch behavior, visual QA, gameplay outcomes, rebuild parity, or no-noticeable-difference parity.

Archived/reference app surfaces:

- `archive/electron-workbench/**`
- `archive/legacy-python/**`
- `archive/legacy-wpf/**`
- `archive/legacy-winui-release/**`

Authoritative strategy docs:

- `README.MD`
- `CONTRIBUTING.md`
- `SECURITY.md`
- `CURRENT_CAPABILITIES.md`
- `roadmap/public-roadmap.md`
- `roadmap/three-lane-product-strategy.md`
- `roadmap/repo-structure-and-archive-map.md`
- `release/readiness/PUBLIC_SIGNOFF_COMMANDS.md`
- `release/readiness/redaction_notes.md`
- `release/readiness/public_AGENTS.md` (materialized as public root `AGENTS.md`)
- `EXPORT_PROVENANCE.json` in materialized public candidates

Private release-accounting inputs, repo state files, and historical operator
checklists remain private maintainer material, not public payload authority.

## 2. What Is Included

The WinUI-first source/export candidate can include only public-safe files selected by the curated manifest. Product focus is WinUI-first; private maintainer disposable unpackaged publish smoke, disposable unsigned MSIX assembly, disposable local MSIX signing, untrusted-install blocking, and TrustedPeople-only cleanup/blocker evidence are recorded as maintainer evidence only, while installer-grade trust/install/uninstall is still a separate future proof.

The public-safe source candidate can include:

- WinUI 3 product code
- AppCore/C# CLI/C# support projects and tests
- patch catalog and safe patch helpers
- curated public-safe reverse-engineering, lore, and roadmap docs rooted at
  public indexes
- reviewed tools when public-safe and selected by the curated public manifest
- release/readiness policy artifacts that are public-safe

Current WinUI binary smoke is intentionally unpackaged. Private maintainers can
use the private root scripts for publish, ZIP, unsigned MSIX, signing,
untrusted-install, and trusted-install probes under ignored `subagents/`.
Public source candidates may include reviewed public-safe probe source when the
script fails closed, uses local explicit-arm guards for state-changing actions,
and is not listed as a public sign-off gate. Do not claim installer-grade
release from source validation, unpackaged publish smoke, unsigned package
assembly, local signing proof, blocked untrusted install proof, or
TrustedPeople-only blocker proof alone.

## 3. What Is Excluded

Public/community release outputs must exclude private, local, archived, or operator-only families, including:

- `game/**`
- `.codex/**`
- `media/**` unless a future public-safe media subset is explicitly classified
- `save-attempts/**`
- `subagents/**`
- `archive/**`
- `release/readiness/private_runtime_evidence/**`
- `onslaught_codex_directive.md`
- repo state files
- private scratch/generated outputs
- local proof/backup-root payloads and machine-specific backup paths
- private release inventories and private sign-off runbooks
- host-only local artifacts and packaged build output
- raw binaries, saves, screenshots, frame captures, media caches, and private runtime evidence

Do not treat the private repo as public-shaped. Do not treat Electron, Python GUI, or WPF as the primary community product surfaces. Do not publish signed/installer-grade WinUI release claims until that packaging path is separately proven.

## 4. Private-Tree Export Gates

Private maintainers run the private release profile, curated manifest,
public-allowlist, repo-hygiene, WinUI/AppCore, and runtime/proof gates from the
private source tree before export. Those private gates can reference scripts,
runtime helpers, Ghidra evidence, copied-game proof roots, and scratch outputs
that are intentionally absent from public source candidates.

Public contributors should use the public package commands in
`release/readiness/PUBLIC_SIGNOFF_COMMANDS.md`, not private maintainer command
lists copied from the private root.

`npm run test:md-links` writes ignored reports under `subagents/md-link-check`; it is still a local validation gate, not a public payload.

In the private source tree, `npm run test:public-candidate-inventory` runs the
inventory checker's self-test only. The materialized public candidate's
`package.json` runs the self-test plus `--candidate-root .`, which is the real
payload inventory check for an exported tree.

Archived Electron checks are private-maintainer reference checks only. Public
source candidates exclude `archive/**`, so archive commands are not public
package commands or default WinUI product, release, or UX gates.

## 4b. Local Validation Only

GitHub is used only as a git remote backup for this repo. Do not add hosted validation workflows as release or validation gates. Run validation locally with the commands in this document.

ZIP package probes, explicit WinUI UI Automation smokes, and installer/MSIX
probes remain local Windows desktop checks. `release/readiness/PUBLIC_SIGNOFF_COMMANDS.md`
identifies which commands are public source-candidate gates and which packaging
or installer claims remain out of scope. Private maintainer-only runtime variants
remain outside public export.

## 5. Curated Source/Export Validation

The curated public-candidate source-tree workflow is available for source-safety review. It is WinUI-first for product source and excludes archived app surfaces and private runtime/proof helpers by default:

<!-- public-package-commands:start -->
```powershell
npm run test:doc-commands
npm run test:md-links
npm run test:public-candidate-inventory
npm run test:winui-notices
npm run test:public-allowlist
npm run test:repo-hygiene
```
<!-- public-package-commands:end -->

Private maintainers run the private source-tree release profile, curated
manifest, and `release_package.sh --dry-run` gates before materializing a public
candidate. Those private manifest/accounting gates are not public PR gates
because the public candidate does not include the private curated manifest or
private inventory artifacts.

Materializing a curated tree may still be useful for safety audits:

```powershell
py -3 tools\export_curated_release_tree.py --dest ..\Onslaught-Career-Editor-public-candidate --force-clean
```

`export_curated_release_tree.py` refuses to export from a dirty private source
tree. Commit, stash, or intentionally clear local changes first so the exported
candidate has reproducible provenance. The export writes
`EXPORT_PROVENANCE.json` in the candidate root with the source commit, source
tree status, export timestamp, release allowlist/exporter hashes, selected-file
counts, and inventory requirement without serializing local source or destination
paths. `--force-clean` only replaces a sibling public-candidate directory that
is already marked as a previous export by `EXPORT_PROVENANCE.json` or
`.onslaught-public-candidate-export`; it is not a general recursive-delete
switch for arbitrary destinations.

The source/private root `package.json`, root `AGENTS.md`, and root `.gitignore` are excluded from the public candidate. Export materialization copies `release/readiness/public_package.json` to root `package.json`, `release/readiness/public_AGENTS.md` to root `AGENTS.md`, and `release/readiness/public_gitignore.txt` to root `.gitignore` in the destination. It also materializes public-safe RE, roadmap, lore, and lore-book index variants so the exported documentation graph is curated and link-closed without copying private proof forests. In exported candidates, the root materialized docs are the reader-facing versions; `release/readiness/public_*` files are export templates/mirrors managed from the private source. The export keeps the public source files in `release/readiness/` and reruns destination public safety and markdown-link checks before reporting success.

Run `npm run test:public-candidate-inventory` from a fresh exported candidate
before install/build/test commands if the candidate is being treated as a
publishable payload. The check is expected to fail after validation writes
generated local artifacts such as `bin/`, `obj/`, `subagents/`, `node_modules/`,
or package-lock files. After standalone product/docs validation, regenerate a
fresh candidate from the same pushed source commit before sharing or publishing.

## 6. Pass Criteria

Public-safety/export-ready means:

- Relevant lane gates pass for the lane being changed.
- WinUI/AppCore gates pass before claiming Windows product health.
- C# CLI help/build smoke passes before claiming CLI health.
- Public-safe release candidate evidence exists and the public allowlist has no private/runtime/archive forbidden families or local proof/backup-root payloads.
- C# parity gates pass until their covered behavior is retired.
- Mutating workflows refuse repo-local/install-local originals and operate only on copied targets.
- Bundle/export contents exclude agent, private game/media/save/subagent/state/archive paths.
- Release docs identify WinUI 3 as the product lane.
- Electron, Python GUI, and WPF are documented as archived/reference only.
