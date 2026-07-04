# Ghidra Projectile-Burst Spawn Spine Review Wave1020

Status: complete static read-only evidence
Date: 2026-05-31
Scope: `projectile-burst-spawn-spine-review-wave1020`

Wave1020 re-read the projectile-burst spawn spine with no mutation, no rename, no signature change, no comment change, no tag change, no function-boundary change, no executable-byte change, no BEA launch, and no runtime/game-file mutation.

Primary anchors:

| Address | Evidence |
| --- | --- |
| `0x005069f0 ProjectileBurst__SpawnFromCurrentPreset` | Current-preset projectile-burst body; creates projectile/effect objects from `burstContext +0xa0`; called by the percent-bucket fallback and `CWeapon__HandleFireBurstEvent`; calls `ProjectileBurstPreset__GetListEntryIdByIndex` at `0x00506b75` and `CShell__CopyResourceNameToInlineBuffer` at `0x005076dc`. |
| `0x00506010 ProjectileBurst__SpawnFromPercentBucketFallback` | Percent-bucket fallback dispatcher; uses `burstContext +0xa4`, calls current-preset body at `0x00506143`, pushes follow-up event `0x1389` at `0x005061ca`, and is reached from bounded caller rows including `ProjectileBurstCallerBoundary_0044e020`, `ProjectileBurstCallerBoundary_004f4920`, `CGeneralVolume__DispatchMode3BurstProgressAndSpawn`, `CBattleEngineWalkerPart__ChargeWeapon`, and `CBattleEngineWalkerPart__FireWeapon`. |
| `0x00506930 CWeapon__HandleFireBurstEvent` | DATA pointer at `0x005dfc94`; checks event id `0x1389` at `0x00506937`, calls the current-preset body at `0x005069b6`, and schedules another `0x1389` event at `0x005069d7`. |
| `0x004d9f30 CRound__UpdateEffectTransformByMode_004d9f30` | Prior Wave495 CRound-style effect-transform helper still matches current xref/decompile evidence; callers include `CRound__UpdateRoundAndTriggerLaunchEffect` and recovered CRound/CMissile-style vtable slots. |
| `0x004df530 CShell__CopyResourceNameToInlineBuffer` | Prior Wave507 CShell resource-name helper still matches current evidence; `RET 0x4` and callsite `0x005076dc` preserve the single `resource_name` argument and inline-buffer copy at `this+0x110`. |

Context exports covered `0x005078b0 ProjectileBurstPreset__GetListEntryIdByIndex`, `0x005068f0 CWeapon__AdvanceChargeProgressIfAnySlotAssigned`, `0x004daa20 CEngine__FindPresetIndexByName`, `0x004db150 CRound__SpawnConfiguredProjectile`, `0x004dea50 CSentinel__Init`, `0x0044e020 ProjectileBurstCallerBoundary_0044e020`, and `0x004f4920 ProjectileBurstCallerBoundary_004f4920`. The `0x005dfc94` pointer-table export confirms slot `0` points to `CWeapon__HandleFireBurstEvent` and slot `1` points to `CWeapon__scalar_deleting_dtor`; the neighboring pointer-table rows are not promoted as a contiguous CWeapon vtable claim.

Read-back evidence:

- Primary exports: 5 metadata rows, 5 tag rows, 22 xref rows, 1651 body-instruction rows, and 5 decompile rows.
- Context exports: 7 metadata rows, 9 xref rows, 970 body-instruction rows, and 7 decompile rows.
- Pointer table export: 48 rows from `0x005dfc94`.
- Export-contract function-quality closure remains `6238/6238 = 100.00%` with 0 commentless, 0 exact-undefined signatures, and 0 `param_N` signatures.
- Wave911 focused re-audit progress advances to `528/1408 = 37.50%`.
- Expanded static surface progress advances to `757/1493 = 50.70%`.
- Wave911 top-500 risk-ranked coverage advances to `456/500 = 91.20%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260531-214433_post_wave1020_projectile_burst_spawn_spine_review_verified`, 19 files, 173968263 bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- The selected saved names, signatures, comments, xrefs, instruction anchors, and decompile rows remain coherent in the loaded Ghidra database.
- The projectile-burst current-preset/fallback/event rows connect to weapon, GeneralVolume, WalkerPart, Sentinel, CRound, and CShell static evidence without needing a new mutation.

What remains separate proof:

- Runtime stealth behavior.
- `weapon_fire_breaks_stealth`.
- Runtime projectile behavior.
- Exact source-body identity.
- Concrete weapon/projectile/burst/round/shell layouts.
- BEA patching behavior.
- Rebuild parity.

Probe token anchor: Wave1020; projectile-burst-spawn-spine-review-wave1020; 0x005069f0 ProjectileBurst__SpawnFromCurrentPreset; 0x00506010 ProjectileBurst__SpawnFromPercentBucketFallback; 0x00506930 CWeapon__HandleFireBurstEvent; 0x004d9f30 CRound__UpdateEffectTransformByMode_004d9f30; 0x004df530 CShell__CopyResourceNameToInlineBuffer; 528/1408 = 37.50%; 757/1493 = 50.70%; 456/500 = 91.20%; 6238/6238 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260531-214433_post_wave1020_projectile_burst_spawn_spine_review_verified; no mutation.
