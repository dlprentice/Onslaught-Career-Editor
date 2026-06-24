# Texture/Mesh Asset Bridge Proof Plan

Status: active public-safe proof plan, not runtime proof
Last updated: 2026-06-08
Scope: texture/resource/decode plus mesh asset bridge

This plan is the first selected slice from `roadmap/static-to-proof-rebuild-transition-backlog.md` after static closeout. It converts the static texture/resource/decode and mesh/resource/render contracts into a deterministic manifest and copied-output inventory plan. It does not launch BEA, mutate Ghidra, mutate the installed game, create runtime screenshots, start Godot work, or claim rebuild parity.

## Static Authority

Current static closeout remains unchanged:

- Static Ghidra function-quality closure: `6411/6411 = 100.00%`.
- Static debt: `0 / 0 / 0` commentless, exact-undefined, and `param_N` rows.
- Expanded post-100 static surface: `1560/1560 = 100.00%`.
- Active current-risk focused accounting: `1179/1179 = 100.00%`.
- Remaining active focused work: `0`.
- Wave911 focused remains historical-retired/non-reconstructable at `812/1408 = 57.67%`; it is not the active completion gate.

The percentage front door remains `reverse-engineering/binary-analysis/static-reaudit-measurement-register.md` and `reverse-engineering/binary-analysis/static-reaudit-progress.json`. This proof plan does not create a new static RE percentage.

Primary static contract sources:

- `reverse-engineering/binary-analysis/texture-resource-decode-static-contract.md`.
- `reverse-engineering/binary-analysis/mesh-resource-render-static-contract.md`.
- `reverse-engineering/game-assets/extraction-pipeline.md`.
- `reverse-engineering/quick-reference/aya-tags.md`.
- `reverse-engineering/quick-reference/aya-resource-chunks.md`.

Relevant retained evidence tokens:

- Wave1163 texture/decode current-risk evidence: `17` rows, `68` xref rows, `2779` instruction rows, and `17` decompile rows.
- Texture contract boundary: JPEG Huffman separate from inflate Huffman.
- Existing private corpus counts: `301` PC resource archives, `232` goodie archives, top-level chunks `TEXT 18857`, `MESH 3492`, and `GDIE 232`.
- Existing export/catalog coverage: `847/847` loose textures, `213/213` loose meshes, `139/139` embedded packed mesh bodies, and `4050` catalog rows.
- Existing packed reference bridge counts: `TEXT 601/601`, reference `MESH 209/209`, `GDIE` textures `206/206`, and `GDIE` meshes `42/42`.
- Existing model bridge counts: `352/352` model material/texture-binding metadata rows and `213/213` unique model texture sidecar references.

## Allowed Inputs And Outputs

Inputs must be copied/app-owned or read-only:

- Preferred full proof input: a copied `data/Resources` tree or an app-owned private game mirror treated as read-only for the run.
- Public-safe fixture input: synthetic manifests from `py -3 tools\export_asset_catalog.py --self-test`.
- Stuart source and AYAResourceExtractor can explain tool behavior, but retail manifests and saved Ghidra evidence remain authority.

Outputs must stay in an ignored/app-owned root, for example:

```text
subagents/texture_mesh_asset_bridge_proof_2026-06-08/
```

Expected output layout for a full copied-corpus run:

```text
aya_asset_manifest.json
aya_embedded_meshes/
asset_export/
language_export/
video_manifest/
asset_catalog/
logs/
extraction_summary.json
```

The installed Steam directory and original `BEA.exe` remain read-only source material. Do not commit private assets, raw manifests containing private paths, screenshots, frames, copied executables, copied saves, or generated proof artifacts.

## Proof Rows

