# W2 rebuild delta — Thing, Battle Engine, camera, and gameplay interfaces

Status: current-code inspection receipt; no rebuild code changed
Date: 2026-08-22
Evidence: MEASURED — current base `784367bd43f9ec13125521b00fe0c8352670ffdd` rebuild owners/tests inspected against the 201-row SOURCE receipt and existing tracked retail authorities; implementation proposals remain explicitly ranked, not observed behavior.

Summary: W2 does not justify a duplicate gameplay framework. Current Core/Client/Godot code already carries substantial Battle Engine, camera, actor, damage, weapon, and Level-100 laws. The gaps below are ranked coherent slices, not a 201-function task list.

## Current implementation owners read

- `rebuild/OnslaughtRebuild.Core/RetailCameraLaws.cs` owns fixed aspect-ratio and movie-camera zoom/cache laws; Client/Godot own the opening pan, control-view handoff, first-person attachment, and rendering.
- `RetailBattleEngineConfigurations.cs`, `RetailBattleEngineGravity.cs`, `RetailBattleEngineInterpolation.cs`, `RetailBattleEngineCloak.cs`, and `RetailBattleEngineAugment.cs` own bounded chassis/configuration laws.
- `RetailJetThrust.cs`, `RetailJetFriction.cs`, `RetailJetAutoLevel.cs`, `RetailWalkerWaterEntry.cs`, `RetailWeaponSelection.cs`, `RetailWeaponStores.cs`, and `RetailWeaponCharge.cs` own bounded part/weapon laws.
- `Simulation.cs`, `Level100ActorRegistry.cs`, `Level100ActorMechanics.cs`, and `Level100PlayerDamage.cs` own the deterministic Level-100 player/actor state actually carried today.
- `InteractiveSession.cs`, `FirstFlightGame.cs`, and `FirstFlightWorldView.cs` adapt that state into player input and presentation; they do not become generic simulation truth.

`definitions.tsv` therefore marks rows PARTIAL conservatively. A source accessor is not “ported” merely because current code has a similarly named field or player-visible effect.

## Already-carried laws that make old gap language stale

- Generic “Battle Engine gravity is absent” is stale: float-exact gravity/state ordinals and deterministic grounded/contact integration already exist with focused tests.
- Generic “camera is absent” is stale: aspect ratio, movie zoom memo, six-second opening pan, control handoff, first-person pose, and Battle Engine zoom input are already carried in bounded owners.
- Generic “weapon/configuration behavior is absent” is stale: configuration lookup, store readouts, selection, charge, cloak, augment, and several jet laws already exist. Generic configuration-file loading and all configuration records remain open; the one-row Level-100 projection is not a catalog.
- Generic “Thing/Actor state is absent” is too broad: Level100ActorRegistry/Mechanics already own canonical Level-100 actor pose/lifecycle. What is absent is a source-shaped reusable CThing/CActor contract outside that level-specific owner.

## Ranked implementation slices

### 1. Generic Battle Engine configuration catalog admission

Source coverage: `BattleEngineConfigurations.h:7-27` and `BattleEngineDataManager.h:243-324`, with the existing retail lookup owner. Add a pure Core catalog/state shape that consumes already-materialized records; keep file I/O and retail-data parsing outside Core. Carry ordered configurations, count, index/name fallback, and configuration-name/weapon-store fields without duplicating the existing lookup law. This unlocks more than the hard-coded Aquila Prototype row and has the clearest source/data boundary.

Retail prerequisite: adjudicate the configuration data loader/record layout and preserve the current `RetailBattleEngineConfigurations` measured exceptions. Focused gate: catalog parsing fixture plus Core lookup/state tests; no Godot dependency.

### 2. Source-shaped attached/pan camera state seam

Source coverage: `Camera.h:19-235`, `Camera.cpp:344-393`, and the five named analog rows. Consolidate pose/old-pose/zoom/HUD state behind a Client-facing deterministic camera snapshot while retaining Core only for simulation-owned inputs. Reuse the current six-second opening pan and first-person handoff; do not add a second camera lifecycle. The first slice should cover attached thing pose, pan old/current pose, and the event-scheduled update contract, not every camera subclass.

Retail prerequisite: close the named Camera gaps around the two constructor plates and keep the known caller-supplied pan-duration divergence ledger. Focused gate: Client camera snapshot/update tests plus existing opening-pan tests.

### 3. Reusable Thing/Actor base-state laws

Source coverage: `thing.h:65-252`, `thing.h:257-306`, and `actor.h:13-65`, especially the 27 promoted exact inline/folded rows in those owners. Introduce a small Core base-state law only where Level100ActorRegistry can consume it immediately: visibility/dying/shutdown flags, current/old pose, velocity stop/update, type masks, and contact timestamps. Do not port render/audio virtual defaults into Core; presentation adapters may consume a snapshot instead.

Retail prerequisite: preserve the promoted folded-body identities and identify any Level100ActorRegistry field-law divergence before wiring. Focused gate: base-state pure tests, registry integration tests, deterministic replay/hash tests.

## Remaining boundary

This receipt proves source architecture and bounded retail joins, not full runtime parity. It does not authorize retail payloads in Git, filesystem/clock dependencies in Core, Ghidra mutation, or a one-class-per-source-class rewrite. The implementation lanes should cite this receipt and the exact source rows they carry, then add their retail exceptions to the existing provenance/parity owners rather than creating another status ledger.
