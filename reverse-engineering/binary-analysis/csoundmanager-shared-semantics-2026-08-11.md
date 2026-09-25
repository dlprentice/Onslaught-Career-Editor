# `CSoundManager` shared audio-policy semantic recovery

Status: active, bounded semantic recovery
Last updated: 2026-09-20
Evidence: MEASURED — September 20 original volume/event/backend execution and fresh selected pristine instructions; earlier source/demo/deck analysis below is retained evidence, not rerun here.
Verdict: saved master-volume application and bounded active-event updates are independently rechecked; reset, banks and audible behavior retain explicit limits.

Specimen: pristine PC retail `BEA.exe`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`;
PC demo `BEA.exe`, SHA-256
`d8637dd755b21c720c0cb8f71923f94d2a04a184d90f5343c2e868ce8606e5c2`.

## September 20 independent volume/event recheck

The selected executable is `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`
with the retail hash above. The [audio controls](../../VALIDATION.md#original-audio-volume-controls--september-20)
retain original `004e04c0`, camera getter `0046f2c0` and PC
UpdateSound `00517ae0`. The setter stores the raw float at manager
`+0x20`, logs, writes career `00662aac`, then recalculates both
`+0x64/+0x68` on every event reached from manager `+0x0c` through
event `+0x74`. Nonplaying events also change.

Event gain is `event[+0x20] * event[+0x1c]`. Type 1 uses manager
`+0x24`; every other tested type uses `+0x28`. The predistance
conversion multiplies gain, category, master volume and 127 before x87 integer
conversion. The tracked conversion separately uses bounded
`(50 - length(position.xyz)) * 100 * float32(0.02)` before integer
conversion and further gain/category/master multiplication. Although the body
calls GetCamera, it ignores the returned pointer. The tested camera-pointer
change does not affect the result; this does not describe other spatial-update
functions.

Each converted signed integer is multiplied by 200 using 32-bit arithmetic,
capped above at 10000, reduced by 10000, divided by two toward zero and capped
below at -10000 before storage. Preserve that operation order and its
rounding points; a generic normalized-volume curve is not this implementation.

Only an event's nonzero **low playing byte** and nonnegative signed channel
enter PC UpdateSound. A null buffer slot returns there. With the tested owned
2D COM buffer, original UpdateSound submits the predistance field, transforming
values below -4000 by `3*v+8000`. For example -4600 becomes -5800 at
the intercepted device call. The supplied SetVolume failure result is ignored.
Optional frequency updates use 44100/22050/11025 for selector 0/1/other, times
event pitch, with x87 conversion. The stopped-status and 3D COM paths remain
outside this execution cohort.

The [composed loader check](../../VALIDATION.md#original-load-audio-and-save-composition--september-20)
now runs these setters on an authored two-event list before the actual tail,
preset, language-copy and Save operations. Live-setting preservation modes skip
the setters/events. This is bounded native execution, not device opening,
playback, reset, language-bank loading or a durable save round trip.

## September 20 independent reset and bank recheck

The [original reset controls](../../VALIDATION.md#original-audio-reset-and-music-restoration--september-20)
and [bank controls](../../VALIDATION.md#original-language-bank-admission-and-retry--september-20)
separate operations formerly grouped as sound reset. DeviceShutdown releases
and clears both 64-slot arrays, then the device/wrapper. Bank reload instead
calls the 64-slot buffer Stop path, ignores its supplied results and retains the
pointers. Both controls use owned virtual objects, not an audio driver.

Reload `004e2c50` checks the low initialized byte, obtains the active text
header's language name, formats the path and compares it case-insensitively.
An equal path leaves events, samples and buffers alone. A changed path is copied
**before** active-event recycling, sample deletion or bank admission. The tested
two-event list is moved to the free-list head in reversed traversal order.

Original loader `00517d00` then skips for nonzero `00662dd4` or zero
`0066307c`. Otherwise its Open boundary receives the canonical manager's cached
path. A supplied zero return runs the real buffer destructor and returns without
cache rollback. Repeated same-path calls therefore skip even after either gate
is enabled; changing language retries. The cache proves a requested path, not a
successfully loaded bank. These controls exclude successful file parsing.

An alternate-receiver case uses distinct buffer objects and cache names:
event/sample/cache operations use the selected receiver while Stop and bank load
use the canonical manager. Shared authored event/sample nodes remain a lifetime
limitation. Embedded trace sites call `0040c640`, a one-byte RET in this
specimen; the experiment's intercepted trace records are not retail log output.

Full bank/sample decoding, nonnull language cleanup, actual object destruction,
device setup and audible behavior remain open. See the existing
[save/settings contract](save-options-static-review-2026-05-26.md#original-audio-reset-and-language-bank-retry-behavior)
for composition boundaries.

## Retained August 11 static report

These thirty-four functions cover 10,003 retail bytes and 3,359 decoded
instructions. Every body has an independently linked demo twin with zero
normalized instruction differences; 615 raw bytes differ only in encoded
address or displacement spans. The machine-readable result is
[`csoundmanager-shared-semantics-2026-08-11.tsv`](csoundmanager-shared-semantics-2026-08-11.tsv).
That 10,557-byte table has SHA-256
`162a2f355f672d00a4672254f8729f2bb607e1f8a89d5fc55fb1e99e6a30faa8`.

The retained implementation is
[`references/Onslaught/SoundManager.cpp`](../../references/Onslaught/SoundManager.cpp),
37,556 bytes, SHA-256
`34b1f0c19f28ad53ba2840b03cf00f388ddd5fd7bc1dfc57e1bc3767fca250f8`.
Its interface is
[`references/Onslaught/SoundManager.h`](../../references/Onslaught/SoundManager.h),
8,472 bytes, SHA-256
`c1710946f0e62a09b5788462e2754f239d8c5de1cbd29f6d938483514838cdad`.
Released decompiles are retained under
`local-lab/ghidra-fullpass-2026-07-23/exports/W007/decompile/` and `W009`.

## First-party architecture join

Jeremy Longley's 2003 GDC deck describes a shared `CSoundManager` interface
over platform-specific sound managers and samples. The pristine PC executable
independently preserves `SoundManager.cpp`, `pcsoundmanager.cpp`, `CSample`,
`CPCSample`, `IAudibleThing`, and the fixed-pool warning. The released bodies
make the split concrete: this report's shared policy repeatedly calls the
`CPCSoundManager` backend at `0x00896988` for device initialization, channel
allocation, play/stop, pause, spatial updates, and global updates.

The deck's snippets are edited teaching pseudocode, not a literal header. Its
“say 1000?” event array is 256 production events here; exact `SSoundEvent` and
`CXBOXSoundManager` spellings are still absent from the PC binary. The
architectural boundary is corroborated, while those console/source identifiers
remain search seeds.

## Manager and event lifetime

`Init` loads `data\sounds\sounds.sfx`, allocates 256 `0x88`-byte event records,
chains them into a free pool, seeds master/game/menu and message-volume state,
registers debug controls, then calls the PC device initializer. Active events
are rooted at manager `+0x0C`, free events at `+0x34`, and active count at
`+0x08`; event next/previous links are `+0x74/+0x78`.

`GetSoundEvent` is more accurately described as event allocation: pop the free
head, insert at the active head or after channel-assigned events, increment the
count, and emit `Warning : out of sound events!` on exhaustion. Shutdown
returns active events, frees the pool, destroys samples, releases backend voice
buffers and debug state, frees effects, and clears initialization.

Samples are found case-insensitively. Creation selects sound/music path
context, can consume a supplied stream, can reuse an existing sample, stores
the logical name, links a new sample, and recognizes `_L`/`_R` stereo-side
suffixes. The released getter adds reload-existing and load-policy gates not
present in the retained `GetSample` signature.

## Starting, choosing, and stopping sounds

`PlaySample` suppresses non-repeating starts during pre-running game state and
can reject a duplicate sample/owner when `once` is requested. `StartSoundEvent`
stores owner, sample, tracking, volume, fade, range, loop, pitch, completion,
owner-position, and category state; computes initial position/pan and
attenuation; recycles inaudible non-looping starts; and starts an assigned
backend channel.

`PlayEffect` counts a chained effect family, randomly chooses one member,
multiplies its authored volume, resolves once/loop state, applies symmetric
pitch variance, toggles language-dependent loading around sample resolution,
then delegates to `PlaySample`. Its released ABI carries one additional
owner-position flag beyond the retained source signature. Lookup and
`IsEffectPlaying` operate across all variants, not merely the chain head.

All stop families converge on the same policy: optional owner completion
callback, backend channel release when assigned, playing clear, and monitored
owner-reader clear. The selectors differ—owner, owner+sample pointer,
all instances of a sample, name+owner, or all events—and only the
all-instances path forwards `block_until_stopped=true`.

## Volume, pitch, fades, and channel arbitration

Each event retains authored/master volume and subvolume, manager master volume,
game/menu category scale, spatial attenuation, a pre-distance volume, and a
post-distance volume. `UpdateVolumeForAllSoundEvents` recomputes both stored
values and pushes changes to assigned playing channels.

The released `SetMasterVolume` stores the supplied float directly and persists
it. The retained PC source's tangent conversion was not shipped in retail or
demo. This is the same kind of source/release divergence already observed in
the shared music volume owner.

`SortEventList` performs one adjacent-swap pass by attenuated volume on each
call. Only three quarters of backend capacity is budgeted for active events:
assigned channels beyond the budget are stopped, while unpaused high-priority
events inside it acquire free channels. This is the production arbitration
law, not the deck's simplified `ShouldIBePlaying` example.

`SetPitch` stores the target and `round(seconds * 20)` update ticks. Each status
update moves pitch by the remaining-error/remaining-ticks fraction. `FadeTo`
stores a destination and a signed speed. Status adds the signed step once per
update and completes only after a strict crossing (`>` for positive, `<` for
negative), clamps to the destination, and stops a zero-destination event. Thus
landing exactly on the target retains the fade for one additional update; this
is the released edge used by the reconstruction's warning and flight-loop
fades.

## Spatial, owner, and pause policy

`UpdateSoundPosition` has a released stack-only ABI because it does not need a
manager instance. It updates position/velocity for tracking modes, chooses the
nearest camera in multiplayer, transforms into camera-local coordinates,
handles `_L`/`_R` offsets and X inversion, and refreshes pan. `UpdateStatus`
combines that with camera state, backend globals, fades, pitch, volume,
follow-owner death behavior, completed-channel cleanup, and event recycling.

Pause and unpause walk every event, call the backend for assigned channels, and
set or clear event `+0x84`. `FOLLOWANDDIE` stops when its monitored owner dies;
`FOLLOWDONTDIE` retains its last spatial state; initial-position and no-tracking
modes follow their distinct source-backed update rules.

## Released PC extensions

Four bodies have no exact retained shared-source counterpart:

- build `<root>/data/sounds/sounds_<language>_pc.xap` and detect a changed
  language bank;
- tear down active events/voices/samples and reload that changed bank;
- parse the cached compressed XAP stream into named samples, subject to
  resource-build and compressed-audio gates;
- expose the output-enabled byte used by effect playback.

Device-loss recovery extends retained `Reset`: delete samples, shut down music
and message-box voice, release voice buffers, reinitialize the PC sound device
and music, reload the compressed bank, and refresh samples when enabled. The
full XAP record schema and decoder behavior remain open.

## Boundary

The retained report describes the shared PC retail/demo policy and architectural
split. Its demo comparisons and other subsystem claims have not been independently
rerun by the September 20 volume recheck. It does not prove DirectSound worker timing, the effect-file parser
beyond observed consumers, XAP compression details, audible amplitude/pan,
thread races, device-driver behavior, PS2/Xbox implementation equivalence, or
rebuild parity. No executable, Ghidra project, or archived input is mutated.
