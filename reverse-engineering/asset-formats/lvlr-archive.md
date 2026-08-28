# LVLR level/resource tagged-stream contract

Status: active format contract — complete outer/tag census; most payload schemas
remain owner-specific or open
Date: 2026-08-28
Verdict: all 301 streams and 23,884 top-level tags are accounted for; the
numeric WRES Unit/Feature instance join is bounded, while most other payload
schemas and world dependencies remain partial.
Evidence: MEASURED — all 301 PC mirror-index archive rows inflate to `LVLR`;
the complete earlier top-level chunk census and the exact PS2 packed-resource
census are cited below.
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

### Exact PC demo shelf

The retained 2003 PC demo ZIP (110,691,112 bytes, SHA-256
`62e3f54a25af8049491c96123409f7ee6cc02d9326f4252d84606ffc136acd47`)
contains installer cabinet `BattleEngine/All.gip` (75,388,730 bytes, SHA-256
`90b16dc8df5669bb1ed2dbd09b450c30864047c9a536ecc31bfc6aa55cb66975`).
Its complete `resources/*_res_PC.aya` shelf is exactly:

| Resource | Stored bytes | Stored SHA-256 | Top-level schedule |
| --- | ---: | --- | --- |
| `201_res_PC.aya` | 1,717,469 | `6fbe95f7b267cca19e67c9db781cb99e47479d77a96fe8e9ddb69d5131b4aad1` | `LVLR1,TARG1,AYAD1,TEXT281,MESH56,IMPS1,LNDS1,SURF1,ERES1,SSHD1,WRES1` |
| `base_res_PC.aya` | 17,931 | `0ee8530874425cac759834872f5941bc4be086c40ce6b70553b5c6b539802883` | `LVLR1,TARG1,AYAD1,TEXT4,MESH1,VSDS1,PMIB1,DMKR1,PLAT1` |
| `Frontend_res_PC.aya` | 2,152 | `a94095a5665a269276a44752dc86bf298087e24cb4bc53d43e1aa37ab87c984f` | `LVLR1,TARG1,AYAD1,TEXT105,MESH6` |
| `Loading_res_PC.aya` | 52 | `39ec57b499324a7d96e57c94801a2c5d946a109ab7bf985d7d2e1b8c770722aa` | `LVLR1,TARG1,AYAD1` |

Fresh target-specific Windows Cabinet FDI passes independently reached and
closed all four declared lengths, parsed each complete AYA in memory, and
reproduced byte identity with the same-named pristine retail archives. The demo
thus has one of 66 retail numeric resources, all three special archives, none
of the other 65 numeric resources, and none of the 232 Goodie archives. It has
no language-suffixed `Loading_res_PC_<language>.aya` despite that optional
`PLAYABLE_DEMO` source path.

The cabinet reports a later `FDIERROR_CORRUPT_CABINET` after every selected
resource has already closed. `tar.exe` likewise reports `Invalid CFDATA` and
produces same-length but hash-different output for these targets; its output is
not admitted as payload evidence. The later defective block remains open and
does not make these four exact FDI-recovered members corrupt.

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

## Canonical numeric writer topology

Every numeric archive in the named 66-file retail PC shelf has this exact
top-level run order. The retained USA Xbox census independently carries the
same topology for all 66 corresponding streams, and direct streaming of all 67
numeric members in the exact Europe/USA PS2 retail package proves it there too:

```text
LVLR, TARG, AYAD, TEXT*, MESH*, IMPS, LNDS, SURF, ERES, SSHD, WRES
```

The asterisks describe the writer grammar: each run can be empty after source
filtering, although both are nonempty in every measured numeric shelf. PC has
`TEXT` 249–319 and `MESH` 30–71; PS2 has `TEXT` 240–312 and `MESH` 25–71.
The fixed prefix geometry is `LVLR@0:size4`, `TARG@12:size4`,
`AYAD@24:size24`. Pinned
`references/Onslaught` commit `5352a81cdb838b145a57f7febc5d9fc4b0129ebb`
corroborates the PC-host builder schedule: `ResourceAccumulator.cpp:324-347`
writes the prefix, `:504-592` emits stable filtered texture then mesh runs, and
`:627-697` writes the six numeric tail owners in this order. This does not prove
that decoders require the order or that the pinned source is the exact
historical production revision.

