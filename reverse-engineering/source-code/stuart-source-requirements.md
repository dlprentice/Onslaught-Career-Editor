# Stuart Source Requirements For Full Clarity

Status: active source-code RE planning note
Last updated: 2026-05-01

This checklist moved from the repo root into the source-code RE docs so source-drop requirements live beside the Stuart source analysis corpus. It records what we still need from Stuart and from retail runtime validation to reach maximum RE confidence and safe binary extension work.

## Bottom Line

If the goal is **"100% clarity"** for static understanding and high-confidence patching, we need **the full source and build ecosystem**, not just selected `.cpp` files.

In practical terms: yes, this is effectively "all source + all build/tooling context + symbols + pipeline tooling" for the relevant build lineage.

## Required From Stuart (Non-Negotiable For Full Clarity)

1. Full game/runtime source tree used for PC internal builds
- All engine/gameplay/frontend/platform code.
- All headers, inline files, shared utility code, and generated headers.

2. Full build system and compile/link configuration
- Original project files/solutions/workspaces (VS-era files, scripts, makefiles).
- Preprocessor defines per target/configuration.
- Linker settings, section layout assumptions, and optimization flags.

3. Symbol artifacts for matching builds
- PDBs (if available), MAP files, link maps, and any symbol export manifests.
- Build identifiers matching exact executable variants.

4. Third-party and internal dependency versions
- Exact versions/source for external libs and internal middleware wrappers.
- Any patched forks used by the team.

5. Asset pipeline/toolchain source and binaries
- 3ds Max export plugins and conversion tools (`.msh`, `.aya`, texture pipeline).
- Any preprocessors/postprocessors that transform runtime data.

6. Conditionally compiled developer-only systems
- Tooling/paths compiled out in retail.
- Batch generators for coastlines, LOD tables, sprite baking, and related precompute systems.

7. Command-line/runtime configuration references
- Supported CLI switches, boot modes, and environment/config files.
- Any hidden/debug flags used internally.

8. Platform-delta code and wrappers
- PC/Xbox/PS2 divergence points and platform abstraction layers.
- Build-time feature toggles that affect control flow.

9. Data format references and schema notes
- Struct packing/alignment assumptions for serialized data.
- Versioning rules and migration behavior for save/assets.

10. Build and release notes (if available)
- Changelogs that explain why behavior diverged between internal and retail builds.

11. Exact toolchain and SDK matrix
- Compiler toolset version, service packs, and project upgrade history.
- DirectX SDK version(s), Windows SDK assumptions, CRT/runtime linkage choices.
- Build-machine assumptions that affect codegen/ABI (packing defaults, calling-convention defaults, wchar settings).

12. Content/build provenance and representative test corpus
- Which asset/content revision each executable/build corresponds to.
- Representative internal saves, mission states, and command-line launch recipes used by the team.
- Any scripted regression scenarios used during development.

## What We Already Have (Helpful, Not Sufficient Alone)

- `references/Onslaught` source drop (high value for semantic parity).
- `references/AYAResourceExtractor` and recovered pipeline context.

This is strong for naming and behavior inference, but it is not enough by itself to guarantee perfect runtime equivalence with Steam retail binaries.

## Additional Inputs Needed (Not From Stuart Alone)

To reach practical "through-and-through" confidence on the Steam retail binary, we also need non-Stuart evidence:

1. Retail runtime validation artifacts
- Deterministic traces from the actual Steam executable under controlled scenarios.
- Branch/side-effect confirmations for high-risk paths (save/load, mission transitions, rendering init, input/config propagation).

2. Retail variant control
- Hash-locked executable baselines and per-build address manifests for every patch target.
- Repeatable verification runs whenever the runtime environment changes (driver/runtime/tool updates).

3. Patch-risk controls for extension work
- Hook contract tests (entry/exit invariants, allocator ownership, thread-affinity checks).
- Failure-mode validation (asset missing/corrupt, edge save states, timing-sensitive transitions).

4. Netcode-extension prerequisites (if multiplayer insertion is a goal)
- Simulation/authority model decision (lockstep vs server-authoritative vs hybrid).
- Deterministic-state strategy (tick model, sync boundaries, rollback/reconciliation policy).
- Protocol/schema/versioning plan and compatibility policy for modded clients.
- Runtime security/anti-cheat boundaries and trust model for remote inputs.

Without these retail-side validations, source parity alone cannot guarantee 1:1 dynamic behavior.

## Dynamic RE Tooling Note (Yes, This Means Other Software)

To validate runtime behavior headlessly, we still need additional tooling beyond Ghidra static analysis:

- Debugger/instrumentation stack (e.g., WinDbg/CDB, Frida, or equivalent hook framework).
- Deterministic launcher harness for reproducible run scenarios.
- Logging/trace collectors for call hits, args/returns, memory diffs, and branch outcomes.

Ghidra headless is static analysis only. Dynamic validation requires executing the game with instrumentation.

