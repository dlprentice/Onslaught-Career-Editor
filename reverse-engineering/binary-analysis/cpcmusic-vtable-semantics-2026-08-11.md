# `CPCMusic` platform-interface semantic crosswalk

Status: active, bounded semantic recovery
Last updated: 2026-08-11
Evidence: MEASURED — strict retail/demo RTTI, paired vtables, gapless bodies,
calls, strings, imports, globals, and constants; SOURCE — pinned `Music.h` and
`Music.cpp`; UNKNOWN — the missing retained `PCMusic.cpp` implementation and
runtime worker/device behavior.
Verdict: all eight uniquely `CPCMusic`-owned virtual targets have exact ABI
identities and bounded behavior; one saved shared-function name is corrected.

Specimen: pristine PC retail `BEA.exe`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`;
PC demo `BEA.exe`, SHA-256
`d8637dd755b21c720c0cb8f71923f94d2a04a184d90f5343c2e868ce8606e5c2`.

## Result

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

- `DeviceInitialise` starts the PC async stream, then asks shared `CMusic` to
  add `data\\music`; shared source expands that request to MP3 and WAV on PC;
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

That last body is currently saved as `CMusic__Play` at `0x004BB450`. The source
ABI order and body prove that name wrong: actual shared `CMusic::Play` decides
whether to invoke virtual `DeviceChangeTrack`; the vtable target is the fallback
implementation of `DeviceChangeTrack` itself.

Slot 8 is the inherited one-byte no-op `DeviceUpdateStatus`. It is shared by
228 placements and therefore is not duplicated in this eight-row unique-owner
table. The async worker's thread scheduling, decoder buffering, DirectSound
device behavior, live filesystem results, and audible parity remain open; the
interface contract and the visible PC adapter behavior do not.
