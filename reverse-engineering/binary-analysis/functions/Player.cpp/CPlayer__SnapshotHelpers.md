# CPlayer Snapshot Helpers

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 live correction closeout:** `0x004d2b40` comment correction. Current live Ghidra reflects confirmed rows only; older conflicting text below is superseded only where confirmed. Use the [closeout](../../ghidra-full-reaudit-closeout-2026-07-13.md); final per-address decisions and exact before/after metadata are in `reverse-engineering/binary-analysis/ghidra-reviewed-correction-plan-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

> Addresses: `0x004d2a70`, `0x004d2ae0`, `0x004d2b40`, `0x004d2bb0`
>
> Source: `references/Onslaught/Player.cpp` / `references/Onslaught/Player.h`

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes (Wave471)
- **Verified vs Source:** Partial static source bridge; runtime camera behavior deferred

## Signatures
```c
void __thiscall CPlayer__GetCurrentViewPoint(void * this, void * out_current_view_point);
void __thiscall CPlayer__GetCurrentViewOrientation(void * this, void * out_current_view_orientation);
void __thiscall CPlayer__GetOldCurrentViewPoint(void * this, void * out_old_view_point);
void __thiscall CPlayer__GetOldCurrentViewOrientation(void * this, void * out_old_view_orientation);
```

## Key Observations
- All four helpers return with `RET 0x4`, matching one hidden-return/output pointer stack argument in the retail build.
- The point helpers write 16 bytes: zero fallback when no current camera exists, otherwise a copy from camera slot `0` for current position or slot `+0x8` for old position.
- The orientation helpers write 48 bytes: identity-matrix fallback copied from `DAT_0082b5c0`, optionally replaced by camera slot `+0x4` for current orientation or slot `+0xc` for old orientation.
- The retail code indexes the camera table through the player number field around `this + 0x2c` and `DAT_008a9d58`; the exact table/indexing convention remains unproven beyond static evidence.
- Source header evidence ties these to `FVector GetCurrentViewPoint()`, `FMatrix GetCurrentViewOrientation()`, `FVector GetOldCurrentViewPoint()`, and `FMatrix GetOldCurrentViewOrientation()`.

## Notes
- Wave471 removed stale `param_1`/`param_2` signatures from these four helpers and added bounded comments/tags.
- Runtime camera behavior, exact `CPlayer`/`FVector`/`FMatrix` layouts, camera-table indexing, BEA launch, game patching, and rebuild parity remain deferred.

## Related
- [CPlayer View Helpers](CPlayer__ViewHelpers.md)
- [CPlayer__GotoPanView](CPlayer__GotoPanView.md)
