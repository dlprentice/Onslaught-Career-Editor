# Product-Coupled Battle Engine Aquila Reconstruction Campaign Design

Status: written design awaiting file review before campaign implementation
Date: 2026-07-15

## Decision

Onslaught Toolkit will operate as one product-coupled reconstruction campaign
with three genuine shipping outcomes:

1. a community-facing WinUI Toolkit;
2. a playable, evidence-backed original-code reconstruction; and
3. meaningful tools, patches, and modifications for copied retail Battle
   Engine Aquila installations.

Original-game multiplayer is an explicit strategic epic within the retail
enhancement outcome. Reverse engineering, pinned source analysis, runtime
proof, lore, asset research, and documentation are inputs to those outcomes,
not independent definitions of campaign success.

## Problem Being Corrected

The repository has accumulated extensive research, source crosswalks, lore,
runtime proof infrastructure, and static accounting. It has also delivered a
community WinUI application, a small deterministic Godot prototype, and a safe
copied-executable patch catalog. Those results are real, but the project lacks
a binding rule that turns supporting evidence into product capability.

The resulting failure mode is recognizable:

- research and proof artifacts become the end product;
- static coverage counters substitute for semantic reconstruction;
- contract, readiness, and checker chains grow without a consumer;
- the rebuild remains an isolated synthetic demonstration;
- WinUI does not meaningfully operate or integrate the rebuild; and
- retail modifications remain dominated by compatibility, cosmetic, and
  diagnostic patches rather than community-valued capabilities.

The campaign must measure advancement in playable behavior, useful community
tooling, safe retail enhancement, asset/mission import, or a precise blocker
that changes the chosen technical path. Document count and proof count are not
product advancement by themselves.

## Terminology And Reconstruction Boundary

### Project meaning of reconstruction

The project objective is a **full game reconstruction**:

- recover file formats, assets, behavior, and system relationships from a
  user-owned retail game;
- write original replacement engine and game code;
- import user-owned retail assets locally where supported;
- reproduce increasingly complete playable Battle Engine Aquila experiences;
  and
- ship the engine, tooling, import paths, and original fallback content to the
  community.

The current implementation is accurately described as an
**evidence-backed, RE-informed original-code reconstruction**. The current team
has seen public reference source and decompilation-derived descriptions, so the
implementation is not labeled a strict clean-room implementation.

Strict clean-room is a narrower process term for an independently staffed
implementation team that receives behavior specifications without exposure to
source or decompilation. That future option is retained, but it is not the
primary campaign, a prerequisite for reconstruction work, or a reason to defer
playable implementation.

### Retail assets

The Toolkit may support local extraction and import of textures, models,
terrain, audio, levels, scripts, and other data from a user's own retail copy.
Retail payloads remain outside Git and ordinary release artifacts unless
separate rights establish redistribution authority. Community releases can
ship the reconstruction, import tooling, manifests, and original fallback
content without bundling proprietary game payloads.

## Product Outcome 1: Community WinUI Toolkit

WinUI remains the public front door and the application released for the
Battle Engine Aquila community. It is not merely an internal reverse-
engineering dashboard.

Its intended product responsibilities are:

- discover and validate a user-owned retail installation without mutating it;
- create, configure, patch, restore, and launch safe copied retail profiles;
- expose useful patches and modifications with honest evidence and rollback;
- manage saves, options, media, lore, extracted catalogs, and local assets;
- discover, install or locate, configure, and launch reconstruction builds;
- orchestrate local retail-asset import into the reconstruction;
- distinguish clearly between Retail, Reconstruction, and shared workflows;
- surface community-ready capabilities without exposing proof IDs and raw
  reverse-engineering jargon in normal UI; and
- eventually own supported Host/Join workflows once original-game multiplayer
  gates establish distinct-machine gameplay.

WinUI and the GPL reconstruction remain separate components with a process and
artifact boundary. WinUI may discover, install, configure, launch, and consume
public reports from a reconstruction executable without moving deterministic
simulation into the Toolkit or silently relicensing either component. A later
packaging slice must choose a clearly licensed separate companion artifact or
a clearly partitioned combined distribution.

## Product Outcome 2: Playable Reconstruction

The reconstruction is a first-class product outcome. `rebuild/` remains the
implementation home, but it may no longer be treated as an unrelated top-level
demonstration.

