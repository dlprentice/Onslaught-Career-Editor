# Platform content crosswalk: PC, Xbox, and PS2

Status: active, bounded platform/content finding
Date: 2026-08-22
Summary: PS2's six canonical language tables are byte-identical to PC, all three
platforms carry the same 43 mission titles, and the English character profiles
agree; PS2-only `000` and `888` and PC/Xbox-only `201` are three distinct world
containers rather than sentinels, global/default files, or packaging aliases.
Evidence: MEASURED — complete v3 decode of eighteen PC/Xbox/PS2 language tables,
SHA-256 of all 18 Xbox regional language members, streamed SHA-256 of both PS2
retail ISOs and all six regional RCDF package instances, complete PC/Xbox/PS2
numeric-resource basename censuses, strict AYA/WRES world-identity parses for
`000`/`888`/`201`, complete logical-name comparison against the 302-member Xbox
AYA shelf, byte-exact `worldheaders.dat` replay, loose-script manifests, and
page-image inspection of the PS2 USA manual.
Specimen: pristine PC language tables headed by English SHA-256
`789ecff619d077092769df281c540d138a25fcc74d70023466a604888e59371a`;
Xbox Europe/Korea/USA extracted-game ZIP members; PS2 Europe/USA inner ISOs
SHA-256 `060d883b…9da52` / `3e1fffa9…7ce6`; PS2 USA text PDF SHA-256
`cc4b1e0fc79517ac55f21a0fdf2be17c20d7bb878c413b7bd72c641798163ccb`.
Verdict: the 43-title and six-language PC tables are exact authored data inside
both PS2 retail regions, while Xbox retains a 34-ID subset. PS2 `000` is a real
mode-0 world-0 container of still-unknown purpose; PS2 `888` is a real mode-2
multiplayer world; PC/Xbox `201` is a real mode-0 world absent from PS2's numeric
resource shelf. None is an alias for another member of this three-ID family.

## Scope and method

This pass asks which authored mission, world, faction, and character surfaces
are shared across released platforms, and uses only as much container work as
is needed to reach those metadata rows.

The inputs were read-only:

- all six pristine PC retail `data/language/*.dat` files;
- the six corresponding members inside each Xbox Europe, Korea, and USA
  extracted-game ZIP under `G:\BEA ROMS`;
- the already-anchored PS2 Europe and USA retail ISO members under
  `G:\BEA ROMS`, streamed from ZIP without mounting or executing them;
- the installed PC English manual HTML; and
- the PS2 USA manual's 2,412,322-byte text PDF in the read-only archive.

Every language table was decoded as the documented v3 layout. Comparison used
numeric text ID, UTF-16 text, and audio-name fields independently. Token names
came from the 2,571-row `text.stf` after signed decimal IDs were normalized to
unsigned 32-bit values. That last step is deliberately independent of the
known unsigned-only regex bug in `tools/language_dat_decode.py`; this result does
not close that tool bug.

For PS2, the language-table pass parsed the ISO9660 primary volume descriptor
and root, hashed each `DATA*.NYO` extent, then parsed the package's `RCDF` header
and tail index.
The index is exact and self-bounding: a count followed by 264-byte
path/offset/size rows. At that stage only the six canonical
`\data\language\*.dat` members were extracted into ignored local-lab and
decoded; the later bounded world-role follow-up is described below.

The original PC/Xbox/manual receipt is
[`platform-content-crosswalk-2026-08-22.tsv`](platform-content-crosswalk-2026-08-22.tsv).
The 13-row PS2 package/member receipt is
[`ps2-packed-content-parity-2026-08-22.tsv`](ps2-packed-content-parity-2026-08-22.tsv).
The six-row no-payload world-role receipt is
[`resource-id-roles-000-888-201-2026-08-22.tsv`](resource-id-roles-000-888-201-2026-08-22.tsv).
Raw decoded strings, extracted language members, RCDF indexes, and the page
render remain ignored under `local-lab/platform-content-crosswalk-2026-08-22/`
and `local-lab/ps2-packed-content-parity-2026-08-22/`. The extracted `000`/`888`
members, strict chunk observations, Xbox comparison rows, and script manifests
remain ignored under `local-lab/resource-id-roles-2026-08-22/`.

The world-role follow-up re-streamed and re-hashed the complete PS2 USA ISO,
extracted only the two bounded numeric members, admitted every byte through the
strict raw-tag-stream parser, and then parsed `WRES -> WRLD -> WDAT/RLWD`. It
also decoded PC and Xbox `201` through their explicit envelopes, compared the
PS2 logical texture/mesh names against every AYA member in the Xbox USA ZIP,
round-tripped the 4,783-byte PC `worldheaders.dat`, and hashed the three matching
loose MissionScripts directories. Logical-name overlap is only a refuter here;
the nested world IDs, header fields, modes, and script counts carry the identity
finding.

## Language-table result

