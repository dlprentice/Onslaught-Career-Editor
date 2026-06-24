# Texture/Mesh Asset Bridge Copied-Corpus Proof Readiness Note

Status: copied-corpus inventory/export proof complete, not runtime proof
Date: 2026-06-08
Scope: `texture-mesh-asset-bridge-copied-corpus-proof`

This note records the first post-static static-to-proof slice after Wave1220 closeout. It is a public-safe sanitized evidence packet for copied-corpus inventory/export proof only. It is not a new static re-audit wave. Raw generated outputs remain ignored under `subagents/texture_mesh_asset_bridge_proof_2026-06-08/`.

Static counters remain unchanged: `6411/6411 = 100.00%`, `0 / 0 / 0`, `1560/1560 = 100.00%`, `1179/1179 = 100.00%`, and remaining active focused work `0`.
Remaining active focused work remains `0`.

Commands:

- `py -3 tools\export_game_assets.py --game-root game --out-root subagents\texture_mesh_asset_bridge_proof_2026-06-08 --progress-every 50`
- `py -3 tools\aya_archive_inventory.py game\data\resources --glob *_res_PC.aya --resolve-assets --resource-root game\data\resources --json-out subagents\texture_mesh_asset_bridge_proof_2026-06-08\aya_archive_inventory.json`

Evidence counts:

- Artifact root: `8574` files, `250335133` bytes.
- Structured archive inventory: `301` PC resource archives, including `232` `goodie_*_res_PC.aya` archives.
- Top-level chunk totals: `TEXT 18857`, `MESH 3492`, `GDIE 232`, `LVLR 301`, `TARG 301`, `AYAD 301`.
- Packed-reference bridge: `TEXT 601/601`, reference `MESH 209/209`, `GDIE` textures `206/206`, `GDIE` meshes `42/42`.
- Export lanes: loose textures `847/847`, loose meshes `213/213`, embedded meshes `139/139`, with `0` failed and `0` skipped rows in each lane.
- Catalog: `828` texture rows, `213` loose mesh rows, `139` embedded mesh rows, `66` video rows, `2571` language rows, `233` goodie rows, and `4050` total rows.

What this proves:

- Structured archive hash/chunk-count inventory can be generated for the copied corpus.
- Packed resource references resolve against copied/app-owned resource inputs with the recorded counts.
- The backend extraction harness exports the texture/mesh inventory lanes without failed or skipped rows.
- The asset catalog assembler produces a deterministic `4050`-row catalog from the copied-corpus manifests.

What remains separate proof:

- Runtime parser behavior.
- Runtime texture pixels or JPEG/inflate decode fidelity.
- GPU upload, Direct3D behavior, visual QA, native textured 3D rendering, material visual correctness, skinning, animation, lighting, collision behavior.
- BEA patching behavior.
- Godot parity.
- Rebuild parity and no-noticeable-difference parity.

Follow-up generated material/sidecar ledger proof is recorded in `reverse-engineering/game-assets/texture-mesh-material-sidecar-ledger-proof.md`: `352/352` model rows with texture refs, `213` unique refs, `213` sidecar texture files, `0` missing sidecar refs, and `0` catalog-missing refs. Runtime material visual correctness and material/shader parity remain separate proof.
