# `CPCMusic` platform-interface semantic crosswalk

Status: active, bounded semantic recovery
Last updated: 2026-09-27
Evidence: MEASURED — fresh retail RTTI, complete selected bodies and dispatches;
SOURCE — pinned `Music.h` and `Music.cpp`; RETAINED — August 11 demo comparison;
UNKNOWN — missing PCMusic source, complete ABI and runtime worker/device behavior.
Verdict: eight nonshared interface targets have bounded identity evidence;
their sole table holder does not establish exclusive implementation ownership.

Specimen: pristine PC retail `BEA.exe`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`;
PC demo `BEA.exe`, SHA-256
`d8637dd755b21c720c0cb8f71923f94d2a04a184d90f5343c2e868ce8606e5c2`.

## September 27 retail identity recheck

Fresh retail RTTI establishes the fixed primary `CPCMusic` → `CMusic` chain.
The 36 bytes at `005e4934` have SHA-256
`90255c2cbd21aeaed9d991ea73e3790fee54c4405f51f55545495f62b03fec9a`.
All nine base declarations are present in pinned `Music.h`; the PC header is
absent. Singleton construction at `005152c0`, the table, shared caller dispatches
and complete adapter bodies corroborate the roles without inventing a PC header.

The [music identity promotion](../ghidra/README.md#re-audit-music-identities--september-27)
names seven adapters at `00515320`, `00515340`, `00515350`, `00515360`,
`00515370`, `00515390` and `005153a0`, plus the shared DeviceChangeTrack body
at `004bb450`. Shutdown and Stop retain their saved thunk links to `00528460`
and `005285b0`. All signatures and instructions remain unchanged. In particular,
this name audit does not certify the saved return type of DeviceGetTrackFinished:
its body clears EAX and then loads AL, while the shared caller tests EAX.

The complete 18-function shared/device packet contains 1,975 bytes and 726
instructions. The August 11 demo comparison below was not rerun. The fresh
retail evidence confirms the OGG/source divergence and corrects this document's
earlier MP3/WAV wording; it does not establish device or audible acceptance.

## Retained August 11 comparison

Strict RTTI pairs the nine-slot retail table at `0x005E4934` with the demo
table at `0x005E5934`; their structural key is
`200cb236dd9c376384b4ad1ee7558c461aaf1f95392cd15c8e0ec857f293f5d9`.
The eight unique targets contain 400 retail bytes and 145 decoded
instructions. Sixteen instructions differ in 27 raw bytes between the builds,
while all eight pairs have zero normalized differences.

The machine-readable result is
[`cpcmusic-vtable-semantics-2026-08-11.tsv`](cpcmusic-vtable-semantics-2026-08-11.tsv).
That 1,888-byte table has SHA-256
`ef8024010651d241965e15118512a1a8e260a3c3fe24a31ce689d38b08d869b1`.
The broader independent comparison is
[`pc-demo-retail-virtual-target-map-2026-08-11.tsv`](pc-demo-retail-virtual-target-map-2026-08-11.tsv).

## Recovered shared/platform boundary

This is another literal production instance of the boundary described in Lost
Toys' cross-platform GDC presentation. Shared `CMusic` owns the playlist,
selection policy, fades, current/target volume, and track-transition state.
`CPCMusic` adapts those calls to PC filesystem and asynchronous-stream owners:

- `DeviceInitialise` calls the stream initializer, then asks shared `CMusic` to
  add `data\\music`; the retail wrapper requests `ogg` once. The pinned PC
  source requests MP3 and WAV, a documented source/retail divergence;
- `DevicePlay`, `DeviceStop`, and `DeviceShutdown` are thin async-stream
  forwards, while `DeviceGetTrackFinished` reads the worker completion byte;
- `DeviceSetVolume` converts the shared integer `0..127` value using the exact
  float32 scalar `0.007874016` (`0x3C010204`) at `0x005E4978` before forwarding
  it to the PC stream;
- `DeviceAddDirectoryExtsToPlaylist` builds `dir\\*.ext`, enumerates it through
  `FindFirstFileA`/`FindNextFileA`, formats each result as `dir\\filename`, calls
  shared `CMusic::AddToPlayList`, and closes the search handle;
- slot 7 is the shared fallback `CMusic::DeviceChangeTrack`, whose pinned source
  and released body stop an active device, restore current and target volume,
  set device volume, start the replacement filename, and mark playback active.

That last body was saved as `CMusic__Play` at `0x004BB450`; it is now
`CMusic__DeviceChangeTrack`. The source declarations, callers and body disprove
the old name: actual shared `CMusic::Play` decides
whether to invoke virtual `DeviceChangeTrack`; the vtable target is the fallback
implementation of `DeviceChangeTrack` itself.

Slot 8 is the inherited one-byte no-op `DeviceUpdateStatus`. It is shared by
228 placements in the retained August 11 report and is excluded from the
identity promotion. The eight other targets each occur only in this holder's
table in the fresh RTTI scan; slot 7 still implements a method defined by
CMusic. The async worker's thread scheduling, decoder buffering, DirectSound
device behavior, live filesystem results, audible parity and remaining ABI
details stay open. The adapter operations above are bounded static findings.
