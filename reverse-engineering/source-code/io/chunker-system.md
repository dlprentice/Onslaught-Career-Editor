# Chunk readers and resource dispatch

Status: active, bounded retail/source contract
Last updated: 2026-09-27
Summary: re-derived resource routing and reader behavior; historical invented methods, tag meanings and validation claims are superseded.
Evidence: MEASURED — complete selected pristine bodies, literal-selected calls and isolated original-code reader controls; SOURCE — pinned chunker, resource accumulator, engine, platform and Goodies definitions. No new whole-game loading run.
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

The September 27 recheck covers 22 complete bodies, with retained byte hashes
and disassemblies in `local-data/test-runs/re-audit-20260926/resource-dispatch/`.
The source is `references/Onslaught` at `5352a81cdb838b145a57f7febc5d9fc4b0129ebb`.
It supplies identities to test, not an interchangeable implementation.

## Reader contract

The pinned `chunker.h:32–51` declares `CChunkReader`. `chunker.cpp:96–195`
supplies the eight definitions corresponding to these complete retail bodies:

| Entry | Bytes | Re-derived operation |
| --- | ---: | --- |
| `0x004237d0` | 104 | Constructor allocates a buffer, stores `File` at +4 and sets ownership at +12. It does not initialize Size or ReadSinceChunk. |
| `0x00423840` | 46 | Destructor destroys/frees a non-null File only when owned; then clears its pointer. It does not call Close. |
| `0x00423870` | 75 | `Open(CMEMBUFFER*)` clears Size/+0 and consumed count/+8; destroys the prior owned buffer, relinquishes ownership and adopts/returns the argument. |
| `0x004238c0` | 52 | `Open(char*)` clears those counters and calls the existing buffer's InitFromFile with filename, `0x11,1,0`; returns File on nonzero status, otherwise NULL. Ownership is unchanged. |
| `0x00423900` | 16 | Calls File.Close and converts any nonzero result to 0, zero to -1. This does not add a durable-write guarantee. |
| `0x00423910` | 65 | Clears consumed count; reads a four-byte tag into a local, then four-byte Size into the object. A signed result below four from either read returns zero; otherwise returns the **first** word, the tag. |
| `0x00423960` | 45 | Multiplies size/count modulo 32 bits, advances consumed count before reading and returns full EAX 0/1 according to exact returned-byte equality. It contains no chunk-size assertion or checked multiplication. |
| `0x00423990` | 24 | Computes Size minus consumed count modulo 32 bits, sets consumed count to Size, then forwards that delta to File.Skip. It adds no independent overrun guard. |

These eight bodies total 427 bytes. `membuffer.h:23–26` selects CDXMemBuffer
when `_DIRECTX` is defined. The [buffer contract](../../binary-analysis/functions/DXMemBuffer.cpp.md)
owns the underlying implementation's separate clamp/compression/file behavior.
A wrapped Skip delta must be interpreted there, not assumed to be harmless.
The constructor, destructor and both Open overloads have only static evidence
in this pass. Four smaller routines also have the isolated controls below.

