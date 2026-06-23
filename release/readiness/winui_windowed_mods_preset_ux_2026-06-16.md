# WinUI Windowed & Mods Preset UX Readiness Note

Status: validated local WinUI UX slice
Date: 2026-06-16

Scope: make the guarded executable patch lane clearer for user-tryable windowed and graphics presets.

This slice renamed the visible product lane from `Patch Bench` to `Windowed & Mods` while preserving Patch Bench automation IDs. Follow-up safe-copy work made the normal path a launchable app-owned copied game folder: presets select rows that are applied when the user prepares that safe game copy. The older BEA.exe-only copied executable workflow remains available as an advanced path and does not create a launchable copied game folder.

Tracked outcomes:

| Area | Result |
| --- | --- |
| Navigation | WinUI nav and Home route now show `Windowed & Mods`; access key `P` is preserved for continuity. |
| Presets | `Windowed compatibility` selects `resolution_gate` and `force_windowed`; `Extra graphics gates` selects `extra_graphics_default_on` and `ignore_cardid_tweak_overrides`; `Windowed + graphics defaults` selects those byte-checked stable-track rows together, and clear selection is available. |
| Opt-in color patch | `frontend_clear_screen_dark_red`, `frontend_clear_screen_dark_green`, and `frontend_clear_screen_black` are visible as mutually exclusive copied-executable frontend color patches. This June 16 UX slice made the first color row visible; later June 17 safe-copy evidence adds byte proof plus one local title-screen capture for each of red, green, and black clear-screen margins, while broader menu coverage remains pending. |
| Binding | Patch item selection now raises property-change notifications so preset buttons update checkbox state. |
| Safety boundary | Safe copied game folder preparation patches only copied files; advanced apply/restore still uses the AppCore guarded copied-target contract from `c6ee2d063`. |
| Proof drawer | Patch rows now expose public-safe proof details in the existing technical expander: expected visible result, verified proof, still-unproven behavior, and readiness-note reference. Accessibility help text carries the same proof boundary. |
| Safe-copy profile foundation | WinUI now exposes profile-style starting points without changing patch mechanics: `Compatibility Copy`, `Windowed + Graphics Defaults`, `Custom`, and selectable proof-bounded `Enhanced Profile Preview`. The preview selects exact existing reversible rows only: `resolution_gate`, `force_windowed`, `extra_graphics_default_on`, `ignore_cardid_tweak_overrides`, `version_overlay_use_patched_format_pointer`, `frontend_clear_screen_dark_red`, and `goodies_gallery_display_unlock`; it excludes `skip_auto_toggle` and `free_camera_aurore_gate_bypass`. This is not a monolithic patch, in-game toggle surface, online mode, full overhaul, or control-feel proof. |
| Profile manifest accounting | AppCore validates that a declared profile preset id matches the exact selected row set, rejects mismatches, and records the matched profile id/name/proof status in the generated safe-copy manifest. WinUI's Enhanced Profile Preview also selects copied-options controller-config persistence and sharpened mouse look; those remain separate copied-`defaultoptions.bea` materialization proof. |
| Catalog policy metadata | This historical slice covered the then-current 12 catalog rows. The current catalog has 29 rows (20 visible options plus hidden/companion support rows); current catalog totals are tracked in `CURRENT_CAPABILITIES.md`, `patches/catalog/patches.v2.json`, and the release-accounting probes. AppCore parses the metadata, auto-adds the version-overlay hidden companion from catalog dependencies, hides `hidden_companion` rows, and validates color exclusivity/windowed-pair requirements from shared policy. The lower-level AppCore engine and standalone Python helper also reject invalid dependency/conflict/hidden-companion/exclusive/windowed-pair selections before mutation. |
| Stale safe-copy guard | A prepared safe game copy is treated as stale when source/patch/savegame choices no longer match the prepared-copy content signature; Play and music staging remain disabled until a new safe copy is created, and stale summary text is shown. |
| Music restore safety | Copied-game music restore now uses temp replacement, read-back SHA-256 verification, and manifest hardlink checks before deleting the replacement manifest. |
| Catalog helper safety | The standalone Python catalog helper now refuses mutating `--apply` with arbitrary catalog bytes; mutating proof setup requires the supported catalog SHA-256. |

