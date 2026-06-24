# CGame__GetSlot

> Address: `0x0046d410`
>
> Source: `references/Onslaught/game.cpp` (`CGame::GetSlot(int)`)

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes
- **Verified vs Source:** Yes (retail uses console-print instead of `LOG.AddMessage`)

Wave803 (`game-slot-helpers-wave803`, `wave803-readback-verified`) saved the Ghidra function comment/tags for `0x0046d410 CGame__GetSlot` without renaming or changing its signature. Post-Wave803 queue head moved to `0x00472e50 CVBufTexture__DrawSpriteWithDefaultTextureFallback`.

2026-06-08 MissionScript Slot Command-Effect static proof: `missionscript-slot-command-effect-static-proof.md` and `missionscript-slot-command-effect.v1.json` bind this helper to descriptor slot `GetSlot` at `0x0064ed10`, `IScript__GetSlotBitValue`, `CGame+0x308`, `CCareer__SetSlot` context through the sibling `SetSlotSave` command, true-view save slot base `0x240A`, `6 slot-using level rows`, `18 detailed slot call rows`, `6 GetSlot`, `8 SetSlot`, and `4 SetSlotSave`. This is static bridge accounting only, not runtime command effects, runtime save behavior, runtime slot persistence, live loose-MSL loading, exact `CGame` layout, patch, Godot, rebuild, or no-noticeable-difference proof.

## Purpose
Read a runtime slot bit in `CGame::mSlots` (slot ids `0..255`).

Mission scripts use this via `GetSlot(slot)`.

## Signature
```c
// Source:
BOOL CGame::GetSlot(int num);

// BEA.exe (Ghidra):
bool CGame__GetSlot(void * this, int slot);
```

## Behavior (Retail / Steam)
- Range check: `0 <= slot < 256` (prints an error and returns `false` on failure).
- Compute `index = slot >> 5`, `mask = 1 << (slot & 31)`.
- Return `((mSlots[index] & mask) != 0)`.

Runtime slot array is at `this + 0x308` (`mSlots[32]`).

## Related
- `CGame__SetSlot` (`0x0046d3a0`)
- MissionScript handler: `IScript__GetSlotBitValue` (`0x005339a0`)
