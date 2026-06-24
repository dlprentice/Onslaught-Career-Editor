# Mission Slot Usage (Loose MSL)
> Source: `game/data/MissionScripts/`
> Generated: Feb 4, 2026

This summarizes `SetSlot`, `SetSlotSave`, and `GetSlot` usage found in loose `.msl` files.

Wave803 (`game-slot-helpers-wave803`, `wave803-readback-verified`) saved Ghidra comments/tags for the underlying runtime helpers `0x0046d3a0 CGame__SetSlot` and `0x0046d410 CGame__GetSlot`. This links the loose MSL slot usage to saved static retail Ghidra metadata only; it does not prove runtime mission-script behavior.

Wave903 (`missionscript-static-review-wave903`) places the slot helpers inside the broader static-coherent MissionScript/IScript core after queue closure `6113/6113 = 100.00%`, with `ScriptCommandRegistry__InitBuiltins`, `144` command descriptor records (`0x0064ce50` through `0x0064f210`), `IScript__ScheduleEvent`, `IScript__SetSlotSave`, `IScript__LevelWon`, `CScriptObjectCode__Run`, `CScriptEventNB__PostEvent`, `CMissionScriptObjectCode__LoadAsync`, and `795` loose MSL event-name counts. Verified backup: `G:\GhidraBackups\BEA_20260526-095411_post_wave903_missionscript_static_review_verified`.

Static-to-proof planning for slot/goodie/career command bridges is `../binary-analysis/missionscript-iscript-proof-plan.md`, with the implementation-facing child contract at `../binary-analysis/missionscript-iscript-static-contract.md`; runtime slot persistence and mission outcomes remain separate proof.

MissionScript Slot Command-Effect static proof is `../binary-analysis/missionscript-slot-command-effect-static-proof.md`, backed by `../binary-analysis/missionscript-slot-command-effect.v1.json`. Status: static slot command-effect schema proof complete, not runtime proof. It maps descriptor slots `SetSlot` (`0x0064ecd0`), `GetSlot` (`0x0064ed10`), and `SetSlotSave` (`0x0064ef50`) through `IScript__SetSlot`, `IScript__SetSlotSave`, `IScript__GetSlotBitValue`, `CGame__SetSlot`, `CGame__GetSlot`, `CCareer__SetSlot`, `CGame+0x308`, and save true-view slot base `0x240A` while preserving this corpus count: `6 slot-using level rows`, `18 detailed slot call rows`, `6 GetSlot`, `8 SetSlot`, and `4 SetSlotSave`. It does not prove runtime command effects, runtime save behavior, runtime slot persistence, live loose-MSL loading, patch behavior, visual QA, Godot parity, rebuild parity, or no-noticeable-difference parity.

MissionScript Level100 Tutorial Static Event/Command Walkthrough proof planning is `../binary-analysis/missionscript-level100-tutorial-static-walkthrough-proof-plan.md`, backed by `../binary-analysis/missionscript-level100-tutorial-static-walkthrough.v1.json`. It uses the `level100` slot rows below (`SLOT_TUTORIAL_1` through `SLOT_TUTORIAL_4`, `4` `GetSlot`, and `4` `SetSlotSave`) as static corpus evidence only; runtime slot persistence and live mission behavior remain separate proof.

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