Validation run:

- `dotnet test OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiProductLaneTests|FullyQualifiedName~WinUiAccessibilityAuditTests|FullyQualifiedName~BinaryPatchRegressionTests"` - passed, 36/36.
- `dotnet build OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj --nologo` - passed, 0 warnings, 0 errors.
- `npm run test:winui` - passed, 56 passed, 2 skipped.
- `dotnet test OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiVisualSmokeTests.MainWindow_CapturesScrolledWorkflowSections"` - passed, 1/1.
- Follow-up June 17 focused gates after proof drawer and hardening:
  - `dotnet build OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj --nologo` - passed.
  - `dotnet test OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiProductLaneTests.PatchBench|FullyQualifiedName~WinUiAccessibilityAuditTests.PrimaryShellAndLongWorkflowControls"` - passed, 3/3.
  - `dotnet test OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo --filter "FullyQualifiedName~GameProfileMusicReplacementServiceTests"` - passed, 22/22.
  - `npm run test:winui-safe-copy-music-replacement` - passed.
  - `npm run test:winui-patch-engine-safety` - passed.
  - `dotnet build OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj --nologo` - passed after profile-preset foundation.
  - `dotnet test OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiProductLaneTests.PatchBench|FullyQualifiedName~WinUiAccessibilityAuditTests.PrimaryShellAndLongWorkflowControls"` - passed, 3/3 after profile-preset foundation.
  - `dotnet test OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~BinaryPatchRegressionTests|FullyQualifiedName~WinUiProductLaneTests.PatchBench|FullyQualifiedName~WinUiAccessibilityAuditTests.PrimaryShellAndLongWorkflowControls"` - passed, 33 passed / 1 host-skipped after AppCore profile catalog, catalog policy metadata, and direct-engine policy hardening.
  - `dotnet build OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj --nologo` - passed after AppCore profile catalog, catalog policy metadata, and direct-engine policy hardening.
  - `py -3 -m py_compile tools\apply_bea_catalog_patch.py` - passed after helper policy hardening.
  - `py -3 tools\apply_bea_catalog_patch.py --self-test` - passed after catalog policy metadata, supported-hash refresh, and helper policy hardening.
  - `dotnet test OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo --filter "FullyQualifiedName~GameProfilePreflightServiceTests|FullyQualifiedName~GameProfileControlOptionsServiceTests"` - passed, 28/28 after selectable Enhanced Profile Preview manifest accounting.
  - `dotnet test OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~BinaryPatchRegressionTests|FullyQualifiedName~WinUiProductLaneTests.PatchBench|FullyQualifiedName~WinUiAccessibilityAuditTests.PrimaryShellAndLongWorkflowControls"` - passed, 33 passed / 1 host-skipped after selectable Enhanced Profile Preview profile validation.

Visual proof caveat:

The explicit UIA visual smoke passed, but the generated screenshots were occluded by an existing browser window in this desktop session. Treat this as UIA/build proof plus an unreliable screenshot artifact, not clean visual review.

Not claimed:

- No BEA launch/capture proof in this June 16 preset UX note; later June 17 notes cover bounded safe-copy launch/capture/stop smokes.
- This June 16 preset UX note itself does not provide runtime audio proof for music replacement or runtime visual proof for the frontend color family; later June 17 safe-copy evidence covers one bounded title-screen capture per color preset.
- No installed-game mutation.
- No Godot or clean-room rebuild demo.
- No netcode work.
- Enhanced Profile Preview is not a full overhaul, online multiplayer mode, in-game toggle surface, control-feel proof, or gameplay parity proof.
