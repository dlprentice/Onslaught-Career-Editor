# Ghidra Texture / Resource / Decode / Render Static Review Wave904 Readiness Note

Status: complete static review evidence
Date: 2026-05-26
Scope: `texture-render-static-review-wave904`

Wave904 is a read-only post-100 system review. It makes no Ghidra metadata mutation, no executable-byte change, no save mutation, and no BEA launch. The wave records a `static-coherent texture/resource/decode/render core` after the loaded Ghidra function-quality queue reached `6113/6113 = 100.00%`.

Authority boundary: Stuart's source and AYAResourceExtractor are helpful references, not proof for the Steam retail binary or original PC resource corpus. The evidence below is grounded in the loaded Ghidra database and current local retail extraction manifests.

Evidence summary:

- Selected function rows: `1289` rows across `25` families, all commented and clean-signature.
- Large family anchors: `CDXTexture` `366`, `CFastVB` `347`, `CTexture` `233`, `CVBufTexture` `40`.
- Representative functions: `CDXTexture__LoadTextureFromFile_Core`, `CDXTexture__DecodeMemoryToTextureObject`, `CDXTexture__ValidateJpegFrameAndComputeMcuLayout`, `CFastVB__RenderTriangleStripImmediate`, `CVBufTexture__DrawSpriteEx`, `CVBufTexture__RenderDynamicUnitPass`, `CDXEngine__Render`, and `CMeshRenderer__RenderMesh`.
- Asset extraction bridge: `847/847` loose textures, `213/213` loose meshes, `139/139` embedded meshes, `352/352` model rows with readable material/texture-binding metadata, and `213/213` model texture sidecar refs covered.
- Verified read-only Ghidra backup: `G:\GhidraBackups\BEA_20260526-101300_post_wave904_texture_render_static_review_verified`, `19` files, `173247367` bytes, `DiffCount=0`.

What this proves:

- The selected texture/resource/decode/render owner-family rows are closed under the current function-quality proxy.
- The public docs now review texture lookup/lifetime, DirectX texture load/decode/upload, JPEG/PNG/DXT/image codec paths, CFastVB math/dispatch, CVBuffer/CIBuffer/CVBufTexture buffer/render paths, render-state cache, render queue, and asset-extraction count evidence as one static system slice.
- The claim is static coherence, not runtime rendering parity.

What remains unproven:

- Runtime texture decode pixels.
- GPU upload/device behavior.
- Exact internal object layouts.
- Native textured/animated WinUI rendering.
- In-game render correctness.
- Clean-room rebuild parity.