The measured platform prefixes are:

| Named shelf | Numeric streams | Envelope | `TARG` | `AYAD` six-word tuple |
| --- | ---: | --- | ---: | --- |
| Retail PC | 66 | PC chunked/zlib; raw stream after inflation | 1 | `(344,372,316,5084,92,1)` |
| USA Xbox | 66 | raw tag stream in ZIP | 2 | differs at least at `CMeshPart=320` |
| Europe/USA PS2 | 67 | raw tag stream inside RCDF `DATA0.NYO` | 3 | `(344,372,316,5084,92,1)` |

The two exact PS2 retail ISOs carry byte-identical `DATA0.NYO` packages:
1,691,951,868 bytes, SHA-256
`dc02e657cb6e405c7228c54191d2ca37419c63b4d442a22a9a52b8ef0ab34f99`.
Its RCDF index has 383 rows and SHA-256
`25b628b06f4386f97e36bd9041a38910c8238fa1523d0c337b5e8fed51c51bb9`.
All 67 numeric member intervals were streamed and completely accounted for:
54 distinct run-count strings, 1,443,414,410 payload bytes total, no unknown
top-level tag, interleaving, missing/repeated/swapped tail, gap, overlap, or
residual member byte. Sixty-five IDs overlap the reviewed PC/Xbox set; PS2 adds
`000` and `888` and lacks `201`. This closes emitted topology only for those
exact Europe/USA retail owners; other revisions, prototypes, and the PS2 demo
remain separate specimens.

`tools/aya_archive_inventory.py --expect-numeric-schedule` makes this a
fail-closed, optional SDK/build check and reports the first unexpected tag and
inflated offset. It checks framing/order, not the platform-specific `TARG` or
`AYAD` payload values, and it does not itself open RCDF members. It is
intentionally not duplicated in the Godot asset
materializer: every archive currently admitted there already passes an exact
whole-file SHA-256 gate before inflation.

## Retail PC encounter-order loader contract

The pristine PC function at `0x004D7200–0x004D7A16` is the released outer
dispatcher, not an order-validating decoder. Its exact 2,071 bytes have SHA-256
`4922caa624a79108fbfd90b185e48367e03129b5d3694dbe201d8251807321cf`
in the named `74154bfa…7750` executable. The current specimen-bound signature is:

```text
void __cdecl CResourceAccumulator__ReadResourceFile(
    int resource_id, void *existing_buffer, int skip_optional_chunks)
```

The function loops over `CChunkReader__GetNext` and compares every encountered
FourCC independently. It has no expected-next-tag state and no repeated-run or
singleton counters. `GetNext` reads only the next eight-byte header; it does not
skip an unfinished payload. Each inline handler or subsystem delegate must
therefore consume or skip its own payload before the next iteration. The
canonical sequence above is an emitted/corpus profile, not a stream-order rule
enforced by this loader.

| Tag | Released PC outer action |
| --- | --- |
| `LVLR` | Reads and ignores one `u32`, then skips any remaining payload. |
| `TARG` | Reads and ignores one `u32`; it does not skip an extension. Canonical payload size is exactly four. |
| `AYAD` | Reads and compares five `u32` ABI guards. A mismatch only formats a stack-local message in this body; it then skips the sixth word and any extension. |
| `TEXT` | Calls `CDXTexture__Deserialize` for each occurrence. |
| `MESH` | Calls `CMesh__Deserialize` for each occurrence. |
| `IMPS` | Calls `CDXImposter__Deserialize`. |
| `LNDS` | Skips the payload on PC. |
| `SURF` | Calls `CDXSurf__CreateSurfaceArray`. |
| `ERES` | Calls `CEngine__Deserialize`. |
| `SSHD` | Calls `CStaticShadows__LoadAll`. |
| `WRES` | Calls `CWorld__DeserializeWorld`. |

