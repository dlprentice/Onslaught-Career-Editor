# Main-Agent Execution Summary (Post Depth4)

Date: 2026-03-04

## Wave Integrity

- Depth 1 complete (10 lanes).
- Depth 2 complete (10 lanes).
- Depth 3 complete (10 lanes) with deterministic fix cards + master queue.
- Depth 4 complete (10 lanes) with execution synthesis plans.
- `developer_agent_state.json`, `documentation_agent_state.json`, `re_orchestrator_state.json` remained unchanged throughout subagent waves (verified by SHA256), then were updated only by main agent during implementation pass.

## Implemented Tranches (Main Agent)

### Critical/High truth-alignment fixes

- Updated `documentation-standards` skill to canonical AGENTS/index policy and true-view kill offset framing.
- Corrected conditional defaultoptions write-path wording (`DAT_0082b5b0` load-path condition + multi-flow rewrite nuance) across:
  - `AGENTS.md`
  - `reverse-engineering/save-file/save-format.md`
  - `reverse-engineering/binary-analysis/functions/Controller.cpp/ControlBindings.md`
  - `BesFilePatcher.cs`
  - `patcher.py`
- Expanded `CCareer__Load` summaries in:
  - `reverse-engineering/binary-analysis/executable-analysis.md`
  - `reverse-engineering/binary-analysis/GHIDRA-REFERENCE.md`
- Fixed stale roadmap parity status and stale project-tree entries in `roadmap/gui-expansion.md`.

### App behavior + parity hardening

- Added Python CLI `--version` support with C#-compatible `1.0.0+<sha>` output contract.
- Removed duplicate Options summary section in `onslaught/gui/tabs/save_analyzer.py`.
- Updated Save/Configuration UI copy to reflect accurate `.bes`/`.bea` runtime semantics:
  - `Views/SaveEditorView.xaml`
  - `Views/SaveEditorView.xaml.cs`
  - `onslaught/gui/tabs/save_editor.py`

### Binary patch track hardening

- Introduced explicit Stable vs Experimental labeling in:
  - `Views/BinaryPatchesView.xaml`
  - `Views/BinaryPatchesView.xaml.cs`
  - `onslaught/gui/tabs/binary_patches.py`
  - `onslaught/core/binary_patches.py` (track metadata + report rendering)
  - `patches/README.md`
  - `patches/patch_display_mode_flow.py`

### Companion tooling and release gates

- Added `tools/cardid_preset_manager.py` (dry-run/apply/restore, backup-safe, idempotent managed block updates).
- Added `tools/release_package.sh` dry-run policy gate with `R0/R2/R3/R4` classification and denylist reporting.
- Added release policy section to `AGENTS.md` and linked policy gating in `roadmap/app-delivery-phases.md`.

### Documentation sweeps and modernization notes

- Updated `CURRENT_CAPABILITIES.md` tail-mapping wording to current documented state.
- Updated lore roadmap defaultoptions phrasing to baseline/snapshot semantics.
- Added mirror rewrite policy notes in `lore/_index.md` and `lore-book/lore/_index.md`.
- Updated display modernization plan with drift detection policy, GPU/driver matrix, and d3d8to9 historical caveat.

### Regression coverage added

- Added `tests_pyqt/test_cli_readonly_modes_unittest.py`.
- Added `tests_pyqt/test_cli_options_file_safety_unittest.py`.
- Extended `tests_pyqt/test_binary_patches_unittest.py` with track-label report assertion.
- Updated validation checklist docs to include new test modules.

## Validation Results

Executed successfully:

- `python3 -m compileall -q onslaught onslaught_explorer.py patcher.py tools/cardid_preset_manager.py tests_pyqt`
- `python3 -m unittest tests_pyqt/test_save_patch_regressions_unittest.py tests_pyqt/test_cli_goodie_list_unittest.py tests_pyqt/test_cli_validation_unittest.py tests_pyqt/test_binary_patches_unittest.py tests_pyqt/test_cli_readonly_modes_unittest.py tests_pyqt/test_cli_options_file_safety_unittest.py`
- `python3 tools/cardid_preset_manager.py --dry-run --input game/cardid.txt --preset modern`
- `./tools/release_package.sh --dry-run`
- `"/mnt/c/Program Files/dotnet/dotnet.exe" build "Onslaught - Career Editor.sln"`

## Remaining Queue (not yet closed in this pass)

- C# UI/CLI regression additions analogous to the new Python tests (read-only CLI modes, options-file safety, binary patch semantics).
- Additional medium UI parity cards (menu/status/lore lazy-load contract alignment) where intentional asymmetry is not yet codified.
- Full release allowlist curation output and publish-candidate packaging profile (policy gate exists, packaging policy application remains operational follow-up).
