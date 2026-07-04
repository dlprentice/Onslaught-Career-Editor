# MissionScript HUD / Display Command-Effect Static Proof Readiness Note

Status: static HUD/display command-effect schema proof complete, not runtime proof
Date: 2026-06-08
Scope: `missionscript-hud-display-command-effect-static`

This slice adds a public-safe, machine-checkable static bridge for MissionScript HUD/display command names:

- Proof note: `reverse-engineering/binary-analysis/missionscript-hud-display-command-effect-static-proof.md`
- Schema: `reverse-engineering/binary-analysis/missionscript-hud-display-command-effect.v1.json`
- Probe: `tools/missionscript_hud_display_command_effect_static_probe.py`
- Package script: `npm run test:missionscript-hud-display-command-effect-static`

Static closeout remains unchanged: `6411/6411 = 100.00%`, `0 / 0 / 0`, `1560/1560 = 100.00%`, and `1179/1179 = 100.00%`. Latest verified Ghidra backup remains `[maintainer-local-ghidra-backup-root]\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified`.

## Evidence

| Surface | Static evidence |
| --- | --- |
| Descriptor rows | `33 HighlightHudPart` at `0x0064d690` / `&LAB_00535d70`; `34 UnHighlightHudPart` at `0x0064d6d0` / `&LAB_00535e60`; `75 InitVariable` at `0x0064e110` / `&LAB_00536210`; `76 SetVariable` at `0x0064e150` / `&LAB_00536230`; `77 ShutdownVariable` at `0x0064e190` / `&LAB_00536260`. |
| Corpus counts | Copied loose-MSL command-token counts: `13 / 13 / 77 / 146 / 26` for `HighlightHudPart`, `UnHighlightHudPart`, `InitVariable`, `SetVariable`, and `ShutdownVariable`. |
| HUD context | `CHud__SetHudComponent`, `CHud__RenderOverlayForViewpoint`, `CHudComponent__RenderPass`, active HUD component slot `this+0x1fc`, and pending slot `this+0x200` from `hud-frontend-overlay-static-contract.md`. |
| World-text context | `CWorld__PushWorldTextSlot`, `CWorld__UpdateWorldTextSlotTiming`, `CWorld__ClearWorldTextSlot`, `CWorld__GetWorldTextSlotTimerValue`, and `DAT_00855090` from the CWorld owner map. |

## Boundary

This proves static descriptor/corpus/context accounting only. It does not prove runtime MissionScript execution, runtime HUD behavior, visible HUD flashing, runtime variable display, message overlay behavior, render ordering, live loose-MSL loading, packed-vs-loose script selection, handler-body semantics for the five raw entries, a static call path from the five raw entries into `CHud` functions, exact descriptor/datatype/HUD layout, BEA patching behavior, visual QA, Godot parity, rebuild parity, or no-noticeable-difference parity.
