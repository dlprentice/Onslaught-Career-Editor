## Summary

Current binary patching is split into two active lanes:
- Display/windowed byte patches (3 offsets) implemented in both app stacks (WPF + PyQt), plus shared Python core + standalone script.
- Dev-mode goodies logic fix (1 offset) implemented as a standalone script only.

The display/windowed lane is the only lane surfaced in both GUIs:
- WPF tab wiring: `MainWindow.xaml` and `Views/BinaryPatchesView*`.
- PyQt tab wiring: `onslaught/gui/main_window.py` and `onslaught/gui/tabs/binary_patches.py`.

Backup behavior is mostly consistent for display/windowed flows (`BEA.exe.original.backup`) but inconsistent for dev-mode/archive scripts (`BEA.exe.backup`), which creates restore-flow mismatch risk.

## Patch Catalog (current)

### A) Display/windowed patch set (active in WPF, PyQt, Python core, and script)

| Key | File Offset | VA | Before | After | Behavior | Exposure |
|---|---:|---:|---|---|---|---|
| `resolution_gate` | `0x129696` | `0x00529696` | `CC` | `00` | Neutralizes non-4:3 rejection gate in display mode enumeration | WPF + PyQt + `onslaught/core/binary_patches.py` + `patches/patch_display_mode_flow.py` |
| `force_windowed` | `0x12A644` | `0x0052A644` | `A1 F0 2D 66 00` | `B8 01 00 00 00` | Forces startup windowed decision true on windowed-capable path | WPF + PyQt + core + script |
| `skip_auto_toggle` (optional) | `0x12BB97` | `0x0052BB97` | `75 20` | `EB 20` | Skips one startup fullscreen-toggle gate (partial, environment-dependent) | WPF + PyQt + core + script |

Evidence:
- WPF specs: `Views/BinaryPatchesView.xaml.cs:34-54`.
- WPF UX/tooltips: `Views/BinaryPatchesView.xaml:53-77`.
- PyQt/core specs: `onslaught/core/binary_patches.py:32-55` and `onslaught/gui/tabs/binary_patches.py:76-100`.
- Script specs: `patches/patch_display_mode_flow.py:60-81`.
- Canonical script/docs table: `patches/README.md:35-40`.

### B) Dev-mode goodies logic fix (active script; not in GUI tabs)

| Script | File Offset | VA | Before | After | Behavior |
|---|---:|---:|---|---|---|
| `patch_devmode_goodies_logic_fix.py` | `0x5D819` | `0x0045D819` | `F7 D8` | `33 C0` | Forces `g_Cheat_LATETE` write to 0 inside goodies UI path to avoid dev-mode all-cheats side effect |

Evidence:
- Script patch constant: `patches/patch_devmode_goodies_logic_fix.py:52-59`.
- Script technical details: `patches/patch_devmode_goodies_logic_fix.py:18-24`.
- README status + rationale: `patches/README.md:51-73`.

### C) Archived / do-not-use patch scripts (present but not current)

- `patches/archive/patch_ischeatactive_always_true_BROKEN.py` (explicitly broken; goodies lock).
- `patches/archive/patch_ischeatactive_return_path_bypass.py` (legacy partial behavior).
- Marked archived in `patches/README.md:74-117`.

### D) Backup semantics (current behavior)

| Flow | Backup Filename | Creation Rule | Restore Rule |
|---|---|---|---|
| WPF Binary Patches tab | `BEA.exe.original.backup` | Created once if absent, only when apply proceeds | Restore button copies backup over target after confirmation |
| PyQt Binary Patches tab + core | `BEA.exe.original.backup` | Created once if absent, only when apply proceeds | Restore uses same file via core helper |
| `patch_display_mode_flow.py` | `BEA.exe.original.backup` | Created once if absent | `--restore` copies it back |
| `patch_devmode_goodies_logic_fix.py` | `BEA.exe.backup` | Created once if absent | `--restore` expects `.exe.backup` |
| Archive scripts | `BEA.exe.backup` | Created once if absent | `--restore` expects `.exe.backup` |

Evidence:
- WPF suffix + apply/restore: `Views/BinaryPatchesView.xaml.cs:17`, `283-287`, `324-353`.
- PyQt/core suffix + apply/restore: `onslaught/core/binary_patches.py:14`, `124-149`; UI wiring `onslaught/gui/tabs/binary_patches.py:239-260`.
- Display script suffix + restore: `patches/patch_display_mode_flow.py:48`, `142-170`.
- Dev-mode script suffix + restore: `patches/patch_devmode_goodies_logic_fix.py:64`, `130-141`.
- README safety note on suffix mismatch: `patches/README.md:208-212`.

## Tooling Map

### App surfaces

