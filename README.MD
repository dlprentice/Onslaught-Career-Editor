# Onslaught Toolkit

Status: active
Last updated: 2026-03-11

Onslaught Toolkit is a Battle Engine Aquila (2003) toolkit focused on retail-backed save editing, global options editing, curated binary patch workflows, lore browsing, and media playback.

## Included Components

| Surface | Status | Notes |
|---|---|---|
| `OnslaughtCareerEditor.WinUI` | Active product | Primary Windows desktop app |
| `OnslaughtCareerEditor.AppCore` | Active | Shared retail-backed engine |
| `OnslaughtCareerEditor.Cli` | Active | Supported command-line host |

## Current Capabilities

- `Saves`
  - Save Analyzer for `.bes` and `.bea`
  - Save Editor for `.bes` career files
  - Configuration Editor for `defaultoptions.bea` and other `.bea` options snapshots
- `Binary Patches`
  - verify/apply/restore curated `BEA.exe` patches
  - grouped by functional area with explicit stable/experimental labeling
- `Lore`
  - in-app curated lore browser backed by `lore-book/BOOK.md`
- `Media`
  - in-app audio playback
  - in-app video playback
- `Settings`
  - game-directory selection and shared media behavior options
- `Launch Game`
  - shell action that starts `BEA.exe` from the configured game directory

## Quick Start

From repo root:

```powershell
dotnet build ".\OnslaughtCareerEditor.Release.slnx"
dotnet run --project ".\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj"
dotnet run --project ".\OnslaughtCareerEditor.Cli\OnslaughtCareerEditor.Cli.csproj" -- --help
```

## Safety Rules

- Never create `.bes` career files from scratch.
- Treat retail `BEA.exe` and real save/options files as authoritative.
- Preserve file size and reserved/unknown regions unless the behavior is explicitly documented.
- `defaultoptions.bea` is authoritative for boot-time global options.

## Requirements

- Windows 10/11
- .NET 10 SDK to build
- a valid Battle Engine Aquila installation for game-aware workflows

Common Steam path:
- `C:\Program Files (x86)\Steam\steamapps\common\Battle Engine Aquila`

## Core Docs

- [CURRENT_CAPABILITIES.md](CURRENT_CAPABILITIES.md)
- [reverse-engineering/RE-INDEX.md](reverse-engineering/RE-INDEX.md)
- [lore/LORE-INDEX.md](lore/LORE-INDEX.md)
- [lore-book/BOOK.md](lore-book/BOOK.md)

## License

MIT. See [LICENSE](LICENSE).
