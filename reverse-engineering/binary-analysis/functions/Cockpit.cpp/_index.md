# Cockpit.cpp Functions

> Source File: Cockpit.cpp owner group | Binary: BEA.exe
> Debug Path: not confirmed in the tracked Stuart-source corpus

> **Queue status (2026-05-31):** Ghidra export-contract closure **6222/6222 = 100.00%** (Wave988 read-only cockpit lifecycle review; every exported function object remains commented with clean signatures; not runtime proof). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

## Overview

`CCockpit` and `CDXCockpit` are currently documented as Ghidra RTTI/vtable-backed owner groups. No dedicated tracked Stuart-source cockpit source file has been located in this repo, so the names below are conservative saved-Ghidra labels based on vtable, decompile, xref, and instruction evidence rather than exact source method names.

## Wave988 Cockpit Lifecycle Review

Wave988 (`cockpit-lifecycle-review-wave988`) re-reviewed the cockpit lifecycle rows after the Wave900-Wave987 recheck gate and made no Ghidra mutation. Fresh exports verified 10 metadata rows, 10 tag rows, 169 xref rows, 1248 body-instruction rows, 10 decompile rows, 48 vtable-slot rows, and 3 vtable-type rows. Primary anchors are `0x00405970 CDXCockpit__scalar_deleting_dtor`, `0x00405990 CDXCockpit__dtor_base_thunk`, `0x004244b0 CCockpit__ctor`, `0x00424710 CCockpit__scalar_deleting_dtor`, and `0x00424730 CCockpit__dtor_base`.

The read-only review ties `0x00405970` to `CDXCockpit` vtable `0x005d88b0[1]`, ties `0x00424710` to `CCockpit` vtable `0x005d9524[1]`, keeps `0x004244b0 CCockpit__ctor` anchored at the `CBattleEngine__Init` callsite `0x004055dc`, and keeps `0x00424730 CCockpit__dtor_base` anchored to `CMonitor__Shutdown` at `0x00424786`. The destructor rows have no stale `constructor` tag in the current tag export.

Queue closure remains `6222/6222 = 100.00%`. Wave911 focused re-audit progress is `436/1408 = 30.97%`; expanded static surface progress is `502/1478 = 33.96%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260531-031646_post_wave988_cockpit_lifecycle_review_verified`. Runtime cockpit behavior, exact `CCockpit` / `CDXCockpit` layouts, exact source-body identity, BEA patching, and rebuild parity remain separate proof.

Wave1058 (`cunitai-deploy-tracking-residual-review-wave1058`) re-read deploy-tracking residual context and saved function-tag normalization for `0x004244b0 CCockpit__ctor`, alongside GeneralVolume/UnitAI/BattleEngine/Mat34 rows. Fresh primary/context exports verified `5/5/5/802/5` and `10/10/53/915/10` rows; queue closure remains `6246/6246 = 100.00%`; Wave911 focused progress is `804/1408 = 57.10%`; expanded static surface progress is `1132/1509 = 75.02%`; top-500 coverage is `500/500 = 100.00%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-192010_post_wave1058_cunitai_deploy_tracking_residual_review_verified`. Runtime cockpit/deploy behavior, exact `CCockpit` layout, exact source-body identity, BEA patching, gameplay outcomes, and rebuild parity remain separate proof. Probe token anchor: Wave1058; cunitai-deploy-tracking-residual-review-wave1058; 0x004244b0 CCockpit__ctor; tag normalization.

