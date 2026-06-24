# WinUI Local Gamepad Readiness Artifact Intake

Status: complete parser/UI intake evidence
Date: 2026-06-22
Scope: `winui-local-gamepad-readiness-artifact-intake`

Windowed & Mods can now load a redacted local physical-controller readiness JSON artifact with schema `winui-safe-copy-local-multiplayer-gamepad-readiness.v1` and render the result in Technical online details. This is a hardware-readiness status surface only.

Accepted statuses:

| Status | Meaning |
| --- | --- |
| `blocked_no_present_gamepad` | No present gamepad-like PnP candidate was detected; physical-controller runtime proof remains blocked. |
| `ready_for_physical_gamepad_runtime_attempt` | A present gamepad-like hardware candidate was detected, so a later copied-runtime DirectInput attempt may be scheduled. |

Guardrails:

- Artifacts are capped at 64 KiB.
- Unsupported schema/status values are rejected.
- Candidate count fields must be bounded and match the candidate arrays.
- `claimBoundary` and `nextRuntimeProofRequires` must be present.
- Private paths, private IPs, token-like values, bearer/API/password-like strings, and private repo path markers are rejected.
- Hidden truthy runtime/online overclaims are rejected, including `physicalGamepadRuntimeProof`, DirectInput polling proof, virtual-controller routing proof, visible movement proof, Host/Join enablement, and online proof keys.

Non-claims:

- No BEA launch.
- No CDB attach.
- No DirectInput polling proof.
- No virtual-controller routing proof.
- No visible movement proof.
- No physical gamepad runtime proof.
- No Host/Join enablement.
- No online multiplayer proof.

Validation:

- `dotnet test .\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo --filter "FullyQualifiedName~OnlineMultiplayerReadinessServiceTests"`
- `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiProductLaneTests.PatchBench|FullyQualifiedName~WinUiAccessibilityAuditTests"`
