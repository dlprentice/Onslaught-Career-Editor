# WinUI Second-Host Readiness Artifact Parser Hardening

Status: parser hardening validated
Date: 2026-06-22
Scope: `OnlineMultiplayerReadinessService` redacted readiness/run-kit JSON intake

This follow-up hardens the local WinUI/AppCore artifact intake for second-host readiness and run-kit summaries. It does not change Host/Join availability and does not add runtime proof.

## Hardening

- Caps local readiness/run-kit JSON artifact files at 64 KiB before reading.
- Requires every current Host/Join/online proof boolean to be present as JSON `false`.
- Recursively rejects Host/Join/online proof keys with JSON `true`, nonzero numeric values, or truthy strings such as `true`, `1`, `yes`, `enabled`, `accepted`, or `ready`.
- Allowlists schema-specific status strings before WinUI can display artifact status.
- Recursively rejects private/sensitive string data, including local paths, UNC paths, private IP literals, GitHub-style tokens, bearer/API/password-like values, and private repo path markers.
- Bounds readiness counters to `0..4096`.
- Rejects `ready-to-run-live-command-source` run kits unless host command inputs, client preflight, attempt readiness, and live-validation readiness are all present.

## Validation

```powershell
dotnet test .\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo --filter "FullyQualifiedName~OnlineMultiplayerReadinessServiceTests"
dotnet build .\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj --nologo
npm run test:winui-original-binary-second-host-live-readiness
npm run test:winui-original-binary-second-host-live-run-kit
```

## Non-Claims

- No listener.
- No invitation.
- No BEA launch.
- No CDB attach.
- No input sent.
- No Host/Join enablement.
- No accepted live second-host command-source proof.
- No source-bound copied-runtime causality proof.
- No player-ready online multiplayer.
