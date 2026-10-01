# CDXMemBuffer: retail file buffering and text I/O

Status: active specimen-bound contract; dated historical records retained below
Last updated: 2026-10-01 (bounded Read/Skip comparison; September 27 records retained)
Summary: source method identities, measured receiver fields, retail/source differences,
and bounded original-code evidence for buffered reads, line reading and failed writes. File/device
acceptance and complete save compatibility remain separate.
Source File: `references/Onslaught/DXMemBuffer.cpp` | Binary: `BEA.exe.original.backup`

## Evidence and scope

All retail addresses below refer to
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, 2,506,752 bytes,
SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
The September 27 pass independently decoded the complete twelve bodies below.
Pinned source `references/Onslaught` at
`5352a81cdb838b145a57f7febc5d9fc4b0129ebb` is an identity witness, not a claim
of equivalent code. `DXMemBuffer.cpp` SHA-256 is
`c12a95cdf2f423239d2d298846f89d14554f550cb5ec68619b1be9e418ad505a`;
`DXMemBuffer.h` is
`6f28f9cffa0217bf48d18c6845620ea687d69c6227b34f6eb8416b5176e874ee`.
`membuffer.h` selects `CMEMBUFFER = CDXMemBuffer` for `_DIRECTX`; its
`IMemBuffer` base is nonvirtual. No guessed vtable is used for these identities.

