# Depth4 Lane01 - Deterministic Docs Execution Plan

## Scope
Produce and apply documentation-only corrections synthesized from `subagents/depth1..depth3`, with deterministic ordering, explicit dependencies, and acceptance gates.

Primary source cards:
- `subagents/depth3/lane01_docs_fixcards.md`
- `subagents/depth3/lane03_skill_fixcards.md`
- `subagents/depth3/lane09_semantics_wording_cards.md`
- `subagents/depth3/lane02_lore_fixcards.md`
- `subagents/depth3/lane10_master_fix_queue.tsv`

Supporting constraints/findings:
- `subagents/depth1/lane05_reverse_engineering_docs_inventory.md`
- `subagents/depth1/lane06_lorebook_mirror_inventory.md`
- `subagents/depth2/lane01_canonical_docs_contradictions.md`
- `subagents/depth2/lane02_lore_mirror_contradictions.md`
- `subagents/depth2/lane03_skill_drift_findings.md`
- `subagents/depth2/lane06_binary_patch_gap_findings.md`
- `subagents/depth2/lane09_dataflow_semantics_validation.md`

## Deterministic Sequencing Rules
1. Execute steps in listed order; do not reorder.
2. Do semantic anchor fixes before downstream UI/help wording.
3. Do canonical-doc edits before mirror sync.
4. Mirror sync must be completed before final acceptance.
5. A step is complete only if all its acceptance checks pass.

## Ordered Action Plan

### DOC-00 - Preflight Baseline (Read-Only)
- Cards: gating for all downstream cards.
- Actions:
1. Confirm all target files exist.
2. Capture current matches for stale/target phrases (for deterministic before/after checks).
- Dependencies: none.
- Acceptance checks:
1. `test -f AGENTS.md && test -f roadmap/gui-expansion.md && test -f reverse-engineering/save-file/save-format.md`
2. `test -f /home/dlprentice/.codex/skills/documentation-standards/SKILL.md`

### DOC-01 - Core DefaultOptions Load/Write Semantics
- Cards: `L9-SEM-01`, `FX-003`, `Fix Card 05`.
- Target files:
1. `AGENTS.md`
2. `reverse-engineering/save-file/save-format.md`
3. `reverse-engineering/binary-analysis/functions/Controller.cpp/ControlBindings.md`
4. `BesFilePatcher.cs`
5. `patcher.py`
- Actions:
1. Replace unconditional wording with conditional load-path wording (`DAT_0082b5b0 == 0`).
2. Keep explicit note that other save/menu flows may also rewrite `defaultoptions.bea`.
- Dependencies: `DOC-00`.
- Acceptance checks:
1. `rg -n "DAT_0082b5b0 == 0|may write defaultoptions\\.bea|load/save flows" AGENTS.md reverse-engineering/save-file/save-format.md reverse-engineering/binary-analysis/functions/Controller.cpp/ControlBindings.md BesFilePatcher.cs patcher.py`
2. `rg -n "the game writes defaultoptions\\.bea from the loaded save buffer" AGENTS.md reverse-engineering/save-file/save-format.md reverse-engineering/binary-analysis/functions/Controller.cpp/ControlBindings.md` must return no matches.

### DOC-02 - CCareer::Load Summary Precision
- Cards: `L9-SEM-02`, `FX-004`.
- Target files:
1. `reverse-engineering/binary-analysis/executable-analysis.md`
2. `reverse-engineering/binary-analysis/GHIDRA-REFERENCE.md`
- Actions:
1. Update summaries to include full `flag=0` vs `flag!=0` behavior for sound/music plus options entries/tail apply/skip semantics.
- Dependencies: `DOC-01`.
- Acceptance checks:
1. `rg -n "boot/defaultoptions path, applies Sound/Music and options entries/tail globals" reverse-engineering/binary-analysis/executable-analysis.md reverse-engineering/binary-analysis/GHIDRA-REFERENCE.md`

