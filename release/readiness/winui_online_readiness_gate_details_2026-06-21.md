# WinUI Online Readiness Gate Details

Status: product-surface hardening; no live netplay proof accepted
Date: 2026-06-21

This slice updates the WinUI Windowed & Mods online readiness panel and `OnlineMultiplayerReadinessService` so the disabled Host/Join state names the current proof gates instead of only saying online is blocked.

What changed:

| Area | Requirement |
| --- | --- |
| Proof gate rows | `OnlineMultiplayerReadinessService` exposes live command-source, current hardening, runtime-causality, and fallback rows. |
| Companion readiness | `OnlineMultiplayerReadinessService` exposes `winui-original-binary-companion-session-readiness.v1` for missing, stale, launch-plan-blocked, or ready safe-copy launch states. |
| WinUI rendering | Windowed & Mods renders gate details and disabled-action reasons. |
| Host/Join boundary | Host and Join still have no buttons and remain blocked until accepted live distinct command-source proof plus source-bound runtime causality. |
| UI-surfaced hardening | The UI/service text includes `maxJsonLineBytes=4096` and live physical rejection of `operator-supplied-runtime-host-kind`; deeper non-fixture identity/timestamp/source-hash validation remains enforced by the proof checkers. |
| Runtime-causality dependency | The UI/service text names exact-PID CDB evidence, mapped P2 sequence, host-helper receipt, accepted payload hash binding, and invitation lifecycle hash binding. |
| Safe-copy binding | Missing, stale, or launch-plan-blocked safe copies expose no tryable online-adjacent action; a ready safe copy exposes only the local multiplayer probe. |

Non-claims:

- `acceptedLiveSecondHostCommandSourceProof=false`
- `acceptedLiveSecondHostRuntimeDeliveryProof=false`
- `acceptedLiveSecondHostRuntimeCausalityProof=false`
- `hostJoinControlsMayBeEnabled=false`
- `baseOnlineMultiplayerReady=false`
- `newBeaLaunchCount=0`
- `cdbAttachCount=0`
- no Host/Join buttons
- missing/stale safe copies do not expose online-adjacent tryable actions
- no public endpoint
- no player-ready netplay

Focused gates:

```powershell
dotnet test OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo --filter "FullyQualifiedName~OnlineMultiplayerReadinessServiceTests"
dotnet test OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiProductLaneTests.PatchBench_VisibleCopyPromisesCopiedExecutableWorkflow"
```
