# Retail → Core translation policy (shield regen/drain)

Status: **closed blocked — capped dual-accept did not materialize**
Depends on: shield rate dual-accept (no accepted pair or contract landed)

## Measured retail input

None accepted. Exactly two receipt-bound copied-runtime walker attempts ran on
2026-07-15. Each reached the neutral input-free observation phase, but each
produced zero active shield edges rather than the required five. These
separately closed attempts did not form an accepted canonical pair and produced
no publishable shield rate.

## Planned translation (not yet authorized)

| Parameter | Planned default |
|-----------|-----------------|
| Tick model | Core fixed 30 Hz |
| Core candidates | `WalkerShieldRegenerationPerTick` |

## Explicit non-claims

- No Core constant change is authorized by this closed slice.
- Source shield-efficiency and mirror-from-energy rules are not dual-accepted rates.
- The failed observations say neither that shield regeneration is absent nor
  what its scalar, timing, mission scope, damage response, or vehicle scope
  might be.
