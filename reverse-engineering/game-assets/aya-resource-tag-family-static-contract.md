# AYA resource tag families

Status: active, bounded retail dispatcher vocabulary
Last updated: 2026-09-27
Summary: corrects tag roles from the retail dispatcher; recognition is not a complete payload schema.
Evidence: MEASURED — September 27 literal-selected retail calls; SOURCE — pinned ResourceAccumulator.cpp with recorded platform differences.
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

The [chunk-reader and dispatcher contract](../source-code/io/chunker-system.md)
owns exact entries, calls, source differences and limits. In its retail PC
resource dispatcher, TEXT means texture data, ERES routes to the engine,
IMPS to imposter data and DMKR to landscape damage resources. The former
text/entity/import/debug-marker expansions are withdrawn.

| Tag | Routing family | Remaining boundary |
| --- | --- | --- |
| `LVLR` / `TARG` / `AYAD` | Earlier resource metadata branches | Complete container validation and schema are not established by these tags. |
| `MESH` / `TEXT` | Mesh / texture loaders | Full payloads, animation, collision, decode and rendering acceptance. |
| `ERES` / `WRES` | Engine / world resource loaders | Payload completeness, lifetime and world behavior. |
| `IMPS` / `VSDS` | Imposter / vertex-shader loaders | Platform differences and complete rendering behavior. Retail PC loads VSDS despite the pinned PC source skipping it. |
| `PLAT` | Platform fonts | Decode and visual acceptance. |
| `SURF` / `SSHD` | SURF object / static-shadow data | Exact schemas, concrete owner types and rendering. |
| `PMIB` / `DMKR` | Patch-manager / landscape damage data | Full layouts, concrete owner types and runtime effects. |
| `GDIE` | Goodies/gallery data | Catalog, display and unlock behavior; retail image loading differs from source. |
| `LNDS` | Skipped by this retail PC dispatcher | Recognition is not a landscape-decoder result. |
| `PAGE` | No branch established in this reviewed dispatcher | The earlier page/UI expansion has no support from this pass; any other context needs its own witness. |

Use [aya-asset-format.md](aya-asset-format.md) and
[extraction-pipeline.md](extraction-pipeline.md) for their separately scoped
format and pipeline evidence. Corpus counts are queried from local data;
tag recognition proves neither parser completeness nor asset fidelity.
The user-supplied-data and attribution boundary is in
[attribution.md](../project-meta/attribution.md).
