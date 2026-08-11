# `CTokenArchive` particle grammar and reference semantics

Status: active, bounded semantic recovery
Last updated: 2026-08-11
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
| direct integer | 47 | Requires the integer output and an initial second word, then parses `%d`. |
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

This closes the static semantics of the parser/resolver/formatter unit and its
shipped corpus crosswalk. It does not prove malformed-file crash behavior,
allocation failure, reference overflow, every downstream particle effect,
console-format identity, or rebuild parity. The cheapest runtime falsifier for
the unusual reference path remains a disposable particle-set copy containing a
named optional modifier; no shipped archive should be edited in place.
