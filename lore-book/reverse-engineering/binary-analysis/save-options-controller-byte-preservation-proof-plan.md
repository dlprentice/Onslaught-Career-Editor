# Save / Options Controller Byte-Preservation Proof Plan

Status: active public-safe proof plan, not runtime proof
Last updated: 2026-06-08
Scope: `save-options-controller-byte-preservation-proof-plan`

This plan is the next selected static-to-proof slice from `roadmap/static-to-proof-rebuild-transition-backlog.md` after the Weapon / projectile spawn handoff proof-plan slice. It converts the saved save/options/controller static evidence into a bounded proof design for copied real `.bes` and `defaultoptions.bea` buffers.

This plan does not launch BEA, mutate Ghidra, mutate the installed game, patch an executable, capture screenshots, start Godot work, synthesize save buffers from scratch, or claim runtime menu behavior, runtime controller behavior, runtime Goodies wall behavior, patch behavior, rebuild parity, or no-noticeable-difference parity.

The plan records copied-file guardrails, true-dword-view offsets, byte-preservation requirements, options/defaultoptions separation, controller-layout unknowns, and stop conditions before any executable proof work can start.

## Static Authority

Current static closeout remains unchanged:

- Static Ghidra function-quality closure: `6411/6411 = 100.00%`.
- Static debt: `0 / 0 / 0` commentless, exact-undefined, and `param_N` rows.
- Expanded post-100 static surface: `1560/1560 = 100.00%`.
- Active current-risk focused accounting: `1179/1179 = 100.00%`.
- Remaining active focused work: `0`.
- Wave911 focused remains historical-retired/non-reconstructable at `812/1408 = 57.67%`; it is not the active completion gate.

The percentage front door remains `reverse-engineering/binary-analysis/static-reaudit-measurement-register.md` and `reverse-engineering/binary-analysis/static-reaudit-progress.json`. This proof plan does not create a new static RE percentage.

Primary static contract sources:

- `reverse-engineering/binary-analysis/save-options-static-review-2026-05-26.md`
- `reverse-engineering/save-file/save-format.md`
- `reverse-engineering/save-file/struct-layouts.md`
- `reverse-engineering/binary-analysis/functions/Career.cpp/_index.md`
- `reverse-engineering/binary-analysis/functions/Controller.cpp/ControlBindings.md`

Relevant retained evidence:

- Wave902 save/options static review (`save-options-static-review-wave902`): static-closed save/options/career surface over the fixed `10004`-byte container, version `0x4BD1`, true-view base `0x0002`, kill counters at `0x23F6`, options entries at `0x24BE`, `0x56`-byte options tail, `CCareer__Load`, `CCareer__Save`, `OptionsTail_Write`, `OptionsTail_Read`, `CFEPOptions__WriteDefaultOptionsFile`, and `CPauseMenu__ResumeGameAndPersistOptions`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260526-093817_post_wave902_save_options_static_review_verified`.
- Wave1044 career/controller residual review (`career-controller-residual-review-wave1044`; package script `test:ghidra-career-controller-residual-review-wave1044`): retained Ghidra read-back for career/controller residual rows including `CCareer__SetSlot` and controller lifecycle/record/playback static anchors. Readiness note: `release/readiness/ghidra_career_controller_residual_review_wave1044_2026-06-01.md`.
- Wave1212 options/detail/tweak current-risk review (`wave1212-options-detail-tweak-current-risk-review`): `9` metadata rows, `9` tag rows, `64 xref rows`, `175 instruction rows`, and `9 decompile rows`; context exports covered `PauseMenu__Init`, `CLIParams__ParseCommandLine`, `CReconnectInterface__ctor`, `CVideoDetailLevel__GetCurrentPresetFromItems`, `CRTMesh__SetQualityLevel`, `CMenuItem__Destructor_Thunk`, and `CDXMemoryManager__Free`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260607-065722_post_wave1212_options_detail_tweak_current_risk_review_verified`.

## Static Anchors

The proof plan is built around saved retail Ghidra evidence, canonical save docs, and product/tooling safety rules. Stuart source labels are useful for planning, but retail `.bes` and `defaultoptions.bea` bytes remain layout authority.

| Surface | Static anchor |
| --- | --- |
| Save container | Fixed `10004` bytes (`0x2714`) with 16-bit version word `0x4BD1`. |
| True dword view | Retail `BEA.exe` bulk-copies `CCareer` bytes at `file + 0x0002`; use `file_offset = 0x0002 + career_offset`. |
| Core serializer | `CCareer__Load`, `CCareer__Save`, and `CCareer__GetSaveSize` define the file-size/version/copy boundary. |
| Career graph | `CCareerNode[100]`, `CCareerNodeLink[200]`, `CCareer__ReCalcLinks`, `CCareer__NodeArrayAt`, and `Career_IsWorldUnlocked` define graph/link behavior statically. |
| Goodies | `CGoodie[300]` begins at `0x1F46`; displayable slots are `0-232`, while `233-299` are reserved/preserve rows. |
| Ranks | `CCareerNode +0x3C` stores raw IEEE-754 rank bits; S/A/B/C/D/E/NONE constants are documented in `save-format.md` and `save-ranks.md`. |
| Kill counters | Five packed dwords begin at `0x23F6`; preserve top-byte metadata and change only `(kills & 0x00FFFFFF)` when intentionally editing counts. |
| Tech slots | `mSlots[32]` begins at `0x240A` in true view; only slots `0-255` are source-used, and slot IDs are script-defined persistent flags. |
| Fixed career tail | `0x248A` through `0x24BA` includes career-in-progress, sound/music volumes, cheat-gated god-mode toggle state, invert-Y flags, vibration flags, and controller configuration numbers. |
| Options entries | `0x24BE-0x26BD` contains observed `N=16` options entries, each `0x20` bytes with two binding slots per action. |
| Options tail | `0x26BE-0x2713` is the final `0x56` bytes written/read by `OptionsTail_Write` and `OptionsTail_Read`, including mouse, language, detail, D3D, screen, audio, and landscape-detail globals. |
| defaultoptions separation | `CCareer__Load(..., flag=0)` applies options entries/tail on `defaultoptions.bea` load; normal career `.bes` load uses `flag=1` and skips immediate options-entry/tail application. |
| Frontend persistence | `CFEPLoadGame__DoLoad`, `CFEPOptions__WriteDefaultOptionsFile`, `CFEPOptions__SaveDefaultOptions`, `CPauseMenu__ResumeGameAndPersistOptions`, `CFEPMain__Process`, and `Platform__AsyncSaveCareer` tie frontend save/options flows to serializer/defaultoptions paths statically. |
| Controller configuration | `mControllerConfigurationNum[0/1]` values `1..4` select controller layouts; current tooling should preserve raw values unless a scoped proof edits them. |
| Direct binding patch caveat | Direct options-entry binding patches must account for `g_ControlSchemeIndex`; planned direct binding proofs should force or record `g_ControlSchemeIndex=0` rather than assuming remap behavior. |

