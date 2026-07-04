# Ghidra Round Vtable Boundary Review Wave1011 Readiness Note

Status: complete saved static read-back evidence
Date: 2026-05-31
Scope: `round-vtable-boundary-wave1011`

Wave1011 followed the raw caller from `0x004d8d07` into `0x0040ac50 CBattleEngine__Rearm` and recovered two previously missing CRound / CMissile-style shared vtable function boundaries: `0x004d8ac0 VFuncSlot_16_004d8ac0` and `0x004d8ae0 VFuncSlot_39_004d8ae0`. The pass created two function objects, saved bounded names/signatures/comments/tags, refreshed the function-quality queue to `6236/6236 = 100.00%`, and made no executable-byte change, no BEA launch, and no runtime/game-file mutation.

Primary reviewed anchors:

| Address | Evidence |
| --- | --- |
| `0x0040ac50 CBattleEngine__Rearm` | Existing source-backed BattleEngine rearm helper; Wave1011 proved the raw caller at `0x004d8d07` now belongs to the recovered `0x004d8ae0` slot-39 body. |
| `0x004d8ac0 VFuncSlot_16_004d8ac0` | DATA refs from CRound vtable `0x005de86c` and CMissile-style vtable `0x005e3be4`; compact scalar helper after `0x004d8abb RET`, reading `this+0xf0`, config `+0x2c`, config `+0x8c`, and globals `0x005d8584` / `0x005d85ec`. |
| `0x004d8ae0 VFuncSlot_39_004d8ae0` | DATA refs from CRound vtable `0x005de8c8` and CMissile-style vtable `0x005e3c40`; calls `CComplexThing__Hit`, `CBattleEngine__Rearm`, `CUnit__PlayImpactSoundForMaterials`, `CRound__UpdateEffectTransformByMode_004d9f30`, and `CEventManager__AddEvent_AtTime`, then clears `this+0x124` on one exit path. |
| `0x004d8dc0 VFuncSlot_02_004d8dc0` | Existing adjacent Wave494 shared CRound/CMissile slot-2 boundary; starts immediately after the recovered slot-39 body. |
| `0x004d8e40` | DATA refs from `0x005de934` and `0x005e3cac` show another missing shared vtable target; Wave1011 deliberately deferred it to a later focused wave because it is a larger separate body. |

Read-back evidence:

- Pre-review exports: 4 metadata rows, 5 xref rows, 145 raw caller instruction rows, 644 wide caller instruction rows, 1687 boundary-probe instruction rows, 7 pre-mutation metadata rows, 11 pre-mutation xref rows, and 69 body-instruction rows for existing context functions.
- Boundary apply dry/apply/final dry: dry reported `updated=0 skipped=0 created=0 would_create=2 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`; apply reported `updated=2 skipped=0 created=2 would_create=0 renamed=0 would_rename=0 signature_updated=2 comment_only_updated=0 missing=0 bad=0`; final dry reported `updated=0 skipped=2 created=0 would_create=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`.
- Final exports: 7 metadata rows, 2 tag rows, 11 xref rows, 234 body-instruction rows, and 2 decompile rows.
- Queue closure after refresh: `6236/6236 = 100.00%`, with 0 commentless functions, 0 exact-undefined signatures, and 0 `param_N` signatures.
- Re-audit progress after Wave1011: Wave911 focused `505/1408 = 35.87%`; expanded static surface `705/1491 = 47.28%`; Wave911 top-500 risk-ranked `409/500 = 81.80%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260531-172337_post_wave1011_round_vtable_boundary_verified`, 19 files, 173935495 bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- The recovered `0x004d8ac0` and `0x004d8ae0` rows now exist as saved function objects in the loaded Ghidra database.
- Both recovered rows have saved bounded names, signatures, comments, and `round-vtable-boundary-wave1011` / `wave1011-readback-verified` tags.
- Static xref, instruction, decompile, queue-refresh, and backup evidence support the saved function-boundary recovery and shared CRound/CMissile-style vtable classification.

What remains unproven:

- Exact source virtual names for the recovered slots.
- Runtime projectile, hit, collision, rearm, impact-sound, or event-scheduling behavior.
- Concrete CRound, CMissile, target, collision-report, round-config, or event layouts beyond observed offsets.
- The deferred `0x004d8e40` vtable target.
- BEA patching behavior.
- Rebuild parity.