`OnslaughtRebuild.Core` owns deterministic simulation. Client and render
adapters consume snapshots. Godot remains the first playable adapter unless a
future evidence-backed decision replaces it. Retail-derived behavior enters
through a bounded contract, but the contract is supporting evidence; the
milestone advances when the consumer behavior lands.

The playable capability ladder is:

1. walker and jet control, transform, handling, resources, and camera;
2. shields, hull, weapons, fire cadence, projectiles, damage, and targeting;
3. HUD, audio, effects, game-state transitions, and failure/win conditions;
4. terrain, units, materials, textures, animation, and local retail-asset
   import;
5. missions, objectives, PhysicsScript behavior, AI, progression, and saves;
6. menus, campaign flow, configuration, and complete playable sessions; and
7. multiplayer where the chosen architecture supports it.

Synthetic mechanics and content remain useful scaffolding, but each relevant
vertical slice should replace or clearly isolate another synthetic assumption.
A deterministic replay proves reconstruction stability, not retail truth; a
retail observation proves only its bounded observation, not the whole game.

## Product Outcome 3: Retail Enhancements And Mods

The original game receives a deliberate community-enhancement program rather
than incidental patch discovery.

Candidate work includes, when supported by evidence and safe rollback:

- widescreen, display, HUD, and presentation corrections;
- modern controller, input, sensitivity, and rebinding improvements;
- camera and usability enhancements;
- graphics, audio, mission-selection, and content-authoring tools;
- gameplay, balance, unlock, and quality-of-life modifications;
- local multiplayer improvements; and
- original-game network multiplayer support.

Candidates are ranked by community value, technical feasibility, evidence
strength, reversibility, compatibility, and whether WinUI can provide a safe
workflow. The campaign does not prioritize a patch merely because its function
or byte address is already documented.

Every retail modification operates on a copied target, verifies original and
resulting bytes or state, retains full rollback, and separates static byte
confidence from observed user-visible behavior.

## Strategic Epic: Original-Game Multiplayer

Original-game multiplayer is an explicit long-horizon ambition, not an
implicit side experiment. Host/Join remains disabled until the relevant rung
is accepted, but the campaign actively advances the ladder.

The intended progression is:

1. establish exact P1/P2 input-device, viewport, state, and ownership routing;
2. map the retail engine's existing local-player and split-screen capabilities;
3. prove independently sourced P2 commands across distinct processes and then
   distinct machines;
4. compare input relay, split-screen virtualization, state bridging,
   executable modification, and hybrid approaches;
5. measure command delivery, causality, authority, latency, desynchronization,
   failure recovery, and cleanup;
6. build a bounded community helper controlled through WinUI; and
7. enable Host/Join only after repeatable distinct-machine gameplay and safety
   acceptance.

A failed approach must eliminate or narrow an architecture. It must not create
another recursive readiness chain without executing the next discriminating
experiment.

The current source-shaped and retained contract expectation is P1/viewpoint 0
on the top half and P2/viewpoint 1 on the bottom half in horizontal split
screen. That ordering remains scheduled for a separate focused copied-runtime
retest after this strategy rewrite; this design does not promote a new runtime
claim.

## Consumer-Bound Slice Contract

Every Current Slice records:

- **primary outcome:** `WinUI Community`, `Playable Reconstruction`, or
  `Retail Enhancement`;
- **user outcome:** the capability a player, modder, contributor, or future
  consumer gains;
- **evidence question:** the smallest uncertainty that blocks that outcome;
- **consumer:** the exact code, product surface, patch row, import path, or
  multiplayer rung that consumes the result;
- **acceptance:** the executable, runtime, rendered, or product test that proves
  the consumer works;
- **non-claims:** what remains synthetic, hypothetical, local-only, or
  unproven; and
- **next link:** the direct follow-up if this slice is evidence-only.

### Anti-wheel-spinning rules

1. RE, source analysis, runtime proof, lore, documentation, and harnesses are
   supporting work. They are not primary product outcomes.
2. A research-only slice must name an exact consumer and the uncertainty it
   removes.
3. No second consecutive research-only slice is selected unless the first
   reveals a concrete dependency that can only be resolved by another bounded
   evidence step. That dependency and consumer remain explicit.