## Recommended Dynamic Validation Workflow (Deterministic)

1. Launch known scenario (fixed save + fixed flags + fixed level entry).
2. Attach debugger/instrumentation automatically.
3. Trace selected high-risk functions and state transitions.
4. Compare runtime traces against static contracts/comments.
5. Persist artifacts in `reverse-engineering/binary-analysis/` and state files.

## Confidence Statement

- This checklist is now accurate for current project goals (high-confidence static RE + extension/modding readiness).
- It defines what is needed for maximum clarity, but does not claim that source alone can eliminate dynamic validation for the Steam retail executable.

## Discord-Ready Raw File Delta (Copy/Paste)

This section is intentionally raw and comma-separated so it can be pasted directly into Discord.

Derivation basis (repo-local, auditable):
- Provided set: `reverse-engineering/source-code/stuart-source-file-manifest-2026-02-11.tsv` (`.cpp` entries).
- Missing set: `reverse-engineering/source-code/source-file-inventory.md` "Files Stuart DID NOT PROVIDE" table.
- Strict delta rule: remove any inventory entries already present in provided set.
- Known inventory false-positive removed from request set: `DXMemBuffer.cpp` (already in provided manifest).

```text
ALREADY_PROVIDED_CPP_CSV=activereader.cpp, actor.cpp, Array.cpp, BattleEngine.cpp, BattleEngineConfigurations.cpp, BattleEngineDataManager.cpp, BattleEngineJetPart.cpp, BattleEngineWalkerPart.cpp, Camera.cpp, Career.cpp, chunker.cpp, CLIParams.cpp, Controller.cpp, d3dapp.cpp, DXEngine.cpp, DXFrontend.cpp, DXGame.cpp, DXMemBuffer.cpp, DXMemoryManager.cpp, EditorD3DApp.cpp, EndLevelData.cpp, engine.cpp, event.cpp, eventmanager.cpp, FEPGoodies.cpp, FEPLoadGame.cpp, FEPSaveGame.cpp, FrontEnd.cpp, game.cpp, InitThing.cpp, ltshell.cpp, MemoryCard.cpp, MemoryManager.cpp, Music.cpp, PCController.cpp, PCEngine.cpp, PCFEPLoadGame.cpp, PCFEPSaveGame.cpp, PCFrontend.cpp, PCGame.cpp, PCMemoryCard.cpp, PCPlatform.cpp, pcsoundmanager.cpp, Platform.cpp, Player.cpp, ResourceAccumulator.cpp, scheduledevent.cpp, SoundManager.cpp, SPtrSet.cpp, storage.cpp, thing.cpp, XBoxMemoryCard.cpp

MISSING_FROM_STUART_CPP_CSV=AirUnit.cpp, Atmospherics.cpp, Boat.cpp, Bomber.cpp, BSpline.cpp, Building.cpp, bytesprite.cpp, Cannon.cpp, Carrier.cpp, Carver.cpp, CollisionSeekingRound.cpp, collisionseekingthing.cpp, Component.cpp, console.cpp, CPhysicsScript.cpp, CPhysicsScriptStatements.cpp, Cutscene.cpp, damage.cpp, DestructableSegmentsController.cpp, DiveBomber.cpp, Dropship.cpp, GroundAttackAircraft.cpp, GroundUnit.cpp, GroundVehicle.cpp, HiveBoss.cpp, Infantry.cpp, Mech.cpp, Mine.cpp, Missile.cpp, Plane.cpp, Round.cpp, Sentinel.cpp, Submarine.cpp, Tentacle.cpp, ThunderHead.cpp, Unit.cpp, Warspite.cpp, WarspiteDome.cpp, FEPBEConfig.cpp, FEPDebriefing.cpp, FEPDevelopment.cpp, FEPMain.cpp, FEPDirectory.cpp, FEPMultiplayerStart.cpp, FEPOptions.cpp, FEPWingmen.cpp, MenuItem.cpp, PauseMenu.cpp, Hud.cpp, gcgamut.cpp, HeightField.cpp, ibuffer.cpp, imageloader.cpp, imposter.cpp, landscapeib.cpp, LandscapeTexture.cpp, maptex.cpp, mapwho.cpp, mesh.cpp, MeshCollisionVolume.cpp, MeshPart.cpp, MeshRenderer.cpp, PolyBucket.cpp, RTCutscene.cpp, rtmesh.cpp, StaticShadows.cpp, texture.cpp, tgaloader.cpp, vbuffer.cpp, vbuftexture.cpp, VertexShader.cpp, FastVB.cpp, DXBattleLine.cpp, DXClouds.cpp, DXCompass.cpp, DXFMV.CPP, DXFont.cpp, DXFrontEndVideo.cpp, DXImposter.cpp, DXKempyCube.cpp, DXLandscape.cpp, DXMeshVB.cpp, DXPalletizer.cpp, DXParticleTexture.cpp, DXPatchManager.cpp, DXShadows.cpp, DXSnow.cpp, DXSurf.cpp, DXTexture.cpp, DXTrees.cpp, MissionScript/AsmInstruction.cpp, MissionScript/DataType.cpp, MissionScript/EventFunction.cpp, MissionScript/IScript.cpp, MissionScript/ScriptEventNB.cpp, MissionScript/ScriptObjectCode.cpp, MissionScript/Symtab.cpp, GillM.cpp, GillMHead.cpp, MCBuggy.cpp, MCMech.cpp, MCTentacle.cpp, InfluenceMap.cpp, SquadNormal.cpp, SquadRelaxed.cpp, WaypointManager.cpp, ParticleDescriptor.cpp, ParticleManager.cpp, ParticleSet.cpp, SpawnerThng.cpp, SphereTrigger.cpp, tree.cpp, world.cpp, WorldMeshList.cpp, WorldPhysicsManager.cpp, flexarray.cpp, oids.cpp, RadarWarningReceiver.cpp, text.cpp, TokenArchive.cpp, triangulate.cpp, wavread.cpp, mixermap.cpp, PCRTID.cpp

HIGH_PRIORITY_MISSING_CPP_CURRENTLY_BLOCKING_SOURCE_PARITY_CSV=AirUnit.cpp, Carrier.cpp, DiveBomber.cpp, FEPDebriefing.cpp, HeightField.cpp, Infantry.cpp, Mech.cpp, PauseMenu.cpp, ThunderHead.cpp, Unit.cpp, world.cpp, text.cpp
```