The [six-interface correction](../../ghidra/README.md#re-audit-chunk-reader-interfaces--september-27)
is promoted with exact live readback and independently restored recovery.
Constructor, destructor, Close, GetNext and Skip now use automatic thiscall
receivers in the same physical ECX location. Read returns int in full EAX,
replacing the saved bool/AL type. Its three stack arguments do not move;
low-word multiplication alone does not settle size/count signedness. The
constructor's machine EAX=this return and the destructor's void return remain.
These are bounded machine-interface corrections, not complete class typedefs.

Each chunk header is a four-byte tag followed by a four-byte payload size.
`GetNext` does not search for a requested tag, validate nesting or distinguish
clean EOF from a short tag/size read. Callers decide which nested chunk to read
next. Resource dispatch treats a zero tag result as loop termination; this
alone cannot establish successful or complete asset loading.

The earlier description invented `GetChunk`, `BeginChunk` and `EndChunk`, and
claimed runtime nesting/size validation. The actual writer API uses `Start`
and `End`; the reader uses `GetNext`, `Read` and `Skip`. The writer's 256-entry
nesting array and initial 256 KiB growth unit are source facts, not proven
runtime-reader validation or a fixed-size allocation guarantee.

### Isolated original-code controls — September 27

`original_reader.py` under the private evidence owner runs 49 cases through
the complete unchanged Close/GetNext/Read/Skip bodies: 150 bytes loaded at
their original addresses in a native Linux i386 probe. Buffer calls return
controlled values and use authored memory; a syscall filter denies unexpected
operations. Each run checks stack cleanup and nonvolatile registers. No game,
Windows file operation or real asset was opened.

- Eighteen GetNext cases distinguish first/second short reads, signed count
  admission, zero/high-bit tags and partial size writes. A failed second read
  retains any bytes that the intercepted callee already wrote to Size.
- Fourteen Read cases show low-word size/count multiplication, counter wrapping
  and the requested-count update before the callee. Success compares the full
  returned count for equality. These cases copy zero destination bytes; they
  do not test buffer copying or the real callee's possible return values.
- Twelve Skip cases show wrapped subtraction, assignment of consumed count to
  Size before the callee and unchanged forwarding of its supplied return.
- Five Close cases distinguish a zero callee result from nonzero results,
  including `0x100`, whose low byte alone would be zero.

Two explicitly altered probe copies provide counterfactual controls: changing
GetNext's signed admission branch to unsigned changes the supplied `-1` case;
removing Read's counter write changes both the observed callee-entry state
and the final state. Pristine bytes remain unchanged. The full records are
`resource-dispatch/reader-sahv5bik/results.json` under the evidence owner’s
parent; validation commands and exact private paths are in
[VALIDATION.md](../../../VALIDATION.md#resource-reader-identities-and-controls--september-27).
Underlying buffer I/O, allocator outcomes, ownership and full dispatcher
execution are outside these experiments.

## Resource dispatcher

The complete body at `0x004d7200` is 2,071 bytes, SHA-256
`4922caa624a79108fbfd90b185e48367e03129b5d3694dbe201d8251807321cf`.
The exact function-name timing diagnostic and unknown-chunk diagnostic,
reader construction and tag branches identify the source counterpart
`CResourceAccumulator::ReadResources` (`ResourceAccumulator.cpp:732–1055`).

The existing evidence tool's `tag-calls` command checks 12 direct consumer
calls: exact four-byte discriminator construction, equality direction, EAX
provenance from GetNext, reader/argument transport, receiver constants and absence of direct interior
entries. Explicit RET widths are recorded separately from full cleanup: computed
jumps, unresolved exits, exception paths and stack balance are not certified.
It matches nine unconditional source clauses. Three conditional clauses remain withheld by the checker;
manual correspondence must retain their platform differences. The initial
literal bytes are writable data, so the proof does not assert runtime
immutability. Class spelling is not inferred from a tag or filename.

| Tag | Retail consumer | Bound role; source correspondence |
| --- | --- | --- |
| `MESH` | `0x004aab90` | Mesh data; reader and zero arguments. Source uses `CMESH::Deserialize` with one argument. Concrete alias spelling remains unproved. |
| `TEXT` | `0x00559be0` | Texture data; zero and reader arguments. Source uses `CTEXTURE::Deserialize` with one argument. This is not text/string loading. |
| `ERES` | `0x0044a6e0` | Engine resource loading, corresponding to `ENGINE.Deserialize`. “Entity resources” was an unsupported expansion. |
| `WRES` | `0x0050b780` | WORLD object deserialization. Exact concrete class spelling remains separate. |
| `IMPS` | `0x00543d90` | Imposter data, corresponding to `CIMPOSTER::DeserializeAll`; not imports. Conditional source clause is withheld by the mechanical checker. |
| `LNDS` | No consumer call | Equality at `0x004d773e` routes to common Skip in this retail PC body. It does not establish a landscape decoder here. |
| `VSDS` | `0x005042f0` | Vertex-shader data. Retail PC calls the loader; pinned source calls it only in its XBOX branch and skips on PC. |
| `PLAT` | `0x00515b10` | Platform font deserialization, corresponding to `CPCPlatform::Deserialize`. |
| `SURF` | `0x00556490` | SURF object deserialization. Full schema and concrete class spelling remain open. |
| `SSHD` | `0x004ee8a0` | Static-shadow bulk loading, corresponding to `STATICSHADOWS.DeserializeAll`; not a proved “shadow shader.” The body does not consume the supplied ECX. |
| `PMIB` | `0x00550750` | PATCHMANAGER bulk deserialization; the source's `_DIRECTX` branch. The current patch-object name does not prove its manager's class spelling. |
| `DMKR` | `0x00441000` | Landscape damage-resource bulk loading, corresponding to `GetDamage()->DeserializeAll`; not debug markers. |
| `GDIE` | `0x0045c870` | Goodies/gallery deserialization. Retail's image branch loads one texture and derives its height, unlike the source count/height loop. |

Further source/retail differences matter to a future implementation:

- Retail reads a third argument. After the earlier metadata tags and MESH
  branch, a nonzero value skips later payload branches. The source has two
  arguments; “skip everything except meshes” would overstate the retail gate.
- Retail returns for level -3 after the loading diagnostic, before opening a
  reader. The corresponding source return is commented out.
- The engine consumer calls GetNext but does not check the source's `ENGN`
  assertion, nor enforce its fixed map-texture-count assertion.
- Names and correct tag routing do not prove payload lengths, allocation
  safety, complete schemas, object lifetime or rendering parity.

## Filenames and persistence boundaries

The 643-byte body at `0x004d6f70` corresponds to source GetFileName
(`ResourceAccumulator.cpp:178–206`). Resource IDs -1/-2/-3 select base,
Frontend and Loading names; nonnegative IDs use three-digit level formatting;
remaining negatives use `-level-1000` for the goodie filename. This is distinct
from the source resource-builder's separate 10000 resource-ID starting value.
Platform values 1/3/2 select PC/PS2/XBOX suffixes. The earlier saved comment
claiming 1/2/3 means PC/PS2/XBOX is disproved. Invalid platforms and path
length safety are not certified.

This resource reader is not the `.bes` career serializer. The
[save/settings contract](../../binary-analysis/save-options-static-review-2026-05-26.md)
owns its layout and version/length limits; “a fixed raw struct dump” was too
broad a description of the retail serializer's explicit blocks. The earlier
blanket “AYADATA / version 103” file-header claim is withdrawn here: it was
not proved by the reviewed chunk-reader bodies. See the
[asset-format owner](../../game-assets/aya-asset-format.md) for separately scoped
container evidence.

Unknown payload/type questions need a defining declaration, an independent
retail type witness, or a controlled copy-based loader observation. Full-game
loading, real files and GPU/display behavior were not run in this recheck.
