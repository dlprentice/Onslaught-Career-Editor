# Platform content crosswalk: PC, Xbox, and the PS2 manual

Status: active, bounded platform/content finding
Date: 2026-08-22
Summary: the PC and Xbox releases carry the same 43 mission titles in all six
languages, the same 66 numeric world IDs, and byte-equal English character
profiles; small platform/editorial variants and the still-packed PS2 data shelf
remain explicit.
Evidence: MEASURED — complete v3 decode of twelve PC/Xbox language tables,
SHA-256 of all 18 Xbox regional language members, complete Xbox numeric-resource
basename census, and page-image inspection of the PS2 USA manual.
Specimen: pristine PC language tables headed by English SHA-256
`789ecff619d077092769df281c540d138a25fcc74d70023466a604888e59371a`;
Xbox Europe/Korea/USA extracted-game ZIP members; PS2 USA text PDF SHA-256
`cc4b1e0fc79517ac55f21a0fdf2be17c20d7bb878c413b7bd72c641798163ccb`.
Verdict: mission identity and English character-profile prose are not PC-only,
but equal IDs do not make platform resource payloads equal and this pass does
not decode the PS2 retail data package.

## Scope and method

This pass asks a content question, not a container question: which authored
mission, world, faction, and character surfaces are shared across released
platforms, and where do the measured bytes stop agreeing?

The inputs were read-only:

- all six pristine PC retail `data/language/*.dat` files;
- the six corresponding members inside each Xbox Europe, Korea, and USA
  extracted-game ZIP under `G:\BEA ROMS`;
- the installed PC English manual HTML; and
- the PS2 USA manual's 2,412,322-byte text PDF in the read-only archive.

Every language table was decoded as the documented v3 layout. Comparison used
numeric text ID, UTF-16 text, and audio-name fields independently. Token names
came from the 2,571-row `text.stf` after signed decimal IDs were normalized to
unsigned 32-bit values. That last step is deliberately independent of the
known unsigned-only regex bug in `tools/language_dat_decode.py`; this result does
not close that tool bug.

The complete compact receipt is
[`platform-content-crosswalk-2026-08-22.tsv`](platform-content-crosswalk-2026-08-22.tsv).
Raw decoded strings, archive payloads, and the page render remain ignored under
`local-lab/platform-content-crosswalk-2026-08-22/`.

## Language-table result

Each PC table has 2,571 unique IDs. Each Xbox table has 2,537. For every
language, all 2,537 Xbox IDs occur in PC, PC has exactly 34 additional IDs, and
Xbox has none that PC lacks.

| Language | Shared IDs | PC-only | Shared text differences | Shared audio-name differences | Mission titles different | Character-profile rows different |
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

The 34 PC-only names are frontend/control/memory-card vocabulary. They include
controller-layout labels and PS2-named memory-card strings retained in the later
PC table. Their presence is evidence of a strict ID superset, not 34 extra
missions or story beats.

All 607 audio-bearing IDs keep the same audio identifier in PC and Xbox for all
six languages. This establishes metadata identity only; it is not a claim that
the encoded audio files are byte-identical across platforms.

## Mission identity

Every language contains the same 43 mission-shaped rows (`N.NN - title`) on PC
and Xbox. Within each language, all 43 codes and titles are exact text matches;
there are no PC-only or Xbox-only mission-title rows. This is stronger than
matching the campaign graph: it proves the player-facing title surface as well
as the 43-code set.

English still has 30 non-identical shared rows. Twenty-five are platform UI,
controller, or memory-device text. The five content-facing rows are one
`BRIEFING_211_1` edit and four `GOODIE_TEXT_*` edits. Their bounded word-level
deltas are small (`in`/`an`, `03`/`02`, `no`/`now`, one deleted word, and the
`Arachnadrones`/`Arachadrones` spelling), but they are real authored variants.
This pass records rather than adjudicates them; no platform is silently made
canonical.

## Character profiles

The eight-profile shelf used by [`characters.md`](../lore/characters.md) spans
96 named fields. All 96 English rows are present and text-identical between PC
and Xbox. The same is true in French, Italian, and Spanish. American differs in
`GOODIE_TEXT_3_HAIR` and `GOODIE_TEXT_7_TEXT2`; German differs in
`GOODIE_TEXT_8_TEXT2`.

This settles one narrow provenance point: the English character profiles are
not a PC-port addition. It does not prove that every profile is normally
unlocked, that every locale renders every field, or that the PS2 data package
contains identical rows.

## World IDs and regional resource variants

A strict basename census finds exactly the same **66** numeric
`*_res_xbox.aya` IDs in Xbox Europe, Korea, and USA. The set exactly matches the
66 pristine-PC numeric resource IDs already listed in
[`lore/worlds.md`](../lore/worlds.md): 43 career worlds plus 23 shipped
non-career worlds.

Presence is not byte equality. The existing regional hash matrix proves that
Xbox Europe has different bytes for worlds 612, 856, and 863 while Korea and
USA match for those resources. It also differs in `goodie_124` and cutscene
`24.bik`. A rebuild may share world identity and campaign semantics while still
selecting platform/region-specific assets.

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

- Mission codes and titles may be treated as one PC/Xbox content identity per
  language, but should still be read from user-supplied data rather than copied
  into the reconstruction or toolkit.
- The English character-profile shelf can be tested once against the shared
  PC/Xbox 96-row contract. Localized American and German variants must remain
  platform-sensitive.
- The 66-world identity set is shared across PC and all measured Xbox regions;
  world-resource bytes are not.
- The later PC table's 34 extra frontend IDs must not inflate the mission,
  character, or lore denominator.

## Open boundaries and falsifiers

- PS2 retail `DATA0.NYO`/retail data contents were not decoded here. A controlled
  read-only filesystem/data-package manifest for PS2 Europe and USA is the
  cheapest way to test language, mission-title, profile, and world-set parity.
- Xbox Korea versus USA content equality outside the 18 language members and
  already hashed exception set remains at the ZIP CRC triage boundary described
  in `BUILD_AND_DUMP_MATRIX.md`.
- The five English content-facing edits need source chronology or a design
  reference before one wording can be called later, corrected, or canonical.
- Language-table equality does not imply voice-file or video-stream equality.
