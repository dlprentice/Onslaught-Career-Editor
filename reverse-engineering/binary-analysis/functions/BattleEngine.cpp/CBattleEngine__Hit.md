# CBattleEngine__Hit

Status: active static function note
Last updated: 2026-08-19
Source File: `references/Onslaught/BattleEngine.cpp` | Binary: BEA.exe,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). The Ghidra database was not opened. Cycle
96 accepted WalkerPart Move through UpdateMouseLookAngles. This
wake landed JetPart Move `e54e2d77` and GroundParticleEffect
`b4ecf83c` — not redone. Envelope, not a 114-instruction walk.
Did not mill FUN_*. Did not implement lock sets. Did not widen
the existing Gen31 C2 row.

> Address: `0x00407350`

## Contract

Incoming-ECX `thiscall`. First insn `sub esp, 0x40`. `esi = ecx`.
One `ret 8` at `0x004074c9`. Body `0x00407350`–`0x004074cb` is
380 bytes, SHA-256
`8034efee2c37c5e02579dc82d4405b758cedc96d62b27909f5c66a6cea43ae8a`
(PE bytes; not the C1-table Ghidra digest `28151a2f…`). Capstone:
114 insns, 2 `E8`, zero `E9`, 2 unique rel32 targets. Neighbour
table `CBattleEngine__Gravity` starts at `0x004074d0` and is not
rewritten. Preceding table `CBattleEngine__DisplayLock` is
already pinned and is not rewritten.

Pinned prologue, with `esi = ecx`:

1. `ebx = [esp+0x4c]` after `push ebx` (second stack arg).
   `edi` later loads the first stack arg. Those args are **not**
   named here.
2. `eax = [ebx+0xc8]`. Nonzero stores 0 at `[esi+0x314]`. Those
   fields are **not** named here.
3. `test [esi+0x2c], 4` then tests on `[edi+0x34]`. Counted
   `E8` `CGeneralVolume__SpawnPickupAndDispatch` `0x0040dfb0`
   and `vcall [eax+0x38]`. Those names are **not** adopted as
   `Explode` / `AddShutdownEvent`.
4. `push ebx` / `push edi` / `E8`
   `CUnit__CreateHitRefEvaluateImpulseAndDispatchHit`
   `0x004fcc30`. Then `cmp [ebx+0xc8], 1`. Other of the 2
   targets are counted, not contracted.

Zero inbound `.text` `E8`/`E9`. One image encoding of imm
`50 73 40 00`: file `0x001d8a60` / VA `0x005d8a60` (vtable
slot 39, `+0x9c` from the `CBattleEngine` vtable base
`0x005d89c4` named by HandleEvent). Neighbouring dwords are
**not** this proof.

Source architecture (not proof): `CBattleEngine::Hit`
`BattleEngine.cpp:1014-1061`. Retail `ret 8` matches two stack
args. The `[arg2+0xc8]` / `[this+0x314]=0` pair matches source
`report->mStuck` / `mInSafeCollisionPlace = FALSE` as
architecture only.

Rebuild mapping: `PARTIAL_CONTRACT` (PE envelope only). The
existing Gen31 C2 bounded Hit row is **not** raised or
rewritten. See the section below. Do not implement Core from
this RE root.

Cheapest falsifier: file `0x00007350` is not `83 ec 40`, **or**
`0x00007360` is not `8b f1`, **or** `0x00007366` is not
`c7 86 14 03 00 00 00 00 00 00`, **or** `0x000074c9` is not
`c2 08 00`, **or** body SHA-256 is not `8034efee…3ae8a`, **or**
`tools/call_xref_scan.py` on `0x00407350` is not empty, **or**
`0x001d8a60` is not `50 73 40 00`, **or** a second encoding of
that imm exists.

## Rebuild mapping — 2026-08-19

Grade: `PARTIAL_CONTRACT`. Not `REBUILD_READY`. Independently
re-read official+twin `74154bfa` this wake (2506752 equal). Body
SHA-256 still `8034efee…3ae8a`. `call_xref_scan` still empty.
File `0x001d8a60` still `50 73 40 00`. Did not open Ghidra. Did
not edit `rebuild/**`. Did not walk the two callees. Did not
name `[+0xc8]` or `[+0x314]`. Did not widen the existing C2.

Retail entity: `CBattleEngine` vtable slot-39 Hit. Stuart
architecture (not proof): `BattleEngine.cpp:1014-1061`. Existing
campaign C2 is a bounded runtime row on this same entry; this
note is the PE envelope only.

Nearest reconstruction owner: **none** added. Existing C2 /
Level 521 Hit evidence is not re-derived. L100 card
`t_aa5586e5` is on a playable training-path diet — do not
implement from this mapping until that lane names the arm.

Siblings: `CBattleEngine__HandleEvent` /
`CBattleEngine__DisplayLock` in this folder. Next named:
`CBattleEngine__Gravity` `0x004074d0` (neighbour; no
2026-08-19 PE envelope).

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00407350` | `CBattleEngine__Hit` | `83ec40 8bf1 c7861403000000000000 … c20800` (380 B) | incoming-ECX thiscall; ret-8; 380 B; 2 E8 / 0 E9 / 2 targets; 0 inbound; unique vtable slot 39 at `0x005d8a60`. HIGH on ABI, `[arg2+0xc8]`/`[+0x314]` store, unique slot. Mapping `PARTIAL_CONTRACT`; existing C2 not widened. **Not** on field names or rebuild parity. |
