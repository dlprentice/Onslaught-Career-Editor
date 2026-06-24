# Lane 05 - C# CLI vs Python CLI Parity Validation

## Scope
Validated option and behavior parity between:
- C# CLI entrypoint: `Program.cs`
- Python CLI entrypoint: `patcher.py`

Validation used source inspection, existing tests, and live command artifacts.

## Evidence Used
- Source:
  - `Program.cs:85`, `Program.cs:553`, `Program.cs:586`, `Program.cs:613`, `Program.cs:621`, `Program.cs:632`, `Program.cs:677`, `Program.cs:718`, `Program.cs:736`, `Program.cs:745`, `Program.cs:894`, `Program.cs:1104`, `Program.cs:1134`
  - `patcher.py:787`, `patcher.py:826`, `patcher.py:1615`, `patcher.py:1623`, `patcher.py:1660`, `patcher.py:1701`, `patcher.py:1747`, `patcher.py:1848`, `patcher.py:1860`, `patcher.py:1869`, `patcher.py:1879`, `patcher.py:1885`, `patcher.py:1898`, `patcher.py:1943`, `patcher.py:2093`
- Existing tests:
  - `tests_pyqt/test_cli_validation_unittest.py:23`, `tests_pyqt/test_cli_validation_unittest.py:50`
  - `tests_pyqt/test_cli_goodie_list_unittest.py:107`, `tests_pyqt/test_cli_goodie_list_unittest.py:121`
  - `OnslaughtCareerEditor.UiTests/SavePatchRegressionTests.cs:78`, `OnslaughtCareerEditor.UiTests/SavePatchRegressionTests.cs:125`, `OnslaughtCareerEditor.UiTests/SavePatchRegressionTests.cs:150`
- Live runs (2026-03-04):
  - `python3 -m unittest -v tests_pyqt.test_cli_validation_unittest` -> 2 passed
  - `python3 -m unittest -v tests_pyqt.test_cli_goodie_list_unittest` -> 5 passed
  - `"/mnt/c/Program Files/dotnet/dotnet.exe" test OnslaughtCareerEditor.UiTests/OnslaughtCareerEditor.UiTests.csproj --filter "Name~Cli_"` -> 3 passed
  - Help-surface diff from `patcher.py -h` vs C# `--help`
  - Manual behavior probes (`--version`, invalid `--controller-config-p1`, copy-options conflict, analyze, compare, and a multi-option patch parity run)

## Parity Table
| Area | Result | Evidence | Notes |
|---|---|---|---|
| Long-option surface parity | Partial | Help diff: 56 shared options, C# adds `--version` | Functional parity is high; one explicit surface drift exists. |
| Core patch behavior on complex option set | Match | Same input + multi-option patch command produced byte-identical outputs (`sha256` equal; `cmp` exit 0) | Included rank + level overrides, per-category kills, settings overrides, and keybind overrides. |
| Read-only mode routing precedence (`--compare` > `--analyze` > `--list-goodies`) | Match | `Program.cs:553/586/613`; `patcher.py:1848/1860/1869` | Same precedence and exit behavior intent. |
| Input/output requirements + in-place guard | Match | `Program.cs:621/632`; `patcher.py:1879/1885` | Both reject missing patch output and in-place writes. |
| `--level-rank` parsing/validation semantics | Match | `Program.cs:677`; `patcher.py:787`; regression tests in both stacks | Both enforce `NODE_INDEX:GRADE`, 1..43 external mapping, fatal on invalid entries. |
| `--copy-options-from` conflict (`--no-copy-options-entries` + `--no-copy-options-tail`) | Match (stderr contract), minor stdout drift | `Program.cs:745`; `patcher.py:2093`; tests in both stacks | Both fail with same error string and no output file; Python prints config block before failing, C# does not. |
| `--list-goodies` summary + reserved-slot behavior | Match | Cross-language parity test `tests_pyqt/test_cli_goodie_list_unittest.py:121` | Verified for default and `--show-reserved-goodies` modes. |
| Tri-bool parsing (`on/off/true/false/1/0/...`) | Match | `Program.cs:1104`; `patcher.py:826` | Token sets and preserve semantics are aligned. |
| Keybind override mapping/handling | Match | `Program.cs:1134`; `patcher.py` keybind parser + byte-identical patch artifact | Multi-option parity run included keybind overrides and matched output bytes. |
| Config command availability (`--list-saves`, `--set-game-dir`, `--show-config`) | Match in command availability; environment-dependent output | `Program.cs:894`; `patcher.py:1747`; manual `--show-config` run | Both support commands; output content differs by runtime/config location. |
| Analyze/compare textual output format | Partial | Manual `--analyze` and `--compare` runs both rc=0 | Semantics align, but textual formatting/line counts differ. |

## Residual Divergence Risks
1. `--version` drift (real surface mismatch).
- C# supports `--version` (rc=0, version text).
- Python treats `--version` as unrecognized (argparse error, rc=2).
- Risk: scripts/docs expecting `--version` fail on Python CLI.

2. Validation stage differences for typed numeric args.
- Example: `--controller-config-p1 -1`.
- C#: parse-time rejection by System.CommandLine (prints help + parse error).
- Python: accepts parse as `int`, prints patch config, then fails in patch validation.
- Risk: stdout/stderr contract drift for automation/golden-output tests.

3. Failure-output shape differs on some invalid combinations.
- Example: copy-options conflict prints 13 stdout lines in Python (config preamble) vs 0 in C#.
- Risk: fragile CLI wrapper tooling that expects identical stdout on failure.

4. Analyze/compare output formatting is not fully identical.
- Both succeed and communicate same outcome, but headings/line counts/message wording differ.
- Risk: text scraping/parsing tools may break cross-runtime.

5. Config output varies by runtime environment.
- Python (WSL) and C# (Windows) read different config roots and may auto-detect different game dirs.
- Risk: perceived parity regressions that are environmental, not logic bugs.

## Bottom Line
- Patch semantics and major CLI behaviors are in strong parity.
- The primary explicit option drift is `--version` (C# only).
- Remaining divergence is mostly output-contract/UX-level, not data-patch correctness.
