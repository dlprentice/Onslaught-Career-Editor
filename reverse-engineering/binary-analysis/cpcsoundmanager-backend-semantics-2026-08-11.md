# `CPCSoundManager` DirectSound backend semantic recovery

Status: active, bounded semantic recovery
Last updated: 2026-09-27 (backend identities and stale sample-route/volume wording rechecked; older measurements retain their dates)
Evidence: SOURCE — pinned `pcsoundmanager.cpp`/`.h` and the first-party GDC
shared/platform architecture; MEASURED — complete pristine retail bodies,
DirectSound calls, formats, tables, constants, and twenty normalized-identical
PC demo twins; UNKNOWN — device-driver timing and audible parity.
Verdict: DeviceInit's identity, interface and selected startup branches are
re-grounded below. The dated wider backend analysis remains bounded evidence;
it is not a claim of complete semantic recovery or audible parity.

Specimen: pristine PC retail `BEA.exe`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`;
PC demo `BEA.exe`, SHA-256
`d8637dd755b21c720c0cb8f71923f94d2a04a184d90f5343c2e868ce8606e5c2`.

## DeviceInit recheck — September 26

`0x005169b0` is `CPCSoundManager__DeviceInit`, formerly saved as
`CPCSoundManager__Init`. Its complete body is `[0x005169b0,0x00516ec4)`,
1,300 bytes, SHA-256
`db30b041040db86e32370676d6ab9ea4f6769fdff61811704a20a804363871f8`.
The wave-reader allocation, device setup, primary-buffer format and listener
acquisition identify the counterpart at pinned `pcsoundmanager.cpp:36–109`
(source commit `5352a81cdb838b145a57f7febc5d9fc4b0129ebb`). The embedded
retail allocation line 229 belongs to this operation. In the pinned version,
line 229 falls inside `PlaySound`; that numeric coincidence was a misleading
audit lead, not evidence that this body plays an event.

The interface remains `bool __thiscall(this)`. `CSoundManager__Init` supplies
receiver `0x00896988` at `0x004e028e`, calls at `0x004e0293` and tests AL at
`0x004e0298`. The recovery path calls at `0x00517f49` with its receiver in ECX
and tests AL at `0x00517f4e`. Neither passes an explicit argument. The body
returns true/false in AL and ends with a bare `RET`.

Re-derived retail/source differences:

- Retail writes receiver `+0x2cc=12` before testing `+0x2c8`; an existing
  wave-reader pointer returns true immediately. Source allocates it unconditionally.
- Retail clears 64 main-buffer pointers at `+0xc4`; source defines 32.
- The selected-device check is **upper-bound only**: signed index `>= count`
  resets to zero at `0x00516ab8–0x00516ac4`. Negative indices pass that branch.
  The earlier blanket “clamps” description was too broad.
- Primary output is stereo PCM: quality global `0x00663080` selects 44,100 Hz /
  16-bit for 0, 22,050 Hz / 16-bit for 1, and 11,025 Hz / 8-bit otherwise.
  Source fixes 44,100 Hz / 16-bit. These are primary-device format requests,
  separate from sample-data conversion below.
- Retail keeps the primary buffer locally and releases it after acquiring the
  listener; source retains a member pointer. Retail also enumerates devices and
  queries capabilities before buffer setup, unlike source's default-device path.

Constructor `0x005054a0` installs vtable `0x005dfc4c`; its RTTI identifies
`CWaveSoundRead`. Ownership of the nonvirtual sound manager follows the pinned
class declarations and the reproduced caller/backend structure, not manager RTTI.
Private body/export evidence is in
`local-lab/ghidra-first-training-20260907-v1/re-audit-20260926/startup-identities/`.
No DirectSound driver, playback, audible output or complete failure recovery
was executed in this static recheck. A controlled copied-runtime observation
of device selection, requested format and failure/retry is the remaining falsifier.

## Backend identity and wording recheck — September 27

Twelve complete bodies beyond DeviceInit were independently re-decoded and
reviewed: 1,618 bytes / 531 instructions, including CPCSample's nondeleting
destructor. The parent sound-family record is
`local-data/test-runs/re-audit-20260926/sound/identity-evidence-v4.json`.
These twelve kept names are part of the completed
[41-row sound comment/tag cohort](../ghidra/README.md#re-audit-verified-sound-records--september-27).
Exact live readback and independently restored recovery passed; saved interfaces
were preserved without new certification.
The [direct-call evidence](../../VALIDATION.md#direct-source-call-evidence--september-27)
binds eight shared calls to their target, receiver and ordered arguments;
complete-body/source inspection supplies the explicitly separate identity
premises. These are static findings, not new device runs.

- The stale sample-route statement below is corrected: original `00517290`
  is the five-byte zero-return/RET8 stub reached by CreateSample's **file**
  branch, matching the LoadNewSample role. Its nonnull stream branch reaches
  `005172a0`. The pinned header instead supplies a null inline
  LoadSampleFromBuffer implementation; that source version must not select
  the retail name. The [September 22 contract](save-options-static-review-2026-05-26.md#outer-sample-admission-and-registration)
  owns the earlier original-code checks; they were not rerun here.
- Backend UpdateSound `00517ae0` reads event pre-distance volume `+0x64`,
  not attenuated `+0x68`. Below -4000 it submits `3*v+8000`; velocity XYZ is
  multiplied by 20. Its status-bit check is skipped for first-time or paused
  events. Frequency gate byte `008964d0` is distinct from effect-randomization
  gate `00896c58`. These gates do not by themselves identify device capabilities.
- StopSound `005179b0` ignores its second argument. The 3D-buffer release is
  inside the ordinary-buffer-nonnull branch, not unconditional. PlaySound
  `00517790` sets the event playing byte without checking the final Play result.
- UpdateGlobals `00517a20` constructs and submits a 64-byte listener descriptor;
  the corresponding pinned source body is entirely commented out. The retail
  descriptor uses zero position/velocity, front `(0,1,0)`, top `(0,0,-1)`,
  distance/doppler 1 and a rolloff read from `0063e2ac`. This is not evidence
  that the global remains at its initial approximately 0.7 value.
- FindFreeChannel `00517cb0` reads its bound and buffer array through the
  receiver, but reads active-event head from fixed `00896994`. A hypothetical
  second manager instance therefore cannot be modeled with only its own list.
- GetSampleLength `00517c60` returns through ST0/RET4. Source float-member
  versus saved double-stdcall remains unresolved: an unused incoming ECX and
  x87 result alone cannot settle either source type or calling convention.

Device opening, real HRESULT behavior, mixer output and audible parity remain
open. Use owned COM objects to falsify call ordering/arguments before any live
device experiment; preserve the distinction between those tests and hearing
the complete game.

## Dated August 11 comparison

These twenty functions cover 4,311 retail bytes and 1,402 decoded
instructions. Every body has an independently linked demo twin with zero
normalized instruction differences; 220 raw bytes differ only in encoded
address or displacement spans. The machine-readable result is
[`cpcsoundmanager-backend-semantics-2026-08-11.tsv`](cpcsoundmanager-backend-semantics-2026-08-11.tsv).
That 6,008-byte table has SHA-256
`1d2ee5e9040c6e232a8b56339f9905444655ae030df6ed85240a792cb9ac8fb2`.

The retained backend is
[`references/Onslaught/pcsoundmanager.cpp`](../../references/Onslaught/pcsoundmanager.cpp),
13,986 bytes, SHA-256
`df51f84542fc95991369ed0fadac8ab12c724654f6e7fad501899dc6855bdf4f`.
Its interface is
[`references/Onslaught/pcsoundmanager.h`](../../references/Onslaught/pcsoundmanager.h),
2,197 bytes, SHA-256
`ed7770ae596f1ec9f348fc4e3b29852d5f20ea76fa73f0078de6170963bc361c`.
Released decompiles are retained under
`local-lab/ghidra-fullpass-2026-07-23/exports/W009/decompile/`. The shared
caller and policy half is
[`csoundmanager-shared-semantics-2026-08-11.md`](csoundmanager-shared-semantics-2026-08-11.md).

## Device and channel lifecycle

Initialization creates the wave-reader helper, clears 64 channel slots,
enumerates DirectSound devices into `0x78`-byte records, checks the configured
device index against its upper bound, creates DirectSound8, selects priority cooperative level, queries
capabilities, derives 3D/voice capacity, creates the primary buffer, installs
the quality-dependent PCM format, and acquires the DirectSound3D listener.

Shutdown walks all 64 slots, releases 3D and ordinary buffers, releases the
DirectSound object, and deletes the wave reader. Reset is intentionally
narrower: stop every current buffer but retain allocations. The public count
and indexed record accessor are the frontend sound-device option boundary; the
remaining record fields are not named without evidence.

`FindFreeChannel` scans only the derived active-voice count. A channel is free
when no active shared event names its index and its DirectSound buffer slot is
null. This complements the shared manager's 75% channel budget: shared policy
chooses which events deserve channels, while this backend provides an actually
unused index.

## Production sample pipeline

The retail file-loading route `00517290` is a two-argument null stub, corresponding
to LoadNewSample as rechecked above. Production compressed-bank loading passes a
serialized sample record to `0x005172A0`: read compressed byte count, allocate
or refresh a `0x84`-byte PC sample, read ADPCM, create and lock a secondary
buffer, decode to PCM16, convert to the selected output quality, unlock, and
free temporary storage.

The IMA ADPCM decoder is complete: canonical 16-entry index adjustment and
89-entry step tables, alternating low/high nibbles, signed-16 clamp, and
predictor/index state carried across calls. No codec name is guessed from
shape alone; the table and state transition identify IMA ADPCM mechanically.

Output quality is an exact three-way law:

- index 0 preserves decoded PCM bytes at 44,100 Hz;
- index 1 averages stereo 16-bit pairs into 22,050 Hz 16-bit mono;
- lower quality averages four source samples into 11,025 Hz unsigned 8-bit
  output.

The secondary-buffer helper builds the matching `WAVEFORMAT` and buffer
description, selects the configured 3D algorithm, scales target byte count,
creates the buffer, and locks its full writable range. A separate PCM-data path
uses the same buffer/conversion owner for queued Bink voice samples. Sample
length is decoded bytes divided by the selected rate and two bytes per sample.

## Playback and 3D updates

`PlaySound` computes authored start/end sample offsets, duplicates the sample's
DirectSound buffer into the assigned channel, obtains its 3D buffer interface,
seeds position/volume/frequency, seeks, starts with the event loop flag, and
marks the shared event playing without testing the final Play result. Pause
stops without releasing; unpause calls Play again with the loop flag. Full stop
releases/nulls the ordinary buffer and, within that nonnull branch, the 3D buffer.
The retained `blockuntilstopped` argument has no observed
branch in the PC stop body.

Global updates submit a neutral listener transform plus distance/doppler state
with deferred application. Per-event updates submit position and velocity to
the 3D buffer, use the shared pre-distance volume field for DirectSound volume,
and update frequency when byte `008964d0` permits. A non-first-time, unpaused
event also gets a playback-status check. These branches do not establish actual
audible attenuation or the meaning of every capability flag. `UpdatesDone`
commits all deferred listener settings once per shared-manager update.

## Architecture conclusion and boundary

Together with the shared report, this is a concrete production example of the
GDC deck's recommended architecture: game-facing sound events, ownership,
priority, fades, and spatial policy live in `CSoundManager`; DirectSound device,
buffer, codec, channel, and listener work lives in `CPCSoundManager`. It does
not prove the deck's illustrated Xbox class name or that console backends share
these PC layouts.

Open boundaries are DirectSound HRESULT failure recovery beyond observed
branches, thread/device-driver ordering, exact device-info record fields,
sample-bank container framing above the per-record consumer, audible resampler
quality, Xbox/PS2 codec and channel laws, and rebuild parity. No executable,
Ghidra project, or archive input is mutated.