## Planned Byte-Preservation Proof Shape

The first executable proof after this plan should be copied-file only. It must never synthesize a `.bes` or `.bea` buffer from scratch.

| Row | Planned proof item | Required evidence | Public-safe result |
| --- | --- | --- | --- |
| 1 | Baseline copy guard | Copy one real `.bes` and one real `defaultoptions.bea` into an app-owned scratch/output root. | Sanitized source labels, copied output paths under an ignored artifact root, and file hashes. |
| 2 | Container validation | Verify each copied file is exactly `10004` bytes and starts with version word `0x4BD1`. | Size/version PASS rows. |
| 3 | No-op preservation | Round-trip read-only analysis and no-op write path without changing bytes. | `DiffCount=0` or equivalent byte-equality proof. |
| 4 | Scoped career edit | Pick one safe true-view field family, such as a rank or lower-24-bit kill payload, and write only the expected bytes in a copied `.bes`. | Explicit allowlist of changed offsets and preserved unknown/tail bytes. |
| 5 | Scoped options/defaultoptions edit | Pick one safe options or controller field family only if the proof can keep `.bes` load semantics separate from `defaultoptions.bea` boot semantics. | Separate `.bes` and `defaultoptions.bea` expected-diff rows. |
| 6 | Metadata preservation | Preserve kill top-byte metadata, non-displayable Goodies `233-299`, `CCareerNode.state`, options entries, and options tail unless they are the selected target. | Byte-range preservation table. |
| 7 | True-view enforcement | Reject any legacy aligned-view offset write, including historical traps at `0x23A4`, `0x22D4`, and `0x240C`. | Negative-test rows or explicit guard text. |
| 8 | Stop conditions | Stop on wrong size, wrong version, unexpected diff outside allowlist, missing baseline, ambiguous field, any need to touch the installed game, or private artifact leakage. | Documented blocked/deferred status instead of widening scope. |
| 9 | Rebuild handoff | Translate proven byte behavior into a save/options codec contract only after the future proof result says which rows were observed. | Static codec notes with runtime/menu/controller gaps marked. |

## Copied-File Guardrails

Any later proof execution must:

- Start from copied real `.bes` and `defaultoptions.bea` baselines.
- Never synthesize a save/options buffer from scratch.
- Never mutate the installed Steam game directory or original files.
- Preserve file size, unknown bytes, padding, reserved Goodies, `CCareerNode.state`, packed kill metadata, options entries, and options tail unless a selected target row says otherwise.
- Use true-dword-view offsets only.
- Preserve or explicitly record `N=16`, options entry range `0x24BE-0x26BD`, tail range `0x26BE-0x2713`, `flag=0 applies options`, `flag=1 skips options`, `mControllerConfigurationNum 1..4`, and `g_ControlSchemeIndex=0` requirements for direct binding patches.
- Keep generated outputs, hashes, diffs, and any private baseline paths under ignored evidence or app-owned artifact roots.
- Keep public notes aggregate and sanitized.

## Not Claimed

This plan is a static-to-proof planning artifact only. It does not prove:

- Runtime save/load behavior.
- Runtime defaultoptions boot behavior.
- Runtime menu behavior.
- Runtime controller remap/input behavior.
- Runtime Goodies wall animation or model-viewer behavior.
- Exact source-layout parity for every `CCareer`, options-entry, frontend, controller, or tail field.
- BEA patching behavior.
- Visual QA.
- Godot parity.
- Rebuild parity.
- No-noticeable-difference parity.

## Exit Gate For This Planning Slice

This planning slice is complete only when:

- This document and its lore-book mirror match.
- `roadmap/static-to-proof-rebuild-transition-backlog.md`, `reverse-engineering/binary-analysis/mapped-systems.md`, `reverse-engineering/binary-analysis/_index.md`, `reverse-engineering/RE-INDEX.md`, and `reverse-engineering/save-file/_index.md` point to this plan.
- `release/readiness/save_options_controller_byte_preservation_proof_plan_2026-06-08.md` records the same claim boundaries.
- `tools/save_options_controller_byte_preservation_proof_plan_probe.py --check` passes.
- Static closeout probes still pass without changing `static-reaudit-progress.json` or `static-reaudit-current-risk-ledger.json`.
