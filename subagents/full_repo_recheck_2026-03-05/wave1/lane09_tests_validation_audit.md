# Lane 09: Tests / Validation Audit

Date: 2026-03-05
Scope: automated tests, regression harnesses, proof artifacts, manual test commands, and coverage gaps.
Constraint: read-only audit; no state files edited.

## Current observed status

Commands executed from repo root:

- `"/mnt/c/Program Files/dotnet/dotnet.exe" test "OnslaughtCareerEditor.UiTests/OnslaughtCareerEditor.UiTests.csproj" --no-restore --no-build --logger "console;verbosity=minimal"`
  - Result: `Passed 22/22, Skipped 0, Duration 2m55s`
- `"/mnt/c/Program Files/dotnet/dotnet.exe" test "OnslaughtCareerEditor.UiTests/OnslaughtCareerEditor.UiTests.csproj" --no-restore --no-build --filter "Name~CliReadOnly|Name~OptionsFile|Name~BinaryPatch" --logger "console;verbosity=minimal"`
  - Result: `Passed 12/12, Skipped 0, Duration 1m45s`
- `"/mnt/c/Program Files/dotnet/dotnet.exe" test "OnslaughtCareerEditor.UiTests/OnslaughtCareerEditor.UiTests.csproj" --no-restore --no-build --filter "Name~BinaryPatch" --logger "console;verbosity=minimal"`
  - Result: `Passed 6/6, Skipped 0`
- `python3 -m unittest discover -s tests_pyqt -p 'test_*_unittest.py'`
  - Result: `Ran 23 tests in 102.778s, OK (skipped=1)`
- `python3 -m unittest tests_pyqt/test_save_patch_regressions_unittest.py tests_pyqt/test_cli_goodie_list_unittest.py tests_pyqt/test_cli_validation_unittest.py tests_pyqt/test_save_editor_defaults_unittest.py tests_pyqt/test_binary_patches_unittest.py tests_pyqt/test_cli_readonly_modes_unittest.py tests_pyqt/test_cli_options_file_safety_unittest.py`
  - Result: `Ran 20 tests in 83.522s, OK (skipped=1)`
- `python3 -m unittest -v tests_pyqt.test_save_editor_defaults_unittest`
  - Result: skipped: `PyQt6 unavailable: No module named 'PyQt6'`
- `python3 -m pytest -q tests_pyqt`
  - Result: failed immediately: `No module named pytest`

Inventory observed in code:

- C# test methods: 22 total across four files.
- Python test functions: 29 unittest-style tests plus 1 pytest smoke test.

## Findings

### 1. Medium: `roadmap/app-validation-checklist.md` omits the Python `cardid` regression file from its explicit regression command

Evidence:

- The checklist explicit Python command at `roadmap/app-validation-checklist.md:20-22` does not include `tests_pyqt/test_cardid_preset_unittest.py`.
- The missing file exists and contains 3 tests at `tests_pyqt/test_cardid_preset_unittest.py:17-69`.
- The checklist command ran `20` tests; full unittest discovery ran `23` tests. The delta matches the 3 `cardid` tests.
- `roadmap/app-delivery-phases.md:46-50` already includes `tests_pyqt/test_cardid_preset_unittest.py`, so the repo currently has two conflicting Python regression runbooks.

Impact:

- A maintainer following the checklist gets a green Python regression result without exercising the `cardid.txt` preset safety path.
- The drift is documentation-level, not implementation-level; the tests themselves are present and passing.

### 2. Medium: the documented C# “fast parity/safety gate” skips the entire `SavePatchRegressionTests` class

Evidence:

- The fast gate command is documented at `roadmap/app-validation-checklist.md:25-26` and repeated at `roadmap/app-delivery-phases.md:47-48`.
- That filtered run passed `12/12`; the full C# suite passed `22/22`.
- `OnslaughtCareerEditor.UiTests/SavePatchRegressionTests.cs:11-320` contains 9 regression tests covering save-patch correctness, including:
  - level-rank indexing at `:78-123`
  - invalid `--level-rank` handling at `:125-148`
  - `--copy-options-from` conflict guard at `:150-178`
  - in-place write guard at `:180-209`
  - packed binding fallback parsing at `:211-234`
  - goodie slot 232 / reserved-slot preservation at `:236-280`
  - kill meta preservation at `:282-320`
- Those tests are not part of the 12-test filtered gate.

Impact:

- The repo’s “fast parity/safety gate” does not currently cover the main save-patch regression class, even though its name implies it should.
- This is not a red build issue; it is a runbook-scope issue.

### 3. Medium: the checked-in C# proof artifact is stale and no longer representative

Evidence:

