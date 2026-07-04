# Lane 05 - CLI Parity Implementation Cards

Derived from `subagents/depth2/lane05_cli_parity_validation.md` and direct source validation in `Program.cs` / `patcher.py`.

## Card CLI-01 - Add Python `--version` Option Parity
Priority: P1
Severity: Medium
Category: Option parity

Problem:
- C# CLI exposes `--version` via `System.CommandLine` help surface (`Program.cs` help output).
- Python CLI rejects `--version` as unrecognized (`patcher.py` currently has no version argument).

Implementation scope:
- File: `patcher.py`
- Add explicit version flag in argparse setup near other top-level options:
  - `parser.add_argument('--version', action='version', version='<shared version string>')`
- Source of truth for version string must be deterministic and testable:
  - Preferred: reuse the same string already used by the C# app packaging/build metadata.
  - Minimum acceptable: repo-local constant in `patcher.py` with a follow-up task to centralize.

Acceptance criteria:
1. `python3 patcher.py --version` exits `0`.
2. Output is a single version line (no usage dump, no traceback).
3. C# and Python both support `--version` without parse errors.

Verification commands:
- `python3 patcher.py --version`
- `"/mnt/c/Program Files/dotnet/dotnet.exe" run --project "Onslaught - Career Editor.csproj" -- --version`
- `tmp_py=$(mktemp); tmp_cs=$(mktemp); python3 patcher.py -h > "$tmp_py"; "/mnt/c/Program Files/dotnet/dotnet.exe" run --project "Onslaught - Career Editor.csproj" -- --help > "$tmp_cs"; rg -o -- '--[a-z0-9][a-z0-9-]*' "$tmp_py" | sort -u > /tmp/py_opts.txt; rg -o -- '--[a-z0-9][a-z0-9-]*' "$tmp_cs" | sort -u > /tmp/cs_opts.txt; comm -13 /tmp/py_opts.txt /tmp/cs_opts.txt`
Expected: no meaningful option gap for `--version` (ignore wrapped-token artifacts).

## Card CLI-02 - Align Numeric Arg Validation Stage (`--controller-config-*`)
Priority: P1
Severity: Medium
Category: Error/help alignment

Problem:
- C# rejects invalid negative values at parse-time because options are typed as `uint?` (`Program.cs:219-225`).
- Python accepts `int` parse and fails later during patching (`patcher.py:1693-1696`, `patcher.py:748-756`), creating mismatched error timing and mixed stdout/stderr contracts.

Implementation scope:
- File: `patcher.py`
- Replace `type=int` on:
  - `--controller-config-p1`
  - `--controller-config-p2`
- Use a dedicated argparse type validator (for example `parse_uint32_arg`) that raises `argparse.ArgumentTypeError` unless value is `0..0xFFFFFFFF`.
- Keep the lower-level guard in `patch_file` as a defensive invariant, but normal CLI path should fail at parse-time.

Acceptance criteria:
1. Python rejects `--controller-config-p1 -1` during parse with non-zero exit.
2. Python does not emit patch configuration preamble for this parse-time failure.
3. Error/help flow is stage-aligned with C# for this class of invalid numeric input.

Verification commands:
- `set -o pipefail; python3 patcher.py [private-save-fixture] /tmp/out_py_cfg_fail.bes --controller-config-p1 -1 2>&1 | sed -n '1,40p'; echo "[rc=$?]"`
- `set -o pipefail; "/mnt/c/Program Files/dotnet/dotnet.exe" run --project "Onslaught - Career Editor.csproj" -- "[private-save-fixture]" "C:\\Temp\\out_cs_cfg_fail.bes" --controller-config-p1 -1 2>&1 | sed -n '1,40p'; echo "[rc=$?]"`
Expected: both fail before patch execution; Python no longer prints patch preamble on this input.

## Card CLI-03 - Remove Failure-Path Stdout Preamble Drift
Priority: P0
Severity: High
Category: Output-contract delta

Problem:
- Python prints patch configuration block before certain fatal validation exits (notably `--copy-options-from` combined with both `--no-copy-*` flags; see `patcher.py:2036-2101` then fail at `patcher.py:2090-2097`).
- C# fails cleanly with stderr-only message before patch summary output (`Program.cs:732-747`).

Implementation scope:
- File: `patcher.py`
- Reorder validation so all fatal patch-mode argument checks run before any user-facing patch configuration stdout block.
- Specifically ensure these checks happen before the first `print("Onslaught Career Editor - CLI Mode")` line:
  - copy-options conflict (`--copy-options-from` + both `--no-copy-options-entries` and `--no-copy-options-tail`)
  - any other fatal patch-mode validation currently after preamble

Acceptance criteria:
1. On copy-options conflict, Python exits non-zero with error in stderr.
2. On that failure path, stdout is empty (or at least contains no configuration banner/section).
3. Existing successful patch output remains unchanged.

