# Wave1113 BattleEngine Wave936/Wave1010 Current-Risk Supersession

Status: complete static supersession accounting
Last updated: 2026-06-05
Scope: `wave1113-battleengine-wave936-wave1010-current-risk-supersession`

Wave1113 accounts for `5 rows` from the Wave1108 current focused denominator as already covered by Wave936 `battleengine-init-morph-volume-review-wave936` and Wave1010 `battleengine-weapon-autoaim-review-wave1010` static evidence. This is no new Ghidra export, no mutation, no executable-byte change, no BEA launch, and no installed-game/runtime-file mutation.

## Accounting

| Track | Current |
| --- | ---: |
| Static Ghidra function-quality closure | `6410/6410 = 100.00%` |
| Commentless / exact-undefined / `param_N` debt | `0 / 0 / 0` |
| Expanded post-100 static surface | `1560/1560 = 100.00%` |
| Wave1108 current focused candidates | current focused candidates: 1179 |
| Wave1113 current focused supersession accounting | `33/1179 = 2.80%` |

## Superseded Rows

| Address | Saved row | Prior evidence |
| --- | --- | --- |
| `0x00404dd0` | `CBattleEngine__Init` | Wave936 re-read vtable DATA xref `0x005d89e8`, `RET 0x4`, init/morph/volume context, `+0x578`/`+0x57c` general-volume fields, state `+0x260`, and stealth-adjacent fields `+0x5d4/+0x5d8/+0x5dc`. |
| `0x00406da0` | `CBattleEngine__SelectNearestForwardTargetFromGlobalSet` | Wave936 re-read calls from `CBattleEngine__UpdateAutoTargetSetAndFireProjectiles`, `DAT_008550d0` global target set traversal, profile/mask/range/forward-facing candidate filters, tracked-set exclusion `+0x294`, and `RET 0x18`. |
| `0x0040b6d0` | `CBattleEngine__HandleAutoAim` | Wave1010 re-read source-backed auto-aim handler context, DATA/event dispatch through `CBattleEngine__HandleEvent`, `RET 0x4`, active-reader clearing, MapWho scan, range/angle/trace filters, and event `0x1773` rescheduling evidence. |
| `0x0040dc30` | `CBattleEngine__EnableVolumeEntryGroupsByName` | Wave936 re-read DATA xref `0x005d8b5c`, `RET 0x4`, `+0x578` dispatch through `CGeneralVolume__EnableEntriesByName`, and `+0x57c` dispatch through `CGeneralVolume__EnableLinkedEntriesByName`. |
| `0x0040dc60` | `CBattleEngine__DisableVolumeEntryGroupsByNameAndReselect` | Wave936 re-read DATA xref `0x005d8b60`, `RET 0x4`, `+0x578` dispatch through `CGeneralVolume__DisableEntriesByNameAndReselect`, and `+0x57c` dispatch through `CGeneralVolume__DisableLinkedEntriesByNameAndReselect`. |

Wave936 verified `6` primary metadata rows, `6` tag rows, `12` xref rows, `938` body-instruction rows, and `6` decompile rows, plus `7` context metadata rows, `7` context tag rows, `22` context xref rows, `828` context instruction rows, and `7` context decompile rows. Wave1010 final exports verified `9` metadata rows, `9` tag rows, `12` xref rows, `2044` body-instruction rows, and `9` decompile rows.

Wave936 backup: `G:\GhidraBackups\BEA_20260528-013432_post_wave936_battleengine_init_morph_volume_review_verified`.

Wave1010 backup: `G:\GhidraBackups\BEA_20260531-163000_post_wave1010_battleengine_zoom_autoaim_review_verified`.

Latest completed Ghidra review backup remains `G:\GhidraBackups\BEA_20260604-200748_post_wave1100_cmeshpart_load_geometry_review_verified`.

Probe token anchor: Wave1113; wave1113-battleengine-wave936-wave1010-current-risk-supersession; 33/1179 = 2.80%; 5 rows; current focused candidates: 1179; Wave936; battleengine-init-morph-volume-review-wave936; Wave1010; battleengine-weapon-autoaim-review-wave1010; 0x00404dd0 CBattleEngine__Init; 0x00406da0 CBattleEngine__SelectNearestForwardTargetFromGlobalSet; 0x0040b6d0 CBattleEngine__HandleAutoAim; 0x0040dc30 CBattleEngine__EnableVolumeEntryGroupsByName; 0x0040dc60 CBattleEngine__DisableVolumeEntryGroupsByNameAndReselect; G:\GhidraBackups\BEA_20260528-013432_post_wave936_battleengine_init_morph_volume_review_verified; G:\GhidraBackups\BEA_20260531-163000_post_wave1010_battleengine_zoom_autoaim_review_verified; G:\GhidraBackups\BEA_20260604-200748_post_wave1100_cmeshpart_load_geometry_review_verified; no new Ghidra export; no mutation.

## Boundary

This wave closes current-risk accounting for these five rows only. It does not prove runtime init behavior, runtime targeting behavior, runtime auto-aim behavior, runtime volume behavior, `weapon_fire_breaks_stealth`, exact `CBattleEngine`/target/profile/general-volume layouts, exact source-body identity, BEA patching behavior, gameplay outcomes, visual QA, or rebuild parity.
