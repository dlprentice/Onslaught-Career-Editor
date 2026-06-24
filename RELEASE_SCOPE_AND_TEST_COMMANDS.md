# Release Scope And Test Commands

Status: active public-primary source and release gate
Last updated: 2026-06-24

This file defines repo validation and public safety/release gates. WinUI 3 is
the primary and only forward-facing GUI product lane. Electron, WPF, and the old
Python GUI/CLI app are archived/reference surfaces.

Important distinction: the public source repo is now the primary working repo
and intentionally contains broad source/docs/tools/RE history. The downloadable
portable app ZIP is a much smaller release artifact and must still exclude game
payloads, copied executables, arbitrary saves, full Ghidra databases, raw proof
captures, secrets, and build output.

## 1. Release Shape

The active product/support source shape is:

- `OnslaughtCareerEditor.WinUI/**`
- `OnslaughtCareerEditor.AppCore/**`
- `OnslaughtCareerEditor.AppCore.Tests/**`
- `OnslaughtCareerEditor.UiTests/**`
- `OnslaughtCareerEditor.Cli/**`
- `OnslaughtCareerEditor.AppCore.Host/**`
- `OnslaughtCareerEditor.WinUI.slnx`
- `OnslaughtCareerEditor.Release.slnx`
- `patches/**`
- `tools/**` for package gates, local validation, RE/runtime proof support, and
  public-primary migration checks
- public RE, lore, roadmap, readiness notes, state batons, and compact proof
  summaries

Ghidra static RE posture (Steam retail, loaded database):

- Function-quality closure remains **6411/6411 = 100.00%** with static debt `0 / 0 / 0`.
- Wave1220 aggregate static closeout acceptance validates active current-risk focused accounting at **1179/1179 = 100.00%** with remaining active focused work `0`.
- Public static summary front door: `reverse-engineering/RE-INDEX.md`. The
  detailed measurement registers under `reverse-engineering/binary-analysis/`
  are tracked source material. Static closeout does not prove runtime behavior,
  exact layouts, patch behavior, visual QA, gameplay outcomes, rebuild parity,
  or no-noticeable-difference parity.

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

Release-accounting inputs, repo state files, and historical checklists may be
tracked source material when non-secret and useful. They are not automatically
portable app ZIP payload.

## 2. What Is Included

The WinUI-first public source repo can include broad project material. Product
focus is WinUI-first; disposable unpackaged publish smoke, disposable unsigned
MSIX assembly, disposable local MSIX signing, untrusted-install blocking, and
TrustedPeople-only cleanup/blocker evidence are recorded as local evidence only,
while installer-grade trust/install/uninstall is still a separate future proof.

The public-safe source candidate can include:

- WinUI 3 product code
- AppCore/C# CLI/C# support projects and tests
- patch catalog and safe patch helpers
- reverse-engineering, lore, roadmap, readiness, state, and compact proof docs
  rooted at public indexes
- tools, scripts, checkers, and schemas that operate on user-supplied local
  overlays or public source material
- release/readiness policy artifacts and migration inventory reports

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

Git-tracked source and downloadable app ZIPs have different shapes. The public
source repo may track compact non-secret state batons, `.codex` project-history
notes, text subagent reports, readiness notes, and proof summaries when they are
useful to collaborators. Downloadable app ZIPs, legacy curated exports, and the
public source repo must still exclude hard payloads, including:

- `game/**`
- `media/**` unless a future public-safe media subset is explicitly classified
- `save-attempts/**`
- generated/raw payloads under `subagents/**`; compact text reports are allowed
- `release/artifacts/**` and `release/out/**`
- full Ghidra project databases/backups
- local proof/backup-root payloads and machine-specific generated outputs
- host-only local artifacts and packaged build output
- raw binaries, arbitrary saves/options payloads, screenshots, frame captures,
  media caches, raw CDB logs, copied runtime evidence, and secrets

Portable app ZIPs and legacy curated exports additionally exclude local
operator/project-history surfaces such as `.codex/**`, state batons, and bulky
or maintainer-only proof/accounting material. That exclusion does not make those
compact text files invalid in the public-primary source repo.

Narrow exception: `tests_shared/fixtures/gold_career_save.bin` is the tracked
immutable 10,004-byte regression baseline. Do not generalize that exception to
arbitrary `.bes`, `.bea`, options, or `save-attempts/` payloads.

