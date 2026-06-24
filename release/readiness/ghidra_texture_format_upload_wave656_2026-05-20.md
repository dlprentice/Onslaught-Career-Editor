# Ghidra Texture Format / Upload Wave656 Readiness Note

Status: complete
Date: 2026-05-20

## Scope

Wave656 texture format/upload hardening covered eight adjacent texture-format selection and mapped-upload rows:

| Address | Saved signature |
| --- | --- |
| `0x00574270` | `int * __stdcall CDXTexture__FindFormatDescriptorById(int format_id)` |
| `0x00574296` | `uint __fastcall CFastVB__ComputeFormatMatchPenalty(void * requested_descriptor, void * candidate_descriptor)` |
| `0x0057430b` | `int __stdcall CDXTexture__SelectBestCompatibleFormat(void * format_id_list, int allow_mode_one_descriptor, void * requested_descriptor)` |
| `0x0057437a` | `int __stdcall CFastVB__SelectBestFormatHandler(void * device_or_null, uint usage_flags, int resource_type, void * requested_descriptor)` |
| `0x00574476` | `int __stdcall CDXTexture__MapFormatTokenToInternalCode(int format_token)` |
| `0x00574577` | `int __fastcall CFastVB__ReturnInputInt(int value)` |
| `0x0057457a` | `int __stdcall CDXTexture__LoadAndUploadMappedTexture_0057457a(void * target_ref, void * mode_flags, void * surface_ref, void * context_ref, void * fallback_ref)` |
| `0x00574645` | `void __stdcall Platform__LoadAndUploadMappedTextureWrapper(void * target_ref, void * mode_flags, void * unused_surface_ref, void * context_ref, void * fallback_ref)` |

The pass added bounded comments/tags with the `texture-format-upload-wave656` tag. It made no renames, no function-boundary changes, no executable-byte changes, no installed-game changes, and no runtime claims.

## Evidence

- Pre-state exports: `subagents/ghidra-static-reaudit/wave656-texture-format-upload/pre-metadata.tsv`, `pre-tags.tsv`, `pre-xrefs.tsv`, `pre-instructions.tsv`, and `decompile-pre/`.
- Apply script: `tools/ApplyTextureFormatUploadWave656.java`.
- Dry/apply/final dry:
  - Dry: `updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=8 missing=0 bad=0`.
  - Apply: `updated=8 skipped=0 renamed=0 would_rename=0 signature_updated=8 missing=0 bad=0`.
  - Final dry: `updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`.
- Post-state exports verified `8` metadata rows, `8` tag rows, `49` xref rows, `1768` instruction rows, and `8` clean decompile rows.
- Queue refresh passed with `6093` total functions, `3580` commented, `2513` commentless, `1217` exact-undefined signatures, and `728` `param_N` signatures.
- Comment-backed proxy: `3580/6093 = 58.76%`.
- Strict clean-signature proxy: `3530/6093 = 57.94%`.
- Verified backup: `G:\GhidraBackups\BEA_20260520-205422_post_wave656_texture_format_upload_verified` (`19` files, `163220359` bytes, `DiffCount=0`).
- Next high-signal queue head: `0x00574abb CDXTexture__RepeatCallbackN`.

## Bounded Claim

This proves saved static retail Ghidra metadata for the eight rows above: descriptor lookup/scoring/selection, token mapping, one retained-name identity callback, and the mapped-texture upload wrapper/helper band.

It does not prove exact texture descriptor schema, exact CFastVB owner/template identity, exact device interface identity, file/texture object ownership, runtime format selection/upload behavior, BEA patching, or rebuild parity.
