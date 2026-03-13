# Credits.cpp - Function Analysis

## Overview

Retail binary includes a credits renderer class/function path referenced by game outro flow and frontend credits-page code.
Source clue: `references/Onslaught/game.cpp` includes `Credits.h` and calls `CREDITS.RenderCredits(...)` inside `CGame::RollCredits()`.

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