Do not treat the former private repo as source authority. Do not treat Electron,
Python GUI, or WPF as the primary community product surfaces. Do not publish
signed/installer-grade WinUI release claims until that packaging path is
separately proven.

## 4. Public-Primary Source Gates

Maintainers and contributors run local gates from this public-primary source
tree. Some runtime/proof gates still require ignored local overlays such as a
valid game install, copied proof root, CDB log root, or local Ghidra project.

Public contributors should use the package commands in
`release/readiness/PUBLIC_SIGNOFF_COMMANDS.md` and `package.json`.

`npm run test:md-links` writes ignored reports under `subagents/md-link-check`; it is still a local validation gate, not a public payload.

`npm run test:public-primary-migration-inventory` compares this public repo to
the former private tracked index when the old private checkout is available.
`npm run test:hard-payload-safety` is the normal hard-payload guard for this
public-primary repo.

Archived Electron checks are reference checks only. Archive commands are not
default WinUI product, release, or UX gates.

## 4b. Local Validation Only

GitHub is used only as a git remote backup for this repo. Do not add hosted validation workflows as release or validation gates. Run validation locally with the commands in this document.

ZIP package probes, explicit WinUI UI Automation smokes, and installer/MSIX
probes remain local Windows desktop checks. `release/readiness/PUBLIC_SIGNOFF_COMMANDS.md`
identifies which commands are public source-candidate gates and which packaging
or installer claims remain out of scope. Private maintainer-only runtime variants
remain outside public export.

## 5. Curated Source/Export Validation

The public-primary source-tree workflow is WinUI-first for product source and
keeps hard payloads out by guard, not by reducing the source repo to a tiny
export:

<!-- public-package-commands:start -->
```powershell
npm run test:doc-commands
npm run test:md-links
npm run test:public-primary-migration-inventory
npm run test:winui-notices
npm run test:public-allowlist
npm run test:repo-hygiene
```
<!-- public-package-commands:end -->

Maintainers may still run release profile, curated manifest, and
`release_package.sh --dry-run` gates before packaging release artifacts. Those
are release-accounting checks, not a reason to make the public source sparse.

Materializing a curated tree may still be useful for package-shape safety
audits:

```powershell
py -3 tools\export_curated_release_tree.py --dest ..\Onslaught-Career-Editor-public-candidate --force-clean
```

`export_curated_release_tree.py` refuses to export from a dirty source tree.
Commit, stash, or intentionally clear local changes first so the exported
candidate has reproducible provenance. The export writes
`EXPORT_PROVENANCE.json` in the candidate root with the source commit, source
tree status, export timestamp, release allowlist/exporter hashes, selected-file
counts, and inventory requirement without serializing local source or destination
paths. `--force-clean` only replaces a sibling public-candidate directory that
is already marked as a previous export by `EXPORT_PROVENANCE.json` or
`.onslaught-public-candidate-export`; it is not a general recursive-delete
switch for arbitrary destinations.

Export materialization may still replace root `package.json`, `AGENTS.md`, and
`.gitignore` with package-shaped templates in the destination. That export shape
is for audit or app/package review only; it must not be treated as the complete
public source repo.

Run `npm run test:public-candidate-inventory` from a fresh exported candidate if
that candidate is being treated as a publishable payload. For normal development
in this public-primary repo, run `npm run test:hard-payload-safety` and
`npm run test:public-primary-migration-inventory`.

## 6. Pass Criteria

Public-primary source/release-ready means:

- Relevant lane gates pass for the lane being changed.
- WinUI/AppCore gates pass before claiming Windows product health.
- C# CLI help/build smoke passes before claiming CLI health.
- Public-primary migration inventory passes when the former private checkout is
  available.
- Hard-payload safety passes and no game/runtime payload, secret, build output,
  raw frame/CDB proof, or full Ghidra database is tracked.
- C# parity gates pass until their covered behavior is retired.
- Mutating workflows refuse repo-local/install-local originals and operate only on copied targets.
- App release ZIP/package contents exclude hard payloads and generated proof
  roots.
- Release docs identify WinUI 3 as the product lane.
- Electron, Python GUI, and WPF are documented as archived/reference only.
