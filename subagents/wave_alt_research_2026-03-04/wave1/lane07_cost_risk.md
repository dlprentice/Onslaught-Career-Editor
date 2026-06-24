# Lane 07/08 - Cost/Risk Analysis for Competing Parity Alternatives

Date: 2026-03-04
Mode: Read-only analysis; no state-file edits

## Scope Baseline (Docs + App Behavior touched by prior parity work)

Primary code surfaces:
- `Program.cs`
- `patcher.py`
- `MainWindow.xaml`
- `MainWindow.xaml.cs`
- `Views/SaveEditorView.xaml`
- `Views/SaveEditorView.xaml.cs`
- `Views/SaveAnalyzerView.xaml.cs`
- `onslaught/gui/main_window.py`
- `onslaught/gui/tabs/save_editor.py`
- `onslaught/gui/tabs/save_analyzer.py`

Primary doc surfaces:
- `roadmap/csharp-python-parity.md` (+ `lore-book/roadmap/csharp-python-parity.md` mirror)
- `roadmap/gui-expansion.md`
- `roadmap/app-validation-checklist.md`
- `roadmap/app-delivery-phases.md`
- `README.MD`
- `CURRENT_CAPABILITIES.md`

Current divergence anchors used for costing:
- Config in-place policy mismatch: C# allows in-place `.bea` with backup (`Views/SaveEditorView.xaml.cs:929-1010`), Python blocks same-path always (`onslaught/gui/tabs/save_editor.py:1073-1075`).
- CLI compare error text mismatch: C# `Compare file not found` (`Program.cs:557`) vs Python `Comparison file not found` (`patcher.py:1878`).
- CLI failure-output stage mismatch for copy-options conflict: C# checks before preamble (`Program.cs:743-747`), Python checks after preamble (`patcher.py:2065`, `patcher.py:2118-2124`).
- Docs still contain mixed parity narratives in some lanes (for example historical lore-source wording in `roadmap/gui-expansion.md:102` vs lore-book runtime in code).

Approximate touched surface size for migration planning: ~10,842 lines across core parity code+docs.

## Ranked Implementation Paths

| Rank | Path | Summary | Migration Complexity | Regression Surface | Rollback Cost |
|---|---|---|---|---|---|
| 1 | **Path B - Contract-First Hybrid (Recommended)** | Keep intentional high-risk behavior divergence where justified (config in-place), but close contract drifts (CLI text/stage, docs accuracy, test gates). | **Medium** (2-4 dev days) | **Medium-Low** | **Low-Medium** |
| 2 | **Path A - Docs-First Divergence Formalization** | Freeze behavior as-is; explicitly document differences and tighten parity wording/tests around “intentional divergence”. | **Low** (0.5-1.5 dev days) | **Low in code / Medium in UX drift debt** | **Low** |
| 3 | **Path D - Safety-Canonical Convergence (Disable in-place everywhere)** | Align both stacks to strict no in-place patching for `.bea` and simplify safety model. | **Medium** (1.5-3 dev days) | **Medium** (user workflow break) | **Low-Medium** |
| 4 | **Path C - Full C#-Canonical Behavior Convergence** | Bring Python GUI/CLI to C# behavior contracts, including safe in-place `.bea` backup flow. | **Medium-High** (3-6 dev days) | **Medium-High** | **Medium** |
| 5 | **Path E - Shared-Core Refactor** | Extract shared parity contract/core wrappers to reduce future drift structurally. | **High** (8-15 dev days) | **High during migration** | **High** |

## Path Details

## Path B - Contract-First Hybrid (Recommended)

Implementation shape:
- Keep C# in-place `.bea` flow and Python same-path block temporarily as **explicitly intentional**.
- Normalize CLI contract deltas:
  - compare missing-file wording (`Program.cs:557`, `patcher.py:1878`)
  - failure-output ordering around copy-options conflict (`Program.cs:743-747`, `patcher.py:2118-2124`)
- Keep menu/status parity and lore lazy-load as-is (already aligned in `MainWindow.xaml:27-41`, `MainWindow.xaml.cs:124-137`, `onslaught/gui/main_window.py:121-157`, `onslaught/gui/tabs/lore_browser.py:45-50`).
- Update parity docs to reflect actual intentional divergence and close stale wording pockets.

Estimated migration footprint:
- Code: 4-6 files.
- Tests: 3-5 files (`tests_pyqt/test_cli_*`, `OnslaughtCareerEditor.UiTests/CliReadOnlyAndOptionsSafetyTests.cs`).
- Docs: 4-7 files.

Regression surface:
- Save corruption risk: low (no new write-path complexity introduced).
- CLI automation risk: low after contract normalization.
- UX parity drift risk: medium (config-mode divergence remains, but documented).

