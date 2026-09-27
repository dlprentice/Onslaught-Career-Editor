# CFEPSaveGame__CreateSave

Status: mixed — September 27 result branch rechecked; earlier entry-flow summary retains its limits
Last updated: 2026-09-27
Summary: explicit save checks the slot adapter's result, but that adapter discards a close error after a complete item write.
Source File: `references/Onslaught/FEPSaveGame.cpp` | Binary: pristine `BEA.exe.original.backup`

> Address: 0x00464c50 | Source: `references/Onslaught/FEPSaveGame.cpp` (`CFEPSaveGame::CreateSave`)

## September 27 result-branch recheck

Specimen SHA-256:
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
The full caller body `[0x00464c50,0x0046548f)` is 2,111 bytes, SHA-256
`8f1cecad1e7e0560ca9e16b717b8405995afc36927b4b259c6b3d70d87b14049`.
Fresh instructions show SaveWithFlag at `0x00465045`, slot write at
`0x0046505d`, and a result comparison against zero at `0x00465062`.
Zero takes the source-correlated success branch: text tokens `0x24/0x25`,
message construction, success transition, `0x008a9584=1` and keyboard-fresh
byte clear. Nonzero goes to error handling at `0x00465107`.

The [original adapter controls](../../cpcmemorycard-pc-save-backend-semantics-2026-08-11.md#september-27-slot-write-result-recheck)
show that `fwrite=1` followed by `fclose=-1` returns zero. Its close error is
therefore invisible to this caller's decision. A short item write returns one
and does not select that success branch. This caller conclusion is static;
the new native experiment executes only the complete slot adapter, not this
dialog, the complete menu transaction or real filesystem effects. Source
`FEPSaveGame.cpp:432–463` supports the branch correspondence, not whole-body
equivalence. The earlier summary follows.

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
