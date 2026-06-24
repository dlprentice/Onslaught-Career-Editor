# Onslaught Toolkit Legacy WinUI Portable Bundle

> **SUPERSEDED — archived/historical (2026-05-26):** Electron is **not** the active product surface. WinUI 3 (`OnslaughtCareerEditor.WinUI/`) is the primary product lane. This folder is a legacy WinUI portable-bundle helper only.

Status: legacy WinUI reference bundle / archived/historical
Last updated: 2026-05-01

This folder contains the historical WinUI portable Windows build of Onslaught Toolkit. It remains only for reference/parity history—not for current product releases.

## What's Included

- `Launch Onslaught Toolkit.cmd` - root launcher for the legacy WinUI desktop app
- `app/` - the complete self-contained WinUI payload
- `app/OnslaughtCareerEditor.WinUI.exe` - legacy WinUI desktop application
- `app/cli/` - temporary C# parity command-line tools
- `app/lore-book/` - bundled lore and technical reference material
- `app/patches/catalog/` - bundled patch catalog
- `LICENSE`

## Quick Start

1. Double-click `Launch Onslaught Toolkit.cmd` from the bundle root.
2. In Settings, point the app at your Battle Engine Aquila install folder.
3. Open `app/lore-book/Start-Here.md` if you want the bundled reading guide.
4. Run `app/cli/OnslaughtCareerEditor.Cli.exe --help` only when validating the temporary parity CLI.

## Bundled Docs

- `app/lore-book/Start-Here.md`
- `app/lore-book/BOOK.md`
- `app/lore-book/lore/LORE-INDEX.md`
- `app/lore-book/reverse-engineering/RE-INDEX.md`
- `app/lore-book/roadmap/ROADMAP-INDEX.md`

## Notes

- This portable bundle does not include the game itself.
- Everything the portable app needs lives under `app/`, so the zip root stays small.
- `Launch Onslaught Toolkit.cmd` is a thin wrapper around `app/OnslaughtCareerEditor.WinUI.exe`.
- This is not the Electron release package.
