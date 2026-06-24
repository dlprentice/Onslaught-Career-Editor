# Ghidra Round Vtable Boundary Review Wave1012 Readiness Note

Status: complete saved static read-back evidence
Date: 2026-05-31
Scope: `round-vtable-boundary-wave1012`

Wave1012 continued the deferred CRound / CMissile-style shared vtable boundary review from Wave1011 and recovered two previously missing DATA-backed function objects: `0x004d8e40 VFuncSlot_66_004d8e40` and `0x004d9910 VFuncSlot_00_004d9910`. The pass created two function objects, saved bounded names/signatures/comments/tags, refreshed the function-quality queue to `6238/6238 = 100.00%`, and made no executable-byte change, no BEA launch, and no runtime/game-file mutation.

Primary reviewed anchors:

| Address | Evidence |
| --- | --- |
| `0x004d8dc0 VFuncSlot_02_004d8dc0` | Existing adjacent Wave494 shared CRound/CMissile slot-2 boundary; returns at `0x004d8e38` before the recovered slot-66 body starts. |
| `0x004d8e40 VFuncSlot_66_004d8e40` | DATA refs from CRound vtable `0x005de934` and CMissile-style vtable `0x005e3cac`; observed exits at `0x004d8e70`, `0x004d8f2a`, and `0x004d9904`; calls `ParticleEffectLink__SetHandleStateAndClear`, `CRound__RemoveActiveReaderById`, `Vec3__SetXYZ`, `CGeneralVolume__OffsetPointByForwardScaled`, `CUnit__PushTransformHistoryAndSetCurrent`, and `CRound__UpdateEffectTransformByMode_004d9f30`. |
| `0x004d9910 VFuncSlot_00_004d9910` | DATA refs from CRound vtable base `0x005de82c` and CMissile-style vtable base `0x005e3ba4`; SEH-framed event/switch body returns with `RET 0x4` at `0x004d9d43`; calls `CRound__SelectBestTargetReaderAndSyncAimState`, `CRound__SpawnConfiguredProjectile`, `CEngine__InitRoundLaunchStateDefaults`, `CRound__UpdateEffectTransformByMode_004d9f30`, and virtual slot `+0xc8` on some paths. |
| `0x004d9d10` | Pre-tail candidate exports intentionally left this as no standalone function: no external refs, internal branch path inside the recovered `0x004d9910` body. |
| `0x004d9d60 CEngine__InitRoundLaunchStateDefaults` | Existing saved function starts after the `0x004d9910` switch/jump-table region and remains a separate launch-state default initializer. |

Read-back evidence:

- Pre-review exports: 8 metadata rows, 8 tag rows, 606 xref rows, 601 narrow boundary instruction rows, 1681 wide boundary instruction rows, 61 pre-body instruction rows, 3 pre-decompile rows, 7 tail-candidate metadata rows, and 16 tail-candidate xref rows.
- Boundary apply dry/apply/final dry: dry reported `updated=0 skipped=0 created=0 would_create=2 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`; apply reported `updated=2 skipped=0 created=2 would_create=0 renamed=0 would_rename=0 signature_updated=2 comment_only_updated=0 missing=0 bad=0`; final dry reported `updated=0 skipped=2 created=0 would_create=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`.
- Final exports: 10 metadata rows, 10 tag rows, 609 xref rows, 1182 body-instruction rows, and 4 decompile rows.
- Queue closure after refresh: `6238/6238 = 100.00%`, with 0 commentless functions, 0 exact-undefined signatures, and 0 `param_N` signatures.
- Re-audit progress after Wave1012: Wave911 focused `505/1408 = 35.87%`; expanded static surface `707/1493 = 47.35%`; Wave911 top-500 risk-ranked `409/500 = 81.80%`.
- Verified backup: `G:\GhidraBackups\BEA_20260531-183252_post_wave1012_round_vtable_slot66_verified`, 18 files, 173968263 bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- The recovered `0x004d8e40` and `0x004d9910` rows now exist as saved function objects in the loaded Ghidra database.
- Both recovered rows have saved bounded names, signatures, comments, and `round-vtable-boundary-wave1012` / `wave1012-readback-verified` tags.
- Static xref, instruction, decompile, queue-refresh, and backup evidence support the saved function-boundary recovery and shared CRound/CMissile-style vtable classification.

What remains unproven:

- Exact source virtual names for the recovered slots.
- Runtime projectile, event, effect, active-reader, transform, or dispatch behavior.
- Concrete CRound, CMissile, event-record, target-reader, particle/effect, or round-config layouts beyond observed offsets.
- BEA patching behavior.
- Rebuild parity.
