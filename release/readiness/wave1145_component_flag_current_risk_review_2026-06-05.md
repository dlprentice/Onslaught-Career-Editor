# Wave1145 Component Flag Current-Risk Readiness Note

Status: complete static read-only evidence
Date: 2026-06-05
Scope: `wave1145-component-flag-current-risk-review`

Wave1145 re-read eight PhysicsScript component flag current-risk rows with fresh Ghidra exports and made no mutation: no rename, signature change, comment/tag change, function-boundary change, executable-byte change, BEA launch, installed-game mutation, save mutation, or runtime-file mutation.

Probe token anchor: Wave1145; wave1145-component-flag-current-risk-review; 298/1179 = 25.28%; 8 current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 881; current risk candidates: 6166; PhysicsScript component flag current-risk review; fresh Ghidra export; component flag apply helpers; zero-comparison path; DAT_00855400; 0x005d856c; read-only review; no mutation; no Codex subagent; 0 / 0 / 0; 6411/6411 = 100.00%; CComponentFlag124__ApplyToComponentByName; CComponentFlag128__ApplyToComponentByName; CComponentFlag12C__ApplyToComponentByName; CComponentFlag198__ApplyToComponentByName; CComponentFlag114__ApplyToComponentByName; CComponentFlag19C__ApplyToComponentByName; CComponentFlag134__ApplyToComponentByName; CComponentFlag108__ApplyToComponentByName; G:\GhidraBackups\BEA_20260605-171711_post_wave1145_component_flag_current_risk_review_verified; G:\GhidraBackups\BEA_20260605-165322_post_wave1144_physics_unit_weapon_value_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.

Fresh evidence:

- `pre-metadata.tsv`: `8` rows, `targets=8 found=8 missing=0`.
- `pre-tags.tsv`: `8` rows, `missing=0`.
- `pre-xrefs.tsv`: `8` rows.
- `pre-instructions.tsv`: `608` instruction rows, `targets=8 missing=0`.
- `pre-decompile/index.tsv`: `8` rows, `targets=8 dumped=8 missing=0 failed=0`.
- Verified backup: `G:\GhidraBackups\BEA_20260605-171711_post_wave1145_component_flag_current_risk_review_verified`, `19` files, `175967111` bytes, `DiffCount=0`, `HashDiffCount=0`.
- Previous completed backup: `G:\GhidraBackups\BEA_20260605-165322_post_wave1144_physics_unit_weapon_value_current_risk_review_verified`.
- Codex subagent usage: none for this slice; Codex root selected and audited the component-flag tranche locally.

Reviewed rows:

| Address | Static read-back |
| --- | --- |
| `0x0043ce60 CComponentFlag124__ApplyToComponentByName` | DATA xref `0x005da9e8`; writes component record `+0x124` as `0` on the zero-comparison path and `1` otherwise. |
| `0x0043cf20 CComponentFlag128__ApplyToComponentByName` | DATA xref `0x005da9d4`; writes component record `+0x128` as `0` on the zero-comparison path and `1` otherwise. |
| `0x0043cfe0 CComponentFlag12C__ApplyToComponentByName` | DATA xref `0x005da984`; writes component record `+0x12c` as `0` on the zero-comparison path and `1` otherwise. |
| `0x0043d0a0 CComponentFlag198__ApplyToComponentByName` | DATA xref `0x005da95c`; writes component record `+0x198` as `0` on the zero-comparison path and `1` otherwise. |
| `0x0043d160 CComponentFlag114__ApplyToComponentByName` | DATA xref `0x005da948`; writes component record `+0x114` as `0` on the zero-comparison path and `1` otherwise. |
| `0x0043d220 CComponentFlag19C__ApplyToComponentByName` | DATA xref `0x005da934`; writes component record `+0x19c` as `0` on the zero-comparison path and `1` otherwise. |
| `0x0043d2e0 CComponentFlag134__ApplyToComponentByName` | DATA xref `0x005da920`; writes component record `+0x134` as `0` on the zero-comparison path and `1` otherwise. |
| `0x0043d3a0 CComponentFlag108__ApplyToComponentByName` | DATA xref `0x005da9ac`; writes component record `+0x108` as `0` on the zero-comparison path and `1` otherwise. |

Accounting after Wave1145:

- Static closure: `6411/6411 = 100.00%`.
- Static debt: `0 / 0 / 0`.
- Expanded post-100 static surface: `1560/1560 = 100.00%`.
- Wave911 focused: `812/1408 = 57.67%`.
- Wave911 top-500: `500/500 = 100.00%`.
- Wave1108 current focused accounting: `298/1179 = 25.28%`.
- Current risk candidates: 6166.
- Current focused candidates: 1178.
- Live regenerated current focused candidates: 1178.
- Remaining active focused work: 881.

This is static Ghidra evidence only. Runtime PhysicsScript behavior, runtime component flag behavior, serialized file-format completeness, mission-script outcomes, exact layouts, exact source-body identity, BEA patching behavior, gameplay outcomes, visual QA, and rebuild parity remain separate proof.
