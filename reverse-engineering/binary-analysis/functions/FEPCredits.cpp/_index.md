# FEPCredits.cpp - Function Analysis

## Overview

> **Queue status (2026-06-04):** Ghidra export-contract closure **6410/6410** (Wave1091: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

**Class:** `CFEPCredits` (RTTI type string `.?AVCFEPCredits@@` at `0x00629c78`)

This page owns credits-screen flow in the frontend vtable cluster rooted at `0x005db880`.
Source file content is not present in `references/Onslaught/`, so this mapping is retail-binary-first.

Wave855 static read-back (`fepcredits-transition-wave855`, `wave855-readback-verified`) hardened the final FEPCredits commentless row, `0x0051a970 CFEPCredits__TransitionNotification`. The body is important connective frontend infrastructure: it resets credits timing, starts the credits music selection, and clears the completion flag that `CFEPCredits__Render` sets when `CCredits__RenderCredits` finishes. Verified backup: `G:\GhidraBackups\BEA_20260525-110750_post_wave855_fepcredits_transition_verified`. Exact `CFEPCredits` layout, exact music-track semantics, runtime frontend behavior, source identity, BEA patching, and rebuild parity remain deferred.

Wave1091 static read-back (`credits-renderer-review-wave1091`, `wave1091-readback-verified`) re-read the FE credits-page vtable at `0x005db880` and saved comment/tag normalization for `0x0051a7f0 CFEPCredits__ButtonPressed`, `0x0051a820 CFEPCredits__Process`, `0x0051a880 CFEPCredits__RenderPreCommon`, `0x0051a8b0 CFEPCredits__Render`, and `0x0051a970 CFEPCredits__TransitionNotification`. CFEPCredits vtable export reported `9` OK slots. The page render body calls `0x0051a030 CCredits__RenderCredits` at `0x0051a92b`, and the game-outro path calls the same renderer from `0x00472801` inside `0x004726b0 CGame__RollCredits`. Shared static anchors include `0x00518bf0 CCredits__BuildDefaultEntries`, `DAT_00896ca8`, `CDXFont__DrawTextDynamic`, and `CMusic__PlaySelection`. Progress anchors: `6410/6410 = 100.00%`, `1545/1560 = 99.04%`, `812/1408 = 57.67%`, and `500/500 = 100.00%`. Verified backup: `G:\GhidraBackups\BEA_20260604-143442_post_wave1091_credits_renderer_review_verified`. Runtime credits rendering, frontend navigation behavior, concrete `CCredits` / `CFEPCredits` layout recovery, exact source-body identity, BEA patching, gameplay outcomes, and rebuild parity remain separate proof.

## Confirmed Mapping

| Address | Function | Role | Notes |
|---------|----------|------|-------|
| `0x0051a7f0` | `CFEPCredits__ButtonPressed` | vtable slot 3 | Handles button `0x2e` (back/exit): plays FE sound, returns to page `0x11` (time `0x1e`), resumes FE music |
| `0x0051a820` | `CFEPCredits__Process` | vtable slot 2 | Per-frame page process: watches completion flag at `this+0x08`, performs page/music return when set, and draws prompt code `0x2e` |
| `0x0051a880` | `CFEPCredits__RenderPreCommon` | vtable slot 4 | At `transition == 1.0`, issues FE pre-common pass (`FUN_004679e0(1.0, 0x3fffffff, dest)`) |
| `0x0051a8b0` | `CFEPCredits__Render` | vtable slot 5 | Computes fade alpha from `transition`, calls `CCredits__RenderCredits`, sets completion flag at `this+0x08` when done |
| `0x0051a970` | `CFEPCredits__TransitionNotification` | vtable slot 6 | Wave855 static read-back: DATA xref `0x005db898`; reads platform time, adds float delay `0x005d8ba0`, stores timer at `this+0x04`, calls `CMusic__PlaySelection(&DAT_00889a48, 1, 1)`, clears completion flag at `this+0x08`, returns with `RET 0x4` |

## Vtable Analysis (0x005db880)

RTTI CompleteObjectLocator:
- `0x005db87c` -> `0x00613ac8`
- `0x00613ac8 + 0x0c` -> type descriptor `0x00629c70` (name string at `0x00629c78`)

Current slot map:

| Slot | Address | Status | Notes |
|------|---------|--------|-------|
| 0 | `0x004fdc10` | mapped | inherited/common FE init-style helper |
| 1 | `0x0040c640` | mapped | `DebugTrace` placeholder |
| 2 | `0x0051a820` | mapped | `CFEPCredits__Process` |
| 3 | `0x0051a7f0` | mapped | `CFEPCredits__ButtonPressed` |
| 4 | `0x0051a880` | mapped | `CFEPCredits__RenderPreCommon` |
| 5 | `0x0051a8b0` | mapped | `CFEPCredits__Render` |
| 6 | `0x0051a970` | mapped | `CFEPCredits__TransitionNotification` |
| 7 | `0x004014c0` | mapped | inherited active-notification no-op |
| 8 | `0x00459990` | mapped | inherited deactive-notification no-op |

## Notes

- `0x0051a030` (`CCredits__RenderCredits`) is called from this vtable region (`0x0051a92b`) and from `CGame__RollCredits` (`0x004726b0`), tying page render behavior to the shared credits renderer.
- Calling-convention nuance in this runtime: slot-3/slot-4 read back as `__stdcall` signatures (`ButtonPressed(int button,float val)`, `RenderPreCommon(float transition,int dest)`) even though they are vtable targets; `this` is effectively hidden/unused in those bodies.
- Direct-HTTP mutation quirk observed in this wave: PATCH comment calls for `0x0051a7f0/0x0051a880/0x0051a8b0` returned `COMMENT_FAILED`, but immediate decompile read-back showed comments present. For this runtime, address-level read-back remains source of truth.

## Wave855 FEPCredits Transition (0x0051a970)

Wave855 FEPCredits transition saved comment/tags for `0x0051a970 CFEPCredits__TransitionNotification` without renames, signature changes, function-boundary changes, or executable-byte changes.

Read-back evidence:

| Evidence | Detail |
| --- | --- |
| Vtable slot | FE credits-page transition-notification vtable slot 6; `0x005db898` in CFEPCredits vtable `0x005db880` points to `0x0051a970 CFEPCredits__TransitionNotification`. |
| Timer reset | `PLATFORM__GetSysTimeFloat` result plus float delay `0x005d8ba0` is stored at `this+0x04`. |
| Music/lifecycle | Calls `CMusic__PlaySelection(&DAT_00889a48, 1, 1)`, clears completion flag `this+0x08`, ignores `from_page`, and returns with `RET 0x4`. |
| Credits-page context | Complements `CFEPCredits__Render`, which sets `this+0x08` when `CCredits__RenderCredits` finishes, and `CFEPCredits__Process/ButtonPressed`, which return to page `0x11` and resume frontend music. |
| Queue/backup | Post-Wave855 queue telemetry is `6098` total, `5756` commented, `342` commentless, strict proxy `5756/6098 = 94.39%`; next raw commentless row is `0x0051aa90 CFEPDirectory__Init`; verified backup `G:\GhidraBackups\BEA_20260525-110750_post_wave855_fepcredits_transition_verified`. |

This row is not low-importance code. It is evidence-sparse because there is no matching source file in `references/Onslaught/`, but the static vtable/body context makes it an important FE credits-page lifecycle hook.
