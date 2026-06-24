# Depth4 Lane 10 - Global Prioritized Execution Schedule (Canonical Queue)

## Inputs Used
- `subagents/depth3/lane10_master_fix_queue.tsv` (authoritative global FX backlog, priority, validation commands)
- `subagents/depth3/lane01_docs_fixcards.md`
- `subagents/depth3/lane02_lore_fixcards.md`
- `subagents/depth3/lane03_skill_fixcards.md`
- `subagents/depth3/lane04_gui_fixcards.md`
- `subagents/depth3/lane05_cli_fixcards.md`
- `subagents/depth3/lane06_binary_patch_backlog_cards.md`
- `subagents/depth3/lane07_release_readiness_cards.md`
- `subagents/depth3/lane08_test_implementation_cards.md`
- `subagents/depth3/lane09_semantics_wording_cards.md`

Note: no pre-existing lane plan files were present under `subagents/depth4` at synthesis time; depth3 lane cards are treated as the operative per-lane execution plans.

## Global Execution Rules
1. Run tranches in order; no forward work before the current tranche gate passes.
2. Inside each tranche, execute queue items in listed order unless a hard blocker requires local swap.
3. Every queue item is done only when its `Done Proof` command/check passes.
4. If a tranche gate fails, resolve within-tranche only; do not open the next tranche.

## Tranche T1 (Queue 01-11): Canonical Semantics + Skill/Docs Truth Baseline
### Done-Gate T1
1. Skill/doc canonical anchor corrections are merged and validated (`AGENTS.md` + top-level indexes, true-view offsets).
2. `defaultoptions.bea` semantics are conditional/multi-flow accurate across all targeted docs/comments.
3. Roadmap/capability doc contradictions from FX-005/011/014/015/017 are resolved.

| # | FX | Priority | Execution Unit | Source Plan | Done Proof |
|---|---|---|---|---|---|
| 01 | FX-001 | CRITICAL | Replace `CLAUDE.md` anchors with canonical repo anchors in skill doc | SD-01 | `rg -n "CLAUDE.md|AGENTS.md|RE-INDEX.md|LORE-INDEX.md|ROADMAP-INDEX.md" /home/dlprentice/.codex/skills/documentation-standards/SKILL.md` |
| 02 | FX-002 | CRITICAL | Fix kill-counter example to true-view (`file 0x23F6`, `CCareer 0x23F4`) | SD-02 | `rg -n "0x23F6|0x23F4|legacy aligned|aligned-view" /home/dlprentice/.codex/skills/documentation-standards/SKILL.md` |
| 03 | FX-012 | HIGH | Make top-level canonical index policy mandatory and complete | SD-03 | `rg -n "RE-INDEX.md|LORE-INDEX.md|ROADMAP-INDEX.md|canonical" /home/dlprentice/.codex/skills/documentation-standards/SKILL.md` |
| 04 | FX-013 | HIGH | Align README policy to `_index.md` canonical + compatibility README stance | SD-04 | `rg -n "_index.md|README|compatibility" /home/dlprentice/.codex/skills/documentation-standards/SKILL.md` |
| 05 | FX-003 | HIGH | Normalize conditional load-path write semantics (`DAT_0082b5b0 == 0`) and multi-flow overwrite wording | L9-SEM-01 + FC05 | `rg -n "DAT_0082b5b0|may write defaultoptions.bea|frontend load/save flows" AGENTS.md reverse-engineering/save-file/save-format.md reverse-engineering/binary-analysis/functions/Controller.cpp/ControlBindings.md BesFilePatcher.cs patcher.py` |
| 06 | FX-004 | HIGH | Expand `CCareer__Load` summaries for `flag=0` vs `flag!=0` entries/tail behavior | L9-SEM-02 | `rg -n "flag=0|flag!=0|options entries|tail" reverse-engineering/binary-analysis/executable-analysis.md reverse-engineering/binary-analysis/GHIDRA-REFERENCE.md` |
| 07 | FX-017 | MEDIUM | Update capabilities wording from partial tail map to largely mapped + preserved unknowns | L9-SEM-04 + FC06 | `rg -n "Tail snapshot mapping is largely documented|0x56|unknown|reserved" CURRENT_CAPABILITIES.md` |
| 08 | FX-015 | MEDIUM | Replace template-only framing of `defaultoptions.bea` with baseline/snapshot semantics | L9-SEM-03 | `rg -n "template|baseline|snapshot" lore-book/roadmap/re-investigation.md` |
| 09 | FX-005 | HIGH | Update roadmap status to implemented binary patch parity + current focus | FC01 | `rg -n "Status \(Mar 2026\)|Binary Patches" roadmap/gui-expansion.md` |
| 10 | FX-011 | HIGH | Add missing Python binary patch regression module to validation gates | FC03 + FC04 | `rg -n "test_binary_patches_unittest.py" roadmap/app-validation-checklist.md roadmap/app-delivery-phases.md` |
| 11 | FX-014 | MEDIUM | Refresh stale roadmap project-structure snippet | FC02 | `rg -n "binary_patches.py|settings.py|save_selector.py|hex_viewer.py|media_controls.py" roadmap/gui-expansion.md` |

