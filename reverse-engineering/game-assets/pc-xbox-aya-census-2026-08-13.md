# The PC and USA Xbox AYA shelves pair 301 resources; 63 differ only in TEXT/MESH counts

Status: active measured cross-platform packaging and resource-selection finding
Date: 2026-08-13
Verdict: The pristine PC shelf has 301 strict chunked-zlib AYA archives; the
USA Xbox container has 302 strict raw-tag-stream AYA members. All 301 PC IDs
pair, Xbox alone has `goodie_232`, and the 63 top-level sequence differences
are completely explained by `TEXT`/`MESH` counts. Serialized size does not
establish visual quality.
Evidence: MEASURED — two byte-identical v3 corpus replays through
`tools/aya_cross_platform_compare.py`, bound by the path-free manifests and
output hashes below; pinned source supplies only the cited field ownership.

## Bound inputs and deterministic receipts

The comparison was run over one pristine PC resource shelf and one USA Xbox
ZIP. Retail archives and generated rows remain under `local-lab/`; this note
promotes only the bounded aggregate facts.

| Identity | Value |
| --- | --- |
| PC 301-file canonical manifest SHA-256 | `84658d1c116083dd9d234de1b456da706cb50763d8cc35b03603d98c338c1170` |
| PC stored/raw bytes | 86,646,042 / 231,846,299 |
| PC zlib members | 485: 235 archives with 1, 25 with 3, 30 with 4, 11 with 5 |
| Xbox ZIP length / SHA-256 | 1,943,296,611 / `7a83dcc73fecfc701306bcaf78c96f55c4ecd47ef5d1ab10e9e20766a25281ae` |
| Xbox 302-member canonical manifest SHA-256 | `a040e00ffa6a1ede7778f3bcfe7818bb33fe63e1d8dc53d26cd51bfbfdaa7142` |
| Xbox paired/all raw AYA bytes | 1,624,113,875 / 1,624,113,955 |
| Xbox ZIP-compressed AYA member bytes | 646,813,965; all 302 use ZIP method 8 |
| Comparator SHA-256 | `8d6c834d26fce290c43dc9d1cd3104656f3dd7d019fb540ae3cd3a7112e22e9f` |
| V3 census replay SHA-256 | `839fef00861e08c93903cf93e59af6169090de12e27c1919b7ffb79257b9b601` |
| Geometry replay SHA-256 | `2462f7453fb3b3ec252a0ab4e8f0f08891c3e6338b585e910f289d0a6edd8165` |
| Divergence replay SHA-256 | `e204993f070c4c58a43d079909c5caa098222c14c671a40aa9a409f5feeabed9` |

The two census files use
`bea.pc-xbox-aya-logical-census.v3`. The unchanged chunk-row schema remains
`bea.pc-xbox-aya-chunk-geometry.v2`; it accounts for 47,657 rows. The earlier
`pc-xbox-aya-v2-a-census.json` is superseded: it used the same v2 identifier as
a later shape despite 737 recursive leaf-or-missing-key differences (602 pair,
126 divergence, six summary, three source). Local
`AYA-CENSUS-SCHEMA-SUPERSESSION-2026-08-13.md` owns that disposition.

The two canonical manifests bind different, explicit surfaces:

- PC rows bind normalized ID/basename, stored length/hash, raw length/hash,
  zlib-member count, chunk count, and geometry hash.
- Xbox rows bind normalized ID/basename, central-directory compressed length,
  raw length/hash, CRC32, chunk count, and geometry hash. They do not claim a
  per-member compressed-byte hash. The whole-ZIP SHA-256 binds the container;
  the separate histogram binds its member compression methods.

## Strict framing and census

All 301 PC files decode only through the explicit `pc-chunked-zlib` path. All
302 Xbox AYA members begin directly with a strict `raw-tag-stream`, even though
the surrounding ZIP deflates every member. After decoding, every file is fully
accounted as contiguous `[4-byte tag][u32 payload length][payload]` records;
the length excludes the eight-byte header. No gap, overlap, padding region,
unknown top-level tag, or trailing byte was admitted. This matches the pinned
writer in `references/Onslaught/chunker.cpp:56-80`.

The 301 paired IDs are 232 goodies, 66 numeric levels, and `base`, `frontend`,
and `loading`:

- 238 pairs have the same top-level tag sequence: all 232 goodies plus levels
  `512`, `612`, `621`, `622`, `700`, and `720`.
- 63 differ: the other 60 levels plus `base`, `frontend`, and `loading`.
- Every one of those 63 differences is only a changed `TEXT` and/or `MESH`
  count. Tag-run topology remains equal in 300/301 pairs; `loading` is the one
  exception because Xbox appends one `TEXT` after PC's `LVLR,TARG,AYAD`.
- The six sequence-equal levels still substitute named textures. Five replace
  PC `SnowLayer` and `LandscapeLight` with Xbox rain `_splash` and
  `basicpanel`; level 700 also has PC `m_battleshipdetails2b` versus Xbox
  `m_battleshipdetails`. Sequence equality is therefore not asset identity.

Across paired top-level `TEXT`/`MESH` resources there are 255 PC-only
occurrences over 20 keys and 140 Xbox-only occurrences over 25 keys. The
dominant selection facts are PC `SnowLayer` and `LandscapeLight` (66 each),
Xbox rain `_splash` (66), PC `f_samb` and two hanger-top textures (20 each),
and the 17-pair battleship-detail substitution. Pinned source independently
marks `LandscapeLight` as `RES_NOTONXBOX` in
`references/Onslaught/engine.cpp:209-224`; the other names remain selection
facts, not explanations of rendered behavior.

