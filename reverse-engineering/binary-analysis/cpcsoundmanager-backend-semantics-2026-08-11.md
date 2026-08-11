# `CPCSoundManager` DirectSound backend semantic recovery

Status: active, bounded semantic recovery
Last updated: 2026-08-11
Evidence: SOURCE — pinned `pcsoundmanager.cpp`/`.h` and the first-party GDC
shared/platform architecture; MEASURED — complete pristine retail bodies,
DirectSound calls, formats, tables, constants, and twenty normalized-identical
PC demo twins; UNKNOWN — device-driver timing and audible parity.
Verdict: the PC audio backend is recovered from device enumeration through
sample decode/conversion, DirectSound buffer/channel lifecycle, 3D listener
updates, pause/stop, and playback completion.

Specimen: pristine PC retail `BEA.exe`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`;
PC demo `BEA.exe`, SHA-256
`d8637dd755b21c720c0cb8f71923f94d2a04a184d90f5343c2e868ce8606e5c2`.

## Result

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
enumerates DirectSound devices into `0x78`-byte records, clamps the configured
device index, creates DirectSound8, selects priority cooperative level, queries
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

The retained PC `LoadSampleFromBuffer` path is genuinely a two-argument null
stub in retail and demo. Production compressed-bank loading instead passes a
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
marks the shared event playing. Pause stops without releasing; unpause calls
Play again with the loop flag; full stop releases and nulls both ordinary and
3D buffer slots. The retained `blockuntilstopped` argument has no observed
branch in the PC stop body.

Global updates submit a neutral listener transform plus distance/doppler state
with deferred application. Per-event updates submit position and velocity to
the 3D buffer, combine shared attenuation with backend rolloff, set DirectSound
volume, update playback frequency only when continuous-rate support was
reported, and detect a channel whose play/loop status has ended. `UpdatesDone`
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
