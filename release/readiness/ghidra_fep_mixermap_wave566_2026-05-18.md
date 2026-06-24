# Ghidra FEP/MixerMap Wave566 Readiness Note

Date: 2026-05-18
Status: PASS

## Scope

Wave566 hardened five saved Ghidra rows:

| Address | Saved state | Evidence |
| --- | --- | --- |
| `0x005230e0` | `void * __thiscall CFEPWingmen__FindCurrentLevelRecord(void * this)` | Corrected from stale `CVBufTexture__FindListEntryByGlobalId89D94C`; deferred FEPWingmen callsites pass `ECX=&DAT_0089da44`, and the body walks `this+0x28` / cursor `this+0x30` until record id equals `DAT_0089d94c`. |
| `0x00523190` | `void __thiscall CMixerMap__InitSlot(void * this, void * chunk_reader)` | `RET 0x4`, prologue receiver use, and caller `0x00523381` prove a slot receiver plus one chunk-reader argument. |
| `0x00523210` | `void __thiscall CMixerMap__DestroySlot(void * this)` | ECX-only per-slot cleanup; frees and clears payload pointer at `this+0x04`. |
| `0x00523230` | `void __thiscall CMixerMap__Destroy(void * this)` | Called by `CHeightField__ShutdownAndDestroyMixerMap`; frees the 0x14000-byte slot array payloads and the 0x40000 secondary buffer. |
| `0x005232b0` | `void __thiscall CMixerMap__Init(void * this, void * chunk_reader)` | `RET 0x4` and `CHeightField__DeserializeMapAndInitResources` prove a chunk-reader argument; allocates 0x1000 0x14-byte slots and reads the 0x40000 payload. |

No `source-parity` tag was applied because `FEPWingmen.cpp` and `mixermap.cpp` are absent from `references/Onslaught`.

## Verification

- Dry pass: `updated=0 skipped=5 renamed=0 would_rename=1 missing=0 bad=0`, `REPORT: Save succeeded`
- Apply pass: `updated=5 skipped=0 renamed=1 would_rename=0 missing=0 bad=0`, `REPORT: Save succeeded`
- Final dry: `updated=0 skipped=5 renamed=0 would_rename=0 missing=0 bad=0`, `REPORT: Save succeeded`
- Post exports: `5` metadata rows, `5` tag rows, `17` xref rows, `1125` focused instruction rows, `5` target decompiles, and `341` FEP callsite instruction rows
- Queue refresh: `6089` total functions, `2811` commented, `3278` commentless, `1494` exact-undefined signatures, `1179` `param_N` signatures
- Strict proxy: `2811 / 6089 = 46.17%`
- Focused probe: `py -3 tools\ghidra_fep_mixermap_wave566_probe.py --check` PASS
- NPM wrapper: `cmd.exe /c npm run test:ghidra-fep-mixermap-wave566` PASS
- Backup: `G:\GhidraBackups\BEA_20260518-214519_post_wave566_fep_mixermap_verified`
- Backup verification: `19` files, `159910791` bytes, source/destination manifest hash `C860FBFF2EBE9939D13E861C7459C6D3A0E1C344631BD72C3F92F612B97830C6`

## Limits

This is saved static Ghidra evidence only. Runtime FEPWingmen behavior, concrete `CFEPWingmen` and record layouts, runtime MAP/mixer/audio behavior, exact source identity, BEA launch, game patching, and rebuild parity remain unproven.
