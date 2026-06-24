# Onslaught Workbench Electron Portable Bundle

Status: active maintainer-workbench portable bundle
Last updated: 2026-05-04

This bundle is the Electron maintainer/agentic RE workbench shape for Onslaught Toolkit. It is built from the TypeScript/Electron workbench. It is not the primary user-facing product lane; WinUI 3 owns that role.

## What's included

- `Launch Onslaught Workbench.cmd` - root launcher for the Electron app
- `runtime/electron/` - bundled Electron runtime from npm
- `app/electron/dist/` - Electron main-process host and typed IPC/job runner
- `app/ui/` - built React/Vite renderer
- `app/patches/catalog/` - curated patch metadata only
- community builds include only the curated community-safe docs allowlist
- maintainer builds may also include maintainer docs and allowlisted local helper scripts

The bundle does not include `game/`, `media/`, `save-attempts/`, repo state files, or subagent investigation folders. Users bring their own Battle Engine Aquila install, save files, and output folders.

## Quick start

1. Double-click `Launch Onslaught Workbench.cmd`.
2. Open Game Harness and select your Battle Engine Aquila install folder.
3. Use Save Lab for copied-save/options workflows.
4. Use Patch Bench for copied-`BEA.exe` patch workflows.
5. Use Media for local catalog browsing, OGG audio playback, and cataloged Bink `.vid` preparation into the app-owned MP4 cache when VLC or `ONSLAUGHT_VLC_PATH` is available.

## Safety model

- Renderer code never receives raw Node, shell, debugger, Ghidra, or filesystem access.
- Native operations run through typed Electron IPC and allowlisted job definitions.
- Mutating jobs operate on copied targets under the app artifact/profile root.
- Launch/debug jobs require explicit arm phrases and safe copied profiles.

## Legacy surfaces

The older WinUI portable bundle helper is kept only as historical packaging reference. WPF is archived/reference only. Python is active RE/tooling/lab support, not a shipping GUI/product lane. C# AppCore/CLI code remains in the repo while the Windows lane and parity gates still need it.
