# Save / Options Static Review

Status: static-closed review slice
Date: 2026-05-26
Scope: `save-options-static-review-wave902`

Wave902 is the first concrete post-100 system review after Wave900 closed the loaded Ghidra function-quality queue and Wave901 established the system-review baseline. It reviews save/options/career persistence across the saved Ghidra function snapshot, canonical save docs, AppCore patching rules, CLI/UI test coverage, and public release posture.

Probe token anchor: Wave902; `save-options-static-review-wave902`; static-closed save/options/career; `6113/6113 = 100.00%`; `10004` bytes; version `0x4BD1`; career base `0x0002`; kill counters `0x23F6`; options entries `0x24BE`; options tail `0x56`; `CCareer__Load`; `CCareer__Save`; `OptionsTail_Write`; `OptionsTail_Read`; `CFEPOptions__WriteDefaultOptionsFile`; `CPauseMenu__ResumeGameAndPersistOptions`; `[maintainer-local-ghidra-backup-root]\BEA_20260526-093817_post_wave902_save_options_static_review_verified`.

## Static-Closed Claim

The save/options/career surface is static-closed for file layout, binary serializer/deserializer ownership, frontend persistence call chains, and app/tooling safety rules:

| Area | Static closure evidence | Boundary |
| --- | --- | --- |
| Save container | The retail file is a fixed `10004` bytes, starts with version word `0x4BD1`, and stores the `CCareer` memory region at true-view base `0x0002`. `CCareer__Load`, `CCareer__Save`, and `CCareer__GetSaveSize` are named, signature-clean, commented, and documented. | This does not prove every runtime save-menu path has been observed in BEA. |
| Career graph, ranks, goodies, kills | Canonical docs and function anchors agree on 100 nodes, 200 links, 300 Goodie slots with 233 displayable entries, raw float ranks, and five packed kill-counter dwords starting at `0x23F6`. | Exact in-game UI presentation and every unlock animation remain runtime observations. |
| Options persistence | `OptionsTail_Write`, `OptionsTail_Read`, options-entry helpers, control preset/remap helpers, and docs agree on options flags at `0x249E`, entries at `0x24BE`, and the `0x56`-byte tail snapshot. | Runtime controller behavior, menu navigation, and hardware/input edge cases still need copied-profile proof when claimed. |
| Frontend persistence | `CFEPLoadGame__DoLoad`, `CFEPOptions__SaveDefaultOptions`, `CFEPOptions__WriteDefaultOptionsFile`, `CPauseMenu__ResumeGameAndPersistOptions`, `CFEPMain__Process`, and `Platform__AsyncSaveCareer` tie frontend save/options flows to the serializer and `defaultoptions.bea` writer. | Filesystem timing and live frontend behavior are not replaced by static xrefs. |
| Product/tooling alignment | `BesFilePatcher` validates size/version, starts from real files, rejects in-place patch output, preserves non-displayable Goodies and unknown regions, supports scoped options copy, and blocks career-section writes to options-like files unless explicitly overridden. Tests cover true-view offsets, kill metadata preservation, options safety, and read-only analysis modes. | Product behavior remains a maintained implementation that can regress; tests stay part of the closure claim. |

This is the first post-100 slice that can be called static-closed with a narrow meaning. It is still not runtime parity, source-layout parity, patch proof, or rebuild proof.

## Evidence Inputs

- Queue closure: `subagents/ghidra-static-reaudit/queue/current/static-reaudit-queue.json`
- Function snapshot: `subagents/ghidra-static-reaudit/queue/current/functions_quality.tsv`
- Wave902 evidence:
  - `subagents/ghidra-static-reaudit/wave902-save-options-static-review/save-options-static-review-baseline.json`
  - `subagents/ghidra-static-reaudit/wave902-save-options-static-review/save-options-function-anchors.tsv`
  - `subagents/ghidra-static-reaudit/wave902-save-options-static-review/backup-summary.json`
- Canonical save docs:
  - `reverse-engineering/save-file/save-format.md`
  - `reverse-engineering/save-file/struct-layouts.md`
  - `reverse-engineering/save-file/career-graph.md`
  - `reverse-engineering/save-file/grade-system.md`
  - `reverse-engineering/save-file/goodies-system.md`
  - `reverse-engineering/save-file/kill-tracking.md`
