# Retail → Core (walker morph → jet settle)

Status: **accepted** (2026-07-15)  
Depends on: walker-transform-morph-timing.v1 (xform-p03)

- Measured mid-latency ≈ **4.92 s**
- Core 30 Hz: \( t = \mathrm{round}(L_\mathrm{s} \cdot 30) \) → **148** ticks
- Constant: `MorphToJetSettleTicks = 148`
- Distinct from `TransformDurationTicks` (short mode-toggle lock, not morph settle).
