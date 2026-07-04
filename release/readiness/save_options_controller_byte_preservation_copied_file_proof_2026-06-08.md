# Save / Options Controller Byte-Preservation Copied-File Proof Readiness Note

Status: copied-file byte-preservation proof complete, not runtime proof
Date: 2026-06-08
Scope: `save-options-controller-byte-preservation-copied-file`

This readiness note records a public-safe copied-file proof for the save/options/controller byte-preservation lane. It is not a new static re-audit wave, not a runtime test, not a screenshot/capture proof, not a BEA patch, not a Godot slice, not a save synthesis workflow, and not a rebuild parity claim.

Primary public artifacts:

- `reverse-engineering/binary-analysis/save-options-controller-byte-preservation-copied-file-proof.md`
- `reverse-engineering/binary-analysis/save-options-controller-byte-preservation-copied-file.v1.json`
- `tools/save_options_controller_byte_preservation_copied_file_probe.py`
- Prior plan: `reverse-engineering/binary-analysis/save-options-controller-byte-preservation-proof-plan.md`

Current static closeout remains unchanged:

- Static Ghidra function-quality closure: `6411/6411 = 100.00%`.
- Static debt: `0 / 0 / 0`.
- Expanded post-100 static surface: `1560/1560 = 100.00%`.
- Active current-risk focused accounting: `1179/1179 = 100.00%`.
- Remaining active focused work: `0`.
- Latest verified Ghidra backup remains `[maintainer-local-ghidra-backup-root]\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified`.

Proof evidence was generated under ignored private evidence root `subagents/static-to-proof/save-options-controller-byte-preservation-copied-file-proof/`. Public notes and schema intentionally omit private source paths and source hashes.

Readiness result:

| Check | Result |
| --- | --- |
| Real copied baselines | One career `.bes` and one `defaultoptions.bea` copied into ignored private evidence. |
| Container | `10004` bytes (`0x2714`), version word `0x4BD1`. |
| True-view rule | `file_offset = 0x0002 + career_offset`. |
| No-op career copy | `DiffCount=0`. |
| No-op defaultoptions copy | `DiffCount=0`. |
| Scoped career edit | Aircraft kill counter lower-24 payload allowlist `0x23F6-0x23F8`; observed changed offset `0x23F6`; unexpected diff count `0`. |
| Metadata byte | `0x23F9` preserved. |
| Options entries | `0x24BE-0x26BD` unchanged. |
| Options tail | `0x26BE-0x2713` unchanged. |
| Legacy traps | `0x23A4`, `0x22D4`, and `0x240C` not touched. |

Boundary:

- This proves copied-file byte-preservation behavior only.
- It does not prove runtime save/load behavior.
- It does not prove runtime defaultoptions boot behavior.
- It does not prove runtime menu behavior.
- It does not prove runtime controller remap/input behavior.
- It does not prove runtime Goodies wall behavior.
- It does not prove exact source-layout parity.
- It does not prove BEA patching behavior.
- It does not prove visual QA, Godot parity, rebuild parity, or no-noticeable-difference parity.
