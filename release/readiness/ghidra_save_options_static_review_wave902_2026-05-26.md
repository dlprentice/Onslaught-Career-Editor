# Ghidra Save / Options Static Review Wave902 Readiness Note

Status: complete read-only static review evidence
Date: 2026-05-26
Scope: `save-options-static-review-wave902`

Wave902 reviewed save/options/career persistence after the loaded Ghidra function-quality queue reached `6113/6113 = 100.00%`. The pass records `static-closed save/options/career` for static file-layout and persistence evidence. It made no Ghidra metadata mutation, no executable-byte change, no save mutation, and no BEA launch.

Representative anchors:

| Area | Evidence |
| --- | --- |
| Save container | Fixed `10004`-byte `.bes`/`defaultoptions.bea` shape, version `0x4BD1`, true-view career base `0x0002`, `CCareer__Load`, `CCareer__Save`, and `CCareer__GetSaveSize`. |
| Career data | 100 nodes, 200 links, 300 Goodie slots with 233 displayable entries, raw float ranks, and packed kill counters beginning at `0x23F6`. |
| Options persistence | Options flags at `0x249E`, entries at `0x24BE`, `0x56`-byte tail, `OptionsTail_Write`, `OptionsTail_Read`, and options-entry/control-binding helpers. |
| Frontend persistence | `CFEPLoadGame__DoLoad`, `CFEPOptions__SaveDefaultOptions`, `CFEPOptions__WriteDefaultOptionsFile`, `CPauseMenu__ResumeGameAndPersistOptions`, `CFEPMain__Process`, and `Platform__AsyncSaveCareer`. |
| Product alignment | `BesFilePatcher` validates size/version, rejects in-place patch output, preserves unknown/reserved regions, preserves non-displayable Goodies, scopes options copy, and tests true-view offsets plus options safety behavior. |

Read-only evidence:

- Queue remains closed: `6113` total, `6113` commented, `0` commentless, `0` exact-undefined signatures, `0` `param_N`.
- Function-anchor export: 32 save/options/career/frontend persistence rows, all comment-backed and signature-clean.
- Baseline evidence: `subagents/ghidra-static-reaudit/wave902-save-options-static-review/save-options-static-review-baseline.json`.
- Function anchors: `subagents/ghidra-static-reaudit/wave902-save-options-static-review/save-options-function-anchors.tsv`.
- Verified backup: `G:\GhidraBackups\BEA_20260526-093817_post_wave902_save_options_static_review_verified`, 19 files, 173247367 bytes, `DiffCount=0`.

What this proves:

- Save/options/career persistence is static-closed for public docs and product/tooling alignment under the current evidence set.
- The static binary rows, save-format docs, AppCore constants, and automated tests agree on the fixed file shape and true-view offsets.

What remains unproven:

- Runtime save/load/menu behavior.
- Runtime controller remap/input behavior.
- Runtime Goodies wall animation and model-viewer behavior.
- Exact source-layout identity for every field.
- Rebuild parity.
