# Mapped systems

This page routes implementation work to the smallest current static evidence
owner. It is not a function-completion ledger and does not promote static
analysis to runtime proof.

The July 2026 full re-audit retained a 6,411-address inventory and corrected 91
of 92 independently reviewed candidates; the remaining row was rejected as a
false ABI claim. See the
[`closeout`](ghidra-full-reaudit-closeout-2026-07-13.md),
and [`reviewed correction plan`](ghidra-reviewed-correction-plan-2026-07-13.json).
Older wave-by-wave accounting is available in Git history.

## Canonical system owners

| System | Evidence owner | Current implementation consumer |
| --- | --- | --- |
| Career save layout, grades, unlocks, kills | [`../save-file/_index.md`](../save-file/_index.md) | `BesFilePatcher`, save analyzer/editor, CLI |
| Options and control bindings | [`save-options-static-review-2026-05-26.md`](save-options-static-review-2026-05-26.md) | `ConfigurationEditorService`, CLI |
| Executable identity and patch regions | [`executable-analysis.md`](executable-analysis.md) and focused patch notes | patch catalog, `BinaryPatchEngine` |
| BattleEngine movement, morph, weapons, units | [`unit-battleengine-gameplay-static-contract.md`](unit-battleengine-gameplay-static-contract.md) | rebuild Core policies and copied-target research |
| Target acquisition | [`../game-mechanics/battleengine-target-acquisition-static-contract-v1.md`](../game-mechanics/battleengine-target-acquisition-static-contract-v1.md) | deterministic rebuild targeting work |
| PhysicsScript | [`physics-script-static-contract.md`](physics-script-static-contract.md) | parser/schema and rebuild interface work |
| MissionScript / IScript | [`missionscript-iscript-static-contract.md`](missionscript-iscript-static-contract.md) | scripting format/schema work |
| Frontend, input, HUD | [`hud-frontend-overlay-static-contract.md`](hud-frontend-overlay-static-contract.md) | UI/rebuild interpretation only |
| Meshes, resources, render bridge | [`mesh-resource-render-static-contract.md`](mesh-resource-render-static-contract.md) and [`render-resource-bridge-static-contract.md`](render-resource-bridge-static-contract.md) | asset parsing and rebuild rendering adapters |
| Texture/resource decode | [`texture-resource-decode-static-contract.md`](texture-resource-decode-static-contract.md) | asset inspection/export tooling |
| Audio, media, cutscenes, camera | [`audio-media-cutscene-static-review-2026-05-26.md`](audio-media-cutscene-static-review-2026-05-26.md) | media browser and research |
| Assets, AYA chunks, mission text | [`../game-assets/_index.md`](../game-assets/_index.md) | guarded exporters and asset catalog |
| Local multiplayer evidence | [`local-multiplayer-static-runtime-contract.md`](local-multiplayer-static-runtime-contract.md) | copied-profile split-screen preset only |
| Function-level identities | [`functions/_index.md`](functions/_index.md) | source/evidence lookup |

## Claim boundary

Static evidence can establish addresses, call relationships, constants,
formats, and bounded structures visible in the analyzed specimen. It does not
by itself establish runtime behavior, exact object layouts, source-body
identity, patch safety, visual parity, online play, or reconstruction parity.

Stuart's source and the pinned `references/Onslaught` submodule inform names and
hypotheses but are not retail Steam proof. Controlled runtime observations must
use a verified copied target and record specimen identity; proprietary payloads
and bulky captures remain outside Git.

When a finding changes product behavior, update the owning AppCore/CLI/rebuild
code and its consequential focused test. Do not create a new progress ledger,
wave mirror, generated inventory, or readiness report merely to restate these
owners.
