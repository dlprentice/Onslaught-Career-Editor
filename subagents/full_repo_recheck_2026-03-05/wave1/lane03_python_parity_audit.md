# Lane 03 Python Parity Audit

## Findings

1. High - PyQt startup `--file` handling is broken for `.bea` workflows and does not reliably focus the Saves shell.
Evidence: `onslaught_explorer.py:6-9` advertises `--file defaultoptions.bea`, but `onslaught_explorer.py:63-70` always sends the file to `window.save_editor_tab` and then calls `window.tabs.setCurrentWidget(window.save_editor_tab)`. The top-level tab host only contains `save_tabs`, `media_tabs`, `lore_browser_tab`, `binary_patches_tab`, and `settings_tab` (`onslaught/gui/main_window.py:70-111`), so that focus call targets the wrong widget. The correct `.bea` routing already exists in the menu path, which switches to `config_editor_tab` and then selects the nested Saves tab (`onslaught/gui/main_window.py:174-189`).
Impact: `python3 onslaught_explorer.py --file defaultoptions.bea` does not honor its documented usage, and any startup-opened file can stay hidden if the persisted top-level tab is not `Saves`.

2. Medium - PyQt `Tools > Compare Files...` is still weaker than the WPF implementation even though the parity doc marks the shell/menu lane complete.
Evidence: the PyQt handler only switches to the analyzer tab and shows a status prompt (`onslaught/gui/main_window.py:207-212`). The WPF handler opens both file dialogs and executes the compare immediately through `TryCompareFiles` (`MainWindow.xaml.cs:270-295`). The parity doc currently says `Main Shell Menu/Status` is `COMPLETE` and that `Compare functionality` is implemented (`roadmap/csharp-python-parity.md:19`, `roadmap/csharp-python-parity.md:130`, `roadmap/csharp-python-parity.md:217`).
Impact: the current Python menu flow is not equivalent to the C# lead implementation, and the docs overstate parity on an active user-facing workflow.

3. Medium - CLI/version parity is internally inconsistent, and the current docs overstate alignment.
Evidence: the Python CLI exposes `--version` (`patcher.py:1657-1658`) but hardcodes `1.0.0` in `get_cli_version()` (`patcher.py:1586-1603`), while the shared app constant is `2.0.0` (`onslaught/core/constants.py:146-149`) and the PyQt GUI prints that newer version (`onslaught_explorer.py:27-39`). The Python regression suite also locks in the stale `1.0.0` output (`tests_pyqt/test_cli_readonly_modes_unittest.py:24-27`). On the C# side, `BuildRootCommand()` defines the CLI flags but there is no `--version` option anywhere in the command surface (`Program.cs:85-340`). The parity doc still claims `CLI` is `COMPLETE` and that both CLIs support `--version` (`roadmap/csharp-python-parity.md:11`, `roadmap/csharp-python-parity.md:172-177`).
Impact: automation, release notes, and user support will get conflicting version answers depending on which entry point is used, and the parity doc currently misstates the real CLI surface.

4. Low - The Python regression lane does not cover the startup-open path or the menu-level compare flow, so the active GUI parity drift above is currently unguarded.
Evidence: the PyQt smoke test only asserts tab presence (`tests_pyqt/test_smoke.py:15-45`), and the CLI read-only tests stay on command-line behaviors (`tests_pyqt/test_cli_readonly_modes_unittest.py:23-49`). There is no GUI regression covering `onslaught_explorer.py --file ...` or `MainWindow._on_compare()`.
Impact: the two user-visible GUI issues above can persist without failing the current Python validation checklist.

## Scope Notes

- Read-only audit only.
- Active scope only: Python GUI, Python CLI/core, matching C# implementation, and current parity/capability docs.
- Shelved `Goodie Viewer` and `Asset Browser` were intentionally excluded.
