# Ghidra CDXTexture Image Codec Wave662 Readiness Note

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 live correction closeout:** Historical record; `0x0057c28b` comment correction. The original text below remains provenance rather than current semantic authority. It is superseded only where confirmed. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); final per-address decisions and exact before/after metadata are in `reverse-engineering/binary-analysis/ghidra-reviewed-correction-decisions-2026-07-13.jsonl` and `reverse-engineering/binary-analysis/ghidra-reviewed-correction-plan-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Date: 2026-05-21

## Scope

Wave662 CDXTexture image codec hardening saved static Ghidra signatures, comments, and tags for 21 adjacent CDXTexture image codec, surface-node, descriptor, stream-write, and DXT block-copy rows with the `cdxtexture-image-codec-wave662` and `wave662-readback-verified` tags:

- `0x00579b39 CDXTexture__LookupNamedFormatDescriptor`
- `0x00579bd5 CDXTexture__SetD3D9DebugMute`
- `0x00579ca5 CDXTexture__InitSurfaceNodeZeroed`
- `0x00579cbe CDXTexture__FreeSurfaceNodeTree`
- `0x00579d17 CDXTexture__SurfaceNode_scalar_deleting_dtor`
- `0x00579d33 CDXTexture__InitSurfaceFormatInfoFromDescriptor`
- `0x00579e08 CDXTexture__DecodeBmpDibFromMemory`
- `0x0057a934 CDXTexture__WriteSurfaceAsBmpToHandle`
- `0x0057af0a CDXTexture__DecodeJpegFromMemory`
- `0x0057b182 CDXTexture__DecodeTgaFromMemory`
- `0x0057b6fa CDXTexture__DecodePpmFromMemory`
- `0x0057b9ce CDXTexture__DecodePngFromMemory`
- `0x0057bf1f CDXTexture__BuildDdsSurfaceNodeTree`
- `0x0057c28b CDXTexture__WriteDdsSurfaceChainToHandle`
- `0x0057c57d CDXTexture__FlushStreamWriteBufferChunk`
- `0x0057c5b2 CDXTexture__FlushStreamWriteBufferTail`
- `0x0057c5dc CDXTexture__EncodeRgbBufferToJpegStream`
- `0x0057ca3a CDXTexture__DecodeBmpFromMemory`
- `0x0057cc53 CDXTexture__InitMappedFileContext`
- `0x0057cc5d CDXTexture__ReleaseSurfacePairIfPresent`
- `0x0057cf60 CDXTexture__CopyDxtBlockRegion`

No renames, function-boundary changes, executable-byte changes, runtime probes, or BEA patching were performed in this wave.

## Evidence

Accepted Wave662 Ghidra evidence is under `subagents/ghidra-static-reaudit/wave662-cdxtexture-image-codec/`.

- Patched dry run: `apply-wave662-dry2.log` reported `updated=0 skipped=21 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`.
- Accepted apply run: `apply-wave662-apply2.log` reported `updated=21 skipped=0 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`.
- Final dry run: `apply-wave662-final-dry.log` reported `updated=0 skipped=21 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`.
- All accepted runs reported `REPORT: Save succeeded`.
- Post exports verified `21` metadata rows, `21` tag rows, `59` xref rows, `2793` instruction rows, and `21` clean decompile rows.

An earlier apply-script read-back matcher run reported `bad=10` after saving partial metadata because the script omitted explicit `this` parameters in the expected `__thiscall` signatures. The script was patched, rerun, and superseded by the accepted `dry2` / `apply2` / `final-dry` sequence above.

## Queue Impact

Post-Wave662 queue telemetry:

- `6098` total functions
- `3644` commented functions
- `2454` commentless functions
- `1217` exact-undefined signatures
- `673` `param_N` signatures
- Comment-backed proxy: `3644/6098 = 59.76%`
- Strict clean-signature proxy: `3594/6098 = 58.94%`
- Next queue head: `0x0057c7a4 CMeshCollisionVolume__LoadMappedTextureResourcesByMode`

Delta from Wave661: `+21` commented functions, `-21` commentless functions, exact-undefined signatures unchanged, and `-21` `param_N` signatures.

## Backup

Verified post-wave backup:

```text
[maintainer-local-ghidra-backup-root]\BEA_20260521-001158_post_wave662_cdxtexture_image_codec_verified
```

Backup manifest comparison: `19` files, `163449735` bytes, `DiffCount=0`.

## Boundaries

This note proves saved static retail Ghidra metadata and read-back evidence only. Exact CDXTexture, surface-node, descriptor, stream-writer, COM/D3D, DDS, BMP, TGA, PPM, PNG, JPEG, DXT copy-context, and mapped-file layouts remain unproven. Runtime image fidelity, runtime upload/export behavior, runtime codec-library ABI, BEA patching, and rebuild parity remain deferred.