The [five-name correction](../../ghidra/README.md#re-audit-memory-buffer-identities--september-27)
replaces descriptive aliases with supported source method identities. Retail
implementation differences remain explicit. All displaced plate notes are
retained as fallible leads. The separate
[eight-interface correction](../../ghidra/README.md#re-audit-memory-buffer-abi--september-27)
now fixes six member prototypes and two direct thunk dependents. It preserves
all names, code and locals. The seven already matching method names below have
been statically rechecked here; a complete kept-name comment disposition and
the remaining prototypes are separate work.

Private evidence: `local-data/test-runs/re-audit-20260926/membuffer/` holds
complete body/consumer packets, import/export witnesses, original-code drivers
and retained input/output pairs. These files contain private retail evidence and
remain outside Git. Native experiment commands and limits are also recorded in
[VALIDATION.md](../../../VALIDATION.md#re-memory-buffer-original-code--september-27).

## Method identities and transport

| Address | Current name | Observed interface and role |
| --- | --- | --- |
| `0x00547d40` | `CDXMemBuffer__SetNextReadBufferSize` | One caller-popped DWORD; writes the shared read-size global. |
| `0x00547d70` | `CDXMemBuffer__ctor` | ECX receiver; zeros only `+04/+0c/+10/+14`, returns that receiver in EAX. |
| `0x00547d90` | `CDXMemBuffer__dtor` | ECX receiver; frees `+04/+0c`, without closing a file handle or nulling the fields. |
| `0x00547dc0` | `CDXMemBuffer__InitFromMem` | ECX, filename and memory-type stack words, `RET 8`; opens a file-backed writer, not an input-memory view. |
| `0x00547ec0` | `CDXMemBuffer__InitFromFile` | ECX and four stack words, `RET 16`; initializes a reader, fills it and applies start-skip. The PC body does not consume the source's `mungepath` argument. |
| `0x005482c0` | `CDXMemBuffer__GetFileSize` | Calls PE import `GetFileSize([ECX], NULL)` and returns its full EAX value. |
| `0x005482d0` | `CDXMemBuffer__Skip` | ECX, signed-size stack word, `RET 4`; advances through buffered/refilled data and returns the consumed count. |
| `0x00548570` | `CDXMemBuffer__Read` | ECX, destination and signed size, `RET 8`; copies through refills and returns the copied count. |
| `0x00548820` | `CDXMemBuffer__ReadString` | ECX, destination and maximum, `RET 8`; line/limit loop with the edge cases below. |
| `0x00548a70` | `CDXMemBuffer__Write` | ECX, source and signed-positive size, `RET 8`; buffers and flushes without propagating write failure. |
| `0x00548c00` | `CDXMemBuffer__Close` | ECX, no stack arguments; returns EAX 0 for null data, otherwise reaches EAX 1 after its cleanup paths. This is not a durable-write result. |
| `0x00548d30` | `CDXMemBuffer__EndOfFile` | Loads the full DWORD at `[ECX+0x24]` and returns; it does not query the file or recompute EOF. |

The promoted ABI correction adds the destructor's implicit ECX receiver,
changes Write's size from `uint` to `int` at the same stack location, and
changes InitFromMem, InitFromFile, Close and EndOfFile from `bool`/AL to
four-byte `int`/EAX results. Their full bodies and caller-side EAX tests support
that width; exact source typedef spelling is not established. Close and
EndOfFile normalize their explicit-ECX fastcall metadata to automatic-ECX
thiscall without moving the physical receiver.

The complete five-byte jumps at `0x0048ddf0` and `0x004cdb90` forward directly
to Close and the destructor respectively, without argument or result changes.
They are explicitly included because Ghidra also propagates target interfaces
into these saved thunks. The first isolated rehearsal caught this undeclared
dependency before any live application. The revised gate requires both rows,
checks the jump bytes and matching interfaces, writes only the target, and
reads back both. The adjacent `0x0048ddd0` wrapper remains outside this recheck.
Generic pointers and other saved types remain bounded, not newly certified.

## Receiver fields and initialization

Offsets in this table are hexadecimal. The names in parentheses are source
correspondences; these are measured
accesses, not a newly installed Ghidra structure.

| Offset | Retail access and source correspondence |
| --- | --- |
| `+00` | File handle (`mFile`). |
| `+04/+08` | Allocated buffer and current pointer (`mData/mPtr`). |
| `+0c/+10` | Optional check-byte buffer and current check-byte pointer (`mCRCData/mCRCDataUpTo`); `+10` is not an integer index. |
| `+14` | Source `mCRCFile` slot; constructor and writer initialization set it to zero. The rechecked retail writer does not open/write/close the source sidecar. It is not a flush counter. |
| `+18/+1c` | Cached capacity and valid/buffered byte count (`mSize/mDataSize`). |
| `+20/+24/+28` | Reading, EOF and last-block DWORDs. |
| `+2c..+12b` | 256-byte cached filename; copying 256 bytes does not guarantee NUL termination for overlong names. |
| `+12c/+130` | Logical position and allocation memory-type word. |

The constructor initializes four pointer/slot words only. Do not infer zeroed
EOF, position, filename or handle from construction alone. The destructor frees
buffers; callers needing handle closure must use the close path separately.
The constructor's current plate comment still overstates this as clearing file
and buffered-reader state; its precise replacement is prepared for a later
comment cohort. GetFileSize, Skip and Read comments were also rechecked against
their complete bodies; their refined descriptions have not yet been promoted.

Read-size global `0x00650f6c` initially contains `0x100000`. The setter stores
`0x100000` for zero; otherwise it uses 32-bit `(size + 0xfffff) & 0xfff00000`.
Addition can wrap. The source defaults to 64 KiB and retains nonzero sizes
unchanged. Writer initialization allocates 1 MiB, versus the source PC 2 MiB.
It opens with `GENERIC_WRITE`, share 0, `CREATE_ALWAYS`, attributes `0x80`.
Reader initialization opens with `GENERIC_READ`, share-read, `OPEN_EXISTING`,
attributes `0x80`; source `MB_BUFFERING=0` would add `FILE_FLAG_NO_BUFFERING`.
Both retail initializers format a `.crc` name but do not open that sidecar.
The compiled allocation anchors name `DXMemBuffer.cpp` at `0x00650fd0`;
the method/field/API correspondence establishes owner identity despite line drift.

## Read, skip and compression boundaries — static findings

Read and Skip clamp a request extending beyond a known final block and set EOF;
merely reaching its end exactly does not execute that over-read branch. The
returned consumed count advances `+12c`. A refill compares its valid count
against cached capacity `+18`, while the requested amount comes from the shared
global. Changing that global while buffers are open has not been proved safe.
The unsigned pointer/end clamp precedes the signed-positive count test; this
does not justify saying every negative count is ignored. These Read/Skip
findings were static in the September 27 pass; the October 1 comparison below adds
bounded execution evidence without claiming complete file compatibility.

Filename-suffix comparison with the initial `.aya` string at `0x006318a0`
selects compressed paths. Plain start-skip seeks whole configured buffer units,
then uses Skip for the remainder. The `.aya` path goes through decoded-byte
skipping rather than treating the requested logical offset as a raw file offset.

The inlined compressed refill reads a four-byte encoded length, then that many
bytes into shared scratch `0x008c029c`, and invokes the decompressor. Decoded
counts advance the output pointer and accumulated valid count. The wrapper
passes capacity `0x102927` to each decode, including after the destination has
advanced; this pass found no wrapper check against remaining allocated space
or an incoming encoded length exceeding scratch capacity. This is a bounded
static observation, not an executed malformed-input or exploitation test.

PE thunks `0x0055d5f2` and `0x0055d5f8` jump to imports `zlib.dll` ordinal 63
and 9. The selected retained `local-lab/safe-copy-bea-pristine/zlib.dll`
(63,827 bytes, SHA-256
`9929233274cd1c33395036717dda8da45d5a3a3c880a4aeff6deabac3407ecc2`)
exports `uncompress` and `compress` at those ordinals. This verifies the selected
DLL mapping, not which DLL a running installation loaded. The partial source's
simple ReadFile/WriteFile paths omit these `.aya` branches.

When `+0c` is nonzero, refill compares the output-byte sum modulo 256 to the
byte at `+10`; it is not CRC32. `+10` increments even when checking is disabled.
The rechecked constructor/initializers do not populate a check-byte stream, so
this conditional branch is not evidence of active sidecar validation in a
normal initialized reader. The October 1 comparison supplies an authored check
stream and a modeled decompressor; the actual decoder DLL and real Windows I/O
remain unexecuted.

## Buffered-read comparison — October 1

The lead freshly compiled the reconstructed Read and compared it with original
instructions in 200 authored cases. The 192 nonnegative cases also compare state
and provider-call order with the complete byte-matched Skip body, excluding only
destination writes. Eight negative-size cases remain separate malformed-input
observations. Eighty ready-memory states execute without any providers and have
an independent byte-copy, pointer, count, EOF and position-wrap oracle.

All admitted comparisons agree. Exact final-buffer exhaustion leaves EOF unchanged;
overshoot sets it (`0x0054859e`–`0x005485ad`). The check cursor advances even when
checking is disabled (`0x00548785`–`0x0054878e`). Packed refills may accumulate
several chunks before reaching the shared read threshold. A later chunk-header
failure after successful output returns the accumulated count without querying
GetLastError (`0x005486cc`–`0x00548709`); data-read and decode failures have
different paths. Eight negative controls detect changed EOF/check/refill behavior,
missing providers, a wrong import relocation and incomplete execution.

Refill cases use explicit ReadFile/GetLastError and Python-zlib models. The
original C-locale `stricmp` body and import thunk execute; the original zlib DLL
does not. The test uses an 8-byte read threshold and bounded authored buffers,
not normal-size files, real sidecars or a full resource parser. Fatal-file handling
is a terminal observation boundary; its body is not executed. These distinctions
prevent treating modeled agreement as retail I/O or save compatibility.

Read remains unmatched: a 688-byte compiled section versus the 686-byte retail
body, with 460 differing positions. Thirteen exact object controls survive; no
source behavior correction was demonstrated. Private lead evidence:
`bea-decomp/.worktrees/codex-equiv-20260930/local-data/dxmembuffer-read-root-20261001/`,
`native-model-v1/receipt.json`, SHA-256
`3e5e0d5df525c713e04affbb59c55d30b062f16aa6b2293201210c9caf301c17`.
The next useful runtime falsifier is a disposable real packed-file read through
the selected Windows API/DLL path with observed refill counts; it was not run.

## Text-reader edge cases — 67 original-code cases

The complete 580 bytes `[0x00548820,0x00548a64)` were loaded unchanged at their
original addresses in an isolated ELF32; SHA-256
`30942e4e145f0204c60c2aad1a05dc85f038791e6ef4d00c020d36e8843a9232`.
The harness supplies an authored receiver, guarded destination and 64-byte
buffer, and intercepts only controlled zero-byte ReadFile/GetLastError paths.

- With input CR followed by `X` and maximum 3, the output is `0a 00 00` and
  logical position advances two. At `0x00548a32`, only the penultimate CR is
  tested; there is no requirement for a final LF.
- With an exhausted full buffer beginning `S`, a refill returning TRUE/count 0
  still causes the old `S` to be consumed. FALSE with `ERROR_HANDLE_EOF` has
  the same result. Position advances one and EOF becomes set on the next loop
  check. An already-known final block or maximum 1 suppresses the refill and
  stale-byte consumption.
- Sampled maxima 0 and 1 still write a destination NUL. The harness owns that
  byte; this is not proof that a zero-capacity caller is safe. Negative coverage
  is the single value `-1`, not every signed input.

The unconditional post-refill byte load is at `0x005489f4`. These two edge
conditions are also visible in source `ReadString`; they are not claimed as
retail/source divergences. Complete body loading is not complete branch
coverage. Nonempty refills, compression, CRC and real files remain outside this
run. All 308 authored receiver bytes, source bytes, destination guards, stack cleanup and
callee-saved registers were checked for each case.

Receipt: `readstring-072doz1d/probe.json` under the private owner, SHA-256
`d99ea51f050851da529913aa3c5ecdb3a4191cede1cfee7dca526da455c14cd6`.
The earlier 63-case run is retained; its cases are byte-identical to the first
63 in this expanded run. Independent review reconstructed all 67 results;
root re-read the paired raw controls.

## Write/close failure behavior — 71 original-code cases

The complete Write body `[0x00548a70,0x00548bf7)`, 391 bytes, SHA-256
`aba736cadb2e1e654a32e27a5d8692b207ecee0405e9e4c2b5dbca146dd0aeb9`, and
Close `[0x00548c00,0x00548d2f)`, 303 bytes, SHA-256
`899c986095597e7ec5880c70449a58e3b6735486b1f28ca819db9829ea3e5c84`,
ran unchanged with an authored 64-byte buffer and empty filename, selecting
raw I/O. API/allocator substitutes record checked arguments and event order;
they do not perform file or heap operations.

Exactly filling the buffer does not flush it; an additional byte does. On
WriteFile FALSE, Write logs, queries GetLastError, resets the buffer and
continues advancing logical position. A 129-byte request with 17 initial bytes
and two failed full-buffer flushes still advances position by 129 and leaves
18 bytes buffered. Reported short counts are not inspected.

Close of a writer with 17 buffered bytes returns EAX 1 after WriteFile FALSE,
following trace → CloseHandle → free and nulling `+04`. It also returns 1
for TRUE reporting 0/17 or 16/17 bytes, without the trace. Null `+04` returns 0
with no API calls; reader Close makes no write call. Source Write/Close have
similar failure continuation, so these observations confirm retail behavior
rather than a source-version difference. Retail omits the source sidecar work;
its compressed writer additionally ignores the compressor return code, a
static finding not exercised by this raw-path experiment.

Receipt: `write-close-l0acrscz/probe.json`, SHA-256
`86056e9fd35e010acd2b47653db822b885d0f539d3513acaa5784421190903ed`.
All 71 complete outputs were independently reconstructed; they include 61
Write calls, 41 Close calls and 114 intercepted WriteFile events. In Write-only
cases, the report's `closeReturn: 0` is an untouched harness field, not a called
return. Event payload hashes describe full 64-byte buffer snapshots, including
unused tails, not bytes persisted. CloseHandle failure, compression, real
allocation/files, Windows behavior and crash durability were not tested.

Both native harnesses restrict syscalls to i386 read/write/exit and verify a
denied getpid for every case. This is not a claim that inherited descriptors
are inaccessible, nor a full-process sandbox certification.

## Consumer implications and open work

The retail controller recorder `0x00514720` calls Write three times on its
`this+2c` buffer, with four-byte requests at `0x0051472f/0x0051473c/0x00514749`.
The source records seven words; that difference is also bounded in the
[controller contract](../cpccontroller-vtable-semantics-2026-08-11.md#september-27-joystick-and-recording-recheck).
The menu loader `0x0044fa90` constructs the same stack receiver, initializes it
from a file, reads through it and closes/destroys it. These consumers bind the
family to real code paths. They do not establish that every career/settings
serialization helper uses it or prove a full startup/save round trip.

The rebuild can use the measured byte consumption, buffering and source
variations for compatibility. Companion publication must retain its existing
verified-copy/write/reopen protection: retail Close returning true is not
proof of a successful write.

Remaining work: correct the explicit receiver/signed-size/return-width ABI
findings through caller checks and a separate exact cohort; update the seven
kept live evidence comments; test nonempty and compressed refill boundaries
with controlled payloads; then verify selected real-file integrations on copies.
The cheapest falsifiers are exact caller transport for ABI, intercepted bounded
refills for decoder/count logic, and an owned-copy write/reopen comparison for
actual persistence. No original save or pristine input was written.

## Historical records — not current verification

The entries below preserve earlier metadata changes and receipts. Their field
names, signatures, behavior claims and coverage counts were not certified merely
by exporting Ghidra. The current contract above supersedes conflicting active
claims, including the old preference for descriptive names and the old
`mCRCIndex`/`mFlushCount` layout. Historical aliases are retained here.

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 live correction closeout:** `0x004cf050` → `CMenuItem__Destructor_Thunk` (was `CMenuItem__Destructor`). Current live Ghidra reflects confirmed rows only; older conflicting text below is superseded only where confirmed. Use the [closeout](../ghidra-full-reaudit-closeout-2026-07-13.md); final per-address decisions and exact before/after metadata are in `reverse-engineering/binary-analysis/ghidra-reviewed-correction-plan-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

> Binary-to-source function mappings for DXMemBuffer.cpp
> Last updated: 2026-05-24

## Name corrections — 2026-07-28

Superseded in place against `ghidra-function-name-table-2026-07-27.tsv`, the
2026-07-27 headless export of the live maintainer Ghidra project. The evidence
grade, and the limits of what a corrected name does and does not establish, are
stated once at [the area index](_index.md#the-name-corrections-of-2026-07-28).
Old cell text is quoted below rather than deleted, so a reader who remembers the
withdrawn label can tell it was corrected and not lost.

| Address | Superseded label | Historical replacement | Correction |
| --- | --- | --- | --- |
| `0x0048f2f0` | `CDXLandscape__SetUpdateBoundsAndRebuildVB` | `CDXPatch__SetGridOriginStepAndRebuild` | class prefix and suffix both moved |
| `0x004cf050` | `CMenuItem__Destructor` | `CMenuItem__Destructor_Thunk` | same class; suffix re-read |
| `0x00548ec0` | `CDXEngine__FreeLandscapeCellList_Debug` | `CMemoryManager__DeleteTagList_CtorUnwind` | class prefix and suffix both moved |

Where a row's **suffix** moved rather than only its class prefix, the behavioural
text beside it in this note was written for the old name. This sweep corrected
names against the export and re-derived no behaviour, so read any such gloss as
unverified against the new name until it is re-measured.

---

## Superseded Labels

| Address | Superseded label | Historical replacement |
|---------|------------------|---------------|
| `0x00547d70` | `CChunker__CChunker` | `CDXMemBuffer__ctor` |
| `0x00547d90` | `CChunker__Destructor` | `CDXMemBuffer__dtor_base` |
| `0x00547d40` | `DXMemBuffer__SetBufferSize` | `CDXMemBuffer__SetBufferSize` |
| `0x00547dc0` | `DXMemBuffer__OpenWrite` | `CDXMemBuffer__OpenWrite` |
| `0x00547ec0` | `DXMemBuffer__OpenRead` | `CDXMemBuffer__InitFromFile` |
| `0x005482c0` | `DXMemBuffer__GetFileSize` | `CDXMemBuffer__GetFileSize` |
| `0x005482d0` | `DXMemBuffer__Skip` | `CDXMemBuffer__Skip` |
| `0x00548570` | `DXMemBuffer__ReadBytes` | `CDXMemBuffer__Read` |
| `0x00548820` | `DXMemBuffer__ReadLine` | `CDXMemBuffer__ReadLine` |
| `0x00548a70` | `DXMemBuffer__WriteBytes` | `CDXMemBuffer__WriteBytes` |
| `0x00548c00` | `DXMemBuffer__Close` | `CDXMemBuffer__Close` |
| `0x0048ddf0` | `thunk_DXMemBuffer__Close` | `CDXMemBuffer__Close_Thunk` |
| `0x004cdb90` | `CDXMemBuffer__dtor_base` | `CDXMemBuffer__dtor_base_Thunk` |
| `0x00548d30` | `DXMemBuffer__IsEOF` | `CDXMemBuffer__IsEOF` |

## Wave606 Queue Note

Wave606 added comments/signatures and owner-corrected six rows. Post-Wave606 queue telemetry is `6093` total, `3109` commented, `2984` commentless, `1305` exact-undefined signatures, and `1071` `param_N` signatures. Strict clean-signature proxy is `3064/6093 = 50.29%`. The next queue head is `0x00548ec0 CMemoryManager__DeleteTagList_CtorUnwind`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260519-204906_post_wave606_dxmembuffer_io_verified`.

## Wave806 Close Thunk Note

Wave806 raw commentless head (`raw-commentless-head-wave806`, `wave806-readback-verified`) saved `0x0048ddf0 CDXMemBuffer__Close_Thunk` as `bool __fastcall CDXMemBuffer__Close_Thunk(void * this)`. Static instruction evidence shows a direct jump to `0x00548c00 CDXMemBuffer__Close`, and xref evidence ties the thunk to `CParticleSet__LoadParticleSetFile`. Post-Wave806 queue telemetry is `6098` total, `5581` commented, `517` commentless, `0` exact-undefined signatures, `0` `param_N`, strict proxy `5581/6098 = 91.52%`, and next raw head `0x0048f2f0 CDXPatch__SetGridOriginStepAndRebuild`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260524-102416_post_wave806_raw_commentless_head_verified`.

This proves saved static Ghidra metadata for the thunk only. Runtime particle file teardown, exact CDXMemBuffer layout, BEA patching, and rebuild parity remain deferred.

## Wave823 Destructor Thunk Note

Wave823 particle archive buffer cleanup (`particle-archive-buffer-cleanup-wave823`, `wave823-readback-verified`) saved `0x004cdb90 CDXMemBuffer__dtor_base_Thunk` as `void __fastcall CDXMemBuffer__dtor_base_Thunk(void)`. Static instruction evidence shows a direct jump to `0x00547d90 CDXMemBuffer__dtor_base`, and xref evidence ties the thunk to `0x005d4230 Unwind@005d4230` for the ParticleSet.cpp stack-local buffer at `EBP-0x140`. The same wave corrected `0x004cd7a0 CParticleSet__FindByNameAndTrackLinkSlot`; queue after Wave823 is `6098` total, `5628` commented, `470` commentless, strict proxy `5628/6098 = 92.29%`, and next raw commentless row `0x004cf050 CMenuItem__Destructor_Thunk`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260524-183746_post_wave823_particle_archive_buffer_cleanup_verified`.

This proves saved static Ghidra metadata for the thunk only. Runtime stack-local buffer lifetime, runtime particle archive behavior, exact unwind parent/source-body identity, exact CDXMemBuffer layout, BEA patching, and rebuild parity remain deferred.
