# WinUI Online Companion Netplay Target Model Readiness Note

Status: product-surface contract complete
Date: 2026-06-22
Scope: WinUI Windowed & Mods online readiness language plus AppCore summary contract

This slice makes the intended first-generation netplay product shape explicit in the WinUI/AppCore surface: a host runs a safe copied game session, the second player joins from a separate safe copy, and WinUI or a packaged helper is expected to stay active for session identity, invitation/auth, relay/host authority, input delivery, cleanup, and proof/safety checks.

What changed:

- `OnlineMultiplayerReadinessService` now exposes `OnlineCompanionNetplayTarget`.
- Windowed & Mods now renders `PatchBenchOnlineTargetModel` and `PatchBenchOnlineCompanionModelDetails`.
- The visible copy says `Future design sketch; Host/Join unavailable` and keeps Host/Join disabled until live distinct endpoint command-source proof and source-bound copied-runtime causality both exist.
- Product-lane tests assert the target-model surface and the AppCore non-claim boundary.

Validation scope:

- AppCore focused tests prove the companion target contract is present.
- WinUI static/product-lane tests prove the Windowed & Mods XAML/code surface includes the target model without adding Host/Join controls.
- This slice used Codex read-only consult/adversarial review. Subagents did not edit state files.

Non-claims:

- No BEA launch.
- No CDB attach.
- No Ghidra mutation.
- No byte patch added or changed.
- No Host/Join enablement.
- No accepted live second-host proof.
- No public matchmaking proof.
- No native BEA netcode proof.
- No player-ready online multiplayer.
- No installed or original `BEA.exe` mutation.

Next proof boundary:

Before Host/Join can become tryable, the online ladder still needs accepted live distinct endpoint command-source proof plus source-bound copied-runtime causality in the same proof chain. Same-workstation or VM-only scaffolding may continue to harden the path, but it must not be described as player-ready netplay.
