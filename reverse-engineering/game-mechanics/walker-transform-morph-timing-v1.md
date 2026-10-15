# Walker-to-jet raw-state timing

Status: accepted for the bounded Core transition mapping
Schema: `battleengine-walker-transform-state-timing.v2`

One clean Level 100 copy delivered Transform action `0x21` to player one's
BattleEngine, entered `Morph`, hit the flight-disabled rejection, and remained
in raw state `2`. Two fresh copies with the proven early-flight archive change
repeated raw states `2 → 1 → 3`.

An uninterrupted read-only sampler measured raw state `1` through raw state `3`
at **535.359–535.393 ms** and **537.208–537.249 ms**. Debugger markers proved
the input/Morph identities and detached before state `1`; they did not provide
timing. Core maps this bounded transition to 16 intervals at 30 Hz (533.333 ms).

The old 4.67–5.17 second result did not use these identified state endpoints and
is not a transform duration. This measurement does not establish animation,
camera, jet-to-walker, energy, shield, weapon, or flight-dynamics parity.
