# MissionScript Objective/Outcome Command-Effect Static Proof

Status: static objective/outcome command-effect schema proof complete, not runtime proof
Last updated: 2026-06-08
Scope: `missionscript-objective-outcome-command-effect-static`
Artifact: `missionscript-objective-outcome-command-effect-static-proof.md`; schema: `missionscript-objective-outcome-command-effect.v1.json`

This proof converts saved retail Ghidra evidence from Wave580, Wave585, Wave903, and Wave1049 plus public-safe loose MissionScript indexes into a machine-checkable objective/outcome command-effect map at `missionscript-objective-outcome-command-effect.v1.json`. It is the next narrow IScript command-effect child lane after the completed slot proof.

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
| Descriptor slots | `LevelLost` index `7` at `0x0064d010`; `LevelWon` index `8` at `0x0064d050`; `PrimaryObjectiveComplete` index `82` at `0x0064e2d0`; `SecondaryObjectiveComplete` index `83` at `0x0064e310`; `PrimaryObjectiveFailed` index `86` at `0x0064e3d0`; `SecondaryObjectiveFailed` index `87` at `0x0064e410`; `LevelLostString` index `105` at `0x0064e890`. |
| Objective complete/fail handlers | `0x005343e0 IScript__PrimaryObjectiveComplete`, `0x00534410 IScript__SecondaryObjectiveComplete`, `0x00534440 IScript__PrimaryObjectiveFailed`, and `0x00534470 IScript__SecondaryObjectiveFailed` read integer arguments through datatype getter `+0x30`, write text ids, and set objective state values. |
| Primary objective arrays | Primary objective text writes use `DAT_008a9ae0 + index*8`; primary objective state writes use `DAT_008a9adc + index*8`, with state `1` for complete and state `2` for failed. |
| Secondary objective arrays | Secondary objective text writes use `DAT_008a9b30 + index*8`; secondary objective state writes use `DAT_008a9b2c + index*8`, with state `1` for complete and state `2` for failed. |
| Level outcome handlers | `0x005381a0 IScript__LevelLost` calls `CGame__DeclareLevelLost(&DAT_008a9a98,0,0)`; `0x005381c0 IScript__LevelLostString` reads `message_id` and calls `CGame__DeclareLevelLost(&DAT_008a9a98,message_id,0)`; `0x005381e0 IScript__LevelWon` calls `CGame__DeclareLevelWon(&DAT_008a9a98)`. |
| End-level bridge context | `0x0046d470 CGame__FillOutEndLevelData`, `0x0046f2f0 CGame__DeclareLevelWon`, `0x0046f430 CGame__DeclareLevelLost`, `0x0041bd00 CCareer__Update`, and `0x004496e0 CEndLevelData__IsAllSecondaryObjectivesComplete` preserve the static bridge into end-level snapshot/career context. |
| Loose event corpus | `mission-events-index.md` records `95` level rows, `795` event counts, `36` objective IDs, `115 primary-complete`, `42 secondary-complete`, `0 objective-complete`, `102 primary-failed`, `79 LevelWon`, and `13 LevelLost`. |
| Loose message corpus | `mission-message-usage.md` is kept separate: `67` rows, `1365` PlayCharMessage, `7` AddHelpMessage, `110 LevelLost-family`, and `71 LevelWon-family`. |

Evidence rows consumed by the schema:

| Evidence | Count |
| --- | ---: |
| Wave580 metadata/tag/xref/decompile rows | `6` / `6` / `6` / `6` |
| Wave580 instruction rows and vtable rows | `5454` / `36` |
| Wave585 metadata/tag/xref/decompile rows | `5` / `5` / `5` / `5` |
| Wave585 instruction rows | `1845` |
| Wave1049 primary metadata/xref/instruction/decompile rows | `10` / `13` / `761` / `10` |
| Wave1049 context metadata/xref/instruction/decompile rows | `12` / `23` / `6129` / `12` |

The event and message corpus counts are intentionally separate generated vocabularies. The event index provides objective/outcome counts; the message usage summary collapses `LevelLost*` and cannot distinguish `LevelLost()` from `LevelLostString(...)`.

## Why This Matters

This gives clean-room MissionScript planning a bounded command-effect bridge for objective state and level outcome commands: descriptor name, IScript handler, observed objective state/text arrays, CGame level-result calls, and end-level/career snapshot context. It deliberately leaves PostEvent, message/HUD/audio commands, slots/goodies/score, thing/spawn, live mission execution, and runtime mission outcomes for separate proof lanes.

## Claim Boundary

This proves static objective/outcome command-effect accounting from saved retail Ghidra evidence and public-safe loose-MSL corpus counts. It does not prove runtime MissionScript execution, runtime command effects, runtime objective UI behavior, runtime level outcome behavior, runtime save behavior, runtime career progression, live loose-MSL loading, packed-vs-loose script selection, exact command descriptor layout, exact arity, exact argument type schema, exact CGame layout, exact CCareer layout, exact END_LEVEL_DATA layout, BEA patching behavior, visual QA, Godot parity, rebuild parity, or no-noticeable-difference parity.
