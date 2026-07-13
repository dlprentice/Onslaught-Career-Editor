# Wave1113 BattleEngine Wave936/Wave1010 Current-Risk Supersession Readiness Note

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 semantic revalidation:** Historical record; `0x00406560` → `CBattleEngine__HandleLocks` (was `CBattleEngine__UpdateAutoTargetSetAndFireProjectiles`). The original text below remains provenance rather than current semantic authority. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); exact records are in `reverse-engineering/binary-analysis/ghidra-full-reaudit-corrections-2026-07-13.json` and `reverse-engineering/binary-analysis/ghidra-targeted-revalidation-corrections-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Status: complete static supersession accounting
Date: 2026-06-05
Scope: `wave1113-battleengine-wave936-wave1010-current-risk-supersession`

Wave1113 accounts for `5 rows` from the Wave1108 current focused denominator as superseded by prior BattleEngine static evidence. It makes no Ghidra export, no mutation, no rename, no signature change, no function-boundary change, no executable-byte change, no BEA launch, and no installed-game/runtime-file mutation.

Accounting:

- Static Ghidra function-quality closure remains `6410/6410 = 100.00%`.
- Commentless / exact-undefined / `param_N` debt remains `0 / 0 / 0`.
- Expanded post-100 static surface remains `1560/1560 = 100.00%`.
- Wave1108 current focused denominator remains current focused candidates: 1179.
- Current focused supersession accounting moves to `33/1179 = 2.80%`.

Rows:

| Address | Saved row | Prior static evidence |
| --- | --- | --- |
| `0x00404dd0` | `CBattleEngine__Init` | Wave936 init/morph/volume review; DATA xref `0x005d89e8`; `RET 0x4`; init/morph/volume and stealth-adjacent field context. |
| `0x00406da0` | `CBattleEngine__SelectNearestForwardTargetFromGlobalSet` | Wave936 targeting read-back; calls from `CBattleEngine__UpdateAutoTargetSetAndFireProjectiles`; global target set `DAT_008550d0`; tracked set `+0x294`; `RET 0x18`. |
| `0x0040b6d0` | `CBattleEngine__HandleAutoAim` | Wave1010 zoom/auto-aim review; `CBattleEngine__HandleEvent` dispatch; MapWho/range/angle/trace filters; event `0x1773`; `RET 0x4`. |
| `0x0040dc30` | `CBattleEngine__EnableVolumeEntryGroupsByName` | Wave936 volume-entry read-back; DATA xref `0x005d8b5c`; `+0x578`/`+0x57c` general-volume enable dispatch; `RET 0x4`. |
| `0x0040dc60` | `CBattleEngine__DisableVolumeEntryGroupsByNameAndReselect` | Wave936 volume-entry read-back; DATA xref `0x005d8b60`; `+0x578`/`+0x57c` general-volume disable/reselect dispatch; `RET 0x4`. |

Evidence anchors:

- Wave936 `battleengine-init-morph-volume-review-wave936`: `6` primary metadata rows, `6` tag rows, `12` xref rows, `938` body-instruction rows, `6` decompile rows, `7` context metadata rows, `7` context tag rows, `22` context xref rows, `828` context instruction rows, and `7` context decompile rows.
- Wave1010 `battleengine-weapon-autoaim-review-wave1010`: `9` final metadata rows, `9` tag rows, `12` xref rows, `2044` body-instruction rows, and `9` decompile rows.
- Wave936 backup: `[maintainer-local-ghidra-backup-root]\BEA_20260528-013432_post_wave936_battleengine_init_morph_volume_review_verified`.
- Wave1010 backup: `[maintainer-local-ghidra-backup-root]\BEA_20260531-163000_post_wave1010_battleengine_zoom_autoaim_review_verified`.
- Latest completed Ghidra review backup remains `[maintainer-local-ghidra-backup-root]\BEA_20260604-200748_post_wave1100_cmeshpart_load_geometry_review_verified`.

Probe token anchor: Wave1113; wave1113-battleengine-wave936-wave1010-current-risk-supersession; 33/1179 = 2.80%; 5 rows; current focused candidates: 1179; Wave936; battleengine-init-morph-volume-review-wave936; Wave1010; battleengine-weapon-autoaim-review-wave1010; 0x00404dd0 CBattleEngine__Init; 0x00406da0 CBattleEngine__SelectNearestForwardTargetFromGlobalSet; 0x0040b6d0 CBattleEngine__HandleAutoAim; 0x0040dc30 CBattleEngine__EnableVolumeEntryGroupsByName; 0x0040dc60 CBattleEngine__DisableVolumeEntryGroupsByNameAndReselect; [maintainer-local-ghidra-backup-root]\BEA_20260528-013432_post_wave936_battleengine_init_morph_volume_review_verified; [maintainer-local-ghidra-backup-root]\BEA_20260531-163000_post_wave1010_battleengine_zoom_autoaim_review_verified; [maintainer-local-ghidra-backup-root]\BEA_20260604-200748_post_wave1100_cmeshpart_load_geometry_review_verified; no new Ghidra export; no mutation.

Boundary: this is static current-risk accounting only. Runtime init/targeting/auto-aim/volume behavior, `weapon_fire_breaks_stealth`, exact layouts, exact source-body identity, BEA patching, gameplay outcomes, visual QA, and rebuild parity remain separate proof.
