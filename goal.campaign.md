# Product-Coupled Battle Engine Aquila Campaign

Status: **ACTIVE durable campaign — execution paused; no worker assigned**
Last updated: 2026-07-15 (shield observation blocked; WinUI Reconstruction queued)

Policy: [`goal.policy.md`](goal.policy.md)
Mutable baton: [`goal.md`](goal.md)
Slash goal: [`roadmap/goals/full-rebuild-campaign-slash-goal.md`](roadmap/goals/full-rebuild-campaign-slash-goal.md)

This roadmap coordinates one portfolio with three shipping outcomes:

1. the community WinUI Toolkit;
2. a playable RE-informed original-code reconstruction; and
3. meaningful retail tools, patches, mods, and original-game multiplayer
   progress.

Reverse engineering, source crosswalks, runtime measurement, assets, lore,
documentation, and harnesses support those outcomes. They do not replace them.
The mutable baton owns the current slice; this file changes only when product
priority, milestone state, or an exit criterion materially changes.

## Current product truth

- **WinUI Community:** WinUI 3 is the released community front door. The
  current public `v1.0.9` toolkit supports preservation, saves/options,
  safe-copy patching, media, and Lore. It does not yet provide a coherent
  Reconstruction surface or manage First Flight.
- **Playable Reconstruction:** `rebuild/` contains deterministic Core,
  headless replay/hash verification, and a playable procedural Godot First
  Flight client. Motion scalars are partially retail-derived; resources,
  combat, targeting, world, missions, presentation, and retail content remain
  incomplete or synthetic as documented by their contracts. Both capped shield
  observations produced zero active shield edges and failed the
  minimum-active-edge gate, so no retail-derived shield value, accepted pair,
  or consumer was accepted.
- **Retail Enhancement:** copied-target safe patching and a 29-row catalog are
  established, but most shipped value is compatibility, presentation, or lab
  tooling. Original-game multiplayer is an explicit strategic epic, not a
  released capability; Host/Join stays disabled.
- **Retail assets:** local user-owned asset extraction/import is supported only
  in bounded forms. Proprietary payloads are not tracked or redistributed, and
  complete-corpus extraction has not been proven.
- **Split-screen expectation:** retained source/tests currently shape P1 as the
  top viewport and P2 as the bottom viewport. No fresh native copied-runtime
  P1/P2 ordering test has occurred in this strategy rewrite.

## Campaign operating rules

1. At most one Current Slice is selected. While execution is active, it names a
   primary outcome, user outcome, evidence question, exact consumer,
   acceptance, non-claims, and next link.
2. Retail-derived behavior reaches Core, Godot, WinUI, or a retail patch only
   through evidence proportionate to the claim. A behavior contract does not land
   a product milestone; its consumer must land too.
3. No second consecutive research-only slice is selected without a concrete
   dependency on an unsafe or misleading consumer implementation. Absent that
   dependency, every two accepted slices include a user-observable result.
4. Automated behavioral, visual, capture/replay, native, and regression
   evidence is built with the consumer where it can replace subjective human
   verification.
5. If one slice blocks, record the exact blocker and move to another safe
   shipping outcome. Do not manufacture paperwork or shallow UI to satisfy the
   visible-result rule.
6. Keep installed game files and the original `BEA.exe` immutable; operate on
   copied targets and local user-owned payloads only.

Evidence debt, contracts, checkers, documentation, and standalone harnesses
remain research-only for these rules unless their exact consumer and
acceptance land in the same slice. A user-observable result must change an
invocable WinUI, playable-reconstruction, or copied-retail user path; internal
receipts, operator-only proof UI, disabled controls, or test counts do not
qualify alone.
The result must materially improve and end-to-end accept the named user task;
navigation-only shells, no-op commands, inert scaffolds, and unusable output do
not qualify.

## Consumer-first next-slice picker

After each closeout, choose the highest-value actionable item in this order:

1. correct a shipped safety, data-integrity, or dangerously misleading defect;
2. pay **actionable evidence debt** that blocks a named consumer and cannot be
   implemented honestly yet;
3. complete the nearest playable reconstruction vertical in Core plus its
   headless/Godot acceptance path;
4. deliver a high-value retail enhancement or advance the original-game
   multiplayer epic through a bounded copied-target experiment;
