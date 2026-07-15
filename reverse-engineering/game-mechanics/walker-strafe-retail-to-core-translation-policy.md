# Retail → Core translation (walker Movement/Left path speed)

Status: **accepted** (2026-07-15)  
Depends on: walker-strafe-lateral-scalar-response.v1 (strafe-p02)

- \(v_r \approx 3.015\) retail units/s  
- Map: \(v_\mathrm{tick} = \mathrm{round}(v_r \cdot 1000 / 30)\) → **101**  
- Accepted Core: `WalkerStrafeSpeedPerTick = 101` (milli-retail @ 30 Hz)  
- Source defaults do not authorize this constant. Core agreement ≠ retail proof.