The complete comparison-chain vocabulary is
`LVLR,TARG,AYAD,MESH,TEXT,ERES,WRES,IMPS,LNDS,VSDS,PLAT,SURF,SSHD,PMIB,DMKR,GDIE`.
That comparison order is implementation structure, not required stream order.
The five non-numeric delegates are `VSDS -> CVertexShader__DeserializeAll`,
`PLAT -> PCPlatform__DeserializeFontsAndAssets`,
`PMIB -> CDXPatch__LoadFromFile`, `DMKR -> CDamage__CreateTextureBuffer`, and
`GDIE -> CFEPGoodies__Deserialise`; unknown tags are traced and skipped.

When `skip_optional_chunks` is nonzero, the prefix and every `MESH` still run,
while all other payloads are skipped. All four enumerated direct callers pass
zero: shell/base at `0x004EFF20`, front end at `0x004687F8`, game level at
`0x0046CD87`, and Goodies at `0x0045CC86`. `resource_id == -3` returns after its
status/trace path without opening `Loading_res_PC.aya`, and no direct `-3`
caller is present. At the loop boundary, zero from `GetNext` can mean clean EOF
or a short final tag/size read, so this function does not distinguish those two
conditions.

Pinned `ResourceAccumulator.cpp:732-1055` proves lineage but differs from the
release body: it has two arguments, continues for `-3`, asserts `LVLR`, `TARG`,
and `AYAD` guards, tests `TEXT` before `MESH`, and skips `VSDS` in its PC branch.
Retail PC has the third skip gate, the early `-3` return, ignores `LVLR/TARG`,
only formats local `AYAD` mismatch text, tests `MESH` before that gate, and
deserializes `VSDS`. Both are encounter-order dispatchers and both skip `LNDS`
on PC. The mapped PC demo body is a normalized-instruction twin of this retail
function, and the exact four-member demo archive shelf is now independently
censused above.

## Cross-platform filename and materialization routing

Pinned `ResourceAccumulator.cpp:158-205` (SHA-256
`4f78480aeb6caae9854295ae09a9b322a7a83264da3f3e19a95723505414f1b2`)
defines one five-way filename grammar, reproduced by PC retail/demo, both mapped
Xbox retail families, and all three PS2 executables:

| Resource ID | Relative filename |
| ---: | --- |
| `-1` | `data\\Resources\\base_res_<TARGET>.aya` |
| `-2` | `data\\Resources\\Frontend_res_<TARGET>.aya` |
| `-3` | `data\\Resources\\Loading_res_<TARGET>.aya`, or `_LANGUAGE.aya` only while both playable-demo and pause-for-controls are nonzero |
| `>=0` | `data\\Resources\\%03d_res_<TARGET>.aya` |
| every other negative | `data\\Resources\\goodie_%02d_res_<TARGET>.aya`, where the displayed value is `-id-1000` |

The widths are minimums, not truncation. PC retail constructor
`[0x004D6F70,0x004D71F3)` is 643 bytes with SHA-256
`951264ec345f5e717635317c0a64c84f8455f156cb619a618fec957df97165b8`;
its PC demo twin has SHA-256
`d88028e51b573bf3de17d5f86c95f79e67b54fa08efbc45194db592e23381e10`.
Three 328-byte PS2 constructors normalize word-for-word, and the Xbox
constructors retain the same branch and format topology.

Construction does not imply loading. PC retail/demo and PS2 demo/EU/US return
on `-3` before the constructor and have zero direct `-3` loader callers. Xbox
EU/KR/US/Issue11 do not return: each has 14 direct loader calls, ten of them
literal `(-3, null)`. The USA loader `[0x000D6760,0x000D7180)` is 2,592 bytes
with SHA-256
`e8ce0b00a8c4e6cdd6df17f459cef9ad7e64ed7eb09e9e7e7c81bfabcdc0f05e`;
its `-3` arm rejoins the filename constructor at `0x000D67FF`.