- Binary owner docs:
  - `reverse-engineering/binary-analysis/functions/Career.cpp/_index.md`
  - `reverse-engineering/binary-analysis/functions/Career.cpp/CCareer__Load.md`
  - `reverse-engineering/binary-analysis/functions/Career.cpp/CCareer__Save.md`
  - `reverse-engineering/binary-analysis/functions/Controller.cpp/ControlBindings.md`
  - `reverse-engineering/binary-analysis/functions/FEPOptions.cpp/CFEPOptions__WriteDefaultOptionsFile.md`
  - `reverse-engineering/binary-analysis/functions/PauseMenu.cpp/CPauseMenu__ResumeGameAndPersistOptions.md`
- Product/tooling proof:
  - `OnslaughtCareerEditor.AppCore/BesFilePatcher.cs`
  - `OnslaughtCareerEditor.AppCore.Tests/SaveAnalyzerServiceTests.cs`
  - `OnslaughtCareerEditor.UiTests/SavePatchRegressionTests.cs`
  - `OnslaughtCareerEditor.UiTests/CliReadOnlyAndOptionsSafetyTests.cs`
- Verified read-only Ghidra project backup: `[maintainer-local-ghidra-backup-root]\BEA_20260526-093817_post_wave902_save_options_static_review_verified`

## Function Anchors

Wave902 checks 32 saved Ghidra rows from the current function-quality snapshot. Each row has a non-empty comment, a non-`undefined` signature, and no `param_N` debt.

| Group | Anchors |
| --- | --- |
| Core serializer | `CCareer__Load`, `CCareer__Save`, `CCareer__GetSaveSize` |
| Career update and graph | `CCareer__Update`, `CCareer__ReCalcLinks`, `CCareer__NodeArrayAt` |
| Goodies/ranks/kills | `CCareer__UpdateThingsKilled`, `CCareer__CountGoodies`, `CCareer__UpdateGoodieStates`, `CCareer__GetGradeFromRanking`, `CCareer__GetAndResetGoodieNewCount`, `CCareer__GetAndResetFirstGoodie`, `CCareer__GetGoodiePtr`, `CCareer__GetKillCounterTopByte_23F4`, `CCareer__GetKillCounterTopByte_23F8`, `CCareer__SetKillCounterTopByte_23F4`, `CCareer__SetKillCounterTopByte_23F8` |
| Options entries/tail | `OptionsTail_Write`, `OptionsTail_Read`, `OptionsEntries__FindById`, `OptionsEntries__InitDefaultDualBindingsTable`, `OptionsEntries__InitDefaultSingleBindingsTable`, `OptionsEntries__SetBindingSlot`, `Controls__ApplyPreset`, `Controls__DispatchRemap`, `ControlsUI__RenderBindingsList` |
| Frontend persistence | `CFEPLoadGame__DoLoad`, `CFEPOptions__WriteDefaultOptionsFile`, `CFEPOptions__SaveDefaultOptions`, `CPauseMenu__ResumeGameAndPersistOptions`, `CFEPMain__Process`, `Platform__AsyncSaveCareer` |

## What Remains Open

- Runtime save/load/menu observation in a copied BEA profile.
- Runtime controller remap/input behavior.
- Runtime Goodies wall animation and model-viewer behavior.
- Exact source-layout parity for every `CCareer`, options-entry, and frontend object field.
- Rebuild parity.

## Practical Result

For documentation and product work, save/options/career persistence can now be treated as the first post-100 static-closed system slice. Future corrections should come from contradictory runtime proof, source-layout reconciliation, or an explicit new Ghidra evidence pass, not from unresolved queue debt.

The current static-to-proof planning handoff for this slice is `save-options-controller-byte-preservation-proof-plan.md`. It is a copied-file byte-preservation proof plan for real `.bes` and `defaultoptions.bea` baselines only; it is not runtime save/load, menu/controller, Goodies wall, patch, visual-QA, Godot, rebuild-parity, or no-noticeable-difference proof.
