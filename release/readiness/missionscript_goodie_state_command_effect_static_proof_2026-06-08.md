# MissionScript Goodie State Command-Effect Static Proof Readiness Note

Status: static Goodie state command-effect schema proof complete, not runtime proof
Date: 2026-06-08
Scope: `missionscript-goodie-state-command-effect-static`

This readiness note records the static-to-proof consolidation for `missionscript-goodie-state-command-effect-static-proof.md` and `missionscript-goodie-state-command-effect.v1.json`. It adds no Ghidra mutation, no executable mutation, no runtime proof, no visual QA, no patch, no Godot work, and no rebuild parity claim.

Static closeout remains unchanged:

- Static Ghidra function-quality closure: `6411/6411 = 100.00%`.
- Static debt: `0 / 0 / 0`.
- Expanded post-100 static surface: `1560/1560 = 100.00%`.
- Active current-risk focused accounting: `1179/1179 = 100.00%`.
- Remaining active focused work: `0`.
- Latest verified Ghidra backup remains `[maintainer-local-ghidra-backup-root]\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified`.

Representative anchors:

| Surface | Evidence |
| --- | --- |
| Descriptor names | `SetGoodieState` at descriptor index `118` / `0x0064ebd0`; `GetGoodieState` at descriptor index `119` / `0x0064ec10`. |
| Handler bodies | `IScript__SetGoodieState` writes `g_Career_mGoodies[index-1]`; `IScript__GetGoodieState` reads `g_Career_mGoodies[index-1]` and returns an integer result through `out_result`. |
| Save bridge | Goodie state storage is the `300`-entry array at global address `0x00662564` and true-view file base `0x1F46`; script index N maps to save Goodie index N-1. |
| State values | `0` / `1` / `2` / `3` map to `GS_UNKNOWN` / `GS_INSTRUCTIONS` / `GS_NEW` / `GS_OLD`. |
| AddScore boundary | `AddScore` is preserved as descriptor/name context only at `0x0064e350`; no handler-body proof is claimed in this slice. |

Evidence counts:

- Wave579: `6` metadata rows, `6` tag rows, `6` xref rows, `1326` instruction rows, `6` decompile rows, and `24` vtable rows.
- Focused schema probe: `tools/missionscript_goodie_state_command_effect_static_probe.py --check`.

What this proves:

- The static descriptor table contains `SetGoodieState` and `GetGoodieState` command names and record addresses.
- Saved Wave579 IScript bodies statically bridge MissionScript 1-based Goodie indices to `g_Career_mGoodies[index-1]`.
- The save docs map the same Goodie array to true-view file offset `0x1F46` with `300` 4-byte entries.
- `AddScore` remains descriptor/name context only, not a handler-body claim.

What remains unproven:

- Runtime MissionScript execution.
- Runtime command effects.
- Runtime Goodie state mutation.
- Runtime save behavior.
- Runtime Goodies wall behavior.
- Live loose-MSL loading or packed-vs-loose script selection.
- Exact descriptor or `CCareer` concrete layout.
- `AddScore` handler-body proof.
- BEA patching behavior.
- Visual QA.
- Godot parity.
- Rebuild parity.
- No-noticeable-difference parity.