4. Absent a recorded hard dependency, every two accepted slices include at
   least one user-observable result: playable behavior, a useful retail
   patch/mod, a local extraction/import capability, or a community-facing WinUI
   workflow.
5. A behavior contract does not by itself land a product milestone. The
   milestone remains `in_progress` until its named consumer lands. A narrow
   static correction may close independently only when it prevents a dangerous
   current misimplementation and queues the consumer explicitly.
6. A harness is built with the product behavior it verifies. Harness creation
   without a named behavior or workflow is not an independent advancement.
7. Historical documentation is updated only when it misroutes current work,
   blocks a consumer, or materially affects the shipped community experience.
8. Lore work counts as product progress only when it improves the released
   community knowledge experience or supplies concrete narrative, mission, or
   provenance input to reconstruction.
9. Static function percentages, proof counts, test counts, and document counts
   may describe evidence health but never substitute for a product outcome.

## Portfolio Selection And Balance

The campaign is a portfolio, not three isolated lanes and not a rigid quota.
After each slice, the root selects the highest-value actionable consumer using
this order:

1. repair an unsafe, broken, or falsely claimed shipped capability;
2. pay down an evidence result whose named consumer is now actionable;
3. advance the next playable reconstruction vertical;
4. deliver a high-value retail enhancement or multiplayer discriminating
   experiment;
5. integrate reconstruction or retail capability into the community WinUI
   product;
6. unblock local asset, level, mission, or script import needed by a playable
   vertical;
7. improve community lore/knowledge only under the product rule above.

Do not starve any shipping outcome indefinitely. When two choices have similar
value, prefer the outcome that has gone longest without a user-observable
advancement. Do not create shallow work merely to satisfy balance; a recorded
dependency permits temporary concentration.

## Evidence-To-Product Flow

The preferred flow for retail-derived behavior is:

1. form the smallest source/static hypothesis;
2. establish the released binary identity or structure needed to observe it;
3. measure copied-runtime behavior when causality or values matter;
4. write one bounded public-safe contract;
5. implement the named reconstruction, patch/mod, or WinUI consumer;
6. verify the consumer with deterministic, native, runtime, visual, or
   capture/replay evidence appropriate to the claim; and
7. close the product increment, not merely the research artifact.

Steps may collapse when existing evidence already supports the consumer. A
source constant or reconstructed self-agreement never substitutes for retail
measurement when the claim is retail-derived.

## Automated Verification Strategy

Visual and behavioral automation is part of each consumer, not a standalone
proof industry:

- Core behavior uses deterministic command tapes, independent expected values,
  continuation-state hashes, and readable semantic assertions.
- Godot behavior uses fixed scenes, seeds, inputs, cameras, viewports, semantic
  snapshot receipts, bounded frame captures, and owned-process cleanup.
- Retail runtime work binds copied executable, process, module, window, input,
  and capture identity; visual state corroborates rather than replaces memory
  or causality evidence.
- WinUI uses native UI Automation and exact-build visual capture for the
  workflows changed by the slice.
- Asset work uses parser counts, geometry/material/texture reconciliation,
  deterministic exports, and bounded multi-view renders.

The smallest gate that catches the changed contract is the default. Broad
repository hygiene, release, or payload suites run when their boundary changes
or at an appropriate integration/release checkpoint, not after every narrow
mechanics edit.

## Community Releases

WinUI remains a community release product. Releases are made when a verified
artifact provides meaningful accumulated user value, not merely because a
research slice closed or publication authority exists.

Release notes separate:

- community Toolkit capabilities;
- copied-retail patches and their proof/rollback level;
- reconstruction capabilities and remaining synthetic behavior;
- optional user-owned asset-import support; and
- experimental multiplayer research that is not yet Host/Join-ready.

Reconstruction distribution retains GPL notices and source obligations.
Toolkit distribution retains its own license. Proprietary game payloads are
not bundled by default.

## Initial Product-Coupled Sequence

After this strategy is implemented, the expected initial sequence is:

1. close the current M2.3 target-lock correction narrowly because it prevents
   incorrect combat implementation; fix its premature acceptance/authority
   wording and queue the target-lock consumer;
2. execute shield dual-accept and, if valid, implement the measured behavior in
   Core and Godot with deterministic and rendered verification;
3. add a community WinUI Reconstruction surface that can discover, explain,
   configure, and launch the existing First Flight build through a clear
   component boundary;
