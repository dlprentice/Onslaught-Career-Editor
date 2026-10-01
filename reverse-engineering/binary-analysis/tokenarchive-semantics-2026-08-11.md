# `CTokenArchive` particle grammar and reference semantics

Status: active, bounded semantic recovery
Last updated: 2026-10-01 (allocation-prefix and original numeric-scanner recheck; August corpus evidence retained)
Evidence: MEASURED — complete pristine retail bodies, exact parser tables,
particle-set files, callers, memory layout, and twelve normalized-identical PC
demo twins; UNKNOWN — no retained `TokenArchive.cpp`, malformed-input runtime
causality, allocation failure, and rebuild-wide particle parity.
Verdict: the released particle token grammar, parser dispatch, deferred-reference
resolver, and five compiled formatter stubs are recovered. The five functions
named `Write*` do not actually serialize anything in the shipped PC builds.

Specimen: pristine PC retail `BEA.exe`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`;
PC demo `BEA.exe`, SHA-256
`d8637dd755b21c720c0cb8f71923f94d2a04a184d90f5343c2e868ce8606e5c2`.
The retail binary retains the exact source path
`C:\dev\ONSLAUGHT2\TokenArchive.cpp`, but that file is not present in the
retained Stuart source collection. This report therefore treats the path as
ownership evidence, not source-code evidence.

## Result

The twelve-function unit covers 2,258 retail bytes and 747 decoded
instructions. Every function has an independently mapped demo twin with zero
normalized instruction differences; 369 raw bytes differ only in encoded
addresses or displacements. The machine-readable result is
[`tokenarchive-semantics-2026-08-11.tsv`](tokenarchive-semantics-2026-08-11.tsv),
4,072 bytes, SHA-256
`f29a0be0823dd188fd781a3b1180c1643872088a5fa0d27f5ae3c0547fc0f25e`.

The sealed parser reproof is
`local-lab/tokenarchive-parser-contract-reproof-20260809-v7/`. Its receipt has
SHA-256 `ed2aca4f54a82476a9f1cc1cb7e1a81376fae9b9c6dee22fcf890fe15fbf07bc`.
Its exact 124-row token table, 141-row writer-call table, and 13-row descriptor
loader table have SHA-256 values
`cf9a77aea8df2e375361750657ce16f7b3d10df5f6ea0a6a26e15e4c9d14cc6d`,
`00ff838d301ae36f81fca93280c2b988c89ed84c49b435b933dc67750e756579`,
and `cf9ea88b76d7a3e1a8f91f22bb9f41e4605055642dd855679bd2599cfefea4fc`.

## Grammar and parser

`CTokenArchive::ReadLine` delegates to the existing buffered-file owner and
removes one terminal line-feed byte. `ReadNextToken` reads at most 999 bytes
into a 1,000-byte global line buffer, scans the first two whitespace-delimited
words, then performs a case-sensitive linear lookup through token IDs 0..123.
Unknown names write token ID `-1` and fail.

The 124 names form the complete shipped particle descriptor grammar. Across
`MainSet.par`, `Frontend.par`, and `ModelViewer.par`, the sealed corpus accounts
for 27,186 token lines. The successful dispatch classes are:

| Parse shape | Token IDs | Behavior |
| --- | ---: | --- |
| marker, no value | 2 | Accepts the file header and descriptor separator without a value output. |
| direct integer | 47 | Requires the integer output and an initial second word, then parses `%i`. |
| direct float | 19 | Requires the float output and an initial second word, then parses `%f`. |
| raw remainder string | 3 | Copies everything after the token name, preserving embedded spaces. |
| reference name | 16 | Allocates the remaining name, returns a pending slot index, and defers object binding. |
| float with optional reference | 37 | Parses a leading float, allocates the optional remaining name, and defers the paired pointer binding. |

The adjacent table has 125 one-byte entries and seven branch targets: the six
successful shapes above plus the default failure arm. Later numeric `sscanf`
return values are ignored, so success does not prove that malformed numeric
text converted. The reference branches also have weaker pointer/count guards
than the direct branches. These are released behaviors, not recommendations
for a new parser.

Tokens 49..57 (`Start_*`, `End_*`, and `Transition_*` RGB components) multiply
unreferenced numeric values by the exact retained approximately-`1/255`
constant. All other numeric tokens retain their parsed units.

## Allocation and scan-format recheck — October 1

The integer scanner passes the string at `0x00633a24`, whose bytes are `%i` and
a terminator (`0x004f586c`–`0x004f5876`). The earlier `%d` description above is
corrected. This is a format-string finding; the numeric scanner itself was not
executed by the new prefix experiment. The original guard structure remains:
direct numeric branches check their output pointer and initial scan count;
plain references check the string-output pointer/count and then write the integer
output without its own null check. The float-reference branch enters its scanner
at `0x004f59b7` without those guards. Later scan return values are ignored.

Both reference branches request the remaining name length **plus two bytes**.
For float references, the suffix begins at line plus token length plus value length
plus two; `0x004f5a0e`–`0x004f5a19` counts through its terminator, increments once
more and passes that size to the memory manager. The reconstruction used plus one
for this branch. That discrepancy is corrected without claiming an overflow or
visible effect: a conventional terminator-sized allocation can still hold the name,
and the allocator's bucket behavior was not part of this check.

Freshly compiled old/corrected candidates and original prefixes were compared on
85 float-reference and 85 plain-reference states. All 85 former request differences
are removed; the 85 controls remain equal. Five negative controls catch a removed
increment, wrong suffix origin, escaped/incomplete execution and an unadmitted
read. Inputs are authored scratch strings, including deliberately inconsistent
states. Execution starts after classification/conversion and stops at allocator
entry: no file reader, scanf, allocator, copied name or fixup resolver runs.
All fifteen other callable sections/relocation targets remain unchanged and exact.
ReadToken's 960-byte section still differs at 543 positions; it receives no exact
match credit. The August corpus/demo comparisons were not rerun in this pass.

Private lead evidence:
`bea-decomp/.worktrees/codex-equiv-20260930/local-data/tokenarchive-root-20261001/readback.json`
and `allocation-v1/receipt.json` (SHA-256
`c1fffd33dab5794f33c216438ff47cb5a613c988e8d012eef1a69adb963cde76`).
Complete parser/allocator behavior remains open; a useful next falsifier compares
the whole reader on a disposable particle-set copy with real numeric conversion.

## Original numeric scanner — October 1

The lead independently reproduced `sscanf` at `0x0055e14f`, its `_input`
implementation and admitted original CRT dependencies on 72 authored ASCII cases
using `%i`, `%f` and `%s %s`. Nine negative controls reject missing initialization,
conversion/EOF dependencies, unsupported locale state, incomplete execution,
insufficient output space and missing termination. No conversion, Windows, TLS,
heap or file-I/O routine is replaced. The admitted C locale and original tables
are explicit inputs; this is not a claim that the complete CRT startup ran.

Original `__cfltcvt_init` at `0x0055da8d` is necessary for floating conversion:
it changes the dispatch at `0x00653660` from the trap routine to `_fassign`
at `0x00560dea`. A native i386 runner executes the same 32 admitted function
ranges, trapping all other code. It agrees on all 72 cases and six float edges
under three precision controls and three stack patterns, 120 runs total.
Return count, complete output buffers, consumed input, string-stream state,
input preservation, stack guards, nonvolatile registers and x87 state are checked.

Measured examples under those conditions:

- `%i` parses `010` as eight; `08` yields zero after consuming only the first byte.
- `%f` parses `1e+` as 1.0 and consumes the incomplete exponent. `nan` and `inf`
  fail without writing; `+.` returns EOF without writing.
- `%f` on `1.401298464324817e-45` yields raw float bits `00000002`, including
  the native precision/stack controls. This malformed/extreme-input study does
  not establish ordinary content reachability or a portable parsing rule.

Fresh instructions show ReadToken's initial call at `0x004f57dc` uses `%s %s`
at `0x00625274`. The scanner accepts both words in `File_Version +.`; whether
ReadToken then reports success with an unchanged numeric destination remains
a useful composed falsifier. ReadToken itself and archive I/O did not execute
in this experiment.

Lead reproduction owner:
`bea-decomp/.worktrees/codex-equiv-20260930/local-data/retail-sscanf-20261001/`.
`scanner-v03/receipt.json` SHA-256:
`1328f00bccda3b44438b691f36c3daef9ac9e8fdff7325852948a9f42509a089`;
`native-v04/receipt.json`:
`95f748a72bb132a775c4342368a228ca16c95917b84b9b4cfb3be6eee9701a5d`.

## Deferred reference workspace

The loader allocates an exact `0x1388c`-byte workspace:

- source archive pointer at `+0x0`;
- an unused/cleared word at `+0x4`;
- pending count at `+0x8`;
- 10,000 destination pointers beginning at `+0x0c`;
- 10,000 allocated reference-name pointers beginning at `+0x9c4c`.

`BindIndexedFieldPointer` places a caller's field address in the destination
table. `RegisterReferenceFixup` stores an accompanying scalar in a two-word
record and binds its second word as the destination. No body in this unit checks
the 10,000-entry bound or a failed name allocation.

`ResolveReferences` walks the particle objects through their `+0x38` next
links, builds a temporary pointer array, and resolves every pending name with
CRT `bsearch`. The previously unnamed adjacent function at `0x004f5c70` is the
missing comparator: `stricmp(key, object->name_at_+4)`. `CreateByType` inserts
the same list in case-insensitive name order, closing the sort/search contract.
Each fixup receives the matched object pointer or null; every allocated name
and the temporary array is freed, and pending count is reset to zero.

## Particle factory and format coverage

`CParticleSet::LoadFromArchive` validates header tokens 0, 1, and 2; reads each
descriptor's type/name through tokens 3 and 4; creates its object; dispatches
the object's token loader; then performs one reference-resolution pass. The
factory/RTTI/vtable joins identify all thirteen released descriptor types:
`CPDSimpleSprite`, `CPDEmitter`, `CPDModifier`, `CPDSelector`,
`CPDColourRange`, `CPDTimeline`, `CPDShape`, `CPDTrail`, `CPDMover`,
`CPDFunction`, `CPDMesh`, `CPDFoR`, and `CPDPMesh`.

One asymmetry is exact rather than inferred. Token 32,
`Velocity_Randomness`, is parsed as a direct float but its compiled formatter
call uses the float-plus-reference shape. The type-2 emitter loader can
therefore reuse a stale pending-slot index if a named suffix were supplied.
All 338 shipped token-32 lines contain no named modifier (336 explicit `NONE`,
two with no suffix), masking the defect in the retail corpus.

## The `Write*` bodies are not writers

The five helpers have 141 direct calls from descriptor `WriteTokenFields`
bodies and format the expected textual shapes: integer, float, raw string,
object name or `NONE`, and float plus object name or `NONE`. However, each one
only calls `sprintf` into a private 400-byte stack buffer and returns. There is
no archive receiver, file/memory sink, returned buffer, callback, global write,
or persistent side effect. The demo build contains the same bodies.

Accordingly, these functions are recovered as discarded line formatters—most
likely surviving editor/export scaffolding—not as a working PC serializer.
Their call graph does still prove the intended token/value symmetry for 140 of
141 calls and exposes the token-32 mismatch above.

## Boundary

The August reproof records the static parser/resolver/formatter and corpus
crosswalk; the October corrections above bound the claims freshly rechecked.
These records do not prove malformed-file crash behavior,
allocation failure, reference overflow, every downstream particle effect,
console-format identity, or rebuild parity. The cheapest runtime falsifier for
the unusual reference path remains a disposable particle-set copy containing a
named optional modifier; no shipped archive should be edited in place.
