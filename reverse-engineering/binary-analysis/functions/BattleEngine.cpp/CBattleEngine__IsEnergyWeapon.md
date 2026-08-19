# CBattleEngine__IsEnergyWeapon

Status: active static function note
Last updated: 2026-08-19
Source File: `references/Onslaught/BattleEngine.cpp` | Binary: BEA.exe,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). The Ghidra database was not opened. Cycle
103 accepted through Walker IsWeaponOverheated `33080a9c` — not
redone. Cycle 103 also accepted Walker IsEnergyWeapon `12576541`
— not redone. This wake already landed overheat parent/jet
`4013d039` / `63c63909` — not independently accepted this cycle.
Envelope. Did not mill FUN_*. Did not invent field names. Did not
rename the jet JMP target. Did not invent a Core owner.

> Address: `0x0040c480`

## Contract

Incoming-ECX `thiscall`. First insn `cmp dword [ecx+0x260], 3`.
Zero `ret`. Body `0x0040c480`–`0x0040c49e` is 31 bytes, SHA-256
`f3a52d4f9cc56586a17d9f460accc90ca2f0a5df3fedc1d78dc39d9f4ea2c198`.
Capstone: 6 insns, zero `E8`, 2 `E9`, 2 unique rel32 targets.

Pinned body:

1. `[ecx+0x260]==3` → `ecx = [ecx+0x57c]` / `E9`
   table-named `CBattleEngineJetPart__IsEnergyWeapon`
   `0x004122b0`. That table name is counted, not rewritten.
2. Else `ecx = [ecx+0x578]` / `E9` table-named
   `CBattleEngineWalkerPart__IsEnergyWeapon` `0x004144c0`.
   Cycle 103 accepted that PE note as `12576541` — not redone.

One inbound `.text` `E8`/`E9`: `CALL` at `0x0048695e` inside
`CHud__RoutePanel_T5_00486940`. Zero encodings of imm
`80 c4 40 00` in the image (not a vtable slot). The inbound
parent is counted, not rewritten.

Source architecture (not proof):
`CBattleEngine::IsEnergyWeapon`
`BattleEngine.cpp:2786-2792`. The `[+0x260]==3` jet/walker split
matches that shape. Do **not** treat the jet JMP target as a
2026-08-19 PE envelope.

Rebuild mapping: `PARTIAL_CONTRACT` (named, not implemented). See
the section below. Do not implement Core from this RE root.

Cheapest falsifier: file `0x0000c480` is not
`83 b9 60 02 00 00 03`, **or** `0x0000c48f` is not
`e9 2c 80 00 00`, **or** `0x0000c49a` is not
`e9 11 5e 00 00`, **or** body SHA-256 is not `f3a52d4f…c198`,
**or** `tools/call_xref_scan.py` on `0x0040c480` is not exactly
one `CALL` at `0x0048695e`, **or** any encoding of imm
`80 c4 40 00` exists.

## Rebuild mapping — 2026-08-19

Grade: `PARTIAL_CONTRACT`. Not `REBUILD_READY`. Independently
re-read official+twin `74154bfa` this wake (2506752 equal). Body
SHA-256 still `f3a52d4f…c198`. `call_xref_scan` still one CALL.
Did not open Ghidra. Did not edit `rebuild/**`. Did not rename
`0x004122b0`. Did not invent a Core owner.

Retail entity: BattleEngine energy-weapon dispatcher. Stuart
architecture (not proof): `BattleEngine.cpp:2786-2792`.

Nearest reconstruction owner: **none**. Existing
`RetailWeaponStores` readout is not rewritten and is not raised
to `REBUILD_READY` from this envelope. L100 card `t_aa5586e5`
is on a playable training-path diet — do not implement from this
mapping until that lane names the arm.

Siblings: `CBattleEngineWalkerPart__IsEnergyWeapon` /
`CBattleEngine__IsWeaponOverheated`. Next named:
`CBattleEngineJetPart__IsEnergyWeapon` `0x004122b0` (no
2026-08-19 PE envelope).

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x0040c480` | `CBattleEngine__IsEnergyWeapon` | `83b96002000003 … e92c800000 … e9115e0000` (31 B) | incoming-ECX thiscall; 0 ret; 31 B; 0 E8 / 2 E9 / 2 targets; 1 inbound CALL. HIGH on ABI, `[+0x260]==3` tail-jmp dispatch, unique inbound. Mapping `PARTIAL_CONTRACT`. **Not** on jet-target rewrite or rebuild parity. |
