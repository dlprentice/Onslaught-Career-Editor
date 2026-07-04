# Ghidra WavRead Wave537 Readiness

Date: 2026-05-18
Scope: Static Ghidra boundary recovery plus signature/comment/tag hardening for WavRead and CWaveSoundRead helpers.

## Targets

| Address | Saved state |
| --- | --- |
| `0x00505210` | `int __cdecl WavRead__ReadMMIO(void * hmmio, void * riff_chunk, void * * wave_format_out)` |
| `0x005053d0` | `int __cdecl WavRead__WaveReadFile(void * hmmio, uint byte_count, byte * out_buffer, void * data_chunk, uint * bytes_read_out)` |
| `0x005054a0` | `void __fastcall CWaveSoundRead__Constructor(void * this)` |
| `0x005054b0` | `bool __fastcall CWaveSoundRead__HasFormat(void * this)` |
| `0x005054c0` | `uint __fastcall CWaveSoundRead__GetSampleRate(void * this)` |
| `0x005054d0` | `uint __fastcall CWaveSoundRead__GetChannelCount(void * this)` |
| `0x005054e0` | `void * __thiscall CWaveSoundRead__ScalarDeletingDestructor(void * this, byte delete_flags)` |
| `0x00505500` | `void __fastcall CWaveSoundRead__Close(void * this)` |
| `0x00505570` | `void __fastcall CWaveSoundRead__BaseConstructor(void * this)` |
| `0x00505580` | `void * __thiscall CWaveSoundRead__BaseScalarDeletingDestructor(void * this, byte delete_flags)` |
| `0x005055b0` | `int __thiscall CWaveSoundRead__Open(void * this, char * filename)` |
| `0x00505680` | `int __thiscall CWaveSoundRead__Read(void * this, uint byte_count, byte * out_buffer, uint * bytes_read_out)` |
| `0x005056b0` | `int __fastcall CWaveSoundRead__CloseHandle(void * this)` |

## Evidence

- Read-only pre-export covered metadata, tags, xrefs, entry-neighborhood instructions, decompiles, PC sound caller context, and CWaveSoundRead/base vtable slots under `subagents/ghidra-static-reaudit/wave537-wavread-00505210/`.
- Vtable read-back found six raw slot targets that were not function objects before this wave: `0x005054b0`, `0x005054c0`, `0x005054d0`, `0x00505580`, `0x00505680`, and `0x005056b0`.
- `ApplyWavReadWave537.java` dry-run: `updated=0 skipped=13 renamed=0 would_rename=1 created=0 would_create=6 missing=0 bad=0`.
- Final apply: `updated=13 skipped=0 renamed=1 would_rename=0 created=6 would_create=0 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Final verify dry-run: `updated=0 skipped=13 renamed=0 would_rename=0 created=0 would_create=0 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Post read-back verified `13` metadata rows, `13` tag rows, `13` target xref rows, `1885` instruction rows, `13` target decompile exports, and `14` expected vtable-slot rows.
- Focused probe passed: `py -3 tools\ghidra_wavread_wave537_probe.py --check`.
- NPM wrapper passed: `cmd.exe /c npm run test:ghidra-wavread-wave537`.
- Static re-audit queue passed: `cmd.exe /c npm run test:ghidra-static-reaudit-queue`.

## Queue Snapshot

- Total functions: `6089`
- Commented functions: `2622`
- Commentless functions: `3467`
- Exact-undefined signatures: `1538`
- `param_N` signatures: `1315`
- Comment-backed proxy: `2622/6089 = 43.06%`
- Strict comment-plus-clean-signature proxy: `2568/6089 = 42.17%`

These percentages are telemetry only, not completion or correctness certification.

## Backup

Verified saved-project backup:

```text
[maintainer-local-ghidra-backup-root]\BEA_20260518-072526_post_wave537_wavread_verified
```

Backup verification: `19` files, `159288199` bytes, `MissingCount=0`, `ExtraCount=0`, `HashDiffCount=0`.

## Not Proven

Wave537 is static retail Ghidra metadata and boundary evidence only. It does not prove runtime WAV loading behavior, runtime DirectSound integration, exact DirectX SDK source-body identity, exact concrete CWaveSoundRead/base layouts, all CWaveSoundRead call paths, BEA launch behavior, executable patching, or rebuild parity. The non-code-looking vtable-adjacent values after the recovered CWaveSoundRead/base virtual slots remain treated as table-adjacent data, not function boundaries.
