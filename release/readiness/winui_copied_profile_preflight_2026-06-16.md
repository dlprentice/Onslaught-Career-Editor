# WinUI Safe Copied Game Folder Preflight Readiness Note

Status: validated local preflight slice
Date: 2026-06-16

Scope: add a safe bridge from copied-executable patching to safe copied game folder runtime readiness without starting Battle Engine Aquila.

This slice adds an AppCore safe copied game folder preflight service and a WinUI Windowed & Mods card. The service copies required game entries into an app-owned profile root, copies optional `cardid.txt` / `steam_appid.txt` when present, applies selected visible Patch Bench rows plus the required windowed compatibility rows to the copied `BEA.exe`, verifies selected patch bytes by reading the copied executable back from disk, writes a redacted generated profile manifest, and returns an allowlisted launch-plan preview. WinUI displays the preflight result and launch-plan preview only; it does not start the game.

Tracked outcomes:

| Area | Result |
| --- | --- |
| AppCore service | `GameProfilePreflightService` prepares `winui-copied-game-profile.v1` profiles under an app-owned output root. |
| Patch rows | Selected visible rows are applied to the safe copy; `resolution_gate` and `force_windowed` are always included for launch compatibility. The hidden version-overlay cave payload is applied only when the visible `version_overlay_use_patched_format_pointer` marker row is selected. |
| Specimen identity | WinUI calls this product path and the normal Patch Bench apply path with known clean Steam retail specimen enforcement; byte-layout-only patching remains a test/lab option. |
| Read-back | The copied executable is re-read from disk after patch apply and selected rows must verify as patched. |
| Copy safety | Required entry types are checked, executable overrides must stay under the selected game root, source entries and output-root ancestors reject reparse points, app-owned output roots reject Program Files/protected roots and `steamapps/common/Battle Engine Aquila` install shapes, patch targets reject hardlinks, cleanup stays under the app-owned output root, and manifests avoid absolute local source/target paths. |
| Private saves | `savegames` is not copied by default; WinUI now exposes an explicit `Copy savegames into the safe copy` checkbox for users who want copied saves in the safe game folder. Source savegames remain read-only. |
| Launch plan | Launch preview requires a generated safe-copy manifest, successful patch metadata, current patch-byte read-back, and allowlisted arguments; no process starts in this slice. |
| WinUI surface | Windowed & Mods exposes `Safe copied game folder` with visible `Create safe game copy` action (`PatchBenchPrepareCopiedProfileButton` / automation name `Prepare safe copied game folder`), safe-copy summary, optional savegame copy checkbox, and launch-plan preview controls. |

Validation run:

- `dotnet test OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo --filter FullyQualifiedName~GameProfilePreflightServiceTests` - passed, 24/24 after adding protected-root and Steam-shaped output-root rejection coverage.
- `dotnet test OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiProductLaneTests.PatchBench|FullyQualifiedName~WinUiAccessibilityAuditTests.PrimaryShellAndLongWorkflowControls"` - passed, 3/3.
- `npm run test:winui-copied-profile-preflight` - passed.

Not claimed:

- No BEA launch.
- No desktop/window capture.
- No managed stop/cleanup proof.
- No runtime gameplay proof.
- No music/color/resource mod proof.
- No installed-game or original executable mutation.
- No Ghidra mutation.
- No new Ghidra backup; latest verified Ghidra review backup remains `G:\GhidraBackups\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified`.
- No Godot or clean-room rebuild demo.
- No no-noticeable-difference parity claim.
