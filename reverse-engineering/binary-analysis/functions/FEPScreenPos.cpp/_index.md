# FEPScreenPos.cpp - Function Analysis

## Overview

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

**Class:** `CFEPScreenPos` (RTTI string `.?AVCFEPScreenPos@@` at `0x00629db8`)

This FrontEnd page appears to handle screen-position calibration behavior.
Source file path/debug string has not yet been recovered from the current binary string set.

Wave859 CFEPScreenPos core (`fepscreenpos-core-wave859`, `wave859-readback-verified`) saved static retail Ghidra comments/tags/signatures for five important frontend/screen-position connective rows and corrected the two render signatures that still carried stale extra first parameters. Static evidence ties the tranche to CFEPScreenPos vtable `0x005db858`, calibration field writes at `this+0x04/+0x08`, career top-byte metadata persistence through CFEPOptions/CCareer helpers, the strings `Adjust Screen Position`, `Adjust Screen Position until display is`, and `correctly centered on your television.`, and next raw commentless row `0x0051ff90 CFEPVirtualKeyboard__Init`. Post-Wave859 queue telemetry is `6105` total, `5784` commented, `321` commentless, strict proxy `5784/6105 = 94.74%`; verified backup `[maintainer-local-ghidra-backup-root]\BEA_20260525-131538_post_wave859_fepscreenpos_core_verified`. Exact CFEPScreenPos layout, exact screen-axis semantics, runtime screen-position calibration behavior, runtime frontend/render/input behavior, BEA patching, and rebuild parity remain deferred.

## Confirmed Mapping

| Address | Function | Role | Notes |
|---------|----------|------|-------|
| `0x0051f9f0` | `CFEPScreenPos__Init` | vtable slot 0 | Zeroes two calibration state fields (`this+0x04/+0x08`) and returns `1` |
| `0x0051fa00` | `CFEPScreenPos__ButtonPressed` | vtable slot 3 | Handles calibration input (`0x2a/0x2b/0x36/0x37` adjust ranges, `0x2c/0x2e` page flow + restore path) and writes top-byte metadata via `CCareer__SetKillCounterTopByte_*` helpers |
| `0x0051fb60` | `CFEPScreenPos__RenderPreCommon` | vtable slot 4 | Pre-common transition draw helper (calls `FUN_004679e0` with fixed color `0x3fffffff`) |
| `0x0051fb90` | `CFEPScreenPos__Render` | vtable slot 5 | Main calibration render path; draws "Adjust Screen Position" text/overlays and applies transition alpha |
| `0x0051fd50` | `CFEPScreenPos__TransitionNotification` | vtable slot 6 | Seeds a `now+2.0` timer, syncs two page fields (`+0x04/+0x08`) from backing values (`+0x10/+0x14`), and calls `CFEPOptions__GetKillCounterTopBytes_23F4_23F8` |

## Wave859 CFEPScreenPos Core (0x0051f9f0-0x0051fd50)

Wave859 saved bounded static read-back evidence for the full CFEPScreenPos vtable-owned page slice without renames, function-boundary changes, or executable-byte changes.

| Address | Static read-back evidence |
| --- | --- |
| `0x0051f9f0 CFEPScreenPos__Init` | Vtable `0x005db858` slot 0; clears `this+0x04` and `this+0x08`; returns `1`. |
| `0x0051fa00 CFEPScreenPos__ButtonPressed` | Vtable slot 3; buttons `0x2a/0x2b` adjust `this+0x08` within `-0x32..0x40` and persist through `CCareer__SetKillCounterTopByte_23F8`; buttons `0x36/0x37` adjust `this+0x04` by four within `-0x3f..0x40` and persist through `CCareer__SetKillCounterTopByte_23F4`; button `0x2c` accepts page flow to page `0x11`, while button `0x2e` restores via `CFEPOptions__SetKillCounterTopBytes_23F4_23F8`. |
| `0x0051fb60 CFEPScreenPos__RenderPreCommon` | Corrected signature is `void __stdcall CFEPScreenPos__RenderPreCommon(float transition, int dest)`; raw instructions read only `[ESP+4]`/`[ESP+8]`, return with `RET 0x8`, and call `CFrontEnd__RenderPreCommonFade` when transition is `1.0`. |
| `0x0051fb90 CFEPScreenPos__Render` | Corrected signature is `void __stdcall CFEPScreenPos__Render(float transition, int dest)`; draws the screen-position text strings at `0x0063fcf0`, `0x0063fcc8`, and `0x0063fcb0`, context help prompts `5` and `6`, title bar, and overlay effects. |
| `0x0051fd50 CFEPScreenPos__TransitionNotification` | Vtable slot 6; stores `PLATFORM__GetSysTimeFloat()+delay` at `this+0x0c`, snapshots `CFEPOptions__GetKillCounterTopBytes_23F4_23F8` into `this+0x10/0x14`, then copies those values to active fields `this+0x04/0x08`. |

Read-back evidence: `ApplyFEPScreenPosCoreWave859.java` dry/apply/final dry reported `updated=5 skipped=0 renamed=0 would_rename=0 signature_updated=2 comment_only_updated=3 missing=0 bad=0`, then `updated=5 skipped=0 renamed=0 would_rename=0 signature_updated=2 comment_only_updated=3 missing=0 bad=0`, then `updated=0 skipped=5 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`. Post exports verified 5 metadata rows, 5 tag rows, 5 xref rows, 225 instruction rows, 5 decompile rows, 13 context metadata rows, 13 context decompile rows, and 18 vtable rows. This remains static Ghidra evidence only; exact runtime behavior and rebuild parity are deferred.

## Vtable Analysis (0x005db858)

RTTI CompleteObjectLocator:
- `0x005db854` -> `0x00613d10`
- `0x00613d10 + 0x0c` -> type descriptor `0x00629db0` (name string at `0x00629db8`)

Current slot map:

| Slot | Address | Status | Notes |
|------|---------|--------|-------|
| 0 | `0x0051f9f0` | mapped | `CFEPScreenPos__Init` |
| 1 | `0x0040c640` | mapped | `DebugTrace` placeholder in this class vtable |
| 2 | `0x00452b60` | mapped | inherited process no-op helper |
| 3 | `0x0051fa00` | mapped | `CFEPScreenPos__ButtonPressed` |
| 4 | `0x0051fb60` | mapped | `CFEPScreenPos__RenderPreCommon` |
| 5 | `0x0051fb90` | mapped | `CFEPScreenPos__Render` |
| 6 | `0x0051fd50` | mapped | `CFEPScreenPos__TransitionNotification` |
| 7 | `0x004014c0` | mapped | inherited active-notification no-op |
| 8 | `0x00459990` | mapped | inherited deactive no-op |
