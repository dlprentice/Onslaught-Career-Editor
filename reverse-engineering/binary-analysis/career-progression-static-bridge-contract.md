# Career Progression Static Bridge Contract

Status: source/static public-safe bridge contract, not runtime mission-outcome or save-behavior proof
Last updated: 2026-07-03
Scope: `career-progression-static-bridge-contract`

This contract answers one bounded question from the rebuild front-door map:
how should `CCareer`, `level_structure`, `CGame`, and `CEndLevelData` be
routed into save/career planning docs before any runtime mission-outcome,
save/load, UI-flow, or rebuild claim?

Current answer: use those names only as bridge vocabulary between tracked
source gameplay docs, tracked retail/static save and function docs, and the
existing campaign graph/link maps. The current proof class is Tier C source
gameplay architecture plus Tier B retail/static save and career documentation.
Runtime save/load behavior, mission outcome persistence, career-map UI flow,
Goodies recomputation, exact source-to-retail layout identity, gameplay
outcomes, generated rebuild output, and rebuild parity require
higher-authority proof.

## Evidence Class

| Tier | Current use in this contract | Boundary |
| --- | --- | --- |
| Tier C source gameplay architecture | Names `CCareer`, `level_structure`, `CGame`, and `CEndLevelData` as source-side owners and bridge vocabulary. | Candidate architecture only; not a guarantee of Steam retail persistence, UI behavior, or exact layout identity. |
| Tier B retail/static save and career docs | Routes those source names into tracked `.bes` true-view docs, campaign graph/link maps, and retail static CGame/Career/EndLevelData indexes. | Static bridge context only; not runtime save/load, mission outcome, objective UI, Goodies wall, patch, or rebuild proof. |
| Tier A runtime save/load and mission-outcome proof | Not used in this slice. | Live copied-runtime save/load behavior, mission win/loss persistence, campaign-map UI, objective display, cutscene/outro behavior, and no-noticeable gameplay parity need separate authorization and evidence. |

## Public Anchors

| Anchor | Current boundary used here |
| --- | --- |
| [career-system.md](/reverse-engineering/source-code/gameplay/career-system.md) | Names `CCareer`, `CAREER_VERSION`, `CSArray`, `level_structure`, and retail `.bes` caveats as source-side architecture context. |
| [game-system.md](/reverse-engineering/source-code/gameplay/game-system.md) | Names `CGame` slots, level state, mission-outcome, and `CCareer::Update()` handoff vocabulary. |
| [save-file/_index.md](/reverse-engineering/save-file/_index.md) | Keeps the fixed-size `.bes` true-view, version, slots, options, and not-runtime-proof boundaries as the persistence front door. |
| [career-graph.md](/reverse-engineering/save-file/career-graph.md) | Provides campaign node/link map, `CCareer__Update -> CCareer__ReCalcLinks`, and structural graph validation context. |
| [career-links.md](/reverse-engineering/save-file/career-links.md) | Provides link-index routing for lower/higher mission unlock paths. |
| [Career.cpp/_index.md](/reverse-engineering/binary-analysis/functions/Career.cpp/_index.md) | Tracks static Career-side anchors including `CCareer__Update` and `CCareer__ReCalcLinks` with runtime/progression non-claims. |
| [game.cpp/_index.md](/reverse-engineering/binary-analysis/functions/game.cpp/_index.md) | Tracks static CGame-side anchors including `CGame__FillOutEndLevelData`, `CGame__DeclareLevelWon`, and `CGame__DeclareLevelLost` with runtime outcome non-claims. |
| [EndLevelData.cpp/_index.md](/reverse-engineering/binary-analysis/functions/EndLevelData.cpp/_index.md) | Tracks `CEndLevelData__IsAllSecondaryObjectivesComplete` as a static predicate bridge, not runtime progression proof. |
| [rebuild-front-door-chain-map.md](/roadmap/rebuild-front-door-chain-map.md) | Selects this bridge as a bounded campaign/career progression side guard. |

## Bridge Table

| Bridge item | Static route allowed | Higher authority still required |
| --- | --- | --- |
| `level_structure` graph vocabulary | Route from source career docs into the campaign graph and link-index maps as node/world/link planning vocabulary. | Complete `worldheaders.dat` schema, exact source-to-retail field identity, runtime campaign-map UI flow, and gameplay progression outcomes. |
| `CCareer` progression update vocabulary | Route to `CCareer__Update`, `CCareer__ReCalcLinks`, true-view save offsets, slot bits, and copied-baseline byte-preservation fixture context. | Runtime save/load persistence, defaultoptions boot behavior, Goodies-wall behavior, Goodies recomputation, exact `CCareer` layout identity, and patch behavior. |
| `CGame` outcome snapshot vocabulary | Route to static `CGame__FillOutEndLevelData`, `CGame__DeclareLevelWon`, `CGame__DeclareLevelLost`, and static outcome bridge docs. | Runtime level-win/loss command effects, live MissionScript command effects, objective UI, actual mission result persistence, cutscene/outro flow, and player-visible campaign progression. |
| `CEndLevelData` objective predicate vocabulary | Route to static secondary-objective predicate docs and Career link recalculation context. | Runtime objective completion display, exact `END_LEVEL_DATA` layout, runtime secondary-objective effects, and rebuild parity. |

## Allowed Inputs

This checker-backed slice may read only tracked public Markdown and package
metadata. It may validate mirror parity, local links, required bridge rows,
front-door/index registration, package-script registration, and explicit
non-claims.

Allowed source classes:

- tracked source gameplay architecture docs;
- tracked retail/static save and career docs;
- tracked campaign graph and link-index docs;
- tracked retail/static CGame, Career, and EndLevelData function indexes;
- tracked front-door/index docs that keep the bridge in a planning scope;
- package metadata for a local public checker.

## Out Of Scope

This slice must not:

- read ignored payload overlays, private saves, raw install manifests, raw
  proof bundles, copied executables, screenshots, frame dumps, auth/session/log
  cache material, or secrets;
- launch BEA, attach CDB, mutate Ghidra, patch an executable, mutate an
  installed game, run a save editor, run an extractor, execute an importer, or
  generate asset or save payloads;
- claim runtime save/load behavior, defaultoptions boot behavior, menu behavior,
  runtime mission-outcome persistence, runtime objective UI, runtime Goodies
  wall behavior, runtime Goodies recomputation, live MissionScript command
  effects, patch behavior, gameplay behavior, visual output, renderer behavior,
  runtime parity, rebuild parity, or no-noticeable-difference parity;
- add AppCore, WinUI, CLI, Godot, save-editor, renderer, release, installer,
  packaging, command-arm, or publication support.

## Exit Gate

This planning slice is complete only when:

- this document and its lore-book mirror match byte-for-byte;
- binary-analysis indexes link this contract as a source/static bridge
  contract;
- `roadmap/rebuild-front-door-chain-map.md` links this contract as the
  campaign/career progression side guard without changing active rebuild proof
  scope;
- `tools/career_progression_static_bridge_contract_probe.py --check` passes;
- public documentation, Markdown link, hard-payload safety, and public-allowlist gates
  pass.

After this exit gate, the next safe action is still a bounded schema,
runtime-readiness, or save/career proof-plan question with its own
higher-authority proof class. No runtime proof, save-editor run, MissionScript
runtime proof, Ghidra mutation, extractor run, importer execution, generated
asset or save output, gameplay claim, product exposure, or release action is
authorized by this contract.
