# WinUI Safe-Copy Control Options Readiness Note

Status: local implementation proof plus bounded runtime input-delta proof; not improved input-feel proof
Date: 2026-06-17

Scope:

- `Windowed & Mods` safe-copy launch controls.
- Copied `defaultoptions.bea` control preset support.
- No installed-game mutation, no original `BEA.exe` mutation, no Ghidra mutation, no netcode, no hooks, and no in-game toggle surface.

Implemented:

| Area | Evidence |
| --- | --- |
| Controller configuration launch preset | WinUI now uses a bounded preset selector for no override and configurations `1..4` instead of a freeform controller-configuration textbox. |
| AppCore launch gate | `GameProfilePreflightService.BuildLaunchPlan` accepts `-configuration 1..4` and rejects out-of-range values such as `0` and `5`. |
| Safe-copy mouse look presets | `PatchBenchSharpenMouseLookOption` plus `PatchBenchMouseSensitivityPresetComboBox` applies one bounded `MouseSensitivityOverride` value (`1.5`, `2.25`, or `3.0`) only to the generated safe copy's `defaultoptions.bea`. |
| Safe-copy invert-Y toggles | `PatchBenchInvertWalkerYOption` and `PatchBenchInvertFlightYOption` write P1/P2 walker/flight invert flags only to the generated safe copy's `defaultoptions.bea`. |
| Safe-copy persisted controller config | `PatchBenchPersistControllerConfigOption` writes the selected `-configuration 1..4` value into the generated safe copy's `defaultoptions.bea` for P1/P2 only when explicitly checked. |
| Control diagnostics presets | WinUI now exposes five fill-only diagnostics presets: baseline config 1, sensitivity-test config 1, swapped config 2, alternate morph/jets config 3, and swapped alternate config 4. These populate existing copied-profile launch/options controls only. |
| Safe-copy containment | `GameProfileControlOptionsService` requires a generated app-owned profile, revalidates the launch manifest through `GameProfilePreflightService.BuildLaunchPlan`, writes only the copied `defaultoptions.bea`, and relies on Configuration Editor's in-place backup path. |
| Safe-copy options manifest | `GameProfileControlOptionsService` now writes `onslaught-control-options-manifest.json` with requested values, observed read-back values, pre/post copied-options hashes, changed byte ranges, backup metadata, and proof status `options_byte_materialized_only`; `GameProfilePreflightService.BuildLaunchPlan` rejects copied-options drift when this manifest exists. |
| Hardlink guard | The copied `defaultoptions.bea` target is rejected if Windows reports more than one hardlink, preventing a shared options file from being patched as if it were private copy state. |
| Manifest write guard | The copied-options manifest target is checked for reparse points and hardlinks before `defaultoptions.bea` mutation, then written through a temp file plus replace/move. This prevents an attacker-controlled manifest path from becoming a shared-file write. |
| Product preset boundary | The safe-copy control service accepts only the bounded `1.5`, `2.25`, and `3.0` mouse-look preset values for this UI path, plus explicit copied invert-Y boolean toggles; arbitrary mouse sensitivity values and deeper deadzone/look-curve changes stay out of the product patch flow until separately designed and proven. |
| Control matrix gate | `tools/winui_control_feel_diagnostics_matrix.py --plan` emits the five-scenario collection plan, and the same checker validates future artifacts with optional visual-capture enforcement via `--require-visual`. Visual coverage accepts either `foregroundMatchesTarget=true` or z-order evidence that no meaningfully overlapping visible top-level window was above the BEA target rectangle. |
| Control input-delta gate | `tools/winui_control_input_delta_artifact_check.py` validates future artifacts with pre-input capture(s), scoped input delivery, post-input capture(s), source safety, managed stop, visual-proof metadata, optional on-disk capture hash verification, and a pre/post frame-hash delta. |
| Runtime boundary | The UI says these copied-options presets do not prove runtime feel until `Play` is tested. |

Validation run:

