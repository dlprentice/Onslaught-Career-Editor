# `CSoundManager` shared audio-policy semantic recovery

Status: active, bounded semantic recovery
Last updated: 2026-09-27
Evidence: MEASURED — September 27 original event-queue and intercepted sample-lookup execution; September 20 volume/event/backend execution retains its date. Earlier source/demo/deck analysis below remains bounded evidence.
Verdict: event acquisition preserves the existing active head and inserts after a selected node; earlier head-insertion wording is corrected. Device, mixer and audible behavior retain explicit limits.

Specimen: pristine PC retail `BEA.exe`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`;
PC demo `BEA.exe`, SHA-256
`d8637dd755b21c720c0cb8f71923f94d2a04a184d90f5343c2e868ce8606e5c2`.

## September 27 event-queue correction

The original acquisition body at `004e0fb0`, 134 bytes ending at `004e1036`,
matches pinned `SoundManager.cpp:598–643` (`GetSoundEvent`). Its complete body
SHA-256 is `06b229d0953eeb7e50593f775d7f60efe4ab40a8b59732bbf6e06fad6562258b`.
The source's parameter name `insertattop` must not be taken literally:

- Empty active list: the acquired node becomes the head, with null links.
- Nonempty list and **nonzero 32-bit flag**: insert after its current head.
- Nonempty list and **zero flag**: walk while a successor exists and the current
  node's channel is signed nonnegative; insert after the first negative-channel
  node encountered, or after the tail. It does not insert before that node.

For active channels `[0, -1, 2]`, zero yields `[old0, old1, new, old2]`;
nonzero yields `[old0, new, old1, old2]`. Both preserve the existing head.
This is agreement between source and retail, correcting the inherited report's
description rather than exposing a source-version difference.

Success pops manager `+0x34`, clears the remaining free head's previous link,
repairs next/previous links at event `+0x74/+0x78`, increments manager `+0x08`
and returns the acquired pointer in EAX with `RET4`. Exhaustion returns zero
without changing the authored manager/events. Its warning-string call reaches
the pristine one-byte RET at `0040c640`; the string does **not** prove a warning
was emitted by this executable.

The [native controls](../../VALIDATION.md#original-sound-event-queue--september-27)
passed 60 cases and two altered-copy branch controls, recording the complete
2,048-byte authored area, stack balance and nonvolatile registers. Two deliberately
inconsistent count fields isolate 32-bit wraparound; they do not model valid
queues containing billions of events. Independent read-only review decoded the
actual output chains and both control differences. These checks cover authored
valid links and final state, not all process writes, malformed lists, concurrent
use, channel arbitration, playback, devices or audible behavior.

## September 27 sound-family identity and documentation recheck

Complete pristine bodies for 42 shared/backend candidates cover 11,886 bytes /
3,939 instructions, excluding the already-promoted DeviceInit anchor. The
prepared identity record is `local-data/test-runs/re-audit-20260926/sound/identity-evidence-v4.json`.
It is bound to the current export, source hashes and freshly decoded original
bytes. The [41 kept-name comment/tag records](../ghidra/README.md#re-audit-verified-sound-records--september-27)
have now been promoted and counted, with exact live readback and independently
restored recovery. The subsequent [source-name cohort](../ghidra/README.md#re-audit-sound-source-names-and-arguments--september-27)
corrects GetSoundEvent and GetSample, and labels their relevant arguments
insert_after_head and music. The physical interfaces are unchanged.
Saved interfaces and old plate notes remain fallible; identity is a narrower
claim than complete behavior. Source references below use the pinned commit
`5352a81cdb838b145a57f7febc5d9fc4b0129ebb`.

Consequential fresh instruction findings:

- Init `004e00d0` uses the raw saved master float and clears manager initialized
  byte `+4` when DeviceInit returns zero AL at `004e0298–004e029c`. The pinned
  source's failure return does not clear it. Sample creation `004e0890` has a
  fourth reuse argument beyond the source's three; the existing September 22
  sample contract remains the owner of the earlier controlled execution.
- `PlaySample` checks master volume before pre-run and duplicate suppression.
  At `004e0b3e–004e0b4c`, x87 comparison C3 causes an early return, including
  zero and unordered results. This gate is absent from pinned source lines 359–405.
- Effect variant selection calls CRT RNG `0055dbfe` even for a singleton chain
  (`004e196b`). A second draw at `004e19c4` requires both nonzero variance and
  nonzero AL from `00517ad0`, whose complete body reads byte `00896c58` and
  returns. Source lines 1150–1201 lack that gate. For positive variance, the remainder
  is nonnegative and is added to pitch; this is **not symmetric variation**.
  The minimum-pitch clamp belongs only to that admitted variance path.
- `CEffect::GetEffectByName` `004e2a90` follows main-list links `+0xd8`, counting
  matching names; it never follows variant links `+0xd4`. `PlayEffect` chooses a
  variant separately, and `IsEffectPlaying` explicitly searches that chain.
- Effect-file allocation carries retail line 1566 versus pinned source line 1526.
  A single file-wide line delta is therefore insufficient. The body retains
  signed version thresholds 101/103, but no executable upper-version assertion.
  Its inlined ReadLine overwrites the last returned byte without first testing
  for CR/LF; the final discarded line also skips leading-`#` records. These are
  static observations, not proof of safe malformed-file handling.
- Paused `UpdateStatus` events skip elapsed-time advancement and the pitch/fade/
  owner branch, but the jump at `004e1dff` rejoins at `004e221a`, before the
  playing/channel check and backend call `004e222b`. The pinned source nests
  that call inside the unpaused branch. Frozen state gates position refresh and
  final event recycling; it does not stop the entire updater. A separate
  stopped-event, time-greater-than-five owner-clear path precedes the pause gate.