## Tranche T2 (Queue 12-18): Core CLI/GUI Behavior Parity
### Done-Gate T2
1. Python CLI surface includes `--version` and critical UI/UX semantic copy is corrected.
2. Save Editor/Analyzer parity behavior is aligned across WPF and PyQt for in-place rules, status, menu, and lore loading.
3. Behavior changes are covered by targeted parity tests before moving to full regression tranche.

| # | FX | Priority | Execution Unit | Source Plan | Done Proof |
|---|---|---|---|---|---|
| 12 | FX-006 | HIGH | Add Python CLI `--version` parity | CLI-01 | `python3 patcher.py --version` |
| 13 | FX-007 | HIGH | Remove duplicate `Options` section in PyQt Save Analyzer summary | L4-C05 | `python3 patcher.py --analyze save-attempts/haha-cannon-goes-brrrrr.bes | rg -n "^Options"` |
| 14 | FX-016 | MEDIUM | Update WPF/PyQt Save Editor copy for sync/restart nuance | L9-UI-01/02/03/04 | `rg -n "defaultoptions.bea|load/save|next boot|restart" Views/SaveEditorView.xaml onslaught/gui/tabs/save_editor.py Views/SaveEditorView.xaml.cs` |
| 15 | FX-018 | MEDIUM | Align configuration same-path patch policy (safe in-place parity or explicit divergence) | L4-C01 | `dotnet test OnslaughtCareerEditor.UiTests/OnslaughtCareerEditor.UiTests.csproj --filter "Name~SaveEditorDefaults" && python3 -m unittest -v tests_pyqt.test_save_editor_defaults_unittest` |
| 16 | FX-019 | MEDIUM | Align nested-tab status text contract | L4-C02 | `rg -n "tab active|Status" MainWindow.xaml.cs onslaught/gui/main_window.py` |
| 17 | FX-020 | MEDIUM | Add/align global menu actions across shells | L4-C03 | `rg -n "Open|Analyze|Compare|About|Menu" MainWindow.xaml MainWindow.xaml.cs onslaught/gui/main_window.py` |
| 18 | FX-021 | MEDIUM | Align lore loading strategy to lazy-load contract | L4-C04 | `rg -n "_load_lore_tree|ILazyLoadView|lazy" Views/LoreBrowserView.xaml.cs onslaught/gui/tabs/lore_browser.py` |

## Tranche T3 (Queue 19-26): Regression Harness and Core Test Gates
### Done-Gate T3
1. P0 tests for read-only CLI, options safety, and binary patch safety are implemented and passing in both stacks.
2. P1 parity tests for config, keybind, GUI action smoke, and report structure are passing.
3. Test failures in this tranche block all downstream tranches.

