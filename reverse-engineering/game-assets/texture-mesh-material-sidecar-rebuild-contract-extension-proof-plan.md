# Texture/Mesh Material Sidecar Rebuild Contract Extension Proof Plan

Status: complete static contract extension, not runtime proof
Date: 2026-06-10
Scope: `texture-mesh-material-sidecar-rebuild-contract-extension-proof-plan`

Proof plan name: Texture / Mesh Material Sidecar Rebuild Contract Extension Proof Plan

This contract extension follows the completed [Static-To-Proof Post-PhysicsScript Fixture Next Safe Slice Selection Refresh](../binary-analysis/static-to-proof-post-physics-script-fixture-next-safe-slice-selection-refresh.md). It turns the existing copied-corpus texture/mesh proof and material sidecar ledger into stable rebuild-facing vocabulary for clean-room importer planning.

Result schema: [texture-mesh-material-sidecar-rebuild-contract-extension-proof-plan.v1.json](texture-mesh-material-sidecar-rebuild-contract-extension-proof-plan.v1.json).

## Result

- `contractExtensionStatus=texture-mesh-material-sidecar-rebuild-contract-extension-complete-static-contract-extension-not-runtime-proof`
- `selectedNextSlice=Texture / Mesh Material Sidecar Rebuild Fixture Matrix Proof Plan`
- `selectedNextScope=texture-mesh-material-sidecar-rebuild-fixture-matrix-proof-plan`
- `sourceProofCount=5`
- `contractVocabularyTermCount=14`
- `modelRowsWithTextureRefs=352/352`
- `materialSidecarUniqueRefs=213`
- `materialSidecarFiles=213`
- `materialSidecarMissingRefs=0`
- `catalogMissingRefs=0`
- `ambiguousCatalogRefs=1`
- `embeddedDuplicateOutputBoundaryRows=32`
- `contractFalseGuardCount=39`
- `contractZeroCounterCount=33`
- `publicLeakCheck=PASS`

Static context remains `6411/6411 = 100.00%`, `0 / 0 / 0`, `1560/1560 = 100.00%`, `1179/1179 = 100.00%`, and `remainingActiveFocusedWork=0`.

## Source Evidence

This extension is grounded in tracked, public-safe aggregate evidence:

- [Texture/Mesh Asset Bridge Proof Plan](texture-mesh-asset-bridge-proof-plan.md)
- [Texture/Mesh Asset Bridge Copied-Corpus Proof](texture-mesh-asset-bridge-copied-corpus-proof.md)
- [Texture/Mesh Material Sidecar Ledger Proof](texture-mesh-material-sidecar-ledger-proof.md)
- [Mesh / Resource / Render Static Contract](../binary-analysis/mesh-resource-render-static-contract.md)
- [Texture Resource Decode Static Contract](../binary-analysis/texture-resource-decode-static-contract.md)

Copied-corpus bridge anchors:

- `301` structured PC resource archives.
- `232` goodie archives.
- Top-level chunks `TEXT 18857`, `MESH 3492`, and `GDIE 232`.
- Packed refs: `TEXT 601/601`, reference `MESH 209/209`, `GDIE` textures `206/206`, and `GDIE` meshes `42/42`.
- Export lanes: loose textures `847/847`, loose meshes `213/213`, embedded meshes `139/139`, with `0` failed and `0` skipped rows.
- Catalog rows: `4050`.

Material/sidecar ledger anchors:

- Ledger schema `asset-material-sidecar-ledger.v1`.
- Copied-corpus invariant `8574` files and `250335133` bytes.
- Model rows with texture refs `352/352`.
- Row families: loose `213` rows and embedded `139` rows.
- Texture references: `1268` model texture reference instances and `213` unique model texture refs.
- Sidecar coverage: `213` mesh texture sidecar files, `212` exact filename matches, and `1` stem-only match.
- Catalog coverage: `352/352` rows with all texture refs catalog-mapped, `0` catalog-missing refs, and `1` ambiguous catalog ref.
- Missing coverage: `0` missing sidecar rows and `0` unique refs missing sidecar coverage.
- Loose lane: `213` rows, `602` reference instances, and `213` unique refs.
- Embedded lane: `139` rows, `666` reference instances, and `28` unique refs.
- Duplicate-output boundary: `107` unique output files from `139` embedded rows, `28` duplicate-output groups, and `32` duplicate rows.

Static mesh/texture anchors:

- Wave1163 texture/decode evidence: `17` rows, `68` xref rows, `2779` instruction rows, and the boundary `JPEG Huffman separate from inflate Huffman`.
- Mesh/resource/render bridge counts: `352/352` material/texture-binding rows and `213/213` model texture sidecar refs covered.

## Contract Vocabulary

These terms are now the stable rebuild-facing vocabulary for the next fixture matrix:

