# Ghidra Ogg/Vorbis Wave568 Readiness Note

Date: 2026-05-19
Status: PASS

## Scope

Wave568 hardened eleven saved Ghidra rows:

| Address | Saved state | Evidence |
| --- | --- | --- |
| `0x00523df0` | `int __thiscall OggVorbisStream__InitDecoder(void * this)` | Initializes one Ogg/Vorbis decode stream and records decode state around the `+0x2008`, `+0x200c/+0x2010`, and Vorbis field region. |
| `0x00524180` | `int __thiscall OggVorbisStream__ReadPcmSamples(void * this, void * out_pcm_bytes, uint requested_byte_count)` | `RET 0x8` confirms output buffer plus requested byte count; the loop initializes on demand, decodes Vorbis PCM, and copies bytes to the output buffer. |
| `0x005245a0` | `void * __thiscall COggFileRead__ctor_base(void * this)` | Installs the `COggFileRead` vtable and initializes the stream/open-state fields used by `COggLoader` and async music stream setup. |
| `0x005245e0` | `void * __thiscall COggFileRead__scalar_deleting_dtor(void * this, byte flags)` | Scalar-deleting destructor wrapper; `RET 0x4` confirms one flags argument. |
| `0x00524600` | `void __thiscall COggFileRead__dtor_body(void * this)` | Clears Ogg/Vorbis state, closes the file handle, resets fields, and restores the base `CWaveSoundRead` vtable. |
| `0x005246a0` | `int __thiscall COggFileRead__OpenFileAndPrimeDecoder(void * this, char * file_path)` | Vtable slot 1 open/prime path; opens the file and primes decoding through `OggVorbisStream__ReadPcmSamples(this, null, 0)`. |
| `0x00524710` | `int __thiscall COggFileRead__ReadDecodedPcm(void * this, uint requested_byte_count, void * out_pcm_bytes, int * out_bytes_read)` | Recovered slot 2 boundary; read-back corrected argument order to requested byte count first, then output buffer. |
| `0x00524770` | `int __thiscall COggFileRead__CloseAndReset(void * this)` | Vtable slot 3 close/reset path. |
| `0x00524800` | `int __thiscall COggFileRead__IsOpen(void * this)` | Recovered vtable slot 4 field reader for open-state value at `+0x2008`. |
| `0x00524810` | `int __thiscall COggFileRead__GetSampleRate(void * this)` | Recovered vtable slot 5 field reader for sample rate at `+0x21d0`. |
| `0x00524820` | `int __thiscall COggFileRead__GetChannelCount(void * this)` | Recovered vtable slot 6 field reader for channel count at `+0x21cc`. |

No `source-parity` tag was applied. This tranche is bounded to retail binary evidence.

## Verification

- Dry pass: `updated=0 skipped=11 created=0 would_create=4 renamed=0 would_rename=5 missing=0 bad=0`
- Apply pass: `updated=11 skipped=0 created=4 would_create=0 renamed=5 would_rename=0 missing=0 bad=0`, `REPORT: Save succeeded`
- Initial final dry: `updated=0 skipped=11 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`, `REPORT: Save succeeded`
- Slot-2 correction dry: `updated=0 skipped=0 would_update=1 missing=0 bad=0`
- Slot-2 correction apply: `updated=1 skipped=0 would_update=0 missing=0 bad=0`, `REPORT: Save succeeded`
- Slot-2 correction verify: `updated=0 skipped=1 would_update=0 missing=0 bad=0`, `REPORT: Save succeeded`
- Post exports: `11` metadata rows, `11` tag rows, `20` xref rows, `2607` target instruction rows, `348` callsite instruction rows, `24` vtable-slot rows, and `11` target decompiles
- Queue refresh: `6093` total functions, `2828` commented, `3265` commentless, `1494` exact-undefined signatures, `1167` `param_N` signatures
- Strict/comment proxy: `2828 / 6093 = 46.42%`
- Focused probe: `py -3 tools\ghidra_ogg_vorbis_wave568_probe.py --check` PASS
- NPM wrapper: `cmd.exe /c npm run test:ghidra-ogg-vorbis-wave568` PASS
- Backup: `G:\GhidraBackups\BEA_20260518-224923_post_wave568_ogg_vorbis_verified`
- Backup verification: `19` files, `160009095` bytes, source/destination manifest hash `B990538F54B90A0FB3DF2467786D1C0371616FD07A123F4FEF69AFA9F00672E5`

## Limits

This is saved static Ghidra evidence only. Runtime Ogg streaming/audio behavior, exact `COggFileRead` layout, exact source identity, BEA launch, game patching, and rebuild parity remain unproven.
