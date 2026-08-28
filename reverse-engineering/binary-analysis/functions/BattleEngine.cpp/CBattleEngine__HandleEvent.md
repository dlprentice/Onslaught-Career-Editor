# CBattleEngine__HandleEvent

Status: active static function note; morph-completion arms closed cross-platform
Last updated: 2026-08-28
Source File: `references/Onslaught/BattleEngine.cpp` | Binary: BEA.exe,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — pristine PC instructions and transfer census,
independently reconstructed PS2 demo/EU/USA and Xbox USA/EU/Issue 11
homologs, and exact retained-source correspondence. No Ghidra project was
opened or mutated.

> Address: `0x0040c180`

## Exact PC identity and dispatch

The incoming-`ECX` `thiscall` body is `[0x0040c180,0x0040c2de)`,
350 bytes / 93 instructions, raw SHA-256
`0af705098a485b1f8b1a98ab0cde4b77c664c4b55547e03beb6496cc66b90ade`.
It takes one `CEvent*` stack argument and returns with `ret 4`. The dispatch
prefix `[0x0040c189,0x0040c1b7)`, SHA-256
`c90b9c629319520291769167a987046479813287aa29c8c25e2e60109514d9c2`,
sign-extends the event number from `event+0x04` and compares numeric events
6000, 6001, 4002, 6002, and 6003.

No direct `.text` call or jump targets this entry. A unique image dword at
`0x005d89c4` points to it as the primary `CBattleEngine` vtable event slot;
event-manager delivery is therefore virtual.

The complete handler also routes event 6002 to
`CBattleEngine::CalcUnitOverCrossHair`, event 6003 to
`CBattleEngine::HandleAutoAim`, event 4002 through a sound-effect path, and
unhandled values to `CUnit::HandleEvent`. Those arms are not expanded here.

## Event 6000 / `BECOME_JET`

The PC arm is `[0x0040c1b7,0x0040c1ea)`, 51 bytes, SHA-256
`2cf7550787eab339183c2d5dd33cbb63cc2adbcc19c079b720aef5f7c8514624`.
Its accepted suffix `[0x0040c1c4,0x0040c1ea)` has SHA-256
`1d2bfbe51c1dd22594876f8060514d4e97678aa2b7dfd0f90a43826158da756a`.

It performs exactly this transaction:

1. Require `[this+0x260] == 1` (`MORPHING_INTO_JET`). A mismatch returns
   without a time write, state write, allocation, or collision submission.
2. Copy current event-manager time from `0x00672fd0` to `[this+0x520]`
   (`mTransformStartTime`).
3. Write `[this+0x260] = 3` (`JET`).
4. Call `CBattleEngine::SetCollisionShape` at `0x004063b0`.

The prior name `CBattleEngine__UpdateWeaponEffect` for the callee is false.
Exact body, allocation metadata, `CCylinder` RTTI/vtable, geometry, receiver,
and retained source independently identify `SetCollisionShape`.

## Event 6001 / `BECOME_WALKER`

The PC arm is `[0x0040c273,0x0040c28e)`, 27 bytes, SHA-256
`c54825eaf8176eb6962693f4dc8ea378643f2d5b97cf6adad31fbd709c602477`.
It has no predecessor-state guard and no transform-time access:

1. Write `[this+0x260] = 2` (`WALKER`).
2. Call `CBattleEngine::SetCollisionShape` at `0x004063b0`.

A duplicate or stale 6001 therefore still forces the settled walker state and
replaces the collision shape. This asymmetry with event 6000 is released
behavior, not a missing inferred guard.

## Completion-side boundary

Neither completion arm changes part readers, cockpit state, animation, sound,
energy, takeoff height/time, grounded timers, or controls. Those effects belong
to morph initiation or later movement. Completion only settles state, performs
the event-6000 timestamp write when admitted, and rebuilds/submits the collision
cylinder.

The collision helper constructs a single-player cylinder with radius `0.4f`
and axial half-height `0.95f` (full height `1.9f`); multiplayer changes only
the radius to `1.0f`. The getters do not consult walker/jet state, so the
released dimensions are mode-invariant. The default
`CCSPersistentThing::SetShape` target at `0x00426370` deletes the old shape,
installs the new one, and refreshes its owner-relative center. An allocation
failure still submits null; the default receiver consequently discards the old
shape and then dereferences null rather than recovering locally.

