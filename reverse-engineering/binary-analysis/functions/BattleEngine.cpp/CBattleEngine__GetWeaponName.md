# CBattleEngine__GetWeaponName

Status: active static function note
Last updated: 2026-08-19
Source File: `references/Onslaught/BattleEngine.cpp` | Binary: BEA.exe,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). The Ghidra database was not opened. Cycle
103 follow-up accepted overheat parent/jet `4013d039` /
`63c63909` — not redone. Cycle 103 close: energy dispatcher
`b5df91bf` was not independently accepted that cycle. This wake
already landed Walker GetWeaponName `5c5e6725` — not independently
accepted this cycle. Envelope. Did not mill FUN_*. Did not invent
field names. Did not rename the jet JMP target. Did not invent a
Core owner.

> Address: `0x0040c550`

## Contract

Incoming-ECX `thiscall`. First insn `cmp dword [ecx+0x260], 3`.
Zero `ret`. Body `0x0040c550`–`0x0040c56e` is 31 bytes, SHA-256
`1ced8b7a2f1990b1041a2ac6d17316b1130a8e92859e9a2ec10b20e83232a828`.
Capstone: 6 insns, zero `E8`, 2 `E9`, 2 unique rel32 targets.

Pinned body:

1. `[ecx+0x260]==3` → `ecx = [ecx+0x57c]` / `E9`
   table-named `CGeneralVolume__GetMode3CurrentEntryDisplayString`
   `0x00412420`. That table name is counted, not rewritten.
2. Else `ecx = [ecx+0x578]` / `E9` already-pinned
   `CBattleEngineWalkerPart__GetWeaponName` `0x004145a0`.

One inbound `.text` `E8`/`E9`: `CALL` at `0x00486069` inside
`CHud__RoutePanel_T4_00485d50`. Zero encodings of imm
`50 c5 40 00` in the image (not a vtable slot). The inbound
parent is counted, not rewritten.

Source architecture (not proof):
`CBattleEngine::GetWeaponName`
`BattleEngine.cpp:2819-2825`. The `[+0x260]==3` jet/walker split
matches that shape. Do **not** equate `0x00412420`'s current
table name to source `CBattleEngineJetPart::GetWeaponName`.

Rebuild mapping: `PARTIAL_CONTRACT` (named, not implemented). See
the section below. Do not implement Core from this RE root.

Cheapest falsifier: file `0x0000c550` is not
`83 b9 60 02 00 00 03`, **or** `0x0000c55f` is not
`e9 3c 80 00 00`, **or** `0x0000c56a` is not
`e9 b1 5e 00 00`, **or** body SHA-256 is not `1ced8b7a…a828`,
**or** `tools/call_xref_scan.py` on `0x0040c550` is not exactly
one `CALL` at `0x00486069`, **or** any encoding of imm
`50 c5 40 00` exists.

## Rebuild mapping — 2026-08-19

Grade: `PARTIAL_CONTRACT`. Not `REBUILD_READY`. Independently
re-read official+twin `74154bfa` this wake (2506752 equal). Body
SHA-256 still `1ced8b7a…a828`. `call_xref_scan` still one CALL.
Did not open Ghidra. Did not edit `rebuild/**`. Did not rename
`0x00412420`. Did not invent a Core owner.

Retail entity: BattleEngine weapon-name dispatcher. Stuart
architecture (not proof): `BattleEngine.cpp:2819-2825`.

Nearest reconstruction owner: **none**. L100 card `t_aa5586e5`
is on a playable training-path diet — do not implement from this
mapping until that lane names the arm.

Siblings: `CBattleEngineWalkerPart__GetWeaponName` /
`CBattleEngine__IsEnergyWeapon`. Next named:
`CBattleEngineWalkerPart__GetWeaponPhysicsName` `0x004145d0` (no
2026-08-19 PE envelope).

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x0040c550` | `CBattleEngine__GetWeaponName` | `83b96002000003 … e93c800000 … e9b15e0000` (31 B) | incoming-ECX thiscall; 0 ret; 31 B; 0 E8 / 2 E9 / 2 targets; 1 inbound CALL. HIGH on ABI, `[+0x260]==3` tail-jmp dispatch, unique inbound. Mapping `PARTIAL_CONTRACT`. **Not** on jet-target rename or rebuild parity. |
