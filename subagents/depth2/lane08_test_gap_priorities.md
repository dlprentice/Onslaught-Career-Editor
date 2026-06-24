# Lane 08 - Prioritized Regression/Test Gap List (C# + Python)

## Coverage Snapshot (Current)
- C# tests: 10 total (`OnslaughtCareerEditor.UiTests/SavePatchRegressionTests.cs`, `OnslaughtCareerEditor.UiTests/SmokeTests.cs`).
- Python tests: 18 total (17 `unittest` + 1 `pytest` smoke under `tests_pyqt/`).
- Strongest coverage: save patch offset regressions, basic CLI validation failures, goodie-list parity summary, Python core binary patch roundtrip.
- Weakest coverage: read-only CLI flows (`--analyze/--compare/--dump-mystery`), config commands, C# binary patch engine behavior, GUI behavior beyond tab-presence, docs parity drift checks.

## Priority Scale
- `P0` Critical: high corruption/parity risk or release-gate blind spot.
- `P1` High: frequent user workflow with realistic regression probability.
- `P2` Medium: drift/maintenance risk that compounds over time.

## Risk-Ranked Additions

| Priority | Gap | Why Risk Is High | Evidence (Current Blind Spot) | Recommended Test Additions |
|---|---|---|---|---|
| P0 | Read-only CLI parity suite (`--analyze`, `--compare`, `--dump-mystery`) | These are primary diagnostics; silent drift breaks user trust and debugging flow across stacks. | Flags and handlers exist in C#: `Program.cs:99-113`, `Program.cs:552-616`; Python: `patcher.py:1615-1623`, `patcher.py:1847-1875`. No tests reference these flags in `OnslaughtCareerEditor.UiTests` or `tests_pyqt`. | Add cross-stack golden/snapshot tests for success/failure and key report markers (valid file, invalid file, compare missing file, dump-mystery section presence). |
| P0 | Options-file safety guard coverage (`.bea/defaultoptions` career-section blocking + override) | Wrong defaults here can corrupt global options or write progression data in the wrong file class. | Guard logic in C#: `Program.cs:769-792`; Python: `patcher.py:1930-1939`; GUI confirmations in WPF: `Views/SaveEditorView.xaml.cs:769-791`, PyQt: `onslaught/gui/tabs/save_editor.py:1376-1386`. Existing tests do not cover `--allow-career-sections-on-options-file` paths. | Add C#/Python CLI tests for blocked-by-default behavior and explicit override success. Add GUI tests asserting confirmation prompts/gates are enforced for options-like paths. |
| P0 | C# binary patch regression suite (verify/apply/restore semantics) | Binary patch path mutates `BEA.exe`; failures are high-impact and currently unguarded in C#. | Python core is tested: `tests_pyqt/test_binary_patches_unittest.py:22-78`. C# binary patch implementation is separate and untested: `Views/BinaryPatchesView.xaml.cs:34-314`. | Add C# tests for: known-state verify, apply abort on mismatch, no backup-on-abort, backup creation once, restore success/fail. Add parity test that C# and Python patch specs (offset/original/patched bytes) are identical. |
| P1 | Config command + config migration parity (`--list-saves`, `--set-game-dir`, `--show-config`) | Affects discovery, first-run usability, and persistence across sessions; regressions look like “app is broken” to users. | C# command path: `Program.cs:894-992`; Python command path: `patcher.py:1746-1833`; config cores: `AppConfig.cs:105-338`, `onslaught/core/config.py:40-247`. No direct tests for these command paths. | Add isolated temp-home/appdata tests validating set/show/list flows, legacy config migration, dedupe/sort behavior, and invalid path handling in both stacks. |
| P1 | Keybind override end-to-end tests (CLI + GUI parser behavior) | Complex token parsing with multiple input dialects; easy to regress silently and hard for users to debug. | Heavy parser logic in C#: `Program.cs:1134-1240`, WPF: `Views/SaveEditorView.xaml.cs:1306-1548`; Python CLI/UI parsing: `patcher.py:1953-2034`, `onslaught/gui/tabs/save_editor.py:1212-1345`. Current tests only cover small parser fragments (`SavePatchRegressionTests.cs:210-233`). | Add matrix tests for valid/invalid keybind tokens (`MouseX+/-`, `MouseY+/-`, wheel/buttons, packed vk/scan) verifying precise output mutation and no-write-on-failure behavior. |
| P1 | GUI behavior smoke depth (not just tab presence) | Current smoke can pass while real actions are broken (analyze/compare/patch controls). | C# smoke only checks tab labels and can skip (`SmokeTests.cs:16-77`); PyQt smoke same (`tests_pyqt/test_smoke.py:15-45`, skip at `:16-17`). No automated action-level GUI checks. | Add action-level smoke: load file, run analyze, enable compare button only when 2 files selected, patch button gating, binary-patch verify/apply button state transitions. |
| P1 | Save analyzer/compare output structure contracts | Output formatting is used for user workflows and parity checks; untested report shifts can break tooling/docs. | Report generators are substantial in C#: `BesFilePatcher.cs:1421-1540`, `BesFilePatcher.cs:1545-1745`; Python compare/analyze paths at `patcher.py:934+`, `patcher.py:1859-1866`. No snapshot tests for report sections beyond goodie list. | Add snapshot/structural assertions for required sections and key summary fields (nodes/links/goodies/kills/options tail) for both stacks. |
| P2 | Validation checklist completeness drift | Runbook omissions cause real suites to be skipped in routine validation. | Checklist omits binary patch unittest invocation: `roadmap/app-validation-checklist.md:18-19` (no `tests_pyqt/test_binary_patches_unittest.py`). | Add docs-parity test that checklist command list includes all active regression modules under `tests_pyqt/test_*_unittest.py` and C# test project. |
| P2 | Cross-doc parity contradictions | Conflicting docs create wrong operator expectations and bad triage decisions. | Contradictory status lines: Python binary patch parity “pending” in `roadmap/gui-expansion.md:70` vs “done” in `roadmap/csharp-python-parity.md:210`. | Add docs consistency lint: assert canonical parity claims align across roadmap docs; fail on contradictory status markers for core features. |

## Suggested Execution Order (Fastest Risk Burn-Down)
1. Implement `P0` CLI read-only parity + options-file safety tests first.
2. Implement `P0` C# binary patch tests next (plus cross-stack spec parity check).
3. Implement `P1` config command/migration tests.
4. Expand GUI action smoke (`P1`) after core CLI and binary guards are in place.
5. Add docs-parity lint tests (`P2`) to prevent drift recurrence.

## Minimum New Test Files To Add (Target)
- `tests_pyqt/test_cli_readonly_modes_unittest.py`
- `tests_pyqt/test_cli_options_file_safety_unittest.py`
- `tests_pyqt/test_config_commands_unittest.py`
- `tests_pyqt/test_keybind_overrides_unittest.py`
- `OnslaughtCareerEditor.UiTests/BinaryPatchRegressionTests.cs`
- `OnslaughtCareerEditor.UiTests/CliReadOnlyParityTests.cs`
- `tests_pyqt/test_docs_parity_unittest.py`
