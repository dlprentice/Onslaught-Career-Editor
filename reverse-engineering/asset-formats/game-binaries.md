# Game binaries contract — DLLs and helper executable

Status: active static identity/ABI census
Date: 2026-08-22
Verdict: all five non-main PE files have exact identities, version/import/export
censuses, and bounded evidence-based roles; invocation/load-time behavior stays
open.
Evidence: MEASURED — SHA-256, PE/COFF headers, version resources, import tables,
and export directories parsed read-only from pristine safe-copy files with
`pefile 2024.8.26`; no binary was executed.
Specimen: `local-lab/safe-copy-bea-pristine/{Message.exe,binkw32.dll,ogg.dll,vorbis.dll,zlib.dll}`
with per-file SHA-256 below; retail VAs cite `BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

## Inventory and specimen boundary

The tracked root ledger in
[`installed-corpus-census.md`](../installed-corpus-census.md) contains the main
`BEA.exe`, helper `Message.exe`, and four DLLs. Part A excludes the main game
executable (owned by the pristine `74154bfa…` binary-analysis corpus) and covers
all **five** non-main PE files:

- `Message.exe`
- `binkw32.dll`
- `ogg.dll`
- `vorbis.dll`
- `zlib.dll`

No separate launcher executable exists in that measured root. All five inputs
came from `local-lab\safe-copy-bea-pristine\`; the live Steam tree and its
intentionally patched `BEA.exe` were not used. Presence in the safe copy and
agreement with the tracked census do not independently prove a Steam-depot hash
or Authenticode provenance.

## Identity, version, imports, and exports

| File | Bytes | SHA-256 | PE timestamp UTC | Linker / subsystem | Version resource | Imports (DLL:function count) | Exports |
| --- | ---: | --- | --- | --- | --- | --- | ---: |
| `binkw32.dll` | 375,808 | `2d0ae23a6175dc7b635c402a5e7e9542e923c0d1c376a8c5ef876ca0d5959d23` | 2003-04-17 02:19:57 | 7.0 / GUI | RAD Video Tools, Bink and Smacker, 1.5v | USER32:28; GDI32:12; KERNEL32:66; WINMM:10 = **116** | **85** |
| `Message.exe` | 36,864 | `9985c14692093a56b2e59d9f5ab4605a15dec3b30579d3c5c8bed08325cc01b7` | 2003-03-11 17:07:21 | 6.0 / GUI | none | USER32:1; KERNEL32:38 = **39** | none |
| `ogg.dll` | 49,152 | `308540dbd488f3bceca2dbadefe02cf29d10a27c4ac096bb3da053e3e0b923ea` | 2002-07-19 11:34:39 | 6.0 / GUI | none | KERNEL32:50 = **50** | **44** |
| `vorbis.dll` | 974,848 | `b4fa55cfe7547ade0a2d5b800ef085ce20cdd71f61898d2461ea61eb0241812b` | 2002-07-19 11:34:55 | 6.0 / console | none | ogg.dll:11; MSVCRT:15; KERNEL32:1 = **27** | **35** |
| `zlib.dll` | 63,827 | `9929233274cd1c33395036717dda8da45d5a3a3c880a4aeff6deabac3407ecc2` | 2002-03-11 21:19:54 | 2.56 / console | zlib 1.1.4, GNU for Win32 | msvcrt:22 = **22** | **68** |

All are x86 (`Machine=0x14c`) and carry a zero checksum field. “Console” above
is only PE subsystem value 3; no runtime console behavior was tested. The
complete named ordinal/RVA tables are in
[game-binary-exports.md](game-binary-exports.md); the local JSON receipt retains
full imports and section geometry as well.

## Role assessments

### `binkw32.dll` — RAD Bink video codec

The 1.5v version resource, 85 exported playback/buffer/track/YUV functions, and
many format-specific code sections (`BINK16`, `BINK32A`, `BINKYUY2`,
`BINKYV12`, and others) identify the Bink SDK runtime. USER32/GDI32 imports
support window/blit management and WINMM `waveOut*` imports provide an audio
backend. Pristine `BEA.exe` contains matching `_BinkOpen@8`, frame decode/copy,
track, sound-system, timing, and close names near `0x00620F40`; the static
`CDXFrontEndVideo` chain calls that ABI. This is the codec for the 66 `.vid`
files in [bink-video.md](bink-video.md). It does not prove decoded-frame or audio
fidelity.

### `Message.exe` — standalone tilde-delimited MessageBox helper

There is no version resource or export directory. Its only non-CRT UI import is
`USER32!MessageBoxA`; the other 38 imports are KERNEL32 startup/runtime support.
Static inspection in the installed-corpus owner shows it scans the command line
for three `~` delimiters, copies caption and message into fixed 400-byte buffers,
and calls `MessageBoxA` with type `0x11000`; a practical accepted shape is
`<ignored>~caption~text~`. No literal/direct reference exists in pristine
`BEA.exe`. It is therefore a narrow vendor helper whose invoker—or orphaned
installer-era status—remains unknown, not a proved game launcher.

### `ogg.dll` — libogg bitstream framing

The 44 exports cover the complete `ogg_sync_*`, `ogg_stream_*`, `ogg_page_*`,
and `oggpack_*` public surface. Its only dependency is KERNEL32 runtime support.
Pristine `BEA.exe` has six-byte IAT thunks beginning at `0x0055D5FE` for the
same Ogg functions, with xrefs from `OggVorbisStream` and `COggFileRead`. This is
external container-framing code for [ogg-audio.md](ogg-audio.md), not an embedded
copy inside BEA.

### `vorbis.dll` — libvorbis analysis and synthesis

The 35 exports include the synthesis decoder, analysis/encode setup, comment and
info APIs, plus codec-class tables `_floor_P`, `_mapping_P`, and `_residue_P`.
It imports eleven `oggpack_*` functions from `ogg.dll` and fifteen MSVCRT
allocation/math helpers. Its `.data` virtual size is **893,140 bytes
(approximately 872 KiB)**, not 893 MB; most is static codec-table/data storage.
BEA's adjacent `0x0055D640`–`0x0055D688` IAT thunks connect these exports to
Vorbis header/PCM synthesis paths.

### `zlib.dll` — zlib 1.1.4 compression runtime

The version resource identifies zlib 1.1.4 and GNU for Win32. Its 68 exports
span `compress`/`uncompress`, deflate/inflate, gzip wrappers, checksums, and
legacy internal tables/helpers; imports are 22 MSVCRT stdio/memory functions.
BEA's `uncompress @ 0x0055D5F2` and `compress @ 0x0055D5F8` thunks jump through
IAT slots and are used by `CDXMemBuffer` paths. Separate in-image texture
inflate machinery also exists, so the exact implementation used by each AYA or
texture path must be established per call chain rather than flattened into one
“zlib decoder.”

## ABI join to `BEA.exe`

[`binary-analysis/functions/import-thunks.md`](../binary-analysis/functions/import-thunks.md)
pins the zlib/Ogg/Vorbis IAT thunks in the pristine image. The Bink import-name
cluster is in
[`binary-analysis/binary-strings.md`](../binary-analysis/binary-strings.md).
Together with the DLL export tables, these establish that the required external
names are present. This pass did not perform a loader-time bind trace, call every
export, or claim ABI compatibility beyond the measured symbols.

## Method and receipts

The static scanner streamed SHA-256 in 1 MiB blocks and read PE machine,
timestamp, linker/subsystem, image base/entry point, checksum, section geometry,
version strings, every import name/ordinal, and every export name/ordinal/RVA.

Ignored receipt paths:

- `local-lab/hermes-kanban-campaign-2026-08-22/gamefolder-deep/dll-scan.json`
  — SHA-256
  `56630182de3f164e667dd62023356efd7e385e8f16884a0ce7253b80c15d7da6`;
- the census receipt in the same directory records the read-only run boundary.

## Open questions

- Prove what invokes `Message.exe`, if anything.
- Trace actual DLL binding/load paths and exact failure behavior for missing or
  incompatible codec DLLs.
- Identify the smallest required export subset per game subsystem instead of
  assuming every SDK export is used.
- Do not infer trust, originality, or depot provenance from age, vendor strings,
  unsigned status, or absence of unusual imports.
