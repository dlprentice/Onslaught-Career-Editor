# Canonical Docs Contradictions / Stale Claims (Depth 2, Lane 01)

## Severity-Ranked Findings

### 1) HIGH - `roadmap/gui-expansion.md` claims Python Binary Patches parity is still pending, but code has shipped parity
- Stale claim: `roadmap/gui-expansion.md:70`
- Conflicting docs: `roadmap/ROADMAP-INDEX.md:12`, `roadmap/csharp-python-parity.md:17`
- Code reality: `onslaught/gui/main_window.py:22`, `onslaught/gui/main_window.py:104`, `onslaught/gui/main_window.py:106`, `MainWindow.xaml:83`, `tests_pyqt/test_smoke.py:30`
- Why this matters: this can send contributors to re-open already-complete parity work instead of current polish/reliability tasks.
- Concrete correction text:

```md
**Status (Mar 2026):** Save Editor, Save Analyzer, Configuration Editor, Lore Browser, media tabs, Settings, and Binary Patches are implemented in both WPF and PyQt. Current work is UX polish, reliability hardening, and regression depth.
```

### 2) MEDIUM - `roadmap/gui-expansion.md` project-structure block is stale vs current repo layout
- Stale structure block: `roadmap/gui-expansion.md:37`, `roadmap/gui-expansion.md:50`, `roadmap/gui-expansion.md:51`, `roadmap/gui-expansion.md:54`, `roadmap/gui-expansion.md:55`, `roadmap/gui-expansion.md:57`
- Code reality (active modules): `onslaught/core/binary_patches.py:1`, `onslaught/gui/tabs/settings.py:1`, `onslaught/gui/tabs/binary_patches.py:1`, `onslaught/gui/widgets/__init__.py:6`
- Why this matters: newcomers get a misleading mental model (missing active modules, references to nonexistent widget files/directories).
- Concrete correction text:

```md
Replace the "Project Structure" snippet with a minimal current tree that includes:
- `onslaught/core/binary_patches.py`
- `onslaught/gui/tabs/settings.py`
- `onslaught/gui/tabs/binary_patches.py`
- `onslaught/gui/widgets/save_selector.py`

Also remove placeholder entries that are not present in the repo (for example `hex_viewer.py`, `media_controls.py`, and `onslaught/data/icons/` if they remain absent).
```

### 3) MEDIUM - Validation gate docs omit active Binary Patches regression coverage
- Stale commands: `roadmap/app-validation-checklist.md:18`, `roadmap/app-delivery-phases.md:48`
- Missing active test module: `tests_pyqt/test_binary_patches_unittest.py:6`, `tests_pyqt/test_binary_patches_unittest.py:22`, `tests_pyqt/test_binary_patches_unittest.py:57`
- Feature under test is active UI surface: `onslaught/gui/main_window.py:104`, `MainWindow.xaml:83`
- Why this matters: phase/checklist runs can pass without exercising a shipped parity-critical feature.
- Concrete correction text:

```md
Update Python unittest gate commands to include binary-patch regression coverage:

python3 -m unittest \
  tests_pyqt/test_save_patch_regressions_unittest.py \
  tests_pyqt/test_cli_goodie_list_unittest.py \
  tests_pyqt/test_cli_validation_unittest.py \
  tests_pyqt/test_save_editor_defaults_unittest.py \
  tests_pyqt/test_binary_patches_unittest.py
```

## Scan Note
No material contradictions were found in `AGENTS.md`, `README.MD`, or `CURRENT_CAPABILITIES.md` during this pass; the actionable drift was concentrated in `roadmap/*`.
