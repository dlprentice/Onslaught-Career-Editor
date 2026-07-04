# MissionScript Player-State / Score Command-Effect Static Proof Readiness Note

Status: static player-state/score command-effect schema proof complete, not runtime proof
Date: 2026-06-08
Scope: `missionscript-player-state-score-command-effect-static`

This static-only proof records descriptor/corpus/context evidence for `AddScore`, `ToggleCockpit`, and `SetStealth` without launching BEA, mutating Ghidra, patching an executable, loading a live mission, starting Godot, or claiming runtime behavior.

Evidence anchors:

| Surface | Static evidence |
| --- | --- |
| `AddScore` | Descriptor row `84`, record `0x0064e350`, raw entry `IScript__Unk_00534410`, name symbol `s_AddScore_0064f5c4`, nonzero raw fields `+0x14=1` and `+0x1c=1`, source context `CGame::IncScore`. |
| `AddScore` boundary | Current objective/outcome docs name `0x00534410 IScript__SecondaryObjectiveComplete`; `AddScore` is descriptor/name/corpus context only and no handler-body bridge is claimed. |
| `ToggleCockpit` | Descriptor row `136`, record `0x0064f050`, raw entry `&LAB_00533950`, name symbol `s_ToggleCockpit_0064f288`, copied loose-MSL count `0` direct calls in `0` files, source context `CBattleEngine::ToggleCockpit`. |
| `SetStealth` | Descriptor row `137`, record `0x0064f090`, raw entry `&LAB_00533980`, name symbol `s_SetStealth_0064f27c`, nonzero raw fields `+0x14=1` and `+0x1c=2`, copied loose-MSL count `10` calls in `4` Carver script files, static context `CBattleEngine__HandleCloak`. |

Readiness facts:

- Schema/proof artifacts: `missionscript-player-state-score-command-effect-static-proof.md` and `missionscript-player-state-score-command-effect.v1.json`.
- Copied loose-MSL counts: `15 / 0 / 10` calls across `12 / 0 / 4` files for `AddScore`, `ToggleCockpit`, and `SetStealth`.
- Static closeout remains `6411/6411 = 100.00%`, static debt `0 / 0 / 0`, expanded post-100 static surface `1560/1560 = 100.00%`, active current-risk focused accounting `1179/1179 = 100.00%`, and remaining active focused work `0`.
- Latest verified Ghidra backup remains `[maintainer-local-ghidra-backup-root]\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified`.

What this proves:

- The three selected command descriptor rows exist in the completed static descriptor schema.
- The copied loose-MSL corpus has exact direct command-token counts for the selected commands.
- The `AddScore` alias conflict is explicitly bounded instead of promoted into a false handler-body claim.
- `ToggleCockpit` and `SetStealth` retain source/static context without runtime claims.

What remains unproven:

- Runtime MissionScript execution.
- Runtime command effects.
- Runtime score behavior.
- Runtime cockpit behavior.
- Runtime stealth behavior.
- Weapon-fire/stealth interaction.
- Runtime ranking/career/save behavior.
- Live loose-MSL loading or packed-vs-loose script selection.
- Exact descriptor/datatype/player-state layouts.
- Visual QA, Godot parity, BEA patching behavior, rebuild parity, or no-noticeable-difference parity.
