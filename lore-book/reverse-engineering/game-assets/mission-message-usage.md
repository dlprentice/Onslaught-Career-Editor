# Mission Message Usage (Loose MSL)
> Source: `game/data/MissionScripts/**.msl`
> Generated: Feb 4, 2026

This summarizes message-related calls (`PlayCharMessage*`, `AddHelpMessage`, `LevelLost*`, `LevelWon`).

Static-to-proof planning for MissionScript / IScript message, objective, level outcome, and HUD command bridges is `../binary-analysis/missionscript-iscript-proof-plan.md`, with the implementation-facing child contract at `../binary-analysis/missionscript-iscript-static-contract.md`. This loose-MSL message index is corpus/reference evidence only; runtime voice/audio/HUD output and mission outcome behavior remain separate proof.

MissionScript Objective/Outcome Command-Effect static proof is recorded in `../binary-analysis/missionscript-objective-outcome-command-effect-static-proof.md` and `../binary-analysis/missionscript-objective-outcome-command-effect.v1.json`. It uses this message index only as separate message-family corpus evidence for `110 LevelLost-family` and `71 LevelWon-family`; event/objective counts remain in `mission-events-index.md`. This does not prove runtime command effects, runtime objective UI, runtime level outcomes, runtime voice/audio/HUD output, live loose-MSL loading, patching, Godot, rebuild parity, or no-noticeable-difference parity.

MissionScript Message/Audio Command-Effect static proof is recorded in `../binary-analysis/missionscript-message-audio-command-effect-static-proof.md` and `../binary-analysis/missionscript-message-audio-command-effect.v1.json`. It uses this index as the message-family corpus authority for `1365 PlayCharMessage`, `7 AddHelpMessage`, `110 LevelLost-family`, `71 LevelWon-family`, plus split detailed callsite counts of `1553 detailed message rows`, `11 speakers`, and `499 unique message tokens`. This stays static corpus evidence only; runtime message display, voice/audio playback, HUD output, queue ordering, live loose-MSL loading, patching, Godot, rebuild parity, and no-noticeable-difference parity remain separate proof.

MissionScript Level100 Tutorial Static Event/Command Walkthrough proof planning is recorded in `../binary-analysis/missionscript-level100-tutorial-static-walkthrough-proof-plan.md` and `../binary-analysis/missionscript-level100-tutorial-static-walkthrough.v1.json`. It uses the `level100` message row below (`45` `PlayCharMessage*`, `6` `AddHelpMessage`, `2` `LevelLost`, and `1` `LevelWon`) plus the detailed callsite split to preserve `43` unique message tokens and speakers `P_TATIANA`, `P_KRAMER`, and `P_TECHNICIAN` as static corpus evidence only.

MissionScript Level100 Tutorial Text/Speaker Resolution static proof is recorded in `../binary-analysis/missionscript-level100-tutorial-text-speaker-resolution-proof-plan.md` and `../binary-analysis/missionscript-level100-tutorial-text-speaker-resolution.v1.json`. It resolves the Level100 `45` `PlayCharMessage*` rows, `43` unique message tokens, `6` `AddHelpMessage` tokens, `_100_OBJECTIVE_1` through `_100_OBJECTIVE_4`, `LOSE_TUTORIAL_BROKE`, speakers `P_TATIANA`, `P_KRAMER`, and `P_TECHNICIAN`, generated-only tokens `TUTORIAL_13_MOD`, `TUTORIAL_DODGE_MOD`, `TUTORIAL_THROTTLE_MOD`, `HELP_FIRE`, `HELP_RETRO`, `HELP_TRANSFORM`, `HELP_WEAPON_SELECT`, `HELP_ZOOM_IN`, and `HELP_ZOOM_OUT`, with `68/68` relevant static tokens resolved and `0 missing`. This remains static text/speaker resolution only, not runtime text/audio behavior, message display, voice/audio playback, live loose-MSL loading, visual QA, Godot, rebuild, or no-noticeable-difference proof.

MissionScript Level100 Tutorial Runtime Harness Boundary proof is recorded in `../binary-analysis/missionscript-level100-tutorial-runtime-harness-boundary-proof-plan.md` and `../binary-analysis/missionscript-level100-tutorial-runtime-harness-boundary.v1.json`. It carries the completed text/speaker counts into a copied-profile planning boundary with required future artifacts including source-selection observation log, bounded event/message/HUD/object observation checklist, private artifact inventory, and public-safe result summary. Status: runtime-harness boundary proof plan complete, not runtime proof.

## Per-Level Summary