| Term | Meaning |
| --- | --- |
| `model row` | One exported loose or embedded model catalog row that participates in texture linkage accounting. |
| `row family` | The row source family: `loose` or `embedded`. |
| `model texture reference instance` | One texture reference observed inside a model row after placeholder filtering. |
| `unique model texture ref` | A distinct compact texture reference name after linkage normalization. |
| `mesh texture sidecar file` | A generated sidecar texture file that can satisfy one or more model texture refs by exact filename or stem. |
| `exact filename match` | A sidecar coverage match where the normalized reference maps to the exact expected filename. |
| `stem-only match` | A sidecar coverage match where only the normalized stem maps cleanly. |
| `catalog-mapped ref` | A model texture ref with a matching texture row in the assembled asset catalog. |
| `catalog-missing ref` | A model texture ref with no catalog texture row; current count is `0`. |
| `missing sidecar ref` | A model texture ref with no local sidecar coverage; current count is `0`. |
| `ambiguous catalog ref` | A model texture ref with multiple catalog variants that must stay explicit; current count is `1`. |
| `duplicate-output group` | An embedded mesh output filename shared by more than one embedded row. |
| `duplicate row` | An embedded mesh row participating in a duplicate-output group. |
| `unique output file` | A distinct copied-output model file after row export. |

## Rebuild Contract

For clean-room importer planning, the next matrix should treat row coverage and output-file uniqueness as separate dimensions:

- Loose mesh rows have one-to-one row/output-file coverage: `213` rows and `213` unique output files.
- Embedded mesh rows have complete row coverage but non-unique output filenames: `139` rows and `107` unique output files.
- Sidecar coverage is measured by normalized texture reference coverage, not by visual material correctness.
- Catalog coverage is measured by texture-row linkage, not by runtime parser behavior.
- The single ambiguous catalog ref remains a named boundary, not a failure.
- The single stem-only sidecar match remains a named boundary, not an exact filename match.

## What This Proves

- The texture/mesh material sidecar evidence has a stable public-safe vocabulary for rebuild-facing schema and fixture work.
- The current copied-corpus and material sidecar counts can be bound to mesh, texture, sidecar, catalog, duplicate-output, and ambiguous-ref terms without committing private assets.
- The selected next child lane can build a fixture matrix from these terms without launching BEA, mutating Ghidra, starting Godot work, or implementing a renderer.

## What Remains Separate Proof

This is a static contract extension only. It does not prove runtime resource archive parser behavior, runtime texture parser behavior, runtime texture pixels, JPEG/inflate decode fidelity, runtime mesh loading, runtime mesh skinning, animation behavior, collision behavior, Direct3D upload, GPU behavior, native textured 3D rendering, material visual correctness, material/shader parity, asset format completeness, exact mesh/texture layouts, Godot parity, rebuild implementation, rebuild parity, or no-noticeable-difference parity.

Boundary token: runtimeExecution=false; beLaunch=false; newLaunch=false; screenshotCapture=false; privateFrameReviewPerformed=false; rowObservation=false; sourceSelectionObserved=false; sourceSelectionProven=false; nativeInput=false; debuggerAttachment=false; godotWork=false; ghidraMutation=false; executablePatching=false; productUiWired=false; rebuildImplementation=false; runtimeTextureParserBehaviorProven=false; runtimeTexturePixelsProven=false; runtimeJpegInflateDecodeFidelityProven=false; runtimeMeshLoadingProven=false; runtimeMeshSkinningProven=false; runtimeAnimationBehaviorProven=false; runtimeCollisionBehaviorProven=false; runtimeDirect3DUploadProven=false; runtimeGpuBehaviorProven=false; nativeTextured3DRenderingProven=false; materialVisualCorrectnessProven=false; materialShaderParityProven=false; visualQaComplete=false; cleanRoomRendererImplemented=false; assetFormatCompletenessProven=false; exactMeshTextureLayoutsProven=false; runtimeResourceArchiveParserProven=false; runtimeSidecarMaterialLoadProven=false; runtimeObjectIdentityProven=false; runtimeWorldLoadingProven=false; rebuildParityProven=false; noNoticeableDifferenceParityProven=false; privateAssetPublication=false; publicPrivateProofLeak=false; runtimeObservationRows=0; textureRuntimeEvidenceRows=0; meshRuntimeEvidenceRows=0; materialRuntimeEvidenceRows=0; materialVisualReviewRows=0; screenshotRows=0; privateFrameRowsObserved=0; rowObservationRows=0; sourceObservedRows=0; newLaunchRows=0; captureRows=0; ocrRows=0; rawDialogueRows=0; ghidraMutationRows=0; executablePatchRows=0; productUiRows=0; godotRows=0; rebuildImplementationRows=0; runtimeTexturePixelRows=0; runtimeMeshRenderRows=0; runtimeMaterialRows=0; runtimeCollisionRows=0; cleanRoomRendererRows=0; runtimeResourceArchiveParserRows=0; runtimeSidecarMaterialLoadRows=0; beProcessesAfterSelection=0.
