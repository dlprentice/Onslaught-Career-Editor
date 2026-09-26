# CGame__SetSlot

Status: active function note
Last updated: 2026-09-26 (RE audit: the bit is set only for val == 1; the error path is LOG.AddMessage)
Summary: CGame::SetSlot sets or clears one of 256 runtime slot bits at CGame+0x308; the script SetSlot and SetSlotSave natives reach it, and a won level carries the bits into the career.
Evidence: MEASURED — pristine instructions; SOURCE — `game.cpp:853-876`.
Specimen: pristine `BEA.exe.original.backup`, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: `references/Onslaught/game.cpp` (`CGame::SetSlot`, lines 853-876) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x0046d3a0`
>
> Source: `references/Onslaught/game.cpp` (`CGame::SetSlot(int, BOOL)`)

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes
- **Verified vs Source:** Yes. The out-of-range path pushes the slot, the format `0x0062434c` ("Error: Outside slot range (%d) in call to SetSlot") and the log object `0x0066f580`, then calls `0x00441740` (`0x0046d3f6-0x0046d401`), which is how `LOG.AddMessage` compiles elsewhere, so it matches `game.cpp:857`.

Wave803 (`game-slot-helpers-wave803`, `wave803-readback-verified`) saved the Ghidra function comment/tags for `0x0046d3a0 CGame__SetSlot` without renaming or changing its signature. Post-Wave803 queue head moved to `0x00472e50 CVBufTexture__DrawSpriteWithDefaultTextureFallback`.

The exact native registry binds `SetSlot` at index 123, record `0x0064ece0`,
to handler `0x005338d0`. Source-backed helpers connect that command to the
`CGame+0x308` slot state and `CCareer__SetSlot` persistence path. Runtime
persistence and exact `CGame` layout remain separate proof.

## Purpose
Set/clear a runtime slot bit in `CGame::mSlots` (slot ids `0..255`).

Mission scripts use this via `SetSlot(slot,val)` and `SetSlotSave(slot,val)`.

## Signature
```c
// Source:
void CGame::SetSlot(int num, BOOL val);

// BEA.exe (Ghidra):
void CGame__SetSlot(void * this, int slot, int val);
```

## Behavior (Retail / Steam)
- Range check: `0 <= slot < 256` (prints an error on failure).
- Compute `index = slot >> 5`, `mask = 1 << (slot & 31)`.
- If `val == 1`: `mSlots[index] |= mask` (`cmp [esp+0xc],1; jne` at `0x0046d3c5`,
  as `game.cpp:869` `if (val == TRUE)`).
- Else, including 2 or −1: `mSlots[index] &= ~mask`.
- `CCareer::SetSlot` has the same `== 1` test (`0x00421505`). Both script callers
  pass `getter(arg) & 0xff` (`0x005338e1`, `0x00533912`), and that getter yields
  0 or 1 for `CInt` and `CBool`, so the difference never shows for scripts.

Runtime slot array is at `this + 0x308` (`mSlots[32]`).

## Persistence Chain
1. Mission scripts mutate `GAME.mSlots` through `CGame__SetSlot`.
2. End-of-level: `CGame__FillOutEndLevelData` copies `END_LEVEL_DATA.mSlots = GAME.mSlots`.
3. On **LevelWon**: `CCareer__Update` overwrites persistent `CCareer.mSlots` from `END_LEVEL_DATA.mSlots`.

`SetSlotSave` additionally calls `CCareer__SetSlot` (`0x004214e0`) to persist immediately into the save.

## Related
- `CGame__GetSlot` (`0x0046d410`)
- `CCareer__SetSlot` (`0x004214e0`) - persistent slots stored in `.bes` at file offset `0x240A` (true dword view)
- MissionScript handlers: `IScript__SetSlot` (`0x005338d0`), `IScript__SetSlotSave` (`0x00533900`)
