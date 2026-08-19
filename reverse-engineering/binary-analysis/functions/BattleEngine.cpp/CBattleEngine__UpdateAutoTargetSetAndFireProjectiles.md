# CBattleEngine__HandleLocks

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 live correction closeout:** `0x00406560` → `CBattleEngine__HandleLocks` (was `CBattleEngine__UpdateAutoTargetSetAndFireProjectiles`). Current live Ghidra reflects confirmed rows only; older conflicting text below is superseded only where confirmed. Use the [closeout](../../ghidra-full-reaudit-closeout-2026-07-13.md); final per-address decisions and exact before/after metadata are in `reverse-engineering/binary-analysis/ghidra-reviewed-correction-plan-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

> Address: `0x00406560` | Source family: `references/Onslaught/BattleEngine.cpp`
> The legacy filename is retained so historical links do not break.

## Status

- Current live-Ghidra name: `CBattleEngine__HandleLocks` (applied and exactly
  read back on 2026-07-13)
- Revalidated static identity: `CBattleEngine__HandleLocks`
- Evidence: fresh final-snapshot metadata, xrefs, instructions, decompile, and
  direct source-shape comparison
- Runtime behavior proof: not established

## Summary

Source-aligned BattleEngine lock-maintenance and acquisition helper. It is
called from `CBattleEngine__Move` with the BattleEngine pointer in `ECX` and no
explicit stack arguments. The body selects the active JetPart or WalkerPart
weapon, prunes null, dying, or out-of-deflection entries from the lock set at
`+0x294`, enforces weapon readiness and maximum-lock gates, and handles direct,
proximity, and sequence lock modes.

## Interpretation

The old projectile interpretation came from inherited dependent helper labels.
Raw call shapes inside this body pass target, lock time, and a direct-lock flag
to the helper currently named `CBattleEngine__AddProjectile`; those arguments
and the surrounding source order identify that callee as lock-entry creation in
this context. The direct caller position and full body align with
`CBattleEngine::HandleLocks` in Stuart's source.

The bounded public contract is
[`battleengine-target-acquisition-static-contract-v1`](../../../game-mechanics/battleengine-target-acquisition-static-contract-v1.md).
It keeps the candidate helper at `0x00406da0` and the lock-entry creation helper
at `0x00406fc0` address-bound, with their stronger source names explicitly
hypothesis-only.

## Boundaries

- Static identity and ABI evidence only.
- The confirmed live Ghidra name/comment correction was applied under the
  bounded 2026-07-13 mutation lease.
- Dependent helper names and concrete layouts remain subject to bounded review.
- No runtime target acquisition, firing, gameplay, patch behavior, or rebuild
  parity is claimed.

## 2026-08-19 byte contract

Independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). The Ghidra database was not opened. This
wake landed `1093bee8` StartLock and `c87456f5` LockHit — not
redone. Cycle 90 accepted the trio map. Name-correction history
above is not rewritten. This is an envelope, not a 647-instruction
walk.

Incoming-ECX `thiscall`. First insn `sub esp, 0x4c`. One bare `ret`
at `0x00406d12`. Body `0x00406560`–`0x00406d12` is 1971 bytes,
SHA-256
`7ed9ecb5536b6841a856608668551ed3fcb0c6b945a976b7453fef8cb700b04e`.
Capstone: 647 insns, 53 `E8`, zero `E9`, 24 unique rel32 targets.
Raw `0xE8` byte count is 59 and is not the instruction count.
Neighbour table `CSPtrSet__First` starts at `0x00406d20` and is
not rewritten. Preceding table
`CBattleEngine__SwapPrimarySecondaryPartReadersForState` ends at
`0x00406556` and is not rewritten.

Pinned prologue:

1. `ebx = ecx`. `[ebx+0x260]` compared to 3 (same JET arm
   DisplayLock uses).
2. Jet: `ecx=[ebx+0x57c]` / `E8` `0x00414b30`. Walker:
   `ecx=[ebx+0x578]` / same `0x00414b30`. Table name
   `TargetSet__AnyUnitTargetTimeoutBeforeProfileLimit`. Nonzero
   EAX jumps to the epilogue. That table name, and source
   `IsFiring()`, are **not** this proof.
3. Jet: `E8` `CBattleEngineJetPart__GetCurrentWeapon`
   `0x00412610` then `CBattleEngineJetPart__CanWeaponFire`
   `0x00412570`. Walker: `CBattleEngineWalkerPart__GetCurrentWeapon`
   `0x00414030` then `CBattleEngineWalkerPart__CanWeaponFire`
   `0x00414630`. Zero from CanWeaponFire stores 1 at `[esp+0x14]`.
   Null weapon jumps to the epilogue.
4. Walk set `this+0x294` (`lea esi, [ebx+0x294]`). Same occupancy
   StartLock appends to.

Four `E8` to `CBattleEngine__StartLock` `0x00406fc0` at
`0x004068d9`, `0x00406a51`, `0x00406aae`, `0x00406d06` — already
pinned on `1093bee8`. Other of the 24 targets (set First/Next,
Remove+dtor+Free, `CWeapon__GetDistanceProfileField*`,
`SelectNearestForwardTargetFromGlobalSet`,
`CalcUnitOverCrossHair`) are counted, not contracted here.

One inbound `.text` `E8`/`E9`: `CALL` at `0x00408b84` inside
table `CBattleEngine__Move` `0x004081c0`–`0x00409751`, after
`mov ecx, ebp`. Zero encodings of imm `60 65 40 00` in the image.

Source architecture (not proof): `CBattleEngine::HandleLocks`
`BattleEngine.cpp:586-752`. Retail uses the same `+0x260==3`
part split DisplayLock uses, then the `+0x294` prune / acquire
body.

Rebuild mapping: `PARTIAL_CONTRACT` (named, not implemented). See
the section below. Do not implement Core from this RE root.

Cheapest falsifier: file `0x00006560` is not `83 ec 4c`, **or**
`0x00006568` is not `8b 83 60 02 00 00`, **or** `0x0000656e` is
not `be 03 00 00 00`, **or** `0x0000657e` is not
`e8 ad e5 00 00`, **or** `0x00006d12` is not `c3`, **or** body
SHA-256 is not `7ed9ecb5…b04e`, **or** `tools/call_xref_scan.py`
on `0x00406560` is not exactly one `CALL` at `0x00408b84`, **or**
a second `.text` `E8`/`E9` to this entry exists, **or**
`call_xref_scan` on `0x00406fc0` is not the same four HandleLocks
sites.

## Rebuild mapping — 2026-08-19

Grade: `PARTIAL_CONTRACT`. Not `REBUILD_READY`. Independently
re-read official+twin `74154bfa` this wake (2506752 equal). Body
SHA-256 still `7ed9ecb5…b04e`. `call_xref_scan` still one `CALL`
at `0x00408b84`. Did not open Ghidra. Did not edit `rebuild/**`.
Did not walk all 53 callees.

Retail entity: player `CBattleEngine` lock-set prune-and-acquire,
called from `Move`. Stuart architecture (not proof):
`BattleEngine.cpp:586-752`.

Nearest reconstruction owner: **none**. Core has no lock-set and
no HandleLocks tick. `Simulation.TryFire` is the FireLock spawn
owner, not this maintenance loop.

Focused test: none. L100 card `t_aa5586e5` is on a playable
training-path diet — do not implement lock sets from this mapping
until that lane names the arm.

Siblings: `CBattleEngine__StartLock` /
`CBattleEngine__FireLock` /
`CBattleEngine__LockHit` /
`CBattleEngine__DisplayLock` /
`CBattleEngine__GetCurrentTarget` in this folder. Next named:
`CBattleEngine__SelectNearestForwardTargetFromGlobalSet`
`0x00406da0` (existing note; no 2026-08-19 PE contract).

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00406560` | `CBattleEngine__HandleLocks` | `83ec4c 53 8bd9 … 8b8360020000 be03000000 … e8ade50000 … c3` (1971 B) | incoming-ECX thiscall; 0 stack args; bare ret ×1; 1971 B; 53 E8 / 0 E9 / 24 targets; 1 inbound Move `0x00408b84`. HIGH on ABI, `+0x260==3` arm, `+0x294` walk start, four StartLock sites, unique inbound. Mapping `PARTIAL_CONTRACT`; no Core owner. **Not** on `IsFiring`, lock-mode names, or rebuild parity. |
