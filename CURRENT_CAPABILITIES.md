# Current Capabilities

Status: active
Last updated: 2026-03-12

This file is the repo-level snapshot of what the active shipping stack can do right now.

Retail `BEA.exe` plus real `.bes` / `.bea` behavior remain authoritative. Source references remain useful for parity and naming, but they are not the shipping truth when they differ.

## Included Components

| Surface | Status | Notes |
|---|---|---|
| `OnslaughtCareerEditor.WinUI` | Active product | Primary desktop application |
| `OnslaughtCareerEditor.AppCore` | Active | Shared non-UI logic boundary |
| `OnslaughtCareerEditor.Cli` | Active | Supported command-line host |

## What The Active Stack Does

Save analysis:
- validates file size and version word
- decodes nodes, links, goodies, kill counters, tech slots, and known settings fields
- compares `.bes` and `.bea` files
- exposes reserved-byte detail views without claiming unknown regions are fully mapped

Save/config patching:
- patches `.bes` career progression safely
- patches `defaultoptions.bea` / `.bea` global settings with backup-aware behavior
- preserves packed kill-counter metadata bits
- preserves file size and unresolved regions

Binary patches:
- verify/apply/restore curated `BEA.exe` patch specs
- group patches by functional area
- keep stable/experimental track visible per patch

Lore/media:
- loads curated lore content from `lore-book/BOOK.md`
- plays game audio and video inline in the WinUI app

Shell/runtime:
- shared `Launch Game` action starts `BEA.exe` from the configured game directory
- shared Settings drive game-directory and media behavior for the app

## Documentation

- `README.MD`
- `reverse-engineering/RE-INDEX.md`
- `lore/LORE-INDEX.md`
- `lore-book/BOOK.md`
