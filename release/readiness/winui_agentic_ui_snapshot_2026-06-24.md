# WinUI Agentic UI Snapshot Readiness Note

Status: focused runtime UIA snapshot evidence complete
Date: 2026-06-24
Scope: WinUI agentic UI inspection hardening

## Summary

This slice keeps WinUI 3 as the primary product lane and adds the first
agent-readable UI inspection artifact. It does not migrate the app to Blazor,
Tauri, Electron, Avalonia, or Python.

The new explicit command is:

```powershell
npm run test:winui-agentic-ui-snapshot
```

The command launches the current WinUI app in an interactive Windows desktop
session, opens representative Home and Windowed & Mods surfaces, and writes
path-redacted UI Automation tree snapshots under:

```text
subagents/winui-agentic-ui-snapshot/current/
```

Generated ignored artifacts from this run:

| Artifact | Evidence |
| --- | --- |
| `home.uia.json` | Home snapshot; 56 UIA nodes, 32 automation IDs, 51 named nodes. |
| `windowed-mods.uia.json` | Windowed & Mods snapshot; 281 UIA nodes, 74 automation IDs, 276 named nodes. |
| `manifest.json` | Snapshot manifest; schema `winui-agentic-accessibility-snapshot.v1`; local path redaction count `0` for both scenarios. |

## Durable Decision

The platform decision is recorded in
`roadmap/winui-agentic-ui-hardening-plan.md` and linked from
`roadmap/winui-ui-ux-redesign-radar.md`.

Current call:

- Keep WinUI 3 as the flagship user-facing Windows product lane.
- Improve agentic workflow through UIA snapshots, ViewModel extraction,
  screenshot smokes, and cleaner page decomposition before considering a
  framework rewrite.
- Treat Blazor Hybrid / WinUI-hosted WebView as a future challenger spike only
  if measured WinUI hardening still fails the agentic workflow bar.
- Keep Electron and Python GUI lanes archived/reference unless a later explicit
  strategy reset reopens them.

## Validation

Focused validation completed:

```powershell
dotnet build .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo
dotnet build .\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj --nologo
npm run test:winui-agentic-ui-snapshot
```

Additional artifact checks:

- `package.json` parsed successfully as JSON.
- Generated snapshot JSON parsed successfully.
- Generated snapshot JSON had no `C:\...` local path tokens.
- No `OnslaughtCareerEditor.WinUI` process was left running after the smoke.

## Non-Claims

This slice does not prove or claim:

- UI redesign completion.
- MVVM/ViewModel extraction completion.
- Blazor/Tauri/Electron/Avalonia/Python migration readiness.
- Safe-copy runtime behavior.
- BEA launch, CDB attach, byte patch, installed-game mutation, original
  executable mutation, online multiplayer readiness, Host/Join enablement,
  rebuild parity, or runtime music audible-output proof.

The snapshot artifacts are private ignored evidence only and are not public
release payload.
