# Full Reconstruction Campaign

Status: **ACTIVE durable campaign**  
Last updated: 2026-07-15 (Save Lab unattended native workflow acceptance landed; Media/catalog harness next)

Policy: [`goal.policy.md`](goal.policy.md)  
Mutable baton: [`goal.md`](goal.md)  
Slash prompt: [`roadmap/goals/full-rebuild-campaign-slash-goal.md`](roadmap/goals/full-rebuild-campaign-slash-goal.md)

This file is the **long-horizon roadmap** for reverse-engineering, rebuilding,
and productizing Battle Engine Aquila work in this repo. Agents mutate
[`goal.md`](goal.md) every cycle; they update **this** file when a milestone
status, priority, or exit criterion changes—not for routine slice chatter.

## North star

Produce a growing, **evidence-backed reconstruction** of Battle Engine Aquila:

| Lane | North-star outcome |
|------|--------------------|
| **RE** | Source-named systems mapped with static + copied-runtime proof, contracts in retail units |
| **Rebuild** | Deterministic Core + Godot adapter implementing accepted contracts (RE-informed, not fake clean-room) |
| **WinUI 3** | Primary toolkit: safe-copy, patch/mod, saves, media/lore, honest labels for proven vs research |
| **Lore** | Searchable, linked, packageable narrative/history without hard payloads |
| **Harnesses** | Automated unit/integration/runtime gates so each land stays green |

**Not** the north star: mutate Steam install, claim parity-complete retail clone,
player-ready online, public release/tag without separate authority, or thrash on
known hard blockers (e.g. MSB4278 native AYA DLLs) without new evidence.

## Operating rules (summary)

Full loop contract lives in `goal.policy.md`. Campaign-specific:

1. **One active slice at a time** in `goal.md`, but the campaign runs **many
   slices in sequence** until exit or a well-formed `BLOCKED_*` record.
2. **Agent chooses the next slice** using the priority order below after each
   `ADVANCEMENT` or resolved blocker—not only when a human rewrites the slice.
3. **Measurement before Core** for retail-derived scalars/behavior: dual-accept
   copied-runtime (or equivalent named gate) → public contract → translation
   policy → Core/goldens/tests.
4. **Harness with the work:** every new behavior path gets the smallest durable
   test/checker that would catch regression; prefer `tools/*_test.py`, AppCore
   tests, `npm run test:rebuild`, focused WinUI gates.
5. **Lab hygiene:** safe-copy while running; strip bulky trees after closeout;
   keep compact evidence only (`runtime-proof-lab-retention.md`).
6. **Lane balance:** do not starve WinUI or lore for rebuild-only sprints, or
   the reverse, for more than ~3 consecutive slices unless a hard dependency
   forces it—record the bias in `goal.md`.

## Priority order (default next-slice picker)

When choosing the next slice, walk this list top-down; take the first item that
is **actionable**, **not closed**, and **not blocked without a new attempt**:

1. **Unblock / hygiene** — disk explosion, broken gates, false CI, unsafe path
2. **Rebuild-grade RE contract** ready to land (measurement done, Core pending)
3. **Next scalar/system measurement** that unblocks Core fidelity
4. **Core + goldens + harness** for an accepted contract
5. **Godot/Client adapter** only as needed for the new Core truth
6. **WinUI product** — safe-copy, patch honesty, save lab, media, Home focus if
   native proof is authorized
7. **Lore / packaging** — links, pack freshness, offline search quality
8. **Asset/AYA pipeline** — only if extractor/tooling blocker cleared
9. **Online research** — docs/proof ladders only; Host/Join stays disabled
10. **Docs/state truth** — only when it unblocks the next real slice

Skip thrashing: if the same blocker repeats without new evidence, escalate via
`BLOCKED_*` with owner/next_action, do not invent a fifth identical attempt.

## Milestone map

Statuses: `open` | `in_progress` | `landed` | `blocked` | `deferred`

### M0 — Operating system (landed foundation)

| ID | Milestone | Status |
|----|-----------|--------|
| M0.1 | Public primary repo + `AGENTS.md` / validation matrix | landed |
| M0.2 | WinUI + AppCore + CLI primary product lane | landed |
| M0.3 | Rebuild Core + Headless goldens + Godot First Flight | landed |
| M0.4 | `/goal` policy + mutable baton + lab retention hygiene | landed |
| M0.5 | Walker + jet scalar contracts → Core speeds | landed |

### M1 — Motion & vehicle fidelity (rebuild-grade)

| ID | Milestone | Status | Notes |
|----|-----------|--------|-------|
| M1.1 | Walker forward scalar | landed | v2 + `WalkerSpeedPerTick=100` |
| M1.2 | Jet forward/thrust scalar | landed | v1 + `JetSpeedPerTick=381` |
| M1.3 | Turn / yaw rate scalar | landed | turn-p02 dual-accept; v1 + policy; `WalkerLookYawRateMilliRadPerTick=3`; Core LookX integrate |
| M1.4 | Strafe / lateral scalar | landed | strafe-p02 dual-accept; v1 + policy; `WalkerStrafeSpeedPerTick=101` |
| M1.5 | Transform morph timing + energy gate | landed | xform-p03 dual-accept; `MorphToJetSettleTicks=148` |
| M1.6 | Friction / coast / release models beyond scalar speed | in_progress | offline half-life scaffold landed; live dual-accept pending |