- `py -3 tools\winui_control_feel_diagnostics_matrix.py --self-test` - passed.
- `py -3 tools\winui_control_feel_diagnostics_matrix.py --plan` - passed, emits baseline config 1, sensitivity-test config 1, swapped config 2, alternate config 3, and swapped alternate config 4 plan rows.
- `npm run test:winui-control-feel-diagnostics-matrix` - passed.
- `dotnet test OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo --filter "FullyQualifiedName~GameProfileControlOptionsServiceTests|FullyQualifiedName~GameProfilePreflightServiceTests.BuildLaunchPlan_AllowsOnlyBoundedArguments"` - passed, 12/12.
- `dotnet test OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiProductLaneTests.PatchBench|FullyQualifiedName~WinUiAccessibilityAuditTests.PrimaryShellAndLongWorkflowControls"` - passed, 3/3.
- `npm run test:winui-safe-copy-runtime` - passed, including copied-profile/control/runtime AppCore tests, 3 WinUI product/accessibility tests, the control-options artifact checker, the control-feel diagnostics matrix self-test, the input-delta artifact checker self-test, and the live runtime smoke helper self-test.
- `dotnet build OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj --nologo` - passed.
- `dotnet test OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~BinaryPatchRegressionTests|FullyQualifiedName~WinUiProductLaneTests.PatchBench|FullyQualifiedName~WinUiAccessibilityAuditTests.PrimaryShellAndLongWorkflowControls"` - passed, 33 passed / 1 host-skipped.
- `py -3 -m py_compile tools\winui_safe_copy_live_runtime_smoke.py tools\winui_safe_copy_live_runtime_smoke_test.py` - passed.
- `py -3 tools\winui_safe_copy_live_runtime_smoke_test.py` - passed, 5/5.
- `py -3 tools\winui_safe_copy_live_runtime_control_options_artifact_check.py --self-test` - passed.
- `py -3 tools\winui_control_input_delta_artifact_check.py --self-test` - passed.
- `npm run test:winui-control-input-delta-artifact` - passed.
- `py -3 tools\start_game_profile_test.py` - passed, 7/7; print-only `-configuration 1..4` command-shape probe aligned with AppCore while real launch remains retired.
- PowerShell parse check for `tools\start_game_profile.ps1` - passed.

Live copied-game control smoke, mouse-sensitivity-only artifact:

- Command: `py -3 tools\winui_safe_copy_live_runtime_smoke.py --arm-live-bea "LAUNCH SAFE COPY BEA" --controller-configuration 2 --sharpen-mouse-look --capture-count 2 --capture-interval-seconds 2 --timeout-seconds 25`
- Ignored proof artifact: `subagents/winui-safe-copy-live-runtime/20260617-134804/live-safe-copy-runtime-smoke.json`.
- Validator: `py -3 tools\winui_safe_copy_live_runtime_control_options_artifact_check.py subagents\winui-safe-copy-live-runtime\20260617-134804\live-safe-copy-runtime-smoke.json` - passed.
- Captures: `subagents/winui-safe-copy-live-runtime/20260617-134804/capture/safe-copy-frame.png` and `safe-copy-frame-02.png` were captured at verified target-window bounds. Capture metadata recorded `foregroundMatchesTarget=false`, so these frames are not claimed as unoccluded visual proof.
- Source safety: installed `BEA.exe`, `BEA.exe.original.backup`, source `defaultoptions.bea`, and source `savegames` hashes stayed unchanged; no BEA process remained after stop.
- Control proof: launched arguments were `-skipfmv -configuration 2`; copied `defaultoptions.bea` mouse sensitivity read back as `2.25`; copied options hash changed after prepare and before launch; changed byte range intersected the mouse-sensitivity field (`0x26c4+2:4041->1040`); one copied-options backup was recorded.
- Persisted-controller-config note: this artifact predates `PatchBenchPersistControllerConfigOption`, so it proves launch-argument controller configuration plus copied mouse-sensitivity materialization only. The helper/checker now supports persisted controller config artifacts, but no persisted-controller live artifact is claimed here.
- Boundary: this proves materialization and guarded launch/stop only. It still does not prove improved runtime control feel, analog deadzone behavior, look-curve behavior, camera/movement response, gameplay parity, or no-noticeable-difference parity.

Live copied-game control smoke, persisted-controller artifact:

- Command: `py -3 tools\winui_safe_copy_live_runtime_smoke.py --arm-live-bea "LAUNCH SAFE COPY BEA" --controller-configuration 2 --persist-controller-config-in-options --sharpen-mouse-look --capture-count 1 --timeout-seconds 25`
- Ignored proof artifact: `subagents/winui-safe-copy-live-runtime/20260617-151307/live-safe-copy-runtime-smoke.json`.
- Validator: `py -3 tools\winui_safe_copy_live_runtime_control_options_artifact_check.py subagents\winui-safe-copy-live-runtime\20260617-151307\live-safe-copy-runtime-smoke.json` - passed.
- Control proof: launched arguments were `-skipfmv -configuration 2`; copied `defaultoptions.bea` mouse sensitivity read back as `2.25`; requested persisted controller config `2`; observed copied `defaultoptions.bea` controller config P1/P2 read back as `2/2`; proof lever was `copied-defaultoptions-mouse-sensitivity-and-controller-config`; proof status was `options_byte_materialized_only`; changed-range count was `3`; one copied-options backup was recorded; `onslaught-control-options-manifest.json` was written.
- Source safety: installed `BEA.exe`, `BEA.exe.original.backup`, source `defaultoptions.bea`, and source `savegames` hashes stayed unchanged; no BEA process existed before launch and no BEA process remained after stop.
- Capture boundary: one bounded frame was captured at the target-window bounds, but `foregroundMatchesTarget=false`, so it is not visual proof, gameplay proof, or improved runtime control-feel proof.

Five-scenario control diagnostics matrix:

