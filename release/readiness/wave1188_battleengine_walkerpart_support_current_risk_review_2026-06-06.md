# Wave1188 BattleEngine / WalkerPart Support Current-Risk Readiness Note

Status: complete static current-risk comment/tag normalization; artifact and state closeout pushed
Date: 2026-06-06
Scope: `wave1188-battleengine-walkerpart-support-current-risk-review`

Wave1188 accounts for `8 BattleEngine/WalkerPart support current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator:

- `0x00405a40 CBattleEngine__dtor_base`
- `0x00405f60 CBattleEngine__scalar_deleting_dtor`
- `0x004063b0 CBattleEngine__UpdateWeaponEffect`
- `0x00406460 CBattleEngine__SwapPrimarySecondaryPartReadersForState`
- `0x00406fc0 CBattleEngine__AddProjectile`
- `0x004080f0 CGame__IsWalkerGroundedOrCollision`
- `0x004145d0 CBattleEngineWalkerPart__GetWeaponPhysicsName`
- `0x00414610 CBattleEngineWalkerPart__GetWeaponIconName`

The saved Ghidra names/signatures were already bounded. The pass normalized saved comments and tags only; it made no rename, no signature change, no function-boundary change, and no executable-byte change.

Evidence:

- Ghidra dry/apply/final-dry: `updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=8 tags_added=128 missing=0 bad=0`, then `updated=8 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=8 tags_added=128 missing=0 bad=0`, then `updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0`.
- Fresh exports after apply: `8` metadata rows, `8` tag rows, `16 xref rows`, `478 instruction rows`, and `8` decompile rows.
- Queue refresh after apply: `6411` total functions, `6411` commented, `0` commentless, `0` exact-undefined signatures, `0` `param_N` signatures.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-160404_post_wave1188_battleengine_walkerpart_support_current_risk_review_verified`, `19` files, `176163719` bytes, `DiffCount=0`, `HashDiffCount=0`.
- Accounting: `801/1179 = 67.94%`, current focused candidates: 1169, live regenerated current focused candidates: 1169, remaining active focused work: 378, current risk candidates: 6166.

Static contract:

`CBattleEngine__dtor_base` and `CBattleEngine__scalar_deleting_dtor` bound the destructor/allocator cleanup path for BattleEngine-owned particle-effect links, active-reader sets, walker/jet part objects, parked readers, and safe-pointer registrations. `CBattleEngine__UpdateWeaponEffect` creates the BattleEngine.cpp line `0x1f5` CLine-like effect object and submits it through the nested manager. `CBattleEngine__SwapPrimarySecondaryPartReadersForState` binds mode/latch-driven reader swaps around `this+0x260`, `this+0x5f0`, `this+0x5ec`, `this+0x30`, `this+0x70`, and `this+0x5f4`. `CBattleEngine__AddProjectile` records the tracked projectile active-reader insertion path at `this+0x294` from BattleEngine.cpp line `0x332`. `CGame__IsWalkerGroundedOrCollision` bridges game update/input to BattleEngine walker collision/height gating. The WalkerPart name adapters bridge BattleEngine weapon name/icon requests into current weapon data.

One Codex read-only consult was used and recommended this BattleEngine/WalkerPart support slice. No Cursor/Composer was used.

Mutation boundary:

- Comment/tag normalization only.
- No rename.
- No signature change.
- No function-boundary change.
- No executable-byte change.
- No BEA launch, installed-game mutation, save mutation, or runtime-file mutation.

Static clean-room target: rebuild-grade static contracts as a rebuild-grade specification for a future clean-room implementation aiming at no noticeable difference from the original game.

Not proven here: exact BattleEngine/WalkerPart/CWeaponData/projectile-entry concrete layouts, exact source-body identity, runtime weapon/effect/projectile/morph/reader/grounded behavior, `weapon_fire_breaks_stealth` closure, BEA patching behavior, gameplay/visual outcomes, rebuild parity, or no-noticeable-difference parity.

Probe token anchor: Wave1188; wave1188-battleengine-walkerpart-support-current-risk-review; 801/1179 = 67.94%; 8 BattleEngine/WalkerPart support current-risk rows; current focused candidates: 1169; live regenerated current focused candidates: 1169; remaining active focused work: 378; current risk candidates: 6166; fresh Ghidra export; comment/tag normalization; updated=8 skipped=0; comment_only_updated=8; tags_added=128; final dry updated=0 skipped=8; no rename; no signature change; no function-boundary change; no executable-byte change; Codex read-only consult used; no Cursor/Composer; CBattleEngine__dtor_base; CBattleEngine__scalar_deleting_dtor; CBattleEngine__UpdateWeaponEffect; CBattleEngine__SwapPrimarySecondaryPartReadersForState; CBattleEngine__AddProjectile; CGame__IsWalkerGroundedOrCollision; CBattleEngineWalkerPart__GetWeaponPhysicsName; CBattleEngineWalkerPart__GetWeaponIconName; CBattleEngine__HandleEvent; CBattleEngine__UpdateAutoTargetSetAndFireProjectiles; CGame__Update; CPlayer__ReceiveButtonAction; CBattleEngine__GetWeaponPhysicsName; CBattleEngine__GetWeaponIconName; BattleEngine.cpp line 0x1f5; BattleEngine.cpp line 0x332; this+0x294; this+0x5ec; this+0x30; 0 / 0 / 0; 6411/6411 = 100.00%; 16 xref rows; 478 instruction rows; 8 decompile rows; [maintainer-local-ghidra-backup-root]\BEA_20260606-160404_post_wave1188_battleengine_walkerpart_support_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction; rebuild-grade static contracts; no noticeable difference; rebuild-grade specification.