5. integrate a proven reconstruction or retail workflow into the community
   WinUI Toolkit and, when ready, its community release;
6. advance local retail asset/mission import that feeds a named playable or
   WinUI consumer; or
7. improve community knowledge only when it directly supports use,
   contribution, rights/provenance clarity, or the next product decision.

Selection considers user value, dependency criticality, uncertainty reduction,
reversibility, and verification cost—not research counts. A user-observable
result changes what a user can play, see, configure, import, patch, or reliably
verify. Documentation alone qualifies only when the documentation itself is
the community-facing product need.

## Milestone map

Statuses: `open` | `in_progress` | `landed` | `blocked` | `deferred`

### P0 — Product integration foundation

| ID | Consumer-complete increment | Status | Current boundary |
|---|---|---|---|
| P0.1 | Single-writer authority, safe copied-target boundary, mutable baton | landed | One root or designated sole worker owns execution; coordination is optional and need-shaped. |
| P0.2 | Product-coupled slice contract and regression guard | landed | Canonical authorities and both focused strategy/foundation guards are aligned. |
| P0.3 | Deterministic Core/client/headless architecture and First Flight | landed | Foundation only, not retail parity. |
| P0.4 | WinUI/AppCore safe-copy and community release foundation | landed | Latest published app is `v1.0.9`. |

### P1 — Playable reconstruction verticals

| ID | Consumer-complete increment | Status | Current boundary |
|---|---|---|---|
| P1.1 | Procedural First Flight movement/transform vertical | landed | Playable Core/Godot foundation with bounded measured motion constants. |
| P1.2 | Coherent energy + shield resource loop | blocked | Energy drain is consumed; both capped shield attempts failed the active-edge gate, so no retail shield contract or Core/Godot consumer is authorized. |
| P1.3 | Firing, projectile, damage, and destruction loop | in_progress | Current behavior is synthetic/provisional; retail evidence and consumer goldens remain. |
| P1.4 | Deterministic target selection and lock feedback | in_progress | M2.3 static contract now prevents the projectile-shaped misinterpretation; runtime target choice/lock timing and the Core/Godot consumer remain. |
| P1.5 | Camera, world, mission, enemy, and progression verticals | open | Select the smallest playable loop after resources/combat/targeting. |
| P1.6 | Automated playable acceptance | in_progress | Headless hashes and native Godot smoke exist; grow with each vertical. |

### P2 — Community WinUI integration and releases

| ID | Consumer-complete increment | Status | Current boundary |
|---|---|---|---|
| P2.1 | Preservation/saves/options/patch/media/Lore community front door | landed | Public `v1.0.9`; bounded native harnesses exist. |
| P2.2 | WinUI Reconstruction surface | open | Queued next: discover, explain, configure, verify, and launch First Flight without claiming it is already bundled or retail-complete. |
| P2.3 | WinUI local retail-content workflow | open | Guide user-owned extraction/import with provenance and local-only boundaries. |
| P2.4 | Community release of a product-coupled increment | open | Exact artifact and claims must pass release gates; releases are not automatic. |

### P3 — Retail enhancements and mods

| ID | Consumer-complete increment | Status | Current boundary |
|---|---|---|---|
| P3.1 | Safe copied-install creation, patch/restore, launch/stop | landed | Original installation and executable remain immutable. |
| P3.2 | High-value patch/mod expansion | in_progress | Prefer a meaningful player-visible capability over catalog volume. |
| P3.3 | Mod verification and rollback receipts | in_progress | Extend only with each new mutation contract. |
| P3.4 | Community-facing mod discovery/presets | open | WinUI consumer; descriptions stay bounded to proof. |

### P4 — Original-game multiplayer epic

| ID | Consumer-complete increment | Status | Current boundary |
|---|---|---|---|
| P4.1 | P1/P2 viewport, device, state, and command ownership map | open | Fresh copied-runtime ordering/ownership test is queued; source-shaped top/bottom expectation is not runtime acceptance. |
| P4.2 | Distinct command-source causality across separate processes/endpoints | open | Same-process or loopback evidence cannot satisfy this gate. |
| P4.3 | Reversible transport/helper prototype for copied targets | open | No installed-game mutation; exact identity and rollback required. |
| P4.4 | WinUI session UX, identity, invitations, lifecycle, and cleanup | open | Host/Join remains disabled until accepted causality and safety gates. |
| P4.5 | Community multiplayer experiment/release | deferred | Requires distinct-endpoint, security, failure, and player-readiness acceptance. |

