# Localization and mission-text contracts (`language/*.dat`, `.txt`, `.stf`)

Status: active format contract — language DAT layout implemented; loose mission
text/source relations bounded
Date: 2026-08-22
Verdict: the six v3 DAT layouts and ID/audio-name census are closed; loose
TXT/STF selection, signed-ID tooling, and language fallback remain open.
Evidence: MEASURED — 227 mirror-index text-family rows plus six language DATs;
retail loader VAs and the complete corpus crosswalk are cited.
Specimen: `G:\bea-asset-mirror\INDEX.jsonl`, SHA-256
`c45722aeed52e77788c7886cb30b813900d3516b1c387983c442d2b02d4fe4b9`;
retail VAs cite `BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

## Population

| Family | Files | Nonempty | Format boundary |
| --- | ---: | ---: | --- |
| `language/*.dat` | 6 | 6 | binary v3 localization tables |
| Mission `*.txt` | 130 | 46 | bracket-keyed text source; 84 empty |
| `*.stf` | 96 | 5 | text-source definitions when nonempty; 91 empty |
| `MissionScripts/text/textlist.h` | 1 | 1 | generated/demo-era residue |

The mirror classifier calls zero-byte rows `binary` because they have no text
head. That is not evidence of a binary STF container. All five nonempty STF
files are text.

## Language DAT v3 layout

All six files are little-endian and share this layout:

| Offset | Field |
| ---: | --- |
| `0x00` | `u32 magic = 0xFFFFFFBB` (disk `BB FF FF FF`) |
| `0x04` | `u32 version_flags`; shipped value 3, high bit clear |
| `0x08` | `u32 count = 2,571` |
| `0x0C` | `count` entries, 12 bytes each |
| entry `+0x00` | `u32 text_id` |
| entry `+0x04` | `u32 text_off_words` into UTF-16LE text pool |
| entry `+0x08` | `u32 audio_off_bytes` into ASCII audio-name pool; `0xFFFFFFFF` means none |
| after entries | `u32` loader offset, UTF-16LE NUL strings, then audio-pool header/data |

All tables have 2,571 unique IDs in identical order and 607 audio-bearing IDs
with identical ID-to-audio-name mappings. Text serialization differs by
language. After signed-to-unsigned 32-bit normalization, the current global
`text.stf` has an exact 2,571-name/ID bijection to the DAT IDs.

[`tools/language_dat_decode.py`](../../tools/language_dat_decode.py) implements
this v2/v3 layout. Its current STF regex accepts only unsigned decimal text, so
it drops all 151 negative definitions; the byte decoder is useful, but its
general STF-name export is not complete until that bug is fixed.

## Mission TXT and STF source shapes

Nonempty mission TXT files begin bracketed keys such as
`[_400_CLEAR_BEACH...]` followed by quoted localized text. Current `text.stf`
uses C-preprocessor `#define NAME signed_decimal_id` rows; duplicate/older
copies in `MissionScripts/text` reflect earlier mapping states. `textlist.h`
states that `TextConvert.cpp` generated it and contains only 16 sequential IDs.

The loose tree is not self-contained for clean recompilation: 16 active include
paths are absent. Runtime precedence between loose text/script sources and
packed mission objects is unproved.

## Retail decoder anchors

| VA | Identity | Demonstrated boundary |
| --- | --- | --- |
| `0x004F21F0` | `CText__Init` | Selects five UI languages plus American-English override; parses versions 0–3. |
| `0x004F2580` | `CText__GetStringById` | Linear v1/v2/v3 entry scan; returns UTF-16 pool pointer or fallback. |
| `0x004F2500` | `CText__GetStringByIdAfter` | Relative/grouped lookup owner. |

The detailed loader contract is
[`CText__Init.md`](../binary-analysis/functions/text.cpp/CText__Init.md); lookup
semantics are in
[`CText__GetStringById.md`](../binary-analysis/functions/text.cpp/CText__GetStringById.md).
The installed files prove six filesystem tables; the UI selector still has five
language IDs because American is an override of English, not a sixth menu
choice.

## Voice relation

French/German/Italian/Spanish each have 607 Ogg stems that case-fold-match the
607 DAT audio identifiers. English has the same referenced set plus 12 extra
files; no separate American voice directory exists. Exact-case mismatch counts
vary by lane, so any cross-platform consumer must preserve authored names and
apply only a proved case policy.

## Open questions and falsifiers

- Fix and test the signed-STF parser before claiming a complete general export.
- Prove American/English text and voice selection with a copied-profile file-I/O
  trace.
- Map every mission TXT/STF symbol to packed mission representation and runtime
  precedence.
- Preserve encodings, line endings, case, unknown/empty files, and duplicate
  source states; do not normalize the corpus silently.
- Bound malformed offsets and missing IDs against a disposable copy, not the
  pristine files.

## Claim boundary

DAT v3 framing and complete ID/audio-name census are strong. Loose source
selection, compiler behavior, exact case policy, American voice fallback,
malformed-input behavior, and full rebuild localization parity remain open.
