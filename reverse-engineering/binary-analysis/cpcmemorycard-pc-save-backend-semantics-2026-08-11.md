# `CPCMemoryCard` released PC save-backend semantics

Status: active, bounded semantic recovery
Last updated: 2026-08-11
Evidence: MEASURED — complete pristine retail bodies and instruction streams,
retained `CMemoryCard`/`CPCMemoryCard` interfaces, typed frontend callers, exact
path/mode literals, and eleven normalized-identical PC demo twins; UNKNOWN —
fault-injected filesystem runtime behavior, upstream filename constraints,
console adapter parity, and rebuild-wide persistence parity.
Verdict: the released PC build does implement the console-shaped memory-card
interface. It projects one permanently present pseudo-card over ordinary
`savegames\\<name>.bes` files. The retained PC header contains earlier stubs,
not the shipped bodies.

Specimen: pristine PC retail `BEA.exe`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`;
PC demo `BEA.exe`, SHA-256
`d8637dd755b21c720c0cb8f71923f94d2a04a184d90f5343c2e868ce8606e5c2`.
The interface authorities are `references/Onslaught/MemoryCard.h` (2,521
bytes, SHA-256
`80c489b2ca21afe735fc87baa14a893b64bbe0b6da34664683cee047b4aede50`)
and `references/Onslaught/PCMemoryCard.h` (2,039 bytes, SHA-256
`fef1349d7b239e821d4d7539e60c97539f47a30f54c15b8793eaf524a8cc4384`).
The retained `PCMemoryCard.cpp` is only a resource-builder hook (669 bytes,
SHA-256
`c5558395e79d6121d83e148f1ddb9f8e7723372b5ffc3d6bcd67e158d937efc9`).

## Result and ownership correction

The eleven-function unit covers 2,079 retail bytes and 711 decoded
instructions. Every body has an independently mapped PC demo twin with zero
normalized instruction differences; 214 raw bytes differ only in encoded
addresses or displacements. The machine-readable result is
[`cpcmemorycard-pc-save-backend-semantics-2026-08-11.tsv`](cpcmemorycard-pc-save-backend-semantics-2026-08-11.tsv),
4,167 bytes, SHA-256
`532867359fa4a77e2305e62db8cba42b6d91481ac3fa7a9b596415691a7dd2f0`.

Several current Ghidra labels describe effects but miss the owning class.
Contiguous body order, exact stack signatures, and typed calls reproduce the
`CPCMemoryCard` interface sequence:

| Retail VA | Released interface method |
| --- | --- |
| `0x00514950` | `GetNumCards` |
| `0x00514960` | `GetCardInfo` |
| `0x005149a0` | card-name provider (`GetCardName`; an identical folded `GetCardOrPreviousCardName2` remains possible) |
| `0x005149c0` | `GetNumSaves` |
| `0x00514a80` | `GetSaveName` |
| `0x00514be0` | `CreateSave` |
| `0x00514ec0` | `DeleteSave` |
| `0x00514f80` | `WriteSave` |
| `0x00515080` | `ReadSave` |
| `0x00515190` | `GetSaveSize` |
| `0x005151a0` | `MakeHumanReadableSize` |

The strongest correction is `0x00515190`: both callers pass a career data size
and an output-size pointer, and the body copies the former to the latter. The
current label `PCPlatform__CopyStorageDeviceId` is therefore disproven; this is
`CPCMemoryCard::GetSaveSize`. Likewise, the three `EnumerateSaveFiles_*` labels
are the concrete `GetNumSaves`, `GetSaveName`, and `CreateSave` methods rather
than an anonymous utility family.

## One pseudo-card, not a disk-capacity service

`GetNumCards` reports exactly one card. `GetCardInfo` ignores its card index,
reports present and formatted as true, and supplies `0x7fffffff` for requested
free and total sizes. The display-name body copies localization string ID
`0x28`. `GetSaveSize` adds no filesystem or card overhead: it copies the data
size unchanged. `MakeHumanReadableSize` returns an empty wide string.

These values deliberately satisfy a console-shaped frontend. They do not query
Windows disk capacity. Consequently, the PC frontend's pre-write capacity check
cannot discover real free-space exhaustion through this adapter; a later file
operation can only return its generic failure code.

This differs from the retained `PCMemoryCard.h` stubs, which report zero cards,
absent/unformatted state, zero capacity, zero saves, and successful no-op I/O.
The interface names are useful source evidence, but the pristine executable is
the body authority.

## Filename-backed slot model

The exact pristine literals are:

- VA `0x0063df7c`: `savegames\\*.bes`;
- VA `0x0063df8c`: `.bes`;
- VA `0x0063df94`: `savegames\\`;
- VA `0x00629038`: `rb`;
- VA `0x0063316c`: `wb`.

All enumeration uses the Win32 find wrappers, ignores entries whose attributes
intersect `0x16` (`HIDDEN | SYSTEM | DIRECTORY`), and otherwise preserves raw
filesystem enumeration order. `GetNumSaves` counts those entries.
`GetSaveName` selects the zero-based visible entry, removes the final four
`.bes` bytes, converts the byte filename to wide text, and returns `0` on
success or `1` when the index cannot be reached.

`CreateSave` ensures the directory exists, constructs
`savegames\\<converted-name>.bes`, and initializes the output index to `-1`.
If overwrite is disallowed and that path opens for read, it returns
`MCE_FILEEXISTS` (`6`). Otherwise it opens the path as `wb`, immediately
creating or truncating it, closes it, then re-enumerates the directory and
finds the new case-insensitive name to recover its current slot index. It
returns success (`0`) only when that match is found; other create/enumeration
failures collapse to `MCE_FAILURE` (`1`). An enumeration failure can therefore
leave an empty or truncated file for the caller's cleanup path.

The `card` and `slot` arguments to `DeleteSave`, `WriteSave`, and `ReadSave`
are unused. The converted name is the actual identity:

- delete calls `DeleteFileA` and returns `0` on success, `1` on failure;
- write opens `wb`, requires `fwrite(data, size, 1) == 1`, and returns `0` only
  for that complete item write;
- read opens `rb`, requests exactly `size` bytes, reports the observed byte
  count after a read, and returns `0` only when it equals the request.

No explicit filename sanitization or bounded concatenation appears in this
unit. That proves only the local absence; the frontend keyboard's accepted
character set remains a separate upstream boundary. The shared global find
handle/metadata buffer also makes the enumerators non-reentrant.

## Two released stream-lifetime defects

The instruction stream makes two unusual edges exact rather than decompiler
artifacts.

`WriteSave` closes the stream only after `fwrite(..., size, 1)` returns one.
If the file opens but the item write returns anything else, control jumps
directly to failure without `fclose`. That leaks the open CRT stream on the
short/error edge.

`ReadSave` has the opposite error. It calls `fclose(file)` immediately after
`fread`. When the byte count is short, it reports the count and returns failure.
When the count exactly matches the request, it stores the count and calls
`fclose(file)` a second time before returning success. An open failure returns
`1` without initializing `out_read`. The independently linked demo contains
the same normalized instruction paths, so these are shared production-PC
behaviors rather than a retail relocation anomaly.

## Boundary

This closes the static semantics and source ownership of the PC card/file
adapter. It does not justify exercising disk-full, short-write, double-close,
path-length, or removal behavior against a real career. Runtime falsification
must use a copied installation and disposable save directory. Xbox and PS2
memory-card layouts, certification errors, and asynchronous behavior remain
separate implementations.
