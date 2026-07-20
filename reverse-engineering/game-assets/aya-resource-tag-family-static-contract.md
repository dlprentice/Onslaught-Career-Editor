# AYA resource tag families

These tags are bounded loader vocabulary from source/file-format documentation
and retail static analysis. They are not complete payload schemas or runtime
coverage claims.

| Tag | Routing family | Still unproven |
| --- | --- | --- |
| `LVLR` | level resource header/container | complete level/world-header schema and runtime state |
| `WRES` | world resources | world payload layout and runtime loading |
| `ERES` | entity resources | entity schemas, lifetimes, and gameplay behavior |
| `LNDS` | landscape/terrain | page/header schemas, runtime terrain, and visual parity |
| `PAGE` | page/UI resources | payload schema and frontend presentation |
| `GDIE` | Goodie/gallery data | complete catalog semantics and runtime display/unlock behavior |
| `MESH` | mesh resources | complete payloads, animation/skinning, collision, and rendering |
| `TEXT` | context-dependent text/texture resources | per-context schema, decode fidelity, and display semantics |

Canonical supporting evidence is
[`../source-code/io/chunker-system.md`](../source-code/io/chunker-system.md),
[`aya-asset-format.md`](aya-asset-format.md), and
[`extraction-pipeline.md`](extraction-pipeline.md). Corpus counts and generated
assets are queried from the local corpus; tag recognition proves neither parser
completeness nor asset fidelity. The user-supplied-data and attribution boundary
is recorded in [`../project-meta/attribution.md`](../project-meta/attribution.md).