## Cross-platform reproduction

All independently recovered release families preserve the same two observable
completion transactions.

| Family/builds | Handler body | 6000 | 6001 | True difference |
| --- | --- | --- | --- | --- |
| PC retail | `[0x0040c180,0x0040c2de)`, 350 B, `0af70509…0ade` | exact-state-1 gate; time `+0x520`; state 3; shape | unguarded; state 2; shape | PC writes time then state |
| PS2 demo/EU/USA | `[0x0010deb8,0x0010dfb8)`, 256 B; build hashes `375ab11c…ab5c`, `fb60cc28…693c`, `c8aaf5e3…afbc` | exact-state-1 gate; state 3; time `+0x548`; shape | unguarded; state 2 in call delay slot; shape | PS2 writes state before time; final state and helper-entry state match |
| Xbox USA/EU/Issue 11 | 220 B at `0x0016f1f0`, `0x0016f000`, `0x0016f260`; hashes `c6c681cb…00a3`, `55933a1d…b71`, `078d45e4…8eed` | exact-state-1 gate; time `+0x51c`; state 3; shape | unguarded; state 2; shape | relocation/layout and compiled-source-line differences only |

The PS2 6001 arm is byte-identical across its three canonical builds
(`[0x0010df44,0x0010df5c)`, SHA-256
`d81d8b4ded8a6514d441383df6cf98f89c5b064094c032e99332a9b18a9483ad`).
The Xbox 6001 arm is likewise byte-identical across USA/EU/Issue 11 (21 bytes,
SHA-256
`eb63e81ff6f827e125c3e0bcd775e5d40c95bb8c6695f18cdb55e28a370a4a82`).
PS2 uses object fields `+0x280` for state and `+0x548` for transform time;
Xbox retains PC state `+0x260` but uses transform time `+0x51c`.

The PS2 state-before-time order is the one genuine scoped sequencing delta.
Because no intervening call observes the object, it does not change the final
transaction. On every platform the new settled state is visible before
`SetCollisionShape` queries virtual geometry and submits the cylinder.

## Source bridge

Retained `BattleEngine.cpp:2665-2710` reproduces the complete handler
architecture; lines 2669-2684 reproduce these two arms. `BattleEngine.h`
assigns 6000/6001 to `BECOME_JET`/`BECOME_WALKER` and ordinals 1/2/3 to
`MORPHING_INTO_JET`/`WALKER`/`JET`. Retained `event.h` stores a signed short
event number after its four-byte reader, matching the released sign-extending
load at `event+0x04`.

## Rebuild mapping

Grade: `REBUILD_READY` for normal morph-completion policy and order;
`PARTIAL_CONTRACT` for the handler as a whole.

`Simulation.AdvanceTransition` is the correct deterministic Core owner. It
settles `VehicleMode` when the exact scheduled tick expires, emits
`AquilaFlightEvents.TransformCompleted` only afterward, and then clears the
transition. Existing transition timing tests exercise both directions. Core's
mode write therefore already occupies the released state-write boundary.

No numeric retail-event dispatcher, stale-event injection API, heap-shaped
collision compatibility object, or duplicate completion test is justified.
Core already owns the released single-player 400 mm contact radius and 1,900 mm
center-of-gravity height. The remaining parity question is which concrete Core
collision consumers require the proven 950 mm axial half-height; that is being
traced separately before changing simulation behavior.

## Falsifiers

Any of the following rejects this closure: the exact PC body or arm hashes
differ; event 6000 mutates any completion field when state is not exactly 1;
event 6000 does not perform time/state/shape in PC/Xbox order; event 6001 has a
state guard or transform-time access; either arm performs a part-reader,
animation, audio, energy, or takeoff mutation; or any named console homolog
shows a non-relocation behavioral difference beyond the documented PS2
state/time order.

## Functions

| Address | Name | Contract (confidence) |
| --- | --- | --- |
| `0x0040c180` | `CBattleEngine__HandleEvent` | incoming-ECX thiscall; signed-short event dispatch; 350 B; virtual ingress. HIGH on events 6000/6001, state/time predicates and writes, exact collision-helper identity, negative side-effect inventory, and PC/PS2/Xbox equivalence. Whole handler remains partial outside the named arms. |
