# MissionScript HUD / Display Command-Effect Static Proof

Status: static HUD/display command-effect schema proof complete, not runtime proof
Last updated: 2026-06-08
Scope: `missionscript-hud-display-command-effect-static`
Artifact: `missionscript-hud-display-command-effect-static-proof.md`; schema: `missionscript-hud-display-command-effect.v1.json`

This proof converts the completed MissionScript descriptor schema, public MSL command references, a copied loose-MSL command-token scan, the HUD/frontend overlay static contract, and CWorld world-text static anchors into a machine-checkable HUD/display bridge. It is the next narrow MissionScript command-effect child lane after the completed slot, objective/outcome, message/audio, Goodie-state, selected `SpawnThing`, selected `GetThingRef`, cutscene pan-camera/position, vector/range, and thing-value/engine-helper static proofs.

Static closeout remains unchanged:

- Static Ghidra function-quality closure: `6411/6411 = 100.00%`.
- Static debt: `0 / 0 / 0` commentless, exact-undefined, and `param_N` rows.
- Expanded post-100 static surface: `1560/1560 = 100.00%`.
- Active current-risk focused accounting: `1179/1179 = 100.00%`.
- Remaining active focused work: `0`.
- Latest verified Ghidra backup remains `[maintainer-local-ghidra-backup-root]\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified`.

## Schema Result

| Surface | Static result |
| --- | --- |
| HUD highlight descriptors | Descriptor rows `33 HighlightHudPart` and `34 UnHighlightHudPart` exist in `missionscript-command-descriptor-schema.v1.json` at `0x0064d690` / `0x0064d6d0` with raw entries `&LAB_00535d70` / `&LAB_00535e60`. Both preserve nonzero raw descriptor fields `+0x14=1`, `+0x1c=1`, and `+0x38=1`. |
| Variable display descriptors | Descriptor rows `75 InitVariable`, `76 SetVariable`, and `77 ShutdownVariable` exist at `0x0064e110`, `0x0064e150`, and `0x0064e190` with raw entries `&LAB_00536210`, `&LAB_00536230`, and `&LAB_00536260`. Their nonzero raw descriptor fields are `2/1/1/2`, `3/1/2/2/2`, and `1/1/2` across the selected `+0x14`, `+0x1c`, `+0x20`, `+0x24`, and `+0x38` slots. |
| Public MSL command forms | `msl-scripting.md` documents `HighlightHudPart(HUD_COMPASS)`, `UnHighlightHudPart(HUD_COMPASS)`, `InitVariable(TEXT_CONSTANT, VARIABLE_TYPE)`, `SetVariable(TEXT_CONSTANT, value, threshold)`, and `ShutdownVariable(TEXT_CONSTANT)`. It also records HUD constants `HUD_HEALTH_BAR`, `HUD_ENERGY_BAR`, `HUD_COMPASS`, `HUD_BATTLE_LINE_MAP`, `HUD_RADAR`, `HUD_CURRENT_WEAPON` and variable types `VARIABLE_NUMBER`, `VARIABLE_NUMBER_AND_THRESHOLD`, `VARIABLE_TIMER`, `VARIABLE_PERCENTAGE`, `VARIABLE_PERCENTAGE_AND_THRESHOLD`, `VARIABLE_TIME`. |
| Loose corpus scan | A copied loose-MSL non-comment command-token scan found `13 / 13 / 77 / 146 / 26` rows for `HighlightHudPart`, `UnHighlightHudPart`, `InitVariable`, `SetVariable`, and `ShutdownVariable`. The paired highlight rows appear in `level022` and `level100`; variable rows span `41`, `45`, and `18` files respectively. |
| HUD static context | `hud-frontend-overlay-static-contract.md` maps rebuild-planning anchors including `CHud__SetHudComponent`, `CHud__RenderOverlayForViewpoint`, `CHud__RenderBattleline`, `CHud__RenderActiveHudComponentPass`, `CHud__RenderTacticalRadarContacts`, `CHud__RenderObjectiveStatusPanel`, `CHudComponent__RenderPass`, active slot `this+0x1fc`, and pending slot `this+0x200`. |
| World-text static context | The CWorld owner doc maps adjacent display helpers `CWorld__PushWorldTextSlot`, `CWorld__UpdateWorldTextSlotTiming`, `CWorld__ClearWorldTextSlot`, `CWorld__GetWorldTextSlotTimerValue`, and singleton context `DAT_00855090`. These are static display-context anchors for variable-style command planning, not proof that the five raw descriptor entries dispatch to those helpers. |

## Why This Matters

This gives clean-room MissionScript planning a bounded HUD/display command surface:

- HUD element command names and constants are finite enough to model as a small enum surface.
- Variable display command names, variable types, and loose corpus call counts are now measurable.
- HUD render/component static contracts and CWorld world-text helpers are linked as planning context for later scoped runtime proof.
- The raw descriptor entries are preserved as exact static anchors without promoting unproven handler-body names.

The proof intentionally does not claim that `HighlightHudPart`, `UnHighlightHudPart`, `InitVariable`, `SetVariable`, or `ShutdownVariable` runtime effects have been proven. It preserves their descriptor/corpus context so a later copied/app-owned proof can select one visible command path without guessing from the binary.

## Claim Boundary

This proves static HUD/display command-effect accounting from descriptor rows, raw entry labels, public MSL command forms, copied loose-MSL command-token counts, HUD/frontend overlay static context, and CWorld world-text static context. It does not prove runtime MissionScript execution, runtime HUD behavior, visible HUD flashing, runtime variable display, message overlay behavior, render ordering, live loose-MSL loading, packed-vs-loose script selection, handler-body semantics for the five raw entries, a static call path from the five raw entries into `CHud` functions, exact command descriptor layout, exact command arity, exact datatype layout, exact HUD layout, BEA patching behavior, visual QA, Godot parity, rebuild parity, or no-noticeable-difference parity.
