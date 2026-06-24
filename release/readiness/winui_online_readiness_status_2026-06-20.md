# WinUI Online Readiness Status

Status: product-surface guard complete; no new runtime proof
Date: 2026-06-20
Scope: Windowed & Mods online planning/status surface

The WinUI Windowed & Mods page now exposes a passive online readiness panel backed by `OnlineMultiplayerReadinessService`. The panel keeps the current multiplayer truth visible before any Host/Join controls are enabled:

- `BaseOnlineMultiplayerReady=false`
- `MultiHostLanProof=false`
- `PublicMatchmakingProof=false`
- `NativeBeaNetcodeProof=false`
- `ActiveP3P4OriginalBinaryGameplayProof=false`
- accepted original-binary gameplay slots: `P1`, `P2`
- metadata-only slots: `P3`, `P4`
- only safe tryable action: Local Multiplayer Probe with `-skipfmv -level 850`

The WinUI surface intentionally does not add `PatchBenchHostOnlineSessionButton`, `PatchBenchJoinOnlineSessionButton`, or `PatchBenchPublicMatchmakingButton`. The blocked actions are displayed as status text only: Host online session, Join online session, Public matchmaking, and Native BEA netcode.

Validation anchors:

- `OnlineMultiplayerReadinessService.GetCurrentSummary()` centralizes the status rows, tryable action, blocked actions, and non-claims.
- `OnlineMultiplayerReadinessServiceTests` verifies the P1/P2 versus P3/P4 boundary, non-claims, and disabled Host/Join path.
- `WinUiProductLaneTests.PatchBench_VisibleCopyPromisesCopiedExecutableWorkflow` verifies the panel is present and that Host/Join/Matchmaking buttons are absent.
- `dotnet build OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj --nologo` verifies XAML/code-behind integration.

Non-claims:

- This does not implement player-ready online multiplayer.
- This does not prove second-host LAN play.
- This does not add public matchmaking.
- This does not add native BEA netcode.
- This does not prove active P3/P4 original-binary gameplay.
- This does not add a new BEA launch, CDB attach, runtime artifact, executable-byte mutation, Ghidra mutation, or public release.
