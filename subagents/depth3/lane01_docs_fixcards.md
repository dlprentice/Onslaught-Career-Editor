# Lane 01 - Canonical Doc Fix Cards (Depth 3)

Scope focus: `AGENTS.md`, `README.MD`, `CURRENT_CAPABILITIES.md`, and `roadmap/*` canonical docs.
Input findings consumed: `subagents/depth2/lane01_canonical_docs_contradictions.md`, `subagents/depth2/lane09_dataflow_semantics_validation.md`, `subagents/depth2/lane08_test_gap_priorities.md`.

## Fix Card 01
- File: `roadmap/gui-expansion.md`
- Issue: Phase 1 status line says Python Binary Patches parity is pending, but parity is already implemented.
- Exact replacement text intent:
  - Replace the current `**Status (Mar 2026):** ... (WPF also includes a Binary Patches tab; Python parity for that surface is pending.)`
  - With:
    - `**Status (Mar 2026):** Save Editor, Save Analyzer, Configuration Editor, Lore Browser, media tabs, Settings, and Binary Patches are implemented in both WPF and PyQt. Current work is UX polish, reliability hardening, and regression depth.`
- Validation step:
  - Run:
    - `rg -n "Status \(Mar 2026\):.*Binary Patches are implemented in both WPF and PyQt" roadmap/gui-expansion.md`
    - `rg -n "Python parity for that surface is pending" roadmap/gui-expansion.md` (must return no matches)

## Fix Card 02
- File: `roadmap/gui-expansion.md`
- Issue: `Project Structure` code block is stale (missing active modules and listing nonexistent placeholders).
- Exact replacement text intent:
  - Replace the entire code block under `## Project Structure` with this canonical-minimal tree:

```text
Onslaught-Career-Editor/
├── patcher.py
├── onslaught_explorer.py
├── onslaught/
│   ├── core/
│   │   ├── bes_file.py
│   │   ├── binary_patches.py
│   │   ├── config.py
│   │   └── constants.py
│   └── gui/
│       ├── main_window.py
│       ├── theme.py
│       ├── tabs/
│       │   ├── save_editor.py
│       │   ├── save_analyzer.py
│       │   ├── settings.py
│       │   ├── binary_patches.py
│       │   ├── lore_browser.py
│       │   ├── audio_player.py
│       │   ├── video_player.py
│       │   ├── goodie_viewer.py   # prototype (shelved)
│       │   └── asset_browser.py   # prototype (shelved)
│       └── widgets/
│           └── save_selector.py
```

  - Explicit removals in that block: `hex_viewer.py`, `media_controls.py`, `onslaught/data/icons/`.
- Validation step:
  - Run:
    - `rg -n "binary_patches\.py|settings\.py|save_selector\.py" roadmap/gui-expansion.md`
    - `rg -n "hex_viewer\.py|media_controls\.py|onslaught/data/icons" roadmap/gui-expansion.md` (must return no matches)

## Fix Card 03
- File: `roadmap/app-validation-checklist.md`
- Issue: Python regression gate omits active binary patch regression suite.
- Exact replacement text intent:
  - Replace the current unittest command bullet with:

```bash
python3 -m unittest tests_pyqt/test_save_patch_regressions_unittest.py tests_pyqt/test_cli_goodie_list_unittest.py tests_pyqt/test_cli_validation_unittest.py tests_pyqt/test_save_editor_defaults_unittest.py tests_pyqt/test_binary_patches_unittest.py
```

- Validation step:
  - Run:
    - `rg -n "test_binary_patches_unittest\.py" roadmap/app-validation-checklist.md`

## Fix Card 04
- File: `roadmap/app-delivery-phases.md`
- Issue: Phase validation gate unittest command is stale/incomplete vs active parity-critical suites.
- Exact replacement text intent:
  - Replace gate item `4.` with:

```text
4. `python3 -m unittest tests_pyqt/test_save_patch_regressions_unittest.py tests_pyqt/test_cli_goodie_list_unittest.py tests_pyqt/test_cli_validation_unittest.py tests_pyqt/test_save_editor_defaults_unittest.py tests_pyqt/test_binary_patches_unittest.py`
```

- Validation step:
  - Run:
    - `rg -n "test_save_editor_defaults_unittest\.py|test_binary_patches_unittest\.py" roadmap/app-delivery-phases.md`

## Fix Card 05
- File: `AGENTS.md`
- Issue: `defaultoptions.bea` write from load flow is currently phrased as unconditional; validated behavior is conditional (`DAT_0082b5b0 == 0`) and other save/menu flows can also write.
- Exact replacement text intent:
  - Replace the current `Frontend nuance (Steam build): ...` paragraph with:
    - `Frontend nuance (Steam build): in CFEPLoadGame__DoLoad (0x00461e20), the game may write defaultoptions.bea from the loaded save buffer via CFEPOptions__WriteDefaultOptionsFile(source, size) when DAT_0082b5b0 == 0. Other save/menu flows can also update defaultoptions.bea, so a patched .bes can still become next-boot global options after load/save + restart.`
- Validation step:
  - Run:
    - `rg -n "DAT_0082b5b0 == 0|Other save/menu flows can also update defaultoptions\.bea" AGENTS.md`

## Fix Card 06
- File: `CURRENT_CAPABILITIES.md`
- Issue: Options-tail mapping status is stale (`partial`) vs current mapped-tail documentation.
- Exact replacement text intent:
  - Replace:
    - `Partial identification of some tail snapshot globals (mouse sensitivity, control scheme index, language index, screen shape).`
  - With:
    - `Tail snapshot mapping is largely documented (0x56 bytes; input/render/audio globals mapped at tail-relative offsets), with remaining unknown/reserved fields explicitly preserved.`
- Validation step:
  - Run:
    - `rg -n "Tail snapshot mapping is largely documented" CURRENT_CAPABILITIES.md`

## No-Change Determination (Depth2-backed)
- File: `README.MD`
- Determination: no deterministic contradiction requiring canonical text replacement was identified in depth2 canonical-doc findings.
- Validation step:
  - Keep as verify-only in this lane; do not patch unless a new contradictory evidence item is opened.