### DOC-03 - UI/App Wording + Capability Maturity
- Cards: `L9-UI-01`, `L9-UI-02`, `L9-UI-03`, `L9-UI-04`, `L9-SEM-04`, `Fix Card 06`, `FX-016`, `FX-017`.
- Target files:
1. `Views/SaveEditorView.xaml`
2. `Views/SaveEditorView.xaml.cs`
3. `onslaught/gui/tabs/save_editor.py`
4. `CURRENT_CAPABILITIES.md`
- Actions:
1. Update Save Editor notes to include non-immediate `.bes` apply semantics and load/save sync path to `defaultoptions.bea`.
2. Update WPF status tip text to the same semantics.
3. Update capabilities tail wording from partial to largely mapped `0x56` tail.
- Dependencies: `DOC-01`.
- Acceptance checks:
1. `rg -n "load/save frontend flows can sync a \\.bes buffer into defaultoptions\\.bea|restart after a load/save flow" Views/SaveEditorView.xaml`
2. `rg -n "load/save flows may sync it from \\.bes for next boot" Views/SaveEditorView.xaml.cs`
3. `rg -n "does not apply immediately; next-boot behavior can come from load/save sync into defaultoptions\\.bea" onslaught/gui/tabs/save_editor.py`
4. `rg -n "Tail snapshot mapping is largely documented" CURRENT_CAPABILITIES.md`
5. `rg -n "Partial identification of some tail snapshot globals" CURRENT_CAPABILITIES.md` must return no matches.

### DOC-04 - Canonical Roadmap Contradiction Repairs
- Cards: `Fix Card 01`, `Fix Card 02`, `Fix Card 03`, `Fix Card 04`, `FX-005`, `FX-011`, `FX-014`.
- Target files:
1. `roadmap/gui-expansion.md`
2. `roadmap/app-validation-checklist.md`
3. `roadmap/app-delivery-phases.md`
- Actions:
1. Update GUI expansion status to reflect shipped Python Binary Patches parity.
2. Replace stale project structure snippet with current minimal tree.
3. Add `tests_pyqt/test_binary_patches_unittest.py` to required Python gate commands.
- Dependencies: `DOC-00`.
- Acceptance checks:
1. `rg -n "Binary Patches are implemented in both WPF and PyQt" roadmap/gui-expansion.md`
2. `rg -n "Python parity for that surface is pending" roadmap/gui-expansion.md` must return no matches.
3. `rg -n "binary_patches\\.py|settings\\.py|save_selector\\.py" roadmap/gui-expansion.md`
4. `rg -n "hex_viewer\\.py|media_controls\\.py|onslaught/data/icons" roadmap/gui-expansion.md` must return no matches.
5. `rg -n "test_binary_patches_unittest\\.py" roadmap/app-validation-checklist.md roadmap/app-delivery-phases.md`

### DOC-05 - DefaultOptions Template Framing Cleanup (Canonical + Mirror)
- Cards: `L9-SEM-03`, `FX-015`.
- Target files:
1. `roadmap/re-investigation.md`
2. `lore-book/roadmap/re-investigation.md`
- Actions:
1. Replace template-only framing with baseline/snapshot + overwrite-side-effect wording in both canonical and mirror copies.
- Dependencies: `DOC-01`.
- Acceptance checks:
1. `rg -n "baseline/snapshot and overwrite side effects|not just a one-time new-save template" roadmap/re-investigation.md lore-book/roadmap/re-investigation.md`
2. `rg -n "understand template|template used when creating new career saves" roadmap/re-investigation.md lore-book/roadmap/re-investigation.md` must return no matches.

### DOC-06 - Windowed Guard Narrative Consistency
- Cards: `FX-024`.
- Target files:
1. `reverse-engineering/binary-analysis/functions/CLIParams.cpp/_index.md`
2. `reverse-engineering/binary-analysis/windowed-mode-analysis.md`
- Actions:
1. Normalize wording to current-hash default `0x01` with historical-variant caveat.
- Dependencies: `DOC-01`.
- Acceptance checks:
1. `rg -n "0x262F3E|0x01|historical" reverse-engineering/binary-analysis/functions/CLIParams.cpp/_index.md reverse-engineering/binary-analysis/windowed-mode-analysis.md`

### DOC-07 - Documentation Skill Drift Corrections
- Cards: `SD-01`, `SD-02`, `SD-03`, `SD-04`, `SD-05`, `FX-001`, `FX-002`, `FX-012`, `FX-013`.
- Target file:
1. `/home/dlprentice/.codex/skills/documentation-standards/SKILL.md`
- Actions:
1. Remove `CLAUDE.md` canonical guidance; replace with `AGENTS.md` and canonical index references.
2. Correct kill-counter example to `file 0x23F6` + `CCareer 0x23F4` true-view mapping.
3. Make top-level index guidance mandatory and complete (`RE-INDEX.md`, `LORE-INDEX.md`, `ROADMAP-INDEX.md`).
4. Align README guidance to compatibility posture (`_index.md` canonical, folder README allowed but non-divergent).
5. Replace stale god-mode sample status with conservative unverified wording.
- Dependencies: `DOC-01`.
- Acceptance checks:
1. `rg -n "AGENTS.md|RE-INDEX.md|LORE-INDEX.md|ROADMAP-INDEX.md|0x23F6|0x23F4|_index.md|compatibility|Unverified" /home/dlprentice/.codex/skills/documentation-standards/SKILL.md`
2. `rg -n "CLAUDE.md" /home/dlprentice/.codex/skills/documentation-standards/SKILL.md` must return no matches.