| # | FX | Priority | Execution Unit | Source Plan | Done Proof |
|---|---|---|---|---|---|
| 19 | FX-008 | HIGH | Add cross-stack read-only CLI parity tests (`--analyze`, `--compare`, `--dump-mystery`) | P0-01/02/03/04 + CLI-04 | `dotnet test OnslaughtCareerEditor.UiTests/OnslaughtCareerEditor.UiTests.csproj --filter "Name~CliReadOnly" && python3 -m unittest -v tests_pyqt.test_cli_readonly_modes_unittest` |
| 20 | FX-009 | HIGH | Add options-file safety guard + override tests in both stacks | P0-05/06 | `dotnet test OnslaughtCareerEditor.UiTests/OnslaughtCareerEditor.UiTests.csproj --filter "Name~OptionsFile" && python3 -m unittest -v tests_pyqt.test_cli_options_file_safety_unittest` |
| 21 | FX-010 | HIGH | Add C# binary patch mismatch/apply/restore/spec parity regressions | P0-07/08/09 | `dotnet test OnslaughtCareerEditor.UiTests/OnslaughtCareerEditor.UiTests.csproj --filter "Name~BinaryPatch"` |
| 22 | FX-026 | MEDIUM | Add config command/migration parity tests | P1-10/11 | `python3 -m unittest -v tests_pyqt.test_config_commands_unittest` |
| 23 | FX-027 | MEDIUM | Add keybind token matrix and invalid-token no-write tests | P1-12/13 | `python3 -m unittest -v tests_pyqt.test_keybind_overrides_unittest` |
| 24 | FX-028 | MEDIUM | Expand GUI smoke to action-level gating/flows | P1-16/17 | `dotnet test OnslaughtCareerEditor.UiTests/OnslaughtCareerEditor.UiTests.csproj --filter "Name~Smoke" && pytest -q tests_pyqt/test_smoke.py` |
| 25 | FX-029 | MEDIUM | Add analyze/compare structural output contract tests | P1-14/15 | `python3 -m unittest -v tests_pyqt.test_cli_readonly_modes_unittest` |
| 26 | FX-030 | MEDIUM | Add docs consistency lint for roadmap/validation coverage drift | P2-18/19 | `python3 -m unittest -v tests_pyqt.test_docs_parity_unittest` |

## Tranche T4 (Queue 27-30): Binary Patch Track Hardening (Stable First)
### Done-Gate T4
1. Stable/Experimental taxonomy is explicit in docs/UI/script surfaces.
2. Stable-track verify/apply/restore and script mode behaviors are regression-protected.
3. Companion `cardid` tooling path exists as non-binary unlock lane with backup/restore flow.

| # | FX | Priority | Execution Unit | Source Plan | Done Proof |
|---|---|---|---|---|---|
| 27 | FX-022 | MEDIUM | Introduce explicit Stable vs Experimental track taxonomy and guardrails | BP-S-001 | `rg -n "Stable|Experimental|Track" patches/README.md Views/BinaryPatchesView.xaml onslaught/gui/tabs/binary_patches.py patches/patch_display_mode_flow.py` |
| 28 | FX-024 | MEDIUM | Normalize guard-default narrative across docs (`0x262F3E` default caveat) | BP-S-003 + docs normalization | `rg -n "0x262F3E|0x01|0x00|historical variant" reverse-engineering/binary-analysis/functions/CLIParams.cpp/_index.md reverse-engineering/binary-analysis/windowed-mode-analysis.md` |
| 29 | FX-023 | MEDIUM | Add managed `cardid` preset generator/merger lane with backup/restore | BP-S-006 | `python3 tools/cardid_preset_manager.py --dry-run --input game/cardid.txt --preset modern` |
| 30 | FX-025 | MEDIUM | Complete binary patch mode coverage (`resolution-only`, `windowed-only`, `skip-auto-toggle`) + C# parity assertions | BP-S-005 | `python3 -m unittest -v tests_pyqt.test_binary_patches_unittest && dotnet test OnslaughtCareerEditor.UiTests/OnslaughtCareerEditor.UiTests.csproj --filter "Name~BinaryPatch"` |