| Level | Dir | PlayCharMessage | AddHelpMessage | LevelLost | LevelWon |
|------:|-----|---------------:|---------------:|---------:|--------:|
| 3 | level003 | 9 | 0 | 0 | 0 |
| 20 | Level020 | 0 | 0 | 0 | 1 |
| 21 | level021 | 2 | 0 | 0 | 1 |
| 22 | level022 | 20 | 0 | 0 | 1 |
| 100 | level100 | 45 | 6 | 2 | 1 |
| 110 | level110 | 14 | 0 | 1 | 2 |
| 200 | level200 | 32 | 0 | 3 | 1 |
| 201 | level201 | 32 | 0 | 2 | 1 |
| 211 | level211 | 15 | 0 | 1 | 1 |
| 212 | level212 | 15 | 0 | 1 | 1 |
| 221 | level221 | 24 | 0 | 2 | 1 |
| 222 | level222 | 24 | 0 | 2 | 1 |
| 231 | level231 | 60 | 0 | 2 | 1 |
| 232 | level232 | 60 | 0 | 2 | 1 |
| 300 | level300 | 17 | 0 | 1 | 1 |
| 311 | level311 | 11 | 0 | 2 | 1 |
| 312 | level312 | 11 | 0 | 2 | 1 |
| 321 | level321 | 14 | 0 | 1 | 1 |
| 322 | level322 | 17 | 0 | 1 | 1 |
| 331 | level331 | 10 | 0 | 0 | 1 |
| 332 | level332 | 10 | 0 | 0 | 1 |
| 400 | Level400 | 39 | 0 | 4 | 1 |
| 411 | level411 | 24 | 0 | 3 | 1 |
| 412 | level412 | 24 | 0 | 3 | 1 |
| 421 | level421 | 13 | 0 | 2 | 2 |
| 422 | level422 | 13 | 0 | 2 | 2 |
| 431 | level431 | 19 | 0 | 1 | 1 |
| 432 | level432 | 19 | 0 | 1 | 1 |
| 500 | level500 | 14 | 0 | 4 | 1 |
| 511 | Level511 | 10 | 0 | 1 | 2 |
| 512 | level512 | 15 | 0 | 1 | 1 |
| 521 | level521 | 10 | 0 | 3 | 1 |
| 522 | level522 | 11 | 0 | 3 | 1 |
| 523 | level523 | 10 | 0 | 1 | 1 |
| 524 | level524 | 10 | 0 | 1 | 1 |
| 600 | level600 | 27 | 0 | 1 | 1 |
| 611 | level611 | 34 | 0 | 4 | 2 |
| 612 | level612 | 33 | 0 | 5 | 2 |
| 621 | level621 | 10 | 0 | 2 | 1 |
| 622 | level622 | 7 | 0 | 2 | 1 |
| 700 | level700 | 20 | 0 | 2 | 1 |
| 710 | level710 | 11 | 1 | 2 | 1 |
| 720 | level720 | 15 | 0 | 2 | 1 |
| 731 | level731 | 14 | 0 | 2 | 2 |
| 732 | level732 | 15 | 0 | 2 | 3 |
| 741 | level741 | 17 | 0 | 2 | 1 |
| 742 | level742 | 17 | 0 | 3 | 1 |
| 800 | level800 | 8 | 0 | 0 | 1 |
| 850 | level850 | 8 | 0 | 1 | 1 |
| 851 | level851 | 5 | 0 | 0 | 0 |
| 853 | level853 | 61 | 0 | 1 | 1 |
| 856 | level856 | 14 | 0 | 1 | 1 |
| 858 | level858 | 14 | 0 | 1 | 1 |
| 859 | level859 | 26 | 0 | 3 | 1 |
| 860 | level860 | 54 | 0 | 1 | 0 |
| 861 | level861 | 5 | 0 | 0 | 0 |
| 863 | level863 | 54 | 0 | 1 | 0 |
| 864 | level864 | 8 | 0 | 1 | 1 |
| 865 | level865 | 61 | 0 | 1 | 1 |
| 866 | level866 | 26 | 0 | 3 | 1 |
| 901 | level901 | 19 | 0 | 2 | 1 |
| 902 | level902 | 19 | 0 | 2 | 1 |
| 903 | level903 | 19 | 0 | 2 | 1 |
| 904 | level904 | 19 | 0 | 2 | 1 |
| 905 | level905 | 24 | 0 | 2 | 1 |
| 956 | level956 | 14 | 0 | 1 | 1 |
| 958 | level958 | 14 | 0 | 1 | 1 |

## Detailed Call Sites

Split into:

- [mission-message-usage-callsites-1.md](mission-message-usage-callsites-1.md)
- [mission-message-usage-callsites-2.md](mission-message-usage-callsites-2.md)

*Note: This table was split out to keep generated docs under the 1000-line guideline.*