## Tag aggregate

Payload-byte counts exclude top-level headers. Equality is counted after a
within-resource logical join: validated serialized name for `TEXT`/`MESH`, and
tag plus occurrence for other families.

| Tag | PC / Xbox chunks | Logical joins | PC / Xbox only | Same size | Exact payload | PC / Xbox payload bytes |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `AYAD` | 301 / 301 | 301 | 0 / 0 | 301 | 0 | 7,224 / 7,224 |
| `DMKR` | 1 / 1 | 1 | 0 / 0 | 1 | 0 | 5,465 / 5,465 |
| `ERES` | 66 / 66 | 66 | 0 / 0 | 66 | 0 | 151,068,207 / 151,068,207 |
| `GDIE` | 232 / 232 | 232 | 0 / 0 | 38 | 38 | 136,605 / 211,710,264 |
| `IMPS` | 66 / 66 | 66 | 0 / 0 | 0 | 0 | 608,320 / 16,456,400 |
| `LNDS` | 66 / 66 | 66 | 0 / 0 | 66 | 66 | 0 / 0 |
| `LVLR` | 301 / 301 | 301 | 0 / 0 | 301 | 301 | 1,204 / 1,204 |
| `MESH` | 3,492 / 3,494 | 3,482 | 10 / 12 | 0 | 0 | 35,097,912 / 532,758,036 |
| `PLAT` | 1 / 1 | 1 | 0 / 0 | 0 | 0 | 19,424 / 1,854,464 |
| `PMIB` | 1 / 1 | 1 | 0 / 0 | 0 | 0 | 8,340 / 7,796 |
| `SSHD` | 66 / 66 | 66 | 0 / 0 | 27 | 4 | 28,378,824 / 29,853,032 |
| `SURF` | 66 / 66 | 66 | 0 / 0 | 50 | 0 | 1,472,400 / 1,473,552 |
| `TARG` | 301 / 301 | 301 | 0 / 0 | 301 | 0 | 1,204 / 1,204 |
| `TEXT` | 18,857 / 18,740 | 18,612 | 245 / 128 | 0 | 0 | 7,015,488 / 670,830,700 |
| `VSDS` | 1 / 1 | 1 | 0 / 0 | 0 | 0 | 167,500 / 205,655 |
| `WRES` | 66 / 66 | 66 | 0 / 0 | 47 | 46 | 7,667,110 / 7,690,520 |

`LVLR` is 103 everywhere. `TARG` is uniformly 1 on PC and 2 on Xbox. `AYAD`
is PC `(344,372,316,5084,92,1)` versus Xbox
`(344,372,320,5084,92,1)`. Pinned source identifies these as version, target,
and the six ABI/static-shadow guard fields in
`references/Onslaught/ResourceAccumulator.cpp:43-53,324-347`; only
`CMeshPart` differs in the measured guard, 316 versus 320 bytes.

`WRES` gives the strongest next field join: 46/66 are exact, level 611 alone is
same-size/different-payload, and 19 change size. `ERES` is equal-size but
different in all 66. `SURF` has 50 equal-size pairs and no exact payload.
Equal length is alignment evidence, never content equality.

## Texture, mesh, and goodie implications

Every `TEXT` payload on both sides passed a full-coverage `DXTX` wrapper
followed by `CTEX`, with its logical name at payload offset `0x18`. Every
`MESH` passed `PMSH`; PC adds a full-coverage `PMS2` wrapper and stores the name
at `0x10`, while Xbox stores it directly at `0x08`. This yields 18,612 `TEXT`
and 3,482 `MESH` joins.
The comparator labels 1,056 duplicate-name `TEXT` joins as ordered duplicates;
53 mesh joins per platform have an explicit empty name.

No joined `TEXT` or `MESH` top-level payload has equal size or bytes. Source
shows target-specific resource flags, texture-memory/mipmap decisions, and
serialization in `ResourceAccumulator.cpp:351-582`. These facts establish
different storage forms. Without decoded dimensions, formats, mip extents,
pixels, and mesh buffers, they establish nothing about visual quality.

Xbox-only `goodie_232` is a fully accounted 80-byte AYA with
`LVLR,TARG,AYAD,GDIE`. Its raw SHA-256 is
`f8c054abff14e7cb16d49d001dd69f6b1c5ac593963fef7991dcca744333bc63`;
`GDIE` is exactly `GDAT`, size 8, number 232, type 2. Pinned source labels type
2 `GT_FMV` and maps 232 to `cutscenes\33`
(`FEPGoodies.h:11-18`; `FEPGoodies.cpp:801-836,952-968,1004-1148`). The marker
does not prove gallery enumeration, unlock behavior, media presence, or a
visible Xbox-exclusive feature.

## Next falsifiers

1. Parse joined `TEXT` fields through dimensions, format, mip table, and
   decoded pixel hashes before making any fidelity claim.
2. Normalize the PC `PMS2` and Xbox direct-`PMSH` mesh forms into named
   material, part, hierarchy, index, vertex, and buffer-hash rows.
3. Use the 46 exact `WRES` pairs as controls, then field-diff level 611 before
   the 19 size-changing cases; use the four exact `SSHD` pairs similarly.
4. Fully account nested `GDIE` and `IMPS` tags before interpreting their large
   platform size differences.
5. Test goodie 232 independently at the catalog, unlock, and media boundaries.

The reusable comparator and its synthetic tests contain no retail bytes. No
live Ghidra operation contributed to this finding.
