# Ghidra Cockpit Lifecycle Review Wave988 Readiness Note

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 live correction closeout:** Historical record; `0x00405990` → `CDXCockpit__dtor_base_thunk` (was `CDXCockpit__dtor_base`). The original text below remains provenance rather than current semantic authority. It is superseded only where confirmed. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); final per-address decisions and exact before/after metadata are in `reverse-engineering/binary-analysis/ghidra-reviewed-correction-decisions-2026-07-13.jsonl` and `reverse-engineering/binary-analysis/ghidra-reviewed-correction-plan-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Status: complete read-only static evidence review
Date: 2026-05-31
Scope: `cockpit-lifecycle-review-wave988`

Wave988 re-reviewed the cockpit lifecycle owner group after the Wave900-Wave987 recheck gate. It made no Ghidra mutation: no rename, no signature change, no comment/tag change, no function-boundary change, no executable-byte change, no BEA launch, and no runtime/game-file mutation.

Primary cockpit rows:

| Address | Evidence |
| --- | --- |
| `0x00405970 CDXCockpit__scalar_deleting_dtor` | `CDXCockpit` RTTI/vtable slot `0x005d88b0[1]`; wrapper calls `0x00405990 CDXCockpit__dtor_base_thunk`, tests the delete flag, optionally calls `OID__FreeObject`, and returns `this`. |
| `0x00405990 CDXCockpit__dtor_base_thunk` | Jump thunk into `0x00424730 CCockpit__dtor_base`; reached from the CDXCockpit scalar-deleting destructor. |
| `0x004244b0 CCockpit__ctor` | Called from `0x00404dd0 CBattleEngine__Init` at `0x004055dc`; stores the owning battle-engine pointer at `+0x110`, initializes cockpit state, resolves render animation data, schedules event `0x7d1`, and returns `this`. |
| `0x00424710 CCockpit__scalar_deleting_dtor` | `CCockpit` vtable slot `0x005d9524[1]`; wrapper calls `0x00424730 CCockpit__dtor_base`, tests the delete flag, optionally calls `OID__FreeObject`, and returns `this`. |
| `0x00424730 CCockpit__dtor_base` | Resets `CCockpit` vtable slots `0x005d9524` and `0x005d94ac`, releases the owned `+0x8c` object through a vcall when present, and calls `0x004bac40 CMonitor__Shutdown` at `0x00424786`. |

Context rows:

- `0x00404dd0 CBattleEngine__Init`
- `0x00405a40 CBattleEngine__dtor_base`
- `0x0046dbc0 CMonitor__Shutdown_Thunk`
- `0x0049fa30 CMech__InitCockpit`
- `0x004bac40 CMonitor__Shutdown`

Read-back evidence:

- Fresh exports: 10 metadata rows, 10 tag rows, 169 xref rows, 1248 body-instruction rows, 10 decompile rows, 48 vtable-slot rows, and 3 vtable-type rows.
- Vtable type rows resolve `0x005d88b0` to `CDXCockpit`, and `0x005d9524` / `0x005d94ac` to `CCockpit`.
- Existing `test:ghidra-cockpit-compass-signature-correction` passed. Existing Wave321 cockpit/volume/UnitAI probe still resolves its 9 target rows but fails only on historical queue-total drift (`5876`/old debt expectations vs current `6222/6222` closure).
- Queue closure remains `6222/6222 = 100.00%`.
- Wave911 focused re-audit progress is `436/1408 = 30.97%`; expanded static surface progress is `502/1478 = 33.96%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260531-031646_post_wave988_cockpit_lifecycle_review_verified`, 19 files, 173837191 bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- The saved cockpit lifecycle names/signatures/comments remain internally coherent under fresh metadata/tag/xref/instruction/decompile/vtable exports.
- The CDXCockpit and CCockpit destructor rows have vtable-backed owner evidence and no stale `constructor` tag in the current tag export.
- The constructor row remains tied to the BattleEngine init callsite, and the destructor-base row remains tied to the monitor shutdown tail.

What remains separate:

- Runtime cockpit behavior.
- Exact `CCockpit` / `CDXCockpit` layout.
- Exact source-body identity.
- Full vtable slot semantics beyond the rows reviewed here.
- BEA patching behavior.
- Rebuild parity.
