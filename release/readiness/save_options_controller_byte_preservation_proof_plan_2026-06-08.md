# Save / Options Controller Byte-Preservation Proof Plan Readiness Note

Status: proof plan complete, not runtime proof
Date: 2026-06-08
Scope: `save-options-controller-byte-preservation-proof-plan`

This readiness note records a public-safe static-to-proof planning slice for save/options/controller byte preservation. It is not a new static re-audit wave, not a runtime test, not a screenshot/capture proof, not a BEA patch, not a Godot slice, not a save synthesis workflow, and not a rebuild parity claim.

Primary static sources: `save-options-static-review-2026-05-26.md`, `save-format.md`, `struct-layouts.md`, and `ControlBindings.md`. The plan records copied-file guardrails, true-dword-view offsets, byte-preservation requirements, options/defaultoptions separation, controller-layout unknowns, and stop conditions before any executable proof work can start.

Current static closeout remains unchanged:

- Static Ghidra function-quality closure: `6411/6411 = 100.00%`.
- Static debt: `0 / 0 / 0`.
- Expanded post-100 static surface: `1560/1560 = 100.00%`.
- Active current-risk focused accounting: `1179/1179 = 100.00%`.
- Remaining active focused work: `0`.
- Wave911 focused remains historical-retired/non-reconstructable at `812/1408 = 57.67%`.

Static source evidence:

- Wave902 (`save-options-static-review-wave902`): fixed `10004`-byte save/options container, version `0x4BD1`, true-view base `0x0002`, kill counters at `0x23F6`, options entries at `0x24BE`, `0x56`-byte tail, `CCareer__Load`, `CCareer__Save`, `OptionsTail_Write`, `OptionsTail_Read`, `CFEPOptions__WriteDefaultOptionsFile`, and `CPauseMenu__ResumeGameAndPersistOptions`. Verified backup: `G:\GhidraBackups\BEA_20260526-093817_post_wave902_save_options_static_review_verified`.
- Wave1044 (`career-controller-residual-review-wave1044`; package script `test:ghidra-career-controller-residual-review-wave1044`): retained career/controller residual read-back evidence including `CCareer__SetSlot` and controller lifecycle/record/playback static anchors. Readiness note: `release/readiness/ghidra_career_controller_residual_review_wave1044_2026-06-01.md`.
- Wave1212 (`wave1212-options-detail-tweak-current-risk-review`): `9` metadata rows, `9` tag rows, `64 xref rows`, `175 instruction rows`, and `9 decompile rows`. Verified backup: `G:\GhidraBackups\BEA_20260607-065722_post_wave1212_options_detail_tweak_current_risk_review_verified`.

Representative anchors:

| Surface | Static anchor |
| --- | --- |
| Container | `10004` bytes, version `0x4BD1` |
| True dword view | `file_offset = 0x0002 + career_offset` |
| Core serializer | `CCareer__Load`, `CCareer__Save`, `CCareer__GetSaveSize` |
| Goodies | `0x1F46` `CGoodie[300]`, displayable `0-232`, preserve `233-299` |
| Kill counters | `0x23F6` five packed dwords, preserve top-byte metadata |
| Tech slots | `0x240A` `mSlots[32]`, source-used slots `0-255` |
| Options entries | `0x24BE-0x26BD`, observed `N=16`, `0x20` bytes each |
| Options tail | `0x26BE-0x2713`, final `0x56` bytes via `OptionsTail_Write` / `OptionsTail_Read` |
| defaultoptions separation | `CCareer__Load(..., flag=0)` applies entries/tail; `.bes` load flag `1` skips immediate entries/tail application |
| Frontend persistence | `CFEPLoadGame__DoLoad`, `CFEPOptions__WriteDefaultOptionsFile`, `CPauseMenu__ResumeGameAndPersistOptions`, `Platform__AsyncSaveCareer` |
| Controller config | `mControllerConfigurationNum[0/1]` values `1..4` |
| Direct binding patch caveat | planned direct binding proofs must force or record `g_ControlSchemeIndex=0` |

Proof-plan boundaries:

- The plan is limited to copied real `.bes` and `defaultoptions.bea` baselines.
- Any future proof must validate size/version, no-op byte preservation, scoped diff allowlists, true-view offsets, and defaultoptions-vs-career-load separation.
- Any future proof must preserve or explicitly record `N=16`, `0x24BE-0x26BD`, `0x26BE-0x2713`, `flag=0 applies options`, `flag=1 skips options`, `mControllerConfigurationNum 1..4`, and `g_ControlSchemeIndex=0` requirements for direct binding patches.
- Any future proof must preserve unknown bytes, padding, reserved Goodies, `CCareerNode.state`, packed kill metadata, options entries, and options tail unless they are the selected target row.
- The plan explicitly rejects legacy aligned-view write traps such as `0x23A4`, `0x22D4`, and `0x240C`.
- The plan explicitly does not include runtime save/load behavior, runtime menu behavior, runtime controller remap/input behavior, runtime Goodies wall behavior, BEA patching behavior, visual QA, rebuild parity, or no-noticeable-difference parity.

No runtime save/load behavior, runtime defaultoptions boot behavior, runtime menu behavior, runtime controller remap/input behavior, runtime Goodies wall behavior, exact source-layout parity, BEA patching behavior, visual QA, Godot parity, rebuild parity, or no-noticeable-difference parity claim is made.
