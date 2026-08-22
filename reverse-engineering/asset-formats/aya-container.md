# `.aya` container contract (PC chunked-zlib envelope)

Status: active format contract — complete outer framing; payload semantics split
by inflated owner
Date: 2026-08-22
Verdict: all 1,361 PC AYA outer envelopes are accounted for; payload contracts
remain owner-specific.
Evidence: MEASURED — the 2026-08-22 read-only reparse of
`G:\bea-asset-mirror\INDEX.jsonl` accounts for 5,464/5,464 indexed files and all
1,361 PC AYA files. Earlier complete-member measurements and static VAs are
cited rather than silently re-derived.
Specimen: `G:\bea-asset-mirror\INDEX.jsonl`, SHA-256
`c45722aeed52e77788c7886cb30b813900d3516b1c387983c442d2b02d4fe4b9`;
retail VAs cite `BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

## Population and dispatch

The PC tree contains **1,361** `.aya` files:

| Inflated owner | Files | Inflated magic | Contract |
| --- | ---: | --- | --- |
| Level/resource streams | 301 | `LVLR` | [lvlr-archive.md](lvlr-archive.md) |
| Meshes | 213 | `CMSH` | [cmsh-mesh.md](cmsh-mesh.md) |
| Textures | 847 | `DDS ` | [dds-texture.md](dds-texture.md) |

The extension therefore identifies only the outer compression envelope. It does
not identify the inflated payload schema.

## Exact PC envelope

Every measured file is a concatenation of one or more members:

```text
repeat until physical EOF:
    u32le compressed_length
    byte zlib_member[compressed_length]   // RFC-1950 wrapper
```

The four-byte length is the exact stored zlib-member length. Members inflate in
file order and their outputs concatenate; the member boundary is a compression
chunk, not a demonstrated semantic boundary. Zero lengths, truncated prefixes,
member overruns, incomplete zlib streams, trailing compressed bytes, and output
beyond the configured bound are rejected by the tracked fail-closed observer in
[`tools/aya_archive_inventory.py`](../../tools/aya_archive_inventory.py).

The complete earlier pass in
[`installed-corpus-census.md`](../installed-corpus-census.md) measured:

| Owner | Files | Members | Stored bytes | Inflated bytes |
| --- | ---: | ---: | ---: | ---: |
| Resource archives | 301 | 485 | 86,646,042 | 231,846,299 |
| `dxtntextures` | 800 | 951 | 43,268,019 | 232,320,792 |
| Meshes | 213 | 222 | 16,734,865 | 44,175,802 |
| `resources/textures` | 47 | 67 | 5,210,813 | 28,750,036 |
| **Total** | **1,361** | **1,725** | **151,859,739** | **537,092,929** |

The 6,900-byte difference between stored AYA bytes and zlib payload bytes is
exactly 1,725 four-byte length prefixes. Member counts are 1 member in 1,115
files, 2 in 180, 3 in 25, 4 in 30, and 5 in 11. There are 364 full 1 MiB
inflated members; that supports a writer chunking policy, not a universal
payload limit.

## Inflated tagged streams

Resource and mesh payloads use an eight-byte tagged-chunk header:

```text
char tag[4]
u32le payload_size
byte payload[payload_size]
```

The complete allowed tag vocabulary is owner-specific. A recognized fourcc
proves routing vocabulary, not the layout or meaning of every payload byte.
`tools/aya_archive_inventory.py` bounds member counts, output bytes, top-level
chunk counts, chunk lengths, and candidate embedded CMSH bodies. The
AYAResourceExtractor-based harness
[`tools/BeaAssetExportHarness/Program.cs`](../../tools/BeaAssetExportHarness/Program.cs)
is additional tool/source evidence for selected meshes and DDS textures; it is
not retail-runtime proof or a general hostile-input decoder.

## Retail decoder anchors

These VAs are static routes in pristine `BEA.exe` (`74154bfa…`), not a claim
that one function owns the whole outer envelope:

| VA | Static identity | Demonstrated boundary |
| --- | --- | --- |
| `0x00423910` | `CChunkReader__GetNext` | Returns the next four-byte inner tag and resets its per-chunk offset. |
| `0x00423960` | `CChunkReader__Read` | Reads `factorA * factorB` bytes from the current inner stream. |
| `0x00548570` | `CDXMemBuffer__Read` (table label) | Shared buffered read reached by both chunk-reader functions. |
| `0x0055D5F2` | imported `uncompress` thunk | Six-byte IAT thunk used by `CDXMemBuffer` read/open paths. |
| `0x0055D5F8` | imported `compress` thunk | Six-byte IAT thunk used by buffered write/close paths. |

Evidence: the two focused
[`ChunkReader` notes](../binary-analysis/functions/ChunkReader.cpp/CChunkReader__GetNext.md),
[`CChunkReader__Read`](../binary-analysis/functions/ChunkReader.cpp/CChunkReader__Read.md),
and [`import-thunks.md`](../binary-analysis/functions/import-thunks.md).
The precise top-level function that opens every AYA family and its malformed
member behavior remain unpinned.

## Open questions and cheapest falsifiers

- **Outer loader ownership:** trace or statically close the file-open call chain
  for one resource, one mesh, and one texture to determine whether all three use
  the same envelope reader.
- **Chunking policy:** obtain writer/source evidence or compare more platform
  builds before treating 1 MiB as a format rule.
- **Failure behavior:** use only a disposable copied profile and deliberately
  truncate one length prefix/member; never edit the pristine shelf.
- **Search precedence and case:** a file-I/O trace across packed and loose
  resource paths is required.
- **DLL versus internal codec work:** the imported zlib thunk establishes the
  DLL ABI for `compress`/`uncompress`; the separate in-image texture inflate
  machinery does not prove that every AYA path uses the same implementation.

## Claim boundary

This contract closes the PC outer envelope and population. It does not close
LVLR fields, CMSH animation/skinning, decoded texture pixels, runtime load
precedence, malformed-input outcomes, or rebuild fidelity. No asset bytes are
tracked here.
