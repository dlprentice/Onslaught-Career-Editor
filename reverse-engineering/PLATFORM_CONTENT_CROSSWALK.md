# Platform content crosswalk: PC, Xbox, and PS2

Status: active, bounded platform/content finding
Date: 2026-08-22
Summary: PS2's six canonical language tables are byte-identical to PC, all three
platforms carry the same 43 mission titles, and the English character profiles
agree; the PS2 resource-name set differs from the shared PC/Xbox 66-world set.
Evidence: MEASURED — complete v3 decode of eighteen PC/Xbox/PS2 language tables,
SHA-256 of all 18 Xbox regional language members, streamed SHA-256 of both PS2
retail ISOs and all six regional RCDF package instances, complete PC/Xbox/PS2
numeric-resource basename censuses, and page-image inspection of the PS2 USA
manual.
Specimen: pristine PC language tables headed by English SHA-256
`789ecff619d077092769df281c540d138a25fcc74d70023466a604888e59371a`;
Xbox Europe/Korea/USA extracted-game ZIP members; PS2 Europe/USA inner ISOs
SHA-256 `060d883b…9da52` / `3e1fffa9…7ce6`; PS2 USA text PDF SHA-256
`cc4b1e0fc79517ac55f21a0fdf2be17c20d7bb878c413b7bd72c641798163ccb`.
Verdict: the 43-title and six-language PC tables are exact authored data inside
both PS2 retail regions, while Xbox retains a 34-ID subset and PS2's numeric
resource set contains `000` and `888` where the PC/Xbox set instead contains
`201`.

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

For PS2, the pass parsed the ISO9660 primary volume descriptor and root, hashed
each `DATA*.NYO` extent, then parsed the package's `RCDF` header and tail index.
The index is exact and self-bounding: a count followed by 264-byte
path/offset/size rows. Only the six canonical `\data\language\*.dat` members
were extracted into ignored local-lab and decoded. Other payload formats stayed
unopened; their paths, sizes, package hashes, and index hashes remain exact.

The original PC/Xbox/manual receipt is
[`platform-content-crosswalk-2026-08-22.tsv`](platform-content-crosswalk-2026-08-22.tsv).
The 13-row PS2 package/member receipt is
[`ps2-packed-content-parity-2026-08-22.tsv`](ps2-packed-content-parity-2026-08-22.tsv).
Raw decoded strings, extracted language members, RCDF indexes, and the page
render remain ignored under `local-lab/platform-content-crosswalk-2026-08-22/`
and `local-lab/ps2-packed-content-parity-2026-08-22/`.

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

The two PS2-only rows are exact index facts:

- `\data\Resources\000_res_PS2.aya`, 11,432,464 bytes, package offset
  1,666,965,504;
- `\data\Resources\888_res_PS2.aya`, 17,638,345 bytes, package offset
  329,324,544.

Their purpose and runtime reach are unknown. Presence is not a career-node,
unlock, or exclusive-content claim, and absence of `201_res_PS2.aya` does not
prove that PS2 lacks the corresponding authored scenario under another route.

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
- The PC/PS2 table's 34 extra frontend IDs relative to Xbox must not inflate the
  mission, character, or lore denominator.

## Open boundaries and falsifiers

- The six PS2 canonical language members were decoded, but runtime
  language-selection reach was not traced. The other 4,154 RCDF index rows were
  classified by path/size only; their payload formats remain unopened.
- The purpose and reachability of PS2 resource IDs `000` and `888`, and the
  routing of PC/Xbox `201` on PS2, remain open.
- PS2 CHD-to-ISO equivalence remains open; this pass uses the already-anchored
  inner ISOs only.
- Xbox Korea versus USA content equality outside the 18 language members and
  already hashed exception set remains at the ZIP CRC triage boundary described
  in `BUILD_AND_DUMP_MATRIX.md`.
- The five English content-facing edits need source chronology or a design
  reference before one wording can be called later, corrected, or canonical.
- Language-table equality does not imply voice-file or video-stream equality.