4. measure and implement fire cadence/projectile behavior as a playable combat
   increment;
5. select and deliver one materially useful original-game modification through
   the safe-copy catalog and WinUI;
6. begin the explicit original-game multiplayer epic with a focused P1/P2
   ownership and distinct-endpoint architecture decision;
7. turn existing asset extraction work into a repeatable local
   `Import from my game` reconstruction workflow; and
8. continue through combat, world, missions, campaign, and presentation as
   consumer-complete vertical increments.

If a live attempt fails under an attempt cap, the campaign records the exact
blocker and advances another safe shipping outcome. It does not stop the whole
campaign or invent a behavior contract.

## Milestone And Completion Semantics

A product milestone is `landed` only when its user-visible or executable
consumer and proportional acceptance gate are landed. Evidence prerequisites
can be `accepted` while their product milestone remains `in_progress`.

The campaign may declare a phase complete when:

- a coherent playable reconstruction increment exists beyond synthetic First
  Flight scaffolding;
- at least one meaningful new retail enhancement and its WinUI workflow have
  shipped or are explicitly deferred for a technical reason;
- the community WinUI product can operate a reconstruction workflow;
- active evidence debt has named consumers or has been moved to backlog;
- focused Core, Godot, WinUI, patch, import, and payload boundaries touched by
  the phase are green; and
- remaining work is an explicit product backlog rather than silent research
  continuation.

Phase completion is not a claim that Battle Engine Aquila has been fully
reconstructed, that retail parity is complete, that proprietary assets may be
redistributed, or that original-game multiplayer is player-ready.

## Durable Goal Text

The existing durable goal aligns in broad subject and safety boundaries, but it
does not sufficiently require research to reach a product consumer. Replace it
with the following product-coupled form when this design is implemented:

> Continuously reconstruct and enhance Battle Engine Aquila through an
> evidence-backed, product-coupled campaign. Operate one portfolio with three
> shipping outcomes: the community WinUI Toolkit, a playable RE-informed
> original-code reconstruction, and meaningful tools, patches, mods, and
> multiplayer progress for copied retail installations. Treat static analysis,
> pinned source, copied-runtime observation, lore, asset research,
> documentation, and harnesses as inputs rather than ends. Every slice must
> name its primary product outcome, user value, exact consumer, acceptance
> evidence, and non-claims. Do not run consecutive research-only slices unless
> a concrete dependency requires it; absent such a dependency, deliver a
> user-observable capability within every two accepted slices. Translate
> retail-derived behavior through bounded evidence contracts before consumer
> implementation, then close the product increment rather than the proof
> artifact. Keep the installed game and original BEA.exe immutable, proprietary
> payloads local, Host/Join evidence-gated, and spending or genuinely
> destructive operations separately authorized. Operate unattended with
> conservative reversible assumptions, automated behavioral/visual verification,
> prompt integration, and resume-ready state. If one slice blocks, record the
> exact reason and continue another safe shipping outcome. Stop only at an
> accepted phase boundary, a human pause, or when no meaningful authorized
> product work remains; one advancement is progress, not campaign completion.

## Implementation Scope For The Strategy Rewrite

Once this written design is approved, the strategy implementation updates:

- `roadmap/goals/full-rebuild-campaign-slash-goal.md` with the durable goal
  above;
- `goal.policy.md` with the three outcomes, terminology, consumer-bound slice
  contract, evidence-debt rule, and product acceptance semantics;
- `goal.campaign.md` with product-coupled milestones, explicit reconstruction
  verticals, community WinUI integration, retail enhancement selection, and
  the multiplayer epic;
- `goal.md` with a paused/resume-ready baton that preserves the M2.3 worktree
  but requires its direct consumer queue and product fields;
- `README.MD`, `CURRENT_CAPABILITIES.md`, and `rebuild/README.md` only where
  needed to make the public product relationship clear; and
- a focused strategy consistency test that rejects research-as-outcome,
  consumerless consecutive research slices, strict-clean-room mislabeling,
  premature milestone landing, and loss of the community-release or
  multiplayer objectives.

The strategy rewrite does not execute M2.3, launch BEA, test P1/P2 ordering,
change reconstruction behavior, add patches, modify WinUI, extract assets, or
publish a release. Those are campaign slices selected after the user resumes
the implemented durable goal.