| Row | Planned proof item | Validation gate | Public-safe result |
| --- | --- | --- | --- |
| 1 | Static contract binding | Probe verifies this plan cites Wave1220 closeout numbers, Wave1163 texture/decode evidence, mesh/resource/render evidence, and the transition backlog. | Selected slice is static-to-proof planning only. |
| 2 | Resource archive inventory | Later copied-corpus run writes `aya_asset_manifest.json` from `tools/aya_archive_inventory.py` with archive hashes, chunk counts, and packed-ref summaries. | Manifest count bridge, not runtime parser proof. |
| 3 | TEXT/MESH/GDIE reference bridge | Compare manifest summary to `TEXT 601/601`, reference `MESH 209/209`, `GDIE` textures `206/206`, and `GDIE` meshes `42/42`. | Resource references resolve against copied/app-owned inputs. |
| 4 | Texture/mesh export inventory | Later copied-corpus run uses `tools/export_game_assets.py` without `--limit-*` and without `--skip-existing`, unless a separate hash ledger proves pre-existing outputs. | Export counts are deterministic copied-output evidence. |
| 5 | Catalog assembly bridge | Public gate runs `py -3 tools\export_asset_catalog.py --self-test`; copied-corpus gate checks `asset_catalog/summary.json` and split JSON outputs. | Catalog assembly is verified without private assets first. |
| 6 | Material/sidecar ledger schema | Generate and validate [texture-mesh-material-sidecar-ledger-proof.md](texture-mesh-material-sidecar-ledger-proof.md) from the copied-corpus catalog and exported FBX files. | Material sidecar linkage is proven for generated rows; runtime material visual correctness remains separate proof. |
| 7 | Boundary check | Probe rejects runtime, visual, GPU, patch, Godot, and parity wording. | No runtime pixel, GPU upload, visual QA, or parity claim. |

## Later Copied-Corpus Command Shape

The later full proof run should use an explicit output root and avoid date-default ambiguity:

```powershell
py -3 tools\export_game_assets.py --game-root <copied-or-app-owned-game-root> --out-root subagents\texture_mesh_asset_bridge_proof_2026-06-08 --progress-every 50
```

If a smaller diagnostic run is needed, it must be labeled as diagnostic and must not update coverage counts. A full proof count run should avoid `--limit-archives`, `--limit-loose-textures`, `--limit-loose-meshes`, `--limit-embedded-bodies`, and `--skip-existing` unless a separate validation ledger records why skipped existing outputs are still trustworthy.

## Not Claimed

This plan proves a static-bound, copied-corpus proof plan and deterministic manifest/count bridge for resource archive and catalog surfaces. It does not prove runtime parser behavior, runtime texture pixels, JPEG/inflate decode fidelity, exact layouts or ABI, Direct3D upload, visual QA, BEA patching behavior, gameplay behavior, rebuild parity, or no-noticeable-difference parity.

This plan also does not prove native textured 3D rendering, mesh skinning, animation, lighting, material-to-texture visual correctness, collision runtime behavior, camera fidelity, or Godot parity.

## Copied-Corpus Proof Result

The copied-corpus inventory/export proof completed on 2026-06-08 and is recorded in [texture-mesh-asset-bridge-copied-corpus-proof.md](texture-mesh-asset-bridge-copied-corpus-proof.md). The copied-corpus result remains copied-corpus inventory/export proof only. The generated material/sidecar ledger proof is recorded in [texture-mesh-material-sidecar-ledger-proof.md](texture-mesh-material-sidecar-ledger-proof.md). These results are copied-corpus inventory/export and material/sidecar linkage proof only, not runtime parser, pixel, GPU, visual, patch, Godot, rebuild, or no-noticeable-difference proof.

Sanitized result anchors: `301` structured archive rows, `232` goodie archives, `TEXT 18857`, `MESH 3492`, `GDIE 232`, packed refs `TEXT 601/601`, reference `MESH 209/209`, `GDIE` textures `206/206`, `GDIE` meshes `42/42`, export lanes `847/847`, `213/213`, and `139/139` with `0` failed and `0` skipped rows, `4050` catalog rows, and material/sidecar ledger counts `352/352` model rows, `213` unique refs, `213` sidecar files, `0` missing sidecar refs, and `0` catalog-missing refs.

## Exit Gate For This Planning Slice

This planning slice is complete only when:

- This document and its lore-book mirror match.
- `roadmap/static-to-proof-rebuild-transition-backlog.md`, `reverse-engineering/binary-analysis/mapped-systems.md`, and `reverse-engineering/game-assets/_index.md` point to this plan.
- `tools/texture_mesh_asset_bridge_proof_plan_probe.py --check` passes.
- `py -3 tools\export_asset_catalog.py --self-test` passes.
- Static closeout probes still pass without changing `static-reaudit-progress.json` or `static-reaudit-current-risk-ledger.json`.

After that, the next executable slice can run the copied-corpus inventory/export proof under an ignored/app-owned output root.
