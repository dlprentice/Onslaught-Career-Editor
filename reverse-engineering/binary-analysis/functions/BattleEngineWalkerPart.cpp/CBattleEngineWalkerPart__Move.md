# CBattleEngineWalkerPart__Move

Status: active static function note
Last updated: 2026-08-19
Source File: `references/Onslaught/BattleEngineWalkerPart.cpp` | Binary: BEA.exe,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). The Ghidra database was not opened. Cycle
95 accepted Morph `46e8646f` and UpdateAutoAim `1a846174` — not
redone. Live child `t_b3e2361c` owns UpdateCameraVectorsAndInput
`0x00407a50` — not stolen. Envelope, not a 232-instruction walk.
Did not mill FUN_*. Did not implement lock sets. Did not spawn
another RE child.

> Address: `0x00413760`

## Contract

Incoming-ECX `thiscall`. First insn `sub esp, 0x38`. One bare
`ret` at `0x00413a63`. Body `0x00413760`–`0x00413a63` is 772
bytes, SHA-256
`814ff470bba1e295f26c0bc7e6b77a3a5a501638d52a896ca643c7a97c5f09f0`
(PE bytes; not the C1-table Ghidra digest `a20e44e1…`). Capstone:
232 insns, 11 `E8`, 1 `E9`, 11 unique rel32 targets. The `E9` at
`0x0041388a` is intra-body to `0x00413924` and is not named.
Neighbour table `CBattleEngineWalkerPart__GoingIntoWater` starts
at `0x00413a70` after alignment `nop`s and is not rewritten.
Preceding table `CGeneralVolume__ApplyPitchInputByWeaponClass`
ends before the `nop` pad and is not rewritten.

Pinned prologue, with `esi = ecx`:

1. `eax = [esi+0x20]`. Store `2` at `[eax+0x630]`. `[esi+0x20]`
   and `[+0x630]` are **not** named here.
2. `E8` `CBattleEngineWalkerPart__GetCurrentWeapon` `0x00414030`.
   EAX==0 stores 0 at `[esi+0x10]`. That slot is **not** named
   here.
3. `ecx = [esi+0x20]`. `eax = [ecx+0x574]`. Nonzero increments
   `[eax+0x44]`. The player-stat field is **not** named here.
4. Counted list walk on `[esi]` / `[esi+8]` calling table
   `CMonitor__UpdateTrackedRenderPair` `0x005078f0`. That table
   name is **not** adopted as `MoveEmitter`.
5. `fld` BSS `[0x00672fd0]` minus `[main+0xcc]`, `fcomp`
   `[0x005d8cb4]` (`9a 99 99 3e` = 0.3f). Distinct from the
   already-cited 0.5f at `0x005d85ec`.
6. When `[esi+0x14]` is zero, `fmul` `[0x005d85ec]` (0.5f). Then
   store `1` at `[esi+0x14]` and copy `[main+0xfc]` →
   `[main+0x100]`. Those fields are **not** named here.
7. Two `E8` `CBattleEngineWalkerPart__GoingIntoWater`
   `0x00413a70`. Counted, not contracted: `E8`
   `CBattleEngineWalkerPart__Slide` `0x00413b90`; `E8`
   `SharedUnitVFunc_T3_00408120` `0x00408120`; `E8`
   `CBattleEngineWalkerPart__UpdateWalkCycle` `0x00412ad0`. Other
   of the 11 targets are counted, not contracted.

Two inbound `.text` `E8`/`E9`: `CALL` at `0x00408c4b` and
`0x00408c83` inside table `CBattleEngine__Move` (already pinned).
Both load `ecx` from `[ebp+0x578]` — the walker-part slot Init
already stores. Zero encodings of imm `60 37 41 00` in the image
(not a vtable slot).

Source architecture (not proof): `CBattleEngineWalkerPart::Move`
`BattleEngineWalkerPart.cpp:361-439`. Retail bare `ret` matches
zero stack args. The 0.3f ground-recharge compare matches source
line 375; it is not the 0.5f `IsWalking` threshold.

Rebuild mapping: `PARTIAL_CONTRACT` (named; existing Core path
already cites this body). See the section below. Do not implement
Core from this RE root.

Cheapest falsifier: file `0x00013760` is not `83 ec 38`, **or**
`0x00013764` is not `8b f1`, **or** `0x00013769` is not
`c7 80 30 06 00 00 02 00 00 00`, **or** `0x00013773` is not
`e8 b8 08 00 00`, **or** `0x000137d3` is not
`d8 1d b4 8c 5d 00`, **or** `0x0001383b` is not
`c7 46 14 01 00 00 00`, **or** `0x00013a63` is not `c3`, **or**
`0x001d8cb4` is not `9a 99 99 3e`, **or** body SHA-256 is not
`814ff470…09f0`, **or** `tools/call_xref_scan.py` on
`0x00413760` is not exactly those two `CALL`s, **or** a third
`.text` `E8`/`E9` to this entry exists, **or** any encoding of
imm `60 37 41 00` exists.

## Rebuild mapping — 2026-08-19

Grade: `PARTIAL_CONTRACT`. Not `REBUILD_READY`. Independently
re-read official+twin `74154bfa` this wake (2506752 equal). Body
SHA-256 still `814ff470…09f0`. `call_xref_scan` still two Move
sites. File `0x001d8cb4` still `9a 99 99 3e`. Did not open
Ghidra. Did not edit `rebuild/**`. Did not walk all 11 callees.
Did not name `[esi+0x20]`, `[+0x630]`, `[+0x10]`, or `[+0x14]`.

Retail entity: per-frame walker-part Move from the already-pinned
`CBattleEngine__Move` `[+0x578]` sites. Stuart architecture (not
proof): `BattleEngineWalkerPart.cpp:361-439`.

Nearest reconstruction owner: **existing** walker-ground path in
`SimulationConstants` / `Simulation` (0.3f recharge compare and
walk friction already cite this body). Not a new owner. The
`+0x14` half-rate arm stays unmodelled there. L100 card
`t_aa5586e5` is on a playable training-path diet — do not
implement from this mapping until that lane names the arm.

Siblings: `CBattleEngine__Move` in `../BattleEngine.cpp/`. Next
named: `CBattleEngineJetPart__Move` `0x00410c50` (Move callee;
July identity note; no 2026-08-19 PE envelope). Camera body
`0x00407a50` stays with child `t_b3e2361c`.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00413760` | `CBattleEngineWalkerPart__Move` | `83ec38 8bf1 c7803006000002 … d81db48c5d00 … c7461401000000 … c3` (772 B) | incoming-ECX thiscall; bare ret ×1; 772 B; 11 E8 / 1 E9 / 11 targets; 2 inbound Move `[+0x578]`. HIGH on ABI, `[+0x20]`/`[+0x630]=2`, 0.3f compare, unique inbound. Mapping `PARTIAL_CONTRACT`; existing Core path only. **Not** on field names, `MoveEmitter`, or rebuild parity. |
