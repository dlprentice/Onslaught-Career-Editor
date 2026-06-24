# Lane 01 - Canonical App Docs Audit (Read-Only)

Date: 2026-03-04
Scope: `README.MD`, `CURRENT_CAPABILITIES.md`, `roadmap/status-current.md`, `roadmap/app-delivery-phases.md`, `roadmap/app-validation-checklist.md`

## Findings (Severity Ordered)

1. **Medium - "Parity" wording is too strong for current Configuration Editor defaults/backup behavior across WPF vs PyQt**
- Doc claims:
  - `README.MD:21`
  - `CURRENT_CAPABILITIES.md:22`
  - `CURRENT_CAPABILITIES.md:23`
  - `roadmap/status-current.md:21`
- Code reality:
  - WPF Configuration Editor defaults output to input path and allows in-place patching with timestamped `.bak` backup:
    - `Views/SaveEditorView.xaml.cs:689`
    - `Views/SaveEditorView.xaml.cs:692`
    - `Views/SaveEditorView.xaml.cs:1998`
    - `Views/SaveEditorView.xaml.cs:2007`
    - `Views/SaveEditorView.xaml.cs:950`
    - `Views/SaveEditorView.xaml.cs:1004`
    - `Views/SaveEditorView.xaml.cs:1009`
  - PyQt Configuration Editor defaults to `<input>_patched` and blocks same-path patching (no in-place `.bak` flow):
    - `onslaught/gui/tabs/save_editor.py:645`
    - `onslaught/gui/tabs/save_editor.py:647`
    - `onslaught/gui/tabs/save_editor.py:705`
    - `onslaught/gui/tabs/save_editor.py:710`
    - `onslaught/gui/tabs/save_editor.py:1073`
    - `onslaught/gui/tabs/save_editor.py:1074`
- Why this is stale/inaccurate:
  - The docs communicate broad WPF/PyQt "parity active" for core workflows, but defaults/backup semantics for Configuration Editor are materially different between stacks.

2. **Low - Binary patch helper script path is documented ambiguously/inaccurately**
- Doc claim:
  - `CURRENT_CAPABILITIES.md:46` references `patch_display_mode_flow.py` without path.
- Code/filesystem reality:
  - Actual script location is `patches/patch_display_mode_flow.py` (no repo-root `patch_display_mode_flow.py`).
- Impact:
  - Copy/paste from docs can fail unless users prepend `patches/`.

## Checked And Currently Accurate (No Drift Found)

- Active WPF tabs match documented core set and shelved status for Goodie/Asset viewers:
  - `MainWindow.xaml:65`
  - `MainWindow.xaml:70`
  - `MainWindow.xaml:73`
  - `MainWindow.xaml:76`
  - `MainWindow.xaml:82`
  - `MainWindow.xaml:87`
  - `MainWindow.xaml:90`
  - `MainWindow.xaml:96`
  - `MainWindow.xaml:100`
  - `MainWindow.xaml:104`
- Active PyQt tabs match documented core set and shelved status for Goodie/Asset viewers:
  - `onslaught/gui/main_window.py:74`
  - `onslaught/gui/main_window.py:78`
  - `onslaught/gui/main_window.py:82`
  - `onslaught/gui/main_window.py:91`
  - `onslaught/gui/main_window.py:96`
  - `onslaught/gui/main_window.py:102`
  - `onslaught/gui/main_window.py:106`
  - `onslaught/gui/main_window.py:111`
- CLI read-only modes and safety flags (`--analyze`, `--compare`, `--list-goodies`, `--show-reserved-goodies`, options-copy safety checks) are present in both stacks per docs.
- Binary patch verify/apply/restore with `.original.backup` behavior is implemented in both WPF and PyQt stacks.
