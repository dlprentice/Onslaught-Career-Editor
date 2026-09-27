# CBattleEngine__Damage

Status: active, bounded instruction and original-code contract
Last updated: 2026-09-26
Summary: damage, repair and invulnerability ordering re-derived; the old nonpositive early-out and three plate offsets are corrected.
Evidence: MEASURED — complete pristine body, virtual caller, 41 isolated original-code cases and retained Level 521 observation extracts; no fresh full-game or TTD execution.
Source File: `references/Onslaught/BattleEngine.cpp:2127–2240`, pinned commit `5352a81cdb838b145a57f7febc5d9fc4b0129ebb` | Binary: pristine `BEA.exe.original.backup`, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x0040a890`

## Identity and interface

The complete body is `[0x0040a890,0x0040ac25)`, 917 bytes, 233 instructions,
SHA-256 `224c0577b539bbf0d6fa118a6355502f9aead3bc588e59ae3bf08bdf3cd1ff91`.
ECX is the receiver; `RET 0x10` removes four explicit dwords:

```cpp
void __thiscall CBattleEngine__Damage(
    void *this, float amount, void *inByThis, int inDamageShields, int meshPartNo);
```

The fourth argument is unused by this body. RTTI identifies main vtable
`0x005d89c4` as CBattleEngine; slot 40 at `0x005d8a64` points here. The
`DeclareOnGround` counterpart `[0x0040c750,0x0040c984)` calls that slot at
`0x0040c90d` with computed damage, null source, false shield flag and −1.
Its pristine SHA-256 is `312066f6ffdcaf54ee835b4bfd7d962f8ce0a9d4386b653f1fb1b33deef84711`.
This indirect caller resolves the old note's misleading emphasis on zero direct callers.

The body and caller match the pinned Damage definition. Its embedded allocation
coordinate `BattleEngine.cpp:3595` belongs to inlined damage-flash work in this
retail version. That line falls within HandleEngines in the pinned source;
the numeric overlap does not identify the retail function as HandleEngines.
No rename or Damage prototype change is warranted.

## Fields and the historical transcription error

| Meaning supported by the body and source counterpart | Receiver offset | Representative instruction |
| --- | --- | --- |
| Life | `+0xf8` | `0x0040a9c6` |
| Energy | `+0xfc` | `0x0040aaba` |
| Shields | `+0x100` | `0x0040a944` |
| Vulnerability flag | `+0x15c` | `0x0040a9d9`, `0x0040abf0` |
| Battle Engine state | `+0x260` | `0x0040aaab` |
| Last damage time | `+0x2d4` | `0x0040a9f1` |
| Augmentation amount / active flag | `+0x2f8` / `+0x2fc` | `0x0040a969`, `0x0040a93c` |
| Configuration / player / walker pointers | `+0x4b0` / `+0x574` / `+0x578` | `0x0040a915`, `0x0040a8d3`, `0x0040a956` |
| Accumulated vibration | `+0x604` | `0x0040abf8` |

The historical plate incorrectly wrote augmentation `+0x168`, life `+0x154`
and damage time `+0x174`. Those are **comment transcription errors**, not the
field map in the original evidence. Both retained Damage JSONL extracts and
frozen `observation.json` already record `+0x2f8`, `+0xf8` and `+0x2d4`.
For every recorded write, ESI and EDI are `0x079b9750`; subtracting that receiver
from the recorded destination reproduces the correct offsets. No subobject
rebasing is needed. The preserved author `tools/re_level521_damage_writes.py`
and current campaign consumer also use the correct offsets.

The historical Java applier and frozen receipts remain unchanged. This recheck
reads retained observations; the retired TTD recordings cannot be replayed.
One replicated invocation, five nontrivial gaps and nine continuity breaks do
not establish a complete write set or every branch.

## Retail order

1. Save life, shields and energy. The x87 status test `AH & 0x41` at
   `0x0040a8c0` sends zero, negative and masked-unordered amounts to
   `0x0040aa8e`. **It skips the positive-damage section, not the common tail.**
2. Positive amounts add the low 32 bits of `FISTP(amount × 256)` to player
   `+0x48`. This conversion uses the active x87 rounding mode. If life compares
   nonnegative, apply shield-efficiency and life arithmetic. With sufficient
   shields, inactive augmentation receives shield damage only when the walker
   has an augmentation weapon. The shield-exhaustion arm has no such weapon
   check. A resulting negative life calls vtable `+0xc8` only when vulnerability
   equals exactly 1. This call precedes the timestamp and common tail.
3. Positive input writes time from `0x00672fd0` to `+0x2d4`. A nonnull source
   enters damage-flash handling; that arm was inspected statically but is outside
   the isolated execution below.
4. The common tail caps augmentation above 10. State 2 copies shields to energy
   **before repair**. Negative amounts repair life toward configuration `+0x1c`,
   then spend the remainder on energy toward configuration `+0x20`.
5. Compute `(savedLife − currentLife) × 0.125`, halve it for ordered nonzero shields,
   and cap it above `0.25`. Call [AddShockShake](../../../contracts/battleengine/CBattleEngine__RandomizeOffsets4B8_4C0__00407940.md).
   Then cap the same difference above `0.05` and add `difference × 50` to
   vibration. Neither cap is a lower bound: repairing life can reduce vibration.
6. Only afterward, vulnerability equal to 0 restores saved life, shields and
   energy. Statistics, timestamp, augmentation, vibration and shake/RNG effects
   are not restored. A flag of 2 neither invokes the exactly-1 death callback
   nor performs the exactly-0 restoration.

The branch tests are x87 status tests, not CPU CF/ZF from a float comparison.
With masked exceptions, a quiet NaN skips positive damage but enters repair.
For authored life 10, energy 5, shields 4 and caps 20/12, life becomes 20 and
energy NaN; vibration changes from 1 to −30.25. Different state or exception
settings are not implied by that one case.

Two further masked cases use NaN shields: the equality/unordered status bit
skips halving, unlike a high-level `shields != 0` condition. Amount −3 produces
vibration −17.75; amount 0.25 produces vibration 2.5625, with the same initial
state and NaN shields. The shields remain NaN.

## Executed checks and useful counterexamples

Private driver: `local-data/test-runs/re-audit-20260926/battleengine-damage/original_damage.py`.
Accepted receipt: `run-iekrvvq7/damage.json`, SHA-256
`f6a2aab65ef85d1558332a3a3605845cd786a7c1c8949149dac52e9b2a6c130d`.
Six complete unchanged original bodies run at original addresses: Damage,
Battle Engine shake, cockpit shake, game RNG, CRT rand and the three-byte
platform return. Forty-one cases cover zero/negative/positive/NaN amounts,
shield branches, invulnerability, a recorded lethal callback, x87 rounding,
shake thresholds and separate game/CRT RNG states.

Examples start at life 10, energy 5, shields 4, augmentation 2 and vibration 1
unless stated otherwise; configuration caps are 20/12 and shield efficiency 50:

| Input | Observed result | Disproved simplification |
| --- | --- | --- |
| Amount 0, state 2, augmentation 12 | Energy 4, augmentation 10 | Nonpositive input returns immediately |
| Amount −3 | Life 13, vibration −8.375; RNG unchanged | Repair cannot affect vibration |
| Amount −12, state 2 | Life 20, energy 6 | Repair precedes walker energy synchronization |
| Amount 6, invulnerable | Life/shields/energy restored; augmentation 6, vibration 3.5; game seed advances | Invulnerability suppresses all damage side effects |
| Amount `3/512`, no shields | Statistic increment 2 with nearest/up, 1 with down/truncate | The conversion always truncates |

The lethal callback records life −16, shields 0, energy 5, old time 3,
augmentation 13, vibration 1 and the original seed; after it returns, the tail
sets energy 0, time 42 and augmentation 10 and advances shake/RNG. This proves
ordering at that intercepted boundary, not the real death implementation.

The first experiment draft incorrectly expected the NaN case to make life and
vibration NaN. The retained failure was reconciled against the two different
x87 branch masks before correction. Subsequent review added an explicit x87
tag-word guard and distinguished inferred game draw count from counted CRT
provider entries. Earlier runs remain evidence of those limitations.

## Bounds and remaining questions

Objects and settings are authored. The source pointer is null. The death
callback only records entry state; the CRT thread-data provider returns an
authored block. Six retail bodies are byte-identical in the ELF. Stack cleanup,
nonvolatile registers, adjacent guards, original control word, TOP and empty
x87 tags are checked. The write allowlist covers the authored `0x840`-byte
object block, not all copied globals or CRT memory. The executable permits only
read/write/exit syscalls; a denied `getpid` is a negative control.

No full-game death, flash allocation/list lifetime, Windows device behavior,
rendered shake, audible effect or player acceptance is established. Further
falsifiers are a nonnull-attacker experiment with allocation/list boundaries,
actual StartDieProcess composition, and controlled copied-game observations.
Arithmetic outside the measured cases, including unmasked exceptions and
adversarial state, remains open. This does not promote the frozen campaign's
bounded grade or establish complete rebuild parity.
