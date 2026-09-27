# `CPCMemoryCard` released PC save-backend semantics

Status: active, bounded semantic recovery
Last updated: 2026-09-27
Evidence: MEASURED — September 27 complete slot writer executed with intercepted CRT/name boundaries;
September 19 selected PC read/name/card-info bodies executed with
intercepted file/UI services; inherited August evidence — complete retail
bodies, retained interfaces and eleven normalized-identical PC demo twins; UNKNOWN —
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

## September 27 slot-write result recheck

The complete pristine body `[0x00514f80,0x00515073)`, 243 bytes, SHA-256
`a98c74c83c7549d419e03b0b47680a10e4b082e13fdfc0632e16e5bf127e12eb`,
was executed unchanged in an isolated ELF32. Its payload is the unchanged real
10,004-byte gold fixture in read-only pages. Name conversion and CRT entry
points are intercepted; no save or game file is written.

| Supplied boundary results | Original adapter result | Observed calls |
| --- | --- | --- |
| Open succeeds; `fwrite=1`, `fclose=0` | `0` | Open, write, close. |
| Open succeeds; `fwrite=1`, `fclose=-1` | `0` | Open, write, close; close error discarded. |
| Open succeeds; `fwrite=0` | `1` | Open, write; no close. |
| Open succeeds; adversarial `fwrite=2` | `1` | Open, write; no close. |
| Open returns NULL | `1` | Open only. |

The equality check is at `0x00515046`. After the close call at `0x0051504c`,
`0x00515054` clears EAX unconditionally. A separate derivative of the private
ELF replaces only that two-byte clear with NOPs: the close-error case then
returns `0xffffffff`. The pristine file and all five primary executions stay
unchanged. The result of two is an adverse equality control, not an expected
CRT return for a one-item request.

All cases check the constructed path, exact data pointer/size/count, event
sequence, RET 20 and callee-saved registers. The syscall filter refuses the
tested forbidden call. Independent review reconstructs every retained output.
Driver and receipt: `local-data/test-runs/save-startup-20260919/slot_write_control.py`
and `slot-write-run-j8gvjdkw/slot.json` (SHA-256
`9e0be7ee9452416dff323feb215e46c9c65a6d70a13915b9dd97ded750ac9cb8`).
This verifies the adapter's transport and result handling, not serialization,
actual CRT stream lifetime, Windows faults or durable persistence.

Fresh static caller inspection distinguishes three consequences:

- Explicit save at `0x0046505d` checks this result. Zero takes the success
  branch at `0x00465062..0x00465070`, constructs the source-correlated saved
  message and sets the autosave/keyboard state. A supplied close error is
  therefore invisible to that branch. The full dialog/caller was not executed.
- Main-menu call `0x004628d8` ignores the result and proceeds to the default-
  options writer at `0x004628df`.
- Pause-menu call `0x004d07af` also ignores it and proceeds to default-options
  publication at `0x004d07b6`. These last two are unchecked continuations, not
  newly demonstrated save-success dialogs.

These retail consumers use CRT streams. The pinned source's older PC career
writer uses `CMEMBUFFER`; that source path must not be substituted for the
retail serializers and their callers. The separately reviewed CDXMemBuffer
Write/Close failure behavior is not evidence for this slot adapter.

## September 19 independent recheck

The [menu-load controls](save-options-static-review-2026-05-26.md#original-menu-load-and-next-startup-composition)
execute the unchanged PC `GetCardInfo`, `ReadSave` and `FromWCHAR` bodies as
part of the original menu transaction. Twenty cases compare complete selected
state and read/publication buffers with intercepted file, allocation and UI
dependencies. They confirm the read path ignores card/slot, narrows wide names
to low bytes, returns through the failure branch on incomplete reads, and makes
two close calls on full reads. Supplied close errors do not change that branch.
The original card-info stub reports present/formatted throughout.

The write/delete/enumeration unit, demo twins and source ownership claims below
were **not rerun or comprehensively rechecked** in this follow-up. Their August
receipts are inherited evidence. Name constraints upstream of these readers,
real file effects and actual CRT stream-lifetime consequences remain open.

## August result and ownership correction — inherited

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
