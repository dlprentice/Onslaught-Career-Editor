# Depth4 Lane 5/10 - C# CLI + Python CLI Parity Closure Plan

## Inputs Used
- `subagents/depth1/lane01_csharp_app_inventory.md`
- `subagents/depth1/lane02_python_app_inventory.md`
- `subagents/depth1/lane03_test_coverage_inventory.md`
- `subagents/depth2/lane05_cli_parity_validation.md`
- `subagents/depth3/lane05_cli_fixcards.md`
- `subagents/depth3/lane10_master_fix_queue.tsv` (`FX-006`, `FX-036`, `FX-037`, `FX-038`, `FX-039`, `FX-008`)

## Closure Objective
Close the remaining C# vs Python CLI parity gaps that are output-contract and option-surface deltas, while preserving already-verified patch semantics parity.

## Baseline Synthesis
1. Core patch outputs are already byte-identical for complex patch scenarios.
2. Remaining parity gaps are concentrated in CLI UX contracts:
3. `--version` exists in C# but not Python.
4. Python delays some numeric validation until patch execution (`--controller-config-p1/-p2`), while C# fails at parse time.
5. Python emits patch preamble text on at least one fatal validation path (`--copy-options-from` with both no-copy flags), while C# emits stderr-only failure.
6. Analyze/compare semantics match, but output formatting should be contract-tested via stable markers.
7. Missing compare-file wording differs (`Compare file not found` vs `Comparison file not found`).

## Execution Order (Parity Closure Sequence)
1. `CLI-04` contract-first scaffolding:
Define shared read-only output markers and add marker-based tests before heavy wording edits.
Files:
- `tests_pyqt/test_cli_readonly_modes_unittest.py` (new)
- `OnslaughtCareerEditor.UiTests/CliReadOnlyParityTests.cs` (new)
- Small marker-preservation touches in `Program.cs` and `patcher.py` only if needed.

2. `CLI-03` failure-path stdout cleanup:
Move fatal patch-mode validation checks in Python to run before first config/preamble print.
Files:
- `patcher.py` (reorder validation flow around current preamble print and copy-options conflict check).

3. `CLI-02` numeric validation stage alignment:
Promote Python `--controller-config-p1/-p2` validation to argparse type parsing (uint32-range type), keep patch-layer guard as defense-in-depth.
Files:
- `patcher.py` (argparse type function + option bindings).
- `tests_pyqt/test_cli_validation_unittest.py` (assert parse-stage failure behavior + no output file).

4. `CLI-01` option-surface parity (`--version`):
Add Python `--version` and align success contract to C# shape (single-line version output, zero exit).
Files:
- `patcher.py` (argparse version option).
- `tests_pyqt/test_cli_validation_unittest.py` or `tests_pyqt/test_cli_option_surface_unittest.py` (new if separated).

5. `CLI-05` missing-compare canonical wording:
Choose one canonical error phrase and enforce in both stacks.
Recommended canonical string:
- `Error: Compare file not found: <path>`
Files:
- `Program.cs`
- `patcher.py`
- C# and Python CLI validation tests.

6. Final parity gate run and artifact capture:
Run both test stacks plus direct command probes; capture results in lane artifact notes if needed.

## Expected Output Contracts (Authoritative for Lane 5)

| Contract ID | Scenario | Command shape | Expected rc | Stdout contract | Stderr contract | File side-effect contract |
|---|---|---|---|---|---|---|
| `CLI-C-VERSION-001` | Version option success | `python3 patcher.py --version` and C# `-- --version` | `0` | Exactly 1 non-empty line containing version token (`semver` with optional build metadata). No usage/help dump. | Empty | No file writes |
| `CLI-C-ANALYZE-001` | Analyze success markers | `--analyze <input>` | `0` | Must include: `SAVE FILE ANALYSIS`, `FILE VALIDATION`, `MISSION NODES`, `LINKS`, `GOODIES`, `KILL COUNTS` | Empty | No file writes |
| `CLI-C-COMPARE-001` | Compare identical files | `<input> --compare <identical_copy>` | `0` | Must include: `FILE COMPARISON`, `Total differing bytes: 0`, `Files are identical!` | Empty | No file writes |
| `CLI-C-COMPARE-ERR-001` | Compare missing file | `<input> --compare <missing>` | non-zero | Empty or no report headers | Must include canonical phrase `Error: Compare file not found:` | No output patch file written |
| `CLI-C-VAL-UINT-001` | Invalid controller config value | `<input> <output> --controller-config-p1 -1` | non-zero | Must not include `Onslaught Career Editor - CLI Mode` preamble | Must contain argument-validation failure for `--controller-config-p1` | Output file must not exist |
| `CLI-C-VAL-COPY-001` | Copy-options impossible conflict | `<input> <output> --copy-options-from <same> --no-copy-options-entries --no-copy-options-tail` | non-zero | Must be empty (no patch config banner) | Must include `both --no-copy-options-entries and --no-copy-options-tail were set` | Output file must not exist |

## Implementation Mapping (Fixcard -> Files -> Tests)

| Fixcard | Code files | Test files | Primary assertion |
|---|---|---|---|
| `CLI-01` | `patcher.py` | `tests_pyqt/test_cli_validation_unittest.py` (or new option-surface module) | Python supports `--version` with rc `0` and single-line output |
| `CLI-02` | `patcher.py` | `tests_pyqt/test_cli_validation_unittest.py`; C# regression assertions remain in existing suite | Invalid uint args fail in parse stage; no patch preamble; no output file |
| `CLI-03` | `patcher.py` | `tests_pyqt/test_cli_validation_unittest.py`; existing C# test remains reference | Fatal validation no longer emits stdout preamble |
| `CLI-04` | `Program.cs`, `patcher.py` (minimal), plus new test harness files | `tests_pyqt/test_cli_readonly_modes_unittest.py`, `OnslaughtCareerEditor.UiTests/CliReadOnlyParityTests.cs` | Shared marker contracts stable for analyze/compare |
| `CLI-05` | `Program.cs`, `patcher.py` | both validation suites | Canonical missing-compare wording identical across runtimes |

## Verification Gate (Closure Pass)
1. `python3 -m unittest -v tests_pyqt.test_cli_validation_unittest`
2. `python3 -m unittest -v tests_pyqt.test_cli_readonly_modes_unittest`
3. `python3 -m unittest -v tests_pyqt.test_cli_goodie_list_unittest`
4. `"/mnt/c/Program Files/dotnet/dotnet.exe" test OnslaughtCareerEditor.UiTests/OnslaughtCareerEditor.UiTests.csproj --filter "Name~Cli_"`
5. Direct probes:
6. Python + C# `--version`
7. Python + C# missing compare-file error
8. Python + C# invalid `--controller-config-p1 -1`
9. Python + C# identical `--compare` marker checks

## Done Criteria
1. All `CLI-01..CLI-05` acceptance criteria from `subagents/depth3/lane05_cli_fixcards.md` pass.
2. Contracts `CLI-C-*` above are green in both runtimes.
3. No regression in existing CLI tests (`level-rank`, copy-options conflict, goodies list parity).
4. No changes required outside CLI/relevant test surfaces.

## Non-Goals for Lane 5
1. Config-root path output normalization across Windows vs WSL (`--show-config`) is documented parity context, not a closure blocker.
2. GUI parity and binary patch parity work remain in their own lanes.