- UpdateSoundPosition's X inversion at `004e1752–004e175f` is in the shared
  tail. It can negate a retained position when the refresh branch was skipped,
  so it must not be restricted to newly transformed coordinates.

The source-call checker and native queue experiment have separate, stated limits.
The findings above are static rechecks, not new retail runs. Controlled original
calls with recorded RNG draws, paused/frozen combinations and device-call hooks
are the next inexpensive falsifiers; actual mixer/device/audible acceptance
remains separate.

## September 27 sample-lookup correction

The complete pristine body at `[004e0a00,004e0a8e)` is 142 bytes, SHA-256
`b08bf0f23aa00b948de2a47e6d906d92b1a3bb09c32121cdc2f2eea41d0a0cab`,
from `BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
It corresponds to `CSoundManager::GetSample` in pinned SoundManager.cpp
lines 300–333, with retail additions. Its former GetOrCreateSample name is now
GetSample and its former `channel_type` argument label is now `music`, as shown
by the complete CreateSample body and the backend reload caller at
`00517f81–00517f90`. Exact live/rehearsal equality and independently restored
recovery passed; argument types and storage are unchanged.

Original-code execution in an isolated native i386 harness passed **76 cases
and two consequential altered-copy controls**. ASCII name comparison and
CreateSample are intercepted; this tests the original lookup body and call
transport, not CRT collation or actual loading. Inputs cover initialized/empty
guards, missing and duplicate names, case differences, reload values
`0/1/0x100/0x101`, both global gates, full-width music values and zero/nonzero
creation responses. The output checks include all authored object memory,
both gates, callee-saved registers, stack balance and call arguments.

- The first case-insensitive name match returns unchanged when the low byte
  of `reload_if_exists` is zero. Thus `0x100` does not request reload.
- Missing names or an admitted reload reach CreateSample only when
  DWORD `[00662dd4] != 0` or DWORD `[0066307c] == 0`. An existing match with
  no reload bypasses those creation gates.
- The full second DWORD is forwarded as music, followed by a null reader.
  Only the low byte of the final reuse argument is normalized by `SETNE CL`.
  A second harness variant lets the comparison hook clobber volatile ECX;
  original code forwards `0xa5a5be00/01`, preserving the upper 24 bits.
- The lookup returns the intercepted CreateSample result unchanged. This is
  a transport observation: the actual null-reader route bypasses reuse search
  and reaches filename-loader stub `00517290`, which returns zero. A reload
  request does not prove successful loading or reuse.

The two altered-copy controls invert the initialized gate or the matched-name
reload gate; each produces the predicted contrary result. Receipts and complete
input/output files are in the existing private sound owner under
`sample-lookup-4qft4rv1/` and `sample-lookup-kv0o1crh/`; drivers are
`original_sample_lookup.py` and `original_sample_lookup_v2.py`. The latter
variant supplies the nonzero upper-ECX witness. No real device, sample resource,
non-ASCII comparison, allocator/lifetime or audible result is established.

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

`GetSoundEvent` acquires a free node and inserts it according to the corrected
September 27 rules above. It replaces the active head only for an empty list;
the exhaustion trace call is a no-op in this specimen. Shutdown
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
multiplies its authored volume, resolves once/loop state, conditionally adds
pitch variance under the September 27 gates, and toggles language-dependent
loading around sample resolution before reaching `PlaySample`. Its released
ABI carries one additional owner-position flag beyond the retained source
signature. Name lookup walks the main effect list; `IsEffectPlaying` searches
the selected effect's variant chain.

All stop families converge on the same policy: optional owner completion
callback, backend channel release when assigned, playing clear, and monitored
owner-reader clear. The selectors differ—owner, owner+sample pointer,
all instances of a sample, name+owner, or all events. These selector bodies
inline the shared stop sequence. Only all-instances passes backend
`block_until_stopped=true`; the other four pass false. The PC backend ignores
that argument. The September 27 instruction recheck confirms this distinction.

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

`SetPitch` stores the target and uses x87 integer conversion of `seconds * 20`,
writing the low DWORD to the remaining-update field. Rounding depends on the
x87 control state; generic language `round` is not an adequate contract. Each status
update moves pitch by the remaining-error/remaining-ticks fraction. `FadeTo`
stores a destination and a signed speed. Status adds the signed step once per
update and completes only after a strict crossing (`>` for positive, `<` for
negative), clamps to the destination, and stops a zero-destination event. Thus
landing exactly on the target retains the fade for one additional update; this
is the released edge used by the reconstruction's warning and flight-loop
fades.

## Spatial, owner, and pause policy

`UpdateSoundPosition` consumes two stack arguments and does not read incoming
ECX. The [sound interface cohort](../ghidra/README.md#re-audit-sound-interfaces--september-27)
corrects its saved stdcall annotation to an automatic member receiver using
source identity and explicit ECX delivery in all three decoded direct callers.
StopSoundEvent receives the same bounded correction; UpdateStatus's explicit
fastcall receiver becomes automatic thiscall. IsEffectPlaying's full EAX
production and consumption correct saved bool/AL to int/EAX. These annotations
do not certify every retained argument spelling or indirect caller.
UpdateSoundPosition updates position/velocity for tracking modes, chooses the
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
- expose byte `00896c58`, which gates effect pitch randomization; this recheck
  does not establish that it is a general output-enabled flag.

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
