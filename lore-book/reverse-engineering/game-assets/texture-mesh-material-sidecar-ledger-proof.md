# Texture/Mesh Material Sidecar Ledger Proof

Status: generated material/sidecar ledger proof complete, not runtime proof
Date: 2026-06-08
Scope: texture/material sidecar linkage for exported model rows

This result follows [texture-mesh-asset-bridge-copied-corpus-proof.md](texture-mesh-asset-bridge-copied-corpus-proof.md). It reads the existing ignored copied-corpus proof root, uses the public-safe `tools/model_texture_linkage_probe.py` semantics for model texture linkage, and writes the generated material/sidecar ledger to a separate ignored root at `subagents/texture_mesh_material_sidecar_ledger_2026-06-08/asset-material-sidecar-ledger.json`.

This is not a new static re-audit wave and it does not change the static percentage front door:

- Static Ghidra function-quality closure remains `6411/6411 = 100.00%`.
- Static debt remains `0 / 0 / 0`.
- Expanded post-100 static surface remains `1560/1560 = 100.00%`.
- Active current-risk focused accounting remains `1179/1179 = 100.00%`.
- Remaining active focused work remains `0`.

## Command

```powershell
py -3 tools\texture_mesh_material_sidecar_ledger.py --proof-root subagents\texture_mesh_asset_bridge_proof_2026-06-08 --out subagents\texture_mesh_material_sidecar_ledger_2026-06-08\asset-material-sidecar-ledger.json --check
```

## Sanitized Counts

| Surface | Result |
| --- | --- |
| Ledger schema | `asset-material-sidecar-ledger.v1` |
| Copied-corpus proof root invariant | `8574` files, `250335133` bytes |
| Model rows with texture refs | `352/352` |
| Model row families | loose `213` rows, embedded `139` rows |
| Model texture reference instances | `1268` |
| Unique model texture refs | `213` |
| Mesh texture sidecar files | `213` |
| Unique refs with exact sidecar filename | `212` |
| Unique refs with stem-only sidecar match | `1 stem-only` |
| Rows with all texture refs catalog-mapped | `352/352` |
| Rows with missing sidecar refs | `0` missing sidecar rows |
| Unique refs missing sidecar coverage | `0` missing sidecar refs |
| Unique refs missing catalog rows | `0` catalog-missing refs |
| Ambiguous catalog refs | `1` ambiguous catalog ref |
| Loose mesh lane | `213` rows, `602` texture-ref instances, `213` unique refs |
| Embedded mesh lane | `139` rows, `666` texture-ref instances, `28` unique refs |
| Embedded mesh duplicate-output caveat | `107` unique output files from `139` rows, `28` duplicate-output groups, `32` duplicate rows |

## What This Proves

- The generated material/sidecar ledger can be rebuilt from the copied-corpus catalog and exported FBX files without committing private models, textures, or absolute paths.
- Every checked loose and embedded model row has non-template texture references.
- Every unique checked model texture reference resolves to a local mesh texture sidecar by exact filename or stem.
- Every checked model row has texture refs mapped to catalog texture rows after the current placeholder filtering and compact-name matching.
- Embedded mesh rows can share copied-output filenames; this ledger records row coverage separately from unique output-file count.

## What Remains Separate Proof

This is generated material/sidecar ledger proof only. It does not prove runtime parser behavior, runtime texture pixels, JPEG/inflate decode fidelity, exact layouts or ABI, Direct3D upload, GPU upload behavior, visual QA, native textured 3D rendering, material visual correctness, material/shader parity, mesh skinning, animation, lighting, collision runtime behavior, BEA patching behavior, Godot parity, rebuild parity, or no-noticeable-difference parity.
