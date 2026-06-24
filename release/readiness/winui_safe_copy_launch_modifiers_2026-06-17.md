# WinUI Safe-Copy Launch Modifiers Readiness Note

Status: validated local contract and UI wiring
Date: 2026-06-17

Scope: expand Windowed & Mods safe copied game folder launch options without adding new executable mutation.

Tracked outcomes:

| Area | Result |
| --- | --- |
| UI surface | Windowed & Mods exposes copied-process launch controls for skip intro movies, mute music, mute all sound, high detail, static-shadow disable, controller-vibration disable, debug trace, mission id, controller configuration, texture RAM limit, bounded Local Multiplayer Probe, an admin level preset selector, four general fill-only presets, and five Control diagnostics presets. |
| AppCore allowlist | `GameProfilePreflightService` accepts only known launch flags and bounded numeric values. `-configuration` is limited to 1-4; `-textureramlimit` is limited to 8-512 MB worth of bytes. AppCore accepts parser-visible `-showdebugtrace` and diagnostic `-forcewindowed`; WinUI exposes only `-showdebugtrace` from that diagnostic group and relies on the `force_windowed` patch instead of exposing `-forcewindowed` as normal product UX. |
| Source/static basis | `reverse-engineering/quick-reference/cli-parameters.md` and the retail CLIParams docs support `-nostaticshadows`, `-textureramlimit N`, `-norumble`, `-configuration N`, and parser-visible `-showdebugtrace`. Source-only/dev/file-writing flags remain blocked until separately proven. |
| Safety boundary | These are process launch arguments for generated safe copied game folders only. They do not edit the installed game, the original executable, or the copied executable bytes. |
| Test gate | AppCore preflight tests prove allowlist normalization and rejection of unsupported/out-of-range values; WinUI source tests prove the controls and generated arguments remain wired. |
| Live smoke helper | `tools/winui_safe_copy_live_runtime_smoke.py` accepts bounded `--level-id` so local ignored runtime smokes can exercise the same AppCore launch-plan path as the WinUI mission-id and Local Multiplayer Probe UI. |
| Artifact checker | `tools/winui_safe_copy_local_multiplayer_artifact_check.py` validates level-850 launch/source-safety/managed-stop artifacts and only reports visual proof when at least one capture has `foregroundMatchesTarget=true`. |

Launch preset note:

- `Quiet capture` fills `-skipfmv -nomusic` for cleaner launch/capture runs and deliberately does not use `-nosound`, so non-music audio remains available for later audio proof.
- The five `Control diagnostics` presets fill baseline config 1, sharpened config 1, swapped config 2, alternate morph/jets config 3, and swapped alternate config 4 through existing safe-copy launch/options controls. They are measured by `tools/winui_control_feel_diagnostics_matrix.py`; they are not deadzone/look-curve/movement byte patching and do not prove runtime feel.
- `High detail test` fills `-skipfmv -hidetail -textureramlimit 268435456` through the same UI MB field and AppCore byte-limit allowlist. It requests the retail/source-backed high-detail path but does not prove visible rendering quality.
- `Clear launch options` clears only the launch/options controls. It does not change selected executable patch rows or delete any prepared safe copy.
- `Admin level preset` fills the existing validated `-level` field with static/source-backed world IDs `100`, `800`, `850`, or `851`. It does not unlock saves, add a level browser, prove gameplay entry, or add online multiplayer.
- All presets only fill existing controls; prepare/play still go through `BuildSelectedLaunchArguments`, `GameProfilePreflightService.BuildLaunchPlan`, manifest/hash checks, and the guarded safe-copy launch flow.

Developer diagnostics note:

- WinUI exposes only `Show debug trace (-showdebugtrace)` from the development/debug flag group.
- Consulted source/retail evidence keeps `-devmode`, `-killhud`, `-modelviewer`, `-cutsceneeditor`, `-artists`, `-buildresources`, `-record`, `-play`, `-stresstest`, `-mem`, and `-largeram` blocked from the product launch UI/AppCore allowlist for now.
- `-showdebugtrace` is parser-visible but not runtime-output proof. The UI says it may not show visible output and does not enable dev mode, build resources, record demos, add online features, or prove gameplay behavior.

