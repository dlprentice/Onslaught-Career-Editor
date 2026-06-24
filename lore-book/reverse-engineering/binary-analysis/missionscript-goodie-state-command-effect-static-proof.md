# MissionScript Goodie State Command-Effect Static Proof

Status: static Goodie state command-effect schema proof complete, not runtime proof
Last updated: 2026-06-08
Scope: `missionscript-goodie-state-command-effect-static`
Artifact: `missionscript-goodie-state-command-effect-static-proof.md`; schema: `missionscript-goodie-state-command-effect.v1.json`

This proof converts saved retail Ghidra evidence from Wave579, Wave864, and Wave903 plus the canonical save-file Goodie mapping into a machine-checkable Goodie state command-effect map at `missionscript-goodie-state-command-effect.v1.json`. It is the next narrow IScript command-effect child lane after the completed slot, objective/outcome, and message/audio proofs.

Static closeout remains unchanged:

- Static Ghidra function-quality closure: `6411/6411 = 100.00%`.
- Static debt: `0 / 0 / 0` commentless, exact-undefined, and `param_N` rows.
- Expanded post-100 static surface: `1560/1560 = 100.00%`.
- Active current-risk focused accounting: `1179/1179 = 100.00%`.
- Remaining active focused work: `0`.
- Latest verified Ghidra backup remains `G:\GhidraBackups\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified`.

## Schema Result

| Surface | Static result |
| --- | --- |
| Descriptor slots | The descriptor schema records `SetGoodieState` index `118` at `0x0064ebd0` with symbol `s_SetGoodieState_0064f380`, and `GetGoodieState` index `119` at `0x0064ec10` with symbol `s_GetGoodieState_0064f370`. |
| Descriptor raw-entry boundary | The schema preserves raw entry values such as `&LAB_00533b30` and `IScript__SetGoodieState` as static table evidence only. Exact command descriptor field layout and one-to-one command-handler mapping remain bounded, not proven. |
| Goodie state handlers | Wave579 saved `0x00533a70 IScript__SetGoodieState` and `0x00533aa0 IScript__GetGoodieState` with fixed three-stack-argument command ABI signatures. `SetGoodieState` writes `g_Career_mGoodies[index-1]`; `GetGoodieState` reads `g_Career_mGoodies[index-1]`, allocates an 8-byte integer result, installs vtable `0x005e4af8`, and writes `out_result`. |
| Save-file bridge | The same Goodie array is documented as `300` 4-byte entries at global address `0x00662564` and true-view file base `0x1F46`. script index N maps to save Goodie index N-1 and file offset `0x1F46 + (N - 1) * 4`. Displayable entries are `0-232`; entries `233-299` are reserved/preserve rows. |
| State values | `0` = `GS_UNKNOWN`, `1` = `GS_INSTRUCTIONS`, `2` = `GS_NEW`, and `3` = `GS_OLD`. |
| AddScore boundary | `AddScore` appears as descriptor/name context only at index `84`, record `0x0064e350`, symbol `s_AddScore_0064f5c4`, and raw entry `IScript__Unk_00534410`; later objective/outcome evidence names the same raw address as `0x00534410 IScript__SecondaryObjectiveComplete`. This proof does not promote an `AddScore` handler-body bridge; it remains deferred from this static result. |

Evidence rows consumed by the schema:

| Evidence | Count |
| --- | ---: |
| Wave579 metadata/tag/xref/decompile rows | `6` / `6` / `6` / `6` |
| Wave579 instruction rows and vtable rows | `1326` / `24` |

Backups already verified by their original waves:

- Wave579: `G:\GhidraBackups\BEA_20260519-041839_post_wave579_iscript_slot_goodie_verified`
- Latest static closeout backup: `G:\GhidraBackups\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified`

## Why This Matters

This gives clean-room MissionScript planning a bounded Goodie-state bridge: descriptor names, saved IScript Goodie handlers, global Goodie state storage, true-view save offsets, and the known 1-based MissionScript index convention. It turns the earlier Wave579 handler read-back and save docs into a reusable contract for later interpreter, save/career, Goodies, or mission-script slices.

The proof intentionally keeps `AddScore` descriptor/name evidence separate from Goodie-state handler evidence and preserves the `0x00534410 IScript__SecondaryObjectiveComplete` alias boundary. It also keeps runtime mission execution, live script loading, save writes, frontend Goodies wall behavior, and visible unlock results out of scope until copied/app-owned proof explicitly runs.

## Claim Boundary

This proves static Goodie state command-effect accounting from saved retail Ghidra evidence and canonical save-file documentation. It does not prove runtime MissionScript execution, runtime command effects, runtime Goodie state mutation, runtime save behavior, runtime Goodies wall behavior, live loose-MSL loading, packed-vs-loose script selection, exact command descriptor layout, exact arity, exact argument type schema, exact `CCareer` layout, `AddScore` handler-body proof, BEA patching behavior, visual QA, Godot parity, rebuild parity, or no-noticeable-difference parity.
