# CText__Init

Status: independently rechecked static and bounded original-parser contract
Last updated: 2026-09-20
Summary: language-file selection, parsing and loaded-state behavior; an open failure reaches a fatal boundary and read counts are not validated here.
Source File: `text.cpp` is absent from the pinned partial-source snapshot | Binary: pristine `BEA.exe.original.backup`.
Evidence: MEASURED — pristine-body inspection and 19 original parser/cached-read/active-copy cases with admitted files and owned derivatives.
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Address: `0x004f21f0`

## Admission and file selection

The original body uses ECX for the header, takes one language argument and
returns with `RET 4`. It has no meaningful success return. Nonzero header
`+14` or `+4` skips the operation without changing the language.
Otherwise `004f222b` stores the full argument at header `+1c` before
opening or validating any file.

The jump table maps 0/1/2/3/4 to English/French/German/Spanish/Italian.
Out-of-range unsigned values log a diagnostic and select the English filename;
the stored language argument is not corrected. Nonzero global `0083d990`
instead chooses the American file before the switch, irrespective of the
language argument. Its writer/selection policy remains a separate question.

The actual format/literal strings are `data\LANGUAGE\%s.DAT` and
`data\LANGUAGE\american.DAT`. Preserved Linux files are under
`local-lab/safe-copy-bea-pristine/data/language/` with lowercase names;
the obsolete `game/data/language/` route is not the owner on this host.

## Failure and state boundaries

- The Open call at `004f22cb` supplies `(path,0x11,1,0)`. A zero
  result reaches `0042c750` at `004f22e3` **before** the apparent
  diagnostic/Close/destructor tail. Fresh inspection follows that fatal helper
  to `0042cfa0` and the confirmed `ExitProcess(1)` import at
  `0042d064`. Replacing the fatal helper with a returning no-op would
  manufacture a cleanup continuation.
- After Open succeeds, GetFileSize supplies an allocation size. The body checks
  neither allocation failure nor minimum header size.
- The Read call at `004f2350` returns an actual copied count, but Init
  ignores EAX, records the requested file size at `+18`, and immediately
  parses the destination buffer.
- Unknown tagged versions call the ordinary diagnostic at `004f23c3`.
  If that call and Close return, the branch sets `+14=1` at
  `004f2467` while leaving `+0,+8,+c,+10` at their prior values.
  Thus the loaded flag alone does not establish format recognition.
- The body installs/restores an exception frame using `FS:[0]`. Isolated
  normal execution must supply and check that storage; a guarded fault would
  not prove Windows exception dispatch or cleanup.

The controls below execute the parser, normal exception-frame traffic and
cached file helpers. Open failure stops at the fatal-call boundary; its shutdown
chain is static evidence. Actual filesystem failure, allocation failure,
Windows exception dispatch and localized error presentation remain untested.

## Rechecked parsing structure

All offsets below are hexadecimal. Parsing performs no computed table/pool
bounds checks in this body.

| File branch | Header/pointer construction |
| --- | --- |
| First DWORD is not `0xffffffbb` | Treat it as legacy count; set version `+0=0`, count `+10` and text pointer `+8=buffer+4+4*count`. |
| Tagged, masked version 1 | Copy version/count; text pointer becomes `buffer+0xc+8*count`. |
| Tagged, masked version 2 or 3 | Copy version/count; text pointer becomes `buffer+0x10+0xc*count`. Read the intervening pool-byte count at `buffer+0xc+0xc*count`; audio pointer becomes `buffer+0x14+0xc*count+pool_bytes`. |
| Tagged high bit set | Store header `+20=1`; for versions 2/3, compute aligned extra-data pointers after the audio pool, including a `0x40*count` stride. |
| Other tagged version | Diagnostic, then the loaded-state continuation described above; no successful-format claim. |

The tagged version high bit is separately retained at `+20`; version
comparison masks it off. The ordinary Close call precedes the loaded-flag write,
and the file-object destructor follows it. Rechecked read-mode Close closes
the handle and frees/clears its buffers; the destructor itself only frees its
two buffer fields and does not close a handle.

## Preserved resource observations

On September 20, bounded first-hand reads of the six exact files established:

| File | Bytes |
| --- | ---: |
| english.dat | 279933 |
| french.dat | 300067 |
| german.dat | 308567 |
| spanish.dat | 294663 |
| italian.dat | 303027 |
| american.dat | 279819 |

All six begin with magic `0xffffffbb`, version flags 3 and count 2571.
Exact paths/hashes are in private
`local-data/test-runs/save-startup-20260919/language-file-inputs.json`.
The subsequent [19 original-parser controls](../../../../VALIDATION.md#original-language-file-parsing--september-20)
pass those exact files through this body, original file ctor/dtor, size,
cached Read and Close, then original SetLanguage/null cleanup/CopyFrom.
Open supplies an explicitly modeled final-cache object; allocator/free,
formatting and two Win32 API results are intercepted.

The controls compare the complete selected headers, allocations, guards and
source. Read-mode Close frees/clears its cache before the destructor's two
Free(NULL) calls; a supplied CloseHandle error does not change this path.
A 16-byte cached read and an empty cached read use an explicitly zero-filled
remainder: both reach loaded state. This depends on the declared allocation
fill and is not evidence of a valid resource or safe short-read handling.

Unknown-version cases reach loaded state with prior parser fields preserved;
v1/v2/legacy header derivatives establish field arithmetic only. The high-bit
v2/v3 auxiliary-data branch remains unexecuted. Header/buffer guard skips,
American override and invalid-selector English fallback also execute.
The invalid Init argument is 65535; the subsequent SetLanguage call uses
valid cache slot zero. It does not establish safe selection at index 65535.

The [lookup composition](../../../../VALIDATION.md#original-language-lookups-from-parser-output--september-20)
then imports exact active state and executes all three original lookup bodies.
Every one of the 2,571 IDs in each file is unique; selected text/audio pointers,
pool bounds, termination and offline decoding pass. Full rendered localization
and audio playback remain open.

Keep the [language-copy/save controls](../../save-options-static-review-2026-05-26.md#original-language-application-and-persistence)
separate: those earlier authored caches establish Save's language-field source,
while these controls establish real parser/copy/lookup behavior through an
explicit memory-image handoff. No single full-startup/durable-save experiment
combines all of them.
