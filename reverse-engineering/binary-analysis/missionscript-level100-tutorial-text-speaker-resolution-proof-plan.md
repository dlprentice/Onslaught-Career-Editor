# MissionScript Level100 Tutorial Text/Speaker Resolution Static Proof Plan

Status: static text/speaker resolution proof plan complete, not runtime proof
Last updated: 2026-06-08
Scope: `missionscript-level100-tutorial-text-speaker-resolution`
Public proof anchor: `missionscript-level100-tutorial-text-speaker-resolution-proof-plan.md`

This proof-plan slice extends the completed [MissionScript Level100 Tutorial Static Event/Command Walkthrough Proof Plan](missionscript-level100-tutorial-static-walkthrough-proof-plan.md) with static text and speaker-token resolution. It ties the `level100` tutorial message/help/objective/loss/speaker references to level-local `English.txt`, empty level-local `Global.txt`, empty level-local `text.stf`, shared `text/english.txt`, shared `text/global.txt`, and shared `text/text.stf` ID definitions.

Follow-up static-to-proof boundary: the MissionScript Level100 Tutorial Runtime Harness Boundary Proof Plan is recorded at `missionscript-level100-tutorial-runtime-harness-boundary-proof-plan.md`, backed by `missionscript-level100-tutorial-runtime-harness-boundary.v1.json`. That slice is runtime-harness boundary proof plan complete, not runtime proof, and moves the active child lane to MissionScript Level100 Tutorial Copied-Profile Runtime Observation Boundary Planning Proof Plan.

Machine-checkable schema: `missionscript-level100-tutorial-text-speaker-resolution.v1.json`.

This plan does not launch BEA, mutate Ghidra, mutate the installed game, patch an executable, capture screenshots, drive native input, execute scripts, load a live mission, start Godot work, quote raw dialogue, or claim runtime MissionScript execution, runtime text/audio behavior, runtime message display, runtime voice/audio playback, runtime localized text selection, speaker portrait behavior, live loose-MSL loading, packed-vs-loose script selection, runtime Level100 mission outcome, BEA patching behavior, visual QA, rebuild parity, or no-noticeable-difference parity.

## Static Authority

Current static closeout remains unchanged:

- Static Ghidra function-quality closure: `6411/6411 = 100.00%`.
- Static debt: `0 / 0 / 0` commentless, exact-undefined, and `param_N` rows.
- Expanded post-100 static surface: `1560/1560 = 100.00%`.
- Active current-risk focused accounting: `1179/1179 = 100.00%`.
- Remaining active focused work: `0`.
- Latest verified Ghidra backup: `G:\GhidraBackups\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified`.

Primary static and corpus sources:

- `missionscript-level100-tutorial-static-walkthrough-proof-plan.md`
- `missionscript-level100-tutorial-static-walkthrough.v1.json`
- `missionscript-message-audio-command-effect-static-proof.md`
- `missionscript-objective-outcome-command-effect-static-proof.md`
- `mission-message-usage.md`
- `mission-message-usage-callsites-1.md`
- `mission-speaker-index.md`
- `mission-text-index.md`

## Text Corpus Surface

| Surface | Static result |
| --- | --- |
| Level-local text blocks | `English.txt` has `52` token blocks |
| Level-local global text | `Global.txt` has `0` token blocks |
| Level-local generated IDs | level-local `text.stf` has `0` defines |
| Shared speaker/text blocks | shared `text/english.txt` has `241` token blocks |
| Shared global text blocks | shared `text/global.txt` has `2` token blocks |
| Shared generated IDs | shared `text/text.stf` has `2571` signed ID defines |
| Header caveat | `textlist.h` is not the authoritative Level100 tutorial token map |
| Public payload boundary | raw dialogue payloads are not reproduced here |

The important correction is that several Level100 references are generated-ID tokens rather than level-local bracket text blocks. Those are resolved through shared `text/text.stf`; they are not treated as missing just because they do not appear in `level100/English.txt`.

## Level100 Reference Counts

