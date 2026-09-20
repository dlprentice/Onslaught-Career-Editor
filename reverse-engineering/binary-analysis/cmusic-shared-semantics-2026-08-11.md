# `CMusic` shared music-policy semantic recovery

Status: active, bounded semantic recovery
Last updated: 2026-09-20
Evidence: MEASURED — September 20 original setter execution and fresh selected pristine instructions; the August 11 source/demo comparison below is retained evidence, not rerun here.
Verdict: configured music volume and its persistence are independently rechecked; fade/device consumers remain distinct, with earlier static findings explicitly dated.

Specimen: pristine PC retail `BEA.exe`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`;
PC demo `BEA.exe`, SHA-256
`d8637dd755b21c720c0cb8f71923f94d2a04a184d90f5343c2e868ce8606e5c2`.

## September 20 independent volume recheck

The selected executable is `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`
with the retail hash above. The [audio controls](../../VALIDATION.md#original-audio-volume-controls--september-20)
execute the unchanged setter at `004bba10`. It converts `float32 * 127`
through x87 `FISTP` to 64-bit integer storage, takes the low DWORD for
receiver `+0x2c`, logs, then writes the original input float bits to
canonical career `00662ab0`. It does not clamp the configured value or
change target `+0x28`, current `+0x34` or a hardware voice.

The earlier unqualified `round(volume * 127)` description needs an explicit
rounding mode. At input 0.5, nearest/upward give 64 while downward/toward-zero
give 63. The controlled PC53 and PC64 cases agree; their selected arithmetic
fits both precisions. Neither result establishes the post-device retail FPU
state. The retained PC tangent curve in `Music.cpp:557` is absent from
this body; direct inspection confirms that difference.

Fresh static inspection of `004bb4b0` and `004bb530` separates later
consumption from setting: initialized FadeVolumes moves current by five toward
the existing target, snapping differences below ten, then replaces target with
configured volume only when current reaches it. An ordinary stable-playing
change therefore first retargets, with movement on a following update.
UpdateStatus invokes that path while playing, then clamps initialized current
volume and submits it through vtable slot `+0x14`. This is instruction evidence;
fade cadence, queued-track composition and device loudness were not executed
by the setter controls.

The [Load/audio composition](../../VALIDATION.md#original-load-audio-and-save-composition--september-20)
also retains this setter in the real loader before TailRead/preset/language
application and Save. The preserved fixture's music float produces configured
integer 51, while its original float bits survive serialization. Audio reset,
music initialization/playback and durable storage remain separate.

## Retained August 11 static report

These eleven bodies cover 1,631 retail bytes and 604 decoded instructions.
Every function has an independently linked demo twin with zero normalized
instruction differences; 87 raw bytes differ only in encoded address or
displacement spans. The machine-readable result is
[`cmusic-shared-semantics-2026-08-11.tsv`](cmusic-shared-semantics-2026-08-11.tsv).
That 3,551-byte table has SHA-256
`c8809f2387567fa4e5911a0840489e6d4ce9ae998038b6926c603a1dcfbe7742`.

The retained implementation is `references/Onslaught/Music.cpp`, 12,042 bytes,
SHA-256
`01c38767606c2646e03469801f04981c1302832aca8515ba23480ca5ca72d275`.
Its interface is `references/Onslaught/Music.h`, 2,826 bytes, SHA-256
`8715ff13802163367e2e6009c1a14124cb8cf7d76de5135a3fa2548a449ad27a`.
Released decompiles are retained under
`local-lab/ghidra-fullpass-2026-07-23/exports/W006/decompile/`. The PC device
side is separately closed in
[`cpcmusic-vtable-semantics-2026-08-11.md`](cpcmusic-vtable-semantics-2026-08-11.md).

## Shared state and policy

The released field accesses reproduce the shared class layout around the
platform vtable: play type at `+0x04`, playing at `+0x08`, first/current song at
`+0x0C/+0x10`, target/set/queued values at `+0x28/+0x2C/+0x30`, current volume
at `+0x34`, initialized at `+0x38`, and selection at `+0x3C`. `CSong` is a
`0x10C`-byte allocation with a path buffer followed by its next pointer at
`+0x104` and retained index storage at `+0x108`.

Initialization chooses linear playback, calls the platform initializer, seeds
current and target volume to 127, restores the saved career volume, and clears
the queue. Shutdown stops an active stream, invokes platform shutdown, and
frees the full playlist. The retained source's console command/variable
registration is not present in the released `CMusic::Initialise` body; this
report does not relocate that responsibility without evidence.

Playlist insertion is case-insensitive for duplicate rejection and
case-insensitive alphabetical ordering. A null direct `PlayFromList` request
selects a random playlist member. A supplied request while already playing and
fading queues only a different song, sets target volume to zero, and waits for
the fade helper to start it.

The fade law is integer and update-driven: differences below 10 snap to target,
then the current value moves by five toward the target. On reaching zero with a
queued song, device volume is set to zero before the queued track begins. Once
current reaches target, target is restored to the configured set volume.
`UpdateStatus` applies this only while playing, clamps current volume to
`0..127`, and then handles finished tracks as single/stop, linear/wrap,
random, or replay-by-selection.

Selection indices are exact in the released PC builds: frontend is 8 (or 1 in
playable-demo mode), credits 7, tutorial 3, and stealth/gameplay use
`(rand() >> 8) % 8` with 7 remapped to 9 (or 0 in playable-demo mode).

## Released differences from the retained source

The binaries decide three places where source reading alone would be wrong:

- `CMusic::AddDirectoryToPlaylist @ 0x004BB7C0` makes one platform call with
  literal `ogg` at `0x00630A04`. The retained PC branch requests MP3 and WAV.
  `CPCMusic::DeviceInitialise` supplies `data\\music`, so the released playlist
  is `data\\music\\*.ogg`.
- The suspicious retained expression `mPlayType=MPT_RANDOM` is not a
  transcription accident. `CMusic::PlayFromList @ 0x004BB7E0` unconditionally
  writes enum value 2 on its null-song path in both retail and demo. The
  assignment bug is therefore released behavior.
- `CMusic::SetVolume @ 0x004BBA10` does not use the retained non-PS2 tangent
  curve. Both PC builds execute `round(volume * 127)`, log the integer, and
  persist the original float to career state.

The released update, list-play, and selection paths also contain a developer or
all-cheats override that substitutes `data\\music\\BEA 08(Master).wma`. That
literal is measured control-flow behavior; this report does not claim the file
exists in an ordinary retail installation or that the override succeeds.

## Corrected identity and boundary

The saved name `CMusic__Play @ 0x004BB450` is wrong. Its sole reference is
`CPCMusic` vtable slot 7, and its body exactly matches retained
`CMusic::DeviceChangeTrack`: stop, restore current and target volume, set device
volume, play the filename, and mark playback active. The ordinary
`CMusic::Play` policy is inlined at its released call sites and is not assigned
a separate entry here.

The retained report covers shared state layout, playlist construction/order,
track selection, fade arithmetic and shared/platform boundaries. Its demo
comparisons and unexecuted subsystems have not been independently rerun by the
September 20 recheck. It does not prove async
worker cadence, decoder buffering, DirectSound behavior, live filesystem
enumeration results, audible loudness, or PS2/Xbox instruction parity. No
Ghidra or executable mutation is part of this report.
