# Energy live dual-accept checklist (public)

Status: **closed ADVANCEMENT** (pair `energy-p02`, 2026-07-14)  
Related: [jet-energy-drain-scalar-response-v1.md](jet-energy-drain-scalar-response-v1.md)

## Preconditions

1. Copied BEA only (never Steam install mutation).
2. Windowed, controllable mission with player-0 jet available.
3. Authorized private root under ignored lab overlay for receipts/raw.
4. Sampler offsets: `BATTLE_ENGINE_ENERGY_OFFSET=0xFC`.

## Procedure

1. Launch copied profile (example ignored path: `GameProfiles/marathon-energy-jet-01`).
2. Enter mission; transform or spawn jet.
3. Write identity-bound receipt (module path/hash, PID/start, window, BEA module).
4. Run two attempts:
   ```
   --measure energy --vehicle jet
   ```
   via `tools/run_battleengine_walker_trajectory_measurement.py`.
5. Confirm both attempts accepted by energy scaffold (negative steady drain).
6. `materialize_energy_pair_envelope` → public v1 contract → accept translation policy → Core constants + goldens.

## Hygiene

Strip bulky private trees after closeout. Do not commit GameProfiles, receipts,
or raw captures.
