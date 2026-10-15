# Retail → Core translation policy (jet-forward scalar)

Status: **accepted (2026-07-14) for the retail measurement; SUPERSEDED 2026-07-28
for the Core mapping** — identity scale \(s=1\).
Depends on: [jet-forward-scalar-response-v1.md](jet-forward-scalar-response-v1.md)

> **SUPERSEDED 2026-07-28 — the Core mapping only.** The Status line above
> previously read, in full:
>
> > Status: **accepted** (2026-07-14) — identity scale \(s=1\); Core edits may now cite this policy
>
> The constant this policy authorises no longer exists.
> `grep -rn 'JetSpeedPerTick' rebuild/OnslaughtRebuild.Core/` returns nothing.
> Core now carries a two-ended envelope instead of a flat scalar —
> `JetMinimumSpeedPerTick = 200` / `JetMaximumSpeedPerTick = 600`
> (`rebuild/OnslaughtRebuild.Core/SimulationConstants.cs:125-129`) — read from the
> shipped `mMinAirVelocity 0.3` / `mMaxAirVelocity 0.9` bytes in record 3 of
> `data/battle engine configurations.dat` (SHA-256 `58722b12…`, 1,514 bytes). So
> the authority for the Core value moved from a copied-runtime pair to shipped
> data, and the shape of the model changed with it.
>
> **What is NOT withdrawn:** the retail measurement. `jet-p06`'s steady speed of
> 11.431 retail units/s still matches
> `battleengine-jet-forward-scalar-response.v1` exactly, and
> [`jet-forward-scalar-response-v1.md`](jet-forward-scalar-response-v1.md)
> remains the copied-runtime authority for retail jet cruise speed. Only the
> "Core edits may now cite this policy" clause is dead, because there is no
> longer a `JetSpeedPerTick` for a Core edit to set.

## Purpose

Separate the measured retail jet thrust scalar envelope from deterministic Core
`JetSpeedPerTick`. Agreement between Core and this policy is **not** retail
proof; retail truth remains the copied-runtime measurement (pair `jet-p06`).

## Measured retail quantities (inputs)

From `battleengine-jet-forward-scalar-response.v1`:

- Steady speed \(v_r \in [10.860, 12.003]\) retail-world units / second
- Response latency \(L_\mathrm{on} \in [0, 100]\) ms (idle-cruise relative threshold)
- Release latency \(L_\mathrm{off} \in [0, 90]\) ms (coast below active cruise)
- Inferred physics edge period \(T_p \approx 0.05\) s (hypothesis band 0.5×–2×)
- Per-update displacement step \(\approx v_r \cdot T_p\) (≈ 0.57 retail units / update at \(v_r = 11.43\))

## Translation parameters

| Parameter | Accepted default | Notes |
|-----------|------------------|-------|
| Coordinate scale | Core integer **milli-retail** units: \(1000\) Core = \(1\) retail-world unit | Same as walker policy |
| Tick model | Core fixed \(30\) Hz (\(\Delta t = 1/30\) s) | Core-local; retail edge period ≈ \(50\) ms remains a hypothesis |
| Speed map | \(v_\mathrm{tick} = \mathrm{round}(v_r \cdot 1000 / 30)\) | For \(v_r \in [10.860, 12.003]\): \(v_\mathrm{tick} \in [362, 400]\); accepted default **381** |
| On latency | Core may apply full jet step speed on the input tick | Retail \(L_\mathrm{on} \le 100\) ms is not modeled as a ramp |
| Off latency | Core may drop to non-thrust speed on release tick | Retail coast residual is not required |
| Rounding | integer truncation toward zero on diagonal \(181/256\) | Existing Core diagonal rule unchanged |
| Quantization | one Core milli-unit | Bound for position goldens |
| Overflow | clamp to arena | Integer path has no NaN |

## Acceptance checklist

1. [x] This policy file is marked **accepted**.
2. [x] Jet scalar v1 projection remains the authority for retail numbers.
3. [x] Core goldens cite this policy and the v1 schema version explicitly after update.
4. [x] No claim that Core agreement re-proves retail.

## Core authorization

With status **accepted**, deterministic Core may set
`JetSpeedPerTick = 381` (milli-retail units at 30 Hz ≈ 11.43 retail units/s),
citing this policy and schema `battleengine-jet-forward-scalar-response.v1`.
Core self-agreement does not re-prove retail.

The previous unmeasured placeholder `650` is superseded by this measurement.

**SUPERSEDED 2026-07-28.** The authorization above is retained verbatim as the
record of what was accepted on 2026-07-14, but it no longer describes the tree:
there is no `JetSpeedPerTick` in `rebuild/OnslaughtRebuild.Core/` to set. See the
block under the Status line at the head of this document. Do not act on this
section without reading that block first.