### P5 — Retail asset and mission import

| ID | Consumer-complete increment | Status | Current boundary |
|---|---|---|---|
| P5.1 | Deterministic AYA inventory/export records | in_progress | Producer prerequisites exist; complete-corpus extraction/export is unproven. |
| P5.2 | Local user-owned mesh/texture presentation in Godot | in_progress | Bounded local mesh path exists; identity/material/animation fidelity remains unresolved. |
| P5.3 | Mission/world data model and playable importer | open | Parser evidence must feed an exact Core/Godot consumer. |
| P5.4 | WinUI local import orchestration | open | Do not bundle or publish proprietary assets. |

### P6 — Community knowledge supporting outcomes

| ID | Consumer-complete increment | Status | Current boundary |
|---|---|---|---|
| P6.1 | Searchable packaged Lore/RE reading experience | landed foundation | Breadth is not editorial completeness or canon proof. |
| P6.2 | Contributor-facing evidence/provenance maps | in_progress | Maintain only when they unblock safe implementation or review. |
| P6.3 | Player/modder guides tied to shipped workflows | open | Couple guides to WinUI, reconstruction, mod, or multiplayer consumers. |
| P6.4 | Rights and non-claim clarity | continuous | Repository licenses cover only their named material. |

## Immediate product-coupled sequence

1. **Respect the shield closeout:** exactly two separately closed copied-runtime
   observations reached ready neutral state, produced zero active shield edges,
   and failed the minimum-active-edge gate. They did not form an accepted
   canonical pair. No contract, Core mapping, or acceptance waiver follows,
   and no third runtime attempt is authorized by that exhausted slice.
2. **Add WinUI Reconstruction:** give community users a truthful surface to
   discover, configure, verify, and launch the playable companion.
3. **Exercise the multiplayer foundation:** run the bounded P1/P2 viewport and
   command-ownership experiment, then choose the next causality consumer from
   evidence rather than assumption.
4. **Continue consumer-complete combat/targeting or retail-mod increments**
   using the picker, keeping asset/mission import attached to a playable or
   WinUI consumer.

## Closed measurement ledger

These are accepted evidence prerequisites already consumed by deterministic
Core. They remain bounded retail findings, not proof of full reconstruction:

| System | Public contract / consumer | Private pair |
|---|---|---|
| Walker forward | `walker-forward-scalar-response-v2` → `WalkerSpeedPerTick` | p27 |
| Jet thrust | `jet-forward-scalar-response-v1` → `JetSpeedPerTick` | jet-p06 |
| Walker Look/Left yaw | `walker-turn-yaw-scalar-response.v1` → Core look rate | turn-p02 |
| Walker strafe | `walker-strafe-lateral-scalar-response.v1` → Core strafe rate | strafe-p02 |
| Walker→jet settle | `walker-transform-morph-timing.v1` → Core morph timing | xform-p03 |
| Jet energy drain | energy scalar v1 → `JetEnergyDrainPerTick=17` | energy-p02 |

Shield regeneration, fire cooldown, projectile speed, coast/friction, target
selection causality, camera presentation, and P1/P2 ownership are not in this
closed ledger.

## Phase exit criteria

The campaign may pause at an accepted phase boundary only when all hold:

1. At least one new playable vertical beyond the procedural foundation is
   consumer-complete in Core and its headless/Godot acceptance path.
2. WinUI exposes at least one truthful reconstruction or new retail-enhancement
   workflow useful to the community.
3. At least one meaningful retail enhancement or multiplayer epic gate has
   advanced through evidence to an executable consumer or an exact durable
   blocker.
4. Active evidence debt names its consumer or has moved to backlog; no open
   contract/checker chain is being counted as a landed product milestone.
5. Touched product gates are green, proprietary payloads remain local, the
   installed game/original executable remain immutable, and `goal.md` is
   resume-ready.
6. The active campaign owner or maintainer accepts the phase boundary. Full retail
   parity, strict clean-room status, player-ready online play, or exhaustive
   extraction are never inferred from phase completion.

One advancement is progress, not campaign completion. A blocked slice is not
a blocked portfolio while another safe product outcome remains actionable.
