# WinUI Safe Copied Game Runtime Controls Readiness Note

Status: validated local contract and UI wiring
Date: 2026-06-16

Scope: add guarded WinUI/AppCore launch and stop controls for generated safe copied game folders.

This slice extends the safe copied game folder preflight lane with a managed launch/stop contract. AppCore now launches only generated safe copies under the app-owned `GameProfiles` root after revalidating the generated manifest, copied executable full-file size/hash, selected patch bytes, reparse-point boundaries, and allowlisted arguments. Stop targets only the managed process record returned by that launch path. WinUI Windowed & Mods exposes `Launch safe game copy`, `Stop safe game copy`, and a launch-status line while preserving the boundary that a launch attempt is not gameplay, capture, or rendering parity proof.

Tracked outcomes:

| Area | Result |
| --- | --- |
| AppCore runtime service | `GameProfileRuntimeService` validates generated safe-copy roots, starts through `ProcessStartInfo.ArgumentList` with `UseShellExecute=false`, and records process id, executable, working directory, arguments, start time, and manifest path. |
| Stop boundary | Stop rejects unmanaged/out-of-root records and delegates only for the managed safe-copy record. The default runner checks process identity before close/kill. |
| Manifest hardening | `GameProfilePreflightService` generated manifests now include copied executable size and SHA-256, and launch-plan validation rejects later full-file tampering. |
| WinUI surface | Windowed & Mods has stable automation IDs for `PatchBenchLaunchCopiedProfileButton`, `PatchBenchStopCopiedProfileButton`, and `PatchBenchCopiedProfileLaunchStatus` while showing safe-copy wording to users. |
| Test gate | `npm run test:winui-copied-profile-runtime` covers preflight tests, runtime contract tests, and Patch Bench UI/static accessibility checks. |

Validation run:

- `dotnet test OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo --filter "FullyQualifiedName~GameProfileRuntimeServiceTests"` - passed, 7/7.
- `dotnet test OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiProductLaneTests.PatchBench|FullyQualifiedName~WinUiAccessibilityAuditTests.PrimaryShellAndLongWorkflowControls"` - passed, 3/3.
- `npm run test:winui-copied-profile-runtime` - passed: AppCore safe-copy preflight/runtime tests 17/17 and WinUI/static checks 3/3.

Not claimed:

- No live BEA process was launched by this validation run.
- No desktop/window capture.
- No runtime gameplay proof.
- No windowed rendering parity proof.
- No music/color/resource mod proof.
- No installed-game or original executable mutation.
- No Ghidra mutation.
- No new Ghidra backup; latest verified Ghidra review backup remains `G:\GhidraBackups\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified`.
- No Godot or clean-room rebuild demo.
- No no-noticeable-difference parity claim.
