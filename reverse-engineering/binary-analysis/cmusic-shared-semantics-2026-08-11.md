# `CMusic` shared music-policy semantic recovery

Status: active, bounded semantic recovery
Last updated: 2026-09-27
Evidence: MEASURED — September 27 complete retail bodies and interface identities; September 20 original-code controls and August 11 source/demo comparison are retained evidence, not rerun here.
Verdict: shared identities and source differences are rechecked; configured volume, later fade consumption and device acceptance remain distinct.

Specimen: pristine PC retail `BEA.exe`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`;
PC demo `BEA.exe`, SHA-256
`d8637dd755b21c720c0cb8f71923f94d2a04a184d90f5343c2e868ce8606e5c2`.

## September 27 identity recheck

Fresh entry-seeded decoding of all eleven shared retail bodies confirms the
1,631-byte / 604-instruction extent below. Comparison with the pinned source,
the `Music.cpp` allocation anchor in AddToPlayList, concrete virtual calls and
the freshly read device table establishes the selected identities independently
of their saved names. The source graph checks only three direct edges among
these eleven bodies; those edges alone cannot identify the virtual operations.

The [music identity promotion](../ghidra/README.md#re-audit-music-identities--september-27)
corrects `004bb380` to `CMusic__Initialise`, `004bb450` to
`CMusic__DeviceChangeTrack`, and `004bb7c0` to
`CMusic__AddDirectoryToPlaylist`, alongside seven PC adapter names. It preserves
their existing interfaces and code. The subsequent
[eight kept-name records](../ghidra/README.md#re-audit-verified-music-records--september-27)
correct the remaining shared comments and qualify source-parity tags while
preserving every name, interface and instruction. This is a static identity
audit, not a new execution of the reset, setter or demo experiments below.

The fresh bodies confirm OGG-only directory admission, linear configured volume
with x87 conversion, and the missing source console registration in Initialise
as source differences. Assignment to random playback on the immediate null-song
path is agreement with the source, despite its surprising behavior. These
findings do not establish filesystem contents, worker
timing or audible playback. Missing complete ABI details remain open.

The eight complete bodies total 1,432 bytes / 542 instructions. Fresh control-flow
inspection also bounds previously broad descriptions: deferred PlaySelection
queues a song and zero target without updating the saved selection or mode;
those writes occur on its immediate path. UpdateStatus calls the device update
slot before checking playing. Its linear finish path stops only if advancing
and wrapping still leaves a null current pointer; the random finish path stops
on a null head. Shutdown directly clears the list head, leaving current, queued
and initialized fields untouched in this body; callee effects and lifetime
safety are separate. Playlist paths are copied without a local length guard.
No runtime safety or decoder behavior is inferred from these branches.

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

The separate [reset/restoration controls](../../VALIDATION.md#original-audio-reset-and-music-restoration--september-20)
now retain original Shutdown, Init and PlaySelection. Init sets current/target
to 127, derives configured volume from the career float, clears the queue and
sets its initialized byte. The platform-Init hook supplies an owned playlist;
its supplied zero return does not suppress these original state writes.
Shutdown clears the list head but leaves the current-song pointer. The recorded
free calls preserve owned memory, so neither a safe lifetime nor a dangling
access is established.

Level 100 restoration selects policy category 2. The tested frontend route uses
category 0 and Level 110 uses category 4, with original list selection/fallback
and virtual-volume/play call ordering. Device failure returns can still lead to
selection with an empty playlist. Actual playlist enumeration, platform setup,
decoder timing and audible playback remain outside the experiment.

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
side is separately bounded in
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
case-insensitive alphabetical ordering. An immediate null `PlayFromList` request
sets random mode and selects from a nonempty playlist. A request while already playing and
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

## Released source agreements and differences

The retail recheck distinguishes these three cases; the older demo comparison
is retained evidence:

- `CMusic::AddDirectoryToPlaylist @ 0x004BB7C0` makes one platform call with
  literal `ogg` at `0x00630A04`. The retained PC branch requests MP3 and WAV.
  `CPCMusic::DeviceInitialise` supplies `data\\music`, so the released playlist
  is `data\\music\\*.ogg`.
- The suspicious retained expression `mPlayType=MPT_RANDOM` is not a
  transcription accident. `CMusic::PlayFromList @ 0x004BB7E0` unconditionally
  writes enum value 2 on its null-song path in both retail and demo. The
  assignment is released behavior and source agreement, not a source divergence.
- `CMusic::SetVolume @ 0x004BBA10` does not use the retained non-PS2 tangent
  curve. The retail body multiplies by 127, converts through x87 `FISTP` under
  the ambient rounding mode, keeps the low DWORD, logs, and persists the
  original float to career state. There is no local rounding-mode override,
  clamp or device-volume submission. The September 20 controls above establish
  selected rounding cases; exceptional inputs and actual device FPU state stay open.

The released update, list-play, and selection paths also contain an override
that substitutes `data\\music\\BEA 08(Master).wma`, guarded by the DWORD at
`00662df4` and byte at `00679ec1`. Their earlier developer/all-cheats meanings
are unverified leads. The literal and branches are measured instruction facts;
this report does not claim the file
exists in an ordinary retail installation or that the override succeeds.

## Corrected identity and boundary

The former saved name `CMusic__Play @ 0x004BB450` was wrong; the September 27
promotion replaces it with `CMusic__DeviceChangeTrack`. It occupies
`CPCMusic` vtable slot 7, and its body matches retained
`CMusic::DeviceChangeTrack`: stop, restore current and target volume, set device
volume, play the filename, and mark playback active. The ordinary
`CMusic::Play` policy is inlined at its released call sites and is not assigned
a separate entry here.

The retained report covers shared state layout, playlist construction/order,
track selection, fade arithmetic and shared/platform boundaries. Its demo
comparisons have not been rerun by the September 20 or September 27 rechecks.
It does not prove async
worker cadence, decoder buffering, DirectSound behavior, live filesystem
enumeration results, audible loudness, or PS2/Xbox instruction parity. No
executable mutation is part of this report; the September 27 Ghidra metadata
promotion is recorded separately above.