Verification commands:
- `tmp=$(mktemp /tmp/onslaught-in-XXXXXX.bes); cp [private-save-fixture] "$tmp"; set -o pipefail; python3 patcher.py "$tmp" /tmp/out_py_copy_fail.bes --copy-options-from "$tmp" --no-copy-options-entries --no-copy-options-tail > /tmp/py_stdout.txt 2> /tmp/py_stderr.txt; rc=$?; echo "rc=$rc"; wc -l /tmp/py_stdout.txt; sed -n '1,20p' /tmp/py_stderr.txt; rm -f "$tmp"`
- `"/mnt/c/Program Files/dotnet/dotnet.exe" test OnslaughtCareerEditor.UiTests/OnslaughtCareerEditor.UiTests.csproj --filter "Name~Cli_CopyOptionsFromWithBothNoCopyFlags_FailsAndDoesNotWriteOutput"`
- `python3 -m unittest -v tests_pyqt.test_cli_validation_unittest`
Expected: Python failure contract mirrors C# behavior (no preamble on fatal validation).

## Card CLI-04 - Define Shared Read-Only Output Contract Markers (`--analyze`, `--compare`)
Priority: P1
Severity: Medium
Category: Output-contract delta

Problem:
- Both CLIs are semantically correct for analyze/compare, but textual formatting differs (headings/line wording/line counts), creating parser fragility.

Implementation scope:
- Files:
  - `Program.cs`
  - `patcher.py`
  - `tests_pyqt/test_cli_readonly_modes_unittest.py` (new)
  - `OnslaughtCareerEditor.UiTests/CliReadOnlyParityTests.cs` (new)
- Establish a minimal required marker set that both CLIs must emit for read-only paths (exact strings, not full-line-by-line identity), e.g.:
  - Analyze markers: `SAVE FILE ANALYSIS`, `FILE VALIDATION`, `MISSION NODES`, `LINKS`, `GOODIES`, `KILL COUNTS`
  - Compare markers: `FILE COMPARISON`, `Total differing bytes:`
- Update formatters only as needed to guarantee these markers persist across both runtimes.

Acceptance criteria:
1. Both CLIs pass marker-based contract tests for `--analyze` and `--compare`.
2. Identical-file compare still reports `Total differing bytes: 0` and `Files are identical!`.
3. Contract tests are independent of host-specific config paths.

Verification commands:
- `python3 -m unittest -v tests_pyqt.test_cli_readonly_modes_unittest`
- `"/mnt/c/Program Files/dotnet/dotnet.exe" test OnslaughtCareerEditor.UiTests/OnslaughtCareerEditor.UiTests.csproj --filter "Name~Cli_Analyze_Or_Name~Cli_Compare"`
- `tmp1=$(mktemp /tmp/onslaught-a-XXXXXX.bes); tmp2=$(mktemp /tmp/onslaught-b-XXXXXX.bes); cp [private-save-fixture] "$tmp1"; cp [private-save-fixture] "$tmp2"; python3 patcher.py --compare "$tmp1" "$tmp2" | rg -n "FILE COMPARISON|Total differing bytes: 0|Files are identical!"; rm -f "$tmp1" "$tmp2"`

## Card CLI-05 - Normalize Compare Missing-File Error Wording
Priority: P2
Severity: Low
Category: Error/help alignment

Problem:
- Missing compare file text differs (`Compare file not found` in C# vs `Comparison file not found` in Python).
- Semantics are same, but wording drift complicates strict cross-runtime error assertions.

Implementation scope:
- Files:
  - `Program.cs` (`ExecuteCli` compare branch)
  - `patcher.py` (compare branch)
  - corresponding CLI regression tests in both stacks
- Standardize one canonical error string and use it in both CLIs.

Acceptance criteria:
1. Both CLIs return non-zero when compare target is missing.
2. Both emit the same canonical error phrase in stderr.

Verification commands:
- `set -o pipefail; python3 patcher.py [private-save-fixture] --compare /tmp/does-not-exist-compare.bes 2>&1 | sed -n '1,20p'; echo "[rc=$?]"`
- `set -o pipefail; "/mnt/c/Program Files/dotnet/dotnet.exe" run --project "Onslaught - Career Editor.csproj" -- "[private-save-fixture]" --compare "C:\\Temp\\does-not-exist-compare.bes" 2>&1 | sed -n '1,20p'; echo "[rc=$?]"`
- `python3 -m unittest -v tests_pyqt.test_cli_validation_unittest`
- `"/mnt/c/Program Files/dotnet/dotnet.exe" test OnslaughtCareerEditor.UiTests/OnslaughtCareerEditor.UiTests.csproj --filter "Name~Cli_Compare"`
