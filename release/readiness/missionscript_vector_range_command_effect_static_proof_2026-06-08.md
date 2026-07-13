# MissionScript Vector/Range Command-Effect Static Proof Readiness Note

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 semantic revalidation:** Historical record; `0x005345d0` comment correction; `0x00534b80` comment correction; `0x00534c10` comment correction; `0x00534ca0` comment correction. The original text below remains provenance rather than current semantic authority. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); exact records are in `reverse-engineering/binary-analysis/ghidra-full-reaudit-corrections-2026-07-13.json` and `reverse-engineering/binary-analysis/ghidra-targeted-revalidation-corrections-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Status: static vector/range command-effect schema proof complete, not runtime proof
Date: 2026-06-08
Scope: `missionscript-vector-range-command-effect-static`

This readiness note records the static proof slice for `missionscript-vector-range-command-effect-static-proof.md` and `missionscript-vector-range-command-effect.v1.json`.

Static closeout remains unchanged:

- Static Ghidra function-quality closure: `6411/6411 = 100.00%`.
- Static debt: `0 / 0 / 0` commentless, exact-undefined, and `param_N` rows.
- Expanded post-100 static surface: `1560/1560 = 100.00%`.
- Active current-risk focused accounting: `1179/1179 = 100.00%`.
- Remaining active focused work: `0`.
- Latest verified Ghidra backup remains `[maintainer-local-ghidra-backup-root]\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified`.

Representative anchors:

| Address | Static evidence |
| --- | --- |
| `0x005345d0 IScript__GetVectorLength` | Reads vector slot `+0x44`, computes `sqrt(x*x+y*y+z*z)`, and returns float vtable `0x005e4ea4`. |
| `0x005347b0 IScript__CheckValueInRange` | Reads value/min/max through float getter slot `+0x34`, accepts ascending and descending bounds, and returns bool vtable context `0x005e4d50`. |
| `0x00534b80 IScript__GetVectorX` | Reads vector slot `+0x44`, copies component `+0`, and returns float vtable `0x005e4ea4`. |
| `0x00534c10 IScript__GetVectorY` | Reads vector slot `+0x44`, copies component `+4`, and returns float vtable `0x005e4ea4`. |
| `0x00534ca0 IScript__GetVectorZ` | Reads vector slot `+0x44`, copies component `+8`, and returns float vtable `0x005e4ea4`. |

Read-back evidence:

- Wave581 post exports verified `5` metadata rows, `5` tag rows, `5` xref rows, `3545` instruction rows, `5` decompile rows, and `24` vtable rows.
- Descriptor context preserves raw records `0x0064dc50`, `0x0064dc90`, `0x0064dcd0`, `0x0064dd10`, `0x0064dd50`, `0x0064dd90`, `0x0064e850`, `0x0064e890`, and `0x0064e950` as raw static table evidence only.
- A copied loose-MSL non-comment scan found no direct non-comment loose-MSL rows for `GetVectorLength`, `CheckValueInRange`, `GetVectorX`, `GetVectorY`, `GetVectorZ`, or `Magnitude`.
- Wave581 backup: `[maintainer-local-ghidra-backup-root]\BEA_20260519-075959_post_wave581_iscript_vector_range_verified`, `19` files, `160500615` bytes, `DiffCount=0`, manifest hash `66EAC6D25839E7626D5F27E6A496E682085E0169D2D38E22BAD8E61E00E4F687`.
- Latest static closeout backup: `[maintainer-local-ghidra-backup-root]\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified`.

What this proves:

- Saved retail Ghidra metadata/decompile/xref/instruction evidence supports the five Wave581 vector/range handlers.
- The helper bodies expose value-level static semantics useful for clean-room MissionScript VM/value planning.
- Raw descriptor rows and loose corpus absence are recorded without overclaiming exact descriptor layout or runtime command use.

What remains unproven:

- Runtime MissionScript execution.
- Runtime command effects.
- Runtime vector behavior or range behavior.
- Live loose-MSL loading or packed-vs-loose script selection.
- Exact command descriptor layout, exact datatype layout, or exact vector layout.
- BEA patching behavior.
- Visual QA.
- Godot parity.
- Rebuild parity.
- No-noticeable-difference parity.