For normal Xbox `-1`, `-2`, and non-localized `-3` routes, the loader prepends
the `CLIPARAMS` base path, substitutes `Z:` for the archive open, temporarily
substitutes `D:` for `CacheFile`, then restores and opens the `Z:` path. Numeric,
Goodie, and localized-loading routes remain relative. Retail Xbox fixes the
playable-demo flag at zero and therefore emits only the normal loading name;
Issue11 enables the flag and contains normal plus `_0` through `_4` names, but
still requires the pause-for-controls state to select a localized name.

PS2 keeps the page-file roles distinct: a nonnegative level ID derives and
opens a sibling `.apf`, while every materialized route lazily opens the shared
`data\\resources\\pagefile.mpf`. A base `.apf` may exist on disc, but the
released reader does not open it for `-1`. The pure
[`resolve_released_resource_route`](../../tools/aya_archive_inventory.py)
helper preserves these released routing decisions without touching retail
material.

## Released PS2 encounter-order loader contract

The PS2 demo, Europe retail, and USA retail executables each contain one exact
2,000-byte `CResourceAccumulator::ReadResources` correspondent. All three were
streamed from their retained ISO owners and independently rehashed:

| Build | Executable SHA-256 | Loader VA | Raw body SHA-256 |
| --- | --- | --- | --- |
| Demo | `5700b5d0b39554e49afe65e079ad8109fe6688c2aa5e6f0e0ed5afcefd034584` | `[0x002812D8,0x00281AA8)` | `5d850c58d7a567885cccca3ef334d14381ea98cbcdee66bbe3c9680403840a371` |
| Europe | `87cb89b020cf107b3ba4612ac6bc86ed3fcbd6dd985e2cd3978bf897be96b655` | `[0x00281398,0x00281B68)` | `b864394f6ab260db3831f5ecbce8880a6f5de393c4d699e200515c81e71638395` |
| USA | `4cfed76f0b0cdf84377a4d5b1613fd197c27be9a3814743590fecba22ba4e166` | `[0x00281B00,0x002822D0)` | `ee0126daaf2e124b31b5fdfc70bced0746417cbf44be557e11fdcec7d451ee43b` |

Zeroing only MIPS J/JAL target fields and non-SPECIAL/non-SPECIAL2 immediate
fields produces the same normalized SHA-256 for all three bodies:
`8086754d135957b43baf6924b4490b5035b62fec6eddda62610077c3aa05ce87`.
The released ABI is the source-correlated static
`ReadResources(int32 level, CPS2MemBuffer *optional_buffer)`: `$a0` is the
signed resource ID, `$a1` is nullable, callers consume no return, and there is
no PC-style third `skip_optional_chunks` argument.

All three release bodies return immediately for `level == -3` after emitting
the loading status/trace but before filename allocation or archive/pagefile
opening. The surviving source has only a commented return there. An exhaustive
direct-JAL census finds exactly five caller roles in every build: synchronous
Goodie load, asynchronous Goodie-buffer completion, front end `-2`, game-level
load, and startup/base `-1`; none passes `-3`.

For every other ID, PS2 builds the target-3 resource filename and manages two
paging handles before constructing the chunk reader. A nonnegative level closes
the previous APF handle, changes the AYA suffix to `.apf`, opens that per-level
pagefile, and records the AYA name. Every non-`-3` call lazily opens
`data\\resources\\pagefile.mpf` when its master handle is negative. APF/MPF
open failure is traced and loading continues; this body establishes the handles
but does not read or normally close the master pagefile.

### PS2 texture page transport