### DOC-08 - Canonical-to-Mirror Sync for Changed Files
- Cards: mirror policy enforcement from depth1/depth2.
- Target mirrored file pairs:
1. `roadmap/gui-expansion.md` -> `lore-book/roadmap/gui-expansion.md`
2. `roadmap/app-validation-checklist.md` -> `lore-book/roadmap/app-validation-checklist.md`
3. `roadmap/app-delivery-phases.md` -> `lore-book/roadmap/app-delivery-phases.md`
4. `roadmap/re-investigation.md` -> `lore-book/roadmap/re-investigation.md`
5. `reverse-engineering/save-file/save-format.md` -> `lore-book/reverse-engineering/save-file/save-format.md`
6. `reverse-engineering/binary-analysis/executable-analysis.md` -> `lore-book/reverse-engineering/binary-analysis/executable-analysis.md`
7. `reverse-engineering/binary-analysis/GHIDRA-REFERENCE.md` -> `lore-book/reverse-engineering/binary-analysis/GHIDRA-REFERENCE.md`
8. `reverse-engineering/binary-analysis/windowed-mode-analysis.md` -> `lore-book/reverse-engineering/binary-analysis/windowed-mode-analysis.md`
9. `reverse-engineering/binary-analysis/functions/Controller.cpp/ControlBindings.md` -> `lore-book/reverse-engineering/binary-analysis/functions/Controller.cpp/ControlBindings.md`
10. `reverse-engineering/binary-analysis/functions/CLIParams.cpp/_index.md` -> `lore-book/reverse-engineering/binary-analysis/functions/CLIParams.cpp/_index.md`
- Actions:
1. Sync canonical content to mirror paths after canonical edits.
2. Preserve only known intentional mirror-only divergences (`lore/_index.md` AGENTS link depth and previously documented curated exceptions).
- Dependencies: `DOC-02`, `DOC-04`, `DOC-05`, `DOC-06`.
- Acceptance checks:
1. For each pair above, `cmp -s <canonical> <mirror>` returns success.

### DOC-09 - Lore Mirror Integrity Gate
- Cards: `L2-001..L2-014`, `FX-035` (policy note).
- Actions:
1. Verify lore canonical/mirror parity still has exactly one allowed divergence: `lore/_index.md` AGENTS relative-link depth.
2. Record any additional diff as failure.
- Dependencies: `DOC-08`.
- Acceptance checks:
1. `diff -u lore/_index.md lore-book/lore/_index.md | rg "AGENTS.md"` shows only expected `../` vs `../../` delta.
2. For all other lore pairs, `cmp -s` passes.

### DOC-10 - Final Cross-Doc Consistency Sweep
- Cards: closure gate for all documentation cards.
- Actions:
1. Run one deterministic grep suite across all edited surfaces.
2. Ensure no stale phrases remain and all required replacements are present.
- Dependencies: `DOC-03`, `DOC-07`, `DOC-09`.
- Acceptance checks:
1. `rg -n "Python parity for that surface is pending|understand template|template used when creating new career saves|Partial identification of some tail snapshot globals" AGENTS.md roadmap lore-book CURRENT_CAPABILITIES.md reverse-engineering /home/dlprentice/.codex/skills/documentation-standards/SKILL.md` returns no matches.
2. `rg -n "DAT_0082b5b0 == 0|Tail snapshot mapping is largely documented|Binary Patches are implemented in both WPF and PyQt|test_binary_patches_unittest.py" AGENTS.md CURRENT_CAPABILITIES.md roadmap reverse-engineering` returns expected matches.

## Dependency Graph (Compact)
- `DOC-00` -> `DOC-01`, `DOC-04`
- `DOC-01` -> `DOC-02`, `DOC-03`, `DOC-05`, `DOC-06`, `DOC-07`
- `DOC-02` + `DOC-04` + `DOC-05` + `DOC-06` -> `DOC-08`
- `DOC-08` -> `DOC-09`
- `DOC-03` + `DOC-07` + `DOC-09` -> `DOC-10`

## Definition of Done
1. All steps `DOC-00` through `DOC-10` completed in order.
2. Every acceptance check passes.
3. Canonical and mirror docs remain synchronized except explicitly allowed divergences.
4. No non-doc code-path behavior changes are introduced in this lane.
