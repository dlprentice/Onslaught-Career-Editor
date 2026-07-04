# Wave1196 Round/Rocket Projectile Vfunc Residual Current-Risk Review

Status: complete static read-back evidence
Date: 2026-06-06
Tag: `wave1196-round-rocket-projectile-vfunc-residual-current-risk-review`

Wave1196 accounts for `4 Round/Rocket projectile vfunc residual score17 current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator. It normalizes rebuild-grade static comments and tags for the shared CRound/CMissile projectile vfunc residuals plus the CRocket engine-effect vfunc residual.

The pass saved comment/tag normalization only: no rename, no signature change, no function-boundary change, and no executable-byte change.

Representative anchors:

| Address | Function | Static contract |
| --- | --- | --- |
| `0x004d8ae0` | `VFuncSlot_39_004d8ae0` | Shared CRound/CMissile slot 39 via DATA refs `0x005de8c8` and `0x005e3c40`; calls `CComplexThing__Hit`, can call `CBattleEngine__Rearm`, plays material impact sound, updates round effect transform, schedules event `2000`, and clears `this+0x124`. |
| `0x004d8e40` | `VFuncSlot_66_004d8e40` | Shared CRound/CMissile slot 66 via DATA refs `0x005de934` and `0x005e3cac`; clears particle/effect links, removes active-reader state, offsets the forward point, pushes transform history, and updates effect transform. |
| `0x004d9910` | `VFuncSlot_00_004d9910` | Shared CRound/CMissile vtable base slot 0 via DATA refs `0x005de82c` and `0x005e3ba4`; SEH-framed event/switch dispatcher over `event_record+4` that routes target sync, configured projectile spawn, launch-state defaults, effect transforms, event scheduling, and base actor event handling. |
| `0x004d8040` | `CRocket__VFunc_22_CreateBigRocketEngineEffects` | CRocket slot 22 via DATA ref `0x005dd4b0`; resolves `Big Rocket Engine Effect` and creates four particle effects through `CParticleManager__CreateEffect` into handle slots beginning at `this+0xec`. |

Read-back evidence:

| Item | Result |
| --- | --- |
| Pre/post rows | `4` metadata rows, `4` tag rows, `7 xref rows`, `1386 instruction rows`, and `4 decompile rows` |
| Dry run | `updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=4 tags_added=47 missing=0 bad=0` |
| Apply | `updated=4 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=4 tags_added=47 missing=0 bad=0`; `REPORT: Save succeeded` |
| Final dry | `updated=0 skipped=4 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0` |
| Backup | `[maintainer-local-ghidra-backup-root]\BEA_20260606-204237_post_wave1196_round_rocket_projectile_vfunc_residual_current_risk_review_verified` |

Static closure remains `6411/6411 = 100.00%` with `0 / 0 / 0` debt. Expanded static surface remains `1560/1560 = 100.00%`. Wave1108 current focused accounting is now `881/1179 = 74.72%`; current risk candidates: 6166; current focused candidates: 1142; live regenerated current focused candidates: 1142; remaining active focused work: 298; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.

Fresh quality snapshot and current-risk rank were regenerated after the Ghidra write. The live rank still keeps these and other reviewed rows in focused candidates because expected source-identity, exact-layout, runtime/rebuild, generic-name-shape, and critical-family signals remain intentionally deferred; the continuity accounting records that these rows have received bounded static current-risk treatment.

Static clean-room target: rebuild-grade static contracts as a rebuild-grade specification for a future clean-room implementation aiming at no noticeable difference. Exact source virtual names, exact hit/collision/event/effect layouts, concrete CRound/CMissile/CRocket/particle-handle layouts, runtime projectile behavior, runtime engine-effect behavior, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.

Probe token anchor: Wave1196; wave1196-round-rocket-projectile-vfunc-residual-current-risk-review; 881/1179 = 74.72%; 4 Round/Rocket projectile vfunc residual score17 current-risk rows; current focused candidates: 1142; live regenerated current focused candidates: 1142; remaining active focused work: 298; current risk candidates: 6166; fresh Ghidra export; comment/tag normalization; updated=4 skipped=0; comment_only_updated=4; tags_added=47; final dry updated=0 skipped=4; no rename; no signature change; no function-boundary change; no executable-byte change; Codex read-only consults used; no Cursor/Composer; VFuncSlot_39_004d8ae0; VFuncSlot_66_004d8e40; VFuncSlot_00_004d9910; CRocket__VFunc_22_CreateBigRocketEngineEffects; 0 / 0 / 0; 6411/6411 = 100.00%; 7 xref rows; 1386 instruction rows; 4 decompile rows; [maintainer-local-ghidra-backup-root]\BEA_20260606-204237_post_wave1196_round_rocket_projectile_vfunc_residual_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction; rebuild-grade static contracts; no noticeable difference; rebuild-grade specification.
