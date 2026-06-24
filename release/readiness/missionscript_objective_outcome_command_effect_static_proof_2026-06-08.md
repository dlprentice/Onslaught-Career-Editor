# MissionScript Objective/Outcome Command-Effect Static Readiness Note

Status: static objective/outcome command-effect schema proof complete, not runtime proof
Date: 2026-06-08
Scope: `missionscript-objective-outcome-command-effect-static`

This readiness note records the public-safe static proof result for [MissionScript Objective/Outcome Command-Effect Static Proof](../../reverse-engineering/binary-analysis/missionscript-objective-outcome-command-effect-static-proof.md), backed by `missionscript-objective-outcome-command-effect.v1.json`.

Static closeout remains unchanged: `6411/6411 = 100.00%`, `0 / 0 / 0`, `1560/1560 = 100.00%`, `1179/1179 = 100.00%`, and remaining active focused work `0`. Latest verified Ghidra backup remains `G:\GhidraBackups\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified`.

Evidence anchors:

| Surface | Anchor |
| --- | --- |
| Descriptor slots | `LevelLost` `0x0064d010`, `LevelWon` `0x0064d050`, `PrimaryObjectiveComplete` `0x0064e2d0`, `SecondaryObjectiveComplete` `0x0064e310`, `PrimaryObjectiveFailed` `0x0064e3d0`, `SecondaryObjectiveFailed` `0x0064e410`, and `LevelLostString` `0x0064e890`. |
| Objective handlers | `0x005343e0 IScript__PrimaryObjectiveComplete`, `0x00534410 IScript__SecondaryObjectiveComplete`, `0x00534440 IScript__PrimaryObjectiveFailed`, and `0x00534470 IScript__SecondaryObjectiveFailed`; complete writes state `1`, failed writes state `2`. |
| Objective arrays | Primary text/state arrays `DAT_008a9ae0` / `DAT_008a9adc`; secondary text/state arrays `DAT_008a9b30` / `DAT_008a9b2c`. |
| Outcome handlers | `0x005381a0 IScript__LevelLost`, `0x005381c0 IScript__LevelLostString`, and `0x005381e0 IScript__LevelWon`. |
| End-level bridge | `0x0046d470 CGame__FillOutEndLevelData`, `0x0046f2f0 CGame__DeclareLevelWon`, `0x0046f430 CGame__DeclareLevelLost`, `0x0041bd00 CCareer__Update`, and `0x004496e0 CEndLevelData__IsAllSecondaryObjectivesComplete`. |
| Event corpus | `95` level rows, `795` event counts, `36` objective IDs, `115 primary-complete`, `42 secondary-complete`, `0 objective-complete`, `102 primary-failed`, `79 LevelWon`, and `13 LevelLost`. |
| Message corpus | Separate message summary: `67` rows, `1365` PlayCharMessage, `7` AddHelpMessage, `110 LevelLost-family`, and `71 LevelWon-family`. |

Evidence counts: Wave580 `6` metadata rows, `6` xref rows, `5454` instruction rows, `6` decompile rows, and `36` vtable rows; Wave585 `5` metadata rows, `5` xref rows, `1845` instruction rows, and `5` decompile rows; Wave1049 `10` primary metadata rows, `13` xref rows, `761` instruction rows, and `10` decompile rows plus `12` context metadata rows, `23` context xref rows, `6129` context instruction rows, and `12` context decompile rows. This slice used saved static exports and did not mutate Ghidra.

What this proves:

- The static objective command bridge maps descriptor names through IScript handlers into observed primary/secondary objective text and state arrays.
- The static level outcome bridge maps `LevelWon`, `LevelLost`, and `LevelLostString` through IScript handlers into CGame level-result helpers.
- The loose event corpus and message corpus counts are reproducible and intentionally separate.

What remains unproven:

- Runtime MissionScript execution or runtime command effects.
- Runtime objective UI/HUD/audio behavior, runtime level win/loss outcomes, runtime save behavior, or runtime career progression.
- Live loose-MSL loading or packed-vs-loose script selection.
- Exact descriptor, CGame, CCareer, END_LEVEL_DATA, VM, datatype, arity, or argument layouts.
- BEA patching behavior, visual QA, Godot parity, rebuild parity, or no-noticeable-difference parity.
