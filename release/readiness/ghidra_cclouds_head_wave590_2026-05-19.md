# Ghidra CClouds Head Wave590 Readiness Note

Date: 2026-05-19
Status: static saved-Ghidra evidence only

Wave590 hardened two adjacent `CClouds` rows at the current static re-audit queue head.

Saved rows:

| Address | Function |
| --- | --- |
| `0x0053b900` | `CClouds__Constructor` |
| `0x0053ba20` | `CClouds__Shutdown` |

What is proven:

- Ghidra now records clean signatures, comments, and `cclouds-head-wave590` tags for both rows.
- `0x0053b900` was renamed from `CClouds__ctor_like_0053b900` to `CClouds__Constructor`.
- `0x0053ba20` was renamed from `CClouds__VFunc_04_0053ba20` to `CClouds__Shutdown`.
- `Atmospherics__Init` allocates a `0x334` CClouds object, moves the allocation into `ECX`, and calls `CClouds__Constructor`.
- The constructor links the object through `CAtmospheric__Link`, installs vtable `0x005e4f9c`, finds `Atmospherics/Clouds/Cloud.tga`, allocates/configures a `CVBufTexture`, and registers `cg_cloudwidth`.
- Vtable evidence is bounded: slot `0x005e4f9c[4]` points to `CClouds__Shutdown`; `Atmospherics__Shutdown` dispatches each atmospheric object through virtual offset `+0x10`.
- `CClouds__Shutdown` releases the cloud texture reference through `CHud__DecrementCounter9C(texture+8)`, destroys/frees the `CVBufTexture`, and clears both observed fields.
- Post-save read-back verified 2 metadata rows, 2 tag rows, 2 xref rows, 522 instruction rows, 2 decompile rows, 12 vtable rows, 30 callsite instruction rows, 99 proof instruction rows, and 81 shutdown-caller instruction rows.
- The queue refresh reports `6093` total functions, `3021` commented, `3072` commentless, `1347` exact-undefined signatures, and `1112` `param_N` signatures.
- Comment-backed proxy is `3021/6093 = 49.58%`; strict clean-signature proxy is `2975/6093 = 48.83%`.
- The next high-signal queue head is `0x0053bb50 CDXEngine__RenderOptionalFullscreenEffectPass`.
- The live Ghidra project backup verified at `G:\GhidraBackups\BEA_20260519-122425_post_wave590_cclouds_head_verified` with 19 files, 160926599 bytes, `DiffCount=0`, and manifest hash `31163c5c5f3d19d64d073d764769b9625270631f11a06d2ac1d6a9462f0cc898`.

What is not proven:

- Runtime cloud rendering behavior remains unproven.
- Exact source identity remains unproven because no matching tracked Stuart source implementation body was found for this wave.
- Exact `CClouds`, `CAtmospheric`, `CTexture`, `CVBufTexture`, and console-variable field layouts remain unproven beyond the observed fields documented in the read-back notes.
- The full vtable/class boundary remains unproven beyond observed slot `0x005e4f9c[4]` and the recorded raw slots.
- BEA patching, gameplay behavior, and rebuild parity remain unproven.
