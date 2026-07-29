# CGame__GetSlot

> Address: `0x0046d410`
>
> Source: `references/Onslaught/game.cpp` (`CGame::GetSlot(int)`)

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes
- **Verified vs Source:** Yes (retail uses console-print instead of `LOG.AddMessage`)

Wave803 (`game-slot-helpers-wave803`, `wave803-readback-verified`) saved the Ghidra function comment/tags for `0x0046d410 CGame__GetSlot` without renaming or changing its signature. Post-Wave803 queue head moved to `0x00472e50 CVBufTexture__DrawSpriteWithDefaultTextureFallback`.

The exact native registry binds `GetSlot` at index 124, record `0x0064ed20`,
to handler `0x005339a0`. Source-backed helpers connect that command to the
`CGame+0x308` slot state and career persistence path. Runtime persistence and
exact `CGame` layout remain separate proof.

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
