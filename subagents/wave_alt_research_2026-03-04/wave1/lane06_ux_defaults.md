# Lane 06 - UX Defaults Research (Save Editor vs Configuration Editor)

Date: 2026-03-04
Scope: WPF + PyQt labels/tooltips/status copy + docs references affecting user-error risk between `.bes` (career save) and `.bea/defaultoptions` (global configuration).

## Verdict ("rope" test)

Current state: **Partially safe, but still medium rope risk**.

- Strong guardrails already exist (mode/file-type validation, options-file warnings, configuration-mode section disabling).
- Two avoidable UX/default issues still leave room for user self-footguns.

Recommended state after changes below: **Low rope risk**.

## Findings (severity first)

HIGH | Views/SaveEditorView.xaml.cs:689-693, 947-956, 2031 | WPF Configuration Editor defaults output to same path (in-place), so the default happy path is direct mutation of the authoritative global options file. Confirmation + `.bak` helps, but default intent is still destructive. | Default to sibling `_patched.bea`; add explicit `Patch in place (create .bak)` toggle (off by default).

HIGH | onslaught_explorer.py:67-70, onslaught/gui/tabs/save_editor.py:603-607 | PyQt `--file` startup always loads `save_editor_tab` and sets status to `Loaded: ...`, even for `.bea`. Save Editor then rejects `.bea`, so status can claim success while file is not actually loaded in the correct editor. | Route by extension at startup exactly like `MainWindow._on_open_file` (`.bea` -> Configuration Editor tab).

MEDIUM | Views/SaveEditorView.xaml.cs:1081-1087, onslaught/gui/tabs/save_editor.py:526-530 | First copy-source selection in Configuration Editor auto-enables `Copy keybind entries`. This hidden default can introduce unintended writes when user expected pure manual edits. | Keep both copy checkboxes off by default; offer explicit action `Clone from source (entries + tail)`.

MEDIUM | MainWindow.xaml:70,76 and onslaught/gui/main_window.py:74,82 | Tab names rely on user memory (`Save Editor` vs `Configuration Editor`) without file-type affordance in the label itself. | Rename headers to `Career Save Editor (.bes)` and `Global Configuration Editor (.bea/defaultoptions)`.

MEDIUM | Views/SaveEditorView.xaml.cs:177-190 and onslaught/gui/tabs/save_editor.py:69,307,343-347 | Mixed terminology (`save`, `configuration`, `options`, `global settings`) across status/tooltips increases cognitive load at decision points. | Normalize terminology: `Career Save (.bes)` vs `Global Options (.bea/defaultoptions)` in all status/tooltips.

LOW | USER_SANITY_CHECK.md:24-25 | Sanity-check doc references `Configuration Overrides (.bea/.bes)` which no longer matches current UI naming and implies `.bes` is valid in Configuration Editor. | Update to current UI terms and explicit `.bea/defaultoptions only` wording.

LOW | README.MD:62-64 with roadmap/csharp-python-parity.md:17 | WPF quick-start is clear for in-place config patching, but cross-stack differences can still be missed by readers who jump sections. | Add one explicit note in Python GUI section: `Configuration Editor uses separate output file (no in-place patch).`

## What is already good (keep)

PASS | MainWindow.xaml.cs:227-242 and onslaught/gui/main_window.py:185-189 | File-open routing by extension to the correct editor reduces wrong-tab errors.

PASS | Views/SaveEditorView.xaml.cs:157-165, 1244-1251 and onslaught/gui/tabs/save_editor.py:564-586 | Configuration mode disables career mutation controls by default.

PASS | Views/SaveEditorView.xaml.cs:793-801 and onslaught/gui/tabs/save_editor.py:1378-1385 | Explicit confirmation before career-section patching on options-style files.

## Recommended wording/default alternatives

1. Tab headers
- Current: `Save Editor` / `Configuration Editor`
- Recommended: `Career Save Editor (.bes)` / `Global Configuration Editor (.bea/defaultoptions)`

2. Configuration mode banner
- Current (WPF-only): long descriptive paragraph; PyQt has no equivalent banner.
- Recommended (both stacks): `Editing global boot configuration (defaultoptions.bea). Changes affect next boot.`

3. Output default in Configuration Editor
- Current: WPF defaults in-place; PyQt defaults separate output.
- Recommended: both default to separate output; in-place is explicit opt-in with warning text.

4. Copy-from-source defaults
- Current: config mode auto-checks entries on first source selection.
- Recommended: no implicit checks; explicit preset button for full clone.

## Overall answer to the lane question

- **Current alternatives**: reduce many obvious mistakes, but do **not fully minimize user rope** because one stack defaults to in-place global mutation and startup/status behavior in PyQt can mislead for `.bea` CLI-open.
- **Recommended alternatives above**: would materially minimize rope by making the safe path the default and making risky actions explicit.
