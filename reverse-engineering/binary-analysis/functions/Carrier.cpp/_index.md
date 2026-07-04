# Carrier.cpp Functions

> Source File: Carrier.cpp | Binary: BEA.exe
> Debug Path: 0x006243bc

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

## Overview

Aircraft carrier/transport vessel implementation. The current retail-binary mapping is saved in Ghidra for the carrier init path plus two `CCarrierAI` cleanup helpers. `Carrier.cpp` source is not present in the current `references/Onslaught/` snapshot, so these are static retail-binary findings, not source-perfect identities.

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| 0x00421a80 | [CCarrier__Init](./CCarrier__Init.md) | Init path with base air-unit init, child helper allocation, and vtable setup | ~200 bytes |
| 0x00421b80 | CCarrierAI__scalar_deleting_dtor | Scalar-deleting destructor wrapper; corrects stale `CCarrierAI__VFunc_01_00421b80` | ~30 bytes |
| 0x00421ba0 | CCarrierAI__dtor_base | Destructor-base cleanup; corrects stale `CUnitAI__ctor_like_00421ba0` | ~150 bytes |
| 0x0050ee50 | CCarrier__scalar_deleting_dtor | Wave557 primary CCarrier vtable slot-1 wrapper; calls `CCarrier__Destructor` and optionally frees `this` on `delete_flags & 1` | ~32 bytes |
| 0x0050ef30 | CCarrier__Destructor | Wave557 primary CCarrier destructor body; clears owned pointer sets, removes the global-list node, then calls `CUnit__dtor_base` | ~112 bytes |

## Exception Handlers

| Address | Name | Line | Purpose |
|---------|------|------|---------|
| 0x005d1840 | Unwind@005d1840 | 26 | Cleanup for first allocation (0x20 bytes) |
| 0x005d1856 | Unwind@005d1856 | 27 | Cleanup for second allocation (0x60 bytes) |
| 0x005d1880 | Unwind@005d1880 | n/a | Carrier-region monitor shutdown cleanup for pointer at `EBP-0x10` |
| 0x005d1888 | Unwind@005d1888 | n/a | Carrier-region embedded active-reader cleanup at `*(EBP-0x10)+0xc` |
| 0x005d1893 | Unwind@005d1893 | n/a | Carrier-region embedded active-reader cleanup at `*(EBP-0x10)+0x24` |

## Key Observations

- **Carrier init** - Calls the base air-unit init path, sets init/state flags, allocates two child helper objects, stores them at `this+0x208` and `this+0x13c`, and installs their vtables.
- **Wave745 unwind continuation** - Saved static Ghidra comments/tags/signatures for `0x005d1840 Unwind@005d1840` through `0x005d1893 Unwind@005d1893` as the Carrier-region portion of the `unwind-continuation-wave745` tranche. The first two callbacks call `OID__FreeObject_Callback` with Carrier.cpp debug path `0x006243bc`, lines `0x1a`/`0x1b`, and memtypes `0x17`/`0x16`; the remaining callbacks clean monitor and embedded active-reader state. The full Wave745 tranche continues through `0x005d1a98 Unwind@005d1a98`, leaves raw commentless head `0x0042f220 CSPtrSet__Clear`, moves the high-signal head to `0x005d1aa3 Unwind@005d1aa3`, and has verified backup `[maintainer-local-ghidra-backup-root]\BEA_20260522-170426_post_wave745_unwind_continuation_verified`. Exact parent source-body identity, runtime exception behavior, runtime cleanup behavior, BEA patching, and rebuild parity remain unproven.
- **CarrierAI cleanup** - The adjacent `CCarrierAI` wrapper/base destructor functions reset monitor-style vtable state, unlink reader slots, optionally free `this`, and forward to monitor shutdown.
- **Wave1217 CarrierAI tag gap corrected** - Wave1217 (`wave1217-lifecycle-cleanup-tail-current-risk-review`) re-read and comment/tag-normalized `CCarrierAI__scalar_deleting_dtor` and the adjacent `CCarrierAI__dtor_base` context. CCarrierAI tag gap corrected: the pass corrected the empty `CCarrierAI__scalar_deleting_dtor` tag gap, preserved the saved names/signatures, and made no rename, signature, function-boundary, or executable-byte change. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260607-110625_post_wave1217_lifecycle_cleanup_tail_current_risk_review_verified`. Runtime CarrierAI cleanup behavior, exact layouts, exact source identity, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.
- **Wave557 primary cleanup** - `CCarrier__scalar_deleting_dtor` and `CCarrier__Destructor` are saved static Ghidra facts from primary vtable slot-1 read-back and direct xrefs. Exact source virtual names, concrete carrier layout, runtime destruction behavior, and rebuild parity remain unproven.
- **Wave1129 lifecycle/init current-risk review** - Wave1129 (`wave1129-lifecycle-init-current-risk-review`) re-read and tag-normalized `0x00421a80 CCarrier__Init` as part of a `5 rows` score-22 lifecycle/init current-risk cluster with fresh Ghidra export evidence. The same wave also covered `0x00405970 CDXCockpit__scalar_deleting_dtor`, `0x00422440 CCarver__Init`, `0x00422970 CCarverAI__CanStartAttack`, and `0x00424710 CCockpit__scalar_deleting_dtor`. Current focused accounting is `155/1179 = 13.15%`; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 1024; static closure remains `6410/6410 = 100.00%` with `0 / 0 / 0` debt. Mutation status was comment/tag normalization (`69 tags`) with no rename, signature, function-boundary, or executable-byte change. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-075206_post_wave1129_lifecycle_init_current_risk_review_verified`; previous completed backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-072044_post_wave1128_generalvolume_current_risk_review_verified`. Runtime carrier behavior, exact source-body identity, concrete layouts, BEA patching, gameplay outcomes, visual QA, and rebuild parity remain separate proof. Probe token anchor: Wave1129; wave1129-lifecycle-init-current-risk-review; 155/1179 = 13.15%; 5 rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 1024; score-22 lifecycle/init current-risk cluster; fresh Ghidra export; comment/tag normalization; 69 tags; 0 / 0 / 0; 0x00405970 CDXCockpit__scalar_deleting_dtor; 0x00421a80 CCarrier__Init; 0x00422440 CCarver__Init; 0x00422970 CCarverAI__CanStartAttack; 0x00424710 CCockpit__scalar_deleting_dtor; [maintainer-local-ghidra-backup-root]\BEA_20260605-075206_post_wave1129_lifecycle_init_current_risk_review_verified; [maintainer-local-ghidra-backup-root]\BEA_20260605-072044_post_wave1128_generalvolume_current_risk_review_verified.
- **Source boundary** - `Carrier.cpp` source body is absent from the current source snapshot; exact virtual names, concrete layouts, and runtime carrier behavior remain unproven.
- **Wave 318 read-back** - Metadata/decompile/xref/instruction/probe read-back verified the current signatures and comments after serialized headless apply.

## Related Files

- BattleEngine.cpp - Carrier is initialized during battle engine setup
- Unit.cpp - Carrier likely inherits from CUnit base class

---
*Initial entry discovered via Phase 1 xref analysis (Dec 2025); refreshed by Wave 318 Ghidra Carrier/Carver correction on 2026-05-10.*
