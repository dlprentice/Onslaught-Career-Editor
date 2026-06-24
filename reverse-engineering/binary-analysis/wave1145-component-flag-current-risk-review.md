# Wave1145 Component Flag Current-Risk Review

Status: complete static read-only evidence
Date: 2026-06-05
Scope: `wave1145-component-flag-current-risk-review`

Wave1145 re-read eight current-risk PhysicsScript component flag apply helpers from the Wave1108 current focused denominator. The review used fresh Ghidra metadata, tag, xref, instruction, and decompile exports. No Ghidra mutation was warranted.

## Coverage

Each row walks the global component list at `DAT_00855400` by `componentName`, compares the scalar value at `this+0x8` with the zero constant at `0x005d856c`, and writes `0` on the zero-comparison path or `1` otherwise to the matched component record field. Exact flag meaning, concrete component layout, runtime PhysicsScript application behavior, and rebuild parity remain unproven.

| Address | Component field | DATA xref |
| --- | --- | --- |
| `0x0043ce60 CComponentFlag124__ApplyToComponentByName` | `+0x124` | `0x005da9e8` |
| `0x0043cf20 CComponentFlag128__ApplyToComponentByName` | `+0x128` | `0x005da9d4` |
| `0x0043cfe0 CComponentFlag12C__ApplyToComponentByName` | `+0x12c` | `0x005da984` |
| `0x0043d0a0 CComponentFlag198__ApplyToComponentByName` | `+0x198` | `0x005da95c` |
| `0x0043d160 CComponentFlag114__ApplyToComponentByName` | `+0x114` | `0x005da948` |
| `0x0043d220 CComponentFlag19C__ApplyToComponentByName` | `+0x19c` | `0x005da934` |
| `0x0043d2e0 CComponentFlag134__ApplyToComponentByName` | `+0x134` | `0x005da920` |
| `0x0043d3a0 CComponentFlag108__ApplyToComponentByName` | `+0x108` | `0x005da9ac` |

## Evidence Counts

- Primary exports: `8` metadata rows, `8` tag rows, `8` xref rows, `608` instruction rows, and `8` decompile rows.
- Backup: `G:\GhidraBackups\BEA_20260605-171711_post_wave1145_component_flag_current_risk_review_verified`; `19` files, `175967111` bytes, `DiffCount=0`, `HashDiffCount=0`.
- Previous completed backup: `G:\GhidraBackups\BEA_20260605-165322_post_wave1144_physics_unit_weapon_value_current_risk_review_verified`.
- Codex subagent usage: none for this slice; Codex root selected the coherent component-flag tranche from the current-risk denominator and audited the fresh exports locally.

## Progress

- Static Ghidra function-quality closure: `6411/6411 = 100.00%`.
- Static debt: `0 / 0 / 0` commentless / exact-undefined / `param_N`.
- Expanded post-100 static surface: `1560/1560 = 100.00%`.
- Wave911 focused historical residual: `812/1408 = 57.67%`.
- Wave911 top-500: `500/500 = 100.00%`.
- Wave1108 current focused accounting: `298/1179 = 25.28%`.
- Current risk candidates: 6166.
- Current focused candidates: 1178.
- Live regenerated current focused candidates: 1178.
- Remaining active focused work: 881.

## Boundary

Wave1145 is static Ghidra evidence only. It does not prove runtime PhysicsScript behavior, runtime component flag behavior, serialized file-format completeness, mission-script outcomes, exact layouts, exact source-body identity, BEA patching behavior, gameplay outcomes, visual QA, or rebuild parity.

Probe token anchor: Wave1145; wave1145-component-flag-current-risk-review; 298/1179 = 25.28%; 8 current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 881; current risk candidates: 6166; PhysicsScript component flag current-risk review; fresh Ghidra export; component flag apply helpers; zero-comparison path; DAT_00855400; 0x005d856c; read-only review; no mutation; no Codex subagent; 0 / 0 / 0; 6411/6411 = 100.00%; CComponentFlag124__ApplyToComponentByName; CComponentFlag128__ApplyToComponentByName; CComponentFlag12C__ApplyToComponentByName; CComponentFlag198__ApplyToComponentByName; CComponentFlag114__ApplyToComponentByName; CComponentFlag19C__ApplyToComponentByName; CComponentFlag134__ApplyToComponentByName; CComponentFlag108__ApplyToComponentByName; G:\GhidraBackups\BEA_20260605-171711_post_wave1145_component_flag_current_risk_review_verified; G:\GhidraBackups\BEA_20260605-165322_post_wave1144_physics_unit_weapon_value_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.