Rollback strategy:
1. Revert only CLI contract edits (`Program.cs`, `patcher.py`) if parser/output consumers break.
2. Keep doc commit separate so wording rollback is independent from behavior rollback.
3. Trigger rollback if read-only parity tests fail on either stack for two consecutive runs.

## Path A - Docs-First Divergence Formalization

Implementation shape:
- No behavior change.
- Update parity docs/checklists to explicitly declare remaining drifts as intentional.
- Add “semantic parity, not byte-for-byte UX parity” framing where needed.

Estimated migration footprint:
- Code: 0-1 files (tests only, optional).
- Docs: 6-10 files.

Regression surface:
- Runtime behavior risk: minimal.
- Product/support risk: medium (ongoing two-behavior model across stacks).
- Drift recurrence risk: medium-high unless docs-lint is added.

Rollback strategy:
1. Revert doc bundle only.
2. Keep previous parity table snapshot in branch tag before rewrite.
3. Roll back if contributor confusion increases (for example repeated contradictory fix attempts across stacks).

## Path D - Safety-Canonical Convergence (Disable in-place everywhere)

Implementation shape:
- Remove C# config in-place path and require distinct output path like Python.
- Collapse guidance/tooltips to one strict safety model.

Estimated migration footprint:
- Code: 3-5 files (`Views/SaveEditorView.xaml.cs`, `Views/SaveEditorView.xaml`, tests, docs).
- Tests: adjust/replace any in-place expectations.
- Docs: 4-6 files (`README.MD`, parity docs, runbooks).

Regression surface:
- Data safety risk: reduced.
- Workflow regression risk: medium-high for users relying on in-place config patch + auto backup.
- Cross-stack parity risk: reduced.

Rollback strategy:
1. Preserve prior in-place branch/cherry-pickable commit.
2. If user friction spikes, re-enable in-place behind explicit advanced toggle.
3. Roll back on failed manual workflow validation for defaultoptions update path.

## Path C - Full C#-Canonical Behavior Convergence

Implementation shape:
- Port C# safe in-place `.bea` flow into Python GUI:
  - canonical-path detection
  - confirm dialog
  - temp output + timestamped backup + atomic replacement
- Align remaining CLI output/error contracts to C# style.
- Remove intentional-divergence notes from parity docs.

Estimated migration footprint:
- Code: 6-9 files (`onslaught/gui/tabs/save_editor.py`, likely helper in `onslaught/core/*`, plus CLI and tests).
- Tests: 5-8 files across C#/Python.
- Docs: 5-8 files.

Regression surface:
- Highest risk zone is Python file-write path correctness (backup/replace failures, partial writes, permissions, cross-platform path edge cases).
- Medium risk in CLI contract changes for existing output parsers.

Rollback strategy:
1. Ship in-place Python behavior behind feature flag/env gate first.
2. Keep hard fallback to current “same-path blocked” behavior.
3. Automatic rollback trigger: any failed backup+replace integration test or temp-file leak in CI/manual gate.

## Path E - Shared-Core Refactor

Implementation shape:
- Introduce shared contract modules/libraries for CLI messaging, compare/analyze markers, and optionally save-editor safety policy constants.
- Refactor both stacks to consume shared contracts.

Estimated migration footprint:
- Code: 10-16 files minimum.
- Tests: broad rewrite of parity assertions.
- Docs: broad rewrite of implementation authority notes.

Regression surface:
- High due to cross-cutting churn in stable lanes (CLI+GUI+docs simultaneously).
- Not justified until current parity deltas are small and stable.

Rollback strategy:
1. Execute as tranche-based feature branches per subsystem (CLI, GUI, docs) with merge gates.
2. Abort/refreeze on first tranche regression; avoid partial merged state.

## Recommended Order (Risk-Adjusted)

1. Execute **Path B** now.
2. If team wants zero behavior drift despite policy differences, follow with a narrow **Path A** doc hardening pass (docs-lint + parity table locks).
3. Decide between **Path C** and **Path D** only after collecting 1-2 release cycles of telemetry on config in-place usage and support burden.
4. Defer **Path E** until post-stabilization.

## Rollback Readiness Checklist (applies to any path)

- Keep behavior and docs changes in separate commits.
- Keep C# and Python contract-test updates in separate commits from functional behavior edits.
- Before merge, require green gates already used in this repo:
  - `OnslaughtCareerEditor.UiTests` targeted filters (`CliReadOnly|OptionsFile|BinaryPatch`)
  - `tests_pyqt/test_cli_readonly_modes_unittest.py`
  - `tests_pyqt/test_cli_options_file_safety_unittest.py`
- For any write-path change, require manual backup/restore verification on disposable `.bea` copies.
