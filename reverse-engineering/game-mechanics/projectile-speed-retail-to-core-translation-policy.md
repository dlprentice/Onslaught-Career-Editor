# Retail → Core translation policy (projectile speed)

Status: **draft — BUT a Core constant shipped anyway. SUPERSEDED IN PART
2026-07-28; whether the measurement clears this project's dual-accept bar is a
maintainer decision and is recorded below as UNKNOWN.**
Depends on: projectile path-speed dual-accept (not landed)

> **SUPERSEDED IN PART 2026-07-28.** The Status line above previously read, in
> full:
>
> > Status: **draft — blocked on dual-accept**
>
> A policy whose status says "blocked" while the constant it gates is already in
> the shipping deterministic Core cannot tell a reader whether that value was
> authorised or slipped in unauthorised. It shipped. This document has not been
> touched since it was drafted — `git log` returns exactly one commit,
> `c738f811`, 2026-07-14 "docs(re): draft projectile speed retail-to-Core
> policy" — while the constant landed separately.
>
> `rebuild/OnslaughtRebuild.Core/SimulationConstants.cs:388` carries
> `public const int ProjectileSpeedPerTick = 1_167;`, documented in place at
> `:383-387`:
>
> > Fresh copied-Steam Level 100 runs independently repeated four lowest-charge
> > Pulse Cannon rounds against each of the three training tanks. Every round
> > carried definition speed 35 and moved exactly 1.75 units per released 20 Hz
> > update. Core's nearest 30 Hz integer translation is 1.167 units per tick.
>
> **UNKNOWN — is that dual-accept?** Twelve rounds across three targets in
> repeated copied-Steam runs is a copied-runtime observation of exactly the
> quantity this policy lists as pending, but this document does not judge
> whether it satisfies the project's dual-accept bar, and neither does the
> constant's own comment. What would settle it: a named accepted pair (as
> `jet-p06` and `energy-p02` are named for their policies) and a
> `battleengine-projectile-speed-scalar-response.v1` JSON alongside the other
> `*-scalar-response-v1.json` files in this directory. Neither exists today.
> Until one does, the honest status is the one above: shipped, not accepted.

## Measured retail input (pending → landed; see the block above)

Steady projectile path speed from tracked entity samples under fire.

**AMENDED 2026-07-28.** This heading still reads "(pending)" in the original for
the record, but the quantity is no longer unmeasured — see the Status block
above. What remains pending is the *acceptance*, not the measurement.

## Planned translation (not yet authorized)

| Parameter | Planned default |
|-----------|-----------------|
| Tick model | Core fixed 30 Hz |
| Map | milli-retail units/tick like walker/jet speeds |
| Core candidate | `ProjectileSpeedPerTick` |

## Explicit non-claims

- ~~Draft only; no Core constant change authorized.~~ — **OVERTAKEN 2026-07-28.**
  No change was authorized *by this policy*, and none is. But
  `ProjectileSpeedPerTick = 1_167` is in the tree
  (`rebuild/OnslaughtRebuild.Core/SimulationConstants.cs:388`), so this sentence
  no longer describes the repository. It is kept because it correctly records
  what this policy did and did not authorize.
- ~~Source/default projectile speed is not dual-accepted retail truth.~~ —
  **OVERTAKEN 2026-07-28** in one direction only: the shipped value is not a
  source default, it is a copied-runtime observation (definition speed 35,
  1.75 units per released 20 Hz update). Whether it is *dual-accepted* remains
  UNKNOWN — see the Status block.
- Entity pointer chain not yet sampler-wired. — **not withdrawn, and not
  re-checked by the 2026-07-28 pass.** The Level 100 observation cited above was
  taken from released per-update displacement rather than from a wired entity
  sampler, so it does not by itself retire this non-claim.
