# Texture / Resource / Decode / Render Static Review

Status: static-coherent system slice
Date: 2026-05-26
Scope: `texture-render-static-review-wave904`

Wave904 reviews the texture/resource/decode/render chain after the loaded Ghidra function-quality queue reached `6113/6113 = 100.00%`. It ties the texture and render owner-family rows, the recent CDXTexture/CTexture/CFastVB/CVBufTexture hardening waves, and the current public asset-extraction counts into one static system classification.

Classification: `static-coherent texture/resource/decode/render core`.

Source/extractor boundary: Stuart's source and AYAResourceExtractor remain useful architecture/tooling references, but the authority for this review is the Steam retail binary as loaded in Ghidra plus the current local retail resource/extraction evidence.

## Function-Family Surface

The Wave904 evidence snapshot covers `1289` function rows across `25` selected texture/decode/render families. Every selected row has a non-empty comment and a clean signature with no exact-`undefined` return and no `param_N` placeholders.

| Family | Rows |
| --- | ---: |
| `CDXTexture` | 366 |
| `CFastVB` | 347 |
| `CTexture` | 233 |
| `CVBufTexture` | 40 |
| `CVBuffer` | 16 |
| `CIBuffer` | 13 |
| `CDXEngine` | 60 |
| `CEngine` | 55 |
| `CRenderQueue` | 18 |
| `D3DStateCache` | 11 |
| `CVertexShader` | 22 |
| Supporting texture/render families | 108 |

Representative anchors include `CDXTexture__LoadTextureFromFile_Core`, `CDXTexture__DecodeMemoryToTextureObject`, `CDXTexture__DecodeFromMemory_WithFallbackCodecs`, `CDXTexture__UploadDecodedBufferToSurface`, `CDXTexture__ValidateJpegFrameAndComputeMcuLayout`, `CDXTexture__ConvertYCbCrToRgb24_Mmx`, `CTexture__FindTexture`, `CTexture__ctor`, `CTexture__Release`, `CTexture__InitializeDecodePipelineFromHeader`, `CFastVB__RenderTriangleStripImmediate`, `CFastVB__InitDualTexelConversionPipeline`, `CFastVB__DispatchOp_ComposeTransformFromOptionalInputs_SIMD`, `CVBufTexture__DrawSpriteEx`, `CVBufTexture__Render`, `CVBufTexture__RenderModePass`, `CVBufTexture__RenderDynamicUnitPass`, `CVBuffer__Create`, `CIBuffer__CreateConfigured`, `CRenderQueue__RenderMultipassLayerA`, `D3DStateCache__UseDefaultRenderState`, `CEngine__TextureFormatIndexToD3D`, `CDXEngine__Render`, `CVertexShader__CompileScriptWithDirectiveParser`, and `CMeshRenderer__RenderMesh`.

## Asset/Resource Surface

The static binary review aligns with the current public-safe extraction posture:

| Asset signal | Current evidence |
| --- | ---: |
| PC resource archives | 301 |
| `goodie_*_res_PC.aya` archives | 232 |
| Loose textures exported | `847/847` |
| Loose meshes exported | `213/213` |
| Embedded packed mesh bodies exported | `139/139` |
| Packed `TEXT` refs resolved | `601/601` |
| Packed reference `MESH` refs resolved | `209/209` |
| `GDIE` texture refs resolved | `206/206` |
| `GDIE` mesh refs resolved | `42/42` |
| Model rows with readable material/texture-binding metadata | `352/352` |
| Model texture sidecar refs covered | `213/213` |

This is real installed-corpus/tooling evidence, but it is not a runtime-render claim.

## What This Proves

- The loaded Ghidra database has no remaining function-quality queue debt for the selected texture/resource/decode/render owner families.
- The current static documentation connects texture lookup/lifetime, DirectX texture load/decode/upload, image codec paths, texel pack/unpack, SIMD/math dispatch, vertex/index buffer ownership, CVBufTexture render paths, render-state cache paths, render-queue handoff, and mesh-renderer entry anchors.
- The current asset pipeline has public-safe count evidence for installed PC resource archives, texture/mesh/reference extraction, model metadata, and model texture linkage.
- The verified read-only Ghidra backup for this review is `[maintainer-local-ghidra-backup-root]\BEA_20260526-101300_post_wave904_texture_render_static_review_verified`.

## What Remains Separate

- Runtime texture decode pixels, GPU upload results, and Direct3D device behavior.
- Exact `CTexture`, `CDXTexture`, `CFastVB`, `CVBufTexture`, and Direct3D object layouts.
- Native textured/animated WinUI 3D rendering.
- In-game render correctness, animation behavior, material visual parity, and camera/render-state fidelity.
- Rebuild parity.
