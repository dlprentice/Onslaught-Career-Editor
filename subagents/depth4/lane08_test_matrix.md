# Lane 08 - Consolidated Test Matrix (Depth4 Final Synthesis)

Date: 2026-03-04
Scope: C# UI/CLI + Python UI/CLI + manual game verification for `.bes` / `.bea` workflows and `BEA.exe` binary patches.

## 1) Standard Execution Commands

- C# UI/CLI test suite: `"${DOTNET_EXE:-/mnt/c/Program Files/dotnet/dotnet.exe}" test OnslaughtCareerEditor.UiTests/OnslaughtCareerEditor.UiTests.csproj`
- Python CLI/UI regression suites:
  - `python3 -m unittest tests_pyqt/test_save_patch_regressions_unittest.py tests_pyqt/test_cli_goodie_list_unittest.py tests_pyqt/test_cli_validation_unittest.py tests_pyqt/test_save_editor_defaults_unittest.py tests_pyqt/test_binary_patches_unittest.py`
  - `python3 -m pytest -q tests_pyqt/test_smoke.py`
- C# CLI launcher baseline: `"${DOTNET_EXE:-/mnt/c/Program Files/dotnet/dotnet.exe}" run --project "Onslaught - Career Editor.csproj" --`
- Python CLI launcher baseline: `python3 patcher.py`

## 2) Automated Cross-Surface Matrix

Legend:
- `Existing`: already covered in repo tests.
- `Add-P0/P1/P2`: required additions synthesized from Depth2/Depth3 lane 08.

