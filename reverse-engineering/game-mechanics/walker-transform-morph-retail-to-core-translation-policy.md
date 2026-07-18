# Walker-to-jet transition mapping

Status: accepted bounded mapping
Evidence: [`walker-transform-morph-timing-v1.json`](walker-transform-morph-timing-v1.json)

The canonical Steam `Morph` body and copied-runtime behavior establish these
raw `BattleEngine+0x260` meanings for this path: `2` is walker, `1` is the
walker-to-jet transition, and `3` is jet. A clean Level 100 control reached the
flight-disabled rejection without leaving `2`; two early-flight copies repeated
`2 → 1 → 3` under the same Transform action.

The repeated state-`1` intervals were 535.359–537.249 ms. Deterministic Core
therefore owns an explicit `WalkerToJet` state for 16 intervals at 30 Hz
(533.333 ms), keeps stable mode as Walker until completion, rejects repeated
transform input, and blocks movement, turning, and fire during that state.

This mapping does not cover jet-to-walker timing, visual animation, camera
settling, energy/shield semantics, weapons, or flight dynamics. The retired
148-tick conversion used unmatched endpoints and must not return as a Core
constant.
