# CBattleEngine__SelectNearestForwardTargetFromGlobalSet

> Address: `0x00406da0` | Source family: `references/Onslaught/BattleEngine.cpp`

## Status

- Named in Ghidra: yes
- Static authority: [Ghidra reference](../../GHIDRA-REFERENCE.md)
- Source alignment candidate: `CBattleEngine::GetClosestLockableUnit`
- Source candidate status: `hypothesis-only`; no reviewed retail rename was applied
- Runtime behavior proof: not yet

## Current Saved Signature

```c
void * __thiscall CBattleEngine__SelectNearestForwardTargetFromGlobalSet(
    void * this,
    void * profile,
    float originX,
    float originY,
    float originZ,
    float originW,
    float rangeScale);
```

## Summary

Target-selection helper that walks a global candidate set and applies
side/profile, distance, forward-deflection, and existing-lock checks before
returning the nearest retained candidate or null.

The current decompile read-back supports the name with these token-level signals:

- `CUnit__IsCandidateSideCompatibleForTargeting`
- `CWeapon__DoesTargetMaskMatchDistanceProfile`
- `CWeapon__GetDistanceProfileField98`
- `CSPtrSet__First`
- `CSPtrSet__Next`

## Interpretation

This helper is a retail-binary anchor for target filtering and list traversal.
Its body and the three calls from `CBattleEngine__HandleLocks` align closely
with pinned-source `CBattleEngine::GetClosestLockableUnit`, but that exact source
identity remains a hypothesis rather than an accepted retail rename. Runtime
target-choice behavior remains unproven until a separately authorized copied-
runtime observation establishes it.

Wave 309 keeps `originW` because the checked callers pass a 16-byte vector plus `rangeScale`, and instruction read-back shows a `ret 0x18` stack cleanup. The exact vector/profile structures are still untyped.

## Boundaries

- Does not launch the game.
- Does not mutate `BEA.exe`.
- Does not apply a Ghidra rename map.
- Does not prove semantic target choice in gameplay.
- Does not promote source stealth/range semantics into a retail behavior claim.
- Does not accept `CBattleEngine::GetClosestLockableUnit` as the saved retail name.

## 2026-08-19 byte contract

Independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). The Ghidra database was not opened. This
wake landed `9ced05c0` HandleLocks — not redone. Name-correction
history above is not rewritten. Did not promote
`GetClosestLockableUnit`.

Incoming-ECX `thiscall`. First insn `sub esp, 0x4c`. Two `ret 0x18`
(`0x00406fae`, `0x00406fb8`). Body `0x00406da0`–`0x00406fba` is
539 bytes, SHA-256
`8dd454c91e9b940fa98cfcb1e54155952d3e5a1b566b6a7068fd07366e74474e`.
Capstone: 180 insns, 5 `E8`, zero `E9`. Neighbour table
`CBattleEngine__StartLock` starts at `0x00406fc0` after five
`nop`s and is not rewritten. Preceding table `Vec3__NormalizeInPlace`
ends at `0x00406d9a` and is not rewritten.

The body, with `ebp = ecx`:

1. Load dword `[0x008550d0]` into EAX, store it to `[0x008550d8]`,
   take `[eax]` as the first live node or 0. Both addresses are
   BSS (not in the 2,506,752-byte image). Empty walk returns 0
   via the second epilogue (`eax` was zeroed).
2. For each live node `ebx`: `push [ebx+0x138]` / `ecx=ebp` / `E8`
   `CUnit__IsCandidateSideCompatibleForTargeting` `0x004fd3d0`.
   Zero skips the node.
3. `ecx = [esp+0x60]` (first stack arg / profile) / `push ebx` /
   `E8` `CWeapon__DoesTargetMaskMatchDistanceProfile` `0x005061f0`.
   Zero skips.
4. Subtract the origin stack slots from `[ebx+0x1c]` / `+0x20` /
   `+0x24` (distance vector). Later `E8`
   `CWeapon__GetDistanceProfileField98` `0x00506620`.
5. Walk continues through `CSPtrSet__First` `0x00406d20` and
   `CSPtrSet__Next` `0x00406d30` (one each). Callee bodies and
   field names are **not** this proof.

Three inbound `.text` `E8`/`E9`, all inside table
`CBattleEngine__HandleLocks`: `0x004068bf`, `0x00406a8b`,
`0x00406b0c`. Zero encodings of imm `a0 6d 40 00` in the image.

Source architecture (not proof): `CBattleEngine::GetClosestLockableUnit`
`BattleEngine.cpp:755-798`. That exact source identity stays
hypothesis-only.

Rebuild mapping: `PARTIAL_CONTRACT` (named, not implemented). See
the section below. Do not implement Core from this RE root.

Cheapest falsifier: file `0x00006da0` is not `83 ec 4c`, **or**
`0x00006da3` is not `a1 d0 50 85 00`, **or** `0x00006ddc` is not
`e8 ef 65 0f 00`, **or** `0x00006dee` is not `e8 fd f3 0f 00`,
**or** `0x00006fb8` is not `c2 18 00`, **or** body SHA-256 is not
`8dd454c9…474e`, **or** `tools/call_xref_scan.py` on
`0x00406da0` is not exactly those three `CALL`s, **or** a fourth
`.text` `E8`/`E9` to this entry exists.

## Rebuild mapping — 2026-08-19

Grade: `PARTIAL_CONTRACT`. Not `REBUILD_READY`. Independently
re-read official+twin `74154bfa` this wake (2506752 equal). Body
SHA-256 still `8dd454c9…474e`. `call_xref_scan` still three
`CALL`s inside HandleLocks. Did not open Ghidra. Did not edit
`rebuild/**`. Did not promote `GetClosestLockableUnit`.

Retail entity: HandleLocks' nearest-candidate helper. Stuart
architecture (not proof): `BattleEngine.cpp:755-798`.

Nearest reconstruction owner: **none**. Core has no lock-candidate
walk and no `+0x294` occupancy.

Focused test: none. L100 card `t_aa5586e5` is on a playable
training-path diet — do not implement lock sets from this mapping
until that lane names the arm.

Siblings: `CBattleEngine__HandleLocks` /
`CBattleEngine__StartLock` in this folder. Next named:
`CBattleEngine__CalcUnitOverCrossHair` `0x0040acc0`
(HandleLocks callee; no 2026-08-19 PE contract).

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00406da0` | `CBattleEngine__SelectNearestForwardTargetFromGlobalSet` | `83ec4c a1d0508500 … e8ef650f00 … e8fdf30f00 … c21800` (539 B) | incoming-ECX thiscall; ret 0x18 ×2; 539 B; 5 E8 side/profile/field98/First/Next / 0 E9; 3 inbound HandleLocks. HIGH on ABI, BSS set `[0x008550d0]`, unique three-site inbound. Mapping `PARTIAL_CONTRACT`; no Core owner. **Not** on `GetClosestLockableUnit` or rebuild parity. |
