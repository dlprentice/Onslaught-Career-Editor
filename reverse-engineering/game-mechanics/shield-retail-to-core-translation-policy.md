# Retail → Core translation policy (shield ownership)

Status: **source-backed ownership accepted; rate remains blocked**

## Measured retail input

None accepted. Exactly two receipt-bound copied-runtime walker attempts ran on
2026-07-15. Each reached the neutral input-free observation phase, but each
produced zero active shield edges rather than the required five. These
separately closed attempts did not form an accepted canonical pair and produced
no publishable shield rate.

## Source-backed ownership

Stuart's `CBattleEngineWalkerPart::Move` assigns `mShields = mEnergy` on every
non-jet update. `CBattleEngineJetPart::Move` assigns `mShields = 0`. Core now
retains that mode ownership and exposes `Shield` as the current energy store in
walker/morph state rather than inventing a separate capacity or regeneration
rate. This is architecture/source evidence, not a copied-Steam rate measurement.

## Explicit non-claims

- No independent shield regeneration scalar is accepted.
- The source mirror-from-energy rule is not a copied-Steam rate measurement.
- The failed observations say neither that shield regeneration is absent nor
  what its scalar, timing, mission scope, damage response, or vehicle scope
  might be.
