# WinUI Enhanced Profile Preview Readiness Note

Status: validated local profile/accounting slice with accepted follow-up visual proof
Date: 2026-06-17; follow-up visual proof 2026-06-18

Scope: make `Enhanced Profile Preview` selectable only as a proof-bounded safe-copy preset over existing reversible rows, not as a monolithic game overhaul.

## Selected Row Set

The AppCore profile id is `enhanced-edition-preview`. It selects these visible patch rows:

| Row | Boundary |
| --- | --- |
| `resolution_gate` | Windowed compatibility baseline; not widescreen gameplay parity. |
| `force_windowed` | Windowed startup preference; not universal windowing proof. |
| `extra_graphics_default_on` | Defaults one extra-graphics tweak on; visible rendering effect remains separate proof. |
| `ignore_cardid_tweak_overrides` | Bypasses old `cardid.txt` tweak override load; visible rendering effect remains separate proof. |
| `version_overlay_use_patched_format_pointer` | Title/menu `PATCHED` marker row; AppCore adds the hidden cave-string dependency. |
| `frontend_clear_screen_dark_red` | Red frontend clear-screen immediate; current proof is title-screen margin capture only. |
| `goodies_gallery_display_unlock` | Bounded Goodies-wall display-state override; does not edit saves or permanently award Goodies. |

Excluded from the preview:

- `skip_auto_toggle`
- `free_camera_aurore_gate_bypass`
- `frontend_clear_screen_dark_green`
- `frontend_clear_screen_black`
- any online/network patch
- any in-game toggle/menu hook
- any deadzone/look-curve/movement byte patch

## Accounting

- `BinaryPatchPlanBuilder` owns the exact profile row set.
- `patches/catalog/patches.v2.json` marks `enhanced-edition-preview` eligibility only on those visible rows.
- `GameProfilePreflightService` rejects a declared profile id if the supplied patch keys do not exactly match the preset.
- The generated `onslaught-profile-manifest.json` records profile id, display name, proof status, and applied patch keys.
- WinUI's button also turns on copied-options controller-config persistence and sharpened mouse look. Those are recorded by `onslaught-control-options-manifest.json` after safe-copy preparation and remain `defaultoptions.bea` materialization proof only.

## Runtime Artifacts

`subagents/winui-safe-copy-live-runtime/20260617-160606/live-safe-copy-runtime-smoke.json` exercised the Enhanced Preview profile through the guarded live copied-profile helper:

- AppCore profile id: `enhanced-edition-preview`.
- AppCore profile defaults: controller configuration `1`, copied controller-config persistence on, and copied mouse-look sharpening on.
- Requested visible rows matched the exact Enhanced Preview set above.
- Expanded applied rows included hidden dependency `version_overlay_patched_format_cave_string`.
- Copied-options controls requested persisted controller config `1` and sharpened mouse look `2.25`; config `1` read back as `1/1` and remained a byte no-op because it already matched the copied default, while mouse sensitivity changed bytes at `0x26c4`.
- Installed `BEA.exe`, clean `BEA.exe.original.backup`, source `defaultoptions.bea`, and source `savegames` remained unchanged.
- Managed stop succeeded and no `BEA.exe` remained after stop.
- Visual proof remains absent for this earlier run: the `--require-visual` checker failed with `foregroundCaptureCount=0` because the desktop was lock-screen occluded.

A follow-up 2026-06-18 run exercised the same Enhanced Preview profile with foreground visual capture and accepted the combined profile only for bounded safe-copy launch/capture/source-safety, requested/expanded patch-key identity, red frontend-margin capture, copied controller config `1`, copied mouse sensitivity `2.25`, managed stop, and unchanged installed/source material.

Accepted checker summaries for the follow-up run:

| Checker | Bounded outcome |
| --- | --- |
| `tools\winui_enhanced_preview_runtime_artifact_check.py --require-visual` | `visualProof=true`, `foregroundCaptureCount=5`, profile id `enhanced-edition-preview`, requested patch-key set matched the profile, expanded patch-key set included hidden `version_overlay_patched_format_cave_string`, installed/override/source options unchanged, managed stop clean. |
| `tools\winui_frontend_color_runtime_artifact_check.py --expected-patch-key frontend_clear_screen_dark_red --require-after-input-color` | `captureCount=5`, `visualCaptureCount=5`, `matchingColorCaptureCount=2`, `afterInputColorCaptureCount=1`; proves one bounded red frontend-margin capture path for the combined profile only. |
| `tools\winui_safe_copy_live_runtime_control_options_artifact_check.py` | `persistedControllerConfig=1`, `mouseSensitivity=2.25`, copied-options backup/change accounting valid, source options unchanged, managed stop clean. |

## Validation

- `dotnet test OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo --filter "FullyQualifiedName~GameProfilePreflightServiceTests|FullyQualifiedName~GameProfileControlOptionsServiceTests"` - passed, 28/28.
- `dotnet test OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~BinaryPatchRegressionTests|FullyQualifiedName~WinUiProductLaneTests.PatchBench|FullyQualifiedName~WinUiAccessibilityAuditTests.PrimaryShellAndLongWorkflowControls"` - passed, 33 passed / 1 host-skipped after serial rerun.
- `py -3 tools\winui_enhanced_preview_runtime_artifact_check.py --self-test` - passed.
- `py -3 tools\winui_enhanced_preview_runtime_artifact_check.py subagents\winui-safe-copy-live-runtime\20260617-160606\live-safe-copy-runtime-smoke.json` - passed with `visualProof=false`.
- `py -3 tools\winui_enhanced_preview_runtime_artifact_check.py subagents\winui-safe-copy-live-runtime\20260617-160606\live-safe-copy-runtime-smoke.json --require-visual` - failed as expected for the current locked/occluded desktop; this failure preserves the visual-proof boundary.
- `py -3 tools\winui_enhanced_preview_runtime_artifact_check.py <2026-06-18 enhanced-profile artifact> --require-visual` - passed with `visualProof=true`.
- `py -3 tools\winui_frontend_color_runtime_artifact_check.py <2026-06-18 enhanced-profile artifact> --expected-patch-key frontend_clear_screen_dark_red --min-capture-count 5 --min-color-captures 1 --min-visual-captures 5 --require-files --require-input --require-after-input-color` - passed.
- `py -3 tools\winui_safe_copy_live_runtime_control_options_artifact_check.py <2026-06-18 enhanced-profile artifact>` - passed.

## Not Claimed

- Not a full Enhanced Edition.
- Not online multiplayer.
- Not a runtime control-feel improvement proof.
- Not broader frontend/theme/gameplay coverage.
- Not gameplay parity, rebuild parity, or no-noticeable-difference parity.
- Not an installed-game mutation path.
