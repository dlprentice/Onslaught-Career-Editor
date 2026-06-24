# Ghidra Texel Profile Prep Wave667 Readiness

Status: ready for public-safe release accounting
Date: 2026-05-21

## Scope

Wave667 texel-profile prep saved static Ghidra metadata for ten adjacent texel profile preparation rows after Wave666:

| Address | Saved name | Saved signature |
| --- | --- | --- |
| `0x00581263` | `CFastVB__TexelUnpackProfile__dtor` | `void __fastcall CFastVB__TexelUnpackProfile__dtor(void * this)` |
| `0x00581279` | `CFastVB__ConvertTexelVectorDomain` | `int __thiscall CFastVB__ConvertTexelVectorDomain(void * this, float * source_vec4_array, int unused_context)` |
| `0x0058183d` | `CFastVB__TexelCodecProfile__dtor` | `void __fastcall CFastVB__TexelCodecProfile__dtor(void * this)` |
| `0x005818b7` | `CDXTexture__PrepareDxtScaleAndQuantizedUV` | `void __fastcall CDXTexture__PrepareDxtScaleAndQuantizedUV(void * texture_context)` |
| `0x005819b8` | `CFastVB__LookupCurveFromRsqrtScaledInput` | `double __stdcall CFastVB__LookupCurveFromRsqrtScaledInput(float sample_value)` |
| `0x00581a08` | `CFastVB__LookupCurveFromSquaredInput` | `double __stdcall CFastVB__LookupCurveFromSquaredInput(float sample_value)` |
| `0x00581cc0` | `CFastVB__TexelUnpackProfile__InitConversionScratch` | `int __thiscall CFastVB__TexelUnpackProfile__InitConversionScratch(void * this, void * peer_profile, int unused_context)` |
| `0x00581d49` | `CDXTexture__ProbeTexelProfileSample` | `void __fastcall CDXTexture__ProbeTexelProfileSample(void * texel_profile)` |
| `0x00581e1c` | `CFastVB__TexelUnpackProfile__ZeroTexelsMatchingKeyColor` | `void __thiscall CFastVB__TexelUnpackProfile__ZeroTexelsMatchingKeyColor(void * this, float * texel_vec4_array, uint unused_context)` |
| `0x00581e8c` | `CDXTexture__NormalizeAndCopyVec4Array` | `int __thiscall CDXTexture__NormalizeAndCopyVec4Array(void * this, float * source_vec4_array, int unused_context)` |

Tag anchors: `texel-profile-prep-wave667`, `wave667-readback-verified`, `static-reaudit`, `retail-binary-evidence`, `signature-hardened`, and `comment-hardened`.

Probe anchors: `0x00581263 CFastVB__TexelUnpackProfile__dtor`, `0x00581e8c CDXTexture__NormalizeAndCopyVec4Array`, and next queue head `0x0058210e CTexture__PostProcessDecodedTexels_GammaOrSquare`.

## Evidence

- Dry mode: `updated=0 skipped=10 renamed=0 would_rename=0 signature_updated=10 missing=0 bad=0`
- Apply mode: `updated=10 skipped=0 renamed=0 would_rename=0 signature_updated=10 missing=0 bad=0`
- Final dry mode: `updated=0 skipped=10 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`
- All three passes reported `REPORT: Save succeeded`.
- Post exports verified `10` metadata rows, `10` tag rows, `180` xref rows, `870` instruction rows, and `10` clean decompile rows.
- Backup verified: `G:\GhidraBackups\BEA_20260521-021208_post_wave667_texel_profile_verified`, `19` files, `163646343` bytes, `DiffCount=0`.

## Queue

Post-Wave667 queue telemetry:

- Total functions: `6098`
- Commented functions: `3689`
- Commentless functions: `2409`
- Exact-undefined signatures: `1217`
- `param_N` signatures: `628`
- Comment-backed proxy: `3689/6098 = 60.50%`
- Strict clean-signature proxy: `3639/6098 = 59.68%`
- Next queue head: `0x0058210e CTexture__PostProcessDecodedTexels_GammaOrSquare`

## Boundaries

This is static metadata evidence only. Exact texel-profile/profile ABI, texel-domain enum, color-space meaning, DXT format contract, curve identity, callback contract, runtime texture conversion behavior, runtime transparency behavior, BEA patching, and rebuild parity remain unproven.
