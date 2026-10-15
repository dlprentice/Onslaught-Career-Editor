# CBattleEngine__AddShockShake

Status: active, bounded instruction and original-code contract
Last updated: 2026-09-26
Summary: float threshold, replacement shake fields, separate engine/cockpit RNG and the retail no-op rumble boundary.
Evidence: MEASURED — complete pristine bodies/callers/constants and 41 isolated original-code cases; SOURCE — pinned BattleEngine counterpart; no rendered or device acceptance.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: `references/Onslaught/BattleEngine.cpp:1094–1115`, commit `5352a81cdb838b145a57f7febc5d9fc4b0129ebb` | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00407940`

## Identity and interface

Complete body `[0x00407940,0x00407a43)`, 259 bytes, SHA-256
`25d91776f1c292df959df7ff23bf0237a03369f8b18381d4ee71904a7e8cdc45`.
The current name is `CBattleEngine__AddShockShake`; the filename retains the
former analytic label for link stability. ECX is the receiver, entry stack +4
contains a float, and `RET 4` removes that argument. No prototype change is
needed for this function. Direct callers are Damage at `0x0040abc2` and the
RecoilWeapon counterpart at `0x0040c355`.

## Order and numerical contract

1. Compare the float argument to **binary64** `0.001` at `0x005d8bc8`.
   `TEST AH,1` returns before any RNG, field or player access when it is smaller,
   or unordered with x87 exceptions masked. Float bit patterns `3a83126e` and
   `3a83126f` lie on opposite sides. They also straddle the rounded binary32
   threshold, so rounding that constant does not change the accepted float inputs.
2. Cap accepted amounts above `0.75f`. Store `s = float32(16 / amount)`.
3. Call game RNG `0x004de8d0` three times, through seed pointer `0x008a9d9c`.
   Replace receiver `+0x4b8`, `+0x4bc`, `+0x4c0` in order with
   `float32(signed_remainder(draw,32) / s − amount)`. The `+0x4c4` clear
   at `0x00407a03` occurs before the third component store at `0x00407a15`.
   These writes replace prior values; they do not accumulate them. The usual
   nonnegative remainders span 0–31, with an asymmetric interval around zero.
   Use the stored divisor, not an algebraically rearranged expression, when
   matching floating-point results.
4. If `+0x528` is nonnull, call [CCockpit__AddShockShake](../../binary-analysis/functions/Cockpit.cpp/CCockpit__AddShockShake.md)
   with the **already-capped float bits**, after the three engine draws. There is no
   float-to-int conversion. The former factory draft's cast was wrong.
5. Read player pointer `+0x574`, then player number `+0x2c`, subtract 1 and call
   `0x00452b60` with receiver `0x0088a0a8`. This entire retail callee is `RET 4`
   (SHA-256 `e598d0c3ba86d917b177d7adde0556aa99bc355543c57aee0a3e50b684dd7e99`).
   Its historical frontend name does not make this a frontend operation.
   The source call is TriggerRumble; pinned PC source forwards into substantive
   platform code, while this retail body has no hardware effect. The preceding
   player dereferences still occur, including when cockpit is null.

Game RNG has multiplier 48271 and the unusual modulus **214783647**, read from
`0x006321f0/0x006321f4`. It uses signed division and wrapped 32-bit arithmetic,
not arbitrary-precision Park–Miller with modulus 2147483647. Stored states can
be negative; the return applies signed negation to a negative stored state.
The controlled initial seed 1 ends after three draws at signed −649368920;
initial seed 12345 ends at −732905716. The cockpit instead uses four CRT rand
calls and a separate thread-data seed. Its presence must not add four draws
to the gameplay stream.

## Executed evidence

The [Damage recheck](../../binary-analysis/functions/BattleEngine.cpp/CBattleEngine__Damage.md)
owns the shared 41-case experiment and its precise limits. Private receipt:
`local-data/test-runs/re-audit-20260926/battleengine-damage/run-iekrvvq7/damage.json`,
SHA-256 `f6a2aab65ef85d1558332a3a3605845cd786a7c1c8949149dac52e9b2a6c130d`.
It runs this full body, Damage, cockpit, both RNGs and the no-op callee unchanged.
Direct threshold, clamp, negative and NaN cases isolate the gate. Null/non-null
cockpit cases separate the two seed streams. Game call counts are inferred from
static paths and final seeds; CRT thread-data-provider entries are counted.

At amount `0.25`, game seed 12345 produces engine components
`(0.140625, 0.234375, 0.0625)`. With cockpit present and its CRT seed 1, cockpit
components are approximately `(-0.01, -0.01, -0.00390625, -0.1171875)`;
only the first three are clamped. Damage's invulnerability restoration occurs
**after** this call and does not restore either RNG or these fields.

## Evidence limits and historical record

The August 22 packet and its range digests remain frozen historical evidence;
its no-TTD-execution statement concerned that bounded deep-mine corpus. The
current name, float forwarding and operation meanings supersede its analytic
names and integer-cast claim. This does not promote its campaign grade.

Authored objects and a substituted CRT thread-data provider establish bounded
original-code behavior, not full CRT lifecycle, real camera consumption,
rendered motion, devices or player experience. The first three fields have
source names yaw/pitch/roll shake, but their downstream units and perceptual
application still require consumer/runtime checks. Invalid pointers, unmasked
exceptions and arbitrary state were not tested. The cheapest next falsifier is
a consumer-composed camera/recoil experiment with independently controlled RNG
state, followed by comparison with a copied retail run when authorized.