Each PC table has 2,571 unique IDs. Each PS2 canonical table is byte-identical
to its PC counterpart, including all 2,571 IDs, text, and audio-name metadata.
Each Xbox table has 2,537 IDs. For every language, all 2,537 Xbox IDs occur in
PC/PS2, PC/PS2 have exactly 34 additional IDs, and Xbox has none they lack.
The table below therefore compares the identical PC/PS2 rows against Xbox.

| Language | PC/Xbox shared IDs | PC/PS2-only vs Xbox | Shared text differences | Shared audio-name differences | Mission titles different | Character-profile rows different |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| American | 2,537 | 34 | 38 | 0 | 0 of 43 | 2 of 96 |
| English | 2,537 | 34 | 30 | 0 | 0 of 43 | 0 of 96 |
| French | 2,537 | 34 | 51 | 0 | 0 of 43 | 0 of 96 |
| German | 2,537 | 34 | 68 | 0 | 0 of 43 | 1 of 96 |
| Italian | 2,537 | 34 | 42 | 0 | 0 of 43 | 0 of 96 |
| Spanish | 2,537 | 34 | 47 | 0 | 0 of 43 | 0 of 96 |

All 18 Xbox regional language members are byte-identical by SHA-256 within
language: Europe, Korea, and USA carry the same American, English, French,
German, Italian, and Spanish tables. This strengthens the earlier
[`BUILD_AND_DUMP_MATRIX.md`](BUILD_AND_DUMP_MATRIX.md) sample, which pinned only
American and English.

The 34 PC/PS2-only names relative to Xbox are frontend/control/memory-card
vocabulary. They include controller-layout labels and PS2-named memory-card
strings retained in the later PC table. Their presence is evidence of a strict
ID superset, not 34 extra missions or story beats. The exact PS2 bytes show that
this superset predates the PC port rather than originating in it.

All 607 audio-bearing IDs keep the same audio identifier across PC, PS2, and
Xbox for all six languages. This establishes metadata identity only; it is not
a claim that the encoded audio files are byte-identical across platforms.

## Mission identity

Every language contains the same 43 mission-shaped rows (`N.NN - title`) on PC,
PS2, and Xbox. PS2 is byte-identical to PC; Xbox matches all 43 codes and titles
despite its smaller table. There are no platform-only mission-title rows. This
is stronger than matching the campaign graph: it proves the authored title
surface as well as the 43-code set. Runtime language selection was not traced.

English PC/PS2 versus Xbox still has 30 non-identical shared rows. Twenty-five
are platform UI, controller, or memory-device text. The five content-facing
rows are one `BRIEFING_211_1` edit and four `GOODIE_TEXT_*` edits. Their bounded
word-level deltas are small (`in`/`an`, `03`/`02`, `no`/`now`, one deleted word, and the
`Arachnadrones`/`Arachadrones` spelling), but they are real authored variants.
This pass records rather than adjudicates them; no platform is silently made
canonical.

## Character profiles

The eight-profile shelf used by [`characters.md`](../lore/characters.md) spans
96 named fields. All 96 rows in every PS2 canonical language table are exact PC
bytes. Xbox English, French, Italian, and Spanish are also text-identical.
Xbox American differs in `GOODIE_TEXT_3_HAIR` and `GOODIE_TEXT_7_TEXT2`; Xbox
German differs in `GOODIE_TEXT_8_TEXT2`.

This settles the provenance point directly: the character shelf is in the PS2
retail package and is not a PC-port addition. It does not prove that every
profile is normally unlocked or that every locale renders every field.

## World IDs and regional resource variants

A strict basename census finds exactly the same **66** numeric resource IDs on
PC and Xbox Europe, Korea, and USA: 43 career worlds plus 23 shipped non-career
worlds. The PS2 `DATA0.NYO` index instead has **67** numeric
`*_res_PS2.aya` rows. Sixty-five IDs are shared with PC/Xbox; PS2 adds
`000` and `888`, while PC/Xbox `201` has no PS2 numeric-resource row.

The second pass resolves the container roles without inventing normal reach:

| Resource | Exact nested identity | Authored/container role | Reach boundary |
| --- | --- | --- | --- |
| PS2 `000` | 11,432,464 bytes, SHA-256 `fdd9aa99…ce058`; `WDAT=(-1,0)`; RLWD version 48, header id 0, mode field 0; configurations Blaster/Laser/Sniper/Standard; 0 compiled scripts | A real world-0 AYA with all eleven expected top-level resource families, 245 TEXT and 25 MESH chunks. It is not `base`, `Frontend`, or `Loading`: PS2 carries separate RCDF rows for all three. | Its PC loose shelf is one empty `level000/text.stf`. No normal gameplay, developer-page, or tool route is proved, so purpose remains unresolved. |
| PS2 `888` | 17,638,345 bytes, SHA-256 `a3a2f8fc…eea96`; `WDAT=(-1,888)`; RLWD version 50, header id 888, mode field 2; Standard/Laser/Blaster; 3 compiled scripts | A real multiplayer world-888 AYA. The 272 logical asset occurrences include `fenrir-multiplayer.msh` and the `f_ventura*` family; the six-file loose shelf names Fenrir, Venturer, and opposing win events. | Retail `CWorld__IsMultiplayerMode` accepts mode 1 or 2, and `CGame__IsMultiplayer` accepts levels 850..899. The normal multiplayer frontend is narrower at 850..879, so 888 is not proved normally selectable. |
| PC/Xbox `201` | PC/Xbox both carry `WDAT=(2,201)`, RLWD version 50, header id 201, mode field 0, Aquila Prototype, and 13 compiled scripts | A real world-201 container on both platforms, not a set marker. PC also installs a 16-file `level201` source shelf whose `LevelScript.msl` reuses `Level200/text.stf`. | It is absent from the 43-node career graph. The retail PC parser accepts `-level N`, but normal PC/Xbox frontend reach and PS2 routing are not proved. |

