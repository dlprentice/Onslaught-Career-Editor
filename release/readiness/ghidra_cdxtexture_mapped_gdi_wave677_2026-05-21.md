# Ghidra CDXTexture Mapped/GDI Wave677 Readiness Note

Date: 2026-05-21

## Scope

Wave677 CDXTexture mapped/GDI saved static Ghidra metadata for seven adjacent CDXTexture mapped-file context and GDI cleanup helpers from `0x0058864a CDXTexture__InitMappedFileContext` through `0x005888ae CDXTexture__DeleteGdiObjectIfSet`.

The pass used the `cdxtexture-mapped-gdi-wave677` and `wave677-readback-verified` tags. It made no renames, no function-boundary changes, no executable-byte changes, and no runtime decode/export claim.

## Evidence

- Dry/apply/final dry summaries:
  - `updated=0 skipped=7 renamed=0 would_rename=0 signature_updated=7 missing=0 bad=0`
  - `updated=7 skipped=0 renamed=0 would_rename=0 signature_updated=7 missing=0 bad=0`
  - `updated=0 skipped=7 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`
- Post exports verified `7` metadata rows, `7` tag rows, `15` xref rows, `623` instruction rows, and `7` clean decompile rows.
- Queue after Wave677: `6098` total, `3835` commented, `2263` commentless, `1217` exact-undefined signatures, `482` `param_N` signatures, strict clean-signature proxy `3785/6098 = 62.07%`.
- Next queue head: `0x00588cc6 CDXTexture__ProjectPointToPlaneAndScale`.
- Verified Ghidra backup: `G:\GhidraBackups\BEA_20260521-064643_post_wave677_cdxtexture_mapped_gdi_verified`, `19` files, `164334471` bytes, `DiffCount=0`.

## Boundaries

Wave677 proves saved static retail Ghidra name/signature/comment/tag evidence for the observed CDXTexture mapped-file and GDI cleanup tranche. Exact mapped-file context layout, path encoding policy, output mode contract, GDI object ownership, runtime texture decode/export behavior, BEA patching, and rebuild parity remain deferred.

Probe anchors: `Wave677 CDXTexture mapped/GDI`, `cdxtexture-mapped-gdi-wave677`, `0x0058864a CDXTexture__InitMappedFileContext`, `0x005888ae CDXTexture__DeleteGdiObjectIfSet`, `0x00588cc6 CDXTexture__ProjectPointToPlaneAndScale`.
