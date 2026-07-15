# Retail → Core translation policy (walker-forward scalar)

Status: **accepted** (2026-07-14) — identity scale \(s=1\); Core edits may now cite this policy  
Depends on: [walker-forward-scalar-response-v2.md](walker-forward-scalar-response-v2.md)

## Purpose

Separate the measured retail scalar envelope from any future deterministic Core
constant. Agreement between Core and this policy is **not** retail proof; retail
truth remains the copied-runtime measurement.

## Measured retail quantities (inputs)

From `battleengine-walker-forward-scalar-response.v2` pair evidence:

- Steady speed \(v_r \in [2.850, 3.150]\) retail-world units / second
- Response latency \(L_\mathrm{on} \in [0, 80]\) ms (from control-store prove)
- Release latency \(L_\mathrm{off} \in [0, 140]\) ms
- Inferred physics edge period \(T_p \approx 0.05\) s (hypothesis band 0.5×–2×)
- Per-update displacement step \(\approx v_r \cdot T_p\) (≈ 0.15 retail units / update at \(v_r = 3\))

## Translation parameters (to accept before Core write)

| Parameter | Proposed default | Notes |
|-----------|------------------|-------|
| Coordinate scale | Core integer **milli-retail** units: \(1000\) Core = \(1\) retail-world unit | Fits fixed-step integer Core; arena half-extent \(30000\) ≈ \(30\) retail units |
| Tick model | Core fixed \(30\) Hz (\(\Delta t = 1/30\) s) | Core-local; retail edge period ≈ \(50\) ms remains a hypothesis |
| Speed map | \(v_\mathrm{tick} = \mathrm{round}(v_r \cdot 1000 / 30)\) | For \(v_r \in [2.85, 3.15]\): \(v_\mathrm{tick} \in [95, 105]\); accepted default **100** |
| On latency | Core may apply full step speed on the input tick | Retail \(L_\mathrm{on} \le 80\) ms is not modeled as a ramp |
| Off latency | Core may zero velocity on release tick | Retail \(L_\mathrm{off} \le 140\) ms residual is not required |
| Rounding | integer truncation toward zero on diagonal \(181/256\) | Existing Core diagonal rule unchanged |
| Quantization | one Core milli-unit | Bound for position goldens |
| Overflow | clamp to arena; reject non-finite only if floats reappear | Integer path has no NaN |

## Acceptance checklist

Before any Core walker speed edit:

1. [x] This policy file is marked **accepted** (identity scale).
2. [x] Scalar v2 projection remains the authority for retail numbers.
3. [ ] Core goldens cite this policy and the v2 schema version explicitly.
4. [x] No claim that Core agreement re-proves retail.

## Core authorization

With status **accepted**, deterministic Core may set
`WalkerSpeedPerTick = 100` (milli-retail units at 30 Hz ≈ 3.0 retail units/s),
citing this policy and the v2 schema. Core self-agreement does not re-prove retail.
