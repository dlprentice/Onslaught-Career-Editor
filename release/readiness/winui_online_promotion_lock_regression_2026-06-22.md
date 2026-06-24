# WinUI Online Promotion Lock Regression - 2026-06-22

Status: complete local contract hardening
Scope: Windowed & Mods online readiness surface, AppCore online readiness model, and second-host live candidate gate

This slice makes the online readiness lane harder to misread as player-ready Host/Join enablement.

What changed:

- `OnlineMultiplayerReadinessService` now emits an explicit `Host/Join promotion lock` status row.
- The proof-gate rows now include `Host/Join promotion` with the requirement that readiness/run-kit/controller artifacts cannot promote Host/Join without accepted distinct-endpoint command-source proof plus source-bound copied-runtime causality proof.
- The WinUI technical online details now render `PatchBenchOnlinePromotionLockStatus` with plain-language `online play is not available in this release` copy.
- Loaded second-host readiness/run-kit text now states that online play is not available in this release and Host/Join remains unavailable.
- The local safe-copy action status now states that the only tryable action remains local split-screen, not Host/Join or online proof.
- `winui_original_binary_second_host_live_candidate_gate.py` now rejects prose-level public/doc overclaims that imply host/join availability or player-ready online play, not just `field=true` boolean overclaims.

Validation:

- `dotnet test .\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo --filter "FullyQualifiedName~OnlineMultiplayerReadinessServiceTests"`
- `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiProductLaneTests.PatchBench|FullyQualifiedName~WinUiAccessibilityAuditTests.PrimaryShellAndLongWorkflowControls"`
- `npm run test:winui-original-binary-second-host-live-candidate-gate`

Non-claims:

- No BEA launch.
- No CDB attach.
- No DirectInput or physical-controller runtime proof.
- No distinct-endpoint command-source proof.
- No source-bound copied-runtime causality proof.
- No Host/Join implementation.
- No player-ready online multiplayer.
- No public matchmaking.
- No native BEA netcode.