- Commands: five serial `py -3 tools\winui_safe_copy_live_runtime_smoke.py --arm-live-bea "LAUNCH SAFE COPY BEA"` runs under ignored local evidence root `subagents/winui-safe-copy-live-runtime/control-feel-matrix-20260617-occlusion7/`.
- Scenarios: `baseline_config1`, `sharpened_config1` (human label: sensitivity-test config 1), `swapped_config2`, `alternate_config3`, and `swapped_alternate_config4`.
- Matrix validator with `--require-visual`: `py -3 tools\winui_control_feel_diagnostics_matrix.py --artifact baseline_config1=... --artifact sharpened_config1=... --artifact swapped_config2=... --artifact alternate_config3=... --artifact swapped_alternate_config4=... --require-visual` - passed, `matrixComplete=true`, `scenarioCount=5`, `visualCaptureCount=1` for every scenario.
- Source safety: all five artifacts reported source `defaultoptions.bea`/`savegames` unchanged, no pre-existing BEA process, managed stop success, and no BEA process after stop.
- Control proof: baseline config 1 used launch-argument proof only; the other four scenarios recorded copied `defaultoptions.bea` control-options proof. Sensitivity-test config 1 read back mouse sensitivity `2.25`; configs 2, 3, and 4 read back persisted P1/P2 controller configs matching their launch arguments.
- Visual proof: all five captures were `visualProof=true` via z-order occlusion-free metadata. The desktop foreground did not belong to BEA, but z-order inspection found the target window, found zero meaningful overlapping visible windows above it, and recorded two 1x1 tiny overlaps below the `minimumOccluderOverlapArea=64` threshold.
- Boundary: the matrix now proves copied launch/options materialization, source safety, managed stop, and one bounded target-window visual capture per scenario. It still does not prove improved runtime control feel, analog deadzone behavior, look curves, camera response, gameplay parity, or rebuild parity.
- Earlier foreground-only attempts under `control-feel-matrix-20260617/`, `control-feel-matrix-20260617-foreground/`, and intermediate `control-feel-matrix-20260617-occlusion*` roots are retained as ignored debugging/history evidence and are superseded by `control-feel-matrix-20260617-occlusion7/`.

Live copied-game control input-delta artifact:

- Command: `py -3 tools\winui_safe_copy_live_runtime_smoke.py --artifact-root subagents\winui-safe-copy-live-runtime\control-input-delta-20260617-focus1\baseline_config1_left_right --capture-count 2 --pre-input-capture-count 1 --focus-before-pre-input-capture --capture-interval-seconds 1 --post-window-delay-seconds 1 --timeout-seconds 25 --arm-live-bea "LAUNCH SAFE COPY BEA" --controller-configuration 1 --input-sequence "tap:LEFT,wait:100,tap:RIGHT"`.
- Ignored proof artifact: `subagents/winui-safe-copy-live-runtime/control-input-delta-20260617-focus1/baseline_config1_left_right/live-safe-copy-runtime-smoke.json`.
- Validator: `py -3 tools\winui_control_input_delta_artifact_check.py subagents\winui-safe-copy-live-runtime\control-input-delta-20260617-focus1\baseline_config1_left_right\live-safe-copy-runtime-smoke.json --expected-controller-configuration 1 --min-pre-captures 1 --min-post-captures 2 --require-visual --require-files` - passed.
- Source safety: installed `BEA.exe`, `BEA.exe.original.backup`, source `defaultoptions.bea`, and source `savegames` hashes stayed unchanged; no BEA process existed before launch and no BEA process remained after stop.
- Input/capture proof: the no-key pre-input focus step reported `status=sent` and `focused=true`; the measured scoped input sent one sequence with three actions and four key events; one pre-input capture and two post-input captures were `visualProof=true`; on-disk capture files matched reported hashes; pre/post frame hashes differed.
- Visual sample: the pre-input frame showed the real BEA title screen; the first post-input frame showed the same title/menu path with `Click to start`. This proves timed pre/post frame-hash delta around scoped input delivery, not that LEFT/RIGHT caused gameplay state change.
- Boundary: this is stronger than the matrix because it proves scoped input delivery plus frame-hash delta, but it still does not prove improved runtime control feel, analog deadzone behavior, look-curve behavior, camera/movement response, gameplay parity, or no-noticeable-difference parity.

Consult boundary:

- Codex implementation consult recommended the bounded `-configuration 1..4` launch preset as the safest first tryable control-feel slice.
- Codex RE/source consult identified copied `defaultoptions.bea` mouse-look sensitivity presets, invert-Y flags, and config options as the lowest-risk options-file levers, while keeping analog deadzone/look-curve/movement constants as separate Ghidra/runtime proof work.
- Codex adversarial review blocked online multiplayer, DLL injection/hooks, in-game trainers, and a monolithic default mega patch for this slice.
- Codex adversarial follow-up required the hardlink guard and AppCore-side fixed-preset enforcement before treating this slice as acceptable.

Not claimed:

- No proof that the control presets improve feel in live gameplay.
- No analog deadzone, look-curve, camera, movement, physics, or netcode patch.
- No causal gameplay input-response proof, gameplay parity, rebuild parity, or no-noticeable-difference claim.
- No installed game or source specimen mutation.
