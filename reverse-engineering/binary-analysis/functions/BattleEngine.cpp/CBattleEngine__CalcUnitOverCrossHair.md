# CBattleEngine__CalcUnitOverCrossHair

Status: active static function note
Last updated: 2026-08-19
Source File: `references/Onslaught/BattleEngine.cpp` | Binary: BEA.exe,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). The Ghidra database was not opened. Table
name is the saved Ghidra label, not this proof. Cycle 92 accepted
`1093bee8` StartLock and `c87456f5` LockHit — not redone. This wake
also landed `9ced05c0` HandleLocks and `80dc9aca` SelectNearest —
not redone. Envelope, not a 305-instruction walk. Did not mill
`FUN_0040ac30`. Did not implement lock sets.

> Address: `0x0040acc0`

## Contract

Incoming-ECX `thiscall`. First insn `push -1` (SEH cookie). One
`ret 0xc` at `0x0040b0f6`. Body `0x0040acc0`–`0x0040b0f8`
is 1081 bytes, SHA-256
`fb4257ded2a125448eac5fb1d29e5ffcb5cbe1f885bfe3ebfcb935cc5a54d734`.
Capstone: 305 insns, 19 `E8`, zero `E9`. Neighbour table
`CGeneralVolume__ctor_base` starts at `0x0040b100` and is not
rewritten. Preceding table `CBattleEngine__Rearm` ends at
`0x0040acb1` and is not rewritten.

The body, with `edi = ecx`:

1. SEH frame (`push 0x005d124b` / `fs:[0]`), then `sub esp, 0x124`.
2. `cmp [edi+0x574], 0` / `je` a late path. Source architecture
   (not proof): `mPlayer.ToRead()`.
3. A stack dword at `[esp+0x14c]` compared to 0. Nonzero:
   `push 0` / `lea ecx, [edi+0x4c8]` / `E8`
   `CGenericActiveReader__SetReader` `0x00401000`, then the same
   on `[edi+0x4cc]`. Source architecture (not proof):
   `inUpdateData` clears `mCurrentUnitOverCrosshair` and
   `mCurrentUnitOverCrosshairRegardlessOfRange`.
4. Later counted (not contracted) `E8`s include
   `CPlayer__GetCurrentViewPoint` `0x004d2a70`,
   `CPlayer__GetCurrentViewOrientation` `0x004d2ae0`,
   `CWorld__FindFirstThingToHitLine` `0x0050b030`,
   `CEventManager__AddEvent_AtTime` `0x0044b370`. Callee bodies
   and field names are **not** this proof.

Two inbound `.text` `E8`/`E9`: `CALL` at `0x00406b2e` inside
table `CBattleEngine__HandleLocks`; `CALL` at `0x0040c2c3`
inside table `CBattleEngine__HandleEvent` `0x0040c180`–`0x0040c2dd`.
Zero encodings of imm `c0 ac 40 00` in the image.

Source architecture (not proof):
`CBattleEngine::CalcUnitOverCrossHair`
`BattleEngine.cpp:2278-2344`
(`CEvent*`, `BOOL inMeshCollision`, `BOOL inUpdateData`). Retail
`ret 0xc` matches three stack args.

Rebuild mapping: `PARTIAL_CONTRACT` (named, not implemented). See
the section below. Do not implement Core from this RE root.

Cheapest falsifier: file `0x0000acc0` is not `6a ff`, **or**
`0x0000ace7` is not `39 9f 74 05 00 00`, **or** `0x0000ad05` is
not `e8 f6 62 ff ff`, **or** `0x0000b0f6` is not `c2 0c 00`,
**or** body SHA-256 is not `fb4257de…d734`, **or**
`tools/call_xref_scan.py` on `0x0040acc0` is not exactly those
two `CALL`s, **or** a third `.text` `E8`/`E9` to this entry
exists.

## Rebuild mapping — 2026-08-19

Grade: `PARTIAL_CONTRACT`. Not `REBUILD_READY`. Independently
re-read official+twin `74154bfa` this wake (2506752 equal). Body
SHA-256 still `fb4257de…d734`. `call_xref_scan` still two `CALL`s.
Did not open Ghidra. Did not edit `rebuild/**`.

Retail entity: player crosshair unit probe used by HandleLocks
(acquire) and HandleEvent (scheduled refresh). Stuart
architecture (not proof): `BattleEngine.cpp:2278-2344`.

Nearest reconstruction owner: **none**. Core has no crosshair
ray and no `+0x4c8` / `+0x4cc` readers.

Focused test: none. L100 card `t_aa5586e5` is on a playable
training-path diet — do not implement lock sets or this probe
from this mapping until that lane names the arm.

Siblings: `CBattleEngine__HandleLocks` /
`CBattleEngine__SelectNearestForwardTargetFromGlobalSet` in this
folder. Next named: `CBattleEngine__HandleEvent` `0x0040c180`
(the scheduled inbound; no 2026-08-19 PE contract).

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x0040acc0` | `CBattleEngine__CalcUnitOverCrossHair` | `6aff 684b125d00 … 399f74050000 … e8f662ffff … c20c00` (1081 B) | incoming-ECX thiscall; SEH; ret 0xc ×1; 1081 B; 19 E8 / 0 E9; 2 inbound HandleLocks+HandleEvent. HIGH on ABI, `+0x574` gate, `+0x4c8`/`+0x4cc` SetReader(0), unique two-site inbound. Mapping `PARTIAL_CONTRACT`; no Core owner. **Not** on field names or rebuild parity. |
