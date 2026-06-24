# Save / Options Controller Byte-Preservation Copied-File Proof

Status: copied-file byte-preservation proof complete, not runtime proof
Last updated: 2026-06-08
Scope: `save-options-controller-byte-preservation-copied-file`
Artifact: `save-options-controller-byte-preservation-copied-file-proof.md`; schema: `save-options-controller-byte-preservation-copied-file.v1.json`

This proof executes the first bounded child lane from `save-options-controller-byte-preservation-proof-plan.md`. It uses copied real save/options baselines inside the ignored evidence root `subagents/static-to-proof/save-options-controller-byte-preservation-copied-file-proof/`, validates the fixed container shape, proves no-op byte preservation, and proves one scoped true-view career edit stays inside the expected byte allowlist.

Static closeout remains unchanged:

- Static Ghidra function-quality closure: `6411/6411 = 100.00%`.
- Static debt: `0 / 0 / 0` commentless, exact-undefined, and `param_N` rows.
- Expanded post-100 static surface: `1560/1560 = 100.00%`.
- Active current-risk focused accounting: `1179/1179 = 100.00%`.
- Remaining active focused work: `0`.
- Latest verified Ghidra backup remains `G:\GhidraBackups\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified`.

## Proof Result

| Surface | Result |
| --- | --- |
| Baselines | One real career `.bes` baseline and one real `defaultoptions.bea` baseline were copied into ignored private evidence. Public schema omits source paths and source hashes. |
| Container validation | Copied career/defaultoptions buffers are `10004` bytes (`0x2714`) and start with version word `0x4BD1`. |
| True view | The proof uses `file_offset = 0x0002 + career_offset`; legacy aligned-view traps are rejected. |
| No-op preservation | Career no-op copy `DiffCount=0`; defaultoptions no-op copy `DiffCount=0`. |
| Scoped edit | A copied career-save edit changes the Aircraft kill counter lower-24 payload at `0x23F6-0x23F8`; observed changed offset was `0x23F6`. |
| Metadata preservation | The kill-counter metadata byte at `0x23F9` is preserved. |
| Range preservation | Reserved Goodies, tech slots, options entries `0x24BE-0x26BD`, and options tail `0x26BE-0x2713` are unchanged. |
| Negative guards | Legacy aligned-view trap offsets `0x23A4`, `0x22D4`, and `0x240C` were not touched. |

The machine-readable schema records the same result in `save-options-controller-byte-preservation-copied-file.v1.json`.

## Why This Matters

This is the first concrete save/options proof after the static plan. It shows that the documented true-view offsets can support a narrow copied-file codec operation without resizing the container, changing unknown bytes, clobbering the options block, or touching historical trap offsets. That is directly useful for clean-room save/options codec work, WinUI/AppCore patch safety, and later runtime proof planning.

## Claim Boundary

This proves copied-file byte-preservation behavior only. It does not prove runtime save/load behavior, runtime defaultoptions boot behavior, runtime menu behavior, runtime controller remap/input behavior, runtime Goodies wall behavior, exact source-layout parity, BEA patching behavior, visual QA, Godot parity, rebuild parity, or no-noticeable-difference parity.
