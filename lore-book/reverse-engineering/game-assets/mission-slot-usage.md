# Mission Slot Usage (Loose MSL)
> Source: `game/data/MissionScripts/`
> Generated: Feb 4, 2026

This summarizes `SetSlot`, `SetSlotSave`, and `GetSlot` usage found in loose `.msl` files.

## Per-Level Summary

| Level | Dir | Slot Calls |
|------:|-----|-----------|
| 100 | level100 | `SLOT_TUTORIAL_1` (GetSlot/SetSlotSave), `SLOT_TUTORIAL_2` (GetSlot/SetSlotSave), `SLOT_TUTORIAL_3` (GetSlot/SetSlotSave), `SLOT_TUTORIAL_4` (GetSlot/SetSlotSave) |
| 500 | level500 | `61` (SetSlot), `62` (SetSlot) |
| 731 | level731 | `n` (SetSlot) |
| 732 | level732 | `n + 29` (SetSlot) |
| 741 | level741 | `n + 29` (GetSlot) |
| 742 | level742 | `n + 29` (GetSlot) |

## Detailed Call Sites

| Level | Dir | File | Call |
|------:|-----|------|------|
| 100 | level100 | LevelScript.msl | `GetSlot(SLOT_TUTORIAL_1)` |
| 100 | level100 | LevelScript.msl | `GetSlot(SLOT_TUTORIAL_2)` |
| 100 | level100 | LevelScript.msl | `GetSlot(SLOT_TUTORIAL_3)` |
| 100 | level100 | LevelScript.msl | `GetSlot(SLOT_TUTORIAL_4)` |
| 100 | level100 | LevelScript.msl | `SetSlotSave(SLOT_TUTORIAL_1)` |
| 100 | level100 | LevelScript.msl | `SetSlotSave(SLOT_TUTORIAL_2)` |
| 100 | level100 | LevelScript.msl | `SetSlotSave(SLOT_TUTORIAL_3)` |
| 100 | level100 | LevelScript.msl | `SetSlotSave(SLOT_TUTORIAL_4)` |
| 500 | level500 | Level500script.msl | `SetSlot(61)` |
| 500 | level500 | Level500script.msl | `SetSlot(61)` |
| 500 | level500 | Level500script.msl | `SetSlot(62)` |
| 500 | level500 | Submarine.msl | `SetSlot(62)` |
| 731 | level731 | Fenrir.msl | `SetSlot(n)` |
| 731 | level731 | Fenrir.msl | `SetSlot(n)` |
| 732 | level732 | Fenrir.msl | `SetSlot(n + 29)` |
| 732 | level732 | Fenrir.msl | `SetSlot(n + 29)` |
| 741 | level741 | Fenrir.msl | `GetSlot(n + 29)` |
| 742 | level742 | Fenrir.msl | `GetSlot(n + 29)` |