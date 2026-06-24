## Summary
- Automated coverage exists across three surfaces: C# NUnit/FlaUI, Python `unittest`, and Python `pytest`+`pytest-qt`.
- Current suite is strongest on save patching regressions (offset correctness, boundary preservation, CLI validation) and basic UI shell smoke checks.
- High-risk functionality is still untested: analyze/compare flows, config commands (`--list-saves`, `--set-game-dir`, `--show-config`), `.bea` safety guard behavior, and keybind override integration.

## Existing Tests
### C# (`OnslaughtCareerEditor.UiTests`, NUnit + FlaUI)
- `OnslaughtCareerEditor.UiTests/SmokeTests.cs` (1 test)
  - Validates top-level tabs and nested Saves/Media tab labels are present in the WPF app UI.
- `OnslaughtCareerEditor.UiTests/SavePatchRegressionTests.cs` (9 tests)
  - Validates patch-file tail setting offsets and boolean polarity.
  - Validates `--level-rank 1:S` targets node index 0 (not 1).
  - Validates invalid `--level-rank` is fatal and output is not written.
  - Validates conflicting `--copy-options-from` flags are fatal.
  - Validates in-place patching guard rejects same input/output path.
  - Validates keyboard fallback token parsing + formatting round-trip.
  - Validates goodies boundary behavior: slot 232 patched, reserved 233-299 preserved.
  - Validates kill patch preserves high-byte metadata while updating lower 24-bit payload.

### Python `unittest` (`tests_pyqt`)
- `tests_pyqt/test_save_patch_regressions_unittest.py` (4 tests)
  - Mirrors core save patch regressions: tail settings offsets/polarity, level-rank parser 1-based input to 0-based internal mapping, goodies boundary, kill-meta preservation.
- `tests_pyqt/test_save_editor_defaults_unittest.py` (4 tests)
  - Validates `SaveEditorTab` safe defaults for save mode and configuration mode.
  - Validates copy-options controls default/enabled state transitions when source path is set/cleared.
- `tests_pyqt/test_cli_validation_unittest.py` (2 tests)
  - Validates fatal CLI validation paths: invalid `--level-rank`, conflicting `--copy-options-*` flags.
- `tests_pyqt/test_cli_goodie_list_unittest.py` (5 tests)
  - Validates Python and C# `--list-goodies` output modes (default hides reserved, `--show-reserved-goodies` includes reserved).
  - Validates summary parity between Python and C# goodie list output.
- `tests_pyqt/test_binary_patches_unittest.py` (2 tests)
  - Validates Python core binary patch apply/backup/restore roundtrip.
  - Validates apply aborts on unexpected bytes and does not create backup.

### Python `pytest` / `pytest-qt`
- `tests_pyqt/test_smoke.py` (1 test)
  - Validates PyQt main window top-level and nested tab labels.
  - Uses `qtbot` and skips when no GUI display is available.

## Coverage Matrix
| Area | C# NUnit/FlaUI | Python `unittest` | Python `pytest`/qt | Notes |
|---|---|---|---|---|
| Main window tab shell | Yes | No | Yes | Both stacks have UI tab smoke checks. |
| Save patch tail settings offsets/polarity | Yes | Yes | No | Good cross-stack regression coverage. |
| Goodies boundary/reserved preservation | Yes | Yes | No | Explicit slot 232 + reserved slots verified. |
| Kill meta-byte preservation | Yes | Yes | No | Protects packed high-byte metadata semantics. |
| Level-rank semantics | Yes | Yes | No | C# covers CLI end-to-end; Python covers parser semantics + CLI validation. |
| CLI fatal validation paths | Yes | Yes | No | Invalid args and copy-options conflict covered. |
| Goodie list output/parity (Python vs C#) | Indirect (via Python launcher) | Yes | No | Strong parity check for summary and reserved visibility behavior. |
| Binary patch apply/restore | No | Yes | No | Only Python core patch engine is tested. |
| SaveEditor defaults/safe toggles | No | Yes | No | PyQt tab state defaults covered. |
| Config commands (`--list-saves`, `--set-game-dir`, `--show-config`) | No | No | No | Uncovered in all automated suites. |
| Analyze/compare modes (`--analyze`, `--compare`, `--dump-mystery`) | No | No | No | Uncovered in all automated suites. |

## Gaps
1. Critical CLI read-only modes are untested.
- No automated assertions for `--analyze`, `--compare`, and `--dump-mystery` behavior/exit codes on either stack.
- These are core user workflows and should have golden-output or structural output tests.

2. Config/discovery commands are untested.
- No tests for `--list-saves`, `--set-game-dir`, `--show-config` and underlying config persistence/migration logic (`AppConfig.cs`, `onslaught/core/config.py`).
- Risk: path detection regressions, config schema drift, and platform-specific discovery breakage.

3. `.bea` safety guard behavior is untested.
- No tests asserting career-section patching is blocked for options files unless explicitly overridden.
- This is a safety-critical guard against accidental corruption.

4. Keybind override integration is untested.
- Only token parsing fallback is covered; no end-to-end tests for `--bind-*` options writing options entries correctly or forcing expected control scheme behavior.

5. C# binary patch path has no automated tests.
- C# `Views/BinaryPatchesView.xaml.cs` duplicates patch spec/verification/apply/restore logic, but tests only exist for Python `onslaught/core/binary_patches.py`.
- Risk: cross-stack drift in offsets/specs and mismatch handling.

6. Per-category kills and settings override edge cases are largely untested.
- No explicit tests for `--aircraft-kills/--vehicle-kills/...` combinations, tri-bool parser invalid values (`on/off/...`), volume range handling, or controller config edge values.

7. UI automation reliability is environment-gated.
- FlaUI and Qt smoke tests can skip when desktop/display prerequisites are missing, so regressions can pass unnoticed unless runners guarantee interactive GUI availability.

8. Runbook/test-command coverage mismatch.
- `roadmap/app-validation-checklist.md` lists a subset of Python `unittest` modules and omits `tests_pyqt/test_binary_patches_unittest.py`, so that critical suite may be missed in routine runs.
