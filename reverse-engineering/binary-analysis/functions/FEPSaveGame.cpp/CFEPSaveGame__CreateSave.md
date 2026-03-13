# CFEPSaveGame__CreateSave

> Address: 0x00464c50 | Source: `references/Onslaught/FEPSaveGame.cpp` (`CFEPSaveGame::CreateSave`)

## Status

- **Named in Ghidra:** Yes
- **Signature Set:** Yes
- **Verified vs Source:** Partial (logic matches; return/error codes still being mapped)

## Signature

```c
void CFEPSaveGame__CreateSave(void * this);
```

## Purpose

Frontend Save Game menu handler that creates/overwrites a save slot (when allowed), serializes `CAREER` into a temporary buffer, and writes it to disk via `PCPlatform__WriteSaveFile`.

## High-Confidence Behavior (Binary Evidence)

- Queries card/device state and save-file counts via:
  - `FUN_00514960(...)` (device/card info)
  - `EnumerateSaveFiles_1(...)` (count saves)
- Computes required save size via `CCareer__GetSaveSize()` and performs a space/limit check (notably `numsaves > 4095`).
- If space is insufficient and overwrite is not allowed, shows a delete/overwrite prompt path.
- Locates an existing save with the same name via `EnumerateSaveFiles_2(...)` + string compare, recording the existing slot index.
- Selects a slot / resolves overwrite rules via `EnumerateSaveFiles_Main(device, save_name, &slot, allowed_overwrite)`.
- On success (`res == 0`):
  1. `buf = OID__AllocObject(size, ...)`
  2. `CCareer__SaveWithFlag(&CAREER, buf)` (sets `mCareerInProgress` before dumping)
  3. `PCPlatform__WriteSaveFile(device, slot, save_name, buf, size)`
  4. Shows success/failure UI message boxes and updates frontend state.
  5. Frees `buf`.

## Notes / Open Questions

- The save/create/write result codes appear to mirror the source build’s `MCE_*` enum (`MCE_SUCCESS`, `MCE_FILEEXISTS`, `MCE_CARDFULL`, `MCE_TOO_MANY_SAVES`, `MCE_NOFILE`, etc.), but the exact numeric mapping in the PC retail build is not fully confirmed yet.
- This PC port uses `savegames\\<name>.bes` (see `PCPlatform__WriteSaveFile`), rather than console `MEMORYCARD.*` APIs.

