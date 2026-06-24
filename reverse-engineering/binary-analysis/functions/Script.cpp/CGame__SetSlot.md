# CGame__SetSlot

> Address: `0x0046d3a0`
>
> Source: `references/Onslaught/game.cpp` (`CGame::SetSlot(int, BOOL)`)

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes
- **Verified vs Source:** Yes (retail uses console-print instead of `LOG.AddMessage`)

Wave803 (`game-slot-helpers-wave803`, `wave803-readback-verified`) saved the Ghidra function comment/tags for `0x0046d3a0 CGame__SetSlot` without renaming or changing its signature. Post-Wave803 queue head moved to `0x00472e50 CVBufTexture__DrawSpriteWithDefaultTextureFallback`.

2026-06-08 MissionScript Slot Command-Effect static proof: `missionscript-slot-command-effect-static-proof.md` and `missionscript-slot-command-effect.v1.json` bind this helper to descriptor slot `SetSlot` at `0x0064ecd0`, `IScript__SetSlot`, `IScript__SetSlotSave`, `CGame+0x308`, `CCareer__SetSlot`, true-view save slot base `0x240A`, `6 slot-using level rows`, `18 detailed slot call rows`, `6 GetSlot`, `8 SetSlot`, and `4 SetSlotSave`. This is static bridge accounting only, not runtime command effects, runtime save behavior, runtime slot persistence, live loose-MSL loading, exact `CGame` layout, patch, Godot, rebuild, or no-noticeable-difference proof.

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
- If `val != 0`: `mSlots[index] |= mask`.
- Else: `mSlots[index] &= ~mask`.

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
