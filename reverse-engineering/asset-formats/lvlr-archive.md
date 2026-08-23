# LVLR level/resource tagged-stream contract

Status: active format contract — complete outer/tag census; most payload schemas
remain owner-specific or open
Date: 2026-08-22
Verdict: all 301 streams and 23,884 top-level tags are accounted for; most
payload schemas and world dependencies remain partial.
Evidence: MEASURED — all 301 mirror-index archive rows inflate to `LVLR`; the
complete earlier top-level chunk census is cited below.
Specimen: `G:\bea-asset-mirror\INDEX.jsonl`, SHA-256
`c45722aeed52e77788c7886cb30b813900d3516b1c387983c442d2b02d4fe4b9`;
retail VAs cite `BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

## Population

The **301** files are:

- 66 numeric `NNN_res_PC.aya` level archives;
- 232 contiguous `goodie_0_res_PC.aya` through `goodie_231_res_PC.aya`;
- `base_res_PC.aya`, `Frontend_res_PC.aya`, and `Loading_res_PC.aya`.

They occupy 86,646,042 stored bytes, use 485 AYA zlib members, and inflate to
231,846,299 bytes. Every inflated stream begins with tag `LVLR`.

## Container layout

The AYA layer is [aya-container.md](aya-container.md). Its concatenated output is
an ordered tagged stream:

```text
repeat until inflated EOF:
    char tag[4]
    u32le payload_size
    byte payload[payload_size]
```

A top-level tag is a routing/ownership boundary; each payload has its own schema
and may contain nested tagged objects. There is no evidence that all payloads
share one generic record layout. In particular, `LVLR` is not the whole stream:
its payload is one four-byte version value, **103**, in all 301 PC files.
`TARG` is one four-byte target value, **1**, on PC. `AYAD` is six `u32` guard/
ABI words with measured tuple `(344,372,316,5084,92,1)`. The cross-platform
measurement and pinned source ownership are in
[`pc-xbox-aya-census-2026-08-13.md`](../game-assets/pc-xbox-aya-census-2026-08-13.md).

## Complete top-level vocabulary census

The earlier complete pass in
[`installed-corpus-census.md`](../installed-corpus-census.md) measured 23,884
top-level chunks:

| Tag | Count | Bounded meaning |
| --- | ---: | --- |
| `LVLR` | 301 | four-byte resource-format version 103 |
| `TARG` | 301 | four-byte PC target value 1 |
| `AYAD` | 301 | six-word ABI/static-shadow guard tuple |
| `TEXT` | 18,857 | context-dependent texture/text resource |
| `MESH` | 3,492 | embedded mesh resource |
| `GDIE` | 232 | Goodie/gallery archive owner |
| `ERES` | 66 | numeric-level entity resources |
| `IMPS` | 66 | imposter resources |
| `LNDS` | 66 | landscape/terrain owner |
| `SSHD` | 66 | static-shadow owner |
| `SURF` | 66 | surface owner |
| `WRES` | 66 | world-resource placements/data |
| `DMKR` | 1 | deeply bounded Level-100 marker lane |
| `PLAT` / `PMIB` / `VSDS` | 1 each | specialized vocabulary; schemas incomplete |

The canonical warning in
[`game-assets/aya-resource-tag-family-static-contract.md`](../game-assets/aya-resource-tag-family-static-contract.md)
applies: a fourcc is loader vocabulary, not a complete payload schema or runtime
coverage claim.

## Known structural relations

- Each Goodie archive has the four outer chunks `LVLR`, `TARG`, `AYAD`, `GDIE`.
  Filename indices align with save Goodies slots 0–231; terminal slot 232 maps to
  cutscene 33 and has no PC archive.
- Each of the 66 numeric archives has a same-number MissionScripts directory and
  world-header record, but the reverse sets are larger. Shared numeric IDs prove
  a relation, not execution or selection.
- Embedded `MESH` bodies may be carved only as candidates until their exact
  enclosing boundary/dependencies are proved. `TEXT` can own serialized texture
  metadata and must not be interpreted as arbitrary prose.
- The [CMSH animation/usage census](cmsh-animation-usage.md) decodes the
  validated `PMSH[/PMS2]` logical name on all 3,485 `MESH` rows in the 66 numeric
  archives: 3,432 rows join to 205 loose meshes and 53 have an empty name. This
  proves numeric-archive membership, not a WRES placement, spawn, or animation
  schedule. The seven additional all-LVLR `MESH` rows are in Goodie archives.
- Level 100/base/frontend have deep owner-specific work; the other worlds are
  primarily structural inventory.

## Retail decoder anchors

No single function has been proved as the complete `LVLR` decoder. Static routes
that consume the same tagged-resource family are:

| VA | Identity | Demonstrated boundary |
| --- | --- | --- |
| `0x004D6F70` | `CResourceAccumulator__GetResourceFilename` | Builds the resource filename selected by the accumulator path. |
| `0x004D7200` | `CResourceAccumulator__ReadResourceFile` | Reads resource data with seven `CChunkReader__Read` calls. |
| `0x0050B780` | `CWorld__DeserializeWorld` | Reads four tags with `CChunkReader__GetNext` and updates world load state. |
| `0x0040F980` | `CBattleEngineData__LoadFromMemBuffer` | Forty-two buffered reads for one embedded Battle Engine data owner. |
| `0x00423910` / `0x00423960` | `CChunkReader__GetNext` / `Read` | Shared inner tag/field primitives. |

These VAs route future work; they do not establish which function owns every
chunk. Evidence is summarized in
[`coordinate-long-tail.md`](../binary-analysis/functions/coordinate-long-tail.md)
and
[`BattleEngineDataManager.cpp.md`](../binary-analysis/functions/BattleEngineDataManager.cpp.md).

## Decoder/tool evidence

[`tools/aya_archive_inventory.py`](../../tools/aya_archive_inventory.py) is the
tracked fail-closed envelope/top-level observer. It rejects overruns and unknown
raw-stream admission, records exact chunk geometry, and labels embedded CMSH
bodies candidate-only. `tools/aya_corpus_chunk_inventory.py` supplies corpus
aggregation. Cross-platform comparison tools add PC/Xbox geometry evidence but
do not turn differing payloads into decoded semantics.

## Open questions and falsifiers

- Build a per-tag-instance ledger of offsets, lengths, schemas, opaque ranges,
  references, and exact consumer VAs for all 23,884 chunks.
- Close packed mission/object representation and packed-versus-loose precedence.
- Join every world to meshes, textures, physics, scripts, audio, localization,
  videos, and Goodie/career state.
- Trace one non-Level-100 world with a different tag shape before generalizing
  Level-100 field meanings.
- Test malformed lengths only in a disposable copied profile; never edit the
  pristine archive shelf.

## Claim boundary

The 301-file population, AYA framing, top-level geometry, and selected owner
relations are settled. General LVLR field semantics, dependency graphs, runtime
selection/failure behavior, and parity are open.
