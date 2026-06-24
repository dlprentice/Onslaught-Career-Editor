# Texture/Mesh Asset Bridge Copied-Corpus Proof

Status: copied-corpus inventory/export proof complete, not runtime proof
Date: 2026-06-08
Scope: texture/resource/decode plus mesh asset bridge

This result closes the copied-corpus inventory/export slice selected by [texture-mesh-asset-bridge-proof-plan.md](texture-mesh-asset-bridge-proof-plan.md). It used the repo-local ignored `game/` mirror as read-only input and wrote all private generated outputs under the ignored root `subagents/texture_mesh_asset_bridge_proof_2026-06-08/`.

This is not a new static re-audit wave and it does not change the static percentage front door:

- Static Ghidra function-quality closure remains `6411/6411 = 100.00%`.
- Static debt remains `0 / 0 / 0`.
- Expanded post-100 static surface remains `1560/1560 = 100.00%`.
- Active current-risk focused accounting remains `1179/1179 = 100.00%`.
- Remaining active focused work remains `0`.

## Commands

Full copied-corpus export:

```powershell
py -3 tools\export_game_assets.py --game-root game --out-root subagents\texture_mesh_asset_bridge_proof_2026-06-08 --progress-every 50
```

Structured archive hash/chunk-count inventory:

```powershell
py -3 tools\aya_archive_inventory.py game\data\resources --glob *_res_PC.aya --resolve-assets --resource-root game\data\resources --json-out subagents\texture_mesh_asset_bridge_proof_2026-06-08\aya_archive_inventory.json
```

No `--limit-*` options and no `--skip-existing` were used for the proof-count run.

## Sanitized Counts

| Surface | Result |
| --- | --- |
| Ignored artifact root | `subagents/texture_mesh_asset_bridge_proof_2026-06-08/` |
| Artifact files / bytes | `8574` files, `250335133` bytes |
| Structured archive rows | `301` PC resource archives |
| Goodie archives | `232` `goodie_*_res_PC.aya` archives |
| Top-level archive chunks | `TEXT 18857`, `MESH 3492`, `GDIE 232`, `LVLR 301`, `TARG 301`, `AYAD 301` |
| Packed TEXT refs | `601/601` resolved |
| Packed reference MESH refs | `209/209` resolved |
| Packed GDIE texture refs | `206/206` resolved |
| Packed GDIE mesh refs | `42/42` resolved |
| Loose texture export lane | `847` attempted, `847` succeeded, `0` failed, `0` skipped |
| Loose mesh export lane | `213` attempted, `213` succeeded, `0` failed, `0` skipped |
| Embedded mesh export lane | `139` attempted, `139` succeeded, `0` failed, `0` skipped |
| Language rows | `2571` merged rows across `6` languages |
| Video manifest | `66` Bink files, `353110648` bytes |
| Catalog totals | `828` textures, `213` loose meshes, `139` embedded meshes, `66` videos, `2571` language rows, `233` goodies, `4050` total rows |
| Goodie families | `Artwork 149`, `Model 45`, `Video 34`, `Level 5` |

## What This Proves

- The copied corpus can be inventoried into structured archive hash/chunk records for `301` PC resource archives.
- Packed `TEXT`, reference `MESH`, and `GDIE` texture/mesh references resolve against copied/app-owned resource inputs with the counts above.
- The current backend extraction harness can export all loose textures, loose meshes, and embedded mesh bodies in separate lanes with zero failed and zero skipped rows.
- The catalog assembler can combine packed refs, texture/mesh export manifests, language rows, video manifest, and goodie rows into a deterministic `4050`-row catalog.

## What Remains Separate Proof

This is copied-corpus inventory/export proof only. It does not prove runtime parser behavior, runtime texture pixels, JPEG/inflate decode fidelity, exact layouts or ABI, Direct3D upload, GPU upload behavior, visual QA, native textured 3D rendering, material visual correctness, mesh skinning, animation, lighting, collision runtime behavior, BEA patching behavior, Godot parity, rebuild parity, or no-noticeable-difference parity.

Follow-up generated material/sidecar ledger proof is recorded in [texture-mesh-material-sidecar-ledger-proof.md](texture-mesh-material-sidecar-ledger-proof.md): `352/352` model rows with texture refs, `213` unique refs, `213` sidecar texture files, `0` missing sidecar refs, and `0` catalog-missing refs. Runtime material visual correctness and material/shader parity remain separate proof.