The downstream consumer is now closed. Each `TEXT/P2TX/TEXD/TFRM/TMIP/PAGE`
mip stores one encoded `u32`: bit zero selects the process-lifetime master MPF
when set and the current numeric-resource APF when clear; the remaining bits
are the byte offset. Page-in reads exactly
`16 * ceil(width * height / 16)` bytes. Palettes remain inline in AYA `8PAL`,
and model geometry/material bindings remain in AYA `MESH`; the complete paging
static xref census reaches only this texture-mip page-in path.

All measured released words choose the master: 284/284 in the PS2 demo's base
and `201` archives, and 18,955/18,955 in retail base plus 67 numeric archives.
Retail Europe/USA ship no APFs. Their single byte-identical
`pagefile.mpf` is 39,073,280 bytes, SHA-256
`38d118daa95f5ee5e7a0ab92795e5a74318f181243a78901fa9606bc78df59b3`;
872 unique referenced intervals tile its entire byte range with no gap,
overlap, or unreferenced byte. The remaining 18,083 PAGE occurrences alias one
of those intervals.

The demo does ship base and `201` APFs, each beginning with an empty top-level
`PAGE` followed by `TBLK { IDNT, TEX8, FXUP }` blocks. Concatenating all 284
`TEX8` payloads in base-then-201 block order reproduces its 14,507,264-byte MPF
byte-for-byte (SHA-256
`e446faa1712b07f2a0a2bcced144bbbb3dfdcabf073d98dde8198437cf36289f`).
Each `FXUP` identifies the corresponding AYA PAGE-word offset, and every word
equals the concatenated MPF offset with bit zero set. This proves the build
fixup relation while leaving the historical packer executable/name open.

The low-bit-clear APF path remains real released code but is data-dormant in
the complete measured population. Missing APF/MPF opens are initially soft;
a later selected page read has no second valid-handle guard. The pure
[`resolve_ps2_texture_page`](../../tools/aya_archive_inventory.py) helper now
resolves either branch with released selector/offset/length arithmetic and
fails closed on missing or out-of-bounds local inputs. It is an asset-preparation
boundary, not a reason to put PS2 disc handles or page-pool scheduling into the
PC-based deterministic rebuild.

The same tool now owns the inverse offline build seam as `merge_ps2_apfs`.
Given an explicit ordered sequence of APF/sibling-AYA byte pairs, it strictly
requires `PAGE(0), TBLK { IDNT(144), TEX8, FXUP(4) }`, appends `TEX8` without
padding, and writes `cursor | 1` only into copied AYAs at verified `PAGE(4)`
payloads. Duplicate case-folded `(texture name, mip)` keys fail closed because
the historical conflict rule is not recovered; differently named identical
payloads remain distinct. A direct in-memory replay over the exact demo base
then `201` members produced 284 blocks / 115 names / 284 keys and reproduced
all 14,507,264 shipped MPF bytes plus both already-patched AYAs exactly, with
SHA-256 `e446faa1712b07f2a0a2bcced144bbbb3dfdcabf073d98dde8198437cf36289f`.
Retail's measured base-then-numeric-ascending first-seen profile remains
corpus evidence rather than a permissive packer mode.

The complete recognized-tag action table is:

| Tag | Released PS2 action |
| --- | --- |
| `LVLR` | Read one u32, ignore it, then skip the remainder. |
| `TARG` | Read one u32 and ignore it; do not skip trailing payload. |
| `AYAD` | Read five u32 values, perform the nonfatal checks below, then skip. |
| `TEXT` / `MESH` | Deserialize one encountered texture / mesh. |
| `ERES` / `WRES` / `IMPS` | Deserialize engine / world / PS2-imposter data. |
| `LNDS` | Deserialize through the engine landscape owner; unlike PC, do not skip. |
| `VSDS` / `PMIB` | Skip the remaining payload. |
| `PLAT` / `SURF` / `SSHD` | Deserialize PS2 platform / surface / static-shadow data. |
| `DMKR` / `GDIE` | Deserialize landscape damage / front-end Goodie data. |
| other | Trace the FourCC, skip its payload, and continue. |

