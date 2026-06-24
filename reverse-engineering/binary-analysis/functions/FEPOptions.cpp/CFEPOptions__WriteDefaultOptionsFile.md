# CFEPOptions__WriteDefaultOptionsFile

> Address: 0x0051f680 | Source: `references/Onslaught/FEPOptions.cpp`

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes
- **Verified vs Source:** Behavior-level verified (2026-02-23) from decompile + callsite/xref checks.

## Purpose
Low-level helper that writes a serialized options/career buffer to `defaultoptions.bea`.

## Signature
```c
// Binary calling convention: __cdecl, returns void, pops 8 bytes (2 args)
void CFEPOptions__WriteDefaultOptionsFile(void * data, int size);
```

## Verified Behavior (BEA.exe)

1. Opens `defaultoptions.bea` for write:
   - `fopen("defaultoptions.bea", "wb")`
2. If open succeeds:
   - `fwrite(data, size, 1, file)`
   - `fclose(file)`
3. If open fails:
   - emits console message `"Couldn't write defaultoptions"` via `CConsole__Printf`.

No internal allocation or serialization happens here; caller owns `data` and `size`.

## Call Chains and Side Effects (Verified)

### 1) Load-game path (`CFEPLoadGame__DoLoad`, 0x00461e20)
- Reads selected `.bes` into `out_buf` using `PCPlatform__ReadSaveFile`.
- Calls `CCareer__Load(&CAREER, out_buf, 1)`.
- On successful load, if `DAT_0082b5b0 == 0`, calls:
  - `CFEPOptions__WriteDefaultOptionsFile(out_buf, size)`.

**Side effect:** the currently loaded save buffer can overwrite `defaultoptions.bea` (global-options snapshot behavior).

### 2) Async-save tick path (`Platform__AsyncSaveCareer`, 0x004d2580)
- Calls platform tick helper.
- If `DAT_0082b5b0 != 0`, clears it and triggers `CD3DApplication__Reset3DEnvironment(1,1)`.
- If previous flag value was `2`, allocates a temp buffer, serializes via `CCareer__Save`, then calls:
  - `CFEPOptions__WriteDefaultOptionsFile(dest, size)`, then frees.

**Side effect:** asynchronous runtime save-state transitions can update `defaultoptions.bea`.

### 3) PauseMenu-driven path (`FUN_004d06e0`)
- Serializes `CAREER` with `CCareer__Save`.
- Optionally writes selected save slot via `PCPlatform__WriteSaveFile`.
- Also calls:
  - `CFEPOptions__WriteDefaultOptionsFile(buf, size)`.

**Side effect:** this path can update both a slot save and `defaultoptions.bea` in the same flow.

### 4) Main-menu process path (`CFEPMain__Process`, 0x00462640)
- Additional direct caller xref at `0x004628df` is now recovered inside `CFEPMain__Process`.
- Same branch also calls `CCareer__Save` at `0x00462893` and conditionally `PCPlatform__WriteSaveFile`, confirming a full save+defaultoptions chain in main-menu process logic.

## Notes
- This function is central to why `defaultoptions.bea` behaves as a global settings sink, even when actions begin from save-load/save-menu flows.
- Related docs:
  - `../Career.cpp/CCareer__Save.md`
  - `../FEPLoadGame.cpp/CFEPLoadGame__DoLoad.md`
  - `_index.md` (FEPOptions.cpp)
