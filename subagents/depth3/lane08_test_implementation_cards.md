# Lane 08 - Test Implementation Cards

Derived from `subagents/depth2/lane08_test_gap_priorities.md` and coverage evidence in `subagents/depth1/lane03_test_coverage_inventory.md`.

## P0 Cards

### Card P0-01 - Python analyze/dump-mystery contract
Priority: P0
Path: `tests_pyqt/test_cli_readonly_modes_unittest.py`
Test name: `test_analyze_valid_save_and_dump_mystery_emit_required_sections`
Assertions:
1. `python patcher.py <save> --analyze` exits `0`.
2. stdout contains section anchors: `SAVE FILE ANALYSIS`, `FILE VALIDATION`, `MISSION NODES`, `LINKS`, `GOODIES`, `KILL COUNTS`, `TECH SLOTS`.
3. `python patcher.py <save> --analyze --dump-mystery` exits `0` and stdout additionally contains `UNMAPPED / RESERVED REGIONS`.
4. stderr does not contain `Error:` for both runs.
Risk addressed: silent regressions in primary read-only diagnostics (`--analyze`/`--dump-mystery`) that break triage flow.

### Card P0-02 - Python compare failure contract
Priority: P0
Path: `tests_pyqt/test_cli_readonly_modes_unittest.py`
Test name: `test_compare_missing_file_is_fatal_with_clear_error`
Assertions:
1. `python patcher.py <save> --compare <missing>` exits non-zero.
2. stderr contains `Error: Comparison file not found`.
3. stdout does not contain `FILE COMPARISON`.
Risk addressed: compare-mode failure handling drift causing ambiguous operator feedback.

### Card P0-03 - C# analyze/dump-mystery contract
Priority: P0
Path: `OnslaughtCareerEditor.UiTests/CliReadOnlyParityTests.cs`
Test name: `Cli_Analyze_AndDumpMystery_EmitRequiredSections`
Assertions:
1. `dotnet run -- <save> --analyze` exits `0`.
2. stdout contains section anchors: `SAVE FILE ANALYSIS`, `FILE VALIDATION`, `MISSION NODES`, `LINKS`, `GOODIES`, `KILL COUNTS`, `TECH SLOTS`.
3. `dotnet run -- <save> --analyze --dump-mystery` exits `0` and stdout contains `UNMAPPED / RESERVED REGIONS`.
4. stderr does not contain `Error:`.
Risk addressed: read-only C# report regressions going undetected while patch-path tests still pass.

### Card P0-04 - C# compare failure contract
Priority: P0
Path: `OnslaughtCareerEditor.UiTests/CliReadOnlyParityTests.cs`
Test name: `Cli_Compare_MissingFile_IsFatal`
Assertions:
1. `dotnet run -- <save> --compare <missing>` exits non-zero.
2. stderr contains `Error: Compare file not found`.
3. stdout does not contain `FILE COMPARISON`.
Risk addressed: broken compare error behavior that confuses users and wrappers.

### Card P0-05 - Python options-file safety guard + override
Priority: P0
Path: `tests_pyqt/test_cli_options_file_safety_unittest.py`
Test name: `test_options_file_career_sections_blocked_by_default_and_allowed_with_override`
Assertions:
1. With input/output named `defaultoptions.bea` and default patch sections enabled, CLI exits non-zero.
2. stderr includes `Career section patching is blocked for .bea/defaultoptions files by default`.
3. Same invocation with `--allow-career-sections-on-options-file` exits `0`.
4. Override path emits warning text `Applying career section patching to an options-style file`.
Risk addressed: accidental progression/goodie writes into global options file without explicit operator intent.

### Card P0-06 - C# options-file safety guard + override
Priority: P0
Path: `OnslaughtCareerEditor.UiTests/CliOptionsFileSafetyTests.cs`
Test name: `Cli_OptionsFileCareerSections_AreBlockedUnlessExplicitlyAllowed`
Assertions:
1. `dotnet run -- defaultoptions.bea output.bea` with default patch sections exits non-zero.
2. stderr contains `Career section patching is blocked for .bea/defaultoptions files by default`.
3. Re-run with `--allow-career-sections-on-options-file` exits `0`.
4. stderr contains warning text about options-style file patching when override is present.
Risk addressed: safety guard drift in C# CLI causing high-impact options-file corruption.

