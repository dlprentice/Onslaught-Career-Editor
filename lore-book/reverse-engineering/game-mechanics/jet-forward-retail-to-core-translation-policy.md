# Retail → Core translation policy (jet-forward scalar)

Status: **accepted** (2026-07-14) — identity scale \(s=1\); Core edits may now cite this policy  
Depends on: [jet-forward-scalar-response-v1.md](jet-forward-scalar-response-v1.md)

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
