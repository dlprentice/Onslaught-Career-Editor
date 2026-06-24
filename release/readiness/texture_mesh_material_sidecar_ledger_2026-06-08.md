# Texture/Mesh Material Sidecar Ledger Readiness Note

Status: generated material/sidecar ledger proof complete, not runtime proof
Date: 2026-06-08
Scope: texture/material sidecar linkage for exported model rows

The material/sidecar ledger slice generated `asset-material-sidecar-ledger.v1` from the ignored copied-corpus proof root and wrote the ledger under a separate ignored root:

```powershell
py -3 tools\texture_mesh_material_sidecar_ledger.py --proof-root subagents\texture_mesh_asset_bridge_proof_2026-06-08 --out subagents\texture_mesh_material_sidecar_ledger_2026-06-08\asset-material-sidecar-ledger.json --check
```

This is not a new static re-audit wave. Static Ghidra function-quality closure remains `6411/6411 = 100.00%`, static debt remains `0 / 0 / 0`, expanded post-100 static surface remains `1560/1560 = 100.00%`, active current-risk focused accounting remains `1179/1179 = 100.00%`, and Remaining active focused work remains `0`.

Sanitized evidence:

| Surface | Result |
| --- | --- |
| Ledger path | `subagents/texture_mesh_material_sidecar_ledger_2026-06-08/asset-material-sidecar-ledger.json` |
| Copied-corpus proof root invariant | `8574` files, `250335133` bytes |
| Model rows with texture refs | `352/352` |
| Model row families | loose `213` rows, embedded `139` rows |
| Model texture reference instances | `1268` |
| Unique model texture refs / sidecar files | `213` / `213` |
| Sidecar match shape | `212` exact filename, `1 stem-only` |
| Missing sidecar / catalog rows | `0` missing sidecar, `0` catalog-missing |
| Ambiguous catalog refs | `1` ambiguous catalog ref |
| Loose mesh lane | `213` rows, `602` texture-ref instances, `213` unique refs |
| Embedded mesh lane | `139` rows, `666` texture-ref instances, `28` unique refs |
| Embedded mesh duplicate-output caveat | `107` unique output files from `139` rows, `28` duplicate-output groups, `32` duplicate rows |

What this proves:

- The generated material/sidecar ledger can be rebuilt from the copied-corpus catalog and exported FBX files without committing private models, textures, or absolute paths.
- Every checked loose and embedded model row has non-template texture references.
- Every unique checked model texture reference resolves to a local mesh texture sidecar by exact filename or stem.
- Every checked model row has texture refs mapped to catalog texture rows after current placeholder filtering and compact-name matching.
- Embedded mesh rows can share copied-output filenames; this ledger records row coverage separately from unique output-file count.

What remains separate proof:

- Runtime parser behavior.
- Runtime texture pixels.
- JPEG/inflate decode fidelity.
- Exact layouts or ABI.
- Direct3D upload or GPU upload behavior.
- Visual QA, native textured 3D rendering, material visual correctness, material/shader parity, mesh skinning, animation, lighting, or collision runtime behavior.
- BEA patching behavior, Godot parity, rebuild parity, or no-noticeable-difference parity.

This is generated material/sidecar ledger proof only.
