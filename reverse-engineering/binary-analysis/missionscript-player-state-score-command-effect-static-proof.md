# MissionScript Player-State / Score Command-Effect Static Proof

Status: static player-state/score command-effect schema proof complete, not runtime proof
Last updated: 2026-06-08
Scope: `missionscript-player-state-score-command-effect-static`
Artifact: `missionscript-player-state-score-command-effect-static-proof.md`; schema: `missionscript-player-state-score-command-effect.v1.json`

This proof converts the completed MissionScript descriptor schema, copied loose-MSL command-token counts, public MSL references, Stuart source context, and retained IScript/BattleEngine static docs into a bounded player-state/score command bridge. It follows the completed slot, objective/outcome, message/audio, Goodie-state, selected `SpawnThing`, selected `GetThingRef`, cutscene pan-camera/position, vector/range, thing-value/engine-helper, and HUD/display static command-effect proofs.

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
| `AddScore` descriptor | Descriptor row `84 AddScore` exists in `missionscript-command-descriptor-schema.v1.json` at `0x0064e350`, name symbol `s_AddScore_0064f5c4`, raw entry `IScript__Unk_00534410`, and nonzero raw descriptor fields `+0x14=1` and `+0x1c=1`. |
| `AddScore` boundary | Current objective/outcome evidence names `0x00534410 IScript__SecondaryObjectiveComplete`; therefore `AddScore` remains descriptor/name/corpus context only here. This proof preserves the alias conflict and does not claim `AddScore` handler-body proof or runtime score behavior. |
| `ToggleCockpit` descriptor | Descriptor row `136 ToggleCockpit` exists at `0x0064f050`, name symbol `s_ToggleCockpit_0064f288`, raw entry `&LAB_00533950`, and no selected nonzero raw shape fields. The copied loose-MSL scan found `0` direct non-comment calls in `0` files. |
| `SetStealth` descriptor | Descriptor row `137 SetStealth` exists at `0x0064f090`, name symbol `s_SetStealth_0064f27c`, raw entry `&LAB_00533980`, and nonzero raw descriptor fields `+0x14=1` and `+0x1c=2`. |
| Loose corpus scan | A copied loose-MSL non-comment command-token scan found `15 / 0 / 10` calls for `AddScore`, `ToggleCockpit`, and `SetStealth` across `12 / 0 / 4` files. `AddScore` appears in score bonus/penalty contexts including `level100`, `level110`, `level221`, `level222`, `level331`, `level332`, `level411`, and `level412`; `SetStealth` appears in Carver scripts for `level611`, `level612`, `level621`, and `level622`; `ToggleCockpit` has no direct loose-MSL usage in the copied scan. |
| Source/static context | Public MSL docs expose `AddScore(points)` and penalty examples. Stuart source exposes `CGame::IncScore(SINT)`, `CBattleEngine::ToggleCockpit`, and `mStealth` / `mDesiredStealth` flow. Retail static docs anchor `0x0040d4d0 CBattleEngine__HandleCloak` to cloak/desired-stealth context. These are context anchors only, not handler-body or runtime behavior proof for the three descriptor rows. |

## Why This Matters

This turns three gameplay-visible MissionScript command names into a machine-checkable static bridge without guessing:

- `AddScore` is measurable in the loose corpus and public syntax, but its raw descriptor entry collides with an already-named objective handler address.
- `ToggleCockpit` has a descriptor row and source-side concept, but no loose-corpus use and no promoted retail handler body.
- `SetStealth` has descriptor and Carver corpus context plus BattleEngine stealth/cloak context, but no runtime stealth, cloak, or weapon-fire interaction proof.

The result is useful for clean-room planning because score, cockpit, and stealth are now finite command surfaces with explicit uncertainty. A later copied/app-owned proof can choose one path without relying on a stale handler guess.

## Claim Boundary

This proves static player-state/score command-effect accounting from descriptor rows, raw entry labels, copied loose-MSL command-token counts, public MSL syntax, source context, and retained IScript/BattleEngine static docs. It does not prove runtime MissionScript execution, runtime command effects, runtime score behavior, runtime cockpit behavior, runtime stealth behavior, weapon-fire/stealth interaction, runtime ranking/career/save behavior, live loose-MSL loading, packed-vs-loose script selection, `AddScore` handler-body proof, `ToggleCockpit` handler-body proof, `SetStealth` handler-body proof, exact command descriptor layout, exact command arity, exact datatype layout, exact player-state layout, visual QA, Godot parity, BEA patching behavior, rebuild parity, or no-noticeable-difference parity.
