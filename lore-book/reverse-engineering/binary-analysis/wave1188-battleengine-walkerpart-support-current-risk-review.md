# Wave1188 BattleEngine / WalkerPart Support Current-Risk Review

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 semantic revalidation:** `0x00406560` → `CBattleEngine__HandleLocks` (was `CBattleEngine__UpdateAutoTargetSetAndFireProjectiles`). Older conflicting text below is superseded for these rows. Use the [closeout](ghidra-full-reaudit-closeout-2026-07-13.md); exact records are in `reverse-engineering/binary-analysis/ghidra-full-reaudit-corrections-2026-07-13.json` and `reverse-engineering/binary-analysis/ghidra-targeted-revalidation-corrections-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Status: complete static current-risk comment/tag normalization; artifact and state closeout pushed
Date: 2026-06-06
Scope tag: `wave1188-battleengine-walkerpart-support-current-risk-review`

Wave1188 accounts for `8 BattleEngine/WalkerPart support current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator with fresh serialized Ghidra evidence:

- `0x00405a40 CBattleEngine__dtor_base`
- `0x00405f60 CBattleEngine__scalar_deleting_dtor`
- `0x004063b0 CBattleEngine__UpdateWeaponEffect`
- `0x00406460 CBattleEngine__SwapPrimarySecondaryPartReadersForState`
- `0x00406fc0 CBattleEngine__AddProjectile`
- `0x004080f0 CGame__IsWalkerGroundedOrCollision`
- `0x004145d0 CBattleEngineWalkerPart__GetWeaponPhysicsName`
- `0x00414610 CBattleEngineWalkerPart__GetWeaponIconName`

The saved Ghidra names and signatures were already bounded. This wave normalized saved comments and tags only, adding rebuild-grade static-contract anchors and explicit no-noticeable-difference boundary tags.

One Codex read-only consult was used and recommended this BattleEngine/WalkerPart support slice as more rebuild-relevant than the initial CRT-tail candidate. No Cursor/Composer was used.

Static closure remains `6411/6411 = 100.00%` with static debt `0 / 0 / 0`; expanded post-100 static surface remains `1560/1560 = 100.00%`; Wave911 focused is historical-retired/non-reconstructable at `812/1408 = 57.67%`; Wave911 top-500 remains `500/500 = 100.00%`; Wave1108 current focused accounting is now `801/1179 = 67.94%`; current risk candidates: 6166; current focused candidates: 1169; live regenerated current focused candidates: 1169; remaining active focused work: 378; focused threshold `15`; not Wave911 reconstruction.

