# Credits.cpp - Function Analysis

> **Queue status (2026-06-04):** Ghidra export-contract closure **6410/6410** (Wave1091: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

## Overview

Retail binary includes a credits renderer class/function path referenced by game outro flow and frontend credits-page code.
Source clue: `references/Onslaught/game.cpp` includes `Credits.h` and calls `CREDITS.RenderCredits(...)` inside `CGame::RollCredits()`.

Wave1091 static read-back (`credits-renderer-review-wave1091`, `wave1091-readback-verified`) saved comment/tag normalization for the credits renderer path without renames, signature changes, function-boundary changes, executable-byte changes, BEA launch, or installed-game/runtime-file mutation. The pass ties `0x00518bf0 CCredits__BuildDefaultEntries` to startup thunk `0x00518be0` and global table `DAT_00896ca8`, and ties `0x0051a030 CCredits__RenderCredits` to call site `0x00472801` in `0x004726b0 CGame__RollCredits` plus call site `0x0051a92b` in `0x0051a8b0 CFEPCredits__Render`. Render evidence includes `CDXFont__DrawTextDynamic`, and frontend transition context includes `0x0051a970 CFEPCredits__TransitionNotification`, CFEPCredits vtable `0x005db880`, and `CMusic__PlaySelection`. Progress anchors: `6410/6410 = 100.00%`, `1545/1560 = 99.04%`, `812/1408 = 57.67%`, and `500/500 = 100.00%`. Verified backup: `G:\GhidraBackups\BEA_20260604-143442_post_wave1091_credits_renderer_review_verified`. Runtime credits rendering, concrete `CCredits` / `CFEPCredits` layout recovery, exact source-body identity, BEA patching, gameplay outcomes, and rebuild parity remain separate proof.

## Confirmed Mapping

| Address | Function | Role | Notes |
|---------|----------|------|-------|
| `0x00518bf0` | `CCredits__BuildDefaultEntries` | credits table builder | Initializes the hard-coded global credits table (`DAT_00896ca8..DAT_0089754c`) with mixed localized-heading IDs and direct string pointers. |
| `0x0051a010` | `CCredits__WriteEntry_String` | entry writer helper | Small helper used by `CCredits__BuildDefaultEntries` for rows driven by direct string pointers (`{section,text_ptr,0,style}`). |
| `0x00519ff0` | `CCredits__WriteEntry_TextId` | entry writer helper | Small helper used by `CCredits__BuildDefaultEntries` for rows driven by numeric text IDs (`{section,text_id,0,style}`). |
| `0x0051a030` | `CCredits__RenderCredits` | credits renderer | Per-frame credits draw/update helper. Returns `true` while credits should continue, `false` when complete. Uses elapsed-time + alpha parameter. |

## Callers

- `0x00472801` inside `CGame__RollCredits` (`0x004726b0`)
- `0x0051a92b` inside `CFEPCredits__Render` (`0x0051a8b0`)
- `0x00622878` points at startup thunk `LAB_00518be0` (`JMP 0x00518bf0`) for credits-table initialization

## Notes

- Crash-recovery rollback observed once in this wave, but final state was successfully restored using strict single-write/read-back with explicit UI saves between writes.
- Keep the same lock-step discipline for future credits helper mutations.
