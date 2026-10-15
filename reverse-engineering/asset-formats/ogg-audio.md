# Ogg/Vorbis, XAP sample-bank, and SFX catalog contracts

Status: active format contract — Ogg framing and installed media census complete;
XAP/SFX semantics bounded; end-to-end playback graph open
Date: 2026-08-22
Verdict: Ogg framing/metadata and XAP/SFX identity joins are bounded across the
installed corpus; full decode and playback behavior remain open.
Evidence: MEASURED — mirror-index heads/counts rechecked for 3,057 Ogg, five XAP,
and one SFX file; deeper durations and bank/catalog joins cite the complete
installed-corpus pass.
Specimen: `G:\bea-asset-mirror\INDEX.jsonl`, SHA-256
`c45722aeed52e77788c7886cb30b813900d3516b1c387983c442d2b02d4fe4b9`;
retail VAs cite `BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

## Installed population

| Family | Files | Bytes / records | Current boundary |
| --- | ---: | --- | --- |
| Music Ogg Vorbis | 10 | 38,822,467 bytes, 43.946 min | stereo 44.1 kHz metadata |
| Voice Ogg Vorbis | 3,047 | 116,136,138 bytes | mono 44.1 kHz metadata across five lanes |
| XAP sample banks | 5 | 164 `PSMP` records each | common names/order; selected ADPCM decode |
| `sounds.sfx` | 1 | 170 text records | exact catalog-to-bank identity relation |

All **3,057** Ogg files total 154,958,605 bytes and approximately 3.565 hours.
The language lanes are English 619 and French/German/Italian/Spanish 607 each.
No two Ogg files are byte-identical.

## Ogg page and Vorbis packet contract

Every measured Ogg begins `OggS` with stream-structure version 0. The standard
page framing used by the installed files is:

```text
'OggS' | u8 version | u8 header_type | i64le granule_position
u32le serial | u32le page_sequence | u32le checksum
u8 segment_count | u8 lacing[segment_count] | segment payload bytes
```

Lacing values delimit packets across pages. Vorbis identification headers expose
channel/rate metadata; terminal granule positions support the duration census.
The pass did **not** decode every packet or validate every page CRC, so
`OggS`/header/granule success is not an all-packet integrity claim.

## XAP bank contract

The five files are `sounds/sounds_<language>_pc.xap`. Each begins:

```text
'PCXP'
u32le record_count = 164
then 164 ordered 'PSMP' sample records
```

The complete bank join establishes:

- all five banks use the same 164 record names and order;
- 134 payload identities are byte-identical across every language;
- 30 HUD records differ and form the localized subset;
- 820 physical bank-record instances exist;
- selected English records use a high-nibble-first IMA-style ADPCM decode;
- decoded-duration estimates assume the observed 44.1 kHz mono 16-bit target.

Those facts do not yet supply a reusable five-bank decoder, complete record
field layout, malformed-input behavior, or playback semantics.

## `sounds.sfx` text catalog

The single 13,669-byte file starts `# SFX sample list`, declares version 103,
and contains 170 indexed records (0–169), 167 descriptions, and 164 distinct
sample references. Source lineage names five values per record: volume, falloff,
pitch variance, looping, and language dependence; 55 records also carry
comments. Six sample references are reused twice.

Every one of the 164 distinct SFX sample tokens maps to one XAP record, and every
XAP identity is referenced. This proves catalog membership, not runtime
selection, attenuation, language fallback, or audible output.

## Retail decoder anchors

The executable imports the codec ABIs through six-byte IAT thunks documented in
[`import-thunks.md`](../binary-analysis/functions/import-thunks.md):

| VA range / anchor | API lane | Static callers |
| --- | --- | --- |
| `0x0055D5FE`–`0x0055D63A` | `ogg_sync_*`, `ogg_stream_*`, page helpers | `OggVorbisStream__InitDecoder` and read paths |
| `0x0055D640`–`0x0055D688` | Vorbis info/comment/synthesis/block helpers | header parse and PCM synthesis/read paths |
| `0x0055D62E` | `ogg_sync_clear` | Ogg stream and `COggFileRead` close/destructor paths |

The static family review
[`audio-media-cutscene-static-review-2026-05-26.md`](../binary-analysis/audio-media-cutscene-static-review-2026-05-26.md)
connects `COggLoader`, `OggVorbisStream`, `COggFileRead`,
`CSoundManager__LoadCompressedSampleBank`, `CPCSoundManager__DecodeADPCM`, and
the DirectSound backend. It intentionally does not claim runtime decode or
playback behavior.

Part A identifies the pristine codec DLLs:

- `ogg.dll`: 44 public libogg exports;
- `vorbis.dll`: 35 analysis/encode/synthesis exports and 11 imports from
  `ogg.dll`;
- `zlib.dll` is unrelated to Ogg page semantics even though it ships beside
  them.

See [game-binaries.md](game-binaries.md) for hashes and complete export tables.

## Open questions and falsifiers

- Validate every Ogg page checksum and decode every packet with an independent
  decoder before claiming complete media integrity.
- Recover the full `PSMP` record schema and decode all five banks byte-bounded,
  including localized and invariant samples.
- Trace one SFX effect from text row through bank lookup, buffer creation,
  DirectSound3D state, and audible output.
- Prove American-versus-English voice fallback and exact case-folding with
  file-I/O traces.
- Map all 3,057 Ogg files to cue/speaker/mission/UI/music state or an explicit
  unknown.

## Claim boundary

Ogg framing/metadata, corpus counts, XAP name/order relations, and the SFX-to-XAP
bijection are bounded. Full decode, malformed input, cue selection, spatial law,
music transitions, audible output, and rebuild parity remain open.