Validation after developer-diagnostics and admin-level preset updates:

- `dotnet test .\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo --filter "FullyQualifiedName~GameProfilePreflightServiceTests.BuildLaunchPlan_AllowsOnlyBoundedArguments|FullyQualifiedName~GameProfileRuntimeServiceTests.LaunchCopiedProfile_StartsOnlyGeneratedProfileUnderAppOwnedRoot|FullyQualifiedName~GameProfileRuntimeServiceTests.LaunchCopiedProfile_RejectsUnsupportedArgumentsBeforeStarting"`: PASS, 3/3.
- `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiProductLaneTests.PatchBench|FullyQualifiedName~WinUiAccessibilityAuditTests.PrimaryShellAndLongWorkflowControls"`: PASS, 3/3, including the admin-level preset automation ID and source-level wiring.
- `dotnet build .\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj --nologo`: PASS, 0 warnings, 0 errors.
- `npm run test:winui-safe-copy-runtime`: PASS, 50 AppCore tests, 3 WinUI tests, control-options artifact checker, control-feel matrix checker, and live-runtime helper self-tests.

Consult / adversarial guardrails:

- No launch preset uses raw `Process.Start`, preview-text parsing, shell concatenation, a source-root `AllowedRoot`, or `AllowByteLayoutOnlyTarget=true`.
- Launch presets remain separate from `ProfilePresetId`; patch profile ids still mean exact proof-bounded executable row sets only.
- No launch preset exposes `-forcewindowed`; normal product UX relies on the copied executable `force_windowed` patch row plus `resolution_gate`.
- No freeform/admin command text is exposed. New launch arguments still require AppCore normalization, bounds, tests, and path validation for any future path-taking flag.
- Source-only, resource-building, demo-recording, stress-test, and memory-sizing flags are still blocked until they have dedicated static/runtime safety notes and app-owned output handling.
- Future mega/enhanced profiles must remain granular profile manifests over separately proven modules, with explicit conflicts, dependencies, proof levels, restore semantics, and non-claims.

Local multiplayer note:

- WinUI's `Local multiplayer probe` button sets `-skipfmv -level 850` for the generated safe copied game folder only.
- Static/source evidence ties `CGame__IsMultiplayer` to the `850..899` level range; level `850` is therefore a local split-screen/multiplayer study pivot, not an online multiplayer implementation.
- The preset does not patch files, does not add netcode, and does not claim online multiplayer.
- Local ignored live smoke `subagents/winui-safe-copy-live-runtime/20260617-141558/live-safe-copy-runtime-smoke.json` launched a generated safe copy with `-skipfmv -level 850`, verified source executable/options/save hashes unchanged, captured six target-bounds frames, stopped the managed process, and left no BEA process running.
- `tools/winui_safe_copy_local_multiplayer_artifact_check.py` classifies that artifact as `safe-copy launch/source-safety/managed-stop only` with `visualProof=false`, `foregroundCaptureCount=0`, and foreground process id `35596`.
- Those frames were occluded by `LockApp.exe` (`foregroundMatchesTarget=false`), so this proves safe-copy launch-plan materialization/source safety/managed stop only. It does not prove split-screen visuals, gameplay state, controller assignment, or online multiplayer. Future unoccluded local multiplayer visual proof should pass the same checker with `--require-visual`.
- Follow-up foreground-assisted run `subagents/winui-safe-copy-live-runtime/20260617-141756/live-safe-copy-runtime-smoke.json` correctly failed the input helper with `focus-required`, again left source hashes unchanged, and left no BEA process running.

Not claimed:

- No unoccluded local multiplayer, split-screen, controller-assignment, or online multiplayer runtime proof.
- No gameplay, menu, rendering, controller, rumble, texture-memory, or shadow behavior proof.
- No installed-game or original executable mutation.
- No new executable byte patch.
- No Ghidra mutation.
- No new Ghidra backup; latest verified Ghidra review backup remains `G:\GhidraBackups\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified`.