### Card P0-07 - C# binary patch apply/restore roundtrip
Priority: P0
Path: `OnslaughtCareerEditor.UiTests/BinaryPatchRegressionTests.cs`
Test name: `BinaryPatches_ApplyThenRestore_RoundTripsAndCreatesSingleBackup`
Assertions:
1. Seed temp `BEA.exe` with original bytes for selected specs and run apply helper.
2. Selected offsets change to patched bytes.
3. `<exe>.original.backup` is created exactly once and preserves pre-patch bytes.
4. Restore operation returns target file bytes to original.
Risk addressed: untested high-impact mutation path on `BEA.exe` in C# surface.

### Card P0-08 - C# binary patch mismatch abort contract
Priority: P0
Path: `OnslaughtCareerEditor.UiTests/BinaryPatchRegressionTests.cs`
Test name: `BinaryPatches_ApplyAbortsOnMismatch_AndDoesNotCreateBackup`
Assertions:
1. Corrupt one selected patch region before apply.
2. Apply path reports `Apply aborted` and `unexpected`.
3. Target file remains unchanged after abort.
4. `.original.backup` is not created on abort path.
Risk addressed: unsafe patching when bytes are in unknown state.

### Card P0-09 - Cross-stack patch spec parity
Priority: P0
Path: `OnslaughtCareerEditor.UiTests/BinaryPatchSpecParityTests.cs`
Test name: `BinaryPatchSpecs_CSharpAndPython_AreByteIdentical`
Assertions:
1. Export C# patch specs (key, offset, original bytes, patched bytes) via reflection or extracted shared model.
2. Load Python `onslaught.core.binary_patches.PATCH_SPECS` via subprocess JSON dump.
3. Assert identical ordered spec count and per-spec fields.
4. Fail with spec key + field diff when mismatch occurs.
Risk addressed: C#/Python binary patch drift that yields inconsistent verify/apply behavior.

## P1 Cards

### Card P1-10 - Python config command coverage
Priority: P1
Path: `tests_pyqt/test_config_commands_unittest.py`
Test name: `test_set_game_dir_show_config_and_list_saves_with_temp_home`
Assertions:
1. Run commands with isolated `HOME` so config writes to a temp location.
2. `--set-game-dir <valid-dir>` exits `0` and prints `Game directory set to:`.
3. `--show-config` prints `Config file:` and `Game directory:` with set value.
4. `--list-saves` reports discovered `.bes/.bea` and includes size/valid columns.
Risk addressed: first-run and persistence regressions in Python config/discovery workflows.

### Card P1-11 - C# config command + migration coverage
Priority: P1
Path: `OnslaughtCareerEditor.UiTests/ConfigCommandTests.cs`
Test name: `Cli_ConfigCommands_LoadLegacyConfig_AndEmitStableSaveListing`
Assertions:
1. Run CLI subprocess with isolated `APPDATA` pointing to temp tree.
2. Pre-seed legacy `onslaught-career-editor/config.json`; verify `--show-config` succeeds and migrated primary config file is created.
3. `--set-game-dir <valid-dir>` exits `0`; invalid path exits non-zero with `Error: Directory does not exist`.
4. `--list-saves` output is deduped and stable for ties (name/path order after modified-time tie).
Risk addressed: migration and command-surface drift that breaks configuration continuity.

### Card P1-12 - Python keybind override matrix
Priority: P1
Path: `tests_pyqt/test_keybind_overrides_unittest.py`
Test name: `test_keybind_override_tokens_write_expected_entries_and_force_custom_scheme`
Assertions:
1. Apply matrix of valid tokens: keyboard (`A`, `Num7`), look-axis (`MouseX+`, `MouseY-`), wheel (`MouseWheelUp`), mouse buttons (`MouseLeft`, `MouseRight`).
2. Patched file writes expected `(device_code, packed_key)` for affected entry IDs (`0x10..0x21`, `0x3B`, dual write for fire weapon `0x12/0x13`).
3. `OptionsControlSchemeIndex` becomes `0` (Custom) when any keybind override is applied.
4. Unrelated options entries and non-options regions remain unchanged.
Risk addressed: silent parser/mapping regressions in complex keybind override paths.

