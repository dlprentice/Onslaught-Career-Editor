# DXClouds.cpp Functions

> Source File: DXClouds.cpp | Binary: BEA.exe
> Debug Path: 0x006503d4 (`[maintainer-local-source-export-root]\DXClouds.cpp`)

## Overview

DirectX cloud rendering support for the atmospheric cloud layer. Current evidence is static retail Ghidra read-back only. No matching tracked Stuart source implementation body has been found, so no `source-parity` tag is used here.

## Wave590 Saved State

Wave590 hardened the queue-head CClouds constructor and shutdown slot after serialized Ghidra dry/apply/read-back.

| Address | Saved name | Signature | Evidence |
| --- | --- | --- | --- |
| `0x0053b900` | `CClouds__Constructor` | `void * __fastcall CClouds__Constructor(void * this)` | `Atmospherics__Init` allocates a `0x334` object, moves it into `ECX`, and calls this row. The body calls `CAtmospheric__Link`, installs vtable `0x005e4f9c`, finds `Atmospherics/Clouds/Cloud.tga`, stores the texture reference at `this+0x0c`, allocates/configures a `CVBufTexture` at `this+0x08`, and registers `cg_cloudwidth` at `this+0x10`. |
| `0x0053ba20` | `CClouds__Shutdown` | `void __fastcall CClouds__Shutdown(void * this)` | Vtable slot `0x005e4f9c[4]`, dispatched from `Atmospherics__Shutdown` through virtual offset `+0x10`. The body releases the cloud texture reference through `CTexture__DecrementRefCountFromNameField(texture+8)`, destroys and frees the `CVBufTexture`, and clears both observed fields. |

Read-back evidence: `ApplyCCloudsHeadWave590.java` dry/apply/final dry reported `updated=0 skipped=2 renamed=0 would_rename=2 missing=0 bad=0`, then `updated=2 skipped=0 renamed=2 would_rename=0 missing=0 bad=0`, then `updated=0 skipped=2 renamed=0 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`. Post exports verified `2` metadata rows, `2` tag rows, `2` xref rows, `522` instruction rows, `2` target decompiles, `12` vtable rows, `30` callsite instruction rows, `99` proof instruction rows, and `81` shutdown-caller instruction rows.

Queue telemetry after the pass: `6093` total functions, `3021` commented, `3072` commentless, `1347` exact-undefined signatures, `1112` `param_N` signatures, comment-backed proxy `3021/6093 = 49.58%`, strict clean-signature proxy `2975/6093 = 48.83%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260519-122425_post_wave590_cclouds_head_verified`, `19` files, `160926599` bytes, manifest hash `31163c5c5f3d19d64d073d764769b9625270631f11a06d2ac1d6a9462f0cc898`.

## Boundary Notes

- Only vtable slot `0x005e4f9c[4]` is treated as proven for `CClouds__Shutdown`.
- Slots 0 and 3 point at raw addresses without function objects in the current read-back, and later vtable rows appear to leave the CClouds class boundary.
- Runtime cloud rendering, exact class layout, exact texture/CVBufTexture ownership semantics, full vtable boundary, BEA patching, and rebuild parity remain unproven.