| Reference family | Static rows | Unique tokens | Resolution |
| --- | ---: | ---: | --- |
| `PlayCharMessage*` message tokens | `45` | `43` | `40` level-local `English.txt`, `3` generated-only shared `text/text.stf`, `0 missing` |
| `AddHelpMessage` tokens | `6` | `6` | generated-only shared `text/text.stf`, `0 missing` |
| Objective text IDs | `8` rows | `4` | `_100_OBJECTIVE_1` through `_100_OBJECTIVE_4` in shared `text/text.stf`, `0 missing` |
| Loss string IDs | `2` rows | `1` | `LOSE_TUTORIAL_BROKE` in level-local `English.txt` and shared `text/text.stf`, `0 missing` |
| Speaker tokens | `45` rows | `3` | `P_TATIANA`, `P_KRAMER`, and `P_TECHNICIAN` in shared `text/english.txt` and shared `text/text.stf`, `0 missing` |

Speaker row counts remain `P_TATIANA` `40`, `P_KRAMER` `4`, and `P_TECHNICIAN` `1`. Speaker labels are the static label rows already published by `mission-speaker-index.md`; this does not prove runtime portraits, voice selection, message-box layout, or audio playback.

## Generated-Only Tokens

The generated-only Level100 references are intentionally separated from level-local text-block ownership:

- Message tokens: `TUTORIAL_13_MOD`, `TUTORIAL_DODGE_MOD`, and `TUTORIAL_THROTTLE_MOD`.
- Help tokens: `HELP_FIRE`, `HELP_RETRO`, `HELP_TRANSFORM`, `HELP_WEAPON_SELECT`, `HELP_ZOOM_IN`, and `HELP_ZOOM_OUT`.
- Objective tokens: `_100_OBJECTIVE_1`, `_100_OBJECTIVE_2`, `_100_OBJECTIVE_3`, and `_100_OBJECTIVE_4`.

The combined Level100 tutorial static token set relevant to this slice resolves `68/68` through shared `text/text.stf` or shared `text/english.txt`, with `0 missing` tokens.

## Level-Local Extra Tokens

The level-local `English.txt` file also contains `11` bracket tokens not referenced by the parsed Level100 walkthrough message/help/objective/loss calls:

- `HUD_08`
- `TUTORIAL_13`
- `TUTORIAL_AMMO`
- `TUTORIAL_DODGE`
- `TUTORIAL_MOVEMENT`
- `TUTORIAL_OVERHEAT`
- `TUTORIAL_TECHNICIAN_02`
- `TUTORIAL_TECHNICIAN_03`
- `TUTORIAL_THROTTLE`
- `TUTORIAL_WATER`
- `TUTORIAL_WEAPON`

These are retained as static corpus facts for later runtime/rebuild planning. They are not promoted into runtime behavior or visible tutorial-message claims.

## Claims

This slice proves:

- Level100 tutorial message/help/objective/loss/speaker token references resolve statically with `0 missing` tokens across level-local `English.txt`, shared `text/english.txt`, and shared `text/text.stf`.
- Generated-only Level100 references are separated from level-local text blocks instead of being treated as missing dialogue text.
- The text/speaker resolution is strong enough to plan a later copied/app-owned Level100 runtime or rebuild slice without widening static claims into runtime text/audio behavior.

This slice does not prove:

- Runtime MissionScript execution.
- Runtime text/audio behavior.
- Runtime message display.
- Runtime voice/audio playback.
- Runtime localized text selection.
- Speaker portrait behavior.
- Live loose-MSL loading.
- Packed-vs-loose script selection.
- Runtime Level100 mission outcome.
- BEA patching behavior.
- Visual QA.
- Godot parity.
- Rebuild parity.
- No-noticeable-difference parity.

## Exit Gate

This planning slice is complete only when:

- This document and `missionscript-level100-tutorial-text-speaker-resolution.v1.json` have lore-book mirrors.
- `roadmap/static-to-proof-rebuild-transition-backlog.md`, `mapped-systems.md`, `_index.md`, and `RE-INDEX.md` point to this plan.
- MissionScript corpus docs and MissionScript static contract/proof-plan docs point to this plan.
- `release/readiness/missionscript_level100_tutorial_text_speaker_resolution_proof_plan_2026-06-08.md` records the same claim boundaries.
- `tools/missionscript_level100_tutorial_text_speaker_resolution_probe.py --check` passes.

## Follow-Up Child Lane

The next selected static-to-proof child lane is `MissionScript Level100 Tutorial Runtime Harness Boundary Proof Plan`. It should stay a planning/boundary slice until it selects copied/app-owned runtime inputs, stop conditions, source-selection constraints, no-mutation rules, expected artifacts, and proof boundaries. It must not run BEA or claim runtime behavior merely because this text/speaker resolution slice is complete.