The PS2 paths remain exact RCDF facts: `000` is at package offset
1,666,965,504 and `888` at 329,324,544. Their `WRES`, world IDs, modes,
configurations, script counts, hashes, and logical-asset multisets all differ
from PC/Xbox `201`; neither has an exact `WRES` match anywhere in the complete
302-member Xbox AYA shelf. This falsifies sentinel/global/default and
three-member packaging-alias classifications. It does **not** prove that PS2
lacks the authored scenario represented by world 201 under some other route.

Presence is not cross-platform byte equality. The existing regional hash matrix
proves that Xbox Europe has different bytes for worlds 612, 856, and 863 while
Korea and USA match for those resources. It also differs in `goodie_124` and
cutscene `24.bik`. A rebuild may share campaign semantics while still selecting
platform- or region-specific assets and resource IDs.

## PS2 regional package identity

The Europe and USA ISOs are different and place the packages at different
LBAs/order, but all three package pairs are exact bytes:

| Package | Bytes | SHA-256 | RCDF index rows | Indexed role |
| --- | ---: | --- | ---: | --- |
| `DATA0.NYO` | 1,691,951,868 | `dc02e657…34f99` | 383 | language, AYA resources, small authored tables |
| `DATA1.NYO` | 1,729,442,900 | `cbc11eee…5bb4c` | 74 | M2V/PSS/video shelf |
| `DATA2.NYO` | 189,708,988 | `05e39a17…94b84` | 3,703 | VAG/MIB/MIH/audio shelf |

This closes regional identity for the packed content bytes. It does not make
the regional ELFs or ISOs equal, nor does it compare PS2 media/resource payloads
to PC or Xbox encodings.

## The shared manual foundation

The PC English manual HTML and the PS2 USA manual independently print the same
foundation used by [`world-lore.md`](../lore/world-lore.md): Allium in the
Porrum system, the Forseti and Muspell in the Ampeloprasum Archipelago, the
Sohra Treaty of 1174, Forseti territory from Forseti Major to Castellian,
Muspell territory from Iron Isle to Sentinel, and Hawk Winter's dockworker and
loader-racing premise.

The PS2 OCR sidecar misreads **Kensor** as `Rensor`. Direct inspection of the
manual page (PDF page 6, printed page 4) and its map both clearly read
**Kensor**. The OCR spelling is not a regional variant.

The manuals are authored player-facing sources. They support setting and
terminology; they do not prove internal engine behavior. American/British
spelling differences likewise do not establish divergent lore.

## Reconstruction consequences

- Mission codes and titles may be treated as one PC/PS2/Xbox content identity
  per language, but should still be read from user-supplied data rather than
  copied into the reconstruction or toolkit.
- The PC/PS2 character-profile shelf can be tested once against the shared
  96-row contract. Xbox American and German variants remain platform-sensitive.
- The numeric world-resource set is not universal: PC/Xbox have 66, PS2 has 67,
  and only 65 IDs are shared across all measured platforms.
- Preserve `000`, `888`, and `201` as separate authored world identities. Do not
  normalize the platform delta by renaming one archive to another: their nested
  world IDs, modes, configurations, script surfaces, and resource content differ.
- The PC/PS2 table's 34 extra frontend IDs relative to Xbox must not inflate the
  mission, character, or lore denominator.

## Open boundaries and falsifiers

- The six PS2 canonical language members were decoded, but runtime
  language-selection reach was not traced. Two targeted world members were then
  opened; the other 4,152 RCDF index rows remain classified by path/size only.
- `000` is proved as world 0, but its purpose and normal reach remain open.
- `888` is proved as a mode-2 multiplayer world with Fenrir/Venturer content;
  its normal frontend reach and intended shipping role remain open because the
  regular multiplayer selector stops at 879.
- PC/Xbox `201` is proved as a real mode-0 world on both platforms. Its normal
  frontend reach and the route, if any, to corresponding PS2 content remain open.
- PS2 CHD-to-ISO equivalence remains open; this pass uses the already-anchored
  inner ISOs only.
- Xbox Korea versus USA content equality outside the 18 language members and
  already hashed exception set remains at the ZIP CRC triage boundary described
  in `BUILD_AND_DUMP_MATRIX.md`.
- The five English content-facing edits need source chronology or a design
  reference before one wording can be called later, corrected, or canonical.
- Language-table equality does not imply voice-file or video-stream equality.
