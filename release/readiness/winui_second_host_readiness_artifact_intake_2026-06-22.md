# WinUI Second-Host Readiness Artifact Intake Readiness Note

Status: product-surface contract complete
Date: 2026-06-22
Scope: WinUI Windowed & Mods redacted readiness artifact intake, not Host/Join enablement

This slice lets Windowed & Mods load a redacted second-host live-readiness or live-run-kit JSON artifact and render only sanitized readiness status. It also clarifies the current top-level online action: select the local split-screen launch preset, create a safe copy, then play that safe copy. This remains local split-screen only.

What changed:

- `OnlineMultiplayerReadinessService` can parse `winui-original-binary-second-host-live-readiness.v1` and `winui-original-binary-second-host-live-run-kit.v1` summaries.
- The parser rejects unsupported schemas, missing proof booleans, Host/Join or online overclaim booleans, invalid JSON, unreadable files, and run-kit artifacts that report raw private paths serialized in public docs.
- The parser now also rejects oversized local artifacts, missing required false proof keys, nested string/numeric truthy proof overclaims, unsupported display statuses, private/sensitive nested strings such as local paths, private IPs, and token-like values, out-of-range readiness counters, and ready-to-run run kits without matching host/client prerequisites.
- Windowed & Mods now exposes `Load readiness JSON` and `Clear readiness` in Technical online details.
- The page renders status, `readyToRunLiveCommandSource`, `serverCommandInputsComplete`, `clientPreflightProvided`, private-bind/WSL counts, and still keeps Host/Join unavailable.
- The online prep button now says `Use local split-screen launch preset` and records the next user steps: create safe copy, then play safe copy.

Validation:

```powershell
dotnet test .\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo --filter "FullyQualifiedName~OnlineMultiplayerReadinessServiceTests"
dotnet build .\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj --nologo
dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiProductLaneTests.PatchBench|FullyQualifiedName~WinUiAccessibilityAuditTests.PrimaryShellAndLongWorkflowControls"
npm run test:winui-original-binary-second-host-live-readiness
npm run test:winui-original-binary-second-host-live-run-kit
npm run test:winui-original-binary-second-host-command-source
npm run test:winui-original-binary-second-host-runtime-causality
npm run test:winui-original-binary-host-join-enablement
npm run test:winui-safe-copy-preflight
```

Non-claims:

- No listener.
- No invitation.
- No BEA launch.
- No CDB attach.
- No Ghidra mutation.
- No byte patch added or changed.
- No input sent.
- No Host/Join enablement.
- No accepted live second-host command-source proof.
- No source-bound copied-runtime causality proof.
- No public matchmaking proof.
- No native BEA netcode proof.
- No player-ready online multiplayer.
- No installed or original `BEA.exe` mutation.