### Card P1-13 - C# keybind invalid token no-write guard
Priority: P1
Path: `OnslaughtCareerEditor.UiTests/KeybindOverrideRegressionTests.cs`
Test name: `Cli_InvalidKeybindToken_FailsWithoutWritingOutput`
Assertions:
1. Run patch command with invalid keybind token (example: `--bind-look-up NotAToken keep`).
2. CLI exits non-zero and stderr contains `Error: keybind override` or equivalent parse failure marker.
3. Output file is not created.
4. Input file hash remains unchanged.
Risk addressed: malformed keybind inputs causing partial writes or undefined mapping behavior.

### Card P1-14 - Python report structure contract
Priority: P1
Path: `tests_pyqt/test_analysis_output_contract_unittest.py`
Test name: `test_analyze_and_compare_reports_include_required_structural_markers`
Assertions:
1. `--analyze` output includes required anchors: validation, nodes, links, goodies, kill counts, options/settings block.
2. `--compare` output includes `FILE COMPARISON`, `DIFFERENCES BY REGION`, and `MYSTERY REGION DETAILS`.
3. Compare run on identical files reports `Total differing bytes: 0` and `Files are identical!`.
Risk addressed: accidental report-shape changes that break downstream docs/parsers.

### Card P1-15 - C# report structure contract
Priority: P1
Path: `OnslaughtCareerEditor.UiTests/AnalysisOutputContractTests.cs`
Test name: `Cli_AnalyzeAndCompare_EmitStableRequiredSections`
Assertions:
1. `--analyze` output contains required anchors matching C# format contract.
2. `--compare` output contains `FILE COMPARISON`, `DIFFERENCES BY REGION`, and `UNMAPPED / RESERVED REGION DETAILS`.
3. Identical-file compare returns `Total differing bytes: 0`.
Risk addressed: C# output drift breaking parity checks and operational runbooks.

### Card P1-16 - WPF action-level smoke
Priority: P1
Path: `OnslaughtCareerEditor.UiTests/SaveEditorActionSmokeTests.cs`
Test name: `SaveEditor_AnalyzeComparePatchControls_EnforceStateGates`
Assertions:
1. Compare action remains disabled until both primary and compare paths are selected.
2. Patch action remains disabled for invalid input, same-path save mode, or invalid keybind state.
3. In configuration mode with same input/output `.bea`, in-place patch is allowed (with backup flow prompt expected elsewhere).
4. Status text updates to reflect gating reason (`in-place blocked`, `valid file`, etc.).
Risk addressed: GUI can appear healthy in tab-smoke while core actions are broken.

### Card P1-17 - PyQt action-level smoke
Priority: P1
Path: `tests_pyqt/test_gui_action_smoke.py`
Test name: `test_save_analyzer_and_save_editor_controls_gate_actions_correctly`
Assertions:
1. With `qtbot`, verify compare execution path is unavailable until second file selected.
2. Verify patch action warns and aborts when no sections/settings are selected.
3. Verify options-like path + career sections triggers confirmation dialog and respects `No` response.
4. Verify successful analyze action populates summary tree with expected top-level sections.
Risk addressed: PyQt workflow regressions not caught by current tab-label smoke test.

## P2 Cards

### Card P2-18 - Validation checklist command coverage lint
Priority: P2
Path: `tests_pyqt/test_docs_parity_unittest.py`
Test name: `test_app_validation_checklist_lists_all_active_unittest_modules`
Assertions:
1. Parse `roadmap/app-validation-checklist.md` for listed Python regression command modules.
2. Discover active `tests_pyqt/test_*_unittest.py` files (excluding explicitly archived/skipped modules if documented).
3. Assert checklist includes each active unittest module, including `test_binary_patches_unittest.py`.
4. Assert checklist includes C# test project command reference.
Risk addressed: routine validation skips critical suites due stale checklist.

### Card P2-19 - Roadmap parity status consistency lint
Priority: P2
Path: `tests_pyqt/test_docs_parity_unittest.py`
Test name: `test_binary_patch_parity_status_is_consistent_across_roadmap_docs`
Assertions:
1. Parse `roadmap/gui-expansion.md` and `roadmap/csharp-python-parity.md` for Python GUI binary patch parity status tokens.
2. Assert status claims are semantically consistent (`done` vs `pending` mismatch fails).
3. Failure message names conflicting documents and extracted status snippets.
Risk addressed: contradictory docs causing incorrect release-readiness decisions.
