# Onslaught Toolkit Portable Bundle

This folder contains the portable Windows build of Onslaught Toolkit.

## What's Included

- `Launch Onslaught Toolkit.cmd` - root launcher for the desktop app
- `app/` - the complete self-contained app payload
- `app/OnslaughtCareerEditor.WinUI.exe` - desktop application
- `app/cli/` - command-line tools
- `app/lore-book/` - bundled lore and technical reference material
- `app/patches/catalog/` - bundled patch catalog
- `LICENSE`

## Quick Start

1. Double-click `Launch Onslaught Toolkit.cmd` from the bundle root.
2. In Settings, point the app at your Battle Engine Aquila install folder.
3. Open `app/lore-book/Start-Here.md` if you want the bundled reading guide.
4. Run `app/cli/OnslaughtCareerEditor.Cli.exe --help` for command-line usage.

## Bundled Docs

- `app/lore-book/Start-Here.md`
- `app/lore-book/BOOK.md`
- `app/lore-book/lore/LORE-INDEX.md`
- `app/lore-book/reverse-engineering/RE-INDEX.md`
- `app/lore-book/roadmap/ROADMAP-INDEX.md`

## Notes

- This portable bundle does not include the game itself.
- Everything the portable app needs lives under `app/`, so the zip root stays small.
- `Launch Onslaught Toolkit.cmd` is just a thin wrapper around `app/OnslaughtCareerEditor.WinUI.exe`.
