# Lane 07/10 Test Runbook Accuracy Audit (Read-Only)

Date: 2026-03-04
Context: WSL shell at `redacted-private-source`

## Environment Verification (Executed)

- `python3 --version` -> `Python 3.12.3`
- `py --version` -> `command not found`
- `dotnet --version` -> `command not found`
- `"/mnt/c/Program Files/dotnet/dotnet.exe" --version` -> `10.0.200-preview.0.26103.119`
- `python3 -m pip install -r requirements.txt` -> `/usr/bin/python3: No module named pip`
- `pytest -q tests_pyqt` -> `command not found`
- `python3 -m pytest -q tests_pyqt/test_smoke.py` -> `No module named pytest`
- `python3 -m unittest ...` (roadmap command list) -> `OK (skipped=1)`
- `"${DOTNET_EXE:-/mnt/c/Program Files/dotnet/dotnet.exe}" build "Onslaught - Career Editor.sln"` -> succeeds
- `"/mnt/c/Program Files/dotnet/dotnet.exe" test ... --filter "Name~CliReadOnly|Name~OptionsFile|Name~BinaryPatch"` -> Passed (9/9)
- `"/mnt/c/Program Files/dotnet/dotnet.exe" test OnslaughtCareerEditor.UiTests/OnslaughtCareerEditor.UiTests.csproj` -> Passed (19/19)

## Findings (Stale/Missing Caveats)

### 1) HIGH - Missing bootstrap caveat for `pip` in validation runbook
- `roadmap/app-validation-checklist.md:11` requires `python3 -m pip install -r requirements.txt` but does not warn that `pip` itself may be missing on WSL base Python installs.
- In this environment, that exact command fails before dependency installation can begin.
- Impact: blocks the documented test bootstrap path (`pytest`, `pytest-qt`, `PyQt6` cannot be installed).

### 2) MEDIUM - README build/run commands assume `dotnet` on PATH in WSL
- `README.MD:115` and `README.MD:116` use bare `dotnet` invocation.
- In this environment, `dotnet` is not on Linux PATH, but Windows `dotnet.exe` exists and works.
- Missing caveat: WSL users may need explicit `DOTNET_EXE`/full path invocation.

### 3) MEDIUM - AGENTS quick-start WSL note is not wired into commands
- `AGENTS.md:28` notes optional WSL `DOTNET_EXE`, but `AGENTS.md:29-32` still execute bare `dotnet` commands.
- In this environment, those commands fail unless changed to explicit path or variable-aware invocation.
- Supporting code evidence: test suites already support `DOTNET_EXE` fallback logic (`OnslaughtCareerEditor.UiTests/SavePatchRegressionTests.cs:418-427`, `OnslaughtCareerEditor.UiTests/CliReadOnlyAndOptionsSafetyTests.cs:209-219`, `tests_pyqt/test_cli_goodie_list_unittest.py:23-35`).

### 4) MEDIUM - Checklist skip policy omits expected Python UI skip modes
- `roadmap/app-validation-checklist.md:29-32` allows UI skips only for WPF build output/desktop session caveats.
- But Python UI tests intentionally skip for missing PyQt/display:
  - `tests_pyqt/test_smoke.py:6` (`importorskip("PyQt6")`)
  - `tests_pyqt/test_smoke.py:16-17` (skip when no GUI display)
  - `tests_pyqt/test_save_editor_defaults_unittest.py:13-15` (skip when PyQt6 unavailable)
- Impact: current checklist can misclassify legitimate Python UI skips as unexpected failures.

### 5) LOW - `pytest` entrypoint wording is less robust than module form
- `AGENTS.md:370` uses `pytest -q tests_pyqt`.
- In this environment, `pytest` entrypoint is absent even though `python3` is present.
- More portable runbook form is `python3 -m pytest ...` (already used in `roadmap/app-validation-checklist.md:19`).

## No-Finding Notes

- `tools/release_package.sh`: no stale/missing caveats related to test-runbook command accuracy were identified.
- Test code in `OnslaughtCareerEditor.UiTests/*.cs` and `tests_pyqt/*.py` generally encodes expected environment fallbacks/skips correctly; main drift is documentation alignment.