This chain restarts for every chunk. It has no phase, seen-tag set, duplicate
guard, or singleton counter: recognized tags execute in stream encounter order.
`TARG` is the one prefix arm that does not skip after its four-byte read, so a
larger malformed payload would desynchronize the next header even though every
canonical PS2 archive uses four bytes.

Released PS2 prefix enforcement is weaker than the source assertions. `LVLR`
and `TARG` are never compared. `AYAD[0]` and `[4]` are ignored; `[1]` is compared
with 372, aligned `[2]` with 320, and `[3]` with 5084. A mismatch only formats a
diagnostic into a stack buffer and continues because the source `SASSERT` has
no release instruction counterpart. The 67 measured retail PS2 numeric members
use `LVLR=103`, `TARG=3`, and `AYAD=(344,372,316,5084,92,1)`.

The three corresponding `CChunkReader::GetNext`, `Read`, and `Skip` families
are also normalized twins. `GetNext` returns zero for clean EOF, a one-to-three
byte tag, or a short four-byte size read, and the loader then takes its ordinary
success cleanup path. `Read` increments `ReadSinceChunk` before the underlying
read and returns exact-length equality; the source bounds assertion is absent.
`Skip` computes unsigned `Size-ReadSinceChunk` without guarding underflow.
Delegate-level short-read behavior, malformed-skip response, and semantic
safety of arbitrary reordered chunks remain open.

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
  proves numeric-archive membership. The dedicated
  [WRES instance join](wres-instance-join.md) then closes 4,090 type-8/type-35
  definition records through physics mesh fields to one named row and one loose
  CMSH each. The 53 empty rows each own an anonymous embedded CMSH but retain no
  exact WRES/name key. The seven additional all-LVLR `MESH` rows are in Goodie
  archives.
- Level 100/base/frontend retain deeper owner-specific work. All 66 numeric
  worlds now have the bounded WRES Unit/Feature slice above; their remaining
  record families and dependencies are primarily structural inventory.

## Retail decoder anchors

No single function has been proved as the complete `LVLR` decoder. Static routes
that consume the same tagged-resource family are:

| VA | Identity | Demonstrated boundary |
| --- | --- | --- |
| `0x004D6F70` | `CResourceAccumulator__GetResourceFilename` | Builds the resource filename selected by the accumulator path. |
| `0x004D7200` | `CResourceAccumulator__ReadResourceFile` | Encounter-order outer dispatcher for 16 FourCCs; routes each occurrence to its inline/subsystem owner and does not enforce the canonical writer order. |
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
[`tools/cmsh_animation_usage_census.py`](../../tools/cmsh_animation_usage_census.py)
adds the guarded WRES/physics/named-MESH/loose-CMSH join and structurally parses
the 53 direct anonymous `PMS2+309` bodies without naming them.

## Open questions and falsifiers

- Build a per-tag-instance ledger of offsets, lengths, schemas, opaque ranges,
  references, and exact consumer VAs for all 23,884 chunks.
- Close the non-Unit/Feature WRES records, component/dynamic-spawn ownership,
  packed mission/object representation, and packed-versus-loose precedence.
- Join every world to meshes, textures, physics, scripts, audio, localization,
  videos, and Goodie/career state.
- Trace one non-Level-100 world with a different tag shape before generalizing
  Level-100 field meanings.
- Test malformed lengths only in a disposable copied profile; never edit the
  pristine archive shelf.

## Claim boundary

The 301-file retail PC population, exact four-file PC demo shelf, AYA framing,
canonical PC/Xbox/PS2 numeric writer profile for the exact named retail
shelves, released-PC outer dispatch contract, top-level geometry, 4,090 numeric
WRES Unit/Feature joins, and 53 anonymous embedded CMSH bodies are settled.
General LVLR field semantics, other WRES/object dependencies, anonymous body
names, runtime subsystem effects, delegate-level short reads, unmeasured
PS2/prototype shelves, and parity are open.
