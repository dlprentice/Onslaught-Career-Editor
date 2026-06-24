# Lane 04 - C# vs Python parity claims audit (read-only)

## Scope
- Code audited: `Program.cs`, `MainWindow.xaml`, `MainWindow.xaml.cs`, `Views/**`, `onslaught_explorer.py`, `onslaught/gui/**`, `patcher.py`.
- Docs audited: `roadmap/csharp-python-parity.md` and lore mirror `lore-book/roadmap/csharp-python-parity.md`.
- Method: read-only code/doc verification with file:line evidence.

## Findings (false positives / missing caveats)

### 1. HIGH - Lore parity claim is outdated (false positive)
- Claim: Lore Browser scans `lore/`, `reverse-engineering/`, `roadmap/` and status includes project-root context (`roadmap/csharp-python-parity.md:78-81`, mirrored at `lore-book/roadmap/csharp-python-parity.md:78-81`).
- Actual code: both stacks load from `lore-book` only.
  - C#: `Views/LoreBrowserView.xaml.cs:120-129`, `Views/LoreBrowserView.xaml.cs:273-317`.
  - Python: `onslaught/gui/tabs/lore_browser.py:31-32`, `onslaught/gui/tabs/lore_browser.py:155-160`, `onslaught/gui/tabs/lore_browser.py:802-826`.
- Also, C# status text reports load count but not project root (`Views/LoreBrowserView.xaml.cs:180`).
- Verdict: **false positive** in parity docs (and repeated in mirror).

### 2. MEDIUM - Configuration parity has an untracked behavioral divergence (missing caveat)
- Docs do not explicitly track Configuration Editor status in parity table (no Configuration row in `roadmap/csharp-python-parity.md:9-20`; same in mirror).
- Behavior diverges:
  - C# Configuration Editor allows in-place `.bea` patch with confirmation and timestamped `.bak` backup (`Views/SaveEditorView.xaml.cs:929-930`, `Views/SaveEditorView.xaml.cs:947-963`, `Views/SaveEditorView.xaml.cs:1004-1009`, `Views/SaveEditorView.xaml.cs:1998-2032`), and defaults output to input in configuration mode (`Views/SaveEditorView.xaml.cs:691-693`).
  - Python Configuration Editor blocks in-place patching (`onslaught/gui/tabs/save_editor.py:710`, `onslaught/gui/tabs/save_editor.py:1073-1075`) and auto-suggests `<name>_patched` output (`onslaught/gui/tabs/save_editor.py:645-647`).
- Verdict: **missing caveat** (parity doc does not describe this important safety/UX difference).

### 3. MEDIUM - Save Analyzer TreeView claim overstates C# parity (false positive)
- Claim: C# TreeView summary includes file info "path, version" (`roadmap/csharp-python-parity.md:106-109`, mirror same).
- C# tree summary includes size/version/header/new-goodie fields, but not file path (`Views/SaveAnalyzerView.xaml.cs:173-189`).
- Python summary includes explicit Path (`onslaught/gui/tabs/save_analyzer.py:201`).
- Verdict: **false positive** for C# TreeView parity on path field.

### 4. LOW - Save Editor kill-range row is stale (doc drift)
- Claim says minor gap: Python 0-65535 vs C# 0-1000 (`roadmap/csharp-python-parity.md:103`, mirror same).
- Actual code: both are 0-65535.
  - C#: `Views/SaveEditorView.xaml:178`.
  - Python: `onslaught/gui/tabs/save_editor.py:125`.
- Verdict: stale caveat (no current gap).

### 5. LOW - CLI list is not exhaustive (missing caveat, not a parity failure)
- Docs say CLI parity complete (`roadmap/csharp-python-parity.md:11`, `roadmap/csharp-python-parity.md:171`) and list many flags (`roadmap/csharp-python-parity.md:173-190`), but omit at least:
  - `--allow-career-sections-on-options-file` (present in both CLIs: `Program.cs:155-157`, `patcher.py:1676-1677`).
  - `--version` (visible in Python parser `patcher.py:1657`, and C# CLI help output includes `--version`).
- Verdict: missing caveat/documentation completeness issue only.

## Category verdicts
- Save Editor: **Mostly aligned**, with stale doc row on kill-range (`roadmap/csharp-python-parity.md:103`; code at `Views/SaveEditorView.xaml:178`, `onslaught/gui/tabs/save_editor.py:125`).
- Save Analyzer: **Partial mismatch** (C# TreeView missing path while doc says parity; see finding #3).
- Configuration: **Behavioral divergence** not documented (see finding #2).
- Binary Patches: **Aligned** (tabs present and verify/apply/restore flows in both: `Views/BinaryPatchesView.xaml.cs:127-221`, `onslaught/gui/tabs/binary_patches.py:199-261`; tab wiring `MainWindow.xaml:100-102`, `onslaught/gui/main_window.py:105-106`).
- Lore: **Doc false positive** (see finding #1).
- Media: **Aligned** (both stacks include Audio+Video tabs and subdir/root discovery logic: `MainWindow.xaml:82-94`, `onslaught/gui/main_window.py:87-98`, `Views/VideoPlayerView.xaml.cs:254-387`, `onslaught/gui/tabs/video_player.py:322-425`, `Views/AudioPlayerView.xaml.cs:178-241`, `onslaught/gui/tabs/audio_player.py:251-290`).
- Settings: **Aligned** (game-dir + media playback preferences in both: `Views/SettingsView.xaml:21-102`, `Views/SettingsView.xaml.cs:22-179`, `onslaught/gui/tabs/settings.py:30-110`, `onslaught/gui/tabs/settings.py:138-238`).
- CLI safety: **Aligned** (in-place patch blocked + options-file career patch guard in both CLIs: `Program.cs:630-633`, `Program.cs:777-787`, `patcher.py:1912-1914`, `patcher.py:1961-1966`).

## Mirror status
- `lore-book/roadmap/csharp-python-parity.md` mirrors the same parity claims/line content for all findings above, so the same corrections apply there.