Fresh exports verified `8` metadata rows, `8` tag rows, `16 xref rows`, `478 instruction rows`, and `8` decompile rows. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-160404_post_wave1188_battleengine_walkerpart_support_current_risk_review_verified`, `19` files, `176163719` bytes, `DiffCount=0`, `HashDiffCount=0`.

## Reviewed Rows

| Address | Name | Evidence |
| --- | --- | --- |
| `0x00405a40` | `CBattleEngine__dtor_base` | Called by `CBattleEngine__scalar_deleting_dtor`; installs BattleEngine vtables, drains particle-effect links at `this+0x620`, destroys active-reader projectile/target sets at `this+0x294` and `this+0x2a4`, releases walker/jet part objects at `this+0x578` / `this+0x57c`, clears parked reader state at `this+0x5ec` / `this+0x5f4`, removes monitored safe-pointer registrations, clears `CSPtrSet` members, and tail-calls `CUnit__dtor_base`. |
| `0x00405f60` | `CBattleEngine__scalar_deleting_dtor` | DATA xref `0x005d89c8`; calls `CBattleEngine__dtor_base`, checks delete flag bit 0, optionally frees `this` through `CDXMemoryManager__Free`, and returns `this`. |
| `0x004063b0` | `CBattleEngine__UpdateWeaponEffect` | Called by `CBattleEngine__HandleEvent` at `0x0040c1db` and `0x0040c27f`; samples vtable offsets `+0x40` / `+0xc0`, allocates a `0x20` CLine-like object from BattleEngine.cpp line `0x1f5`, writes squared range/timing fields, and submits through the nested manager at `this+0x38` vfunc `+0x24`. |
| `0x00406460` | `CBattleEngine__SwapPrimarySecondaryPartReadersForState` | Called from `CBattleEngine__Init`, `CUnit__ProcessStateSwapAndDeathChecks`, `CBattleEngine__Morph`, and `CGeneralVolume__ResetAndSetActiveReader`; branches on `this+0x260` and latch `this+0x5f0`, swaps `this+0x5ec` with `this+0x30`, parks/restores the active reader through `this+0x70` / `this+0x5f4`, and refreshes influence-map tracking. |
| `0x00406fc0` | `CBattleEngine__AddProjectile` | Called four times by `CBattleEngine__UpdateAutoTargetSetAndFireProjectiles`; skips targets with `target+0x2c` bit 2, scans tracked projectile set `this+0x294`, allocates a `0x14` active-reader entry from BattleEngine.cpp line `0x332`, sets reader/expiry/modeFlag using `DAT_00672fd0 + lifetime`, and appends through `CSPtrSet__AddToTail`. |
| `0x004080f0` | `CGame__IsWalkerGroundedOrCollision` | Called from `CGame__Update` at `0x0046eb8d` and `CPlayer__ReceiveButtonAction` at `0x004d31d3`; requires `battleEngine+0x260 == 2`, then returns true if BattleEngine vfunc `+0x10c` reports contact or `HeightDelta__Below015_D4` succeeds. |
| `0x004145d0` | `CBattleEngineWalkerPart__GetWeaponPhysicsName` | Called by `CBattleEngine__GetWeaponPhysicsName` at `0x0040c57f`; resolves current weapon through `CBattleEngineWalkerPart__GetCurrentWeapon`, then returns the first name pointer through weapon-data pointer `currentWeapon+0xa4`. |
| `0x00414610` | `CBattleEngineWalkerPart__GetWeaponIconName` | Called by `CBattleEngine__GetWeaponIconName` at `0x0040c59f`; resolves current weapon through `CBattleEngineWalkerPart__GetCurrentWeapon`, then returns the icon/name-like pointer at `weaponData+0x38` through `currentWeapon+0xa4`. |

## Mutation Summary

The wave saved comment/tag normalization only: dry/apply/final-dry reported `updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=8 tags_added=128 missing=0 bad=0`, then `updated=8 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=8 tags_added=128 missing=0 bad=0`, then `updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0`.

No rename, signature change, function-boundary change, executable-byte change, BEA launch, installed-game mutation, save mutation, or runtime-file mutation occurred.

## Boundary

This wave strengthens the BattleEngine/WalkerPart static contract needed for a rebuild-grade specification and a future clean-room implementation aiming at no noticeable difference from the original game. It does not prove exact BattleEngine/WalkerPart/CWeaponData/projectile-entry concrete layouts, exact source-body identity, runtime weapon/effect/projectile/morph/reader/grounded behavior, `weapon_fire_breaks_stealth` closure, BEA patching behavior, gameplay/visual outcomes, rebuild parity, or no-noticeable-difference parity.

Probe token anchor: Wave1188; wave1188-battleengine-walkerpart-support-current-risk-review; 801/1179 = 67.94%; 8 BattleEngine/WalkerPart support current-risk rows; current focused candidates: 1169; live regenerated current focused candidates: 1169; remaining active focused work: 378; current risk candidates: 6166; fresh Ghidra export; comment/tag normalization; updated=8 skipped=0; comment_only_updated=8; tags_added=128; final dry updated=0 skipped=8; no rename; no signature change; no function-boundary change; no executable-byte change; Codex read-only consult used; no Cursor/Composer; CBattleEngine__dtor_base; CBattleEngine__scalar_deleting_dtor; CBattleEngine__UpdateWeaponEffect; CBattleEngine__SwapPrimarySecondaryPartReadersForState; CBattleEngine__AddProjectile; CGame__IsWalkerGroundedOrCollision; CBattleEngineWalkerPart__GetWeaponPhysicsName; CBattleEngineWalkerPart__GetWeaponIconName; CBattleEngine__HandleEvent; CBattleEngine__UpdateAutoTargetSetAndFireProjectiles; CGame__Update; CPlayer__ReceiveButtonAction; CBattleEngine__GetWeaponPhysicsName; CBattleEngine__GetWeaponIconName; BattleEngine.cpp line 0x1f5; BattleEngine.cpp line 0x332; this+0x294; this+0x5ec; this+0x30; 0 / 0 / 0; 6411/6411 = 100.00%; 16 xref rows; 478 instruction rows; 8 decompile rows; [maintainer-local-ghidra-backup-root]\BEA_20260606-160404_post_wave1188_battleengine_walkerpart_support_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction; rebuild-grade static contracts; no noticeable difference; rebuild-grade specification.
