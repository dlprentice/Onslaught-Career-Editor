# Bink video contract (`.vid`)

Status: active format contract — installed container/stream census and retail
playback API routes bounded; language-stream mapping and decoded output open
Date: 2026-08-22
Verdict: all 66 Bink files have bounded container/media metadata and a static
playback owner chain; packet/audio selection and runtime fidelity remain open.
Evidence: MEASURED — all 66 mirror-index video heads were rechecked; the earlier
`ffprobe` pass supplies duration/frame-rate/stream metadata.
Specimen: `G:\bea-asset-mirror\INDEX.jsonl`, SHA-256
`c45722aeed52e77788c7886cb30b813900d3516b1c387983c442d2b02d4fe4b9`;
retail VAs cite `BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

## Population

| Owner | Files | Bytes | Duration |
| --- | ---: | ---: | ---: |
| `video/` root | 6 | 33,388,480 | 3.77 min |
| `video/briefings/` | 28 | 78,936,704 | 13.20 min |
| `video/cutscenes/` | 32 | 240,785,464 | 15.38 min |
| **Total** | **66** | **353,110,648** | **32.358 min** |

Every file begins Bink v1 fourcc `BIKi`. The mirror index records fourcc, frame
count, width, and height; the complete earlier probe found:

| Shape | Files |
| --- | ---: |
| 480×300 at 25 fps | 36 |
| 201×149 at 25 fps | 28 |
| 128×128 at 30 fps | 1 |
| 640×480 at 24 fps | 1 |

The 28 201×149 files are silent briefings. Cutscenes divide into 23 files with
five RDFT audio streams, eight with one RDFT stream, and cutscene 02 with five
DCT audio streams. Five streams align structurally with five European language
lanes, but stream order/selection remains unproved.

## Bink v1 head contract

The bounded header fields used by the corpus observers are the legacy Bink v1
shape:

```text
+0x00 char[4] signature = 'BIKi'
+0x04 u32le stored file-size field
+0x08 u32le frame_count
+0x0c u32le largest-frame-size field
+0x10 u32le width
+0x14 u32le height
+0x18 u32le frame-rate numerator
+0x1c u32le frame-rate denominator
... flags, audio-track descriptors, frame-offset table, packet payloads
```

Only signature/frame count/geometry are promoted from the 2026-08-22 mirror
index. Frame-rate, duration, and stream codec/count come from the cited
read-only `ffprobe` census. Packet fields, checksums, audio descriptors, and
frame-offset semantics are not re-derived here.

## Codec DLL and ABI

The pristine `binkw32.dll` is SHA-256
`2d0ae23a6175dc7b635c402a5e7e9542e923c0d1c376a8c5ef876ca0d5959d23`,
RAD Video Tools/Bink 1.5v, with 85 exports. BEA's image contains matching
`_BinkOpen@8`, `BinkDoFrame`, `BinkCopyToBuffer`, track/sound, close, and timing
imports. Full PE identity and export table: [game-binaries.md](game-binaries.md).

## Retail playback anchors

| VA | Identity | Static boundary |
| --- | --- | --- |
| `0x005412E0` | `CDXFrontEndVideo__Open` | Configures RAD allocation, stores the path/dimensions, selects sync/async open. |
| `0x00541430` | `CDXFrontEndVideo__InitVideo` | Reads the Bink handle, decodes the first frame, creates two texture buffers. |
| `0x00541650` | `CDXFrontEndVideo__CloseVideo` | Waits for async open, releases textures, gets summary, calls BinkClose. |
| `0x00541790` | `CDXFrontEndVideo__Render` | Decodes/advances, copies into a locked texture, draws a faded quad. |
| `0x00541D30` | `CDXFrontEndVideo__Update` | Calls BinkWait/DoFrame/NextFrame and checks completion. |
| `0x00541120` | `CBinkOpenThread__ctor` | Constructs the asynchronous Bink-open worker owner. |
| `0x0053F0F0` | `CDXFMV__ctor_base` | Embeds the front-end video object in the lower-level FMV wrapper. |

Evidence:
[`DXFrontEndVideo.cpp.md`](../binary-analysis/functions/DXFrontEndVideo.cpp.md)
and
[`audio-media-cutscene-static-review-2026-05-26.md`](../binary-analysis/audio-media-cutscene-static-review-2026-05-26.md).
These are static ownership/call-chain facts, not runtime playback proof.

## Open questions and falsifiers

- Map language to audio track by decoding one known line from every stream or
  tracing `BinkSetSoundTrack` selection under each language.
- Independently validate frame-offset and packet tables for all 66 files; a
  recognized fourcc and successful `ffprobe` run are not full integrity proof.
- Establish audio timing, frame skipping, texture copy mode, colour conversion,
  and synchronization through controlled capture.
- Reconcile briefing/cutscene IDs to missions, Goodies, subtitles, and career
  state.
- Keep any decode output ignored/local; no video or extracted audio bytes enter
  git.

## Claim boundary

The 66-file population, Bink identity, geometry/rate/stream census, codec DLL
ABI, and static playback owner chain are bounded. Packet decode, audio language
order, runtime synchronization, visible/audible fidelity, and rebuild parity are
open.
