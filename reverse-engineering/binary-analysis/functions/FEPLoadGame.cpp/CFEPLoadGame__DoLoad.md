# CFEPLoadGame__DoLoad

Status: active bounded retail contract; complete UI/filesystem acceptance pending
Last updated: 2026-09-19
Summary: original menu-load composition preserves live volumes and conditionally forwards the entire read buffer to default-options persistence.
Source File: `references/Onslaught/FEPLoadGame.cpp` (`StartLoad`, partial analogue); Binary: pristine `BEA.exe.original.backup`.
Evidence: MEASURED — selected pristine instructions and 20 isolated original-code controls; UI and filesystem services intercepted.
Address: `0x00461e20`, body `[00461e20,004620bc)`.
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

## Purpose

Executes the selected career's read/load transaction. Its local admission checks
are a complete requested read and the career loader's version check, not general
validation of every field or the physical file's complete length.

## Signature
```c
void CFEPLoadGame__DoLoad(void * this);
```

## Independently rechecked behavior

- Requires a selected save slot at `this+0x40`; if `-1`, calls the compiled
  no-op trace at `0040c640` and returns without allocation or file operations.
- Copies the wide name at `this+0x44` into save/keyboard globals before reading.
  The original PC card-info body reports present/formatted regardless of index.
- Allocates a temp buffer of `size = CCareer__GetSaveSize()`.
- Reads the save file into the buffer via:
  - `PCPlatform__ReadSaveFile(device=DAT_008a9694, slot=this+0x40, save_name=this+0x44, out_buf, size, &bytesRead)`
  - Return convention: `0` indicates a full read, non-zero indicates failure.
- Loads career state into the global `CAREER` via:
  - `CCareer__Load(&CAREER, out_buf, flag=1)`
  - Return convention: non-zero indicates success.
- On successful load:
  - Transitions the frontend to the next page/state (success path).
  - Sets `DAT_008a9584 = 1` (frontend state flag used by save/load flows).
  - After the page-transition call, tests only the **low byte** at `0082b5b0`.
    If zero, calls `CFEPOptions__WriteDefaultOptionsFile(out_buf, size)` with
    the original read buffer. A nonzero higher byte alone does not suppress it.
- Frees the temp buffer before returning.

### Live volumes and the next startup are distinct

The selected pristine retail body calls:

- `CCareer__Load(&DAT_00660620, source, 1)` (flag=1)

Inside `CCareer__Load` (`0x00421200`), a nonzero low flag byte restores the pre-load values of:

- `this+0x248C` (Sound volume float)
- `this+0x2490` (Music volume float)

It also skips the binding rows and options-tail reader. The isolated menu
controls compare the complete selected career region and binding table: career
data loads, packed counter top bytes normalize, previous volumes survive, and
bindings remain unchanged. Latest-world selection is recorded but intercepted.

### defaultoptions.bea Side Effect

On successful load, `CFEPLoadGame__DoLoad` may call:

- `CFEPOptions__WriteDefaultOptionsFile(source, size)`

The writer receives the original bytes, including the file's volumes, bindings
and tail. Open failure, a short-write result, or a close-error result does not
turn this caller's already-taken success path into a failure. This proves an
attempted payload and ignored failure results, not durable publication.

The successful menu case's captured payload was fed unchanged into the isolated
original WinMain experiment. Menu-live volumes stayed at the authored
`0.25/0.75`; the next startup loaded the real fixture's `0.6/0.4` volume bits,
copied its bindings and sensitivity, then reset campaign progress. The storage
handoff is explicitly supplied; there was no real file write or desktop launch.

The private controls and receipts live in
`local-data/test-runs/save-startup-20260919/`. Exact commands and limitations are
in [VALIDATION.md](../../../../VALIDATION.md#original-menu-load-and-next-startup--september-19).

### Read-path name conversion

The composed original PC reader builds `savegames\\<name>.bes`, taking only the
low byte of each wide code unit. `GoldA` and `Gold\u0141` therefore produce the
same intercepted path; a nonzero wide character whose low byte is zero truncates
the converted name. These are authored boundary inputs, not proof that the real
keyboard UI can generate those names. Device and slot changes leave this path
unchanged. A complete read makes two calls to `fclose` on the same supplied
stream; short reads make one. No actual CRT double-close consequence was tested.

## File Format Reference

| Offset | Size | Content |
|--------|------|---------|
| 0x0000 | 2 | Version word (0x4BD1) |
| 0x0002 | 4 | `new_goodie_count` (CCareer +0x0000) |
| 0x0006 | 6400 | CCareerNode[100] |
| 0x1906 | 1600 | CCareerNodeLink[200] |
| 0x1F46 | 1200 | Goodies[300] |
| 0x23F6 | 20 | Kill counters[5] |
| 0x240A | 128 | Tech slots[32] |
| ... | ... | Settings and metadata |

## Error Handling

Known failure behaviors:
- If the device/card is absent or unformatted, it routes through the frontend error/whinge path and returns. Wave375 now saves that shared storage-message helper as [`CFEPSaveGame__RemovedMUWhinge`](../FEPSaveGame.cpp/CFEPSaveGame__RemovedMUWhinge.md) at `0x00464b30`.
- If `PCPlatform__ReadSaveFile` fails, the original caller requests message
  `0x41`, calls `SetPage(0,0)`, and frees the buffer under the intercepted UI.
- If `CCareer__Load` rejects the version, it requests message `0x42`, calls
  `SetPage(0,0)`, and frees the buffer. Neither case invokes the options writer.
- Accepted loads request message `0x38` and call `SetPage` with the success
  page/time globals. Rendered messages and actual page callback behavior are
  outside these controls. The unavailable-card branch is unexecuted because
  the original PC card-info body always reports present/formatted.

## Partial source comparison

At `references/Onslaught` commit
`5352a81cdb838b145a57f7febc5d9fc4b0129ebb`, the corresponding body is named
`CFEPLoadGame::StartLoad` in `FEPLoadGame.cpp:128`. It supplies the name-copy,
read, career-load and cleanup analogue. Its success handling uses a message-box
dismiss callback and lacks this retail default-options write. It is therefore
a partial source analogue, not an exact source match for the shipped PC body.

## Inherited post-load cheat notes — not rechecked here

After loading, the save game name is available for cheat code checking. Functions like `IsCheatActive()` use `strstr()` to check if the loaded save name contains any cheat codes (MALLOY, TURKEY, V3R5IOF, Maladim, Aurore, latête). (Source/internal strings differ: V3R5ION/B4K42.)

## Cross-References

### Calls
- File I/O functions (fopen, fread, fclose)
- Career data parsing functions

### Called By
- Frontend menu system when user confirms load selection

### Related
- `CCareer::Load` - lower-level career loading function
- `IsCheatActive` - uses save name after load
- `CFEPSaveGame__RemovedMUWhinge` - shared storage-message dialog helper used by selected load/save/keyboard paths

## Notes

- Migrated from ghidra-analysis.md (Dec 2025)
- Wave375 corrected the adjacent load-game vtable init/button/process/render names and signatures from saved Ghidra read-back; runtime save/load behavior still requires separate proof.
