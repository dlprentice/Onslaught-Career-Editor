# CUnit__Damage

Status: active specimen-bound function contract; September 30 corrections supersede the August behavior summary
Last updated: 2026-09-30
Summary: shared unit damage, repair, mesh-part admission and warning-message ordering, re-derived from retail instructions; source reconstruction and isolated execution do not establish retail gameplay acceptance.
Evidence: MEASURED — fresh pristine instructions, constants and caller reads; 61 bounded original-code cases with explicit callee stubs and separate runtime limits.
Source File: no Unit.cpp body in the pinned partial source; the private reconstruction remains a candidate | Binary: pristine BEA.exe.original.backup, identified below.
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

> Address: `0x004f9a90`

## Identity and ABI

The [September 27 interface audit](../../../ghidra/README.md#re-audit-thing-gameplay-identities--september-27)
records primary slot 40 as `Damage(float, CThing*, BOOL applyShields, int meshPartIndex)`.
The historical filename remains for existing links. The later name correction did not validate the old behavior prose.

Fresh September 30 reads reproduce the 2,586-byte body `[0x004f9a90, 0x004fa4aa)`, ending with
`ret 0x10` at `0x004fa4a7`, and body SHA-256
`c00c805fc86ad1f52e6ab7d8fc739c456983914319ad99870d49c88b8733f859`.
The `thiscall` receiver arrives in ECX. At entry, stack arguments follow the return address in this order:

| Entry stack offset | Argument | After the complete prologue |
| --- | --- | --- |
| `+4` | float damage amount | `[esp+0xb0]` |
| `+8` | source `CThing*` | `[esp+0xb4]`; loaded into EBX before the final two register pushes |
| `+0xc` | integer/BOOL shield-admission flag | `[esp+0xb8]` |
| `+0x10` | mesh-part index; `-1` means unspecified | `[esp+0xbc]` |

Those prologue-relative offsets apply before subsequent argument pushes. The earlier table mixed stack states.

## Ordered contract

The numerical descriptions below cover finite values. Instructions remain the authority for unordered/exceptional
floating-point cases; this note does not declare NaNs, invalid pointers or arbitrary negative mesh indices safe.

1. **Notify the linked squad before damage admission** (`0x004f9abc`–`0x004f9add`). If receiver `+0x148`
   is non-null, source type mask `0x4` is set, source `+0xec` is non-null, and that owner's type mask `0x10`
   is set, call `0x004e6660` with ECX equal to the linked object and the owner as its stack argument.
   The 21-byte callee stores global float `[0x00672fd0] + 5.0f` into **that linked object's `+0x88`** and
   returns with `ret 4`. It does not write the damaged unit's `+0x88`. The old mask polarity and receiver attribution were wrong.
2. **Dying/explosion suppression** (`0x004f9ae2`–`0x004f9b01`). Return when receiver flag mask `0x4`,
   source type mask `0x01000000`, and profile `[receiver+0x164]->+0x124` are all set/nonzero.
   This is a specific damage guard, not a general reentrancy lock.
3. **Deployment-state scaling** (`0x004f9b07`–`0x004f9b2f`). State `[receiver+0x244]` equal to 3, 4 or 5
   multiplies the amount by profile `+0x160` and stores the float result back to its argument slot.
   This is the deployment state, not the unit AI-state field.
4. **Amount split** (`0x004f9b36`–`0x004f9b48`). An ordered positive amount enters the damage arm;
   other comparisons branch to `0x004f9f35`. For finite amounts, that is the nonpositive repair arm.
   The positive arm returns if vulnerability flag `[receiver+0x15c]` is zero; that field is not a profile pointer or a life test.
5. **Nexus restriction** (`0x004f9b5c`–`0x004f9d73`). With receiver `+0x228` nonzero:
   source type mask `0x01000000` causes an immediate return. Otherwise, when `meshPartIndex != -1`,
   a non-null selected part whose name compares **unequal** to `"nexus"` causes a return.
   Equality and a null selected part pass this particular name test. The comparison is case-insensitive;
   `test eax,eax` / `jne` at `0x004f9d71`–`0x004f9d73` establishes its polarity.
6. **Non-weakpoint multiplier** (`0x004f9d79`–`0x004f9dc1`). With receiver `+0x22c` nonzero and index
   not `-1`, a non-null selected part whose name compares **unequal** to `"weakpoint"` multiplies the
   amount by 5.0f. Exact name equality skips the multiplier (`je` at `0x004f9db2`). Preserve this counterintuitive
   retail behavior; the old note reversed it.
7. **Segmented receiver dispatch** (`0x004f9dc8`–`0x004f9de1`). Non-null controller `+0x178` receives
   `(meshPartIndex, amount, source)` through `0x00444030`, then this function returns. Shared shields, life,
   particles and warning messages below are skipped. See the existing
   [segment-controller contract](../DestructableSegmentsController.cpp/CDestructableSegmentsController__DamageSegmentByIndexAndUpdateThreshold.md).
8. **Hook, then shields** (`0x004f9de6`–`0x004f9e5a`). Call primary virtual slot 107 (`+0x1ac`) with
   the amount. Zero shield admission skips all shield arithmetic, leaving shields unchanged and passing
   the full amount to life subtraction. With nonzero admission: if shields `+0x100 >= amount`, subtract
   the amount from shields and return; otherwise, when `amount > shields`, reduce the amount by shields and clear shields.
   Full absorption is an early return; it does not reach the later warning/RNG path.
9. **Life and death** (`0x004f9e61`–`0x004f9ed3`). Subtract the remaining amount from life `+0xf8`.
   Death processing requires the **resulting life < 0**, and receiver flag mask `0x4` clear. Exactly zero
   does not enter it. An ammunition source (mask `0x4`) with an owner at `+0xec` of type mask `0x8`
   increments `[owner+0x574]->+0x30`. If profile `+0x11c` is zero, invoke primary slots 50 (`+0xc8`) and
   71 (`+0x11c`), the latter with `(remaining amount, source)`. Then clear receiver `+0x1f0`.
10. **Positive-arm particles** (`0x004f9edd`–`0x004f9f33`). If shields are **greater than 2.0f** and
    profile `+0` holds an effect descriptor, call `0x004cb3d0` at the source position. Then jump over repair.
    This shield comparison belongs to the particle path; it is not a repair condition.
11. **Repair arm** (`0x004f9f35`–`0x004f9f9a`). Repair only when `0 < life < profile maximum (+0xc0)`.
    If `-amount > maximum - life`, copy the maximum into life; otherwise subtract amount from life.
    The clamp comparison is strict. Repair does not test shields or the positive-arm vulnerability flag,
    does not revive zero/negative life, and is not reached by falling through positive damage/death.
12. **Deferred death hook** (`0x004f9fa0`–`0x004f9fc7`). Profile `+0x11c` nonzero and life below zero
    invoke primary slot 100 (`+0x190`). This shared tail follows damage or repair paths that did not return earlier.
13. **Warning-message path** (`0x004f9fcd` onward). Profile `+0x120` gates the entire path. If enabled,
    call the RNG at `0x004de8d0` through the pointer `[0x008a9d9c]` **once before checking any threshold or latch**,
    taking its signed remainder modulo 3. This draw still occurs when no warning is due or text display is disabled.
    Resolve the speaker from the case-sensitive profile name: Tara Fighter, Billy Fighter, or the default.

## Retained unreachable nexus branch

The executable contains a nexus-search, transform, radius and world-line test at
`0x004f9b90`–`0x004f9d47`. It is not ordinarily reachable through this entry's preceding guards:
entering it requires receiver `+0x228 != 0`, a specified mesh index and the source explosion mask set,
but the same mask already caused the return at `0x004f9b69`. There is no call or write between the two
tests that could change that result. This conclusion assumes stable ordinary object memory, not concurrent
external mutation. The byte-matching source retains the code; do not implement it as an independently reachable
explosion damage path based on the old prose.

## Warning thresholds and latches

The branches are an **exclusive else-if chain**, including each branch's latch test. A zero latch means
that warning has not been issued; stores of one suppress later repeats. This body never clears these latches.

| Priority | Condition, with the corresponding latch zero | Latches written to one | Anchors |
| --- | --- | --- | --- |
| First | life < 0 | `+0x23c`, `+0x238`, `+0x234` | `0x004fa099`–`0x004fa1c9` |
| Second | life < 0.25 × maximum | `+0x238`, `+0x234` | `0x004fa1ce`–`0x004fa2fc` |
| Third | life < 0.5 × maximum | `+0x234` | `0x004fa301`–`0x004fa423` |

Equality does not pass the corresponding threshold. A failed latch test can fall through to the next
condition; this is not three independent warning emissions. Each chosen branch resolves one message id
from its profile-specific three-way table through `0x004f2580` and updates the latches before the display gate.
If `[0x008a9d84]` is nonzero and the returned message pointer is non-null, the tail allocates/constructs a
message on successful allocation and submits it to `0x004b7ca0`. Null allocation skips construction but
still calls that submission boundary with null (`0x004fa45d`–`0x004fa48a`). This establishes call and state order, not audible playback or
successful presentation. The old 0.25/0.5/1.0 threshold description and “re-armed” interpretation were wrong.

The separate September 30 queue probe now bounds that null edge. With a prepopulated node pool, original
submission code plus the original pointer-set constructor, append, assignment and clear routines return an
empty queue for **empty queue + null**, with playback allowed either zero or one. With one real message already
queued, a null incoming message instead attempts a DWORD read at address `0x2c`, instruction `0x004b7cee`.
Ten cases agree with the current reconstruction, including valid-message controls that preserve ascending
priority and stable ordering for equal priorities. Unknown calls and an unrelated bad-receiver fault are
rejected rather than accepted as the expected null observation. No allocator, logger, playback or exception
handler runs; this is not an observed Windows crash or proof of an actual allocation-failure path.

The lead reran the frozen private script
`bea-decomp/.worktrees/codex-career-nearmiss-20260930/build/messagebox-queue-review-20260930/probe.py`
with `bea-decomp/local-data/venv/bin/python -B` and
`--out local-data/messagebox-queue-root-20260930` from `bea-decomp` main. Script SHA-256:
`f40a99c04dcc7af1b80efdee4de1ed40cb071c7b75a6b6f2e11b1ac9e601b866`.
The output records pinned specimen/source/object identities, exact call boundaries, queue/canary state and
the two refusal controls. The submission function still has an unresolved byte mismatch.

## Caller corrections

Fresh whole-body reads correct two earlier forwarding interpretations:

- `CBuilding::Damage` (`0x004179a0`, call at `0x00417a16`) first updates a timer and can change its
  animation state. It then forwards all four arguments when the segments pointer `+0x178` is non-null
  **or** dying flag mask `0x4` is clear. It skips the base call only when there are no segments and that
  flag is set (`0x004179f0`–`0x004179fe`). It is not a pure forwarder; the old admission polarity was wrong.
- `CHiveBoss::Damage` (`0x00480050`, call at `0x0048006d`) skips sources with explosion mask
  `0x01000000`; otherwise it forwards all four original arguments unchanged. Loads at `0x00480062`
  and `0x00480068` use the stack after preceding pushes. The old claim that it reused the source pointer
  as the mesh-part argument resulted from mixing stack states.

These are bounded caller checks, not a fresh whole-executable caller census.

## Field roles established here

| Receiver offset | Role in this body |
| --- | --- |
| `+0x2c`, mask `0x4` | dying-style flag used by the admission and death guards |
| `+0xf8`, `+0x100` | life and shields |
| `+0x148` | linked squad/monitor receiver used by the initial notification |
| `+0x15c` | vulnerability flag checked only in the positive arm |
| `+0x164` | profile pointer; `+0xc0` within the profile is maximum life |
| `+0x178` | segments-controller pointer |
| `+0x228`, `+0x22c` | nexus restriction and non-weakpoint multiplier admission |
| `+0x234`, `+0x238`, `+0x23c` | half-life, quarter-life and below-zero warning latches |
| `+0x244` | deployment state used by the scaling arm |

The receiver's `+0x88` is not established as a cooldown by this function. The initial timer write uses the
linked receiver instead. Source field spellings and saved Ghidra names remain separate identity claims.

## Evidence and limits

September 30: independent read-only review followed by lead re-derivation from the verified specimen,
whole-body disassembly, fresh body hash, string/constant reads and timer-callee inspection. Private lead
receipts are under `bea-decomp/.worktrees/codex-equiv-20260930/build/`:
`unit-damage-static-readback-20260930.txt`, `unit-damage-constants-20260930.json` and
`unit-damage-caller-readback-root-20260930.txt`.

The lead separately inspected and reran the helper's **50 original-code cases**, then authored and ran
**11 additional controls** for partial-latch fall-through, shield bypass, repair at/above maximum life and
repair with low/high shields. All 61 completed with the expected finite-case outputs and `ret 16`,
callee-saved registers and SEH chain preserved. With event time fixed to 10, the real squad helper wrote
15 to the linked object's `+0x88` while the damaged unit's sentinel there remained 9. No ordinary-entry
case reached the guarded nexus explosion-geometry block. Negative controls distinguish equal/unequal mesh
names, exact-zero death, exact/either-side warning thresholds, exact versus oversized repair, source masks
2/4, nonzero high-byte flags, disabled text display and already-set warning latches.

Reproduction commands, from private `bea-decomp` main:

```text
local-data/venv/bin/python .worktrees/codex-collision-nearmiss-20260930/build/unit-damage-branch-probe/probe.py --out local-data/unit-damage-branch-probe-root-20260930.json
local-data/venv/bin/python local-data/unit-damage-extra-controls-root-20260930.py
```

The frozen 50-case script's SHA-256 is `0bea2afe08e7cd49056d99b41aeb6ad2433381acc1848316f94abd74d1059514`;
both JSON outputs record their script and specimen hashes. Only Damage and the squad helper execute original
code. Virtual hooks, RNG results, mesh lookup, name comparison, effects, allocation, text and message callees
are explicit stubs; the selected objects and names are synthetic. `FNINIT` supplies the isolated FPU state,
not a measured live-game control word. No geometry, exceptions, concurrent mutation, failed allocation,
real audio/rendering or message lifetime is exercised. These are bounded branch observations, not a retail
session, full equivalence proof or acceptance result.

The August 22 caller census reported four direct callers and 19 vtable/data references; that census was
not rerun for this correction. Its original tools/receipts remain under `local-lab/unitdmg/`. The
[historical packet contract](../../../contracts/unitai/CUnit__ApplyDamage__004f9a90.md) preserves the
older evidence inventory and retained TTD coverage reports. Coverage does not prove the branch claims;
deleted recordings cannot be replayed. Neither the old “byte-exact” heading nor a correct body hash validates
an analyst's interpretation of a conditional branch.

The private C++ candidate preserves the inspected guards and thresholds but is still not a whole-function
byte match. No rebuild or companion code, Ghidra database, original save or retail installation changed for
this correction. Caller object lifetime, indirect-callee effects, exceptional floating-point states,
allocation failure and real-game presentation still require their own evidence.

## Reconstruction implications and falsifiers

- Preserve the exact mesh-name polarities, strict zero/death/repair boundaries, early returns, RNG draw
  position and latch order. Do not tune these to make a Level 100 driver finish.
- Segmented units still take the terminal controller-dispatch route; this does not by itself validate
  any aggregate Warehouse implementation or Level 100 acceptance claim.
- Useful distinguishing inputs: nexus/non-nexus names; weakpoint/non-weakpoint names; life exactly zero;
  repair with shields below and above two; life exactly at and on either side of 25%/50%; all warning latches
  already set; and warning display disabled while the profile's warning path remains enabled.
- The isolated probes capture life, shields, receiver identity, callback order, RNG calls and all three
  latches. A stronger falsifier would replace a consequential stub with its actual callee while preserving
  admitted object lifetimes; a controlled retail playthrough remains a separate acceptance step.
