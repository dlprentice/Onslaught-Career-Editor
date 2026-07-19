# Onslaught Toolkit

Onslaught Toolkit is a preservation, tooling, and original-code reconstruction
project for *Battle Engine Aquila* (2003). The primary product is a WinUI 3
Windows app for inspecting and safely editing real save/options files, preparing
copied game profiles, applying evidence-backed patches to copied executables,
and browsing locally supplied media, catalogs, and project lore.

The toolkit never replaces or mutates the installed retail game. The
GPL-licensed [`rebuild/`](rebuild/README.md) lane is a separate RE-informed
implementation with deterministic Core behavior and a Godot handling lab. It
currently renders the released Aquila walker/jet, two Level 100 facilities,
coarse terrain, macro terrain blend, and sky at their bounded reconstruction
state; it does not claim retail parity. The
project has permission to use, modify, and distribute the original game assets;
integration into the rebuild remains implementation work, not a legal blocker.

## Active surfaces

| Path | Owner |
| --- | --- |
| `OnslaughtCareerEditor.WinUI/` | Primary Windows user experience |
| `OnslaughtCareerEditor.AppCore/` | Save, options, safe-copy, patch, media, catalog, and lore correctness |
| `OnslaughtCareerEditor.Cli/` | Unshipped maintainer adapter over AppCore |
| `rebuild/` | GPL RE-informed deterministic reconstruction |
| `reverse-engineering/` | Provenance-bounded technical evidence and format notes |
| `lore/` | Canonical public lore/history library |
| `tools/` | Focused extraction, validation, release, Ghidra, and copied-runtime helpers |

Retired Electron, Python GUI, WPF, generated readiness waves, and mirrored
documentation remain available in Git history; they are not current source
lanes. [`CURRENT_CAPABILITIES.md`](CURRENT_CAPABILITIES.md) describes what the
current product does and what remains unproven.

## Build and run

Requirements:

- Windows 10 or 11
- .NET 10 SDK for WinUI/AppCore/CLI and .NET 8 for the rebuild
- Node.js 24.x with npm 11.12.x
- Python 3 through the Windows `py` launcher
- PowerShell 7 for rebuild tooling

From the repository root:

```powershell
npm test
npm run dev
```

`npm test` builds the active solution once, then checks the consequential
save/codec/write/copy/patch contracts and the static WinUI accessibility audit.
It deliberately excludes broad UI, native Godot, release packaging, Ghidra,
local runtime evidence, and historical accounting.
Use the smallest focused command for narrower work:

```powershell
npm run test:appcore
npm run test:ui
npm run test:safe-copy
npm run test:cli
npm run test:docs
npm run test:safety
npm run test:rebuild-core
```

Root [`package.json`](package.json) is the command authority. See
[`VALIDATION.md`](VALIDATION.md) for proportional command selection and
[`CONTRIBUTING.md`](CONTRIBUTING.md) for contribution boundaries.

The Level 100 Opening Slice can be launched independently:

```powershell
npm run run:rebuild-godot
```

Its first run downloads and verifies the pinned Godot .NET archive into a
per-user cache. It does not require a retail game install.

## Data and mutation safety

- Never synthesize `.bes` saves from scratch. Start from a real baseline and
  preserve file length, reserved fields, and unknown bytes.
- Never patch an installed `BEA.exe`. Executable changes are allowed only on a
  verified copied target or an app-created safe game copy.
- Keep game binaries, real saves, Ghidra backups/alternate projects, debugger
  transcripts, private captures, secrets, bulk extraction output, and build
  output out of Git. The reviewed canonical Ghidra project is the sole database
  exception under `reverse-engineering/ghidra/`.
- The project owner's permission covers use, modification, and distribution of
  original game assets. Curate only assets consumed by an active product or
  rebuild slice, retain credits/provenance, and review third-party components
  separately. Parser success establishes format support, not visual fidelity.
- Online multiplayer is not player-ready. The app exposes a local split-screen
  copied-profile preset only; Host/Join remains unavailable.

The tracked regression fixture
`tests_shared/fixtures/gold_career_save.bin` is the reviewed narrow exception to
the no-save-payload rule. See [`SECURITY.md`](SECURITY.md) and
[`LOCAL_LAB_OVERLAY.md`](LOCAL_LAB_OVERLAY.md) for handling local inputs.

## Evidence and provenance

[`reverse-engineering/RE-INDEX.md`](reverse-engineering/RE-INDEX.md) is the
technical evidence front door. Static analysis proves only the identities and
structures it directly demonstrates; controlled copied-runtime work is needed
for observed behavior and measured values. Stuart's source and the pinned
[`references/Onslaught`](references/Onslaught) submodule are source references,
not proof of Steam behavior or exact source identity.

The canonical lore library begins at [`lore/_index.md`](lore/_index.md).
[`lore-book/BOOK.md`](lore-book/BOOK.md) is a short reading guide, not a mirror.
Release candidates generate an ignored short-path offline pack from those
canonical inputs.

## Releases and licenses

Published unsigned portable Windows ZIPs, when available, are on
[GitHub Releases](https://github.com/dlprentice/Onslaught-Career-Editor/releases).
The source checkout may be newer than the latest published asset. Building a
candidate does not publish, sign, install, or announce it; see
[`README.RELEASE.md`](README.RELEASE.md).

Repository licensing, third-party notices, source attribution, and the rebuild
GPL boundary remain authoritative in [`LICENSE`](LICENSE),
[`rebuild/LICENSE`](rebuild/LICENSE), [`rebuild/PROVENANCE.md`](rebuild/PROVENANCE.md),
and [`reverse-engineering/project-meta/attribution.md`](reverse-engineering/project-meta/attribution.md).