## Tranche T5 (Queue 31-32): Release Policy Enforcement and Packaging Gates
### Done-Gate T5
1. R0-R4 allowlist-first release policy is codified in repo docs/runbook.
2. Packaging dry-run enforces denylist patterns for private/proprietary/runtime-residue families.
3. No hard-exclude (`R4`) family can pass allowlist gate.

| # | FX | Priority | Execution Unit | Source Plan | Done Proof |
|---|---|---|---|---|---|
| 31 | FX-031 | MEDIUM | Codify enforceable release profile (allowlist-first, R0-R4) | Lane07 INV/ALW/DEN/POL cards | `rg -n "R0|R1|R2|R3|R4|allowlist" AGENTS.md roadmap` |
| 32 | FX-032 | MEDIUM | Implement packaging denylist enforcement script/runbook | Lane07 DEN-02/03/04 | `./tools/release_package.sh --dry-run | rg -n "game/|media/|save-attempts/|subagents/|_state.json"` |

## Tranche T6 (Queue 33-40): Modernization Stability + Low-Severity Harmonization
### Done-Gate T6
1. Modernization docs include drift detection, compatibility matrix, and stale-pilot annotations.
2. Lore mirror normalization policy and low-severity CLI output/validation drifts are resolved or explicitly documented as intentional.
3. Cross-stack low-severity parity checks run clean.

| # | FX | Priority | Execution Unit | Source Plan | Done Proof |
|---|---|---|---|---|---|
| 33 | FX-033 | MEDIUM | Add `defaultoptions` drift detection/reapply policy to modernization workflow | Depth2 lane10 findings | `rg -n "drift|defaultoptions|reapply" reverse-engineering/binary-analysis/display-modernization-plan.md` |
| 34 | FX-034 | MEDIUM | Define fixed GPU/driver matrix for staged modernization rollout | Depth2 lane10 findings | `rg -n "NVIDIA|AMD|Intel|driver|matrix" reverse-engineering/binary-analysis/display-modernization-plan.md` |
| 35 | FX-040 | LOW | Mark `d3d8to9` pilot language as historical unless revalidated for current retail hash | Depth2 lane10 findings | `rg -n "d3d8to9|historical|retail hash|D3D9" reverse-engineering/binary-analysis/display-modernization-plan.md` |
| 36 | FX-035 | LOW | Document allowed lore mirror path normalization rewrite rule | Lane02 card set | `rg -n "allowed mirror rewrite|path normalization" lore/_index.md lore-book/lore/_index.md` |
| 37 | FX-036 | LOW | Align numeric validation stage for controller-config args | CLI-02 | `python3 patcher.py save-attempts/haha-cannon-goes-brrrrr.bes out.bes --controller-config-p1 -1; "/mnt/c/Program Files/dotnet/dotnet.exe" run --project "Onslaught - Career Editor.csproj" -- save-attempts/haha-cannon-goes-brrrrr.bes out.bes --controller-config-p1 -1` |
| 38 | FX-037 | LOW | Remove failure preamble drift on copy-options conflict path | CLI-03 | `python3 patcher.py save-attempts/haha-cannon-goes-brrrrr.bes out.bes --copy-options-from save-attempts/haha-cannon-goes-brrrrr.bes --no-copy-options-entries --no-copy-options-tail` |
| 39 | FX-038 | LOW | Align analyze/compare marker wording contract across CLIs | CLI-04 | `python3 patcher.py --analyze save-attempts/haha-cannon-goes-brrrrr.bes && "/mnt/c/Program Files/dotnet/dotnet.exe" run --project "Onslaught - Career Editor.csproj" -- --analyze save-attempts/haha-cannon-goes-brrrrr.bes` |
| 40 | FX-039 | LOW | Document environment-scoped `show-config` parity expectations | CLI parity findings | `python3 patcher.py --show-config && "/mnt/c/Program Files/dotnet/dotnet.exe" run --project "Onslaught - Career Editor.csproj" -- --show-config` |

## Canonical Queue Completion Condition
All six tranche gates pass in sequence, and queue items `01` through `40` each have passing `Done Proof` evidence.
