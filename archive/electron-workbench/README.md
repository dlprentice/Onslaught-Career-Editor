# Archived Electron Workbench

Status: archived/reference
Last updated: 2026-05-05

This folder preserves the Electron/React/TypeScript workbench detour after the repo returned to a WinUI 3-first product direction.

The current product app is:

- `OnslaughtCareerEditor.WinUI/`

The current shared Windows core/support lane is:

- `OnslaughtCareerEditor.AppCore/`
- `OnslaughtCareerEditor.Cli/`
- `OnslaughtCareerEditor.AppCore.Tests/`
- `OnslaughtCareerEditor.UiTests/`

Electron is no longer an active product lane, public release lane, or default maintainer workflow. Keep it here for reference, provenance, and future extraction of narrow ideas only.

## Contents

| Path | Purpose |
| --- | --- |
| `apps/electron/` | Archived Electron main process, typed job runner, native adapters, and smoke scripts. |
| `packages/ui/` | Archived React/Vite renderer. |
| `packages/contracts/` | Archived TypeScript IPC/job/artifact contracts coupled to the Electron workbench. |
| `packages/cli/` | Archived TypeScript CLI over the Electron job runner. |
| `release/` | Archived Electron portable-bundle helpers and bundle-policy smoke scripts. |

## Optional Reference Commands

Run these only when deliberately investigating the archived Electron workbench:

```powershell
npm run archive:electron:build
npm run archive:electron:dev
npm run archive:electron:test:renderer-smoke
npm run archive:electron:test:parity
npm run archive:electron:test:cli-smoke
```

These commands are not WinUI product gates. If they fail, classify the failure as archived-workbench health unless the current task explicitly reactivates this archive.

## Rules

- Do not restart broad Electron product polish.
- Do not treat Electron as the community app.
- Do not route new player-facing UX into this archive.
- Do not expose raw Node, shell, filesystem, debugger, Ghidra, desktop capture, or input privileges to a renderer if this code is ever revived.
- Port useful logic out deliberately instead of reactivating the whole app.