| Component | File(s) | Purpose |
|---|---|---|
| WPF tab host | `MainWindow.xaml:83-85` | Adds top-level `Binary Patches` tab and mounts `BinaryPatchesView` |
| WPF patch UI + engine-in-view | `Views/BinaryPatchesView.xaml`, `Views/BinaryPatchesView.xaml.cs` | Select/verify/apply/restore for display/windowed patch set |
| PyQt tab host | `onslaught/gui/main_window.py:104-107` | Adds top-level `Binary Patches` tab |
| PyQt tab UI | `onslaught/gui/tabs/binary_patches.py` | UI shell for same 3 display/windowed patch specs |
| PyQt shared core | `onslaught/core/binary_patches.py` | Canonical Python patch spec/state/apply/restore logic consumed by PyQt + tests |

### Script tooling (`patches/`)

| Script | Status | Scope |
|---|---|---|
| `patches/patch_display_mode_flow.py` | Active | Display/windowed patch set with verify/apply/restore and subset flags |
| `patches/patch_devmode_goodies_logic_fix.py` | Active (advanced/dev-mode only) | Goodies UI logic correction for dev-mode all-cheats path |
| `patches/archive/*.py` | Archived | Historical reference only |
| `patches/README.md` | Canonical script status doc | Operational status, offsets/bytes, and safety notes |

### Docs and asset references

| Type | File | Notes |
|---|---|---|
| Capability status | `CURRENT_CAPABILITIES.md:45-48` | Declares display/windowing + dev-mode script status |
| Parity doc | `lore-book/roadmap/csharp-python-parity.md:17` | States Binary Patches tab parity complete |
| Conflicting old roadmap note | `lore-book/roadmap/gui-expansion.md:70` | Still says Python Binary Patches parity pending (stale) |
| Analysis docs | `reverse-engineering/binary-analysis/windowed-mode-analysis.md`, `reverse-engineering/binary-analysis/widescreen-patch-analysis.md` | Behavior context + offsets/addresses |
| Archival roadmap | `roadmap/executable-modding.md:5-16` | Explicitly archival/non-shipping recommendations |
| Patch asset | `media/patches/battleengineaqulawidescreenfix.zip` | External widescreen patch artifact (reference) |
| Binary artifacts | `BEA_Widescreen.exe`, `BEA.exe.gzf`, `game/BEA.exe` | Patched executable sample, Ghidra DB bundle, base target binary |

### Test coverage map

| Coverage | File | What is covered |
|---|---|---|
| Python patch-core behavior | `tests_pyqt/test_binary_patches_unittest.py:22-78` | Apply/restore roundtrip; mismatch abort; backup creation semantics |
| GUI smoke only (PyQt) | `tests_pyqt/test_smoke.py:30` | Top-level tab presence includes Binary Patches |
| GUI smoke only (WPF) | `OnslaughtCareerEditor.UiTests/SmokeTests.cs:67-70` | Top-level tab presence includes Binary Patches |

## Gaps/Opportunities

1. Backup suffix inconsistency across tools.
- Display/windowed flows use `.original.backup`; dev-mode/archive scripts use `.exe.backup`.
- Opportunity: unify to one suffix or support both in all restore paths to prevent operator confusion.

2. Patch spec duplication across stacks.
- Same 3 display offsets/bytes are duplicated in WPF (`Views/BinaryPatchesView.xaml.cs`) and Python core/script.
- Opportunity: generate WPF specs from a shared manifest (JSON/YAML) to reduce drift risk.

3. WPF patch logic lacks targeted automated tests.
- Current WPF tests only verify tab existence (`OnslaughtCareerEditor.UiTests/SmokeTests.cs:67-70`).
- Opportunity: add unit tests for verify/apply/restore state transitions and backup behavior (like Python tests already do).

4. Script-level test coverage is uneven.
- Python core has regression tests, but standalone scripts (`patch_display_mode_flow.py`, `patch_devmode_goodies_logic_fix.py`) do not have direct automated tests.
- Opportunity: add hermetic script tests against synthetic bytearrays/temp files.

5. No hash gate before patching in active code paths.
- Docs define canonical target hash, but active apply code verifies only local bytes at selected offsets.
- Opportunity: optional SHA256 preflight for strict mode, with explicit override for known variants.

6. Doc drift exists inside roadmap docs.
- `lore-book/roadmap/gui-expansion.md:70` conflicts with parity/current-capabilities docs by claiming Python binary patch parity is pending.
- Opportunity: align stale roadmap statements with current implemented reality.

7. Archived patch scripts are still executable and adjacent to active scripts.
- They are documented as archived, but discoverability can still cause accidental use.
- Opportunity: require explicit archive prefix command, or add hard runtime guard prompt unless `--i-know-what-im-doing`.
