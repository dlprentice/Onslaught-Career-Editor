# WinUI Dual Safe-Copy Topology Intake

Status: passive topology intake and display only
Date: 2026-06-23
Scope: Windowed & Mods technical online-readiness details

This slice makes the existing public-safe dual-safe-copy topology contract
loadable through AppCore and visible in the WinUI Windowed & Mods maintainer
diagnostics panel. It does not create a new topology contract and does not move
Host/Join closer by itself; it only gives the app a bounded way to display that
the companion model expects one future host safe copy and one future joiner safe
copy on the same workstation.

## What Changed

- Added `OnlineDualSafeCopyTopologyArtifactSummary`.
- Added `OnlineMultiplayerReadinessService.TryLoadDualSafeCopyTopologyArtifact`.
- Added strict JSON parsing for `winui-original-binary-online-dual-safe-copy-topology.v1`.
- Added the loaded topology to `OnlineMultiplayerReadinessSummary`, status rows,
  proof-ladder rows, and non-claims.
- Added Windowed & Mods technical-detail copy and load/clear buttons for the
  topology JSON.
- Added AppCore and WinUI tests for accepted topology intake, overclaim
  rejection, private-path rejection, UI copy, and automation ids.
- Tightened the parser after adversarial review so unknown fields, extra
  future-evidence rows, weak `mustProve` rows, case-varied overclaim fields,
  and non-public-safe topology tokens fail closed.

## Accepted Shape

The accepted artifact must remain descriptor-only:

| Field | Required value |
| --- | --- |
| `schema` | `winui-original-binary-online-dual-safe-copy-topology.v1` |
| `scope` | `dual-safe-copy-same-workstation-topology-not-online-play` |
| `safeCopyCount` | `2` |
| roles | `host`, `joiner` |
| `sameWorkstationOnly` | `true` |
| `samePhysicalMachineOnly` | `true` |
| `hostJoinControlsMayBeEnabled` | `false` |
| `baseOnlineMultiplayerReady` | `false` |

The parser rejects private paths, private/sensitive strings, invalid roles,
missing descriptors, unsupported status/scope/date values, unknown JSON fields,
extra future-evidence rows, weak `mustProve` rows, non-public-safe topology
tokens, truthy Host/Join or online overclaim keys, nonzero side-effect counters,
and runtime/proof booleans that try to promote this descriptor into gameplay
evidence. The unloaded WinUI copy is neutral: no topology contract is treated as
loaded until the user selects an accepted JSON artifact.

## Non-Claims

This is not online multiplayer, multi-host LAN proof, public matchmaking,
native BEA netcode, active P3/P4 original-binary gameplay, a BEA launch, CDB
attach, listener, invitation, input send, patch-byte change, Ghidra mutation,
distinct-endpoint command-source proof, source-bound runtime-causality proof,
Host/Join enablement, player-ready netplay, rebuild parity, or
no-noticeable-difference proof.

## Consults

Codex read-only and adversarial consults, Cursor Agent Opus/Gemini ask-mode
consults, Grok Build, and Grok Composer 2.5 Fast reviewed the bounded
topology-intake direction using sanitized non-secret context. The converged
recommendation was to keep the surface passive, avoid raw paths, avoid
`ready`/Host/Join language, and require future VM/second-PC command-source plus
source-bound copied-runtime causality before any promotion.

## Validation

- `dotnet test .\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo --filter "FullyQualifiedName~OnlineMultiplayerReadinessServiceTests"`
- `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiProductLaneTests.PatchBench|FullyQualifiedName~WinUiAccessibilityAuditTests.PrimaryShellAndLongWorkflowControls"`
- `dotnet build .\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj --nologo`
- `npm run test:winui-original-binary-dual-safe-copy-topology`
