# CCarrier__Init

> Address: 0x00421a80 | Source: Carrier.cpp (source file not present in `references/Onslaught/` snapshot)

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes (headless postscript + read-back verified, refreshed 2026-05-10)
- **Verified vs Source:** No source-body match available (`Carrier.cpp` is not present in current `references/Onslaught/` snapshot)

## Purpose

Initialize a carrier object by allocating and configuring two child component objects. The carrier appears to be a transport vessel or aircraft carrier that holds other units.

## Signature
```c
void __thiscall CCarrier__Init(void * this, void * init);
```

Read-back verified by the Wave 318 Carrier/Carver correction artifacts under ignored `subagents/ghidra-static-reaudit/carrier-carver-wave318/current/` and guarded by `tools\ghidra_carrier_carver_boundary_signature_correction_probe.py`.

## Responsibilities

- **First allocation** - Allocates 0x20 byte object (type 0x17) at line 26
- **First vtable** - Sets vtable pointer to 0x005d940c
- **Store first child** - Saves pointer at this+0x208
- **Second allocation** - Allocates 0x60 byte object (type 0x16) at line 27
- **Second vtable** - Sets vtable pointer to 0x005d93d4
- **Store second child** - Saves pointer at this+0x13c
- **State flags** - Sets flags at this+0x7c, this+0x80, and related init fields from the init object
- **Flag OR** - ORs this+0x70 with 0xa100100

## Key Observations

- **Two component objects** - 0x20 and 0x60 byte allocations
- **Different vtables** - Each child has its own virtual method table
- **Exception safe** - Unwind handlers at 0x005d1840 and 0x005d1856
- **Called via FUN_0044d6f0** - Likely BattleEngine menu/UI initialization
- **Thiscall convention** - ECX = this pointer

## Current Evidence Boundary

Wave 318 saved a bounded function comment in Ghidra: Carrier init takes `this` plus an init object, seeds init flags at `+0x7c` / `+0x80` / `+0x70`, calls `CAirUnit__Init`, allocates two Carrier.cpp child helper objects at `+0x208` and `+0x13c`, and installs their vtables. This note intentionally avoids raw decompile excerpts and does not assign concrete structure field names.

Wave1129 (`wave1129-lifecycle-init-current-risk-review`) re-read and tag-normalized `0x00421a80 CCarrier__Init` as part of a `5 rows` score-22 lifecycle/init current-risk cluster with fresh Ghidra export evidence. Static anchors for the full cluster are `0x00405970 CDXCockpit__scalar_deleting_dtor`, `0x00421a80 CCarrier__Init`, `0x00422440 CCarver__Init`, `0x00422970 CCarverAI__CanStartAttack`, and `0x00424710 CCockpit__scalar_deleting_dtor`. Current focused accounting is `155/1179 = 13.15%`; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 1024; static closure remains `6410/6410 = 100.00%` with `0 / 0 / 0` debt. Mutation status was comment/tag normalization (`69 tags`) with no rename, signature, function-boundary, or executable-byte change. Verified backup: `G:\GhidraBackups\BEA_20260605-075206_post_wave1129_lifecycle_init_current_risk_review_verified`; previous completed backup: `G:\GhidraBackups\BEA_20260605-072044_post_wave1128_generalvolume_current_risk_review_verified`. Runtime carrier behavior, exact source-body identity, concrete layouts, BEA patching, gameplay outcomes, visual QA, and rebuild parity remain separate proof. Probe token anchor: Wave1129; wave1129-lifecycle-init-current-risk-review; 155/1179 = 13.15%; 5 rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 1024; score-22 lifecycle/init current-risk cluster; fresh Ghidra export; comment/tag normalization; 69 tags; 0 / 0 / 0; 0x00405970 CDXCockpit__scalar_deleting_dtor; 0x00421a80 CCarrier__Init; 0x00422440 CCarver__Init; 0x00422970 CCarverAI__CanStartAttack; 0x00424710 CCockpit__scalar_deleting_dtor; G:\GhidraBackups\BEA_20260605-075206_post_wave1129_lifecycle_init_current_risk_review_verified; G:\GhidraBackups\BEA_20260605-072044_post_wave1128_generalvolume_current_risk_review_verified.

## Notes

- Initially discovered via xref to debug path string at 0x006243bc
- Adjacent `CCarrierAI__scalar_deleting_dtor` and `CCarrierAI__dtor_base` are now documented in the Carrier index
- Carrier likely holds units/aircraft in game (aircraft carrier mechanics)
- Concrete layout, exact source virtual names, runtime carrier behavior, and rebuild parity remain unproven

## Related Functions

- [CUnit__Init](../Unit.cpp/CUnit__Init.md) - Base class initialization
- [CBattleEngine__Init](../BattleEngine.cpp/CBattleEngine__Init.md) - Calls carrier init

---
*Discovered via Phase 1 xref analysis (Dec 2025); refreshed by Wave 318 Ghidra Carrier/Carver correction on 2026-05-10.*