Suggested single-line ask to Stuart:

```text
Could you share the remaining Onslaught source files from this list (and matching headers where available): AirUnit.cpp, Atmospherics.cpp, Boat.cpp, Bomber.cpp, BSpline.cpp, Building.cpp, bytesprite.cpp, Cannon.cpp, Carrier.cpp, Carver.cpp, CollisionSeekingRound.cpp, collisionseekingthing.cpp, Component.cpp, console.cpp, CPhysicsScript.cpp, CPhysicsScriptStatements.cpp, Cutscene.cpp, damage.cpp, DestructableSegmentsController.cpp, DiveBomber.cpp, Dropship.cpp, GroundAttackAircraft.cpp, GroundUnit.cpp, GroundVehicle.cpp, HiveBoss.cpp, Infantry.cpp, Mech.cpp, Mine.cpp, Missile.cpp, Plane.cpp, Round.cpp, Sentinel.cpp, Submarine.cpp, Tentacle.cpp, ThunderHead.cpp, Unit.cpp, Warspite.cpp, WarspiteDome.cpp, FEPBEConfig.cpp, FEPDebriefing.cpp, FEPDevelopment.cpp, FEPMain.cpp, FEPDirectory.cpp, FEPMultiplayerStart.cpp, FEPOptions.cpp, FEPWingmen.cpp, MenuItem.cpp, PauseMenu.cpp, Hud.cpp, gcgamut.cpp, HeightField.cpp, ibuffer.cpp, imageloader.cpp, imposter.cpp, landscapeib.cpp, LandscapeTexture.cpp, maptex.cpp, mapwho.cpp, mesh.cpp, MeshCollisionVolume.cpp, MeshPart.cpp, MeshRenderer.cpp, PolyBucket.cpp, RTCutscene.cpp, rtmesh.cpp, StaticShadows.cpp, texture.cpp, tgaloader.cpp, vbuffer.cpp, vbuftexture.cpp, VertexShader.cpp, FastVB.cpp, DXBattleLine.cpp, DXClouds.cpp, DXCompass.cpp, DXFMV.CPP, DXFont.cpp, DXFrontEndVideo.cpp, DXImposter.cpp, DXKempyCube.cpp, DXLandscape.cpp, DXMeshVB.cpp, DXPalletizer.cpp, DXParticleTexture.cpp, DXPatchManager.cpp, DXShadows.cpp, DXSnow.cpp, DXSurf.cpp, DXTexture.cpp, DXTrees.cpp, MissionScript/AsmInstruction.cpp, MissionScript/DataType.cpp, MissionScript/EventFunction.cpp, MissionScript/IScript.cpp, MissionScript/ScriptEventNB.cpp, MissionScript/ScriptObjectCode.cpp, MissionScript/Symtab.cpp, GillM.cpp, GillMHead.cpp, MCBuggy.cpp, MCMech.cpp, MCTentacle.cpp, InfluenceMap.cpp, SquadNormal.cpp, SquadRelaxed.cpp, WaypointManager.cpp, ParticleDescriptor.cpp, ParticleManager.cpp, ParticleSet.cpp, SpawnerThng.cpp, SphereTrigger.cpp, tree.cpp, world.cpp, WorldMeshList.cpp, WorldPhysicsManager.cpp, flexarray.cpp, oids.cpp, RadarWarningReceiver.cpp, text.cpp, TokenArchive.cpp, triangulate.cpp, wavread.cpp, mixermap.cpp, PCRTID.cpp
```
