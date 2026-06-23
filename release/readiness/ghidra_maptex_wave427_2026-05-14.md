# Ghidra CMapTex Wave427 Static Correction

Status: public-safe static Ghidra evidence note
Date: 2026-05-14
Scope: saved retail `BEA.exe` Ghidra signature/comment/tag correction

## Summary

Wave427 serialized headless dry/apply/read-back hardened the six saved `CMapTex` terrain mixer-texture functions at `0x00491180` through `0x004916c0`. The pass preserved the already useful names and replaced generic/undefined signature debt with argument names and proof-boundary comments for reset, TGA load, downsample, mixer-set load, LOD copy, and chunk deserialization behavior.

This is public-safe static evidence only. It does not launch or patch `BEA.exe`, does not mutate the installed Steam game, and does not include raw decompile text or private runtime proof. The retail debug string names `C:\dev\ONSLAUGHT2\maptex.cpp`, but `maptex.cpp` is absent from the current Stuart source snapshot, so this wave is binary-led rather than source-body parity.

## Saved Ghidra Changes

| Address | Saved state | Static evidence summary |
| --- | --- | --- |
| `0x00491180` | `void __fastcall CMapTex__Reset(void * this)` | `RET` with no stack cleanup; writes `-1` to `+0x0c`, frees owned pointers at `+0x00/+0x08`, and clears each slot. |
| `0x004911c0` | `int __thiscall CMapTex__LoadTexture(void * this, char * texture_path, int texture_width, int texture_index)` | `RET 0xc`; constructs `CTGALoader`, copies texture data, derives the fourth height/alpha channel, and tracks min/max values at `+0x1c/+0x34`. |
| `0x00491340` | `void __thiscall CMapTex__DownsampleTexture(void * this, void * dest_buffer, void * src_buffer)` | `RET 0x8`; performs 2x2 downsample into the destination buffer, including signed averaging for the fourth channel. |
| `0x004914b0` | `int __thiscall CMapTex__LoadMixerTextureSet(void * this, int set_id, int texture_count, int texture_width)` | `RET 0xc`; caches set id, sizes texture storage from count/width, formats the mixer TGA path, and calls `CMapTex__LoadTexture`. |
| `0x004915d0` | `void __thiscall CMapTex__CopyFromOther(void * this, void * source_map_tex)` | `RET 0x4`; copies source set/count/min/max metadata, halves the destination width, allocates a new buffer, and calls `CMapTex__DownsampleTexture`. |
| `0x004916c0` | `void __thiscall CMapTex__Deserialize(void * this, void * chunk_reader, int texture_index)` | `RET 0x8`; `texture_index` is callsite/return-cleanup proven but not consumed in the current decompile; body reads the `0x4c` header and conditional payload buffers through `chunk_reader`. |

## Validation

| Command or check | Result | Important output |
| --- | --- | --- |
| `py -3 tools\ghidra_maptex_wave427_probe_test.py` | PASS | Focused tests passed `4/4`. |
| `py -3 -m py_compile tools\ghidra_maptex_wave427_probe.py tools\ghidra_maptex_wave427_probe_test.py` | PASS | Both focused Python files compile. |
| Pre-apply `cmd.exe /c npm run test:ghidra-maptex-wave427` | FAIL, expected red | Probe rejected the missing post-apply artifacts before saved Ghidra apply/read-back existed. |
| Headless `ApplyMapTexWave427.java` dry run | PASS | `updated=0 skipped=6 renamed=0 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`; dry logic made no metadata mutation. |
| Headless `ApplyMapTexWave427.java` apply | PASS | `updated=6 skipped=0 renamed=0 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`. |
| Post-apply metadata/tag/xref/instruction/decompile read-back | PASS | Verified `6` metadata rows, `6` tag rows, `12` xref rows, `1566` instruction rows, `6` target decompile exports, `4` caller decompile exports, and `245` focused callsite instruction rows. |
| Post-apply `cmd.exe /c npm run test:ghidra-maptex-wave427` | PASS | Focused probe accepted the saved signatures, comments, tags, xrefs, instruction terminators, and proof-boundary wording. |
| Headless whole-database quality snapshot | PASS | `total_functions=6043`; `commented_functions=1692`. |
| `cmd.exe /c npm run test:ghidra-static-reaudit-queue` | PASS | Queue reports `6043` functions, `4351` commentless functions, `1855` undefined signatures, `1795` `param_N` signatures, and zero broad uncertain/helper/wrapper debt. |
| Live Ghidra project backup | PASS | Private post-mutation backup verified `19` files, `155224967` bytes, `MissingCount=0`, and `HashDiffCount=0`. |

## Current Queue Telemetry

The refreshed static re-audit queue now reports:

- Total function objects: `6043`
- Functions with non-empty function comments: `1692`
- Commentless function objects: `4351`
- `undefined` signatures: `1855`
- Signatures still using `param_N`: `1795`
- Comment-backed telemetry proxy: `1692/6043 = 28.00%`
- Strict clean-signature telemetry proxy: `1630/6043 = 26.97%`

These are triage proxies only. They are not certification and are not completion gates.

## Not Proven

This wave does not prove runtime terrain texture behavior, runtime mixer loading behavior, exact concrete `CMapTex` layout, exact local variable names/types, exact source-body identity, source-to-retail rebuild parity, BEA launch behavior, game patching, or runtime gameplay behavior.
