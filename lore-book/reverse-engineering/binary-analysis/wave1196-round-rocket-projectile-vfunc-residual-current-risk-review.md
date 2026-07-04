# Wave1196 Round/Rocket Projectile Vfunc Residual Current-Risk Review

Status: complete static read-back evidence
Date: 2026-06-06
Tag: `wave1196-round-rocket-projectile-vfunc-residual-current-risk-review`

Wave1196 accounts for `4 Round/Rocket projectile vfunc residual score17 current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator. It uses fresh Ghidra metadata, tag, xref, instruction, and decompile exports plus saved comment/tag normalization to make these residual projectile vfunc rows explicit rebuild-grade static contracts.

The pass preserved existing names and signatures. It made no rename, no signature change, no function-boundary change, and no executable-byte change.

## Counted Rows

| Address | Function | Static contract |
| --- | --- | --- |
| `0x004d8ae0` | `VFuncSlot_39_004d8ae0` | Shared CRound/CMissile slot 39 via DATA refs `0x005de8c8` and `0x005e3c40`; calls `CComplexThing__Hit`, can call `CBattleEngine__Rearm`, calls `CUnit__PlayImpactSoundForMaterials`, calls `CRound__UpdateEffectTransformByMode_004d9f30`, schedules event `2000` through `CEventManager__AddEvent_AtTime`, and clears `this+0x124`. |
| `0x004d8e40` | `VFuncSlot_66_004d8e40` | Shared CRound/CMissile slot 66 via DATA refs `0x005de934` and `0x005e3cac`; touches `this+0xe0/+0xe4/+0xe8/+0xec/+0xf0/+0x120`, clears particle/effect links, removes active-reader state, calls `Vec3__SetXYZ`, `CGeneralVolume__OffsetPointByForwardScaled`, `CUnit__PushTransformHistoryAndSetCurrent`, and `CRound__UpdateEffectTransformByMode_004d9f30`. |
| `0x004d9910` | `VFuncSlot_00_004d9910` | Shared CRound/CMissile vtable base slot 0 via DATA refs `0x005de82c` and `0x005e3ba4`; SEH-framed dispatcher that switches on `event_record+4` and routes target sync, configured projectile spawn, launch-state defaults, effect transforms, event scheduling, actor event forwarding, and a CRound-style virtual slot `+0xc8` path. |
| `0x004d8040` | `CRocket__VFunc_22_CreateBigRocketEngineEffects` | CRocket slot 22 via DATA ref `0x005dd4b0`; sets `this+0xe4`, resolves `Big Rocket Engine Effect` through `CParticleSet__FindByNameAndTrackLinkSlot`, and creates four particle effects with output handle slots starting at `this+0xec` and global effect vector payload `0x0083cc48..0x0083cc54`. |

## Evidence

| Item | Result |
| --- | --- |
| Pre/post rows | `4` metadata rows, `4` tag rows, `7 xref rows`, `1386 instruction rows`, and `4 decompile rows` |
| Dry run | `updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=4 tags_added=47 missing=0 bad=0` |
| Apply | `updated=4 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=4 tags_added=47 missing=0 bad=0`; `REPORT: Save succeeded` |
| Final dry | `updated=0 skipped=4 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0` |
| Backup | `[maintainer-local-ghidra-backup-root]\BEA_20260606-204237_post_wave1196_round_rocket_projectile_vfunc_residual_current_risk_review_verified` |

Static closure remains `6411/6411 = 100.00%` with `0 / 0 / 0` debt. Expanded static surface remains `1560/1560 = 100.00%`. Wave1108 current focused accounting is now `881/1179 = 74.72%`; current risk candidates: 6166; current focused candidates: 1142; live regenerated current focused candidates: 1142; remaining active focused work: 298; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.

## Boundary

This wave proves static retail Ghidra read-back for the selected projectile vfunc residuals and records their rebuild-grade static contracts. It does not prove exact source virtual names, exact hit/collision/event/effect layouts, concrete CRound/CMissile/CRocket/particle-handle layouts, runtime projectile behavior, runtime engine-effect behavior, BEA patching behavior, rebuild parity, or no-noticeable-difference parity.

Probe token anchor: Wave1196; wave1196-round-rocket-projectile-vfunc-residual-current-risk-review; 881/1179 = 74.72%; 4 Round/Rocket projectile vfunc residual score17 current-risk rows; current focused candidates: 1142; live regenerated current focused candidates: 1142; remaining active focused work: 298; current risk candidates: 6166; fresh Ghidra export; comment/tag normalization; updated=4 skipped=0; comment_only_updated=4; tags_added=47; final dry updated=0 skipped=4; no rename; no signature change; no function-boundary change; no executable-byte change; Codex read-only consults used; no Cursor/Composer; VFuncSlot_39_004d8ae0; VFuncSlot_66_004d8e40; VFuncSlot_00_004d9910; CRocket__VFunc_22_CreateBigRocketEngineEffects; 0 / 0 / 0; 6411/6411 = 100.00%; 7 xref rows; 1386 instruction rows; 4 decompile rows; [maintainer-local-ghidra-backup-root]\BEA_20260606-204237_post_wave1196_round_rocket_projectile_vfunc_residual_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction; rebuild-grade static contracts; no noticeable difference; rebuild-grade specification.