### M2 — Combat & resources

| ID | Milestone | Status |
|----|-----------|--------|
| M2.1 | Fire cooldown / projectile speed retail contracts | in_progress | scaffolds + pair envelopes + draft policies; live dual-accept pending |
| M2.2 | Damage / hull / shield regeneration contracts | in_progress | **jet energy drain dual-accepted energy-p02 → JetEnergyDrainPerTick=17**; shield BE+0x100 neutral-control/input-free runner and symmetric correlation gate landed, live pair authority-blocked; walker regen provisional |
| M2.3 | Target / lock behavior (bounded, evidence-first) | open |
| M2.4 | Core combat goldens + harness expansion | open |

### M3 — World, camera, UI systems (rebuild + RE)

| ID | Milestone | Status |
|----|-----------|--------|
| M3.1 | Camera / look contracts (retail → Core/Client) | in_progress | body LookX Core/Client/Godot from turn-p02; camera scaffold offline; free-cam not Core authority |
| M3.2 | Level load readiness gates (850-class smoke stays) | open |
| M3.3 | Mission/script hooks as public-safe behavior contracts | open |
| M3.4 | Godot presentation upgrades driven by Core truth only | open |

### M4 — Assets & extraction

| ID | Milestone | Status |
|----|-----------|--------|
| M4.1 | Safe Python / tracked extraction pipeline | landed / partial |
| M4.2 | Full AYA corpus export | blocked | MSB4278 / native DLL |
| M4.3 | Local Godot BYO mesh path (non-parity) | landed foundation |
| M4.4 | Catalog/import product path honesty in WinUI | open |

### M5 — WinUI product depth

| ID | Milestone | Status |
|----|-----------|--------|
| M5.1 | Safe-copy launch / stop / patch apply-restore | landed foundation |
| M5.2 | Patch catalog honesty + Lab UX | landed foundation |
| M5.3 | Home native-focus acceptance | landed | unattended exact-build first-run/ready focus plus normal/760 schema-3 visual receipts |
| M5.4 | Save Lab / options workflows polish + tests | landed | exact repo-build UIA-only first-use/options gate; 8 normal/compact captures, 2 semantically reparsed workflows, receipt-bound cleanup, zero process census |
| M5.5 | Media library + catalog workflows | open |
| M5.6 | Release hygiene (no auto-release from campaign) | open |

### M6 — Lore & knowledge

| ID | Milestone | Status |
|----|-----------|--------|
| M6.1 | Lore pack generation + offline search | landed foundation |
| M6.2 | Link integrity / browser-opening labels | landed foundation |
| M6.3 | Curated BOOK / index freshness vs RE corpus | open |
| M6.4 | Provenance/rights non-claims kept accurate | open |

### M7 — Online research (not product netplay)

| ID | Milestone | Status |
|----|-----------|--------|
| M7.1 | Distinct-endpoint command-source proof ladder | open |
| M7.2 | Host/Join remains disabled until accepted proofs | in force |
| M7.3 | Docs only until causality proofs land | open |

### M8 — Harness maturity (continuous)

| ID | Milestone | Status |
|----|-----------|--------|
| M8.1 | Runtime pair runners + unit tests (no live BEA for unit) | landed foundation |
| M8.2 | Lab strip after closeout | landed |
| M8.3 | Per-system regression checkers for each landed contract | landed | walker+jet+yaw+strafe JSON regression CLI (2026-07-15) |
| M8.4 | Expand `npm` scripts only when a gate is re-run often | open |

## Campaign exit criteria (when `/goal` may stop)

The campaign may declare **phase-complete** (not “game fully reverse-engineered”)
when **all** hold:

1. M1 motion scalars needed for playable First Flight fidelity are **landed**
   or **deferred** with written non-claims.
2. M2 combat has at least one dual-accept or static-backed Core contract for
   fire + projectile path, or explicit deferred non-claims.
3. Rebuild `npm run test:rebuild` green; WinUI primary lane gates green for
   touched product surfaces.
4. No multi-GB unmanaged proof trees under active lab roots (hygiene policy).
5. `goal.md` lists remaining open milestones as a **backlog**, not a silent stop.
6. Human or integration owner accepts campaign pause/complete.

**Never** auto-claim: retail parity, clean-room purity, online play-ready, or
public release.

## Closed measurement ledger (compact)

| System | Contract | Core | Private label |
|--------|----------|------|---------------|
| Walker forward | `walker-forward-scalar-response-v2` | `WalkerSpeedPerTick=100` | p27 |
| Jet thrust | `jet-forward-scalar-response-v1` | `JetSpeedPerTick=381` | jet-p06 |
| Walker Look/Left yaw | `walker-turn-yaw-scalar-response.v1` | `WalkerLookYawRateMilliRadPerTick=3` | turn-p02 |
| Walker Movement/Left path | `walker-strafe-lateral-scalar-response.v1` | `WalkerStrafeSpeedPerTick=101` | strafe-p02 |
| Walker morph→jet settle | `walker-transform-morph-timing.v1` | `MorphToJetSettleTicks=148` | xform-p03 |

## How agents update this file

- After landing a milestone: set status → `landed`, one-line note, date.
- After durable blocker: status → `blocked`, link `goal.md` BLOCKED record.
- After reprioritizing: edit priority notes; do not rewrite history.
- Do **not** paste full attempt logs here—keep those in private compact roots
  or RE proof summaries.