| ID | Scenario | C# CLI Coverage | C# UI Coverage | Python CLI Coverage | Python UI Coverage | Priority / Status |
|---|---|---|---|---|---|---|
| A01 | Save patch core offsets + boolean polarity | `SavePatchRegressionTests.PatchFile_WritesTailSettingsAtCorrectOffsets_WithNormalBooleanPolarity` | Indirect only | `test_tail_settings_offsets_and_boolean_polarity` | Indirect only | Existing |
| A02 | Level-rank semantics and invalid input fail-fast | `Cli_LevelRank_OneTargetsFirstNode_NotSecondNode`, `Cli_InvalidLevelRankEntry_FailsAndDoesNotWriteOutput` | Indirect only | `test_level_rank_parser_is_zero_based`, `test_invalid_level_rank_entry_is_fatal` | Indirect only | Existing |
| A03 | Goodie boundary + reserved slots preserved | `PatchFile_GoodiesBoundary_PatchesSlot232_AndPreservesReservedSlots` | Indirect only | `test_goodies_patch_includes_slot_232_and_preserves_reserved_slots` | Indirect only | Existing |
| A04 | Kill counter patch preserves metadata high byte | `PatchFile_KillPatch_PreservesMetaHighByte` | Indirect only | `test_kill_patch_preserves_meta_high_byte` | Indirect only | Existing |
| A05 | Copy-options argument conflict fails without write | `Cli_CopyOptionsFromWithBothNoCopyFlags_FailsAndDoesNotWriteOutput` | Indirect only | `test_copy_options_flags_conflict_is_fatal` | Indirect only | Existing |
| A06 | In-place `.bes` patch blocking | `PatchFile_RejectsInPlaceOutputPath` | SaveEditor gating present but no dedicated UI action test | CLI blocks in-place (`patcher.py`), covered by validation paths | SaveEditorTab blocks same-path patch (`_do_patch`) | Existing (CLI) / Add-P1 (UI action test) |
| A07 | Read-only report contract (`--analyze`, `--dump-mystery`) | `Cli_Analyze_AndDumpMystery_EmitRequiredSections` | Save Analyzer tab exists, no contract test | `test_analyze_valid_save_and_dump_mystery_emit_required_sections` | Save Analyzer tab exists, no contract test | Add-P0 |
| A08 | Compare-mode failure contract (missing compare file) | `Cli_Compare_MissingFile_IsFatal` | Compare button gating exists, no failure-path test | `test_compare_missing_file_is_fatal_with_clear_error` | Compare button gating exists, no failure-path test | Add-P0 |
| A09 | Options-file safety guard (`.bea/defaultoptions`) + explicit override | `Cli_OptionsFileCareerSections_AreBlockedUnlessExplicitlyAllowed` | `ConfirmOptionsFilePatchRiskIfNeeded()` exists; no action automation | `test_options_file_career_sections_blocked_by_default_and_allowed_with_override` | Confirmation dialog path exists; no automation | Add-P0 |
| A10 | Binary patch apply/restore roundtrip + mismatch abort | No CLI binary-patch surface | `BinaryPatches_ApplyThenRestore_RoundTripsAndCreatesSingleBackup`, `BinaryPatches_ApplyAbortsOnMismatch_AndDoesNotCreateBackup` | Core coverage exists (`test_apply_then_restore_roundtrip`, `test_apply_aborts_on_unexpected_bytes`) | UI flow exists; action smoke missing | Add-P0 for C# UI tests, Add-P1 for Python UI action smoke |
| A11 | Binary patch spec parity (C# specs vs Python `PATCH_SPECS`) | N/A | `BinaryPatchSpecs_CSharpAndPython_AreByteIdentical` | N/A | N/A | Add-P0 |
| A12 | Config commands (`--set-game-dir`, `--show-config`, `--list-saves`) | `Cli_ConfigCommands_LoadLegacyConfig_AndEmitStableSaveListing` | Settings UI exists; no parity automation | `test_set_game_dir_show_config_and_list_saves_with_temp_home` | Settings tab basic behavior, no regression matrix | Add-P1 |
| A13 | Keybind override matrix and invalid-token no-write guard | `Cli_InvalidKeybindToken_FailsWithoutWritingOutput` + parser coverage | SaveEditor keybind validation exists; no action-level automation | `test_keybind_override_tokens_write_expected_entries_and_force_custom_scheme` | SaveEditor validation present; no matrix automation | Add-P1 |
| A14 | Report structure stability (`--analyze`/`--compare`) | `Cli_AnalyzeAndCompare_EmitStableRequiredSections` | Save Analyzer tab visual only | `test_analyze_and_compare_reports_include_required_structural_markers` | Save Analyzer tab visual only | Add-P1 |
| A15 | UI action-level gating (buttons/state transitions) | N/A | `SaveEditor_AnalyzeComparePatchControls_EnforceStateGates` | N/A | `test_save_analyzer_and_save_editor_controls_gate_actions_correctly` | Add-P1 |
| A16 | Docs/checklist parity lint for regression command drift | N/A | N/A | `test_app_validation_checklist_lists_all_active_unittest_modules`, `test_binary_patch_parity_status_is_consistent_across_roadmap_docs` | N/A | Add-P2 |

## 3) Manual Game Verification Matrix (.bes / .bea / Binary Patches)

| ID | Area | Setup | Procedure | Pass Criteria |
|---|---|---|---|---|
| M01 | `.bes` career patch end-to-end | Copy `save-attempts/haha-cannon-goes-brrrrr.bes` to temp output paths (do not patch baseline in place). | Patch once with C# CLI and once with Python CLI using equivalent options (rank/kills/new goodies). Load each patched save in game and enter mission select / goodies UI. | No load crash; expected mission unlock/rank/goodie states visible; patched files remain exactly `10004` bytes and valid version word `0x4BD1`. |
| M02 | `.bes` read-only parity checks | Use same source + patched outputs from M01. | Run both CLIs with `--analyze`, `--analyze --dump-mystery`, and `--compare` between baseline and patched outputs. | Both stacks report same semantic differences (format can differ); compare shows non-zero diff for patched files and zero diff for identical pairs. |
| M03 | `.bea` safety guardrails in tooling | Prepare `defaultoptions.bea` copy (input/output as `.bea`). | In both CLIs, attempt career-section patching against `.bea` without override, then with override flag (`--allow-career-sections-on-options-file`). | Default run blocks with explicit safety error; override run proceeds and emits warning. |
| M04 | `.bea` runtime application at boot | Use a `.bea` with intentionally distinct options values (sound/music, invert toggles, controller config, options entries). | Place as active `defaultoptions.bea`; cold-launch game to main menu/options. | Runtime options reflect `.bea` values on boot (global options path works). |
| M05 | `.bes` vs `.bea` global-options behavior | Use two files with intentionally different options-entry/tail values. | Boot from `defaultoptions.bea`; then load a career `.bes` with conflicting options values. Observe active options and inspect on-disk `defaultoptions.bea` after load/exit cycle. | Active options follow boot globals (not per-save apply during load); after load/exit, `defaultoptions.bea` updates to match loaded save buffer for options regions. |
| M06 | Binary patch byte-safety flow (both GUIs) | Use a disposable copy of `BEA.exe`. Select any subset of three supported patch specs: `0x129696`, `0x12A644`, `0x12BB97`. | In WPF and PyQt Binary Patches tabs: `Verify Selected` -> `Apply Selected` -> `Verify Selected` -> `Restore Backup`. | Verify reports known states before apply; first apply creates `BEA.exe.original.backup`; post-apply verify shows `already patched`; restore returns bytes to original and remains verifiable. |
| M07 | Binary patch mismatch-abort safety | Corrupt one target patch byte in disposable `BEA.exe` before apply. | Run verify/apply in UI on corrupted target. | Apply aborts with `unexpected bytes`; no write to target patch region for selected spec; no backup created on abort path. |
| M08 | Runtime binary-patch behavior validation | Use patched executable from M06. | Launch game and validate display/window behavior on target machine: widescreen acceptance, startup window mode behavior, optional patch 3 effect only when needed. | Byte-level patch state must be correct regardless of UX outcome; runtime behavior recorded as pass/warn per machine because patch 3 is explicitly optional/non-universal. |

## 4) Manual Verification Evidence Requirements

For each manual matrix item, capture:
- Exact command(s) or UI path used.
- Input/output file paths and SHA-256 hashes before/after.
- Key report excerpts (`--analyze`, `--compare`, or patch output panel text).
- In-game observation notes with timestamp and machine profile.
- Final verdict: `PASS`, `FAIL`, or `WARN (environment-specific runtime variance)`.

## 5) Release Gate Recommendation (Lane 08)

Minimum gate before release candidate:
- All `Existing` automated rows remain green.
- All `Add-P0` rows implemented and green on CI/local validation.
- Manual rows `M01` through `M07` pass at least once on the primary Windows validation machine.
- `M08` documented with machine-specific outcome and byte-level verification evidence.