- `OnslaughtCareerEditor.UiTests/TestResults/ui-tests.trx:2-3` is dated `2026-03-02`.
- `OnslaughtCareerEditor.UiTests/TestResults/ui-tests.trx:65-70` reports `total="8"` and `discovered 8 of 8`.
- Current source has 22 C# tests, and the live run on 2026-03-05 passed all 22.
- Release docs already classify this family as excluded at `release/readiness/redaction_notes.md:13-14`.

Impact:

- `ui-tests.trx` should not be treated as current proof of validation status.
- This is a proof-artifact hygiene issue, not a release-packaging blocker, because release docs already exclude it.

### 4. Medium: Python/C# validation runbooks are fragmented enough that “green” means different things depending on which doc you follow

Evidence:

- `roadmap/app-validation-checklist.md:20-26` uses an explicit Python unittest list plus a separate pytest smoke command.
- `roadmap/app-delivery-phases.md:46-50` uses a different explicit Python unittest list and the same C# fast filter.
- `RELEASE_SCOPE_AND_TEST_COMMANDS.md:137-156` recommends `py -m pytest -q tests_pyqt` in PowerShell, but the WSL section only runs `python3 -m unittest discover ...` and does not run the PyQt smoke test.
- `release/readiness/LOCAL_SIGNOFF_COMMANDS.md:47-57` also uses `py -m pytest -q tests_pyqt` as the single Python gate.

Impact:

- Shell choice and document choice change what actually gets exercised.
- The repo has enough tests to support a cleaner canonical gate, but the docs are not converged yet.

## Coverage gaps still open

These are not doc mismatches; they are genuine test-depth gaps relative to current implementation and stated priorities.

### Automated coverage present

- C# save-patch correctness and safety regressions: `OnslaughtCareerEditor.UiTests/SavePatchRegressionTests.cs`
- C# read-only CLI and options-file safety: `OnslaughtCareerEditor.UiTests/CliReadOnlyAndOptionsSafetyTests.cs`
- C# binary patch + `cardid` core flows: `OnslaughtCareerEditor.UiTests/BinaryPatchRegressionTests.cs`
- WPF shell smoke for tab structure only: `OnslaughtCareerEditor.UiTests/SmokeTests.cs`
- Python save-patch regressions: `tests_pyqt/test_save_patch_regressions_unittest.py`
- Python CLI read-only / validation / goodie parity: `tests_pyqt/test_cli_readonly_modes_unittest.py`, `tests_pyqt/test_cli_validation_unittest.py`, `tests_pyqt/test_cli_goodie_list_unittest.py`
- Python binary patch + `cardid` core flows: `tests_pyqt/test_binary_patches_unittest.py`, `tests_pyqt/test_cardid_preset_unittest.py`
- Python GUI default-state checks: `tests_pyqt/test_save_editor_defaults_unittest.py` (currently skipped here because `PyQt6` is absent)
- PyQt shell smoke: `tests_pyqt/test_smoke.py` (not runnable here because `pytest` is absent)

### Important gaps

- No automated success-path verification for `--copy-options-from`; only the failure-path conflict is covered in C# and Python (`OnslaughtCareerEditor.UiTests/SavePatchRegressionTests.cs:150-178`, `tests_pyqt/test_cli_validation_unittest.py:50-76`).
- No automated coverage for keybind override writes (`--bind-*`) even though the product priority explicitly calls out keybind coverage in `WHAT_WE_CAN_DO_NOW.md:18`.
- No automated coverage for save/options discovery commands (`--list-saves`, `--set-game-dir`, `--show-config`) even though they are documented in `README.MD:46-55`.
- No automated line-by-line parity assertion for analyze/compare output formatting; current tests mostly check markers and summary parity, which matches the still-open debt in `roadmap/technical-debt.md:22-34`.
- Manual GUI signoff expects much more than current UI automation covers. `release/readiness/LOCAL_SIGNOFF_COMMANDS.md:67-70` expects real Save Editor/Configuration Editor/Binary Patches/Lore workflows, while the only WPF UI automation currently checks tab presence and nested-tab names in `OnslaughtCareerEditor.UiTests/SmokeTests.cs:16-116`.
- No committed Python-side proof artifact equivalent to the tracked C# `.trx`; Python validation evidence is console-only right now.

## Bottom line

- Implementation status is healthier than the stale proof artifact suggests: C# full suite is green at `22/22`, and Python unittest coverage is green at `23` discovered tests with one PyQt-dependent skip.
- The main problems are runbook drift and incomplete gate definitions, not failing tests.
- The two highest-value doc fixes would be:
  - unify the Python regression command set so every runbook includes the same files
  - replace or relabel the C# fast filter so it is honest about excluding `SavePatchRegressionTests`, or expand it to include that class