Wave1129 (`wave1129-lifecycle-init-current-risk-review`) re-read and normalized comments/tags for `0x00405970 CDXCockpit__scalar_deleting_dtor` and `0x00424710 CCockpit__scalar_deleting_dtor` as part of a `5 rows` score-22 lifecycle/init current-risk cluster with fresh Ghidra export evidence. The same wave also covered `0x00421a80 CCarrier__Init`, `0x00422440 CCarver__Init`, and `0x00422970 CCarverAI__CanStartAttack`. Current focused accounting is `155/1179 = 13.15%`; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 1024; static closure remains `6410/6410 = 100.00%` with `0 / 0 / 0` debt. Mutation status was comment/tag normalization (`69 tags`) with no rename, signature, function-boundary, or executable-byte change. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-075206_post_wave1129_lifecycle_init_current_risk_review_verified`; previous completed backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-072044_post_wave1128_generalvolume_current_risk_review_verified`. Runtime cockpit behavior, exact source-body identity, concrete layouts, BEA patching, gameplay outcomes, visual QA, and rebuild parity remain separate proof. Probe token anchor: Wave1129; wave1129-lifecycle-init-current-risk-review; 155/1179 = 13.15%; 5 rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 1024; score-22 lifecycle/init current-risk cluster; fresh Ghidra export; comment/tag normalization; 69 tags; 0 / 0 / 0; 0x00405970 CDXCockpit__scalar_deleting_dtor; 0x00421a80 CCarrier__Init; 0x00422440 CCarver__Init; 0x00422970 CCarverAI__CanStartAttack; 0x00424710 CCockpit__scalar_deleting_dtor; [maintainer-local-ghidra-backup-root]\BEA_20260605-075206_post_wave1129_lifecycle_init_current_risk_review_verified; [maintainer-local-ghidra-backup-root]\BEA_20260605-072044_post_wave1128_generalvolume_current_risk_review_verified.

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| 0x00405970 | CDXCockpit__scalar_deleting_dtor | Scalar-deleting destructor wrapper that calls the CDXCockpit destructor-base thunk and optionally frees the object | ~32 bytes |
| 0x00405990 | CDXCockpit__dtor_base_thunk | Jump thunk that forwards CDXCockpit base destruction into the shared CCockpit destructor-base body | ~16 bytes |
| 0x004244b0 | [CCockpit__ctor](./CCockpit__ctor.md) | Constructor-like body called from `CBattleEngine__Init`; stores owning BattleEngine pointer, initializes cockpit matrices/state, resolves animation data, and schedules event `0x7d1` | ~600 bytes |
| 0x00424710 | CCockpit__scalar_deleting_dtor | Scalar-deleting destructor wrapper that calls CCockpit__dtor_base and optionally frees the object | ~32 bytes |
| 0x00424730 | CCockpit__dtor_base | Destructor-base body that resets CCockpit vtable slots, releases an owned object at `+0x8c`, and calls CMonitor__Shutdown | ~176 bytes |

## Key Observations

- **RTTI/vtable owners** - Vtable `0x005d88b0` resolves to `CDXCockpit`; vtable slots `0x005d9524` and `0x005d94ac` resolve to `CCockpit`.
- **Constructor callsite** - `CBattleEngine__Init` allocates a `0x130`-byte cockpit object, passes the owning BattleEngine as the lone explicit stack argument, and stores the constructed cockpit at BattleEngine `+0x528`.
- **Destructor wrappers** - `0x00405970` and `0x00424710` both have scalar-deleting destructor shape: base-dtor call, delete-flag test, optional `OID__FreeObject`, `this` return, and one stack argument.
- **Shared base cleanup** - `0x00424730` resets the two CCockpit vtable slots, releases the `+0x8c` owned object through its vtable when present, clears that field, and calls `CMonitor__Shutdown`.
- **Superseded owner** - Wave 314 corrected the older `0x00418120` `CCockpit__AdvanceOpenCloseAnimationState` label to `CBuilding__AdvanceOpenCloseAnimationState` from CBuilding vtable evidence.
- **Wave 321 correction** - Saved `0x004244b0` as `CCockpit__ctor` with signature `void * __thiscall CCockpit__ctor(void * this, void * battleEngine)`, replacing the stale extra `param_2`.
- **Proof boundary** - Exact source virtual names, concrete layouts, tags, local variables, runtime behavior, and rebuild parity remain open.

## Related Files

- `DXCompass.cpp` - DirectX compass HUD helpers; this same wave hardened two tracked-position getter signatures.
- `Hud.cpp` - HUD setup and component ownership context.
- `Monitor.cpp` / CMonitor owner group - base shutdown path reached by `CCockpit__dtor_base`.

---
*Updated by Wave988 cockpit lifecycle read-only review (2026-05-31).*

## Wave1151 Current-Risk Tag Normalization

Wave1151 tag-only normalization also covers `0x00405990 CDXCockpit__dtor_base_thunk` as a score21 current-risk row. It preserves the destructor jump-thunk evidence into `CCockpit__dtor_base` and adds Wave1151/current-risk tags only; no semantic mutation was made. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-201419_post_wave1151_mixed_score21_current_risk_review_verified`. Runtime behavior, exact layouts, exact source-body identity, BEA patching behavior, gameplay outcomes, visual QA, and rebuild parity remain separate proof.
